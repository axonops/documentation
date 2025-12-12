# CQLAI Commands Reference

CQLAI supports all standard CQL commands plus additional meta-commands and AI features for enhanced functionality.

## CQL Commands

Execute any valid CQL statement supported by your Cassandra cluster:

### Data Definition (DDL)

```sql
-- Keyspaces
CREATE KEYSPACE my_keyspace WITH replication = {
    'class': 'NetworkTopologyStrategy', 'dc1': 3
};
ALTER KEYSPACE my_keyspace WITH replication = {
    'class': 'NetworkTopologyStrategy', 'dc1': 3, 'dc2': 3
};
DROP KEYSPACE my_keyspace;

-- Tables
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    username TEXT,
    email TEXT
);
ALTER TABLE users ADD phone TEXT;
DROP TABLE users;
TRUNCATE users;

-- Indexes
CREATE INDEX ON users (email);
CREATE INDEX users_email_idx ON users (email) USING 'sai';
DROP INDEX users_email_idx;

-- User-Defined Types
CREATE TYPE address (
    street TEXT,
    city TEXT,
    zip TEXT
);
ALTER TYPE address ADD country TEXT;
DROP TYPE address;

-- Functions and Aggregates
CREATE FUNCTION my_func(input TEXT)
    CALLED ON NULL INPUT
    RETURNS TEXT
    LANGUAGE java
    AS 'return input.toUpperCase();';
DROP FUNCTION my_func;
```

### Data Manipulation (DML)

```sql
-- Insert
INSERT INTO users (user_id, username, email)
VALUES (uuid(), 'john_doe', 'john@example.com');

INSERT INTO users (user_id, username, email)
VALUES (uuid(), 'temp_user', 'temp@example.com')
USING TTL 86400;

-- Select
SELECT * FROM users;
SELECT username, email FROM users WHERE user_id = ?;
SELECT JSON * FROM users;  -- Returns proper JSON

-- Update
UPDATE users SET email = 'new@example.com'
WHERE user_id = 550e8400-e29b-41d4-a716-446655440000;

UPDATE users USING TTL 3600
SET temp_field = 'value'
WHERE user_id = ?;

-- Delete
DELETE FROM users WHERE user_id = ?;
DELETE email FROM users WHERE user_id = ?;

-- Batch
BEGIN BATCH
    INSERT INTO users (user_id, username) VALUES (uuid(), 'user1');
    INSERT INTO users (user_id, username) VALUES (uuid(), 'user2');
APPLY BATCH;
```

### Data Control (DCL)

```sql
-- Roles
CREATE ROLE admin WITH PASSWORD = 'pass' AND SUPERUSER = true AND LOGIN = true;
ALTER ROLE admin WITH PASSWORD = 'newpass';
DROP ROLE admin;

-- Permissions
GRANT ALL PERMISSIONS ON KEYSPACE my_app TO admin;
GRANT SELECT ON TABLE users TO readonly_role;
REVOKE DELETE ON TABLE users FROM app_role;
LIST ALL PERMISSIONS OF admin;
```

---

## Meta-Commands

### Session Management

#### USE

Switch to a keyspace:

```sql
USE my_keyspace;
```

#### CONSISTENCY

Set or show consistency level:

```sql
-- Show current level
CONSISTENCY;

-- Set level
CONSISTENCY QUORUM;
CONSISTENCY LOCAL_QUORUM;
CONSISTENCY ONE;
```

Available levels:
- `ANY` - Write to any node (including hints)
- `ONE` - One replica
- `TWO` - Two replicas
- `THREE` - Three replicas
- `QUORUM` - Majority of replicas
- `ALL` - All replicas
- `LOCAL_QUORUM` - Majority in local DC
- `EACH_QUORUM` - Quorum in each DC
- `LOCAL_ONE` - One replica in local DC
- `SERIAL` - For lightweight transactions
- `LOCAL_SERIAL` - Local serial

#### PAGING

Control result pagination:

```sql
-- Show current page size
PAGING;

-- Set page size
PAGING 100;
PAGING 1000;

-- Disable paging
PAGING OFF;
```

#### TRACING

Enable query tracing:

```sql
-- Enable tracing
TRACING ON;

-- Run query (trace shown in F4 view)
SELECT * FROM users WHERE user_id = ?;

-- Disable tracing
TRACING OFF;
```

#### EXPAND

Toggle vertical output mode:

```sql
-- Enable expanded output
EXPAND ON;

-- Query shows one field per line
SELECT * FROM users LIMIT 1;

-- Disable expanded output
EXPAND OFF;
```

#### OUTPUT

Set output format:

```sql
-- Show current format
OUTPUT;

-- Set format
OUTPUT TABLE;    -- Default table format
OUTPUT JSON;     -- JSON format
OUTPUT ASCII;    -- ASCII table
OUTPUT EXPAND;   -- Expanded vertical format
```

---

### Schema Description

#### DESCRIBE / DESC

View schema information:

```sql
-- List all keyspaces
DESCRIBE KEYSPACES;

-- Show keyspace definition
DESCRIBE KEYSPACE my_keyspace;

-- List tables in current keyspace
DESCRIBE TABLES;

-- Show table structure
DESCRIBE TABLE users;
DESC users;  -- Short form

-- Show table in specific keyspace
DESC my_keyspace.users;

-- User-Defined Types
DESCRIBE TYPES;
DESCRIBE TYPE address;

-- Functions
DESCRIBE FUNCTIONS;
DESCRIBE FUNCTION my_func;

-- Aggregates
DESCRIBE AGGREGATES;
DESCRIBE AGGREGATE my_agg;

-- Materialized Views
DESCRIBE MATERIALIZED VIEWS;
DESCRIBE MATERIALIZED VIEW user_by_email;

-- Indexes
DESCRIBE INDEX users_email_idx;

-- Cluster information
DESCRIBE CLUSTER;
```

#### SHOW

Display session information:

```sql
-- Show Cassandra version
SHOW VERSION;

-- Show current connection
SHOW HOST;

-- Show all session settings
SHOW SESSION;
```

---

### Data Import/Export

#### COPY TO

Export table data to file:

```sql
-- Export to CSV
COPY users TO 'users.csv';

-- Export to Parquet (auto-detected by extension)
COPY users TO 'users.parquet';

-- Export specific columns
COPY users (id, name, email) TO 'users_partial.csv';

-- Export with options
COPY users TO 'users.csv' WITH HEADER=TRUE AND DELIMITER='|';

-- Export to stdout
COPY users TO STDOUT WITH HEADER=TRUE;

-- Parquet with compression
COPY users TO 'users.parquet' WITH FORMAT='PARQUET' AND COMPRESSION='SNAPPY';
```

**COPY TO Options**:

| Option | Default | Description |
|--------|---------|-------------|
| `FORMAT` | CSV | Output format: CSV or PARQUET |
| `HEADER` | TRUE | Include column headers (CSV) |
| `DELIMITER` | `,` | Field separator (CSV) |
| `NULLVAL` | (empty) | String for NULL values |
| `PAGESIZE` | 1000 | Rows per page for large exports |
| `COMPRESSION` | SNAPPY | For Parquet: SNAPPY, GZIP, ZSTD, LZ4, NONE |
| `CHUNKSIZE` | 10000 | Rows per chunk (Parquet) |

#### COPY FROM

Import data from file:

```sql
-- Import from CSV
COPY users FROM 'users.csv';

-- Import from Parquet
COPY users FROM 'users.parquet';

-- Import with header row
COPY users FROM 'users.csv' WITH HEADER=TRUE;

-- Import specific columns
COPY users (id, name, email) FROM 'users_partial.csv';

-- Import from stdin
COPY users FROM STDIN;

-- Import with options
COPY users FROM 'data.csv' WITH HEADER=TRUE AND DELIMITER='|' AND NULLVAL='N/A';
```

**COPY FROM Options**:

| Option | Default | Description |
|--------|---------|-------------|
| `FORMAT` | CSV | Input format: CSV or PARQUET |
| `HEADER` | FALSE | First row contains headers |
| `DELIMITER` | `,` | Field separator |
| `NULLVAL` | (empty) | String representing NULL |
| `MAXROWS` | -1 | Max rows to import (-1=unlimited) |
| `SKIPROWS` | 0 | Rows to skip at start |
| `MAXPARSEERRORS` | -1 | Max parse errors allowed |
| `MAXINSERTERRORS` | 1000 | Max insert errors allowed |
| `MAXBATCHSIZE` | 20 | Max rows per batch |
| `MINBATCHSIZE` | 2 | Min rows per batch |
| `CHUNKSIZE` | 5000 | Progress update interval |
| `ENCODING` | UTF8 | File encoding |
| `QUOTE` | `"` | Quote character |

#### CAPTURE

Capture query output continuously:

```sql
-- Start capturing to text file
CAPTURE 'output.txt';

-- Capture as JSON
CAPTURE JSON 'output.json';

-- Capture as CSV
CAPTURE CSV 'output.csv';

-- Run queries (output captured)
SELECT * FROM users;
SELECT * FROM orders;

-- Stop capturing
CAPTURE OFF;
```

#### SAVE

Save displayed results to file:

```sql
-- Run a query first
SELECT * FROM users WHERE status = 'active';

-- Save displayed results
SAVE;                      -- Interactive dialog
SAVE 'users.csv';         -- Auto-detect format
SAVE 'users.json';        -- JSON format
SAVE 'data.txt' ASCII;    -- ASCII table
```

**Difference from CAPTURE**: SAVE exports currently displayed results without re-executing the query. CAPTURE records all subsequent query results.

---

### Script Execution

#### SOURCE

Execute CQL script from file:

```sql
-- Execute script
SOURCE 'schema.cql';

-- Absolute path
SOURCE '/path/to/script.cql';
```

---

### Help

#### HELP

Display command help:

```sql
-- Show all commands
HELP;

-- Help for specific command
HELP DESCRIBE;
HELP CONSISTENCY;
HELP COPY;
```

---

## AI Commands

### .ai

Generate CQL from natural language:

```sql
-- Simple queries
.ai show all users
.ai find products with price less than 100
.ai count orders from last month

-- Complex operations
.ai create a table for storing customer feedback with id, customer_id, rating, and comment
.ai update user status to inactive where last_login is older than 90 days
.ai delete all expired sessions

-- Schema exploration
.ai what tables are in this keyspace
.ai describe the structure of the users table
.ai show me the primary key of the orders table
```

**How it works**:
1. Type `.ai` followed by your request
2. CQLAI extracts your current schema for context
3. AI generates a CQL query
4. Preview the query before execution
5. Execute, edit, or cancel

**Safety features**:
- Read-only preference (prefers SELECT unless asked otherwise)
- Warnings for destructive operations (DROP, DELETE, TRUNCATE)
- Confirmation required for dangerous queries
- Schema validation

See [AI Features Guide](../ai-features/index.md) for configuration and advanced usage.

---

## Keyboard Shortcuts Reference

### Navigation & Control

| Shortcut | Action |
|----------|--------|
| `↑` / `↓` | Navigate command history |
| `Tab` | Auto-complete |
| `Ctrl+C` | Clear input / Cancel / Exit (twice) |
| `Ctrl+D` | Exit application |
| `Ctrl+R` | Search command history |
| `Esc` | Toggle navigation mode |
| `Enter` | Execute / Load next page |

### Text Editing

| Shortcut | Action |
|----------|--------|
| `Ctrl+A` | Jump to beginning of line |
| `Ctrl+E` | Jump to end of line |
| `Ctrl+K` | Cut to end of line |
| `Ctrl+U` | Cut to beginning of line |
| `Ctrl+W` | Cut word backward |
| `Ctrl+Y` | Paste cut text |

### View Switching

| Shortcut | Action |
|----------|--------|
| `F2` | Query/history view |
| `F3` | Table view |
| `F4` | Trace view |
| `F5` | AI conversation view |
| `F6` | Toggle column types |

### Navigation Mode (Tables)

| Shortcut | Action |
|----------|--------|
| `j` / `k` | Scroll line down/up |
| `d` / `u` | Scroll half page |
| `g` / `G` | Jump to top/bottom |
| `<` / `>` | Scroll left/right (10 cols) |
| `0` / `$` | First/last column |

---

## Next Steps

- **[AI Features](../ai-features/index.md)** - Configure AI providers
- **[Parquet Support](../parquet/index.md)** - Work with Parquet files
- **[Configuration](../configuration/index.md)** - Full configuration reference
