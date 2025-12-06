# nodetool tpstats

Displays thread pool statistics for all Cassandra thread pools, providing visibility into task queuing and processing.

## Synopsis

```bash
nodetool [connection_options] tpstats
```

## Description

The `tpstats` command shows the current state of all thread pools used by Cassandra for processing various operations. Thread pools manage concurrent execution of reads, writes, compactions, and other internal operations. Monitoring these statistics helps identify bottlenecks and capacity issues.

The output includes active tasks, pending tasks, completed tasks, and blocked tasks for each thread pool, followed by message drop statistics.

## Connection Options

| Option | Description |
|--------|-------------|
| -h, --host | Hostname or IP address to connect to (default: localhost) |
| -p, --port | JMX port number (default: 7199) |
| -F, --format | Output format: json, yaml (Cassandra 4.0+) |

## Output Format

The output consists of two sections:

1. **Thread Pool Statistics** - Current state of each thread pool
2. **Message Drops** - Count of dropped messages by type

## Thread Pool Statistics

### Output Fields

| Field | Description |
|-------|-------------|
| Pool Name | Name identifying the thread pool function |
| Active | Number of tasks currently executing |
| Pending | Number of tasks waiting to execute |
| Completed | Total tasks completed since startup |
| Blocked | Tasks that could not be queued (back-pressure applied) |
| All time blocked | Cumulative blocked count since startup |

### Thread Pools Reference

| Pool Name | Purpose | Warning Threshold |
|-----------|---------|-------------------|
| ReadStage | Local read operations | Pending > 0 sustained |
| MutationStage | Local write operations | Pending > 0 sustained |
| CounterMutationStage | Counter write operations | Pending > 0 sustained |
| ViewMutationStage | Materialized view updates | Pending > 0 sustained |
| GossipStage | Gossip protocol messages | Blocked > 0 |
| RequestResponseStage | Inter-node request/response handling | Pending > 0 |
| ReadRepairStage | Background read repair operations | High pending = consistency overhead |
| CompactionExecutor | Compaction task execution | High pending = falling behind |
| MemtableFlushWriter | Memtable flush to SSTable | Pending > 2 = flush bottleneck |
| MemtablePostFlush | Post-flush cleanup | Pending > 0 |
| MemtableReclaimMemory | Memtable memory reclamation | Pending > 0 |
| HintsDispatcher | Hint delivery to recovered nodes | Pending > 0 = hints accumulating |
| MigrationStage | Schema migration handling | N/A |
| MiscStage | Miscellaneous operations | N/A |
| InternalResponseStage | Internal coordination | N/A |
| AntiEntropyStage | Repair operations | Pending during repair is normal |
| CacheCleanupExecutor | Cache maintenance | N/A |
| Native-Transport-Requests | CQL request handling | Pending > 0 = client bottleneck |
| ValidationExecutor | Merkle tree validation (repair) | Active during repair is normal |
| ViewBuildExecutor | Materialized view construction | Pending = view build in progress |
| SecondaryIndexManagement | Secondary index maintenance | N/A |
| PendingRangeCalculator | Token range calculations | N/A |
| Sampler | Request sampling | N/A |

## Message Drop Statistics

### Output Fields

| Field | Description |
|-------|-------------|
| Message type | Type of inter-node message |
| Dropped | Number of messages that timed out before processing |
| Latency percentiles | Queue wait time at 50%, 95%, 99%, and Max percentiles |

### Message Types

| Message Type | Cause of Drops | Investigation |
|--------------|----------------|---------------|
| READ | read_request_timeout exceeded | Disk I/O, data model, partition size |
| RANGE_SLICE | range_request_timeout exceeded | Large partitions, inefficient queries |
| MUTATION | write_request_timeout exceeded | Disk I/O, commitlog, write volume |
| COUNTER_MUTATION | counter_write_request_timeout exceeded | Counter table design |
| HINT | hint timeout | Hint accumulation, node recovery |
| READ_REPAIR | read_repair timeout | Network latency, repair overhead |
| REQUEST_RESPONSE | request_timeout exceeded | Network issues, node overload |
| BATCH_STORE | batch timeout | Batch size, batchlog pressure |
| BATCH_REMOVE | batch timeout | Batchlog cleanup issues |

## Examples

### Basic Thread Pool Statistics

```bash
nodetool tpstats
```

**Output:**
```
Pool Name                         Active   Pending      Completed   Blocked  All time blocked
ReadStage                              2         0       98765432         0                 0
MutationStage                          4         0       87654321         0                 0
CounterMutationStage                   0         0              0         0                 0
ViewMutationStage                      0         0              0         0                 0
GossipStage                            0         0        1234567         0                 0
RequestResponseStage                   0         0       76543210         0                 0
ReadRepairStage                        0         0         123456         0                 0
CompactionExecutor                     2         5         234567         0                 0
MemtableFlushWriter                    1         0          12345         0                 0
MemtablePostFlush                      0         0          12345         0                 0
MemtableReclaimMemory                  0         0          12345         0                 0
HintsDispatcher                        0         0           1234         0                 0
Native-Transport-Requests              8         0      123456789         0                 0
ValidationExecutor                     0         0              0         0                 0
ViewBuildExecutor                      0         0              0         0                 0

Message type           Dropped   Latency waiting in queue (micros)
                                              50%        95%        99%        Max
READ                         0                42         98        210       3450
RANGE_SLICE                  0                56        145        298       5670
MUTATION                     0                35         87        175       2890
COUNTER_MUTATION             0                 0          0          0          0
HINT                         0                23         67        134       1890
READ_REPAIR                  0                89        234        456       6780
REQUEST_RESPONSE             0                12         34         78       1234
BATCH_STORE                  0                45        123        234       3456
BATCH_REMOVE                 0                34         89        178       2345
```

### JSON Output (Cassandra 4.0+)

```bash
nodetool tpstats -F json
```

### Filter for Issues Only

```bash
# Show only pools with pending or blocked tasks
nodetool tpstats | awk 'NR==1 || $3>0 || $5>0'
```

### Monitor Drops Only

```bash
# Show only message types with drops
nodetool tpstats | grep -A 20 "Message type" | awk 'NR==1 || $2>0'
```

## Interpreting Results

### Healthy State

A healthy node typically shows:
- Pending = 0 for most pools (transient non-zero is acceptable)
- Blocked = 0 for all pools
- Dropped = 0 for all message types

### Warning Indicators

| Condition | Indication | Investigation |
|-----------|------------|---------------|
| Pending > 0 (sustained) | Thread pool cannot keep up | Increase threads, reduce load, optimize operations |
| Blocked > 0 | Back-pressure applied | Immediate capacity issue |
| All time blocked > 0 | Historical capacity issues | Review sizing and workload |
| Dropped > 0 | Operations timing out | Critical - data consistency at risk |

### Common Patterns

**Read Bottleneck:**
```
ReadStage                             12        45       98765432         0                 0
```
- High pending in ReadStage
- Investigate: Disk I/O, partition sizes, read latency

**Write Bottleneck:**
```
MutationStage                         16        78       87654321         0                 0
```
- High pending in MutationStage
- Investigate: Commitlog disk, memtable flush, write volume

**Compaction Backlog:**
```
CompactionExecutor                     4       128         234567         0                 0
```
- High pending in CompactionExecutor
- Investigate: Compaction throughput, disk I/O, compaction strategy

**Flush Bottleneck:**
```
MemtableFlushWriter                    2         8          12345         0                 0
```
- High pending in MemtableFlushWriter
- Investigate: Disk I/O, memtable size, concurrent_writes

## Common Use Cases

### Health Check Script

```bash
#!/bin/bash
# Alert on any dropped messages or blocked threads

DROPS=$(nodetool tpstats | awk '/^READ|^MUTATION|^RANGE_SLICE/ {sum+=$2} END {print sum}')
BLOCKED=$(nodetool tpstats | awk 'NR>1 && !/Message/ {sum+=$5} END {print sum}')

if [ "$DROPS" -gt 0 ]; then
    echo "CRITICAL: $DROPS dropped messages detected"
    exit 2
fi

if [ "$BLOCKED" -gt 0 ]; then
    echo "WARNING: $BLOCKED blocked tasks detected"
    exit 1
fi

echo "OK: No drops or blocks"
exit 0
```

### Continuous Monitoring

```bash
# Watch thread pools every 5 seconds
watch -n 5 'nodetool tpstats | head -20'
```

### Prometheus Metrics Export

```bash
#!/bin/bash
# Export metrics in Prometheus format
nodetool tpstats | awk '
    NR>1 && !/Message/ && !/^$/ {
        pool=$1
        gsub(/-/, "_", pool)
        print "cassandra_threadpool_active{pool=\"" pool "\"} " $2
        print "cassandra_threadpool_pending{pool=\"" pool "\"} " $3
        print "cassandra_threadpool_completed{pool=\"" pool "\"} " $4
        print "cassandra_threadpool_blocked{pool=\"" pool "\"} " $5
    }
'
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Command executed successfully |
| 1 | Error connecting to JMX or executing command |

## Related Commands

- [nodetool info](info.md) - Node memory and cache statistics
- [nodetool tablestats](tablestats.md) - Per-table read/write latencies
- [nodetool compactionstats](compactionstats.md) - Compaction progress
- [nodetool netstats](netstats.md) - Network and streaming statistics

## Related Documentation

- [Monitoring - Key Metrics](../../../monitoring/key-metrics/index.md) - Understanding thread pool metrics
- [Troubleshooting - Read Timeout](../../../troubleshooting/playbooks/read-timeout.md) - Diagnosing read issues
- [Troubleshooting - Write Timeout](../../../troubleshooting/playbooks/write-timeout.md) - Diagnosing write issues
- [Performance - JVM Tuning](../../../performance/jvm-tuning/index.md) - Thread and memory optimization
- [Configuration - cassandra.yaml](../../../configuration/cassandra-yaml/index.md) - Thread pool configuration

## Version Information

Available in all Apache Cassandra versions. The `-F` format option was added in Cassandra 4.0. Thread pool names and availability may vary slightly between versions.
