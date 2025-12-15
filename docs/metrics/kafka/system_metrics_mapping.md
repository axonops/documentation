---
title: "AxonOps Kafka System Dashboard Metrics Mapping"
description: "Kafka system dashboard metrics mapping. CPU, memory, and disk metrics."
meta:
  - name: keywords
    content: "Kafka system metrics, CPU, memory, disk"
---

# AxonOps Kafka System Dashboard Metrics Mapping

## Overview

The Kafka System Dashboard provides comprehensive monitoring of system-level resources across your Kafka cluster. It tracks CPU utilization, disk I/O, memory usage, JVM performance, and network statistics to ensure optimal cluster health and performance.

## Metrics Mapping

| Dashboard Metric | Description | Attributes |
|-----------------|---------------------------|-------------|
| **CPU Metrics** | | | |
| `host_CPU_Percent_Merge` | Overall CPU utilization percentage | time='real' |
| `host_CPU` (mode='iowait') | CPU time waiting for I/O operations | mode='iowait' |
| `host_load15` | 15-minute load average | - |
| **Disk Metrics** | | | |
| `host_Disk_UsedPercent` | Percentage of disk space used | - |
| `host_Disk_Used` | Absolute disk space used in bytes | - |
| `host_Disk_SectorsRead` | Disk read throughput in bytes/sec | - |
| `host_Disk_SectorsWrite` | Disk write throughput in bytes/sec | - |
| `host_Disk_IOCount` | Input/output operations per second | - |
| `host_Disk_avgqsz` | Average disk queue size | - |
| `host_Disk_WeightedIO` | Weighted I/O time in milliseconds | - |
| `host_Disk_IoTime` | Time spent on disk I/O operations | - |
| `host_filefd_allocated` | Number of allocated file descriptors | - |
| `host_filefd_max` | Maximum available file descriptors | - |
| **Memory Metrics** | | | |
| `host_Memory_Used` | Used system memory in bytes | - |
| `host_Memory_Cached` | Cached memory in bytes | - |
| `host_Memory_UsedPercent` | Memory usage percentage | - |
| **JVM Metrics** | | | |
| `jvm_Threading_` | JVM thread count | type=Threading |
| `jvm_GarbageCollector_G1_Young_Generation` | G1 GC statistics | name=G1 Young Generation |
| `jvm_GarbageCollector_ZGC` | ZGC statistics | name=ZGC |
| `jvm_GarbageCollector_Shenandoah_Cycles` | Shenandoah GC statistics | name=Shenandoah |
| `jvm_GarbageCollector_ConcurrentMarkSweep` | CMS GC statistics | name=ConcurrentMarkSweep |
| `jvm_GarbageCollector_ParNew` | ParNew GC statistics | name=ParNew |
| `jvm_Memory_` | JVM heap and non-heap memory usage | type=Memory |
| **Network Metrics** | | | |
| `host_netIOCounters_BytesRecv` | Network bytes received per second | - |
| `host_netIOCounters_BytesSent` | Network bytes sent per second | - |
| `host_ntp_offset_seconds` | NTP time offset in seconds | - |

## Query Examples

### CPU Usage by Rack
```promql
avg(host_CPU_Percent_Merge{time='real',rack=~'$rack',host_id=~'$host_id', node_type='$node_type', type='kafka'}) by (rack)
```

### I/O Wait Percentage
```promql
avg(host_CPU{axonfunction='rate',mode='iowait',rack=~'$rack',host_id=~'$host_id',node_type='$node_type', type='kafka'}) by (host_id) * 100
```

### Disk I/O Throughput
```promql
// Read throughput
host_Disk_SectorsRead{axonfunction='rate',rack=~'$rack',host_id=~'$host_id',partition=~'$partition',node_type='$node_type', type='kafka'}

// Write throughput
host_Disk_SectorsWrite{axonfunction='rate',rack=~'$rack',host_id=~'$host_id',partition=~'$partition', node_type='$node_type', type='kafka'}
```

### File Descriptor Usage
```promql
(host_filefd_allocated{rack=~'$rack',host_id=~'$host_id'} / host_filefd_max{rack=~'$rack',host_id=~'$host_id', node_type='$node_type', type='kafka'})*100
```

### JVM Heap Memory Usage
```promql
jvm_Memory_{function='used',scope='HeapMemoryUsage',rack=~'$rack',host_id=~'$host_id', node_type='$node_type', type='kafka'}
```

### GC Rate
```promql
jvm_GarbageCollector_G1_Young_Generation{axonfunction='rate',function='CollectionCount',rack=~'$rack',host_id=~'$host_id', node_type='$node_type', type='kafka'}
```

## Panel Organization

**Overview Section**

   - Average CPU Usage per Rack

**CPU and Load**

   - CPU usage per host
   - Load Average (15m)
   - Avg IO wait CPU per Host

**Disk Statistics**

   - Disk % Usage by mount point
   - Used Disk Space Per Node
   - Bytes Read/Write Per Second
   - IOPS
   - Disk avgqsz
   - Disk WeightedIO time
   - % File Descriptors Allocated
   - Time Spent on Disk IO

**Memory Statistics**

   - Used memory
   - Cached memory
   - Used Memory Percentage
   - JVM Thread Count
   - GC Count per sec
   - GC Duration
   - JVM Utilization (Heap/Non-Heap)
   - JVM Heap Utilization

**Network Statistics**

   - Network Received (bytes)
   - Network Transmitted (bytes)
   - NTP offset (milliseconds)

## Filters

- **node_type**: Filter by node type (broker, controller, etc.)

- **rack**: Filter by rack location

- **host_id**: Filter by specific host/node

- **mountpoint**: Filter by disk mount point

- **partition**: Filter by disk partition

- **Interface**: Filter by network interface

## Best Practices

**CPU Monitoring**

   - Monitor CPU usage to ensure it stays below 80% for production workloads
   - High I/O wait indicates disk bottlenecks
   - Monitor load average relative to CPU core count

**Disk Monitoring**

   - Keep disk usage below 85% to prevent performance degradation
   - Monitor IOPS and queue size for disk saturation
   - Track weighted I/O time for disk latency issues

**Memory Monitoring**

   - Monitor both system and JVM memory usage
   - Ensure adequate memory for page cache (cached memory)
   - Track JVM heap usage to prevent OutOfMemory errors

**GC Monitoring**

   - Monitor GC frequency and duration
   - Excessive GC activity indicates memory pressure
   - Different GC algorithms (G1, ZGC, Shenandoah) have different characteristics

**Network Monitoring**

   - Track network throughput for replication and client traffic
   - Monitor NTP offset to ensure time synchronization
   - High network usage may indicate replication storms

**File Descriptors**

   - Monitor file descriptor usage to prevent "too many open files" errors
   - Kafka requires many file descriptors for log segments and network connections