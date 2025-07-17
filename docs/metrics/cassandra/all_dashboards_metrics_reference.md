# AxonOps All Dashboards Metrics Reference

This document provides a comprehensive reference of all metrics used across AxonOps dashboards, organized by metric prefix and category.

## Table of Contents

1. [System Metrics (host_)](#system-metrics-host_)
2. [JVM Metrics (jvm_)](#jvm-metrics-jvm_)
3. [Cassandra Metrics (cas_)](#cassandra-metrics-cas_)
4. [Client Metrics (client_)](#client-metrics-client_)
5. [Authentication Metrics](#authentication-metrics)
6. [Event-Based Monitoring](#event-based-monitoring)
7. [Special Functions and Attributes](#special-functions-and-attributes)

## System Metrics (host_)

System-level metrics collected from the operating system.

### CPU Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `host_CPU_Percent_Merge` | Merged CPU usage percentage | `time` (real/user/sys), `dc`, `rack`, `host_id` | System, Overview, Reporting |

### Memory Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `host_Memory_Used` | Used memory in bytes | `dc`, `rack`, `host_id` | System, Overview |
| `host_Memory_Free` | Free memory in bytes | `dc`, `rack`, `host_id` | System |
| `host_Memory_Total` | Total memory in bytes | `dc`, `rack`, `host_id` | System |
| `host_Memory_Buffers` | Buffer memory | `dc`, `rack`, `host_id` | System |
| `host_Memory_Cached` | Cached memory | `dc`, `rack`, `host_id` | System |

### Disk Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `host_Disk_UsedPercent` | Disk usage percentage | `mountpoint`, `dc`, `rack`, `host_id` | System, Overview, Reporting |
| `host_Disk_Used` | Used disk space in bytes | `mountpoint`, `dc`, `rack`, `host_id` | System, Reporting |
| `host_Disk_SectorsRead` | Disk sectors read | `partition`, `axonfunction` (rate), `dc`, `rack`, `host_id` | System, Reporting |
| `host_Disk_SectorsWrite` | Disk sectors written | `partition`, `axonfunction` (rate), `dc`, `rack`, `host_id` | System, Reporting |

### Network Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `host_Network_ReceiveBytes` | Network bytes received | `interface`, `axonfunction` (rate), `dc`, `rack`, `host_id` | System |
| `host_Network_TransmitBytes` | Network bytes transmitted | `interface`, `axonfunction` (rate), `dc`, `rack`, `host_id` | System |

## JVM Metrics (jvm_)

Java Virtual Machine metrics for monitoring Cassandra's JVM.

### Memory Pool Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `jvm_Memory_Heap` | Heap memory usage | `type` (usage/init/committed/max), `dc`, `rack`, `host_id` | System, Overview |
| `jvm_MemoryPool_*` | Specific memory pool metrics | `pool_name`, `type`, `dc`, `rack`, `host_id` | System |

### Garbage Collection Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `jvm_GarbageCollector_*` | GC metrics by collector | `collector_name`, `function` (CollectionTime/CollectionCount), `axonfunction` (rate), `dc`, `rack`, `host_id` | System, Table |
| `jvm_GarbageCollector_G1_Young_Generation` | G1 young gen GC | See above | System, Table |
| `jvm_GarbageCollector_Shenandoah_Cycles` | Shenandoah GC cycles | See above | Table |
| `jvm_GarbageCollector_Shenandoah_Pauses` | Shenandoah GC pauses | See above | Table |
| `jvm_GarbageCollector_ZGC` | ZGC metrics | See above | Table |

## Cassandra Metrics (cas_)

Cassandra-specific metrics.

### Client Connection Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `cas_Client_connectedNativeClients` | Connected native protocol clients | `dc`, `rack`, `host_id` | Application, Coordinator |

### Client Request Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `cas_ClientRequest_Latency` | Request latency at coordinator | `scope` (Read*/Write*/RangeSlice), `function` (percentiles/Count), `axonfunction` (rate), `dc`, `rack`, `host_id` | Overview, Coordinator, Reporting |
| `cas_ClientRequest_Timeouts` | Request timeouts | `scope` (Read/Write), `function` (Count), `axonfunction` (rate), `dc`, `rack`, `host_id` | Overview, Entropy |
| `cas_ClientRequest_Unavailables` | Unavailable exceptions | `scope` (Read/Write), `function` (Count), `axonfunction` (rate), `dc`, `rack`, `host_id` | Overview, Entropy |

### Cache Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `cas_Cache_*` | Cache statistics | `scope` (KeyCache/RowCache/CounterCache), `metric` (Capacity/Size/Hits/Requests), `dc`, `rack`, `host_id` | Cache |

### Compaction Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `cas_Compaction_TotalCompactionsCompleted` | Completed compactions | `axonfunction` (rate), `dc`, `rack`, `host_id` | Compactions |
| `cas_Compaction_BytesCompacted` | Bytes compacted | `axonfunction` (rate), `dc`, `rack`, `host_id` | Compactions |
| `cas_CompactionManager_*` | Compaction manager metrics | `metric` (PendingTasks/CompletedTasks), `dc`, `rack`, `host_id` | Compactions |

### Table Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `cas_Table_ReadLatency` | Local read latency | `keyspace`, `scope` (table), `function` (percentiles/Count), `axonfunction` (rate), `dc`, `rack`, `host_id` | Table |
| `cas_Table_WriteLatency` | Local write latency | See above | Table |
| `cas_Table_RangeLatency` | Local range query latency | See above | Table |
| `cas_Table_CoordinatorReadLatency` | Coordinator read latency | See above | Table |
| `cas_Table_CoordinatorWriteLatency` | Coordinator write latency | See above | Table |
| `cas_Table_CoordinatorScanLatency` | Coordinator range scan latency | See above | Table |
| `cas_Table_LiveDiskSpaceUsed` | Live data disk space | `keyspace`, `scope` (table), `function` (Count), `dc`, `rack`, `host_id` | Data, Table, Keyspace |
| `cas_Table_TotalDiskSpaceUsed` | Total disk space | See above | Data |
| `cas_Table_CompressionRatio` | Compression effectiveness | `keyspace`, `scope` (table), `dc`, `rack`, `host_id` | Data |
| `cas_Table_LiveSSTableCount` | Number of SSTables | See above | Data, Table |
| `cas_Table_MinPartitionSize` | Minimum partition size | See above | Data |
| `cas_Table_MeanPartitionSize` | Average partition size | See above | Data, Table |
| `cas_Table_MaxPartitionSize` | Maximum partition size | See above | Data, Table |
| `cas_Table_EstimatedPartitionCount` | Estimated partitions | See above | Table |
| `cas_Table_SSTablesPerReadHistogram` | SSTables per read | `function` (percentiles), See above | Table |
| `cas_Table_TombstoneScannedHistogram` | Tombstones scanned | See above | Table |
| `cas_Table_SpeculativeRetries` | Speculative retry attempts | `function` (Count), `axonfunction` (rate), See above | Table |
| `cas_Table_BloomFilterFalseRatio` | Bloom filter false positive ratio | See above | Table |
| `cas_Table_BloomFilterDiskSpaceUsed` | Bloom filter disk usage | See above | Table |
| `cas_Table_AllMemtablesHeapSize` | Memtable heap memory | See above | Table |
| `cas_Table_AllMemtablesOffHeapSize` | Memtable off-heap memory | See above | Table |

### Keyspace Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `cas_Keyspace_ReadLatency` | Keyspace read latency | `keyspace`, `function` (percentiles/Count), `axonfunction` (rate), `dc`, `rack`, `host_id` | Keyspace |
| `cas_Keyspace_WriteLatency` | Keyspace write latency | See above | Keyspace |
| `cas_Keyspace_RangeLatency` | Keyspace range latency | See above | Keyspace |
| `cas_Keyspace_MemtableOnHeapDataSize` | Keyspace memtable heap size | `keyspace`, `function` (Value), `dc`, `rack`, `host_id` | Keyspace |
| `cas_Keyspace_SSTablesPerReadHistogram` | SSTables per read by keyspace | `keyspace`, `function` (Count), `axonfunction` (rate), `dc`, `rack`, `host_id` | Keyspace |

### Thread Pool Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `cas_ThreadPools_request` | Request thread pools | `scope` (pool name), `key` (ActiveTasks/PendingTasks/CompletedTasks), `axonfunction` (rate), `dc`, `rack`, `host_id` | Thread Pools, Entropy |
| `cas_ThreadPools_internal` | Internal thread pools | See above | Thread Pools, Entropy |
| `cas_ThreadPools_transport` | Transport thread pools | See above | Thread Pools |

### Storage Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `cas_Storage_TotalHints` | Total hints created | `axonfunction` (rate), `dc`, `rack`, `host_id` | Entropy |
| `cas_Storage_TotalHintsInProgress` | Active hints being delivered | `dc`, `rack`, `host_id` | Entropy |

### Read Repair Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `cas_ReadRepair_Attempted` | Read repair attempts | `function` (Count), `axonfunction` (rate), `dc`, `rack`, `host_id` | Entropy |
| `cas_ReadRepair_RepairedBackground` | Background repairs completed | See above | Entropy |
| `cas_ReadRepair_RepairedBlocking` | Blocking repairs completed | See above | Entropy |

### CQL Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `cas_CQL_PreparedStatementsExecuted` | Prepared statements executed | `function` (Count), `axonfunction` (rate), `dc`, `rack`, `host_id` | CQL |
| `cas_CQL_RegularStatementsExecuted` | Regular statements executed | See above | CQL |
| `cas_CQL_PreparedStatementsCount` | Cached prepared statements | `function` (Value), `axonfunction` (rate), `dc`, `rack`, `host_id` | CQL |
| `cas_CQL_PreparedStatementsRatio` | Prepared statement ratio | `function` (Value), `dc`, `rack`, `host_id` | CQL |

### Dropped Message Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `cas_DroppedMessage_Dropped` | Dropped messages by type | `scope` (MUTATION/READ/HINT/etc), `function` (Count), `axonfunction` (rate), `dc`, `rack`, `host_id` | Dropped Messages |

### CommitLog Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `cas_CommitLog_WaitingOnSegmentAllocation` | Time waiting for segment allocation | `function` (percentile), `dc`, `rack`, `host_id` | Coordinator |

## Client Metrics (client_)

Application-level client interaction metrics.

| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `client_throughput_read` | Client read throughput | `dc`, `rack`, `host_id` | Application, Overview |
| `client_throughput_write` | Client write throughput | `dc`, `rack`, `host_id` | Application, Overview |
| `client_latency_read` | Client read latency | `function` (percentile), `dc`, `rack`, `host_id` | Application, Overview |
| `client_latency_write` | Client write latency | `function` (percentile), `dc`, `rack`, `host_id` | Application, Overview |

## Authentication Metrics

| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `cas_authentication_success` | Successful authentications | `username`, `axonfunction` (rate), `dc`, `rack`, `host_id` | Security |

## Event-Based Monitoring

The Security dashboard primarily uses event filtering rather than metrics.

### Event Types
| Event Type | Source | Description | Used In |
|-----------|--------|-------------|---------|
| `authentication` | Cassandra | Authentication attempts | Security |
| `authorization` | Cassandra | Authorization attempts | Security |
| `DDL_query` | Cassandra | Data Definition Language queries | Security |
| `DCL_query` | Cassandra | Data Control Language queries | Security |
| `DML_query` | Cassandra | Data Manipulation Language queries | Security |
| `jmx` | System | JMX access events | Security |

## Special Functions and Attributes

### Common Function Values
- **Percentiles**: `50thPercentile`, `75thPercentile`, `95thPercentile`, `98thPercentile`, `99thPercentile`, `999thPercentile`
- **Aggregations**: `Count`, `Min`, `Max`, `Mean`, `Value`
- **Special**: `axonfunction='rate'` - Converts counter to rate

### Common Attributes
- **Location**: `dc` (datacenter), `rack`, `host_id` (node)
- **Scope**: Varies by metric type (table name, cache name, thread pool name, etc.)
- **Filtering**: `groupBy` - Dynamic aggregation dimension

### Scope Patterns for ClientRequest Metrics
- **Read Operations**: `Read`, `Read-ALL`, `Read-ONE`, `Read-QUORUM`, etc.
- **Write Operations**: `Write`, `Write-ALL`, `Write-ANY`, `Write-QUORUM`, etc.
- **Range Operations**: `RangeSlice`

### Dropped Message Scopes
- `MUTATION`, `COUNTER_MUTATION`, `HINT`, `READ`, `RANGE_SLICE`, `PAGED_RANGE`
- `READ_REPAIR`, `BATCH_STORE`, `BATCH_REMOVE`, `REQUEST_RESPONSE`, `_TRACE`

## Metric Naming Conventions

1. **Prefix indicates source**:
   - `host_` - System metrics
   - `jvm_` - JVM metrics
   - `cas_` - Cassandra metrics
   - `client_` - Client application metrics

2. **Middle part indicates component**:
   - Examples: `CPU`, `Memory`, `Disk`, `Table`, `Keyspace`, `Cache`

3. **Suffix indicates measurement**:
   - Examples: `Latency`, `Count`, `Size`, `Ratio`, `Used`

## Notes

- Some metrics use `axonfunction='rate'` to calculate per-second rates from counters
- The `function` attribute typically indicates the aggregation or percentile
- Many queries filter out `Min` and `Max` values using `function!='Min|Max'`
- Event-based panels (mainly in Security dashboard) don't use metrics queries
- Some metrics have special scope filters like `scope!=''` to exclude empty values