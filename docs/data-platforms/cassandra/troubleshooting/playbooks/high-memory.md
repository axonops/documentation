---
title: "Cassandra High Memory Usage"
description: "High memory troubleshooting playbook. Debug memory pressure issues."
meta:
  - name: keywords
    content: "high memory troubleshooting, memory issues, heap pressure"
search:
  boost: 3
---

# High Memory Usage

High memory usage can lead to OOM kills, long GC pauses, and degraded performance. This playbook covers diagnosis and resolution of memory-related issues.

---

## Symptoms

- OOM (OutOfMemoryError) in logs
- Process killed by Linux OOM killer (`dmesg | grep -i killed`)
- Long GC pauses (see [GC Pause Issues](gc-pause.md))
- Swap usage increasing
- Cassandra process consuming more than expected memory
- Slow queries during high memory periods

---

## Diagnosis

### Step 1: Check Current Memory Usage

```bash
# Heap usage
nodetool info | grep -i heap

# Process memory
ps aux | grep cassandra

# System memory
free -h
```

### Step 2: Check for OOM Events

```bash
# Linux OOM killer
dmesg | grep -i "killed process\|oom"

# Cassandra OOM errors
grep -i "outofmemory\|heap space" /var/log/cassandra/system.log
```

### Step 3: Analyze Memory Breakdown

```bash
# GC stats
nodetool gcstats

# Check off-heap usage (bloom filters, compression metadata)
nodetool info | grep -i "off.heap\|bloom\|compression"
```

### Step 4: Check for Memory-Intensive Operations

```bash
# Large partitions being read
grep -i "large partition" /var/log/cassandra/system.log | tail -20

# Compaction activity
nodetool compactionstats

# Streaming activity
nodetool netstats
```

### Step 5: Analyze Heap Dump (if available)

```bash
# Generate heap dump
jmap -dump:format=b,file=/tmp/heap.hprof $(pgrep -f CassandraDaemon)

# Analyze with tools like Eclipse MAT or jhat
```

---

## Resolution

### Immediate: Reduce Memory Pressure

```bash
# Clear caches
nodetool invalidatekeycache
nodetool invalidaterowcache

# Reduce concurrent operations
nodetool setconcurrency read 16
nodetool setconcurrency write 16

# Trigger GC
nodetool gcstats  # Shows GC activity
```

### Short-term: Adjust Memory Settings

**Right-size heap:**

```bash
# In jvm.options
# Generally 8GB max for most workloads
-Xms8G
-Xmx8G
```

**Tune GC:**

```bash
# For G1GC
-XX:+UseG1GC
-XX:MaxGCPauseMillis=300
-XX:G1HeapRegionSize=16m
```

### Medium-term: Address Root Causes

**Cause 1: Large partitions**

See [Large Partition Issues](large-partition.md).

```bash
# Find large partitions
grep "large partition" /var/log/cassandra/system.log
nodetool tablestats my_keyspace | grep -i partition
```

**Cause 2: Too many SSTables**

```bash
# Check SSTable counts
nodetool tablestats my_keyspace | grep -E "Table:|SSTable count"

# Run compaction if needed
nodetool compact my_keyspace my_table
```

**Cause 3: Row cache enabled**

```bash
# Check row cache
nodetool info | grep -i "row cache"

# Disable if causing issues
ALTER TABLE my_table WITH caching = {'keys': 'ALL', 'rows_per_partition': 'NONE'};
```

**Cause 4: Bloom filter memory**

```bash
# Check bloom filter size
nodetool tablestats my_keyspace | grep -i "bloom"

# Adjust bloom filter FP chance (higher = less memory)
ALTER TABLE my_table WITH bloom_filter_fp_chance = 0.1;
```

**Cause 5: Concurrent repairs/streaming**

```bash
# Check active streams
nodetool netstats

# Reduce concurrent repairs
nodetool repair_admin cancel --force
```

### Long-term: Capacity Planning

**Calculate required memory:**

```
Total memory needed =
  JVM Heap (8-16GB)
  + Off-heap structures (~1-4GB depending on data size)
  + OS page cache (remaining available RAM)
  + OS overhead (~1GB)
```

**Right-size the node:**

| Data per node | Recommended RAM |
|---------------|-----------------|
| < 500 GB | 16 GB |
| 500 GB - 1 TB | 32 GB |
| 1 TB - 2 TB | 64 GB |
| > 2 TB | 64 GB + add nodes |

---

## Recovery

### After OOM

```bash
# Check if node is running
systemctl status cassandra

# If down, start it
sudo systemctl start cassandra

# Monitor startup
tail -f /var/log/cassandra/system.log

# Verify node rejoined cluster
nodetool status
```

### Verify Memory Stability

```bash
# Monitor heap usage
watch -n 10 'nodetool info | grep -i heap'

# Watch for GC issues
watch -n 30 'nodetool gcstats'
```

---

## Memory Configuration Reference

### JVM Heap Settings

```bash
# jvm.options
-Xms8G                    # Initial heap
-Xmx8G                    # Maximum heap (should equal -Xms)
-XX:+AlwaysPreTouch       # Pre-touch heap pages
```

### Off-Heap Settings

```yaml
# cassandra.yaml
# Memtable space
memtable_heap_space_in_mb: 2048
memtable_offheap_space_in_mb: 2048

# Native transport
native_transport_max_concurrent_connections: 128
```

### Memory Guidelines

| Component | Typical Size | Notes |
|-----------|--------------|-------|
| Heap | 8 GB | Rarely benefit from > 16 GB |
| Memtables | 2-4 GB | Configured in cassandra.yaml |
| Bloom filters | Varies | ~1.25 bytes per key |
| Compression metadata | Varies | ~60 bytes per 64KB chunk |
| Page cache | Remaining RAM | OS managed |

---

## Prevention

1. **Monitor heap usage** - Alert at 75% utilization
2. **Set heap limits** - Don't let JVM grow unbounded
3. **Avoid large partitions** - Design for bounded partition sizes
4. **Disable row cache** - Unless specific use case requires it
5. **Regular compaction** - Reduce SSTable overhead
6. **Capacity planning** - Add nodes before memory becomes critical

---

## Related Commands

| Command | Purpose |
|---------|---------|
| `nodetool info` | Memory usage overview |
| `nodetool gcstats` | GC statistics |
| `nodetool tablestats` | Per-table memory usage |
| `nodetool invalidatekeycache` | Clear key cache |
| `nodetool invalidaterowcache` | Clear row cache |

## Related Documentation

- [GC Pause Issues](gc-pause.md) - GC-related problems
- [Large Partition Issues](large-partition.md) - Partition size problems
- [JVM Options](../../operations/configuration/jvm-options/index.md) - JVM tuning
