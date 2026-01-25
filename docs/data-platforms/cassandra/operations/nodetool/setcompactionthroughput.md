---
title: "nodetool setcompactionthroughput"
description: "Set compaction throughput limit in Cassandra using nodetool setcompactionthroughput."
meta:
  - name: keywords
    content: "nodetool setcompactionthroughput, compaction throughput, throttle, Cassandra"
---

# nodetool setcompactionthroughput

Sets the total compaction throughput limit across all compaction threads on a node.

---

## Synopsis

```bash
nodetool [connection_options] setcompactionthroughput <throughput_mb_per_sec>
```

## Description

`nodetool setcompactionthroughput` controls the maximum rate at which all compaction operations combined can write data to disk. This throttle prevents compaction from consuming too much disk I/O and impacting production read/write workloads.

### Total Throughput, Not Per-Thread

!!! info "Aggregate Limit"
    The throughput limit is the **total aggregate limit across all concurrent compaction threads**, not a per-thread limit.

    For example, with `concurrent_compactors: 4` and throughput set to `128 MiB/s`:

    - All 4 compaction threads **share** the 128 MiB/s budget
    - Each thread averages approximately 32 MiB/s (128 ÷ 4)
    - The actual distribution varies based on workload

    ```
    ┌─────────────────────────────────────────────────────┐
    │              Total Throughput: 128 MiB/s             │
    ├─────────────────────────────────────────────────────┤
    │  Thread 1    Thread 2    Thread 3    Thread 4       │
    │   ~32 MiB/s    ~32 MiB/s    ~32 MiB/s    ~32 MiB/s      │
    │      ↓           ↓           ↓           ↓          │
    │  ═══════════════════════════════════════════════    │
    │                    Disk I/O                         │
    └─────────────────────────────────────────────────────┘
    ```

!!! warning "Non-Persistent Setting"
    This setting is applied at runtime only and does not persist across node restarts. After a restart, the value reverts to the `compaction_throughput` setting in `cassandra.yaml` (default: 64 MiB/s).

    To make the change permanent, update `cassandra.yaml`:

    ```yaml
    compaction_throughput: 128MiB/s
    ```

---

## Arguments

| Argument | Description |
|----------|-------------|
| `throughput_mib_per_sec` | Maximum MiB/s for all compaction writes combined. 0 = unlimited |

!!! note "cassandra.yaml Parameter"
    The corresponding cassandra.yaml parameter changed in 4.1:

    | Cassandra Version | Parameter Name | Example |
    |-------------------|----------------|---------|
    | Pre-4.1 | `compaction_throughput_mb_per_sec` | `64` |
    | 4.1+ | `compaction_throughput` | `64MiB/s` |

---

## Examples

### Set Throughput to 128 MiB/s

```bash
nodetool setcompactionthroughput 128
```

### Remove Throttling (Unlimited)

```bash
nodetool setcompactionthroughput 0
```

### Check Current Setting

```bash
nodetool getcompactionthroughput
```

---

## When to Adjust Compaction Throughput

### Scenario 1: Compaction Backlog Growing

**Symptoms:**
- `nodetool compactionstats` shows increasing pending compactions
- SSTable counts rising over time
- Read latencies gradually increasing

**Action:** Increase throughput to help compaction keep pace:

```bash
# Check current pending compactions
nodetool compactionstats

# Check current throughput
nodetool getcompactionthroughput

# Increase throughput
nodetool setcompactionthroughput 256

# Monitor progress
watch -n 10 'nodetool compactionstats'
```

### Scenario 2: Production Latencies Spiking During Compaction

**Symptoms:**
- Read/write latencies spike when compaction is active
- Disk I/O at or near 100% utilization
- Application timeouts correlate with compaction activity

**Action:** Decrease throughput to reduce I/O contention:

```bash
# Check if compaction is running
nodetool compactionstats

# Reduce throughput to ease disk pressure
nodetool setcompactionthroughput 64

# Monitor latencies
nodetool proxyhistograms
```

### Scenario 3: Maintenance Window - Clear Backlog

**Symptoms:**
- Scheduled maintenance with reduced traffic
- Need to clear compaction backlog before peak hours

**Action:** Temporarily maximize throughput:

```bash
# Remove throttle during maintenance
nodetool setcompactionthroughput 0

# Or set very high value
nodetool setcompactionthroughput 1024

# Wait for compactions to complete
watch -n 10 'nodetool compactionstats'

# Restore normal throttle before traffic returns
nodetool setcompactionthroughput 128
```

### Scenario 4: After Bulk Data Load

**Symptoms:**
- Large amount of data just loaded
- Many SSTables created, pending compaction

**Action:** Increase throughput to consolidate data faster:

```bash
# After bulk load completes
nodetool setcompactionthroughput 512

# Monitor compaction progress
nodetool compactionstats

# Once caught up, restore normal value
nodetool setcompactionthroughput 128
```

### Scenario 5: Disk Space Running Low

**Symptoms:**
- Disk usage approaching capacity
- Compaction can free space by removing tombstones/overwrites

**Action:** Increase throughput to accelerate space reclamation:

```bash
# Check disk space
df -h /var/lib/cassandra

# Increase compaction speed
nodetool setcompactionthroughput 512

# Optionally trigger compaction on specific tables
nodetool compact my_keyspace my_table
```

---

## Performance Metrics to Monitor

### Before Adjusting Throughput

Gather baseline metrics to understand current state:

```bash
#!/bin/bash
# baseline_metrics.sh - Capture before changing throughput

echo "=== Current Compaction Throughput ==="
nodetool getcompactionthroughput

echo ""
echo "=== Pending Compactions ==="
nodetool compactionstats

echo ""
echo "=== SSTable Counts (top 10 tables) ==="
nodetool tablestats | grep -E "Table:|SSTable count" | head -20

echo ""
echo "=== Disk I/O ==="
iostat -x 1 3 | tail -10

echo ""
echo "=== Read/Write Latencies ==="
nodetool proxyhistograms
```

### Key Metrics to Watch

| Metric | How to Check | What to Look For |
|--------|--------------|------------------|
| **Pending compactions** | `nodetool compactionstats` | Should decrease after increasing throughput |
| **Disk I/O utilization** | `iostat -x 1` | %util should not sustain 100% |
| **Disk I/O await** | `iostat -x 1` | await (ms) indicates I/O latency |
| **Read latency** | `nodetool proxyhistograms` | 99th percentile read latency |
| **Write latency** | `nodetool proxyhistograms` | 99th percentile write latency |
| **SSTable count** | `nodetool tablestats` | Should decrease as compaction catches up |
| **Compaction throughput** | `nodetool compactionstats` | Actual MiB/s being written |

### Monitoring During Adjustment

```bash
#!/bin/bash
# monitor_compaction.sh - Watch key metrics in real-time

while true; do
    clear
    echo "=== $(date) ==="
    echo ""

    echo "--- Compaction Status ---"
    nodetool compactionstats | head -15
    echo ""

    echo "--- Disk I/O ---"
    iostat -x 1 1 | grep -E "Device|sda|nvme" | tail -2
    echo ""

    echo "--- Recent Latencies ---"
    nodetool proxyhistograms | head -10

    sleep 10
done
```

### Warning Signs

| Observation | Problem | Action |
|-------------|---------|--------|
| Disk %util consistently 100% | I/O saturated | Decrease throughput |
| await > 20ms (SSD) or > 100ms (HDD) | I/O congestion | Decrease throughput |
| Read 99th percentile spiking | Compaction impacting reads | Decrease throughput |
| Pending compactions growing | Throughput too low | Increase throughput |
| SSTable count rising steadily | Compaction can't keep up | Increase throughput |

---

## Recommended Values by Storage Type

| Storage Type | Default | Conservative | Aggressive | Notes |
|--------------|---------|--------------|------------|-------|
| **HDD (7200 RPM)** | 64 MiB/s | 32 MiB/s | 128 MiB/s | Limited by seek time, be conservative |
| **HDD (15K RPM)** | 64 MiB/s | 48 MiB/s | 160 MiB/s | Slightly better than 7200 RPM |
| **SATA SSD** | 128 MiB/s | 64 MiB/s | 256 MiB/s | Good baseline for most SSDs |
| **NVMe SSD** | 256 MiB/s | 128 MiB/s | 512+ MiB/s | Can handle much higher throughput |
| **Cloud (EBS gp3)** | 128 MiB/s | 64 MiB/s | Provisioned IOPS | Depends on provisioned performance |
| **Cloud (local NVMe)** | 256 MiB/s | 128 MiB/s | 512+ MiB/s | Similar to on-prem NVMe |

### Tuning Approach

```bash
# 1. Start with default or conservative value
nodetool setcompactionthroughput 64

# 2. Monitor disk utilization and latencies
iostat -x 5
nodetool proxyhistograms

# 3. If disk has headroom (util < 70%), increase
nodetool setcompactionthroughput 128

# 4. Continue monitoring
# 5. If latencies spike, back off
nodetool setcompactionthroughput 96

# 6. Find the sweet spot where:
#    - Compaction keeps pace (pending not growing)
#    - Disk not saturated (util < 80%)
#    - Latencies acceptable
```

---

## Impact Analysis

### Effects of Different Throughput Settings

```
Low Throughput (32-64 MiB/s)
├── Pros
│   ├── Minimal impact on production I/O
│   ├── Stable read/write latencies
│   └── Predictable disk behavior
└── Cons
    ├── Compaction may fall behind
    ├── SSTable count grows
    ├── Read performance degrades over time
    └── Disk space may fill with uncompacted data

High Throughput (256+ MiB/s)
├── Pros
│   ├── Compaction keeps pace with writes
│   ├── Fewer SSTables, better read performance
│   └── Faster tombstone removal
└── Cons
    ├── May impact production I/O
    ├── Potential latency spikes
    └── Disk saturation risk

Unlimited (0)
├── Pros
│   ├── Maximum compaction speed
│   └── Clears backlog fastest
└── Cons
    ├── Can severely impact production
    ├── Risk of disk saturation
    └── Only safe during maintenance windows
```

### Finding the Right Balance

The optimal throughput balances:

1. **Compaction keeping pace** - Pending compactions not growing
2. **Acceptable latencies** - Production traffic not impacted
3. **Disk headroom** - I/O utilization not saturated

```bash
# Good balance indicators:
# - Pending compactions: stable or decreasing
# - Disk I/O util: 50-70%
# - Read p99: within SLA
# - Write p99: within SLA
```

---

## Concurrent Compactors Interaction

The throughput limit interacts with the number of concurrent compactors:

```yaml
# cassandra.yaml
concurrent_compactors: 4  # Number of parallel compaction threads
compaction_throughput: 128MiB/s  # Total throughput for all threads
```

| concurrent_compactors | throughput | Per-Thread Average |
|-----------------------|------------|-------------------|
| 2 | 128 MiB/s | ~64 MiB/s |
| 4 | 128 MiB/s | ~32 MiB/s |
| 8 | 128 MiB/s | ~16 MiB/s |
| 4 | 256 MiB/s | ~64 MiB/s |
| 4 | 512 MiB/s | ~128 MiB/s |

!!! tip "Balancing Threads and Throughput"
    More compactors with the same throughput means each individual compaction runs slower, but more compactions run in parallel. The total throughput remains capped.

    For CPU-bound compaction (compression), more threads can help. For I/O-bound compaction, the throughput limit is the bottleneck.

---

## Cluster-Wide Configuration

### Apply to All Nodes

```bash
#!/bin/bash
# set_compaction_throughput_cluster.sh

THROUGHPUT="${1:-128}"

# Get list of node IPs from local nodetool status
nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

echo "Setting compaction throughput to $THROUGHPUT MiB/s on all nodes..."

for node in $nodes; do
    echo -n "$node: "
    ssh "$node" 'nodetool setcompactionthroughput '"$THROUGHPUT"' && echo "set to '"$THROUGHPUT"' MiB/s" || echo "FAILED"'
done

echo ""
echo "Verification:"
for node in $nodes; do
    echo -n "$node: "
    ssh "$node" "nodetool getcompactionthroughput"
done
```

### Making Changes Permanent

```yaml
# cassandra.yaml - applies after restart
compaction_throughput: 128MiB/s
```

---

## Troubleshooting

### Throughput Seems Limited Despite High Setting

```bash
# Check actual compaction throughput in compactionstats
nodetool compactionstats
# Look for "throughput" in output

# May be limited by:
# 1. Disk I/O capacity
# 2. CPU (if heavy compression)
# 3. No compactions pending

# Check disk I/O
iostat -x 1 5
```

### Compaction Still Slow After Increasing Throughput

```bash
# Check if compactions are actually running
nodetool compactionstats

# Check if disk is the bottleneck
iostat -x 1 3

# Check if CPU is bottleneck (compression)
top -H -p $(pgrep -f CassandraDaemon)

# May need to increase concurrent_compactors instead
# (requires cassandra.yaml change and restart)
```

### Setting Reverted After Restart

```bash
# Runtime setting doesn't persist
# Check cassandra.yaml
grep compaction_throughput /etc/cassandra/cassandra.yaml

# Update for persistence
# Then restart or set runtime value
```

---

## Best Practices

!!! tip "Throughput Guidelines"

    1. **Monitor before changing** - Establish baseline metrics
    2. **Adjust incrementally** - Change by 50-100% at a time, not 10x
    3. **Watch disk I/O** - Keep utilization below 80%
    4. **Check latencies** - Ensure production traffic isn't impacted
    5. **Time it right** - Make aggressive changes during low-traffic periods
    6. **Make permanent** - Update `cassandra.yaml` after validating changes
    7. **Apply cluster-wide** - Set same value on all nodes for consistency

!!! warning "Avoid These Mistakes"

    - Setting unlimited (0) during peak traffic
    - Ignoring disk I/O metrics when increasing throughput
    - Forgetting to persist changes to `cassandra.yaml`
    - Setting different values on different nodes (causes imbalance)

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [getcompactionthroughput](getcompactionthroughput.md) | View current throughput setting |
| [compactionstats](compactionstats.md) | Monitor active and pending compactions |
| [setconcurrentcompactors](setconcurrentcompactors.md) | Adjust number of compaction threads |
| [setstreamthroughput](setstreamthroughput.md) | Control streaming throughput (different from compaction) |
| [tablestats](tablestats.md) | View SSTable counts per table |
| [proxyhistograms](proxyhistograms.md) | Check read/write latencies |
