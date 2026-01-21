---
title: "AxonOps Reporting Dashboard Metrics Mapping"
description: "Cassandra reporting dashboard metrics mapping. Operational reporting metrics."
meta:
  - name: keywords
    content: "reporting metrics, operational metrics, Cassandra"
search:
  boost: 8
---

# AxonOps Reporting Dashboard Metrics Mapping

This document maps the metrics used in the AxonOps Reporting dashboard.

## Dashboard Overview

The Reporting dashboard provides high-level system resource utilization and coordinator performance metrics for reporting and capacity planning. It focuses on aggregated views of resource usage and request distribution by consistency level.

## Metrics Mapping

### System Resource Metrics

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `host_Disk_Used` | Used disk space in bytes | `mountpoint`, `dc`, `rack`, `host_id` |
| `host_Disk_UsedPercent` | Disk usage percentage | `mountpoint`, `dc`, `rack`, `host_id` |
| `host_Disk_SectorsWrite` | Disk sectors written | `partition`, `axonfunction` (rate), `dc`, `rack`, `host_id` |
| `host_Disk_SectorsRead` | Disk sectors read | `partition`, `axonfunction` (rate), `dc`, `rack`, `host_id` |
| `host_CPU_Percent_Merge` | CPU usage percentage | `time` (real), `dc`, `rack`, `host_id` |

### Coordinator Metrics

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `cas_ClientRequest_Latency` | Request latency at coordinator | `scope` (Read*/Write*), `function` (percentiles/Count), `axonfunction` (rate), `dc`, `rack`, `host_id` |

## Query Examples

### System Resource Utilization
```promql
// Used Disk Space Per Node
host_Disk_Used{mountpoint=~'$mountpoint',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}

// Average Disk % Usage (Pie Chart)
// Used
avg(host_Disk_UsedPercent{mountpoint=~'$mountpoint',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'})
// Free
avg(100-host_Disk_UsedPercent{mountpoint=~'$mountpoint',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'})

// Max Disk Write Per Second
max(host_Disk_SectorsWrite{axonfunction='rate',dc=~'$dc',rack=~'$rack',host_id=~'$host_id',partition=~'$partition'})

// Max Disk Read Per Second
max(host_Disk_SectorsRead{axonfunction='rate',dc=~'$dc',rack=~'$rack',host_id=~'$host_id',partition=~'$partition'})

// Average CPU Usage per DC
avg(host_CPU_Percent_Merge{time='real',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by (dc)
```

### Coordinator Distribution
```promql
// Coordinator Reads Distribution (Pie Chart)
sum(cas_ClientRequest_Latency{axonfunction='rate',scope='Read*',scope!='Read',function='Count',function!='Min|Max',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by (scope)

// Coordinator Writes Distribution (Pie Chart)
sum(cas_ClientRequest_Latency{axonfunction='rate',scope='Write*',scope!='Write',function='Count',function!='Min|Max',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by (scope)
```

### Coordinator Performance by Consistency
```promql
// Read Throughput by Consistency
sum(cas_ClientRequest_Latency{axonfunction='rate',scope='Read.*$consistency',function='Count',function!='Min|Max',dc=~'$dc',rack=~'$rack', host_id=~'$host_id'}) by ($groupBy)

// Write Throughput by Consistency
sum(cas_ClientRequest_Latency{axonfunction='rate',scope='Write.*$consistency',function='Count',function!='Min|Max',dc=~'$dc',rack=~'$rack', host_id=~'$host_id'}) by ($groupBy)

// Max Read Latency by Consistency
max(cas_ClientRequest_Latency{scope='Read.*$consistency',function='$percentile',function!='Min|Max',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'})

// Max Write Latency by Consistency
max(cas_ClientRequest_Latency{scope='Write.*$consistency',function='$percentile',function!='Min|Max',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'})
```

## Panel Organization

### System Resource Utilisation
- **Average Disk % Usage** - Pie chart showing used vs free disk space

- **Used Disk Space Per Node** - Line chart of disk usage trends

- **Max Disk Read Per Second** - Peak disk read throughput

- **Max Disk Write Per Second** - Peak disk write throughput

- **Average CPU Usage per DC** - CPU utilization by datacenter

### Coordinator
- **Coordinator Reads distribution** - Pie chart of read consistency level distribution

- **Coordinator Writes distribution** - Pie chart of write consistency level distribution

- **Coordinator Read Throughput Per $groupBy ($consistency)** - Read ops/sec by consistency

- **Total Coordinator Write Throughput Per $groupBy ($consistency)** - Write ops/sec by consistency

- **Max Coordinator Read $consistency Latency** - Maximum read latency for selected consistency

- **Max Coordinator Write $consistency Latency** - Maximum write latency for selected consistency

## Filters

- **data center** (`dc`) - Filter by data center

- **rack** - Filter by rack

- **node** (`host_id`) - Filter by specific node

- **percentile** - Select latency percentile (50th, 75th, 95th, 98th, 99th, 999th)

- **groupBy** - Dynamic grouping (dc, rack, host_id)

- **mount point** (`mountpoint`) - Filter by disk mount point

- **partition** - Filter by disk partition

- **consistency** - Filter by consistency level (ALL, ANY, ONE, TWO, THREE, SERIAL, QUORUM, etc.)

## Understanding the Reporting Dashboard

### Purpose
- High-level cluster health overview
- Resource capacity planning
- Performance trend analysis
- Consistency level impact assessment

### Key Metrics for Reporting

**Resource Utilization**:

   - Disk usage trends for capacity planning
   - I/O throughput for performance baseline
   - CPU usage for load distribution

**Consistency Patterns**:

   - Distribution shows application behavior
   - Performance impact of consistency choices
   - Helps optimize consistency settings

**Aggregated Views**:

   - DC-level CPU averages
   - Cluster-wide consistency distribution
   - Peak performance metrics

## Report Generation Use Cases

### Capacity Planning Reports
```
Metrics to Include:
- Average Disk % Usage - Current utilization
- Used Disk Space Per Node - Growth trends
- Average CPU Usage per DC - Processing capacity
```

### Performance Baseline Reports
```
Metrics to Include:
- Max Disk Read/Write Per Second - I/O capacity
- Max Coordinator Latencies - SLA compliance
- Throughput by Consistency - Workload patterns
```

### Consistency Analysis Reports
```
Metrics to Include:
- Coordinator Read/Write distribution - Usage patterns
- Latency by Consistency - Performance impact
- Throughput by Consistency - Load distribution
```

## Best Practices

### Resource Monitoring
**Disk Space**:

   - Monitor usage trends
   - Set alerts at 80% utilization
   - Plan expansion at 70%

**I/O Performance**:

   - Track peak read/write rates
   - Identify I/O bottlenecks
   - Correlate with application load

**CPU Usage**:

   - Monitor DC-level averages
   - Identify hot spots
   - Balance load distribution

### Consistency Reporting
**Distribution Analysis**:

   - Understand application patterns
   - Identify consistency misuse
   - Optimize for performance

**Performance Impact**:

   - Compare latency by consistency
   - Measure throughput differences
   - Make data-driven decisions

## Data Aggregation Notes

### Disk Metrics
- Sectors are converted to bytes for display
- Rates calculated using `axonfunction='rate'`
- Mount points exclude system paths (`/etc*`)

### CPU Metrics
- Uses `time='real'` for actual CPU usage
- Averaged by datacenter for overview
- Percentage scale 0-100

### Coordinator Metrics
- Excludes base scopes (`scope!='Read'`, `scope!='Write'`)
- Filters out Min/Max functions for cleaner data
- Groups by configurable dimensions

## Units and Display

- **Disk Space**: bytes (binary units)

- **Disk I/O**: bytes/second

- **CPU**: percent (0-100)

- **Latency**: microseconds

- **Throughput**: rps/wps (reads/writes per second)

**Legend Format**:

  - Resources: `$dc - $host_id - $mountpoint/$partition`
  - Coordinator: `$groupBy` or `$scope`

## Troubleshooting

### Missing Disk Metrics
1. Verify mount point filter
2. Check partition naming
3. Confirm agent disk collection

### Inconsistent CPU Averages
1. Check node availability
2. Verify DC assignment
3. Review time range

### No Consistency Distribution
1. Ensure client requests exist
2. Check consistency filter
3. Verify scope patterns

## Notes

- Pie charts show current distribution, not historical
- Max functions used for worst-case reporting
- Some queries use special filtering like excluding empty consistency (`.*$consistency`)