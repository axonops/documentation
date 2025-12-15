---
title: "CQLAI - Modern AI-Powered CQL Shell"
description: "CQLAI documentation. AI-powered CQL shell for Apache Cassandra."
meta:
  - name: keywords
    content: "CQLAI documentation, AI CQL shell, Cassandra tool"
---

# CQLAI - Modern AI-Powered CQL Shell

CQLAI is a fast, portable interactive terminal for Apache Cassandra, built in Go by AxonOps. It provides a modern, user-friendly alternative to `cqlsh` with an advanced terminal UI, client-side command parsing, and optional AI-powered query generation.

## Why CQLAI?

| Feature | cqlsh | CQLAI |
|---------|-------|-------|
| **Language** | Python (requires Python) | Go (single binary) |
| **Dependencies** | Python 2.7/3.x required | None |
| **AI Query Generation** | No | Yes (optional) |
| **Tab Completion** | Basic | Context-aware |
| **Output Formats** | Limited | Table, JSON, CSV, Parquet |
| **Terminal UI** | Basic readline | Rich TUI with mouse support |
| **Parquet Support** | No | Full import/export |
| **Memory Management** | Can OOM on large results | Virtualized, memory-bounded |

## Key Features

### Zero Dependencies

```bash
# Download and run - that is it!
./cqlai --host cassandra.example.com
```

CQLAI is distributed as a single static binary for:
- Linux x86-64 and aarch64
- macOS x86-64 and arm64 (Apple Silicon)
- Windows x86-64

### Rich Terminal UI

- Full-screen alternate buffer (preserves terminal history)
- Virtualized, scrollable tables for large result sets
- Vim-style keyboard navigation
- Full mouse support including wheel scrolling
- Sticky status bar with connection details and query latency
- Modal overlays for history, help, and completion

### Optional AI-Powered Query Generation

Convert natural language to CQL queries:

```sql
.ai show all active users created in the last 7 days
.ai create a table for storing product inventory
.ai find orders with total greater than 1000
```

Supports multiple AI providers:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude 3)
- Google Gemini
- Ollama (local models)
- OpenRouter
- Synthetic

**AI is completely optional** - CQLAI works as a full-featured CQL shell without any AI configuration.

### Apache Parquet Support

Export and import data in Parquet format for analytics:

```sql
-- Export to Parquet
COPY users TO 'users.parquet';

-- Export with compression
COPY events TO 'events.parquet' WITH COMPRESSION='ZSTD';

-- Import from Parquet
COPY analytics_data FROM 'dataset.parquet';
```

### Smart Tab Completion

Context-aware completion for:
- CQL keywords and commands
- Keyspace and table names
- Column names
- Consistency levels
- File paths

```sql
SELECT * FROM us<Tab>    -- Completes to 'users'
CONSISTENCY LOC<Tab>     -- Shows LOCAL_ONE, LOCAL_QUORUM, LOCAL_SERIAL
```

---

## Quick Start

### Installation

```bash
# Using Go
go install github.com/axonops/cqlai/cmd/cqlai@latest

# Or download from releases
# https://github.com/axonops/cqlai/releases
```

See [Installation Guide](installation/index.md) for detailed instructions including package managers.

### Connect to Cassandra

```bash
# Basic connection
cqlai --host 127.0.0.1

# With authentication
cqlai --host cassandra.example.com -u myuser
# Password: [hidden prompt]

# With keyspace
cqlai --host 127.0.0.1 -k my_keyspace
```

### Run Queries

```sql
-- Standard CQL
SELECT * FROM users;
DESCRIBE TABLES;
CONSISTENCY QUORUM;

-- AI-powered (requires configuration)
.ai list all tables in this keyspace
```

---

---

## Comparison with cqlsh

### What CQLAI Does Better

1. **No Python Required**
   - cqlsh requires Python 2.7 or 3.x with cassandra-driver
   - CQLAI is a single binary with zero dependencies

2. **Better Performance**
   - Faster startup time
   - Memory-bounded result display (will not OOM on large queries)
   - Streaming export for large tables

3. **Modern Terminal Experience**
   - Rich UI with mouse support
   - Vim-style navigation
   - Better auto-completion

4. **AI Integration**
   - Generate queries from natural language
   - Schema-aware suggestions

5. **Parquet Support**
   - Direct export to Parquet format
   - Integration with analytics workflows

### Full Compatibility

CQLAI supports:
- All CQL commands your cluster supports
- Meta-commands: DESCRIBE, SHOW, CONSISTENCY, TRACING, etc.
- COPY TO/FROM for data import/export
- SSL/TLS and authentication
- User-Defined Types (UDTs) and complex types
- Batch mode for scripting

---

## Example Session

```
$ cqlai --host 127.0.0.1 -k my_app

Connected to: 127.0.0.1:9042 | Keyspace: my_app | CL: LOCAL_ONE

cqlai> DESCRIBE TABLES;

users
orders
products
events

cqlai> SELECT * FROM users LIMIT 5;

┌──────────────────────────────────────┬────────────┬─────────────────────┐
│ user_id                              │ username   │ email               │
├──────────────────────────────────────┼────────────┼─────────────────────┤
│ 550e8400-e29b-41d4-a716-446655440000 │ john_doe   │ john@example.com    │
│ 660e8400-e29b-41d4-a716-446655440001 │ jane_smith │ jane@example.com    │
│ 770e8400-e29b-41d4-a716-446655440002 │ bob_wilson │ bob@example.com     │
└──────────────────────────────────────┴────────────┴─────────────────────┘
(3 rows)  |  Latency: 2.3ms

cqlai> .ai find users who registered this month

Generated CQL:
  SELECT * FROM users
  WHERE created_at >= '2024-01-01'
  AND created_at < '2024-02-01'
  ALLOW FILTERING;

Execute? [Y/n]: y

┌──────────────────────────────────────┬────────────┬─────────────────────┐
│ user_id                              │ username   │ created_at          │
├──────────────────────────────────────┼────────────┼─────────────────────┤
│ 880e8400-e29b-41d4-a716-446655440003 │ new_user   │ 2024-01-15 10:30:00 │
└──────────────────────────────────────┴────────────┴─────────────────────┘
(1 row)  |  Latency: 4.1ms

cqlai> COPY users TO 'users_backup.parquet' WITH COMPRESSION='SNAPPY';

Exported 3 rows to users_backup.parquet (Parquet, Snappy)

cqlai>
```

---

## Resources

- **GitHub**: [github.com/axonops/cqlai](https://github.com/axonops/cqlai)
- **Releases**: [github.com/axonops/cqlai/releases](https://github.com/axonops/cqlai/releases)
- **Issues**: [github.com/axonops/cqlai/issues](https://github.com/axonops/cqlai/issues)
- **Discussions**: [github.com/axonops/cqlai/discussions](https://github.com/axonops/cqlai/discussions)

---

## Next Steps

- **[GitHub Repository](https://github.com/axonops/cqlai)** - Download and documentation
