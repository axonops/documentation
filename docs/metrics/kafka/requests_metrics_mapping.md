# Kafka Requests Dashboard Metrics Mapping

## Overview

The Kafka Requests Dashboard provides comprehensive monitoring of request rates, processing times, and message conversions across your Kafka cluster. It helps identify performance bottlenecks, track request patterns, and monitor client compatibility issues.

## Metrics Mapping

| Dashboard Metric | Description | Attributes |
|-----------------|-----------|-------------|
| **Request Rate Metrics** |
| `kaf_RequestMetrics_RequestsPerSec` | Rate of requests per second by type | request={type} |
| `kaf_BrokerTopicMetrics_TotalProduceRequestsPerSec` | Produce requests per second per topic | topic={topic} |
| `kaf_BrokerTopicMetrics_TotalFetchRequestsPerSec` | Fetch requests per second per topic | topic={topic} |
| **Request Timing Metrics** |
| `kaf_RequestMetrics_TotalTimeMs` | Total time to process requests | request={type} |
| `kaf_RequestMetrics_RequestQueueTimeMs` | Time requests spend in queue | request={type} |
| **Message Conversion Metrics** |
| `kaf_BrokerTopicMetrics_FetchMessageConversionsPerSec` | Rate of message conversions during fetch | - |
| `kaf_BrokerTopicMetrics_ProduceMessageConversionsPerSec` | Rate of message conversions during produce | - |
| **Client Metrics** |
| `kaf_socket_server_metrics_` (function='connections') | Client connections by version | listener={listener}, clientSoftwareName={name}, clientSoftwareVersion={version} |

## Query Examples

### Request Rates
```promql
# Total requests per second per broker
sum(kaf_RequestMetrics_RequestsPerSec{axonfunction='rate',function='Count',rack=~'$rack',host_id=~'$host_id'}) by (host_id)

# Produce requests per second
sum(kaf_RequestMetrics_RequestsPerSec{axonfunction='rate',function='Count',request='Produce',rack=~'$rack',host_id=~'$host_id'}) by (host_id)

# Fetch consumer requests per second
sum(kaf_RequestMetrics_RequestsPerSec{axonfunction='rate',function='Count',request='FetchConsumer',rack=~'$rack',host_id=~'$host_id'}) by (host_id)

# Metadata requests per second
sum(kaf_RequestMetrics_RequestsPerSec{axonfunction='rate',function='Count',request='Metadata',rack=~'$rack',host_id=~'$host_id'}) by (host_id)
```

### Topic-Level Request Rates
```promql
# Produce requests per topic
sum(kaf_BrokerTopicMetrics_TotalProduceRequestsPerSec{axonfunction='rate',function='Count',rack=~'$rack',host_id=~'$host_id', topic!=''}) by (topic)

# Fetch requests per topic
sum(kaf_BrokerTopicMetrics_TotalFetchRequestsPerSec{axonfunction='rate',function='Count',rack=~'$rack',host_id=~'$host_id',topic=~'$topic', topic!=''}) by (topic)
```

### Request Processing Times
```promql
# Produce request total time
kaf_RequestMetrics_TotalTimeMs{request='Produce',function=~'$percentile',rack=~'$rack',host_id=~'$host_id'}

# Fetch request total time
kaf_RequestMetrics_TotalTimeMs{request='Fetch',function=~'$percentile',rack=~'$rack',host_id=~'$host_id'}

# Fetch follower request total time
kaf_RequestMetrics_TotalTimeMs{request='FetchFollower',function=~'$percentile',rack=~'$rack',host_id=~'$host_id'}
```

### Request Queue Times
```promql
# Fetch request queue time
kaf_RequestMetrics_RequestQueueTimeMs{request='Fetch',function=~'$percentile',rack=~'$rack',host_id=~'$host_id'}

# Fetch follower request queue time
kaf_RequestMetrics_RequestQueueTimeMs{request='FetchFollower',function=~'$percentile',rack=~'$rack',host_id=~'$host_id'}
```

### Message Conversions
```promql
# Fetch message conversions per second
sum(kaf_BrokerTopicMetrics_FetchMessageConversionsPerSec{axonfunction='rate',rack=~'$rack',host_id=~'$host_id'})

# Produce message conversions per second
kaf_BrokerTopicMetrics_ProduceMessageConversionsPerSec{function='MeanRate',rack=~'$rack',host_id=~'$host_id'}

# Client version distribution
sum(kaf_socket_server_metrics_{function='connections',rack=~'$rack',host_id=~'$host_id'}) by (clientSoftwareVersion, clientSoftwareName)
```

## Panel Organization

**Overview Section**

   - Empty row for spacing/organization

**Requests**

   - Total Request Per Sec
   - Metadata Request Per Sec
   - Produce Request Per Sec
   - Fetch Request Per Sec
   - Produce request per sec per topic
   - Fetch request per sec per topic

**Request Times**

   - Produce Time
   - Fetch Time
   - FetchFollower Time

**Request Queues**

   - Request Queue Fetch Follower Requests Time
   - Request Queue Fetch Requests Time

**Message Conversion**

   - Number of produced message conversion
   - Number of consumed message conversion
   - Client version repartition

## Filters

- **rack**: Filter by rack location

- **host_id**: Filter by specific host/broker

- **topic**: Filter by specific topic(s)

- **percentile**: Select percentile for latency metrics (50th, 95th, 99th, etc.)

## Best Practices

**Request Rate Monitoring**

   - Monitor total request rates for capacity planning
   - High metadata request rates may indicate client issues
   - Balance request rates across brokers

**Request Timing Analysis**

   - Monitor 99th percentile for worst-case scenarios
   - High total time indicates processing bottlenecks
   - Compare request types to identify slow operations

**Queue Time Monitoring**

   - High queue times indicate thread pool saturation
   - Consider increasing request handler threads
   - Queue time should be minimal compared to total time

**Message Conversion Impact**

   - Message conversions impact performance significantly
   - High conversion rates suggest client version mismatches
   - Update clients to match broker message format version

**Client Version Management**

   - Monitor client version distribution
   - Identify and upgrade outdated clients
   - Ensure compatibility with broker version

**Performance Tuning**

   - Adjust `num.network.threads` for high request rates
   - Tune `num.io.threads` for I/O operations
   - Monitor and adjust `queued.max.requests`

**Troubleshooting**

   - High produce times: Check replication settings
   - High fetch times: Review consumer configurations
   - Message conversions: Align client/broker versions