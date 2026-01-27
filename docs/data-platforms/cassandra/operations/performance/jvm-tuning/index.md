---
title: "JVM Tuning for Cassandra"
description: "Cassandra JVM tuning guide. Garbage collection and memory optimization."
meta:
  - name: keywords
    content: "Cassandra JVM tuning, GC tuning, memory optimization"
---

# JVM Tuning for Cassandra

Optimize JVM settings for optimal Cassandra performance.

## Heap Configuration

### Sizing Guidelines

| System RAM | Heap Size | Notes |
|------------|-----------|-------|
| 8GB | 4GB | Development only |
| 32GB | 8GB | Small production |
| 64GB | 16GB | Standard production |
| 128GB+ | 31GB | Maximum recommended |

**Key Rules:**
- Never exceed 31GB (compressed oops limit)
- Leave 50%+ RAM for OS page cache
- Set `-Xms` equal to `-Xmx`

### Configuration

```bash
# jvm11-server.options or jvm17-server.options

# Heap size (adjust for your system)
-Xms16G
-Xmx16G
```

## Garbage Collection

### G1GC (Default, Recommended)

```bash
# G1GC Configuration
-XX:+UseG1GC
-XX:MaxGCPauseMillis=500
-XX:G1RSetUpdatingPauseTimePercent=5
-XX:InitiatingHeapOccupancyPercent=70
-XX:ParallelGCThreads=16
-XX:ConcGCThreads=4
-XX:+ParallelRefProcEnabled
-XX:MaxTenuringThreshold=1
-XX:G1HeapWastePercent=10
```

### ZGC (Low Latency)

```bash
# ZGC for ultra-low latency
-XX:+UseZGC

# ZGenerational is available in JDK 21+ only
# -XX:+ZGenerational

-XX:SoftMaxHeapSize=28G
-XX:ZCollectionInterval=0
```

!!! note "ZGC Version Requirements"
    - **JDK 11-16**: ZGC is experimental (`-XX:+UnlockExperimentalVMOptions` required)
    - **JDK 17-20**: ZGC is production-ready (non-generational)
    - **JDK 21+**: ZGenerational mode available via `-XX:+ZGenerational`

### Shenandoah (JDK 11+, Alternative)

```bash
# Shenandoah GC
-XX:+UseShenandoahGC
-XX:ShenandoahGCHeuristics=compact
```

## GC Logging

### JDK 11+ Format

```bash
# Comprehensive GC logging
-Xlog:gc*:file=/var/log/cassandra/gc.log:time,uptime,level,tags:filecount=10,filesize=10M
-Xlog:safepoint:file=/var/log/cassandra/safepoint.log:time,uptime:filecount=5,filesize=5M
```

## Memory Settings

### Metaspace

```bash
-XX:MetaspaceSize=128M
-XX:MaxMetaspaceSize=256M
```

### Direct Memory (Off-Heap)

```bash
# For memtable_offheap and file cache
-XX:MaxDirectMemorySize=4G
```

### Thread Stack

```bash
# Reduce stack size for many threads
-Xss256k
```

## Performance Optimizations

### String Optimization

```bash
# String deduplication (G1GC only)
-XX:+UseStringDeduplication
-XX:StringDeduplicationAgeThreshold=1
```

### Compilation

```bash
# Tiered compilation (default)
-XX:+TieredCompilation

# Code cache
-XX:ReservedCodeCacheSize=256M
-XX:+UseCodeCacheFlushing
```

### Disable Explicit GC

```bash
# Prevent application-triggered GC
-XX:+DisableExplicitGC
```

## Debugging and Monitoring

### Heap Dumps

```bash
# Automatic heap dump on OOM
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/lib/cassandra/

# Exit on OOM (let orchestrator restart)
-XX:+ExitOnOutOfMemoryError
```

### JMX (if external)

```bash
-Djava.rmi.server.hostname=<node_ip>
-Dcom.sun.management.jmxremote.port=7199
-Dcom.sun.management.jmxremote.ssl=false
-Dcom.sun.management.jmxremote.authenticate=false
```

## Complete Configuration Example

```bash
# /etc/cassandra/jvm11-server.options

#####################
# HEAP CONFIGURATION
#####################
-Xms16G
-Xmx16G

#####################
# GC CONFIGURATION
#####################
-XX:+UseG1GC
-XX:MaxGCPauseMillis=500
-XX:InitiatingHeapOccupancyPercent=70
-XX:ParallelGCThreads=16
-XX:ConcGCThreads=4
-XX:+ParallelRefProcEnabled
-XX:MaxTenuringThreshold=1
-XX:G1HeapWastePercent=10
-XX:+UseStringDeduplication

#####################
# GC LOGGING
#####################
-Xlog:gc*:file=/var/log/cassandra/gc.log:time,uptime:filecount=10,filesize=10M

#####################
# MEMORY
#####################
-XX:MetaspaceSize=128M
-XX:MaxMetaspaceSize=256M
-XX:MaxDirectMemorySize=4G
-Xss256k

#####################
# ERROR HANDLING
#####################
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/lib/cassandra/
-XX:+ExitOnOutOfMemoryError

#####################
# PERFORMANCE
#####################
-XX:+DisableExplicitGC
-XX:+AlwaysPreTouch
-XX:+UseLargePages
```

## Tuning by Workload

| Workload | Heap | GC | Key Settings |
|----------|------|-----|--------------|
| Write-heavy | 16-24GB | G1GC | Higher IHOP (75%) |
| Read-heavy | 16-31GB | G1GC | Lower pause target |
| Low latency | 16GB | ZGC | `-XX:+UseZGC` |
| Mixed | 16GB | G1GC | Default settings |

## Monitoring GC

```bash
# Check GC activity
nodetool gcstats

# Watch GC logs
tail -f /var/log/cassandra/gc.log
```

---

## Next Steps

- **[OS Tuning](../os-tuning/index.md)** - Operating system optimization
- **[Hardware](../hardware/index.md)** - Hardware recommendations
- **[JVM Options](../../configuration/jvm-options/index.md)** - Complete options reference