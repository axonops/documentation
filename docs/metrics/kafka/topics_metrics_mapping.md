# Kafka Topics Dashboard Metrics Mapping

## Overview

The Kafka Topics Dashboard provides detailed monitoring of individual topic performance and health. It tracks message throughput, byte rates, log sizes, segment counts, and offset progression to help manage and optimize topic performance.

## Metrics Mapping

| Dashboard Metric | Description | Attributes |
|-----------------|-----------|-------------|
| **Topic Throughput Metrics** |
| `kaf_BrokerTopicMetrics_MessagesInPerSec` | Rate of messages produced to topic | topic={topic} |
| `kaf_BrokerTopicMetrics_BytesInPerSec` | Rate of bytes produced to topic | topic={topic} |
| `kaf_BrokerTopicMetrics_BytesOutPerSec` | Rate of bytes consumed from topic | topic={topic} |
| **Log Metrics** |
| `kaf_Log_LogEndOffset` | End offset of the log | topic={topic}, partition={partition} |
| `kaf_Log_NumLogSegments` | Number of log segments | topic={topic}, partition={partition} |
| `kaf_Log_Size` | Size of the log in bytes | topic={topic}, partition={partition} |
| **Log Manager Metrics** |
| `kaf_LogManager_LogDirectoryOffline` | Number of offline log directories | logDirectory={path} |

## Query Examples

### Topic Throughput - General View
```promql
# Messages in per topic
sum(kaf_BrokerTopicMetrics_MessagesInPerSec{axonfunction='rate',rack=~'$rack',host_id=~'$host_id',topic!='',topic='$topic'}) by (topic)

# Bytes in per topic
sum(kaf_BrokerTopicMetrics_BytesInPerSec{axonfunction='rate',rack=~'$rack',host_id=~'$host_id', topic!='', topic='$topic'}) by(topic)

# Bytes out per topic
sum(kaf_BrokerTopicMetrics_BytesOutPerSec{axonfunction='rate',rack=~'$rack',host_id=~'$host_id', topic!='',topic='$topic'}) by(topic)
```

### Topic Throughput - Detailed View
```promql
# Messages in per topic (all topics)
sum(kaf_BrokerTopicMetrics_MessagesInPerSec{axonfunction='rate',rack=~'$rack',host_id=~'$host_id',topic=~'$topic',topic!=''}) by (topic)

# Bytes in per topic (all topics)
sum(kaf_BrokerTopicMetrics_BytesInPerSec{axonfunction='rate', topic='$topic',rack=~'$rack',host_id=~'$host_id',topic!=''}) by (topic)

# Bytes out per topic (all topics)
sum(kaf_BrokerTopicMetrics_BytesOutPerSec{axonfunction='rate', topic='$topic',rack=~'$rack',host_id=~'$host_id',topic!=''}) by (topic)
```

### Log Offset and Segments
```promql
# End offset increase rate per topic
sum(rate(kaf_Log_LogEndOffset{rack=~'$rack',host_id=~'$host_id',topic!='',topic='$topic'}[5m])) by (topic)

# Number of log segments per topic
sum(kaf_Log_NumLogSegments{rack=~'$rack',host_id=~'$host_id',topic='$topic'}) by (topic)
```

### Log Size Metrics
```promql
# Log size per topic
sum(kaf_Log_Size{rack=~'$rack',host_id=~'$host_id', topic='$topic'}) by (topic)

# Log size per broker
sum(kaf_Log_Size{rack=~'$rack',host_id=~'$host_id', topic='$topic'}) by (host_id)

# Offline log directories
kaf_LogManager_LogDirectoryOffline{rack=~'$rack',host_id=~'$host_id'}
```

## Panel Organization

1. **Overview Section**
   - Empty row for spacing/organization

2. **General**
   - Messages In
   - Bytes In
   - Bytes Out
   - End Offset Increase Per Topic
   - No. Log Segments per topic

3. **Log Size**
   - Log size per Topic
   - Log size per Broker
   - Log Directories Offline

4. **Throughput**
   - Messages In Per Topic
   - Bytes In Per Topic
   - Bytes Out Per Topic

## Filters

- **rack**: Filter by rack location
- **host_id**: Filter by specific host/broker
- **topic**: Filter by specific topic(s)
- **percentile**: Select percentile for latency metrics
- **groupBy**: Group results by rack or host_id

## Best Practices

1. **Topic Throughput Monitoring**
   - Monitor message and byte rates for capacity planning
   - Identify hot topics with disproportionate traffic
   - Compare bytes in vs bytes out for consumption patterns

2. **Log Management**
   - Monitor log sizes to prevent disk space issues
   - Track segment counts for retention policy effectiveness
   - Watch for rapid offset increases indicating high activity

3. **Performance Analysis**
   - High bytes in with low messages indicates large messages
   - Compare throughput across brokers for load distribution
   - Monitor topic growth trends for capacity planning

4. **Log Directory Health**
   - Offline log directories indicate disk failures
   - Requires immediate attention to prevent data loss
   - May trigger under-replicated partitions

5. **Segment Management**
   - High segment counts may impact performance
   - Consider adjusting segment.ms or segment.bytes
   - Monitor segment creation rate for tuning

6. **Topic-Specific Tuning**
   - Different topics may need different configurations
   - High-throughput topics may need more partitions
   - Consider compression for high-volume topics

7. **Retention Monitoring**
   - Log size indicates retention effectiveness
   - Monitor growth rate vs retention settings
   - Ensure cleanup policies are working correctly