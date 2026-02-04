---
title: "nodetool getconcurrentviewbuilders"
description: "Display concurrent view builder threads in Cassandra using nodetool getconcurrentviewbuilders."
meta:
  - name: keywords
    content: "nodetool getconcurrentviewbuilders, view builders, materialized views, Cassandra"
---

# nodetool getconcurrentviewbuilders

Displays the number of concurrent view builders.

---

## Synopsis

```bash
nodetool [connection_options] getconcurrentviewbuilders
```
See [connection options](index.md#connection-options) for connection options.

## Description

`nodetool getconcurrentviewbuilders` shows the current number of threads available for building materialized views concurrently.

---

## Examples

### Basic Usage

```bash
nodetool getconcurrentviewbuilders
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [setconcurrentviewbuilders](setconcurrentviewbuilders.md) | Modify builders |
| [viewbuildstatus](viewbuildstatus.md) | View build status |