---
description: "Complete CQL (Cassandra Query Language) reference guide covering DDL, DML, data types, functions, and indexing."
meta:
  - name: keywords
    content: "CQL, Cassandra Query Language, SQL, query syntax, Cassandra database"
---

# CQL Reference

Cassandra Query Language (CQL) is the interface for interacting with Apache Cassandra. This reference provides complete syntax documentation for all CQL statements.

---

## Documentation

| Section | Description |
|---------|-------------|
| **[DDL Commands](ddl/index.md)** | Schema management: keyspaces, tables, indexes, types, functions |
| **[DML Commands](dml/index.md)** | Data operations: SELECT, INSERT, UPDATE, DELETE, BATCH |
| **[Data Types](data-types/index.md)** | Native types, collections, UDTs, vectors |
| **[Functions](functions/index.md)** | Scalar functions, aggregates, UDFs |
| **[Indexing](indexing/index.md)** | Secondary indexes, SAI, materialized views |

---

## Syntax Notation

This documentation uses syntax notation conventions adopted from [PostgreSQL Documentation](https://www.postgresql.org/docs/current/sql.html) and consistent with the [Apache Cassandra CQL specification](https://cassandra.apache.org/doc/latest/cassandra/developing/cql/index.html).

### Notation Conventions

| Element | Meaning |
|---------|---------|
| `KEYWORD` | SQL keyword (uppercase, literal) |
| *identifier* | Placeholder for user-supplied name or value (shown in italics) |
| `[ ]` | Optional element |
| `{ }` | Required choice—select one of the alternatives |
| `\|` | Separates alternatives within `{ }` or `[ ]` |
| `[, ...]` | Preceding element may repeat (comma-separated) |

### Example

```cqlsyntax
INSERT INTO *table_name* [ ( *column_name* [, ...] ) ]
    { DEFAULT VALUES | VALUES ( *value* [, ...] ) | *query* }
    [ IF NOT EXISTS ]
    [ USING TTL *seconds* ]
```

Reading this syntax:
- `INSERT INTO` and *table_name* are required
- Column list `( *column_name* [, ...] )` is optional
- One of the three alternatives in `{ }` is required: `DEFAULT VALUES`, `VALUES (...)`, or a *query*
- `IF NOT EXISTS` clause is optional
- `USING TTL` clause is optional

### Standard Terminology

Placeholder terms follow SQL grammar conventions from the ISO/IEC 9075 standard:

| Term | Description |
|------|-------------|
| *keyspace_name* | Identifier for a keyspace |
| *table_name* | Identifier for a table |
| *column_name* | Identifier for a column |
| *term* | A value: literal, bind marker (`?`), or function call |
| *relation* | A condition expression (e.g., `column = value`) |
| *operator* | Comparison operator (`=`, `<`, `>`, `<=`, `>=`, `IN`, `CONTAINS`) |

### References

- **ISO/IEC 9075** - Information technology — Database languages — SQL
- **[PostgreSQL Documentation](https://www.postgresql.org/docs/current/sql.html)** - Notation conventions
- **[Apache Cassandra CQL Documentation](https://cassandra.apache.org/doc/latest/cassandra/developing/cql/index.html)** - Official CQL specification

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

## CQL vs SQL

CQL syntax resembles SQL but operates differently due to Cassandra's distributed architecture.

| Aspect | SQL (RDBMS) | CQL (Cassandra) |
|--------|-------------|-----------------|
| Query flexibility | Any column | Must include partition key |
| JOINs | Supported | Not supported |
| Schema changes | May lock table | Instant (metadata only) |
| WHERE clause | Any conditions | Restricted to key columns |
| ORDER BY | Any column | Clustering columns only |
| GROUP BY | Any columns | Partition + clustering keys |
| Subqueries | Supported | Not supported |
| Transactions | ACID | LWT (Paxos-based) |
| OFFSET | Supported | Not supported |

### Query Restrictions

CQL requires efficient query patterns:

```sql
-- Requires partition key
SELECT * FROM users WHERE user_id = ?;

-- Range queries require partition key + clustering column
SELECT * FROM events WHERE tenant_id = ? AND event_time > ?;

-- Without partition key, requires ALLOW FILTERING (avoid in production)
SELECT * FROM users WHERE email = ? ALLOW FILTERING;
```

---

## Query Execution

Every query executes in a distributed environment:

1. **Client connects** to any node (becomes coordinator)
2. **Coordinator hashes** partition key to locate replica nodes
3. **Replicas contacted** based on consistency level
4. **Results merged** and returned to client

```
Client → Coordinator → Replica Nodes → Response
           │
           └── hash(partition_key) → node selection
```

## Primary Key Structure

The primary key determines data distribution and query capabilities:

```
PRIMARY KEY ((partition_key), clustering_col1, clustering_col2)
            └──────┬──────┘  └────────────┬────────────────┘
        Data distribution         Sort order within partition
```

| Component | Description |
|-----------|-------------|
| Partition key | Determines which node stores the data |
| Clustering columns | Define sort order within partition |

```sql
-- Simple: single partition key
CREATE TABLE users (user_id UUID PRIMARY KEY, ...);

-- Compound: partition key + clustering
CREATE TABLE messages (
    user_id UUID,
    sent_at TIMESTAMP,
    PRIMARY KEY ((user_id), sent_at)
) WITH CLUSTERING ORDER BY (sent_at DESC);

-- Composite: multiple partition key columns
CREATE TABLE events (
    tenant_id TEXT,
    date DATE,
    event_time TIMESTAMP,
    PRIMARY KEY ((tenant_id, date), event_time)
);
```

---

## Query Efficiency

| Query Pattern | Efficiency |
|---------------|------------|
| Partition key equality | Excellent |
| Partition + clustering range | Excellent |
| Partition + IN (< 10 values) | Good |
| Secondary index | Poor |
| ALLOW FILTERING | Avoid |

---

## Common Data Types

| Type | Description |
|------|-------------|
| `UUID` | Random unique identifier |
| `TIMEUUID` | Time-based UUID |
| `TEXT` | UTF-8 string |
| `INT` / `BIGINT` | 32-bit / 64-bit integer |
| `TIMESTAMP` | Date/time |
| `BOOLEAN` | True/false |
| `LIST<T>` | Ordered collection |
| `SET<T>` | Unique values |
| `MAP<K,V>` | Key-value pairs |

See **[Data Types](data-types/index.md)** for complete reference.

---

## Common Functions

| Function | Description |
|----------|-------------|
| `uuid()` | Generate random UUID |
| `now()` | Current time as TIMEUUID |
| `toTimestamp()` | Convert to timestamp |
| `token()` | Partition key hash value |
| `TTL()` | Remaining time-to-live |
| `WRITETIME()` | Write timestamp |

See **[Functions](functions/index.md)** for complete reference.

---

## Best Practices

| Do | Avoid |
|----|-------|
| Include partition key in queries | ALLOW FILTERING in production |
| Design one table per query pattern | Unbounded partitions |
| Use prepared statements | Large IN clauses (> 20 values) |
| Use TTL for expiring data | Secondary indexes on high-cardinality |
| Keep partitions < 100MB | Collections with > 100 elements |

---

## Related Documentation

- **[Data Modeling](../data-modeling/index.md)** - Query-first design
- **[Architecture](../architecture/storage-engine/index.md)** - Storage internals
- **[Anti-Patterns](../data-modeling/anti-patterns/index.md)** - Common mistakes
