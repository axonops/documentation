---
title: "Cassandra CQL Index Commands"
description: "CREATE INDEX syntax in CQL for secondary indexes and SAI indexes on Cassandra tables."
meta:
  - name: keywords
    content: "CREATE INDEX, secondary index, SAI, Cassandra indexing"
---

# Index Commands

Secondary indexes enable queries on columns that are not part of the primary key. Cassandra supports multiple index implementations, each with different performance characteristics and query capabilities.

---

## Behavioral Guarantees

### What Index Operations Guarantee

- CREATE INDEX initiates asynchronous index building; the command returns before indexing completes
- Index updates are applied synchronously as part of the write path once the index is built
- IF NOT EXISTS provides idempotent index creation
- DROP INDEX removes the index immediately; the command returns after schema propagation
- Each index is local to each node (node indexes only its own data)

### What Index Operations Do NOT Guarantee

!!! warning "Undefined Behavior"
    The following behaviors are undefined and must not be relied upon:

    - **Query availability during build**: Queries using the index may fail or return partial results until build completes on all nodes
    - **Build completion time**: Index build duration depends on data volume and cluster load; no timeout or progress guarantee
    - **Query performance**: Scatter-gather queries (without partition key) have unbounded latency depending on cluster size and data distribution
    - **Result completeness during failures**: If nodes are unavailable, indexed queries may return incomplete results
    - **Index-only scans**: All index queries require reading the base table; index does not store complete row data

### Index Build Contract

| State | Query Behavior | How to Check |
|-------|---------------|--------------|
| Building | Queries may fail or return partial results | `nodetool indexbuildstatus` |
| Built | Queries return complete results from available nodes | `nodetool indexbuildstatus` (no pending builds) |
| Failed | Index unusable; must drop and recreate | Check logs for build errors |

*Note: `system_schema.indexes` shows index definitions but not build status. Use `nodetool indexbuildstatus` to check build progress.*

### Query Execution Contract

| Query Type | Nodes Contacted | Performance |
|------------|-----------------|-------------|
| Index query with partition key | Replicas for that partition | Fast (single partition) |
| Index query without partition key | All nodes in cluster | Slow (scatter-gather) |
| Index query with token range | Nodes owning that range | Variable |

### Failure Semantics

| Failure Mode | Outcome | Client Action |
|--------------|---------|---------------|
| Timeout during CREATE INDEX | Schema may have propagated; build may be in progress | Check index status |
| Node failure during build | Build continues on other nodes; failed node rebuilds on restart | Monitor build status |
| Query timeout on indexed column | Partial results possible | Retry or add partition key constraint |
| `IndexNotAvailableException` | Index build incomplete | Wait for build to complete |

### Version-Specific Behavior

| Version | Behavior |
|---------|----------|
| 3.4+ | SASI indexes available (CASSANDRA-10661) |
| 4.0+ | Improved index build handling |
| 5.0+ | SAI as default index implementation (CEP-7), SASI deprecated |

---

## Index Architecture

### How Secondary Indexes Work

Secondary indexes in Cassandra are **local indexes**—each node indexes only the data it owns. When querying an indexed column without the partition key:

```
Client Query → Coordinator → Scatter to ALL Nodes → Gather Results → Return
                                    │
                                    └── Each node searches local index
```

This architecture has implications:

- **Without partition key**: Query must contact all nodes (scatter-gather)
- **With partition key**: Query contacts only replica nodes (efficient)
- **Index maintenance**: Indexes are updated synchronously with writes

!!! warning "Performance Consideration"
    Secondary indexes perform best when:

    - The query includes the partition key
    - The indexed column has low-to-medium cardinality
    - The data distribution is relatively uniform

    For high-cardinality columns or queries without partition keys, consider denormalized tables or materialized views instead.

### Index Types

| Type | Implementation | Best For | Cassandra Version |
|------|----------------|----------|-------------------|
| Legacy Secondary | `2i` | Low cardinality, equality queries | All |
| SASI | `SASIIndex` | Text search, ranges | 3.4+ |
| SAI | `StorageAttachedIndex` | General purpose, ranges, text | 5.0+ |

---

## CREATE INDEX

Create a secondary index on a table column.

### Synopsis

```cqlsyntax
CREATE [ CUSTOM ] INDEX [ IF NOT EXISTS ] [ *index_name* ]
    ON [ *keyspace_name*. ] *table_name* ( *index_target* )
    [ USING '*index_class*' ]
    [ WITH OPTIONS = { *option_map* } ]
```

**index_target**:

```cqlsyntax
*column_name*
| KEYS ( *map_column* )
| VALUES ( *map_column* )
| ENTRIES ( *map_column* )
| FULL ( *frozen_collection_column* )
```

### Description

`CREATE INDEX` creates a secondary index enabling queries on the specified column. The index is built asynchronously after creation; the command returns before indexing completes.

### Parameters

#### *index_name*

Optional name for the index. If omitted, Cassandra generates a name in the format `table_column_idx`.

```sql
-- Named index
CREATE INDEX users_email_idx ON users (email);

-- Auto-named (becomes users_email_idx)
CREATE INDEX ON users (email);
```

#### IF NOT EXISTS

Prevents error if index already exists.

#### *index_target*

Specifies what to index:

##### Column Index

Index regular column values:

```sql
CREATE INDEX ON users (email);
CREATE INDEX ON users (country);
```

##### Collection Indexes

Index collection elements:

```sql
-- Index SET or LIST elements
CREATE INDEX ON users (tags);  -- SET<TEXT>
CREATE INDEX ON users (phone_numbers);  -- LIST<TEXT>

-- Index MAP keys
CREATE INDEX ON users (KEYS(attributes));

-- Index MAP values
CREATE INDEX ON users (VALUES(attributes));

-- Index MAP key-value pairs
CREATE INDEX ON users (ENTRIES(attributes));

-- Index entire frozen collection
CREATE INDEX ON users (FULL(frozen_addresses));
```

| Target | Collection Type | Enables Query |
|--------|-----------------|---------------|
| `column` | `SET`, `LIST` | `WHERE column CONTAINS value` |
| `KEYS(column)` | `MAP` | `WHERE column CONTAINS KEY key` |
| `VALUES(column)` | `MAP` | `WHERE column CONTAINS value` |
| `ENTRIES(column)` | `MAP` | `WHERE column[key] = value` |
| `FULL(column)` | `FROZEN` | `WHERE column = entire_collection` |

#### USING

Specifies the index implementation class.

##### Legacy Secondary Index (Default)

```sql
CREATE INDEX ON users (country);
```

- Hash-based index
- Equality queries only
- Best for low-cardinality columns

##### Storage-Attached Index (SAI)

```sql
CREATE CUSTOM INDEX ON users (email)
    USING 'StorageAttachedIndex';
```

SAI (Cassandra 5.0+) provides:

- Efficient numeric range queries
- Text pattern matching (`LIKE`)
- Better performance than legacy indexes
- Lower storage overhead

##### SASI Index

```sql
CREATE CUSTOM INDEX ON users (username)
    USING 'org.apache.cassandra.index.sasi.SASIIndex';
```

!!! warning "SASI Status"
    SASI is marked as experimental and is not recommended for production use. Use SAI (Cassandra 5.0+) instead.

#### WITH OPTIONS

Index-specific configuration options.

##### SAI Options

```sql
CREATE CUSTOM INDEX ON users (email)
    USING 'StorageAttachedIndex'
    WITH OPTIONS = {
        'case_sensitive': 'false',
        'normalize': 'true',
        'ascii': 'true'
    };
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `case_sensitive` | boolean | `true` | Case-sensitive text comparison |
| `normalize` | boolean | `false` | Unicode normalization |
| `ascii` | boolean | `false` | ASCII folding (é → e) |

##### SASI Options

```sql
CREATE CUSTOM INDEX ON products (description)
    USING 'org.apache.cassandra.index.sasi.SASIIndex'
    WITH OPTIONS = {
        'mode': 'CONTAINS',
        'analyzer_class': 'org.apache.cassandra.index.sasi.analyzer.StandardAnalyzer',
        'case_sensitive': 'false'
    };
```

| Option | Values | Description |
|--------|--------|-------------|
| `mode` | `PREFIX`, `CONTAINS`, `SPARSE` | Query matching mode |
| `analyzer_class` | Class name | Text analyzer for tokenization |
| `case_sensitive` | `true`/`false` | Case sensitivity |
| `max_compaction_flush_memory_in_mb` | Number | Memory limit for indexing |

### Examples

#### Basic Indexes

```sql
-- Simple column index
CREATE INDEX ON users (email);

-- Named index
CREATE INDEX users_country_idx ON users (country);

-- Index with IF NOT EXISTS
CREATE INDEX IF NOT EXISTS ON users (last_name);
```

#### SAI Indexes (Cassandra 5.0+)

```sql
-- Numeric column for range queries
CREATE CUSTOM INDEX ON products (price)
    USING 'StorageAttachedIndex';

-- Case-insensitive text search
CREATE CUSTOM INDEX ON users (username)
    USING 'StorageAttachedIndex'
    WITH OPTIONS = {'case_sensitive': 'false'};

-- Multiple SAI indexes on same table
CREATE CUSTOM INDEX ON orders (status) USING 'StorageAttachedIndex';
CREATE CUSTOM INDEX ON orders (total) USING 'StorageAttachedIndex';
CREATE CUSTOM INDEX ON orders (created_at) USING 'StorageAttachedIndex';
```

#### Collection Indexes

```sql
-- Table with collections
CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY,
    tags SET<TEXT>,
    attributes MAP<TEXT, TEXT>,
    scores LIST<INT>
);

-- Index SET elements
CREATE INDEX ON user_profiles (tags);
-- Query: WHERE tags CONTAINS 'premium'

-- Index MAP keys
CREATE INDEX ON user_profiles (KEYS(attributes));
-- Query: WHERE attributes CONTAINS KEY 'department'

-- Index MAP values
CREATE INDEX ON user_profiles (VALUES(attributes));
-- Query: WHERE attributes CONTAINS 'engineering'

-- Index MAP entries
CREATE INDEX ON user_profiles (ENTRIES(attributes));
-- Query: WHERE attributes['department'] = 'engineering'
```

#### Querying Indexed Columns

```sql
-- Equality query
SELECT * FROM users WHERE email = 'user@example.com';

-- SAI range query
SELECT * FROM products WHERE price > 100 AND price < 500;

-- SAI pattern matching
SELECT * FROM users WHERE username LIKE 'john%';

-- Collection query
SELECT * FROM user_profiles WHERE tags CONTAINS 'premium';

-- With partition key (most efficient)
SELECT * FROM orders
WHERE customer_id = ? AND status = 'pending';
```

### Restrictions

!!! danger "Restrictions"
    - Cannot index partition key columns (already indexed)
    - Cannot create multiple indexes on the same column
    - Cannot index `COUNTER` columns
    - Legacy indexes do not support range queries
    - `LIKE` queries require SAI or SASI indexes

!!! warning "Cardinality Considerations"
    | Cardinality | Example | Index Recommendation |
    |-------------|---------|----------------------|
    | Very low | `boolean`, `status` (few values) | Secondary index OK |
    | Low-medium | `country`, `category` | Secondary index OK |
    | High | `email`, `user_id` | Avoid; use primary key or denormalize |
    | Unique | `uuid`, `timestamp` | Never index; use primary key |

    High-cardinality indexes create large index structures on each node, causing:
    - High memory usage
    - Slow index lookups
    - Heavy read amplification

### Notes

- Index building occurs asynchronously after `CREATE INDEX` returns
- Monitor index build progress: `nodetool compactionstats`
- Indexes are stored in separate SSTable files
- Dropping a table automatically drops all its indexes
- Index updates are synchronous with writes, adding write latency

!!! tip "Index Build Time"
    For existing tables with data, index building can take significant time:
    ```bash
    # Monitor index build progress
    nodetool compactionstats

    # View pending index builds
    nodetool compactionstats | grep "Secondary index"
    ```

---

## DROP INDEX

Remove a secondary index.

### Synopsis

```cqlsyntax
DROP INDEX [ IF EXISTS ] [ *keyspace_name*. ] *index_name*
```

### Description

`DROP INDEX` removes a secondary index. Queries using the index will fail after removal. The index data is deleted asynchronously.

### Parameters

#### IF EXISTS

Prevents error if index does not exist.

#### *index_name*

The name of the index to drop. Must be qualified with keyspace if not using `USE`.

### Examples

```sql
-- Drop by name
DROP INDEX users_email_idx;

-- With keyspace qualification
DROP INDEX my_keyspace.users_email_idx;

-- Safe drop
DROP INDEX IF EXISTS users_country_idx;
```

### Finding Index Names

```sql
-- List all indexes in keyspace
SELECT index_name, table_name, options
FROM system_schema.indexes
WHERE keyspace_name = 'my_keyspace';

-- Describe table to see indexes
DESCRIBE TABLE users;
```

### Restrictions

!!! warning "Restrictions"
    - Cannot drop index while queries are actively using it (they will fail)
    - Requires DROP permission on the table

### Notes

- Index drop is a metadata operation; data files are deleted asynchronously
- Queries using the dropped index will fail with error
- Consider application impact before dropping indexes in production

---

## Index Selection Guidelines

### When to Use Secondary Indexes

!!! tip "Good Use Cases"
    - Low-to-medium cardinality columns (< 1000 unique values per partition)
    - Queries that usually include the partition key
    - Filtering within partitions
    - Collection element searches

### When to Avoid Secondary Indexes

!!! warning "Avoid Indexes When"
    - Column has high cardinality (many unique values)
    - Queries never include the partition key
    - Column is frequently updated
    - Table has very large partitions

### Alternative Approaches

| Scenario | Alternative to Secondary Index |
|----------|-------------------------------|
| High-cardinality lookups | Create a lookup table with the column as partition key |
| Complex queries | Use materialized views |
| Full-text search | External search engine (Elasticsearch, Solr) |
| Range queries on multiple columns | Denormalized tables |

---

## Related Documentation

- **[Materialized Views](materialized-view.md)** - Alternative to indexes for query patterns
- **[Data Modeling](../../data-modeling/index.md)** - Query-first design
- **[SAI Documentation](../indexing/index.md)** - Storage-Attached Index details
