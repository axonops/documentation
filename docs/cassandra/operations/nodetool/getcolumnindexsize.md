---
description: "Display column index size setting in Cassandra using nodetool getcolumnindexsize."
meta:
  - name: keywords
    content: "nodetool getcolumnindexsize, column index, index size, Cassandra configuration"
---

# nodetool getcolumnindexsize

Displays the current column index size threshold.

---

## Synopsis

```bash
nodetool [connection_options] getcolumnindexsize
```

---

## Description

`nodetool getcolumnindexsize` displays the current column index size threshold in kilobytes. This threshold controls how frequently Cassandra creates index entries within partitions when writing SSTables. The column index (more accurately called the partition index) enables efficient row lookups within large partitions.

!!! info "Understanding the Column Index"
    Despite the name "column index," this setting controls **partition index granularity**—how Cassandra navigates within partitions to find specific rows. See [setcolumnindexsize](setcolumnindexsize.md) for detailed explanation of what this index does and why it matters.

---

## What This Value Means

The column index size threshold determines the maximum amount of partition data written before Cassandra creates an index entry:

| Displayed Value | Meaning |
|-----------------|---------|
| 16 KB | Index entry created every 16 KB of partition data |
| 64 KB (default) | Index entry created every 64 KB of partition data |
| 128 KB | Index entry created every 128 KB of partition data |

### Impact on Queries

```
Partition Data (256 KB total)

With 64 KB threshold (default):
┌────────────┬────────────┬────────────┬────────────┐
│  Block 1   │  Block 2   │  Block 3   │  Block 4   │
└────────────┴────────────┴────────────┴────────────┘
      ▲            ▲            ▲            ▲
   Index 1      Index 2      Index 3      Index 4

→ 4 index entries = 4 possible seek points

With 128 KB threshold:
┌──────────────────────┬──────────────────────┐
│       Block 1        │       Block 2        │
└──────────────────────┴──────────────────────┘
           ▲                      ▲
        Index 1                Index 2

→ 2 index entries = 2 possible seek points (less precise)
```

---

## Examples

### Basic Usage

```bash
nodetool getcolumnindexsize
```

**Sample output:**
```
Current column index size: 64 KB
```

### Check Value on Remote Node

```bash
nodetool -h 192.168.1.100 getcolumnindexsize
```

### Check Value Across Cluster

```bash
#!/bin/bash
# check_column_index_cluster.sh

echo "=== Column Index Size Across Cluster ==="

nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo -n "$node: "
    nodetool -h $node getcolumnindexsize 2>/dev/null | grep -oP '\d+ KB' || echo "FAILED"
done
```

**Sample output:**
```
=== Column Index Size Across Cluster ===
192.168.1.101: 64 KB
192.168.1.102: 64 KB
192.168.1.103: 32 KB   <-- Inconsistent!
```

---

## Interpreting the Value

### Default Value (64 KB)

The default value of 64 KB is appropriate for most workloads. This provides:

- Reasonable index granularity for partitions up to ~10 MB
- Balanced memory usage for index storage
- Good read performance for typical access patterns

### Values Below Default (16-32 KB)

Indicates the cluster has been tuned for:

- Large partitions (> 10 MB average)
- Frequent point queries on wide partitions
- Latency-sensitive read workloads

**Trade-off:** Higher memory usage for index storage.

### Values Above Default (128+ KB)

Indicates the cluster has been tuned for:

- Small partitions (< 100 KB average)
- Memory-constrained nodes
- Workloads where read latency is less critical

**Trade-off:** Potentially slower row lookups within partitions.

---

## When to Check This Value

### Performance Investigation

When read latency is higher than expected:

```bash
# Check current setting
nodetool getcolumnindexsize

# Compare with partition sizes
nodetool tablestats my_keyspace.my_table | grep -E "partition size"

# If large partitions + large column index size = potential issue
```

### Configuration Audit

Ensure consistent configuration across cluster:

```bash
#!/bin/bash
# audit_column_index.sh

echo "Checking column index size consistency..."

values=()
for node in $(nodetool status | grep "^UN" | awk '{print $2}'); do
    value=$(nodetool -h $node getcolumnindexsize 2>/dev/null | grep -oP '\d+')
    values+=("$node:$value")
done

# Check for inconsistency
unique_values=$(printf '%s\n' "${values[@]}" | cut -d: -f2 | sort -u | wc -l)

if [ "$unique_values" -gt 1 ]; then
    echo "WARNING: Inconsistent column index sizes detected!"
    printf '%s\n' "${values[@]}"
else
    echo "OK: All nodes have consistent column index size"
fi
```

### Before Tuning

Always check current value before making changes:

```bash
# Document current state
echo "Current column index size: $(nodetool getcolumnindexsize)"
echo "Partition sizes:"
nodetool tablestats my_keyspace.my_table | grep -i "partition"

# Then make informed decision about changes
```

---

## Relationship to cassandra.yaml

The displayed value reflects the runtime setting, which may differ from `cassandra.yaml`:

| Source | Precedence | Persistence |
|--------|------------|-------------|
| `nodetool setcolumnindexsize` | Active at runtime | Lost on restart |
| `cassandra.yaml` | Loaded at startup | Permanent |

### Checking Configuration vs Runtime

```bash
# Runtime value (what's actually in use)
nodetool getcolumnindexsize

# Configuration file value (what will be used after restart)
grep "column_index_size" /etc/cassandra/cassandra.yaml
```

If these differ, the runtime value was changed via `nodetool setcolumnindexsize` and will revert to the configuration file value on restart.

---

## Decision Guide

Based on the value returned:

| If Value Is | And Partition Sizes Are | Consider |
|-------------|-------------------------|----------|
| 64 KB | Small (< 100 KB) | Increasing to 128 KB to save memory |
| 64 KB | Large (> 10 MB) | Decreasing to 32 KB for better read latency |
| 16-32 KB | Small | Increasing to 64 KB (default may be better) |
| 128+ KB | Large | Decreasing for better read performance |

---

## Common Issues

### Value Differs from cassandra.yaml

```bash
# Check both
nodetool getcolumnindexsize
grep column_index_size /etc/cassandra/cassandra.yaml

# If different, someone used setcolumnindexsize
# Either update cassandra.yaml or wait for restart
```

### Inconsistent Values Across Cluster

```bash
# Standardize across cluster
TARGET_SIZE=64

for node in $(nodetool status | grep "^UN" | awk '{print $2}'); do
    echo "Setting column index size on $node..."
    nodetool -h $node setcolumnindexsize $TARGET_SIZE
done

# Update cassandra.yaml on all nodes for persistence
```

### Not Sure If Current Value Is Optimal

See the comprehensive guide in [setcolumnindexsize](setcolumnindexsize.md) for:

- How to analyze partition sizes
- Trade-offs of different values
- Tuning workflow and best practices

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [setcolumnindexsize](setcolumnindexsize.md) | Modify the threshold (includes detailed explanation) |
| [tablestats](tablestats.md) | Check partition sizes to inform tuning decisions |
| [info](info.md) | View memory usage including index structures |
