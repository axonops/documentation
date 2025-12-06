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

## Documentation Structure

### MBeans Reference

Detailed documentation for all 30+ MBeans:

- **[StorageServiceMBean](mbeans/storage-service.md)** - Core cluster operations
- **[StorageProxyMBean](mbeans/storage-proxy.md)** - Request coordination
- **[CompactionManagerMBean](mbeans/compaction-manager.md)** - Compaction management
- **[ColumnFamilyStoreMBean](mbeans/column-family-store.md)** - Per-table operations
- **[GossiperMBean](mbeans/gossiper.md)** - Gossip protocol
- **[StreamManagerMBean](mbeans/stream-manager.md)** - Data streaming
- **[CacheServiceMBean](mbeans/cache-service.md)** - Cache management
- **[CommitLogMBean](mbeans/commit-log.md)** - Commit log operations
- **[HintedHandoffManagerMBean](mbeans/hinted-handoff.md)** - Hint management
- **[MessagingServiceMBean](mbeans/messaging-service.md)** - Messaging statistics
- **[EndpointSnitchMBean](mbeans/endpoint-snitch.md)** - Topology awareness
- **[FailureDetectorMBean](mbeans/failure-detector.md)** - Node failure detection
- **[BatchlogManagerMBean](mbeans/batchlog-manager.md)** - Batch operations

### Metrics Reference

Comprehensive metrics documentation organized by category:

- **[Client Request Metrics](metrics/client-requests.md)** - Read/write latencies
- **[Table Metrics](metrics/tables.md)** - Per-table statistics
- **[Compaction Metrics](metrics/compaction.md)** - Compaction statistics
- **[Cache Metrics](metrics/caches.md)** - Key/row/chunk cache
- **[Thread Pool Metrics](metrics/thread-pools.md)** - Executor statistics
- **[Storage Metrics](metrics/storage.md)** - Disk usage
- **[Streaming Metrics](metrics/streaming.md)** - Data transfer
- **[Connection Metrics](metrics/connections.md)** - Client/internode
- **[Dropped Messages](metrics/dropped-messages.md)** - Timeout tracking
- **[Memory Metrics](metrics/memory.md)** - Heap/off-heap

### Connecting

- **[JMX Configuration](connecting/configuration.md)** - Enable and secure JMX
- **[Authentication](connecting/authentication.md)** - JMX security
- **[Remote Access](connecting/remote-access.md)** - Connect remotely
- **[SSL/TLS](connecting/ssl.md)** - Encrypted connections

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

## Tools Integration

### Prometheus + Grafana

Use the JMX Exporter for Prometheus:

```yaml
# jmx_exporter_config.yaml
lowercaseOutputName: true
lowercaseOutputLabelNames: true
rules:
  - pattern: org.apache.cassandra.metrics<type=(Table), keyspace=(\w+), scope=(\w+), name=(\w+)><>(Count|Value|Mean|99thPercentile)
    name: cassandra_table_$4
    labels:
      keyspace: "$2"
      table: "$3"
```

### AxonOps

AxonOps provides automated JMX metric collection with pre-built dashboards:

```yaml
# axon-agent.yml
cassandra:
  jmx:
    host: localhost
    port: 7199
```

### DataStax MCAC

Metrics Collector for Apache Cassandra:

```bash
# Install MCAC
tar -xzf mcac.tar.gz -C /opt/cassandra/lib/
```

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

1. **[MBeans Reference](mbeans/index.md)** - Detailed MBean documentation
2. **[Metrics Reference](metrics/index.md)** - Complete metrics catalog
3. **[JMX Configuration](connecting/configuration.md)** - Setup and security
4. **[Monitoring Guide](../monitoring/index.md)** - End-to-end monitoring
