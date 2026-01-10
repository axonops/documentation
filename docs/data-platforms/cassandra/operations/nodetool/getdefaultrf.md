---
title: "nodetool getdefaultrf"
description: "Display default replication factor for system keyspaces using nodetool getdefaultrf."
meta:
  - name: keywords
    content: "nodetool getdefaultrf, replication factor, default RF, Cassandra replication"
---

# nodetool getdefaultrf

!!! info "Cassandra 4.1+"
    This command is available in Cassandra 4.1 and later.

Displays the default replication factor.

---

## Synopsis

```bash
nodetool [connection_options] getdefaultrf
```

## Description

`nodetool getdefaultrf` shows the default replication factor that will be used for keyspaces when not explicitly specified.

---

## Examples

### Basic Usage

```bash
nodetool getdefaultrf
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [setdefaultrf](setdefaultrf.md) | Modify default RF |
| [describecluster](describecluster.md) | Cluster information |
