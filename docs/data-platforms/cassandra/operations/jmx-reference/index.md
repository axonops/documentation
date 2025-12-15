---
title: "Cassandra JMX Reference"
description: "Cassandra JMX reference. MBeans, metrics, and management operations."
meta:
  - name: keywords
    content: "Cassandra JMX, MBeans reference, JMX metrics"
---

# Cassandra JMX Reference

JMX is how to see inside Cassandra. Every metric the database tracks—request latencies, compaction progress, thread pool utilization, disk usage—is exposed through JMX. When `nodetool status` runs, it is querying JMX. When Prometheus scrapes metrics, it is reading JMX.

The metric names are verbose (`org.apache.cassandra.metrics:type=ClientRequest,scope=Read,name=Latency`) but logical once the structure is understood. Most metrics include multiple statistics: count, mean, p50, p75, p95, p99, p999, and rate.

This reference documents the MBeans used in practice, what each metric means, and how to interpret the values.

## Overview

Cassandra exposes hundreds of metrics through JMX, organized into MBeans (Managed Beans). These metrics provide visibility into:

- **Cluster Health**: Node status, gossip, and membership
- **Performance**: Latencies, throughput, and resource utilization
- **Storage**: Disk usage, compaction, and SSTable statistics
- **Operations**: Read/write patterns, cache efficiency
- **Resources**: Memory, threads, and connections

## Quick Start

### Connecting via JMX

#### Using nodetool

```bash
# Most nodetool commands use JMX internally
nodetool status
nodetool info
nodetool tpstats
```

#### Using jconsole

```bash
# Connect to local node
jconsole

# Connect to remote node
jconsole cassandra.example.com:7199
```

#### Using VisualVM

```bash
# With JMX plugin
visualvm --openjmx cassandra.example.com:7199
```

#### Programmatic Access (Java)

```java
import javax.management.*;
import javax.management.remote.*;

String url = "service:jmx:rmi:///jndi/rmi://localhost:7199/jmxrmi";
JMXServiceURL serviceUrl = new JMXServiceURL(url);
JMXConnector connector = JMXConnectorFactory.connect(serviceUrl);
MBeanServerConnection mbsc = connector.getMBeanServerConnection();

// Query all Cassandra metrics
ObjectName pattern = new ObjectName("org.apache.cassandra.metrics:*");
Set<ObjectName> names = mbsc.queryNames(pattern, null);
```

---

## MBean Categories

Cassandra organizes MBeans into these primary domains:

| Domain | Purpose |
|--------|---------|
| `org.apache.cassandra.metrics` | Performance metrics |
| `org.apache.cassandra.db` | Database operations |
| `org.apache.cassandra.net` | Network/messaging |
| `org.apache.cassandra.internal` | Internal operations |
| `org.apache.cassandra.request` | Request handling |

### Key MBeans

| MBean | Purpose | Key Operations |
|-------|---------|----------------|
| **StorageServiceMBean** | Cluster operations | Bootstrap, decommission, repair |
| **StorageProxyMBean** | Request coordination | Timeout settings |
| **CompactionManagerMBean** | Compaction control | Start/stop compaction |
| **ColumnFamilyStoreMBean** | Table operations | Force flush, snapshots |
| **GossiperMBean** | Gossip protocol | Node status |
| **StreamManagerMBean** | Streaming operations | Monitor transfers |
| **CacheServiceMBean** | Cache management | Key/row cache |
| **CommitLogMBean** | Commit log | Archive settings |
| **HintedHandoffManagerMBean** | Hinted handoff | Hint delivery |
| **MessagingServiceMBean** | Inter-node messaging | Dropped messages |

---

---

## Essential Metrics Quick Reference

### Health Indicators

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Heap Usage | > 70% | > 85% | Check GC, reduce load |
| Pending Compactions | > 20 | > 50 | Check disk I/O |
| Dropped Messages | > 0 | > 100/min | Check timeouts |
| Read Latency (p99) | > 50ms | > 500ms | Check data model |
| Write Latency (p99) | > 10ms | > 100ms | Check disk I/O |

### Key Metric Paths

```
# Read latency (per table)
org.apache.cassandra.metrics:type=Table,keyspace=ks,scope=table,name=ReadLatency

# Write latency (per table)
org.apache.cassandra.metrics:type=Table,keyspace=ks,scope=table,name=WriteLatency

# Compactions pending
org.apache.cassandra.metrics:type=Compaction,name=PendingTasks

# Heap usage
java.lang:type=Memory/HeapMemoryUsage

# Thread pool stats
org.apache.cassandra.metrics:type=ThreadPools,path=request,scope=ReadStage,name=ActiveTasks
```

---

## Monitoring Best Practices

### What to Monitor

**Always Monitor**:
1. Request latencies (read/write p99)
2. Heap usage and GC activity
3. Pending compactions
4. Dropped messages
5. Disk space utilization

**Monitor for Capacity**:
1. Request rates
2. Storage growth
3. Connection counts
4. Thread pool utilization

**Monitor for Problems**:
1. Timeout exceptions
2. Unavailable exceptions
3. Tombstone warnings
4. Large partition warnings

### Alert Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Heap Usage | 70% | 85% |
| Disk Usage | 60% | 80% |
| Read Latency p99 | 50ms | 500ms |
| Write Latency p99 | 10ms | 100ms |
| Pending Compactions | 20 | 50 |
| Dropped Mutations | 0 | 100/min |
| GC Pause Time | 200ms | 500ms |

### Collection Intervals

| Metric Type | Interval | Reason |
|-------------|----------|--------|
| Latencies | 10-30s | High granularity needed |
| Throughput | 30-60s | Trend analysis |
| Resource usage | 60s | Capacity planning |
| Compaction | 60s | Long-running operations |

---

## AxonOps Integration

While JMX can be accessed directly via nodetool, jconsole, or custom tooling, [AxonOps](https://axonops.com) provides automated JMX metric collection with purpose-built Cassandra dashboards and alerting.

### Automated Metric Collection

AxonOps eliminates the need to manually configure JMX exporters or build dashboards:

| Manual JMX Approach | AxonOps |
|---------------------|---------|
| Configure JMX exporter YAML rules | Automatic—no configuration needed |
| Build and maintain Grafana dashboards | Pre-built Cassandra dashboards |
| Write custom alerting rules | Integrated alerting with Cassandra-aware thresholds |
| Correlate metrics across nodes manually | Unified cluster view |
| No historical retention by default | Full metric history with trends |

### Agent Configuration

```yaml
# axon-agent.yml
cassandra:
  jmx:
    host: localhost
    port: 7199
```

### What AxonOps Collects

The AxonOps agent automatically collects all critical Cassandra JMX metrics:

- **Request metrics** — Read/write latency percentiles, throughput, timeouts, unavailables
- **Thread pool metrics** — Pending tasks, active threads, blocked threads per stage
- **Storage metrics** — SSTable counts, disk usage, compaction pending/completed
- **JVM metrics** — Heap usage, GC pause times, off-heap memory
- **Table-level metrics** — Per-table latency, partition sizes, tombstone counts
- **Streaming metrics** — Repair progress, bootstrap/decommission status

See [AxonOps Installation](../../../../get_started/cloud.md) for setup instructions and [AxonOps Monitoring](../../../../monitoring/overview.md) for dashboard features.

---

## Common Operations via JMX

### Trigger Compaction

```java
ObjectName compactionManager = new ObjectName(
    "org.apache.cassandra.db:type=CompactionManager"
);
mbsc.invoke(compactionManager, "forceUserDefinedCompaction",
    new Object[]{"keyspace", "table"},
    new String[]{"java.lang.String", "java.lang.String"});
```

### Force Flush

```java
ObjectName storageService = new ObjectName(
    "org.apache.cassandra.db:type=StorageService"
);
mbsc.invoke(storageService, "forceKeyspaceFlush",
    new Object[]{"keyspace"},
    new String[]{"java.lang.String"});
```

### Get Cluster Status

```java
ObjectName storageService = new ObjectName(
    "org.apache.cassandra.db:type=StorageService"
);
List<String> liveNodes = (List<String>) mbsc.getAttribute(
    storageService, "LiveNodes"
);
```

---

## Next Steps

- **[AxonOps Monitoring](../../../../monitoring/overview.md)** — Pre-built dashboards for all Cassandra JMX metrics
- **[Key Metrics](../monitoring/key-metrics/index.md)** — Essential metrics and alert thresholds
- **[Monitoring Guide](../monitoring/index.md)** — End-to-end monitoring setup
