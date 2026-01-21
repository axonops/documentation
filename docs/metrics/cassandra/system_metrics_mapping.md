---
title: "AxonOps System Dashboard Metrics Mapping"
description: "Cassandra system dashboard metrics mapping. CPU, memory, and disk metrics."
meta:
  - name: keywords
    content: "system metrics, CPU metrics, memory metrics, disk, Cassandra"
search:
  boost: 8
---

# AxonOps System Dashboard Metrics Mapping

This document maps the metrics used in the AxonOps System dashboard to their corresponding sources.

## Dashboard Overview

The System dashboard provides comprehensive monitoring of system resources including CPU, memory, disk, network, and JVM metrics. It helps monitor the health and performance of Cassandra nodes at the operating system level.

## Metrics Mapping

### CPU and Load Metrics

| Dashboard Metric | Source | Description | Attributes |
|-----------------|--------|-------------|------------|
| `host_CPU_Percent_Merge` | System metrics | Overall CPU usage percentage | `time=real`, `dc`, `rack`, `host_id` |
| `host_CPU` | System metrics | CPU usage by mode | `mode` (system/nice/user/iowait/irq/softirq), `dc`, `rack`, `host_id` |
| `host_load15` | System metrics | 15-minute load average | `dc`, `rack`, `host_id` |

### Memory Metrics

| Dashboard Metric | Source | Description | Attributes |
|-----------------|--------|-------------|------------|
| `host_Memory_Used` | System metrics | Used memory in bytes | `dc`, `rack`, `host_id` |
| `host_Memory_UsedPercent` | System metrics | Used memory percentage | `dc`, `rack`, `host_id` |
| `host_Memory_Cached` | System metrics | Cached memory in bytes | `dc`, `rack`, `host_id` |

### Disk Metrics

| Dashboard Metric | Source | Description | Attributes |
|-----------------|--------|-------------|------------|
| `host_Disk_UsedPercent` | System metrics | Disk usage percentage | `mountpoint`, `dc`, `rack`, `host_id` |
| `host_Disk_Used` | System metrics | Used disk space in bytes | `mountpoint`, `dc`, `rack`, `host_id` |
| `host_Disk_avgqsz` | System metrics | Average queue size | `partition`, `dc`, `rack`, `host_id` |
| `host_Disk_IOCount` | System metrics | I/O operations count | `partition`, `dc`, `rack`, `host_id` |
| `host_Disk_SectorsRead` | System metrics | Sectors read | `partition`, `dc`, `rack`, `host_id` |
| `host_Disk_SectorsWrite` | System metrics | Sectors written | `partition`, `dc`, `rack`, `host_id` |
| `host_Disk_WeightedIO` | System metrics | Weighted I/O time | `partition`, `dc`, `rack`, `host_id` |
| `host_Disk_IoTime` | System metrics | Time spent on disk I/O | `partition`, `dc`, `rack`, `host_id` |
| `host_filefd_allocated` | System metrics | Allocated file descriptors | `dc`, `rack`, `host_id` |
| `host_filefd_max` | System metrics | Maximum file descriptors | `dc`, `rack`, `host_id` |

### Network Metrics

| Dashboard Metric | Source | Description | Attributes |
|-----------------|--------|-------------|------------|
| `host_netIOCounters_BytesRecv` | System metrics | Network bytes received | `Interface`, `dc`, `rack`, `host_id` |
| `host_netIOCounters_BytesSent` | System metrics | Network bytes sent | `Interface`, `dc`, `rack`, `host_id` |
| `host_ntp_offset_seconds` | System metrics | NTP time offset in seconds | `dc`, `rack`, `host_id` |

### JVM Metrics

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `jvm_Memory_` | JVM memory usage | `function` (used/max/committed), `scope` (HeapMemoryUsage/NonHeapMemoryUsage) |
| `jvm_Threading_` | JVM thread information | `function` (ThreadCount) |
| `jvm_GarbageCollector_*` | GC statistics | `function` (CollectionCount/CollectionTime), collector name |

## Query Examples

### CPU Usage per Host
```promql
host_CPU_Percent_Merge{time='real',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}
```

### Average IO Wait CPU per Host
```promql
avg(host_CPU{axonfunction='rate',mode='iowait',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by (host_id) * 100
```

### Disk Usage Percentage
```promql
host_Disk_UsedPercent{mountpoint=~'$mountpoint',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}
```

### Network Received Bytes Rate
```promql
host_netIOCounters_BytesRecv{axonfunction='rate',Interface=~'$Interface',Interface!='lo',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}
```

### JVM Heap Utilization
```promql
jvm_Memory_{function='used',scope='HeapMemoryUsage',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}
```

### GC Count per Second
```promql
jvm_GarbageCollector_G1_Young_Generation{axonfunction='rate',function='CollectionCount',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}
```

## Panel Types and Descriptions

- **CPU usage per host** - Line chart showing overall CPU utilization

- **Avg IO wait CPU per Host** - Line chart highlighting I/O wait time

- **Load Average (15m)** - Line chart displaying system load

- **CPU Usage Detail** - Multiple line charts for different CPU modes (User, System, Nice, I/O Wait, Interrupt)

- **Disk Statistics** - Charts for disk usage, IOPS, bytes read/write, queue size

- **Memory Statistics** - Charts for memory usage, JVM heap, GC activity

- **Network Statistics** - Charts for network I/O and NTP offset

## Filters

- **data center** (`dc`) - Filter by data center

- **rack** - Filter by rack

- **node** (`host_id`) - Filter by specific node

- **mount point** (`mountpoint`) - Filter by disk mount point

- **partition** - Filter by disk partition

- **interface** (`Interface`) - Filter by network interface

## Notes

1. Host metrics are collected by the AxonOps agent at the OS level
2. JVM metrics are collected via JMX from the Cassandra process
3. The `axonfunction='rate'` label calculates rate-based metrics
4. Network interface 'lo' (loopback) is typically excluded from network metrics
5. CPU percentages are calculated from rate metrics and multiplied by 100
6. File descriptor usage is shown as a percentage: `(allocated/max)*100`