# AxonOps All Kafka Dashboards Metrics Reference

This document provides a comprehensive reference of all metrics used across AxonOps Kafka dashboards, organized by metric prefix and category.

## Table of Contents

1. [System Metrics (host_ and jvm_)](#system-metrics-host_-and-jvm_)
2. [Kafka Controller Metrics](#kafka-controller-metrics)
3. [Kafka Server Metrics](#kafka-server-metrics)
4. [Kafka Network Metrics](#kafka-network-metrics)
5. [Kafka Log Metrics](#kafka-log-metrics)
6. [Kafka Connect Metrics](#kafka-connect-metrics)
7. [ZooKeeper Metrics](#zookeeper-metrics)
8. [Special Functions and Attributes](#special-functions-and-attributes)
9. [Dashboard Coverage](#dashboard-coverage)

## System Metrics (host_ and jvm_)

System-level metrics collected from the operating system and JVM, shared with Cassandra monitoring.

### CPU Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `host_CPU_Percent_Merge` | Merged CPU usage percentage | `time` (real/user/sys), `rack`, `host_id` | System, Performance |

### Memory Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `host_Memory_Used` | Used memory in bytes | `rack`, `host_id` | System |
| `host_Memory_Free` | Free memory in bytes | `rack`, `host_id` | System |
| `host_Memory_Total` | Total memory in bytes | `rack`, `host_id` | System |
| `host_Memory_Buffers` | Buffer memory | `rack`, `host_id` | System |
| `host_Memory_Cached` | Cached memory | `rack`, `host_id` | System |

### Disk Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `host_Disk_Free` | Free disk space | `partition`, `rack`, `host_id` | System |
| `host_Disk_SectorsRead` | Disk sectors read | `partition`, `axonfunction` (rate), `rack`, `host_id` | System |
| `host_Disk_SectorsWrite` | Disk sectors written | `partition`, `axonfunction` (rate), `rack`, `host_id` | System |

### Network Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `host_Network_ReceiveBytes` | Network bytes received | `interface`, `axonfunction` (rate), `rack`, `host_id` | System |
| `host_Network_TransmitBytes` | Network bytes transmitted | `interface`, `axonfunction` (rate), `rack`, `host_id` | System |

### JVM Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `jvm_Memory_Heap` | Heap memory usage | `type` (usage/max), `rack`, `host_id` | System |
| `jvm_GarbageCollector_*` | GC metrics by collector | `collector_name`, `function` (CollectionTime/CollectionCount), `axonfunction` (rate), `rack`, `host_id` | System |

## Kafka Controller Metrics

Metrics related to Kafka cluster control and coordination.

| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `kaf_KafkaController_ActiveControllerCount` | Active controller count (should be 1) | `rack`, `host_id` | Overview, Controller |
| `kaf_KafkaController_OfflinePartitionsCount` | Partitions without leaders | `dc`, `rack`, `host_id` | Overview, Controller |
| `kaf_KafkaController_PreferredReplicaImbalanceCount` | Partitions with non-preferred leaders | `dc`, `rack`, `host_id` | Overview |
| `kaf_KafkaController_GlobalTopicCount` | Total topics in cluster | `rack`, `host_id` | Controller |
| `kaf_KafkaController_GlobalPartitionCount` | Total partitions in cluster | `rack`, `host_id` | Controller |
| `kaf_KafkaController_FencedBrokerCount` | Number of fenced brokers | `rack`, `host_id` | Controller |
| `kaf_KafkaController_LastAppliedRecordTimestamp` | Last applied record timestamp | `rack`, `host_id` | Controller |
| `kaf_KafkaController_MetadataErrorCount` | Metadata error count | `rack`, `host_id` | Controller |
| `kaf_ControllerStats_UncleanLeaderElectionsPerSec` | Unclean leader election rate | `function` (MeanRate), `rack`, `host_id` | Overview, Controller |
| `kaf_ControllerStats_LeaderElectionRateAndTimeMs` | Leader election rate and time | `function`, `rack`, `host_id` | Controller |

## Kafka Server Metrics

Core Kafka broker server metrics.

### Replica Manager
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `kaf_ReplicaManager_LeaderCount` | Partitions where broker is leader | `rack`, `host_id` | Overview, Replication |
| `kaf_ReplicaManager_PartitionCount` | Total partitions on broker | `dc`, `rack`, `host_id` | Overview, Replication |
| `kaf_ReplicaManager_UnderReplicatedPartitions` | Under-replicated partitions | `dc`, `rack`, `host_id` | Overview, Replication |
| `kaf_ReplicaManager_UnderMinIsrPartitionCount` | Partitions under min ISR | `dc`, `rack`, `host_id` | Overview, Replication |
| `kaf_ReplicaManager_OfflineReplicaCount` | Offline replica count | `rack`, `host_id` | Replication |
| `kaf_ReplicaManager_IsrShrinksPerSec` | ISR shrink rate | `function` (MeanRate), `rack`, `host_id` | Overview, Replication |
| `kaf_ReplicaManager_IsrExpandsPerSec` | ISR expansion rate | `function` (MeanRate), `rack`, `host_id` | Overview, Replication |
| `kaf_ReplicaManager_ReassigningPartitions` | Partitions being reassigned | `rack`, `host_id` | Replication |
| `kaf_ReplicaManager_AtMinIsrPartitionCount` | Partitions at min ISR | `rack`, `host_id` | Replication |

### Broker Topic Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `kaf_BrokerTopicMetrics_BytesInPerSec` | Incoming byte rate | `axonfunction` (rate), `rack`, `host_id`, `topic` | Overview, Topics, Requests |
| `kaf_BrokerTopicMetrics_BytesOutPerSec` | Outgoing byte rate | `axonfunction` (rate), `rack`, `host_id`, `topic` | Overview, Topics, Requests |
| `kaf_BrokerTopicMetrics_MessagesInPerSec` | Incoming message rate | `axonfunction` (rate), `rack`, `host_id`, `topic` | Overview, Topics, Requests |
| `kaf_BrokerTopicMetrics_TotalFetchRequestsPerSec` | Fetch request rate | `axonfunction` (rate), `rack`, `host_id`, `topic` | Topics, Requests |
| `kaf_BrokerTopicMetrics_TotalProduceRequestsPerSec` | Produce request rate | `axonfunction` (rate), `rack`, `host_id`, `topic` | Topics, Requests |
| `kaf_BrokerTopicMetrics_FailedFetchRequestsPerSec` | Failed fetch request rate | `axonfunction` (rate), `rack`, `host_id`, `topic` | Topics, Requests |
| `kaf_BrokerTopicMetrics_FailedProduceRequestsPerSec` | Failed produce request rate | `axonfunction` (rate), `rack`, `host_id`, `topic` | Topics, Requests |
| `kaf_BrokerTopicMetrics_BytesRejectedPerSec` | Rejected bytes rate | `axonfunction` (rate), `rack`, `host_id`, `topic` | Topics |
| `kaf_BrokerTopicMetrics_FetchMessageConversionsPerSec` | Fetch message conversion rate | `axonfunction` (rate), `rack`, `host_id` | Requests |
| `kaf_BrokerTopicMetrics_ProduceMessageConversionsPerSec` | Produce message conversion rate | `axonfunction` (rate), `rack`, `host_id` | Requests |

### Request Handler Pool
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `kaf_KafkaRequestHandlerPool_RequestHandlerAvgIdlePercent` | Request handler idle percentage | `function` (OneMinuteRate), `rack`, `host_id` | Overview, Performance |

### Log Manager
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `kaf_LogManager_LogDirectoryOffline` | Offline log directories | `logDirectory`, `rack`, `host_id` | System |

### Delayed Operation Purgatory
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `kaf_DelayedOperationPurgatory_PurgatorySize` | Delayed operations in purgatory | `delayedOperation` (Produce/Fetch/Heartbeat), `rack`, `host_id` | Performance |

### Raft Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `kaf_RaftMetrics_CurrentLeader` | Current Raft leader | `rack`, `host_id` | Controller |
| `kaf_RaftMetrics_CurrentEpoch` | Current Raft epoch | `rack`, `host_id` | Controller |
| `kaf_RaftMetrics_HighWatermark` | Raft high watermark | `rack`, `host_id` | Controller |
| `kaf_RaftMetrics_CurrentState` | Current Raft state | `rack`, `host_id` | Controller |
| `kaf_RaftMetrics_CommitLatencyAvg` | Average commit latency | `rack`, `host_id` | Controller |
| `kaf_RaftMetrics_AppendRecordsRate` | Record append rate | `rack`, `host_id` | Controller |
| `kaf_RaftMetrics_PollIdleRatioAvg` | Poll idle ratio | `rack`, `host_id` | Controller |

## Kafka Network Metrics

Network and request handling metrics.

### Socket Server
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `kaf_socket_server_metrics_` | Socket server metrics | `function` (connection_count), `rack`, `host_id` | Overview, Connections |
| `kaf_SocketServer_NetworkProcessorAvgIdlePercent` | Network processor idle percentage | `networkProcessor`, `rack`, `host_id` | Performance |
| `kaf_Acceptor_AcceptorBlockedPercent` | Acceptor blocked percentage | `listener`, `rack`, `host_id` | Connections |

### Request Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `kaf_RequestMetrics_RequestsPerSec` | Request rate | `axonfunction` (rate), `function` (Count), `request`, `rack`, `host_id` | Overview, Performance, Requests |
| `kaf_RequestMetrics_TotalTimeMs` | Total request time | `request`, `function` (percentiles/Mean), `rack`, `host_id` | Performance |
| `kaf_RequestMetrics_LocalTimeMs` | Local processing time | `request`, `function` (percentiles/Mean), `rack`, `host_id` | Performance |
| `kaf_RequestMetrics_RemoteTimeMs` | Remote processing time | `request`, `function` (percentiles/Mean), `rack`, `host_id` | Performance |
| `kaf_RequestMetrics_RequestQueueTimeMs` | Time in request queue | `request`, `function` (percentiles/Mean), `rack`, `host_id` | Performance |
| `kaf_RequestMetrics_ResponseQueueTimeMs` | Time in response queue | `request`, `function` (percentiles/Mean), `rack`, `host_id` | Performance |
| `kaf_RequestMetrics_ResponseSendTimeMs` | Response send time | `request`, `function` (percentiles/Mean), `rack`, `host_id` | Performance |

### Request Channel
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `kaf_RequestChannel_RequestQueueSize` | Request queue size | `rack`, `host_id` | Performance |
| `kaf_RequestChannel_ResponseQueueSize` | Response queue size | `processor`, `rack`, `host_id` | Performance |

## Kafka Log Metrics

Log and partition-level metrics.

### Log Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `kaf_Log_NumLogSegments` | Number of log segments | `topic`, `partition`, `rack`, `host_id` | Topics |
| `kaf_Log_Size` | Log size in bytes | `topic`, `partition`, `rack`, `host_id` | Topics |
| `kaf_Log_LogEndOffset` | Log end offset | `topic`, `partition`, `rack`, `host_id` | Topics |
| `kaf_Log_LogStartOffset` | Log start offset | `topic`, `partition`, `rack`, `host_id` | Topics |

### Partition Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `kaf_Partition_UnderReplicated` | Under-replicated partition | `topic`, `partition`, `rack`, `host_id` | Replication |
| `kaf_Partition_AtMinIsr` | Partition at minimum ISR | `topic`, `partition`, `rack`, `host_id` | Replication |
| `kaf_Partition_UnderMinIsr` | Partition under minimum ISR | `topic`, `partition`, `rack`, `host_id` | Replication |
| `kaf_Partition_InSyncReplicasCount` | In-sync replicas count | `topic`, `partition`, `rack`, `host_id` | Replication |
| `kaf_Partition_ReplicasCount` | Total replicas count | `topic`, `partition`, `rack`, `host_id` | Replication |
| `kaf_Partition_LastStableOffsetLag` | Last stable offset lag | `topic`, `partition`, `rack`, `host_id` | Replication |

## Kafka Connect Metrics

Metrics for Kafka Connect distributed mode.

### Worker Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `kaf_connect_worker_metrics_task_count` | Number of tasks | `status`, `rack`, `host_id` | Connect Overview |
| `kaf_connect_worker_metrics_connector_count` | Number of connectors | `status`, `rack`, `host_id` | Connect Overview |
| `kaf_connect_worker_metrics_connector_startup_attempts_total` | Connector startup attempts | `rack`, `host_id` | Connect Workers |
| `kaf_connect_worker_metrics_connector_startup_failure_total` | Connector startup failures | `rack`, `host_id` | Connect Workers |
| `kaf_connect_worker_metrics_connector_startup_success_total` | Connector startup successes | `rack`, `host_id` | Connect Workers |
| `kaf_connect_worker_metrics_task_startup_attempts_total` | Task startup attempts | `rack`, `host_id` | Connect Workers |
| `kaf_connect_worker_metrics_task_startup_failure_total` | Task startup failures | `rack`, `host_id` | Connect Workers |
| `kaf_connect_worker_metrics_task_startup_success_total` | Task startup successes | `rack`, `host_id` | Connect Workers |
| `kaf_connect_worker_rebalance_rebalance_completed_total` | Rebalances completed | `rack`, `host_id` | Connect Workers |
| `kaf_connect_worker_rebalance_rebalancing` | Currently rebalancing | `rack`, `host_id` | Connect Workers |
| `kaf_connect_worker_rebalance_connect_protocol` | Connect protocol | `rack`, `host_id` | Connect Workers |

### Connector/Task Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `kaf_connector_task_batch_size_avg` | Average batch size | `connector`, `task`, `rack`, `host_id` | Connect Tasks |
| `kaf_connector_task_offset_commit_avg_time_ms` | Offset commit time | `connector`, `task`, `rack`, `host_id` | Connect Tasks |
| `kaf_connector_task_offset_commit_success_percentage` | Offset commit success rate | `connector`, `task`, `rack`, `host_id` | Connect Tasks |
| `kaf_source_task_source_record_poll_rate` | Source record poll rate | `connector`, `task`, `rack`, `host_id` | Connect Tasks |
| `kaf_source_task_source_record_write_rate` | Source record write rate | `connector`, `task`, `rack`, `host_id` | Connect Tasks |
| `kaf_sink_task_sink_record_read_rate` | Sink record read rate | `connector`, `task`, `rack`, `host_id` | Connect Tasks |
| `kaf_sink_task_sink_record_send_rate` | Sink record send rate | `connector`, `task`, `rack`, `host_id` | Connect Tasks |
| `kaf_sink_task_sink_record_lag_max` | Maximum sink record lag | `connector`, `task`, `rack`, `host_id` | Connect Tasks |

### Task Error Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `kaf_task_error_deadletterqueue_produce_failures` | DLQ produce failures | `connector`, `task`, `rack`, `host_id` | Connect Tasks |
| `kaf_task_error_deadletterqueue_produce_requests` | DLQ produce requests | `connector`, `task`, `rack`, `host_id` | Connect Tasks |
| `kaf_task_error_total_errors_logged` | Total errors logged | `connector`, `task`, `rack`, `host_id` | Connect Tasks |
| `kaf_task_error_total_record_errors` | Total record errors | `connector`, `task`, `rack`, `host_id` | Connect Tasks |
| `kaf_task_error_total_record_failures` | Total record failures | `connector`, `task`, `rack`, `host_id` | Connect Tasks |
| `kaf_task_error_total_retries` | Total retries | `connector`, `task`, `rack`, `host_id` | Connect Tasks |

## ZooKeeper Metrics

Metrics for ZooKeeper connectivity and performance.

### Session Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `kaf_SessionExpireListener_ZooKeeperDisconnectsPerSec` | ZooKeeper disconnect rate | `function` (MeanRate), `rack`, `host_id` | ZooKeeper |
| `kaf_SessionExpireListener_ZooKeeperExpiresPerSec` | ZooKeeper session expiry rate | `function` (MeanRate), `rack`, `host_id` | ZooKeeper |
| `kaf_SessionExpireListener_ZooKeeperAuthFailuresPerSec` | ZooKeeper auth failure rate | `function` (MeanRate), `rack`, `host_id` | ZooKeeper |
| `kaf_SessionExpireListener_ZooKeeperSyncConnectsPerSec` | ZooKeeper sync connect rate | `function` (MeanRate), `rack`, `host_id` | ZooKeeper |

### Client Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `kaf_ZooKeeperClientMetrics_ZooKeeperRequestLatencyMs` | ZooKeeper request latency | `function` (percentiles/Max), `rack`, `host_id` | ZooKeeper |

## Consumer Group Metrics

Metrics for consumer group coordination and lag monitoring.

### Group Metadata Manager
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `kaf_GroupMetadataManager_NumGroups` | Total consumer groups | `rack`, `host_id` | Overview, Consumer Groups |
| `kaf_GroupMetadataManager_NumGroupsStable` | Stable consumer groups | `rack`, `host_id` | Overview, Consumer Groups |
| `kaf_GroupMetadataManager_NumGroupsPreparingRebalance` | Groups preparing rebalance | `rack`, `host_id` | Overview, Consumer Groups |
| `kaf_GroupMetadataManager_NumGroupsDead` | Dead consumer groups | `rack`, `host_id` | Overview, Consumer Groups |
| `kaf_GroupMetadataManager_NumGroupsCompletingRebalance` | Groups completing rebalance | `rack`, `host_id` | Overview, Consumer Groups |
| `kaf_GroupMetadataManager_NumGroupsEmpty` | Empty consumer groups | `rack`, `host_id` | Overview, Consumer Groups |

### Consumer Lag Metrics
| Metric | Description | Common Attributes | Used In |
|--------|-------------|-------------------|---------|
| `kaf_kafka_consumer_lag_millis` | Consumer lag in milliseconds | `group_id`, `topic`, `partition`, `rack`, `host_id` | Consumer Groups |

## Special Functions and Attributes

### Common Function Values
- **Percentiles**: `50thPercentile`, `75thPercentile`, `95thPercentile`, `98thPercentile`, `99thPercentile`, `999thPercentile`
- **Rates**: `OneMinuteRate`, `FiveMinuteRate`, `FifteenMinuteRate`, `MeanRate`
- **Aggregations**: `Count`, `Min`, `Max`, `Mean`, `Value`
- **Special**: `axonfunction='rate'` - Converts counter to rate

### Common Attributes
- **Location**: `dc` (datacenter), `rack`, `host_id` (node)
- **Kafka Components**: `topic`, `partition`, `group_id`, `connector`, `task`
- **Request Types**: `request` (Produce, Fetch, Metadata, etc.)
- **Filtering**: `groupBy` - Dynamic aggregation dimension

### Request Type Values
Common request types for RequestMetrics:
- `Produce`, `Fetch`, `Metadata`, `ListOffsets`, `OffsetCommit`, `OffsetFetch`
- `FindCoordinator`, `JoinGroup`, `Heartbeat`, `LeaveGroup`, `SyncGroup`
- `DescribeGroups`, `ListGroups`, `ApiVersions`, `CreateTopics`, `DeleteTopics`

## Metric Naming Conventions

1. **Prefix indicates source**:
   - `host_` - System metrics
   - `jvm_` - JVM metrics
   - `kaf_` - Kafka metrics

2. **Middle part indicates component**:
   - Examples: `KafkaController`, `ReplicaManager`, `BrokerTopicMetrics`, `RequestMetrics`

3. **Suffix indicates measurement**:
   - Examples: `Count`, `PerSec`, `TimeMs`, `Percent`

## Notes

- Kafka metrics use `kaf_` prefix consistently
- Many metrics use `axonfunction='rate'` for per-second calculations
- Connect metrics have their own sub-namespaces for different components
- Some metrics are topic-specific (with `topic` attribute) while others are cluster-wide
- Percentile functions are commonly available for latency metrics
- The `rack` and `host_id` attributes enable filtering by location and specific broker