---
title: "Cassandra and Java Virtual Machine (JVM)"
description: "JVM configuration for Cassandra. Heap sizing, garbage collection tuning, and G1GC settings."
meta:
  - name: keywords
    content: "Cassandra JVM, heap size, garbage collection, G1GC, JVM tuning"
---

# Java Virtual Machine (JVM)

Cassandra is written in Java and runs on the Java Virtual Machine (JVM). The JVM provides automatic memory management through garbage collection (GC), which periodically reclaims memory from unused objects. Understanding JVM behavior is essential for operating Cassandra effectively.

---

## Evolution of Java Garbage Collection

Garbage collection has been both a strength and a challenge for Java applications like Cassandra. Understanding this history explains why GC tuning has historically been critical for Cassandra operations—and why modern GCs are changing this.

### The Stop-The-World Problem

All traditional garbage collectors require **stop-the-world (STW) pauses**—moments when all application threads freeze while the GC performs certain operations. For databases, these pauses directly impact:

- Query latency (p99 spikes during GC)
- Coordinator timeouts (nodes appearing unresponsive)
- Cluster stability (gossip failures during long pauses)

### CMS: The First Low-Pause Collector (JDK 1.4, 2002)

The **Concurrent Mark-Sweep (CMS)** collector was Java's first attempt at reducing pause times. CMS performed most of its work concurrently with application threads, but still required STW pauses for initial marking and final remarking.

CMS was the recommended collector for Cassandra for many years, but had significant drawbacks:

- **Fragmentation**: CMS did not compact memory, leading to fragmentation over time
- **Concurrent mode failure**: If allocation outpaced collection, a full STW collection occurred
- **Tuning complexity**: Required careful tuning of dozens of parameters
- **Deprecated**: Removed in JDK 14

```bash
# Historical CMS configuration (do not use)
# -XX:+UseConcMarkSweepGC
# -XX:+CMSParallelRemarkEnabled
# -XX:CMSInitiatingOccupancyFraction=75
```

!!! warning "CMS is Deprecated"
    CMS was deprecated in JDK 9 and removed in JDK 14. Do not use CMS for new deployments.

### G1: The Balanced Approach (JDK 7, 2011)

**G1 (Garbage First)** replaced CMS as the default collector in JDK 9. G1 divides the heap into regions and prioritizes collecting regions with the most garbage, aiming to meet a configurable pause time target.

G1 improvements over CMS:

- **Compaction**: Eliminates fragmentation
- **Predictable pauses**: Targets a maximum pause time (`-XX:MaxGCPauseMillis`)
- **Self-tuning**: Requires less manual configuration
- **No concurrent mode failure**: Degrades gracefully under pressure

However, G1 still has STW pauses that scale with heap size and object graph complexity—typically 50-500ms for Cassandra workloads.

### Modern Era: Sub-Millisecond Pauses (2017+)

The latest generation of garbage collectors achieves pause times in the low single-digit milliseconds regardless of heap size, effectively eliminating GC as an operational concern.

**Shenandoah** (Red Hat, 2017)

- Concurrent compaction eliminates long STW pauses
- Pause times typically 1-5ms
- Backported to JDK 8 and 11 in OpenJDK distributions
- Production-proven with Cassandra workloads

**ZGC** (Oracle, 2018)

- Sub-millisecond pauses (< 1ms target)
- Designed for very large heaps (multi-terabyte)
- Production-ready in JDK 15+

### The Future: Generational Mode

Generational garbage collection separates objects by age:

- **Young generation**: Newly allocated objects (most die quickly)
- **Old generation**: Long-lived objects

This allows the collector to focus on the young generation where most garbage is created, improving overall efficiency.

**Generational ZGC** (JDK 21+, production-ready)

```bash
# JDK 21+ Generational ZGC
-XX:+UseZGC
-XX:+ZGenerational
```

**Generational Shenandoah** (JDK 25+, production-ready)

Generational Shenandoah was experimental in JDK 21-24 and became a production feature in JDK 25 (September 2025).

```bash
# JDK 25+ Generational Shenandoah
-XX:+UseShenandoahGC
-XX:ShenandoahGCMode=generational
```

!!! warning "JDK 21+ Support"
    JDK 21+ support depends on Cassandra version. Check the release notes for the target Cassandra version. JDK 21 support is tracked in [CASSANDRA-18831](https://issues.apache.org/jira/browse/CASSANDRA-18831).

### Timeline Summary

| Year | Collector | Typical Pause | Key Innovation |
|------|-----------|---------------|----------------|
| 2002 | CMS | 100-500ms | Concurrent marking |
| 2011 | G1 | 50-500ms | Region-based, predictable pauses |
| 2017 | Shenandoah | 1-5ms | Concurrent compaction |
| 2018 | ZGC | < 1ms | Colored pointers, load barriers |
| 2023 | Generational ZGC (JDK 21) | < 1ms | Generational + concurrent compaction |
| 2025 | Generational Shenandoah (JDK 25) | < 1ms | Generational + concurrent compaction |

*Note: Timeline shows JDK release years. Availability for Cassandra depends on Cassandra's JDK support.*

---

## JVM Requirements

| Cassandra Version | Supported JDK | Recommended |
|-------------------|---------------|-------------|
| 4.0 | JDK 8, 11 | JDK 11 |
| 4.1 | JDK 8, 11, 17 | JDK 11 or 17 |
| 5.0 | JDK 11, 17 | JDK 17 |

!!! tip "Use Latest Patch Version"
    Always use the latest patch version of the chosen JDK for security updates and bug fixes.

---

## JDK Distributions

Several JDK distributions are available, all based on OpenJDK. The choice depends on support requirements, licensing, and specific features like garbage collectors.

| Distribution | Vendor | License | Shenandoah | Notes |
|--------------|--------|---------|------------|-------|
| [OpenJDK](https://openjdk.org/) | Oracle/Community | GPL v2 | JDK 12+ | Reference implementation |
| [Eclipse Temurin](https://adoptium.net/) | Adoptium | GPL v2 | JDK 17+ | Formerly AdoptOpenJDK; widely used |
| [Amazon Corretto](https://aws.amazon.com/corretto/) | Amazon | GPL v2 | Verify per version | Long-term support; production-tested at Amazon |
| [Azul Zulu](https://www.azul.com/downloads/) | Azul | GPL v2 | Verify per version | Free community and paid enterprise editions |
| [Red Hat OpenJDK](https://developers.redhat.com/products/openjdk/download) | Red Hat | GPL v2 | JDK 8+ | Shenandoah backported to JDK 8 |
| [Oracle JDK](https://www.oracle.com/java/technologies/downloads/) | Oracle | Commercial | No | Requires license for production use |
| [GraalVM](https://www.graalvm.org/) | Oracle | GPL v2 / Commercial | No | Not recommended for Cassandra |

### Recommended Distributions

For Cassandra production deployments:

**Eclipse Temurin** (Adoptium)

- Community-driven, well-tested builds
- Available for all major platforms
- [https://adoptium.net/](https://adoptium.net/)

**Amazon Corretto**

- Battle-tested at Amazon scale
- Long-term support with security patches
- Shenandoah included in JDK 11+
- [https://aws.amazon.com/corretto/](https://aws.amazon.com/corretto/)

**Azul Zulu**

- Free Community edition with TCK-verified builds
- Enterprise edition available with support
- Shenandoah included in JDK 11+
- [https://www.azul.com/downloads/](https://www.azul.com/downloads/)

!!! note "Shenandoah Availability"
    Shenandoah GC is not included in all JDK distributions. If low-latency GC is required, verify Shenandoah support before selecting a distribution. Amazon Corretto, Azul Zulu, and Red Hat OpenJDK all include Shenandoah in their JDK 11 builds.

---

## Garbage Collection

The garbage collector (GC) automatically frees memory by identifying and removing objects that are no longer referenced. During GC cycles, application threads pause briefly—these **GC pauses** directly impact query latency.

### GC Pause Impact

| Heap Size | GC Frequency | GC Pause Duration | Impact |
|-----------|--------------|-------------------|--------|
| Small (4-8GB) | More frequent | Shorter pauses (workload-dependent) | Lower p99 latency |
| Medium (16-24GB) | Moderate | Moderate pauses (workload-dependent) | Balanced |
| Large (>24GB) | Less frequent | Longer pauses (workload-dependent) | Higher p99 latency spikes |

*Note: Actual pause durations vary significantly based on workload, object allocation patterns, and GC configuration.*

### G1 Garbage Collector

Cassandra uses the **G1 (Garbage First)** garbage collector by default. G1 divides the heap into regions and collects the regions with the most garbage first, aiming to limit pause times while maintaining throughput.

**G1 Configuration:**

```bash
# jvm-server.options

# Enable G1 (default in modern JDKs)
-XX:+UseG1GC

# Target maximum GC pause time
-XX:MaxGCPauseMillis=500

# G1 region size (auto-calculated if not set)
# -XX:G1HeapRegionSize=16m
```

### ZGC

**ZGC** is a low-latency garbage collector with pause times typically under 1ms regardless of heap size. It is available in JDK 15+ (production-ready) and experimentally in JDK 11-14.

```bash
# jvm-server.options

# Enable ZGC (JDK 15+)
-XX:+UseZGC

# ZGC works well with larger heaps
-Xms32G
-Xmx32G
```

!!! warning "Limited Production Evidence"
    While ZGC performs well in benchmarks, there is limited production evidence specific to Cassandra workloads compared to G1 and Shenandoah. Thorough testing in non-production environments is recommended before deployment.

### Shenandoah

**Shenandoah** is a low-pause garbage collector developed by Red Hat that performs concurrent compaction, reducing GC pause times to low single-digit milliseconds regardless of heap size. This effectively eliminates the GC pause issues that historically plagued large-heap Java applications.

Shenandoah is available in:
- OpenJDK 12+ (standard)
- OpenJDK 11 (backport in most distributions)
- OpenJDK 8 (backport in Red Hat and Amazon Corretto builds)

```bash
# jvm-server.options

# Enable Shenandoah
-XX:+UseShenandoahGC

# Optional: tune for ultra-low pause (may reduce throughput)
-XX:ShenandoahGCHeuristics=compact
```

!!! tip "Shenandoah for Cassandra"
    Shenandoah is particularly well-suited for Cassandra workloads because:

    - **Predictable latency**: Pause times typically 1-5ms, eliminating p99 latency spikes from GC
    - **Large heap friendly**: No penalty for heaps >31GB (though CompressedOops limit still applies)
    - **Write-heavy workloads**: Concurrent collection handles high allocation rates well
    - **Wide availability**: Backported to JDK 11 and 8, unlike ZGC

### GC Comparison

| Collector | Typical Pause | Throughput | CPU Overhead | Production Evidence |
|-----------|---------------|------------|--------------|---------------------|
| **G1** | 50-500ms | High | Low | Extensive |
| **Shenandoah** | 1-5ms | Medium-High | Medium | Good (OpenJDK users) |
| **ZGC** | < 1ms | Medium-High | Medium | Limited for Cassandra |

**When to use each:**

- **G1**: Default choice, well-proven, good balance of throughput and latency
- **Shenandoah**: Recommended for low latency needs, proven in production, available on JDK 11+
- **ZGC**: Experimental for Cassandra; test thoroughly before production use

!!! note "Low-Latency GC Trade-offs"
    Both ZGC and Shenandoah achieve low pause times by performing more work concurrently with application threads. This requires:

    - ~10-15% more CPU for GC work
    - ~3-5% more memory overhead
    - Slightly lower peak throughput than G1

    For most Cassandra deployments, the latency improvements far outweigh these costs.

---

## Heap Sizing

### Sizing Guidelines

| Server RAM | Recommended Heap | Rationale |
|------------|------------------|-----------|
| 16GB | 4-8GB | Small deployments |
| 32GB | 8-16GB | Standard production |
| 64GB | 16-24GB | Large deployments |
| 128GB+ | 24-31GB | Maximum practical heap |

!!! warning "31GB Limit"
    Do not exceed 31GB heap. Beyond this threshold, the JVM cannot use compressed ordinary object pointers (CompressedOops), effectively wasting ~4GB of addressable memory. A 31GB heap often outperforms a 48GB heap.

### Configuration

```bash
# jvm-server.options

# Set heap size (min = max for predictable behavior)
-Xms24G
-Xmx24G
```

Setting `-Xms` equal to `-Xmx` prevents heap resizing during operation, which can cause latency spikes.

### Young Generation Sizing

The young generation holds newly created objects. For Cassandra workloads:

```bash
# jvm-server.options

# Young generation size (G1 typically auto-tunes this well)
# Only set if experiencing issues
# -Xmn8G

# G1: target young gen size as percentage of heap
# -XX:G1NewSizePercent=20
# -XX:G1MaxNewSizePercent=30
```

---

## JVM Options Files

Cassandra uses separate JVM options files for different environments:

| File | Purpose |
|------|---------|
| `jvm-server.options` | Production server settings |
| `jvm11-server.options` | JDK 11-specific options |
| `jvm17-server.options` | JDK 17-specific options |
| `jvm-clients.options` | Client tools (nodetool, cqlsh) |

Location: `$CASSANDRA_HOME/conf/` or `/etc/cassandra/`

### Common JVM Options

```bash
# jvm-server.options

# Heap settings
-Xms24G
-Xmx24G

# GC settings
-XX:+UseG1GC
-XX:MaxGCPauseMillis=500

# GC logging (JDK 11+)
-Xlog:gc*:file=/var/log/cassandra/gc.log:time,uptime,level,tags:filecount=10,filesize=100M

# Out of memory handling
-XX:+ExitOnOutOfMemoryError
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/lib/cassandra/java_pid.hprof

# Performance
-XX:+AlwaysPreTouch
-XX:-UseBiasedLocking
```

---

## GC Logging and Analysis

### Enable GC Logging

```bash
# jvm-server.options (JDK 11+)
-Xlog:gc*:file=/var/log/cassandra/gc.log:time,uptime,level,tags:filecount=10,filesize=100M
```

### Analyze GC Logs

```bash
# Check GC pause times
grep "pause" /var/log/cassandra/gc.log

# Using Cassandra's nodetool
nodetool gcstats
```

### Key Metrics to Monitor

| Metric | Healthy Range | Action if Exceeded |
|--------|---------------|-------------------|
| GC pause time | < 500ms | Reduce heap or tune GC |
| GC frequency | < 1/minute for full GC | Check for memory leaks |
| Heap after GC | < 70% of max | Increase heap if growing |
| Allocation rate | Stable | Investigate if spiking |

---

## Troubleshooting

### Long GC Pauses

**Symptoms:**
- Query timeouts
- High p99 latency
- "GC pause" warnings in logs

**Solutions:**

1. Switch to a low-latency GC (Shenandoah or ZGC)
2. Reduce heap size (counterintuitive but often effective with G1)
3. Move memtables off-heap (see [Memory Management](memory.md))
4. Tune G1 settings:
   ```bash
   -XX:MaxGCPauseMillis=300
   -XX:G1HeapRegionSize=16m
   ```

!!! tip "Recommended: Shenandoah"
    If experiencing GC pause issues, switching to Shenandoah often provides immediate relief without extensive tuning. Shenandoah is available on OpenJDK 11+ and has proven effective for Cassandra workloads.

### OutOfMemoryError

**Symptoms:**
- Node crashes with OOM
- "java.lang.OutOfMemoryError" in logs

**Solutions:**

1. Increase heap (up to 31GB)
2. Reduce number of tables
3. Move data structures off-heap
4. Check for memory leaks with heap dump analysis

```bash
# Analyze heap dump
jmap -histo:live <pid> | head -20
```

### High CPU from GC

**Symptoms:**
- High system CPU usage
- Frequent GC cycles
- Low throughput

**Solutions:**

1. Increase heap to reduce GC frequency
2. Check for excessive object allocation (profiling)
3. Tune young generation size

---

## Best Practices

### Production Settings

```bash
# jvm-server.options

# Heap
-Xms24G
-Xmx24G

# G1 GC
-XX:+UseG1GC
-XX:MaxGCPauseMillis=500
-XX:+ParallelRefProcEnabled

# Performance
-XX:+AlwaysPreTouch
-XX:-UseBiasedLocking
-XX:+UseStringDeduplication

# Crash handling
-XX:+ExitOnOutOfMemoryError
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/lib/cassandra/

# GC logging
-Xlog:gc*:file=/var/log/cassandra/gc.log:time,uptime,level,tags:filecount=10,filesize=100M
```

### Do Not

- Set heap > 31GB
- Use CMS garbage collector (deprecated)
- Disable compressed oops manually
- Run without GC logging in production

---

## Related Documentation

- **[Memory Management](memory.md)** - Cassandra memory structures
- **[Storage Engine Overview](../storage-engine/index.md)** - Architecture overview
