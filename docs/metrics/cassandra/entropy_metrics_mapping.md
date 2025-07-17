# AxonOps Entropy Dashboard Metrics Mapping

This document maps the metrics used in the AxonOps Entropy dashboard.

## Dashboard Overview

The Entropy dashboard (also known as Anti-Entropy) monitors Cassandra's data consistency mechanisms including hinted handoff, read repairs, and repair operations. These features ensure eventual consistency across the cluster by detecting and fixing data inconsistencies.

## Metrics Mapping

### Hints Metrics

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `cas_Storage_TotalHints` | Total number of hints created | `axonfunction` (rate), `dc`, `rack`, `host_id` |
| `cas_Storage_TotalHintsInProgress` | Currently active hints being delivered | `dc`, `rack`, `host_id` |

### Read Repair Metrics

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `cas_ReadRepair_Attempted` | Read repair attempts | `function` (Count), `axonfunction` (rate), `dc`, `rack`, `host_id` |
| `cas_ReadRepair_RepairedBackground` | Background read repairs completed | `function` (Count), `axonfunction` (rate), `dc`, `rack`, `host_id` |
| `cas_ReadRepair_RepairedBlocking` | Blocking read repairs completed | `function` (Count), `axonfunction` (rate), `dc`, `rack`, `host_id` |

### Coordinator Error Metrics

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `cas_ClientRequest_Timeouts` | Request timeouts at coordinator | `scope` (Read/Write), `function` (Count), `axonfunction` (rate), `dc`, `rack`, `host_id` |
| `cas_ClientRequest_Unavailables` | Unavailable exceptions at coordinator | `scope` (Read/Write), `function` (Count), `axonfunction` (rate), `dc`, `rack`, `host_id` |

### Thread Pool Metrics

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `cas_ThreadPools_request` | Request thread pool statistics | `scope` (pool name), `key` (CompletedTasks), `axonfunction` (rate), `dc`, `rack`, `host_id` |
| `cas_ThreadPools_internal` | Internal thread pool statistics | `scope` (pool name), `key` (CompletedTasks), `axonfunction` (rate), `dc`, `rack`, `host_id` |

## Query Examples

### Hints Section
```promql
# Total Hints Created Rate
cas_Storage_TotalHints{axonfunction='rate',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}

# Hints Currently In Progress
cas_Storage_TotalHintsInProgress{dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}
```

### Read Repairs Section
```promql
# Attempted Per Second
sum(cas_ReadRepair_Attempted{axonfunction='rate',function='Count',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by ($groupBy)

# Repaired Background
sum(cas_ReadRepair_RepairedBackground{axonfunction='rate',function='Count',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by ($groupBy)

# Repaired Blocking
sum(cas_ReadRepair_RepairedBlocking{axonfunction='rate',function='Count',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by ($groupBy)
```

### Coordinator Request Errors Section
```promql
# Read Timeouts
sum(cas_ClientRequest_Timeouts{axonfunction='rate',function='Count',scope='Read',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by ($groupBy)

# Read Unavailables
sum(cas_ClientRequest_Unavailables{axonfunction='rate',function='Count',scope='Read',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by ($groupBy)

# Write Timeouts
sum(cas_ClientRequest_Timeouts{axonfunction='rate',scope='Write',function='Count',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by ($groupBy)

# Write Unavailables
sum(cas_ClientRequest_Unavailables{axonfunction='rate',scope='Write',function='Count',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by ($groupBy)
```

### Thread Pools Section
```promql
# Request Thread Pool Distribution (Pie Chart)
sum(cas_ThreadPools_request{axonfunction='rate',key='CompletedTasks',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by (scope)

# Internal Thread Pool Distribution (Pie Chart)
sum(cas_ThreadPools_internal{axonfunction='rate',key='CompletedTasks',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by (scope)

# Anti-Entropy Stage Tasks
sum(cas_ThreadPools_internal{axonfunction='rate',scope='AntiEntropyStage',key='CompletedTasks',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by ($groupBy)

# Read Repair Stage Tasks
sum(cas_ThreadPools_internal{axonfunction='rate',scope='ReadRepairStage',key='CompletedTasks',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by ($groupBy)

# Hints Dispatcher Tasks
sum(cas_ThreadPools_internal{axonfunction='rate',scope='HintsDispatcher',key='CompletedTasks',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by ($groupBy)
```

## Panel Organization

### Hints Section
1. **Total Hints Created By Each Node** - Rate of hint creation
2. **Total Hints In Progress** - Active hint delivery count

### Read Repairs Section
1. **Attempted Per Second** - Read repair attempt rate
2. **Repaired Background** - Background repairs completed
3. **Repaired Blocked** - Blocking repairs completed

### Coordinator Requests Errors Section
1. **Read Timeouts Per Second** - Read operation timeout rate
2. **Read Unavailables Per Second** - Read unavailable exception rate
3. **Write Timeouts Per Second** - Write operation timeout rate
4. **Write Unavailables Per Second** - Write unavailable exception rate

### Thread Pools Section
1. **ThreadPools Request** - Request thread pool activity distribution
2. **ThreadPools Internal** - Internal thread pool activity distribution
3. **Completed Tasks per sec - Anti Entropy Stage** - Repair coordination tasks
4. **Completed Tasks per sec - Read Repair Stage** - Read repair execution tasks
5. **Completed Tasks per sec - Hinted Handoff** - Hint delivery tasks

### Events Section
1. **Starting Repair Events** - Repair start event frequency
2. **Streaming Events** - Data streaming event frequency

## Filters

- **data center** (`dc`) - Filter by data center
- **rack** - Filter by rack
- **node** (`host_id`) - Filter by specific node
- **groupBy** - Dynamic grouping (dc, rack, host_id, keyspace)

## Understanding Anti-Entropy Mechanisms

### Hinted Handoff
- **Purpose**: Temporary storage of writes when replicas are unavailable
- **TotalHints**: Accumulating counter of all hints created
- **HintsInProgress**: Current active hint deliveries
- **Impact**: High hint rates indicate replica availability issues

### Read Repair
- **Attempted**: All read repair attempts
- **RepairedBackground**: Asynchronous repairs (non-blocking)
- **RepairedBlocking**: Synchronous repairs (blocks read response)
- **Types**:
  - Background: Happens after read completes
  - Blocking: Happens before read response

### Coordinator Errors
- **Timeouts**: Request exceeded configured timeout
- **Unavailables**: Not enough replicas available
- **Causes**:
  - Node overload
  - Network issues
  - Insufficient replicas

### Thread Pools
- **AntiEntropyStage**: Handles repair coordination
- **ReadRepairStage**: Executes read repairs
- **HintsDispatcher**: Delivers hints to recovered nodes

## Best Practices

### Hints Monitoring
1. **Zero Hints Ideal**: Indicates all replicas available
2. **Growing Hints**: Sign of persistent replica issues
3. **High In-Progress**: May indicate slow hint delivery
4. **Actions**:
   - Check node health
   - Review network connectivity
   - Monitor hint storage capacity

### Read Repair Monitoring
1. **Background vs Blocking**:
   - High blocking repairs impact read latency
   - Background repairs are preferred
2. **High Attempt Rate**:
   - Indicates data inconsistency
   - May need full repair
3. **Success Rate**:
   - Compare attempted vs repaired
   - Low success indicates issues

### Error Monitoring
1. **Zero Tolerance**:
   - Any timeouts/unavailables are concerning
   - Investigate root cause immediately
2. **Read vs Write**:
   - Different implications
   - Write unavailables risk data loss
3. **Correlation**:
   - Check with dropped messages
   - Monitor system resources

### Thread Pool Health
1. **Balanced Distribution**:
   - Even work across pools
   - No single pool dominating
2. **Anti-Entropy Activity**:
   - Spikes during repairs
   - Should be low normally
3. **Hints Dispatcher**:
   - Activity indicates recovery
   - Should complete eventually

## Troubleshooting Guide

### High Hint Rate
1. Check node status
2. Review network connectivity
3. Monitor disk space for hints
4. Consider max_hint_window_in_ms setting

### High Read Repair Rate
1. Run nodetool repair
2. Check consistency levels
3. Review replication factor
4. Monitor for flapping nodes

### Timeout/Unavailable Errors
1. Check system resources
2. Review timeout settings
3. Monitor GC activity
4. Check request patterns

### Thread Pool Congestion
1. Monitor pending tasks
2. Check blocked tasks
3. Review pool sizing
4. Consider capacity expansion

## Units and Display

- **Rates**: operations per second (short)
- **Counts**: absolute numbers (short)
- **Legend Format**: 
  - Aggregated: `$groupBy`
  - Node-specific: `$dc - $host_id`
  - Thread pools: `$scope`

## Notes

- Events use message filtering for repair and streaming activities
- Thread pool metrics use `key='CompletedTasks'` for rate calculations
- The dashboard name "Entropy" refers to anti-entropy (consistency) mechanisms
- All rate metrics use `axonfunction='rate'` for per-second calculations