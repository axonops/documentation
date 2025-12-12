---
description: "Kafka performance dashboard metrics mapping. Latency and throughput statistics."
meta:
  - name: keywords
    content: "Kafka performance metrics, latency, throughput"
---

# AxonOps Kafka Performance Dashboard Metrics Mapping

## Overview

The Kafka Performance Dashboard provides detailed insights into Kafka broker performance, including request processing times, throughput metrics, thread utilization, and queue sizes. This dashboard is essential for identifying performance bottlenecks and optimizing Kafka cluster performance.

## Metrics Mapping

| Dashboard Metric | Description | Attributes |
|-----------------|-----------|-------------|
| **Request Timing Metrics** | | | |
| `kaf_RequestMetrics_TotalTimeMs` | Total time to process requests (produce/fetch) | request={Produce,Fetch,FetchFollower} |
| `kaf_RequestMetrics_RequestQueueTimeMs` | Time requests spend in request queue | request={Fetch,FetchFollower} |
| **Throughput Metrics** | | | |
| `kaf_BrokerTopicMetrics_MessagesInPerSec` | Rate of messages received per second | topic={topic} |
| `kaf_BrokerTopicMetrics_BytesInPerSec` | Rate of bytes received per second | topic={topic} |
| `kaf_BrokerTopicMetrics_BytesOutPerSec` | Rate of bytes sent per second | topic={topic} |
| **Queue Metrics** | | | |
| `kaf_RequestChannel_RequestQueueSize` | Current size of request queue | - |
| `kaf_RequestChannel_ResponseQueueSize` | Current size of response queue | processor={id} |
| **Thread Utilization Metrics** | | | |
| `kaf_SocketServer_NetworkProcessorAvgIdlePercent` | Average idle percentage of network threads | - |
| `kaf_KafkaRequestHandlerPool_RequestHandlerAvgIdlePercent` | Average idle percentage of request handler threads | - |
| **Purgatory Metrics** | | | |
| `kaf_DelayedOperationPurgatory_PurgatorySize` | Number of delayed operations in purgatory | delayedOperation={Produce,Fetch} |

## Query Examples

### Request Processing Time
```promql
// Total time for produce requests (selected percentile)
kaf_RequestMetrics_TotalTimeMs{request='Produce',function='$percentile',rack=~'$rack',host_id=~'$host_id'}

// Total time for fetch requests
kaf_RequestMetrics_TotalTimeMs{request='Fetch',function='$percentile',rack=~'$rack',host_id=~'$host_id'}

// Total time for follower fetch requests
kaf_RequestMetrics_TotalTimeMs{request='FetchFollower',function='$percentile',rack=~'$rack',host_id=~'$host_id'}
```

### Message Throughput
```promql
// Messages per second per broker
sum(kaf_BrokerTopicMetrics_MessagesInPerSec{axonfunction='rate',rack=~'$rack',host_id=~'$host_id',topic=~'$topic'}) by (host_id)

// Bytes in per second per broker
sum(kaf_BrokerTopicMetrics_BytesInPerSec{axonfunction='rate',rack=~'$rack',host_id=~'$host_id',topic=~'$topic'}) by (host_id)

// Bytes out per second per broker
sum(kaf_BrokerTopicMetrics_BytesOutPerSec{axonfunction='rate',rack=~'$rack',host_id=~'$host_id',topic=~'$topic'}) by (host_id)
```

### Thread Utilization
```promql
// Network processor idle percentage
kaf_SocketServer_NetworkProcessorAvgIdlePercent{rack=~'$rack',host_id=~'$host_id'} * 100

// Request handler idle percentage
kaf_KafkaRequestHandlerPool_RequestHandlerAvgIdlePercent{function='OneMinuteRate',rack=~'$rack',host_id=~'$host_id'} * 100
```

### Queue Sizes
```promql
// Request queue size
kaf_RequestChannel_RequestQueueSize{rack=~'$rack',host_id=~'$host_id'}

// Response queue size
kaf_RequestChannel_ResponseQueueSize{processor='', rack=~'$rack',host_id=~'$host_id'}
```

### Request Queue Time
```promql
// Fetch request queue time
kaf_RequestMetrics_RequestQueueTimeMs{request='Fetch',function=~'$percentile',rack=~'$rack',host_id=~'$host_id'}

// Follower fetch request queue time
kaf_RequestMetrics_RequestQueueTimeMs{request='FetchFollower',function=~'$percentile',rack=~'$rack',host_id=~'$host_id'}
```

### Purgatory Sizes
```promql
// Producer purgatory size
kaf_DelayedOperationPurgatory_PurgatorySize{delayedOperation='Produce',rack=~'$rack',host_id=~'$host_id'}

// Fetch purgatory size
kaf_DelayedOperationPurgatory_PurgatorySize{delayedOperation='Fetch', rack=~'$rack',host_id=~'$host_id'}
```

## Panel Organization

**Overview Section**

   - Empty row for spacing/organization

**Throughput**

   - Total time (produce/fetch) by percentile
   - Messages In Per Broker
   - Bytes In Per Broker
   - Bytes Out Per Broker

**Purgatory**

   - Producer Purgatory Size
   - Fetch Purgatory Size

**Request Queue**

   - Request Queue Fetch Follower Requests Time
   - Request Queue Fetch Requests Time

**Thread Utilization**

   - Request Queue Size
   - Response Queue Size
   - Network Processor Avg Idle Percent
   - Request Handler Avg Idle Percent

## Filters

- **rack**: Filter by rack location

- **host_id**: Filter by specific host/broker

- **percentile**: Select percentile for latency metrics (50th, 95th, 99th, etc.)

- **topic**: Filter metrics by specific topics

## Best Practices

**Request Latency Monitoring**

   - Monitor 99th percentile latencies to catch outliers
   - High total time indicates performance issues
   - Compare produce vs fetch latencies

**Throughput Monitoring**

   - Balance bytes in/out across brokers
   - Monitor message rates for capacity planning
   - Identify hot partitions or uneven load distribution

**Queue Monitoring**

   - Request queue size should remain low
   - High queue sizes indicate thread pool saturation
   - Monitor queue time to identify bottlenecks

**Thread Utilization**

   - Network processor idle % should be > 30%
   - Request handler idle % should be > 30%  
   - Low idle percentages indicate need for more threads

**Purgatory Monitoring**

   - High purgatory sizes indicate delayed operations
   - Producer purgatory: waiting for replication
   - Fetch purgatory: waiting for data availability

**Performance Tuning**

   - Adjust thread pools based on utilization
   - Optimize batch sizes for better throughput
   - Monitor and tune request timeouts