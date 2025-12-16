---
title: "Metrics Tables"
description: "Cassandra virtual tables for latency metrics, read statistics, and CQL performance monitoring."
meta:
  - name: keywords
    content: "Cassandra metrics, latency monitoring, tombstones per read, CQL metrics"
---

# Metrics Tables

The metrics virtual tables provide latency measurements, read statistics, and CQL-specific metrics for monitoring Cassandra performance.

---

## Latency Metrics

### Coordinator Latency Tables

These tables measure the full request lifecycle from the coordinator's perspective, including network time to replicas.

#### coordinator_read_latency

```sql
VIRTUAL TABLE system_views.coordinator_read_latency (
    keyspace_name text,
    table_name text,
    count bigint,
    max_ms double,
    p50th_ms double,
    p99th_ms double,
    per_second double,
    PRIMARY KEY ((keyspace_name, table_name))
)
```

| Column | Type | Description |
|--------|------|-------------|
| `keyspace_name` | text | Keyspace name |
| `table_name` | text | Table name |
| `count` | bigint | Total read operations |
| `p50th_ms` | double | Median latency (milliseconds) |
| `p99th_ms` | double | 99th percentile latency |
| `max_ms` | double | Maximum observed latency |
| `per_second` | double | Current operations per second |

**Example:**

```sql
-- Find tables with high read latency
SELECT keyspace_name, table_name, p99th_ms, max_ms, per_second
FROM system_views.coordinator_read_latency
WHERE p99th_ms > 50;
```

#### coordinator_write_latency

Same schema as `coordinator_read_latency`, measuring write operations.

```sql
-- Read latency by table
SELECT keyspace_name, table_name, p99th_ms
FROM system_views.coordinator_read_latency
WHERE p99th_ms > 10;

-- Write latency by table
SELECT keyspace_name, table_name, p99th_ms
FROM system_views.coordinator_write_latency
WHERE p99th_ms > 10;
```

#### coordinator_scan_latency

Same schema, measuring range scan operations (queries returning multiple rows).

```sql
-- Find tables with expensive scans
SELECT keyspace_name, table_name, p99th_ms, count
FROM system_views.coordinator_scan_latency
WHERE p99th_ms > 100;
```

### Local Latency Tables

These tables measure time spent on the local node only, excluding network overhead. Useful for isolating local vs network issues.

#### local_read_latency / local_write_latency / local_scan_latency

Same schema as coordinator tables, but measuring local processing time only.

```sql
-- Coordinator latency (includes network time)
SELECT keyspace_name, table_name, p99th_ms AS coordinator_p99
FROM system_views.coordinator_read_latency
WHERE p99th_ms > 20;

-- Local latency (local processing only)
SELECT keyspace_name, table_name, p99th_ms AS local_p99
FROM system_views.local_read_latency
WHERE p99th_ms > 20;

-- Compare results: if coordinator_p99 >> local_p99, network is the bottleneck
```

**Interpretation:**

| Scenario | Coordinator p99 | Local p99 | Diagnosis |
|----------|-----------------|-----------|-----------|
| Both high | 100ms | 90ms | Local disk/CPU issue |
| Coordinator high, local low | 100ms | 10ms | Network or remote replica issue |
| Both low | 5ms | 4ms | Healthy |

---

## Read Statistics

### rows_per_read

Tracks how many rows are returned per read operation. High values may indicate inefficient queries or oversized partitions.

```sql
VIRTUAL TABLE system_views.rows_per_read (
    keyspace_name text,
    table_name text,
    count bigint,
    max double,
    p50th double,
    p99th double,
    PRIMARY KEY ((keyspace_name, table_name))
)
```

| Column | Type | Description |
|--------|------|-------------|
| `keyspace_name` | text | Keyspace name |
| `table_name` | text | Table name |
| `count` | bigint | Number of reads sampled |
| `p50th` | double | Median rows per read |
| `p99th` | double | 99th percentile rows per read |
| `max` | double | Maximum rows in a single read |

**Example:**

```sql
-- Find tables returning many rows per query
SELECT keyspace_name, table_name, p50th, p99th, max
FROM system_views.rows_per_read
WHERE max > 1000;
```

**Warning thresholds:**

| Metric | Normal | Warning | Critical |
|--------|--------|---------|----------|
| `p50th` | < 100 | 100-1000 | > 1000 |
| `p99th` | < 1000 | 1000-10000 | > 10000 |
| `max` | < 10000 | 10000-100000 | > 100000 |

### tombstones_per_read

Tracks tombstone encounters during reads. High values indicate deletion patterns causing performance degradation.

```sql
VIRTUAL TABLE system_views.tombstones_per_read (
    keyspace_name text,
    table_name text,
    count bigint,
    max double,
    p50th double,
    p99th double,
    PRIMARY KEY ((keyspace_name, table_name))
)
```

| Column | Type | Description |
|--------|------|-------------|
| `keyspace_name` | text | Keyspace name |
| `table_name` | text | Table name |
| `count` | bigint | Number of reads sampled |
| `p50th` | double | Median tombstones per read |
| `p99th` | double | 99th percentile tombstones |
| `max` | double | Maximum tombstones in a single read |

**Example:**

```sql
-- Find tables with tombstone problems
SELECT keyspace_name, table_name, p50th, p99th, max
FROM system_views.tombstones_per_read
WHERE p99th > 100;
```

!!! warning "Tombstone Thresholds"
    | Metric | Normal | Warning | Critical |
    |--------|--------|---------|----------|
    | `p50th` | < 10 | 10-100 | > 100 |
    | `p99th` | < 100 | 100-1000 | > 1000 |
    | `max` | < 1000 | 1000-10000 | > 10000 (may cause `TombstoneOverwhelmingException`) |

**Common causes of high tombstone counts:**

- Queue-like access patterns (insert, process, delete)
- Wide partitions with range deletes
- TTL expiration on many cells
- Frequent null updates

---

## Batch Metrics

### batch_metrics

Metrics specific to BATCH statement execution.

```sql
VIRTUAL TABLE system_views.batch_metrics (
    name text PRIMARY KEY,
    max bigint,
    p50th double,
    p999th double,
    p99th double
)
```

| Metric Name | Description |
|-------------|-------------|
| `partitions_per_logged_batch` | Partitions touched per logged batch |
| `partitions_per_unlogged_batch` | Partitions touched per unlogged batch |
| `partitions_per_counter_batch` | Partitions touched per counter batch |

**Example:**

```sql
SELECT name, p50th, p99th, max
FROM system_views.batch_metrics;
```

```
 name                          | p50th | p99th | max
-------------------------------+-------+-------+-----
 partitions_per_logged_batch   |   1.0 |   3.0 |  15
 partitions_per_unlogged_batch |   1.0 |   1.0 |   5
 partitions_per_counter_batch  |   1.0 |   1.0 |   2
```

!!! warning "Multi-Partition Batches"
    High `partitions_per_logged_batch` values indicate anti-pattern usage:
    - `p99th > 5`: Review batch usage patterns
    - `max > 50`: Likely misusing batches for bulk loading

    See [BATCH documentation](../../cql/dml/batch.md) for proper batch usage.

---

## CQL Metrics

### cql_metrics

CQL layer metrics including prepared statement cache statistics.

```sql
VIRTUAL TABLE system_views.cql_metrics (
    name text PRIMARY KEY,
    value double
)
```

| Metric Name | Description |
|-------------|-------------|
| `prepared_statements_count` | Number of prepared statements in cache |
| `prepared_statements_evicted` | Prepared statements evicted from cache |
| `prepared_statements_executed` | Total prepared statement executions |
| `regular_statements_executed` | Total non-prepared statement executions |
| `prepared_statements_ratio` | Ratio of prepared to total statements |

**Example:**

```sql
SELECT name, value FROM system_views.cql_metrics;
```

```
 name                          | value
-------------------------------+------------
 prepared_statements_count     |       1247
 prepared_statements_evicted   |         23
 prepared_statements_executed  |  987654321
 regular_statements_executed   |      12345
 prepared_statements_ratio     |   0.999987
```

!!! tip "Prepared Statement Best Practices"
    | Metric | Healthy | Warning |
    |--------|---------|---------|
    | `prepared_statements_ratio` | > 0.95 | < 0.90 |
    | `prepared_statements_evicted` | Low/stable | Growing rapidly |

    Low ratio indicates applications not using prepared statements—causes:
    - Higher CPU usage for query parsing
    - Larger network payloads
    - No query plan caching benefits

---

## Monitoring Queries

### Performance Dashboard Queries

```sql
-- Read latency overview
SELECT keyspace_name, table_name, count, p50th_ms, p99th_ms, per_second
FROM system_views.coordinator_read_latency
WHERE per_second > 0;

-- Write latency overview
SELECT keyspace_name, table_name, count, p50th_ms, p99th_ms, per_second
FROM system_views.coordinator_write_latency
WHERE per_second > 0;

-- Scan latency overview
SELECT keyspace_name, table_name, count, p50th_ms, p99th_ms, per_second
FROM system_views.coordinator_scan_latency
WHERE per_second > 0;
```

### Alerting Queries

```sql
-- Alert: High read latency
SELECT keyspace_name, table_name, p99th_ms
FROM system_views.coordinator_read_latency
WHERE p99th_ms > 100;

-- Alert: Tombstone accumulation
SELECT keyspace_name, table_name, p99th, max
FROM system_views.tombstones_per_read
WHERE p99th > 500;

-- Alert: Poor prepared statement usage
SELECT name, value
FROM system_views.cql_metrics
WHERE name = 'prepared_statements_ratio'
  AND value < 0.90;
```

---

## Related Documentation

- **[Virtual Tables Overview](index.md)** - Introduction to virtual tables
- **[Thread Pools](thread-pools.md)** - Thread pool monitoring
- **[Performance Tuning](../performance/index.md)** - Optimization strategies
