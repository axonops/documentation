---
title: "nodetool reloadlocalschema"
description: "Reload schema from local storage in Cassandra using nodetool reloadlocalschema."
meta:
  - name: keywords
    content: "nodetool reloadlocalschema, reload schema, local schema, Cassandra"
search:
  boost: 3
---

# nodetool reloadlocalschema

Reloads the local schema from disk.

---

## Synopsis

```bash
nodetool [connection_options] reloadlocalschema
```

## Description

`nodetool reloadlocalschema` re-reads the schema definition from the local system tables. This can help resolve schema disagreements or refresh schema after manual modifications.

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
