---
description: "CQL DDL (Data Definition Language) commands for creating and managing keyspaces, tables, indexes, and views."
meta:
  - name: keywords
    content: "CQL DDL, CREATE KEYSPACE, CREATE TABLE, Cassandra schema"
---

# DDL Commands

Data Definition Language (DDL) commands manage schema objects in Apache Cassandra. This section provides comprehensive reference documentation for all DDL statements.

---

## Overview

DDL commands create, modify, and remove schema objects: keyspaces, tables, indexes, materialized views, user-defined types, functions, and aggregates. Unlike traditional relational databases where schema changes may require table locks or data migration, Cassandra applies schema modifications as metadata operations that propagate cluster-wide through the gossip protocol.

---

## Schema Architecture

### Distributed Schema Management

Cassandra maintains schema information in the `system_schema` keyspace. Unlike user keyspaces where replication factor determines how many nodes store data, **every node in the cluster stores a complete copy of the schema**. This ensures all nodes can independently validate queries and understand the data model without contacting other nodes.

The `system_schema` keyspace uses `LocalStrategy` for replication, meaning each node manages its own local copy. Schema synchronization occurs through the gossip protocol rather than normal read/write replication:

```sql
DESCRIBE KEYSPACE system_schema;

CREATE KEYSPACE system_schema
    WITH REPLICATION = { 'class': 'LocalStrategy' }
    AND DURABLE_WRITES = true;
```

```
Client → Coordinator → Local Schema Update → Gossip Propagation → All Nodes
                              │                                        │
                              └── system_schema tables updated         └── Every node receives
                                                                           complete schema
```

When a DDL statement executes:

1. The coordinator node validates the DDL statement
2. Schema metadata is written to local `system_schema` tables
3. A schema mutation is broadcast via gossip to all nodes
4. Each node applies the schema change to its local `system_schema` independently
5. Schema agreement is reached when all nodes have matching schema versions

!!! note "Schema vs Data Replication"
    Schema replication is independent of keyspace replication settings:

    - **Schema**: Always stored on every node (via gossip)
    - **Data**: Stored on nodes determined by partition key and replication factor

    A keyspace with `replication_factor: 3` stores data on 3 nodes, but the schema definition for that keyspace exists on all nodes in the cluster.

### Schema Agreement

Before returning success for a DDL operation, Cassandra waits for schema agreement—a state where all live nodes have the same schema version. The schema version is a UUID computed from the hash of all schema metadata.

```sql
-- Check current schema versions across the cluster
SELECT schema_version FROM system.local;
SELECT peer, schema_version FROM system.peers;
```

!!! warning "Schema Disagreement"
    If schema agreement cannot be reached within the timeout (default 10 seconds), the DDL statement returns a warning but the change may still propagate. Operations during schema disagreement may produce unpredictable results. Monitor `nodetool describecluster` for schema version mismatches.

### System Schema Tables

Schema metadata is stored in the `system_schema` keyspace:

| Table | Contents |
|-------|----------|
| `keyspaces` | Keyspace definitions and replication settings |
| `tables` | Table schemas, options, and flags |
| `columns` | Column definitions for each table |
| `types` | User-defined type definitions |
| `functions` | User-defined function code and signatures |
| `aggregates` | User-defined aggregate definitions |
| `indexes` | Secondary index metadata |
| `views` | Materialized view definitions |
| `triggers` | Trigger configurations |

---

## Online Schema Changes

Cassandra supports online schema modifications without blocking reads or writes. This capability stems from the storage engine architecture:

### How Online Changes Work

**Adding Columns**

New columns are metadata-only changes. Existing SSTables are not modified. When reading rows written before the column was added, Cassandra returns `null` for the new column.

**Dropping Columns**

Dropped columns are marked in metadata but data remains in SSTables until compaction. Reading dropped column data is prevented at the storage layer.

**Altering Types**

Type changes for non-primary-key columns are permitted if the new type is compatible (e.g., widening `INT` to `BIGINT`). The storage engine interprets existing bytes according to the new type.

!!! note "Primary Key Immutability"
    Primary key columns (partition key and clustering columns) cannot be modified after table creation. The primary key structure determines data distribution and physical storage layout.

### Schema Change Propagation Time

Schema changes propagate at gossip speed, typically completing cluster-wide within seconds. Factors affecting propagation:

- **Cluster size**: Larger clusters require more gossip rounds
- **Network latency**: Cross-datacenter propagation adds delay
- **Node health**: Unresponsive nodes delay agreement

```
Typical propagation times:
  - 3-node cluster: < 1 second
  - 50-node cluster: 1-3 seconds
  - 200-node multi-DC cluster: 3-10 seconds
```

---

## Schema Versioning

Each schema modification increments the schema version. Cassandra tracks schema history but does not provide built-in rollback capabilities.

!!! tip "Schema Version Control"
    Maintain DDL scripts in version control. Use migration tools like `cassandra-migration` or application-level schema management to track and apply schema changes systematically.

### Snapshot Before Schema Changes

Before significant schema modifications, create snapshots:

```bash
# Snapshot specific table before altering
nodetool snapshot -t pre_alter_backup keyspace_name table_name

# Snapshot entire keyspace
nodetool snapshot -t pre_migration keyspace_name
```

---

## Schema Objects

### Hierarchy

```
Cluster
└── Keyspace (namespace + replication configuration)
    ├── Table (column families)
    │   ├── Column definitions
    │   ├── Primary key structure
    │   ├── Indexes
    │   └── Materialized views
    ├── User-Defined Types
    ├── Functions
    └── Aggregates
```

### Naming Rules

#### Identifier Syntax

All schema object names follow these rules:

| Rule | Unquoted Identifiers | Quoted Identifiers |
|------|---------------------|-------------------|
| First character | Letter (a-z, A-Z) | Any character |
| Subsequent characters | Letters, digits (0-9), underscore (_) | Any character |
| Case sensitivity | Case-insensitive (stored as lowercase) | Case-sensitive (preserved exactly) |
| Reserved words | Not allowed | Allowed |
| Maximum length | 48 characters | 48 characters |

```sql
-- Unquoted: stored as lowercase
CREATE TABLE UserEvents (...);   -- Stored as 'userevents'
CREATE TABLE user_events (...);  -- Stored as 'user_events'

-- Quoted: case and special characters preserved
CREATE TABLE "UserEvents" (...); -- Stored as 'UserEvents'
CREATE TABLE "user-events" (...); -- Stored as 'user-events'
CREATE TABLE "select" (...);     -- Reserved word allowed when quoted
```

#### Maximum Lengths by Object Type

| Object Type | Maximum Length | Notes |
|-------------|----------------|-------|
| Keyspace name | 48 characters | |
| Table name | 48 characters | |
| Column name | 65535 characters | Practical limit ~100 for readability |
| Index name | 48 characters | Auto-generated: `table_column_idx` |
| Materialized view name | 48 characters | |
| User-defined type name | 48 characters | |
| UDT field name | 65535 characters | |
| Function name | 48 characters | |
| Aggregate name | 48 characters | |
| Role name | 256 characters | |

!!! warning "Directory Name Limits"
    On disk, keyspace and table names become directory names. Some filesystems have path length limits (255 characters for most). Very long names combined with Cassandra's data directory path may exceed filesystem limits.

#### Permitted Characters

**Unquoted identifiers** (recommended for portability):

- Letters: `a-z`, `A-Z` (ASCII only)
- Digits: `0-9` (not as first character)
- Underscore: `_`

**Quoted identifiers** allow additional characters:

- Spaces and hyphens: `"my table"`, `"user-events"`
- Unicode characters: `"日本語テーブル"`
- Special characters: `"table.name"`, `"column@v2"`
- Reserved words: `"select"`, `"table"`, `"index"`

```sql
-- Valid unquoted names
CREATE TABLE user_events_2024 (...);
CREATE TABLE t1 (...);

-- Invalid unquoted names (require quoting)
CREATE TABLE 2024_events (...);    -- ERROR: starts with digit
CREATE TABLE user-events (...);    -- ERROR: contains hyphen
CREATE TABLE select (...);         -- ERROR: reserved word

-- Valid quoted equivalents
CREATE TABLE "2024_events" (...);
CREATE TABLE "user-events" (...);
CREATE TABLE "select" (...);
```

#### Reserved Words

CQL reserves certain keywords that cannot be used as unquoted identifiers. Common reserved words include:

| | | | | |
|---|---|---|---|---|
| ADD | ALTER | AND | AS | ASC |
| BATCH | BEGIN | BY | COLUMN | CREATE |
| DELETE | DESC | DROP | EXISTS | FROM |
| GRANT | IF | IN | INDEX | INSERT |
| INTO | KEYSPACE | LIMIT | NOT | NULL |
| OF | ON | OR | ORDER | PRIMARY |
| REVOKE | ROLE | SELECT | SET | TABLE |
| TO | TOKEN | TRUNCATE | UPDATE | USE |
| USING | VALUES | WHERE | WITH | |

For a complete list, consult the [CQL specification](https://cassandra.apache.org/doc/latest/cassandra/cql/appendices.html#appendix-a-cql-keywords).

!!! tip "Best Practice"
    Use lowercase unquoted identifiers with underscores for maximum compatibility:

    - `user_events` ✓
    - `UserEvents` ✓ (stored as `userevents`)
    - `"user-events"` - works but requires quoting everywhere
    - `"select"` - works but confusing

```sql
-- These are equivalent
CREATE TABLE users (...);
CREATE TABLE Users (...);
CREATE TABLE USERS (...);

-- This preserves case
CREATE TABLE "UserAccounts" (...);
```

---

## Command Reference

### Keyspace Commands

Keyspaces define namespaces and replication configuration for tables.

| Command | Description |
|---------|-------------|
| [CREATE KEYSPACE](keyspace.md#create-keyspace) | Create a new keyspace with replication settings |
| [ALTER KEYSPACE](keyspace.md#alter-keyspace) | Modify keyspace replication or options |
| [DROP KEYSPACE](keyspace.md#drop-keyspace) | Remove a keyspace and all contents |
| [USE](keyspace.md#use) | Set the current keyspace for the session |

### Table Commands

Tables store data as rows organized by primary key.

| Command | Description |
|---------|-------------|
| [CREATE TABLE](table.md#create-table) | Define a new table with columns and primary key |
| [ALTER TABLE](table.md#alter-table) | Add/drop columns or modify table options |
| [DROP TABLE](table.md#drop-table) | Remove a table and all its data |
| [TRUNCATE](table.md#truncate) | Remove all rows from a table |

### Index Commands

Indexes enable queries on non-primary-key columns.

| Command | Description |
|---------|-------------|
| [CREATE INDEX](create-index.md#create-index) | Create a secondary index or SAI index |
| [DROP INDEX](create-index.md#drop-index) | Remove an index |

#### Collection Indexing

Cassandra supports indexing collection types (SET, LIST, MAP) to enable `CONTAINS` and element-specific queries:

| Collection Type | Index Target | Query Enabled |
|-----------------|--------------|---------------|
| `SET<T>` | Column name | `WHERE set_col CONTAINS value` |
| `LIST<T>` | Column name | `WHERE list_col CONTAINS value` |
| `MAP<K,V>` | `KEYS(column)` | `WHERE map_col CONTAINS KEY key` |
| `MAP<K,V>` | `VALUES(column)` | `WHERE map_col CONTAINS value` |
| `MAP<K,V>` | `ENTRIES(column)` | `WHERE map_col[key] = value` |
| `FROZEN<collection>` | `FULL(column)` | `WHERE frozen_col = entire_value` |

```sql
-- Index SET elements
CREATE INDEX ON users (tags);
SELECT * FROM users WHERE tags CONTAINS 'premium';

-- Index MAP entries for key-value lookups
CREATE INDEX ON users (ENTRIES(attributes));
SELECT * FROM users WHERE attributes['role'] = 'admin';
```

#### User-Defined Type Indexing

UDT indexing capabilities depend on whether the type is frozen and the index implementation:

| UDT State | Index Type | Capability |
|-----------|------------|------------|
| `FROZEN<udt>` | 2i, SAI | Index entire frozen value for equality matching |
| Non-frozen | SAI (5.0+) | Index individual UDT fields |

**Frozen UDT indexing:**

```sql
CREATE TYPE address (
    street TEXT,
    city TEXT,
    zip TEXT
);

CREATE TABLE customers (
    id UUID PRIMARY KEY,
    home_address FROZEN<address>
);

-- Index entire frozen UDT
CREATE INDEX ON customers (home_address);

-- Query requires exact match of all fields
SELECT * FROM customers
WHERE home_address = {street: '123 Main St', city: 'NYC', zip: '10001'};
```

**Non-frozen UDT field indexing (SAI, Cassandra 5.0+):**

```sql
CREATE TABLE customers (
    id UUID PRIMARY KEY,
    home_address address  -- non-frozen
);

-- Index specific UDT field
CREATE CUSTOM INDEX ON customers (home_address.city)
    USING 'StorageAttachedIndex';

-- Query individual field
SELECT * FROM customers WHERE home_address.city = 'NYC';
```

!!! note "Frozen vs Non-Frozen UDT Indexing"
    - **Frozen UDTs**: Serialized as single value; only equality matching on complete UDT supported
    - **Non-frozen UDTs**: Individual fields addressable; SAI enables field-level indexing and queries
    - Legacy secondary indexes (2i) do not support non-frozen UDT field indexing

### Materialized View Commands

Materialized views maintain denormalized copies of base table data.

| Command | Description |
|---------|-------------|
| [CREATE MATERIALIZED VIEW](materialized-view.md#create-materialized-view) | Create an auto-maintained view |
| [ALTER MATERIALIZED VIEW](materialized-view.md#alter-materialized-view) | Modify view options |
| [DROP MATERIALIZED VIEW](materialized-view.md#drop-materialized-view) | Remove a materialized view |

### User-Defined Type Commands

UDTs define composite types with named fields.

| Command | Description |
|---------|-------------|
| [CREATE TYPE](type.md#create-type) | Define a new user-defined type |
| [ALTER TYPE](type.md#alter-type) | Add fields or rename existing fields |
| [DROP TYPE](type.md#drop-type) | Remove a user-defined type |

### Function Commands

User-defined functions extend CQL with custom scalar operations.

| Command | Description |
|---------|-------------|
| [CREATE FUNCTION](function.md#create-function) | Create a user-defined scalar function |
| [DROP FUNCTION](function.md#drop-function) | Remove a user-defined function |

### Aggregate Commands

User-defined aggregates process multiple rows into a single value.

| Command | Description |
|---------|-------------|
| [CREATE AGGREGATE](aggregate.md#create-aggregate) | Create a user-defined aggregate |
| [DROP AGGREGATE](aggregate.md#drop-aggregate) | Remove a user-defined aggregate |

---

## Best Practices

### Schema Design

!!! tip "Design Principles"
    - Design tables for specific query patterns (query-first modeling)
    - Denormalize data to avoid joins
    - Keep partition sizes under 100MB
    - Limit clustering columns to support required query patterns

### Schema Changes in Production

!!! warning "Production Deployments"
    1. **Test schema changes** in a staging environment first
    2. **Create snapshots** before applying changes
    3. **Apply changes during low-traffic periods** when possible
    4. **Monitor schema agreement** after changes
    5. **Run repairs** after replication changes

### Avoiding Common Issues

| Issue | Cause | Prevention |
|-------|-------|------------|
| Schema disagreement | Network issues, slow nodes | Monitor cluster health, increase timeout if needed |
| Orphaned data | Dropping columns without compaction | Run `nodetool compact` after dropping columns |
| Replication lag | Changing RF without repair | Always run repair after replication changes |
| Type mismatches | Incompatible column type changes | Only widen types (INT→BIGINT), never narrow |

---

## Compatibility

### CQL Version Features

| Feature | Minimum CQL Version | Cassandra Version |
|---------|---------------------|-------------------|
| Basic DDL | 3.0 | 2.0+ |
| User-Defined Types | 3.0 | 2.1+ |
| User-Defined Functions | 3.0 | 2.2+ |
| Materialized Views | 3.4 | 3.0+ |
| SASI Indexes | 3.4 | 3.4+ |
| Storage-Attached Indexes | 3.4.7 | 5.0+ |
| Vector Types | 3.4.7 | 5.0+ |

---

## Related Documentation

- **[DML Commands](../dml/index.md)** - Data manipulation: SELECT, INSERT, UPDATE, DELETE
- **[Security Commands](../security/index.md)** - Roles, permissions, GRANT, REVOKE
- **[Data Types](../data-types/index.md)** - Native types, collections, UDTs, vectors
- **[Data Modeling](../../data-modeling/index.md)** - Query-first design principles
- **[Architecture](../../architecture/index.md)** - Storage engine and distributed systems
