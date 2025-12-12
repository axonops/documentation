---
description: "Display coordinator read/write latency histograms using nodetool proxyhistograms."
meta:
  - name: keywords
    content: "nodetool proxyhistograms, latency histogram, coordinator latency, Cassandra"
---

# nodetool proxyhistograms

Displays latency histograms for coordinator operations including reads, writes, and range queries.

---

## Synopsis

```bash
nodetool [connection_options] proxyhistograms
```

## Description

`nodetool proxyhistograms` shows coordinator-level latency percentiles for:

- Read operations
- Write operations
- Range slice queries (scans)
- CAS read operations
- CAS write operations
- View write operations

These are end-to-end latencies as seen by the coordinator node, including network time to replicas.

---

## Output Example

```
proxy histograms
Percentile      Read Latency     Write Latency     Range Latency    CAS Read Latency   CAS Write Latency  View Write Latency
                    (micros)          (micros)          (micros)            (micros)            (micros)            (micros)
50%                   234.00             89.00            567.00              345.00              456.00                0.00
75%                   345.00            123.00            789.00              567.00              678.00                0.00
95%                   678.00            234.00           1234.00              890.00             1012.00                0.00
98%                   890.00            345.00           1567.00             1234.00             1345.00                0.00
99%                  1234.00            456.00           2345.00             1567.00             1789.00                0.00
Min                    45.00             23.00            123.00               89.00              123.00                0.00
Max                  5678.00           1234.00           9012.00             4567.00             5678.00                0.00
```

---

## Output Fields

### Latency Types

| Type | Description |
|------|-------------|
| Read Latency | Point read operations (SELECT by primary key) |
| Write Latency | Mutations (INSERT, UPDATE, DELETE) |
| Range Latency | Range queries (SELECT with range or no key) |
| CAS Read Latency | Lightweight transaction reads |
| CAS Write Latency | Lightweight transaction writes |
| View Write Latency | Materialized view updates |

### Percentiles

| Percentile | Meaning |
|------------|---------|
| 50% (median) | Half of requests are faster than this |
| 75% | 75% of requests are faster |
| 95% | 95% of requests are faster |
| 98% | 98% of requests are faster |
| 99% | 99% of requests are faster (p99) |
| Min | Fastest observed request |
| Max | Slowest observed request |

---

## Interpreting Results

### Healthy Latencies (SSD)

| Operation | p50 | p99 | Assessment |
|-----------|-----|-----|------------|
| Read | < 500μs | < 5ms | Excellent |
| Read | < 2ms | < 20ms | Good |
| Read | < 5ms | < 50ms | Acceptable |
| Write | < 200μs | < 2ms | Excellent |
| Write | < 500μs | < 5ms | Good |
| Write | < 1ms | < 10ms | Acceptable |

### Warning Signs

```
Percentile      Read Latency
50%                  5000.00
99%                 50000.00
```

!!! danger "High Latencies"
    p50 > 5ms or p99 > 50ms suggests:

    - Disk I/O issues
    - GC pressure
    - Network problems
    - Large partitions
    - Inefficient queries

### High Tail Latency (p99)

```
50%                   234.00
99%                 25000.00
```

Large gap between p50 and p99 indicates:

| Cause | Investigation |
|-------|---------------|
| GC pauses | Check `gcstats`, JVM logs |
| Large partitions | Check `tablestats` partition sizes |
| Network variability | Check inter-node latency |
| Slow replica | Check `tpstats` on all nodes |

### Zero Latencies

```
View Write Latency
        0.00
```

Zero means no operations of that type occurred since restart.

---

## When to Use

### Baseline Performance

Establish baseline latencies during normal operation:

```bash
nodetool proxyhistograms > baseline_$(date +%Y%m%d).txt
```

### During Incidents

Compare current latencies to baseline:

```bash
nodetool proxyhistograms
```

### After Changes

After configuration or schema changes:

```bash
nodetool proxyhistograms
```

### Continuous Monitoring

```bash
watch -n 30 'nodetool proxyhistograms'
```

---

## Examples

### Basic Usage

```bash
nodetool proxyhistograms
```

### Compare All Nodes

```bash
for node in node1 node2 node3; do
    echo "=== $node ==="
    nodetool -h $node proxyhistograms
done
```

### Extract Read p99

```bash
nodetool proxyhistograms | grep "99%" | awk '{print "Read p99:", $2, "μs"}'
```

### Track Over Time

```bash
while true; do
    echo "$(date): $(nodetool proxyhistograms | grep '99%' | awk '{print "R:"$2 " W:"$3}')"
    sleep 60
done
```

---

## Coordinator vs. Local Latency

### What proxyhistograms Measures

The `proxyhistograms` command measures the total time from when the coordinator receives a query to when it returns the result to the client. This includes:

| Step | Description |
|------|-------------|
| 1 | Client sends query to coordinator |
| 2 | Coordinator sends read requests to replicas (R1, R2, R3) |
| 3 | Replicas process and return responses |
| 4 | Coordinator aggregates results and returns to client |

!!! info "Measurement Scope"
    `proxyhistograms` measures the entire span from query receipt to result return, including all network round-trips to replicas.

### Coordinator vs. Local

| Command | Measures | Includes |
|---------|----------|----------|
| `proxyhistograms` | Coordinator latency | Network + all replicas |
| `tablehistograms` | Local latency | Only local disk operations |

High proxy latency with low table latency = network issue or slow remote replicas.

---

## Troubleshooting High Latencies

### Step 1: Identify Scope

```bash
# Check if all nodes affected
for node in node1 node2 node3; do
    nodetool -h $node proxyhistograms | grep "99%"
done
```

### Step 2: Compare Proxy vs. Local

```bash
# Proxy (coordinator) latency
nodetool proxyhistograms

# Local (single node) latency
nodetool tablehistograms my_keyspace my_table
```

### Step 3: Check for Obvious Issues

```bash
# Thread pools
nodetool tpstats

# GC stats
nodetool gcstats

# Compaction backlog
nodetool compactionstats
```

### Step 4: Investigate Specific Tables

```bash
# Which tables are slow?
nodetool tablestats my_keyspace | grep -E "Table:|read latency|write latency"
```

---

## Latency Degradation Patterns

### Gradual Increase

- Growing data volume
- SSTable accumulation
- Bloom filter pressure

### Sudden Spike

- Node failure
- Network partition
- GC storm
- Compaction pressure

### Periodic Spikes

- Scheduled jobs
- Backup operations
- Repair running
- Compaction cycles

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [tablestats](tablestats.md) | Table statistics including latencies |
| [tpstats](tpstats.md) | Thread pool statistics |
| [gcstats](gcstats.md) | Garbage collection statistics |
| [compactionstats](compactionstats.md) | Compaction activity |
