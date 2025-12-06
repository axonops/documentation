# DDL Commands Reference

Schema changes in Cassandra happen online—columns can be added, tables created, or replication settings changed while the cluster serves traffic. Run `ALTER TABLE users ADD phone text` on a table with billions of rows, and it completes instantly. The schema propagates through gossip, and within seconds every node knows about the change.

This is different from relational databases where `ALTER TABLE` on a large table can lock it for hours. In Cassandra, schema is metadata—the actual data does not need to be rewritten (in most cases).

This reference covers creating and modifying keyspaces, tables, indexes, user-defined types, and functions.

## Quick Reference

| Command | Purpose |
|---------|---------|
| `CREATE KEYSPACE` | Create namespace with replication |
| `ALTER KEYSPACE` | Modify keyspace settings |
| `DROP KEYSPACE` | Delete keyspace and all data |
| `CREATE TABLE` | Create table with schema |
| `ALTER TABLE` | Modify table schema |
| `DROP TABLE` | Delete table and all data |
| `TRUNCATE` | Delete all data, keep schema |
| `CREATE INDEX` | Create secondary index |
| `DROP INDEX` | Remove index |
| `CREATE TYPE` | Create user-defined type |
| `CREATE FUNCTION` | Create user-defined function |
| `CREATE AGGREGATE` | Create user-defined aggregate |

---

## Keyspace Commands

### CREATE KEYSPACE

```sql
-- Simple replication (development only)
CREATE KEYSPACE my_keyspace WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};

-- Network topology (production)
CREATE KEYSPACE my_keyspace WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3,
    'dc2': 3
};

-- With durable writes (default true)
CREATE KEYSPACE my_keyspace WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3
} AND durable_writes = true;

-- If not exists
CREATE KEYSPACE IF NOT EXISTS my_keyspace WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3
};
```

### ALTER KEYSPACE

```sql
-- Change replication
ALTER KEYSPACE my_keyspace WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3,
    'dc2': 3
};

-- Disable durable writes (not recommended)
ALTER KEYSPACE my_keyspace WITH durable_writes = false;
```

**After altering replication**, run repair:
```bash
nodetool repair my_keyspace
```

### DROP KEYSPACE

```sql
-- Drop keyspace (deletes all data!)
DROP KEYSPACE my_keyspace;

-- Safe drop
DROP KEYSPACE IF EXISTS my_keyspace;
```

### USE

```sql
USE my_keyspace;
```

---

## Table Commands

### CREATE TABLE

#### Basic Table

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    username TEXT,
    email TEXT,
    created_at TIMESTAMP
);
```

#### Compound Primary Key

```sql
CREATE TABLE messages (
    user_id UUID,
    message_time TIMESTAMP,
    message_id UUID,
    content TEXT,
    PRIMARY KEY ((user_id), message_time, message_id)
) WITH CLUSTERING ORDER BY (message_time DESC, message_id ASC);
```

**Primary Key Components**:
- `(user_id)`: Partition key (determines node)
- `message_time, message_id`: Clustering columns (sort order within partition)

#### Composite Partition Key

```sql
CREATE TABLE events (
    tenant_id TEXT,
    date DATE,
    event_time TIMESTAMP,
    event_id UUID,
    data TEXT,
    PRIMARY KEY ((tenant_id, date), event_time, event_id)
);
```

#### With Table Options

```sql
CREATE TABLE sensor_data (
    sensor_id TEXT,
    reading_time TIMESTAMP,
    value DOUBLE,
    PRIMARY KEY ((sensor_id), reading_time)
) WITH
    -- Clustering order
    CLUSTERING ORDER BY (reading_time DESC)

    -- Compaction strategy
    AND compaction = {
        'class': 'TimeWindowCompactionStrategy',
        'compaction_window_unit': 'HOURS',
        'compaction_window_size': '1'
    }

    -- Compression
    AND compression = {
        'class': 'LZ4Compressor',
        'chunk_length_in_kb': '64'
    }

    -- TTL default
    AND default_time_to_live = 86400  -- 24 hours

    -- GC grace
    AND gc_grace_seconds = 864000  -- 10 days

    -- Bloom filter
    AND bloom_filter_fp_chance = 0.01

    -- Caching
    AND caching = {
        'keys': 'ALL',
        'rows_per_partition': 'NONE'
    }

    -- Comments
    AND comment = 'Time-series sensor data';
```

#### Static Columns

```sql
CREATE TABLE user_posts (
    user_id UUID,
    post_id TIMEUUID,
    -- Static columns: same value for all rows in partition
    username TEXT STATIC,
    user_email TEXT STATIC,
    -- Regular columns
    post_content TEXT,
    PRIMARY KEY ((user_id), post_id)
);

-- Static column is set once per partition
INSERT INTO user_posts (user_id, username, user_email)
VALUES (?, 'john_doe', 'john@example.com');

-- Regular columns per row
INSERT INTO user_posts (user_id, post_id, post_content)
VALUES (?, now(), 'Hello World!');
```

### ALTER TABLE

```sql
-- Add column
ALTER TABLE users ADD phone TEXT;
ALTER TABLE users ADD (address TEXT, city TEXT);

-- Drop column
ALTER TABLE users DROP phone;
ALTER TABLE users DROP (address, city);

-- Rename column (clustering columns only, Cassandra 3.0+)
ALTER TABLE messages RENAME message_time TO sent_at;

-- Change table options
ALTER TABLE sensor_data WITH
    compaction = {
        'class': 'LeveledCompactionStrategy',
        'sstable_size_in_mb': '160'
    };

-- Change TTL
ALTER TABLE sensor_data WITH default_time_to_live = 172800;

-- Change compression
ALTER TABLE users WITH compression = {
    'class': 'ZstdCompressor'
};
```

### DROP TABLE

```sql
DROP TABLE users;
DROP TABLE IF EXISTS users;
```

### TRUNCATE

```sql
-- Delete all data, keep schema
TRUNCATE users;
TRUNCATE TABLE users;
```

---

## Index Commands

### CREATE INDEX

#### Secondary Index

```sql
-- Basic index
CREATE INDEX ON users (email);

-- Named index
CREATE INDEX users_email_idx ON users (email);

-- Index on collection values
CREATE INDEX ON users (tags);  -- If tags is a SET

-- Index on map keys
CREATE INDEX ON users (KEYS(preferences));

-- Index on map values
CREATE INDEX ON users (VALUES(preferences));

-- Index on map entries
CREATE INDEX ON users (ENTRIES(preferences));

-- Index on full frozen collection
CREATE INDEX ON users (FULL(frozen_list));
```

#### Storage-Attached Index (SAI) - Cassandra 4.0+

```sql
-- Basic SAI index
CREATE INDEX ON users (email) USING 'sai';

-- SAI with options
CREATE INDEX ON users (username) USING 'sai'
WITH OPTIONS = {
    'case_sensitive': 'false',
    'normalize': 'true'
};

-- SAI on map
CREATE INDEX ON users (VALUES(attributes)) USING 'sai';
```

### DROP INDEX

```sql
DROP INDEX users_email_idx;
DROP INDEX IF EXISTS users_email_idx;
DROP INDEX my_keyspace.users_email_idx;
```

---

## Materialized View Commands

### CREATE MATERIALIZED VIEW

```sql
-- Base table
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    username TEXT,
    email TEXT,
    country TEXT
);

-- Materialized view for query by email
CREATE MATERIALIZED VIEW users_by_email AS
    SELECT * FROM users
    WHERE email IS NOT NULL AND user_id IS NOT NULL
    PRIMARY KEY (email, user_id);

-- View with selected columns
CREATE MATERIALIZED VIEW users_by_country AS
    SELECT user_id, username, country FROM users
    WHERE country IS NOT NULL AND user_id IS NOT NULL
    PRIMARY KEY (country, user_id);
```

**Requirements**:
- All primary key columns from base table must be in view
- View primary key must include all base table primary key columns
- Only one non-primary key column can be added to view primary key

### ALTER MATERIALIZED VIEW

```sql
ALTER MATERIALIZED VIEW users_by_email WITH
    compaction = {'class': 'LeveledCompactionStrategy'};
```

### DROP MATERIALIZED VIEW

```sql
DROP MATERIALIZED VIEW users_by_email;
DROP MATERIALIZED VIEW IF EXISTS users_by_email;
```

---

## User-Defined Type Commands

### CREATE TYPE

```sql
CREATE TYPE address (
    street TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    country TEXT
);

CREATE TYPE phone_number (
    country_code TEXT,
    number TEXT,
    type TEXT  -- 'home', 'work', 'mobile'
);
```

### ALTER TYPE

```sql
-- Add field
ALTER TYPE address ADD apartment TEXT;

-- Rename field
ALTER TYPE address RENAME zip_code TO postal_code;
```

### DROP TYPE

```sql
DROP TYPE address;
DROP TYPE IF EXISTS address;
```

---

## Function Commands

### CREATE FUNCTION

```sql
-- Java UDF
CREATE FUNCTION my_keyspace.to_uppercase(input TEXT)
    CALLED ON NULL INPUT
    RETURNS TEXT
    LANGUAGE java
    AS 'return input.toUpperCase();';

-- JavaScript UDF (if enabled)
CREATE FUNCTION my_keyspace.concat_with_space(a TEXT, b TEXT)
    CALLED ON NULL INPUT
    RETURNS TEXT
    LANGUAGE javascript
    AS 'a + " " + b';

-- Null handling
CREATE FUNCTION my_keyspace.safe_length(input TEXT)
    RETURNS NULL ON NULL INPUT
    RETURNS INT
    LANGUAGE java
    AS 'return input.length();';
```

### DROP FUNCTION

```sql
DROP FUNCTION my_keyspace.to_uppercase;
DROP FUNCTION IF EXISTS my_keyspace.to_uppercase;
DROP FUNCTION my_keyspace.to_uppercase(TEXT);  -- Specific signature
```

### CREATE AGGREGATE

```sql
-- State function for average
CREATE FUNCTION my_keyspace.avg_state(state TUPLE<INT, BIGINT>, val INT)
    CALLED ON NULL INPUT
    RETURNS TUPLE<INT, BIGINT>
    LANGUAGE java
    AS 'if (val != null) { state.setInt(0, state.getInt(0) + 1); state.setLong(1, state.getLong(1) + val); } return state;';

-- Final function
CREATE FUNCTION my_keyspace.avg_final(state TUPLE<INT, BIGINT>)
    CALLED ON NULL INPUT
    RETURNS DOUBLE
    LANGUAGE java
    AS 'if (state.getInt(0) == 0) return null; return (double)state.getLong(1) / state.getInt(0);';

-- Aggregate
CREATE AGGREGATE my_keyspace.my_avg(INT)
    SFUNC avg_state
    STYPE TUPLE<INT, BIGINT>
    FINALFUNC avg_final
    INITCOND (0, 0);
```

### DROP AGGREGATE

```sql
DROP AGGREGATE my_keyspace.my_avg;
DROP AGGREGATE IF EXISTS my_keyspace.my_avg(INT);
```

---

## Table Options Reference

### Compaction Options

```sql
-- Size-Tiered (default)
compaction = {
    'class': 'SizeTieredCompactionStrategy',
    'min_threshold': '4',
    'max_threshold': '32'
}

-- Leveled
compaction = {
    'class': 'LeveledCompactionStrategy',
    'sstable_size_in_mb': '160'
}

-- Time-Window
compaction = {
    'class': 'TimeWindowCompactionStrategy',
    'compaction_window_unit': 'HOURS',
    'compaction_window_size': '1'
}

-- Unified (5.0+)
compaction = {
    'class': 'UnifiedCompactionStrategy',
    'scaling_parameters': 'T4'
}
```

### Compression Options

```sql
-- LZ4 (default, fast)
compression = {'class': 'LZ4Compressor'}

-- Snappy
compression = {'class': 'SnappyCompressor'}

-- Zstd (best ratio)
compression = {'class': 'ZstdCompressor'}

-- Deflate
compression = {'class': 'DeflateCompressor'}

-- No compression
compression = {'enabled': 'false'}
```

### Other Options

| Option | Default | Description |
|--------|---------|-------------|
| `bloom_filter_fp_chance` | 0.01 | False positive rate |
| `caching` | keys=ALL | Key and row caching |
| `comment` | '' | Table description |
| `default_time_to_live` | 0 | Default TTL in seconds |
| `gc_grace_seconds` | 864000 | Time before tombstone removal |
| `memtable_flush_period_in_ms` | 0 | Auto-flush interval |
| `read_repair` | BLOCKING | Read repair behavior |
| `speculative_retry` | 99p | Speculative retry trigger |

---

## Next Steps

- **[Keyspaces Detail](keyspaces.md)** - Keyspace management
- **[Tables Detail](tables.md)** - Table design
- **[Indexes Detail](indexes.md)** - Indexing strategies
- **[DML Commands](../dml/index.md)** - Data manipulation
