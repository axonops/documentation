---
title: "CQLAI"
description: "CQLAI - AI-powered CQL shell for Apache Cassandra. Natural language queries and intelligent assistance."
meta:
  - name: keywords
    content: "CQLAI, AI CQL, Cassandra AI, natural language queries, intelligent shell"
---

# CQLAI

CQLAI is a modern, AI-powered CQL shell built by AxonOps as an alternative to `cqlsh`. It provides a rich terminal interface, zero dependencies, and optional AI-powered query generation from natural language.

---

## Why CQLAI for Development?

| cqlsh Limitation | CQLAI Solution |
|------------------|----------------|
| Requires Python installation | Single static binary, no dependencies |
| Slow startup (2-3 seconds) | Fast startup (~100ms) |
| Basic terminal interface | Rich TUI with mouse support |
| Limited output formats | Table, JSON, CSV, Parquet export |
| No AI assistance | Natural language to CQL conversion |
| Can OOM on large results | Memory-bounded virtualized display |

---

## Key Features

- **Zero Dependencies** — Single binary for Linux, macOS, Windows
- **Rich Terminal UI** — Full-screen mode, vim navigation, mouse support
- **AI Query Generation** — Convert natural language to CQL (optional)
- **Apache Parquet Support** — Native import/export for analytics integration
- **Smart Auto-Completion** — Context-aware completion for tables, columns, keywords

---

## Quick Example

```bash
# Connect to Cassandra
cqlai --host cassandra.example.com -u myuser -k my_keyspace

# Run standard CQL
cqlai> SELECT * FROM users LIMIT 10;

# Use AI to generate queries
cqlai> .ai find all orders placed today with total over 100

# Export to Parquet
cqlai> COPY users TO 'users.parquet' WITH COMPRESSION='ZSTD';
```

---

## Full Documentation

For complete documentation including installation, configuration, and all features, see the **[CQLAI Tools Reference](../tools/cqlai/index.md)**.

| Section | Description |
|---------|-------------|
| [Installation](../tools/cqlai/installation/index.md) | APT, YUM, binary download, Docker, build from source |
| [Getting Started](../tools/cqlai/getting-started/index.md) | Connection options, authentication, SSL/TLS |
| [Configuration](../tools/cqlai/configuration/index.md) | Config files, environment variables, options |
| [AI Features](../tools/cqlai/ai-features/index.md) | AI providers, natural language queries |
| [Data Import/Export](../tools/cqlai/data-import-export/index.md) | CSV, Parquet, COPY commands |
| [Commands](../tools/cqlai/commands/index.md) | All supported commands |
| [Troubleshooting](../tools/cqlai/troubleshooting.md) | Common issues and solutions |

---

## Resources

- **GitHub Repository**: [github.com/axonops/cqlai](https://github.com/axonops/cqlai)
- **Releases**: [github.com/axonops/cqlai/releases](https://github.com/axonops/cqlai/releases)

---

## Related Documentation

| Topic | Description |
|-------|-------------|
| [AxonOps Workbench](workbench.md) | GUI-based Cassandra development tool |
| [cqlsh](../tools/cqlsh/index.md) | Standard CQL shell |
| [CQL Reference](../cql/index.md) | CQL syntax and commands |
| [Drivers](drivers/index.md) | Application driver configuration |