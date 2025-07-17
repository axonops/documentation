# Kafka Controller Dashboard Metrics Mapping

## Overview

The Kafka Controller Dashboard monitors the health and performance of the Kafka controller, particularly in KRaft mode (Kafka without ZooKeeper). It tracks Raft consensus metrics, metadata operations, authentication rates, and controller state changes.

## Metrics Mapping

| Dashboard Metric | Description | Attributes |
|-----------------|-----------|-------------|
| **Controller State Metrics** |
| `kaf_KafkaController_FencedBrokerCount` | Number of fenced (isolated) brokers | - |
| `kaf_KafkaController_LastAppliedRecordTimestamp` | Timestamp of last applied metadata record | - |
| `kaf_KafkaController_MetadataErrorCount` | Count of metadata errors | - |
| **Raft Consensus Metrics** |
| `kaf_raft_metrics_` (function='current_leader') | Current Raft leader node ID | function='current_leader' |
| `kaf_raft_metrics_` (function='log_end_offset') | End offset of the Raft log | function='log_end_offset' |
| `kaf_raft_metrics_` (function='commit_latency_avg') | Average commit latency | function='commit_latency_avg' |
| `kaf_raft_metrics_` (function='fetch_records_rate') | Rate of fetching records | function='fetch_records_rate' |
| **Raft Channel Metrics** |
| `kaf_raft_channel_metrics_` (function='request_rate') | Raft request rate | function='request_rate' |
| `kaf_raft_channel_metrics_` (function='successful_authentication_rate') | Successful authentication rate | function='successful_authentication_rate' |
| `kaf_raft_channel_metrics_` (function='failed_reauthentication_rate') | Failed re-authentication rate | function='failed_reauthentication_rate' |

## Query Examples

### Controller State
```promql
# Fenced broker count
kaf_KafkaController_FencedBrokerCount

# Last applied record timestamp rate of change
kaf_KafkaController_LastAppliedRecordTimestamp{axonfunction='rate'}

# Metadata error rate
kaf_KafkaController_MetadataErrorCount{axonfunction='rate'}
```

### Raft Leader Information
```promql
# Current Raft leader
kaf_raft_metrics_{function='current_leader'}

# Raft log end offset changes
sum(kaf_raft_metrics_{function='log_end_offset'}) by (host_id)
```

### Raft Performance
```promql
# Commit latency average
kaf_raft_metrics_{function='commit_latency_avg'}

# Fetch records rate
kaf_raft_metrics_{function='fetch_records_rate'}

# Request rate
kaf_raft_channel_metrics_{function='request_rate'}
```

### Authentication Metrics
```promql
# Successful authentication rate
kaf_raft_channel_metrics_{function='successful_authentication_rate'}

# Failed re-authentication rate
kaf_raft_channel_metrics_{function='failed_reauthentication_rate'}
```

## Panel Organization

1. **Overview Section**
   - Empty row for spacing/organization

2. **Controller**
   - Fenced Broker Count (counter)
   - Current Raft Leader (counter)
   - Last record offset timestamp
   - Raft log offset change
   - Commit Latency Avg
   - Fetch Records Rate
   - Raft Request Rate
   - Metadata Error Rate
   - New Active Controllers Count (placeholder)

3. **Authentication**
   - Successful Auth Rate
   - Failed Auth Rate

## Filters

Note: The controller dashboard has no configurable filters, as controller metrics are cluster-wide.

## Best Practices

1. **Controller Health Monitoring**
   - Fenced broker count should be 0 for healthy clusters
   - Monitor metadata error rate for controller issues
   - Track last applied record timestamp for activity

2. **Raft Consensus Monitoring**
   - Ensure stable Raft leader (minimal changes)
   - Monitor commit latency for consensus performance
   - High fetch records rate indicates active metadata changes

3. **Log Growth Monitoring**
   - Track Raft log offset growth rate
   - Rapid growth may indicate frequent metadata changes
   - Monitor for log compaction effectiveness

4. **Authentication Monitoring**
   - High failed authentication rates indicate security issues
   - Monitor successful auth rate for normal operations
   - Investigate spikes in failed re-authentication

5. **Performance Tuning**
   - Low commit latency ensures fast metadata propagation
   - Monitor request rates for controller load
   - Balance metadata operations across the cluster

6. **Troubleshooting**
   - Fenced brokers indicate network or configuration issues
   - Metadata errors suggest controller processing problems
   - Authentication failures may indicate credential issues

7. **KRaft Mode Considerations**
   - Controller metrics are specific to KRaft mode
   - In ZooKeeper mode, different metrics apply
   - Monitor for smooth leader elections and stable consensus