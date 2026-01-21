---
title: "nodetool refresh"
description: "Load newly added SSTables without restart using nodetool refresh command."
meta:
  - name: keywords
    content: "nodetool refresh, load SSTables, hot loading, Cassandra"
search:
  boost: 3
---

# nodetool refresh

Loads newly placed SSTables into a running node without restart.

---

## Synopsis

```bash
nodetool [connection_options] refresh <keyspace> <table>
```

## Description

`nodetool refresh` scans a table's data directory for new SSTable files and loads them into the running Cassandra process. This is useful for bulk loading data or restoring from backups without restarting the node.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | The keyspace containing the table |
| `table` | The table to refresh |

---

## When to Use

### Bulk Loading Data

After copying SSTables from another source:

```bash
# 1. Copy SSTables to data directory
cp /backup/nb-*.db /var/lib/cassandra/data/my_keyspace/my_table-uuid/

# 2. Load them into Cassandra
nodetool refresh my_keyspace my_table
```

### Restore from Backup

```bash
# 1. Copy snapshot files
cp /snapshots/backup_name/*.db /var/lib/cassandra/data/my_keyspace/my_table-uuid/

# 2. Refresh to load
nodetool refresh my_keyspace my_table
```

### SSTableLoader Alternative

For loading SSTables generated on the same cluster topology:

```bash
# Simpler than sstableloader when topology matches
nodetool refresh my_keyspace my_table
```

---

## Examples

### Refresh Single Table

```bash
nodetool refresh my_keyspace my_table
```

### Bulk Load Workflow

```bash
#!/bin/bash
# bulk_load.sh

KEYSPACE="my_keyspace"
TABLE="my_table"
DATA_DIR="/var/lib/cassandra/data/$KEYSPACE"
TABLE_DIR=$(ls -d $DATA_DIR/${TABLE}-* 2>/dev/null | head -1)

# Copy SSTables
cp /source/sstables/*.db "$TABLE_DIR/"
cp /source/sstables/*.txt "$TABLE_DIR/"

# Load into Cassandra
nodetool refresh $KEYSPACE $TABLE

echo "Loaded SSTables into $KEYSPACE.$TABLE"
```

---

## Prerequisites

### SSTable Compatibility

!!! warning "Version Match Required"
    SSTables must be compatible with the running Cassandra version:

    - Same or older SSTable format version
    - If older, consider running `upgradesstables` after refresh

### File Location

SSTables must be placed in the correct data directory:

```
/var/lib/cassandra/data/<keyspace>/<table>-<uuid>/
```

### Required Files

A complete SSTable includes multiple files:

```
nb-1-big-Data.db
nb-1-big-Index.db
nb-1-big-Filter.db
nb-1-big-Statistics.db
nb-1-big-Summary.db
nb-1-big-TOC.txt
nb-1-big-CompressionInfo.db  # If compressed
```

All files for an SSTable must be present.

---

## Process Flow

1. Cassandra scans the table directory for new SSTables
2. Validates SSTable format and compatibility
3. Loads SSTable metadata into memory
4. Makes data available for queries
5. SSTables become part of normal compaction cycle

---

## Refresh vs Import

| Aspect | refresh | import |
|--------|---------|--------|
| Location | Must be in data directory | Can be from external directory |
| File handling | Files stay in place | Files can be moved or copied |
| Availability | Cassandra 3.x+ | Cassandra 4.0+ |
| Use case | Quick load | External bulk import |

---

## Common Issues

### "Unknown SSTable"

If SSTables are from a different cluster or schema version:

```bash
# May need to use sstableloader instead
sstableloader -d localhost /path/to/sstables/
```

### Missing Files

```
ERROR: Missing component Data.db
```

Ensure all SSTable component files are present.

### Permission Errors

```bash
# Fix ownership
chown -R cassandra:cassandra /var/lib/cassandra/data/my_keyspace/my_table-*/

# Then refresh
nodetool refresh my_keyspace my_table
```

### Wrong Directory

Verify the table UUID directory:

```bash
# Find correct directory
ls -la /var/lib/cassandra/data/my_keyspace/ | grep my_table
```

---

## Verification

### After Refresh

```bash
# Verify data is visible
nodetool tablestats my_keyspace.my_table

# Query the data
cqlsh -e "SELECT COUNT(*) FROM my_keyspace.my_table;"
```

### Check Logs

```bash
tail -f /var/log/cassandra/system.log | grep -i refresh
```

---

## Best Practices

!!! tip "Refresh Guidelines"
    1. **Validate SSTables first** - Check compatibility before copying
    2. **Use correct permissions** - cassandra:cassandra ownership
    3. **Copy all files** - Include all SSTable components
    4. **Monitor after refresh** - Check for errors in logs
    5. **Consider repair** - Run repair after bulk load for consistency

---

## Alternative: sstableloader

For loading SSTables to a different cluster or when topology differs:

```bash
sstableloader -d node1,node2,node3 /path/to/sstables/
```

sstableloader is more flexible but slower than refresh.

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [import](import.md) | Import SSTables from external location |
| [tablestats](tablestats.md) | Verify table after refresh |
| [upgradesstables](upgradesstables.md) | Upgrade SSTable format if needed |
| [snapshot](snapshot.md) | Create backups to restore later |
