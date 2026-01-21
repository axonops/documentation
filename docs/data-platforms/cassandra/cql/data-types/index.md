---
title: "Cassandra CQL Data Types"
description: "Cassandra CQL data types reference including text, int, UUID, timestamp, collections, and user-defined types."
meta:
  - name: keywords
    content: "CQL data types, Cassandra types, UUID, timestamp, collections, UDT"
search:
  boost: 3
---

# CQL Data Types

Choosing the right data type affects storage efficiency, query performance, and available operations. BIGINT vs INT might not matter for small datasets, but at scale the 4 bytes per row add up. TIMEUUID vs UUID determines whether time-range queries are possible. Frozen collections serialize as blobs; unfrozen ones allow partial updates.

CQL's type system covers the basics (integers, text, timestamps), identifiers (UUID, TIMEUUID for time-ordered unique IDs), collections (lists, sets, maps), and complex types (user-defined types, tuples). Cassandra 5.0 added VECTOR for embedding storage.

This reference covers each type, when to use it, and the trade-offs involved.

---

## Behavioral Guarantees

### What Data Types Guarantee

- Values are validated against type constraints at write time
- Type conversion failures are reported immediately (no silent truncation)
- Integer overflow causes write rejection (not wrap-around)
- TEXT stores UTF-8 encoded data; invalid UTF-8 is rejected
- TIMEUUID values contain embedded timestamps extractable via `toTimestamp()`
- FROZEN collections are serialized atomically and compared byte-for-byte

### What Data Types Do NOT Guarantee

!!! warning "Undefined Behavior"
    The following behaviors are undefined and must not be relied upon:

    - **Floating point precision**: FLOAT and DOUBLE are approximate; exact equality comparisons may fail
    - **Collection ordering across versions**: Internal sort order for sets and map keys may vary between Cassandra versions
    - **VARINT/DECIMAL performance**: Arbitrary precision types have higher computation and storage costs
    - **Empty vs null**: Empty string ('') and empty collections are distinct from null, but behavior may vary
    - **Large value handling**: Very large text or blob values (approaching 2GB) may cause memory pressure

### Type Comparison Contract

| Type | Comparison Semantics |
|------|---------------------|
| Numeric (int, bigint, etc.) | Numerical ordering |
| TEXT, VARCHAR | UTF-8 byte ordering |
| ASCII | ASCII byte ordering |
| TIMESTAMP | Chronological ordering (milliseconds since epoch) |
| TIMEUUID | Chronological ordering (time component) |
| UUID | Lexicographical ordering |
| BLOB | Byte ordering |
| BOOLEAN | false < true |
| Collections (frozen) | Element-by-element comparison |

### Null Handling Contract

| Operation | Behavior |
|-----------|----------|
| INSERT with null | Creates tombstone for column |
| NULL in primary key | Rejected (invalid) |
| NULL in clustering column | Rejected (invalid) |
| NULL in collection element | Behavior varies by collection type |
| Comparison with NULL | NULL is not equal to NULL |

### Storage Size Contract

| Type | Fixed/Variable | Size |
|------|----------------|------|
| TINYINT | Fixed | 1 byte |
| SMALLINT | Fixed | 2 bytes |
| INT | Fixed | 4 bytes |
| BIGINT | Fixed | 8 bytes |
| FLOAT | Fixed | 4 bytes |
| DOUBLE | Fixed | 8 bytes |
| UUID/TIMEUUID | Fixed | 16 bytes |
| TEXT, BLOB | Variable | Length prefix + data |
| VARINT, DECIMAL | Variable | Value-dependent |
| Collections | Variable | Element count + elements |

### Version-Specific Behavior

| Version | Behavior |
|---------|----------|
| 2.0+ | Collections (list, set, map) |
| 2.1+ | User-defined types (UDTs), tuple type |
| 2.2+ | TINYINT, SMALLINT, DATE, TIME types |
| 3.0+ | Non-frozen UDTs and collections |
| 4.0+ | DURATION type |
| 5.0+ | VECTOR type for ML embeddings (CEP-30) |

---

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

Collections store multiple values in a single column. Cassandra provides three collection types: LIST, SET, and MAP. Collections are designed for small, bounded datasets that are typically read together with the row.

### Collection Architecture

Collections are stored as a set of cells within the row, not as a separate data structure:

```
Row Storage:
┌──────────────┬─────────────────────────────────────────────────┐
│ Primary Key  │ Cells                                           │
├──────────────┼─────────────────────────────────────────────────┤
│ user_id=123  │ name="Alice" │ tags[0]="a" │ tags[1]="b" │ ... │
└──────────────┴─────────────────────────────────────────────────┘
```

Each collection element is stored as an individual cell with its own timestamp. This enables:

- Partial updates without reading the entire collection
- Per-element TTL
- Last-write-wins conflict resolution at element level

!!! warning "Collections Are Not Tables"
    Collections are optimized for small datasets (tens to hundreds of elements). For large or unbounded data, use a separate table with a clustering column instead of a collection.

### When to Use Collections

| Use Case | Recommended Type | Example |
|----------|------------------|---------|
| Ordered items with duplicates | LIST | Recent search queries, action history |
| Unique tags or categories | SET | User roles, product tags, permissions |
| Key-value properties | MAP | User preferences, metadata, attributes |
| Large or unbounded data | **Separate table** | Order line items, comments, events |

### LIST

Ordered collection that maintains insertion order and allows duplicate values. Elements are accessed by index position.

**Characteristics:**

- Maintains insertion order
- Allows duplicate values
- Index-based access (0-indexed)
- Append and prepend operations
- Read-before-write required for index updates

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    phone_numbers LIST<TEXT>,
    recent_searches LIST<TEXT>
);

-- Insert list
INSERT INTO users (user_id, phone_numbers, recent_searches)
VALUES (uuid(), ['+1-555-0100', '+1-555-0101'], ['cassandra', 'database']);

-- Append to end (efficient)
UPDATE users SET phone_numbers = phone_numbers + ['+1-555-0102']
WHERE user_id = ?;

-- Prepend to beginning (efficient)
UPDATE users SET recent_searches = ['nosql'] + recent_searches
WHERE user_id = ?;

-- Remove by value (removes all occurrences)
UPDATE users SET recent_searches = recent_searches - ['database']
WHERE user_id = ?;

-- Update by index (requires read-before-write internally)
UPDATE users SET phone_numbers[0] = '+1-555-9999'
WHERE user_id = ?;

-- Delete by index
DELETE phone_numbers[1] FROM users WHERE user_id = ?;
```

!!! danger "LIST Anti-Patterns"
    - **Index-based updates**: `list[i] = value` requires reading the list first, creating a race condition under concurrent writes
    - **Large lists**: Reading a list reads all elements; large lists cause latency spikes
    - **Frequent middle insertions**: No efficient way to insert at arbitrary positions

**When to Use LIST:**

- Small, bounded ordered sequences (< 100 elements)
- Append/prepend-only patterns (logs, history)
- When duplicates are meaningful
- When order matters

### SET

Unordered collection of unique elements. Elements are stored in sorted order internally (by element value).

**Characteristics:**

- Unique elements only (duplicates ignored)
- Sorted internally by element value
- Efficient add/remove operations
- No index-based access
- Idempotent additions

```sql
CREATE TABLE articles (
    article_id UUID PRIMARY KEY,
    tags SET<TEXT>,
    liked_by SET<UUID>
);

-- Insert set
INSERT INTO articles (article_id, tags)
VALUES (uuid(), {'technology', 'programming', 'cassandra'});

-- Add elements (idempotent - adding existing element has no effect)
UPDATE articles SET tags = tags + {'database', 'nosql'}
WHERE article_id = ?;

-- Remove elements
UPDATE articles SET tags = tags - {'programming'}
WHERE article_id = ?;

-- Check membership with CONTAINS (requires index or ALLOW FILTERING)
SELECT * FROM articles WHERE tags CONTAINS 'cassandra' ALLOW FILTERING;

-- With secondary index
CREATE INDEX ON articles (tags);
SELECT * FROM articles WHERE tags CONTAINS 'cassandra';
```

**When to Use SET:**

- Tags, categories, labels
- Many-to-many relationships (small cardinality)
- Permissions or roles
- When uniqueness is required
- When order doesn't matter

### MAP

Collection of key-value pairs. Keys must be unique; values can be any type.

**Characteristics:**

- Unique keys
- Keys sorted internally
- Direct key-based access
- Efficient single-key updates
- Keys and values can be different types

```sql
CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY,
    preferences MAP<TEXT, TEXT>,
    scores MAP<TEXT, INT>,
    metadata MAP<TEXT, FROZEN<some_udt>>
);

-- Insert map
INSERT INTO user_profiles (user_id, preferences, scores)
VALUES (uuid(),
    {'theme': 'dark', 'language': 'en', 'timezone': 'UTC'},
    {'level': 5, 'points': 1000, 'achievements': 42});

-- Update specific key (efficient, no read required)
UPDATE user_profiles SET preferences['theme'] = 'light'
WHERE user_id = ?;

-- Add multiple keys
UPDATE user_profiles SET preferences = preferences + {'notifications': 'on', 'beta': 'true'}
WHERE user_id = ?;

-- Remove specific key
DELETE preferences['timezone'] FROM user_profiles
WHERE user_id = ?;

-- Remove multiple keys
UPDATE user_profiles SET preferences = preferences - {'beta', 'notifications'}
WHERE user_id = ?;

-- Query by key (requires index or ALLOW FILTERING)
CREATE INDEX ON user_profiles (KEYS(preferences));
SELECT * FROM user_profiles WHERE preferences CONTAINS KEY 'theme';

-- Query by value
CREATE INDEX ON user_profiles (VALUES(preferences));
SELECT * FROM user_profiles WHERE preferences CONTAINS 'dark';

-- Query by entry (key-value pair)
CREATE INDEX ON user_profiles (ENTRIES(preferences));
SELECT * FROM user_profiles WHERE preferences['theme'] = 'dark';
```

**When to Use MAP:**

- Configuration or preferences
- Dynamic attributes (schema-less properties)
- Counters by category
- Localized content (language → text)
- Metadata storage

### Collection Storage and Performance

#### Cell-Per-Element Storage

Each collection element is stored as a separate cell:

| Collection | Cell Key | Cell Value |
|------------|----------|------------|
| `LIST<TEXT>` | UUID (timeuuid) | Element value |
| `SET<TEXT>` | Element value | Empty |
| `MAP<K,V>` | Key | Value |

This means:

- **Reading**: All elements are read together (no partial reads)
- **Writing**: Individual elements can be added/removed without reading
- **Size**: Collection overhead scales with element count

#### Performance Implications

| Operation | LIST | SET | MAP |
|-----------|------|-----|-----|
| Read entire collection | O(n) | O(n) | O(n) |
| Append/prepend | O(1) | N/A | N/A |
| Add element | O(1) | O(1) | O(1) |
| Remove by value | O(n) | O(1) | O(1) |
| Update by index | O(n)* | N/A | N/A |
| Update by key | N/A | N/A | O(1) |

*Requires read-before-write

### Collection Restrictions

!!! danger "Hard Limits"
    | Limit | Value | Notes |
    |-------|-------|-------|
    | Maximum element size | 64 KB | Per individual element |
    | Maximum elements | 2 billion | Practical limit much lower |
    | Maximum collection size | 2 GB | Total serialized size |
    | Primary key usage | Frozen only | Non-frozen cannot be in PK |

!!! warning "Practical Limits"
    - **Recommended max elements**: ~100 for optimal performance
    - **Query impact**: Large collections cause GC pressure and latency
    - **Tombstones**: Removing elements creates tombstones until compaction
    - **No pagination**: Cannot partially read a collection

#### Operations Not Supported

- **No sorting**: Cannot ORDER BY collection contents
- **No aggregation**: Cannot SUM/AVG collection elements
- **No filtering on non-indexed**: CONTAINS requires index or ALLOW FILTERING
- **No atomic pop**: Cannot atomically read-and-remove
- **No intersection/union**: Set operations must be done client-side

### Frozen Collections

The `FROZEN` modifier serializes the entire collection as a single blob value.

```sql
-- Non-frozen (default): individual element updates possible
tags SET<TEXT>

-- Frozen: entire collection replaced on update
tags FROZEN<SET<TEXT>>
```

| Aspect | Non-Frozen | Frozen |
|--------|------------|--------|
| Element updates | Individual | Replace entire collection |
| Storage | Cell per element | Single blob |
| Primary key | Not allowed | Allowed |
| Nested collections | Not allowed | Required for nesting |
| Equality comparison | Not supported | Supported |

```sql
-- Frozen required for primary key
CREATE TABLE user_groups (
    members FROZEN<SET<UUID>> PRIMARY KEY,
    group_name TEXT
);

-- Frozen required for nested collections
CREATE TABLE complex_data (
    id UUID PRIMARY KEY,
    matrix LIST<FROZEN<LIST<INT>>>,
    nested_map MAP<TEXT, FROZEN<MAP<TEXT, INT>>>
);
```

!!! tip "When to Use Frozen"
    - Collection is part of primary key
    - Nested collections (always required)
    - Collection is always replaced entirely
    - Need equality comparison (`WHERE col = {frozen_value}`)

### Collection Anti-Patterns

!!! danger "Avoid These Patterns"

    **Unbounded collections**
    ```sql
    -- BAD: followers can grow infinitely
    followers SET<UUID>

    -- GOOD: use a separate table
    CREATE TABLE followers (
        user_id UUID,
        follower_id UUID,
        PRIMARY KEY ((user_id), follower_id)
    );
    ```

    **Large collections**
    ```sql
    -- BAD: storing all order items in collection
    items LIST<FROZEN<order_item>>

    -- GOOD: use clustering column
    CREATE TABLE order_items (
        order_id UUID,
        item_id UUID,
        ...,
        PRIMARY KEY ((order_id), item_id)
    );
    ```

    **Concurrent list index updates**
    ```sql
    -- BAD: race condition
    UPDATE users SET history[0] = 'new' WHERE user_id = ?;

    -- GOOD: append-only
    UPDATE users SET history = history + ['new'] WHERE user_id = ?;
    ```

    **Using collections for querying**
    ```sql
    -- BAD: scanning all rows
    SELECT * FROM products WHERE tags CONTAINS 'sale' ALLOW FILTERING;

    -- GOOD: denormalize to separate table
    CREATE TABLE products_by_tag (
        tag TEXT,
        product_id UUID,
        PRIMARY KEY ((tag), product_id)
    );
    ```

### Best Practices

1. **Keep collections small**: Target < 100 elements
2. **Use frozen for immutable data**: Better performance when not updating elements
3. **Prefer SET over LIST**: Unless order or duplicates matter
4. **Avoid index updates on LIST**: Use append/prepend only
5. **Consider denormalization**: Large collections → separate table
6. **Index strategically**: CONTAINS queries need secondary index
7. **Monitor tombstones**: Element deletes create tombstones

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

- **[DDL Commands](../ddl/index.md)** - Schema management
