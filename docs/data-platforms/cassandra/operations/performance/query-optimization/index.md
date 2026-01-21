---
title: "Query Optimization for Cassandra"
description: "Cassandra query optimization. Improve CQL query performance."
meta:
  - name: keywords
    content: "Cassandra query optimization, CQL performance, slow queries"
search:
  boost: 3
---

# Query Optimization for Cassandra

Optimize CQL queries for better performance.

## Query Tracing

### Enable Tracing

```sql
-- Enable tracing
TRACING ON;

-- Run query
SELECT * FROM users WHERE user_id = 123e4567-e89b-12d3-a456-426614174000;

-- Disable tracing
TRACING OFF;
```

### Analyze Trace Output

```
Key trace events to monitor:
- Parsing query
- Preparing statement
- Reading data from disk/cache
- Merging data from multiple SSTables
- Sending response
```

## Slow Query Logging

### Configuration

```yaml
# cassandra.yaml
slow_query_log_timeout: 500ms
```

### Log Analysis

```bash
# Find slow queries
grep "slow query" /var/log/cassandra/system.log
```

## Query Patterns

### Efficient Patterns

```sql
-- ✓ Query by partition key (fastest)
SELECT * FROM orders WHERE customer_id = ?;

-- ✓ Query with partition key and clustering columns
SELECT * FROM orders
WHERE customer_id = ? AND order_date >= '2024-01-01';

-- ✓ Query specific columns
SELECT order_id, total FROM orders WHERE customer_id = ?;

-- ✓ Use prepared statements
PreparedStatement ps = session.prepare(
    "SELECT * FROM orders WHERE customer_id = ?"
);
```

### Inefficient Patterns

```sql
-- ✗ ALLOW FILTERING (full table scan)
SELECT * FROM orders WHERE status = 'pending' ALLOW FILTERING;

-- ✗ Secondary index on high-cardinality column
SELECT * FROM users WHERE user_id = ?;  -- if user_id is indexed, not PK

-- ✗ SELECT * when only a few columns are needed
SELECT * FROM wide_table WHERE id = ?;

-- ✗ IN clause with many values
SELECT * FROM users WHERE user_id IN (?, ?, ?, ... 1000 values);
```

## Batch Optimization

### Good Batches

```sql
-- ✓ Batch writes to same partition
BEGIN BATCH
  INSERT INTO user_events (user_id, event_time, event_type) VALUES (?, ?, ?);
  INSERT INTO user_events (user_id, event_time, event_type) VALUES (?, ?, ?);
  INSERT INTO user_events (user_id, event_time, event_type) VALUES (?, ?, ?);
APPLY BATCH;
```

### Bad Batches

```sql
-- ✗ Batch across multiple partitions (creates coordination overhead)
BEGIN BATCH
  INSERT INTO user_events (user_id, ...) VALUES ('user1', ...);
  INSERT INTO user_events (user_id, ...) VALUES ('user2', ...);
  INSERT INTO user_events (user_id, ...) VALUES ('user3', ...);
APPLY BATCH;
```

### Batch Guidelines

| Scenario | Recommendation |
|----------|----------------|
| Same partition | Use UNLOGGED batch |
| Multiple partitions | Use async single writes |
| Atomicity required | Use LOGGED batch (slower) |
| Counter updates | Use COUNTER batch |

## Pagination

### Token-Based Pagination

```sql
-- First page
SELECT * FROM events
WHERE bucket = '2024-01'
LIMIT 100;

-- Next page (using last token)
SELECT * FROM events
WHERE bucket = '2024-01'
  AND token(event_id) > token('last-event-id')
LIMIT 100;
```

### Driver Pagination

```java
// Java driver automatic pagination
Statement stmt = SimpleStatement.builder("SELECT * FROM large_table")
    .setPageSize(1000)
    .build();

ResultSet rs = session.execute(stmt);
for (Row row : rs) {
    // Automatically fetches next page
}
```

## Index Usage

### When to Use Secondary Indexes

```sql
-- ✓ Low cardinality, query with partition key
CREATE INDEX ON orders(status);
SELECT * FROM orders WHERE customer_id = ? AND status = 'pending';

-- ✓ SAI for better performance
CREATE CUSTOM INDEX ON orders(status) USING 'StorageAttachedIndex';
```

### When to Avoid Indexes

```sql
-- ✗ High cardinality columns
CREATE INDEX ON users(email);  -- Bad: nearly unique values

-- ✗ Frequently updated columns
CREATE INDEX ON orders(last_modified);  -- Bad: constant updates

-- ✗ Very low cardinality (boolean)
CREATE INDEX ON users(is_active);  -- Bad: only 2 values
```

## Materialized Views vs Denormalization

### Manual Denormalization (Recommended)

```sql
-- Write to both tables in application
INSERT INTO orders_by_customer (customer_id, order_id, ...) VALUES (...);
INSERT INTO orders_by_date (order_date, order_id, ...) VALUES (...);
```

### Materialized View (Use Cautiously)

```sql
CREATE MATERIALIZED VIEW orders_by_status AS
  SELECT * FROM orders
  WHERE status IS NOT NULL AND order_id IS NOT NULL
  PRIMARY KEY (status, order_id);
```

## Read Performance

### Reduce Read Latency

```yaml
# cassandra.yaml - tune read settings

# Increase key cache
key_cache_size_in_mb: 100

# Increase row cache for hot rows (use sparingly)
row_cache_size_in_mb: 0  # Disabled by default

# Read-ahead for sequential scans
disk_optimization_strategy: ssd
```

### Consistency Level Trade-offs

| CL | Latency | Consistency |
|----|---------|-------------|
| ONE | Fastest | Eventual |
| LOCAL_QUORUM | Moderate | Strong (local) |
| QUORUM | Higher | Strong |
| ALL | Highest | Strongest |

## Write Performance

### Tune Write Path

```yaml
# cassandra.yaml

# Commitlog settings
commitlog_sync: periodic
commitlog_sync_period_in_ms: 10000

# Memtable settings
memtable_heap_space_in_mb: 2048
memtable_offheap_space_in_mb: 2048
```

### Write Patterns

```sql
-- ✓ Async writes for non-critical data
-- Use CL=ONE or LOCAL_ONE

-- ✓ TTL for automatic cleanup
INSERT INTO session_data (...) VALUES (...) USING TTL 86400;

-- ✓ Lightweight transactions only when needed
INSERT INTO users (email, ...) VALUES (...)
IF NOT EXISTS;  -- Use sparingly
```

## Query Profiling Checklist

1. ☐ Is partition key specified?
2. ☐ Are only needed columns being selected?
3. ☐ Is ALLOW FILTERING avoided?
4. ☐ Are batches single-partition?
5. ☐ Is consistency level appropriate?
6. ☐ Are prepared statements used?
7. ☐ Is pagination implemented for large results?

---

## Next Steps

- **[Indexing](../../../cql/indexing/index.md)** - Index strategies
- **[Data Modeling](../../../data-modeling/index.md)** - Design for queries
- **[Anti-Patterns](../../../data-modeling/anti-patterns/index.md)** - What to avoid
