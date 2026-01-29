---
title: "Accessing AxonOps Metrics with Grafana"
description: "View AxonOps metrics in Grafana. Export and visualize Cassandra and Kafka metrics."
meta:
  - name: keywords
    content: "Grafana integration, AxonOps Grafana, metrics visualization"
---

# Accessing AxonOps Metrics with Grafana

## Generate API Token

Generate an API token with *read-only* permission to the clusters you wish to access.

- Log in to [https://console.axonops.com](https://console.axonops.com).
- Navigate in the left menu to API Tokens.

    <img src="/monitoring/grafana/api_token_menu.png" class="skip-lightbox" alt="api_token_menu">

- Click on Create New API Token button and complete the details.
    <img src="/monitoring/grafana/generate_api_token.png" class="skip-lightbox" alt="generate_api_token">


## Configure Grafana

- Configure a new Prometheus data source in Grafana
- Set the URL to **https://dash.axonops.cloud/$ORGNAME** 
- Enable Basic auth. 
- Paste the API key in the User field 
- Click Save & Test

Now you should be able to browse and query the metrics from the Explore interface.

See the video below:
![type:video](./setup.mov)

## Available Metrics

AxonOps exposes metrics using a Prometheus-compatible API. Metrics are organized by prefix:

- `host_` - System metrics (CPU, memory, disk, network)
- `jvm_` - JVM metrics (heap, garbage collection)
- `cas_` - Cassandra metrics (client requests, tables, compaction, thread pools)
- `client_` - Client application metrics (throughput, latency)
- `kaf_` - Kafka metrics (controller, replication, topics, consumers)

For complete metric references, see:

- [Cassandra Metrics Reference](../../metrics/cassandra/all_dashboards_metrics_reference.md)
- [Kafka Metrics Reference](../../metrics/kafka/all_kafka_dashboards_metrics_reference.md)

### Cassandra Metrics

#### System Metrics

| Metric | Description |
|--------|-------------|
| `host_CPU_Percent_Merge` | CPU usage percentage |
| `host_Memory_Used` | Used memory in bytes |
| `host_Memory_Free` | Free memory in bytes |
| `host_Memory_Total` | Total memory in bytes |
| `host_Memory_Buffers` | Buffer memory |
| `host_Memory_Cached` | Cached memory |
| `host_Disk_UsedPercent` | Disk usage percentage |
| `host_Disk_Used` | Used disk space in bytes |
| `host_Disk_SectorsRead` | Disk sectors read |
| `host_Disk_SectorsWrite` | Disk sectors written |
| `host_Network_ReceiveBytes` | Network bytes received |
| `host_Network_TransmitBytes` | Network bytes transmitted |

#### JVM Metrics

| Metric | Description |
|--------|-------------|
| `jvm_Memory_Heap` | Heap memory usage |
| `jvm_MemoryPool_*` | Specific memory pool metrics |
| `jvm_GarbageCollector_*` | GC metrics by collector |
| `jvm_GarbageCollector_G1_Young_Generation` | G1 young gen GC |
| `jvm_GarbageCollector_Shenandoah_Cycles` | Shenandoah GC cycles |
| `jvm_GarbageCollector_Shenandoah_Pauses` | Shenandoah GC pauses |
| `jvm_GarbageCollector_ZGC` | ZGC metrics |

#### Client Request Metrics

| Metric | Description |
|--------|-------------|
| `cas_ClientRequest_Latency` | Request latency at coordinator |
| `cas_ClientRequest_Timeouts` | Request timeouts |
| `cas_ClientRequest_Unavailables` | Unavailable exceptions |
| `cas_Client_connectedNativeClients` | Connected native protocol clients |

#### Table Metrics

| Metric | Description |
|--------|-------------|
| `cas_Table_ReadLatency` | Local read latency |
| `cas_Table_WriteLatency` | Local write latency |
| `cas_Table_RangeLatency` | Local range query latency |
| `cas_Table_CoordinatorReadLatency` | Coordinator read latency |
| `cas_Table_CoordinatorWriteLatency` | Coordinator write latency |
| `cas_Table_CoordinatorScanLatency` | Coordinator range scan latency |
| `cas_Table_LiveDiskSpaceUsed` | Live data disk space |
| `cas_Table_TotalDiskSpaceUsed` | Total disk space |
| `cas_Table_LiveSSTableCount` | Number of SSTables |
| `cas_Table_CompressionRatio` | Compression effectiveness |
| `cas_Table_MinPartitionSize` | Minimum partition size |
| `cas_Table_MeanPartitionSize` | Average partition size |
| `cas_Table_MaxPartitionSize` | Maximum partition size |
| `cas_Table_EstimatedPartitionCount` | Estimated partitions |
| `cas_Table_TombstoneScannedHistogram` | Tombstones scanned |
| `cas_Table_SSTablesPerReadHistogram` | SSTables per read |
| `cas_Table_SpeculativeRetries` | Speculative retry attempts |
| `cas_Table_BloomFilterFalseRatio` | Bloom filter false positive ratio |
| `cas_Table_BloomFilterDiskSpaceUsed` | Bloom filter disk usage |
| `cas_Table_AllMemtablesHeapSize` | Memtable heap memory |
| `cas_Table_AllMemtablesOffHeapSize` | Memtable off-heap memory |

#### Compaction Metrics

| Metric | Description | Key Attributes |
|--------|-------------|----------------|
| `cas_Compaction_TotalCompactionsCompleted` | Completed compactions | `axonfunction` |
| `cas_Compaction_BytesCompacted` | Bytes compacted | `axonfunction` |
| `cas_CompactionManager_*` | Compaction manager metrics | `metric` (PendingTasks/CompletedTasks) |

#### Thread Pool Metrics

| Metric | Description | Key Attributes |
|--------|-------------|----------------|
| `cas_ThreadPools_request` | Request thread pools | `scope` (pool name), `key` (ActiveTasks/PendingTasks/CompletedTasks) |
| `cas_ThreadPools_internal` | Internal thread pools | `scope` (pool name), `key` (ActiveTasks/PendingTasks/CompletedTasks) |
| `cas_ThreadPools_transport` | Transport thread pools | `scope` (pool name), `key` (ActiveTasks/PendingTasks/CompletedTasks) |

#### Cache Metrics

| Metric | Description | Key Attributes |
|--------|-------------|----------------|
| `cas_Cache_*` | Cache statistics | `scope` (KeyCache/RowCache/CounterCache), `metric` (Capacity/Size/Hits/Requests) |

#### CQL Metrics

| Metric | Description |
|--------|-------------|
| `cas_CQL_PreparedStatementsExecuted` | Prepared statements executed |
| `cas_CQL_RegularStatementsExecuted` | Regular statements executed |
| `cas_CQL_PreparedStatementsCount` | Cached prepared statements |
| `cas_CQL_PreparedStatementsRatio` | Prepared statement ratio |

#### Dropped Message Metrics

| Metric | Description |
|--------|-------------|
| `cas_DroppedMessage_Dropped` | Dropped messages by type |

#### Storage Metrics

| Metric | Description |
|--------|-------------|
| `cas_Storage_TotalHints` | Total hints created |
| `cas_Storage_TotalHintsInProgress` | Active hints being delivered |

#### Read Repair Metrics

| Metric | Description |
|--------|-------------|
| `cas_ReadRepair_Attempted` | Read repair attempts |
| `cas_ReadRepair_RepairedBackground` | Background repairs completed |
| `cas_ReadRepair_RepairedBlocking` | Blocking repairs completed |

#### Keyspace Metrics

| Metric | Description |
|--------|-------------|
| `cas_Keyspace_ReadLatency` | Keyspace read latency |
| `cas_Keyspace_WriteLatency` | Keyspace write latency |
| `cas_Keyspace_RangeLatency` | Keyspace range latency |
| `cas_Keyspace_MemtableOnHeapDataSize` | Keyspace memtable heap size |
| `cas_Keyspace_SSTablesPerReadHistogram` | SSTables per read by keyspace |

#### CommitLog Metrics

| Metric | Description |
|--------|-------------|
| `cas_CommitLog_WaitingOnSegmentAllocation` | Time waiting for segment allocation |

#### Client Metrics

| Metric | Description |
|--------|-------------|
| `client_throughput_read` | Client read throughput |
| `client_throughput_write` | Client write throughput |
| `client_latency_read` | Client read latency |
| `client_latency_write` | Client write latency |

#### Authentication Metrics

| Metric | Description |
|--------|-------------|
| `cas_authentication_success` | Successful authentications |

### Kafka Metrics

#### Controller Metrics

| Metric | Description |
|--------|-------------|
| `kaf_KafkaController_ActiveControllerCount` | Active controller count (should be 1) |
| `kaf_KafkaController_OfflinePartitionsCount` | Partitions without leaders |
| `kaf_KafkaController_PreferredReplicaImbalanceCount` | Partitions with non-preferred leaders |
| `kaf_KafkaController_GlobalTopicCount` | Total topics in cluster |
| `kaf_KafkaController_GlobalPartitionCount` | Total partitions in cluster |
| `kaf_KafkaController_FencedBrokerCount` | Number of fenced brokers |
| `kaf_KafkaController_LastAppliedRecordTimestamp` | Last applied record timestamp |
| `kaf_KafkaController_MetadataErrorCount` | Metadata error count |
| `kaf_ControllerStats_UncleanLeaderElectionsPerSec` | Unclean leader election rate |
| `kaf_ControllerStats_LeaderElectionRateAndTimeMs` | Leader election rate and time |

#### Replication Metrics

| Metric | Description |
|--------|-------------|
| `kaf_ReplicaManager_LeaderCount` | Partitions where broker is leader |
| `kaf_ReplicaManager_PartitionCount` | Total partitions on broker |
| `kaf_ReplicaManager_UnderReplicatedPartitions` | Under-replicated partitions |
| `kaf_ReplicaManager_UnderMinIsrPartitionCount` | Partitions under min ISR |
| `kaf_ReplicaManager_AtMinIsrPartitionCount` | Partitions at min ISR |
| `kaf_ReplicaManager_OfflineReplicaCount` | Offline replica count |
| `kaf_ReplicaManager_IsrShrinksPerSec` | ISR shrink rate |
| `kaf_ReplicaManager_IsrExpandsPerSec` | ISR expansion rate |
| `kaf_ReplicaManager_ReassigningPartitions` | Partitions being reassigned |

#### Topic Metrics

| Metric | Description |
|--------|-------------|
| `kaf_BrokerTopicMetrics_BytesInPerSec` | Incoming byte rate |
| `kaf_BrokerTopicMetrics_BytesOutPerSec` | Outgoing byte rate |
| `kaf_BrokerTopicMetrics_MessagesInPerSec` | Incoming message rate |
| `kaf_BrokerTopicMetrics_TotalFetchRequestsPerSec` | Fetch request rate |
| `kaf_BrokerTopicMetrics_TotalProduceRequestsPerSec` | Produce request rate |
| `kaf_BrokerTopicMetrics_FailedFetchRequestsPerSec` | Failed fetch request rate |
| `kaf_BrokerTopicMetrics_FailedProduceRequestsPerSec` | Failed produce request rate |
| `kaf_BrokerTopicMetrics_BytesRejectedPerSec` | Rejected bytes rate |
| `kaf_BrokerTopicMetrics_FetchMessageConversionsPerSec` | Fetch message conversion rate |
| `kaf_BrokerTopicMetrics_ProduceMessageConversionsPerSec` | Produce message conversion rate |

#### Request Metrics

| Metric | Description |
|--------|-------------|
| `kaf_RequestMetrics_RequestsPerSec` | Request rate |
| `kaf_RequestMetrics_TotalTimeMs` | Total request time |
| `kaf_RequestMetrics_LocalTimeMs` | Local processing time |
| `kaf_RequestMetrics_RemoteTimeMs` | Remote processing time |
| `kaf_RequestMetrics_RequestQueueTimeMs` | Time in request queue |
| `kaf_RequestMetrics_ResponseQueueTimeMs` | Time in response queue |
| `kaf_RequestMetrics_ResponseSendTimeMs` | Response send time |
| `kaf_RequestChannel_RequestQueueSize` | Request queue size |
| `kaf_RequestChannel_ResponseQueueSize` | Response queue size |

#### Performance Metrics

| Metric | Description |
|--------|-------------|
| `kaf_KafkaRequestHandlerPool_RequestHandlerAvgIdlePercent` | Request handler idle percentage |
| `kaf_SocketServer_NetworkProcessorAvgIdlePercent` | Network processor idle percentage |
| `kaf_DelayedOperationPurgatory_PurgatorySize` | Delayed operations in purgatory |
| `kaf_socket_server_metrics_` | Socket server metrics |
| `kaf_Acceptor_AcceptorBlockedPercent` | Acceptor blocked percentage |
| `kaf_LogManager_LogDirectoryOffline` | Offline log directories |

#### Raft Metrics (KRaft Mode)

| Metric | Description |
|--------|-------------|
| `kaf_RaftMetrics_CurrentLeader` | Current Raft leader |
| `kaf_RaftMetrics_CurrentEpoch` | Current Raft epoch |
| `kaf_RaftMetrics_HighWatermark` | Raft high watermark |
| `kaf_RaftMetrics_CurrentState` | Current Raft state |
| `kaf_RaftMetrics_CommitLatencyAvg` | Average commit latency |
| `kaf_RaftMetrics_AppendRecordsRate` | Record append rate |
| `kaf_RaftMetrics_PollIdleRatioAvg` | Poll idle ratio |

#### Consumer Group Metrics

| Metric | Description |
|--------|-------------|
| `kaf_GroupMetadataManager_NumGroups` | Total consumer groups |
| `kaf_GroupMetadataManager_NumGroupsStable` | Stable consumer groups |
| `kaf_GroupMetadataManager_NumGroupsPreparingRebalance` | Groups preparing rebalance |
| `kaf_GroupMetadataManager_NumGroupsCompletingRebalance` | Groups completing rebalance |
| `kaf_GroupMetadataManager_NumGroupsDead` | Dead consumer groups |
| `kaf_GroupMetadataManager_NumGroupsEmpty` | Empty consumer groups |
| `kaf_kafka_consumer_lag_millis` | Consumer lag in milliseconds |

#### Log Metrics

| Metric | Description |
|--------|-------------|
| `kaf_Log_NumLogSegments` | Number of log segments |
| `kaf_Log_Size` | Log size in bytes |
| `kaf_Log_LogEndOffset` | Log end offset |
| `kaf_Log_LogStartOffset` | Log start offset |

#### Partition Metrics

| Metric | Description |
|--------|-------------|
| `kaf_Partition_UnderReplicated` | Under-replicated partition |
| `kaf_Partition_AtMinIsr` | Partition at minimum ISR |
| `kaf_Partition_UnderMinIsr` | Partition under minimum ISR |
| `kaf_Partition_InSyncReplicasCount` | In-sync replicas count |
| `kaf_Partition_ReplicasCount` | Total replicas count |
| `kaf_Partition_LastStableOffsetLag` | Last stable offset lag |

#### ZooKeeper Metrics

| Metric | Description |
|--------|-------------|
| `kaf_SessionExpireListener_ZooKeeperDisconnectsPerSec` | ZooKeeper disconnect rate |
| `kaf_SessionExpireListener_ZooKeeperExpiresPerSec` | ZooKeeper session expiry rate |
| `kaf_SessionExpireListener_ZooKeeperAuthFailuresPerSec` | ZooKeeper auth failure rate |
| `kaf_SessionExpireListener_ZooKeeperSyncConnectsPerSec` | ZooKeeper sync connect rate |
| `kaf_ZooKeeperClientMetrics_ZooKeeperRequestLatencyMs` | ZooKeeper request latency |

#### Kafka Connect Metrics

| Metric | Description |
|--------|-------------|
| `kaf_connect_worker_metrics_task_count` | Number of tasks |
| `kaf_connect_worker_metrics_connector_count` | Number of connectors |
| `kaf_connect_worker_metrics_connector_startup_attempts_total` | Connector startup attempts |
| `kaf_connect_worker_metrics_connector_startup_failure_total` | Connector startup failures |
| `kaf_connect_worker_metrics_connector_startup_success_total` | Connector startup successes |
| `kaf_connect_worker_metrics_task_startup_attempts_total` | Task startup attempts |
| `kaf_connect_worker_metrics_task_startup_failure_total` | Task startup failures |
| `kaf_connect_worker_metrics_task_startup_success_total` | Task startup successes |
| `kaf_connect_worker_rebalance_rebalance_completed_total` | Rebalances completed |
| `kaf_connect_worker_rebalance_rebalancing` | Currently rebalancing |
| `kaf_connect_worker_rebalance_connect_protocol` | Connect protocol |
| `kaf_connector_task_batch_size_avg` | Average batch size |
| `kaf_connector_task_offset_commit_avg_time_ms` | Offset commit time |
| `kaf_connector_task_offset_commit_success_percentage` | Offset commit success rate |
| `kaf_source_task_source_record_poll_rate` | Source record poll rate |
| `kaf_source_task_source_record_write_rate` | Source record write rate |
| `kaf_sink_task_sink_record_read_rate` | Sink record read rate |
| `kaf_sink_task_sink_record_send_rate` | Sink record send rate |
| `kaf_sink_task_sink_record_lag_max` | Maximum sink record lag |
| `kaf_task_error_deadletterqueue_produce_failures` | DLQ produce failures |
| `kaf_task_error_deadletterqueue_produce_requests` | DLQ produce requests |
| `kaf_task_error_total_errors_logged` | Total errors logged |
| `kaf_task_error_total_record_errors` | Total record errors |
| `kaf_task_error_total_record_failures` | Total record failures |
| `kaf_task_error_total_retries` | Total retries |

## Query Syntax

AxonOps uses a Prometheus-compatible query language. For detailed documentation, see [Prometheus Query Language](https://prometheus.io/docs/prometheus/latest/querying/basics/){target="_blank"}.

### Key Difference: Rate Function

AxonOps optimizes rate calculations at the source. Instead of using the Prometheus `rate()` function, embed `axonfunction='rate'` as a label:

```promql
# AxonOps rate syntax
cas_ClientRequest_Latency{axonfunction='rate',function='Count'}

# Instead of Prometheus style
rate(cas_ClientRequest_Latency{function='Count'}[5m])
```

### Common Attributes

- `dc` - Datacenter
- `rack` - Rack
- `host_id` - Node identifier
- `keyspace` - Cassandra keyspace
- `scope` - Table name or operation type
- `function` - Aggregation type (Count, percentiles)

### Percentile Functions

Available percentile values:

- `50thPercentile`, `75thPercentile`, `95thPercentile`
- `98thPercentile`, `99thPercentile`, `999thPercentile`

## Example Queries

### Cassandra Examples

**Read latency P99 by node:**
```promql
cas_ClientRequest_Latency{scope='Read',function='99thPercentile'}
```

**Write throughput (rate):**
```promql
cas_ClientRequest_Latency{axonfunction='rate',scope='Write',function='Count'}
```

**Disk usage percentage:**
```promql
host_Disk_UsedPercent{mountpoint='/var/lib/cassandra'}
```

**Heap memory usage:**
```promql
jvm_Memory_Heap{type='usage'}
```

**Pending compactions:**
```promql
cas_CompactionManager{metric='PendingTasks'}
```

**Table read latency for a specific keyspace:**
```promql
cas_Table_ReadLatency{keyspace='my_keyspace',function='99thPercentile'}
```

**Connected clients:**
```promql
cas_Client_connectedNativeClients
```

**Dropped messages rate:**
```promql
cas_DroppedMessage_Dropped{axonfunction='rate',function='Count'}
```

**Key cache hit rate:**
```promql
cas_Cache{scope='KeyCache',metric='Hits'}
```

**Pending tasks in MutationStage thread pool:**
```promql
cas_ThreadPools_request{scope='MutationStage',key='PendingTasks'}
```

### Kafka Examples

**Under-replicated partitions:**
```promql
kaf_ReplicaManager_UnderReplicatedPartitions
```

**Messages in per second:**
```promql
kaf_BrokerTopicMetrics_MessagesInPerSec{axonfunction='rate'}
```

**Consumer lag:**
```promql
kaf_kafka_consumer_lag_millis{group_id='my-consumer-group'}
```

**Request handler idle percentage:**
```promql
kaf_KafkaRequestHandlerPool_RequestHandlerAvgIdlePercent{function='OneMinuteRate'}
```

**ISR shrinks (indicates replication issues):**
```promql
kaf_ReplicaManager_IsrShrinksPerSec{function='MeanRate'}
```

### Filtering Examples

**Filter by datacenter:**
```promql
cas_ClientRequest_Latency{dc='dc1',function='99thPercentile'}
```

**Filter by multiple nodes using regex:**
```promql
host_CPU_Percent_Merge{host_id=~'node1|node2|node3'}
```

**Exclude specific racks:**
```promql
cas_Table_ReadLatency{rack!='rack1',function='99thPercentile'}
```
