# Kafka Replication Dashboard Metrics Mapping

## Overview

The Kafka Replication Dashboard provides comprehensive monitoring of Kafka's data replication health and performance. It tracks partition states, ISR (In-Sync Replica) changes, and request latencies for both leaders and followers to ensure data durability and availability.

## Metrics Mapping

| Dashboard Metric | Description | Attributes |
|-----------------|-----------|-------------|
| **Partition State Metrics** |
| `kaf_ReplicaManager_UnderReplicatedPartitions` | Number of under-replicated partitions | - |
| `kaf_KafkaController_OfflinePartitionsCount` | Number of offline partitions | - |
| `kaf_ReplicaManager_PartitionCount` | Total number of partitions on the broker | - |
| `kaf_ReplicaManager_UnderMinIsrPartitionCount` | Partitions with ISR count below min.insync.replicas | - |
| **ISR Change Metrics** |
| `kaf_ReplicaManager_IsrShrinksPerSec` | Rate of ISR shrinks per second | - |
| `kaf_ReplicaManager_IsrExpandsPerSec` | Rate of ISR expansions per second | - |
| **Leader Request Metrics** |
| `kaf_RequestMetrics_LocalTimeMs` (request='FetchFollower') | Time leader spends processing follower fetch requests | request=FetchFollower |
| `kaf_RequestMetrics_LocalTimeMs` (request='Fetch') | Time leader spends processing consumer fetch requests | request=Fetch |
| `kaf_RequestMetrics_LocalTimeMs` (request='FetchConsumer') | Time leader spends processing consumer fetch requests | request=FetchConsumer |
| `kaf_RequestMetrics_LocalTimeMs` (request='Produce') | Time leader spends processing produce requests | request=Produce |
| **Follower Request Metrics** |
| `kaf_RequestMetrics_RemoteTimeMs` (request='Produce') | Time follower waits for produce replication | request=Produce |
| `kaf_RequestMetrics_RemoteTimeMs` (request='Fetch') | Time follower waits for fetch requests | request=Fetch |
| `kaf_RequestMetrics_RemoteTimeMs` (request='FetchConsumer') | Time follower waits for consumer fetch | request=FetchConsumer |
| `kaf_RequestMetrics_RemoteTimeMs` (request='FetchFollower') | Time follower waits for follower fetch | request=FetchFollower |

## Query Examples

### Partition Health
```promql
# Under-replicated partitions
kaf_ReplicaManager_UnderReplicatedPartitions{rack=~'$rack',host_id=~'$host_id'}

# Offline partitions
kaf_KafkaController_OfflinePartitionsCount{rack=~'$rack',host_id=~'$host_id'}

# Total partition count
kaf_ReplicaManager_PartitionCount{rack=~'$rack',host_id=~'$host_id'}

# Under min ISR partitions
kaf_ReplicaManager_UnderMinIsrPartitionCount{rack=~'$rack',host_id=~'$host_id'}
```

### ISR Changes
```promql
# ISR shrink rate
kaf_ReplicaManager_IsrShrinksPerSec{function='MeanRate',rack=~'$rack',host_id=~'$host_id'}

# ISR expand rate
kaf_ReplicaManager_IsrExpandsPerSec{function='MeanRate', rack=~'$rack',host_id=~'$host_id'}
```

### Leader Performance
```promql
# Leader processing time for follower fetch requests
kaf_RequestMetrics_LocalTimeMs{request='FetchFollower',function=~'$percentile',rack=~'$rack',host_id=~'$host_id'}

# Leader processing time for consumer fetch requests
kaf_RequestMetrics_LocalTimeMs{request='Fetch',function=~'$percentile',rack=~'$rack',host_id=~'$host_id'}

# Leader processing time for produce requests
kaf_RequestMetrics_LocalTimeMs{request='Produce',function=~'$percentile',rack=~'$rack',host_id=~'$host_id'}
```

### Follower Performance
```promql
# Follower wait time for produce replication
kaf_RequestMetrics_RemoteTimeMs{request='Produce', function=~'$percentile',rack=~'$rack',host_id=~'$host_id'}

# Follower wait time for fetch requests
kaf_RequestMetrics_RemoteTimeMs{request='Fetch',function=~'$percentile',rack=~'$rack',host_id=~'$host_id'}

# Follower wait time for follower fetch
kaf_RequestMetrics_RemoteTimeMs{request='FetchFollower',function=~'$percentile',rack=~'$rack',host_id=~'$host_id'}
```

## Panel Organization

**Overview Section**

   - Empty row for spacing/organization

**Replication**

   - Under Replicated Partitions
   - Online Partitions
   - Offline Partitions
   - Under Min ISR Partitions

**Leader Performance**

   - Leader FetchFollower Requests
   - Leader Fetch Requests
   - Leader FetchConsumer Requests
   - Leader Produce Requests

**Follower Performance**

   - Follower Produce Requests Time
   - Follower Fetch Requests Time
   - Follower FetchConsumer Request Time
   - Follower FetchFollower Request Time

**ISR Shrinks / Expands**

   - IsrShrinks per Sec by Host
   - IsrExpands per Sec By Host

## Filters

- **rack**: Filter by rack location

- **host_id**: Filter by specific host/broker

- **percentile**: Select percentile for latency metrics (50th, 95th, 99th, etc.)

## Best Practices

**Partition Health Monitoring**

   - Under-replicated partitions should be 0
   - Offline partitions indicate serious issues
   - Monitor under min ISR for potential data loss risk

**ISR Monitoring**

   - Frequent ISR shrinks indicate replication lag
   - High ISR churn suggests network or performance issues
   - ISR expansions should follow shrinks during recovery

**Leader Performance**

   - Monitor leader request processing times
   - High FetchFollower times indicate replication bottlenecks
   - Compare produce vs fetch latencies

**Follower Performance**

   - High RemoteTimeMs indicates replication delays
   - Monitor follower fetch times for lag issues
   - Ensure followers can keep up with leaders

**Replication Tuning**

   - Adjust `replica.lag.time.max.ms` for ISR membership
   - Tune `num.replica.fetchers` for better throughput
   - Monitor `min.insync.replicas` compliance

**Troubleshooting**

   - Under-replicated partitions: Check broker health and network
   - ISR shrinks: Investigate disk I/O and network latency
   - High follower lag: Check replication thread count
   - Offline partitions: Critical issue requiring immediate attention