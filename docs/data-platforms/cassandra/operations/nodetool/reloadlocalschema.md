---
title: "nodetool reloadlocalschema"
description: "Reload schema from local storage in Cassandra using nodetool reloadlocalschema."
meta:
  - name: keywords
    content: "nodetool reloadlocalschema, reload schema, local schema, Cassandra"
---

# nodetool reloadlocalschema

Reloads the local schema from disk.

---

## Synopsis

```bash
nodetool [connection_options] reloadlocalschema
```
See [connection options](index.md#connection-options) for connection options.

## Description

`nodetool reloadlocalschema` re-reads the schema definition from the local system tables. This can help resolve schema disagreements.

!!! warning "Do Not Manually Modify Schema Tables"
    Direct modifications to schema system tables (`system_schema.*`) are unsupported and can corrupt the schema. Always use CQL DDL statements (CREATE, ALTER, DROP) to modify schema. The `reloadlocalschema` command is intended for recovery scenarios, not for applying manual edits.

---

## Examples

### Basic Usage

```bash
nodetool reloadlocalschema
```

---

## When to Use

### Schema Disagreement

```bash
# Check for schema disagreement
nodetool describecluster | grep -A 5 "Schema versions"

# If disagreement exists, try reloading
nodetool reloadlocalschema
```

### After Schema Recovery

```bash
# After restoring schema from backup
nodetool reloadlocalschema
```

---

## Troubleshooting

### Persistent Schema Issues

```bash
# 1. Check schema versions
nodetool describecluster

# 2. Reload local schema
nodetool reloadlocalschema

# 3. If issues persist, consider resetlocalschema
nodetool resetlocalschema
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [resetlocalschema](resetlocalschema.md) | Reset schema from cluster |
| [describecluster](describecluster.md) | View schema versions |