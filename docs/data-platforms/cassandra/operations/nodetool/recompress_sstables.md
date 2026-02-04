---
title: "nodetool recompress_sstables"
description: "Recompress SSTables with a new compression algorithm using nodetool recompress_sstables."
meta:
  - name: keywords
    content: "nodetool recompress_sstables, recompress, SSTable compression, Cassandra"
---

# nodetool recompress_sstables

!!! info "Cassandra 4.1+"
    This command is available in Cassandra 4.1 and later.

Recompresses SSTables with current compression settings.

---

## Synopsis

```bash
nodetool [connection_options] recompress_sstables [options] [keyspace] [tables...]
```
See [connection options](index.md#connection-options) for connection options.

## Description

`nodetool recompress_sstables` rewrites SSTables using the current compression configuration. Use this after changing a table's compression settings to apply them to existing data.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | Target keyspace (optional; if omitted, recompresses all keyspaces) |
| `tables` | Optional: specific tables |

## Options

| Option | Description |
|--------|-------------|
| `-j, --jobs` | Number of parallel jobs |

---

## Examples

### Recompress All Tables

```bash
nodetool recompress_sstables my_keyspace
```

### Recompress Specific Table

```bash
nodetool recompress_sstables my_keyspace my_table
```

### Parallel Recompression

```bash
nodetool recompress_sstables --jobs 2 my_keyspace
```

---

## When to Use

### After Changing Compression

```bash
# After ALTER TABLE ... WITH compression = ...
nodetool recompress_sstables my_keyspace my_table
```

### Switch Compression Algorithm

```bash
# Changed from LZ4 to Zstd
nodetool recompress_sstables my_keyspace my_table
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [upgradesstables](upgradesstables.md) | Upgrade SSTable format |
| [compact](compact.md) | Force compaction |