---
title: "sstableutil"
description: "List SSTable component files for a table using sstableutil. Find data file locations."
meta:
  - name: keywords
    content: "sstableutil, list SSTables, SSTable files, Cassandra storage"
---

# sstableutil

Lists SSTable files belonging to a table, including active, temporary, and obsolete files.

---

## Synopsis

```bash
sstableutil [options] <keyspace> <table>
```

---

## Description

`sstableutil` provides a comprehensive listing of all SSTable files associated with a table. It identifies not only active SSTables but also temporary files from in-progress operations and obsolete files awaiting cleanup.

This tool is useful for:

- **Identifying SSTable files** before running other SSTable tools
- **Diagnosing cleanup issues** - Finding orphaned or obsolete files
- **Understanding storage layout** - Seeing all files for a table
- **Pre-operation verification** - Confirming SSTable paths before maintenance

!!! info "Safe to Run While Cassandra Is Active"
    `sstableutil` can safely run while Cassandra is active. It performs read-only filesystem operations.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | Name of the keyspace containing the table |
| `table` | Name of the table to list SSTables for |

---

## Options

| Option | Description |
|--------|-------------|
| `-c, --cleanup` | Only list obsolete files (cleanup candidates) |
| `-d, --debug` | Enable debug output |
| `-o, --oplog` | Include transaction log files |
| `-s, --snapshot <name>` | List SSTables in a specific snapshot |
| `-t, --type <type>` | Filter by SSTable type: `tmp`, `final`, `all` |

---

## Examples

### List All SSTables

```bash
# List all SSTable files for a table
sstableutil my_keyspace my_table
```

### List Active SSTables Only

```bash
# Only show final (active) SSTables
sstableutil -t final my_keyspace my_table
```

### List Temporary Files

```bash
# Show temporary files from in-progress operations
sstableutil -t tmp my_keyspace my_table
```

### Find Obsolete Files

```bash
# List files that should be cleaned up
sstableutil --cleanup my_keyspace my_table
```

### List Snapshot SSTables

```bash
# List SSTables in a specific snapshot
sstableutil --snapshot my_snapshot my_keyspace my_table
```

### Include Transaction Logs

```bash
# Also show transaction log files
sstableutil --oplog my_keyspace my_table
```

---

## Output Format

### Standard Output

```
Listing files for my_keyspace.my_table
/var/lib/cassandra/data/my_keyspace/my_table-a1b2c3d4/nb-1-big-CompressionInfo.db
/var/lib/cassandra/data/my_keyspace/my_table-a1b2c3d4/nb-1-big-Data.db
/var/lib/cassandra/data/my_keyspace/my_table-a1b2c3d4/nb-1-big-Digest.crc32
/var/lib/cassandra/data/my_keyspace/my_table-a1b2c3d4/nb-1-big-Filter.db
/var/lib/cassandra/data/my_keyspace/my_table-a1b2c3d4/nb-1-big-Index.db
/var/lib/cassandra/data/my_keyspace/my_table-a1b2c3d4/nb-1-big-Statistics.db
/var/lib/cassandra/data/my_keyspace/my_table-a1b2c3d4/nb-1-big-Summary.db
/var/lib/cassandra/data/my_keyspace/my_table-a1b2c3d4/nb-1-big-TOC.txt
/var/lib/cassandra/data/my_keyspace/my_table-a1b2c3d4/nb-2-big-CompressionInfo.db
/var/lib/cassandra/data/my_keyspace/my_table-a1b2c3d4/nb-2-big-Data.db
...
```

### SSTable Components

Each SSTable consists of multiple component files:

| Component | Extension | Description |
|-----------|-----------|-------------|
| Data | `-Data.db` | Actual row data |
| Index | `-Index.db` | Partition index |
| Filter | `-Filter.db` | Bloom filter |
| Statistics | `-Statistics.db` | SSTable metadata |
| Summary | `-Summary.db` | Index summary |
| Compression | `-CompressionInfo.db` | Compression metadata |
| Digest | `-Digest.crc32` | Data checksum |
| TOC | `-TOC.txt` | Table of contents |

---

## Understanding SSTable Names

### Naming Convention

```
<version>-<generation>-<format>-<component>.<extension>

Example: nb-1-big-Data.db
         │  │  │    │
         │  │  │    └── Component type
         │  │  └─────── Format (big = standard)
         │  └────────── Generation number
         └───────────── Version (nb = 4.0)
```

### Version Codes

| Code | Cassandra Version |
|------|-------------------|
| jb | 2.0.x |
| ka | 2.1.x |
| la | 2.2.x |
| ma | 3.0.x |
| mb | 3.11.x |
| nb | 4.0.x |
| nc | 4.1.x |
| oa | 5.0.x |

---

## Common Use Cases

### Find SSTable Paths for Other Tools

```bash
# Get Data.db paths for sstablemetadata
sstableutil my_keyspace my_table | grep "Data.db$"

# Use with sstablemetadata
for f in $(sstableutil my_keyspace my_table | grep "Data.db$"); do
    sstablemetadata "$f"
done
```

### Count SSTables

```bash
# Count number of SSTables for a table
sstableutil my_keyspace my_table | grep -c "Data.db$"
```

### Calculate Total Size

```bash
#!/bin/bash
# sstable_size.sh - Calculate total SSTable size

KEYSPACE="$1"
TABLE="$2"

total_size=0
for f in $(sstableutil "$KEYSPACE" "$TABLE"); do
    size=$(stat -c%s "$f" 2>/dev/null)
    total_size=$((total_size + size))
done

echo "Total size: $((total_size / 1024 / 1024)) MB"
```

### Find Orphaned Files

```bash
#!/bin/bash
# find_orphaned.sh - Find files not tracked by Cassandra

KEYSPACE="$1"
TABLE="$2"
DATA_DIR="/var/lib/cassandra/data"

# Get tracked files
tracked=$(sstableutil "$KEYSPACE" "$TABLE" | sort)

# Get all files in directory
all_files=$(find ${DATA_DIR}/${KEYSPACE}/${TABLE}-*/ -type f ! -name "*.log" | sort)

echo "Files not tracked by Cassandra:"
comm -13 <(echo "$tracked") <(echo "$all_files")
```

### Cleanup Verification

```bash
#!/bin/bash
# verify_cleanup.sh - Check for files needing cleanup

KEYSPACE="$1"
TABLE="$2"

echo "Checking for obsolete files in ${KEYSPACE}.${TABLE}..."

obsolete=$(sstableutil --cleanup "$KEYSPACE" "$TABLE")

if [ -z "$obsolete" ]; then
    echo "No obsolete files found"
else
    echo "Obsolete files found:"
    echo "$obsolete"
    echo ""
    echo "Run 'nodetool cleanup' or wait for automatic cleanup"
fi
```

### Snapshot Verification

```bash
#!/bin/bash
# verify_snapshot.sh - Verify snapshot contents

KEYSPACE="$1"
TABLE="$2"
SNAPSHOT="$3"

echo "SSTables in snapshot '$SNAPSHOT' for ${KEYSPACE}.${TABLE}:"

sstableutil --snapshot "$SNAPSHOT" "$KEYSPACE" "$TABLE" | grep "Data.db$"

count=$(sstableutil --snapshot "$SNAPSHOT" "$KEYSPACE" "$TABLE" | grep -c "Data.db$")
echo ""
echo "Total SSTables in snapshot: $count"
```

### Pre-Tool Verification

```bash
#!/bin/bash
# pre_tool_check.sh - Verify SSTables before running offline tools

KEYSPACE="$1"
TABLE="$2"

echo "SSTable verification for ${KEYSPACE}.${TABLE}"
echo "============================================="

# Check for active SSTables
echo ""
echo "Active SSTables:"
sstableutil -t final "$KEYSPACE" "$TABLE" | grep "Data.db$" | wc -l

# Check for temporary files
echo ""
echo "Temporary files:"
tmp_count=$(sstableutil -t tmp "$KEYSPACE" "$TABLE" | wc -l)
if [ "$tmp_count" -gt 0 ]; then
    echo "WARNING: $tmp_count temporary files found"
    echo "An operation may be in progress"
    sstableutil -t tmp "$KEYSPACE" "$TABLE"
else
    echo "None"
fi

# Check for obsolete files
echo ""
echo "Obsolete files:"
obsolete_count=$(sstableutil --cleanup "$KEYSPACE" "$TABLE" | wc -l)
if [ "$obsolete_count" -gt 0 ]; then
    echo "WARNING: $obsolete_count obsolete files found"
    sstableutil --cleanup "$KEYSPACE" "$TABLE"
else
    echo "None"
fi
```

---

## SSTable File Types

### Final (Active) SSTables

Active SSTables currently being used by Cassandra:

```bash
sstableutil -t final my_keyspace my_table
```

### Temporary Files

Files from in-progress operations (compaction, streaming):

```bash
sstableutil -t tmp my_keyspace my_table
```

Temporary files may indicate:
- Active compaction
- Active streaming
- Incomplete operation (if Cassandra crashed)

### Obsolete Files

Files marked for deletion but not yet removed:

```bash
sstableutil --cleanup my_keyspace my_table
```

Obsolete files are cleaned up:
- Automatically after compaction
- When `nodetool cleanup` is run
- After repair operations

---

## Transaction Logs

Transaction logs track pending SSTable operations:

```bash
sstableutil --oplog my_keyspace my_table
```

### Transaction Log Files

| File Pattern | Purpose |
|--------------|---------|
| `*.log` | Pending operation log |
| `*_txn_*.log` | Transaction in progress |

Transaction logs ensure atomicity of SSTable operations. They should be automatically cleaned up after operations complete.

---

## Troubleshooting

### No SSTables Found

```bash
# Check if table exists
cqlsh -e "DESCRIBE TABLE my_keyspace.my_table;"

# Check data directory
ls -la /var/lib/cassandra/data/my_keyspace/

# Table may be empty - check with flush first
nodetool flush my_keyspace my_table
sstableutil my_keyspace my_table
```

### Permission Denied

```bash
# Run as cassandra user
sudo -u cassandra sstableutil my_keyspace my_table

# Or check permissions
ls -la /var/lib/cassandra/data/my_keyspace/my_table-*/
```

### Stale Temporary Files

If temporary files persist after Cassandra restart:

```bash
# Check for stale temp files
sstableutil -t tmp my_keyspace my_table

# If Cassandra is stopped and these are from crashed operations:
# They can usually be safely deleted
# But verify Cassandra is stopped first!
```

---

## Best Practices

!!! tip "sstableutil Guidelines"

    1. **Use before other tools** - Verify paths before running offline tools
    2. **Check for temp files** - Before maintenance, ensure no operations in progress
    3. **Regular cleanup checks** - Monitor for accumulating obsolete files
    4. **Verify snapshots** - Confirm snapshot contents before restores
    5. **Script integration** - Use in automation scripts for path discovery
    6. **Safe operation** - Can run while Cassandra is active

!!! info "Safe Operation"

    `sstableutil` is completely read-only and safe to run at any time, whether Cassandra is running or not.

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [sstablemetadata](sstablemetadata.md) | Get metadata for listed SSTables |
| [sstabledump](sstabledump.md) | Dump data from listed SSTables |
| [sstableverify](sstableverify.md) | Verify listed SSTables |
| [nodetool cleanup](../nodetool/cleanup.md) | Remove obsolete files |
| [nodetool compact](../nodetool/compact.md) | Compact SSTables |
