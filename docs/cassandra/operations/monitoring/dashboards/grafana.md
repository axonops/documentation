# AxonOps Dashboard Configuration

AxonOps provides pre-configured dashboards for Cassandra monitoring. This guide covers dashboard navigation, customization, and interpretation.

## Dashboard Overview

### Available Dashboards

| Dashboard | Purpose |
|-----------|---------|
| Cluster Overview | High-level cluster health and status |
| Node Details | Per-node metrics and resource utilization |
| Table Statistics | Per-table performance metrics |
| Compaction | Compaction activity and backlog |
| Repair Status | Repair progress and scheduling |
| Backup Status | Backup job status and history |

---

## Cluster Overview Dashboard

The Cluster Overview dashboard provides a summary of cluster health.

### Health Indicators

| Indicator | Green | Yellow | Red |
|-----------|-------|--------|-----|
| Node Status | All nodes UP | 1 node DOWN | Multiple nodes DOWN |
| Schema Agreement | All nodes agree | - | Schema disagreement |
| Repair Status | Within SLA | Approaching SLA | Overdue |

### Key Panels

**Node Status Panel**

Displays the current state of all nodes in the cluster:

- UP: Node is operational and responding
- DOWN: Node is unreachable
- JOINING: Node is bootstrapping
- LEAVING: Node is decommissioning

**Latency Panel**

Shows read and write latency percentiles:

- p50: Median latency (50th percentile)
- p99: 99th percentile latency
- p999: 99.9th percentile latency

Latency spikes correlate with:

- Compaction activity
- GC pauses
- Disk I/O saturation
- Network issues

**Request Rate Panel**

Displays operations per second:

- Read requests/sec
- Write requests/sec
- Range scan requests/sec

Use for capacity planning and anomaly detection.

---

## Node Details Dashboard

Per-node metrics for detailed analysis.

### Resource Utilization

**CPU Usage**

| Metric | Description |
|--------|-------------|
| User CPU | Application processing |
| System CPU | Kernel operations |
| I/O Wait | Waiting for disk |

High I/O wait indicates disk bottleneck.

**Memory Usage**

| Metric | Description |
|--------|-------------|
| Heap Used | JVM heap consumption |
| Heap Max | Configured heap limit |
| Off-Heap | Native memory usage |

Monitor heap usage trends for GC tuning.

**Disk Usage**

| Metric | Description |
|--------|-------------|
| Data Directory | SSTable storage |
| Commit Log | Write-ahead log |
| Total Used | Combined usage |

Plan for capacity when usage exceeds 60%.

### JVM Metrics

**Garbage Collection**

| Metric | Description |
|--------|-------------|
| Young GC Count | Minor collections |
| Young GC Time | Time in minor GC |
| Old GC Count | Major collections |
| Old GC Time | Time in major GC |

Increasing old GC frequency indicates memory pressure.

**Thread Pools**

| Pool | Purpose | Watch For |
|------|---------|-----------|
| ReadStage | Read operations | Pending > 0 |
| MutationStage | Write operations | Pending > 0 |
| CompactionExecutor | Compaction tasks | Blocked > 0 |
| MemtableFlushWriter | Memtable flushes | Pending > 0 |

Blocked threads indicate resource constraints.

---

## Table Statistics Dashboard

Per-table metrics for data model optimization.

### Key Metrics

| Metric | Description | Action Threshold |
|--------|-------------|------------------|
| SSTable Count | Number of SSTables | > 20 per table |
| Read Latency | Local read time | > 10ms |
| Write Latency | Local write time | > 5ms |
| Partition Size | Average partition size | > 100MB |
| Tombstone Count | Deleted data markers | > 1000 per read |

### Identifying Problematic Tables

High SSTable counts indicate:

- Insufficient compaction throughput
- Inappropriate compaction strategy
- High write volume

High tombstone counts indicate:

- Excessive deletes
- TTL-heavy workload
- Need for tombstone-aware queries

Large partitions indicate:

- Unbounded partition growth
- Data model issues
- Need for partition splitting

---

## Compaction Dashboard

Monitor compaction activity and backlog.

### Compaction Metrics

| Metric | Description |
|--------|-------------|
| Pending Tasks | Compactions waiting to run |
| Active Compactions | Currently running compactions |
| Compaction Throughput | MB/s being compacted |
| Estimated Remaining | Bytes remaining to compact |

### Interpreting Compaction Status

| Pending Tasks | Status | Action |
|---------------|--------|--------|
| 0-10 | Healthy | None |
| 10-30 | Elevated | Monitor |
| 30-50 | Warning | Investigate |
| > 50 | Critical | Intervene |

### Compaction Strategy Indicators

**Size-Tiered (STCS)**

- Good for write-heavy workloads
- Watch for space amplification
- SSTable count may grow during write bursts

**Leveled (LCS)**

- Good for read-heavy workloads
- Steady SSTable count
- Higher write amplification

**Time-Window (TWCS)**

- Good for time-series data
- Partitioned by time windows
- Efficient TTL handling

---

## Repair Dashboard

Track repair status and history.

### Repair Metrics

| Metric | Description |
|--------|-------------|
| Last Repair | Time since last successful repair |
| Repair Duration | Average repair time |
| Repair Progress | Current repair completion |
| Failed Repairs | Repairs that did not complete |

### Repair SLA

| Interval | Risk Level |
|----------|------------|
| < 7 days | Low |
| 7-10 days | Medium |
| > 10 days | High |
| > gc_grace_seconds | Critical |

Repairs must complete within `gc_grace_seconds` to prevent data resurrection.

---

## Dashboard Customization

### Time Range Selection

| Range | Use Case |
|-------|----------|
| Last 1 hour | Real-time troubleshooting |
| Last 24 hours | Daily patterns |
| Last 7 days | Weekly trends |
| Last 30 days | Capacity planning |

### Filtering

Filter dashboards by:

- Cluster name
- Datacenter
- Node
- Keyspace
- Table

### Annotations

Mark events on dashboards:

- Deployments
- Configuration changes
- Incidents
- Maintenance windows

---

## Creating Custom Dashboards

### Adding Panels

1. Navigate to dashboard edit mode
2. Select **Add Panel**
3. Choose visualization type
4. Select metric from available metrics
5. Configure display options

### Available Visualizations

| Type | Use Case |
|------|----------|
| Time Series | Metrics over time |
| Gauge | Current value with thresholds |
| Stat | Single value display |
| Table | Tabular data |
| Heatmap | Distribution visualization |

### Metric Selection

Metrics are organized by category:

```
cassandra.
├── client_request.
│   ├── read.
│   │   ├── latency.{p50,p99,p999}
│   │   └── count
│   └── write.
│       ├── latency.{p50,p99,p999}
│       └── count
├── compaction.
│   ├── pending_tasks
│   └── bytes_compacted
├── storage.
│   ├── load
│   └── exceptions
└── thread_pool.
    ├── {pool_name}.active
    ├── {pool_name}.pending
    └── {pool_name}.blocked
```

---

## Dashboard Best Practices

### Organization

```
Recommended dashboard hierarchy:

1. Cluster Overview (executive summary)
2. Node Details (operational view)
3. Table Statistics (data model view)
4. Operations (repair, compaction, backup)
5. Troubleshooting (detailed diagnostics)
```

### Refresh Intervals

| Dashboard Type | Refresh Rate |
|----------------|--------------|
| Real-time monitoring | 10-30 seconds |
| Operational overview | 1-5 minutes |
| Historical analysis | Manual |

### Alerting from Dashboards

Configure alerts based on dashboard panel thresholds. See [Alert Configuration](../alerting/index.md) for details.

---

## Exporting and Sharing

### Export Options

- PDF report generation
- Scheduled email reports
- API access for integration

### Sharing Dashboards

- Share links to specific dashboards
- Embed dashboards in other tools
- Export dashboard configurations

---

## Next Steps

- **[Alert Configuration](../alerting/index.md)** - Set up alerts
- **[Key Metrics](../key-metrics/index.md)** - Metrics reference
- **[Monitoring Overview](../index.md)** - Monitoring guide
