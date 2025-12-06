# CQL Functions Reference

CQL includes built-in functions for common operations: generating UUIDs, working with timestamps, computing aggregates. The most useful ones—`now()` for time-based UUIDs, `token()` for understanding data distribution, `toTimestamp()` for converting between time formats—show up constantly in production schemas.

Aggregates deserve a warning: `SELECT COUNT(*) FROM users` looks innocent, but without a partition key it scans the entire cluster. That is fine for a thousand rows; it will timeout with a billion. Aggregates work efficiently when scoped to a partition.

This reference covers scalar functions, aggregates, and user-defined functions (available since Cassandra 4.0).

## Function Categories

| Category | Purpose | Examples |
|----------|---------|----------|
| Scalar | Transform single values | `toDate()`, `token()`, `cast()` |
| Aggregate | Compute across rows | `COUNT()`, `SUM()`, `AVG()` |
| Time/UUID | Generate temporal values | `now()`, `uuid()`, `toTimestamp()` |
| Collection | Work with collections | `ttl()`, `writetime()` |

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
-- Convert ASCII code to character
SELECT blobastext(intasblob(65)); -- 'A'

-- Text length
SELECT length(text_column) FROM data;

-- Substring (Cassandra 4.0+)
-- Note: No built-in substring; use application layer
```

### Math Functions (Cassandra 4.0+)

```sql
-- Absolute value
SELECT abs(numeric_column) FROM data;

-- Exponential
SELECT exp(numeric_column) FROM data;

-- Logarithm
SELECT log(numeric_column) FROM data;
SELECT log10(numeric_column) FROM data;

-- Power
SELECT power(base, exponent) FROM data;

-- Round
SELECT round(numeric_column) FROM data;
SELECT round(numeric_column, 2) FROM data;  -- 2 decimal places

-- Floor/Ceiling
SELECT floor(numeric_column) FROM data;
SELECT ceil(numeric_column) FROM data;

-- Square root
SELECT sqrt(numeric_column) FROM data;
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

-- Current time boundaries
SELECT * FROM events
WHERE user_id = ?
  AND event_id > minTimeuuid(toTimestamp(now()) - 1h)
  AND event_id <= now();
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

## Collection Functions

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

### Collection Element Access

```sql
-- List element by index
SELECT phone_numbers[0] FROM users WHERE user_id = ?;

-- Map element by key
SELECT preferences['theme'] FROM users WHERE user_id = ?;

-- Frozen collection functions
SELECT * FROM users WHERE tags CONTAINS 'premium';
SELECT * FROM users WHERE preferences CONTAINS KEY 'theme';
SELECT * FROM users WHERE preferences CONTAINS 'dark';
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
-- enable_user_defined_functions: true
-- enable_scripted_user_defined_functions: true

-- Create Java UDF
CREATE FUNCTION my_keyspace.double_value(input int)
    CALLED ON NULL INPUT
    RETURNS int
    LANGUAGE java
    AS 'return input * 2;';

-- Create JavaScript UDF
CREATE FUNCTION my_keyspace.concat_strings(a text, b text)
    RETURNS NULL ON NULL INPUT
    RETURNS text
    LANGUAGE javascript
    AS 'a + " " + b';
```

### Using UDFs

```sql
-- Use in SELECT
SELECT user_id, double_value(score) FROM scores;

-- Use in WHERE (if deterministic)
SELECT * FROM scores WHERE double_value(score) > 100;
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

## Function Reference Table

### Scalar Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `token()` | partition key | bigint | Murmur3 token value |
| `uuid()` | none | uuid | Random UUID v4 |
| `now()` | none | timeuuid | Current time UUID |
| `toDate()` | timestamp/timeuuid | date | Extract date |
| `toTimestamp()` | date/timeuuid | timestamp | Convert to timestamp |
| `toUnixTimestamp()` | timestamp/timeuuid | bigint | Unix time (ms) |
| `minTimeuuid()` | timestamp | timeuuid | Min UUID for time |
| `maxTimeuuid()` | timestamp | timeuuid | Max UUID for time |
| `ttl()` | column | int | Remaining TTL (s) |
| `writetime()` | column | bigint | Write timestamp (μs) |
| `cast()` | value AS type | varies | Type conversion |
| `toJson()` | value | text | Convert to JSON |
| `fromJson()` | json text | varies | Parse JSON |

### Aggregate Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `COUNT()` | * or column | bigint | Row/value count |
| `SUM()` | numeric column | varies | Sum of values |
| `AVG()` | numeric column | varies | Average value |
| `MIN()` | column | varies | Minimum value |
| `MAX()` | column | varies | Maximum value |

---

## Next Steps

- **[Data Types](../data-types/index.md)** - Type reference
- **[DML Reference](../dml/index.md)** - SELECT, INSERT, UPDATE
- **[Indexing](../indexing/index.md)** - Secondary indexes
- **[Data Modeling](../../data-modeling/index.md)** - Query-first design
