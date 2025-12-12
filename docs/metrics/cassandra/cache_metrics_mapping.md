---
description: "Cassandra cache dashboard metrics mapping. Key cache and row cache metrics."
meta:
  - name: keywords
    content: "cache metrics, key cache, row cache, Cassandra caching"
---

# AxonOps Cache Dashboard Metrics Mapping

This document maps the metrics used in the AxonOps Cache dashboard.

## Dashboard Overview

The Cache dashboard monitors Cassandra's caching layers including KeyCache, RowCache, and CounterCache. These caches improve read performance by storing frequently accessed data in memory. The dashboard helps optimize cache configuration and monitor cache effectiveness.

## Metrics Mapping

### Cache Metrics (Applied to all cache types)

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `cas_Cache_HitRate` | Cache hit ratio (0.0-1.0) | `scope` (KeyCache/RowCache/CounterCache), `dc`, `rack`, `host_id` |
| `cas_Cache_Size` | Current cache size in bytes | `scope`, `dc`, `rack`, `host_id` |
| `cas_Cache_Capacity` | Maximum cache capacity in bytes | `scope`, `dc`, `rack`, `host_id` |
| `cas_Cache_Entries` | Number of entries in cache | `scope`, `dc`, `rack`, `host_id` |
| `cas_Cache_Requests` | Total cache requests | `scope`, `dc`, `rack`, `host_id` |

## Cache Types

### KeyCache
- Caches partition index entries
- Enabled by default in Cassandra
- Reduces disk seeks for finding partition locations

### RowCache
- Caches entire rows of data
- Disabled by default due to memory overhead
- Useful for small, hot datasets

### CounterCache
- Caches counter column values
- Improves counter read performance
- Only applies to counter columns

## Query Examples

### KeyCache Hit Rate
```promql
cas_Cache_HitRate{scope='KeyCache',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}
```

### KeyCache Size by Group
```promql
sum(cas_Cache_Size{scope='KeyCache',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by ($groupBy)
```

### KeyCache Requests per Second
```promql
sum(cas_Cache_Requests{axonfunction='rate',scope='KeyCache',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by ($groupBy)
```

### RowCache Entries Count
```promql
sum(cas_Cache_Entries{scope='RowCache',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by ($groupBy)
```

### CounterCache Capacity
```promql
sum(cas_Cache_Capacity{scope='CounterCache',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by ($groupBy)
```

## Panel Organization

### Key Cache Section
- **KeyCache HitRate Per Node** - Line chart showing cache hit effectiveness (0-1 scale)

- **KeyCache Size** - Line chart showing memory used by cache

- **KeyCache Capacity** - Line chart showing maximum cache size

- **KeyCache Number of Entries** - Line chart showing entry count

- **KeyCache Requests Count Per Second** - Line chart showing request rate

### Row Cache Section
- **RowCache Size** - Line chart showing memory used

- **RowCache Capacity** - Line chart showing maximum size

- **RowCache Number of Entries** - Line chart showing entry count

- **RowCache Requests Count Per Second** - Line chart showing request rate

### Counter Cache Section
- **CounterCache HitRate** - Line chart showing hit ratio

- **CounterCache Size** - Line chart showing memory used

- **CounterCache Capacity** - Line chart showing maximum size

- **CounterCache Number of Entries** - Line chart showing entry count

- **CounterCache Requests Count Per Second** - Line chart showing request rate

## Filters

- **data center** (`dc`) - Filter by data center

- **rack** - Filter by rack

- **node** (`host_id`) - Filter by specific node

- **groupBy** - Dynamic grouping by dc, rack, or host_id

## Metric Aggregation

The dashboard uses the `groupBy` variable for flexible aggregation:
- Group by data center to see cache usage per DC
- Group by rack for rack-level analysis
- Group by host_id for node-level details

Legend format:
- Size metrics: `size_$groupBy`
- Capacity metrics: `capacity_$groupBy`
- Other metrics: `$groupBy`

## Important Notes

**Hit Rate Interpretation**:

   - Value between 0.0 and 1.0 (shown as `percentunit`)
   - Higher values indicate better cache effectiveness
   - Low hit rates may indicate cache size needs adjustment

**Cache Sizing**:

   - Size should not exceed Capacity
   - Monitor the Size/Capacity ratio
   - Adjust capacity in cassandra.yaml if needed

**Version Compatibility**:

   - Note states "Only Cassandra and DSE prior to version 6.0" for some metrics
   - Cache metrics may vary in newer versions

**Performance Impact**:

   - KeyCache has minimal overhead and high benefit
   - RowCache can consume significant memory
   - Monitor request rates to understand cache load

**Units**:

   - Size and Capacity: bytes (with SI units disabled)
   - Hit Rate: percentunit (0.0-1.0 scale)
   - Requests: operations per second (ops)