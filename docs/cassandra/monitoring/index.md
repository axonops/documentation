# Cassandra Monitoring Guide

Cassandra exposes hundreds of metrics via JMX. A subset of these metrics provides visibility into cluster health: read/write latency, pending compactions, dropped mutations, and heap usage.

This guide covers key metrics, alerting thresholds, and dashboard configuration.

## Monitoring Overview

### The Four Golden Signals

| Signal | Cassandra Metric | Target |
|--------|------------------|--------|
| **Latency** | Read/Write p99 | < 100ms read, < 50ms write |
| **Traffic** | Requests/second | Baseline + capacity |
| **Errors** | Timeouts, Unavailables | 0 or near-zero |
| **Saturation** | CPU, Disk, Memory | < 70% utilization |

### Key Metrics Categories

1. **Client Requests** - Read/write latency and throughput
2. **Cluster Health** - Node status, gossip, schema
3. **Storage** - Disk usage, SSTables, compaction
4. **Resources** - CPU, memory, threads
5. **JVM** - Heap usage, GC activity

---

## Documentation Structure

### Key Metrics

- **[Key Metrics Overview](key-metrics/index.md)** - Essential metrics to track
- **[Latency Metrics](key-metrics/latency.md)** - Request latencies
- **[Throughput Metrics](key-metrics/throughput.md)** - Request rates
- **[Resource Metrics](key-metrics/resources.md)** - CPU, memory, disk
- **[JVM Metrics](key-metrics/jvm.md)** - Heap and GC

### Alerting

- **[Alert Setup](alerting/index.md)** - Configuring alerts
- **[Alert Thresholds](alerting/thresholds.md)** - Recommended values
- **[Alert Runbooks](alerting/runbooks.md)** - Response procedures

### Dashboards

- **[Dashboard Overview](dashboards/index.md)** - Visualization best practices
- **[AxonOps Dashboards](dashboards/axonops.md)** - AxonOps dashboard configuration

### Logging

- **[Log Configuration](logging/index.md)** - Logback setup
- **[Log Analysis](logging/analysis.md)** - Understanding logs
- **[Log Aggregation](logging/aggregation.md)** - Centralized logging

---

## Essential Metrics Quick Reference

### Must-Monitor Metrics

| Metric | Warning | Critical | nodetool Command |
|--------|---------|----------|------------------|
| Heap Usage | > 70% | > 85% | `nodetool info` |
| Read Latency p99 | > 50ms | > 500ms | `nodetool proxyhistograms` |
| Write Latency p99 | > 10ms | > 100ms | `nodetool proxyhistograms` |
| Pending Compactions | > 20 | > 50 | `nodetool compactionstats` |
| Dropped Messages | > 0 | > 100/min | `nodetool tpstats` |
| Disk Usage | > 60% | > 80% | `df -h` |

### JMX Metric Paths

```
# Read latency
org.apache.cassandra.metrics:type=ClientRequest,scope=Read,name=Latency

# Write latency
org.apache.cassandra.metrics:type=ClientRequest,scope=Write,name=Latency

# Pending compactions
org.apache.cassandra.metrics:type=Compaction,name=PendingTasks

# Dropped mutations
org.apache.cassandra.metrics:type=DroppedMessage,scope=MUTATION,name=Dropped

# Heap usage
java.lang:type=Memory/HeapMemoryUsage
```

---

## Metrics Collection

### Using nodetool

```bash
#!/bin/bash
# basic_monitoring.sh

echo "=== Node Status ==="
nodetool status

echo "=== Thread Pools ==="
nodetool tpstats | head -30

echo "=== Latencies ==="
nodetool proxyhistograms

echo "=== Compaction ==="
nodetool compactionstats

echo "=== Table Stats ==="
nodetool tablestats <keyspace> | grep -E "Read Latency|Write Latency|SSTable count"
```

### Using JMX

```bash
# Connect with jconsole
jconsole localhost:7199

# Or use jmxterm for scripting
java -jar jmxterm.jar -l localhost:7199
> bean org.apache.cassandra.metrics:type=ClientRequest,scope=Read,name=Latency
> get 99thPercentile
```

### Using AxonOps Agent

The AxonOps agent collects metrics via JMX and reports to the AxonOps server. Configuration is defined in the agent configuration file.

```yaml
# /etc/axonops/axon-agent.yml

axon-server:
  hosts: "axonops-server.example.com"
  port: 1888

cassandra:
  host: localhost
  jmx_port: 7199
  # JMX authentication (if enabled)
  # jmx_user: cassandra
  # jmx_password: cassandra

metrics:
  enabled: true
  interval: 15s

logs:
  enabled: true
  path: /var/log/cassandra/
```

Verify agent connectivity:

```bash
# Check agent status
systemctl status axon-agent

# View agent logs
journalctl -u axon-agent -f
```

---

## Alert Thresholds

### Critical Alerts (Immediate Response)

| Metric | Condition | Typical Cause |
|--------|-----------|---------------|
| Node Down | Node unreachable > 1m | Process crash, network partition |
| Heap Usage | > 85% for 5m | Memory pressure, GC issues |
| Disk Usage | > 85% | Data growth, compaction debt |
| Dropped Messages | Any | Overload, timeout |

### Warning Alerts (Investigation Required)

| Metric | Condition | Typical Cause |
|--------|-----------|---------------|
| Read Latency p99 | > 100ms for 10m | Compaction backlog, disk issues |
| Write Latency p99 | > 50ms for 10m | Commit log contention |
| Pending Compactions | > 30 for 15m | Write volume exceeds compaction capacity |
| Heap Usage | > 70% for 10m | Approaching memory pressure |

---

## Dashboard Essentials

### Cluster Overview Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│                    Cluster Health                           │
│  Nodes: 6 UP / 0 DOWN    Schema: AGREE    Repair: OK       │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────┐  ┌──────────────────────┐
│   Read Latency p99   │  │   Write Latency p99  │
│   ████████░░ 45ms    │  │   ███░░░░░░░ 8ms     │
└──────────────────────┘  └──────────────────────┘

┌──────────────────────┐  ┌──────────────────────┐
│   Requests/sec       │  │   Pending Compaction │
│   Reads:  12,450     │  │   ██░░░░░░░░ 8       │
│   Writes:  8,230     │  │                      │
└──────────────────────┘  └──────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Per-Node Metrics                         │
│  Node        Heap%   Disk%   CPU%   Read p99   Write p99   │
│  cass-1      62%     45%     23%    42ms       7ms         │
│  cass-2      58%     47%     19%    38ms       6ms         │
│  cass-3      65%     46%     25%    48ms       9ms         │
└─────────────────────────────────────────────────────────────┘
```

### Key Graphs

1. **Latency over time** - Read/Write p50, p99, p999
2. **Request rate** - Operations per second
3. **Heap usage** - Used vs max over time
4. **Disk usage** - Per-node disk utilization
5. **Compaction** - Pending tasks and throughput
6. **GC activity** - Pause times and frequency

---

## Monitoring Best Practices

### Collection Intervals

| Metric Type | Interval | Reason |
|-------------|----------|--------|
| Latencies | 10-30s | Granularity for troubleshooting |
| Throughput | 30-60s | Trend analysis |
| Resource usage | 60s | Slow-changing values |
| Disk space | 5m | Slow-changing values |

### Retention

| Data Type | Retention | Resolution |
|-----------|-----------|------------|
| Real-time | 1 hour | 10s |
| Recent | 1 day | 1m |
| Historical | 30 days | 5m |
| Long-term | 1 year | 1h |

### Alert Fatigue Prevention

- Set thresholds based on baseline measurements
- Use duration requirements to filter transient spikes
- Create runbooks for every alert
- Review and tune alerts regularly

---

## Troubleshooting with Metrics

### High Latency Investigation

```
1. Check nodetool proxyhistograms
   └─> High coordinator latency?
       └─> Check network to replicas

2. Check nodetool tablehistograms <ks> <table>
   └─> High local latency?
       └─> Check tablestats for:
           - SSTable count (compaction?)
           - Partition size (data model?)
           - Tombstones (too many deletes?)

3. Check nodetool tpstats
   └─> ReadStage blocked?
       └─> Capacity issue

4. Check GC logs
   └─> Long pauses?
       └─> Tune JVM or reduce load
```

### Capacity Planning

```
Current utilization:
- CPU: 40% average, 70% peak
- Disk: 55% used
- Memory: 65% heap average

Growth rate:
- Data: 10GB/day
- Traffic: 5% monthly increase

Time to capacity:
- Disk: (remaining GB) / (daily growth) = X days
- Traffic: When peak CPU > 80%
```

---

## Next Steps

- **[Key Metrics Detail](key-metrics/index.md)** - Deep dive on metrics
- **[Alert Configuration](alerting/index.md)** - Set up alerts
- **[AxonOps Dashboards](dashboards/axonops.md)** - Dashboard configuration
