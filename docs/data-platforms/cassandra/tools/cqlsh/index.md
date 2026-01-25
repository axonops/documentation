---
title: "Cassandra cqlsh Reference Guide"
description: "CQLSH command-line shell reference for Apache Cassandra. Execute CQL queries, explore schemas, manage data, and configure connections with this interactive CLI."
meta:
  - name: keywords
    content: "cqlsh, CQL shell, command line, interactive queries"
---

# cqlsh Reference Guide

For those who have used `mysql` or `psql`, cqlsh will feel familiar—a command-line interface for running queries, exploring schemas, and managing data. It ships with Cassandra and has been the default way to interact with clusters since CQL replaced Thrift in 2011.

cqlsh is written in Python, which means Python must be installed, and occasionally version compatibility issues arise. It is functional but basic: no AI assistance, minimal autocompletion, and output limited to text tables. For a more modern alternative, check out [CQLAI](../cqlai/index.md)—it handles everything cqlsh does plus AI-powered query generation, Parquet exports, and better formatting.

But cqlsh is everywhere. It is on every Cassandra node, requires no installation, and every tutorial assumes its use. This reference covers everything needed to be productive with it.

## Installation and Setup

### Included with Cassandra

```bash
# cqlsh is included in Cassandra installation
/opt/cassandra/bin/cqlsh

# Or if in PATH
cqlsh
```

### Standalone Installation

```bash
# Python 3.6–3.11 required
# cqlsh is included with Cassandra; for standalone use, install the driver:
pip install cassandra-driver
```

!!! note "Python Version Compatibility"
    cqlsh requires Python 3.6 through 3.11. Python 3.12+ may not be fully compatible. Use `python3 --version` to verify.

---

## Connecting to Cassandra

### Basic Connection

```bash
# Connect to localhost
cqlsh

# Connect to specific host
cqlsh 10.0.0.1

# Connect to specific host and port
cqlsh 10.0.0.1 9042

# With authentication
cqlsh -u username -p password 10.0.0.1

# Prompt for password (more secure)
cqlsh -u username 10.0.0.1
# Enter password when prompted
```

### Connection with SSL

```bash
# Basic SSL (certificate paths configured in cqlshrc)
cqlsh --ssl 10.0.0.1
```

!!! note "SSL Configuration"
    SSL certificates must be configured in `~/.cassandra/cqlshrc` under the `[ssl]` section. There is no command-line flag for specifying certificate files directly.

### cqlshrc Configuration

```ini
# ~/.cassandra/cqlshrc

[authentication]
username = cassandra
password = cassandra

[connection]
hostname = 10.0.0.1
port = 9042
timeout = 10

[ssl]
certfile = /path/to/ca-cert.pem
validate = true
# userkey = /path/to/client-key.pem
# usercert = /path/to/client-cert.pem

[cql]
version = 3.4.5

[ui]
color = on
float_precision = 5
timezone = UTC
encoding = utf8
```

---

## Command-Line Options

**Usage:** `cqlsh [options] [host [port]]`

!!! note "Port Specification"
    Port is a positional argument, not a flag. Use `cqlsh hostname 9042` (not `--port`).

| Option | Description |
|--------|-------------|
| `-u, --username` | Username for authentication |
| `-p, --password` | Password for authentication |
| `-k, --keyspace` | Keyspace to use |
| `-f, --file` | Execute commands from file |
| `-e, --execute` | Execute command and exit |
| `--ssl` | Use SSL (configure certs in cqlshrc) |
| `--connect-timeout` | Connection timeout in seconds |
| `--request-timeout` | Request timeout in seconds |
| `--encoding` | Character encoding |
| `--cqlversion` | CQL version to use |
| `--debug` | Show debug output |

### Examples

```bash
# Execute single command
cqlsh -e "SELECT * FROM system.local"

# Execute file
cqlsh -f /path/to/script.cql

# Connect to specific keyspace
cqlsh -k my_keyspace 10.0.0.1

# With timeout
cqlsh --connect-timeout=10 --request-timeout=60 10.0.0.1
```

---

## Shell Commands

### Help Commands

```sql
HELP;                    -- Show all commands
HELP <command>;          -- Help for specific command
HELP SELECT;             -- Help for SELECT
```

### Navigation Commands

```sql
-- Use keyspace
USE my_keyspace;

-- Show current keyspace
-- (shown in prompt: cqlsh:my_keyspace>)

-- Describe commands
DESCRIBE KEYSPACES;
DESC KEYSPACES;          -- Abbreviation

DESCRIBE KEYSPACE my_keyspace;
DESCRIBE TABLES;
DESCRIBE TABLE users;
DESCRIBE TYPES;
DESCRIBE FUNCTIONS;
DESCRIBE AGGREGATES;
DESCRIBE CLUSTER;

-- Full schema
DESCRIBE SCHEMA;
DESC FULL SCHEMA;        -- With internals
```

### Execution Control

```sql
-- Enable/disable tracing
TRACING ON;
TRACING OFF;

-- Set consistency level
CONSISTENCY;             -- Show current
CONSISTENCY QUORUM;
CONSISTENCY LOCAL_QUORUM;

-- Serial consistency (for LWT)
SERIAL CONSISTENCY LOCAL_SERIAL;

-- Expand output (vertical format)
EXPAND ON;
EXPAND OFF;

-- Paging
PAGING ON;
PAGING OFF;
PAGING 100;              -- Set page size
```

### Input/Output Commands

```sql
-- Capture output to file
CAPTURE '/path/to/output.txt';
CAPTURE OFF;

-- Source commands from file
SOURCE '/path/to/commands.cql';

-- Login (change user)
LOGIN username 'password';

-- Exit
EXIT;
QUIT;
```

---

## Query Formatting

### Output Formats

```sql
-- Standard output
SELECT * FROM users;

-- Expanded output (vertical)
EXPAND ON;
SELECT * FROM users LIMIT 1;

-- JSON output
SELECT JSON * FROM users LIMIT 1;
```

### Column Display

```sql
-- Select specific columns
SELECT user_id, username FROM users;

-- With functions
SELECT user_id, TTL(email), WRITETIME(email) FROM users;
```

---

## COPY Command

### Export Data (COPY TO)

```sql
-- Export to CSV
COPY my_keyspace.users TO '/path/to/users.csv';

-- With header
COPY my_keyspace.users TO '/path/to/users.csv' WITH HEADER = TRUE;

-- Specific columns
COPY my_keyspace.users (user_id, username, email) TO '/path/to/users.csv';

-- With options
COPY my_keyspace.users TO '/path/to/users.csv'
WITH HEADER = TRUE
 AND DELIMITER = '|'
 AND NULL = 'N/A'
 AND ENCODING = 'UTF8';
```

### Import Data (COPY FROM)

```sql
-- Import from CSV
COPY my_keyspace.users FROM '/path/to/users.csv';

-- With header (skip first row)
COPY my_keyspace.users FROM '/path/to/users.csv' WITH HEADER = TRUE;

-- Import specific columns
COPY my_keyspace.users (user_id, username, email) FROM '/path/to/users.csv';

-- With options
COPY my_keyspace.users FROM '/path/to/users.csv'
WITH HEADER = TRUE
 AND DELIMITER = ','
 AND NULL = ''
 AND MAXBATCHSIZE = 20
 AND INGESTRATE = 10000;
```

### COPY Options

| Option | Description | Default |
|--------|-------------|---------|
| `DELIMITER` | Column delimiter | `,` |
| `QUOTE` | Quote character | `"` |
| `ESCAPE` | Escape character | `\` |
| `HEADER` | First row is header | `FALSE` |
| `NULL` | NULL representation | empty |
| `ENCODING` | File encoding | `UTF8` |
| `MAXBATCHSIZE` | Batch size | 20 |
| `INGESTRATE` | Rows per second | 100000 |
| `CHUNKSIZE` | Chunk size | 5000 |
| `MAXROWS` | Max rows to import | -1 (all) |

---

## Working with Data Types

### UUIDs

```sql
-- Generate UUID
INSERT INTO users (user_id, name) VALUES (uuid(), 'John');

-- Generate TimeUUID
INSERT INTO events (event_id, data) VALUES (now(), 'event');

-- Query with UUID
SELECT * FROM users WHERE user_id = 550e8400-e29b-41d4-a716-446655440000;
```

### Timestamps

```sql
-- Insert timestamp
INSERT INTO events (id, created_at) VALUES (uuid(), '2024-01-15 10:30:00');

-- With timezone
INSERT INTO events (id, created_at) VALUES (uuid(), '2024-01-15 10:30:00+0000');

-- Current timestamp
INSERT INTO events (id, created_at) VALUES (uuid(), toTimestamp(now()));
```

### Collections

```sql
-- List
INSERT INTO users (id, phones) VALUES (uuid(), ['+1-555-0100', '+1-555-0101']);
UPDATE users SET phones = phones + ['+1-555-0102'] WHERE id = ?;

-- Set
INSERT INTO users (id, tags) VALUES (uuid(), {'premium', 'verified'});
UPDATE users SET tags = tags + {'new_tag'} WHERE id = ?;

-- Map
INSERT INTO users (id, prefs) VALUES (uuid(), {'theme': 'dark', 'lang': 'en'});
UPDATE users SET prefs['theme'] = 'light' WHERE id = ?;
```

### User-Defined Types

```sql
-- Create type
CREATE TYPE address (
    street TEXT,
    city TEXT,
    postal_code TEXT
);

-- Use in table
CREATE TABLE users (
    id UUID PRIMARY KEY,
    name TEXT,
    home_address FROZEN<address>
);

-- Insert UDT
INSERT INTO users (id, name, home_address)
VALUES (uuid(), 'John', {street: '123 Main St', city: 'NYC', postal_code: '10001'});

-- Access UDT fields
SELECT name, home_address.city FROM users;
```

---

## Scripting with cqlsh

### Script File Example

```sql
-- setup.cql

-- Create keyspace
CREATE KEYSPACE IF NOT EXISTS my_app WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'datacenter1': 3
};

USE my_app;

-- Create tables
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY,
    username TEXT,
    email TEXT,
    created_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS events (
    user_id UUID,
    event_time TIMESTAMP,
    event_type TEXT,
    data TEXT,
    PRIMARY KEY ((user_id), event_time)
) WITH CLUSTERING ORDER BY (event_time DESC);

-- Create indexes
CREATE INDEX IF NOT EXISTS ON users (email);

-- Insert sample data
INSERT INTO users (user_id, username, email, created_at)
VALUES (uuid(), 'admin', 'admin@example.com', toTimestamp(now()));
```

### Running Scripts

```bash
# Execute script
cqlsh -f setup.cql

# With authentication
cqlsh -u admin -p password -f setup.cql

# Execute inline
cqlsh -e "USE my_app; SELECT * FROM users;"

# Pipe commands
echo "SELECT * FROM system.local;" | cqlsh
```

### Conditional Logic (Shell)

```bash
#!/bin/bash
# check_and_create.sh

# Check if keyspace exists
result=$(cqlsh -e "DESCRIBE KEYSPACE my_app" 2>&1)

if [[ $result == *"not found"* ]]; then
    echo "Creating keyspace..."
    cqlsh -f create_keyspace.cql
else
    echo "Keyspace exists"
fi
```

---

## Troubleshooting

### Connection Issues

```bash
# Test basic connectivity
nc -zv 10.0.0.1 9042

# Check with debug
cqlsh --debug 10.0.0.1

# Check SSL issues
openssl s_client -connect 10.0.0.1:9042
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Connection refused` | Cassandra not running or wrong port | Check service, verify port |
| `Authentication failed` | Wrong credentials | Check username/password |
| `SSL handshake failed` | Certificate issues | Check cert paths, validate certs |
| `Request timed out` | Query too slow | Increase timeout, optimize query |
| `No host available` | All nodes down | Check cluster status |

### Performance Issues

```sql
-- Enable tracing to diagnose slow queries
TRACING ON;
SELECT * FROM large_table WHERE id = ?;

-- Check consistency level impact
CONSISTENCY LOCAL_ONE;  -- Faster
CONSISTENCY QUORUM;     -- Slower but consistent
```

---

## Tips and Best Practices

### Efficiency

```bash
# Use keyspace flag instead of USE command
cqlsh -k my_keyspace

# Execute multiple commands from file
cqlsh -f batch_operations.cql

# Increase timeout for large operations
cqlsh --request-timeout=300
```

### Security

```bash
# Don't pass password on command line (visible in history)
# Bad:
cqlsh -u admin -p password

# Good:
cqlsh -u admin  # Prompts for password

# Or use cqlshrc
# ~/.cassandra/cqlshrc with restricted permissions
chmod 600 ~/.cassandra/cqlshrc
```

### Data Operations

```sql
-- Use COPY for bulk operations, not individual INSERTs
-- Good:
COPY users FROM 'users.csv';

-- Less efficient for bulk:
INSERT INTO users ...;
INSERT INTO users ...;
-- (thousands of times)

-- Limit results during exploration
SELECT * FROM users LIMIT 10;
```

---

## Next Steps

- **[CQLAI](../cqlai/index.md)** - Modern CQL shell with AI
- **[CQL Reference](../../cql/index.md)** - CQL language guide
- **[nodetool Reference](../../operations/nodetool/index.md)** - Administration tool
- **[Data Modeling](../../data-modeling/index.md)** - Query design
