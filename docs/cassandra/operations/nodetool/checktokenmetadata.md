---
description: "Verify token metadata consistency across the Cassandra cluster using nodetool checktokenmetadata."
meta:
  - name: keywords
    content: "nodetool checktokenmetadata, token metadata, Cassandra tokens, cluster consistency"
---

# nodetool checktokenmetadata

Checks the token metadata for inconsistencies.

---

## Synopsis

```bash
nodetool [connection_options] checktokenmetadata
```

## Description

`nodetool checktokenmetadata` validates the token metadata stored in the cluster for inconsistencies. This helps identify issues with token ring configuration.

---

## Examples

### Basic Usage

```bash
nodetool checktokenmetadata
```

---

## When to Use

### After Topology Changes

```bash
# After adding/removing nodes
nodetool checktokenmetadata
```

### Troubleshoot Ring Issues

```bash
# If routing seems incorrect
nodetool checktokenmetadata
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [ring](ring.md) | View token ring |
| [describering](describering.md) | Ring details |
| [status](status.md) | Cluster status |
