---
title: "CQLAI Features"
description: "CQLAI features overview. All capabilities of the AI-powered CQL shell."
meta:
  - name: keywords
    content: "CQLAI features, shell capabilities, feature overview"
---

# CQLAI Features

Comprehensive guide to CQLAI's features and capabilities.

## Shell Features

### Syntax Highlighting

CQLAI provides real-time syntax highlighting for:
- CQL keywords (SELECT, INSERT, CREATE, etc.)
- Table and keyspace names
- Data types
- String literals
- Numbers
- Comments

### Auto-Completion

```
cqlai> SEL<Tab>
SELECT

cqlai> SELECT * FROM us<Tab>
users    user_events    user_sessions

cqlai> SELECT * FROM users WHERE user_<Tab>
user_id    user_name    user_email
```

### Multi-Line Queries

```sql
cqlai> SELECT user_id,
   ...>        username,
   ...>        email
   ...> FROM users
   ...> WHERE user_id = 123e4567-e89b-12d3-a456-426614174000;
```

### Query History

```bash
# Search history
Ctrl+R: search history

# View history
cqlai> .history

# Execute from history
cqlai> !42  # Run command #42
```

## Output Formats

### Table Format (Default)

```
cqlai> SELECT * FROM users LIMIT 3;

┌──────────────────────────────────────┬──────────┬─────────────────────┐
│ user_id                              │ username │ email               │
├──────────────────────────────────────┼──────────┼─────────────────────┤
│ 123e4567-e89b-12d3-a456-426614174000 │ alice    │ alice@example.com   │
│ 223e4567-e89b-12d3-a456-426614174001 │ bob      │ bob@example.com     │
│ 323e4567-e89b-12d3-a456-426614174002 │ charlie  │ charlie@example.com │
└──────────────────────────────────────┴──────────┴─────────────────────┘
3 rows
```

### JSON Format

```
cqlai> .format json
cqlai> SELECT * FROM users LIMIT 1;

{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "alice",
  "email": "alice@example.com"
}
```

### CSV Format

```
cqlai> .format csv
cqlai> SELECT * FROM users LIMIT 3;

user_id,username,email
123e4567-e89b-12d3-a456-426614174000,alice,alice@example.com
223e4567-e89b-12d3-a456-426614174001,bob,bob@example.com
```

### Vertical Format

```
cqlai> .format vertical
cqlai> SELECT * FROM users LIMIT 1;

*************************** 1. row ***************************
 user_id: 123e4567-e89b-12d3-a456-426614174000
username: alice
   email: alice@example.com
```

## Schema Commands

### Describe Keyspace

```
cqlai> DESCRIBE KEYSPACE my_keyspace;

CREATE KEYSPACE my_keyspace WITH replication = {
  'class': 'NetworkTopologyStrategy',
  'dc1': 3
} AND durable_writes = true;
```

### Describe Table

```
cqlai> DESCRIBE TABLE users;

CREATE TABLE my_keyspace.users (
    user_id uuid PRIMARY KEY,
    username text,
    email text,
    created_at timestamp
) WITH bloom_filter_fp_chance = 0.01
    AND caching = {'keys': 'ALL', 'rows_per_partition': 'NONE'}
    AND compaction = {'class': 'LeveledCompactionStrategy'}
    ...
```

### Quick Description

```
cqlai> .desc users

Table: users
Keyspace: my_keyspace

Columns:
  user_id     uuid        partition key
  username    text
  email       text
  created_at  timestamp

Indexes: none
```

## Query Execution

### Consistency Level

```
cqlai> CONSISTENCY LOCAL_QUORUM;
Consistency level set to LOCAL_QUORUM.

cqlai> SELECT * FROM users;
```

### Tracing

```
cqlai> TRACING ON;
cqlai> SELECT * FROM users WHERE user_id = ?;

Tracing session: abc123
Activity                                   | Timestamp     | Source
-------------------------------------------+---------------+-----------
Execute CQL3 query                         | 10:30:45.123  | 192.168.1.10
Parsing SELECT * FROM users WHERE...       | 10:30:45.124  | 192.168.1.10
Executing single-partition query on users  | 10:30:45.125  | 192.168.1.10
...
```

### Paging

```
cqlai> .page 50
Page size set to 50.

cqlai> SELECT * FROM large_table;
[First 50 rows displayed]
-- Press Enter for more, q to quit --
```

## Connection Management

### Multiple Connections

```
cqlai> .connect production -h prod-cluster.example.com -u admin
Connected to production.

cqlai> .connect staging -h staging.example.com
Connected to staging.

cqlai> .switch production
Switched to production.
```

### Connection Status

```
cqlai> .status

Connection: production
Host: prod-cluster.example.com:9042
Keyspace: my_keyspace
User: admin
Protocol: v4
Consistency: LOCAL_QUORUM
```

## Scripting

### Execute Script File

```bash
# From command line
cqlai -f script.cql

# From shell
cqlai> SOURCE '/path/to/script.cql';
```

### Script Example

```sql
-- script.cql
USE my_keyspace;

-- Create tables
CREATE TABLE IF NOT EXISTS events (
    event_id uuid PRIMARY KEY,
    event_type text,
    payload text
);

-- Insert test data
INSERT INTO events (event_id, event_type, payload)
VALUES (uuid(), 'test', '{"data": "value"}');

-- Verify
SELECT * FROM events;
```

### Batch Mode

```bash
# Non-interactive execution
echo "SELECT * FROM users LIMIT 5;" | cqlai -h localhost

# Pipe results
cqlai -h localhost -e "SELECT * FROM users" | grep "alice"
```

## Utility Commands

### Clear Screen

```
cqlai> .clear
```

### Show Settings

```
cqlai> .settings

Current Settings:
  Host: localhost:9042
  Keyspace: my_keyspace
  Consistency: LOCAL_QUORUM
  Page size: 100
  Format: table
  Color: enabled
  AI Provider: openai
```

### Help

```
cqlai> .help

Available Commands:
  .ai <prompt>        Natural language to CQL
  .clear              Clear screen
  .connect            Manage connections
  .desc <table>       Quick table description
  .export             Export data
  .format <type>      Set output format
  .help               Show this help
  .history            Show command history
  .import             Import data
  .page <size>        Set page size
  .settings           Show current settings
  .status             Connection status
```

---

## Next Steps

- **[AI Features](../ai-features/index.md)** - AI capabilities
- **[Data Import/Export](../data-import-export/index.md)** - Data migration
- **[Configuration](../configuration/index.md)** - Advanced settings
