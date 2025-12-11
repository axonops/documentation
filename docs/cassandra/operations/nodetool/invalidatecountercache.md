# nodetool invalidatecountercache

Invalidates the counter cache on the node.

---

## Synopsis

```bash
nodetool [connection_options] invalidatecountercache
```

## Description

`nodetool invalidatecountercache` clears all entries from the counter cache on the node. The counter cache stores counter cell values, allowing faster access to frequently read counters by avoiding disk reads for their current values.

After invalidation, the cache is empty and will be repopulated as subsequent counter read operations occur.

!!! info "Counter-Specific Cache"
    This cache only affects counter columns. If the workload does not use counters, this cache will be empty and invalidation has no effect.

---

## Examples

### Basic Usage

```bash
nodetool invalidatecountercache
```

### Invalidate and Monitor Refill

```bash
nodetool invalidatecountercache
watch -n 5 'nodetool info | grep "Counter Cache"'
```

### On Remote Node

```bash
nodetool -h 192.168.1.100 invalidatecountercache
```

---

## Counter Cache Overview

### What the Counter Cache Stores

| Cached Data | Description |
|-------------|-------------|
| Counter cell location | Reference to counter column |
| Current counter value | Most recent counter value |
| Merge information | Data for counter merges |

### How It Improves Performance

```
Without Counter Cache:
  Counter Read → Read all counter shards from disk → Merge → Return value

With Counter Cache Hit:
  Counter Read → Return cached merged value
  (Avoids disk reads and merge computation)
```

### Counter Operations

Counters in Cassandra are distributed and require merging values from multiple sources:

1. Local shard value
2. Remote shard values
3. Historical values for consistency

The counter cache stores the merged result, avoiding repeated computation.

---

## When to Use

### After Counter Repair

Clear potentially inconsistent cached values:

```bash
# After running repair on counter tables
nodetool invalidatecountercache
```

### Troubleshooting Counter Discrepancies

If counter values appear incorrect:

```bash
# Clear counter cache
nodetool invalidatecountercache

# Re-read counters to get fresh values
```

### After Counter Table Restore

Following restore from backup:

```bash
# After restoring counter data
nodetool invalidatecountercache
```

### Memory Optimization

Release memory if counter cache is large:

```bash
# Check current size
nodetool info | grep "Counter Cache"

# Clear if necessary
nodetool invalidatecountercache
```

---

## Impact Assessment

### Immediate Effects

| Aspect | Impact |
|--------|--------|
| Counter cache entries | All cleared |
| Memory usage | Temporarily reduced |
| Counter read latency | Temporarily increases |
| Disk I/O for counters | Increases |

### Recovery Timeline

| Phase | Duration | Cache State |
|-------|----------|-------------|
| Immediately after | 0 | Empty |
| Warming up | Minutes | Partially filled |
| Fully warm | Hours | Optimally filled |

!!! note "Impact Scope"
    Impact is limited to counter column workloads. Non-counter reads are unaffected.

---

## Monitoring Cache Status

### Before and After

```bash
# Check cache status before
echo "Before invalidation:"
nodetool info | grep -A 5 "Counter Cache"

# Invalidate
nodetool invalidatecountercache

# Check immediately after
echo "After invalidation:"
nodetool info | grep -A 5 "Counter Cache"
```

### Monitor Refill Progress

```bash
#!/bin/bash
# monitor_countercache_refill.sh

echo "=== Counter Cache Refill Monitor ==="
echo "Press Ctrl+C to stop"
echo ""

while true; do
    info=$(nodetool info 2>/dev/null | grep -A 2 "Counter Cache")
    entries=$(echo "$info" | grep "entries" | awk '{print $4}')
    hit_rate=$(echo "$info" | grep "hit rate" | awk '{print $4}')
    size=$(echo "$info" | grep "size" | awk '{print $4}')

    echo "$(date '+%H:%M:%S') - Entries: $entries, Hit Rate: $hit_rate, Size: $size"
    sleep 10
done
```

---

## Workflow: Counter Cache Management

```bash
#!/bin/bash
# counter_cache_management.sh

echo "=== Counter Cache Management ==="

# 1. Check current state
echo "1. Current counter cache status:"
nodetool info | grep -A 3 "Counter Cache"

# 2. Check if counters are in use
entries=$(nodetool info 2>/dev/null | grep -A 1 "Counter Cache" | grep "entries" | awk '{print $4}')
if [ "$entries" = "0" ]; then
    echo ""
    echo "Counter cache is empty - no counters in use or caching disabled."
    echo "Invalidation would have no effect."
    exit 0
fi

# 3. Proceed with invalidation
echo ""
echo "2. Invalidating counter cache..."
nodetool invalidatecountercache

# 4. Verify
echo ""
echo "3. Cache status after invalidation:"
nodetool info | grep -A 3 "Counter Cache"

# 5. Monitor refill
echo ""
echo "4. Monitoring refill (30 seconds)..."
for i in {1..6}; do
    sleep 5
    entries=$(nodetool info 2>/dev/null | grep -A 1 "Counter Cache" | grep "entries" | awk '{print $4}')
    echo "  Entries: $entries"
done

echo ""
echo "=== Complete ==="
```

---

## Cluster-Wide Operations

### Invalidate on All Nodes

```bash
#!/bin/bash
# invalidate_countercache_cluster.sh

echo "Invalidating counter cache cluster-wide..."

nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo -n "$node: "
    nodetool -h $node invalidatecountercache 2>/dev/null && echo "invalidated" || echo "FAILED"
done

echo ""
echo "Monitor recovery with: nodetool info | grep 'Counter Cache'"
```

### Rolling Invalidation

```bash
#!/bin/bash
# rolling_countercache_invalidate.sh

nodes=$(nodetool status | grep "^UN" | awk '{print $2}')
WAIT_TIME=120  # 2 minutes between nodes

for node in $nodes; do
    echo "$(date): Invalidating counter cache on $node..."
    nodetool -h $node invalidatecountercache

    echo "Waiting ${WAIT_TIME}s for cache warmup..."
    sleep $WAIT_TIME

    hit_rate=$(nodetool -h $node info 2>/dev/null | grep -A 2 "Counter Cache" | grep "hit rate" | awk '{print $4}')
    echo "  Hit rate: $hit_rate"
done

echo "Rolling invalidation complete."
```

---

## Configuration

### Counter Cache Settings

```yaml
# cassandra.yaml
counter_cache_size_in_mb:   # Default: min(2.5% of heap, 50MB)
counter_cache_save_period: 7200  # Save interval in seconds
counter_cache_keys_to_save:  # Keys to save on shutdown
```

### Check Configuration

```bash
# View current counter cache configuration
nodetool info | grep "Counter Cache"

# Check cassandra.yaml
grep counter_cache /etc/cassandra/cassandra.yaml
```

---

## Troubleshooting

### Counter Cache Always Empty

```bash
# Check if any tables use counters
cqlsh -e "SELECT keyspace_name, table_name FROM system_schema.columns WHERE type = 'counter' ALLOW FILTERING;"

# If no counter tables, cache will be empty
```

### Low Hit Rate

```bash
# Check cache size vs counter working set
nodetool info | grep "Counter Cache"

# Consider increasing cache size if entries are at capacity
# but hit rate is low
```

### Counter Values Incorrect After Invalidation

```bash
# Run repair on counter tables
nodetool repair -pr my_keyspace counter_table

# Then allow cache to rebuild with correct values
```

---

## Counter Best Practices

!!! tip "Counter Cache Guidelines"

    1. **Understand counter workload** - Only useful if using counter columns
    2. **Invalidate after repair** - Ensure cached values are consistent
    3. **Monitor hit rates** - Low hit rate may indicate sizing issue
    4. **Consider alternatives** - For simple counting, regular columns may be better
    5. **Test impact** - Measure latency impact before production invalidation

!!! info "Counter Limitations"

    Remember that Cassandra counters have specific limitations:

    - Cannot be part of primary key
    - Can only increment/decrement (no set)
    - Subject to consistency challenges
    - Counter cache helps mitigate read overhead

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [invalidatekeycache](invalidatekeycache.md) | Invalidate key cache |
| [invalidaterowcache](invalidaterowcache.md) | Invalidate row cache |
| [info](info.md) | View cache statistics |
| [setcachecapacity](setcachecapacity.md) | Adjust cache sizes |
| [repair](repair.md) | Repair data including counters |
