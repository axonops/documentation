# CQL Data Types

Choosing the right data type affects storage efficiency, query performance, and available operations. BIGINT vs INT might not matter for small datasets, but at scale the 4 bytes per row add up. TIMEUUID vs UUID determines whether time-range queries are possible. Frozen collections serialize as blobs; unfrozen ones allow partial updates.

CQL's type system covers the basics (integers, text, timestamps), identifiers (UUID, TIMEUUID for time-ordered unique IDs), collections (lists, sets, maps), and complex types (user-defined types, tuples). Cassandra 5.0 added VECTOR for embedding storage.

This reference covers each type, when to use it, and the trade-offs involved.

## Type Categories

| Category | Types | Use Case |
|----------|-------|----------|
| **Numeric** | int, bigint, smallint, tinyint, varint, float, double, decimal | Numbers and calculations |
| **Text** | text, varchar, ascii | String data |
| **Temporal** | timestamp, date, time, duration | Date and time |
| **Identifiers** | uuid, timeuuid | Unique identifiers |
| **Binary** | blob | Raw bytes |
| **Boolean** | boolean | True/false |
| **Network** | inet | IP addresses |
| **Collections** | list, set, map | Multiple values |
| **Complex** | tuple, UDT, frozen | Structured data |
| **Vector** | vector | ML embeddings (5.0+) |

---

## Numeric Types

### Integer Types

| Type | Size | Range | Example |
|------|------|-------|---------|
| `TINYINT` | 1 byte | -128 to 127 | `127` |
| `SMALLINT` | 2 bytes | -32,768 to 32,767 | `32767` |
| `INT` | 4 bytes | -2³¹ to 2³¹-1 | `2147483647` |
| `BIGINT` | 8 bytes | -2⁶³ to 2⁶³-1 | `9223372036854775807` |
| `VARINT` | Variable | Arbitrary precision | `123456789012345678901234567890` |

```sql
CREATE TABLE metrics (
    id UUID PRIMARY KEY,
    count_small TINYINT,
    count_medium INT,
    count_large BIGINT,
    count_huge VARINT
);

INSERT INTO metrics (id, count_small, count_medium, count_large, count_huge)
VALUES (uuid(), 100, 1000000, 9223372036854775807, 123456789012345678901234567890);
```

### Floating Point Types

| Type | Size | Precision | Example |
|------|------|-----------|---------|
| `FLOAT` | 4 bytes | ~7 digits | `3.14159` |
| `DOUBLE` | 8 bytes | ~15 digits | `3.141592653589793` |
| `DECIMAL` | Variable | Arbitrary | `123.456789012345678901234567890` |

```sql
CREATE TABLE measurements (
    id UUID PRIMARY KEY,
    temperature FLOAT,
    precise_value DOUBLE,
    currency DECIMAL
);

INSERT INTO measurements (id, temperature, precise_value, currency)
VALUES (uuid(), 23.5, 3.141592653589793, 1234567.89);
```

**Best Practices**:
- Use `INT`/`BIGINT` for counters and IDs
- Use `DECIMAL` for financial data (exact precision)
- Use `DOUBLE` for scientific calculations
- Avoid `FLOAT` unless space is critical

---

## Text Types

| Type | Description | Max Size |
|------|-------------|----------|
| `TEXT` | UTF-8 encoded string | 2GB |
| `VARCHAR` | Alias for TEXT | 2GB |
| `ASCII` | US-ASCII string | 2GB |

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    username TEXT,
    bio TEXT,
    legacy_code ASCII
);

-- Text supports Unicode
INSERT INTO users (user_id, username, bio)
VALUES (uuid(), '日本語ユーザー', 'こんにちは世界 🌍');
```

**Best Practices**:
- Use `TEXT` for all string data (UTF-8 support)
- Only use `ASCII` for legacy compatibility
- Don't store large text in frequently queried columns

---

## Temporal Types

### TIMESTAMP

Milliseconds since Unix epoch (January 1, 1970 UTC).

```sql
CREATE TABLE events (
    event_id UUID PRIMARY KEY,
    event_time TIMESTAMP
);

-- Various timestamp formats
INSERT INTO events (event_id, event_time) VALUES
    (uuid(), '2024-01-15 10:30:00'),
    (uuid(), '2024-01-15 10:30:00+0000'),
    (uuid(), '2024-01-15T10:30:00Z'),
    (uuid(), 1705315800000);  -- Milliseconds

-- Using functions
INSERT INTO events (event_id, event_time)
VALUES (uuid(), toTimestamp(now()));
```

### DATE

Calendar date without time component.

```sql
CREATE TABLE daily_stats (
    stat_date DATE PRIMARY KEY,
    count INT
);

INSERT INTO daily_stats (stat_date, count)
VALUES ('2024-01-15', 100);

-- Using function
INSERT INTO daily_stats (stat_date, count)
VALUES (toDate(now()), 200);
```

### TIME

Time of day in nanoseconds since midnight.

```sql
CREATE TABLE schedules (
    id UUID PRIMARY KEY,
    start_time TIME,
    end_time TIME
);

INSERT INTO schedules (id, start_time, end_time)
VALUES (uuid(), '09:00:00', '17:30:00.123456789');
```

### DURATION

A period of time (months, days, nanoseconds).

```sql
CREATE TABLE subscriptions (
    user_id UUID PRIMARY KEY,
    duration DURATION
);

-- Various formats
INSERT INTO subscriptions (user_id, duration) VALUES
    (uuid(), '1y2mo'),           -- 1 year, 2 months
    (uuid(), '3w4d'),            -- 3 weeks, 4 days
    (uuid(), '12h30m'),          -- 12 hours, 30 minutes
    (uuid(), '89h4m48s');        -- 89 hours, 4 minutes, 48 seconds

-- ISO 8601 format
INSERT INTO subscriptions (user_id, duration)
VALUES (uuid(), 'P1Y2M3DT4H5M6S');  -- 1 year, 2 months, 3 days, 4 hours, 5 minutes, 6 seconds
```

**Note**: DURATION cannot be used in primary keys.

---

## Identifier Types

### UUID

128-bit universally unique identifier.

```sql
CREATE TABLE items (
    item_id UUID PRIMARY KEY,
    name TEXT
);

-- Generate random UUID
INSERT INTO items (item_id, name)
VALUES (uuid(), 'Widget');

-- Use specific UUID
INSERT INTO items (item_id, name)
VALUES (550e8400-e29b-41d4-a716-446655440000, 'Gadget');
```

### TIMEUUID

Time-based UUID (version 1) that includes timestamp.

```sql
CREATE TABLE events (
    partition_id TEXT,
    event_id TIMEUUID,
    data TEXT,
    PRIMARY KEY ((partition_id), event_id)
) WITH CLUSTERING ORDER BY (event_id DESC);

-- Generate time-based UUID
INSERT INTO events (partition_id, event_id, data)
VALUES ('partition1', now(), 'event data');

-- Extract timestamp from timeuuid
SELECT dateOf(event_id), unixTimestampOf(event_id), data FROM events;

-- Query by time range using timeuuid
SELECT * FROM events
WHERE partition_id = 'partition1'
  AND event_id >= minTimeuuid('2024-01-01 00:00:00')
  AND event_id < maxTimeuuid('2024-01-02 00:00:00');
```

**When to use**:
- `UUID`: Random unique identifiers
- `TIMEUUID`: When time-ordering and uniqueness are needed

---

## Binary Type

### BLOB

Binary Large Object - arbitrary bytes.

```sql
CREATE TABLE files (
    file_id UUID PRIMARY KEY,
    file_name TEXT,
    content BLOB
);

-- Insert hex-encoded binary
INSERT INTO files (file_id, file_name, content)
VALUES (uuid(), 'test.bin', 0x48656c6c6f20576f726c64);

-- Insert using textAsBlob
INSERT INTO files (file_id, file_name, content)
VALUES (uuid(), 'hello.txt', textAsBlob('Hello World'));
```

**Functions**:
- `textAsBlob(text)` - Convert text to blob
- `blobAsText(blob)` - Convert blob to text
- `intAsBlob(int)` / `blobAsInt(blob)` - Integer conversions

---

## Boolean Type

```sql
CREATE TABLE settings (
    user_id UUID PRIMARY KEY,
    notifications_enabled BOOLEAN,
    dark_mode BOOLEAN
);

INSERT INTO settings (user_id, notifications_enabled, dark_mode)
VALUES (uuid(), true, false);
```

---

## Network Type

### INET

IPv4 or IPv6 address.

```sql
CREATE TABLE access_logs (
    log_id TIMEUUID PRIMARY KEY,
    client_ip INET,
    request TEXT
);

INSERT INTO access_logs (log_id, client_ip, request) VALUES
    (now(), '192.168.1.100', 'GET /api/users'),
    (now(), '2001:0db8:85a3:0000:0000:8a2e:0370:7334', 'POST /api/data');
```

---

## Collection Types

### LIST

Ordered collection allowing duplicates.

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    phone_numbers LIST<TEXT>,
    tags LIST<TEXT>
);

-- Insert list
INSERT INTO users (user_id, phone_numbers, tags)
VALUES (uuid(), ['+1-555-0100', '+1-555-0101'], ['premium', 'verified']);

-- Append to list
UPDATE users SET phone_numbers = phone_numbers + ['+1-555-0102']
WHERE user_id = ?;

-- Prepend to list
UPDATE users SET tags = ['vip'] + tags
WHERE user_id = ?;

-- Remove from list
UPDATE users SET tags = tags - ['verified']
WHERE user_id = ?;

-- Update by index
UPDATE users SET phone_numbers[0] = '+1-555-9999'
WHERE user_id = ?;
```

### SET

Unordered collection of unique elements.

```sql
CREATE TABLE articles (
    article_id UUID PRIMARY KEY,
    categories SET<TEXT>
);

-- Insert set
INSERT INTO articles (article_id, categories)
VALUES (uuid(), {'technology', 'programming', 'database'});

-- Add elements
UPDATE articles SET categories = categories + {'nosql', 'distributed'}
WHERE article_id = ?;

-- Remove elements
UPDATE articles SET categories = categories - {'programming'}
WHERE article_id = ?;
```

### MAP

Key-value pairs.

```sql
CREATE TABLE user_preferences (
    user_id UUID PRIMARY KEY,
    preferences MAP<TEXT, TEXT>,
    scores MAP<TEXT, INT>
);

-- Insert map
INSERT INTO user_preferences (user_id, preferences, scores)
VALUES (uuid(),
    {'theme': 'dark', 'language': 'en', 'timezone': 'UTC'},
    {'level': 5, 'points': 1000});

-- Update specific key
UPDATE user_preferences SET preferences['theme'] = 'light'
WHERE user_id = ?;

-- Add new keys
UPDATE user_preferences SET preferences = preferences + {'notifications': 'enabled'}
WHERE user_id = ?;

-- Remove keys
DELETE preferences['timezone'] FROM user_preferences
WHERE user_id = ?;
```

**Collection Limitations**:
- Max 64KB per element
- Max 2 billion elements
- Cannot be part of primary key (unless frozen)
- Overwrites on concurrent updates (last write wins)

---

## Tuple Type

Fixed-length ordered collection of typed elements.

```sql
CREATE TABLE locations (
    location_id UUID PRIMARY KEY,
    coordinates TUPLE<DOUBLE, DOUBLE>,    -- (latitude, longitude)
    address TUPLE<TEXT, TEXT, TEXT, TEXT>  -- (street, city, state, zip)
);

INSERT INTO locations (location_id, coordinates, address)
VALUES (uuid(),
    (37.7749, -122.4194),
    ('123 Main St', 'San Francisco', 'CA', '94102'));

-- Access tuple elements (0-indexed)
SELECT coordinates, address FROM locations;
```

---

## User-Defined Types (UDT)

Custom composite types.

```sql
-- Create UDT
CREATE TYPE address (
    street TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    country TEXT
);

CREATE TYPE phone (
    country_code TEXT,
    number TEXT,
    type TEXT
);

-- Use UDT in table
CREATE TABLE customers (
    customer_id UUID PRIMARY KEY,
    name TEXT,
    billing_address FROZEN<address>,
    shipping_address FROZEN<address>,
    phones LIST<FROZEN<phone>>
);

-- Insert with UDT
INSERT INTO customers (customer_id, name, billing_address, phones)
VALUES (uuid(), 'John Doe',
    {street: '123 Main St', city: 'NYC', state: 'NY', zip_code: '10001', country: 'USA'},
    [{country_code: '+1', number: '555-0100', type: 'mobile'}]);

-- Query UDT fields
SELECT name, billing_address.city, billing_address.state FROM customers;
```

---

## Frozen Type

Makes collections and UDTs immutable (required for use in primary keys).

```sql
-- Frozen collection in primary key
CREATE TABLE user_groups (
    group_members FROZEN<SET<UUID>>,
    group_name TEXT,
    PRIMARY KEY (group_members)
);

-- Frozen UDT
CREATE TABLE orders (
    order_id UUID PRIMARY KEY,
    shipping_address FROZEN<address>  -- Entire UDT is replaced on update
);
```

**Frozen vs Non-Frozen**:
- Frozen: Entire value serialized together, atomic updates only
- Non-Frozen: Individual elements can be updated

---

## Vector Type (Cassandra 5.0+)

Fixed-size array of floats for ML embeddings.

```sql
CREATE TABLE embeddings (
    id UUID PRIMARY KEY,
    content TEXT,
    embedding VECTOR<FLOAT, 384>  -- 384-dimensional vector
);

-- Insert vector
INSERT INTO embeddings (id, content, embedding)
VALUES (uuid(), 'Sample text', [0.1, 0.2, 0.3, ...]);  -- 384 values

-- Create SAI index for vector search
CREATE INDEX ON embeddings (embedding) USING 'sai';

-- Approximate nearest neighbor search
SELECT * FROM embeddings
ORDER BY embedding ANN OF [0.1, 0.2, 0.3, ...]
LIMIT 10;
```

---

## Type Conversion Functions

| Function | Description |
|----------|-------------|
| `toTimestamp(timeuuid)` | TIMEUUID → TIMESTAMP |
| `toDate(timestamp)` | TIMESTAMP → DATE |
| `toUnixTimestamp(timeuuid)` | TIMEUUID → BIGINT |
| `dateOf(timeuuid)` | TIMEUUID → TIMESTAMP |
| `textAsBlob(text)` | TEXT → BLOB |
| `blobAsText(blob)` | BLOB → TEXT |
| `typeAsBlob(value)` | Any type → BLOB |

---

## Next Steps

- **[Native Types Detail](native-types.md)** - In-depth native type reference
- **[Collections Detail](collections.md)** - Collection operations
- **[User-Defined Types](udts.md)** - Creating and using UDTs
- **[DDL Commands](../ddl/index.md)** - Schema management
