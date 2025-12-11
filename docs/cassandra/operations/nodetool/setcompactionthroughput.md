# nodetool setcompactionthroughput

Sets the compaction throughput limit in megabytes per second.

---

## Synopsis

```bash
nodetool [connection_options] setcompactionthroughput <throughput_mb_per_sec>
```

## Description

`nodetool setcompactionthroughput` controls how fast compaction operations can write data. Throttling compaction prevents it from consuming too much I/O and impacting production workloads.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `throughput_mb_per_sec` | Maximum MB/s for compaction writes. 0 = unlimited |

---

## Examples

### Set Throughput

```bash
# Set to 128 MB/s
nodetool setcompactionthroughput 128
```

### Unlimited Throughput

```bash
# Remove throttling
nodetool setcompactionthroughput 0
```

### Check Current Setting

```bash
nodetool getcompactionthroughput
```

---

## When to Use

### Reduce Production Impact

During peak hours, reduce compaction throughput:

```bash
nodetool setcompactionthroughput 64
```

### Speed Up Compaction

During maintenance windows, increase throughput:

```bash
nodetool setcompactionthroughput 512
```

### Compaction Falling Behind

If pending compactions are growing:

```bash
# Check current setting
nodetool getcompactionthroughput

# Increase if disk can handle it
nodetool setcompactionthroughput 256

# Monitor
nodetool compactionstats
```

---

## Recommended Values

| Environment | Throughput | Rationale |
|-------------|------------|-----------|
| HDD | 64-128 MB/s | Avoid I/O saturation |
| SSD | 256-512 MB/s | Can handle higher throughput |
| NVMe | 512+ MB/s | Very high I/O capacity |
| Peak traffic | 32-64 MB/s | Minimize production impact |
| Maintenance | 256-512+ MB/s | Clear backlog quickly |

!!! tip "Tuning Approach"
    Start conservative and increase while monitoring:

    - Disk utilization
    - Read/write latencies
    - Compaction pending count

---

## Impact

### Too Low

- Compaction backlog grows
- More SSTables accumulate
- Read performance degrades
- Disk space may fill

### Too High

- Competes with production I/O
- Increased read/write latencies
- Disk saturation

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [getcompactionthroughput](getcompactionthroughput.md) | Check current setting |
| [compactionstats](compactionstats.md) | Monitor compaction progress |
