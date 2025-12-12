# nodetool getdefaultrf

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
