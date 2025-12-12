# CQLAI Quickstart

Get started with CQLAI in under 5 minutes.

---

## Installation

### macOS

```bash
# Using Homebrew
brew install axonops/tap/cqlai

# Or download directly
curl -L https://github.com/axonops/cqlai/releases/latest/download/cqlai-darwin-arm64 -o cqlai
chmod +x cqlai
sudo mv cqlai /usr/local/bin/
```

### Linux

```bash
curl -L https://github.com/axonops/cqlai/releases/latest/download/cqlai-linux-amd64 -o cqlai
chmod +x cqlai
sudo mv cqlai /usr/local/bin/
```

### Verify Installation

```bash
cqlai --version
```

---

## Connect to Cassandra

### Local Cassandra

```bash
cqlai
```

### Remote Cassandra

```bash
cqlai --host cassandra.example.com
```

### With Authentication

```bash
cqlai --host cassandra.example.com --username myuser --password mypassword
```

### With SSL

```bash
cqlai --host cassandra.example.com --ssl
```

---

## Basic Usage

### Execute CQL Queries

```sql
cqlai> USE my_keyspace;
cqlai:my_keyspace> SELECT * FROM users LIMIT 10;
```

### View Schema

```sql
-- List keyspaces
cqlai> DESCRIBE KEYSPACES;

-- Describe a table
cqlai> DESCRIBE TABLE my_keyspace.users;

-- Quick schema view
cqlai> .schema
```

### Useful Commands

| Command | Description |
|---------|-------------|
| `.help` | Show available commands |
| `.schema` | Show current schema |
| `.tables` | List tables in current keyspace |
| `.clear` | Clear the screen |
| `.exit` | Exit CQLAI |

---

## AI Query Generation (Optional)

Generate CQL queries from natural language descriptions.

### Setup (Choose One Provider)

```bash
# OpenAI
export OPENAI_API_KEY=sk-...

# Anthropic Claude
export ANTHROPIC_API_KEY=sk-ant-...

# Local Ollama (no API key needed)
ollama serve
```

### Generate Queries

```sql
cqlai> .ai show all users who signed up this week

Generated CQL:
  SELECT * FROM users
  WHERE created_at >= '2024-01-08'
  ALLOW FILTERING;

Execute? [Y/n]: y
```

---

## Export Data

### To CSV

```sql
cqlai> .export csv users.csv SELECT * FROM users;
```

### To Parquet

```sql
cqlai> .export parquet users.parquet SELECT * FROM users;
```

### To JSON

```sql
cqlai> .export json users.json SELECT * FROM users;
```

---

## Configuration File

Create `~/.cqlai/config.yaml` for persistent settings:

```yaml
connection:
  host: cassandra.example.com
  port: 9042
  username: myuser
  ssl: true

ai:
  provider: openai
  model: gpt-4
```

---

## Next Steps

- [Full Installation Guide](installation/index.md) - Detailed installation options
- [Configuration](configuration/index.md) - All configuration options
- [AI Features](ai-features/index.md) - AI provider setup and usage
- [Commands Reference](commands/index.md) - Complete command reference
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
