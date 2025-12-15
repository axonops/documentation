---
title: "Cassandra Metrics Reference"
description: "Cassandra JMX metrics reference. Key metrics for monitoring and alerting."
meta:
  - name: keywords
    content: "Cassandra JMX metrics, monitoring metrics, performance metrics"
---

# Cassandra Metrics Reference

Apache Cassandra exposes 500+ metrics via JMX using the Dropwizard Metrics library. This reference provides comprehensive documentation of all metrics with recommended thresholds.

## Metrics Overview

Cassandra metrics follow this naming pattern:

```
org.apache.cassandra.metrics:type={Type},keyspace={ks},scope={scope},name={MetricName}
```

### Metric Types

| Type | Description |
|------|-------------|
| **Timer** | Latency distribution (count, mean, percentiles) |
| **Counter** | Cumulative count |
| **Gauge** | Point-in-time value |
| **Histogram** | Value distribution |
| **Meter** | Rate of events |

---

## Client Request Metrics

**Type**: `ClientRequest`

### Read Latency

**ObjectName**: `org.apache.cassandra.metrics:type=ClientRequest,scope=Read,name=Latency`

| Attribute | Type | Description |
|-----------|------|-------------|
| `Count` | long | Total reads |
| `Mean` | double | Mean latency (μs) |
| `50thPercentile` | double | p50 latency |
| `75thPercentile` | double | p75 latency |
| `95thPercentile` | double | p95 latency |
| `99thPercentile` | double | p99 latency |
| `999thPercentile` | double | p999 latency |
| `Max` | double | Maximum latency |
| `OneMinuteRate` | double | Reads per second |

**Thresholds**:

| Percentile | Warning | Critical |
|------------|---------|----------|
| p50 | 5ms | 20ms |
| p99 | 50ms | 500ms |
| p999 | 200ms | 2000ms |

### Write Latency

**ObjectName**: `org.apache.cassandra.metrics:type=ClientRequest,scope=Write,name=Latency`

| Attribute | Type | Description |
|-----------|------|-------------|
| `Count` | long | Total writes |
| `Mean` | double | Mean latency (μs) |
| `50thPercentile` | double | p50 latency |
| `99thPercentile` | double | p99 latency |
| `OneMinuteRate` | double | Writes per second |

**Thresholds**:

| Percentile | Warning | Critical |
|------------|---------|----------|
| p50 | 2ms | 10ms |
| p99 | 10ms | 100ms |

### Timeouts

**ObjectName**: `org.apache.cassandra.metrics:type=ClientRequest,scope={Read|Write},name=Timeouts`

| Attribute | Description |
|-----------|-------------|
| `Count` | Total timeout count |
| `OneMinuteRate` | Timeouts per second |

**Alert**: Any timeouts warrant investigation.

### Unavailables

**ObjectName**: `org.apache.cassandra.metrics:type=ClientRequest,scope={Read|Write},name=Unavailables`

| Attribute | Description |
|-----------|-------------|
| `Count` | Total unavailable errors |
| `OneMinuteRate` | Unavailables per second |

**Alert**: Indicates insufficient replicas available for requested consistency level.

### Failures

**ObjectName**: `org.apache.cassandra.metrics:type=ClientRequest,scope={Read|Write},name=Failures`

| Attribute | Description |
|-----------|-------------|
| `Count` | Total failures |
| `OneMinuteRate` | Failures per second |

---

## Table Metrics

**Type**: `Table`

Per-keyspace and per-table metrics.

### Read/Write Latency (Per Table)

**ObjectName**: `org.apache.cassandra.metrics:type=Table,keyspace={ks},scope={table},name=ReadLatency`

Same attributes as ClientRequest latency but scoped to specific table.

### Live SSTable Count

**ObjectName**: `org.apache.cassandra.metrics:type=Table,keyspace={ks},scope={table},name=LiveSSTableCount`

| Attribute | Description |
|-----------|-------------|
| `Value` | Number of live SSTables |

**Threshold**: > 20-30 SSTables may indicate compaction lag.

### SSTable Size

**ObjectName**: `org.apache.cassandra.metrics:type=Table,keyspace={ks},scope={table},name=TotalDiskSpaceUsed`

| Attribute | Description |
|-----------|-------------|
| `Count` | Bytes on disk |

### Memtable Size

**ObjectName**: `org.apache.cassandra.metrics:type=Table,keyspace={ks},scope={table},name=MemtableLiveDataSize`

| Attribute | Description |
|-----------|-------------|
| `Value` | Bytes in memtable |

### Partition Size

**ObjectName**: `org.apache.cassandra.metrics:type=Table,keyspace={ks},scope={table},name=EstimatedPartitionSizeHistogram`

| Attribute | Description |
|-----------|-------------|
| `Value` | Histogram array of partition sizes |

**Alert**: Partitions > 100MB are problematic.

### Tombstone Scans

**ObjectName**: `org.apache.cassandra.metrics:type=Table,keyspace={ks},scope={table},name=TombstoneScannedHistogram`

| Attribute | Description |
|-----------|-------------|
| `Value` | Histogram of tombstones scanned per read |

**Threshold**: > 1000 tombstones/read indicates query optimization needed.

### Bloom Filter

**ObjectName**: `org.apache.cassandra.metrics:type=Table,keyspace={ks},scope={table},name=BloomFilterFalseRatio`

| Attribute | Description |
|-----------|-------------|
| `Value` | False positive ratio (0.0-1.0) |

**Threshold**: > 0.01 may indicate need for larger bloom filters.

### Speculative Retries

**ObjectName**: `org.apache.cassandra.metrics:type=Table,keyspace={ks},scope={table},name=SpeculativeRetries`

| Attribute | Description |
|-----------|-------------|
| `Count` | Number of speculative retries |

---

## Compaction Metrics

**Type**: `Compaction`

### Pending Tasks

**ObjectName**: `org.apache.cassandra.metrics:type=Compaction,name=PendingTasks`

| Attribute | Description |
|-----------|-------------|
| `Value` | Pending compaction tasks |

**Thresholds**:

| Level | Value |
|-------|-------|
| Normal | < 5 |
| Warning | 5-20 |
| Critical | > 50 |

### Completed Tasks

**ObjectName**: `org.apache.cassandra.metrics:type=Compaction,name=CompletedTasks`

| Attribute | Description |
|-----------|-------------|
| `Value` | Completed compactions |

### Bytes Compacted

**ObjectName**: `org.apache.cassandra.metrics:type=Compaction,name=BytesCompacted`

| Attribute | Description |
|-----------|-------------|
| `Count` | Total bytes compacted |
| `OneMinuteRate` | Compaction throughput |

### Total Compactions

**ObjectName**: `org.apache.cassandra.metrics:type=Compaction,name=TotalCompactionsCompleted`

| Attribute | Description |
|-----------|-------------|
| `Count` | Total completed compactions |
| `OneMinuteRate` | Compactions per second |

---

## Thread Pool Metrics

**Type**: `ThreadPools`

### Stage Pools

| Pool | Path | Description |
|------|------|-------------|
| `ReadStage` | request | Processes reads |
| `MutationStage` | request | Processes writes |
| `CounterMutationStage` | request | Counter writes |
| `ViewMutationStage` | request | MV updates |
| `GossipStage` | internal | Gossip processing |
| `CompactionExecutor` | internal | Compaction |
| `MemtableFlushWriter` | internal | Memtable flush |
| `MemtablePostFlush` | internal | Post-flush |
| `Native-Transport-Requests` | transport | CQL requests |

### Active Tasks

**ObjectName**: `org.apache.cassandra.metrics:type=ThreadPools,path={path},scope={stage},name=ActiveTasks`

| Attribute | Description |
|-----------|-------------|
| `Value` | Currently active tasks |

### Pending Tasks

**ObjectName**: `org.apache.cassandra.metrics:type=ThreadPools,path={path},scope={stage},name=PendingTasks`

| Attribute | Description |
|-----------|-------------|
| `Value` | Tasks waiting in queue |

**Alert**: Pending tasks > 0 for extended periods indicates overload.

### Blocked Tasks

**ObjectName**: `org.apache.cassandra.metrics:type=ThreadPools,path={path},scope={stage},name=CurrentlyBlockedTasks`

| Attribute | Description |
|-----------|-------------|
| `Count` | Total blocked tasks |
| `Value` | Currently blocked |

**Alert**: Any blocked tasks indicate severe overload.

### Completed Tasks

**ObjectName**: `org.apache.cassandra.metrics:type=ThreadPools,path={path},scope={stage},name=CompletedTasks`

| Attribute | Description |
|-----------|-------------|
| `Value` | Total completed tasks |

---

## Cache Metrics

**Type**: `Cache`

### Key Cache

| Metric | ObjectName Suffix | Description |
|--------|-------------------|-------------|
| Size | `scope=KeyCache,name=Size` | Entries in cache |
| Capacity | `scope=KeyCache,name=Capacity` | Max entries |
| Hits | `scope=KeyCache,name=Hits` | Cache hits |
| Requests | `scope=KeyCache,name=Requests` | Total requests |
| HitRate | `scope=KeyCache,name=HitRate` | Hit ratio |

**Target**: > 85% hit rate.

### Row Cache

| Metric | ObjectName Suffix | Description |
|--------|-------------------|-------------|
| Size | `scope=RowCache,name=Size` | Entries in cache |
| Capacity | `scope=RowCache,name=Capacity` | Max entries |
| Hits | `scope=RowCache,name=Hits` | Cache hits |
| HitRate | `scope=RowCache,name=HitRate` | Hit ratio |

### Counter Cache

| Metric | ObjectName Suffix | Description |
|--------|-------------------|-------------|
| Size | `scope=CounterCache,name=Size` | Entries in cache |
| HitRate | `scope=CounterCache,name=HitRate` | Hit ratio |

### Chunk Cache (Off-Heap)

**ObjectName**: `org.apache.cassandra.metrics:type=Cache,scope=ChunkCache,name={metric}`

| Metric | Description |
|--------|-------------|
| `Size` | Cached chunks |
| `Misses` | Cache misses |
| `MissLatency` | Miss latency |

---

## Dropped Messages Metrics

**Type**: `DroppedMessage`

**ObjectName**: `org.apache.cassandra.metrics:type=DroppedMessage,scope={type},name=Dropped`

| Type | Description |
|------|-------------|
| `MUTATION` | Dropped writes |
| `READ` | Dropped reads |
| `READ_REPAIR` | Dropped read repairs |
| `RANGE_SLICE` | Dropped range queries |
| `COUNTER_MUTATION` | Dropped counter writes |
| `HINT` | Dropped hints |
| `PAGED_RANGE` | Dropped paged queries |

| Attribute | Description |
|-----------|-------------|
| `Count` | Total dropped |
| `OneMinuteRate` | Drops per second |

**Alert**: Any dropped messages indicate severe issues.

---

## Storage Metrics

**Type**: `Storage`

### Disk Space

**ObjectName**: `org.apache.cassandra.metrics:type=Storage,name=Load`

| Attribute | Description |
|-----------|-------------|
| `Count` | Total bytes on disk |

### Exceptions

**ObjectName**: `org.apache.cassandra.metrics:type=Storage,name=Exceptions`

| Attribute | Description |
|-----------|-------------|
| `Count` | Storage exceptions |

---

## Connection Metrics

**Type**: `Connection`

### Client Connections

**ObjectName**: `org.apache.cassandra.metrics:type=Client,name=connectedNativeClients`

| Attribute | Description |
|-----------|-------------|
| `Value` | Connected CQL clients |

### Inter-node Connections

**ObjectName**: `org.apache.cassandra.metrics:type=Connection,scope={host},name=*`

| Metric | Description |
|--------|-------------|
| `CommandPendingTasks` | Pending requests |
| `CommandCompletedTasks` | Completed requests |
| `CommandDroppedTasks` | Dropped requests |

---

## Streaming Metrics

**Type**: `Streaming`

**ObjectName**: `org.apache.cassandra.metrics:type=Streaming,scope={host},name=*`

| Metric | Description |
|--------|-------------|
| `IncomingBytes` | Bytes received |
| `OutgoingBytes` | Bytes sent |

---

## JVM Metrics

Standard JVM MBeans:

### Heap Memory

**ObjectName**: `java.lang:type=Memory`

| Attribute | Description |
|-----------|-------------|
| `HeapMemoryUsage.used` | Current heap usage |
| `HeapMemoryUsage.max` | Maximum heap |

**Threshold**: > 70% warning, > 85% critical.

### Garbage Collection

**ObjectName**: `java.lang:type=GarbageCollector,name={collector}`

| Attribute | Description |
|-----------|-------------|
| `CollectionCount` | Total collections |
| `CollectionTime` | Total collection time (ms) |

---

## Metrics Categories Summary

| Category | Key Metrics | Alert Focus |
|----------|-------------|-------------|
| **Client Requests** | Latency, Timeouts, Unavailables | Response times |
| **Tables** | SSTable count, Partition size | Data model |
| **Compaction** | Pending tasks | Maintenance lag |
| **Thread Pools** | Pending, Blocked | Capacity |
| **Caches** | Hit rate | Efficiency |
| **Dropped Messages** | All types | Overload |

---

## Next Steps

- **[MBeans Reference](../mbeans/index.md)** - MBean operations
- **[Monitoring Guide](../../monitoring/index.md)** - End-to-end monitoring
- **[Alerting](../../monitoring/alerting/index.md)** - Alert configuration
- **[Troubleshooting](../../troubleshooting/index.md)** - Using metrics for diagnosis
