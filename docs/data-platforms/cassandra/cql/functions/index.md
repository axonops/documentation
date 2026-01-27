---
title: "Cassandra CQL Functions Reference"
description: "Cassandra CQL built-in functions reference including aggregates, time functions, type conversions, and UUID generation."
meta:
  - name: keywords
    content: "CQL functions, built-in functions, uuid(), now(), toTimestamp(), Cassandra"
---

# CQL Functions Reference

CQL includes built-in functions for common operations: generating UUIDs, working with timestamps, computing aggregates. The most useful ones `now()` for time-based UUIDs, `token()` for understanding data distribution, `toTimestamp()` for converting between time formats show up constantly in production schemas.

Aggregates deserve a warning: `SELECT COUNT(*) FROM users` looks innocent, but without a partition key it scans the entire cluster. That is fine for a thousand rows; it will timeout with a billion. Aggregates work efficiently when scoped to a partition.

This reference covers scalar functions, aggregates, and user-defined functions (available since Cassandra 2.2).

---

## Behavioral Guarantees

### What Functions Guarantee

- Scalar functions are evaluated on the coordinator for each result row
- `uuid()` generates a unique random UUID (version 4) per invocation
- `now()` generates the same time-based UUID (version 1) for all invocations within a single statement
- `token()` returns the partition token for the given partition key columns
- Aggregate functions are evaluated on the coordinator after collecting all matching rows
- Type conversion functions fail predictably on incompatible input

### What Functions Do NOT Guarantee

!!! warning "Undefined Behavior"
    The following behaviors are undefined and must not be relied upon:

    - **`now()` monotonicity**: Multiple `now()` calls in a statement return the same value; across statements, clock skew may cause non-monotonic values
    - **Aggregate performance**: Aggregates without partition key constraints scan the entire cluster with unbounded latency
    - **`uuid()` ordering**: Random UUIDs have no ordering relationship
    - **Cross-node time consistency**: Time functions reflect coordinator node's clock; clock skew between nodes affects results
    - **Null propagation**: Some functions return null on null input; others may fail

### Function Evaluation Contract

| Function Type | Evaluation Location | Per-Row | Notes |
|---------------|--------------------:|:-------:|-------|
| Scalar | Coordinator | ✅ Yes | Evaluated for each result row |
| Aggregate | Coordinator | ❌ No | Evaluated once after collecting rows |
| `now()` | Coordinator | ❌ No | Same value within statement |
| `uuid()` | Coordinator | ✅ Yes | Different value per invocation |
| `token()` | Coordinator | ✅ Yes | Computed from partition key |

### Time Function Contract

| Function | Return Type | Uniqueness | Monotonicity |
|----------|-------------|------------|--------------|
| `now()` | `timeuuid` | Unique per statement | Within node only |
| `currentTimestamp()` | `timestamp` | Not unique | Within node only |
| `currentTimeUUID()` | `timeuuid` | Unique per invocation | Within node only |
| `currentDate()` | `date` | Not unique | Within node only |
| `currentTime()` | `time` | Not unique | Within node only |

### Aggregate Performance Contract

| Query Pattern | Performance | Notes |
|---------------|-------------|-------|
| `SELECT COUNT(*) FROM t WHERE pk = ?` | Fast | Single partition |
| `SELECT COUNT(*) FROM t` | Slow/Timeout | Full cluster scan |
| `SELECT SUM(x) FROM t WHERE pk = ?` | Fast | Single partition |
| `SELECT AVG(x) FROM t` | Slow/Timeout | Full cluster scan |

### Version-Specific Behavior

| Version | Behavior |
|---------|----------|
| 2.2+ | User-defined functions (UDFs) |
| 3.0+ | `toDate()`, `toTimestamp()` conversion functions |
| 4.0+ | Improved function execution, `currentTimestamp()` |
| 5.0+ | Vector similarity functions, masking functions |

---

## Function Categories

| Category | Purpose | Examples |
|----------|---------|----------|
| Scalar | Transform single values | `toDate()`, `token()`, `cast()` |
| Aggregate | Compute across rows | `COUNT()`, `SUM()`, `AVG()` |
| Time/UUID | Generate temporal values | `now()`, `uuid()`, `toTimestamp()` |
| Cell Metadata | Query column metadata | `ttl()`, `writetime()` |
| Collection | Operate on collections | `map_keys()`, `collection_count()` |
| Data Masking | Protect sensitive data | `mask_default()`, `mask_inner()` |
| Vector | Vector similarity search | `similarity_cosine()` |

---

## Scalar Functions

### Type Conversion

```sql
-- Cast between types
SELECT CAST(age AS text) FROM users;
SELECT CAST('123' AS int) FROM users;

-- Convert blob to type
SELECT blobAsInt(blob_column) FROM data;
SELECT intAsBlob(123);

-- Type conversion functions
SELECT toDate(timestamp_column) FROM events;
SELECT toTimestamp(date_column) FROM events;
SELECT toUnixTimestamp(timestamp_column) FROM events;
```

### Token Function

```sql
-- Get token value for partition key
SELECT token(user_id), username FROM users;

-- Query by token range (full table scan)
SELECT * FROM users WHERE token(user_id) > -9223372036854775808;

-- Useful for parallel scanning
SELECT * FROM users
WHERE token(user_id) >= -9223372036854775808
  AND token(user_id) < 0;
```

### UUID Functions

```sql
-- Generate random UUID
INSERT INTO users (user_id, username) VALUES (uuid(), 'john');

-- Generate time-based UUID (timeuuid)
INSERT INTO events (event_id, event_time) VALUES (now(), 'click');

-- Extract timestamp from timeuuid
SELECT dateOf(event_id) FROM events;
SELECT unixTimestampOf(event_id) FROM events;
SELECT toTimestamp(event_id) FROM events;

-- Min/max timeuuid for time range queries
SELECT * FROM events
WHERE event_id > minTimeuuid('2024-01-01 00:00:00+0000')
  AND event_id < maxTimeuuid('2024-01-31 23:59:59+0000');
```

### Time Functions

```sql
-- Current timestamp
SELECT toTimestamp(now()) AS current_time FROM system.local;

-- Current date
SELECT currentDate() FROM system.local;

-- Current time
SELECT currentTime() FROM system.local;

-- Current timestamp in various formats
SELECT currentTimestamp() FROM system.local;
SELECT currentTimeUUID() FROM system.local;
```

### Blob Functions

```sql
-- Convert types to blob
SELECT bigintAsBlob(9223372036854775807);
SELECT booleanAsBlob(true);
SELECT doubleAsBlob(3.14159);
SELECT floatAsBlob(3.14);
SELECT intAsBlob(42);
SELECT textAsBlob('hello');
SELECT timestampAsBlob(toTimestamp(now()));
SELECT uuidAsBlob(uuid());
SELECT varintAsBlob(12345);

-- Convert blob to types
SELECT blobAsBigint(blob_column) FROM data;
SELECT blobAsBoolean(blob_column) FROM data;
SELECT blobAsDouble(blob_column) FROM data;
SELECT blobAsFloat(blob_column) FROM data;
SELECT blobAsInt(blob_column) FROM data;
SELECT blobAsText(blob_column) FROM data;
SELECT blobAsTimestamp(blob_column) FROM data;
SELECT blobAsUuid(blob_column) FROM data;
SELECT blobAsVarint(blob_column) FROM data;
```

### Text Functions

```sql
-- Convert blob to text
SELECT blobastext(blob_column) FROM data;

-- Convert text to blob
SELECT textasblob('hello');

-- Note: CQL has no built-in string manipulation functions
-- (no length, substring, concat, etc.) - use application layer
```

### Math Functions (Cassandra 4.0+)

```sql
-- Absolute value
SELECT abs(numeric_column) FROM data;

-- Exponential (e raised to power)
SELECT exp(numeric_column) FROM data;

-- Logarithm (natural log)
SELECT log(numeric_column) FROM data;
SELECT log10(numeric_column) FROM data;

-- Round to nearest integer (HALF_UP mode)
SELECT round(numeric_column) FROM data;
```

---

## Aggregate Functions

### COUNT

```sql
-- Count all rows
SELECT COUNT(*) FROM users;

-- Count non-null values in column
SELECT COUNT(email) FROM users;

-- Count with grouping
SELECT department, COUNT(*) as employee_count
FROM employees
GROUP BY department;
```

### SUM

```sql
-- Sum numeric column
SELECT SUM(amount) FROM orders WHERE user_id = ?;

-- Sum with grouping
SELECT user_id, SUM(amount) as total_spent
FROM orders
GROUP BY user_id;

-- Sum with time grouping
SELECT user_id, toDate(order_time) as day, SUM(amount)
FROM orders
WHERE user_id = ?
GROUP BY user_id, toDate(order_time);
```

### AVG

```sql
-- Average of column
SELECT AVG(price) FROM products;

-- Average with grouping
SELECT category, AVG(price) as avg_price
FROM products
GROUP BY category;
```

### MIN / MAX

```sql
-- Minimum value
SELECT MIN(price) FROM products;

-- Maximum value
SELECT MAX(created_at) FROM users;

-- Min/Max with grouping
SELECT user_id, MIN(order_time), MAX(order_time)
FROM orders
GROUP BY user_id;
```

### GROUP BY Usage

```sql
-- Group by partition key
SELECT user_id, COUNT(*) as message_count
FROM messages
GROUP BY user_id;

-- Group by clustering columns
SELECT user_id, toDate(sent_at) as day, COUNT(*)
FROM messages
WHERE user_id = ?
GROUP BY user_id, toDate(sent_at);

-- Multiple aggregates
SELECT user_id,
       COUNT(*) as orders,
       SUM(total) as revenue,
       AVG(total) as avg_order,
       MIN(order_time) as first_order,
       MAX(order_time) as last_order
FROM orders
GROUP BY user_id;
```

---

## Time and UUID Functions

### now() and uuid()

```sql
-- Generate timeuuid (time-based UUID v1)
INSERT INTO events (event_id, data) VALUES (now(), 'event');

-- Generate random UUID (v4)
INSERT INTO users (user_id, name) VALUES (uuid(), 'John');
```

### Timestamp Extraction

```sql
-- From timeuuid to timestamp
SELECT toTimestamp(event_id) FROM events;

-- From timeuuid to date
SELECT toDate(event_id) FROM events;

-- From timeuuid to Unix timestamp (milliseconds)
SELECT toUnixTimestamp(event_id) FROM events;

-- dateOf (deprecated, use toTimestamp)
SELECT dateOf(event_id) FROM events;

-- unixTimestampOf (deprecated, use toUnixTimestamp)
SELECT unixTimestampOf(event_id) FROM events;
```

### Time Range Queries

```sql
-- minTimeuuid / maxTimeuuid for time-based queries
SELECT * FROM events
WHERE user_id = ?
  AND event_id > minTimeuuid('2024-01-01 00:00:00+0000')
  AND event_id < maxTimeuuid('2024-01-31 23:59:59+0000');

-- Query events up to current time
SELECT * FROM events
WHERE user_id = ?
  AND event_id <= now();

-- Note: CQL has no timestamp arithmetic; calculate time bounds
-- in application code and pass as prepared statement parameters
```

### Current Time Functions

```sql
-- Current timestamp (microseconds)
SELECT currentTimestamp() FROM system.local;

-- Current date
SELECT currentDate() FROM system.local;

-- Current time (nanoseconds since midnight)
SELECT currentTime() FROM system.local;

-- Current timeuuid
SELECT currentTimeUUID() FROM system.local;
```

---

## Cell Metadata Functions

### TTL Function

```sql
-- Check remaining TTL (seconds)
SELECT TTL(email) FROM users WHERE user_id = ?;

-- TTL returns null for columns without TTL
SELECT username, TTL(username), email, TTL(email) FROM users;
```

### WRITETIME Function

```sql
-- Check write timestamp (microseconds since epoch)
SELECT WRITETIME(email) FROM users WHERE user_id = ?;

-- Compare write times
SELECT username, WRITETIME(username), email, WRITETIME(email) FROM users;
```

---

## Collection Functions

### Map Functions

```sql
-- Extract keys from map as a set
SELECT map_keys(preferences) FROM users WHERE user_id = ?;

-- Extract values from map as a list
SELECT map_values(preferences) FROM users WHERE user_id = ?;
```

### Collection Aggregates

```sql
-- Count elements in collection
SELECT collection_count(tags) FROM users WHERE user_id = ?;

-- Min/max element in set or list
SELECT collection_min(scores) FROM users WHERE user_id = ?;
SELECT collection_max(scores) FROM users WHERE user_id = ?;

-- Sum/average of numeric collection
SELECT collection_sum(scores) FROM users WHERE user_id = ?;
SELECT collection_avg(scores) FROM users WHERE user_id = ?;
```

---

## JSON Functions

### toJson

```sql
-- Convert column to JSON
SELECT user_id, toJson(preferences) FROM users;

-- Convert entire row to JSON
SELECT JSON * FROM users WHERE user_id = ?;

-- Convert specific columns
SELECT JSON user_id, username, email FROM users;
```

### fromJson

```sql
-- Insert from JSON
INSERT INTO users (user_id, username, preferences)
VALUES (fromJson('"550e8400-e29b-41d4-a716-446655440000"'),
        fromJson('"john"'),
        fromJson('{"theme": "dark", "lang": "en"}'));

-- Update with JSON
UPDATE users
SET preferences = fromJson('{"theme": "light"}')
WHERE user_id = ?;
```

### JSON Insert

```sql
-- Full row as JSON
INSERT INTO users JSON '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john",
    "email": "john@example.com",
    "preferences": {"theme": "dark"}
}';

-- With DEFAULT UNSET for missing columns
INSERT INTO users JSON '{"user_id": "...", "username": "john"}' DEFAULT UNSET;

-- With DEFAULT NULL for missing columns
INSERT INTO users JSON '{"user_id": "...", "username": "john"}' DEFAULT NULL;
```

---

## User-Defined Functions (UDF)

### Creating UDFs

```sql
-- Enable UDFs in cassandra.yaml first:
-- user_defined_functions_enabled: true

-- Create Java UDF
CREATE FUNCTION my_keyspace.double_value(input int)
    CALLED ON NULL INPUT
    RETURNS int
    LANGUAGE java
    AS 'return input * 2;';

-- Create UDF with null handling
CREATE FUNCTION my_keyspace.safe_double(input int)
    RETURNS NULL ON NULL INPUT
    RETURNS int
    LANGUAGE java
    AS 'return input * 2;';
```

### Using UDFs

```sql
-- Use in SELECT
SELECT user_id, double_value(score) FROM scores;

-- Use in INSERT/UPDATE
INSERT INTO scores (user_id, adjusted_score)
VALUES (?, double_value(?));
```

### Managing UDFs

```sql
-- List functions
SELECT * FROM system_schema.functions;

-- Drop function
DROP FUNCTION my_keyspace.double_value;

-- Replace function
CREATE OR REPLACE FUNCTION my_keyspace.double_value(input int)
    CALLED ON NULL INPUT
    RETURNS int
    LANGUAGE java
    AS 'return input * 3;';  -- Changed to triple
```

---

## User-Defined Aggregates (UDA)

### Creating UDAs

```sql
-- First create state function
CREATE FUNCTION my_keyspace.avgState(state tuple<int, bigint>, val int)
    CALLED ON NULL INPUT
    RETURNS tuple<int, bigint>
    LANGUAGE java
    AS 'if (val != null) {
        state.setInt(0, state.getInt(0) + 1);
        state.setLong(1, state.getLong(1) + val);
    }
    return state;';

-- Create final function
CREATE FUNCTION my_keyspace.avgFinal(state tuple<int, bigint>)
    CALLED ON NULL INPUT
    RETURNS double
    LANGUAGE java
    AS 'if (state.getInt(0) == 0) return null;
    return (double) state.getLong(1) / state.getInt(0);';

-- Create aggregate
CREATE AGGREGATE my_keyspace.custom_avg(int)
    SFUNC avgState
    STYPE tuple<int, bigint>
    FINALFUNC avgFinal
    INITCOND (0, 0);
```

### Using UDAs

```sql
-- Use like built-in aggregates
SELECT user_id, custom_avg(score) FROM scores GROUP BY user_id;
```

---

## Data Masking Functions (Cassandra 5.0+)

Data masking functions protect sensitive data by replacing values with masked versions.

```sql
-- Return null for any value
SELECT mask_null(email) FROM users;

-- Return type-appropriate default (asterisks for text, zero for numbers)
SELECT mask_default(email) FROM users;

-- Replace with specific value
SELECT mask_replace(email, '***@***.***') FROM users;

-- Mask inner characters, expose prefix/suffix
-- mask_inner(value, begin_unmasked, end_unmasked, [padding_char])
SELECT mask_inner(phone, 3, 4) FROM users;  -- '+1-***-**-5678'

-- Mask outer characters, expose middle
-- mask_outer(value, begin_masked, end_masked, [padding_char])
SELECT mask_outer(ssn, 3, 4) FROM users;  -- '***-45-****'

-- Return SHA-256 hash as blob
SELECT mask_hash(email) FROM users;
```

---

## Vector Similarity Functions (Cassandra 5.0+)

Vector similarity functions compare float vectors for similarity search operations.

```sql
-- Cosine similarity between vectors (range: -1 to 1)
SELECT similarity_cosine(embedding, ?) FROM documents;

-- Euclidean distance between vectors
SELECT similarity_euclidean(embedding, ?) FROM documents;

-- Dot product of vectors
SELECT similarity_dot_product(embedding, ?) FROM documents;
```

---

## Function Reference Table

### Scalar Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `token()` | partition key | bigint | Murmur3 token value |
| `uuid()` | none | uuid | Random UUID v4 |
| `now()` | none | timeuuid | Current time UUID |
| `to_date()` | timestamp/timeuuid | date | Extract date |
| `to_timestamp()` | date/timeuuid | timestamp | Convert to timestamp |
| `to_unix_timestamp()` | timestamp/timeuuid | bigint | Unix time (ms) |
| `min_timeuuid()` | timestamp | timeuuid | Min UUID for time |
| `max_timeuuid()` | timestamp | timeuuid | Max UUID for time |
| `ttl()` | column | int | Remaining TTL (s) |
| `writetime()` | column | bigint | Write timestamp (μs) |
| `cast()` | value AS type | varies | Type conversion |
| `to_json()` | value | text | Convert to JSON |
| `from_json()` | json text | varies | Parse JSON |

### Math Functions (4.0+)

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `abs()` | numeric | same | Absolute value |
| `exp()` | numeric | same | e raised to power |
| `log()` | numeric | same | Natural logarithm |
| `log10()` | numeric | same | Base-10 logarithm |
| `round()` | numeric | same | Round (HALF_UP) |

### Aggregate Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `count()` | * or column | bigint | Row/value count |
| `sum()` | numeric column | varies | Sum of values |
| `avg()` | numeric column | varies | Average value |
| `min()` | column | varies | Minimum value |
| `max()` | column | varies | Maximum value |

### Collection Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `map_keys()` | map | set | Extract map keys |
| `map_values()` | map | list | Extract map values |
| `collection_count()` | collection | int | Element count |
| `collection_min()` | set/list | element type | Minimum element |
| `collection_max()` | set/list | element type | Maximum element |
| `collection_sum()` | numeric set/list | numeric | Sum of elements |
| `collection_avg()` | numeric set/list | numeric | Average of elements |

### Data Masking Functions (5.0+)

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `mask_null()` | value | null | Returns null |
| `mask_default()` | value | same type | Type-appropriate mask |
| `mask_replace()` | value, replacement | same type | Replace with value |
| `mask_inner()` | value, begin, end, [pad] | same type | Mask inner chars |
| `mask_outer()` | value, begin, end, [pad] | same type | Mask outer chars |
| `mask_hash()` | value, [algorithm] | blob | SHA-256 hash |

### Vector Functions (5.0+)

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `similarity_cosine()` | vector, vector | float | Cosine similarity |
| `similarity_euclidean()` | vector, vector | float | Euclidean distance |
| `similarity_dot_product()` | vector, vector | float | Dot product |

---

## Next Steps

- **[Data Types](../data-types/index.md)** - Type reference
- **[DML Reference](../dml/index.md)** - SELECT, INSERT, UPDATE
- **[Indexing](../indexing/index.md)** - Secondary indexes
- **[Data Modeling](../../data-modeling/index.md)** - Query-first design