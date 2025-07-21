# AxonOps Coordinator Dashboard Metrics Mapping

This document maps the metrics used in the AxonOps Coordinator dashboard.

## Dashboard Overview

The Coordinator dashboard monitors coordinator-level request handling in Cassandra. When a client sends a request, the coordinator node handles the request and coordinates with replica nodes. This dashboard tracks latency and throughput broken down by consistency level, providing insights into how different consistency levels impact performance.

## Metrics Mapping

### Client Request Metrics

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `cas_ClientRequest_Latency` | Request latency at coordinator level | `scope` (Read*/Write*/RangeSlice), `function` (percentiles/count), `dc`, `rack`, `host_id` |
| `cas_Client_connectedNativeClients` | Number of connected native protocol clients | `dc`, `rack`, `host_id` |
| `cas_CommitLog_WaitingOnSegmentAllocation` | Time waiting for commit log segment allocation | `function` (percentile), `dc`, `rack`, `host_id` |

## Scope Patterns

### Read Operations
- `Read` - Simple read (no consistency level)
- `Read-ALL` - Read with ALL consistency
- `Read-ONE` - Read with ONE consistency
- `Read-TWO` - Read with TWO consistency
- `Read-THREE` - Read with THREE consistency
- `Read-QUORUM` - Read with QUORUM consistency
- `Read-LOCAL_QUORUM` - Read with LOCAL_QUORUM consistency
- `Read-EACH_QUORUM` - Read with EACH_QUORUM consistency
- `Read-SERIAL` - Read with SERIAL consistency
- `Read-LOCAL_SERIAL` - Read with LOCAL_SERIAL consistency
- `Read-LOCAL_ONE` - Read with LOCAL_ONE consistency

### Write Operations
- `Write` - Simple write (no consistency level)
- `Write-ALL` - Write with ALL consistency
- `Write-ANY` - Write with ANY consistency
- `Write-ONE` - Write with ONE consistency
- `Write-TWO` - Write with TWO consistency
- `Write-THREE` - Write with THREE consistency
- `Write-QUORUM` - Write with QUORUM consistency
- `Write-LOCAL_QUORUM` - Write with LOCAL_QUORUM consistency
- `Write-EACH_QUORUM` - Write with EACH_QUORUM consistency
- `Write-LOCAL_ONE` - Write with LOCAL_ONE consistency

### Range Operations
- `RangeSlice` - Range query operations (SELECT with ranges)

## Query Examples

### Coordinator Read Distribution (Pie Chart)
```promql
sum(cas_ClientRequest_Latency{axonfunction='rate',scope='Read*',scope!='Read',function='Count',function!='Min|Max',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by (scope)
```

### Coordinator Write Distribution (Pie Chart)
```promql
sum(cas_ClientRequest_Latency{axonfunction='rate',scope='Write*',scope!='Write',function='Count',function!='Min|Max',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by (scope)
```

### Read Latency by Consistency Level
```promql
cas_ClientRequest_Latency{scope='Read.*$consistency',function='$percentile',function!='Min|Max',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}
```

### Range Read Latency
```promql
cas_ClientRequest_Latency{scope='RangeSlice',function='$percentile',function!='Min|Max',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}
```

### Write Latency by Consistency Level
```promql
cas_ClientRequest_Latency{scope='Write.*$consistency',function='$percentile',function!='Min|Max',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}
```

### Read Throughput by Consistency
```promql
sum(cas_ClientRequest_Latency{axonfunction='rate',scope='Read.*$consistency',function='Count',function!='Min|Max',dc=~'$dc',rack=~'$rack', host_id=~'$host_id'}) by ($groupBy)
```

### Commit Log Waiting Time
```promql
cas_CommitLog_WaitingOnSegmentAllocation{dc=~'$dc',rack='$rack',host_id=~'$host_id',function='$percentile'}
```

## Panel Organization

### Consistency Distribution Section
1. **Coordinator Reads distribution** - Pie chart showing read request distribution by consistency level
2. **Coordinator Writes distribution** - Pie chart showing write request distribution by consistency level

### Latency Statistics By Node Section
1. **Coordinator Read $consistency Latency - $percentile** - Line chart for read latency at selected consistency
2. **Coordinator Range Read Request Latency - $percentile** - Line chart for range query latency
3. **Coordinator Write $consistency Latency - $percentile** - Line chart for write latency at selected consistency

### Throughput Statistics Section
1. **Coordinator Read Throughput Per $groupBy ($consistency) - Count Per Second** - Read operations per second
2. **Coordinator Range Read Request Throughput - Count Per Second** - Range queries per second
3. **Coordinator Write Throughput Per $groupBy ($consistency) - Count Per Second** - Write operations per second

### Connections Section
1. **Number of Native Connections per host** - Line chart showing client connections

### Commitlog Statistics Section
1. **Waiting on Segment Allocation** - Time spent waiting for commit log segments

## Filters

- **data center** (`dc`) - Filter by data center
- **rack** - Filter by rack
- **node** (`host_id`) - Filter by specific node
- **groupBy** - Dynamic grouping (dc, rack, host_id)
- **percentile** - Select latency percentile (50th, 75th, 95th, 98th, 99th, 999th)
- **consistency** - Filter by consistency level (ALL, ANY, ONE, TWO, THREE, SERIAL, QUORUM, etc.)

## Consistency Levels

### Strong Consistency
- **ALL** - All replicas must respond
- **QUORUM** - Majority of replicas must respond
- **LOCAL_QUORUM** - Majority in local datacenter
- **EACH_QUORUM** - Quorum in each datacenter

### Weak Consistency
- **ONE** - Only one replica must respond
- **TWO** - Two replicas must respond
- **THREE** - Three replicas must respond
- **ANY** - Any node can accept write (including hints)
- **LOCAL_ONE** - One replica in local datacenter

### Serial Consistency
- **SERIAL** - Linearizable consistency
- **LOCAL_SERIAL** - Linearizable in local datacenter

## Important Considerations

**Latency vs Consistency Trade-off**:

   - Higher consistency levels increase latency
   - Monitor percentiles to understand impact
   - Consider LOCAL variants for multi-DC

**Throughput Patterns**:

   - Distribution shows application consistency preferences
   - Imbalanced distribution may indicate issues
   - Monitor for consistency level changes

**Coordinator Load**:

   - Each node can be a coordinator
   - High coordinator load impacts performance
   - Balance using client-side load balancing

**Range Queries**:

   - Typically more expensive than point reads
   - Monitor separately from regular reads
   - Consider pagination for large ranges

## Units and Display

- **Latency**: microseconds
- **Throughput**: reads/writes per second (rps/wps)
- **Connections**: count (short)
- **Legend Format**: `$dc - $host_id` or `$groupBy` for aggregated views