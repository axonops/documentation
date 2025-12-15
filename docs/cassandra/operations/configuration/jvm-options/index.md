---
title: "Cassandra JVM Options"
description: "Cassandra JVM options configuration. Heap size, GC settings, and performance tuning."
meta:
  - name: keywords
    content: "Cassandra JVM options, heap size, garbage collection, JVM tuning"
---

# Cassandra JVM Options

Configure JVM settings for optimal Cassandra performance.

## Configuration Files

| JDK Version | File |
|-------------|------|
| JDK 11+ | `jvm11-server.options` |
| JDK 17+ | `jvm17-server.options` |

Location: `/etc/cassandra/`

## Heap Configuration

```bash
# jvm11-server.options

# Set heap size (same for min and max)
-Xms16G
-Xmx16G

# Guidelines:
# - Max 31GB (compressed oops)
# - 1/4 of total RAM typically
# - Leave room for OS page cache
```

### Heap Sizing Guidelines

| RAM | Heap Size | Notes |
|-----|-----------|-------|
| 8GB | 4GB | Development |
| 32GB | 8GB | Small production |
| 64GB | 16GB | Standard production |
| 128GB+ | 31GB | Max recommended |

## Garbage Collection

### G1GC (Recommended)

```bash
-XX:+UseG1GC
-XX:MaxGCPauseMillis=500
-XX:InitiatingHeapOccupancyPercent=70
-XX:ParallelGCThreads=16
-XX:ConcGCThreads=4
-XX:+ParallelRefProcEnabled
```

### ZGC (JDK 17+)

```bash
-XX:+UseZGC
-XX:+ZGenerational
-XX:SoftMaxHeapSize=28G
```

## GC Logging

```bash
# JDK 11+
-Xlog:gc*:file=/var/log/cassandra/gc.log:time,uptime:filecount=10,filesize=10M
```

## Memory Settings

```bash
# Metaspace
-XX:MetaspaceSize=128M
-XX:MaxMetaspaceSize=256M

# Direct memory (off-heap)
-XX:MaxDirectMemorySize=4G

# String deduplication
-XX:+UseStringDeduplication
```

## Performance Options

```bash
# Disable explicit GC calls
-XX:+DisableExplicitGC

# Large pages (if enabled in OS)
-XX:+UseLargePages

# Thread stack size
-Xss256k
```

## Debug Options

```bash
# Heap dump on OOM
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/lib/cassandra/

# Print GC details (JDK 8 style for reference)
# Deprecated in JDK 11+, use Xlog instead
```

## Complete Example

```bash
# /etc/cassandra/jvm11-server.options

# Heap
-Xms16G
-Xmx16G

# GC
-XX:+UseG1GC
-XX:MaxGCPauseMillis=500
-XX:InitiatingHeapOccupancyPercent=70

# GC Logging
-Xlog:gc*:file=/var/log/cassandra/gc.log:time,uptime:filecount=10,filesize=10M

# Metaspace
-XX:MetaspaceSize=128M
-XX:MaxMetaspaceSize=256M

# Error handling
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/lib/cassandra/

# Performance
-XX:+DisableExplicitGC
-XX:+UseStringDeduplication
```

---

## Next Steps

- **[cassandra.yaml](../cassandra-yaml/index.md)** - Main configuration
- **[Performance Tuning](../../performance/index.md)** - Optimization
- **[Monitoring](../../monitoring/index.md)** - JVM monitoring
