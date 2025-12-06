# Cassandra Repair Guide

Repair is how Cassandra fixes inconsistencies between replicas. When a node misses writes (because it was down, or a network partition occurred), repair brings it back in sync with the other replicas.

The critical constraint: repair must complete on every node within `gc_grace_seconds` (default 10 days). Here is why—when data is deleted, Cassandra writes a tombstone. After `gc_grace_seconds`, that tombstone gets garbage collected. If a replica missed the delete and has not been repaired before the tombstone disappears, the old data comes back. This is called "zombie data," and it is a real problem.

This guide covers repair types, scheduling strategies, and how to monitor repair progress.

## Why Repair is Needed

### Data Inconsistency Sources

```
Inconsistency can occur when:
1. Node was down during writes
2. Hints expired (> max_hint_window)
3. Network partition occurred
4. Hinted handoff was disabled
5. Read repair has not run
```

### Repair and gc_grace_seconds

```
Critical relationship:
- gc_grace_seconds = 10 days (default)
- Tombstones can be removed after gc_grace_seconds
- If repair does not run within gc_grace_seconds:
  → Deleted data can resurrect ("zombie data")

Rule: Complete repair on all nodes within gc_grace_seconds
```

---

## Repair Types

### Full Repair vs Incremental Repair

| Feature | Full Repair | Incremental Repair |
|---------|-------------|-------------------|
| Scope | All data | Only unrepaired data |
| Resource usage | Higher | Lower |
| Duration | Longer | Shorter |
| Complexity | Simpler | Tracks repaired state |
| Default (4.0+) | No | Yes |

### Primary Range Repair (-pr)

```bash
# Repairs only data owned by this node
nodetool repair -pr my_keyspace

# Recommended for routine maintenance
# Run on each node to repair entire cluster
```

### Full Repair (-full)

```bash
# Repairs all data this node has a copy of
nodetool repair -full my_keyspace

# More thorough but causes redundant repairs
# Use for: disaster recovery, cluster restoration
```

---

## Running Repair

### Basic Commands

```bash
# Incremental repair (default, 4.0+)
nodetool repair my_keyspace

# Primary range only (recommended)
nodetool repair -pr my_keyspace

# Specific table
nodetool repair -pr my_keyspace my_table

# Full repair
nodetool repair -full my_keyspace

# Parallel repair (multiple token ranges simultaneously)
nodetool repair -pr --parallel my_keyspace

# Sequential repair (one token range at a time)
nodetool repair -pr --sequential my_keyspace
```

### Repair Options

```bash
# Data center aware (repair within DC)
nodetool repair -pr -dc datacenter1 my_keyspace

# Partition range
nodetool repair -pr -st <start_token> -et <end_token> my_keyspace

# Number of parallel jobs
nodetool repair -pr -j 4 my_keyspace

# Trace repair (verbose)
nodetool repair -pr --trace my_keyspace

# Preview repair (show what would be repaired)
nodetool repair -pr --preview my_keyspace
```

### Check Repair Status

```bash
# During repair
nodetool netstats | grep -i repair

# Check pending repair sessions
nodetool repair_admin list

# Cancel stuck repair
nodetool repair_admin cancel <repair_id>
```

---

## Repair Strategies

### Strategy 1: Sequential Repair (Conservative)

```bash
#!/bin/bash
# sequential_repair.sh
# Run on each node, one at a time

KEYSPACE="my_keyspace"

echo "Starting repair on $(hostname)"

for table in $(cqlsh -e "DESC KEYSPACE ${KEYSPACE}" | grep "CREATE TABLE" | awk '{print $3}'); do
    echo "Repairing table: ${table}"
    nodetool repair -pr ${KEYSPACE} ${table}
    if [ $? -ne 0 ]; then
        echo "ERROR: Repair failed for ${table}"
        exit 1
    fi
done

echo "Repair complete on $(hostname)"
```

**Schedule**: Run on one node at a time, complete cluster within gc_grace_seconds

### Strategy 2: Parallel Repair (Faster)

```bash
#!/bin/bash
# parallel_repair.sh
# Runs repair across multiple token ranges in parallel

KEYSPACE="my_keyspace"

nodetool repair -pr --parallel ${KEYSPACE}
```

**Schedule**: More aggressive, uses more resources

### Strategy 3: Subrange Repair (Large Clusters)

```bash
#!/bin/bash
# subrange_repair.sh
# Breaks repair into smaller chunks

KEYSPACE="my_keyspace"
RANGES=32  # Number of subranges

# Get token ranges for this node
ranges=$(nodetool describering ${KEYSPACE} | grep -E "^\s+start_token" | awk '{print $2}')

# Repair each subrange
for range in ${ranges}; do
    # Calculate subrange boundaries
    # ... (implementation depends on partitioner)
    nodetool repair -pr -st ${start} -et ${end} ${KEYSPACE}
done
```

---

## Automated Repair

### Using cron

```bash
# /etc/cron.d/cassandra-repair
# Repair on different nodes at different times

# Node 1 - Monday
0 2 * * 1 cassandra /opt/cassandra/scripts/repair.sh my_keyspace >> /var/log/cassandra/repair.log 2>&1

# Node 2 - Tuesday
0 2 * * 2 cassandra /opt/cassandra/scripts/repair.sh my_keyspace >> /var/log/cassandra/repair.log 2>&1

# Node 3 - Wednesday
0 2 * * 3 cassandra /opt/cassandra/scripts/repair.sh my_keyspace >> /var/log/cassandra/repair.log 2>&1
```

### Using systemd Timer

```ini
# /etc/systemd/system/cassandra-repair.timer
[Unit]
Description=Weekly Cassandra Repair

[Timer]
OnCalendar=Mon 02:00
Persistent=true

[Install]
WantedBy=timers.target
```

```ini
# /etc/systemd/system/cassandra-repair.service
[Unit]
Description=Cassandra Repair

[Service]
Type=oneshot
User=cassandra
ExecStart=/opt/cassandra/scripts/repair.sh my_keyspace
```

### Using AxonOps

AxonOps provides automated repair scheduling with:
- Intelligent scheduling across nodes
- Progress monitoring
- Automatic retry on failure
- Repair history and reporting

---

## Repair Scheduling Guidelines

### Cluster Size vs Repair Frequency

| Cluster Size | Repair Frequency | Strategy |
|--------------|------------------|----------|
| 3-6 nodes | Weekly | Sequential |
| 6-20 nodes | 2-3x per week | Parallel |
| 20-50 nodes | Daily subrange | Subrange |
| 50+ nodes | Continuous | Tool-assisted |

### Calculating Repair Schedule

```
gc_grace_seconds = 864000 (10 days)
Number of nodes = N
Time per node repair = T

Schedule: T × N < gc_grace_seconds

Example:
- 6 nodes
- 4 hours per node repair
- Total = 24 hours
- Plenty of buffer within 10 days
- Can run weekly
```

### Off-Peak Scheduling

```
Recommendations:
- Run during lowest traffic periods
- Avoid running with other intensive operations
- Stagger repairs across nodes
- Monitor impact on latency
```

---

## Monitoring Repair

### During Repair

```bash
# Check progress
nodetool netstats | grep -i repair

# Sample output:
# Repair command #1234567 (src/dst, repair_id):
#     Range 0:100% complete
#     Range 1:45% complete

# Check thread pools
nodetool tpstats | grep -E "Pool|AntiEntropy"

# Check compaction (repair triggers compaction)
nodetool compactionstats
```

### Repair Metrics

```
JMX metrics to monitor:
- org.apache.cassandra.metrics:type=Repair,name=PercentRepaired
- org.apache.cassandra.metrics:type=Storage,name=TotalHints
- org.apache.cassandra.metrics:type=AntiEntropyStage
```

### Post-Repair Verification

```bash
# Check percent repaired
nodetool tablestats my_keyspace.my_table | grep -i repaired

# Example output:
# Percent repaired: 95.5%

# Should be close to 100% after full repair cycle
```

---

## Troubleshooting Repair

### Repair Hangs or Times Out

```bash
# Check for stuck sessions
nodetool repair_admin list

# Cancel stuck repair
nodetool repair_admin cancel <repair_id>

# Check network connectivity
ping <other_node>
nc -zv <other_node> 7000

# Check system resources
iostat -xz 1 5
top -b -n 1 | head -20
```

### Repair Fails

```bash
# Check logs for errors
grep -i repair /var/log/cassandra/system.log | tail -100

# Common issues:
# - Network timeout: Increase streaming_socket_timeout_in_ms
# - Disk full: Free up space
# - OOM: Reduce repair parallelism
# - Validation failure: SSTable corruption
```

### High Repair Impact

```bash
# Reduce compaction throughput during repair
nodetool setcompactionthroughput 32

# Reduce streaming throughput
nodetool setstreamthroughput 100

# Use sequential repair
nodetool repair -pr --sequential my_keyspace

# Repair during off-peak hours
```

### Repair Never Completes

```
Causes:
1. Cluster too large for repair to complete in time
2. Node failures during repair
3. High write volume invalidating repaired data
4. Resource contention

Solutions:
1. Use subrange repair
2. Automated repair tool (AxonOps, Reaper)
3. Schedule repairs during low traffic
4. Increase resources or reduce repair parallelism
```

---

## Repair Best Practices

### Do's

```
✓ Run repair regularly (within gc_grace_seconds)
✓ Use -pr flag for routine maintenance
✓ Schedule repairs during off-peak hours
✓ Monitor repair progress and completion
✓ Test repair procedures in staging
✓ Document repair schedule and procedures
✓ Use automated repair management tools
```

### Don'ts

```
✗ Skip repair for extended periods
✗ Run repair on all nodes simultaneously
✗ Run repair during traffic spikes
✗ Ignore repair failures
✗ Forget about repair after adding nodes
✗ Reduce gc_grace_seconds without faster repair cycles
```

### After Topology Changes

```bash
# After adding nodes
# 1. Run cleanup on existing nodes
nodetool cleanup my_keyspace

# 2. Run repair to redistribute data
nodetool repair -pr my_keyspace

# After removing nodes
# 1. Ensure decommission completed
nodetool status

# 2. Run repair to ensure consistency
nodetool repair -pr my_keyspace
```

---

## Repair Configuration

### cassandra.yaml Settings

```yaml
# Repair session timeout
repair_session_max_tree_depth: 20

# Validation preview
enable_materialized_views: false  # If views are problematic

# Repair parallelism (Cassandra 4.0+)
repair_session_space_in_mb: 256  # Memory for repair sessions
```

### Runtime Adjustments

```bash
# Set compaction throttle during repair
nodetool setcompactionthroughput 32

# Set stream throttle
nodetool setstreamthroughput 100

# Disable autocompaction during repair (advanced)
nodetool disableautocompaction my_keyspace my_table
# Re-enable after repair
nodetool enableautocompaction my_keyspace my_table
```

---

## Repair Tools

### Apache Cassandra Reaper

Open-source repair scheduler and manager.

```bash
# Web UI at http://localhost:8080
# Features:
# - Scheduled repairs
# - Segment-based repair
# - Multi-datacenter awareness
# - Repair history
```

### AxonOps

Enterprise repair management with:
- Automatic scheduling
- Adaptive repair strategies
- Cluster-wide coordination
- Alerting and reporting

### Custom Scripts

```bash
#!/bin/bash
# repair_with_monitoring.sh

KEYSPACE=$1
LOG_FILE="/var/log/cassandra/repair_$(date +%Y%m%d).log"

echo "Starting repair: $(date)" >> ${LOG_FILE}

# Pre-repair checks
echo "Pre-repair status:" >> ${LOG_FILE}
nodetool status >> ${LOG_FILE}
nodetool tpstats | head -20 >> ${LOG_FILE}

# Run repair
nodetool repair -pr ${KEYSPACE} 2>&1 | tee -a ${LOG_FILE}
RESULT=$?

# Post-repair status
echo "Post-repair status:" >> ${LOG_FILE}
nodetool tablestats ${KEYSPACE} | grep -i repaired >> ${LOG_FILE}

if [ ${RESULT} -eq 0 ]; then
    echo "Repair completed successfully: $(date)" >> ${LOG_FILE}
else
    echo "Repair FAILED: $(date)" >> ${LOG_FILE}
    # Send alert
    # mail -s "Cassandra Repair Failed" ops@example.com < ${LOG_FILE}
fi
```

---

## Next Steps

- **[Operations Guide](../index.md)** - Cluster operations
- **[Backup Guide](../backup-restore/index.md)** - Backup procedures
- **[Troubleshooting](../../troubleshooting/index.md)** - Problem resolution
- **[Monitoring](../../monitoring/index.md)** - Repair monitoring
