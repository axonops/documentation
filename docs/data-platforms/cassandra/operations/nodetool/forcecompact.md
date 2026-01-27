---
title: "nodetool forcecompact"
description: "Force compaction on specific SSTables in Cassandra using nodetool forcecompact command."
meta:
  - name: keywords
    content: "nodetool forcecompact, force compaction, Cassandra compaction, SSTable"
---

# nodetool forcecompact

!!! info "Cassandra 5.0+"
    This command is available in Cassandra 5.0 and later.

Forces compaction of SSTables containing specified partition keys, ignoring `gc_grace_seconds`.

---

## Synopsis

```bash
nodetool [connection_options] forcecompact <keyspace> <table> <keys>...
```

## Description

`nodetool forcecompact` forces compaction of SSTables containing the specified partition keys. Unlike regular compaction, this command ignores `gc_grace_seconds` when purging tombstones, allowing immediate removal of deleted data for specific partitions.

!!! warning "Use With Caution"
    This command ignores `gc_grace_seconds`, which means tombstones may be removed before they have propagated to all replicas. Use only when you are certain all replicas have seen the deletions, or after running repair.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | Target keyspace |
| `table` | Target table |
| `keys` | Partition keys to force compact |

---

## Examples

### Force Compact Specific Partition Keys

```bash
nodetool forcecompact my_keyspace my_table user123 user456
```

---

## When to Use

### Remove Tombstones Immediately

```bash
# After ensuring all replicas have seen deletions
nodetool repair my_keyspace my_table

# Force compact specific partitions to remove tombstones
nodetool forcecompact my_keyspace my_table partition_key_value
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [compact](compact.md) | General compaction |
| [compactionstats](compactionstats.md) | View compaction status |
| [getsstables](getsstables.md) | List SSTables for key |