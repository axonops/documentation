# DML Commands Reference

CQL's data manipulation commands look like SQL but behave differently in important ways. INSERT and UPDATE are the same operation—both upsert, meaning they create the row if it does not exist or update it if it does. DELETE does not remove data immediately; it writes a tombstone that marks the data as deleted, with actual removal happening later during compaction.

The biggest difference is SELECT. Without a partition key, Cassandra does not know which node has the data. Add `ALLOW FILTERING` and it will scan the whole cluster—but that is almost never appropriate in production. Efficient queries always include the partition key.

This reference covers each DML command, how it really works, and the patterns that work well at scale.

## Quick Reference

| Command | Purpose |
|---------|---------|
| `SELECT` | Query data |
| `INSERT` | Add new data |
| `UPDATE` | Modify existing data |
| `DELETE` | Remove data |
| `BATCH` | Group multiple operations |

---

## SELECT

### Basic Syntax

```sql
SELECT select_expression
FROM table_name
[WHERE clause]
[GROUP BY clause]
[ORDER BY clause]
[LIMIT n]
[ALLOW FILTERING];
```

### Select All Columns

```sql
SELECT * FROM users;
SELECT * FROM users LIMIT 10;
```

### Select Specific Columns

```sql
SELECT username, email FROM users;
SELECT user_id, username, email, created_at FROM users;
```

### Select with Functions

```sql
-- Count
SELECT COUNT(*) FROM users;

-- Other aggregates
SELECT COUNT(*), MIN(created_at), MAX(created_at) FROM users;

-- Token function
SELECT token(user_id), username FROM users;

-- TTL and WriteTime
SELECT TTL(email), WRITETIME(email) FROM users WHERE user_id = ?;
```

### WHERE Clause

```sql
-- By partition key (required for efficiency)
SELECT * FROM users WHERE user_id = 550e8400-e29b-41d4-a716-446655440000;

-- By partition key with IN
SELECT * FROM users WHERE user_id IN (?, ?, ?);

-- With clustering columns
SELECT * FROM messages
WHERE user_id = ?
  AND message_time >= '2024-01-01'
  AND message_time < '2024-02-01';

-- With secondary index
SELECT * FROM users WHERE email = 'john@example.com';
```

### Operators

| Operator | Usage | Example |
|----------|-------|---------|
| `=` | Equality | `WHERE user_id = ?` |
| `<`, `>`, `<=`, `>=` | Comparison | `WHERE age >= 18` |
| `IN` | Multiple values | `WHERE user_id IN (?, ?)` |
| `CONTAINS` | Collection contains | `WHERE tags CONTAINS 'important'` |
| `CONTAINS KEY` | Map contains key | `WHERE prefs CONTAINS KEY 'theme'` |

### ORDER BY

```sql
-- Must match or reverse clustering order
SELECT * FROM messages
WHERE user_id = ?
ORDER BY message_time DESC;

-- Multiple clustering columns
SELECT * FROM events
WHERE partition_key = ?
ORDER BY event_time DESC, event_id ASC;
```

### LIMIT and PER PARTITION LIMIT

```sql
-- Limit total results
SELECT * FROM users LIMIT 100;

-- Limit per partition
SELECT * FROM messages
PER PARTITION LIMIT 10
LIMIT 1000;
```

### GROUP BY

```sql
-- Group by partition key
SELECT user_id, COUNT(*) as message_count
FROM messages
GROUP BY user_id;

-- Group by clustering columns
SELECT user_id, toDate(message_time) as day, COUNT(*)
FROM messages
WHERE user_id = ?
GROUP BY user_id, toDate(message_time);
```

### ALLOW FILTERING

```sql
-- WARNING: Full table scan - avoid in production!
SELECT * FROM users WHERE age > 30 ALLOW FILTERING;
```

**When ALLOW FILTERING is needed**:
- Filtering on non-indexed, non-primary key columns
- Range query on partition key
- Complex conditions

### JSON Output

```sql
-- All columns as JSON
SELECT JSON * FROM users WHERE user_id = ?;

-- Specific columns
SELECT JSON username, email FROM users WHERE user_id = ?;

-- toJson function
SELECT user_id, toJson(preferences) FROM users;
```

---

## INSERT

### Basic Insert

```sql
INSERT INTO users (user_id, username, email, created_at)
VALUES (uuid(), 'john_doe', 'john@example.com', toTimestamp(now()));
```

### Insert with TTL

```sql
-- Data expires after 86400 seconds (24 hours)
INSERT INTO users (user_id, username, email)
VALUES (uuid(), 'temp_user', 'temp@example.com')
USING TTL 86400;
```

### Insert with Timestamp

```sql
-- Set write timestamp explicitly
INSERT INTO users (user_id, username, email)
VALUES (uuid(), 'john_doe', 'john@example.com')
USING TIMESTAMP 1705315800000000;  -- Microseconds
```

### Insert with TTL and Timestamp

```sql
INSERT INTO users (user_id, username, email)
VALUES (uuid(), 'temp_user', 'temp@example.com')
USING TTL 86400 AND TIMESTAMP 1705315800000000;
```

### Conditional Insert (IF NOT EXISTS)

```sql
-- Lightweight transaction - only insert if row does not exist
INSERT INTO users (user_id, username, email)
VALUES (uuid(), 'unique_user', 'unique@example.com')
IF NOT EXISTS;

-- Returns applied=true if inserted, applied=false if already exists
```

### Insert JSON

```sql
INSERT INTO users JSON '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "json_user",
    "email": "json@example.com"
}';

-- With DEFAULT for missing columns
INSERT INTO users JSON '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "partial_user"
}' DEFAULT UNSET;
```

### Insert into Collections

```sql
-- List
INSERT INTO users (user_id, phone_numbers)
VALUES (uuid(), ['+1-555-0100', '+1-555-0101']);

-- Set
INSERT INTO users (user_id, tags)
VALUES (uuid(), {'premium', 'verified'});

-- Map
INSERT INTO users (user_id, preferences)
VALUES (uuid(), {'theme': 'dark', 'language': 'en'});
```

---

## UPDATE

### Basic Update

```sql
UPDATE users
SET email = 'new@example.com'
WHERE user_id = 550e8400-e29b-41d4-a716-446655440000;
```

### Update Multiple Columns

```sql
UPDATE users
SET email = 'new@example.com',
    username = 'new_username',
    updated_at = toTimestamp(now())
WHERE user_id = ?;
```

### Update with TTL

```sql
-- Set TTL on specific columns
UPDATE users USING TTL 3600
SET temp_token = 'abc123'
WHERE user_id = ?;
```

### Update with Timestamp

```sql
UPDATE users USING TIMESTAMP 1705315800000000
SET email = 'new@example.com'
WHERE user_id = ?;
```

### Conditional Update (IF)

```sql
-- Only update if condition is met
UPDATE users
SET email = 'new@example.com'
WHERE user_id = ?
IF email = 'old@example.com';

-- Check if exists
UPDATE users
SET status = 'active'
WHERE user_id = ?
IF EXISTS;
```

### Update Collections

#### Lists

```sql
-- Replace entire list
UPDATE users SET phone_numbers = ['+1-555-9999']
WHERE user_id = ?;

-- Append
UPDATE users SET phone_numbers = phone_numbers + ['+1-555-0102']
WHERE user_id = ?;

-- Prepend
UPDATE users SET phone_numbers = ['+1-555-0000'] + phone_numbers
WHERE user_id = ?;

-- Remove by value
UPDATE users SET phone_numbers = phone_numbers - ['+1-555-0100']
WHERE user_id = ?;

-- Update by index
UPDATE users SET phone_numbers[0] = '+1-555-1111'
WHERE user_id = ?;
```

#### Sets

```sql
-- Replace entire set
UPDATE users SET tags = {'new_tag'}
WHERE user_id = ?;

-- Add elements
UPDATE users SET tags = tags + {'vip', 'verified'}
WHERE user_id = ?;

-- Remove elements
UPDATE users SET tags = tags - {'unverified'}
WHERE user_id = ?;
```

#### Maps

```sql
-- Replace entire map
UPDATE users SET preferences = {'theme': 'light'}
WHERE user_id = ?;

-- Update/add specific keys
UPDATE users SET preferences['theme'] = 'dark'
WHERE user_id = ?;

-- Add multiple keys
UPDATE users SET preferences = preferences + {'lang': 'en', 'tz': 'UTC'}
WHERE user_id = ?;

-- Remove key
DELETE preferences['old_key'] FROM users
WHERE user_id = ?;
```

### Counter Updates

```sql
-- Counters can only be incremented/decremented
UPDATE page_views SET view_count = view_count + 1
WHERE page_id = ?;

UPDATE user_stats SET followers = followers - 1
WHERE user_id = ?;
```

---

## DELETE

### Delete Entire Row

```sql
DELETE FROM users WHERE user_id = ?;
```

### Delete Specific Columns

```sql
DELETE email, phone FROM users WHERE user_id = ?;
```

### Delete from Collections

```sql
-- Delete list element by index
DELETE phone_numbers[0] FROM users WHERE user_id = ?;

-- Delete map entry
DELETE preferences['old_key'] FROM users WHERE user_id = ?;
```

### Delete with Timestamp

```sql
DELETE FROM users USING TIMESTAMP 1705315800000000
WHERE user_id = ?;
```

### Conditional Delete

```sql
DELETE FROM users WHERE user_id = ?
IF EXISTS;

DELETE FROM users WHERE user_id = ?
IF status = 'inactive';
```

### Delete Range (Clustering Columns)

```sql
-- Delete range of rows within partition
DELETE FROM messages
WHERE user_id = ?
  AND message_time >= '2024-01-01'
  AND message_time < '2024-02-01';
```

---

## BATCH

### Logged Batch (Default)

```sql
BEGIN BATCH
    INSERT INTO users (user_id, username) VALUES (?, 'user1');
    INSERT INTO users (user_id, username) VALUES (?, 'user2');
    UPDATE user_stats SET count = count + 2 WHERE stat_id = 'total_users';
APPLY BATCH;
```

### Unlogged Batch

```sql
-- Faster but no atomicity guarantee across partitions
BEGIN UNLOGGED BATCH
    INSERT INTO logs (log_id, message) VALUES (uuid(), 'log1');
    INSERT INTO logs (log_id, message) VALUES (uuid(), 'log2');
APPLY BATCH;
```

### Counter Batch

```sql
BEGIN COUNTER BATCH
    UPDATE page_stats SET views = views + 1 WHERE page_id = 'home';
    UPDATE page_stats SET views = views + 1 WHERE page_id = 'about';
APPLY BATCH;
```

### Batch with Timestamp

```sql
BEGIN BATCH USING TIMESTAMP 1705315800000000
    INSERT INTO users (user_id, username) VALUES (?, 'user1');
    INSERT INTO users (user_id, username) VALUES (?, 'user2');
APPLY BATCH;
```

### Batch Best Practices

**Do**:
- Use batches for operations on the **same partition**
- Keep batches small (< 100 operations)
- Use unlogged batches when atomicity is not required

**Don't**:
- Use batches as a performance optimization (they're not!)
- Create large batches (causes coordinator overload)
- Batch operations across many partitions

---

## Lightweight Transactions (LWT)

### Compare-and-Set Operations

```sql
-- Insert if not exists
INSERT INTO users (user_id, username, email)
VALUES (?, 'unique_user', 'unique@example.com')
IF NOT EXISTS;

-- Update if condition met
UPDATE users
SET email = 'new@example.com'
WHERE user_id = ?
IF email = 'old@example.com';

-- Delete if exists
DELETE FROM users WHERE user_id = ?
IF EXISTS;

-- Multiple conditions
UPDATE inventory
SET quantity = quantity - 1
WHERE product_id = ?
IF quantity > 0;
```

### LWT Response

```sql
-- Returns [applied] column
[applied]
---------
     True

-- If not applied, returns current values
[applied] | email
----------+------------------
    False | current@example.com
```

### LWT Performance Considerations

- 4x latency compared to regular operations
- Uses Paxos consensus protocol
- Should be used sparingly
- Not suitable for high-throughput scenarios

---

## Using TTL and Timestamp

### Check TTL

```sql
SELECT TTL(column_name) FROM table WHERE pk = ?;
```

### Check WriteTime

```sql
SELECT WRITETIME(column_name) FROM table WHERE pk = ?;
```

### Update TTL

```sql
-- Reset TTL on column
UPDATE users USING TTL 86400
SET email = email
WHERE user_id = ?;
```

---

## Next Steps

- **[SELECT Detail](select.md)** - Advanced queries
- **[INSERT Detail](insert.md)** - Insert patterns
- **[Batch Operations](batch.md)** - Batch best practices
- **[LWT Detail](lwt.md)** - Lightweight transactions
- **[Data Modeling](../../data-modeling/index.md)** - Query-driven design
