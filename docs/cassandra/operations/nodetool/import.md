# nodetool import

Imports SSTables from an external directory into a table.

---

## Synopsis

```bash
nodetool [connection_options] import [options] <keyspace> <table> <directory>
```

## Description

`nodetool import` loads SSTables from an external directory into a Cassandra table. Unlike `refresh`, which requires files to be in the data directory, `import` can load from any location and optionally moves or copies files.

Available in Cassandra 4.0+.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | Target keyspace |
| `table` | Target table |
| `directory` | Directory containing SSTables to import |

---

## Options

| Option | Description |
|--------|-------------|
| `-c, --no-verify` | Skip SSTable verification |
| `-e, --extended-verify` | Extended verification of SSTables |
| `-k, --keep-level` | Keep original SSTable level (for LCS) |
| `-l, --keep-repaired` | Keep repaired status |
| `-q, --quick` | Quick import (less verification) |
| `-r, --no-invalidate-caches` | Don't invalidate caches |
| `-v, --no-verify-tokens` | Skip token verification |
| `-p, --copy-data` | Copy files instead of moving |

---

## Examples

### Basic Import

```bash
nodetool import my_keyspace my_table /path/to/sstables/
```

### Import with Copy (Keep Original)

```bash
nodetool import -p my_keyspace my_table /backup/sstables/
```

### Quick Import (Less Verification)

```bash
nodetool import -q my_keyspace my_table /path/to/sstables/
```

### Import Keeping LCS Levels

```bash
nodetool import -k my_keyspace my_table /path/to/sstables/
```

### Extended Verification Import

```bash
nodetool import -e my_keyspace my_table /path/to/sstables/
```

---

## Import vs Refresh vs SSTableLoader

| Feature | import | refresh | sstableloader |
|---------|--------|---------|---------------|
| External directory | Yes | No | Yes |
| Move/copy files | Yes | No | Streams |
| Token verification | Optional | No | Yes |
| Different topology | No | No | Yes |
| Cassandra version | 4.0+ | 3.x+ | All |
| Speed | Fast | Fast | Slower |

---

## Workflow: Restore from Backup

```bash
# 1. Extract backup to a directory
tar -xzf backup.tar.gz -C /tmp/restore/

# 2. Import SSTables
nodetool import my_keyspace my_table /tmp/restore/my_keyspace/my_table/

# 3. Verify
nodetool tablestats my_keyspace.my_table
```

---

## Workflow: Bulk Load

```bash
# 1. Generate SSTables externally (e.g., from Spark)
# Files are in /data/generated/my_keyspace/my_table/

# 2. Import to each node
nodetool import my_keyspace my_table /data/generated/my_keyspace/my_table/

# 3. Repair for consistency
nodetool repair my_keyspace my_table
```

---

## Directory Requirements

The source directory should contain SSTable files:

```
/path/to/sstables/
├── nb-1-big-Data.db
├── nb-1-big-Index.db
├── nb-1-big-Filter.db
├── nb-1-big-Statistics.db
├── nb-1-big-Summary.db
├── nb-1-big-TOC.txt
└── nb-1-big-CompressionInfo.db
```

---

## Token Verification

By default, import verifies tokens belong to this node:

```bash
# Normal import (verifies tokens)
nodetool import my_keyspace my_table /path/

# Skip token verification (use carefully)
nodetool import -v my_keyspace my_table /path/
```

!!! warning "Token Verification"
    Skipping token verification (`-v`) may import data that doesn't belong to this node. Only use when certain about data placement.

---

## File Handling

### Default (Move)

By default, files are moved from source to data directory:

```bash
nodetool import my_keyspace my_table /tmp/sstables/
# Files moved from /tmp/sstables/ to data directory
# Source directory will be empty after import
```

### Copy Mode

Use `-p` to copy instead of move:

```bash
nodetool import -p my_keyspace my_table /backup/sstables/
# Files copied, originals remain in /backup/sstables/
```

---

## Common Issues

### Permission Denied

```bash
# Ensure Cassandra can read source directory
chmod -R 755 /path/to/sstables/
chown -R cassandra:cassandra /path/to/sstables/
```

### Invalid SSTable

```
ERROR: SSTable is not valid
```

Try with verification options:

```bash
# Extended verification to see details
nodetool import -e my_keyspace my_table /path/

# Or skip verification (risky)
nodetool import -c my_keyspace my_table /path/
```

### Token Range Mismatch

```
ERROR: Token ... is not owned by this node
```

Either:
- Import to the correct node
- Use `-v` to skip verification (if certain data is correct)
- Use `sstableloader` for different topologies

---

## Post-Import Steps

```bash
# 1. Verify import
nodetool tablestats my_keyspace.my_table

# 2. Check data is queryable
cqlsh -e "SELECT COUNT(*) FROM my_keyspace.my_table;"

# 3. Run repair for consistency (recommended for bulk loads)
nodetool repair -pr my_keyspace my_table
```

---

## Best Practices

!!! tip "Import Guidelines"
    1. **Use copy mode for backups** - Keep original files with `-p`
    2. **Verify first** - Use extended verification for critical data
    3. **Check token ownership** - Ensure SSTables belong to this node
    4. **Run repair after** - Ensure consistency across replicas
    5. **Monitor space** - Ensure sufficient disk for imported data

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [refresh](refresh.md) | Load SSTables from data directory |
| [snapshot](snapshot.md) | Create backups |
| [tablestats](tablestats.md) | Verify after import |
| [repair](repair.md) | Run after bulk imports |
