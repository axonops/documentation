---
title: "Cassandra CQL Indexing Reference"
description: "Cassandra indexing guide covering secondary indexes, SASI, and SAI. Choose the right index type."
meta:
  - name: keywords
    content: "Cassandra indexing, secondary index, SASI, SAI, index types"
---

# CQL Indexing Reference

Indexes in Cassandra do not work like relational indexes, and that surprises many. A relational index is a global structure—query it, and all matching rows are returned. A Cassandra secondary index is local to each node—query it without a partition key, and Cassandra has to ask every node in the cluster. That is an all-node scatter query, and it does not scale.

This makes secondary indexes useful only in specific situations: queries that always include the partition key, or low-cardinality columns when combined with partition key constraints. For high-cardinality lookups like email addresses, a separate denormalized table is usually more appropriate.

SAI (Storage-Attached Indexes), available experimentally in 4.0 and production-ready in 5.0, handle more use cases efficiently. Materialized views offer another option—automated denormalization at the cost of write amplification.

This guide covers when each approach makes sense.

---

## Behavioral Guarantees

### What Indexes Guarantee

- Index updates are applied synchronously as part of the write path
- Indexes are local to each node (each node indexes only its own data)
- Queries with partition key plus indexed column contact only partition replicas
- Index build is asynchronous; queries may return partial results during build
- DROP INDEX removes the index immediately from schema

### What Indexes Do NOT Guarantee

!!! warning "Undefined Behavior"
    The following behaviors are undefined and must not be relied upon:

    - **Global ordering**: Index queries without partition key return results in undefined order
    - **Latency bounds**: Scatter-gather queries have unbounded latency proportional to cluster size
    - **Memory usage**: Large result sets from index queries may exhaust coordinator memory
    - **Build time**: Index build duration depends on data volume; no progress or completion guarantee
    - **Result completeness during build**: Queries may miss data on nodes still building the index
    - **Performance consistency**: Query performance varies significantly based on data distribution

### Index Type Comparison Contract

| Index Type | Query Types | Cardinality | Production Status |
|------------|-------------|-------------|-------------------|
| Legacy (2i) | Equality only | Low | Supported |
| SASI | Equality, range, LIKE | Medium | Deprecated |
| SAI | Equality, range, LIKE, ANN | Any | Recommended (5.0+) |

### Query Execution Contract

| Query Pattern | Nodes Contacted | Performance |
|---------------|-----------------|-------------|
| `pk = ? AND indexed = ?` | RF replicas | Fast |
| `indexed = ?` | All nodes | Slow (scatter-gather) |
| `indexed = ? LIMIT n` | All nodes (early termination) | Variable |
| `indexed > ? AND indexed < ?` | All nodes (SAI/SASI only) | Variable |

### Index Selection Contract

| Scenario | Recommended Index | Alternative |
|----------|-------------------|-------------|
| Low cardinality + partition key | Legacy 2i or SAI | None needed |
| High cardinality lookup | SAI | Denormalized table |
| Text search (prefix/suffix) | SAI | Application-side filtering |
| Vector similarity | SAI with ANN | External vector database |
| Frequent alternative access pattern | Materialized view | Application-managed table |

### Failure Semantics

| Failure Mode | Outcome | Client Action |
|--------------|---------|---------------|
| Index build incomplete | Partial results | Wait for build or query specific partitions |
| Node unavailable | Results from available nodes only | Retry or accept partial results |
| Query timeout | Partial results or exception | Add partition key or reduce scope |
| Index not found | Query fails | Create index or use ALLOW FILTERING |

### Version-Specific Behavior

| Version | Behavior |
|---------|----------|
| All | Legacy secondary indexes (2i) |
| 3.4+ | SASI indexes (experimental) |
| 4.0+ | SASI officially not recommended for production |
| 5.0+ | SAI (Storage-Attached Indexes) as recommended default (CEP-7) |

---

## Index Types Overview

| Type | Best For | Limitations |
|------|----------|-------------|
| **Secondary Index** | Low cardinality, occasional queries | Full cluster scan |
| **SAI (Cassandra 5.0+)** | General purpose, high cardinality | Requires Cassandra 5.0+ |
| **SASI (deprecated)** | Prefix/suffix search | Being replaced by SAI |
| **Materialized View** | Frequent alternative queries | Write amplification |

---

## Secondary Indexes

### Creating Secondary Indexes

```sql
-- Basic secondary index
CREATE INDEX ON users (email);

-- Named index
CREATE INDEX users_email_idx ON users (email);

-- Index on collection values
CREATE INDEX ON users (tags);  -- For set/list

-- Index on map keys
CREATE INDEX ON users (KEYS(preferences));

-- Index on map values
CREATE INDEX ON users (VALUES(preferences));

-- Index on map entries
CREATE INDEX ON users (ENTRIES(preferences));

-- Index on full frozen collection
CREATE INDEX ON users (FULL(address));
```

### Querying with Secondary Indexes

```sql
-- Query by indexed column
SELECT * FROM users WHERE email = 'john@example.com';

-- With collection index
SELECT * FROM users WHERE tags CONTAINS 'premium';

-- With map index
SELECT * FROM users WHERE preferences CONTAINS KEY 'theme';
SELECT * FROM users WHERE preferences CONTAINS 'dark';
SELECT * FROM users WHERE preferences['theme'] = 'dark';
```

### When to Use Secondary Indexes

**Good use cases**:
- Low cardinality columns (status, country)
- Infrequent queries
- Combined with partition key
- Small result sets expected

**Bad use cases**:
- High cardinality columns (user_id, email)
- Frequently queried columns
- Large result sets
- Primary access pattern

### Secondary Index Limitations

```sql
-- These queries require ALLOW FILTERING or fail:

-- No partition key, no index
SELECT * FROM users WHERE age > 30;  -- Error

-- Range query on indexed column
SELECT * FROM users WHERE age > 30 ALLOW FILTERING;  -- Slow

-- Multiple conditions without partition key
SELECT * FROM users WHERE status = 'active' AND country = 'US';
-- Slow even if both indexed
```

### Collection Index Behavior

Secondary indexes on collections have special query semantics:

| Collection Type | Index Type | Query Operator | Example |
|-----------------|------------|----------------|---------|
| SET/LIST | Values | `CONTAINS` | `WHERE tags CONTAINS 'premium'` |
| MAP | `KEYS()` | `CONTAINS KEY` | `WHERE preferences CONTAINS KEY 'theme'` |
| MAP | `VALUES()` | `CONTAINS` | `WHERE preferences CONTAINS 'dark'` |
| MAP | `ENTRIES()` | `[]` accessor | `WHERE preferences['theme'] = 'dark'` |
| FROZEN | `FULL()` | `=` (full match) | `WHERE address = {street: '...', city: '...'}` |

!!! warning "Collection Index Restrictions"
    - `CONTAINS` and `CONTAINS KEY` only work with indexed collections
    - Cannot combine multiple `CONTAINS` on same collection in one query
    - Each element in collection is indexed separately (storage overhead)
    - `FULL()` index requires exact match of entire frozen collection
    - Collection indexes still result in scatter-gather without partition key

    ```sql
    -- ERROR: Cannot use multiple CONTAINS on same column
    SELECT * FROM users
    WHERE tags CONTAINS 'premium' AND tags CONTAINS 'verified';

    -- WORKAROUND: Filter in application or use intersection
    ```

### High-Cardinality Performance Pitfalls

!!! danger "Avoid Secondary Indexes on High-Cardinality Columns"
    Secondary indexes on high-cardinality columns (many unique values) cause severe performance problems:

    | Issue | Impact |
    |-------|--------|
    | Index size | Approaches table size; one entry per unique value |
    | Read amplification | Must check index on every node |
    | Hotspots | Popular values create uneven load |
    | Tombstone buildup | Deleted values leave tombstones in index |
    | Memory pressure | Large indexes consume heap on each node |

    **Example of problematic indexing:**

    ```sql
    -- BAD: High cardinality
    CREATE INDEX ON users (email);        -- Unique per user
    CREATE INDEX ON orders (order_id);    -- Unique per order
    CREATE INDEX ON events (timestamp);   -- High cardinality

    -- BETTER: Low cardinality
    CREATE INDEX ON users (account_type); -- Few values: 'free', 'premium', 'enterprise'
    CREATE INDEX ON orders (status);      -- Few values: 'pending', 'shipped', 'delivered'
    ```

    **For high-cardinality lookups, use:**

    - Denormalized tables with the lookup column as partition key
    - SAI indexes (Cassandra 5.0+) which handle cardinality better
    - Application-side caching for frequently accessed values

---

## Storage-Attached Indexes (SAI)

SAI is the next-generation indexing in Cassandra 5.0+, offering better performance and more capabilities than secondary indexes.

### Creating SAI Indexes

```sql
-- Basic SAI index
CREATE CUSTOM INDEX ON users (email)
USING 'StorageAttachedIndex';

-- Named SAI index
CREATE CUSTOM INDEX users_email_sai ON users (email)
USING 'StorageAttachedIndex';

-- SAI with options
CREATE CUSTOM INDEX ON users (description)
USING 'StorageAttachedIndex'
WITH OPTIONS = {
    'case_sensitive': 'false',
    'normalize': 'true'
};

-- Numeric index for range queries
CREATE CUSTOM INDEX ON products (price)
USING 'StorageAttachedIndex';
```

### SAI Query Capabilities

```sql
-- Equality queries
SELECT * FROM users WHERE email = 'john@example.com';

-- Range queries (numeric)
SELECT * FROM products WHERE price >= 100 AND price < 500;

-- AND queries with multiple SAI columns
SELECT * FROM products
WHERE category = 'electronics'
  AND price < 1000
  AND in_stock = true;

-- Combined with partition key (most efficient)
SELECT * FROM orders
WHERE user_id = ?
  AND status = 'pending';
```

### SAI vs Secondary Index

| Feature | Secondary Index | SAI |
|---------|-----------------|-----|
| High cardinality | Poor | Good |
| Range queries | No | Yes |
| Multiple conditions | Poor | Better |
| Write overhead | Lower | Higher |
| Text search | No | Limited |
| Availability | All versions | 5.0+ |

### SAI Limitations

- Still scans all nodes for queries without partition key
- Not a replacement for proper data modeling
- Higher storage overhead than secondary indexes
- Text search is basic (no fuzzy matching)

---

## SASI Indexes (Deprecated)

SASI (SSTable Attached Secondary Index) is deprecated but still available. Use SAI instead for new deployments.

### Creating SASI Indexes

```sql
-- Prefix search index
CREATE CUSTOM INDEX ON users (username)
USING 'org.apache.cassandra.index.sasi.SASIIndex'
WITH OPTIONS = {
    'mode': 'PREFIX',
    'analyzer_class': 'org.apache.cassandra.index.sasi.analyzer.StandardAnalyzer',
    'case_sensitive': 'false'
};

-- Contains search index
CREATE CUSTOM INDEX ON users (bio)
USING 'org.apache.cassandra.index.sasi.SASIIndex'
WITH OPTIONS = {
    'mode': 'CONTAINS',
    'analyzer_class': 'org.apache.cassandra.index.sasi.analyzer.StandardAnalyzer',
    'case_sensitive': 'false'
};

-- Numeric sparse index
CREATE CUSTOM INDEX ON orders (total)
USING 'org.apache.cassandra.index.sasi.SASIIndex'
WITH OPTIONS = {
    'mode': 'SPARSE'
};
```

### SASI Query Patterns

```sql
-- Prefix search (LIKE 'prefix%')
SELECT * FROM users WHERE username LIKE 'john%';

-- Contains search (LIKE '%substring%')
SELECT * FROM users WHERE bio LIKE '%developer%';

-- Range queries
SELECT * FROM orders WHERE total > 100 AND total < 500;
```

---

## Materialized Views

Materialized views automatically maintain denormalized copies of data with different primary keys.

### Creating Materialized Views

```sql
-- Base table
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    username TEXT,
    email TEXT,
    country TEXT,
    created_at TIMESTAMP
);

-- Materialized view by email
CREATE MATERIALIZED VIEW users_by_email AS
    SELECT * FROM users
    WHERE email IS NOT NULL AND user_id IS NOT NULL
    PRIMARY KEY (email, user_id);

-- View with filtered data
CREATE MATERIALIZED VIEW active_users_by_country AS
    SELECT user_id, username, country, created_at FROM users
    WHERE country IS NOT NULL
      AND user_id IS NOT NULL
      AND status = 'active'
    PRIMARY KEY (country, created_at, user_id)
    WITH CLUSTERING ORDER BY (created_at DESC);
```

### Querying Materialized Views

```sql
-- Query the view like a regular table
SELECT * FROM users_by_email WHERE email = 'john@example.com';

SELECT * FROM active_users_by_country
WHERE country = 'US'
ORDER BY created_at DESC
LIMIT 100;
```

### Materialized View Rules

**Requirements**:
- All base table primary key columns must be in the view's primary key
- One new column can be added to the partition key
- All non-null filters must use IS NOT NULL
- View primary key must include base table primary key

```sql
-- Base table
CREATE TABLE orders (
    order_id UUID,
    user_id UUID,
    status TEXT,
    amount DECIMAL,
    created_at TIMESTAMP,
    PRIMARY KEY ((order_id))
);

-- Valid view: adds user_id to partition key
CREATE MATERIALIZED VIEW orders_by_user AS
    SELECT * FROM orders
    WHERE user_id IS NOT NULL AND order_id IS NOT NULL
    PRIMARY KEY ((user_id), created_at, order_id)
    WITH CLUSTERING ORDER BY (created_at DESC);

-- Invalid: order_id not in primary key
-- CREATE MATERIALIZED VIEW invalid_view AS
--     SELECT * FROM orders
--     WHERE user_id IS NOT NULL
--     PRIMARY KEY ((user_id), created_at);  -- Missing order_id!
```

### Materialized View Limitations

| Limitation | Impact |
|------------|--------|
| Write amplification | Every write to base table writes to all views |
| Eventual consistency | Views may lag behind base table |
| Limited transformations | Cannot use functions or aggregates |
| Repair complexity | Views need repair too |
| Schema changes | Cannot alter view; must drop and recreate |

### When to Use Materialized Views

**Good use cases**:
- Small number of views per table
- Low write throughput
- Need guaranteed consistency with base table
- Simple alternative access patterns

**Avoid when**:
- High write throughput
- Many views needed
- Complex transformations required
- Critical latency requirements

---

## Index Management

### Listing Indexes

```sql
-- List all indexes
SELECT * FROM system_schema.indexes;

-- Indexes for specific keyspace
SELECT * FROM system_schema.indexes WHERE keyspace_name = 'my_keyspace';

-- Indexes for specific table
SELECT * FROM system_schema.indexes
WHERE keyspace_name = 'my_keyspace' AND table_name = 'users';
```

### Dropping Indexes

```sql
-- Drop by name
DROP INDEX IF EXISTS users_email_idx;

-- Drop by keyspace.name
DROP INDEX my_keyspace.users_email_idx;
```

### Rebuilding Indexes

```bash
# Rebuild all indexes on a table
nodetool rebuild_index my_keyspace users

# Rebuild specific index
nodetool rebuild_index my_keyspace users users_email_idx
```

### Managing Materialized Views

```sql
-- List views
SELECT * FROM system_schema.views WHERE keyspace_name = 'my_keyspace';

-- Drop view
DROP MATERIALIZED VIEW IF EXISTS users_by_email;

-- Cannot alter views; must drop and recreate
```

---

## Index Best Practices

### Secondary Index Guidelines

```
DO:
✓ Use for low-cardinality columns
✓ Combine with partition key when possible
✓ Use for occasional queries
✓ Index columns queried with equality

DON'T:
✗ Index high-cardinality columns (use SAI instead)
✗ Rely on indexes for primary access patterns
✗ Use for range queries (use SAI instead)
✗ Create many indexes on single table
```

### SAI Guidelines (5.0+)

```
DO:
✓ Use for high-cardinality columns
✓ Use for range queries
✓ Combine multiple SAI indexes in queries
✓ Use with partition key for best performance

DON'T:
✗ Use as replacement for good data model
✗ Query without partition key for large datasets
✗ Expect full-text search capabilities
```

### Materialized View Guidelines

```
DO:
✓ Limit to 2-3 views per table
✓ Use for guaranteed consistency needs
✓ Use for simple access pattern changes
✓ Include all base table PK columns

DON'T:
✗ Create many views per table
✗ Use with high write throughput
✗ Use for complex data transformations
✗ Forget to repair views
```

---

## Index Selection Decision Tree

```
Need to query by non-PK column?
│
├── Is this a frequent/primary access pattern?
│   └── Yes: Create a new table (denormalization)
│
├── Need guaranteed consistency with base table?
│   └── Yes: Consider Materialized View
│
├── Running Cassandra 5.0+?
│   ├── Yes: Use SAI
│   │   ├── High cardinality: SAI
│   │   ├── Range queries: SAI
│   │   └── Multiple conditions: SAI
│   │
│   └── No: Secondary Index or SASI
│       ├── Low cardinality: Secondary Index
│       ├── Prefix/contains search: SASI
│       └── High cardinality: Consider data model change
│
└── Is performance acceptable?
    ├── Yes: Keep current solution
    └── No: Redesign data model
```

---

## Next Steps

- **[Data Modeling](../../data-modeling/index.md)** - Query-first design
- **[DML Reference](../dml/index.md)** - Query syntax
- **[Performance Tuning](../../operations/performance/index.md)** - Optimization
- **[Anti-Patterns](../../data-modeling/anti-patterns/index.md)** - What to avoid