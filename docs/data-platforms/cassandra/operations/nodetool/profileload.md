---
title: "nodetool profileload"
description: "Profile read/write load for tables in Cassandra using nodetool profileload command."
meta:
  - name: keywords
    content: "nodetool profileload, load profiling, table statistics, Cassandra performance"
---

# nodetool profileload

Profiles read and write operations on a table for a specified duration to identify hot partitions and access patterns.

---

## Synopsis

```bash
nodetool [connection_options] profileload [options] [keyspace] [table] [duration]
```

## Description

`nodetool profileload` samples operations on a specific table for the given duration and produces a report showing the most frequently accessed partitions. This is essential for identifying hot partitions—partitions that receive disproportionately high traffic compared to others.

### Why Hot Partitions Matter

In Cassandra, data is distributed across nodes based on partition keys. Ideally, traffic should be evenly distributed across all partitions and nodes. Hot partitions cause problems:

| Problem | Impact |
|---------|--------|
| **Uneven load** | One node handles disproportionate traffic while others are idle |
| **Latency spikes** | Hot partition queries queue up, increasing response times |
| **Resource exhaustion** | CPU, memory, or disk I/O saturated on specific nodes |
| **Scaling limitations** | Adding nodes doesn't help if one partition is the bottleneck |
| **Compaction pressure** | Frequent updates to hot partitions increase compaction load |

### How Profiling Works

When `profileload` runs:

1. **Sampling begins** - Cassandra starts tracking operations on the specified table
2. **Operations recorded** - Each read and write operation's partition key is sampled
3. **Duration elapses** - Sampling continues for the specified time
4. **Report generated** - Statistics compiled and displayed showing top accessed partitions

The profiling uses sampling (not exhaustive tracking) to minimize overhead.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | Target keyspace name (or `*` for all keyspaces) |
| `table` | Target table name (or `*` for all tables) |
| `duration` | Sampling duration in milliseconds (default: 10000) |

## Options

| Option | Description |
|--------|-------------|
| `-s <capacity>` | Sampler capacity (number of top keys to track) |
| `-k <count>` | Number of top partitions to display |
| `-a <samplers>` | Comma-separated list of samplers to use |
| `-i, --interval <ms>` | Schedule sampling at regular intervals |
| `-t, --stop` | Stop scheduled sampling |
| `-l, --list` | List scheduled samplings |

---

## Output Format

```
Table: my_keyspace.my_table
Samples: 10000
Duration: 60000 ms

Top 10 Partitions:
  Partition Key              Reads      Writes     Total
  user_12345                 4523       1245       5768
  user_98765                 3211       892        4103
  user_55555                 2105       445        2550
  order_2024_01_15           1892       234        2126
  user_00001                 1456       312        1768
  ...

Read/Write Ratio: 78% reads, 22% writes
```

### Output Fields

| Field | Description |
|-------|-------------|
| **Partition Key** | The partition key value receiving traffic |
| **Reads** | Number of read operations sampled for this partition |
| **Writes** | Number of write operations sampled for this partition |
| **Total** | Combined read and write count |

---

## Examples

### Basic 30-Second Profile

```bash
nodetool profileload my_keyspace users 30000
```

### 2-Minute Profile for Detailed Analysis

```bash
nodetool profileload my_keyspace events 120000
```

### Profile During Peak Hours

```bash
# Run during known high-traffic period
nodetool profileload ecommerce orders 300000  # 5 minutes
```

### Profile on Remote Node

```bash
ssh 192.168.1.100 "nodetool profileload my_keyspace my_table 60000"
```

### Save Output for Analysis

```bash
nodetool profileload my_keyspace my_table 60000 > profile_report.txt
```

---

## Use Case Scenarios

### Scenario 1: Investigating Latency Spikes

**Symptom:** Application reports intermittent slow queries on the `users` table.

**Investigation:**

```bash
# Profile during a period when latency issues occur
nodetool profileload myapp users 60000
```

**Analysis:** If output shows one partition with 80% of traffic, that's the hot partition causing queuing and latency.

**Resolution options:**
- Redesign partition key to distribute load
- Add caching layer for hot data
- Consider time-bucketing for time-series data

### Scenario 2: Capacity Planning

**Symptom:** Planning to scale out, need to understand current access patterns.

**Investigation:**

```bash
# Profile each major table
nodetool profileload myapp users 120000
nodetool profileload myapp orders 120000
nodetool profileload myapp events 120000
```

**Analysis:** Identify which tables have even distribution vs. hot spots. Tables with hot partitions won't benefit from horizontal scaling without schema changes.

### Scenario 3: Validating Data Model Design

**Symptom:** New table deployed, want to verify access patterns match expectations.

**Investigation:**

```bash
# Profile during normal operation
nodetool profileload myapp new_table 300000
```

**Analysis:** Compare actual access patterns with design assumptions. If certain partitions are hotter than expected, the data model may need adjustment.

### Scenario 4: Debugging Uneven Node Load

**Symptom:** `nodetool status` shows one node with significantly higher load.

**Investigation:**

```bash
# Profile on the hot node
ssh hot_node "nodetool profileload myapp main_table 60000"

# Compare with other nodes
ssh other_node "nodetool profileload myapp main_table 60000"
```

**Analysis:** Determine if specific partition keys are causing the imbalance. Hot partitions always land on the same node(s) based on the token ring.

### Scenario 5: Time-Series Data Evaluation

**Symptom:** Time-series table using date as partition key, suspecting today's partition is overwhelmed.

**Investigation:**

```bash
nodetool profileload metrics sensor_readings 60000
```

**Analysis:** If output shows `2024-01-15` (today) with 95% of traffic, the current day's partition is hot. Consider time-bucketing (hourly partitions) or a different partitioning strategy.

### Scenario 6: Pre-Production Load Testing Validation

**Symptom:** Running load tests, need to verify traffic distribution.

**Investigation:**

```bash
# During load test
nodetool profileload testks test_table 60000
```

**Analysis:** Verify load test is generating realistic, distributed traffic patterns. Uneven distribution in testing means the load test isn't representative.

---

## Impact on Cluster Performance

### Overhead Assessment

| Aspect | Impact |
|--------|--------|
| **CPU** | Minimal - sampling-based, not exhaustive |
| **Memory** | Low - maintains counters for sampled partitions |
| **Disk I/O** | None - operates in memory only |
| **Query latency** | Negligible - sampling adds microseconds per operation |
| **Network** | None - local operation only |

!!! info "Safe for Production"
    `profileload` is designed to be safe for production use. The sampling approach ensures minimal overhead even on high-traffic tables. However, avoid running multiple concurrent profiles on the same table.

### Recommendations

| Scenario | Duration | Notes |
|----------|----------|-------|
| Quick check | 30 seconds | Sufficient for high-traffic tables |
| Standard analysis | 1-2 minutes | Good balance of data and time |
| Comprehensive profiling | 5 minutes | For detailed analysis or low-traffic tables |
| Peak period analysis | Match peak duration | Capture full peak behavior |

---

## Interpreting Results

### Healthy Distribution

```
Top 10 Partitions:
  Partition Key              Reads      Writes     Total
  user_12345                 234        45         279
  user_98765                 228        52         280
  user_55555                 241        38         279
  user_44444                 225        51         276
  user_33333                 239        42         281
```

**Interpretation:** Top partitions have similar access counts. This indicates even distribution—good data model design.

### Hot Partition Detected

```
Top 10 Partitions:
  Partition Key              Reads      Writes     Total
  user_admin                 45230      12450      57680     ← Hot!
  user_98765                 321        89         410
  user_55555                 210        44         254
  user_44444                 189        31         220
```

**Interpretation:** `user_admin` receives 100x more traffic than others. This is a severe hot partition requiring immediate attention.

### Write-Heavy Partition

```
Top 10 Partitions:
  Partition Key              Reads      Writes     Total
  metrics_2024_01_15         234        89450      89684     ← Write-heavy
  metrics_2024_01_14         12000      45         12045
```

**Interpretation:** Today's partition is receiving heavy writes while yesterday's is read-only. Common in time-series data—consider finer time bucketing.

---

## Addressing Hot Partitions

Once identified, hot partitions can be addressed through several strategies:

### Data Model Changes

```cql
-- Before: Single partition per user
CREATE TABLE user_events (
    user_id text,
    event_time timestamp,
    event_data text,
    PRIMARY KEY (user_id, event_time)
);

-- After: Add time bucket to distribute load
CREATE TABLE user_events_v2 (
    user_id text,
    time_bucket text,  -- e.g., '2024-01-15_14' for hourly buckets
    event_time timestamp,
    event_data text,
    PRIMARY KEY ((user_id, time_bucket), event_time)
);
```

### Application-Level Caching

```bash
# If profiling shows read-heavy hot partition
# Implement caching for frequently accessed data
```

### Rate Limiting

```bash
# If hot partition is due to misbehaving client
# Implement application-level rate limiting
```

---

## Comparing with Related Commands

| Command | Purpose | Scope | Overhead |
|---------|---------|-------|----------|
| `profileload` | Detailed partition access profiling | Single table | Low |
| `toppartitions` | Real-time top partition view | Single table | Low |
| `tablestats` | General table statistics | All tables | None |
| `tablehistograms` | Latency distribution | Single table | None |

### When to Use Each

- **`profileload`** - Detailed investigation of specific table's access patterns
- **`toppartitions`** - Quick check of current hot partitions
- **`tablestats`** - Overview of table health and metrics
- **`tablehistograms`** - Understanding latency distribution

---

## Cluster-Wide Profiling

To understand cluster-wide patterns, profile across all nodes:

```bash
#!/bin/bash
# profile_all_nodes.sh

KEYSPACE="$1"
TABLE="$2"
DURATION="${3:-60000}"

if [ -z "$KEYSPACE" ] || [ -z "$TABLE" ]; then
    echo "Usage: $0 <keyspace> <table> [duration_ms]"
    exit 1
fi

OUTPUT_DIR="/tmp/profiles_$(date +%Y%m%d_%H%M%S)"
mkdir -p $OUTPUT_DIR

# Get list of node IPs from local nodetool status
nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

echo "Profiling $KEYSPACE.$TABLE for ${DURATION}ms on all nodes..."
echo "Output directory: $OUTPUT_DIR"
echo ""

# Start profiling on all nodes in parallel
for node in $nodes; do
    echo "Starting profile on $node..."
    ssh "$node" "nodetool profileload $KEYSPACE $TABLE $DURATION > "$OUTPUT_DIR/profile_$node.txt" &"
done

# Wait for all to complete
wait

echo ""
echo "Profiling complete. Results:"
echo ""

# Display summary from each node
for node in $nodes; do
    echo "=== $node ==="
    head -20 "$OUTPUT_DIR/profile_$node.txt"
    echo ""
done
```

---

## Best Practices

!!! tip "Profiling Guidelines"

    1. **Profile during representative periods** - Run during normal load, not idle times
    2. **Use appropriate duration** - Longer for low-traffic tables, shorter for high-traffic
    3. **Profile multiple times** - Compare peak vs. off-peak patterns
    4. **Profile all nodes** - Hot partitions may only appear on specific nodes
    5. **Correlate with symptoms** - Run when latency issues occur
    6. **Document findings** - Save output for historical comparison
    7. **Act on results** - Profiling is only useful if hot partitions are addressed

!!! warning "Considerations"

    - Results are samples, not exact counts
    - Profile duration should match workload patterns
    - One profile may not capture intermittent issues
    - Hot partitions identified are node-local (partition may be hot on one replica)

---

## Troubleshooting

### No Output or Empty Results

```bash
# Verify table has traffic
nodetool tablestats my_keyspace.my_table | grep "operations"

# Ensure duration is sufficient
# Try longer duration for low-traffic tables
nodetool profileload my_keyspace my_table 300000
```

### Command Times Out

```bash
# Reduce duration
nodetool profileload my_keyspace my_table 30000

# Check JMX connectivity
nodetool info
```

### Results Don't Match Expected Patterns

```bash
# Profile on specific node that's showing issues
ssh problem_node "nodetool profileload my_keyspace my_table 60000"

# Verify correct table
nodetool tablestats my_keyspace.my_table
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [toppartitions](toppartitions.md) | Real-time view of hot partitions |
| [tablestats](tablestats.md) | Table statistics and metrics |
| [tablehistograms](tablehistograms.md) | Latency histograms for table operations |
| [proxyhistograms](proxyhistograms.md) | Coordinator-level latency metrics |
| [status](status.md) | Node load distribution |