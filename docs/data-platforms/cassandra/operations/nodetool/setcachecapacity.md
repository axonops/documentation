---
title: "nodetool setcachecapacity"
description: "Set key cache and row cache capacity in Cassandra using nodetool setcachecapacity."
meta:
  - name: keywords
    content: "nodetool setcachecapacity, cache capacity, key cache, row cache, Cassandra"
---

# nodetool setcachecapacity

Sets the capacity of the key cache, row cache, and counter cache.

---

## Synopsis

```bash
nodetool [connection_options] setcachecapacity <key-cache-capacity> <row-cache-capacity> <counter-cache-capacity>
```

## Description

`nodetool setcachecapacity` adjusts the maximum size of Cassandra's three main caches at runtime. This allows tuning cache sizes without restarting the node, useful for responding to memory pressure or optimizing for workload changes.

!!! info "Runtime Change"
    Cache capacity changes take effect immediately but don't persist across restarts. For permanent changes, update `cassandra.yaml`.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `key-cache-capacity` | Maximum size of key cache in MB |
| `row-cache-capacity` | Maximum size of row cache in MB |
| `counter-cache-capacity` | Maximum size of counter cache in MB |

---

## Examples

### Set All Cache Sizes

```bash
# Set key cache to 100MB, row cache to 0MB (disabled), counter cache to 50MB
nodetool setcachecapacity 100 0 50
```

### Increase Key Cache

```bash
# Increase key cache while keeping others unchanged
# First check current values
nodetool info | grep -E "Key Cache|Row Cache|Counter Cache"

# Then set new values
nodetool setcachecapacity 200 0 50
```

### Disable Row Cache

```bash
# Disable row cache by setting to 0
nodetool setcachecapacity 100 0 50
```

---

## Cache Types

### Key Cache

| Aspect | Description |
|--------|-------------|
| Purpose | Caches partition key locations in SSTables |
| Benefit | Reduces partition index disk reads |
| Default | 5% of heap (capped) |
| Impact of size | Larger = more partitions cached |

### Row Cache

| Aspect | Description |
|--------|-------------|
| Purpose | Caches complete partition data |
| Benefit | Eliminates disk I/O for cached partitions |
| Default | 0 (disabled) |
| Impact of size | High memory per entry, JVM pressure |

### Counter Cache

| Aspect | Description |
|--------|-------------|
| Purpose | Caches counter values |
| Benefit | Reduces counter read overhead |
| Default | min(2.5% of heap, 50MB) |
| Impact of size | Only useful with counter columns |

---

## When to Use

### Memory Pressure

Reduce cache sizes during memory emergencies:

```bash
# Reduce all caches significantly
nodetool setcachecapacity 50 0 25

# Monitor memory
watch -n 5 'nodetool info | grep -E "Heap|Cache"'
```

### Performance Tuning

Increase key cache for read-heavy workloads:

```bash
# Check current hit rates
nodetool info | grep "Key Cache"

# If hit rate is low and entries at capacity, increase size
nodetool setcachecapacity 256 0 50
```

### Disable Unused Caches

Free memory from unused caches:

```bash
# No counter columns? Disable counter cache
nodetool setcachecapacity 100 0 0
```

### Testing Different Configurations

Experiment with cache sizes without restart:

```bash
# Test larger key cache
nodetool setcachecapacity 200 0 50

# Run workload, measure metrics

# Try different size
nodetool setcachecapacity 300 0 50
```

---

## Workflow: Cache Optimization

```bash
#!/bin/bash
# cache_optimization.sh

echo "=== Cache Optimization Workflow ==="

# 1. Current state
echo "1. Current cache statistics:"
nodetool info | grep -E "Key Cache|Row Cache|Counter Cache" -A 1

# 2. Analyze hit rates
echo ""
echo "2. Analyzing hit rates..."
key_hit=$(nodetool info | grep "Key Cache" -A 1 | grep "hit rate" | awk '{print $4}')
key_entries=$(nodetool info | grep "Key Cache" -A 1 | grep "entries" | awk '{print $4}')
key_capacity=$(nodetool info | grep "Key Cache" -A 1 | grep "capacity" | awk '{print $4}')

echo "   Key Cache: Hit Rate=$key_hit, Entries=$key_entries, Capacity=$key_capacity"

# 3. Recommendations
echo ""
echo "3. Recommendations:"

# Parse hit rate (remove % if present)
hit_rate_num=$(echo $key_hit | tr -d '%')

if [ "$key_entries" = "$key_capacity" ] && [ "$hit_rate_num" -lt 90 ]; then
    echo "   - Key cache at capacity with low hit rate. Consider increasing."
fi

# 4. Ask for action
echo ""
read -p "Enter new cache sizes (key row counter) or 'skip': " sizes

if [ "$sizes" != "skip" ]; then
    echo ""
    echo "4. Applying new cache sizes..."
    nodetool setcachecapacity $sizes

    echo ""
    echo "5. New cache configuration:"
    nodetool info | grep -E "Key Cache|Row Cache|Counter Cache" -A 1
fi
```

---

## Impact Assessment

### Increasing Cache Size

| Effect | Impact |
|--------|--------|
| Memory usage | Increases |
| Hit rate | May improve |
| GC pressure | Increases (especially row cache) |
| Read performance | May improve |

### Decreasing Cache Size

| Effect | Impact |
|--------|--------|
| Memory usage | Decreases |
| Hit rate | May decrease |
| Evictions | Increase |
| Read latency | May increase |

---

## Monitoring After Change

### Watch Cache Metrics

```bash
# Monitor cache behavior after change
watch -n 10 'nodetool info | grep -E "Key Cache|Row Cache|Counter Cache" -A 1'
```

### Track Memory

```bash
# Monitor heap usage
watch -n 10 'nodetool info | grep "Heap Memory"'
```

### Verify Hit Rates

```bash
#!/bin/bash
# monitor_cache_after_change.sh

echo "Monitoring cache after size change..."
echo "Press Ctrl+C to stop"
echo ""

while true; do
    key_hit=$(nodetool info 2>/dev/null | grep "Key Cache" -A 1 | grep "hit rate" | awk '{print $4}')
    key_size=$(nodetool info 2>/dev/null | grep "Key Cache" -A 1 | grep "size" | awk '{print $4}')
    counter_hit=$(nodetool info 2>/dev/null | grep "Counter Cache" -A 1 | grep "hit rate" | awk '{print $4}')

    echo "$(date '+%H:%M:%S') - Key: $key_hit ($key_size), Counter: $counter_hit"
    sleep 30
done
```

---

## Cluster-Wide Changes

### Set on All Nodes

```bash
#!/bin/bash
# set_cache_cluster.sh

KEY_CACHE=$1
ROW_CACHE=$2
COUNTER_CACHE=$3

if [ -z "$KEY_CACHE" ] || [ -z "$ROW_CACHE" ] || [ -z "$COUNTER_CACHE" ]; then
    echo "Usage: $0 <key_cache_mb> <row_cache_mb> <counter_cache_mb>"
    exit 1
fi

echo "Setting cache capacity cluster-wide..."
echo "Key: ${KEY_CACHE}MB, Row: ${ROW_CACHE}MB, Counter: ${COUNTER_CACHE}MB"

# Get list of node IPs from local nodetool status
nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo -n "$node: "
    ssh "$node" "nodetool setcachecapacity $KEY_CACHE $ROW_CACHE $COUNTER_CACHE" && echo "OK" || echo "FAILED"
done
```

---

## Configuration Persistence

### Runtime vs Permanent

| Setting Source | Persistence | Scope |
|----------------|-------------|-------|
| `setcachecapacity` | Until restart | This node only |
| `cassandra.yaml` | Permanent | All restarts |

### Making Changes Permanent

```yaml
# cassandra.yaml (4.1+ data size format)
key_cache_size: 200MiB
row_cache_size: 0MiB
counter_cache_size: 50MiB

# Pre-4.1
# key_cache_size_in_mb: 200
# row_cache_size_in_mb: 0
# counter_cache_size_in_mb: 50
```

After editing, changes apply on next restart.

---

## Troubleshooting

### Command Fails

```bash
# Check JMX connectivity
nodetool info

# Verify arguments are valid numbers
```

### Memory Issues After Increase

```bash
# If OOM or GC issues after increase
# Reduce cache sizes
nodetool setcachecapacity 50 0 25

# Or check heap usage
nodetool gcstats
```

### Cache Not Filling After Increase

```bash
# Cache fills based on workload
# Wait for reads to populate cache

# Verify caching is enabled on tables
cqlsh -e "SELECT table_name, caching FROM system_schema.tables WHERE keyspace_name = 'my_keyspace';"
```

---

## Best Practices

!!! tip "Cache Sizing Guidelines"

    1. **Start conservative** - Begin with defaults, increase based on metrics
    2. **Monitor hit rates** - Low hit rate with full cache suggests sizing issue
    3. **Consider heap** - Caches compete with application for heap
    4. **Row cache caution** - High memory per entry, GC impact
    5. **Update cassandra.yaml** - Make permanent after testing
    6. **Cluster consistency** - Set same values across all nodes

!!! info "General Recommendations"

    - **Key cache**: Let auto-sizing work (5% of heap), increase if hit rate low at capacity
    - **Row cache**: Keep disabled (0) unless specific hot partition use case
    - **Counter cache**: Default is usually sufficient unless heavy counter usage

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [invalidatekeycache](invalidatekeycache.md) | Clear key cache |
| [invalidaterowcache](invalidaterowcache.md) | Clear row cache |
| [invalidatecountercache](invalidatecountercache.md) | Clear counter cache |
| [info](info.md) | View cache statistics |
