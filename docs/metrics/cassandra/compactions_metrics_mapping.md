---
title: "AxonOps Compactions Dashboard Metrics Mapping"
description: "Cassandra compaction dashboard metrics mapping. Compaction progress and throughput."
meta:
  - name: keywords
    content: "compaction metrics, compaction progress, throughput, Cassandra"
search:
  boost: 8
---

# AxonOps Compactions Dashboard Metrics Mapping

This document maps the metrics used in the AxonOps Compactions dashboard.

## Dashboard Overview

The Compactions dashboard monitors Cassandra's compaction operations, which merge SSTables to improve read performance and reclaim disk space. It tracks compaction throughput, pending tasks, and bytes processed to help identify compaction bottlenecks.

## Metrics Mapping

### Compaction Metrics

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `cas_Compaction_TotalCompactionsCompleted` | Total number of completed compactions | `function=Count`, `dc`, `rack`, `host_id` |
| `cas_Compaction_CompletedTasks` | Completed compaction tasks in thread pool | `dc`, `rack`, `host_id` |
| `cas_Compaction_BytesCompacted` | Total bytes compacted | `dc`, `rack`, `host_id` |
| `cas_Compaction_PendingTasks` | Pending compaction tasks in thread pool | `dc`, `rack`, `host_id` |
| `cas_Keyspace_PendingCompactions` | Pending compactions per keyspace | `keyspace`, `dc`, `rack`, `host_id` |

## Query Examples

### Total Compactions Completed per Second
```promql
cas_Compaction_TotalCompactionsCompleted{axonfunction='rate',function='Count',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}
```

### Completed Thread Pool Compaction Tasks per Second
```promql
cas_Compaction_CompletedTasks{axonfunction='rate',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}
```

### Bytes Compacted per Second
```promql
cas_Compaction_BytesCompacted{axonfunction='rate',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}
```

### Pending Thread Pool Compaction Tasks
```promql
cas_Compaction_PendingTasks{dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}
```

### Keyspace Pending Compactions per Second
```promql
sum(cas_Keyspace_PendingCompactions{axonfunction='rate',keyspace='$keyspace',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by ($groupBy)
```

## Panel Organization

### Compactions Per Node Section
- **Total Compactions Completed per sec** - Line chart showing overall compaction completion rate

- **Completed TP Compactions Tasks per sec** - Line chart showing thread pool task completion rate

- **Bytes Compacted per sec** - Line chart showing data throughput of compactions

- **Pending TP Compaction Tasks** - Line chart showing backlog of compaction tasks

### Pending Compactions Per Keyspace Section
- **$keyspace TP Keyspace Pending Compactions per sec** - Line chart showing pending compactions rate for selected keyspace

## Filters

- **data center** (`dc`) - Filter by data center

- **rack** - Filter by rack

- **node** (`host_id`) - Filter by specific node

- **groupBy** - Dynamic grouping (dc, rack, host_id, keyspace)

- **keyspace** - Filter by specific keyspace

## Metric Details

### Compaction Task Metrics
- **TotalCompactionsCompleted**: Cumulative counter of all compactions finished

- **CompletedTasks**: Thread pool level metric for task completion

- Both metrics use `axonfunction='rate'` to show per-second rates

### Throughput Metrics
- **BytesCompacted**: Shows data processing rate

- Helps identify if compaction is keeping up with write load
- Unit displayed as bytes/second

### Pending Tasks
- **PendingTasks**: Thread pool queue size

- **PendingCompactions**: Keyspace-specific pending count

- High values indicate compaction falling behind

## Important Considerations

**Compaction Performance**:

   - High pending tasks indicate compaction bottleneck
   - May need to tune concurrent_compactors
   - Consider compaction throughput limits

**Resource Impact**:

   - Compactions consume CPU, disk I/O, and memory
   - Monitor bytes compacted rate vs write rate
   - Balance between compaction speed and query performance

**Keyspace Specifics**:

   - Different keyspaces may have different compaction strategies
   - Monitor pending compactions per keyspace
   - Some keyspaces may require different tuning

**Thread Pool Monitoring**:

   - CompactionExecutor thread pool handles all compactions
   - Pool saturation affects all keyspaces
   - May need to adjust thread pool size

## Units and Display

- **Rates**: Operations per second (short unit)

- **Bytes**: Displayed with binary units (bytes/s)

- **Counts**: Simple numeric values (short unit)

- **Legend Format**: `$dc - $host_id` for most panels

## Compaction Strategy Impact

Different compaction strategies have different characteristics:

  - **STCS**: Fewer, larger compactions

  - **LCS**: Many smaller, predictable compactions
  
  - **TWCS**: Time-based, minimal overlap
  
  - Monitor patterns based on your strategy