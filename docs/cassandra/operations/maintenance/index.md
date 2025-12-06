# Cassandra Maintenance Guide

All Cassandra maintenance happens online. Need to restart a node? Drain it first, and traffic routes to other replicas. Need to change configuration? Roll through nodes one at a time. Need to upgrade versions? Same approach—one node restarts while the others handle requests.

The pattern is always the same: take one node out of rotation, do the work, bring it back, verify it is healthy, then move to the next. With replication factor 3 and LOCAL_QUORUM consistency, losing one node temporarily does not affect availability.

This guide covers routine maintenance tasks: repair scheduling, compaction monitoring, disk management, and rolling restarts.

## Maintenance Philosophy

Cassandra is designed for continuous operation. All maintenance procedures can be performed without cluster downtime using rolling operations—apply changes to one node at a time while the rest of the cluster serves traffic.

```
Rolling Operation Pattern:
─────────────────────────────────────────────────────────────────────────────
For each node in cluster:
   1. Drain node (stop accepting writes, flush data)
   2. Perform maintenance (restart, upgrade, etc.)
   3. Wait for node to rejoin and stabilize
   4. Verify cluster health
   5. Proceed to next node

Never: Perform maintenance on multiple nodes simultaneously
       (unless they are in different failure domains AND RF > 2)
```

---

## Maintenance Task Reference

| Task | Frequency | Impact | When to Perform |
|------|-----------|--------|-----------------|
| Repair | Weekly to daily | Medium | Off-peak hours |
| Cleanup | After topology changes | Medium | After adding/removing nodes |
| Rolling restart | As needed | Low | Configuration changes |
| Compaction tuning | Ongoing | None | When metrics indicate issues |
| Schema changes | As needed | Low | Any time (for most changes) |
| Upgrades | Quarterly | High | Planned maintenance window |
| Log rotation | Daily | None | Automated |
| Backup verification | Weekly to monthly | None | Scheduled |

---

## Rolling Restart

### When to Perform

- After changing `cassandra.yaml` configuration
- After changing JVM options
- To apply OS patches
- To clear memory/restart after issues
- As part of upgrade process

### Procedure

```bash
#!/bin/bash
# rolling_restart.sh - Run on each node sequentially

set -e

HOSTNAME=$(hostname -f)
echo "=== Starting rolling restart on ${HOSTNAME} ==="

# 1. Check cluster health before proceeding
echo "Checking cluster health..."
STATUS=$(nodetool status)
if echo "${STATUS}" | grep -E "^D[NLM]"; then
    echo "ERROR: Down nodes detected. Fix before proceeding."
    exit 1
fi

# Check for pending operations
PENDING=$(nodetool compactionstats | grep "pending tasks" | awk '{print $3}' || echo "0")
if [ "${PENDING:-0}" -gt 20 ]; then
    echo "WARNING: ${PENDING} pending compactions. Consider waiting."
fi

# 2. Drain the node
echo "Draining node..."
nodetool drain

# drain does:
# - Stops accepting new connections
# - Flushes all memtables to disk
# - Stops listening on native and thrift ports

# 3. Stop Cassandra
echo "Stopping Cassandra..."
sudo systemctl stop cassandra

# 4. Apply changes (configuration, JVM options, etc.)
# --- Your changes here ---

# 5. Start Cassandra
echo "Starting Cassandra..."
sudo systemctl start cassandra

# 6. Wait for node to come up
echo "Waiting for node to join cluster..."
MAX_WAIT=300  # 5 minutes
WAITED=0

while true; do
    if nodetool status 2>/dev/null | grep -E "^UN.*${HOSTNAME}" > /dev/null; then
        echo "Node is up and normal (UN)"
        break
    fi

    if [ ${WAITED} -ge ${MAX_WAIT} ]; then
        echo "ERROR: Node did not come up within ${MAX_WAIT} seconds"
        exit 1
    fi

    sleep 10
    WAITED=$((WAITED + 10))
    echo "Waiting... (${WAITED}s)"
done

# 7. Wait for streaming to complete (if any)
echo "Checking for streaming..."
while nodetool netstats | grep -q "Receiving\|Sending"; do
    echo "Streaming in progress, waiting..."
    sleep 30
done

# 8. Final health check
echo "Final health check..."
nodetool status
nodetool tpstats | head -15

echo "=== Rolling restart complete on ${HOSTNAME} ==="
echo "Wait at least 2 minutes before proceeding to next node"
```

### Important Notes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  DO NOT skip the wait between nodes!                                        │
│                                                                             │
│  Why:                                                                       │
│  - Node needs time to stabilize and warm caches                             │
│  - Gossip needs to propagate new state                                      │
│  - Pending hints need to be delivered                                       │
│  - Compaction from flush needs to complete                                  │
│                                                                             │
│  Minimum wait: 2 minutes for small clusters, 5+ minutes for large clusters  │
├─────────────────────────────────────────────────────────────────────────────┤
│  Watch for restarting too quickly:                                          │
│  - Hints piling up                                                          │
│  - Increased read latency                                                   │
│  - Temporary consistency issues                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Cleanup

### What Cleanup Does

After topology changes (adding/removing nodes), data is redistributed. Nodes that no longer own certain token ranges keep the old data. Cleanup removes this orphaned data.

```
Before cleanup:
─────────────────────────────────────────────────────────────────────────────
Original 3-node cluster: Each node owns ~33% of data

After adding 4th node:
- Each node now owns ~25% of data
- But original 3 nodes still have ~33% of data on disk
- Extra 8% per node is orphaned

Cleanup removes the orphaned 8%, freeing disk space
```

### When to Run

```
Run cleanup AFTER:
✓ Adding nodes (and bootstrap completes)
✓ Changing keyspace replication factor
✓ Restoring from backup to different topology

Do NOT run cleanup:
✗ Before repair completes (may lose not-yet-repaired data)
✗ During another maintenance operation
✗ When cluster is under heavy load
```

### Procedure

```bash
#!/bin/bash
# cleanup.sh - Run on each EXISTING node after adding new nodes

KEYSPACE=$1

if [ -z "$KEYSPACE" ]; then
    echo "Usage: cleanup.sh <keyspace>"
    exit 1
fi

echo "Starting cleanup for keyspace: ${KEYSPACE}"
echo "This may take a while for large keyspaces..."

# Check disk space before cleanup
DISK_BEFORE=$(df -h /var/lib/cassandra | tail -1)
echo "Disk before: ${DISK_BEFORE}"

# Run cleanup
# Cleanup is CPU and I/O intensive
nodetool cleanup ${KEYSPACE}

# Check disk space after
DISK_AFTER=$(df -h /var/lib/cassandra | tail -1)
echo "Disk after: ${DISK_AFTER}"

echo "Cleanup complete"
```

### Cleanup for All Keyspaces

```bash
# List all keyspaces and run cleanup
cqlsh -e "DESC KEYSPACES" | tr ' ' '\n' | grep -v "^$\|system" | while read ks; do
    echo "Cleaning up keyspace: ${ks}"
    nodetool cleanup ${ks}
done
```

### Throttling Cleanup

```bash
# Reduce cleanup impact on production traffic
# Set compaction throughput (cleanup uses compaction resources)
nodetool setcompactionthroughput 32  # MB/s (default is 64)

# Run cleanup
nodetool cleanup my_keyspace

# Reset to default
nodetool setcompactionthroughput 64
```

---

## Compaction Management

### Understanding Compaction

Compaction merges SSTables to:
- Reclaim space from overwrites and deletes
- Reduce number of SSTables to read
- Remove expired data (TTL)
- Purge tombstones (after gc_grace_seconds)

### Monitoring Compaction

```bash
# Current compaction activity
nodetool compactionstats

# Example output:
# pending tasks: 15
# - keyspace.table: 3
# - keyspace.table2: 12
#
# id                                   compaction type keyspace  table     completed total    unit  progress
# c91a-...                             COMPACTION      my_ks     my_table  1234567   9876543 bytes 12.5%

# Historical compaction statistics
nodetool compactionhistory

# Table-level compaction metrics
nodetool tablestats my_keyspace.my_table | grep -i compact
```

### Compaction Thresholds

| Metric | Normal | Warning | Action |
|--------|--------|---------|--------|
| Pending tasks | 0-5 | 20-50 | Investigate if sustained |
| Pending tasks | 50+ | 100+ | Increase throughput or add resources |
| SSTable count per table | < 20 | 50+ | May need compaction strategy change |

### Tuning Compaction

```bash
# Increase compaction throughput (default 64 MB/s)
nodetool setcompactionthroughput 128

# Decrease (to reduce impact on reads)
nodetool setcompactionthroughput 32

# View current setting
nodetool getcompactionthroughput

# Set concurrent compactors (default based on CPUs)
# Edit cassandra.yaml: concurrent_compactors: 4
```

### Forcing Compaction

Use sparingly—forced compaction creates large SSTables that must be recompacted later:

```bash
# Force compaction on specific table
nodetool compact my_keyspace my_table

# Force major compaction (creates single SSTable - usually BAD!)
nodetool compact my_keyspace my_table --user-defined

# Better: Upgrade SSTables after Cassandra upgrade
nodetool upgradesstables my_keyspace my_table
```

### Stopping Compaction

In emergencies only:

```bash
# Stop all compactions
nodetool stop COMPACTION

# Check that compactions stopped
nodetool compactionstats

# Compactions will resume automatically
# To re-enable immediately:
nodetool enableautocompaction my_keyspace my_table
```

---

## Schema Management

### Schema Best Practices

```
DO:
✓ Make schema changes from a single node
✓ Wait for schema agreement before next change
✓ Test schema changes in staging first
✓ Back up schema before major changes

DON'T:
✗ Make schema changes from multiple nodes simultaneously
✗ Drop columns without verifying they're not in use
✗ Change primary keys (requires table recreation)
✗ Make schema changes during high load
```

### Checking Schema Agreement

```bash
# All nodes should show same schema version
nodetool describecluster | grep -A10 "Schema versions"

# Output should show single version with all IPs:
# Schema versions:
#     abc123-def456 [10.0.0.1, 10.0.0.2, 10.0.0.3]

# Multiple versions = disagreement:
#     abc123-def456 [10.0.0.1, 10.0.0.2]
#     xyz789-... [10.0.0.3]  ← Problem!
```

### Fixing Schema Disagreement

```bash
# Option 1: Wait (usually resolves within minutes)
sleep 60 && nodetool describecluster | grep -A10 "Schema versions"

# Option 2: Restart affected node
# (node with different schema version)
ssh affected_node "nodetool drain && sudo systemctl restart cassandra"

# Option 3: Reset local schema (last resort, lose local schema modifications)
nodetool resetlocalschema
```

### Safe Schema Changes

```sql
-- Adding columns (instant, no data movement)
ALTER TABLE my_keyspace.users ADD phone TEXT;
ALTER TABLE my_keyspace.users ADD (address TEXT, city TEXT);

-- Dropping columns (instant, data remains until compaction)
ALTER TABLE my_keyspace.users DROP phone;

-- Changing table options
ALTER TABLE my_keyspace.users WITH
    compaction = {'class': 'LeveledCompactionStrategy'}
    AND gc_grace_seconds = 172800;

-- Adding indexes (may take time to build)
CREATE INDEX ON my_keyspace.users (email);
```

### Dangerous Schema Changes

```sql
-- Cannot change primary key (must recreate table)
-- DO NOT: ALTER TABLE users ALTER PRIMARY KEY...

-- Cannot change column types (must recreate)
-- DO NOT: ALTER TABLE users ALTER email TYPE blob;

-- Dropping tables (immediate, data lost)
DROP TABLE my_keyspace.users;  -- DATA LOSS!

-- Use IF EXISTS to prevent errors
DROP TABLE IF EXISTS my_keyspace.old_table;
```

---

## Disk Maintenance

### Monitoring Disk Usage

```bash
# Per-node disk usage
df -h /var/lib/cassandra

# Per-keyspace disk usage
nodetool tablestats my_keyspace | grep "Space used"

# Find large directories
du -sh /var/lib/cassandra/data/*

# Find large tables
du -sh /var/lib/cassandra/data/*/* | sort -h | tail -20
```

### Reclaiming Disk Space

```bash
# Clear snapshots (major space consumer)
nodetool listsnapshots
nodetool clearsnapshot -t old_snapshot_name
nodetool clearsnapshot  # Clear ALL snapshots

# Clear incremental backups (if enabled)
find /var/lib/cassandra/data -path "*/backups/*" -delete

# Force compaction to reclaim tombstone space
# Only if gc_grace_seconds has passed and repair is current
nodetool compact my_keyspace my_table
```

### Disk Space Alerts

Set up alerts for:

| Threshold | Action |
|-----------|--------|
| 60% used | Plan capacity expansion |
| 75% used | Urgent: add capacity soon |
| 85% used | Critical: add capacity immediately |
| 90% used | Emergency: stop writes if necessary |

---

## Log Maintenance

### Log Files

```
Default log locations:
─────────────────────────────────────────────────────────────────────────────
/var/log/cassandra/system.log    → Main application log
/var/log/cassandra/debug.log     → Debug output (high volume)
/var/log/cassandra/gc.log        → Garbage collection logs
/var/log/cassandra/audit/        → Audit logs (if enabled)
```

### Log Rotation

```bash
# Logrotate configuration (/etc/logrotate.d/cassandra)
/var/log/cassandra/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 cassandra cassandra
}

# Manual rotation
logrotate -f /etc/logrotate.d/cassandra

# Clear old logs manually
find /var/log/cassandra -name "*.log.*" -mtime +7 -delete
```

### Important Log Patterns

```bash
# Find errors
grep -i "error\|exception" /var/log/cassandra/system.log | tail -50

# Find warnings
grep -i "warn" /var/log/cassandra/system.log | tail -50

# GC pauses
grep "GC pause" /var/log/cassandra/gc.log | tail -20

# Compaction issues
grep -i "compact" /var/log/cassandra/system.log | grep -i "error\|fail"

# Dropped messages
grep "DROPPED" /var/log/cassandra/system.log | tail -20
```

---

## Version Upgrades

### Upgrade Planning

```
Upgrade Path Rules:
─────────────────────────────────────────────────────────────────────────────
1. Always upgrade one major version at a time
   3.11 → 4.0 → 4.1 → 5.0 (correct)
   3.11 → 5.0 (WRONG - skip versions)

2. Read release notes for breaking changes
3. Test in staging with production data
4. Schedule during low-traffic period
5. Have rollback plan ready
```

### Pre-Upgrade Checklist

```bash
#!/bin/bash
# pre_upgrade_check.sh

echo "=== Pre-Upgrade Checklist ==="

# 1. Cluster health
echo "1. Checking cluster health..."
nodetool status | grep -E "^[UD][NLMJ]"

# 2. No pending operations
echo "2. Checking pending operations..."
nodetool compactionstats | head -5
nodetool netstats | head -10

# 3. Backup
echo "3. Verify recent backup exists..."
nodetool listsnapshots | head -10

# 4. Repair status
echo "4. Check repair status..."
nodetool tablestats system.local | grep -i repair

# 5. Schema agreement
echo "5. Checking schema agreement..."
nodetool describecluster | grep -A10 "Schema versions"

# 6. Disk space for SSTable upgrade
echo "6. Checking disk space..."
df -h /var/lib/cassandra

echo ""
echo "Review above output before proceeding with upgrade"
```

### Upgrade Procedure

```bash
#!/bin/bash
# upgrade_node.sh - Run on each node sequentially

set -e

NEW_VERSION="4.1.3"

echo "=== Upgrading to Cassandra ${NEW_VERSION} ==="

# 1. Drain and stop
echo "Draining node..."
nodetool drain
echo "Stopping Cassandra..."
sudo systemctl stop cassandra

# 2. Backup configuration
echo "Backing up configuration..."
cp /etc/cassandra/cassandra.yaml /etc/cassandra/cassandra.yaml.bak.$(date +%Y%m%d)
cp /etc/cassandra/jvm*.options /etc/cassandra/jvm.options.bak.$(date +%Y%m%d)

# 3. Upgrade packages
echo "Upgrading packages..."
# For package manager install:
sudo apt-get update && sudo apt-get install cassandra=${NEW_VERSION}
# Or for tarball:
# Stop, extract new version, update symlinks

# 4. Merge configuration changes
echo "Review configuration changes..."
# diff /etc/cassandra/cassandra.yaml.bak /etc/cassandra/cassandra.yaml.new
# Apply necessary changes

# 5. Start Cassandra
echo "Starting Cassandra..."
sudo systemctl start cassandra

# 6. Wait for node to join
echo "Waiting for node to join..."
sleep 60
nodetool status

# 7. Upgrade SSTables (run after all nodes upgraded)
# echo "Upgrading SSTables..."
# nodetool upgradesstables

echo "=== Upgrade complete on this node ==="
```

### Post-Upgrade Tasks

```bash
# After ALL nodes upgraded:

# 1. Upgrade SSTables to new format
nodetool upgradesstables -a  # -a for all keyspaces

# 2. Run repair
nodetool repair -pr

# 3. Verify metrics and logs
tail -100 /var/log/cassandra/system.log | grep -i error

# 4. Test application functionality
```

---

## Automated Maintenance Script

```bash
#!/bin/bash
# weekly_maintenance.sh

LOG_FILE="/var/log/cassandra/maintenance_$(date +%Y%m%d).log"
KEYSPACE="my_keyspace"

exec > >(tee -a ${LOG_FILE}) 2>&1

echo "=== Weekly Maintenance: $(date) ==="

# 1. Health check
echo -e "\n--- Health Check ---"
nodetool status
nodetool describecluster | grep -A5 "Schema"

# 2. Take snapshot before maintenance
echo -e "\n--- Taking Snapshot ---"
SNAPSHOT="weekly_$(date +%Y%m%d)"
nodetool flush ${KEYSPACE}
nodetool snapshot -t ${SNAPSHOT} ${KEYSPACE}

# 3. Run repair
echo -e "\n--- Running Repair ---"
nodetool repair -pr ${KEYSPACE}

# 4. Check and clear old snapshots
echo -e "\n--- Managing Snapshots ---"
nodetool listsnapshots
# Clear snapshots older than 2 weeks
for snap in $(nodetool listsnapshots | grep "weekly_" | awk '{print $1}' | sort | head -n -2); do
    echo "Clearing old snapshot: ${snap}"
    nodetool clearsnapshot -t ${snap}
done

# 5. Final status
echo -e "\n--- Final Status ---"
nodetool compactionstats | head -5
df -h /var/lib/cassandra

echo -e "\n=== Maintenance Complete: $(date) ==="
```

---

## Troubleshooting Common Issues

### High Pending Compactions

```bash
# Diagnose
nodetool compactionstats          # What is pending
nodetool tablestats | grep -i sstable  # SSTable counts

# Solutions
nodetool setcompactionthroughput 128   # Increase throughput
# Or check if disk I/O is saturated
iostat -x 1 5
```

### Slow Queries

```bash
# Enable slow query logging (cassandra.yaml)
# slow_query_log_timeout_in_ms: 500

# Check logs
grep "slow" /var/log/cassandra/debug.log

# Common causes:
# - Large partitions (nodetool tablehistograms)
# - Tombstone accumulation (enable tracing)
# - Missing indexes (check query plans)
```

### Disk Space Issues

```bash
# Find what is using space
du -sh /var/lib/cassandra/data/*
du -sh /var/lib/cassandra/data/*/*
du -sh /var/lib/cassandra/commitlog

# Clear snapshots
nodetool clearsnapshot

# Check for large tombstone-heavy tables
nodetool tablestats | grep -i tombstone
```

---

## Next Steps

- **[Repair Guide](../repair/index.md)** - Detailed repair procedures
- **[Backup Guide](../backup-restore/index.md)** - Backup strategies
- **[Monitoring](../../monitoring/index.md)** - Set up observability
- **[Troubleshooting](../../troubleshooting/index.md)** - Problem resolution
