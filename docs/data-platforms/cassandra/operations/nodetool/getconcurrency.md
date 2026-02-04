---
title: "nodetool getconcurrency"
description: "Display read/write concurrency settings in Cassandra using nodetool getconcurrency."
meta:
  - name: keywords
    content: "nodetool getconcurrency, concurrency settings, read write threads, Cassandra"
---

# nodetool getconcurrency

Displays the concurrency settings.

---

## Synopsis

```bash
nodetool [connection_options] getconcurrency [stage_name ...]
```
See [connection options](index.md#connection-options) for connection options.

## Arguments

| Argument | Description |
|----------|-------------|
| `stage_name` | Optional. One or more stage names to filter output (e.g., `READ`, `MUTATION`) |

## Description

`nodetool getconcurrency` displays the core and maximum pool sizes for Cassandra's thread stages. These stages handle various internal operations and can be filtered by name.

---

## Output Format

| Field | Description |
|-------|-------------|
| `Stage` | Thread stage name |
| `CorePoolSize` | Minimum number of threads maintained |
| `MaximumPoolSize` | Maximum threads allowed under load |

---

## Examples

### Basic Usage (All Stages)

```bash
nodetool getconcurrency
```

**Sample output:**
```
Stage                           CorePoolSize  MaximumPoolSize
READ                            32            32
MUTATION                        32            32
COUNTER_MUTATION                32            32
...
```

### Filter by Stage Name

```bash
nodetool getconcurrency READ MUTATION
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [setconcurrency](setconcurrency.md) | Modify concurrency |
| [tpstats](tpstats.md) | Thread pool statistics |