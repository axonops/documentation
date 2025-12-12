---
description: "CQLAI - AI-powered CQL shell for Apache Cassandra. Natural language queries and intelligent assistance."
meta:
  - name: keywords
    content: "CQLAI, AI CQL, Cassandra AI, natural language queries, intelligent shell"
---

# CQLAI

CQLAI is a modern, AI-powered CQL shell built by AxonOps as an alternative to `cqlsh`. It provides a rich terminal interface, zero dependencies, and optional AI-powered query generation from natural language.

---

## Overview

CQLAI addresses common pain points with the traditional `cqlsh` tool:

| Limitation of cqlsh | CQLAI Solution |
|---------------------|----------------|
| Requires Python installation | Single static binary, no dependencies |
| Slow startup (2-3 seconds) | Fast startup (~100ms) |
| Basic terminal interface | Rich TUI with mouse support |
| Limited output formats | Table, JSON, CSV, Parquet export |
| No AI assistance | Natural language to CQL conversion |
| Can OOM on large results | Memory-bounded virtualized display |

CQLAI maintains full compatibility with CQL commands while adding modern development conveniences.

---

## Key Features

### Zero Dependencies

CQLAI is distributed as a single static binary:

```bash
# Download and run - no installation required
./cqlai --host cassandra.example.com
```

Available for:
- Linux x86-64 and aarch64
- macOS x86-64 and arm64 (Apple Silicon)
- Windows x86-64

### Rich Terminal Interface

Modern terminal UI features:

| Feature | Description |
|---------|-------------|
| **Full-screen Mode** | Alternate buffer preserves terminal history |
| **Virtualized Tables** | Scrollable results for large datasets |
| **Vim Navigation** | Keyboard shortcuts for efficient navigation |
| **Mouse Support** | Click, scroll, and select with mouse |
| **Status Bar** | Connection info and query latency display |
| **Modal Overlays** | History, help, and completion panels |

### AI-Powered Query Generation

Convert natural language to CQL (optional feature):

```sql
cqlai> .ai show all users who registered in the last 30 days

Generated CQL:
  SELECT * FROM users
  WHERE created_at >= '2024-11-11'
  ALLOW FILTERING;

Execute? [Y/n]: y
```

Supported AI providers:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google Gemini
- Ollama (local models)
- OpenRouter
- Synthetic

!!! note "AI is Optional"
    CQLAI functions as a complete CQL shell without any AI configuration. The AI feature enhances productivity but is not required.

### Apache Parquet Support

Native Parquet import/export for analytics integration:

```sql
-- Export to Parquet
COPY users TO 'users.parquet';

-- Export with compression
COPY events TO 'events.parquet' WITH COMPRESSION='ZSTD';

-- Import from Parquet
COPY analytics_data FROM 'dataset.parquet';
```

Supported compression: Snappy, ZSTD, GZIP, LZ4

### Smart Auto-Completion

Context-aware completion:

```sql
SELECT * FROM us<Tab>    -- Completes table names
WHERE user_<Tab>         -- Completes column names
CONSISTENCY LOC<Tab>     -- Shows LOCAL_ONE, LOCAL_QUORUM, LOCAL_SERIAL
```

Completions include:
- CQL keywords and commands
- Keyspace and table names
- Column names (after FROM clause)
- Consistency levels
- File paths (for COPY commands)

---

## Installation

### Using Go

```bash
go install github.com/axonops/cqlai/cmd/cqlai@latest
```

### Binary Download

Download from [GitHub releases](https://github.com/axonops/cqlai/releases):

```bash
# Linux x86-64
curl -LO https://github.com/axonops/cqlai/releases/latest/download/cqlai-linux-amd64
chmod +x cqlai-linux-amd64
mv cqlai-linux-amd64 /usr/local/bin/cqlai

# macOS arm64 (Apple Silicon)
curl -LO https://github.com/axonops/cqlai/releases/latest/download/cqlai-darwin-arm64
chmod +x cqlai-darwin-arm64
mv cqlai-darwin-arm64 /usr/local/bin/cqlai
```

### Verify Installation

```bash
cqlai --version
```

---

## Connecting to Cassandra

### Basic Connection

```bash
# Connect to localhost
cqlai

# Connect to specific host
cqlai --host 192.168.1.100

# Connect to specific host and port
cqlai --host cassandra.example.com --port 9042
```

### With Authentication

```bash
# Username with password prompt
cqlai --host cassandra.example.com -u myuser
Password: [hidden]

# Username and password (not recommended for production)
cqlai --host cassandra.example.com -u myuser -p mypassword
```

### With Keyspace

```bash
# Connect directly to a keyspace
cqlai --host cassandra.example.com -k my_keyspace
```

### With SSL/TLS

```bash
# Enable SSL
cqlai --host cassandra.example.com --ssl

# With certificate verification
cqlai --host cassandra.example.com --ssl --ssl-ca /path/to/ca.crt
```

### Connection String

```bash
# Full connection specification
cqlai --host node1.example.com,node2.example.com --port 9042 -u admin -k production
```

---

## Usage

### Running Queries

Standard CQL commands work as expected:

```sql
cqlai> USE my_keyspace;
cqlai> SELECT * FROM users LIMIT 10;
cqlai> DESCRIBE TABLES;
cqlai> CONSISTENCY QUORUM;
```

### Output Modes

Switch output formats:

```sql
-- Table format (default)
cqlai> SELECT * FROM users;

-- JSON output
cqlai> .json
cqlai> SELECT * FROM users;

-- CSV output
cqlai> .csv
cqlai> SELECT * FROM users;

-- Return to table format
cqlai> .table
```

### Data Export

Export query results or entire tables:

```sql
-- Export to CSV
COPY users TO 'users.csv';

-- Export to JSON
COPY users TO 'users.json' WITH FORMAT='JSON';

-- Export to Parquet with compression
COPY users TO 'users.parquet' WITH COMPRESSION='SNAPPY';

-- Export query results
COPY (SELECT * FROM users WHERE active = true) TO 'active_users.csv';
```

### Data Import

Import data from files:

```sql
-- Import from CSV
COPY users FROM 'users.csv';

-- Import from Parquet
COPY users FROM 'users.parquet';

-- Import with options
COPY users FROM 'users.csv' WITH HEADER=true AND DELIMITER='|';
```

### AI Query Generation

Use natural language to generate CQL:

```sql
-- Generate SELECT query
cqlai> .ai find all orders placed today with total over 100

-- Generate schema
cqlai> .ai create a table for storing user sessions with TTL

-- Generate aggregation
cqlai> .ai count users grouped by country

-- Explain query
cqlai> .ai explain what this table structure means
```

The AI considers the current schema context when generating queries.

### Keyboard Navigation

| Key | Action |
|-----|--------|
| `↑` / `↓` | Navigate history / scroll results |
| `Ctrl+R` | Search command history |
| `Tab` | Auto-complete |
| `Ctrl+C` | Cancel current query |
| `Ctrl+D` | Exit CQLAI |
| `Ctrl+L` | Clear screen |
| `?` or `F1` | Show help |

### Vim-Style Navigation (in results)

| Key | Action |
|-----|--------|
| `j` / `k` | Scroll down / up |
| `h` / `l` | Scroll left / right |
| `g` / `G` | Go to top / bottom |
| `q` | Close results view |

---

## Configuration

### Configuration File

Create `~/.cqlai/config.yaml`:

```yaml
# Default connection settings
host: cassandra.example.com
port: 9042
username: myuser
keyspace: my_keyspace

# SSL settings
ssl:
  enabled: true
  ca_cert: /path/to/ca.crt

# AI configuration (optional)
ai:
  provider: openai
  api_key: sk-...
  model: gpt-4

# Display settings
display:
  format: table
  max_rows: 1000
  timezone: UTC
```

### Environment Variables

```bash
# Connection
export CQLAI_HOST=cassandra.example.com
export CQLAI_PORT=9042
export CQLAI_USERNAME=myuser
export CQLAI_PASSWORD=mypassword
export CQLAI_KEYSPACE=my_keyspace

# AI (optional)
export CQLAI_AI_PROVIDER=openai
export OPENAI_API_KEY=sk-...
```

### AI Provider Configuration

#### OpenAI

```yaml
ai:
  provider: openai
  api_key: sk-your-api-key
  model: gpt-4  # or gpt-3.5-turbo
```

#### Anthropic

```yaml
ai:
  provider: anthropic
  api_key: sk-ant-your-api-key
  model: claude-3-sonnet-20240229
```

#### Ollama (Local)

```yaml
ai:
  provider: ollama
  endpoint: http://localhost:11434
  model: llama2
```

---

## Comparison with cqlsh

### Feature Comparison

| Feature | cqlsh | CQLAI |
|---------|-------|-------|
| **Dependencies** | Python 2.7/3.x + cassandra-driver | None |
| **Startup Time** | ~2-3 seconds | ~100ms |
| **Terminal UI** | Basic readline | Rich TUI |
| **Mouse Support** | No | Yes |
| **Output Formats** | Text, JSON | Table, JSON, CSV, Parquet |
| **AI Assistance** | No | Yes (optional) |
| **Large Results** | May OOM | Memory-bounded |
| **Parquet** | No | Native support |
| **Tab Completion** | Basic | Context-aware |

### Command Compatibility

CQLAI supports all standard CQL commands:

- All DDL: `CREATE`, `ALTER`, `DROP`, `TRUNCATE`
- All DML: `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `BATCH`
- Meta-commands: `DESCRIBE`, `SHOW`, `USE`, `CONSISTENCY`, `TRACING`
- Data commands: `COPY TO`, `COPY FROM`
- Authentication: `LOGIN`

### Migration from cqlsh

Replace `cqlsh` commands directly:

```bash
# Before (cqlsh)
cqlsh 192.168.1.100 -u admin -k my_keyspace

# After (CQLAI)
cqlai --host 192.168.1.100 -u admin -k my_keyspace
```

Scripts using `cqlsh -e` work with CQLAI:

```bash
# Execute single command
cqlai --host localhost -e "SELECT * FROM users LIMIT 5"

# Execute from file
cqlai --host localhost -f queries.cql
```

---

## Use Cases

### Development Workflow

Quick query testing during development:

```bash
# Connect to dev cluster
cqlai --host localhost -k dev_keyspace

# Test queries
cqlai> SELECT * FROM users WHERE user_id = ?;
cqlai> .ai show me the schema for the orders table
```

### Data Investigation

Explore production data (with read-only user):

```bash
cqlai --host prod-cassandra -u readonly -k production

# Investigate issue
cqlai> .ai find orders from yesterday that are still pending
cqlai> SELECT * FROM orders WHERE status = 'pending' AND created_at > '2024-01-10' ALLOW FILTERING;
```

### Data Migration

Export and transform data:

```bash
# Export to Parquet for analytics
cqlai> COPY events TO 'events.parquet' WITH COMPRESSION='ZSTD';

# Export specific data
cqlai> COPY (SELECT user_id, email FROM users WHERE active = true) TO 'active_users.csv';
```

### Schema Documentation

Generate schema documentation:

```bash
cqlai --host localhost -e "DESCRIBE KEYSPACE my_keyspace" > schema.cql
```

---

## Troubleshooting

### Connection Issues

**Cannot connect:**

```bash
# Verify connectivity
nc -zv cassandra.example.com 9042

# Check with verbose output
cqlai --host cassandra.example.com --debug
```

**Authentication failure:**

```bash
# Verify credentials work with cqlsh first
cqlsh cassandra.example.com -u myuser

# Then try CQLAI
cqlai --host cassandra.example.com -u myuser
```

### AI Not Working

**No response from AI:**

1. Verify API key is set correctly
2. Check network connectivity to AI provider
3. Confirm model name is valid

```bash
# Test AI configuration
cqlai> .ai-status
```

### Performance Issues

**Slow queries:**

- Add `LIMIT` to unbounded queries
- Use appropriate consistency level
- Check cluster health

**Memory issues:**

CQLAI limits result set memory. For very large exports:

```sql
-- Use COPY for large data transfers
COPY large_table TO 'output.parquet';
```

---

## Resources

- **GitHub Repository**: [github.com/axonops/cqlai](https://github.com/axonops/cqlai)
- **Releases**: [github.com/axonops/cqlai/releases](https://github.com/axonops/cqlai/releases)
- **Issues**: [github.com/axonops/cqlai/issues](https://github.com/axonops/cqlai/issues)
- **Documentation**: [CQLAI Tools Section](../tools/cqlai/index.md)

---

## Related Documentation

| Topic | Description |
|-------|-------------|
| [AxonOps Workbench](workbench.md) | GUI-based Cassandra development tool |
| [cqlsh](../tools/cqlsh/index.md) | Standard CQL shell |
| [CQL Reference](../cql/index.md) | CQL syntax and commands |
| [Drivers](drivers/index.md) | Application driver configuration |
