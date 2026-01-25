---
title: "nodetool getdefaultrf"
description: "Display default replication factor for keyspace validation using nodetool getdefaultrf."
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

`nodetool getdefaultrf` shows the default replication factor used for keyspace creation and validation. This setting affects guardrails that validate replication factor adequacy when creating or altering keyspaces.

---

## Output Format

The command outputs a single numeric value representing the default replication factor:

```
3
```

---

## Examples

### Basic Usage

```bash
nodetool getdefaultrf
```

**Sample output:**
```
3
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [setdefaultrf](setdefaultrf.md) | Modify default RF |
| [describecluster](describecluster.md) | Cluster information |
