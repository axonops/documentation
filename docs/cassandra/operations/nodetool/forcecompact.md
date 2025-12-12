# nodetool forcecompact

Forces compaction of specified SSTables.

---

## Synopsis

```bash
nodetool [connection_options] forcecompact <keyspace> <table> <sstable_files>...
```

## Description

`nodetool forcecompact` forces compaction of specific SSTable files. Unlike `compact` which compacts based on strategy, this command allows targeting specific files.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | Target keyspace |
| `table` | Target table |
| `sstable_files` | SSTable file paths to compact |

---

## Examples

### Force Compact Specific SSTables

```bash
nodetool forcecompact my_keyspace my_table /path/to/sstable1 /path/to/sstable2
```

---

## When to Use

### Target Specific Files

```bash
# Compact specific problematic SSTables
nodetool forcecompact my_keyspace my_table /var/lib/cassandra/data/my_keyspace/my_table-xxx/mc-1-big-Data.db
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [compact](compact.md) | General compaction |
| [compactionstats](compactionstats.md) | View compaction status |
| [getsstables](getsstables.md) | List SSTables for key |
