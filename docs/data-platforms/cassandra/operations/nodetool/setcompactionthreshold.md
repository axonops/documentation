---
title: "nodetool setcompactionthreshold"
description: "Set min/max compaction thresholds for a table using nodetool setcompactionthreshold."
meta:
  - name: keywords
    content: "nodetool setcompactionthreshold, compaction threshold, Cassandra compaction"
---

# nodetool setcompactionthreshold

Sets the minimum and maximum SSTable count thresholds that trigger compaction for a table using SizeTieredCompactionStrategy.

---

## Synopsis

```bash
nodetool [connection_options] setcompactionthreshold <keyspace> <table> <min_threshold> <max_threshold>
```

## Description

`nodetool setcompactionthreshold` modifies the compaction trigger thresholds for a specific table. These thresholds determine when Cassandra initiates compaction based on the number of similarly-sized SSTables.

!!! warning "SizeTieredCompactionStrategy Only"
    This command **only applies to tables using SizeTieredCompactionStrategy (STCS)**. It has no effect on tables using:

    - LeveledCompactionStrategy (LCS)
    - TimeWindowCompactionStrategy (TWCS)
    - UnifiedCompactionStrategy (UCS)

    For other strategies, thresholds are either not applicable or configured differently.

!!! warning "Non-Persistent Setting"
    This setting is applied at runtime only and does not persist across node restarts. After a restart, thresholds revert to the table's schema definition.

    To make changes permanent, use `ALTER TABLE`:

    ```cql
    ALTER TABLE my_keyspace.my_table
    WITH compaction = {
        'class': 'SizeTieredCompactionStrategy',
        'min_threshold': '4',
        'max_threshold': '32'
    };
    ```

---

## Understanding Compaction Thresholds

### What Are Thresholds?

In SizeTieredCompactionStrategy, SSTables are grouped into "buckets" based on their size. When the number of SSTables in a bucket reaches the **min_threshold**, compaction is triggered to merge them.

| Threshold | Default | Purpose |
|-----------|---------|---------|
| `min_threshold` | 4 | Minimum number of similarly-sized SSTables required to trigger compaction |
| `max_threshold` | 32 | Maximum number of SSTables to include in a single compaction operation |

### How STCS Compaction Works

```
SizeTieredCompactionStrategy Flow:

1. SSTables accumulate from flushes
   [10MB] [12MB] [11MB] [9MB] [50MB] [48MB] [52MB]

2. SSTables grouped by similar size (buckets)
   Bucket 1: [10MB] [12MB] [11MB] [9MB]  ← 4 SSTables (= min_threshold)
   Bucket 2: [50MB] [48MB] [52MB]         ← 3 SSTables (< min_threshold)

3. Bucket 1 triggers compaction (has >= min_threshold)
   [10MB] [12MB] [11MB] [9MB] → Compaction → [42MB]

4. Result:
   [42MB] [50MB] [48MB] [52MB]

5. Eventually bucket of ~50MB SSTables will compact when it reaches 4
```

### The Role of Each Threshold

**min_threshold:**
- Controls how many SSTables must exist before compaction starts
- Lower values = more frequent compaction = better read performance, more I/O
- Higher values = less frequent compaction = better write throughput, more SSTables to read through

**max_threshold:**
- Limits how many SSTables are compacted at once
- Prevents very long-running compactions
- Controls peak disk space usage during compaction

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | Target keyspace name |
| `table` | Target table name |
| `min_threshold` | Minimum SSTables to trigger compaction (default: 4) |
| `max_threshold` | Maximum SSTables per compaction operation (default: 32) |

---

## Examples

### View Current Thresholds

```bash
# Check existing settings before changing
nodetool getcompactionthreshold my_keyspace my_table
```

### Set Default Thresholds

```bash
nodetool setcompactionthreshold my_keyspace my_table 4 32
```

### Aggressive Compaction (Better Reads)

```bash
# Lower min_threshold triggers compaction sooner
nodetool setcompactionthreshold my_keyspace my_table 2 16
```

### Conservative Compaction (Better Writes)

```bash
# Higher min_threshold allows more SSTables before compacting
nodetool setcompactionthreshold my_keyspace my_table 8 64
```

---

## Why Change Compaction Thresholds?

### Scenario 1: High Read Latency Due to Many SSTables

**Problem:** Read queries are slow because Cassandra must check many SSTables.

**Diagnosis:**
```bash
# Check SSTable count
nodetool tablestats my_keyspace.my_table | grep "SSTable count"
# High count (e.g., 50+) indicates compaction isn't keeping up
```

**Solution:** Lower min_threshold to trigger compaction sooner:
```bash
nodetool setcompactionthreshold my_keyspace my_table 2 16
```

**Trade-off:** More I/O spent on compaction, but fewer SSTables improves read latency.

### Scenario 2: Compaction Can't Keep Up with Writes

**Problem:** Write-heavy workload generates SSTables faster than compaction can merge them.

**Diagnosis:**
```bash
# Check pending compactions
nodetool compactionstats
# Many pending compactions indicates compaction is overwhelmed
```

**Solution:** Raise min_threshold to reduce compaction frequency:
```bash
nodetool setcompactionthreshold my_keyspace my_table 8 64
```

**Trade-off:** More SSTables accumulate, potentially impacting read performance.

### Scenario 3: Disk Space Pressure During Compaction

**Problem:** Large compactions consume too much temporary disk space.

**Diagnosis:**
```bash
# Monitor disk during compaction
df -h /var/lib/cassandra

# Check compaction size
nodetool compactionstats
```

**Solution:** Lower max_threshold to limit compaction size:
```bash
nodetool setcompactionthreshold my_keyspace my_table 4 16
```

**Trade-off:** Smaller compactions mean more total compactions over time.

### Scenario 4: Temporary Tuning During Bulk Load

**Problem:** Bulk loading data causes excessive compaction overhead.

**Solution:** Temporarily raise thresholds during load:
```bash
# Before bulk load - reduce compaction
nodetool setcompactionthreshold my_keyspace my_table 16 64

# Perform bulk load...

# After bulk load - restore and compact
nodetool setcompactionthreshold my_keyspace my_table 4 32
nodetool compact my_keyspace my_table
```

### Scenario 5: Time-Series Data with Varying Access Patterns

**Problem:** Recent data is read frequently, older data rarely accessed.

**Solution:** Use TWCS instead, but if stuck with STCS:
```bash
# More aggressive compaction for hot tables
nodetool setcompactionthreshold my_keyspace hot_table 2 16

# Less aggressive for cold tables
nodetool setcompactionthreshold my_keyspace cold_table 8 64
```

---

## Compaction Strategy Comparison

### Which Strategies Use Thresholds?

| Strategy | min/max_threshold | Configuration Method |
|----------|-------------------|---------------------|
| **SizeTieredCompactionStrategy (STCS)** | Yes | `setcompactionthreshold` or table schema |
| **LeveledCompactionStrategy (LCS)** | No | Uses `sstable_size_in_mb` instead |
| **TimeWindowCompactionStrategy (TWCS)** | Partial | Inherits STCS thresholds for window compaction |
| **UnifiedCompactionStrategy (UCS)** | No | Uses different parameters |

### STCS Schema Configuration

```cql
CREATE TABLE my_keyspace.my_table (
    id uuid PRIMARY KEY,
    data text
) WITH compaction = {
    'class': 'SizeTieredCompactionStrategy',
    'min_threshold': '4',
    'max_threshold': '32',
    'min_sstable_size': '52428800',      -- 50MB minimum size for bucketing
    'bucket_low': '0.5',                  -- Bucket size ratio low bound
    'bucket_high': '1.5'                  -- Bucket size ratio high bound
};
```

### LCS Configuration (Different Approach)

```cql
-- LCS doesn't use min/max_threshold
-- It uses fixed SSTable sizes and levels
ALTER TABLE my_keyspace.my_table
WITH compaction = {
    'class': 'LeveledCompactionStrategy',
    'sstable_size_in_mb': '160'
};
```

### TWCS Configuration

```cql
-- TWCS uses time windows, but inherits threshold behavior
ALTER TABLE my_keyspace.my_table
WITH compaction = {
    'class': 'TimeWindowCompactionStrategy',
    'compaction_window_unit': 'DAYS',
    'compaction_window_size': '1',
    'min_threshold': '4',
    'max_threshold': '32'
};
```

---

## Impact Assessment

### Trade-offs Summary

| Setting | Effect on Reads | Effect on Writes | Disk I/O | Disk Space |
|---------|-----------------|------------------|----------|------------|
| Lower min_threshold | Improved (fewer SSTables) | May slow (more compaction) | Higher | More stable |
| Higher min_threshold | May degrade (more SSTables) | Improved (less compaction) | Lower | May spike during compaction |
| Lower max_threshold | Neutral | Neutral | Smaller peaks | Smaller peaks |
| Higher max_threshold | Neutral | Neutral | Larger peaks | Larger peaks |

### Monitoring After Changes

```bash
#!/bin/bash
# monitor_compaction.sh - Watch compaction after threshold change

echo "=== SSTable Count ==="
nodetool tablestats my_keyspace.my_table | grep "SSTable count"

echo ""
echo "=== Pending Compactions ==="
nodetool compactionstats

echo ""
echo "=== Read Latency ==="
nodetool tablehistograms my_keyspace.my_table | head -20
```

---

## Cluster-Wide Configuration

### Apply to All Nodes

Since thresholds are per-node settings, apply to all nodes for consistency:

```bash
#!/bin/bash
# set_thresholds_cluster.sh

KEYSPACE="$1"
TABLE="$2"
MIN_THRESHOLD="$3"
MAX_THRESHOLD="$4"

if [ -z "$MAX_THRESHOLD" ]; then
    echo "Usage: $0 <keyspace> <table> <min_threshold> <max_threshold>"
    exit 1
fi

# Get list of node IPs from local nodetool status
nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo -n "$node: "
    ssh "$node" 'nodetool setcompactionthreshold '"$KEYSPACE"' '"$TABLE"' '"$MIN_THRESHOLD"' '"$MAX_THRESHOLD"' && echo "set to '"$MIN_THRESHOLD"'/'"$MAX_THRESHOLD"'" || echo "FAILED"'
done
```

### Making Changes Permanent

Runtime changes don't persist. Use `ALTER TABLE` for permanent changes:

```cql
-- This persists across restarts and applies cluster-wide
ALTER TABLE my_keyspace.my_table
WITH compaction = {
    'class': 'SizeTieredCompactionStrategy',
    'min_threshold': '4',
    'max_threshold': '32'
};
```

---

## Recommended Values

### General Guidelines

| Workload | min_threshold | max_threshold | Rationale |
|----------|---------------|---------------|-----------|
| Balanced (default) | 4 | 32 | Good for most workloads |
| Read-heavy | 2-3 | 16 | Fewer SSTables, better read performance |
| Write-heavy | 6-8 | 64 | Less compaction overhead |
| Bulk loading | 16+ | 64 | Minimize compaction during load |
| Space-constrained | 4 | 16 | Smaller compactions, predictable disk usage |

### Values to Avoid

!!! danger "Invalid and Problematic Settings"

    - **min_threshold < 2**: Not allowed. The minimum valid value is 2.
    - **min_threshold = 0 or max_threshold = 0**: Deprecated and rejected in current versions. Use `nodetool disableautocompaction` or set `compaction = {'enabled': 'false'}` instead.
    - **min_threshold > max_threshold**: Invalid configuration
    - **Very high min_threshold (32+)**: Too many SSTables accumulate, degrading reads
    - **Very low max_threshold (< 4)**: Tiny compactions, inefficient

---

## Troubleshooting

### Thresholds Not Taking Effect

```bash
# Verify the change was applied
nodetool getcompactionthreshold my_keyspace my_table

# Check if table uses STCS
cqlsh -e "DESCRIBE TABLE my_keyspace.my_table;" | grep compaction
```

### SSTable Count Still High After Lowering Threshold

```bash
# Thresholds only affect future compactions
# Force compaction to reduce current SSTables
nodetool compact my_keyspace my_table

# Or run major compaction (creates one SSTable)
nodetool compact --user-defined my_keyspace my_table
```

### Compaction Running Constantly

```bash
# min_threshold may be too low
# Check current setting
nodetool getcompactionthreshold my_keyspace my_table

# Raise threshold to reduce frequency
nodetool setcompactionthreshold my_keyspace my_table 6 32

# Or consider switching to LCS for predictable compaction
```

---

## Best Practices

!!! tip "Threshold Guidelines"

    1. **Start with defaults** - 4/32 works well for most cases
    2. **Measure before changing** - Get baseline SSTable counts and latencies
    3. **Change incrementally** - Adjust by 1-2, observe, then adjust again
    4. **Make permanent via schema** - Use `ALTER TABLE` after validating runtime changes
    5. **Apply cluster-wide** - Set same thresholds on all nodes for consistency
    6. **Consider strategy switch** - If tuning STCS heavily, LCS or TWCS may be better fits

!!! warning "Common Mistakes"

    - Applying to non-STCS tables (has no effect)
    - Forgetting to persist changes (lost on restart)
    - Setting only on one node (inconsistent behavior)
    - Extreme values that cause performance problems

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [getcompactionthreshold](getcompactionthreshold.md) | View current threshold settings |
| [compactionstats](compactionstats.md) | Monitor active and pending compactions |
| [compact](compact.md) | Manually trigger compaction |
| [tablestats](tablestats.md) | View SSTable counts and table metrics |
| [tablehistograms](tablehistograms.md) | Check read latency distribution |
