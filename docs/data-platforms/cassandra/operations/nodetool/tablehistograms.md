---
title: "nodetool tablehistograms"
description: "Display read/write latency histograms for a table using nodetool tablehistograms."
meta:
  - name: keywords
    content: "nodetool tablehistograms, latency histogram, table statistics, Cassandra"
search:
  boost: 3
---

# nodetool tablehistograms

Displays latency and size histograms for a specific table.

---

## Synopsis

```bash
nodetool [connection_options] tablehistograms <keyspace> <table>
```

## Description

`nodetool tablehistograms` provides detailed latency percentile distributions and size statistics for a specific table. This is more detailed than `tablestats` and shows how read/write latencies are distributed.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | The keyspace containing the table |
| `table` | The table to analyze |

---

## Output Sections

### Read Latency Histogram

```
my_keyspace/my_table histograms
Percentile  Read Latency   Write Latency  SSTables     Partition Size  Cell Count
                (micros)       (micros)                     (bytes)
50%              158.49          120.00      1.00             310            1
75%              219.34          158.49      1.00             535            2
95%              545.79          315.85      2.00            1597            5
98%              943.13          545.79      2.00            2759            8
99%             1258.93          776.05      3.00            4768           14
Min                 61              52      1.00              104            1
Max              25109           15209      7.00          1213897        29173
```

---

## Output Fields

| Field | Description |
|-------|-------------|
| `Read Latency` | Local read latency in microseconds |
| `Write Latency` | Local write latency in microseconds |
| `SSTables` | Number of SSTables read per query |
| `Partition Size` | Size of partitions in bytes |
| `Cell Count` | Number of cells per partition |

---

## Understanding Percentiles

| Percentile | Meaning |
|------------|---------|
| 50% (P50) | Median - half of operations are faster |
| 75% (P75) | 75% of operations are faster |
| 95% (P95) | Common SLA target |
| 98% (P98) | Near-worst case |
| 99% (P99) | Tail latency |
| Min | Fastest observed |
| Max | Slowest observed |

---

## Examples

### View Table Histograms

```bash
nodetool tablehistograms my_keyspace my_table
```

### Compare Multiple Tables

```bash
for table in users orders products; do
    echo "=== $table ==="
    nodetool tablehistograms my_keyspace $table | head -10
done
```

---

## Interpreting Results

### Healthy Read Latency

```
50%:  100-500 µs    (excellent)
95%:  1-5 ms        (good)
99%:  5-20 ms       (acceptable)
Max:  < 100 ms      (no major outliers)
```

### Problematic Indicators

| Symptom | Possible Cause |
|---------|----------------|
| High P50 | Slow disks, large partitions |
| P99 >> P95 | GC pauses, disk contention |
| High Max | Occasional extreme latency |
| High SSTable count | Compaction backlog |
| Large partition size | Data model issue |

---

## SSTables Per Read

The `SSTables` column shows how many SSTables are read per query:

```
SSTables
    1.00    # Ideal - data in one SSTable
    2.00    # Good - minor merging needed
    5.00+   # Problem - compaction needed
```

!!! warning "High SSTable Count"
    If P95+ shows many SSTables per read:

    - Check compaction is running
    - Consider different compaction strategy
    - May indicate writes outpacing compaction

---

## Partition Size Analysis

```
Partition Size (bytes)
50%:   310        # Small partitions (good)
99%:   4768       # Larger partitions
Max:   1213897    # ~1.2 MB largest partition
```

| Size | Assessment |
|------|------------|
| < 10 KB | Excellent |
| 10-100 KB | Good |
| 100 KB - 1 MB | Monitor |
| > 1 MB | Potential problem |
| > 100 MB | Serious issue |

---

## Cell Count

Number of cells (column values) per partition:

```
Cell Count
50%:   1          # Minimal cells
99%:   14         # Moderate
Max:   29173      # Wide partition
```

High cell counts indicate wide partitions that may cause:
- Slow reads
- Memory pressure
- GC issues

---

## Use Cases

### Performance Baseline

```bash
# Capture baseline for comparison
nodetool tablehistograms my_keyspace my_table > baseline_$(date +%Y%m%d).txt
```

### Troubleshoot Slow Queries

```bash
# Check if table has latency issues
nodetool tablehistograms my_keyspace slow_table
```

Look for:
- High P95/P99 latencies
- High SSTable counts
- Large partitions

### Capacity Planning

```bash
# Understand data distribution
nodetool tablehistograms my_keyspace my_table | grep -A10 "Partition Size"
```

---

## Comparison with Other Commands

| Command | Scope | Detail Level |
|---------|-------|--------------|
| `tablehistograms` | Single table | Detailed percentiles |
| `tablestats` | All tables | Summary statistics |
| `proxyhistograms` | Coordinator level | Network + local latency |

### Local vs Coordinator Latency

- `tablehistograms`: Local read/write on this node only
- `proxyhistograms`: Full request (includes network to replicas)

If `proxyhistograms` >> `tablehistograms`, the issue is network/remote nodes.

---

## Scripting Examples

### Extract P99 Read Latency

```bash
nodetool tablehistograms my_keyspace my_table | grep "99%" | awk '{print $2}'
```

### Alert on High Latency

```bash
#!/bin/bash
P99=$(nodetool tablehistograms my_keyspace my_table | grep "99%" | awk '{print $2}')
THRESHOLD=5000  # 5ms in microseconds

if (( $(echo "$P99 > $THRESHOLD" | bc -l) )); then
    echo "ALERT: P99 read latency is ${P99}µs (threshold: ${THRESHOLD}µs)"
fi
```

### Monitor Multiple Tables

```bash
#!/bin/bash
echo "Table,P50_Read,P95_Read,P99_Read,Max_Read"
for table in users orders products; do
    stats=$(nodetool tablehistograms my_keyspace $table)
    p50=$(echo "$stats" | grep "50%" | awk '{print $2}')
    p95=$(echo "$stats" | grep "95%" | awk '{print $2}')
    p99=$(echo "$stats" | grep "99%" | awk '{print $2}')
    max=$(echo "$stats" | grep "Max" | awk '{print $2}')
    echo "$table,$p50,$p95,$p99,$max"
done
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [tablestats](tablestats.md) | Summary statistics for tables |
| [proxyhistograms](proxyhistograms.md) | Coordinator-level latencies |
| [compactionstats](compactionstats.md) | Check compaction backlog |
| [tpstats](tpstats.md) | Thread pool statistics |
