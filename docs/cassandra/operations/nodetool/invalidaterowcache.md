---
description: "Clear row cache in Cassandra using nodetool invalidaterowcache command."
meta:
  - name: keywords
    content: "nodetool invalidaterowcache, row cache, clear cache, Cassandra performance"
---

# nodetool invalidaterowcache

Invalidates the row cache on the node.

---

## Synopsis

```bash
nodetool [connection_options] invalidaterowcache
```

## Description

`nodetool invalidaterowcache` clears all entries from the row cache on the node. The row cache stores complete partition data in memory, providing the fastest possible read path by eliminating disk access entirely for cached partitions.

After invalidation, the cache is empty and will be repopulated as subsequent read operations occur with caching enabled at the table level.

!!! warning "Significant Performance Impact"
    Invalidating the row cache can cause substantial read latency increases, especially for workloads that heavily rely on row caching. The row cache stores entire partitions, so rebuilding it requires full partition reads from disk.

---

## Examples

### Basic Usage

```bash
nodetool invalidaterowcache
```

### Invalidate and Monitor Refill

```bash
nodetool invalidaterowcache
watch -n 5 'nodetool info | grep "Row Cache"'
```

### On Remote Node

```bash
nodetool -h 192.168.1.100 invalidaterowcache
```

---

## Row Cache Overview

### What the Row Cache Stores

The row cache stores complete partition data:

| Cached Data | Description |
|-------------|-------------|
| Full partition | Complete partition with all rows |
| All columns | All column values |
| Tombstones | Including deletion markers |

### How It Improves Performance

```
Without Row Cache:
  Read Request → Bloom Filter → Key Cache → Partition Index → Data (disk)

With Row Cache Hit:
  Read Request → Row Cache → Response
  (Zero disk I/O)
```

### Row Cache vs Key Cache

| Aspect | Row Cache | Key Cache |
|--------|-----------|-----------|
| Stores | Complete partition data | Partition location |
| Memory usage | High | Low |
| Benefit | Eliminates all disk I/O | Reduces index seeks |
| Use case | Hot, frequently read partitions | General read optimization |

---

## When to Use

### After Data Corruption Recovery

Clear potentially stale cached data:

```bash
# After repair or data recovery
nodetool invalidaterowcache
```

### Troubleshooting Stale Reads

If cached data appears outdated:

```bash
# Clear row cache to force fresh reads
nodetool invalidaterowcache

# Verify data is now correct
```

### Memory Pressure

During severe memory emergencies:

```bash
# Release row cache memory
nodetool invalidaterowcache

# Consider also reducing row cache size
nodetool setcachecapacity <key_cache_mb> 0 <counter_cache_mb>
```

### Before Performance Testing

Establish cold-cache baseline:

```bash
# Clear all caches
nodetool invalidaterowcache
nodetool invalidatekeycache
nodetool invalidatecountercache

# Run benchmark
```

---

## Impact Assessment

### Immediate Effects

| Aspect | Impact |
|--------|--------|
| Row cache entries | All cleared |
| Memory usage | Significantly reduced |
| Disk I/O | Increases substantially |
| Read latency | May increase dramatically |

### Recovery Timeline

| Phase | Duration | Impact |
|-------|----------|--------|
| Immediately after | Severe | 100% cache miss rate |
| Initial warming | Minutes | High disk I/O, elevated latency |
| Partially warm | Hours | Improving performance |
| Fully warm | Hours to days | Normal performance |

!!! danger "Production Warning"
    Row cache invalidation in production can cause severe performance degradation. The impact is proportional to how much the workload depends on row caching. Consider:

    - Performing during maintenance windows
    - Using rolling invalidation across nodes
    - Having capacity to handle increased disk I/O

---

## Monitoring Cache Status

### Before and After

```bash
# Check cache status before
echo "Before invalidation:"
nodetool info | grep -A 5 "Row Cache"

# Invalidate
nodetool invalidaterowcache

# Check immediately after
echo "After invalidation:"
nodetool info | grep -A 5 "Row Cache"
```

### Monitor Refill Progress

```bash
#!/bin/bash
# monitor_rowcache_refill.sh

echo "=== Row Cache Refill Monitor ==="
echo "Press Ctrl+C to stop"
echo ""

while true; do
    info=$(nodetool info 2>/dev/null | grep -A 2 "Row Cache")
    entries=$(echo "$info" | grep "entries" | awk '{print $4}')
    hit_rate=$(echo "$info" | grep "hit rate" | awk '{print $4}')
    size=$(echo "$info" | grep "size" | awk '{print $4}')

    echo "$(date '+%H:%M:%S') - Entries: $entries, Hit Rate: $hit_rate, Size: $size"
    sleep 10
done
```

### Monitor Read Latency Impact

```bash
# Watch read latency during cache rebuild
watch -n 10 'nodetool proxyhistograms | head -15'
```

---

## Workflow: Controlled Row Cache Clear

```bash
#!/bin/bash
# controlled_rowcache_clear.sh

echo "=== Controlled Row Cache Clear ==="
echo ""

# 1. Check current state
echo "1. Current row cache status:"
nodetool info | grep -A 3 "Row Cache"

# 2. Check cache dependency
entries=$(nodetool info 2>/dev/null | grep -A 1 "Row Cache" | grep "entries" | awk '{print $4}')
echo ""
echo "2. Current entries: $entries"

if [ "$entries" -gt 100000 ]; then
    echo "   WARNING: Large cache, invalidation will have significant impact!"
fi

# 3. Record baseline
echo ""
echo "3. Baseline read latencies (p99):"
nodetool proxyhistograms | grep -E "Read|percentile" | head -5

# 4. Confirm
echo ""
read -p "Proceed with row cache invalidation? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "Aborted."
    exit 1
fi

# 5. Invalidate
echo ""
echo "5. Invalidating row cache..."
start_time=$(date +%s)
nodetool invalidaterowcache

# 6. Verify
echo ""
echo "6. Cache status after invalidation:"
nodetool info | grep -A 3 "Row Cache"

# 7. Monitor impact
echo ""
echo "7. Monitoring read latency impact (60 seconds)..."
for i in {1..6}; do
    sleep 10
    p99=$(nodetool proxyhistograms 2>/dev/null | grep "Read" | head -1 | awk '{print $4}')
    entries=$(nodetool info 2>/dev/null | grep -A 1 "Row Cache" | grep "entries" | awk '{print $4}')
    echo "  $(date '+%H:%M:%S') - Read p99: ${p99}us, Cache entries: $entries"
done

echo ""
echo "=== Complete ==="
```

---

## Cluster-Wide Operations

### Rolling Invalidation (Recommended)

```bash
#!/bin/bash
# rolling_rowcache_invalidate.sh

echo "=== Rolling Row Cache Invalidation ==="
echo ""

nodes=$(nodetool status | grep "^UN" | awk '{print $2}')
WAIT_TIME=600  # 10 minutes between nodes

for node in $nodes; do
    echo "$(date): Processing $node..."

    # Check current cache size
    entries=$(nodetool -h $node info 2>/dev/null | grep -A 1 "Row Cache" | grep "entries" | awk '{print $4}')
    echo "  Current entries: $entries"

    # Invalidate
    echo "  Invalidating..."
    nodetool -h $node invalidaterowcache

    # Wait for cache to warm
    echo "  Waiting ${WAIT_TIME}s for cache warmup..."
    sleep $WAIT_TIME

    # Check recovery
    hit_rate=$(nodetool -h $node info 2>/dev/null | grep -A 2 "Row Cache" | grep "hit rate" | awk '{print $4}')
    echo "  Hit rate after warmup: $hit_rate"
    echo ""
done

echo "=== Rolling invalidation complete ==="
```

### Simultaneous (Use with Caution)

```bash
#!/bin/bash
# WARNING: Significant performance impact

nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

echo "WARNING: Invalidating row cache on ALL nodes simultaneously!"
echo "This may cause severe performance degradation."
read -p "Continue? (yes/no): " confirm

if [ "$confirm" = "yes" ]; then
    for node in $nodes; do
        echo -n "$node: "
        nodetool -h $node invalidaterowcache 2>/dev/null && echo "invalidated" || echo "FAILED"
    done
fi
```

---

## Configuration

### Row Cache Settings

```yaml
# cassandra.yaml
row_cache_size_in_mb: 0  # Disabled by default
row_cache_save_period: 0  # Save interval (0 = disabled)
row_cache_keys_to_save: 0  # Keys to save (0 = all)
```

### Per-Table Row Caching

```sql
-- Enable row caching for a specific table
ALTER TABLE my_keyspace.hot_data
WITH caching = {'keys': 'ALL', 'rows_per_partition': 'ALL'};

-- Disable row caching
ALTER TABLE my_keyspace.hot_data
WITH caching = {'keys': 'ALL', 'rows_per_partition': 'NONE'};
```

### Check Table Caching Settings

```sql
SELECT table_name, caching
FROM system_schema.tables
WHERE keyspace_name = 'my_keyspace';
```

---

## Troubleshooting

### Row Cache Not Being Used

```bash
# Check if row cache is configured
nodetool info | grep "Row Cache"

# If size is 0, row cache is disabled
# Check cassandra.yaml row_cache_size_in_mb

# Check table-level settings
cqlsh -e "SELECT caching FROM system_schema.tables WHERE keyspace_name='my_ks' AND table_name='my_table';"
```

### Cache Not Refilling

```bash
# Verify row caching is enabled on tables
# Check if reads are occurring for cached tables
nodetool tablehistograms my_keyspace my_table | head -20
```

### Memory Pressure from Row Cache

```bash
# Check row cache size
nodetool info | grep "Row Cache"

# Reduce cache capacity if needed
nodetool setcachecapacity <key_mb> <row_mb> <counter_mb>

# Or disable row caching on specific tables
```

---

## Best Practices

!!! tip "Row Cache Guidelines"

    1. **Use rolling invalidation** - One node at a time to maintain cluster performance
    2. **Schedule during low traffic** - Minimize user impact
    3. **Allow warmup time** - Wait for cache to rebuild before next node
    4. **Monitor closely** - Watch latency and hit rates during rebuild
    5. **Consider impact** - Row cache stores entire partitions; impact is significant
    6. **Document reason** - Record why invalidation was necessary

!!! warning "Row Cache Considerations"

    Row cache is typically disabled by default because:

    - High memory consumption (stores full partitions)
    - JVM garbage collection pressure
    - Often not needed with fast SSDs
    - Key cache usually provides sufficient benefit

    Only enable row caching for specific hot tables with careful monitoring.

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [invalidatekeycache](invalidatekeycache.md) | Invalidate key cache |
| [invalidatecountercache](invalidatecountercache.md) | Invalidate counter cache |
| [info](info.md) | View cache statistics |
| [setcachecapacity](setcachecapacity.md) | Adjust cache sizes |
