---
title: "nodetool compactionstats"
description: "Monitor active compaction progress in Cassandra using nodetool compactionstats command."
meta:
  - name: keywords
    content: "nodetool compactionstats, compaction progress, Cassandra monitoring, active compactions"
---

# nodetool compactionstats

Displays statistics about currently running compactions and pending compaction tasks.

---

## Synopsis

```bash
nodetool [connection_options] compactionstats [-H]
```

## Description

`nodetool compactionstats` shows:

- Currently active compaction operations
- Progress of each compaction
- Pending compaction tasks by keyspace
- Compaction throughput

This is essential for monitoring compaction health and identifying backlogs.

---

## Options

| Option | Description |
|--------|-------------|
| `-H, --human-readable` | Display sizes in human-readable format |
| `-V, --vtable` | Use virtual table format for output |

---

## Output Example

```
pending tasks: 15
- my_keyspace.users: 8
- my_keyspace.orders: 7
          id                compaction type        keyspace           table       completed           total      unit   progress
          abc123-def4-...        Compaction     my_keyspace           users      1234567890      2345678901     bytes     52.65%
          def456-abc7-...        Compaction     my_keyspace          orders       567890123      1234567890     bytes     46.01%
          ghi789-jkl0-...        Validation     my_keyspace           users        45678901       123456789     bytes     37.00%
Active compaction remaining time :   0h12m34s
```

Note: The output includes pending tasks broken down by keyspace and table, plus a per-compaction `id` column (unless `-V/--vtable` is used).

---

## Output Fields

| Field | Description |
|-------|-------------|
| pending tasks | Total compaction tasks waiting to run (with per-keyspace.table breakdown) |
| id | Unique identifier for the active compaction operation |
| compaction type | Type of operation (Compaction, Validation, Cleanup, etc.) |
| keyspace | Keyspace being compacted |
| table | Table being compacted |
| completed | Bytes processed so far |
| total | Total bytes to process |
| unit | Unit of measurement |
| progress | Percentage complete |

### Compaction Types

| Type | Description |
|------|-------------|
| Compaction | Regular SSTable compaction |
| Validation | Building Merkle tree for repair |
| Cleanup | Removing data not owned by node |
| Scrub | Rebuilding corrupted SSTables |
| Upgrade | Upgrading SSTable format |
| Index_build | Building secondary index |
| Anticompaction | Splitting SSTables for incremental repair |

---

## Interpreting Results

### Healthy State

```
pending tasks: 0
Active compaction remaining time :        n/a
```

No active compactions and no backlog.

### Active Compaction

```
pending tasks: 3
          compaction type        keyspace           table       completed           total      unit   progress
               Compaction     my_keyspace           users      1234567890      2345678901     bytes     52.65%
Active compaction remaining time :   0h05m23s
```

Normal operation with manageable workload.

### Compaction Backlog

```
pending tasks: 150
          compaction type        keyspace           table       completed           total      unit   progress
               Compaction     my_keyspace           users      1234567890      2345678901     bytes     52.65%
Active compaction remaining time :   2h45m12s
```

!!! danger "High Pending Tasks"
    Large pending task count indicates:

    - Writes exceeding compaction capacity
    - Insufficient compaction throughput
    - Need to tune compaction settings

    **Actions:**
    - Increase compaction throughput
    - Add more concurrent compactors
    - Reduce write rate if possible
    - Review compaction strategy

### Multiple Active Compactions

```
pending tasks: 10
          compaction type        keyspace           table       completed           total      unit   progress
               Compaction     my_keyspace           users      1234567890      2345678901     bytes     52.65%
               Compaction     my_keyspace          orders       567890123      1234567890     bytes     46.01%
               Compaction      other_ks           events       123456789       234567890     bytes     52.63%
               Compaction      other_ks            logs        234567890       345678901     bytes     67.95%
```

Multiple concurrent compactors running (controlled by `concurrent_compactors`).

---

## When to Use

### Monitor Compaction Health

```bash
# Periodic check
nodetool compactionstats

# Continuous monitoring
watch -n 5 'nodetool compactionstats'
```

### During High Write Load

Monitor for backlog buildup:

```bash
watch -n 2 'nodetool compactionstats | head -5'
```

### During Repair

Validation compactions appear during repair:

```bash
nodetool compactionstats | grep Validation
```

### After Adding Data

After bulk loads or migrations:

```bash
# Watch compaction catch up
watch -n 10 'nodetool compactionstats'
```

---

## Examples

### Basic Usage

```bash
nodetool compactionstats
```

### Human-Readable Output

```bash
nodetool compactionstats -H
```

Output:
```
pending tasks: 15
          compaction type        keyspace           table       completed           total      unit   progress
               Compaction     my_keyspace           users           1.2 GB           2.3 GB   bytes     52.65%
```

### Check Pending Tasks Only

```bash
nodetool compactionstats | head -1
```

### Monitor Continuously

```bash
watch -n 5 'nodetool compactionstats -H'
```

### Compare Across Nodes

```bash
for node in node1 node2 node3; do
    echo "=== $node ==="
    ssh "$node" "nodetool compactionstats | head -3"
done
```

---

## Managing Compaction Backlog

### Increase Throughput

```bash
# Check current throughput
nodetool getcompactionthroughput

# Increase throughput (MB/s)
nodetool setcompactionthroughput 256
```

### Add Concurrent Compactors

```bash
# Check current setting
nodetool getconcurrentcompactors

# Increase (use cautiously)
nodetool setconcurrentcompactors 4
```

!!! warning "Concurrent Compactors"
    More compactors = more parallel I/O. Only increase if disk can handle it.

### Stop Non-Critical Compactions

```bash
# Stop current compactions (for emergency)
nodetool stop COMPACTION

# Better: Stop specific types
nodetool stop INDEX_BUILD
```

---

## Pending Tasks Analysis

### Understanding Pending Count

```
pending tasks: 150
```

Pending tasks accumulate when:

| Cause | Solution |
|-------|----------|
| High write rate | Increase throughput/compactors |
| Large SSTables | Tune compaction strategy |
| Slow disks | Improve I/O capacity |
| Repairs running | Normal during repair |
| Insufficient threads | Increase compactors |

### Checking Task Distribution

```bash
# See which tables have pending compactions
nodetool compactionstats -H
```

Tables with consistently high pending may need:
- Different compaction strategy
- More frequent cleanup
- Data model review

---

## Compaction Throughput

### Current Setting

```bash
nodetool getcompactionthroughput
```

### Adjust Throughput

```bash
# Increase to 256 MB/s
nodetool setcompactionthroughput 256

# Unlimited (not recommended)
nodetool setcompactionthroughput 0
```

!!! tip "Throughput Guidelines"
    - Default: 64 MB/s
    - SSD clusters: 256-512 MB/s
    - HDD clusters: 64-128 MB/s
    - Monitor disk utilization when increasing

---

## Warning Signs

### Continuous Backlog Growth

```bash
# Check every minute
while true; do
    echo "$(date): $(nodetool compactionstats | head -1)"
    sleep 60
done
```

If pending continuously increases, action required.

### Very Long Compactions

Compactions running for hours may indicate:

- Very large SSTables
- Slow disk I/O
- Memory pressure (GC during compaction)

### High CPU During Compaction

Check with system tools:

```bash
top -p $(pgrep -f CassandraDaemon)
```

Compression/decompression is CPU-intensive.

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [getcompactionthroughput](getcompactionthroughput.md) | Check throughput setting |
| [setcompactionthroughput](setcompactionthroughput.md) | Adjust throughput |
| [compact](compact.md) | Force compaction |
| [tablestats](tablestats.md) | SSTable counts per table |