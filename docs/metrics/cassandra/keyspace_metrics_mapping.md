---
title: "AxonOps Keyspace Dashboard Metrics Mapping"
description: "Cassandra keyspace dashboard metrics mapping. Per-keyspace statistics."
meta:
  - name: keywords
    content: "keyspace metrics, per-keyspace stats, Cassandra"
---

# AxonOps Keyspace Dashboard Metrics Mapping

This document maps the metrics used in the AxonOps Keyspace dashboard.

## Dashboard Overview

The Keyspace dashboard provides keyspace-level performance metrics including latency, throughput, and data distribution. It helps monitor performance characteristics across different keyspaces and identify which keyspaces are consuming the most resources or experiencing performance issues.

## Metrics Mapping

### Keyspace Performance Metrics

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `cas_Keyspace_ReadLatency` | Read operation latency | `keyspace`, `function` (percentiles/Count), `dc`, `rack`, `host_id` |
| `cas_Keyspace_RangeLatency` | Range query latency | `keyspace`, `function` (percentiles/Count), `dc`, `rack`, `host_id` |
| `cas_Keyspace_WriteLatency` | Write operation latency | `keyspace`, `function` (percentiles/Count), `dc`, `rack`, `host_id` |

### Data Size Metrics

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `cas_Table_LiveDiskSpaceUsed` | Live data size per table | `keyspace`, `scope` (table), `function=Count`, `dc` |

## Query Examples

### Keyspace Data Size Distribution (Pie Chart)
```promql
sum by (keyspace) (cas_Table_LiveDiskSpaceUsed{function='Count',dc=~'$dc'})
```

### Read Latency by Keyspace
```promql
cas_Keyspace_ReadLatency{function='$percentile',function!='Min|Max',dc=~'$dc',rack=~'$rack',host_id=~'$host_id',keyspace=~'$keyspace'}
```

### Range Read Latency
```promql
cas_Keyspace_RangeLatency{keyspace=~'$keyspace',function='$percentile',function!='Min|Max',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}
```

### Write Latency
```promql
cas_Keyspace_WriteLatency{keyspace=~'$keyspace',function='$percentile',function!='Max|Min',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}
```

### Read Throughput (ops/sec)
```promql
cas_Keyspace_ReadLatency{axonfunction='rate',keyspace=~'$keyspace',function='Count',function!='Min|Max',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}
```

### Range Read Throughput
```promql
cas_Keyspace_RangeLatency{axonfunction='rate',keyspace=~'$keyspace',function='Count',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}
```

### Write Throughput
```promql
cas_Keyspace_WriteLatency{axonfunction='rate',keyspace=~'$keyspace',function='Count',function!='Max|Min',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}
```

## Panel Organization

### Keyspaces Overview Section
- **Keyspace Data Size % Distribution** - Pie chart showing relative data size per keyspace

### Latency Statistics Section
- **Read Latency $percentile** - Line chart showing read latency at selected percentile

- **Range Read Request Latency $percentile** - Line chart for range query latency

- **Write Latency $percentile** - Line chart showing write latency

### Throughput Statistics Section
- **Reads/sec** - Line chart showing read operations per second

- **Range Read Requests/sec** - Line chart for range queries per second

- **Writes/sec** - Line chart showing write operations per second

## Filters

- **data center** (`dc`) - Filter by data center

- **rack** - Filter by rack

- **node** (`host_id`) - Filter by specific node

- **groupBy** - Dynamic grouping (dc, rack, host_id)

- **percentile** - Select latency percentile (50th, 75th, 95th, 98th, 99th, 999th)

- **keyspace** - Filter by specific keyspace(s)

- **table** (`scope`) - Filter by specific table(s)

## Metric Details

### Latency Metrics
- Measured in microseconds
- Available percentiles: 50th, 75th, 95th, 98th, 99th, 999th
- `Min` and `Max` values are excluded from queries
- Shows latency at the keyspace aggregation level

### Throughput Metrics
- Uses `axonfunction='rate'` to calculate per-second rates
- Based on the Count function of latency metrics
- Units: 
  - Reads: rps (reads per second)
  - Writes: wps (writes per second)

### Data Size Distribution
- Aggregates `LiveDiskSpaceUsed` across all tables in each keyspace
- Shows relative size as percentage in pie chart
- Helps identify keyspaces consuming most storage

## Legend Format

- Latency/Throughput panels: `$host_id - $keyspace`
- Shows both node and keyspace for easy correlation

## Performance Insights

**Keyspace Comparison**:

   - Compare latencies across keyspaces
   - Identify keyspaces with performance issues
   - Monitor throughput distribution

**Data Distribution**:

   - Pie chart shows storage distribution
   - Helps with capacity planning
   - Identifies data hotspots

**Operation Types**:

   - Separate metrics for reads, writes, and range queries
   - Range queries typically have higher latency
   - Monitor all three for complete picture

## Best Practices

**Monitor Latency Percentiles**:

   - 50th percentile: median performance
   - 95th/99th percentile: tail latencies
   - Large differences indicate inconsistent performance

**Track Throughput Patterns**:

   - Correlate with application usage
   - Identify peak usage times
   - Plan capacity accordingly

**Data Size Monitoring**:

   - Regular growth indicates active keyspace
   - Sudden changes may indicate issues
   - Use for storage capacity planning

## Notes

- Keyspace metrics aggregate all tables within the keyspace
- Metrics are collected at the coordinator level
- Range queries include operations like `SELECT` with `ALLOW FILTERING` or token ranges