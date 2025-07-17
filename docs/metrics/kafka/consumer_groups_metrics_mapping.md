# Kafka Consumer Groups Dashboard Metrics Mapping

## Overview

The Kafka Consumer Groups Dashboard provides monitoring of consumer group lag across topics and partitions. This dashboard is essential for tracking consumer performance, identifying consumption bottlenecks, and ensuring consumers are keeping up with producers.

## Metrics Mapping

| Dashboard Metric | Description | Attributes |
|-----------------|-----------|-------------|
| **Consumer Group Metrics** |
| `kaf_consumer_group` | Consumer group lag per partition | client-id={client-id} |

Note: Consumer group metrics are typically collected from Kafka's consumer group command-line tools or APIs rather than JMX, as they represent cluster-wide state rather than individual broker metrics.

## Query Examples

### Consumer Group Lag
```promql
# Consumer group lag by group, topic, and partition
sum(kaf_consumer_group{Topic='$topic',GroupID='$groupid'}) by (GroupID, Topic, Partition)

# Total lag for a consumer group across all partitions
sum(kaf_consumer_group{GroupID='$groupid'}) by (GroupID)

# Lag for specific topic
sum(kaf_consumer_group{Topic='$topic'}) by (GroupID, Partition)
```

## Panel Organization

1. **Overview Section**
   - Empty row for spacing/organization

2. **Consumer Groups**
   - Consumer Group Lag (detailed view by GroupID, Topic, and Partition)

## Filters

- **groupid**: Filter by specific consumer group ID(s)
- **topic**: Filter by specific topic(s)

## Best Practices

1. **Lag Monitoring**
   - Monitor lag trends over time, not just absolute values
   - Set alerts for increasing lag trends
   - Consider normal lag during consumer restarts

2. **Performance Analysis**
   - High lag indicates consumers can't keep up with producers
   - Compare lag across partitions to identify imbalances
   - Monitor lag spikes during peak traffic

3. **Consumer Group Health**
   - Zero lag doesn't always mean healthy consumption
   - Check for stalled consumers (lag not changing)
   - Monitor consumer group state (active, rebalancing, dead)

4. **Troubleshooting High Lag**
   - Check consumer processing time
   - Verify consumer parallelism matches partition count
   - Look for rebalancing issues
   - Check for consumer errors or failures

5. **Capacity Planning**
   - Use lag trends for scaling decisions
   - Add consumers when lag consistently increases
   - Monitor lag during traffic peaks

6. **Partition Assignment**
   - Ensure even distribution of partitions to consumers
   - Monitor for partition ownership changes
   - Check for idle consumers (no partitions assigned)

7. **Alert Configuration**
   - Alert on lag threshold (e.g., > 100k messages)
   - Alert on lag growth rate
   - Alert on consumer group state changes
   - Different thresholds for different topics/groups