---
title: "nodetool getcompactionthroughput"
description: "Display compaction throughput limit in Cassandra using nodetool getcompactionthroughput."
meta:
  - name: keywords
    content: "nodetool getcompactionthroughput, compaction throughput, Cassandra performance, throttle"
---

# nodetool getcompactionthroughput

Displays the current compaction throughput limit.

---

## Synopsis

```bash
nodetool [connection_options] getcompactionthroughput [options]
```

## Options

| Option | Description |
|--------|-------------|
| `-d, --precise-mib` | Display precise MiB/s value as a decimal (avoids rounding errors when configured value is not an integer) |

## Description

`nodetool getcompactionthroughput` returns the maximum rate at which compaction operations can write data, measured in mebibytes per second (MiB/s). The output also includes current throughput metrics for the last 1/5/15 minute intervals. This throttle helps prevent compaction from consuming excessive disk I/O and impacting read/write performance.

Compaction throughput affects:

- **SSTable merge operations** - How fast SSTables are combined
- **Disk I/O utilization** - Balance between compaction and client traffic
- **Compaction backlog** - How quickly pending compactions complete
- **Read performance** - Fewer SSTables means faster reads

---

## Output

### Standard Output

```
Current compaction throughput: 64 MiB/s
throughput_1min: 45 MiB/s
throughput_5min: 52 MiB/s
throughput_15min: 48 MiB/s
```

### Output Values

| Value | Meaning |
|-------|---------|
| `64 MiB/s` | Default throughput limit |
| `0 MiB/s` | Unlimited (no throttling) |
| `16-256 MiB/s` | Typical operational range |

---

## Examples

### Basic Usage

```bash
nodetool getcompactionthroughput
```

Output:
```
Current compaction throughput: 64 MB/s
```

### Check Remote Node

```bash
ssh 192.168.1.100 "nodetool getcompactionthroughput"
```

### Cluster-Wide Check

```bash
for node in node1 node2 node3; do
    echo -n "$node: "
    ssh "$node" "nodetool getcompactionthroughput"
done
```

### Extract Value Only

```bash
nodetool getcompactionthroughput | awk '{print $4}'
```

Output:
```
64
```

---

## Understanding Compaction Throughput

### How Throttling Works

Cassandra limits the rate at which compaction writes output SSTables:

1. Compaction reads input SSTables
2. Merges and processes data in memory
3. **Writes output SSTables at throttled rate**
4. Rate is controlled by compaction throughput setting

### Impact of Different Values

| Throughput | Compaction Speed | I/O Impact | Use Case |
|------------|------------------|------------|----------|
| 16 MB/s | Very slow | Minimal | Heavy read load |
| 32 MB/s | Slow | Low | Normal production |
| 64 MB/s | Moderate | Moderate | Default/balanced |
| 128 MB/s | Fast | High | Maintenance windows |
| 256+ MB/s | Very fast | Very high | Dedicated compaction |
| 0 (unlimited) | Maximum | Maximum | Recovery/emergency |

---

## When to Use

### Routine Monitoring

Check current throughput setting:

```bash
nodetool getcompactionthroughput
```

### Before Adjusting

Verify current value before making changes:

```bash
# Check current
nodetool getcompactionthroughput

# Adjust if needed
nodetool setcompactionthroughput 128

# Verify change
nodetool getcompactionthroughput
```

### During Compaction Issues

When investigating compaction performance:

```bash
# Check throughput limit
nodetool getcompactionthroughput

# Check current compaction activity
nodetool compactionstats

# Check if throughput is the bottleneck
# (compare active rate vs configured limit)
```

### Cluster Configuration Audit

Verify consistency across nodes:

```bash
#!/bin/bash
# Check compaction throughput on all nodes

echo "=== Compaction Throughput Audit ==="
for node in $(nodetool status | grep "^UN" | awk '{print $2}'); do
    throughput=$(ssh "$node" "nodetool getcompactionthroughput 2>/dev/null | awk '{print $4}')"
    echo "$node: $throughput MB/s"
done
```

---

## Correlation with Compaction Stats

### Monitoring Actual Throughput

```bash
# Check configured limit
nodetool getcompactionthroughput

# Check actual compaction activity
nodetool compactionstats
```

Example `compactionstats` output:
```
pending tasks: 5
- system_schema.tables: 0
- my_keyspace.my_table: 5

Active compaction:
   Compacting (my_keyspace.my_table)
   Progress: 45.2% (2.3/5.1 GB)
   Throughput: 62.5 MB/s
```

If "Throughput" consistently matches the configured limit, compaction is being throttled.

### Signs Throughput is Too Low

| Indicator | Symptom |
|-----------|---------|
| Growing pending tasks | `nodetool compactionstats` shows increasing backlog |
| High SSTable count | `nodetool tablestats` shows many SSTables |
| Read latency increase | More SSTables to scan for reads |
| Disk usage growth | Uncompacted data accumulating |

### Signs Throughput is Too High

| Indicator | Symptom |
|-----------|---------|
| I/O saturation | High disk utilization (iostat) |
| Read/write latency | Client operations slowed |
| Dropped messages | `nodetool tpstats` shows drops |
| CPU pressure | Compaction using too much CPU |

---

## Default Values

### Default Value

The default compaction throughput is **64 MB/s** in Cassandra 4.x and later.

### Configuration File

The cassandra.yaml parameter name varies by version:

| Cassandra Version | Parameter Name | Example |
|-------------------|----------------|---------|
| Pre-4.1 | `compaction_throughput_mb_per_sec` | `64` |
| 4.1+ | `compaction_throughput` | `64MiB/s` |

```yaml
# cassandra.yaml (4.1+)
compaction_throughput: 64MiB/s

# cassandra.yaml (Pre-4.1)
# compaction_throughput_mb_per_sec: 64
```

---

## Comparison with Related Settings

| Setting | Purpose | Command |
|---------|---------|---------|
| Compaction throughput | SSTable write rate limit | `getcompactionthroughput` / `setcompactionthroughput` |
| Stream throughput | Node-to-node transfer rate | `getstreamthroughput` / `setstreamthroughput` |
| Concurrent compactors | Parallel compaction threads | `getconcurrentcompactors` / `setconcurrentcompactors` |

### Understanding the Relationship

```bash
# Check all compaction-related settings
echo "=== Compaction Settings ==="
echo "Throughput: $(nodetool getcompactionthroughput)"
echo "Concurrent compactors: $(nodetool getconcurrentcompactors)"
echo ""
echo "=== Current Activity ==="
nodetool compactionstats
```

Effective throughput = `throughput_per_compactor × concurrent_compactors`

---

## Tuning Guidelines

### When to Increase

- Compaction backlog growing
- Many pending compaction tasks
- During maintenance windows
- SSTable count too high

```bash
# Check current
nodetool getcompactionthroughput

# Increase for maintenance
nodetool setcompactionthroughput 128

# Monitor progress
watch nodetool compactionstats
```

### When to Decrease

- High client latencies during compaction
- I/O contention observed
- Disk utilization too high
- During peak traffic periods

```bash
# Check current
nodetool getcompactionthroughput

# Reduce to minimize impact
nodetool setcompactionthroughput 32

# Verify client latencies improve
nodetool proxyhistograms
```

---

## Monitoring Script

```bash
#!/bin/bash
# compaction_monitor.sh - Monitor compaction throughput and activity

while true; do
    clear
    echo "=== Compaction Monitor $(date) ==="
    echo ""

    # Configured limit
    echo "Configured throughput: $(nodetool getcompactionthroughput)"
    echo ""

    # Current activity
    echo "Current compaction activity:"
    nodetool compactionstats

    echo ""
    echo "Press Ctrl+C to exit"
    sleep 10
done
```

---

## Troubleshooting

### Throughput Shows 0

```bash
nodetool getcompactionthroughput
# Output: Current compaction throughput: 0 MB/s
```

This means compaction is **unlimited** (no throttling). This is intentional in some configurations but may cause I/O saturation.

```bash
# Set a reasonable limit
nodetool setcompactionthroughput 64
```

### Value Doesn't Persist After Restart

Runtime changes with `setcompactionthroughput` don't persist. Update `cassandra.yaml`:

```yaml
compaction_throughput_mb_per_sec: 64
```

### Different Values Across Nodes

```bash
# Audit cluster
for node in node1 node2 node3; do
    echo "$node: $(ssh "$node" "nodetool getcompactionthroughput | awk '{print $4}')""
done

# Output:
# node1: 64
# node2: 32  # Different!
# node3: 64

# Standardize
ssh node2 "nodetool setcompactionthroughput 64"
```

---

## Best Practices

!!! tip "Compaction Throughput Guidelines"

    1. **Monitor regularly** - Include in operational dashboards
    2. **Consistent across cluster** - Use same setting on all nodes
    3. **Adjust for workload** - Lower during peak, higher during maintenance
    4. **Balance with streaming** - Consider total I/O budget
    5. **Document changes** - Log when and why throughput was adjusted
    6. **Persist settings** - Update cassandra.yaml for permanent changes

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [setcompactionthroughput](setcompactionthroughput.md) | Modify throughput limit |
| [compactionstats](compactionstats.md) | View active compactions |
| [compactionhistory](compactionhistory.md) | View past compactions |
| [setstreamthroughput](setstreamthroughput.md) | Set streaming rate |
| [tablestats](tablestats.md) | SSTable counts per table |