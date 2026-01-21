---
title: "Cassandra Key Metrics Reference"
description: "Key Cassandra metrics to monitor. Essential metrics for cluster health."
meta:
  - name: keywords
    content: "Cassandra key metrics, essential metrics, monitoring priorities"
search:
  boost: 3
---

# Cassandra Key Metrics Reference

This guide covers the essential metrics to monitor for a healthy Cassandra cluster.

## Metrics Overview

### The Four Golden Signals

| Signal | Cassandra Metrics | Significance |
|--------|-------------------|----------------|
| **Latency** | Read/Write p99 | User experience |
| **Traffic** | Requests/second | Capacity planning |
| **Errors** | Timeouts, Unavailables | Service reliability |
| **Saturation** | CPU, Disk, Memory | Resource headroom |

### Metric Categories

| Category | Description |
|----------|-------------|
| **Client Request Metrics** | Read/Write latency, throughput, errors |
| **Thread Pool Metrics** | Active, Pending, Blocked, Completed |
| **Storage Metrics** | SSTable count, Disk usage, Compaction |
| **JVM Metrics** | Heap usage, GC pauses, Off-heap |
| **System Metrics** | CPU, Memory, Disk I/O, Network |

---

## Critical Metrics

### 1. Read/Write Latency

**JMX Path**:
```
org.apache.cassandra.metrics:type=ClientRequest,scope=Read,name=Latency
org.apache.cassandra.metrics:type=ClientRequest,scope=Write,name=Latency
```

**nodetool**:
```bash
nodetool proxyhistograms
```

**Thresholds**:
| Percentile | Read | Write |
|------------|------|-------|
| p50 | < 5ms | < 2ms |
| p99 | < 50ms | < 20ms |
| p999 | < 200ms | < 100ms |

**Recommended Alerts**:

| Alert | Condition | Duration | Severity |
|-------|-----------|----------|----------|
| High Read Latency | p99 > 100ms | 5 min | Warning |
| Critical Read Latency | p99 > 500ms | 5 min | Critical |
| High Write Latency | p99 > 50ms | 5 min | Warning |
| Critical Write Latency | p99 > 200ms | 5 min | Critical |

### 2. Request Throughput

**JMX Path**:
```
org.apache.cassandra.metrics:type=ClientRequest,scope=Read,name=Latency/Count
org.apache.cassandra.metrics:type=ClientRequest,scope=Write,name=Latency/Count
```

**What to look for**:
- Sudden drops (node issues, network problems)
- Unexpected spikes (traffic surge, retry storms)
- Uneven distribution across nodes (hot spots)

### 3. Dropped Messages

**JMX Path**:
```
org.apache.cassandra.metrics:type=DroppedMessage,scope=READ,name=Dropped
org.apache.cassandra.metrics:type=DroppedMessage,scope=MUTATION,name=Dropped
org.apache.cassandra.metrics:type=DroppedMessage,scope=RANGE_SLICE,name=Dropped
```

**nodetool**:
```bash
nodetool tpstats | grep -E "Message|Dropped"
```

**Thresholds**:
| Metric | Warning | Critical |
|--------|---------|----------|
| Any dropped | > 0 | > 100/min |

**What drops mean**:
- Messages exceeded timeout while queued
- System overloaded or GC paused too long
- Need capacity increase or query optimization

### 4. Pending Tasks

**JMX Path**:
```
org.apache.cassandra.metrics:type=ThreadPools,path=request,scope=*,name=PendingTasks
```

**nodetool**:
```bash
nodetool tpstats
```

**Key thread pools**:
| Pool | Warning | Critical |
|------|---------|----------|
| MutationStage | > 15 | > 50 |
| ReadStage | > 15 | > 50 |
| CompactionExecutor | > 32 | > 64 |
| MemtableFlushWriter | > 4 | > 8 |

---

## Storage Metrics

### 5. SSTable Count

**JMX Path**:
```
org.apache.cassandra.metrics:type=Table,name=LiveSSTableCount
```

**nodetool**:
```bash
nodetool tablestats my_keyspace.my_table | grep "SSTable count"
```

**Thresholds**:
| Level | Count | Action |
|-------|-------|--------|
| Normal | < 20 | None |
| Warning | 20-50 | Check compaction |
| Critical | > 50 | Investigate |

**High SSTable count indicates**:
- Compaction falling behind
- Write-heavy workload
- Inappropriate compaction strategy

### 6. Pending Compactions

**JMX Path**:
```
org.apache.cassandra.metrics:type=Compaction,name=PendingTasks
```

**nodetool**:
```bash
nodetool compactionstats
```

**Thresholds**:
| Level | Pending | Action |
|-------|---------|--------|
| Normal | < 10 | None |
| Warning | 10-50 | Monitor |
| Critical | > 50 | Increase throughput |

### 7. Disk Usage

**nodetool**:
```bash
nodetool status  # Shows Load per node
df -h /var/lib/cassandra
```

**Thresholds**:
| Level | Usage | Action |
|-------|-------|--------|
| Normal | < 50% | None |
| Warning | 50-70% | Plan expansion |
| Critical | > 70% | Urgent expansion |

**Important**: Leave 50% free for compaction operations.

---

## JVM Metrics

### 8. Heap Usage

**JMX Path**:
```
java.lang:type=Memory/HeapMemoryUsage
```

**nodetool**:
```bash
nodetool info | grep "Heap Memory"
```

**Thresholds**:
| Level | Usage | Action |
|-------|-------|--------|
| Normal | < 60% | None |
| Warning | 60-80% | Monitor GC |
| Critical | > 80% | Risk of OOM |

### 9. GC Pause Time

**JMX Path**:
```
java.lang:type=GarbageCollector,name=G1 Young Generation/CollectionTime
java.lang:type=GarbageCollector,name=G1 Old Generation/CollectionTime
```

**Log analysis**:
```bash
grep -E "GC pause" /var/log/cassandra/gc.log | tail -20
```

**Thresholds**:
| Level | Pause | Frequency |
|-------|-------|-----------|
| Normal | < 200ms | Occasional |
| Warning | 200-500ms | Frequent |
| Critical | > 500ms | Any |

---

## Error Metrics

### 10. Timeouts

**JMX Path**:
```
org.apache.cassandra.metrics:type=ClientRequest,scope=Read,name=Timeouts
org.apache.cassandra.metrics:type=ClientRequest,scope=Write,name=Timeouts
```

**Recommended Alerts**:

| Alert | Condition | Severity |
|-------|-----------|----------|
| Read Timeouts | Any timeouts occurring | Warning |
| Write Timeouts | Any timeouts occurring | Warning |
| Sustained Timeouts | > 10 timeouts/min for 5 min | Critical |

### 11. Unavailables

**JMX Path**:
```
org.apache.cassandra.metrics:type=ClientRequest,scope=Read,name=Unavailables
org.apache.cassandra.metrics:type=ClientRequest,scope=Write,name=Unavailables
```

**Recommended Alerts**:

| Alert | Condition | Severity |
|-------|-----------|----------|
| Read Unavailables | Any unavailable errors | Critical |
| Write Unavailables | Any unavailable errors | Critical |

!!! warning "Unavailables Indicate Serious Issues"
    Unavailable errors mean insufficient replicas are accessible to satisfy the consistency level. This typically indicates multiple node failures or network partitions requiring immediate investigation.

### 12. Exceptions

**JMX Path**:
```
org.apache.cassandra.metrics:type=Storage,name=Exceptions
```

**nodetool**:
```bash
nodetool info | grep "Exceptions"
```

---

## Per-Table Metrics

### Read/Write Latency per Table

**JMX Path**:
```
org.apache.cassandra.metrics:type=Table,keyspace=my_ks,scope=my_table,name=ReadLatency
org.apache.cassandra.metrics:type=Table,keyspace=my_ks,scope=my_table,name=WriteLatency
```

**nodetool**:
```bash
nodetool tablehistograms my_keyspace my_table
```

### Partition Size

**nodetool**:
```bash
nodetool tablehistograms my_keyspace my_table | grep "Partition Size"
```

**Thresholds**:
| Percentile | Warning | Critical |
|------------|---------|----------|
| p99 | > 50MB | > 100MB |

### Tombstone Metrics

**JMX Path**:
```
org.apache.cassandra.metrics:type=Table,name=TombstoneScannedHistogram
```

**nodetool**:
```bash
nodetool tablestats my_keyspace | grep -i tombstone
```

---

## Monitoring Quick Reference

### nodetool Commands

```bash
# Overall health
nodetool status
nodetool info
nodetool describecluster

# Performance
nodetool tpstats
nodetool proxyhistograms
nodetool tablestats my_keyspace

# Storage
nodetool compactionstats
nodetool tablehistograms my_keyspace my_table

# Operations
nodetool netstats
nodetool gossipinfo
```

### AxonOps Dashboard

[AxonOps](https://axonops.com) provides purpose-built dashboards for Cassandra monitoring, displaying all key metrics in a unified interface without requiring manual dashboard configuration.

**Pre-built Cassandra dashboards include:**

- **Cluster Overview** — Node status, schema agreement, cluster health at a glance
- **Latency & Throughput** — Read/write latency percentiles, request rates, error rates
- **Resource Utilization** — Heap usage, CPU, disk I/O, network across all nodes
- **Compaction & Storage** — Pending compactions, SSTable counts, disk usage trends
- **Per-Table Metrics** — Table-level latency, partition sizes, tombstone counts
- **Thread Pool Status** — Pending tasks, blocked threads, dropped messages

**Key advantages over manual monitoring:**

| Aspect | Manual (nodetool/JMX) | AxonOps |
|--------|----------------------|---------|
| Setup time | Hours to days | Minutes |
| Historical data | Not retained | Full retention |
| Cross-node correlation | Manual comparison | Automatic |
| Alerting | Separate configuration | Integrated |
| Query analysis | Not available | Slow query detection |

See [AxonOps Monitoring](../../../../../monitoring/overview.md) for dashboard features and configuration.

---

## Alert Configuration

### Critical Alerts (Page Immediately)

| Alert | Condition | Duration | Response |
|-------|-----------|----------|----------|
| Node Down | Node unreachable | 1 min | Check process, network, hardware |
| Heap Critical | Heap usage > 85% | 5 min | Investigate memory pressure, potential OOM |
| Disk Critical | Disk usage > 80% | 5 min | Clear snapshots, add capacity |
| Dropped Messages | Any messages dropped | 1 min | Check thread pools, timeouts, capacity |
| Unavailable Errors | Any unavailables | Immediate | Check replica availability |

### Warning Alerts (Review Soon)

| Alert | Condition | Duration | Response |
|-------|-----------|----------|----------|
| High Latency | p99 read > 100ms | 10 min | Check compaction, GC, disk I/O |
| Compaction Backlog | Pending > 30 | 15 min | Check throughput, consider tuning |
| Heap Warning | Heap usage > 70% | 10 min | Monitor trend, prepare mitigation |
| Hints Growing | Hints > 1000 | 10 min | Check target node health |
| Schema Disagreement | Multiple versions | 5 min | Check for stuck migrations |

### AxonOps Alert Configuration

AxonOps provides pre-configured alerts for all critical Cassandra metrics. Alerts can be customized through the AxonOps dashboard:

- **Threshold adjustment** — Modify alert thresholds based on workload characteristics
- **Notification routing** — Route alerts to Slack, PagerDuty, email, or webhooks
- **Alert suppression** — Configure maintenance windows to suppress expected alerts
- **Escalation policies** — Define escalation paths for unacknowledged alerts

See [Setup Alert Rules](../../../../../how-to/setup-alert-rules.md) for detailed configuration instructions.

---

## Next Steps

- **[AxonOps Monitoring](../../../../../monitoring/overview.md)** — Purpose-built Cassandra dashboards and alerting
- **[Alerting Guide](../alerting/index.md)** — Configure alert thresholds and notifications
- **[JMX Reference](../../jmx-reference/index.md)** — Complete JMX metrics reference
- **[Troubleshooting](../../troubleshooting/index.md)** — Diagnose and resolve issues
