---
title: "Cassandra Compaction Issues"
description: "Compaction issues troubleshooting playbook. Diagnose compaction problems."
meta:
  - name: keywords
    content: "compaction troubleshooting, compaction issues, stuck compaction"
---

# Compaction Issues

Compaction merges SSTables to maintain read performance and reclaim space. When compaction falls behind or behaves unexpectedly, read performance degrades and disk usage grows.

---

## Symptoms

- Growing pending compaction count
- Increasing SSTable count per table
- Degrading read latency over time
- Disk space not being reclaimed after deletes
- High I/O during compaction spikes
- "Compaction stuck" or very slow progress

---

## Diagnosis

### Step 1: Check Compaction Status

```bash
nodetool compactionstats
```

**Problem indicators:**
- High pending count (> 50 per table)
- Same compaction running for hours
- No active compactions despite pending

### Step 2: Check SSTable Counts

```bash
nodetool tablestats my_keyspace | grep -E "Table:|SSTable count"
```

**Target:** Generally < 20 SSTables per table (varies by strategy).

### Step 3: Check Compaction Throughput

```bash
nodetool getcompactionthroughput
```

**Default:** 64 MB/s. May need increase for high-write workloads.

### Step 4: Check Disk I/O

```bash
iostat -x 1 10
```

**Problem indicators:**
- Disk utilization at 100%
- High await times

### Step 5: Check Compaction Strategy

```bash
cqlsh -e "SELECT table_name, compaction FROM system_schema.tables WHERE keyspace_name = 'my_keyspace';"
```

---

## Resolution

### Case 1: Compaction Falling Behind

**Increase compaction throughput:**

```bash
# Check current
nodetool getcompactionthroughput

# Increase (MB/s)
nodetool setcompactionthroughput 128
```

**Increase concurrent compactors:**

```bash
# Check current
nodetool getconcurrentcompactors

# Increase
nodetool setconcurrentcompactors 4
```

### Case 2: Compaction Disabled

```bash
# Check if auto-compaction is enabled
nodetool statusautocompaction my_keyspace my_table

# Enable if disabled
nodetool enableautocompaction my_keyspace my_table
```

### Case 3: Wrong Compaction Strategy

**For read-heavy workloads (many updates):**

```sql
ALTER TABLE my_table WITH compaction = {
    'class': 'LeveledCompactionStrategy',
    'sstable_size_in_mb': 160
};
```

**For time-series data:**

```sql
ALTER TABLE my_table WITH compaction = {
    'class': 'TimeWindowCompactionStrategy',
    'compaction_window_unit': 'DAYS',
    'compaction_window_size': 1
};
```

**For write-heavy workloads:**

```sql
ALTER TABLE my_table WITH compaction = {
    'class': 'SizeTieredCompactionStrategy',
    'min_threshold': 4,
    'max_threshold': 32
};
```

### Case 4: Force Manual Compaction

**For specific table:**

```bash
nodetool compact my_keyspace my_table
```

**For major compaction (use sparingly):**

```bash
# Warning: Resource intensive
nodetool compact --split-output my_keyspace my_table
```

!!! warning "Major Compaction"
    Major compaction creates one large SSTable and can cause significant I/O. Use `--split-output` to create multiple smaller SSTables instead.

### Case 5: Compaction Stuck on Large SSTable

**Check what's happening:**

```bash
nodetool compactionstats -H
```

**If stuck on validation:**

```bash
# May need to restart node if truly stuck
# First try waiting - large SSTables take time

# If necessary, cancel specific compaction
# (Requires identifying compaction ID from logs)
```

### Case 6: Disk Full Preventing Compaction

See [Handle Full Disk](handle-full-disk.md).

```bash
# Quick space recovery
nodetool clearsnapshot --all

# Check space
df -h /var/lib/cassandra
```

---

## Compaction Strategy Selection

| Strategy | Best For | SSTable Behavior |
|----------|----------|------------------|
| **STCS** | Write-heavy, space-efficient | Many SSTables, tiered by size |
| **LCS** | Read-heavy, consistent performance | Fixed-size levels |
| **TWCS** | Time-series, TTL data | Time-based windows |
| **UCS** | Flexible, Cassandra 5.0+ | Unified approach |

### Migration Between Strategies

```sql
-- Check current strategy
SELECT compaction FROM system_schema.tables
WHERE keyspace_name = 'my_ks' AND table_name = 'my_table';

-- Change strategy (takes effect gradually)
ALTER TABLE my_table WITH compaction = {
    'class': 'LeveledCompactionStrategy'
};

-- Force migration
nodetool compact my_keyspace my_table
```

---

## Tuning Parameters

### Size-Tiered (STCS)

```sql
ALTER TABLE my_table WITH compaction = {
    'class': 'SizeTieredCompactionStrategy',
    'min_threshold': 4,        -- Min SSTables to compact
    'max_threshold': 32,       -- Max SSTables to compact
    'min_sstable_size': 50     -- Min size to consider (MB)
};
```

### Leveled (LCS)

```sql
ALTER TABLE my_table WITH compaction = {
    'class': 'LeveledCompactionStrategy',
    'sstable_size_in_mb': 160  -- Target SSTable size
};
```

### Time-Window (TWCS)

```sql
ALTER TABLE my_table WITH compaction = {
    'class': 'TimeWindowCompactionStrategy',
    'compaction_window_unit': 'DAYS',
    'compaction_window_size': 1,
    'max_threshold': 32
};
```

---

## Recovery

### Verify Compaction Health

```bash
# Pending should decrease
watch -n 30 'nodetool compactionstats | head -10'

# SSTable count should stabilize
nodetool tablestats my_keyspace.my_table | grep "SSTable count"
```

### Verify Read Performance

```bash
# Latencies should improve
nodetool tablehistograms my_keyspace my_table
```

---

## Monitoring

### Key Metrics

| Metric | Warning | Critical |
|--------|---------|----------|
| Pending compactions | > 20 | > 100 |
| SSTable count | > 20 | > 50 |
| Compaction throughput | Near limit | At 0 |
| Disk usage | > 70% | > 85% |

### Monitoring Script

```bash
#!/bin/bash
# monitor_compaction.sh

while true; do
    clear
    echo "=== $(date) ==="
    echo ""
    echo "--- Compaction Stats ---"
    nodetool compactionstats | head -20
    echo ""
    echo "--- SSTable Counts ---"
    nodetool tablestats 2>/dev/null | grep -E "Table:|SSTable count" | head -20
    echo ""
    echo "--- Disk Usage ---"
    df -h /var/lib/cassandra
    sleep 60
done
```

---

## Prevention

1. **Choose appropriate strategy** - Match to workload pattern
2. **Monitor pending compactions** - Alert early
3. **Adequate disk space** - Keep < 70% utilization
4. **Sufficient I/O capacity** - SSD recommended
5. **Tune throughput** - Match to hardware capability
6. **Regular table maintenance** - Monitor SSTable counts

---

## Related Commands

| Command | Purpose |
|---------|---------|
| `nodetool compactionstats` | Current compaction status |
| `nodetool compact` | Force compaction |
| `nodetool setcompactionthroughput` | Adjust throughput |
| `nodetool getconcurrentcompactors` | View compactor count |
| `nodetool enableautocompaction` | Enable auto-compaction |
| `nodetool disableautocompaction` | Disable auto-compaction |

## Related Documentation

- [Compaction Management](../../operations/compaction-management/index.md) - Compaction strategies and management
- [Handle Full Disk](handle-full-disk.md) - Disk space issues
- [Tombstone Accumulation](tombstone-accumulation.md) - Tombstone compaction
