# DDL Commands

Data Definition Language (DDL) commands manage schema objects in Cassandra: keyspaces, tables, indexes, user-defined types, functions, and aggregates. Schema changes propagate through gossip and are applied online without blocking reads or writes.

---

## Keyspace Commands

### CREATE KEYSPACE

Create a new keyspace with replication configuration.

#### Synopsis

```cqlsyntax
CREATE KEYSPACE [ IF NOT EXISTS ] *keyspace_name*
    WITH REPLICATION = { *replication_map* }
    [ AND DURABLE_WRITES = { true | false } ]
```

**replication_map**:

```cqlsyntax
'class': '*strategy_name*' [, *strategy_options* ]
```

**strategy_name**:

| Strategy | Description | Options |
|----------|-------------|---------|
| `SimpleStrategy` | Single datacenter deployments | `'replication_factor': *n*` |
| `NetworkTopologyStrategy` | Multi-datacenter deployments | `'*datacenter_name*': *n* [, ...]` |

#### Description

CREATE KEYSPACE defines a new namespace for tables with specified replication settings. The replication strategy determines how data is distributed across nodes.

`SimpleStrategy` places replicas on consecutive nodes in the ring without considering datacenter topology. Use only for development or single-datacenter clusters.

`NetworkTopologyStrategy` places replicas in each datacenter according to specified replication factors, ensuring replicas are distributed across racks when possible. Required for multi-datacenter deployments.

#### Parameters

**IF NOT EXISTS**

Prevents an error if the keyspace already exists. The statement succeeds without modifying the existing keyspace.

**REPLICATION**

Required. Specifies the replication strategy and options. The strategy class determines how replicas are placed across the cluster.

**DURABLE_WRITES**

Controls whether writes to the keyspace are written to the commit log. Default is `true`. Setting to `false` disables the commit log for this keyspace, risking data loss on node failure. Use only for data that can be regenerated.

#### Examples

Development keyspace with SimpleStrategy:

```sql
CREATE KEYSPACE dev_keyspace
WITH REPLICATION = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};
```

Production keyspace with NetworkTopologyStrategy:

```sql
CREATE KEYSPACE prod_keyspace
WITH REPLICATION = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3,
    'dc2': 3
};
```

Keyspace with durable writes disabled:

```sql
CREATE KEYSPACE cache_keyspace
WITH REPLICATION = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3
}
AND DURABLE_WRITES = false;
```

Idempotent creation:

```sql
CREATE KEYSPACE IF NOT EXISTS my_keyspace
WITH REPLICATION = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3
};
```

#### Notes

After creating a keyspace, run `nodetool repair` if data needs to be distributed according to the new replication settings.

Keyspace names are case-insensitive unless quoted. Quoted names preserve case and allow special characters.

---

### ALTER KEYSPACE

Modify keyspace properties.

#### Synopsis

```cqlsyntax
ALTER KEYSPACE *keyspace_name*
    WITH REPLICATION = { *replication_map* }
    [ AND DURABLE_WRITES = { true | false } ]
```

#### Description

ALTER KEYSPACE changes the replication strategy or durable writes setting for an existing keyspace. The change takes effect immediately for new writes.

#### Examples

Change replication factor:

```sql
ALTER KEYSPACE my_keyspace
WITH REPLICATION = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 5
};
```

Add a datacenter:

```sql
ALTER KEYSPACE my_keyspace
WITH REPLICATION = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3,
    'dc2': 3
};
```

#### Notes

After altering replication, run `nodetool repair` on all nodes to redistribute data according to the new settings. Until repair completes, reads at consistency levels requiring more replicas than available may fail.

---

### DROP KEYSPACE

Remove a keyspace and all its contents.

#### Synopsis

```cqlsyntax
DROP KEYSPACE [ IF EXISTS ] *keyspace_name*
```

#### Description

DROP KEYSPACE permanently removes a keyspace and all tables, data, indexes, types, functions, and aggregates within it. This operation cannot be undone.

#### Examples

```sql
DROP KEYSPACE my_keyspace;
DROP KEYSPACE IF EXISTS my_keyspace;
```

#### Notes

Dropping a keyspace is an immediate metadata operation. Data files are deleted asynchronously.

---

### USE

Set the current keyspace for the session.

#### Synopsis

```cqlsyntax
USE *keyspace_name*
```

#### Description

USE sets the default keyspace for subsequent statements that do not specify a keyspace explicitly. This is a session-level setting.

#### Examples

```sql
USE my_keyspace;
SELECT * FROM users;  -- Queries my_keyspace.users
```

---

## Table Commands

### CREATE TABLE

Create a new table with columns and primary key.

#### Synopsis

```cqlsyntax
CREATE TABLE [ IF NOT EXISTS ] [ *keyspace_name*. ] *table_name*
    ( *column_definition* [, *column_definition* ... ] ,
      PRIMARY KEY ( *primary_key* ) )
    [ WITH *table_options* ]
```

**column_definition**:

```cqlsyntax
*column_name* *data_type* [ STATIC ] [ PRIMARY KEY ]
```

**primary_key**:

```cqlsyntax
*partition_key*
| ( *partition_key* ) [, *clustering_column* ... ]
```

**partition_key**:

```cqlsyntax
*column_name*
| ( *column_name* [, *column_name* ... ] )
```

**table_options**:

```cqlsyntax
*option* = *value* [ AND *option* = *value* ... ]
| CLUSTERING ORDER BY ( *column_name* [ ASC | DESC ] [, ... ] )
| COMPACT STORAGE
```

#### Description

CREATE TABLE defines a new table with specified columns and primary key structure. The primary key determines data distribution and query capabilities.

The partition key (first element of PRIMARY KEY) determines which node stores each row. Rows with the same partition key are stored together, enabling efficient range queries.

Clustering columns (remaining PRIMARY KEY elements) determine sort order within a partition and enable range queries on those columns.

#### Parameters

**STATIC**

Marks a column as static. Static columns have one value per partition, shared by all rows in that partition. Cannot be part of the primary key.

**CLUSTERING ORDER BY**

Specifies the sort order for clustering columns. Default is ascending (ASC). Determines both on-disk storage order and default query order.

**table_options**

| Option | Default | Description |
|--------|---------|-------------|
| `bloom_filter_fp_chance` | 0.01 | False positive rate for bloom filter |
| `caching` | keys: ALL, rows: NONE | Caching configuration |
| `comment` | empty | Human-readable description |
| `compaction` | STCS | Compaction strategy and options |
| `compression` | LZ4 | Compression algorithm |
| `crc_check_chance` | 1.0 | Probability of CRC check on reads |
| `default_time_to_live` | 0 | Default TTL in seconds |
| `gc_grace_seconds` | 864000 | Tombstone retention period |
| `max_index_interval` | 2048 | Maximum index interval |
| `memtable_flush_period_in_ms` | 0 | Automatic flush interval |
| `min_index_interval` | 128 | Minimum index interval |
| `read_repair` | BLOCKING | Read repair behavior |
| `speculative_retry` | 99p | Speculative retry threshold |

#### Examples

Simple primary key:

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    username TEXT,
    email TEXT,
    created_at TIMESTAMP
);
```

Compound primary key with clustering:

```sql
CREATE TABLE messages (
    user_id UUID,
    sent_at TIMESTAMP,
    message_id UUID,
    content TEXT,
    PRIMARY KEY ((user_id), sent_at, message_id)
) WITH CLUSTERING ORDER BY (sent_at DESC, message_id ASC);
```

Composite partition key:

```sql
CREATE TABLE events (
    tenant_id TEXT,
    event_date DATE,
    event_time TIMESTAMP,
    event_id UUID,
    payload TEXT,
    PRIMARY KEY ((tenant_id, event_date), event_time, event_id)
);
```

Static columns:

```sql
CREATE TABLE user_posts (
    user_id UUID,
    post_id TIMEUUID,
    username TEXT STATIC,
    user_email TEXT STATIC,
    post_content TEXT,
    PRIMARY KEY ((user_id), post_id)
);
```

With table options:

```sql
CREATE TABLE sensor_data (
    sensor_id TEXT,
    reading_time TIMESTAMP,
    value DOUBLE,
    PRIMARY KEY ((sensor_id), reading_time)
) WITH CLUSTERING ORDER BY (reading_time DESC)
    AND compaction = {
        'class': 'TimeWindowCompactionStrategy',
        'compaction_window_unit': 'HOURS',
        'compaction_window_size': '1'
    }
    AND compression = {'class': 'LZ4Compressor'}
    AND default_time_to_live = 2592000
    AND gc_grace_seconds = 86400;
```

Collections:

```sql
CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY,
    phone_numbers LIST<TEXT>,
    tags SET<TEXT>,
    preferences MAP<TEXT, TEXT>
);
```

Frozen UDT:

```sql
CREATE TABLE customers (
    customer_id UUID PRIMARY KEY,
    name TEXT,
    address FROZEN<address_type>
);
```

#### Notes

Tables require at least one partition key column. Partition keys cannot be modified after table creation.

Collection columns (`LIST`, `SET`, `MAP`) cannot be part of the primary key unless frozen.

The `COMPACT STORAGE` option is deprecated and should not be used for new tables.

---

### ALTER TABLE

Modify table schema or properties.

#### Synopsis

```cqlsyntax
ALTER TABLE [ *keyspace_name*. ] *table_name* *alter_instruction*
```

**alter_instruction**:

```cqlsyntax
ADD *column_name* *data_type* [ STATIC ] [, *column_name* *data_type* [ STATIC ] ... ]
| DROP *column_name* [, *column_name* ... ]
| RENAME *column_name* TO *new_name* [ AND *column_name* TO *new_name* ... ]
| WITH *table_options*
```

#### Description

ALTER TABLE modifies an existing table's columns or options. Adding columns is an instant metadata operation. Dropping columns marks the data for removal during compaction.

#### Parameters

**ADD**

Adds one or more columns. New columns have null values for existing rows. Cannot add primary key columns.

**DROP**

Removes columns from the table schema. Data is not immediately deleted; it is removed during compaction. Cannot drop primary key columns.

**RENAME**

Renames clustering columns. Cannot rename partition key columns or regular columns.

**WITH**

Modifies table options such as compaction strategy, compression, or TTL settings.

#### Examples

Add columns:

```sql
ALTER TABLE users ADD phone TEXT;
ALTER TABLE users ADD phone TEXT, address TEXT, age INT;
ALTER TABLE users ADD metadata TEXT STATIC;
```

Drop columns:

```sql
ALTER TABLE users DROP phone;
ALTER TABLE users DROP phone, address;
```

Rename clustering column:

```sql
ALTER TABLE events RENAME event_time TO occurred_at;
```

Change table options:

```sql
ALTER TABLE logs WITH
    compaction = {'class': 'LeveledCompactionStrategy'}
    AND compression = {'class': 'ZstdCompressor'};
```

Change TTL:

```sql
ALTER TABLE sessions WITH default_time_to_live = 7200;
```

#### Notes

Adding columns to tables with existing data is instant because Cassandra does not rewrite existing rows.

Dropped column data remains on disk until compaction. To immediately free space, run `nodetool compact`.

---

### DROP TABLE

Remove a table and all its data.

#### Synopsis

```cqlsyntax
DROP TABLE [ IF EXISTS ] [ *keyspace_name*. ] *table_name*
```

#### Description

DROP TABLE permanently removes a table and all its data, indexes, and materialized views. This operation cannot be undone.

#### Examples

```sql
DROP TABLE users;
DROP TABLE IF EXISTS my_keyspace.users;
```

---

### TRUNCATE

Remove all data from a table.

#### Synopsis

```cqlsyntax
TRUNCATE [ TABLE ] [ *keyspace_name*. ] *table_name*
```

#### Description

TRUNCATE removes all rows from a table while preserving the schema. A snapshot is created before truncation.

#### Examples

```sql
TRUNCATE users;
TRUNCATE TABLE my_keyspace.users;
```

#### Notes

TRUNCATE requires all nodes to be available and acknowledges the operation. On large tables, this may take significant time.

The automatic snapshot can be disabled with `auto_snapshot: false` in cassandra.yaml, but this is not recommended.

---

## Index Commands

### CREATE INDEX

Create a secondary index on a column.

#### Synopsis

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

**index_class** (for CUSTOM INDEX):

```cqlsyntax
'StorageAttachedIndex'
| 'org.apache.cassandra.index.sasi.SASIIndex'
```

#### Description

CREATE INDEX creates a secondary index enabling queries on non-primary key columns. Secondary indexes are stored locally on each node, indexing only the data that node owns.

Storage-Attached Indexes (SAI), introduced in Cassandra 5.0, provide improved performance over legacy secondary indexes, especially for high-cardinality columns and range queries.

#### Parameters

**CUSTOM**

Creates a custom index using the specified implementation class. Required for SAI and SASI indexes.

**index_target**

Specifies what to index:

| Target | Collection Type | Indexes |
|--------|-----------------|---------|
| `column_name` | Regular/SET/LIST | Column values |
| `KEYS(column)` | MAP | Map keys |
| `VALUES(column)` | MAP | Map values |
| `ENTRIES(column)` | MAP | Key-value pairs |
| `FULL(column)` | FROZEN | Entire frozen collection |

**USING**

Specifies the index implementation. Default is the legacy secondary index.

**WITH OPTIONS**

Index-specific options. SAI supports `case_sensitive`, `normalize`, and `ascii` for text columns.

#### Examples

Basic secondary index:

```sql
CREATE INDEX ON users (email);
CREATE INDEX users_email_idx ON users (email);
```

Index on collection elements:

```sql
CREATE INDEX ON users (tags);  -- SET elements
CREATE INDEX ON users (KEYS(preferences));  -- MAP keys
CREATE INDEX ON users (VALUES(preferences));  -- MAP values
CREATE INDEX ON users (ENTRIES(preferences));  -- MAP entries
```

SAI index (Cassandra 5.0+):

```sql
CREATE CUSTOM INDEX ON users (email) USING 'StorageAttachedIndex';

CREATE CUSTOM INDEX ON users (username) USING 'StorageAttachedIndex'
WITH OPTIONS = {
    'case_sensitive': 'false',
    'normalize': 'true'
};
```

#### Notes

Secondary indexes perform best on low-to-medium cardinality columns where queries also include the partition key.

High-cardinality indexes (many unique values) can cause performance issues because queries must contact many nodes.

SAI indexes support range queries on numeric columns and LIKE queries on text columns.

---

### DROP INDEX

Remove an index.

#### Synopsis

```cqlsyntax
DROP INDEX [ IF EXISTS ] [ *keyspace_name*. ] *index_name*
```

#### Examples

```sql
DROP INDEX users_email_idx;
DROP INDEX IF EXISTS my_keyspace.users_email_idx;
```

---

## Materialized View Commands

### CREATE MATERIALIZED VIEW

Create an automatically maintained denormalized view.

#### Synopsis

```cqlsyntax
CREATE MATERIALIZED VIEW [ IF NOT EXISTS ] [ *keyspace_name*. ] *view_name*
    AS SELECT *select_clause*
    FROM [ *keyspace_name*. ] *base_table*
    WHERE *where_clause*
    PRIMARY KEY ( *primary_key* )
    [ WITH *table_options* ]
```

#### Description

CREATE MATERIALIZED VIEW creates a server-maintained copy of base table data organized by a different primary key. Cassandra automatically propagates inserts, updates, and deletes from the base table to the view.

#### Parameters

**select_clause**

Columns to include in the view. Must include all base table primary key columns.

**WHERE clause**

Must include `IS NOT NULL` conditions for all view primary key columns.

**PRIMARY KEY**

Must include all base table primary key columns. May reorder columns or add one regular column from the base table.

#### Examples

View with reordered primary key:

```sql
CREATE MATERIALIZED VIEW users_by_email AS
    SELECT user_id, email, username, created_at
    FROM users
    WHERE email IS NOT NULL AND user_id IS NOT NULL
    PRIMARY KEY (email, user_id);
```

View with additional clustering column:

```sql
CREATE MATERIALIZED VIEW users_by_country AS
    SELECT *
    FROM users
    WHERE country IS NOT NULL AND user_id IS NOT NULL
    PRIMARY KEY (country, user_id);
```

#### Notes

Materialized views add write latency because updates must be propagated synchronously.

Views cannot be altered after creation. To change the schema, drop and recreate the view.

Only one non-primary key column from the base table can be added to the view's primary key.

---

### ALTER MATERIALIZED VIEW

Modify view properties.

#### Synopsis

```cqlsyntax
ALTER MATERIALIZED VIEW [ *keyspace_name*. ] *view_name*
    WITH *table_options*
```

#### Examples

```sql
ALTER MATERIALIZED VIEW users_by_email
WITH compaction = {'class': 'LeveledCompactionStrategy'};
```

---

### DROP MATERIALIZED VIEW

Remove a materialized view.

#### Synopsis

```cqlsyntax
DROP MATERIALIZED VIEW [ IF EXISTS ] [ *keyspace_name*. ] *view_name*
```

#### Examples

```sql
DROP MATERIALIZED VIEW users_by_email;
DROP MATERIALIZED VIEW IF EXISTS my_keyspace.users_by_email;
```

---

## User-Defined Type Commands

### CREATE TYPE

Create a user-defined type.

#### Synopsis

```cqlsyntax
CREATE TYPE [ IF NOT EXISTS ] [ *keyspace_name*. ] *type_name*
    ( *field_name* *data_type* [, *field_name* *data_type* ... ] )
```

#### Description

CREATE TYPE defines a composite type containing multiple named fields. UDTs must be frozen when used as column types.

#### Examples

```sql
CREATE TYPE address (
    street TEXT,
    city TEXT,
    state TEXT,
    zip TEXT,
    country TEXT
);

CREATE TYPE phone (
    country_code TEXT,
    number TEXT,
    type TEXT
);
```

Using UDTs in tables:

```sql
CREATE TABLE customers (
    customer_id UUID PRIMARY KEY,
    name TEXT,
    home_address FROZEN<address>,
    phones LIST<FROZEN<phone>>
);
```

---

### ALTER TYPE

Modify a user-defined type.

#### Synopsis

```cqlsyntax
ALTER TYPE [ *keyspace_name*. ] *type_name* *alter_instruction*
```

**alter_instruction**:

```cqlsyntax
ADD *field_name* *data_type*
| RENAME *field_name* TO *new_name* [ AND *field_name* TO *new_name* ... ]
```

#### Description

ALTER TYPE adds fields or renames existing fields. Fields cannot be dropped or have their types changed.

#### Examples

```sql
ALTER TYPE address ADD apartment TEXT;
ALTER TYPE address RENAME zip TO postal_code;
```

#### Notes

Adding fields to a UDT does not affect existing data. New fields have null values in existing rows.

---

### DROP TYPE

Remove a user-defined type.

#### Synopsis

```cqlsyntax
DROP TYPE [ IF EXISTS ] [ *keyspace_name*. ] *type_name*
```

#### Description

DROP TYPE removes a UDT. The type cannot be in use by any table or other type.

#### Examples

```sql
DROP TYPE address;
DROP TYPE IF EXISTS my_keyspace.phone;
```

---

## Function Commands

### CREATE FUNCTION

Create a user-defined function.

#### Synopsis

```cqlsyntax
CREATE [ OR REPLACE ] FUNCTION [ IF NOT EXISTS ] [ *keyspace_name*. ] *function_name*
    ( [ *arg_name* *arg_type* [, *arg_name* *arg_type* ... ] ] )
    { CALLED ON NULL INPUT | RETURNS NULL ON NULL INPUT }
    RETURNS *return_type*
    LANGUAGE { java | javascript }
    AS '*function_body*'
```

#### Description

CREATE FUNCTION defines a user-defined scalar function (UDF) that can be used in SELECT, WHERE, and other CQL clauses.

#### Parameters

**CALLED ON NULL INPUT**

Function is invoked even when arguments are null.

**RETURNS NULL ON NULL INPUT**

Function returns null immediately if any argument is null, without executing.

**LANGUAGE**

Programming language for the function body. Java is always available. JavaScript requires enabling in cassandra.yaml.

#### Examples

Java function:

```sql
CREATE FUNCTION my_keyspace.double_value(input INT)
    CALLED ON NULL INPUT
    RETURNS INT
    LANGUAGE java
    AS 'return input == null ? null : input * 2;';
```

JavaScript function:

```sql
CREATE FUNCTION my_keyspace.concat_strings(a TEXT, b TEXT)
    RETURNS NULL ON NULL INPUT
    RETURNS TEXT
    LANGUAGE javascript
    AS 'a + b';
```

#### Notes

UDFs must be enabled in cassandra.yaml:

```yaml
enable_user_defined_functions: true
enable_scripted_user_defined_functions: true  # For JavaScript
```

UDFs execute in a sandboxed environment with restrictions on system access.

---

### DROP FUNCTION

Remove a user-defined function.

#### Synopsis

```cqlsyntax
DROP FUNCTION [ IF EXISTS ] [ *keyspace_name*. ] *function_name*
    [ ( [ *arg_type* [, *arg_type* ... ] ] ) ]
```

#### Description

DROP FUNCTION removes a UDF. If multiple overloads exist, specify argument types to identify the function.

#### Examples

```sql
DROP FUNCTION my_keyspace.double_value;
DROP FUNCTION my_keyspace.concat_strings(TEXT, TEXT);
DROP FUNCTION IF EXISTS my_keyspace.my_function;
```

---

## Aggregate Commands

### CREATE AGGREGATE

Create a user-defined aggregate function.

#### Synopsis

```cqlsyntax
CREATE [ OR REPLACE ] AGGREGATE [ IF NOT EXISTS ] [ *keyspace_name*. ] *aggregate_name*
    ( [ *arg_type* [, *arg_type* ... ] ] )
    SFUNC *state_function*
    STYPE *state_type*
    [ FINALFUNC *final_function* ]
    [ INITCOND *initial_condition* ]
```

#### Description

CREATE AGGREGATE defines a user-defined aggregate function (UDA) that processes multiple rows and returns a single value.

#### Parameters

**SFUNC**

The state function called for each row. Must accept the state type as first argument followed by the aggregate's input types.

**STYPE**

The type of the state variable accumulated across rows.

**FINALFUNC**

Optional function to transform the final state into the result. If omitted, the final state is returned directly.

**INITCOND**

Initial value for the state variable. Defaults to null.

#### Examples

Sum aggregate:

```sql
CREATE FUNCTION my_keyspace.sum_state(state INT, val INT)
    RETURNS NULL ON NULL INPUT
    RETURNS INT
    LANGUAGE java
    AS 'return state + val;';

CREATE AGGREGATE my_keyspace.my_sum(INT)
    SFUNC sum_state
    STYPE INT
    INITCOND 0;
```

Average aggregate with final function:

```sql
CREATE FUNCTION my_keyspace.avg_state(state TUPLE<BIGINT, BIGINT>, val INT)
    CALLED ON NULL INPUT
    RETURNS TUPLE<BIGINT, BIGINT>
    LANGUAGE java
    AS 'if (val == null) return state; return new Tuple(state.getLong(0) + val, state.getLong(1) + 1);';

CREATE FUNCTION my_keyspace.avg_final(state TUPLE<BIGINT, BIGINT>)
    RETURNS NULL ON NULL INPUT
    RETURNS DOUBLE
    LANGUAGE java
    AS 'return (double)state.getLong(0) / state.getLong(1);';

CREATE AGGREGATE my_keyspace.my_avg(INT)
    SFUNC avg_state
    STYPE TUPLE<BIGINT, BIGINT>
    FINALFUNC avg_final
    INITCOND (0, 0);
```

---

### DROP AGGREGATE

Remove a user-defined aggregate.

#### Synopsis

```cqlsyntax
DROP AGGREGATE [ IF EXISTS ] [ *keyspace_name*. ] *aggregate_name*
    [ ( [ *arg_type* [, *arg_type* ... ] ] ) ]
```

#### Examples

```sql
DROP AGGREGATE my_keyspace.my_sum;
DROP AGGREGATE my_keyspace.my_avg(INT);
DROP AGGREGATE IF EXISTS my_keyspace.my_aggregate;
```

---

## Security Commands

### CREATE ROLE

Create a role for authentication and authorization.

#### Synopsis

```cqlsyntax
CREATE ROLE [ IF NOT EXISTS ] *role_name*
    [ WITH *role_option* [ AND *role_option* ... ] ]
```

**role_option**:

```cqlsyntax
PASSWORD = '*password*'
| LOGIN = { true | false }
| SUPERUSER = { true | false }
| OPTIONS = { *option_map* }
```

#### Description

CREATE ROLE creates a new role for authentication (LOGIN) and/or authorization (permissions). Roles can be granted to other roles to create hierarchical permission structures.

#### Examples

Login role:

```sql
CREATE ROLE app_user WITH PASSWORD = 'secret' AND LOGIN = true;
```

Superuser role:

```sql
CREATE ROLE admin WITH PASSWORD = 'admin_pwd' AND LOGIN = true AND SUPERUSER = true;
```

Permission group (no login):

```sql
CREATE ROLE developers;
CREATE ROLE readers;
```

---

### ALTER ROLE

Modify role properties.

#### Synopsis

```cqlsyntax
ALTER ROLE *role_name*
    WITH *role_option* [ AND *role_option* ... ]
```

#### Examples

```sql
ALTER ROLE app_user WITH PASSWORD = 'new_password';
ALTER ROLE app_user WITH SUPERUSER = true;
ALTER ROLE app_user WITH LOGIN = false;
```

---

### DROP ROLE

Remove a role.

#### Synopsis

```cqlsyntax
DROP ROLE [ IF EXISTS ] *role_name*
```

#### Examples

```sql
DROP ROLE app_user;
DROP ROLE IF EXISTS temp_user;
```

---

### GRANT

Grant permissions or roles.

#### Synopsis

```cqlsyntax
GRANT *permission* ON *resource* TO *role_name*
GRANT *role_name* TO *role_name*
```

**permission**:

```cqlsyntax
ALL [ PERMISSIONS ]
| ALTER | AUTHORIZE | CREATE | DESCRIBE | DROP | EXECUTE | MODIFY | SELECT
```

**resource**:

```cqlsyntax
ALL KEYSPACES
| KEYSPACE *keyspace_name*
| [ TABLE ] [ *keyspace_name*. ] *table_name*
| ALL FUNCTIONS [ IN KEYSPACE *keyspace_name* ]
| FUNCTION [ *keyspace_name*. ] *function_name* ( [ *arg_type* [, ... ] ] )
| ALL ROLES
| ROLE *role_name*
```

#### Examples

Grant permissions:

```sql
GRANT SELECT ON KEYSPACE my_keyspace TO reader_role;
GRANT MODIFY ON my_keyspace.users TO writer_role;
GRANT ALL PERMISSIONS ON KEYSPACE my_keyspace TO admin_role;
GRANT EXECUTE ON FUNCTION my_keyspace.my_func(INT) TO app_role;
```

Grant role to role:

```sql
GRANT developers TO senior_dev;
GRANT readers TO app_user;
```

---

### REVOKE

Remove permissions or roles.

#### Synopsis

```cqlsyntax
REVOKE *permission* ON *resource* FROM *role_name*
REVOKE *role_name* FROM *role_name*
```

#### Examples

```sql
REVOKE MODIFY ON my_keyspace.users FROM app_role;
REVOKE developers FROM junior_dev;
```

---

### LIST PERMISSIONS

Display granted permissions.

#### Synopsis

```cqlsyntax
LIST *permission* [ ON *resource* ] [ OF *role_name* ] [ NORECURSIVE ]
```

#### Examples

```sql
LIST ALL PERMISSIONS;
LIST ALL PERMISSIONS OF app_user;
LIST SELECT ON KEYSPACE my_keyspace;
LIST ALL PERMISSIONS OF app_user NORECURSIVE;
```

---

### LIST ROLES

Display roles.

#### Synopsis

```cqlsyntax
LIST ROLES [ OF *role_name* ] [ NORECURSIVE ]
```

#### Examples

```sql
LIST ROLES;
LIST ROLES OF admin;
LIST ROLES OF admin NORECURSIVE;
```

---

## Administrative Commands

### DESCRIBE

Display schema information.

#### Synopsis

```cqlsyntax
DESCRIBE CLUSTER
| DESCRIBE [ FULL ] SCHEMA
| DESCRIBE KEYSPACES
| DESCRIBE [ KEYSPACE ] *keyspace_name*
| DESCRIBE TABLES
| DESCRIBE [ TABLE ] [ *keyspace_name*. ] *table_name*
| DESCRIBE INDEX *index_name*
| DESCRIBE MATERIALIZED VIEW *view_name*
| DESCRIBE TYPE [ *keyspace_name*. ] *type_name*
| DESCRIBE FUNCTION [ *keyspace_name*. ] *function_name*
| DESCRIBE AGGREGATE [ *keyspace_name*. ] *aggregate_name*
```

#### Examples

```sql
DESCRIBE CLUSTER;
DESCRIBE KEYSPACES;
DESCRIBE KEYSPACE my_keyspace;
DESCRIBE TABLE my_keyspace.users;
DESCRIBE FULL SCHEMA;
```

---

## Related Documentation

- **[DML Commands](../dml/index.md)** - SELECT, INSERT, UPDATE, DELETE, BATCH
- **[Data Types](../data-types/index.md)** - Native types, collections, UDTs
- **[Functions](../functions/index.md)** - Built-in and user-defined functions
- **[Indexing](../indexing/index.md)** - Secondary indexes and SAI
