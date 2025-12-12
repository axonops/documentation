---
description: "Kafka Connect overview dashboard metrics mapping. Connector status and throughput."
meta:
  - name: keywords
    content: "Kafka Connect metrics, connector status, throughput"
---

# AxonOps Kafka Connect Overview Dashboard Metrics Mapping

## Overview

The Kafka Connect Overview Dashboard provides comprehensive monitoring of Kafka Connect clusters, including worker health, connector status, task distribution, rebalancing activity, and network metrics. This dashboard helps monitor the overall health and performance of your Kafka Connect deployment.

## Metrics Mapping

| Dashboard Metric | Description | Attributes |
|-----------------|-----------|-------------|
| **Worker Metrics** |
| `con_connect_worker_metrics_` (function='connectorfailedtaskcount') | Number of failed tasks | connector={connector} |
| `con_connect_worker_metrics_` (function='task_count') | Total number of tasks | - |
| `con_connect_worker_rebalance_metrics_` (function='rebalancing') | Rebalancing status (0 or 1) | - |
| `con_connect_worker_rebalance_metrics_` (function='rebalance_avg_time_ms') | Average rebalance time | - |
| **Coordinator Metrics** |
| `con_connect_coordinator_metrics_` (function='assigned_connectors') | Number of assigned connectors | - |
| `con_connect_coordinator_metrics_` (function='assigned_tasks') | Number of assigned tasks | - |
| `con_connect_coordinator_metrics_` (function='failed_rebalance_total') | Total failed rebalances | - |
| `con_connect_coordinator_metrics_` (function='last_heartbeat_seconds_ago') | Seconds since last heartbeat | - |
| `con_connect_coordinator_metrics_` (function='join_total') | Total join operations | - |
| `con_connect_coordinator_metrics_` (function='sync_rate') | Group sync rate | - |
| `con_connect_coordinator_metrics_` (function='rebalance_total') | Total rebalances | - |
| **Connection Metrics** |
| `con_connect_metrics_` (function='connection_count') | Active connection count | - |
| `con_connect_metrics_` (function='connection_close_total') | Total connections closed | - |
| `con_connect_metrics_` (function='connection_creation_total') | Total connections created | - |
| `con_connect_metrics_` (function='failed_authentication_total') | Total authentication failures | - |
| **Network Metrics** |
| `con_connect_metrics_` (function='request_total') | Total requests | - |
| `con_connect_metrics_` (function='response_total') | Total responses | - |
| `con_connect_metrics_` (function='incoming_byte_rate') | Incoming bytes per second | - |
| `con_connect_metrics_` (function='outgoing_byte_rate') | Outgoing bytes per second | - |
| `con_connect_metrics_` (function='network_io_rate') | Network I/O rate | - |
| `con_connect_metrics_` (function='iotime_total') | Total I/O time | - |
| `con_connect_metrics_` (function='io_waittime_total') | Total I/O wait time | - |

## Query Examples

### Worker Health
```promql
// Failed task count
con_connect_worker_metrics_{function="connectorfailedtaskcount",type='kafka', node_type='connect'}

// Total task count
sum(con_connect_worker_metrics_{function='task_count',type='kafka', node_type='connect'})

// Rebalancing status
con_connect_worker_rebalance_metrics_{function="rebalancing",type='kafka', node_type='connect'}
```

### Coordinator Metrics
```promql
// Assigned connectors per worker
con_connect_coordinator_metrics_{function="assigned_connectors",type='kafka', node_type='connect',client_id=~'$client_id'}

// Assigned tasks per worker
con_connect_coordinator_metrics_{function="assigned_tasks",type='kafka', node_type='connect',client_id=~'$client_id'}

// Failed rebalances
con_connect_coordinator_metrics_{function="failed_rebalance_total",type='kafka', node_type='connect',client_id=~'$client_id'}

// Heartbeat monitoring
con_connect_coordinator_metrics_{function="last_heartbeat_seconds_ago",type='kafka', node_type='connect',client_id=~'$client_id'}
```

### Connection Management
```promql
// Active connections
con_connect_metrics_{function="connection_count",type='kafka', node_type='connect',client_id=~'$client_id'}

// Connection creation/close rates
con_connect_metrics_{function="connection_creation_total",type='kafka', node_type='connect',client_id=~'$client_id'}
con_connect_metrics_{function="connection_close_total",type='kafka', node_type='connect',client_id=~'$client_id'}

// Authentication failures
con_connect_metrics_{function="failed_authentication_total",type='kafka', node_type='connect'}
```

### Network Performance
```promql
// Request/Response tracking
con_connect_metrics_{function="request_total",type='kafka', node_type='connect'}
con_connect_metrics_{function="response_total",type='kafka', node_type='connect'}

// Byte rates
con_connect_metrics_{function="incoming_byte_rate",type='kafka', node_type='connect'}
con_connect_metrics_{function="outgoing_byte_rate",type='kafka', node_type='connect'}

// I/O performance
con_connect_metrics_{axonfunction='rate',function="iotime_total",type='kafka', node_type='connect'}
con_connect_metrics_{axonfunction='rate',function="io_waittime_total",type='kafka', node_type='connect'} / 1000
```

### Rebalancing Metrics
```promql
// Average rebalance time
con_connect_worker_rebalance_metrics_{function="rebalance_avg_time_ms",type='kafka', node_type='connect'}

// Total rebalances
con_connect_coordinator_metrics_{function="rebalance_total",type='kafka', node_type='connect',client_id=~'$client_id'}

// Join operations
con_connect_coordinator_metrics_{function="join_total",type='kafka', node_type='connect',client_id=~'$client_id'}

// Sync rate
con_connect_coordinator_metrics_{function="sync_rate",type='kafka', node_type='connect',client_id=~'$client_id'}
```

## Panel Organization

**Overview Section**

   - Empty row for spacing/organization

**Overview**

   - Connector Workers (counter)
   - Connectors Rebalancing (counter)
   - Connector Tasks Failed (counter)

**Coordinator Metrics**

   - Assigned Connectors
   - Assigned Tasks
   - Failed Rebalances
   - Last Heartbeat (Seconds ago)
   - Rebalances
   - Joins
   - Sync Rate

**Connect Metrics**

   - Connections
   - Connection Close
   - Connection Creations
   - Rebalance average time
   - Requests vs Response
   - Failed Authentication
   - Incoming Byte Rate
   - Outgoing Byte Rate
   - Network IO Rate
   - IO Time
   - IO Wait Time

## Filters

- **host_id**: Filter by specific Connect worker node

- **client_id**: Filter by specific client ID

## Best Practices

**Worker Health Monitoring**

   - Monitor failed task count - should be 0
   - Track total tasks for capacity planning
   - Watch for frequent rebalancing

**Task Distribution**

   - Ensure even distribution of connectors/tasks
   - Monitor for workers with no assignments
   - Check for imbalanced workloads

**Rebalancing Analysis**

   - Frequent rebalances indicate instability
   - High rebalance time impacts availability
   - Monitor failed rebalances for issues

**Heartbeat Monitoring**

   - High heartbeat lag indicates worker issues
   - Set alerts for heartbeat timeouts
   - Correlate with worker failures

**Connection Management**

   - Monitor connection churn rate
   - High authentication failures indicate security issues
   - Track connection count for capacity

**Network Performance**

   - Monitor byte rates for throughput
   - Check request/response balance
   - High I/O wait time indicates bottlenecks

**Troubleshooting**

   - Failed tasks: Check connector logs
   - Rebalancing issues: Review worker health
   - Authentication failures: Verify credentials
   - Network issues: Check Kafka broker connectivity