# Materialized View Commands

Materialized views are server-maintained tables that automatically synchronize with a base table. They enable efficient queries on alternative primary key structures without manual denormalization.

---

## Production Readiness Warning

!!! danger "Experimental Feature - Use With Caution"
    Materialized views have been available since Cassandra 3.0 but remain **problematic in production environments**. Despite years of bug fixes, fundamental architectural issues can cause data inconsistencies that are difficult to detect and repair.

    **Evaluate carefully before using in production. Many organizations choose application-managed denormalization instead.**

### Known Issues

The following JIRA tickets document significant issues with materialized views:

| Issue | Summary | Status |
|-------|---------|--------|
| [CASSANDRA-13666](https://issues.apache.org/jira/browse/CASSANDRA-13666) | Base table and MV can become inconsistent | Multiple related fixes |
| [CASSANDRA-13883](https://issues.apache.org/jira/browse/CASSANDRA-13883) | MV update may be skipped on base table update | Fixed in 4.0 |
| [CASSANDRA-14092](https://issues.apache.org/jira/browse/CASSANDRA-14092) | MV can miss rows after range tombstone | Fixed in 4.0 |
| [CASSANDRA-12888](https://issues.apache.org/jira/browse/CASSANDRA-12888) | MV causes significant performance degradation | Ongoing |
| [CASSANDRA-10368](https://issues.apache.org/jira/browse/CASSANDRA-10368) | Repair does not repair MV inconsistencies | Partially addressed |
| [CASSANDRA-13911](https://issues.apache.org/jira/browse/CASSANDRA-13911) | Race conditions during concurrent modifications | Fixed in 4.1 |
| [CASSANDRA-15921](https://issues.apache.org/jira/browse/CASSANDRA-15921) | MV may have stale data after node failures | Ongoing |

### Recommendations

!!! warning "Before Using Materialized Views"
    1. **Test extensively** with realistic failure scenarios (node failures, network partitions)
    2. **Monitor for inconsistencies** using tools like `nodetool viewbuildstatus` and periodic validation queries
    3. **Plan for repair** - regular repairs are essential but may not catch all inconsistencies
    4. **Have a fallback plan** - be prepared to rebuild views or switch to application-managed denormalization
    5. **Consider Cassandra 4.1+** which includes significant MV bug fixes
    6. **Limit to read-heavy workloads** where occasional inconsistency is tolerable

### Alternatives to Materialized Views

| Approach | Pros | Cons |
|----------|------|------|
| **Application-managed denormalization** | Full control, reliable | More application code, must handle failures |
| **Batch writes to multiple tables** | Atomic within partition | Not atomic across partitions |
| **Change Data Capture (CDC)** | Async, decoupled | Additional infrastructure, latency |
| **Secondary indexes (SAI)** | Simple, no data duplication | Query limitations, performance varies |

---

## Materialized View Architecture

### How Materialized Views Work

When a row is written to a base table, Cassandra automatically generates and applies corresponding mutations to all materialized views:

```
Write to Base Table
        │
        ├──► Local View Update (same node)
        │
        └──► Replicate to View Replicas
                    │
                    └──► Stored as separate table
```

Views are stored as regular tables with their own SSTables, compaction, and repair requirements.

### Synchronization Guarantees

Materialized views provide **eventual consistency** with the base table:

- View updates are applied **synchronously** as part of the write path
- If a view replica is unavailable, updates are **hinted** for later delivery
- Inconsistencies can occur during failures and are resolved by repair

!!! warning "Consistency Considerations"
    Materialized views can become inconsistent with base tables during:

    - Node failures during write operations
    - Network partitions
    - Unrepaired data

    Run regular repairs on both base tables and views to maintain consistency.

### Write Path Impact

Materialized views add overhead to every write:

| Operation | Without MV | With 1 MV | With 3 MVs |
|-----------|------------|-----------|------------|
| Write latency | Baseline | ~2x | ~4x |
| Coordinator work | 1 mutation | 2 mutations | 4 mutations |
| Cluster writes | RF replicas | 2×RF replicas | 4×RF replicas |

!!! danger "Performance Impact"
    Each materialized view approximately **doubles write latency**. Consider carefully before creating multiple views on write-heavy tables.

---

## CREATE MATERIALIZED VIEW

Create an automatically maintained denormalized view of a base table.

### Synopsis

```cqlsyntax
CREATE MATERIALIZED VIEW [ IF NOT EXISTS ] [ *keyspace_name*. ] *view_name*
    AS SELECT *select_clause*
    FROM [ *keyspace_name*. ] *base_table*
    WHERE *where_clause*
    PRIMARY KEY ( *primary_key* )
    [ WITH *table_options* ]
```

### Description

`CREATE MATERIALIZED VIEW` defines a view that Cassandra maintains automatically. The view contains a copy of data from the base table, organized by a different primary key to support different query patterns.

### Parameters

#### *view_name*

Identifier for the materialized view. Views exist in the same keyspace as the base table unless explicitly qualified.

#### SELECT *select_clause*

Columns to include in the view. Two forms are supported:

```sql
-- All columns
SELECT *

-- Specific columns (must include all primary key columns)
SELECT user_id, email, username, created_at
```

!!! note "Column Requirements"
    The SELECT clause must include:

    - All base table primary key columns
    - All columns that will form the view's primary key
    - Any additional columns needed for queries

#### FROM *base_table*

The source table for the view.

#### WHERE *where_clause*

Filter conditions for the view. Must include `IS NOT NULL` for every primary key column:

```sql
WHERE email IS NOT NULL
  AND user_id IS NOT NULL
```

The `IS NOT NULL` constraint ensures the view only contains rows where primary key columns have values (views cannot store rows with null primary keys).

Additional filter conditions are allowed:

```sql
WHERE email IS NOT NULL
  AND user_id IS NOT NULL
  AND status = 'active'
```

!!! tip "Filtered Views"
    Add filter conditions to create partial views containing only relevant data:
    ```sql
    -- View of only premium users
    CREATE MATERIALIZED VIEW premium_users AS
        SELECT * FROM users
        WHERE is_premium = true
          AND user_id IS NOT NULL
        PRIMARY KEY (is_premium, user_id);
    ```

#### PRIMARY KEY

The view's primary key structure. Must follow these rules:

1. **Include all base table primary key columns**
2. **May add one additional column** from the base table
3. **May reorder columns** as partition key or clustering columns

```sql
-- Base table: PRIMARY KEY (user_id)
-- View: Reorder to query by email
PRIMARY KEY (email, user_id)

-- Base table: PRIMARY KEY ((tenant_id), user_id)
-- View: Add status column, reorder
PRIMARY KEY ((tenant_id, status), user_id)
```

##### Valid Primary Key Transformations

| Base Table PK | View PK (Valid) | Purpose |
|---------------|-----------------|---------|
| `(id)` | `(email, id)` | Query by email |
| `((a), b)` | `((b), a)` | Swap partition/cluster |
| `((a), b)` | `((a, c), b)` | Add column `c` to partition |
| `((a, b), c)` | `((a), b, c)` | Split partition key |

#### WITH *table_options*

Views support most table options:

```sql
WITH compaction = {'class': 'LeveledCompactionStrategy'}
AND compression = {'class': 'ZstdCompressor'}
AND gc_grace_seconds = 864000
AND caching = {'keys': 'ALL', 'rows_per_partition': 'NONE'}
```

### Examples

#### Query by Non-Primary-Key Column

```sql
-- Base table
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    email TEXT,
    username TEXT,
    created_at TIMESTAMP
);

-- View to query by email
CREATE MATERIALIZED VIEW users_by_email AS
    SELECT *
    FROM users
    WHERE email IS NOT NULL
      AND user_id IS NOT NULL
    PRIMARY KEY (email, user_id);

-- Query the view
SELECT * FROM users_by_email WHERE email = 'user@example.com';
```

#### Reverse Clustering Order

```sql
-- Base table: oldest first
CREATE TABLE events (
    sensor_id TEXT,
    event_time TIMESTAMP,
    data TEXT,
    PRIMARY KEY ((sensor_id), event_time)
) WITH CLUSTERING ORDER BY (event_time ASC);

-- View: newest first
CREATE MATERIALIZED VIEW events_recent AS
    SELECT *
    FROM events
    WHERE sensor_id IS NOT NULL
      AND event_time IS NOT NULL
    PRIMARY KEY ((sensor_id), event_time)
    WITH CLUSTERING ORDER BY (event_time DESC);
```

#### Add Column to Primary Key

```sql
-- Base table
CREATE TABLE orders (
    customer_id UUID,
    order_id TIMEUUID,
    status TEXT,
    total DECIMAL,
    PRIMARY KEY ((customer_id), order_id)
);

-- View to query by status
CREATE MATERIALIZED VIEW orders_by_status AS
    SELECT customer_id, order_id, status, total
    FROM orders
    WHERE customer_id IS NOT NULL
      AND order_id IS NOT NULL
      AND status IS NOT NULL
    PRIMARY KEY ((status), customer_id, order_id);

-- Query pending orders
SELECT * FROM orders_by_status WHERE status = 'pending';
```

#### Filtered View

```sql
-- View containing only active users
CREATE MATERIALIZED VIEW active_users AS
    SELECT *
    FROM users
    WHERE status = 'active'
      AND user_id IS NOT NULL
      AND email IS NOT NULL
    PRIMARY KEY (email, user_id);
```

#### Optimized View with Options

```sql
CREATE MATERIALIZED VIEW high_value_orders AS
    SELECT *
    FROM orders
    WHERE total > 1000
      AND customer_id IS NOT NULL
      AND order_id IS NOT NULL
    PRIMARY KEY ((customer_id), order_id)
    WITH compaction = {'class': 'LeveledCompactionStrategy'}
    AND caching = {'keys': 'ALL', 'rows_per_partition': '100'};
```

### Restrictions

!!! danger "Restrictions"
    **Primary Key Constraints:**

    - All base table primary key columns must be in the view's primary key
    - Only **one** non-primary-key column can be added to the view's primary key
    - Cannot use computed or derived columns

    **Column Constraints:**

    - Cannot include columns added to base table after view creation
    - Static columns from base table become non-static in view
    - Counter columns are not supported

    **Schema Constraints:**

    - Cannot alter view schema after creation (must drop and recreate)
    - Cannot create views on other views
    - Cannot create views on tables with `COMPACT STORAGE`

    **Data Constraints:**

    - Views cannot store rows where any primary key column is null
    - Collection columns cannot be part of view primary key

### Notes

- View build for existing data is asynchronous; monitor with `nodetool viewbuildstatus`
- Views require repair independently of base tables
- Tombstones in base table propagate to views
- Views increase write latency proportionally to number of views

!!! tip "Monitoring View Build"
    ```bash
    # Check view build status
    nodetool viewbuildstatus

    # View progress for specific keyspace
    nodetool viewbuildstatus keyspace_name
    ```

---

## ALTER MATERIALIZED VIEW

Modify materialized view options.

### Synopsis

```cqlsyntax
ALTER MATERIALIZED VIEW [ *keyspace_name*. ] *view_name*
    WITH *table_options*
```

### Description

`ALTER MATERIALIZED VIEW` changes view storage options. The view schema (columns, primary key) cannot be modified.

### Parameters

#### WITH *table_options*

View options that can be modified:

- `compaction` - Compaction strategy and options
- `compression` - Compression settings
- `gc_grace_seconds` - Tombstone retention
- `caching` - Caching configuration
- `bloom_filter_fp_chance` - Bloom filter settings
- `speculative_retry` - Speculative retry configuration

### Examples

#### Change Compaction Strategy

```sql
ALTER MATERIALIZED VIEW users_by_email
WITH compaction = {
    'class': 'LeveledCompactionStrategy',
    'sstable_size_in_mb': 160
};
```

#### Optimize for Read-Heavy Workload

```sql
ALTER MATERIALIZED VIEW orders_by_status
WITH caching = {'keys': 'ALL', 'rows_per_partition': '1000'}
AND bloom_filter_fp_chance = 0.001;
```

#### Adjust GC Grace Period

```sql
ALTER MATERIALIZED VIEW events_recent
WITH gc_grace_seconds = 172800;  -- 2 days
```

### Restrictions

!!! warning "Restrictions"
    - Cannot change view name
    - Cannot modify primary key or columns
    - Cannot change base table reference
    - Cannot modify WHERE clause filters

### Notes

- Option changes take effect immediately for new data
- Some options (like compaction) may trigger background operations

---

## DROP MATERIALIZED VIEW

Remove a materialized view.

### Synopsis

```cqlsyntax
DROP MATERIALIZED VIEW [ IF EXISTS ] [ *keyspace_name*. ] *view_name*
```

### Description

`DROP MATERIALIZED VIEW` removes a view and all its data. The base table is not affected.

### Parameters

#### IF EXISTS

Prevents error if view does not exist.

### Examples

```sql
-- Basic drop
DROP MATERIALIZED VIEW users_by_email;

-- With keyspace
DROP MATERIALIZED VIEW my_keyspace.orders_by_status;

-- Safe drop
DROP MATERIALIZED VIEW IF EXISTS temp_view;
```

### Restrictions

!!! warning "Restrictions"
    - Requires DROP permission on the view
    - Dropping base table automatically drops all its views

### Notes

- View drop is a metadata operation; data files deleted asynchronously
- Dropping a view removes write overhead from base table operations
- Cannot be undone; create snapshot before dropping if needed

---

## Best Practices

### When to Use Materialized Views

!!! tip "Good Use Cases"
    - Query by alternate unique identifier (email, phone)
    - Reverse sort order queries
    - Query by status or category (low cardinality partition key)
    - Filter to subset of data (active records only)

### When to Avoid Materialized Views

!!! warning "Avoid When"
    - High write throughput (each view multiplies writes)
    - Many views needed (each adds latency)
    - Complex transformations required (views are simple projections)
    - Strict consistency required (views are eventually consistent)

### Alternatives to Consider

| Use Case | Alternative |
|----------|-------------|
| High write throughput | Application-managed denormalization |
| Complex queries | Secondary indexes with SAI |
| Real-time analytics | External analytics system |
| Many access patterns | Multiple tables with batch writes |

### Operational Considerations

!!! note "Operations"
    - Run repairs on views independently: `nodetool repair keyspace view_name`
    - Monitor view build: `nodetool viewbuildstatus`
    - Views can become inconsistent; repair regularly
    - Consider view consistency before relying on view data for critical operations

---

## Related Documentation

- **[CREATE TABLE](table.md)** - Base table design
- **[CREATE INDEX](create-index.md)** - Alternative: Secondary indexes
- **[Data Modeling](../../data-modeling/index.md)** - Denormalization strategies
