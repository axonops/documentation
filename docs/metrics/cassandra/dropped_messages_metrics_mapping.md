# AxonOps Dropped Messages Dashboard Metrics Mapping

This document maps the metrics used in the AxonOps Dropped Messages dashboard.

## Dashboard Overview

The Dropped Messages dashboard monitors when Cassandra drops messages due to overload or timeout conditions. Dropped messages are a critical indicator of cluster health and performance issues. When Cassandra cannot process messages within configured timeouts, it drops them to prevent system overload.

## Metrics Mapping

### Dropped Message Metrics

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `cas_DroppedMessage_Dropped` | Count of dropped messages by type | `scope` (message type), `function` (Count), `axonfunction` (rate), `dc`, `rack`, `host_id` |

## Message Types (Scopes)

### Data Operation Messages
| Scope | Description | Common Causes |
|-------|-------------|---------------|
| `MUTATION` | Write operations (INSERT, UPDATE, DELETE) | Write overload, slow disks, GC pauses |
| `COUNTER_MUTATION` | Counter column updates | Similar to MUTATION but for counter operations |
| `HINT` | Hinted handoff messages | Node recovery backlog, network issues |
| `READ` | Read operations (SELECT) | Read overload, large partitions, slow queries |
| `RANGE_SLICE` | Range queries (token ranges) | Large range scans, inefficient queries |
| `PAGED_RANGE` | Paginated range queries | Similar to RANGE_SLICE but with pagination |

### Repair and Maintenance Messages
| Scope | Description | Common Causes |
|-------|-------------|---------------|
| `READ_REPAIR` | Read repair operations | Inconsistent data, repair overload |
| `BATCH_STORE` | Batch log writes | Batch operation overload |
| `BATCH_REMOVE` | Batch log cleanup | Batch completion backlog |

### Internal Messages
| Scope | Description | Common Causes |
|-------|-------------|---------------|
| `REQUEST_RESPONSE` | Inter-node response messages | Network latency, coordinator overload |
| `_TRACE` | Tracing messages | Heavy tracing load |

## Query Examples

### Dropped Mutations per Second
```promql
cas_DroppedMessage_Dropped{axonfunction='rate',function='Count',scope='MUTATION',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}
```

### Dropped Hints per Second
```promql
cas_DroppedMessage_Dropped{axonfunction='rate',function='Count',scope='HINT',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}
```

### Dropped Reads per Second
```promql
cas_DroppedMessage_Dropped{axonfunction='rate',function='Count',scope='READ',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}
```

### Total Count Queries (not rate)
```promql
# Counter Mutations
cas_DroppedMessage_Dropped{function='Count',scope='COUNTER_MUTATION',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}

# Paged Range
cas_DroppedMessage_Dropped{function='Count',scope='PAGED_RANGE',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}
```

## Panel Organization

### Dropped Messages Section
Row 1:
1. **Dropped Mutation per secs** - Write operation drops
2. **Dropped Hints per secs** - Hinted handoff drops
3. **Dropped Read per secs** - Read operation drops

Row 2:
1. **Dropped Counter Mutation** - Counter operation drops (total count)
2. **Dropped Read Repair per secs** - Read repair drops
3. **Dropped Paged Range** - Paginated range query drops (total count)

Row 3:
1. **Dropped Batch Store** - Batch log write drops (total count)
2. **Dropped Batch Remove** - Batch log cleanup drops (total count)
3. **Dropped Request Response** - Inter-node response drops (total count)

Row 4:
1. **Dropped Range Slice** - Range query drops (total count)
2. **Dropped Trace** - Tracing message drops (total count)

## Filters

- **data center** (`dc`) - Filter by data center
- **rack** - Filter by rack
- **node** (`host_id`) - Filter by specific node
- **groupBy** - Dynamic grouping (dc, rack, host_id, keyspace)

## Understanding Dropped Messages

### Why Messages Are Dropped
1. **Timeout**: Message exceeds configured timeout
2. **Queue Full**: Internal queue reaches capacity
3. **Overload**: Node cannot keep up with request rate
4. **Resource Constraints**: Memory, CPU, or I/O limitations

### Message Type Timeouts (Default)
- `MUTATION`: 5000ms (write_request_timeout_in_ms)
- `READ`: 5000ms (read_request_timeout_in_ms)
- `RANGE_SLICE`: 10000ms (range_request_timeout_in_ms)
- `COUNTER_MUTATION`: 5000ms (counter_write_request_timeout_in_ms)
- `REQUEST_RESPONSE`: 10000ms (request_timeout_in_ms)

### Impact of Dropped Messages

1. **Dropped Mutations**:
   - Write failures at consistency level
   - Potential data loss if hints also dropped
   - Client receives timeout exceptions

2. **Dropped Reads**:
   - Read timeouts for clients
   - Incomplete query results
   - Application errors

3. **Dropped Hints**:
   - Delayed consistency
   - Requires repair to fix
   - Indicates replica communication issues

4. **Dropped Read Repairs**:
   - Inconsistencies persist longer
   - Manual repair may be needed
   - Background repair falling behind

## Troubleshooting Guide

### High Dropped Mutations
1. Check disk I/O performance
2. Monitor GC pauses
3. Review write load distribution
4. Consider increasing timeout
5. Check for large batches

### High Dropped Reads
1. Look for large partitions
2. Check read patterns
3. Monitor CPU usage
4. Review query efficiency
5. Consider read timeout increase

### High Dropped Hints
1. Check node availability
2. Monitor network health
3. Review hint storage capacity
4. Check for overloaded nodes
5. Consider hint delivery throttling

### General Recommendations
1. **Zero Tolerance**: Aim for zero dropped messages
2. **Early Warning**: Any drops indicate problems
3. **Root Cause**: Always investigate underlying cause
4. **Capacity Planning**: Drops often indicate need for scaling

## Units and Display

- **Rate Metrics**: messages per second (short)
- **Count Metrics**: absolute count (short)
- **Legend Format**: `$dc - $host_id`

## Best Practices

1. **Monitor Continuously**:
   - Set alerts for any dropped messages
   - Track trends over time
   - Correlate with other metrics

2. **Investigate Immediately**:
   - Dropped messages indicate serious issues
   - Check system resources
   - Review recent changes

3. **Preventive Measures**:
   - Proper capacity planning
   - Regular performance tuning
   - Appropriate timeout configuration
   - Load testing before production

## Notes

- Some panels show rate (`axonfunction='rate'`), others show total count
- Rate metrics are more useful for real-time monitoring
- Total counts help understand historical impact
- The `_TRACE` scope has underscore prefix in the actual metric