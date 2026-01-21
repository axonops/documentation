---
title: "Getting Started with CQLAI"
description: "Getting started with CQLAI. Quick setup and first queries."
meta:
  - name: keywords
    content: "CQLAI getting started, quick start, first queries"
search:
  boost: 3
---

# Getting Started with CQLAI

CQLAI is a modern, AI-powered CQL shell for Apache Cassandra that enhances productivity with intelligent query suggestions, data analysis, and seamless import/export capabilities.

## What is CQLAI?

CQLAI is a next-generation command-line interface for Cassandra that combines:
- **Modern CQL Shell** - Fast, feature-rich alternative to cqlsh
- **AI Assistance** - Natural language to CQL translation
- **Data Tools** - Easy import/export with multiple formats
- **Enhanced UX** - Syntax highlighting, auto-completion, query history

## Installation

### Download Binary

```bash
# Linux (AMD64)
curl -L https://github.com/axonops/cqlai/releases/latest/download/cqlai-linux-amd64 -o cqlai
chmod +x cqlai
sudo mv cqlai /usr/local/bin/

# Linux (ARM64)
curl -L https://github.com/axonops/cqlai/releases/latest/download/cqlai-linux-arm64 -o cqlai
chmod +x cqlai
sudo mv cqlai /usr/local/bin/

# macOS (Intel)
curl -L https://github.com/axonops/cqlai/releases/latest/download/cqlai-darwin-amd64 -o cqlai
chmod +x cqlai
sudo mv cqlai /usr/local/bin/

# macOS (Apple Silicon)
curl -L https://github.com/axonops/cqlai/releases/latest/download/cqlai-darwin-arm64 -o cqlai
chmod +x cqlai
sudo mv cqlai /usr/local/bin/
```

### Using Homebrew (macOS)

```bash
brew install axonops/tap/cqlai
```

### Verify Installation

```bash
cqlai --version
```

## Quick Start

### Connect to Cassandra

```bash
# Local connection (default: localhost:9042)
cqlai

# Specify host and port
cqlai -h 192.168.1.10 -p 9042

# With authentication
cqlai -h 192.168.1.10 -u cassandra -P cassandra

# Connect to specific keyspace
cqlai -h 192.168.1.10 -k my_keyspace
```

### Basic Commands

```sql
-- List keyspaces
DESCRIBE KEYSPACES;

-- Use a keyspace
USE my_keyspace;

-- List tables
DESCRIBE TABLES;

-- Run a query
SELECT * FROM users LIMIT 10;

-- Exit
EXIT;
```

## AI Features

### Natural Language Queries

```bash
# Enable AI mode with provider
cqlai --ai-provider openai --ai-key YOUR_API_KEY

# Or set environment variable
export CQLAI_AI_PROVIDER=openai
export CQLAI_AI_KEY=YOUR_API_KEY
cqlai
```

### Ask AI

```
cqlai> .ai show me all users who signed up last month

Generated CQL:
SELECT * FROM users
WHERE created_at >= '2024-11-01' AND created_at < '2024-12-01'
ALLOW FILTERING;

Execute? [Y/n]:
```

### Schema Suggestions

```
cqlai> .ai suggest a schema for storing IoT sensor data

Suggested schema:
CREATE TABLE sensor_readings (
    sensor_id text,
    bucket text,
    reading_time timestamp,
    temperature double,
    humidity double,
    PRIMARY KEY ((sensor_id, bucket), reading_time)
) WITH CLUSTERING ORDER BY (reading_time DESC);

Explanation:
- Partition by sensor_id and time bucket for even distribution
- Cluster by time for efficient range queries
- Descending order for latest-first queries
```

## Data Import/Export

### Export Data

```bash
# Export to CSV
cqlai> .export users /tmp/users.csv

# Export to JSON
cqlai> .export users /tmp/users.json --format json

# Export query results
cqlai> .export "SELECT * FROM orders WHERE status = 'pending'" /tmp/pending.csv
```

### Import Data

```bash
# Import from CSV
cqlai> .import /tmp/users.csv users

# Import from JSON
cqlai> .import /tmp/users.json users --format json

# Preview before import
cqlai> .import /tmp/users.csv users --preview
```

## Configuration

### Configuration File

```yaml
# ~/.cqlai/config.yaml
connection:
  host: localhost
  port: 9042
  username: cassandra
  keyspace: default_ks

ai:
  provider: openai
  model: gpt-4
  # key loaded from CQLAI_AI_KEY environment variable

display:
  page_size: 100
  color: true
  format: table
```

### Environment Variables

```bash
# Connection
export CQLAI_HOST=192.168.1.10
export CQLAI_PORT=9042
export CQLAI_USERNAME=cassandra
export CQLAI_PASSWORD=secret

# AI
export CQLAI_AI_PROVIDER=openai
export CQLAI_AI_KEY=sk-...
export CQLAI_AI_MODEL=gpt-4
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Tab` | Auto-complete |
| `Ctrl+R` | Search history |
| `Ctrl+C` | Cancel query |
| `Ctrl+D` | Exit |
| `Up/Down` | Navigate history |

## Command Reference

| Command | Description |
|---------|-------------|
| `.help` | Show help |
| `.ai <prompt>` | AI natural language query |
| `.export <table> <file>` | Export data |
| `.import <file> <table>` | Import data |
| `.desc <table>` | Describe table |
| `.clear` | Clear screen |
| `.history` | Show command history |
| `.settings` | Show current settings |

---

## Next Steps

- **[Features](../features/index.md)** - Full feature reference
- **[AI Features](../ai-features/index.md)** - AI capabilities
- **[Data Import/Export](../data-import-export/index.md)** - Data migration
- **[Configuration](../configuration/index.md)** - Advanced configuration
