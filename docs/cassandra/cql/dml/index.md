# DML Commands

Data Manipulation Language (DML) commands retrieve and modify data in Cassandra tables. This reference documents the complete syntax for SELECT, INSERT, UPDATE, DELETE, and BATCH statements.

---

## SELECT

Retrieve rows from a table.

### Synopsis

```cqlsyntax
SELECT [ JSON | DISTINCT ] *select_clause*
    FROM [ *keyspace_name*. ] *table_name*
    [ WHERE *where_clause* ]
    [ GROUP BY *column_name* [, *column_name* ... ] ]
    [ ORDER BY *column_name* [ ASC | DESC ] [, *column_name* [ ASC | DESC ] ... ] ]
    [ PER PARTITION LIMIT *integer* ]
    [ LIMIT *integer* ]
    [ ALLOW FILTERING ]
```

**select_clause**:

```cqlsyntax
*
| *column_name* [ AS *alias* ] [, *column_name* [ AS *alias* ] ... ]
| *function_name* ( [ *arguments* ] ) [ AS *alias* ] [, ... ]
| COUNT (*) | COUNT (1)
```

**where_clause**:

```cqlsyntax
*relation* [ AND *relation* ... ]
```

**relation**:

```cqlsyntax
*column_name* *operator* *term*
| *column_name* IN ( *term* [, *term* ... ] )
| ( *column_name* [, *column_name* ... ] ) IN ( ( *term* [, *term* ... ] ) [, ... ] )
| TOKEN ( *column_name* [, *column_name* ... ] ) *operator* *term*
```

**operator**:

```cqlsyntax
= | < | > | <= | >= | CONTAINS | CONTAINS KEY
```

### Description

SELECT retrieves rows and columns from a table. Unlike SQL databases, Cassandra requires queries to include the partition key for efficient execution. Queries without partition key restrictions must include `ALLOW FILTERING` and result in a full cluster scan.

The query coordinator receives the request, determines which nodes hold the relevant partitions using the partition key hash, sends requests to those nodes based on the consistency level, and merges results before returning to the client.

### Parameters

**JSON**

Returns each row as a single JSON-encoded string column named `[json]`. All column values are converted to their JSON representations.

**DISTINCT**

Returns only the partition key columns, eliminating duplicate partition keys. Useful for listing all partitions in a table.

**select_clause**

Specifies which columns to retrieve. An asterisk (`*`) selects all columns. Individual columns can be specified with optional aliases. Aggregate functions (`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`) and scalar functions can be included.

**WHERE clause**

Filters rows based on conditions. Partition key columns must use equality (`=`) or `IN`. Clustering columns support equality, inequality (`<`, `>`, `<=`, `>=`), and range comparisons when partition key is specified. Regular columns require secondary indexes or `ALLOW FILTERING`.

| Column Type | Supported Operators | Notes |
|-------------|---------------------|-------|
| Partition key | `=`, `IN`, `TOKEN()` | Required for efficient queries |
| Clustering column | `=`, `<`, `>`, `<=`, `>=`, `IN` | Must follow primary key order |
| Regular column | `=`, `<`, `>`, `<=`, `>=`, `IN`, `CONTAINS` | Requires index or ALLOW FILTERING |

**GROUP BY**

Groups rows by specified columns for aggregate calculations. Columns must be partition key columns followed by clustering columns in order. Cannot skip clustering columns.

**ORDER BY**

Specifies result ordering. Only clustering columns in their defined order (or complete reverse) are permitted. The partition key must be restricted by equality.

**PER PARTITION LIMIT**

Limits rows returned from each partition. Applied before LIMIT. Useful for "top N per partition" queries.

**LIMIT**

Limits total rows returned. Default is 10,000 for cqlsh. Applied after PER PARTITION LIMIT.

**ALLOW FILTERING**

Permits queries that require scanning multiple partitions or filtering on non-indexed columns. These queries do not scale and should be avoided in production workloads.

### Examples

Basic query:

```sql
SELECT * FROM users WHERE user_id = 550e8400-e29b-41d4-a716-446655440000;
```

Select specific columns:

```sql
SELECT username, email, created_at FROM users WHERE user_id = ?;
```

Query with clustering column range:

```sql
SELECT * FROM events
WHERE tenant_id = 'acme'
  AND event_date = '2024-01-15'
  AND event_time >= '2024-01-15 00:00:00'
  AND event_time < '2024-01-15 12:00:00';
```

Query multiple partitions:

```sql
SELECT * FROM users WHERE user_id IN (
    550e8400-e29b-41d4-a716-446655440000,
    6ba7b810-9dad-11d1-80b4-00c04fd430c8
);
```

Aggregation:

```sql
SELECT COUNT(*), MIN(created_at), MAX(created_at) FROM users;
```

Group by with aggregates:

```sql
SELECT tenant_id, event_date, COUNT(*) as event_count
FROM events
WHERE tenant_id = 'acme'
GROUP BY tenant_id, event_date;
```

Ordering results:

```sql
SELECT * FROM messages
WHERE user_id = ?
ORDER BY sent_at DESC
LIMIT 20;
```

Per partition limit:

```sql
SELECT * FROM user_posts
WHERE user_id IN (?, ?, ?)
PER PARTITION LIMIT 5
LIMIT 100;
```

JSON output:

```sql
SELECT JSON * FROM users WHERE user_id = ?;
SELECT JSON user_id, username, email FROM users WHERE user_id = ?;
```

Token range query (full table scan):

```sql
SELECT * FROM users
WHERE TOKEN(user_id) > -9223372036854775808
  AND TOKEN(user_id) <= 0;
```

Check TTL and write time:

```sql
SELECT username, TTL(email), WRITETIME(email) FROM users WHERE user_id = ?;
```

### Notes

The `IN` clause on partition keys creates a multi-partition query that contacts multiple nodes. Limit to 10-20 values for acceptable performance.

Queries without WHERE clause return data from all partitions but are limited by the LIMIT clause. These execute as range scans and should only be used for small tables or administrative purposes.

Collection columns (`LIST`, `SET`, `MAP`) cannot be used in WHERE clauses without a secondary index. With an index, `CONTAINS` filters by element value and `CONTAINS KEY` filters by map key.

The `TOKEN()` function enables range scans across the token ring. This is used for full table scans in analytics workloads but should not be used in application queries.

---

## INSERT

Add a row to a table.

### Synopsis

```cqlsyntax
INSERT INTO [ *keyspace_name*. ] *table_name*
    ( *column_name* [, *column_name* ... ] )
    VALUES ( *term* [, *term* ... ] )
    [ IF NOT EXISTS ]
    [ USING *update_parameter* [ AND *update_parameter* ... ] ]
```

```cqlsyntax
INSERT INTO [ *keyspace_name*. ] *table_name*
    JSON *json_string*
    [ DEFAULT ( NULL | UNSET ) ]
    [ IF NOT EXISTS ]
    [ USING *update_parameter* [ AND *update_parameter* ... ] ]
```

**update_parameter**:

```cqlsyntax
TTL *seconds*
| TIMESTAMP *microseconds*
```

### Description

INSERT adds a new row or updates an existing row with the specified column values. Cassandra performs an upsert operation: if the row exists, it is updated; if it does not exist, it is created. This differs from SQL databases where INSERT fails if the row exists.

All primary key columns must be specified. Non-primary key columns not included in the INSERT retain their existing values (if the row exists) or remain unset (if the row is new).

### Parameters

**IF NOT EXISTS**

Converts the INSERT to a lightweight transaction (LWT) using Paxos consensus. The insert occurs only if no row with the specified primary key exists. Returns a result set with an `[applied]` column indicating success (true) or failure (false). When false, the existing row values are returned.

**USING TTL**

Sets Time-To-Live in seconds for the inserted columns. After the TTL expires, the columns are marked for deletion and removed during compaction. TTL applies to non-primary key columns only; primary key columns cannot expire.

**USING TIMESTAMP**

Sets the write timestamp in microseconds since Unix epoch. Cassandra uses timestamps for conflict resolution: the value with the highest timestamp wins. If not specified, the coordinator assigns the current time.

**JSON**

Accepts row data as a JSON object string. Keys must match column names. Missing keys use NULL or UNSET based on the DEFAULT clause.

**DEFAULT NULL | UNSET**

For JSON inserts, specifies handling of missing keys. `DEFAULT NULL` sets missing columns to null (creates a tombstone if the row exists). `DEFAULT UNSET` leaves missing columns unchanged. Default is `DEFAULT NULL`.

### Examples

Basic insert:

```sql
INSERT INTO users (user_id, username, email, created_at)
VALUES (uuid(), 'johndoe', 'john@example.com', toTimestamp(now()));
```

Insert with TTL (expires in 24 hours):

```sql
INSERT INTO sessions (session_id, user_id, token, created_at)
VALUES (uuid(), ?, 'abc123xyz', toTimestamp(now()))
USING TTL 86400;
```

Insert with explicit timestamp:

```sql
INSERT INTO users (user_id, username, email)
VALUES (uuid(), 'johndoe', 'john@example.com')
USING TIMESTAMP 1705315800000000;
```

Insert with TTL and timestamp:

```sql
INSERT INTO cache_entries (key, value)
VALUES ('user:123', 'cached_data')
USING TTL 3600 AND TIMESTAMP 1705315800000000;
```

Conditional insert (lightweight transaction):

```sql
INSERT INTO users (user_id, username, email)
VALUES (550e8400-e29b-41d4-a716-446655440000, 'unique_user', 'unique@example.com')
IF NOT EXISTS;
```

JSON insert:

```sql
INSERT INTO users JSON '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "jsonuser",
    "email": "json@example.com",
    "created_at": "2024-01-15T10:30:00.000Z"
}';
```

JSON insert with default unset:

```sql
INSERT INTO users JSON '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "partialuser"
}' DEFAULT UNSET;
```

Insert collection values:

```sql
-- List
INSERT INTO users (user_id, phone_numbers)
VALUES (uuid(), ['+1-555-0100', '+1-555-0101']);

-- Set
INSERT INTO users (user_id, roles)
VALUES (uuid(), {'admin', 'user', 'moderator'});

-- Map
INSERT INTO users (user_id, preferences)
VALUES (uuid(), {'theme': 'dark', 'language': 'en', 'timezone': 'UTC'});
```

Insert with frozen UDT:

```sql
INSERT INTO users (user_id, address)
VALUES (uuid(), {street: '123 Main St', city: 'Boston', zip: '02101'});
```

### Notes

INSERT and UPDATE are functionally equivalent in Cassandra. Both perform upserts and can set TTL and timestamp.

`IF NOT EXISTS` incurs approximately 4x latency compared to unconditional inserts due to Paxos consensus rounds. Use sparingly.

Inserting null for a column creates a tombstone, which has performance implications. Use UNSET to avoid creating tombstones for columns that should retain existing values.

---

## UPDATE

Modify column values in existing rows.

### Synopsis

```cqlsyntax
UPDATE [ *keyspace_name*. ] *table_name*
    [ USING *update_parameter* [ AND *update_parameter* ... ] ]
    SET *assignment* [, *assignment* ... ]
    WHERE *where_clause*
    [ IF *condition* [ AND *condition* ... ] | IF EXISTS ]
```

**update_parameter**:

```cqlsyntax
TTL *seconds*
| TIMESTAMP *microseconds*
```

**assignment**:

```cqlsyntax
*column_name* = *term*
| *column_name* = *column_name* ( + | - ) *term*
| *column_name* [ *index* ] = *term*
| *column_name* [ *key* ] = *term*
```

**condition**:

```cqlsyntax
*column_name* *operator* *term*
| *column_name* [ *index* ] *operator* *term*
| *column_name* [ *key* ] *operator* *term*
| *column_name* IN ( *term* [, *term* ... ] )
```

### Description

UPDATE modifies column values for rows matching the WHERE clause. Like INSERT, UPDATE performs an upsert: if the row does not exist, it is created with the specified values.

The WHERE clause must include all partition key columns with equality conditions. Clustering columns may be included to target specific rows within a partition.

### Parameters

**USING TTL**

Sets Time-To-Live for the updated columns. The TTL countdown begins from the update time. Setting TTL to 0 removes any existing TTL from the columns.

**USING TIMESTAMP**

Sets the write timestamp for conflict resolution. Only cells with timestamps lower than the specified value are updated.

**SET**

Specifies column assignments. Simple assignment replaces the value. Collection operations use `+` to add elements or `-` to remove elements. Indexed assignment updates specific list positions or map keys.

**WHERE**

Identifies rows to update. All partition key columns required with equality. Clustering columns narrow the scope within partitions. Range conditions on clustering columns update multiple rows.

**IF condition / IF EXISTS**

Converts the UPDATE to a lightweight transaction. `IF EXISTS` succeeds only if the row exists. `IF condition` succeeds only if the condition evaluates to true. Returns `[applied]` column with current values if the condition fails.

### Examples

Basic update:

```sql
UPDATE users
SET email = 'newemail@example.com'
WHERE user_id = 550e8400-e29b-41d4-a716-446655440000;
```

Update multiple columns:

```sql
UPDATE users
SET email = 'newemail@example.com',
    username = 'newusername',
    updated_at = toTimestamp(now())
WHERE user_id = ?;
```

Update with TTL:

```sql
UPDATE sessions USING TTL 3600
SET token = 'newtoken123'
WHERE session_id = ?;
```

Remove TTL from column:

```sql
UPDATE users USING TTL 0
SET temp_data = temp_data
WHERE user_id = ?;
```

Update with explicit timestamp:

```sql
UPDATE users USING TIMESTAMP 1705315800000000
SET email = 'timestamped@example.com'
WHERE user_id = ?;
```

Conditional update (lightweight transaction):

```sql
UPDATE users
SET email = 'verified@example.com'
WHERE user_id = ?
IF email = 'unverified@example.com';
```

Update if exists:

```sql
UPDATE users
SET last_login = toTimestamp(now())
WHERE user_id = ?
IF EXISTS;
```

List operations:

```sql
-- Append to list
UPDATE users SET phone_numbers = phone_numbers + ['+1-555-0102']
WHERE user_id = ?;

-- Prepend to list
UPDATE users SET phone_numbers = ['+1-555-0000'] + phone_numbers
WHERE user_id = ?;

-- Remove from list by value
UPDATE users SET phone_numbers = phone_numbers - ['+1-555-0100']
WHERE user_id = ?;

-- Update list by index
UPDATE users SET phone_numbers[0] = '+1-555-9999'
WHERE user_id = ?;
```

Set operations:

```sql
-- Add elements
UPDATE users SET roles = roles + {'moderator', 'reviewer'}
WHERE user_id = ?;

-- Remove elements
UPDATE users SET roles = roles - {'guest'}
WHERE user_id = ?;
```

Map operations:

```sql
-- Add or update entries
UPDATE users SET preferences = preferences + {'theme': 'dark', 'font_size': '14'}
WHERE user_id = ?;

-- Update single key
UPDATE users SET preferences['theme'] = 'light'
WHERE user_id = ?;

-- Remove entry (use DELETE syntax)
DELETE preferences['deprecated_key'] FROM users
WHERE user_id = ?;
```

Counter update:

```sql
UPDATE page_stats SET view_count = view_count + 1
WHERE page_id = 'homepage';

UPDATE user_stats SET follower_count = follower_count - 1
WHERE user_id = ?;
```

Update range of rows:

```sql
UPDATE sensor_readings USING TTL 86400
SET status = 'archived'
WHERE sensor_id = 'temp-001'
  AND reading_time >= '2024-01-01'
  AND reading_time < '2024-02-01';
```

### Notes

Counter columns can only be updated using increment (`+`) or decrement (`-`) operations. Direct assignment is not supported.

Collection updates are not idempotent. Appending the same element twice results in duplicates for lists.

List index operations (`column[n] = value`) require reading the list first to determine positions, which impacts performance and may cause race conditions.

`IF` conditions incur Paxos overhead. Avoid in high-throughput scenarios.

---

## DELETE

Remove rows or column values.

### Synopsis

```cqlsyntax
DELETE [ *column_name* [, *column_name* ... ] ]
    FROM [ *keyspace_name*. ] *table_name*
    [ USING TIMESTAMP *microseconds* ]
    WHERE *where_clause*
    [ IF *condition* [ AND *condition* ... ] | IF EXISTS ]
```

### Description

DELETE removes entire rows or specific column values. Cassandra does not immediately remove data; instead, it writes a tombstone marking the data as deleted. Tombstones are removed during compaction after `gc_grace_seconds` (default 10 days).

When column names are specified, only those columns are deleted. When no columns are specified, the entire row is deleted.

### Parameters

**column_name**

Specific columns to delete. Collection elements can be targeted using `column[index]` for lists or `column[key]` for maps. Omitting column names deletes the entire row.

**USING TIMESTAMP**

Specifies the deletion timestamp. Only data written with timestamps less than or equal to this value is deleted. Data written after this timestamp is preserved.

**WHERE**

Identifies rows to delete. Partition key columns required with equality. Clustering columns can restrict deletion to specific rows or ranges within a partition.

**IF condition / IF EXISTS**

Lightweight transaction conditions. The delete executes only if conditions are satisfied. Returns `[applied]` column indicating success.

### Examples

Delete entire row:

```sql
DELETE FROM users WHERE user_id = 550e8400-e29b-41d4-a716-446655440000;
```

Delete specific columns:

```sql
DELETE email, phone FROM users WHERE user_id = ?;
```

Delete list element by index:

```sql
DELETE phone_numbers[0] FROM users WHERE user_id = ?;
```

Delete map entry:

```sql
DELETE preferences['deprecated_setting'] FROM users WHERE user_id = ?;
```

Delete with timestamp:

```sql
DELETE FROM users
USING TIMESTAMP 1705315800000000
WHERE user_id = ?;
```

Conditional delete:

```sql
DELETE FROM users
WHERE user_id = ?
IF status = 'inactive';
```

Delete if exists:

```sql
DELETE FROM sessions
WHERE session_id = ?
IF EXISTS;
```

Delete range within partition:

```sql
DELETE FROM events
WHERE tenant_id = 'acme'
  AND event_date = '2024-01-15'
  AND event_time >= '2024-01-15 00:00:00'
  AND event_time < '2024-01-15 06:00:00';
```

Delete all rows in partition:

```sql
DELETE FROM user_messages WHERE user_id = ?;
```

### Notes

Tombstones consume storage and impact read performance. Excessive tombstones (from frequent deletes or TTL expirations) can cause read timeouts. Design data models to minimize deletes.

The `gc_grace_seconds` table property determines how long tombstones persist. This grace period prevents deleted data from reappearing if a node was down during the delete. In single-datacenter clusters with regular repairs, this can be reduced.

Range deletes create a single range tombstone rather than individual cell tombstones, which is more efficient.

Deleting from a counter column is not supported. Counter tables can only be truncated.

---

## BATCH

Execute multiple statements atomically.

### Synopsis

```cqlsyntax
BEGIN [ UNLOGGED | COUNTER ] BATCH
    [ USING TIMESTAMP *microseconds* ]
    *dml_statement* ;
    [ *dml_statement* ; ... ]
APPLY BATCH
```

**dml_statement**:

```cqlsyntax
INSERT ... | UPDATE ... | DELETE ...
```

### Description

BATCH groups multiple INSERT, UPDATE, or DELETE statements into a single operation. All statements in a logged batch are guaranteed to eventually complete or none will, providing atomicity across partitions.

Batches are not a performance optimization. Each statement in the batch is still executed as a separate mutation. Batches should be used when atomicity is required, not to reduce round trips.

### Parameters

**UNLOGGED**

Disables the batch log mechanism. Statements are sent directly to replicas without coordination through the batch log. Faster but provides no atomicity guarantee if failures occur. Recommended only when all statements target the same partition.

**COUNTER**

Required for batches containing counter updates. Counter batches cannot include non-counter statements.

**USING TIMESTAMP**

Applies the specified timestamp to all statements in the batch. Individual statements cannot override this timestamp.

### Examples

Logged batch (default):

```sql
BEGIN BATCH
    INSERT INTO users (user_id, username) VALUES (?, 'newuser');
    INSERT INTO user_emails (email, user_id) VALUES ('new@example.com', ?);
    UPDATE user_counts SET count = count + 1 WHERE counter_id = 'total';
APPLY BATCH;
```

Unlogged batch (same partition):

```sql
BEGIN UNLOGGED BATCH
    UPDATE user_profile SET name = 'John' WHERE user_id = ?;
    UPDATE user_profile SET email = 'john@example.com' WHERE user_id = ?;
    UPDATE user_profile SET updated_at = toTimestamp(now()) WHERE user_id = ?;
APPLY BATCH;
```

Counter batch:

```sql
BEGIN COUNTER BATCH
    UPDATE page_stats SET views = views + 1 WHERE page_id = 'home';
    UPDATE page_stats SET views = views + 1 WHERE page_id = 'about';
    UPDATE daily_stats SET requests = requests + 2 WHERE date = '2024-01-15';
APPLY BATCH;
```

Batch with timestamp:

```sql
BEGIN BATCH USING TIMESTAMP 1705315800000000
    INSERT INTO events (event_id, type) VALUES (uuid(), 'signup');
    INSERT INTO audit_log (log_id, action) VALUES (uuid(), 'user_created');
APPLY BATCH;
```

Conditional batch (lightweight transaction):

```sql
BEGIN BATCH
    INSERT INTO users (user_id, username) VALUES (?, 'newuser') IF NOT EXISTS;
    INSERT INTO usernames (username, user_id) VALUES ('newuser', ?) IF NOT EXISTS;
APPLY BATCH;
```

### Notes

Logged batches write to the batch log on the coordinator before execution. If the coordinator fails, another node replays the batch. This adds latency compared to unlogged batches.

Batches spanning multiple partitions require coordination across nodes. For optimal performance, group statements by partition.

Large batches (>5KB warn threshold, >50KB fail threshold by default) can overload coordinators and should be avoided. These thresholds are configured with `batch_size_warn_threshold_in_kb` and `batch_size_fail_threshold_in_kb`.

Conditional statements (`IF` clauses) within batches cause all statements to use Paxos, significantly increasing latency.

Mixing counter and non-counter statements in a batch is not permitted.

---

## Lightweight Transactions

Compare-and-set operations using Paxos consensus.

### Synopsis

```cqlsyntax
INSERT ... IF NOT EXISTS

UPDATE ... IF *condition* [ AND *condition* ... ]
UPDATE ... IF EXISTS

DELETE ... IF *condition* [ AND *condition* ... ]
DELETE ... IF EXISTS
```

### Description

Lightweight transactions (LWT) provide linearizable consistency for operations that require read-before-write semantics. They use the Paxos consensus protocol to ensure only one operation succeeds when concurrent modifications target the same row.

LWT operations return a result set with an `[applied]` boolean column. If false, the current row values are returned so the client can retry with updated conditions.

### Parameters

**IF NOT EXISTS**

For INSERT: succeeds only if no row with the primary key exists.

**IF EXISTS**

For UPDATE and DELETE: succeeds only if a row with the primary key exists.

**IF condition**

Succeeds only if all conditions evaluate to true against current row values. Conditions can reference any column and use comparison operators.

### Examples

Insert if not exists:

```sql
INSERT INTO users (user_id, username, email)
VALUES (?, 'desired_username', 'email@example.com')
IF NOT EXISTS;

-- Result if applied:
--  [applied]
--  True

-- Result if not applied:
--  [applied] | user_id | username | email
--  False     | ...     | ...      | ...
```

Update with condition:

```sql
UPDATE inventory
SET quantity = 99
WHERE product_id = 'SKU-001'
IF quantity = 100;
```

Update if exists:

```sql
UPDATE users
SET last_seen = toTimestamp(now())
WHERE user_id = ?
IF EXISTS;
```

Multiple conditions:

```sql
UPDATE accounts
SET balance = 900
WHERE account_id = ?
IF balance >= 100 AND status = 'active';
```

Optimistic locking pattern:

```sql
UPDATE documents
SET content = 'new content', version = 2
WHERE doc_id = ?
IF version = 1;
```

Delete with condition:

```sql
DELETE FROM sessions
WHERE session_id = ?
IF user_id = ? AND created_at < '2024-01-01';
```

### Notes

LWT operations have 4x higher latency than regular operations due to multiple consensus rounds.

Serial consistency (`SERIAL` or `LOCAL_SERIAL`) determines the scope of linearizability. `LOCAL_SERIAL` restricts Paxos to the local datacenter.

Contention on the same partition key causes LWT operations to fail and return `[applied] = false`. Implement retry logic with exponential backoff.

LWT should not be used for high-throughput operations. Consider data model changes to eliminate the need for read-before-write patterns.

All LWT operations on the same partition are serialized, limiting throughput to a single operation at a time per partition.

---

## Related Documentation

- **[DDL Commands](../ddl/index.md)** - Schema management
- **[Data Types](../data-types/index.md)** - CQL type reference
- **[Functions](../functions/index.md)** - Built-in and user-defined functions
- **[Data Modeling](../../data-modeling/index.md)** - Query-driven design patterns
