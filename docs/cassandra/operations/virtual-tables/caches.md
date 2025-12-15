---
title: "Caches"
description: "Cassandra caches virtual table reference. Monitor key cache, row cache, and counter cache performance."
meta:
  - name: keywords
    content: "Cassandra cache, key cache, row cache, cache hit ratio, cache monitoring"
---

# Caches

The `caches` virtual table provides statistics for all Cassandra caches, enabling monitoring of cache efficiency and capacity.

---

## Overview

Cassandra maintains several caches to reduce disk I/O and improve read performance. The `caches` table shows hit rates, sizes, and capacity for each cache.

```sql
SELECT name, capacity_bytes, size_bytes, entry_count, hit_ratio
FROM system_views.caches;
```

---

## Schema

```sql
VIRTUAL TABLE system_views.caches (
    name text PRIMARY KEY,
    capacity_bytes bigint,
    entry_count int,
    hit_count bigint,
    hit_ratio double,
    recent_hit_rate_per_second bigint,
    recent_request_rate_per_second bigint,
    request_count bigint,
    size_bytes bigint
)
```

| Column | Type | Description |
|--------|------|-------------|
| `name` | text | Cache name |
| `capacity_bytes` | bigint | Maximum configured cache size |
| `size_bytes` | bigint | Current memory used by cache |
| `entry_count` | int | Number of entries in cache |
| `hit_count` | bigint | Total cache hits since startup |
| `request_count` | bigint | Total cache requests since startup |
| `hit_ratio` | double | Hit rate (0.0-1.0) |
| `recent_hit_rate_per_second` | bigint | Recent hits per second |
| `recent_request_rate_per_second` | bigint | Recent requests per second |

---

## Cache Types

### KeyCache

Caches partition index locations to avoid index file lookups.

| Aspect | Description |
|--------|-------------|
| **Purpose** | Maps partition keys to SSTable positions |
| **Impact** | Reduces disk seeks for partition lookups |
| **Size** | Configured via `key_cache_size_in_mb` |
| **Target hit ratio** | > 0.85 for active partitions |

**Configuration:**

```yaml
# cassandra.yaml
key_cache_size_in_mb: 100        # Cache size (auto if empty)
key_cache_save_period: 14400     # Save interval (seconds)
key_cache_keys_to_save: 0        # 0 = save all
```

### RowCache

Caches entire rows (off-heap). Disabled by default due to memory overhead.

| Aspect | Description |
|--------|-------------|
| **Purpose** | Stores complete row data |
| **Impact** | Eliminates disk I/O for cached rows |
| **Size** | Per-table via `caching` option |
| **Target hit ratio** | > 0.90 if enabled |

**Enable per table:**

```sql
ALTER TABLE my_table WITH caching = {
    'keys': 'ALL',
    'rows_per_partition': '100'
};
```

!!! warning "Row Cache Considerations"
    Row cache is suitable only for:
    - Small, frequently-read rows
    - Rarely-updated data
    - Sufficient off-heap memory

    Unsuitable for:
    - Large rows
    - Frequently-updated data
    - Memory-constrained nodes

### CounterCache

Caches counter values for faster counter reads.

| Aspect | Description |
|--------|-------------|
| **Purpose** | Stores recent counter values |
| **Impact** | Reduces counter read latency |
| **Size** | Configured via `counter_cache_size_in_mb` |
| **Target hit ratio** | > 0.90 for active counters |

**Configuration:**

```yaml
# cassandra.yaml
counter_cache_size_in_mb: 50
counter_cache_save_period: 7200
```

### ChunkCache

Caches compressed SSTable chunks (Cassandra 4.0+).

| Aspect | Description |
|--------|-------------|
| **Purpose** | Stores decompressed SSTable data |
| **Impact** | Reduces decompression overhead |
| **Size** | Auto-sized based on available memory |
| **Target hit ratio** | Varies by workload |

---

## Monitoring Queries

### Cache Overview

```sql
SELECT
    name,
    size_bytes / 1048576 AS size_mb,
    capacity_bytes / 1048576 AS capacity_mb,
    entry_count,
    hit_ratio,
    recent_hit_rate_per_second AS hits_per_sec
FROM system_views.caches;
```

### Cache Efficiency

```sql
-- Cache efficiency metrics
SELECT name, hit_ratio, size_bytes, capacity_bytes
FROM system_views.caches;
```

**Interpreting hit_ratio:**

| hit_ratio | Status |
|-----------|--------|
| ≥ 0.90 | Excellent |
| 0.80–0.89 | Good |
| 0.60–0.79 | Fair |
| < 0.60 | Poor |

### Cache Pressure

```sql
-- Check cache fill levels
SELECT name, size_bytes, capacity_bytes
FROM system_views.caches;
```

Cache is at pressure when `size_bytes / capacity_bytes > 0.95`.

---

## Alerting Rules

### Low Hit Ratio Alert

```sql
-- Key cache hit ratio degradation
SELECT name, hit_ratio
FROM system_views.caches
WHERE name = 'KeyCache' AND hit_ratio < 0.80;
```

**Thresholds:**

| Cache | Warning | Critical |
|-------|---------|----------|
| KeyCache | < 0.85 | < 0.70 |
| RowCache | < 0.90 | < 0.80 |
| CounterCache | < 0.85 | < 0.70 |

### Cache Full Alert

```sql
-- Cache sizes (alert when size_bytes approaches capacity_bytes)
SELECT name, size_bytes, capacity_bytes
FROM system_views.caches;
```

Alert when `size_bytes / capacity_bytes > 0.98`.

---

## Troubleshooting

### Low Key Cache Hit Ratio

**Symptoms:**
- `KeyCache` hit_ratio < 0.80
- Increased read latency

**Common Causes:**
1. Cache too small for working set
2. Access patterns with poor locality
3. Many unique partitions accessed once

**Resolution:**
```yaml
# Increase key cache size
key_cache_size_in_mb: 200  # Increase from default
```

Monitor after change:
```sql
SELECT name, hit_ratio, entry_count
FROM system_views.caches
WHERE name = 'KeyCache';
```

### Cache Thrashing

**Symptoms:**
- Cache at capacity
- Hit ratio declining over time
- High eviction rate (not directly visible, inferred from stagnant hit_ratio with high request_rate)

**Resolution:**
1. Increase cache size if memory available
2. Review access patterns for cache-unfriendly queries
3. Consider if caching is appropriate for workload

### Counter Cache Misses

**Symptoms:**
- `CounterCache` hit_ratio low
- Counter read latency high

**Resolution:**
```yaml
# Increase counter cache
counter_cache_size_in_mb: 100
```

---

## Configuration Reference

### Key Cache Settings

```yaml
# cassandra.yaml
key_cache_size_in_mb:           # Size in MB (empty = auto: min(5% heap, 100MB))
key_cache_save_period: 14400    # Save to disk interval (seconds)
key_cache_keys_to_save: 0       # Number of keys to save (0 = all)
```

### Row Cache Settings

Row cache is configured per-table:

```sql
-- Enable row cache
ALTER TABLE keyspace.table WITH caching = {
    'keys': 'ALL',
    'rows_per_partition': '100'
};

-- Disable row cache
ALTER TABLE keyspace.table WITH caching = {
    'keys': 'ALL',
    'rows_per_partition': 'NONE'
};
```

### Counter Cache Settings

```yaml
# cassandra.yaml
counter_cache_size_in_mb:       # Size in MB (empty = auto: min(2.5% heap, 50MB))
counter_cache_save_period: 7200 # Save interval (seconds)
counter_cache_keys_to_save: 0   # Keys to save (0 = all)
```

---

## Best Practices

1. **Key Cache**: Almost always beneficial. Size should accommodate active partition count.

2. **Row Cache**: Use sparingly. Only for small, read-heavy, rarely-updated tables.

3. **Counter Cache**: Important for counter-heavy workloads. Size based on active counter count.

4. **Monitoring**: Track hit ratios over time, not just point-in-time values.

5. **Capacity Planning**: Cache working set, not entire dataset.

---

## Related Documentation

- **[Virtual Tables Overview](index.md)** - Introduction to virtual tables
- **[Metrics Tables](metrics.md)** - Latency monitoring
- **[Performance Tuning](../performance/index.md)** - Optimization strategies
- **[cassandra.yaml Reference](../configuration/cassandra-yaml/index.md)** - Cache configuration
