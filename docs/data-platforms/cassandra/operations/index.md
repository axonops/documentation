---
title: "Cassandra Operations Guide"
description: "Apache Cassandra operations guide covering repair, compaction, monitoring, backup, configuration, and maintenance procedures for production cluster management."
meta:
  - name: keywords
    content: "Cassandra operations, cluster management, maintenance"
---

# Cassandra Operations Guide

Cassandra does not need scheduled downtime. Nodes can be added, removed, upgraded, and reconfigured while the cluster serves traffic. But this flexibility comes with responsibility—Cassandra does not maintain itself.

Three things will cause problems if neglected: repair (synchronizes replicas, prevents deleted data from resurrecting), compaction (merges SSTables, keeps reads fast), and monitoring (catches issues before users notice). Most Cassandra incidents trace back to skipping one of these.

This guide covers day-to-day operations, maintenance procedures, and emergency response.

## Operations Philosophy

Cassandra is designed for continuous operation. The operational model prioritizes availability—the database should never go down for maintenance. This influences every procedure in this guide.

!!! abstract "Cassandra Operational Principles"
    | Principle | Implication |
    |-----------|-------------|
    | No single point of failure | Any node can handle any request |
    | Continuous availability | Rolling operations, no downtime windows |
    | Eventual consistency | Background processes maintain correctness |
    | Self-healing | Repair and anti-entropy fix inconsistencies |
    | Horizontal scaling | Add capacity by adding nodes |

### The Three Critical Operations

These three operations must be performed regularly. Neglecting any of them leads to production failures:

| Operation | Why It is Critical | What Happens If Neglected |
|-----------|-------------------|---------------------------|
| **Repair** | Fixes inconsistencies between replicas | Data divergence, zombie data after deletes |
| **Backup** | Enables recovery from disasters | Permanent data loss |
| **Monitoring** | Detect problems before failures | Surprise outages, cascading failures |

---

## Cluster Health Assessment

Before performing any operation, assess cluster health:

```bash
# Essential health check commands
nodetool status           # Node states and token distribution
nodetool describecluster  # Schema agreement, cluster name
nodetool tpstats          # Thread pool status (blocked = problem)
nodetool compactionstats  # Pending compactions
nodetool gossipinfo       # Inter-node communication
```

!!! tip "Virtual Tables Alternative (Cassandra 4.0+)"
    Many nodetool commands have CQL equivalents via [virtual tables](virtual-tables/index.md):
    ```sql
    SELECT * FROM system_views.gossip_info;         -- gossipinfo
    SELECT * FROM system_views.thread_pools;        -- tpstats
    SELECT * FROM system_views.sstable_tasks;       -- compactionstats
    SELECT * FROM system_views.clients;             -- clientstats
    ```

### Understanding Node States

```
nodetool status output:

Datacenter: dc1
===============
Status=Up/Down
|/ State=Normal/Leaving/Joining/Moving
--  Address       Load       Tokens  Owns    Host ID
UN  10.0.0.1     125.4 GB   256     25.2%   abc123...
UN  10.0.0.2     118.9 GB   256     24.8%   def456...
UN  10.0.0.3     122.1 GB   256     25.0%   ghi789...
DN  10.0.0.4     0 bytes    256     25.0%   jkl012...  ← Problem!

Status letters:
  U = Up (node is online)
  D = Down (node is offline)

State letters:
  N = Normal (healthy, serving requests)
  L = Leaving (decommissioning)
  J = Joining (bootstrapping)
  M = Moving (rebalancing tokens)
```

### Red Flags to Watch For

!!! danger "Critical — Take Immediate Action"
    - Any node showing DN (Down Normal) state
    - Schema disagreement in `describecluster`
    - Blocked thread pools in `tpstats`
    - Dropped messages > 0 in `tpstats`
    - Pending compactions > 100 (or growing continuously)
    - Disk usage > 80% on any node
    - Heap usage consistently > 85%

!!! warning "Warning — Investigate Within 24 Hours"
    - Uneven load distribution (> 20% variance between nodes)
    - Pending compactions > 20
    - Read latency p99 > 100ms
    - Hints growing on any node
    - GC pause times > 500ms

---

## Daily Health Check Script

Run this script daily (or automate it):

```bash
#!/bin/bash
# daily_health_check.sh

LOG_FILE="/var/log/cassandra/health_$(date +%Y%m%d).log"

echo "=== Cassandra Health Check: $(date) ===" | tee -a ${LOG_FILE}

# 1. Cluster Status
echo -e "\n--- Cluster Status ---" | tee -a ${LOG_FILE}
STATUS=$(nodetool status 2>&1)
echo "${STATUS}" | tee -a ${LOG_FILE}

# Check for down nodes
if echo "${STATUS}" | grep -q "^DN"; then
    echo "CRITICAL: Down nodes detected!" | tee -a ${LOG_FILE}
fi

# 2. Schema Agreement
echo -e "\n--- Schema Agreement ---" | tee -a ${LOG_FILE}
SCHEMA=$(nodetool describecluster 2>&1 | grep -A5 "Schema versions")
echo "${SCHEMA}" | tee -a ${LOG_FILE}

SCHEMA_COUNT=$(echo "${SCHEMA}" | grep -c "\[")
if [ ${SCHEMA_COUNT} -gt 1 ]; then
    echo "WARNING: Schema disagreement detected!" | tee -a ${LOG_FILE}
fi

# 3. Thread Pools
echo -e "\n--- Thread Pool Status ---" | tee -a ${LOG_FILE}
TPSTATS=$(nodetool tpstats 2>&1)
echo "${TPSTATS}" | head -20 | tee -a ${LOG_FILE}

# Check for blocked pools
if echo "${TPSTATS}" | grep -E "Blocked.*[1-9]"; then
    echo "CRITICAL: Blocked thread pools!" | tee -a ${LOG_FILE}
fi

# Check for dropped messages
DROPPED=$(echo "${TPSTATS}" | grep -E "Dropped" | awk '{sum += $NF} END {print sum}')
if [ "${DROPPED}" -gt 0 ]; then
    echo "WARNING: ${DROPPED} dropped messages detected!" | tee -a ${LOG_FILE}
fi

# 4. Compaction
echo -e "\n--- Compaction Status ---" | tee -a ${LOG_FILE}
COMPACTION=$(nodetool compactionstats 2>&1)
echo "${COMPACTION}" | head -5 | tee -a ${LOG_FILE}

PENDING=$(echo "${COMPACTION}" | grep "pending tasks" | awk '{print $3}')
if [ "${PENDING}" -gt 50 ]; then
    echo "WARNING: High pending compactions (${PENDING})" | tee -a ${LOG_FILE}
fi

# 5. Disk Usage
echo -e "\n--- Disk Usage ---" | tee -a ${LOG_FILE}
DISK=$(df -h /var/lib/cassandra 2>&1)
echo "${DISK}" | tee -a ${LOG_FILE}

DISK_PERCENT=$(df /var/lib/cassandra | tail -1 | awk '{print $5}' | tr -d '%')
if [ ${DISK_PERCENT} -gt 80 ]; then
    echo "CRITICAL: Disk usage at ${DISK_PERCENT}%!" | tee -a ${LOG_FILE}
fi

# 6. Recent Errors
echo -e "\n--- Recent Errors (last 100 lines) ---" | tee -a ${LOG_FILE}
ERROR_COUNT=$(grep -c -i "error\|exception\|warn" /var/log/cassandra/system.log | tail -100)
echo "Errors/Warnings in recent logs: ${ERROR_COUNT}" | tee -a ${LOG_FILE}

# 7. Summary
echo -e "\n=== Health Check Complete ===" | tee -a ${LOG_FILE}
```

---

## Operations Quick Reference

### Cluster Management

```bash
# Add a new node
# 1. Install Cassandra on new node
# 2. Configure cassandra.yaml (same cluster_name, seeds pointing to existing nodes)
# 3. Start Cassandra - it will automatically bootstrap
sudo systemctl start cassandra

# Monitor bootstrap progress
nodetool netstats

# After bootstrap, run cleanup on existing nodes
# This removes data they no longer own
for node in existing_nodes; do
    ssh $node "nodetool cleanup"
done

# Remove a node (graceful - node is running)
nodetool decommission

# Remove a node (dead - node is not running)
nodetool removenode <host_id>

# Replace a dead node
# Add to JVM options on new node:
# -Dcassandra.replace_address_first_boot=<dead_node_ip>
# Then start Cassandra
```

### Backup Operations

```bash
# Take a snapshot (point-in-time backup)
nodetool flush                                    # Flush memtables first
nodetool snapshot -t backup_$(date +%Y%m%d)      # Create snapshot

# List snapshots
nodetool listsnapshots

# Clear old snapshots
nodetool clearsnapshot -t old_backup_name

# Snapshot location
# /var/lib/cassandra/data/<keyspace>/<table>/snapshots/<snapshot_name>/
```

### Repair Operations

```bash
# Primary range repair (recommended for routine maintenance)
nodetool repair -pr my_keyspace

# Repair specific table
nodetool repair -pr my_keyspace my_table

# Full repair (after disaster recovery)
nodetool repair -full my_keyspace

# Check repair progress
nodetool netstats | grep -i repair

# Cancel stuck repair
nodetool repair_admin list
nodetool repair_admin cancel <repair_id>
```

### Maintenance Operations

```bash
# Rolling restart (on each node)
nodetool drain                        # Stop accepting writes, flush
sudo systemctl stop cassandra         # Stop the service
sudo systemctl start cassandra        # Start the service

# Cleanup (after topology changes)
nodetool cleanup my_keyspace

# Force compaction (use sparingly)
nodetool compact my_keyspace my_table

# Refresh SSTables (after manually copying files)
nodetool refresh my_keyspace my_table
```

---

## Repair: Preventing Data Inconsistency

Repair is the most important maintenance operation. Without regular repair, clusters develop inconsistencies and eventually lose data.

### Why Repair Is Essential

```
Scenario: Write to node that goes down before replication completes
─────────────────────────────────────────────────────────────────────────────

Time T0: Client writes row with RF=3
         Coordinator → Node A (success)
                    → Node B (success)
                    → Node C (fails - network issue)

         Result: Row exists on A, B, but NOT on C

Time T1 to T7: No repair runs, reads happen to hit A or B
               Data looks consistent to clients

Time T8: Node A disk fails, replaced
         New A bootstraps from B and C
         Row missing on C, so new A does not receive it

Time T9: Node B fails
         Row is now LOST - only existed on original A and B

Without repair: Data was silently lost
With repair: Inconsistency would have been detected and fixed at T1
```

### Repair and Tombstones (Zombie Data)

```
The gc_grace_seconds Problem:
─────────────────────────────────────────────────────────────────────────────

gc_grace_seconds default: 864000 (10 days)

This setting controls when tombstones (delete markers) can be purged.
If repair does not run within gc_grace_seconds:

Time T0:  DELETE row WHERE id = 123
          Tombstone created on Nodes A, B
          Node C was down, didn't get tombstone

Time T5:  Node C comes back online
          Still has the original row (no tombstone)

Time T11: gc_grace_seconds expires
          Nodes A, B purge tombstone during compaction

Time T12: Read repair or repair runs
          Node C's "live" row is propagated to A, B
          DELETED DATA HAS RESURRECTED!

Rule: Complete repair on all nodes within gc_grace_seconds
```

### Repair Scheduling

| Cluster Size | Repair Frequency | Strategy |
|--------------|------------------|----------|
| 3-6 nodes | Weekly | Sequential on each node |
| 6-20 nodes | Every 3-4 days | Parallel/sequential mix |
| 20-50 nodes | Daily subrange | Break into token ranges |
| 50+ nodes | Continuous | Use automated tools |

---

## Backup: Protecting Against Data Loss

### Backup Strategy Matrix

| Strategy | RPO | Complexity | Storage Cost |
|----------|-----|------------|--------------|
| Daily snapshots | 24 hours | Low | High |
| Snapshot + incremental | 1-4 hours | Medium | Medium |
| Snapshot + commit log | Minutes | High | Medium |
| Continuous replication | Seconds | High | High (2x) |

RPO = Recovery Point Objective (maximum data loss acceptable)

### What to Back Up

```
Essential:
─────────────────────────────────────────────────────────────────────────────
✓ SSTables (data files)           → /var/lib/cassandra/data/
✓ Schema                          → cqlsh -e "DESC SCHEMA"
✓ Cassandra configuration         → /etc/cassandra/

Recommended:
─────────────────────────────────────────────────────────────────────────────
✓ JVM options                     → /etc/cassandra/jvm*.options
✓ System keyspace (if needed)     → system_schema, system_auth

NOT needed in backup:
─────────────────────────────────────────────────────────────────────────────
✗ Commit logs                     → Unless doing PITR
✗ Saved caches                    → Rebuilt automatically
✗ Hints                           → Transient
```

### Backup Verification Checklist

```bash
# Monthly: Verify backup restores correctly

1. [ ] Restore backup to staging cluster
2. [ ] Verify schema was restored
3. [ ] Run application queries against restored data
4. [ ] Compare row counts between production and restored
5. [ ] Test point-in-time recovery (if using commit log archiving)
6. [ ] Document restore time (for RTO planning)
7. [ ] Update restore runbook if procedures changed
```

---

## Capacity Planning

### Disk Space Planning

```
Disk Space Formula:
─────────────────────────────────────────────────────────────────────────────

Required = (Raw Data × RF × Compaction Overhead × Growth Buffer) / Nodes

Where:
- Raw Data = Your actual data size
- RF = Replication Factor (typically 3)
- Compaction Overhead = 1.5 (STCS) or 1.1 (LCS)
- Growth Buffer = 1.5 (50% headroom for compaction + growth)

Example:
- Raw Data: 500 GB
- RF: 3
- Compaction: STCS (1.5x)
- Buffer: 1.5x
- Nodes: 6

Required per node = (500 × 3 × 1.5 × 1.5) / 6 = 562.5 GB

Recommendation: 1TB per node
```

### When to Add Nodes

Add capacity when any of these thresholds approach:

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Disk usage | 60% | 75% | Add nodes or disk |
| CPU usage | 70% sustained | 85% sustained | Add nodes |
| Read latency p99 | 50ms | 100ms | Investigate, possibly add nodes |
| Write latency p99 | 20ms | 50ms | Investigate, possibly add nodes |
| Pending compactions | 20 sustained | 50 sustained | Add disk throughput or nodes |

---

## Emergency Procedures

### Node Won't Start

```bash
# 1. Check logs
tail -500 /var/log/cassandra/system.log | grep -i "error\|exception"

# 2. Common causes and fixes

# OOM killer?
dmesg | grep -i "killed process"
→ Fix: Increase heap or add RAM

# Commit log corruption?
grep -i "corrupt" /var/log/cassandra/system.log
→ Fix: Move corrupted commit logs (DATA LOSS!)
→ mv /var/lib/cassandra/commitlog/* /var/lib/cassandra/commitlog_bad/

# SSTable corruption?
grep -i "sstable" /var/log/cassandra/system.log | grep -i "error"
→ Fix: nodetool scrub (after node starts) or sstablescrub

# Disk full?
df -h /var/lib/cassandra
→ Fix: Clear snapshots, delete old logs, add disk

# Permissions?
ls -la /var/lib/cassandra
→ Fix: chown -R cassandra:cassandra /var/lib/cassandra
```

### Cluster Split Brain

```bash
# Symptoms: Different nodes see different cluster membership

# 1. Check gossip on each node
nodetool gossipinfo

# 2. Check for network partition
# From each node, test connectivity to others
for node in 10.0.0.1 10.0.0.2 10.0.0.3; do
    nc -zv $node 7000  # Inter-node
    nc -zv $node 9042  # CQL
done

# 3. Resolution
# - Fix network issues
# - If necessary, restart nodes one at a time
# - Run repair after cluster stabilizes
```

### Schema Disagreement

```bash
# Check schema versions
nodetool describecluster

# If multiple versions:
# 1. Identify which node(s) have wrong schema
# 2. Try restarting the affected node
# 3. If persists, reset local schema (LAST RESORT):
nodetool resetlocalschema

# Prevention: Ensure DDL runs on single node, wait for propagation
```

---

## Documentation Sections

### [Cluster Management](cluster-management/index.md)
- Adding nodes to expand capacity
- Removing nodes (decommission)
- Replacing failed nodes
- Topology changes (rack/DC)

### [Backup & Restore](backup-restore/index.md)
- Snapshot procedures
- Incremental backups
- Point-in-time recovery
- Restore procedures

### [Repair](repair/index.md)
- Repair types and strategies
- Scheduling repair
- Troubleshooting repair
- Automation tools

### [Compaction Management](compaction-management/index.md)
- Compaction configuration
- Strategy selection and tuning
- Troubleshooting compaction issues

### [Maintenance](maintenance/index.md)
- Rolling restarts
- Schema management
- Cleanup operations
- Upgrade procedures

### [Monitoring](monitoring/index.md)
- Critical metrics to monitor
- JMX metrics reference
- Alert configuration
- Dashboard design

### [Virtual Tables](virtual-tables/index.md)
- Query internal state via CQL
- Metrics, caches, and thread pools
- Repair tracking
- Client connections and cluster state

### [Performance](performance/index.md)
- Read/write optimization
- JVM and GC tuning
- Compaction tuning
- Hardware sizing

### [Troubleshooting](troubleshooting/index.md)
- Node issues
- Performance issues
- Cluster issues
- Emergency procedures

---

## Key Metrics to Monitor

| Metric | Warning | Critical | Source |
|--------|---------|----------|--------|
| Node state | Any DN | Multiple DN | `nodetool status`, `system_views.gossip_info` |
| Heap usage | >75% | >85% | JMX/metrics |
| Disk usage | >60% | >80% | `df -h`, `system_views.disk_usage` |
| Pending compactions | >20 | >50 | `nodetool compactionstats`, `system_views.sstable_tasks` |
| Dropped messages | Any | Growing | `nodetool tpstats`, `system_views.thread_pools` |
| Read latency p99 | >50ms | >100ms | JMX/metrics, `system_views.coordinator_read_latency` |
| Write latency p99 | >20ms | >50ms | JMX/metrics, `system_views.coordinator_write_latency` |
| GC pause time | >500ms | >1s | GC logs |
| Tombstones per read | >100 p99 | >1000 p99 | `system_views.tombstones_per_read` |
| Cache hit ratio | <80% | <60% | `system_views.caches` |

---

## AxonOps Operations Platform

Operating Cassandra at scale requires coordinating multiple tools, scripts, and processes across nodes. [AxonOps](https://axonops.com) provides an integrated operations platform designed specifically for Cassandra.

### Unified Operations Console

AxonOps provides:

- **Single-pane-of-glass**: All cluster metrics, logs, and operations in one interface
- **Multi-cluster management**: Manage multiple Cassandra clusters from a single console
- **Role-based access control**: Define who can view, operate, or administer clusters
- **Audit logging**: Complete history of all operational actions

### Automated Maintenance

- **Scheduled repairs**: Intelligent repair scheduling that minimizes impact
- **Automated backups**: Policy-driven backup with multiple storage backends
- **Rolling operations**: Coordinated rolling restarts and upgrades across nodes
- **Cleanup automation**: Post-topology-change cleanup orchestration

### Proactive Monitoring

- **Pre-configured alerts**: Out-of-the-box alerts for common issues
- **Trend analysis**: Identify gradual degradation before failures
- **Capacity forecasting**: Predict when resources will be exhausted
- **Anomaly detection**: ML-based detection of unusual patterns

### Operational Workflows

- **Guided procedures**: Step-by-step wizards for complex operations
- **Pre-flight checks**: Automatic validation before operations
- **Rollback support**: Quick recovery from failed operations
- **Runbook integration**: Link alerts to resolution procedures

See the [AxonOps documentation](../../../get_started/cloud.md) for setup and configuration.

---

## Next Steps

- **[Cluster Management](cluster-management/index.md)** - Node lifecycle operations
- **[Backup & Restore](backup-restore/index.md)** - Data protection procedures
- **[Repair](repair/index.md)** - Maintain consistency
- **[Maintenance](maintenance/index.md)** - Day-to-day upkeep
- **[Monitoring](monitoring/index.md)** - Observability setup
- **[Performance](performance/index.md)** - Optimization procedures
- **[Troubleshooting](troubleshooting/index.md)** - Problem resolution