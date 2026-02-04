---
title: "nodetool resetlocalschema"
description: "Reset local schema to match cluster using nodetool resetlocalschema command."
meta:
  - name: keywords
    content: "nodetool resetlocalschema, reset schema, schema sync, Cassandra"
---

# nodetool resetlocalschema

Resets the local schema by fetching it from another node.

---

## Synopsis

```bash
nodetool [connection_options] resetlocalschema
```
See [connection options](index.md#connection-options) for connection options.

## Description

`nodetool resetlocalschema` discards the local schema and fetches a fresh copy from another node in the cluster. This is useful for resolving schema disagreements when a node has incorrect or corrupted schema.

!!! warning "Destructive Operation"
    This discards the local schema entirely. Ensure other nodes have the correct schema before running.

---

## Examples

### Basic Usage

```bash
nodetool resetlocalschema
```

---

## When to Use

### Persistent Schema Disagreement

```bash
# Check schema versions
nodetool describecluster | grep -A 5 "Schema versions"

# If this node has unique/wrong schema
nodetool resetlocalschema
```

### After Failed Schema Migration

```bash
# If schema migration left node in bad state
nodetool resetlocalschema
```

---

## Process Flow

```
1. Local schema tables are truncated
2. Schema is fetched from another node
3. Local schema is rebuilt
4. Node should match cluster schema
```

---

## Best Practices

!!! tip "Guidelines"

    1. **Verify cluster schema** - Ensure other nodes are correct
    2. **Last resort** - Try reloadlocalschema first
    3. **Monitor after** - Verify schema agreement

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [reloadlocalschema](reloadlocalschema.md) | Reload local schema |
| [describecluster](describecluster.md) | View schema versions |