---
title: "Cassandra Compaction Management"
description: "Cassandra compaction management. Strategies, tuning, and monitoring compaction."
meta:
  - name: keywords
    content: "Cassandra compaction, compaction strategies, STCS, LCS, TWCS"
---

# Compaction Management

This document covers compaction configuration, tuning, strategy changes, and troubleshooting procedures.

## Configuration

### Global Settings

```yaml
# cassandra.yaml

# Maximum compaction throughput per node (MB/s)
# Higher = faster compaction, more disk I/O competition
# 0 = unlimited (not recommended)
compaction_throughput_mb_per_sec: 64

# Number of concurrent compaction threads
# Default: min(4, number_of_disks)
concurrent_compactors: 4

# Compaction large partition warning threshold
compaction_large_partition_warning_threshold_mb: 100
```
  
### Runtime Adjustments

```bash
# Adjust compaction throughput (MB/s)
nodetool setcompactionthroughput 128
nodetool getcompactionthroughput

# Adjust concurrent compactors
nodetool setconcurrentcompactors 4
nodetool getconcurrentcompactors
```

### Per-Table Settings

```sql
-- View current compaction settings
SELECT compaction FROM system_schema.tables
WHERE keyspace_name = 'my_keyspace' AND table_name = 'my_table';

-- Modify compaction settings
ALTER TABLE my_keyspace.my_table WITH compaction = {
    'class': 'LeveledCompactionStrategy',
    'sstable_size_in_mb': 160
};
```

---

## Monitoring

### nodetool Commands

```bash
# Current compaction activity
nodetool compactionstats

# Sample output:
# pending tasks: 5
# compactions completed: 1234
#    id   compaction type   keyspace   table   completed   total      unit
# abc123  Compaction        my_ks      users   1073741824  2147483648  bytes

# Per-table statistics
nodetool tablestats keyspace.table

# Key fields:
# - SSTable count
# - Space used (live)
# - Space used (total)
# - Compacted partition maximum bytes

# Compaction history
nodetool compactionhistory

# SSTable distribution for LCS
nodetool tablestats keyspace.table | grep "SSTables in each level"
```

### JMX Metrics

```
# Pending compaction tasks
org.apache.cassandra.metrics:type=Compaction,name=PendingTasks

# Compaction throughput
org.apache.cassandra.metrics:type=Compaction,name=BytesCompacted

# Per-table metrics
org.apache.cassandra.metrics:type=Table,keyspace=*,scope=*,name=LiveSSTableCount
org.apache.cassandra.metrics:type=Table,keyspace=*,scope=*,name=PendingCompactions
org.apache.cassandra.metrics:type=Table,keyspace=*,scope=*,name=TotalDiskSpaceUsed

# LCS-specific
org.apache.cassandra.metrics:type=Table,keyspace=*,scope=*,name=SSTablesPerLevel
```

### Alerting Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Pending compactions | >50 | >200 |
| SSTable count (STCS) | >20 | >50 |
| L0 count (LCS) | >8 | >32 |
| Disk free | <30% | <20% |

---

## Manual Operations

### Forcing Compaction

```bash
# Compact specific table
nodetool compact keyspace table

# Compact all tables in keyspace
nodetool compact keyspace

# Compact specific SSTables (user-defined compaction)
nodetool compact --user-defined /path/to/sstable-Data.db
```

**When to force compaction:**

- After bulk data load
- After many deletes to reclaim space
- Before taking snapshots (smaller snapshot size)
- During maintenance windows to reduce SSTable count

**When NOT to force compaction:**

- During normal production operations
- When disk space is low (compaction needs temporary space)
- On write-heavy tables (compaction will fall behind again)

### Stopping Compaction

```bash
# Stop all compactions (emergency only)
nodetool stop COMPACTION

# Stop specific compaction types
nodetool stop COMPACTION --compaction-id <id>
```

**Warning:** Stopping compaction leaves partial results. Only use in emergencies.

### Enable/Disable Auto-Compaction

```bash
# Disable auto-compaction (maintenance only)
nodetool disableautocompaction keyspace table

# Re-enable auto-compaction
nodetool enableautocompaction keyspace table

# Check status
nodetool tablestats keyspace.table | grep "Compaction"
```

**Use cases for disabling:**

- During bulk loads
- During schema migrations
- Troubleshooting compaction issues

**Always re-enable** after maintenance completes.

---

## Changing Strategies

### Strategy Switch Commands

```sql
-- Switch from STCS to LCS
ALTER TABLE keyspace.table WITH compaction = {
    'class': 'LeveledCompactionStrategy',
    'sstable_size_in_mb': 160
};

-- Switch from LCS to STCS
ALTER TABLE keyspace.table WITH compaction = {
    'class': 'SizeTieredCompactionStrategy',
    'min_threshold': 4
};

-- Switch to TWCS
ALTER TABLE keyspace.table WITH compaction = {
    'class': 'TimeWindowCompactionStrategy',
    'compaction_window_unit': 'HOURS',
    'compaction_window_size': 1
};

-- Switch to UCS (Cassandra 5.0+)
ALTER TABLE keyspace.table WITH compaction = {
    'class': 'UnifiedCompactionStrategy',
    'scaling_parameters': 'T4'
};
```

### What Happens During Strategy Change

```
1. New strategy takes effect immediately
2. Existing SSTables are NOT rewritten
3. New compactions follow new strategy rules
4. Gradual migration as old SSTables compact
```

### Strategy-Specific Transitions

**STCS → LCS:**

- Old SSTables treated as L0
- May cause temporary L0 backlog
- Monitor L0 count closely

```bash
watch 'nodetool tablestats keyspace.table | grep "SSTables in each level"'
```

**LCS → STCS:**

- Levels are ignored
- SSTables grouped by size
- Generally smooth transition

**Any → TWCS:**

- Old data grouped into "old" window
- Only new data gets proper windowing
- May need time for full benefit

### Migration Best Practices

1. **Test in non-production first**
2. **Check disk space**: Strategy change may trigger compaction
3. **Time appropriately**: Execute during low-traffic period
4. **Monitor closely**: Watch pending compactions and latency
5. **Have rollback plan**: Know how to switch back

```bash
# Pre-change checklist
nodetool tablestats keyspace.table  # Current state
df -h /var/lib/cassandra/data       # Disk space
nodetool compactionstats            # Current activity

# During change
watch 'nodetool compactionstats && nodetool tablestats keyspace.table | head -30'

# Post-change verification
nodetool tablestats keyspace.table | grep -E "SSTable|Space|Compaction"
```

---

## Troubleshooting

### Problem: Compaction Cannot Keep Up

**Symptoms:**

- Pending compaction tasks growing continuously
- SSTable count increasing
- Read latency increasing

**Diagnosis:**

```bash
nodetool compactionstats
# pending tasks: 150 (and growing)

nodetool tpstats | grep -i compact
# Check for blocked tasks

iostat -x 1
# Check disk utilization
```

**Solutions:**

1. Increase compaction throughput:
   ```bash
   nodetool setcompactionthroughput 128
   ```

2. Add concurrent compactors:
   ```bash
   nodetool setconcurrentcompactors 4
   ```

3. Reduce write rate temporarily

4. Check for large partitions:
   ```bash
   nodetool tablestats keyspace.table | grep "Compacted partition maximum"
   ```

5. Consider strategy change (STCS for write-heavy workloads)

### Problem: High Write Amplification

**Symptoms:**

- Disk throughput at 100%
- High iowait
- Write latency increasing
- SSD wearing faster than expected

**Diagnosis:**

```bash
iostat -x 1
# %util approaching 100%

nodetool tablestats keyspace.table
# Compare write counts to actual client writes
```

**Solutions:**

1. Switch from LCS to STCS:
   ```sql
   ALTER TABLE keyspace.table WITH compaction = {
       'class': 'SizeTieredCompactionStrategy'
   };
   ```

2. Increase LCS SSTable size:
   ```sql
   ALTER TABLE keyspace.table WITH compaction = {
       'class': 'LeveledCompactionStrategy',
       'sstable_size_in_mb': 256
   };
   ```

3. Throttle compaction:
   ```bash
   nodetool setcompactionthroughput 32
   ```

### Problem: Space Not Being Reclaimed

**Symptoms:**

- Disk usage growing despite TTL or deletes
- Tombstones not being removed

**Diagnosis:**

```bash
# Check gc_grace_seconds
cqlsh -e "SELECT gc_grace_seconds FROM system_schema.tables
          WHERE keyspace_name='keyspace' AND table_name='table';"

# Check tombstone counts
nodetool tablestats keyspace.table | grep -i tombstone

# Check last repair
nodetool repair_admin list
```

**Causes and Solutions:**

| Cause | Solution |
|-------|----------|
| gc_grace_seconds not passed | Wait, or reduce if repair is frequent |
| Tombstones in different SSTables than data | Run major compaction |
| Repair not running | Run repair before reducing gc_grace |
| TWCS with out-of-order writes | Fix data pipeline |

### Problem: Large Partition Blocking Compaction

**Symptoms:**

- Compaction stuck at same percentage
- One SSTable significantly larger than expected
- "Compacting large partition" in logs

**Diagnosis:**

```bash
grep "Compacting large partition" /var/log/cassandra/system.log

nodetool tablestats keyspace.table | grep -i "maximum"
# Compacted partition maximum bytes: 2147483648
```

**Solutions:**

1. Fix data model:
   ```sql
   -- Add time bucket to partition key
   PRIMARY KEY ((user_id, date_bucket), event_time)
   ```

2. Increase warning threshold:
   ```
   # jvm.options
   -Dcassandra.compaction.large_partition_warning_threshold_mb=1000
   ```

3. For LCS, increase SSTable size:
   ```sql
   ALTER TABLE keyspace.table WITH compaction = {
       'class': 'LeveledCompactionStrategy',
       'sstable_size_in_mb': 320
   };
   ```

### Problem: Disk Space Running Low During Compaction

**Symptoms:**

- Compaction fails with "No space left on device"
- Disk utilization spikes during compaction

**Prevention:**

```bash
# Monitor disk space
df -h /var/lib/cassandra/data

# STCS can require 2x space temporarily
# Maintain at least 50% free for STCS
# Maintain at least 30% free for LCS
```

**Emergency Response:**

```bash
# Stop compaction
nodetool stop COMPACTION

# Clear snapshots
nodetool clearsnapshot

# Remove obsolete SSTables
nodetool cleanup keyspace

# Add storage or remove data before resuming
```

### Problem: LCS L0 Backlog

**Symptoms:**

- L0 SSTable count >4 and growing
- Read latency increasing

**Diagnosis:**

```bash
nodetool tablestats keyspace.table | grep "SSTables in each level"
# [15, 10, 100, 1000, ...]
# 15 L0 SSTables = significant backlog
```

**Solutions:**

1. Increase throughput:
   ```bash
   nodetool setcompactionthroughput 128
   ```

2. Throttle writes temporarily

3. Switch to STCS if write-heavy:
   ```sql
   ALTER TABLE keyspace.table WITH compaction = {
       'class': 'SizeTieredCompactionStrategy'
   };
   ```

---

## Operational Best Practices

### Daily Monitoring

```bash
# Quick health check
nodetool compactionstats
nodetool tablestats <keyspace>.<table> | grep -E "SSTable count|Pending"
```

### Weekly Review

```bash
# Comprehensive review
nodetool tablestats --human-readable
nodetool compactionhistory
df -h /var/lib/cassandra/data
```

### Before Major Operations

```bash
# Pre-operation checklist
echo "=== Disk Space ==="
df -h /var/lib/cassandra/data

echo "=== Pending Compactions ==="
nodetool compactionstats

echo "=== Table Stats ==="
nodetool tablestats keyspace.table | head -30

echo "=== Current Settings ==="
cqlsh -e "SELECT compaction FROM system_schema.tables
          WHERE keyspace_name='keyspace' AND table_name='table';"
```

---

## AxonOps Compaction Management

Managing compaction across a cluster requires monitoring multiple nodes, correlating metrics, and understanding workload patterns. [AxonOps](https://axonops.com) provides integrated compaction management tools.

### Compaction Visibility

AxonOps provides:

- **Cross-cluster view**: Pending compactions and SSTable counts across all nodes
- **Per-table analysis**: Identify tables with compaction issues
- **Historical trends**: Track compaction throughput and backlog over time
- **Anomaly detection**: Alert when compaction patterns deviate from normal

### Strategy Optimization

- **Workload analysis**: Recommendations based on read/write patterns
- **Strategy comparison**: Simulate impact of strategy changes
- **Migration support**: Guided strategy transitions with monitoring
- **Impact assessment**: Predict resource requirements for strategy changes

### Automated Response

- **Throttle management**: Automatic throughput adjustment based on cluster load
- **Alert-driven actions**: Automated response to compaction backlogs
- **Capacity warnings**: Proactive alerts when disk space will be exhausted
- **Performance correlation**: Link compaction activity to latency changes

See the [AxonOps documentation](../../../../monitoring/overview.md) for compaction monitoring features.

---

## Related Documentation

- **[Compaction Overview](../../architecture/storage-engine/compaction/index.md)** - Concepts and strategy selection
- **[STCS](../../architecture/storage-engine/compaction/stcs.md)** - Size-Tiered Compaction Strategy
- **[LCS](../../architecture/storage-engine/compaction/lcs.md)** - Leveled Compaction Strategy
- **[TWCS](../../architecture/storage-engine/compaction/twcs.md)** - Time-Window Compaction Strategy
- **[UCS](../../architecture/storage-engine/compaction/ucs.md)** - Unified Compaction Strategy
- **[Tombstones](../../architecture/storage-engine/tombstones.md)** - gc_grace_seconds and tombstone handling
