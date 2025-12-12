---
description: "Display number of concurrent compaction threads in Cassandra using nodetool getconcurrentcompactors."
meta:
  - name: keywords
    content: "nodetool getconcurrentcompactors, compaction threads, concurrent compaction, Cassandra"
---

# nodetool getconcurrentcompactors

Displays the number of concurrent compactor threads.

---

## Synopsis

```bash
nodetool [connection_options] getconcurrentcompactors
```

---

## Description

`nodetool getconcurrentcompactors` shows the current number of threads available for concurrent compaction operations. Each compactor thread can process one compaction task at a time, allowing multiple compactions to run in parallel when multiple threads are available.

!!! info "What Are Concurrent Compactors?"
    Compactors are background threads that merge SSTables, remove tombstones, and consolidate data. More compactors enable faster compaction throughput but consume more CPU and I/O resources. See [setconcurrentcompactors](setconcurrentcompactors.md) for detailed explanation.

---

## Examples

### Basic Usage

```bash
nodetool getconcurrentcompactors
```

**Sample output:**
```
Current concurrent compactors: 4
```

### Check Value on Remote Node

```bash
nodetool -h 192.168.1.100 getconcurrentcompactors
```

### Check Cluster-Wide Consistency

```bash
#!/bin/bash
# check_compactors_cluster.sh

echo "=== Concurrent Compactors Across Cluster ==="

nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    value=$(nodetool -h $node getconcurrentcompactors 2>/dev/null | grep -oP '\d+')
    echo "$node: $value compactors"
done
```

**Sample output:**
```
=== Concurrent Compactors Across Cluster ===
192.168.1.101: 4 compactors
192.168.1.102: 4 compactors
192.168.1.103: 4 compactors
```

---

## Understanding the Value

### Default Calculation

If not explicitly configured, Cassandra calculates the default:

```
concurrent_compactors = min(number_of_data_directories, number_of_cpu_cores)
```

| Hardware | Expected Default |
|----------|------------------|
| 8 cores, 1 disk | 1 |
| 8 cores, 4 disks | 4 |
| 16 cores, 8 disks | 8 |
| 4 cores, 8 disks | 4 |

### Interpreting Different Values

| Value | Indicates | Typical Reason |
|-------|-----------|----------------|
| 1 | Minimal parallelism | Single disk or resource-constrained |
| 2-4 | Moderate parallelism | Balanced configuration |
| 5-8 | High parallelism | Multiple disks, write-heavy workload |
| 8+ | Maximum parallelism | Large JBOD, bulk loading |

---

## When to Check This Value

### Performance Investigation

When compaction appears slow:

```bash
# Check compactor count
nodetool getconcurrentcompactors

# Compare with pending tasks
nodetool compactionstats | head -10

# If many pending tasks and few compactors, consider increasing
```

### Capacity Planning

Before changing workload:

```bash
# Current compactors
nodetool getconcurrentcompactors

# Current hardware capacity
echo "CPU cores: $(nproc)"
echo "Data directories: $(grep -A 10 'data_file_directories:' /etc/cassandra/cassandra.yaml | grep '^ *-' | wc -l)"

# Current compaction throughput
nodetool getcompactionthroughput
```

### Configuration Audit

Verify cluster consistency:

```bash
#!/bin/bash
# audit_compactors.sh

echo "Auditing compactor settings..."

# Check runtime values
echo ""
echo "Runtime values:"
for node in $(nodetool status | grep "^UN" | awk '{print $2}'); do
    runtime=$(nodetool -h $node getconcurrentcompactors 2>/dev/null | grep -oP '\d+')
    echo "  $node: $runtime"
done

# Check config file (local node)
echo ""
echo "Config file (local):"
grep concurrent_compactors /etc/cassandra/cassandra.yaml || echo "  Not set (using default)"
```

---

## Relationship to Performance

### Impact on Compaction Throughput

```
Total Compaction Capacity ≈ concurrent_compactors × compaction_throughput_mb_per_sec
```

| Compactors | Throughput Setting | Total Capacity |
|------------|--------------------|----------------|
| 2 | 64 MB/s | ~128 MB/s |
| 4 | 64 MB/s | ~256 MB/s |
| 8 | 64 MB/s | ~512 MB/s |

### Checking If Current Value Is Adequate

```bash
#!/bin/bash
# check_compaction_health.sh

echo "=== Compaction Health Check ==="

# Current setting
compactors=$(nodetool getconcurrentcompactors | grep -oP '\d+')
echo "Concurrent compactors: $compactors"

# Pending tasks
pending=$(nodetool compactionstats | grep "pending tasks" | grep -oP '\d+')
echo "Pending compaction tasks: $pending"

# Assessment
if [ "$pending" -gt 100 ]; then
    echo ""
    echo "WARNING: High pending tasks. Consider:"
    echo "  nodetool setconcurrentcompactors $((compactors + 2))"
elif [ "$pending" -lt 10 ]; then
    echo ""
    echo "OK: Compaction keeping up"
else
    echo ""
    echo "MONITOR: Moderate backlog"
fi
```

---

## Configuration Reference

### Runtime vs cassandra.yaml

| Source | What getconcurrentcompactors Shows |
|--------|-----------------------------------|
| After startup (no changes) | Value from cassandra.yaml or calculated default |
| After `setconcurrentcompactors` | Runtime-modified value |
| After restart | Value from cassandra.yaml (runtime changes lost) |

### Checking Both Values

```bash
# Runtime (active) value
nodetool getconcurrentcompactors

# Configured (persistent) value
grep concurrent_compactors /etc/cassandra/cassandra.yaml
```

If these differ, someone used `setconcurrentcompactors` to change the runtime value.

### cassandra.yaml Reference

```yaml
# cassandra.yaml

# Number of simultaneous compactions to allow
# Comment out or omit for auto-calculated default
concurrent_compactors: 4
```

---

## Common Scenarios

### Value Lower Than Expected

**Possible causes:**
- Explicitly set low in cassandra.yaml
- Single data directory configured
- Few CPU cores

```bash
# Check why value is low
echo "CPU cores: $(nproc)"
grep data_file_directories -A 5 /etc/cassandra/cassandra.yaml
grep concurrent_compactors /etc/cassandra/cassandra.yaml
```

### Value Differs Across Nodes

**Possible causes:**
- Different hardware configurations
- Manual runtime changes not persisted
- Inconsistent cassandra.yaml

```bash
# Standardize across cluster
TARGET=4
for node in $(nodetool status | grep "^UN" | awk '{print $2}'); do
    nodetool -h $node setconcurrentcompactors $TARGET
done

# Update cassandra.yaml on all nodes for persistence
```

### Value Changed After Restart

**Cause:** Runtime change via `setconcurrentcompactors` was not persisted to cassandra.yaml

```bash
# To make permanent, update cassandra.yaml
echo "concurrent_compactors: 6" >> /etc/cassandra/cassandra.yaml

# Or edit existing value
sed -i 's/concurrent_compactors:.*/concurrent_compactors: 6/' /etc/cassandra/cassandra.yaml
```

---

## Related Metrics

When viewing concurrent compactors, also check:

```bash
# Compaction activity
nodetool compactionstats

# Throughput limit
nodetool getcompactionthroughput

# SSTable counts (indicates if compaction is keeping up)
nodetool tablestats | grep -E "Table:|SSTable count"

# Thread pool stats
nodetool tpstats | grep -i compaction
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [setconcurrentcompactors](setconcurrentcompactors.md) | Modify the setting (includes detailed explanation) |
| [compactionstats](compactionstats.md) | Monitor compaction activity |
| [getcompactionthroughput](getcompactionthroughput.md) | View I/O limit per compactor |
| [setcompactionthroughput](setcompactionthroughput.md) | Modify I/O limit |
| [tablestats](tablestats.md) | View SSTable counts |
| [tpstats](tpstats.md) | View thread pool statistics |
