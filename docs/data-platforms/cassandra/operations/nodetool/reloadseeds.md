---
title: "nodetool reloadseeds"
description: "Reload seed node list from configuration using nodetool reloadseeds command."
meta:
  - name: keywords
    content: "nodetool reloadseeds, reload seeds, seed nodes, Cassandra configuration"
search:
  boost: 3
---

# nodetool reloadseeds

Reloads the seed node list from configuration.

---

## Synopsis

```bash
nodetool [connection_options] reloadseeds
```

## Description

`nodetool reloadseeds` re-reads the seed node configuration from cassandra.yaml without requiring a node restart. This allows updating the seed list at runtime.

---

## Examples

### Basic Usage

```bash
nodetool reloadseeds
```

### Update and Reload

```bash
# 1. Edit cassandra.yaml
# 2. Reload seeds
nodetool reloadseeds

# 3. Verify
nodetool getseeds
```

---

## When to Use

### Adding New Seeds

```bash
# After adding new seeds to cassandra.yaml
nodetool reloadseeds
```

### Removing Failed Seeds

```bash
# After removing failed node from seeds
nodetool reloadseeds
```

---

## Best Practices

!!! tip "Guidelines"

    1. **Edit config first** - Update cassandra.yaml before reloading
    2. **Verify after** - Check with getseeds
    3. **Cluster-wide** - Update and reload on all nodes

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [getseeds](getseeds.md) | View current seeds |
| [status](status.md) | Cluster status |
