# Cassandra Key Metrics Reference

This guide covers the essential metrics to monitor for a healthy Cassandra cluster.

## Metrics Overview

### The Four Golden Signals

| Signal | Cassandra Metrics | Why It Matters |
|--------|-------------------|----------------|
| **Latency** | Read/Write p99 | User experience |
| **Traffic** | Requests/second | Capacity planning |
| **Errors** | Timeouts, Unavailables | Service reliability |
| **Saturation** | CPU, Disk, Memory | Resource headroom |

### Metric Categories

```
┌─────────────────────────────────────────────────────────────┐
│                  Cassandra Metrics Hierarchy                │
├─────────────────────────────────────────────────────────────┤
│ Client Request Metrics                                      │
│   └── Read/Write latency, throughput, errors                │
├─────────────────────────────────────────────────────────────┤
│ Thread Pool Metrics                                         │
│   └── Active, Pending, Blocked, Completed                   │
├─────────────────────────────────────────────────────────────┤
│ Storage Metrics                                             │
│   └── SSTable count, Disk usage, Compaction                 │
├─────────────────────────────────────────────────────────────┤
│ JVM Metrics                                                 │
│   └── Heap usage, GC pauses, Off-heap                       │
├─────────────────────────────────────────────────────────────┤
│ System Metrics                                              │
│   └── CPU, Memory, Disk I/O, Network                        │
└─────────────────────────────────────────────────────────────┘
```

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

**Alerts**:
```yaml
- alert: HighReadLatency
  expr: cassandra_clientrequest_latency{scope="Read",quantile="0.99"} > 100000
  for: 5m
  severity: warning

- alert: CriticalReadLatency
  expr: cassandra_clientrequest_latency{scope="Read",quantile="0.99"} > 500000
  for: 5m
  severity: critical
```

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

**Alert**:
```yaml
- alert: ReadTimeouts
  expr: rate(cassandra_clientrequest_timeouts{scope="Read"}[5m]) > 0.1
  severity: warning
```

### 11. Unavailables

**JMX Path**:
```
org.apache.cassandra.metrics:type=ClientRequest,scope=Read,name=Unavailables
org.apache.cassandra.metrics:type=ClientRequest,scope=Write,name=Unavailables
```

**Alert**:
```yaml
- alert: ReadUnavailables
  expr: rate(cassandra_clientrequest_unavailables{scope="Read"}[5m]) > 0
  severity: critical
```

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

### Essential Metrics Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│                    Cluster Health                           │
│  Nodes: 6 UN / 0 DN    Schema: AGREE    Repair: OK         │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────────┐  ┌───────────────────────────┐
│   Latency (p99)          │  │   Throughput              │
│   Read:  ████░░░ 45ms    │  │   Reads:   12,450 ops/s   │
│   Write: ██░░░░░  8ms    │  │   Writes:   8,230 ops/s   │
└──────────────────────────┘  └───────────────────────────┘

┌──────────────────────────┐  ┌───────────────────────────┐
│   Errors (5m rate)       │  │   Resources               │
│   Timeouts:     0        │  │   Heap:    62% ████████░░ │
│   Unavailables: 0        │  │   CPU:     35% ████░░░░░░ │
│   Dropped:      0        │  │   Disk:    55% ██████░░░░ │
└──────────────────────────┘  └───────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│   Per-Node Status                                           │
│   Node        Heap%   Disk%   Read p99   Pending Compact   │
│   cass-1      62%     55%     42ms       5                 │
│   cass-2      58%     53%     38ms       3                 │
│   cass-3      65%     56%     48ms       8                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Alert Configuration

### Critical Alerts (Page Immediately)

```yaml
alerts:
  - name: CassandraNodeDown
    condition: up{job="cassandra"} == 0
    duration: 1m
    severity: critical

  - name: CassandraHeapCritical
    condition: jvm_memory_heap_used / jvm_memory_heap_max > 0.85
    duration: 5m
    severity: critical

  - name: CassandraDiskCritical
    condition: disk_used_percent > 80
    duration: 5m
    severity: critical

  - name: CassandraDroppedMessages
    condition: rate(cassandra_droppedmessage_dropped_total[5m]) > 1
    duration: 1m
    severity: critical
```

### Warning Alerts (Review Soon)

```yaml
alerts:
  - name: CassandraHighLatency
    condition: cassandra_clientrequest_latency{quantile="0.99"} > 100000
    duration: 10m
    severity: warning

  - name: CassandraCompactionBacklog
    condition: cassandra_compaction_pendingtasks > 30
    duration: 15m
    severity: warning

  - name: CassandraHeapWarning
    condition: jvm_memory_heap_used / jvm_memory_heap_max > 0.70
    duration: 10m
    severity: warning
```

---

## Next Steps

- **[Alerting Guide](../alerting/index.md)** - Set up alerts
- **[Dashboards](../dashboards/index.md)** - Build dashboards
- **[JMX Reference](../../jmx-reference/index.md)** - Complete metrics list
- **[Troubleshooting](../../troubleshooting/index.md)** - Problem resolution
