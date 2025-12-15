---
title: "Cassandra Alerting Configuration"
description: "Cassandra alerting configuration. Set up alerts for critical metrics."
meta:
  - name: keywords
    content: "Cassandra alerting, monitoring alerts, metric thresholds"
---

# Cassandra Alerting Configuration

Effective alerting enables proactive response to cluster issues before they impact application performance.

## Alert Categories

| Category | Priority | Response Time | Examples |
|----------|----------|---------------|----------|
| Critical | P1 | Immediate (< 5 min) | Node down, disk full, dropped messages |
| Warning | P2 | Soon (< 1 hour) | High latency, compaction backlog |
| Info | P3 | Next business day | Certificate expiring, minor threshold breach |

---

## Critical Alerts

### Node Down

A node becomes unreachable, reducing cluster capacity and fault tolerance.

| Parameter | Value |
|-----------|-------|
| Metric | Node status via gossip or agent heartbeat |
| Condition | Unreachable for > 1 minute |
| Severity | Critical |

**Response:**
1. Verify node status with `nodetool status` from another node
2. Check if process is running on the affected node
3. Review system logs for crash indicators
4. Check network connectivity

### High Heap Usage

Sustained high heap usage indicates memory pressure and increases GC pause risk.

| Parameter | Value |
|-----------|-------|
| Metric | `java.lang:type=Memory/HeapMemoryUsage` |
| Condition | > 85% for 5 minutes |
| Severity | Critical |

**Response:**
1. Check GC logs for long pauses
2. Review `nodetool tpstats` for blocked stages
3. Consider reducing concurrent operations
4. Evaluate heap size configuration

### Disk Full

Cassandra stops accepting writes when disk usage exceeds thresholds.

| Parameter | Value |
|-----------|-------|
| Metric | Filesystem usage on data directories |
| Condition | > 85% used |
| Severity | Critical |

**Response:**
1. Identify largest tables with `nodetool tablestats`
2. Run cleanup if data was recently deleted: `nodetool cleanup`
3. Check for compaction backlog
4. Add capacity or remove data

### Dropped Messages

Dropped messages indicate the cluster cannot process requests within timeout.

| Parameter | Value |
|-----------|-------|
| Metric | `org.apache.cassandra.metrics:type=DroppedMessage` |
| Condition | Any dropped messages |
| Severity | Critical |

**Response:**
1. Identify which message types are dropping via `nodetool tpstats`
2. Check for overloaded thread pools
3. Review client request patterns
4. Evaluate cluster capacity

---

## Warning Alerts

### High Read Latency

Elevated read latency impacts application response times.

| Parameter | Value |
|-----------|-------|
| Metric | `ClientRequest.Read.Latency.99thPercentile` |
| Condition | > 100ms for 10 minutes |
| Severity | Warning |

**Response:**
1. Check `nodetool proxyhistograms` for coordinator vs local latency
2. Review `nodetool tablestats` for problematic tables
3. Check pending compactions
4. Evaluate read patterns and data model

### High Write Latency

Elevated write latency may indicate commit log or memtable pressure.

| Parameter | Value |
|-----------|-------|
| Metric | `ClientRequest.Write.Latency.99thPercentile` |
| Condition | > 50ms for 10 minutes |
| Severity | Warning |

**Response:**
1. Check commit log directory disk I/O
2. Review memtable flush frequency
3. Verify commit log is on separate disk from data
4. Check for concurrent compaction activity

### Compaction Backlog

Pending compactions indicate write volume exceeds compaction throughput.

| Parameter | Value |
|-----------|-------|
| Metric | `org.apache.cassandra.metrics:type=Compaction,name=PendingTasks` |
| Condition | > 30 for 15 minutes |
| Severity | Warning |

**Response:**
1. Review compaction throughput settings
2. Check disk I/O utilization
3. Evaluate compaction strategy for workload
4. Consider increasing `concurrent_compactors`

### Heap Usage Warning

Early warning of approaching memory pressure.

| Parameter | Value |
|-----------|-------|
| Metric | `java.lang:type=Memory/HeapMemoryUsage` |
| Condition | > 70% for 10 minutes |
| Severity | Warning |

**Response:**
1. Monitor GC activity trends
2. Review recent workload changes
3. Check for large partition access patterns
4. Prepare for potential heap tuning

---

## Alert Thresholds Summary

| Metric | Warning | Critical | JMX Path |
|--------|---------|----------|----------|
| Heap Usage | > 70% | > 85% | `java.lang:type=Memory` |
| Disk Usage | > 60% | > 80% | OS-level metric |
| Read Latency p99 | > 50ms | > 200ms | `ClientRequest.Read.Latency` |
| Write Latency p99 | > 20ms | > 100ms | `ClientRequest.Write.Latency` |
| Pending Compactions | > 20 | > 50 | `Compaction.PendingTasks` |
| Dropped Messages | > 0 | > 10/s | `DroppedMessage.*.Dropped` |
| GC Pause | > 500ms | > 1s | `java.lang:type=GarbageCollector` |

---

## AxonOps Alert Configuration

### Creating Alerts

Alerts are configured in the AxonOps dashboard under **Settings > Alerts**.

1. Navigate to **Settings > Alerts > Create Alert**
2. Select the metric to monitor
3. Define threshold conditions
4. Set evaluation interval and duration
5. Configure notification channels

### Alert Rule Parameters

| Parameter | Description |
|-----------|-------------|
| Metric | The JMX metric or derived value to evaluate |
| Operator | Comparison operator (>, <, =, !=) |
| Threshold | Value that triggers the alert |
| Duration | Time the condition must persist |
| Severity | Critical, Warning, or Info |

### Example: High Latency Alert

```
Name: High Read Latency
Metric: cassandra.client_request.read.latency.p99
Condition: > 100
Duration: 10 minutes
Severity: Warning
```

### Notification Channels

AxonOps supports multiple notification integrations:

| Channel | Use Case |
|---------|----------|
| Email | General notifications |
| Slack | Team collaboration |
| PagerDuty | On-call escalation |
| Webhook | Custom integrations |
| OpsGenie | Incident management |

Configure channels under **Settings > Integrations**.

---

## Alert Routing

### Severity-Based Routing

| Severity | Notification |
|----------|--------------|
| Critical | PagerDuty + Slack |
| Warning | Slack only |
| Info | Email digest |

### Time-Based Routing

Configure different notification behavior for business hours vs off-hours:

- **Business hours**: Warning alerts to Slack
- **Off-hours**: Only critical alerts to PagerDuty

---

## Runbook Integration

Each alert should reference a runbook with:

1. **Description**: What the alert means
2. **Impact**: How this affects the cluster/application
3. **Diagnosis**: Steps to investigate
4. **Resolution**: Actions to resolve
5. **Escalation**: When and how to escalate

---

## Best Practices

### Threshold Tuning

- Establish baselines during normal operation
- Set warning thresholds at 2x baseline
- Set critical thresholds at 4x baseline or operational limits
- Review and adjust quarterly

### Reducing Alert Fatigue

- Require duration before alerting (avoid transient spikes)
- Group related alerts
- Use warning alerts for early indicators
- Reserve critical for immediate action required

### Alert Coverage

Minimum alert coverage for production clusters:

- [ ] Node availability
- [ ] Heap usage (warning and critical)
- [ ] Disk usage (warning and critical)
- [ ] Read/write latency
- [ ] Dropped messages
- [ ] Pending compactions
- [ ] GC pause duration

---

## Next Steps

- **[Key Metrics](../key-metrics/index.md)** - Metrics reference
- **[Logging](../logging/index.md)** - Log analysis and configuration
