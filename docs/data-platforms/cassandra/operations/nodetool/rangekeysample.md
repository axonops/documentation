---
title: "nodetool rangekeysample"
description: "Sample partition keys from SSTables using nodetool rangekeysample command."
meta:
  - name: keywords
    content: "nodetool rangekeysample, key sample, partition keys, Cassandra"
---

# nodetool rangekeysample

Displays a sample of partition keys from each token range owned by the node.

---

## Synopsis

```bash
nodetool [connection_options] rangekeysample
```

## Description

`nodetool rangekeysample` returns a sample of partition keys from each token range owned by the local node. The samples are obtained from the SSTable index files, providing a quick way to see representative partition keys without scanning all data.

### How It Works

Cassandra maintains partition key samples in memory for each SSTable, derived from the SSTable index. These samples are used internally for:

- Estimating partition counts
- Calculating data distribution statistics
- Optimizing read operations

The `rangekeysample` command exposes these samples, showing actual partition key values that exist in each token range on the node.

### What the Output Represents

Each line in the output represents a sampled partition key. The keys shown are:

- **Actual partition keys** from SSTables on the local node
- **Distributed across token ranges** the node owns
- **A statistical sample**, not an exhaustive list
- **Representative of data distribution** patterns

---

## Output Format

```
<partition_key_1>
<partition_key_2>
<partition_key_3>
...
```

### Example Output

For a table with UUID partition keys:

```
550e8400-e29b-41d4-a716-446655440000
6ba7b810-9dad-11d1-80b4-00c04fd430c8
6ba7b811-9dad-11d1-80b4-00c04fd430c8
7c9e6679-7425-40de-944b-e07fc1f90ae7
...
```

For a table with text partition keys:

```
user_12345
user_23456
user_34567
order_98765
order_87654
...
```

For composite partition keys, the output shows the combined key representation.

---

## Arguments

This command takes no arguments. It samples keys from all keyspaces and tables on the node.

---

## Examples

### Basic Usage

```bash
nodetool rangekeysample
```

### Save Samples to File

```bash
nodetool rangekeysample > /tmp/key_samples.txt
```

### Count Sample Size

```bash
nodetool rangekeysample | wc -l
```

### View First 20 Samples

```bash
nodetool rangekeysample | head -20
```

### Filter for Specific Key Patterns

```bash
# Find samples matching a pattern
nodetool rangekeysample | grep "user_"

# Find samples starting with specific prefix
nodetool rangekeysample | grep "^order"
```

---

## Use Cases

### Investigating Data Distribution

Examine what partition keys exist on a specific node to understand data placement:

```bash
# Sample keys on each node to compare distribution
for node in node1 node2 node3; do
    echo "=== $node ==="
    ssh "$node" "nodetool rangekeysample" | wc -l
done
```

Uneven sample counts may indicate data skew or hot spots.

### Identifying Partition Key Patterns

Discover what types of partition keys exist in the cluster:

```bash
# Get unique prefixes to understand key naming patterns
nodetool rangekeysample | cut -c1-10 | sort | uniq -c | sort -rn | head -20
```

### Validating Data After Migration

After migrating data, verify that expected partition keys are present:

```bash
# Check if specific key patterns exist
nodetool rangekeysample | grep -c "expected_prefix"
```

### Debugging Hot Partitions

When investigating potential hot partitions, sample keys to identify candidates:

```bash
# Sample keys and cross-reference with known hot partition patterns
nodetool rangekeysample > samples.txt
# Compare with application logs showing slow queries
```

### Estimating Partition Count

While not exact, the sample count gives a rough indication of partition density:

```bash
# Samples per node
nodetool rangekeysample | wc -l
# Higher counts suggest more partitions
```

### Pre-Migration Analysis

Before cluster migration or expansion, understand current key distribution:

```bash
# Document current key samples for comparison after migration
nodetool rangekeysample > pre_migration_samples_$(hostname).txt
```

---

## Understanding the Sample

### Sample Size

The number of keys returned depends on:

- **Total partitions** on the node
- **SSTable count** per table
- **Sampling interval** configured in Cassandra (default samples every 128th key)
- **Index entries** in each SSTable

### Sampling Rate

Cassandra's SSTable index sampling interval is configured in `cassandra.yaml`:

```yaml
# Default: sample 1 key per 128 partitions
index_summary_resize_interval_in_minutes: 60
index_summary_capacity_in_mb: 0  # Auto-calculated based on heap
```

### Interpreting Results

| Observation | Possible Meaning |
|-------------|------------------|
| Few samples | Node has few partitions or few SSTables |
| Many samples | Node stores many partitions |
| Patterns in keys | Application key design visible |
| No output | Node may have no data or SSTables |

---

## Limitations

!!! info "Important Considerations"

    - **Not exhaustive** - Only returns sampled keys, not all partition keys
    - **Local node only** - Shows keys from the node where command is run
    - **All tables combined** - Cannot filter by keyspace or table
    - **Point-in-time** - Represents data at execution time
    - **No token information** - Does not show which token range each key belongs to
    - **Memory-based** - Samples are from index summaries held in memory

### Getting Complete Key Lists

For exhaustive partition key lists (not just samples), use CQL:

```cql
-- Warning: This can be expensive on large tables
SELECT DISTINCT token(partition_key), partition_key
FROM keyspace.table;
```

Or use `sstablekeys` tool for offline analysis:

```bash
# List all keys in an SSTable
sstablekeys /var/lib/cassandra/data/keyspace/table-uuid/nb-1-big-Data.db
```

---

## Combining with Other Commands

### With Token Ring Information

```bash
# Compare key samples with token ranges
echo "=== Token Ranges ==="
nodetool ring | head -20

echo ""
echo "=== Key Samples ==="
nodetool rangekeysample | head -20
```

### With Table Statistics

```bash
# Correlate samples with partition counts
echo "=== Estimated Partitions ==="
nodetool tablestats my_keyspace.my_table | grep "Number of partitions"

echo ""
echo "=== Sample Count ==="
nodetool rangekeysample | wc -l
```

### Across All Nodes

```bash
#!/bin/bash
# collect_key_samples.sh - Gather samples from all nodes

OUTPUT_DIR="/tmp/key_samples_$(date +%Y%m%d)"
mkdir -p $OUTPUT_DIR

# Get list of node IPs from local nodetool status
nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo "Collecting from $node..."
    ssh "$node" "nodetool rangekeysample" > "$OUTPUT_DIR/samples_$node.txt"
    count=$(wc -l < "$OUTPUT_DIR/samples_$node.txt")
    echo "  $count samples collected"
done

echo ""
echo "Samples saved to $OUTPUT_DIR"

# Summary
echo ""
echo "=== Sample Counts by Node ==="
wc -l $OUTPUT_DIR/samples_*.txt
```

---

## Troubleshooting

### Empty Output

If the command returns no output:

```bash
# Check if node has data
nodetool tablestats | grep "Space used"

# Check if SSTables exist
ls /var/lib/cassandra/data/*/*/*.db | head

# Node may need compaction to generate index summaries
nodetool compactionstats
```

### Very Few Samples

Few samples may indicate:

- Low partition count
- Few SSTables (data mostly in memtables)
- Recent node with limited data

```bash
# Force flush to create SSTables
nodetool flush

# Then re-sample
nodetool rangekeysample | wc -l
```

### Command Hangs

If the command takes too long:

```bash
# May indicate memory pressure or large index summaries
# Check JMX connectivity
nodetool info

# Check for memory issues
nodetool gcstats
```

---

## Best Practices

!!! tip "Usage Guidelines"

    1. **Use for exploration** - Helpful for understanding data, not production monitoring
    2. **Combine with other tools** - Cross-reference with `ring`, `tablestats`, `getendpoints`
    3. **Sample all nodes** - For complete picture, gather from entire cluster
    4. **Consider timing** - Run after compaction for most accurate representation
    5. **Save for comparison** - Store samples before and after major changes

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [ring](ring.md) | View token ring and ownership |
| [getendpoints](getendpoints.md) | Find which nodes store a specific key |
| [describering](describering.md) | Detailed ring information |
| [tablestats](tablestats.md) | Table statistics including partition estimates |
| [status](status.md) | Cluster status and data load per node |
