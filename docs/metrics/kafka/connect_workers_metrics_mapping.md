---
description: "Kafka Connect workers dashboard metrics mapping. Worker node statistics."
meta:
  - name: keywords
    content: "Connect workers metrics, worker stats, Kafka Connect"
---

# AxonOps Kafka Connect Workers Dashboard Metrics Mapping

## Overview

The Kafka Connect Workers Dashboard provides comprehensive monitoring of individual Connect workers, tracking connector and task lifecycle, startup/shutdown events, and rebalancing activities. This dashboard helps monitor worker health and identify issues with connector deployment and task management.

## Metrics Mapping

| Dashboard Metric | Description | Attributes |
|-----------------|-----------|-------------|
| **Worker Overview Metrics** |
| `con_connect_worker_metrics_` (function='task_count') | Total number of tasks on worker | - |
| `con_connect_worker_metrics_` (function='connector_count') | Total number of connectors on worker | - |
| **Connector Lifecycle Metrics** |
| `con_connect_worker_metrics_` (function='connector_failed_task_count') | Failed tasks per connector | connector={connector} |
| `con_connect_worker_metrics_` (function='connector_startup_attempts_total') | Total connector startup attempts | - |
| `con_connect_worker_metrics_` (function='connector_startup_failure_total') | Failed connector startup attempts | - |
| `con_connect_worker_metrics_` (function='connector_startup_success_total') | Successful connector startup attempts | - |
| `con_connect_worker_metrics_` (function='connector_total_task_count') | Total tasks per connector | connector={connector} |
| **Task State Metrics** |
| `con_connect_worker_metrics_` (function='connector_paused_task_count') | Paused tasks per connector | connector={connector} |
| `con_connect_worker_metrics_` (function='connector_destroyed_task_count') | Destroyed tasks per connector | connector={connector} |
| `con_connect_worker_metrics_` (function='connector_running_task_count') | Running tasks per connector | connector={connector} |
| **Task Lifecycle Metrics** |
| `con_connect_worker_metrics_` (function='task_startup_attempts_total') | Total task startup attempts | - |
| `con_connect_worker_metrics_` (function='task_startup_failure_total') | Failed task startup attempts | - |
| `con_connect_worker_metrics_` (function='task_startup_success_total') | Successful task startup attempts | - |
| **Rebalance Metrics** |
| `con_connect_worker_rebalance_metrics_` (function='rebalance_avg_time_ms') | Average rebalance time | - |
| `con_connect_worker_rebalance_metrics_` (function='completed_rebalances_total') | Total completed rebalances | - |

## Query Examples

### Worker Overview
```promql
// Total task count
con_connect_worker_metrics_{function="task_count",type='kafka', node_type='connect'}

// Total connector count
con_connect_worker_metrics_{function="connector_count",type='kafka', node_type='connect'}
```

### Connector Lifecycle
```promql
// Connector count by host
sum(con_connect_worker_metrics_{function="connector_count",type='kafka', node_type='connect'}) by (host_id)

// Failed tasks by connector
con_connect_worker_metrics_{function="connector_failed_task_count",type='kafka', node_type='connect'}

// Connector startup attempts (total, failed, successful)
con_connect_worker_metrics_{function='connector_startup_attempts_total',type='kafka', node_type='connect'}
con_connect_worker_metrics_{function='connector_startup_failure_total',type='kafka', node_type='connect'}
con_connect_worker_metrics_{function='connector_startup_success_total',type='kafka', node_type='connect'}
```

### Task States
```promql
// Running tasks by connector
sum(con_connect_worker_metrics_{function="connector_running_task_count",type='kafka', node_type='connect', connector='$connector'}) by (connector)

// Paused tasks by connector
sum(con_connect_worker_metrics_{function="connector_paused_task_count",type='kafka', node_type='connect', connector='$connector'}) by (connector)

// Failed tasks by connector
sum(con_connect_worker_metrics_{function="connector_failed_task_count",type='kafka', node_type='connect', connector='$connector'}) by (connector)

// Destroyed tasks by connector
sum(con_connect_worker_metrics_{function="connector_destroyed_task_count",type='kafka', node_type='connect', connector='$connector'}) by (connector)
```

### Task Lifecycle
```promql
// Task startup attempts (total, failed, successful)
con_connect_worker_metrics_{function='task_startup_attempts_total',type='kafka', node_type='connect'}
con_connect_worker_metrics_{function='task_startup_failure_total',type='kafka', node_type='connect'}
con_connect_worker_metrics_{function='task_startup_success_total',type='kafka', node_type='connect'}

// Total tasks per connector
con_connect_worker_metrics_{function="connector_total_task_count",type='kafka', node_type='connect', connector='$connector'}
```

### Rebalancing
```promql
// Average rebalance time
con_connect_worker_rebalance_metrics_{function="rebalance_avg_time_ms",type='kafka', node_type='connect'}

// Completed rebalances
con_connect_worker_rebalance_metrics_{function="completed_rebalances_total",type='kafka', node_type='connect'}
```

## Panel Organization

**Overview Section**

   - Empty row for spacing/organization

**Workers**

   - Connector Count (counter)
   - Task Count (counter)

**Worker Metrics**

   - Connector Count (time series)
   - Connector Startup
   - Connector Failed
   - Connector Task Count
   - Connector Task Startup by Host
   - Connector Paused Tasks
   - Connector Destroyed

**Worker Tasks**

   - Connector Running Tasks
   - Connector Failed Tasks
   - Connector Destroyed Tasks

**Rebalance Metrics**

   - Connector Rebalances (duplicate panels)
   - Connectors Avg Rebalance Time

## Filters

- **host_id**: Filter by specific Connect worker node

- **connector**: Filter by specific connector name

## Best Practices

**Worker Health Monitoring**

   - Monitor task and connector counts per worker
   - Ensure balanced distribution across workers
   - Track failed task counts for issues

**Connector Lifecycle**

   - Monitor startup success vs failure rates
   - High failure rates indicate configuration issues
   - Track connector count changes over time

**Task State Management**

   - Running tasks should match expected count
   - Paused tasks may indicate manual intervention
   - Failed tasks require investigation
   - Destroyed tasks indicate connector removal

**Startup Monitoring**

   - Compare startup attempts vs successes
   - High failure rates suggest configuration problems
   - Monitor both connector and task startups

**Rebalancing Analysis**

   - Frequent rebalances impact availability
   - High rebalance times affect task availability
   - Monitor after adding/removing workers

**Troubleshooting**

   - Failed connectors: Check logs and configuration
   - Paused tasks: Verify intentional vs error state
   - Startup failures: Review connector configs
   - Destroyed tasks: Confirm planned removals

**Capacity Planning**

   - Monitor task distribution across workers
   - Plan worker scaling based on task counts
   - Balance connectors for even resource usage