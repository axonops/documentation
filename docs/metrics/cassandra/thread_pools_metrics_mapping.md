# AxonOps Thread Pools Dashboard Metrics Mapping

This document maps the metrics used in the AxonOps Thread Pools dashboard.

## Dashboard Overview

The Thread Pools dashboard monitors Cassandra's internal thread pools that handle various operations like reads, writes, compactions, and repairs. Understanding thread pool behavior is crucial for identifying performance bottlenecks and tuning Cassandra for optimal performance.

## Metrics Mapping

### Thread Pool Metrics

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `cas_ThreadPools_internal` | Internal thread pool metrics | `scope` (pool name), `key` (metric type), `dc`, `rack`, `host_id` |

### Metric Keys (Types)

| Key | Description |
|-----|-------------|
| `ActiveTasks` | Number of tasks currently being executed |
| `PendingTasks` | Number of tasks waiting in the queue |
| `CompletedTasks` | Total number of completed tasks (cumulative) |
| `TotalBlockedTasks` | Total number of tasks that were blocked (cumulative) |
| `CurrentlyBlockedTasks` | Number of tasks currently blocked |

## Common Thread Pool Scopes

| Scope | Purpose |
|-------|---------|
| `MutationStage` | Handles write operations |
| `ReadStage` | Handles read operations |
| `RequestResponseStage` | Handles request/response messaging |
| `CompactionExecutor` | Handles compaction tasks |
| `ValidationExecutor` | Handles validation tasks (repairs) |
| `GossipStage` | Handles gossip protocol |
| `AntiEntropyStage` | Handles anti-entropy repairs |
| `MigrationStage` | Handles schema migrations |
| `MemtableFlushWriter` | Handles memtable flush operations |
| `MemtablePostFlush` | Handles post-flush operations |
| `HintsDispatcher` | Handles hint delivery |

## Query Examples

### Active Tasks
```promql
sum(cas_ThreadPools_internal{scope=~'$scope',key='ActiveTasks',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by ($groupBy)
```

### Pending Tasks
```promql
sum(cas_ThreadPools_internal{scope=~'$scope',key='PendingTasks',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by ($groupBy)
```

### Completed Tasks Rate
```promql
sum(cas_ThreadPools_internal{axonfunction='rate',scope=~'$scope',key='CompletedTasks',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by ($groupBy)
```

### Total Blocked Tasks Rate
```promql
sum(cas_ThreadPools_internal{axonfunction='rate',scope=~'$scope',key='TotalBlockedTasks',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by ($groupBy)
```

### Currently Blocked Tasks
```promql
sum(cas_ThreadPools_internal{scope=~'$scope',key='CurrentlyBlockedTasks',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by ($groupBy)
```

## Panel Organization

For each selected thread pool ($scope), the dashboard shows:

1. **Active Tasks** - Line chart showing currently executing tasks
2. **Pending Tasks** - Line chart showing queued tasks waiting for execution
3. **Completed Tasks Rate by $groupBy** - Line chart showing task completion rate
4. **Total Blocked Tasks Rate** - Line chart showing rate of tasks being blocked
5. **Currently Blocked Tasks Rate** - Line chart showing currently blocked tasks

## Filters

- **data center** (`dc`) - Filter by data center
- **rack** - Filter by rack
- **node** (`host_id`) - Filter by specific node
- **Pool (scope)** - Select specific thread pool(s) to monitor
- **groupBy** - Dynamic grouping (scope, dc, rack, host_id)

## Important Thread Pools to Monitor

### MutationStage
- Handles all write operations
- High pending tasks indicate write bottleneck
- Blocked tasks suggest memtable pressure

### ReadStage
- Handles all read operations
- Pending tasks indicate read latency issues
- May need to tune concurrent_reads

### CompactionExecutor
- Manages compaction operations
- High pending tasks mean compactions falling behind
- Affects disk space and read performance

### MemtableFlushWriter
- Flushes memtables to disk
- Blocked tasks indicate disk I/O issues
- Critical for write performance

## Performance Indicators

### Healthy Patterns
- Low or zero pending tasks
- No currently blocked tasks
- Steady completed task rate
- Active tasks within thread pool size

### Warning Signs
- Consistently growing pending tasks
- Frequent blocked tasks
- Active tasks at maximum pool size
- Sudden drops in completion rate

## Tuning Considerations

1. **Thread Pool Sizing**:
   - Configured in cassandra.yaml
   - Balance between concurrency and resource usage
   - Consider CPU cores and workload type

2. **Common Adjustments**:
   - `concurrent_reads`: For read-heavy workloads
   - `concurrent_writes`: For write-heavy workloads
   - `concurrent_compactors`: For compaction throughput

3. **Monitoring Strategy**:
   - Watch for sustained pending tasks
   - Monitor blocked tasks for resource contention
   - Compare completion rates across nodes

## Grouping and Aggregation

The `groupBy` variable allows flexible analysis:
- By `scope`: Compare different thread pools
- By `dc`: Data center level patterns
- By `rack`: Rack level distribution
- By `host_id`: Individual node behavior

## Units and Display

- **Task Counts**: Displayed as short numbers
- **Rates**: Tasks per second
- **Legend**: Shows the groupBy dimension
- **Time Series**: Real-time and historical trends