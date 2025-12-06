# CQL Reference

CQL looks like SQL, which is both its strength and its trap. The `SELECT`, `INSERT`, `UPDATE`, and `DELETE` statements feel familiar—but the rules underneath are completely different.

Running `SELECT * FROM users WHERE email = 'test@example.com'` without a partition key or index causes Cassandra to refuse the query. Running `SELECT * FROM users` on a large table causes a timeout. These are not bugs; Cassandra is protecting against queries that would scan the entire cluster.

Understanding why CQL has these constraints—how queries route through the cluster, how partition keys determine data placement—is the key to using it effectively. This reference covers both the syntax and the mechanics.

## Understanding CQL's Distributed Nature

Every CQL query is executed in a distributed environment. Understanding how queries are processed helps with writing efficient CQL and avoiding common pitfalls.

```
Client Query → Coordinator Node → Replica Nodes → Response Aggregation → Client
      │              │                  │                 │
      │              │                  │                 └── Merge results from replicas
      │              │                  └── Parallel requests to replica nodes
      │              └── Hash partition key to find replicas
      └── Connected to any node (becomes coordinator)
```

### Query Execution Flow

```sql
SELECT * FROM users WHERE user_id = '550e8400-e29b-41d4-a716-446655440000';
```

1. **Coordinator receives query** - The connected node becomes the coordinator
2. **Partition key hashed** - `user_id` is hashed to determine which nodes hold the data
3. **Replicas contacted** - Based on consistency level (e.g., QUORUM means majority of replicas)
4. **Results returned** - Coordinator aggregates and returns response

This is fundamentally different from SQL databases where queries hit a single database server.

---

## CQL vs SQL: Critical Differences

| Aspect | SQL (RDBMS) | CQL (Cassandra) |
|--------|-------------|-----------------|
| **Query flexibility** | Any column, any time | Must include partition key |
| **JOINs** | Full support | Not supported |
| **Schema changes** | Expensive ALTER TABLE | Instant ADD/DROP columns |
| **WHERE clause** | Any conditions | Restricted to key columns |
| **ORDER BY** | Any column | Only clustering columns |
| **GROUP BY** | Any columns | Partition + clustering keys |
| **Subqueries** | Full support | Not supported |
| **Transactions** | ACID | Limited (LWT only) |
| **Aggregations** | Efficient | Limited, expensive |
| **OFFSET** | Supported | Not supported (use tokens) |

### Why These Differences Matter

```sql
-- Works in SQL, FAILS in CQL (without index or ALLOW FILTERING)
SELECT * FROM users WHERE email = 'john@example.com';

-- CQL requires partition key
SELECT * FROM users WHERE user_id = ?;

-- To query by email, create a separate table
CREATE TABLE users_by_email (
    email TEXT PRIMARY KEY,
    user_id UUID,
    username TEXT
);
```

**CQL's restrictions exist because:**
- Queries without partition key require scanning ALL nodes
- Scanning all nodes does not scale
- Predictable performance requires predictable query patterns

---

## CQL Version Compatibility

| CQL Version | Cassandra Version | Key Features |
|-------------|-------------------|--------------|
| CQL 3.0 | 2.0+ | Collections, lightweight transactions |
| CQL 3.4 | 3.0+ | Materialized views, JSON support, UDFs |
| CQL 3.4.5 | 4.0+ | Virtual tables, audit logging, duration type |
| CQL 3.4.6 | 4.1+ | CONTAINS KEY for maps, improved aggregations |
| CQL 3.4.7 | 5.0+ | Vectors, SAI, unified compaction |

---

## Core CQL Concepts

### Primary Key Structure

The primary key is the most important aspect of table design:

```sql
PRIMARY KEY ((partition_key), clustering_col1, clustering_col2)
            └──────┬──────┘  └────────────┬────────────────┘
        Data distribution         Sort order within partition
```

**Partition Key** (inside double parentheses):
- Determines which node stores the data
- All rows with same partition key stored together
- Must be included in all queries (or use ALLOW FILTERING)

**Clustering Columns** (after partition key):
- Define sort order within a partition
- Enable range queries
- Must be queried in order (columns cannot be skipped)

```sql
-- Three primary key patterns

-- 1. Simple: Single partition key, no clustering
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    username TEXT
);

-- 2. Compound: Single partition key with clustering
CREATE TABLE messages (
    user_id UUID,
    sent_at TIMESTAMP,
    message_id UUID,
    content TEXT,
    PRIMARY KEY ((user_id), sent_at, message_id)
) WITH CLUSTERING ORDER BY (sent_at DESC);

-- 3. Composite: Multiple partition keys
CREATE TABLE events (
    tenant_id TEXT,
    date DATE,
    event_time TIMESTAMP,
    event_id UUID,
    PRIMARY KEY ((tenant_id, date), event_time)
);
```

### Clustering Order

Defines how rows are physically stored and returned:

```sql
CREATE TABLE sensor_readings (
    sensor_id TEXT,
    reading_time TIMESTAMP,
    value DOUBLE,
    PRIMARY KEY ((sensor_id), reading_time)
) WITH CLUSTERING ORDER BY (reading_time DESC);

-- Query returns newest first
SELECT * FROM sensor_readings WHERE sensor_id = 'temp-001' LIMIT 10;

-- Can reverse order in query
SELECT * FROM sensor_readings WHERE sensor_id = 'temp-001'
ORDER BY reading_time ASC LIMIT 10;
```

**Important:** ORDER BY only works with clustering columns, and only in the defined order or its complete reverse.

---

## Query Patterns and Efficiency

### Efficient Queries (Use These)

```sql
-- By partition key (single partition, single node group)
SELECT * FROM users WHERE user_id = ?;

-- By partition key with clustering range
SELECT * FROM messages
WHERE user_id = ?
  AND sent_at >= '2024-01-01'
  AND sent_at < '2024-02-01';

-- Multiple partition keys with IN (use sparingly)
SELECT * FROM users WHERE user_id IN (?, ?, ?);
```

### Inefficient Queries (Avoid These)

```sql
-- Missing partition key (full cluster scan)
SELECT * FROM users WHERE username = 'john' ALLOW FILTERING;

-- Range on partition key (hits all nodes)
SELECT * FROM users WHERE token(user_id) > ? AND token(user_id) < ?;

-- Large IN clause (parallel queries to many partitions)
SELECT * FROM users WHERE user_id IN (/* 100+ values */);
```

### Query Efficiency Matrix

| Query Pattern | Nodes Hit | Efficiency | Use Case |
|---------------|-----------|------------|----------|
| Partition key equality | 1-3 (RF) | Excellent | Primary access |
| Partition + clustering range | 1-3 (RF) | Excellent | Time-series |
| Partition + IN (< 10 values) | 1-3 × N | Good | Batch lookup |
| Secondary index | All nodes | Poor | Occasional queries |
| ALLOW FILTERING | All nodes | Very Poor | Avoid in production |

---

## Data Type Quick Reference

### Commonly Used Types

| Type | Description | Size | Example |
|------|-------------|------|---------|
| `UUID` | Random unique identifier | 16 bytes | `uuid()` |
| `TIMEUUID` | Time-based UUID (v1) | 16 bytes | `now()` |
| `TEXT` | UTF-8 string | Variable | `'hello'` |
| `INT` | 32-bit signed integer | 4 bytes | `42` |
| `BIGINT` | 64-bit signed integer | 8 bytes | `9223372036854775807` |
| `TIMESTAMP` | Date/time (ms precision) | 8 bytes | `'2024-01-15 10:30:00'` |
| `DATE` | Date only | 4 bytes | `'2024-01-15'` |
| `BOOLEAN` | True/false | 1 byte | `true` |
| `DOUBLE` | 64-bit floating point | 8 bytes | `3.14159` |
| `DECIMAL` | Arbitrary precision | Variable | `123.456` |
| `BLOB` | Binary data | Variable | `0x48656c6c6f` |

### Collection Types

```sql
-- List: Ordered, allows duplicates
tags LIST<TEXT>
-- Operations: append (+), prepend, index access [i], remove (-)

-- Set: Unordered, unique values
categories SET<TEXT>
-- Operations: add (+), remove (-)

-- Map: Key-value pairs
preferences MAP<TEXT, TEXT>
-- Operations: put ([key]=), add (+), remove (DELETE key)

-- IMPORTANT: Collections should have < 100 elements
-- For larger datasets, use separate tables
```

### Special Types

```sql
-- Counter: Only increment/decrement
page_views COUNTER
-- Cannot be part of primary key
-- Cannot mix with non-counter columns in same table

-- TIMEUUID for time-ordered unique IDs
event_id TIMEUUID
-- Includes timestamp, can query by time range using minTimeuuid/maxTimeuuid

-- Duration: Time periods (not usable in primary key)
retention DURATION
-- Examples: '1h30m', '2d', '1y2mo3d4h5m6s'
```

---

## Essential Statements

### Data Definition (DDL)

```sql
-- Create keyspace (production)
CREATE KEYSPACE my_app WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3,
    'dc2': 3
};

-- Create table with all options
CREATE TABLE events (
    tenant_id TEXT,
    date DATE,
    event_time TIMESTAMP,
    event_id UUID,
    event_type TEXT,
    payload TEXT,
    PRIMARY KEY ((tenant_id, date), event_time, event_id)
) WITH CLUSTERING ORDER BY (event_time DESC, event_id ASC)
  AND compaction = {
      'class': 'TimeWindowCompactionStrategy',
      'compaction_window_unit': 'DAYS',
      'compaction_window_size': '1'
  }
  AND default_time_to_live = 2592000   -- 30 days
  AND gc_grace_seconds = 86400          -- 1 day
  AND compression = {'class': 'LZ4Compressor'};

-- Modify table (instant operations)
ALTER TABLE events ADD metadata MAP<TEXT, TEXT>;
ALTER TABLE events DROP payload;
ALTER TABLE events WITH default_time_to_live = 604800;
```

### Data Manipulation (DML)

```sql
-- Insert (also acts as upsert)
INSERT INTO events (tenant_id, date, event_time, event_id, event_type)
VALUES ('acme', '2024-01-15', toTimestamp(now()), uuid(), 'page_view');

-- Insert with TTL (expires after 1 hour)
INSERT INTO events (tenant_id, date, event_time, event_id, event_type)
VALUES ('acme', '2024-01-15', toTimestamp(now()), uuid(), 'temp_event')
USING TTL 3600;

-- Update
UPDATE events SET event_type = 'click'
WHERE tenant_id = 'acme'
  AND date = '2024-01-15'
  AND event_time = ?
  AND event_id = ?;

-- Delete row
DELETE FROM events
WHERE tenant_id = 'acme'
  AND date = '2024-01-15'
  AND event_time = ?
  AND event_id = ?;

-- Delete range (clustering column range)
DELETE FROM events
WHERE tenant_id = 'acme'
  AND date = '2024-01-15'
  AND event_time < '2024-01-15 12:00:00';
```

### Queries

```sql
-- Basic select
SELECT * FROM events
WHERE tenant_id = 'acme' AND date = '2024-01-15'
LIMIT 100;

-- Select specific columns
SELECT event_time, event_type FROM events
WHERE tenant_id = 'acme' AND date = '2024-01-15';

-- Time range query
SELECT * FROM events
WHERE tenant_id = 'acme'
  AND date = '2024-01-15'
  AND event_time >= '2024-01-15 09:00:00'
  AND event_time < '2024-01-15 18:00:00';

-- Aggregation (within partition)
SELECT COUNT(*), MIN(event_time), MAX(event_time)
FROM events
WHERE tenant_id = 'acme' AND date = '2024-01-15';

-- JSON output
SELECT JSON * FROM events
WHERE tenant_id = 'acme' AND date = '2024-01-15'
LIMIT 10;
```

---

## Batches and Transactions

### Logged Batches (Atomic)

```sql
-- Atomic write to multiple partitions
BEGIN BATCH
    INSERT INTO users (user_id, email) VALUES (?, ?);
    INSERT INTO users_by_email (email, user_id) VALUES (?, ?);
APPLY BATCH;
```

**Use logged batches for:**
- Maintaining denormalized data consistency
- Multi-table writes that must all succeed or all fail

**Logged batch limitations:**
- Performance penalty (coordinator log write)
- Not faster than individual writes (common misconception!)
- Best when all writes are to same partition

### Unlogged Batches

```sql
-- No atomicity guarantee, just convenience
BEGIN UNLOGGED BATCH
    INSERT INTO logs (log_id, message) VALUES (uuid(), 'log1');
    INSERT INTO logs (log_id, message) VALUES (uuid(), 'log2');
APPLY BATCH;
```

**Use unlogged batches for:**
- Writes to same partition (efficient grouping)
- When atomicity is not required

### Lightweight Transactions (LWT)

```sql
-- Insert if not exists
INSERT INTO users (user_id, email, username)
VALUES (?, ?, ?)
IF NOT EXISTS;

-- Returns: [applied] = true/false

-- Conditional update
UPDATE users SET email = ?
WHERE user_id = ?
IF email = ?;  -- Only if current email matches

-- Returns: [applied] = true/false, plus current values if false
```

**LWT characteristics:**
- Uses Paxos consensus protocol
- 4x latency of regular operations
- Use sparingly for critical consistency needs
- Good for: user registration, inventory reservation
- Bad for: high-throughput counters

---

## Common Operations

### Pagination

```sql
-- First page
SELECT * FROM events
WHERE tenant_id = 'acme' AND date = '2024-01-15'
LIMIT 100;

-- Next page (using last row's clustering values)
SELECT * FROM events
WHERE tenant_id = 'acme'
  AND date = '2024-01-15'
  AND (event_time, event_id) < (?, ?)  -- Last row's values
LIMIT 100;
```

**Note:** CQL does not support OFFSET. Use token-based pagination instead.

### Full Table Scan (Token Range)

```sql
-- Scan entire table (for ETL, analytics)
SELECT * FROM users
WHERE token(user_id) >= ?
  AND token(user_id) < ?
LIMIT 10000;

-- Application iterates through token ranges
-- Split: [-2^63, -2^63 + range), [-2^63 + range, -2^63 + 2*range), ...
```

### TTL Management

```sql
-- Check remaining TTL
SELECT TTL(email), email FROM users WHERE user_id = ?;

-- Insert with TTL
INSERT INTO sessions (session_id, user_id, data)
VALUES (?, ?, ?)
USING TTL 86400;  -- 24 hours

-- Update TTL (re-set with same value)
UPDATE sessions USING TTL 86400
SET data = data
WHERE session_id = ?;

-- Remove TTL (set to 0)
UPDATE sessions USING TTL 0
SET data = data
WHERE session_id = ?;
```

---

## Functions Reference

### Time and UUID Functions

| Function | Returns | Usage |
|----------|---------|-------|
| `now()` | TIMEUUID | Current time as TIMEUUID |
| `uuid()` | UUID | Random UUID |
| `currentTimestamp()` | TIMESTAMP | Current timestamp |
| `currentDate()` | DATE | Current date |
| `toDate(timestamp)` | DATE | Extract date from timestamp |
| `toTimestamp(timeuuid)` | TIMESTAMP | Extract timestamp from TIMEUUID |
| `toUnixTimestamp(timeuuid)` | BIGINT | Unix timestamp in milliseconds |
| `minTimeuuid(timestamp)` | TIMEUUID | Minimum TIMEUUID for time |
| `maxTimeuuid(timestamp)` | TIMEUUID | Maximum TIMEUUID for time |

### Token Function

```sql
-- Get token for partition key
SELECT token(user_id), user_id, username FROM users;

-- Query by token range
SELECT * FROM users
WHERE token(user_id) >= -9223372036854775808
  AND token(user_id) < 0;
```

### Type Conversion

```sql
-- CAST
SELECT CAST(count AS TEXT) FROM stats;

-- Blob conversions
SELECT textAsBlob('hello');
SELECT blobAsText(blob_column) FROM data;
SELECT intAsBlob(42);
```

---

## Best Practices

### Do

```
✓ Always include partition key in queries
✓ Design one table per query pattern
✓ Use prepared statements (prevents CQL injection, improves performance)
✓ Set appropriate LIMIT on queries
✓ Use TTL for expiring data instead of DELETE
✓ Keep partitions bounded (< 100MB)
✓ Use clustering columns for range queries
✓ Use TIMEUUID for time-ordered unique IDs
```

### Don't

```
✗ Use ALLOW FILTERING in production
✗ Create unbounded partitions
✗ Use large IN clauses (> 20 values)
✗ Use secondary indexes on high-cardinality columns
✗ Use collections for large datasets (> 100 elements)
✗ Use batches as a performance optimization
✗ Use Cassandra as a queue (frequent deletes)
✗ Rely on ORDER BY without clustering columns
```

---

## Documentation Sections

### Data Types
- **[Data Types Overview](data-types/index.md)** - All supported types
- Numeric, text, temporal, binary types
- Collections (LIST, SET, MAP)
- User-Defined Types (UDTs)
- Vector type (Cassandra 5.0+)

### DDL (Schema Management)
- **[DDL Overview](ddl/index.md)** - Schema commands
- CREATE/ALTER/DROP KEYSPACE
- CREATE/ALTER/DROP TABLE
- Index management

### DML (Data Operations)
- **[DML Overview](dml/index.md)** - Data commands
- SELECT with filtering and aggregation
- INSERT, UPDATE, DELETE
- Batch operations
- Lightweight transactions

### Indexing
- **[Indexing Overview](indexing/index.md)** - Index types and usage
- Secondary indexes
- Storage-Attached Indexes (SAI)
- Materialized views

### Functions
- **[Functions Overview](functions/index.md)** - Built-in functions
- Scalar functions
- Aggregate functions
- User-defined functions

---

## Next Steps

- **[Data Modeling](../data-modeling/index.md)** - Query-first design methodology
- **[Architecture](../architecture/storage-engine/index.md)** - How Cassandra stores data
- **[Anti-Patterns](../data-modeling/anti-patterns/index.md)** - Common mistakes
