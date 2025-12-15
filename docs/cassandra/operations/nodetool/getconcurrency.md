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
nodetool [connection_options] getconcurrency
```

## Description

`nodetool getconcurrency` shows the current concurrency settings for various operations including reads, writes, and counter writes.

---

## Examples

### Basic Usage

```bash
nodetool getconcurrency
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [setconcurrency](setconcurrency.md) | Modify concurrency |
| [tpstats](tpstats.md) | Thread pool statistics |
