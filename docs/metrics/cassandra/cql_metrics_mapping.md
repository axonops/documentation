---
title: "AxonOps CQL Dashboard Metrics Mapping"
description: "Cassandra CQL dashboard metrics mapping. Query performance and prepared statements."
meta:
  - name: keywords
    content: "CQL metrics, query performance, prepared statements"
---

# AxonOps CQL Dashboard Metrics Mapping

This document maps the metrics used in the AxonOps CQL dashboard.

## Dashboard Overview

The CQL (Cassandra Query Language) dashboard monitors CQL statement execution and prepared statement management. It provides insights into query patterns, prepared statement cache efficiency, and CQL workload distribution across the cluster.

## Metrics Mapping

### CQL Statement Metrics

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `cas_CQL_PreparedStatementsExecuted` | Number of prepared statements executed | `function` (Count), `axonfunction` (rate), `dc`, `rack`, `host_id` |
| `cas_CQL_RegularStatementsExecuted` | Number of regular (non-prepared) statements executed | `function` (Count), `axonfunction` (rate), `dc`, `rack`, `host_id` |
| `cas_CQL_PreparedStatementsCount` | Current number of cached prepared statements | `function` (Value), `dc`, `rack`, `host_id` |
| `cas_CQL_PreparedStatementsRatio` | Ratio of prepared statements to total statements | `function` (Value), `dc`, `rack`, `host_id` |

## Query Examples

### Prepared Statements Executed per Second
```promql
sum(cas_CQL_PreparedStatementsExecuted{axonfunction='rate',function='Count',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by ($groupBy)
```

### Regular Statements Executed per Second
```promql
sum(cas_CQL_RegularStatementsExecuted{axonfunction='rate',function='Count',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by ($groupBy)
```

### Number of Cached Prepared Statements
```promql
cas_CQL_PreparedStatementsCount{function='Value',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}
```

### Prepared Statements Evicted per Second
```promql
cas_CQL_PreparedStatementsCount{axonfunction='rate',function='Value',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}
```

### Prepared Statements Ratio
```promql
cas_CQL_PreparedStatementsRatio{function='Value',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}
```

## Panel Organization

### CQL Stats Section
- **Prepared Statements Executed per Second** - Rate of prepared statement execution

- **Regular Statements Executed per Second** - Rate of regular statement execution

- **Number of Cached Prepared Statements per Node** - Current cache size

- **Prepared Statements Evicted per Second per Node** - Cache eviction rate

- **Prepared Statements Ratio per Node** - Ratio of prepared to total statements

## Filters

- **data center** (`dc`) - Filter by data center

- **rack** - Filter by rack

- **node** (`host_id`) - Filter by specific node

- **groupBy** - Dynamic grouping (dc, rack, host_id, keyspace)

## Important Metrics Explained

### Prepared vs Regular Statements
- **Prepared Statements**: Pre-parsed and optimized queries with placeholders

- **Regular Statements**: Ad-hoc queries parsed on each execution

- Prepared statements are more efficient for repeated queries

### Prepared Statement Count
- Shows current number of statements in cache
- High values may indicate memory pressure
- Monitor for cache size limits

### Eviction Rate
- When `axonfunction='rate'` is applied to PreparedStatementsCount
- Indicates cache pressure when positive
- High eviction rates impact performance

### Prepared Statements Ratio
- Percentage of executed statements that are prepared
- Higher ratios indicate better query optimization
- Low ratios suggest opportunities for optimization

## Best Practices

**Maximize Prepared Statement Usage**:

   - Aim for high prepared statement ratio (>90%)
   - Use prepared statements for all repeated queries
   - Avoid string concatenation in queries

**Monitor Cache Size**:

   - Watch for increasing cache counts
   - Set appropriate cache size limits
   - Monitor memory usage

**Track Eviction Rates**:

   - Zero evictions is ideal
   - Positive rates indicate cache thrashing
   - May need to increase cache size or optimize queries

**Analyze Query Patterns**:

   - Group by keyspace to identify heavy users
   - Compare prepared vs regular by node
   - Look for imbalanced query distribution

## Performance Considerations

**Prepared Statement Benefits**:

   - Reduced parsing overhead
   - Better performance for repeated queries
   - Protection against CQL injection

**Cache Management**:

   - Each unique prepared statement uses memory
   - Too many unique statements can cause evictions
   - Balance between reuse and memory usage

**Regular Statement Overhead**:

   - Each execution requires full parsing
   - Higher CPU usage on coordinator
   - Should be minimized in production

## Units and Display

- **Execution Rates**: statements per second (short)

- **Counts**: absolute numbers (short)

- **Ratio**: decimal between 0-1 (short)

**Legend Format**:

  - Aggregated views: `$groupBy`
  - Node-specific views: `$host_id`

## Troubleshooting

**High Regular Statement Rate**:

   - Review application code for ad-hoc queries
   - Convert repeated patterns to prepared statements
   - Check for dynamic query generation

**High Eviction Rate**:

   - Increase prepared statement cache size
   - Review for unique statement explosion
   - Consider query consolidation

**Low Prepared Statement Ratio**:

   - Audit application query patterns
   - Implement prepared statement best practices
   - Monitor after code changes

## Notes

- The `groupBy` filter includes keyspace for workload analysis
- Rate calculations use `axonfunction='rate'` for per-second metrics
- All metrics are collected at the coordinator level
- Cache metrics reflect local node state, not cluster-wide