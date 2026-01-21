---
title: "AxonOps Kafka Overview Dashboard Metrics Mapping"
description: "Kafka overview dashboard metrics mapping. Cluster health and throughput."
meta:
  - name: keywords
    content: "Kafka overview metrics, cluster health, throughput"
search:
  boost: 8
---

# AxonOps Kafka Overview Dashboard Metrics Mapping

This document maps the metrics used in the AxonOps Kafka Overview dashboard.

## Dashboard Overview

The Kafka Overview dashboard provides a comprehensive view of Kafka cluster health, including controller status, partition health, replication status, network throughput, and consumer group coordination. It serves as the primary dashboard for monitoring overall Kafka cluster performance and health.

## Metrics Mapping

### Controller Metrics

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `kaf_KafkaController_ActiveControllerCount` | Number of active controllers in the cluster (should be 1) | `rack`, `host_id` |
| `kaf_KafkaController_OfflinePartitionsCount` | Number of partitions without an active leader | `dc`, `rack`, `host_id` |
| `kaf_KafkaController_PreferredReplicaImbalanceCount` | Number of partitions where preferred replica is not the leader | `dc`, `rack`, `host_id` |
| `kaf_ControllerStats_UncleanLeaderElectionsPerSec` | Rate of unclean leader elections | `function` (MeanRate), `rack`, `host_id` |

### Replica Manager Metrics

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `kaf_ReplicaManager_UnderMinIsrPartitionCount` | Partitions with fewer than minimum in-sync replicas | `dc`, `rack`, `host_id` |
| `kaf_ReplicaManager_UnderReplicatedPartitions` | Number of under-replicated partitions | `dc`, `rack`, `host_id` |
| `kaf_ReplicaManager_PartitionCount` | Total number of partitions on the broker | `dc`, `rack`, `host_id` |
| `kaf_ReplicaManager_LeaderCount` | Number of partitions for which this broker is the leader | `rack`, `host_id` |
| `kaf_ReplicaManager_IsrShrinksPerSec` | Rate of ISR shrinks | `function` (MeanRate), `rack`, `host_id` |
| `kaf_ReplicaManager_IsrExpandsPerSec` | Rate of ISR expansions | `function` (MeanRate), `rack`, `host_id` |

### Broker Topic Metrics

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `kaf_BrokerTopicMetrics_BytesInPerSec` | Incoming byte rate | `axonfunction` (rate), `rack`, `host_id`, `topic`, `node_type` |
| `kaf_BrokerTopicMetrics_BytesOutPerSec` | Outgoing byte rate | `axonfunction` (rate), `rack`, `host_id`, `topic`, `node_type` |
| `kaf_BrokerTopicMetrics_MessagesInPerSec` | Incoming message rate | `axonfunction` (rate), `rack`, `host_id`, `topic` |

### Network Metrics

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `kaf_socket_server_metrics_` | Socket server connection metrics | `function` (connection_count), `rack`, `host_id` |
| `kaf_KafkaRequestHandlerPool_RequestHandlerAvgIdlePercent` | Request handler idle percentage | `function` (OneMinuteRate), `rack`, `host_id` |

### Group Coordinator Metrics

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `kaf_GroupMetadataManager_NumGroups` | Total number of consumer groups | `rack`, `host_id` |
| `kaf_GroupMetadataManager_NumGroupsStable` | Number of stable consumer groups | `rack`, `host_id` |
| `kaf_GroupMetadataManager_NumGroupsPreparingRebalance` | Groups preparing to rebalance | `rack`, `host_id` |
| `kaf_GroupMetadataManager_NumGroupsDead` | Number of dead consumer groups | `rack`, `host_id` |
| `kaf_GroupMetadataManager_NumGroupsCompletingRebalance` | Groups completing rebalance | `rack`, `host_id` |
| `kaf_GroupMetadataManager_NumGroupsEmpty` | Number of empty consumer groups | `rack`, `host_id` |

### Request Metrics

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `kaf_RequestMetrics_RequestsPerSec` | Request rate per second | `axonfunction` (rate), `function` (Count), `request`, `rack`, `host_id` |
| `kaf_RequestMetrics_TotalTimeMs` | Total request processing time | `request` (Fetch), `function` (percentiles), `rack`, `host_id` |

## Query Examples

### Healthcheck Queries
```promql
// Active Controllers (should be 1)
sum(kaf_KafkaController_ActiveControllerCount{host_id!=""})

// Under min insync replicas partitions
kaf_ReplicaManager_UnderMinIsrPartitionCount{dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}

// Under Replicated Partitions
kaf_ReplicaManager_UnderReplicatedPartitions{dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}

// Offline Partitions
kaf_KafkaController_OfflinePartitionsCount{dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}
```

### Network Throughput
```promql
// Cluster network throughput - Bytes in
sum(kaf_BrokerTopicMetrics_BytesInPerSec{axonfunction='rate',rack=~'$rack',host_id=~'$host_id', topic!='',node_type='$node_type'})

// Cluster network throughput - Bytes out
sum(kaf_BrokerTopicMetrics_BytesOutPerSec{axonfunction='rate',rack=~'$rack',host_id=~'$host_id', topic!='',node_type='$node_type'})

// Incoming Messages
sum(kaf_BrokerTopicMetrics_MessagesInPerSec{axonfunction='rate',rack=~'$rack',host_id=~'$host_id', topic=''})
```

### Group Coordinator
```promql
// Consumer groups per coordinator
kaf_GroupMetadataManager_NumGroups{rack=~'$rack',host_id=~'$host_id'}

// Consumer groups by state
sum(kaf_GroupMetadataManager_NumGroupsStable{rack=~'$rack',host_id=~'$host_id'})
sum(kaf_GroupMetadataManager_NumGroupsPreparingRebalance{rack=~'$rack',host_id=~'$host_id'})
sum(kaf_GroupMetadataManager_NumGroupsDead{rack=~'$rack',host_id=~'$host_id'})
```

### Request Rates
```promql
// Total Request Per Sec
sum(kaf_RequestMetrics_RequestsPerSec{axonfunction='rate',function='Count',rack=~'$rack',host_id=~'$host_id'}) by (host_id)

// Metadata Request Per Sec
sum(kaf_RequestMetrics_RequestsPerSec{axonfunction='rate',function='Count',request='Metadata',rack=~'$rack',host_id=~'$host_id'}) by (host_id)
```

## Panel Organization

### Healthcheck Section
- **Active Controllers** - Counter showing cluster controller status

- **Brokers Online** - Number of active brokers

- **Online Partitions** - Total partition count

- **Offline Partitions** - Partitions without leaders

- **Preferred Replica Imbalance** - Leader distribution health

- **Under Replicated Partitions** - Replication lag indicator

- **Connections** - Total client connections

- **Under min insync replicas partitions** - Critical replication status

- **Unclean Leader Election Rate** - Data loss risk indicator

- **Cluster network throughput** - Overall I/O performance

- **Incoming Messages** - Message ingestion rate

- **Cluster Connections** - Connection trend

### General Section
- **Broker Count** - Total brokers in cluster

- **Active Controller** - Controller assignment over time

- **Request Handler Avg Idle Percent** - Request handler capacity

- **Under Replicated Partitions** - Replication health trends

- **Unclean Leader Elections Per Sec** - Data integrity monitoring

- **In-sync replicas Shrinks vs Expands** - ISR stability

### Group Coordinator Section
- **Consumer groups number per coordinator** - Group distribution

- **No consumer groups per state** - Group lifecycle monitoring

### Request Rate Section
- **Total Request Per Sec** - Overall request load

- **Metadata Request Per Sec** - Metadata request patterns

## Filters

- **rack** - Filter by rack location

- **node** (`host_id`) - Filter by specific Kafka broker

- **topic** - Filter by Kafka topic

- **node type** - Filter by node type

- **percentile** - Select latency percentile (for request metrics)

- **groupBy** - Dynamic grouping (topic, host_id)

## Understanding the Metrics

### Critical Health Indicators
- **Active Controllers**: Must be exactly 1. More or less indicates cluster issues

- **Offline Partitions**: Should be 0. Any value > 0 means data unavailability

- **Under Replicated Partitions**: Should be 0. Indicates replication lag

- **Under Min ISR**: Critical - indicates potential data loss risk

### Performance Indicators
- **Network Throughput**: Monitor for capacity planning

- **Request Handler Idle %**: Lower values indicate high load

- **ISR Shrinks/Expands**: Frequent changes indicate instability

### Consumer Group Health
**Group States**:

   - Stable: Normal operating state
   - Rebalancing: Temporary during membership changes
   - Dead: Groups that need cleanup
   - Empty: Groups without active members

## Best Practices

### Monitoring Guidelines
**Set Alerts for**:

   - Active Controllers ≠ 1
   - Offline Partitions > 0
   - Under Replicated Partitions > 0
   - Unclean Leader Elections > 0

**Regular Checks**:

   - Network throughput trends
   - Consumer group stability
   - Request rate patterns

### Troubleshooting

**No Active Controller**:

   - Check ZooKeeper connectivity
   - Review controller logs
   - Verify network partitions

**High Under-Replicated Partitions**:

   - Check broker health
   - Verify network bandwidth
   - Review replica lag settings

**Consumer Group Issues**:

   - Monitor rebalance frequency
   - Check consumer lag
   - Verify coordinator load

## Data Resolution

- Most metrics use `low` resolution for efficiency
- Rate metrics use `axonfunction='rate'` for accurate per-second calculations
- Percentile metrics available for latency measurements

## Units

- **Bytes**: Network throughput (bytes/sec)

- **short**: Counts and rates

- **percent**: Utilization metrics (0-100)

- **rps**: Requests per second

## Notes

- Empty topic filter (`topic=''`) shows aggregate metrics
- `host_id!=""` ensures only active brokers are counted
- The `node_type` filter allows monitoring mixed clusters
- ISR metrics use `MeanRate` for smoothed values