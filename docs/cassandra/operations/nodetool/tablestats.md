---
title: "nodetool tablestats"
description: "Display detailed statistics for Cassandra tables using nodetool tablestats command."
meta:
  - name: keywords
    content: "nodetool tablestats, table statistics, Cassandra metrics, table info"
---

# nodetool tablestats

Displays detailed statistics for tables including read/write latencies, SSTable counts, partition sizes, and space usage.

---

## Synopsis

```bash
nodetool [connection_options] tablestats [options] [--] [keyspace[.table] ...]
```

## Description

`nodetool tablestats` provides comprehensive metrics for tables including:

- Read and write operation counts and latencies
- SSTable counts and sizes
- Partition statistics (count, size)
- Bloom filter and compression metrics
- Memtable information
- Percent repaired (for incremental repair)

This is one of the most important commands for capacity planning and performance analysis.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | Display stats for all tables in keyspace |
| `keyspace.table` | Display stats for specific table |

---

## Options

| Option | Description |
|--------|-------------|
| `-H, --human-readable` | Display sizes in human-readable format |
| `-F, --format` | Output format (json, yaml) |
| `-s, --sort` | Sort by column (read, write, space, etc.) |
| `-t, --top` | Show only top N tables |
| `-i, --ignore` | Ignore specific keyspaces/tables |

---

## Output Example

```
Keyspace : my_keyspace
        Read Count: 12345678
        Read Latency: 0.234 ms
        Write Count: 9876543
        Write Latency: 0.123 ms
        Pending Flushes: 0

                Table: users
                SSTable count: 12
                Old SSTable count: 0
                Max SSTable size: 128 MB
                Space used (live): 1.5 GB
                Space used (total): 1.8 GB
                Space used by snapshots (total): 256 MB
                Memtable cell count: 12345
                Memtable data size: 64 MB
                Memtable switch count: 234
                Speculative retries: 0
                Local read count: 5678901
                Local read latency: 0.456 ms
                Local write count: 3456789
                Local write latency: 0.123 ms
                Pending flushes: 0
                Percent repaired: 98.5
                Bloom filter false positives: 123
                Bloom filter false ratio: 0.00001
                Bloom filter space used: 24 MB
                Compression ratio: 0.35
                Compacted partition minimum bytes: 64
                Compacted partition maximum bytes: 65536
                Compacted partition mean bytes: 1024
                Average live cells per slice (last five minutes): 12.5
                Maximum live cells per slice (last five minutes): 150
                Average tombstones per slice (last five minutes): 0.5
                Maximum tombstones per slice (last five minutes): 10
                Dropped mutations: 0
                Droppable tombstone ratio: 0.05
```

---

## Key Metrics Explained

### Read/Write Latencies

| Metric | Description | Healthy Range |
|--------|-------------|---------------|
| Local read latency | Average read time | < 5ms (SSD), < 20ms (HDD) |
| Local write latency | Average write time | < 1ms |

!!! warning "High Read Latency"
    Read latency > 10ms consistently may indicate:

    - Large partitions
    - Too many SSTables
    - Bloom filter issues
    - Disk I/O problems

### SSTable Metrics

| Metric | Description | Action Threshold |
|--------|-------------|------------------|
| SSTable count | Number of SSTables | > 20-30 warrants investigation |
| Max SSTable size | Largest SSTable | Varies by compaction strategy |
| Space used (live) | Data excluding tombstones | Capacity planning |
| Space used (total) | All data including tombstones | Disk usage |

!!! tip "SSTable Count"
    High SSTable counts increase read latency and memory usage:

    - STCS: May have many SSTables naturally
    - LCS: Should be mostly in L1+
    - TWCS: One per time window

### Partition Statistics

| Metric | Description | Warning Signs |
|--------|-------------|---------------|
| Compacted partition mean bytes | Average partition size | > 100MB is large |
| Compacted partition maximum bytes | Largest partition | > 100MB needs attention |
| Live cells per slice | Cells read per query | > 10000 may be problematic |

!!! danger "Large Partitions"
    Large partitions cause:

    - Heap pressure
    - GC issues
    - Uneven load distribution
    - Repair/compaction problems

### Tombstone Metrics

| Metric | Description |
|--------|-------------|
| Tombstones per slice | Tombstones scanned per read |
| Droppable tombstone ratio | Ratio of tombstones eligible for GC |

!!! warning "Tombstone Warnings"
    High tombstones per slice indicates:

    - Delete-heavy workload
    - Queries scanning past deletes
    - Potential for tombstone warnings in logs

### Bloom Filter

| Metric | Description |
|--------|-------------|
| Bloom filter false positives | Incorrect positive matches |
| Bloom filter false ratio | False positive rate |
| Bloom filter space used | Memory for bloom filters |

Target false ratio: < 0.01 (1%)

### Compression

| Metric | Description |
|--------|-------------|
| Compression ratio | Compressed size / uncompressed size |

- 0.3-0.5 is typical for most data
- < 0.2 indicates highly compressible data
- > 0.8 may indicate compression isn't helping

---

## Examples

### All Tables in Keyspace

```bash
nodetool tablestats my_keyspace
```

### Specific Table

```bash
nodetool tablestats my_keyspace.users
```

### Human-Readable Sizes

```bash
nodetool tablestats -H my_keyspace
```

### Top 10 Tables by Read Count

```bash
nodetool tablestats -s reads -t 10
```

### JSON Output

```bash
nodetool tablestats -F json my_keyspace.users
```

### Extract Specific Metrics

```bash
# SSTable counts for all tables
nodetool tablestats | grep -E "Table:|SSTable count"

# Read latencies
nodetool tablestats | grep -E "Table:|Local read latency"

# Space usage
nodetool tablestats | grep -E "Table:|Space used"
```

### Compare Across Nodes

```bash
for node in node1 node2 node3; do
    echo "=== $node ==="
    nodetool -h $node tablestats my_keyspace.users | grep -E "SSTable|Space|latency"
done
```

---

## Common Analysis Patterns

### Finding Large Partitions

```bash
nodetool tablestats | grep -A2 "Table:" | grep -E "Table:|maximum bytes"
```

Tables with max partition > 100MB need data model review.

### Identifying Tables Needing Compaction

```bash
nodetool tablestats | grep -A5 "Table:" | grep -E "Table:|SSTable count"
```

High SSTable counts may indicate compaction falling behind.

### Checking Tombstone Issues

```bash
nodetool tablestats | grep -E "Table:|tombstones per slice|Droppable"
```

High tombstones per slice correlates with read latency issues.

### Repair Status

```bash
nodetool tablestats | grep -E "Table:|Percent repaired"
```

Track incremental repair progress.

---

## Performance Baselines

### Healthy Metrics

| Metric | Target |
|--------|--------|
| Local read latency | < 5ms |
| Local write latency | < 1ms |
| SSTable count | < 20-30 |
| Bloom filter false ratio | < 0.01 |
| Tombstones per slice | < 100 |
| Partition mean bytes | < 10MB |

### Warning Thresholds

| Metric | Warning Level |
|--------|---------------|
| Local read latency | > 20ms |
| SSTable count | > 50 |
| Bloom filter false ratio | > 0.1 |
| Tombstones per slice | > 1000 |
| Partition maximum bytes | > 100MB |

---

## Troubleshooting with tablestats

### Slow Reads

Check these metrics:
1. SSTable count - too many?
2. Partition size - too large?
3. Tombstones per slice - too many?
4. Bloom filter false ratio - ineffective?

### High Disk Usage

Check:
1. Space used by snapshots - orphaned snapshots?
2. Droppable tombstone ratio - need compaction?
3. Compression ratio - compression working?

### Memory Issues

Check:
1. Bloom filter space - large tables consume heap
2. Memtable size - appropriate for workload?
3. Partition sizes - large partitions stress heap

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [tpstats](tpstats.md) | Thread pool statistics |
| [proxyhistograms](proxyhistograms.md) | Coordinator-level latencies |
| [compactionstats](compactionstats.md) | Active compaction information |
| [info](info.md) | Node-level overview |
