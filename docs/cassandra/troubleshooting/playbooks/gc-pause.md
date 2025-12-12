---
description: "GC pause troubleshooting playbook. Diagnose garbage collection issues."
meta:
  - name: keywords
    content: "GC pause troubleshooting, garbage collection, JVM GC issues"
---

# GC Pause Issues

Long garbage collection pauses cause application stalls, timeouts, and can trigger node failures in extreme cases.

---

## Symptoms

- Application timeouts correlating with GC events
- "GC pause" warnings in Cassandra logs (> 200ms)
- Nodes marked DOWN intermittently
- Spiky latency patterns
- `nodetool tpstats` showing dropped messages

---

## Diagnosis

### Step 1: Check GC Statistics

```bash
nodetool gcstats
```

**Healthy output:**
```
Interval (ms)  Max GC Elapsed (ms)  Total GC Elapsed (ms)  Stdev GC Elapsed (ms)  GC Reclaimed (MB)  Collections  Direct Memory Bytes
      1053721                   45                    892                      12              15234          123           104857600
```

**Problem indicators:**
- Max GC Elapsed > 500ms
- Many collections with high elapsed time

### Step 2: Analyze GC Logs

```bash
# Find long pauses
grep "GC pause" /var/log/cassandra/gc.log | awk '$NF > 500 {print}' | tail -20

# Or for G1GC
grep "Pause" /var/log/cassandra/gc.log | tail -50
```

### Step 3: Check Heap Usage

```bash
nodetool info | grep -i heap
```

**Problem indicators:**
- Used heap consistently > 75% of max
- Heap usage approaching max

### Step 4: Correlate with Cassandra Logs

```bash
# Find GC-related warnings
grep -i "gc\|pause\|heap" /var/log/cassandra/system.log | tail -50
```

### Step 5: Check for Large Partitions

```bash
# Large partitions cause heap pressure during reads
nodetool tablestats my_keyspace | grep -E "Table:|partition size"
```

---

## Resolution

### Immediate: Reduce Heap Pressure

```bash
# Clear key cache if very large
nodetool invalidatekeycache

# Reduce concurrent reads/writes temporarily
nodetool setconcurrency read 16
nodetool setconcurrency write 16
```

### Short-term: Tune GC Settings

**For G1GC (recommended for heaps > 8GB):**

```bash
# In jvm.options or jvm11-server.options
-XX:+UseG1GC
-XX:G1HeapRegionSize=16m
-XX:MaxGCPauseMillis=300
-XX:InitiatingHeapOccupancyPercent=45
-XX:ParallelGCThreads=8
-XX:ConcGCThreads=4
```

**For CMS (legacy, heaps < 8GB):**

```bash
-XX:+UseConcMarkSweepGC
-XX:+CMSParallelRemarkEnabled
-XX:CMSInitiatingOccupancyFraction=75
-XX:+UseCMSInitiatingOccupancyOnly
```

### Medium-term: Adjust Heap Size

**Rule of thumb:**
- Maximum heap: 8GB for most workloads
- Heap > 16GB often increases GC pauses
- Leave room for off-heap (page cache, bloom filters)

```bash
# In jvm.options
-Xms8G
-Xmx8G
```

!!! info "Heap Sizing"
    Larger heaps don't always improve performance. Cassandra uses off-heap memory for many structures. 8GB is often optimal.

### Long-term: Address Root Causes

**Cause 1: Large partitions**

```bash
# Find large partitions
nodetool tablestats my_keyspace | grep -E "Compacted partition maximum bytes"
```

Fix: Redesign data model to limit partition size to < 100MB.

**Cause 2: Wide rows with many columns**

Fix: Limit columns per row, consider separate tables.

**Cause 3: Heavy read/write load**

Fix: Add nodes, optimize queries, implement caching.

**Cause 4: Tombstone scans**

```bash
nodetool tablestats my_keyspace | grep tombstone
```

Fix: See [Tombstone Accumulation](tombstone-accumulation.md) playbook.

---

## Recovery

### Verify GC Improvement

```bash
# Monitor GC stats
watch -n 10 'nodetool gcstats'

# Check for reduced pause times
grep "Pause" /var/log/cassandra/gc.log | tail -20
```

### Monitor Application Impact

- Check client-side latencies
- Verify no dropped messages: `nodetool tpstats | grep -i dropped`
- Confirm node stability: `nodetool status`

---

## GC Tuning Reference

### G1GC Options

| Option | Default | Recommended | Purpose |
|--------|---------|-------------|---------|
| `G1HeapRegionSize` | Auto | 16m | Region size for G1 |
| `MaxGCPauseMillis` | 200 | 300 | Target max pause |
| `InitiatingHeapOccupancyPercent` | 45 | 45-65 | When to start concurrent GC |
| `ParallelGCThreads` | cores | cores | Parallel GC threads |
| `ConcGCThreads` | cores/4 | cores/4 | Concurrent GC threads |

### Heap Size Guidelines

| Workload | Recommended Heap | Notes |
|----------|------------------|-------|
| Light (< 100 GB data) | 4-8 GB | Smaller heap = faster GC |
| Medium (100-500 GB) | 8 GB | Sweet spot for most |
| Heavy (> 500 GB) | 8-16 GB | Consider more nodes instead |
| Very large partitions | 16-31 GB | Fix data model if possible |

---

## Prevention

1. **Monitor GC metrics** - Alert on pauses > 500ms
2. **Limit partition sizes** - Design for < 100MB per partition
3. **Run repairs** - Enables tombstone cleanup
4. **Avoid heap > 16GB** - Diminishing returns
5. **Use G1GC** - Better pause time control
6. **Profile workloads** - Identify memory-intensive operations

---

## Related Commands

| Command | Purpose |
|---------|---------|
| `nodetool gcstats` | GC statistics |
| `nodetool info` | Heap usage |
| `nodetool tablestats` | Table metrics including partition sizes |
| `nodetool tpstats` | Thread pool and dropped messages |

## Related Documentation

- [JVM Options](../../operations/configuration/jvm-options/index.md) - JVM configuration
- [Performance Tuning](../../operations/performance/index.md) - Performance optimization
- [Large Partition Issues](large-partition.md) - Handling large partitions
