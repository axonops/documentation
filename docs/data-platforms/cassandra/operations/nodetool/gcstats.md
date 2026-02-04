---
title: "nodetool gcstats"
description: "Display JVM garbage collection statistics for Cassandra using nodetool gcstats command."
meta:
  - name: keywords
    content: "nodetool gcstats, GC statistics, JVM garbage collection, Cassandra performance"
---

# nodetool gcstats

Displays garbage collection statistics for the Cassandra JVM.

---

## Synopsis

```bash
nodetool [connection_options] gcstats [options]
```
See [connection options](index.md#connection-options) for connection options.

## Options

| Option | Description |
|--------|-------------|
| `-F, --format <format>` | Output format: `json`, `yaml`, or `table` (default) |
| `-H, --human-readable` | Display sizes in human-readable format |

## Description

`nodetool gcstats` shows cumulative garbage collection metrics including:

- GC invocation counts
- Total GC time
- Time since last GC

Monitoring GC is critical as excessive garbage collection can cause latency spikes and node instability.

!!! info "JVM Metrics Source"
    These statistics are retrieved from the JVM's garbage collection MXBeans via JMX (`java.lang:type=GarbageCollector`), not from Cassandra's internal metrics. The values represent what the JVM reports about its garbage collection activity.

!!! warning "GC Elapsed Time vs Stop-the-World Pauses"
    The elapsed time values reported by `gcstats` represent the total time the garbage collector was active, which **may not directly correspond to stop-the-world (STW) pause times**:

    - **Concurrent collectors** (G1GC, ZGC, Shenandoah) perform much of their work concurrently with application threads. The elapsed time includes both concurrent phases and STW phases.
    - **Parallel collectors** (ParallelGC) are fully STW, so elapsed time equals pause time.
    - For accurate STW pause analysis, enable GC logging and use specialized GC analysis tools.

    The metrics are still valuable for identifying GC pressure trends, but should not be interpreted as exact application pause durations when using concurrent collectors.

---

## Output Example

```
       Interval (ms) Max GC Elapsed (ms)Total GC Elapsed (ms)Stdev GC Elapsed (ms)   GC Reclaimed (bytes)         GC Count   Allocated Direct Memory Bytes  Max Direct Memory Bytes  Reserved Direct Memory Bytes
                 986                 123                45678                   45              129536000             1234                        67108864                134217728                     134217728
```

---

## Output Fields

| Field | Description |
|-------|-------------|
| Interval (ms) | Time since gcstats was last called |
| Max GC Elapsed (ms) | Longest single GC pause |
| Total GC Elapsed (ms) | Cumulative GC time |
| Stdev GC Elapsed (ms) | Standard deviation of GC times |
| GC Reclaimed (bytes) | Memory reclaimed by GC (in bytes; use `-H` for human-readable units) |
| GC Count | Number of GC invocations |
| Allocated Direct Memory Bytes | Currently allocated off-heap (direct) memory |
| Max Direct Memory Bytes | Maximum off-heap memory configured |
| Reserved Direct Memory Bytes | Reserved off-heap memory |

---

## Interpreting Results

### Healthy GC

```
Max GC Elapsed (ms)Total GC Elapsed (ms)   Collections
                50                 5000          1000
```

- Max GC < 200ms: No significant pauses
- Average GC (Total/Collections) < 50ms: Normal
- GC is working efficiently

### GC Pressure Signs

```
Max GC Elapsed (ms)Total GC Elapsed (ms)   Collections
               2000               500000         50000
```

!!! danger "GC Problems"
    Warning signs:

    - Max GC > 500ms: Long stop-the-world pauses
    - High collection count: GC running frequently
    - Average GC increasing over time

### Long GC Pauses

```
Max GC Elapsed (ms): 2345
```

!!! danger "Impact of Long GC"
    GC pauses > 500ms cause:

    - Client timeouts
    - Node marked as down by gossip (if > 10s)
    - Read/write failures
    - Coordinator failovers

---

## When to Use

### Routine Monitoring

```bash
# Check GC health periodically
nodetool gcstats
```

### Investigating Latency Issues

When experiencing slow queries:

```bash
nodetool gcstats
nodetool tpstats
nodetool proxyhistograms
```

### After Heap Tuning

Verify GC behavior after JVM changes:

```bash
# Before change
nodetool gcstats > gc_before.txt

# Make JVM changes, restart

# After change
nodetool gcstats > gc_after.txt
diff gc_before.txt gc_after.txt
```

### During Load Testing

Monitor GC under stress:

```bash
watch -n 5 'nodetool gcstats'
```

---

## GC Analysis Over Time

### Comparing Intervals

```bash
# Take samples
nodetool gcstats
sleep 60
nodetool gcstats
```

The difference shows GC activity in that interval:

| Metric | Sample 1 | Sample 2 | Delta | Interpretation |
|--------|----------|----------|-------|----------------|
| Collections | 1000 | 1050 | 50 | ~1 GC/sec |
| Total GC | 5000 | 7000 | 2000ms | 2 sec GC in 60 sec |
| GC % | - | - | 3.3% | Acceptable |

### Calculating GC Overhead

```
GC overhead = (Total GC Elapsed / Node Uptime) × 100
```

| Overhead | Assessment |
|----------|------------|
| < 5% | Normal |
| 5-10% | Monitor closely |
| > 10% | Tuning needed |
| > 20% | Critical |

---

## Common GC Issues

### Frequent Full GC

High collection count with large Max GC indicates full GCs:

**Causes:**
- Heap too small
- Memory leak
- Large allocations

**Solutions:**
- Increase heap size
- Check for memory leaks
- Review workload patterns

### Long GC Pauses

**Causes:**
- Large heap with old collector
- Promotion failures
- Too many live objects

**Solutions:**
- Tune GC settings
- Use G1GC or ZGC
- Reduce object allocation rate

### Memory Not Reclaimed

Low GC Reclaimed despite high collections:

**Causes:**
- Most objects are long-lived
- Memory leak
- Off-heap pressure

**Solutions:**
- Review caching settings
- Check for leaks
- Monitor off-heap usage

---

## JVM GC Tuning

### Common Settings

```bash
# In jvm.options

# G1GC (recommended for modern Cassandra)
-XX:+UseG1GC
-XX:MaxGCPauseMillis=500
-XX:G1HeapRegionSize=16m

# Heap sizes
-Xms8G
-Xmx8G
```

### GC Logging

Enable GC logs for detailed analysis:

```bash
# jvm.options
-Xlog:gc*:file=/var/log/cassandra/gc.log:time,uptime:filecount=10,filesize=10M
```

### Analyzing GC Logs

Use tools like:
- GCViewer
- GCEasy
- VisualVM

---

## Correlation with Other Metrics

### GC and Thread Pools

```bash
nodetool gcstats
nodetool tpstats
```

High GC often correlates with:
- Blocked threads
- Pending tasks
- Dropped messages

### GC and Latency

```bash
nodetool gcstats
nodetool proxyhistograms
```

GC pauses directly impact p99 latencies.

### GC and Heap

```bash
nodetool gcstats
nodetool info | grep "Heap Memory"
```

Near-full heap triggers more frequent GC.

---

## Examples

### Basic Check

```bash
nodetool gcstats
```

### Monitor Continuously

```bash
watch -n 10 'nodetool gcstats'
```

### Compare Across Nodes

```bash
for node in node1 node2 node3; do
    echo "=== $node ==="
    ssh "$node" "nodetool gcstats"
done
```

### Alert on High GC

```bash
#!/bin/bash
max_gc=$(nodetool gcstats | tail -1 | awk '{print $2}')
if [ "$max_gc" -gt 1000 ]; then
    echo "WARNING: Max GC pause ${max_gc}ms exceeds threshold"
fi
```

---

## Best Practices

!!! tip "GC Monitoring Guidelines"
    1. **Baseline normal GC** - Know what healthy looks like
    2. **Monitor continuously** - Include in alerting
    3. **Enable GC logging** - Essential for troubleshooting
    4. **Correlate with latency** - GC often explains spikes
    5. **Right-size heap** - Not too big, not too small
    6. **Use modern GC** - G1GC or better for large heaps

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [info](info.md) | Heap memory usage |
| [tpstats](tpstats.md) | Thread pool status |
| [proxyhistograms](proxyhistograms.md) | Latency histograms |
| [tablestats](tablestats.md) | Table metrics |