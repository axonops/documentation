---
title: "nodetool invalidatekeycache"
description: "Clear key cache in Cassandra using nodetool invalidatekeycache command."
meta:
  - name: keywords
    content: "nodetool invalidatekeycache, key cache, clear cache, Cassandra performance"
search:
  boost: 3
---

# nodetool invalidatekeycache

Invalidates the key cache on the node.

---

## Synopsis

```bash
nodetool [connection_options] invalidatekeycache
```

## Description

`nodetool invalidatekeycache` clears all entries from the key cache on the node. The key cache stores partition index entries, allowing Cassandra to skip disk seeks when locating partitions within SSTables.

After invalidation, the cache is empty and will be repopulated as subsequent read operations occur. This causes a temporary performance impact until the cache is warm again.

!!! warning "Performance Impact"
    Invalidating the key cache causes temporary read latency increases as cached partition locations must be re-read from disk. Use during maintenance windows when possible.

---

## Examples

### Basic Usage

```bash
nodetool invalidatekeycache
```

### Invalidate and Monitor Refill

```bash
nodetool invalidatekeycache
watch -n 5 'nodetool info | grep "Key Cache"'
```

---

## Key Cache Overview

### What the Key Cache Stores

The key cache stores partition key to SSTable position mappings:

| Cached Data | Purpose |
|-------------|---------|
| Partition key hash | Identify the partition |
| SSTable file reference | Which SSTable contains the data |
| Position offset | Byte offset within the SSTable |

### How It Improves Performance

```
Without Key Cache:
  Read Request → Bloom Filter → Partition Index (disk) → Data (disk)

With Key Cache Hit:
  Read Request → Key Cache → Data (disk)
  (Skips partition index read)
```

---

## When to Use

### After Schema Changes

Clear stale cache entries after significant schema modifications:

```bash
# After ALTER TABLE operations that affect partition structure
nodetool invalidatekeycache
```

### Troubleshooting Stale Data

If cached data may be causing issues:

```bash
# Clear potentially stale cache
nodetool invalidatekeycache

# Verify issue resolution
```

### Memory Pressure

During memory emergencies (though reducing cache size may be better):

```bash
# Immediate memory release
nodetool invalidatekeycache
```

### Before Performance Testing

Ensure cold-cache baseline measurements:

```bash
# Clear all caches for baseline test
nodetool invalidatekeycache
nodetool invalidaterowcache
nodetool invalidatecountercache

# Run performance tests
```

---

## Impact Assessment

### Immediate Effects

| Aspect | Impact |
|--------|--------|
| Key cache entries | All cleared |
| Memory usage | Temporarily reduced |
| Disk I/O | Increases (partition index reads) |
| Read latency | Temporarily increases |

### Recovery Timeline

| Phase | Duration | Cache State |
|-------|----------|-------------|
| Immediately after | 0 | Empty |
| Warming up | Minutes to hours | Partially filled |
| Fully warm | Hours (workload dependent) | Optimally filled |

---

## Monitoring Cache Status

### Before and After

```bash
# Check cache status before
echo "Before invalidation:"
nodetool info | grep -A 5 "Key Cache"

# Invalidate
nodetool invalidatekeycache

# Check immediately after
echo "After invalidation:"
nodetool info | grep -A 5 "Key Cache"
```

### Monitor Refill Progress

```bash
#!/bin/bash
# monitor_keycache_refill.sh

echo "=== Key Cache Refill Monitor ==="
echo "Press Ctrl+C to stop"
echo ""

while true; do
    info=$(nodetool info 2>/dev/null | grep -A 1 "Key Cache")
    entries=$(echo "$info" | grep "entries" | awk '{print $4}')
    hit_rate=$(echo "$info" | grep "hit rate" | awk '{print $4}')
    size=$(echo "$info" | grep "size" | awk '{print $4}')

    echo "$(date '+%H:%M:%S') - Entries: $entries, Hit Rate: $hit_rate, Size: $size"
    sleep 10
done
```

### Cache Statistics

```bash
# Detailed cache statistics
nodetool info | grep -E "Key Cache|Row Cache|Counter Cache"
```

---

## Workflow: Controlled Cache Clear

```bash
#!/bin/bash
# controlled_cache_clear.sh

echo "=== Controlled Key Cache Clear ==="

# 1. Check current state
echo "1. Current key cache status:"
nodetool info | grep -A 2 "Key Cache"

# 2. Record baseline metrics
echo ""
echo "2. Baseline read latencies:"
nodetool proxyhistograms | head -20

# 3. Confirm
echo ""
read -p "Proceed with key cache invalidation? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "Aborted."
    exit 1
fi

# 4. Invalidate
echo ""
echo "4. Invalidating key cache..."
nodetool invalidatekeycache

# 5. Verify invalidation
echo ""
echo "5. Cache status after invalidation:"
nodetool info | grep -A 2 "Key Cache"

# 6. Monitor recovery
echo ""
echo "6. Monitoring cache refill (30 seconds)..."
for i in {1..6}; do
    sleep 5
    entries=$(nodetool info | grep -A 1 "Key Cache" | grep "entries" | awk '{print $4}')
    echo "  $(date '+%H:%M:%S') - Entries: $entries"
done

echo ""
echo "=== Complete ==="
echo "Continue monitoring with: watch 'nodetool info | grep -A 2 \"Key Cache\"'"
```

---

## Cluster-Wide Operations

### Invalidate on All Nodes

```bash
#!/bin/bash
# invalidate_keycache_cluster.sh

echo "WARNING: Invalidating key cache cluster-wide!"
echo "This will cause temporary read latency increases."
echo ""

# Get list of node IPs from local nodetool status
nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo -n "$node: "
    ssh "$node" "nodetool invalidatekeycache" 2>/dev/null && echo "invalidated" || echo "FAILED"
done

echo ""
echo "Monitor recovery with: nodetool info | grep 'Key Cache'"
```

### Rolling Invalidation

For minimal impact, invalidate one node at a time:

```bash
#!/bin/bash
# rolling_keycache_invalidate.sh

# Get list of node IPs from local nodetool status
nodes=$(nodetool status | grep "^UN" | awk '{print $2}')
WAIT_TIME=300  # 5 minutes between nodes

for node in $nodes; do
    echo "$(date): Invalidating key cache on $node..."
    ssh "$node" "nodetool invalidatekeycache"

    echo "Waiting ${WAIT_TIME}s for cache to warm..."
    sleep $WAIT_TIME

    # Check hit rate before proceeding
    hit_rate=$(ssh "$node" "nodetool info" 2>/dev/null | grep -A 1 "Key Cache" | grep "hit rate" | awk '{print $4}')
    echo "  Hit rate: $hit_rate"
done

echo "Rolling invalidation complete."
```

---

## Configuration

### Key Cache Size

```yaml
# cassandra.yaml
key_cache_size_in_mb:  # Leave empty for auto (5% of heap)
key_cache_save_period: 14400  # Save interval in seconds
key_cache_keys_to_save:  # Number of keys to save (empty = all)
```

### Adjust Cache Size

```bash
# Check current size
nodetool info | grep "Key Cache"

# If cache is too small/large, adjust in cassandra.yaml and restart
# Or consider per-table caching settings
```

---

## Troubleshooting

### Low Hit Rate After Warmup

```bash
# Check cache size vs working set
nodetool info | grep "Key Cache"

# If entries near capacity with low hit rate,
# consider increasing cache size
```

### Cache Not Refilling

```bash
# Check if caching is enabled for tables
nodetool describecluster

# Check table-level caching
cqlsh -e "SELECT table_name, caching FROM system_schema.tables WHERE keyspace_name = 'my_keyspace';"
```

### Memory Issues

```bash
# If key cache is using too much memory
# Consider reducing size in cassandra.yaml

# Check current usage
nodetool info | grep "Key Cache" | grep "size"
```

---

## Best Practices

!!! tip "Key Cache Guidelines"

    1. **Avoid frequent invalidation** - Let cache warm naturally
    2. **Use during maintenance windows** - Minimize user impact
    3. **Monitor after invalidation** - Track cache refill and hit rates
    4. **Consider rolling approach** - Invalidate one node at a time
    5. **Check cache sizing** - Ensure cache is appropriately sized
    6. **Document the reason** - Record why cache was invalidated

!!! info "When NOT to Invalidate"

    - During peak traffic hours
    - Without understanding the performance impact
    - Routinely (let cache manage itself)
    - On all nodes simultaneously in production

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [invalidaterowcache](invalidaterowcache.md) | Invalidate row cache |
| [invalidatecountercache](invalidatecountercache.md) | Invalidate counter cache |
| [info](info.md) | View cache statistics |
| [setcachecapacity](setcachecapacity.md) | Adjust cache sizes |
