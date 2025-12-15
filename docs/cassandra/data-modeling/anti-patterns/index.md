---
title: "Cassandra Data Modeling Anti-Patterns"
description: "Cassandra data modeling anti-patterns. Common mistakes and how to avoid them."
meta:
  - name: keywords
    content: "Cassandra anti-patterns, data modeling mistakes, design pitfalls"
---

# Cassandra Anti-Patterns

These patterns work fine in development and testing. They might even work in early production. Then data grows, traffic increases, and they fail—usually in ways that are not obvious without understanding Cassandra internals.

Unbounded partitions grow until reads timeout. Tombstone accumulation makes queries slower over time. ALLOW FILTERING queries that took milliseconds start taking minutes. Queue patterns create tombstones faster than compaction can remove them.

The fix is usually straightforward once the problem is understood. This guide covers each anti-pattern: why it seems reasonable, how it fails, and how to fix it.

## Anti-Pattern Severity Reference

| Anti-Pattern | Severity | Time to Impact | Symptoms |
|--------------|----------|----------------|----------|
| Unbounded partitions | Critical | Weeks-Months | Timeouts, OOM, repair failures |
| Tombstone accumulation | Critical | Days-Weeks | Increasing read latency, query failures |
| ALLOW FILTERING | Critical | Immediate | Full cluster scan, timeouts |
| Queue pattern | High | Days | Tombstones, hot partitions |
| Secondary index abuse | High | Immediate | All-node queries, high latency |
| Large IN clauses | High | Immediate | Coordinator overload |
| Collection abuse | Medium | Weeks | Memory pressure, slow writes |
| Counter misuse | Medium | Immediate | Errors, data inconsistency |
| Over-normalization | Medium | Immediate | Multiple queries per operation |

---

## Unbounded Partitions (Critical)

### The Problem

Partitions that grow without limit eventually exceed what Cassandra can handle efficiently.

```sql
-- ANTI-PATTERN: Partition grows forever
CREATE TABLE user_activity (
    user_id UUID,
    activity_time TIMESTAMP,
    activity_type TEXT,
    details TEXT,
    PRIMARY KEY ((user_id), activity_time)
);
```

What happens over time:

```
Month 1:   1,000 rows per user        ~100 KB per partition ✓
Month 6:   50,000 rows per user       ~5 MB per partition ✓
Year 1:    500,000 rows per user      ~50 MB per partition ⚠
Year 3:    5,000,000 rows per user    ~500 MB per partition ✗
Year 5:    15,000,000 rows per user   ~1.5 GB per partition ☠
```

### What Goes Wrong

| Stage | Partition Size | Symptoms |
|-------|----------------|----------|
| **1. Read Performance Degrades** | > 100 MB | Queries slow down. "Get latest activity" now scans gigabytes to find recent rows. Bloom filters help but not enough. |
| **2. Compaction Problems** | > 500 MB | Compaction must load entire partition into memory. Compaction threads consume heap, leading to GC pauses. Other operations stall waiting for compaction to complete. |
| **3. Repair Failures** | > 1 GB | Repair streams entire partitions between nodes. Streaming 1GB over network causes timeouts. Repair fails repeatedly. Data consistency cannot be maintained. |
| **4. Cluster Instability** | > 2 GB | Nodes hosting these partitions become unresponsive. Hints queue up for unavailable nodes. Cascade failures begin. Full cluster becomes unstable. |

### Detection

```bash
# Check partition size distribution
nodetool tablehistograms keyspace.user_activity

# Warning signs in output:
# 99th percentile partition size > 100MB
# Max partition size > 500MB

# Check for large partition warnings in logs
grep "Compacting large partition" /var/log/cassandra/system.log
grep "Writing large partition" /var/log/cassandra/system.log
```

### Solution: Time Bucketing

```sql
-- CORRECT: Bounded partitions by time bucket
CREATE TABLE user_activity (
    user_id UUID,
    month TEXT,              -- '2024-01'
    activity_time TIMESTAMP,
    activity_type TEXT,
    details TEXT,
    PRIMARY KEY ((user_id, month), activity_time)
) WITH CLUSTERING ORDER BY (activity_time DESC);
```

Now each partition covers one month:

```
user_id=alice, month='2024-01': 40,000 rows, ~4 MB ✓
user_id=alice, month='2024-02': 38,000 rows, ~3.8 MB ✓
user_id=alice, month='2024-03': 42,000 rows, ~4.2 MB ✓
```

### Migration Strategy

For existing unbounded partitions:

```sql
-- 1. Create new time-bucketed table
CREATE TABLE user_activity_v2 (...);

-- 2. Migrate data in application
-- Read from old table, write to new with bucket

-- 3. Dual-write during transition
-- Write to both tables

-- 4. Switch reads to new table

-- 5. Drop old table after validation
```

---

## Tombstone Accumulation (Critical)

### The Problem

Every DELETE in Cassandra creates a tombstone—a marker that says "this data was deleted." Tombstones must be scanned during reads until they're purged by compaction.

```sql
-- ANTI-PATTERN: High-frequency deletes
CREATE TABLE message_queue (
    queue_id TEXT,
    message_id TIMEUUID,
    payload TEXT,
    PRIMARY KEY ((queue_id), message_id)
);

-- Application pattern
INSERT INTO message_queue (...) VALUES (...);
-- Process message
DELETE FROM message_queue WHERE queue_id = ? AND message_id = ?;
-- Repeat thousands of times per hour
```

### What Goes Wrong

```
Day 1:   100 live rows, 1,000 tombstones
         Read scans 1,100 entries to return 100 rows
         Query time: 5ms

Day 7:   100 live rows, 50,000 tombstones
         Read scans 50,100 entries to return 100 rows
         Query time: 200ms

Day 30:  100 live rows, 500,000 tombstones
         Read scans 500,100 entries to return 100 rows
         Query time: 2,000ms → TIMEOUT

         Eventually: TombstoneOverwhelmingException
         Query fails at tombstone_failure_threshold (default 100,000)
```

### Why Tombstones Persist

Tombstones cannot be removed until:
1. `gc_grace_seconds` has passed (default 10 days)
2. All replicas have the tombstone (ensured by repair)
3. Compaction runs and merges SSTables containing the tombstone

| Day | Event | Notes |
|-----|-------|-------|
| 0 | DELETE executed | Tombstone created |
| 1-9 | Tombstone must stay | `gc_grace_seconds` = 10 days |
| 10 | Tombstone eligible for removal | Requires compaction to actually remove |
| ?? | Compaction runs | Tombstone finally removed |

!!! warning "Tombstone Removal Risks"
    - If repair has not run: Tombstone removal is **unsafe** (data resurrection risk)
    - If compaction is behind: Tombstone persists indefinitely

### Detection

```sql
-- Enable query tracing
TRACING ON;
SELECT * FROM message_queue WHERE queue_id = 'orders';

-- Look for in trace output:
-- "Read 100 live rows and 50000 tombstone cells"
```

```bash
# Check tombstone metrics
nodetool tablestats keyspace.message_queue | grep -i tombstone

# Check for warnings in logs
grep "tombstone" /var/log/cassandra/system.log
grep "TombstoneOverwhelmingException" /var/log/cassandra/system.log

# cassandra.yaml thresholds
tombstone_warn_threshold: 1000     # Log warning
tombstone_failure_threshold: 100000  # Fail query
```

### Solutions

**Solution 1: Use TTL instead of DELETE**

```sql
-- Let data expire automatically
INSERT INTO message_queue (queue_id, message_id, payload)
VALUES (?, now(), ?)
USING TTL 3600;  -- Expires after 1 hour

-- No explicit DELETE needed
-- TTL creates tombstones too, but predictably
```

**Solution 2: Time-windowed tables with TWCS**

```sql
CREATE TABLE message_queue (
    queue_id TEXT,
    hour TIMESTAMP,
    message_id TIMEUUID,
    payload TEXT,
    PRIMARY KEY ((queue_id, hour), message_id)
) WITH compaction = {
    'class': 'TimeWindowCompactionStrategy',
    'compaction_window_size': '1',
    'compaction_window_unit': 'HOURS'
}
AND default_time_to_live = 86400
AND gc_grace_seconds = 3600;

-- TWCS drops entire SSTables when all data expires
-- No tombstone accumulation
```

**Solution 3: Reduce gc_grace_seconds (with frequent repair)**

```sql
-- Only if repair runs more frequently than gc_grace_seconds
ALTER TABLE message_queue WITH gc_grace_seconds = 86400;  -- 1 day

-- MUST run repair daily or more frequently
-- Otherwise: data resurrection risk
```

**Solution 4: Range deletes for batch cleanup**

```sql
-- Instead of individual deletes
-- Accumulate work, then delete entire partition

-- Delete all messages older than 1 hour (partition delete)
DELETE FROM message_queue
WHERE queue_id = 'orders'
  AND message_id < minTimeuuid('2024-01-15 14:00:00');
```

---

## ALLOW FILTERING (Critical)

### The Problem

`ALLOW FILTERING` tells Cassandra to scan all partitions in a table, filtering results in memory.

```sql
-- ANTI-PATTERN: Query without partition key
SELECT * FROM users WHERE country = 'US' ALLOW FILTERING;
```

### What Actually Happens

For `SELECT * FROM users WHERE country = 'US' ALLOW FILTERING`:

| Step | Action |
|------|--------|
| 1 | Coordinator receives query |
| 2 | Coordinator sends request to **all nodes**: "Scan ALL your partitions, filter by country" |
| 3 | Each node reads every SSTable, deserializes every row, checks if `country = 'US'` |
| 4 | Each node returns matching rows to coordinator |
| 5 | Coordinator aggregates and returns results |

**Complexity**: O(n) where n = total rows in table

| Table Size | Rows Scanned |
|------------|--------------|
| 1 million users | 1 million rows |
| 10 million users | 10 million rows |
| 100 million users | 100 million rows |

### When ALLOW FILTERING Is Acceptable

In very limited cases:

```sql
-- OK: Small table (< 10,000 rows), infrequent queries
SELECT * FROM configuration WHERE feature = 'dark_mode' ALLOW FILTERING;

-- OK: Already constrained to single partition
SELECT * FROM user_orders
WHERE user_id = '550e8400-e89b-12d3-a456-426614174000'
  AND status = 'pending'
ALLOW FILTERING;
-- Only scans one partition, not entire table
```

### Solutions

**Solution 1: Create a table for the query**

```sql
-- Instead of: SELECT * FROM users WHERE country = 'US' ALLOW FILTERING

-- Create dedicated table
CREATE TABLE users_by_country (
    country TEXT,
    user_id UUID,
    username TEXT,
    email TEXT,
    PRIMARY KEY ((country), user_id)
);

-- Query without ALLOW FILTERING
SELECT * FROM users_by_country WHERE country = 'US' LIMIT 100;
```

**Solution 2: Secondary index (low-cardinality only)**

```sql
-- For low-cardinality columns (< 100 unique values)
CREATE INDEX ON users (status);  -- active/inactive/pending

-- Query uses index
SELECT * FROM users WHERE status = 'active';

-- WARNING: Still queries all nodes, but more efficiently
```

**Solution 3: SAI (Cassandra 5.0+)**

```sql
-- Storage-Attached Index for high-cardinality
CREATE CUSTOM INDEX ON users (email)
USING 'StorageAttachedIndex';

SELECT * FROM users WHERE email = 'alice@example.com';
```

---

## Queue Anti-Pattern (High)

### The Problem

Using Cassandra as a message queue combines multiple anti-patterns: tombstone accumulation, hot partitions, and race conditions.

```sql
-- ANTI-PATTERN: Queue table
CREATE TABLE job_queue (
    queue_name TEXT,
    job_id TIMEUUID,
    payload TEXT,
    status TEXT,
    PRIMARY KEY ((queue_name), job_id)
);

-- Worker pattern
WHILE true:
    -- Poll for jobs
    SELECT * FROM job_queue
    WHERE queue_name = 'processing'
    LIMIT 10;

    -- Process job

    -- Delete completed job
    DELETE FROM job_queue
    WHERE queue_name = 'processing' AND job_id = ?;
```

### What Goes Wrong

| Problem | Description |
|---------|-------------|
| **1. Tombstone Accumulation** | Every DELETE creates a tombstone. After 10,000 jobs: 10 live rows, 10,000 tombstones. SELECT scans 10,010 entries to return 10 rows. |
| **2. Hot Partition** | All workers read from same partition (`queue_name = 'processing'`). One partition handles 100% of queue traffic. Node hosting this partition is overwhelmed while others idle. |
| **3. Race Conditions** | Multiple workers poll simultaneously. Worker A and Worker B both read `job_id = 123`. Both process the same job → data corruption or duplicate processing. |
| **4. No Ordering Guarantees** | Cassandra's eventual consistency means DELETE might not be visible immediately, job might be re-read before delete propagates, and FIFO ordering is not guaranteed. |

### Solution: Use a Real Message Queue

Cassandra is not a message queue. Use:
- **Apache Kafka** - High-throughput streaming
- **RabbitMQ** - Traditional message broker
- **Amazon SQS** - Managed queue service
- **Redis Streams** - Fast in-memory queue

### If Cassandra Must Be Used for Queue-Like Patterns

```sql
-- Time-windowed processing batches
CREATE TABLE processing_batches (
    batch_hour TIMESTAMP,
    worker_id INT,           -- Partition by worker to avoid contention
    job_id TIMEUUID,
    payload TEXT,
    PRIMARY KEY ((batch_hour, worker_id), job_id)
) WITH default_time_to_live = 86400;  -- TTL instead of delete

-- Each worker owns specific partition
-- Worker 0 reads (batch_hour, worker_id=0)
-- Worker 1 reads (batch_hour, worker_id=1)
-- No contention, no deletes, bounded partitions
```

```sql
-- Status tracking without deletes
CREATE TABLE job_status (
    job_id UUID PRIMARY KEY,
    status TEXT,
    updated_at TIMESTAMP
) WITH default_time_to_live = 604800;  -- 7 days

-- Update status instead of delete
UPDATE job_status SET status = 'completed', updated_at = toTimestamp(now())
WHERE job_id = ?;
```

---

## Secondary Index Abuse (High)

### The Problem

Secondary indexes in Cassandra query all nodes in the cluster, making them expensive for primary access patterns.

```sql
-- ANTI-PATTERN: Index as primary access pattern
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    email TEXT,
    username TEXT,
    country TEXT
);

CREATE INDEX ON users (email);

-- 90% of queries use this index
SELECT * FROM users WHERE email = ?;
```

### What Happens

| Query Type | Nodes Contacted | Latency |
|------------|-----------------|---------|
| **PRIMARY KEY query** | 1-3 nodes (based on RF) | 2-5 ms |
| **Secondary index query** | ALL nodes | 20-200 ms (scales with cluster size) |

| Cluster Size | Nodes Queried (Secondary Index) |
|--------------|--------------------------------|
| 5 nodes | 5 nodes |
| 50 nodes | 50 nodes |
| 500 nodes | 500 nodes |

### When Secondary Indexes Are OK

```sql
-- OK: Low cardinality, occasional queries
CREATE INDEX ON orders (status);  -- Few values: pending, shipped, delivered

SELECT * FROM orders WHERE status = 'pending';
-- Acceptable for dashboard/reporting queries

-- OK: Combined with partition key
SELECT * FROM user_orders
WHERE user_id = ? AND status = 'pending';
-- Index only scans within one partition
```

### When to Avoid Secondary Indexes

```sql
-- BAD: High cardinality
CREATE INDEX ON users (email);      -- Millions of unique values
CREATE INDEX ON orders (order_id);  -- Every order has unique ID

-- BAD: Primary access pattern
-- If > 10% of queries use the index, create a dedicated table

-- BAD: Large result sets
SELECT * FROM users WHERE country = 'US';  -- Returns millions of rows
```

### Solution: Dedicated Table

```sql
-- Instead of index on email
CREATE TABLE users_by_email (
    email TEXT PRIMARY KEY,
    user_id UUID,
    username TEXT
);

-- Maintain both tables
BEGIN BATCH
    INSERT INTO users (user_id, email, username) VALUES (?, ?, ?);
    INSERT INTO users_by_email (email, user_id, username) VALUES (?, ?, ?);
APPLY BATCH;

-- Query by email hits single partition
SELECT user_id FROM users_by_email WHERE email = ?;
```

---

## Large IN Clauses (High)

### The Problem

Large IN clauses create parallel requests that overwhelm coordinators.

```sql
-- ANTI-PATTERN: Hundreds of values
SELECT * FROM products WHERE product_id IN (
    '550e8400-e89b-12d3-a456-426614174000',
    '550e8400-e89b-12d3-a456-426614174001',
    -- ... 500 more UUIDs ...
);
```

### What Happens

For an IN clause with 500 values:

| Step | Action |
|------|--------|
| 1 | Coordinator receives query |
| 2 | Spawns 500 sub-queries (one per value) |
| 3 | Each sub-query routes to different partition on different node(s) |
| 4 | Coordinator tracks 500 outstanding requests in memory |
| 5 | All 500 must complete before response sent |

| Problem | Impact |
|---------|--------|
| Coordinator heap pressure | Memory: 500 × (request state + response buffer) |
| Single slow sub-query | Entire query times out |
| Any failure | No partial results returned |
| Latency | = max(all sub-query latencies) |

### Solutions

**Solution 1: Batch in application**

```python
def get_products_batch(session, product_ids, batch_size=20):
    """Query in smaller batches."""
    results = []

    for i in range(0, len(product_ids), batch_size):
        batch = product_ids[i:i + batch_size]
        rows = session.execute(
            "SELECT * FROM products WHERE product_id IN %s",
            (tuple(batch),)
        )
        results.extend(rows)

    return results
```

**Solution 2: Parallel async queries**

```python
async def get_products_async(session, product_ids):
    """Individual queries, controlled parallelism."""
    stmt = session.prepare("SELECT * FROM products WHERE product_id = ?")

    # Control concurrency with semaphore
    semaphore = asyncio.Semaphore(50)

    async def fetch_one(pid):
        async with semaphore:
            return await session.execute_async(stmt, [pid])

    tasks = [fetch_one(pid) for pid in product_ids]
    results = await asyncio.gather(*tasks)
    return [row for result in results for row in result]
```

**Solution 3: Denormalize if IDs come from another query**

```sql
-- If the pattern is: Get orders → Get products for those orders
-- Consider storing product info in orders table

CREATE TABLE orders_with_products (
    order_id UUID,
    product_id UUID,
    product_name TEXT,      -- Denormalized
    product_price DECIMAL,  -- Denormalized
    quantity INT,
    PRIMARY KEY ((order_id), product_id)
);

-- Single query returns order with product details
```

### Guidelines

| IN Clause Size | Recommendation |
|----------------|----------------|
| 1-20 | Generally safe |
| 20-100 | Monitor coordinator latency |
| 100-500 | Split into batches |
| 500+ | Redesign approach |

---

## Collection Abuse (Medium)

### The Problem

Collections (LIST, SET, MAP) are stored as single cells and read/written atomically.

```sql
-- ANTI-PATTERN: Unbounded collection
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    name TEXT,
    activity_log LIST<TEXT>  -- Grows forever
);

-- Every page view appends to list
UPDATE users SET activity_log = activity_log + ['viewed product X']
WHERE user_id = ?;
```

### What Goes Wrong

```
Month 1:    100 activities     → Collection size: 10 KB
Month 6:    50,000 activities  → Collection size: 5 MB
Year 1:     500,000 activities → Collection size: 50 MB

Problems:
- Entire 50 MB collection read on any access
- Entire 50 MB collection written on any update
- Cannot query/page through collection
- Cannot TTL individual elements
- Memory pressure during serialization
```

### Collection Limits

| Limit | Issue |
|-------|-------|
| ~64KB | Cell size warning in logs |
| ~10MB | Significant performance impact |
| ~100 elements | Recommended maximum for good performance |

### Solution: Use a Table Instead

```sql
-- CORRECT: Separate table for unbounded data
CREATE TABLE user_activity (
    user_id UUID,
    activity_time TIMESTAMP,
    activity TEXT,
    PRIMARY KEY ((user_id), activity_time)
) WITH CLUSTERING ORDER BY (activity_time DESC)
  AND default_time_to_live = 2592000;  -- 30 days

-- Can query specific ranges
SELECT * FROM user_activity
WHERE user_id = ?
LIMIT 100;

-- Can TTL individual rows
-- Can page through results
-- Each row is independent
```

### When Collections Are OK

```sql
-- OK: Small, bounded collections
CREATE TABLE products (
    product_id UUID PRIMARY KEY,
    name TEXT,
    tags SET<TEXT>,              -- 5-20 tags max
    attributes MAP<TEXT, TEXT>,   -- 10-20 attributes max
    image_urls LIST<TEXT>         -- 5-10 images max
);

-- Application enforces size limits
-- Collection rarely updated after initial write
```

---

## Counter Misuse (Medium)

### The Problem

Counters have strict limitations that cause errors when violated.

```sql
-- ANTI-PATTERN: Mixing counters with non-counters
CREATE TABLE page_stats (
    page_id UUID PRIMARY KEY,
    title TEXT,           -- Non-counter
    view_count COUNTER    -- Counter
);
-- ERROR: Cannot mix counter and non-counter columns
```

```sql
-- ANTI-PATTERN: TTL on counters
UPDATE page_views USING TTL 3600
SET views = views + 1 WHERE page_id = ?;
-- ERROR: TTL is not supported on counter mutations
```

```sql
-- ANTI-PATTERN: Setting counter to specific value
UPDATE page_views SET views = 0 WHERE page_id = ?;
-- ERROR: Cannot set counter to specific value
```

### Counter Rules

| Rule | Restriction |
|------|-------------|
| **Table contents** | Counter tables can ONLY contain primary key columns and counter columns. No other column types allowed. |
| **Operations** | Counters can ONLY be incremented (`views = views + 1`) or decremented (`views = views - 1`). Cannot be set to a specific value. |
| **Limitations** | No TTL allowed. No lightweight transactions. No batches with non-counter operations. |
| **Consistency** | Eventual consistency (may show stale values). Not suitable for exact counts. Good for approximate metrics. |

### Correct Counter Usage

```sql
-- Counter table (counters only)
CREATE TABLE page_views (
    page_id UUID PRIMARY KEY,
    view_count COUNTER,
    unique_visitors COUNTER
);

-- Metadata table (separate)
CREATE TABLE page_info (
    page_id UUID PRIMARY KEY,
    title TEXT,
    url TEXT,
    created_at TIMESTAMP
);

-- Update counter
UPDATE page_views SET view_count = view_count + 1
WHERE page_id = ?;

-- Batch counter updates (counter-only batch)
BEGIN COUNTER BATCH
    UPDATE page_views SET view_count = view_count + 1 WHERE page_id = ?;
    UPDATE page_views SET unique_visitors = unique_visitors + 1 WHERE page_id = ?;
APPLY BATCH;
```

### When to Avoid Counters

If the application needs:
- Exact counts → Use application-level aggregation
- Time-windowed counts → Use pre-aggregated tables
- TTL on counts → Use regular columns with application increment
- Resettable counts → Use regular BIGINT columns

```sql
-- Alternative: Manual aggregation
CREATE TABLE daily_page_views (
    page_id UUID,
    date DATE,
    views BIGINT,
    PRIMARY KEY ((page_id), date)
);

-- Can set specific values, use TTL
UPDATE daily_page_views
SET views = views + 1  -- Application handles read-modify-write
WHERE page_id = ? AND date = toDate(now());
```

---

## Over-Normalization (Medium)

### The Problem

Applying relational normalization to Cassandra requires multiple queries and application-level joins.

```sql
-- ANTI-PATTERN: Normalized schema
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    username TEXT,
    email TEXT
);

CREATE TABLE addresses (
    address_id UUID PRIMARY KEY,
    user_id UUID,
    street TEXT,
    city TEXT,
    country TEXT
);

CREATE TABLE orders (
    order_id UUID PRIMARY KEY,
    user_id UUID,
    total DECIMAL,
    created_at TIMESTAMP
);

-- To display order with user and address:
-- Query 1: Get order
-- Query 2: Get user
-- Query 3: Get address
-- Application joins results
```

### Problems

- Multiple round-trips increase latency
- Network overhead multiplied
- No transactional guarantees across queries
- Application complexity for joins
- Inconsistent results if data changes between queries

### Solution: Denormalize for Query Patterns

```sql
-- Order display query needs: order + user info + shipping address
CREATE TABLE orders_with_details (
    order_id UUID,
    user_id UUID,
    user_name TEXT,           -- Denormalized from users
    user_email TEXT,          -- Denormalized from users
    shipping_street TEXT,     -- Denormalized from addresses
    shipping_city TEXT,
    shipping_country TEXT,
    total DECIMAL,
    created_at TIMESTAMP,
    PRIMARY KEY ((order_id))
);

-- Single query returns everything needed
SELECT * FROM orders_with_details WHERE order_id = ?;
```

### Trade-off Management

| Aspect | Trade-off |
|--------|-----------|
| **Storage** | More disk space (data duplicated) |
| **Write complexity** | Must update multiple tables on change |
| **Consistency** | Denormalized data may become stale |

| Aspect | Benefit |
|--------|---------|
| **Read performance** | Single query, single partition |
| **Latency** | Predictable, low latency |
| **Scalability** | Horizontal scaling works |

---

## Anti-Pattern Detection Checklist

### Log Analysis

```bash
# Tombstone warnings
grep -i "tombstone" /var/log/cassandra/system.log

# Large partition warnings
grep "Compacting large partition" /var/log/cassandra/system.log
grep "Writing large partition" /var/log/cassandra/system.log

# Query warnings
grep "ALLOW FILTERING" /var/log/cassandra/debug.log
grep "Slow query" /var/log/cassandra/debug.log
```

### nodetool Diagnostics

```bash
# Partition sizes
nodetool tablehistograms keyspace.table

# Tombstone metrics
nodetool tablestats keyspace.table | grep -i tombstone

# Query latencies
nodetool tablestats keyspace.table | grep -i latency
```

### Query Tracing

```sql
TRACING ON;
SELECT * FROM suspicious_table WHERE ...;
-- Analyze trace for:
-- - Tombstones scanned
-- - SSTable count
-- - Node latencies
```

### JMX Metrics

```
# Key metrics to monitor
ReadLatency, WriteLatency          - Per-table latencies
TombstoneScannedHistogram          - Tombstones per read
EstimatedPartitionSizeHistogram    - Partition size distribution
PendingCompactions                 - Compaction backlog
```

---

## Summary: Design Checklist

Before deploying any Cassandra table:

| Check | Requirement |
|-------|-------------|
| ☐ Partition key | Has high cardinality |
| ☐ Partition size | Bounded (< 100 MB) |
| ☐ Growth pattern | No unbounded growth |
| ☐ Queries | Do not require `ALLOW FILTERING` |
| ☐ Secondary indexes | Not on high-cardinality columns |
| ☐ Collections | Limited to ~100 elements |
| ☐ DELETEs | Minimized (use TTL instead) |
| ☐ Counters | Properly isolated in counter-only tables |
| ☐ Access patterns | Each pattern has a dedicated table |
| ☐ IN clauses | Limited to ~20 values |

---

## Next Steps

- **[Data Modeling Concepts](../concepts/index.md)** - Correct design patterns
- **[Time Bucketing](../patterns/time-bucketing.md)** - Partition management
- **[Performance Tuning](../../operations/performance/index.md)** - Optimization
- **[Troubleshooting](../../troubleshooting/index.md)** - Problem diagnosis
