---
title: "nodetool tpstats"
description: "Display thread pool statistics for Cassandra stages using nodetool tpstats command."
meta:
  - name: keywords
    content: "nodetool tpstats, thread pool stats, Cassandra threads, SEDA stages"
---

# nodetool tpstats

Displays statistics for thread pools and message queues, providing insight into Cassandra's internal task processing and potential bottlenecks.

---

## Synopsis

```bash
nodetool [connection_options] tpstats [options]
```
See [connection options](index.md#connection-options) for connection options.

## Description

`nodetool tpstats` shows the status of Cassandra's thread pools, which handle different types of operations. This is essential for diagnosing performance issues and identifying bottlenecks.

---

## Options

| Option | Description |
|--------|-------------|
| `-F, --format` | Output format (json, yaml) |
| `-v, --verbose` | Show detailed thread pool sizes (core, max, active) |

---

## Output Format

```
Pool Name                         Active   Pending      Completed   Blocked  All time blocked
ReadStage                              2         0        1234567         0                 0
MutationStage                          4         3        9876543         0                 0
CounterMutationStage                   0         0           1234         0                 0
GossipStage                            0         0         567890         0                 0
RequestResponseStage                   0         0        8765432         0                 0
AntiEntropyStage                       0         0            123         0                 0
MigrationStage                         0         0             12         0                 0
MiscStage                              0         0           5678         0                 0
CompactionExecutor                     2         0         234567         0                 0
MemtableFlushWriter                    1         0          12345         0                 0
MemtablePostFlush                      0         0          12345         0                 0
MemtableReclaimMemory                  0         0          12345         0                 0
PendingRangeCalculator                 0         0              5         0                 0
Sampler                                0         0              0         0                 0
SecondaryIndexManagement               0         0             50         0                 0
HintsDispatcher                        0         0            100         0                 0
Native-Transport-Requests              8        12       12345678         0                 0
ViewMutationStage                      0         0              0         0                 0
ViewBuildExecutor                      0         0              0         0                 0

Message type           Dropped    Latency waiting in queue (micros)
                                             50%        75%        95%        98%        99%       Max
READ                         0            125.0      234.0      567.0      890.0     1234.0    5678.0
RANGE_SLICE                  0            234.0      345.0      678.0      901.0     1345.0    6789.0
MUTATION                     0             89.0      123.0      345.0      456.0      567.0    2345.0
READ_REPAIR                  0            456.0      567.0      789.0     1012.0     1234.0    7890.0
COUNTER_MUTATION             0            123.0      234.0      456.0      567.0      678.0    3456.0
HINT                         0             45.0       67.0      123.0      178.0      234.0    1234.0
REQUEST_RESPONSE             0             34.0       45.0       89.0      123.0      156.0     890.0
```

---

## Output Fields

### Thread Pool Statistics

| Field | Description |
|-------|-------------|
| Pool Name | Name of the thread pool |
| Active | Threads currently executing tasks |
| Pending | Tasks waiting for a thread |
| Completed | Total tasks completed |
| Blocked | Tasks currently blocked |
| All time blocked | Total tasks ever blocked |

### Message Statistics

| Field | Description |
|-------|-------------|
| Message type | Type of inter-node message |
| Dropped | Messages dropped due to timeout |
| Latency percentiles | Time spent waiting in queue |

---

## Key Thread Pools

### Read/Write Operations

| Pool | Purpose | Warning Signs |
|------|---------|---------------|
| ReadStage | Processes local reads | High pending = disk bottleneck |
| MutationStage | Processes local writes | High pending = write overload |
| Native-Transport-Requests | CQL request handling | High pending = client overload |

### Background Operations

| Pool | Purpose | Warning Signs |
|------|---------|---------------|
| CompactionExecutor | Compaction tasks | High pending = compaction behind |
| MemtableFlushWriter | Memtable flushes | High pending = flush pressure |
| AntiEntropyStage | Repair operations | High active during repair |

### Cluster Communication

| Pool | Purpose | Warning Signs |
|------|---------|---------------|
| GossipStage | Gossip protocol | Should rarely be active |
| RequestResponseStage | Inter-node responses | High pending = network issues |
| HintsDispatcher | Hint delivery | High pending = hints accumulating |

---

## Interpreting Results

### Healthy State

```
Pool Name                         Active   Pending      Completed   Blocked  All time blocked
ReadStage                              1         0        1234567         0                 0
MutationStage                          2         0        9876543         0                 0
CompactionExecutor                     1         0         234567         0                 0
```

- Active threads = work being done
- Pending = 0 (no backlog)
- Blocked = 0 (no contention)

### Read Bottleneck

```
Pool Name                         Active   Pending      Completed   Blocked  All time blocked
ReadStage                             32       150        1234567         0                 0
```

!!! danger "High Pending Reads"
    High pending on ReadStage indicates:

    - Disk I/O bottleneck
    - Too many concurrent reads
    - Large partition reads
    - Insufficient read threads

    **Actions:**
    - Check disk latency
    - Review read patterns
    - Consider increasing `concurrent_reads`

### Write Overload

```
Pool Name                         Active   Pending      Completed   Blocked  All time blocked
MutationStage                         64       500        9876543         0                 0
```

!!! danger "High Pending Mutations"
    High pending on MutationStage indicates:

    - Write rate exceeds capacity
    - Memtable flush pressure
    - Commit log bottleneck

    **Actions:**
    - Reduce write rate
    - Check flush backpressure
    - Verify commit log disk performance

### Compaction Backlog

```
Pool Name                         Active   Pending      Completed   Blocked  All time blocked
CompactionExecutor                     4       200         234567         0                 0
```

!!! warning "Compaction Falling Behind"
    High pending compactions indicate:

    - Writes faster than compaction
    - Insufficient compaction throughput
    - Large SSTable accumulation

    **Actions:**
    - Increase compaction throughput
    - Check I/O capacity
    - Review compaction strategy settings

### Hints Accumulating

```
Pool Name                         Active   Pending      Completed   Blocked  All time blocked
HintsDispatcher                        1       500            100         0                 0
```

!!! warning "Hint Backlog"
    High pending hints indicate:

    - Nodes were recently unavailable
    - Network issues between nodes
    - Hint delivery slower than accumulation

    **Actions:**
    - Check cluster connectivity
    - Monitor node health
    - Consider increasing hint delivery rate

---

## Dropped Messages

```
Message type           Dropped
READ                       125
MUTATION                    50
```

!!! danger "Dropped Messages Are Critical"
    Dropped messages indicate:

    - Requests timing out
    - Overload conditions
    - Data inconsistency risk

    **Zero dropped messages is the target.**

### Common Causes of Dropped Messages

| Message Type | Common Causes |
|--------------|---------------|
| READ | Slow disks, large partitions, GC pauses |
| MUTATION | Write overload, memtable flush pressure |
| READ_REPAIR | Repair taking too long |
| REQUEST_RESPONSE | Network latency, cross-DC communication |

### Investigating Dropped Messages

```bash
# Check over time
watch -n 5 'nodetool tpstats | grep -E "Dropped|READ|MUTATION"'

# Check message latency
nodetool proxyhistograms
```

---

## Examples

### Basic Usage

```bash
nodetool tpstats
```

### JSON Output for Parsing

```bash
nodetool tpstats -F json
```

### Verbose Output with Thread Pool Sizes

```bash
nodetool tpstats -v
```

### Monitor Thread Pools Continuously

```bash
watch -n 2 'nodetool tpstats | head -20'
```

### Check for Any Blocked/Pending

```bash
nodetool tpstats | awk '$3 > 0 || $5 > 0 {print}'
```

### Compare Across Nodes

```bash
#!/bin/bash
# Compare thread pool stats across all nodes using SSH

for node in node1 node2 node3; do
    echo "=== $node ==="
    ssh "$node" "nodetool tpstats" | grep -E "ReadStage|MutationStage|Pending"
done
```

---

## Thread Pool Sizing

### Configuration Parameters

| Parameter | Default | Thread Pool |
|-----------|---------|-------------|
| `concurrent_reads` | 32 | ReadStage |
| `concurrent_writes` | 32 | MutationStage |
| `concurrent_counter_writes` | 32 | CounterMutationStage |
| `concurrent_compactors` | auto | CompactionExecutor |

### When to Adjust

Increase thread pool sizes when:

1. **Pending consistently > 0** over time
2. **Hardware has capacity** (CPU, I/O not maxed)
3. **Latency is acceptable** (not just throughput)

!!! warning "Thread Pool Tuning"
    More threads doesn't always help:

    - More threads = more contention
    - I/O-bound operations won't benefit from more threads
    - Monitor actual resource utilization first

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [info](info.md) | General node information |
| [proxyhistograms](proxyhistograms.md) | Request latency histograms |
| [tablestats](tablestats.md) | Table-level statistics |
| [compactionstats](compactionstats.md) | Active compaction details |
| [netstats](netstats.md) | Network/streaming statistics |
| [gcstats](gcstats.md) | GC statistics |