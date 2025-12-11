# nodetool snapshot

Creates a snapshot (hard-link backup) of one or more tables.

---

## Synopsis

```bash
nodetool [connection_options] snapshot [options] [--] [keyspace ...]
```

## Description

`nodetool snapshot` creates a point-in-time copy of SSTable files using filesystem hard links. Snapshots are instantaneous, require minimal additional disk space initially, and serve as the foundation for Cassandra backups.

### Why Snapshots Matter

Cassandra continuously modifies data through compaction, which merges and deletes SSTable files. Without snapshots, there is no way to recover data from a specific point in time. Snapshots freeze a consistent view of the data that can be:

- **Restored locally** if data is accidentally deleted or corrupted
- **Copied off-node** for disaster recovery
- **Used for cloning** to create test environments from production data

### What Snapshots Capture

| Captured | Not Captured |
|----------|--------------|
| All committed SSTable data | Uncommitted data in memtables (unless flushed first) |
| Table schema definitions | Commit log files |
| Secondary index data | Configuration files |
| Materialized view data | System keyspace data (unless explicitly included) |

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | Keyspace(s) to snapshot. If omitted, snapshots all keyspaces |

---

## Options

| Option | Description |
|--------|-------------|
| `-t, --tag` | Name/tag for the snapshot |
| `-cf, --column-family` | Table(s) to snapshot (comma-separated) |
| `-sf, --skip-flush` | Skip flushing memtables before snapshot |
| `-kt, --kt-list` | List of keyspace.table to snapshot |
| `--ttl` | Time-to-live for snapshot (auto-deletion) |

---

## Examples

### Snapshot All Keyspaces

```bash
nodetool snapshot -t full_backup_20240115
```

Creates snapshot of all user keyspaces.

### Snapshot Specific Keyspace

```bash
nodetool snapshot -t my_backup my_keyspace
```

### Snapshot Specific Table

```bash
nodetool snapshot -t users_backup -cf users my_keyspace
```

### Snapshot Multiple Tables

```bash
nodetool snapshot -t tables_backup -kt my_keyspace.users,my_keyspace.orders
```

### Snapshot with TTL (Auto-Delete)

```bash
nodetool snapshot -t temp_backup --ttl 24h my_keyspace
```

!!! info "Snapshot TTL"
    Available in Cassandra 4.0+. The snapshot automatically deletes after the specified duration.

    Format: `<number><unit>` where unit is `s` (seconds), `m` (minutes), `h` (hours), `d` (days).

---

## Snapshot Location

Snapshots are stored within each table's data directory:

```
/var/lib/cassandra/data/<keyspace>/<table>-<uuid>/snapshots/<tag>/
```

Example:
```
/var/lib/cassandra/data/my_keyspace/users-a1b2c3d4/snapshots/my_backup/
├── nb-1-big-Data.db
├── nb-1-big-Index.db
├── nb-1-big-Filter.db
├── nb-1-big-CompressionInfo.db
├── nb-1-big-Statistics.db
├── nb-1-big-Digest.crc32
├── nb-1-big-TOC.txt
└── manifest.json
```

---

## When to Use

### Before Destructive Operations

!!! tip "Always Snapshot First"
    Take snapshots before:

    - Schema changes (ALTER TABLE, DROP)
    - Bulk deletes
    - Major compaction
    - Version upgrades
    - Data migrations

```bash
# Before dropping a column
nodetool snapshot -t before_schema_change my_keyspace
ALTER TABLE my_keyspace.users DROP old_column;
```

### Regular Backups

```bash
# Daily backup with date tag
nodetool snapshot -t daily_$(date +%Y%m%d) my_keyspace
```

### Before Upgrades

```bash
nodetool snapshot -t pre_upgrade_4.1
```

---

## When NOT to Use

### Without Flushing First

!!! danger "Flush Before Snapshot"
    By default, `nodetool snapshot` flushes memtables first. If using `-sf` (skip flush), recent writes will NOT be included:

    ```bash
    # WRONG - May miss recent data
    nodetool snapshot -sf -t my_backup

    # CORRECT - Ensures all data is captured
    nodetool flush my_keyspace
    nodetool snapshot -t my_backup my_keyspace
    ```

### Relying Solely on Snapshots

!!! warning "Snapshots Are Not Complete Backups"
    Snapshots alone are insufficient:

    - Only exist on local node
    - Lost if disk fails
    - Don't include commit logs

    Use snapshots as part of a complete backup strategy that copies data off-node.

---

## How Snapshots Work

### Understanding Hard Links

A **hard link** is a filesystem feature that allows multiple directory entries to point to the same physical data on disk. Unlike a copy, a hard link does not duplicate the data—it creates another reference to the existing data blocks.

```
┌─────────────────────────────────────────────────────────────────┐
│                         DISK STORAGE                            │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Actual Data Blocks (100 MB)                │    │
│  │              [SSTable file contents]                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                    ▲                    ▲                       │
│                    │                    │                       │
│               Reference 1          Reference 2                  │
│                    │                    │                       │
│  ┌─────────────────┴───┐    ┌──────────┴─────────────────┐     │
│  │ data/ks/tbl/        │    │ data/ks/tbl/snapshots/     │     │
│  │   nb-1-big-Data.db  │    │   backup/nb-1-big-Data.db  │     │
│  │ (original file)     │    │ (hard link - same data)    │     │
│  └─────────────────────┘    └────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘

Total disk usage: 100 MB (not 200 MB)
```

**Key properties of hard links:**

| Property | Behavior |
|----------|----------|
| Creation speed | Instantaneous (just adds a directory entry) |
| Initial space | Zero additional space (same data blocks) |
| Data persistence | Data remains until ALL references are deleted |
| Independence | Each link is equal; there is no "original" vs "copy" |

This is why snapshots are fast and space-efficient: creating a snapshot of 500 GB of data takes seconds and uses no additional disk space at the moment of creation.

### Space Usage Over Time

The space efficiency of hard links has a time dimension. When compaction runs, Cassandra deletes the original SSTable files—but the snapshot's hard links keep the data alive:

| Time | Event | Disk State | Space Impact |
|------|-------|------------|--------------|
| T=0 | Snapshot created | Both original and snapshot reference same blocks | +0 MB |
| T+1 | Compaction merges SSTables | Original files deleted, snapshot links remain | +0 MB |
| T+2 | Data blocks now only referenced by snapshot | Snapshot "owns" the data exclusively | Full size now attributed to snapshot |

**Example timeline:**

```
Day 1: Take snapshot of 100 GB table
       - Snapshot size shown: ~0 (hard links to active SSTables)

Day 3: Compaction runs, creates new SSTables, deletes old ones
       - Snapshot size shown: 100 GB (now holds exclusive references)
       - Active table size: 95 GB (new compacted SSTables)
       - Total disk usage: 195 GB
```

!!! warning "Snapshot Space Growth"
    Old snapshots accumulate disk space as compaction removes the original SSTables they reference. A week-old snapshot may consume as much space as the original data. Monitor with `nodetool listsnapshots` and clean up regularly.

---

## Disk Space Management

### Check Snapshot Sizes

```bash
nodetool listsnapshots
```

Output:
```
Snapshot name    Keyspace name    Column family name    True size    Size on disk
my_backup        my_keyspace      users                 1.5 GB       1.5 GB
my_backup        my_keyspace      orders                2.3 GB       2.3 GB
old_backup       my_keyspace      users                 1.2 GB       1.2 GB
```

### Check via tablestats

```bash
nodetool tablestats my_keyspace.users | grep "Space used by snapshots"
```

### Manual Space Check

```bash
du -sh /var/lib/cassandra/data/*/*/snapshots/*
```

---

## Complete Backup Workflow

### Step 1: Flush Memtables

```bash
nodetool flush my_keyspace
```

### Step 2: Create Snapshot

```bash
nodetool snapshot -t backup_$(date +%Y%m%d_%H%M%S) my_keyspace
```

### Step 3: Copy Off-Node

```bash
# Find snapshot files
find /var/lib/cassandra/data/my_keyspace -path "*/snapshots/backup_*" -type f

# Copy to backup location
rsync -av /var/lib/cassandra/data/my_keyspace/*/snapshots/backup_*/ /backup/location/
```

### Step 4: Clean Up Local Snapshot

```bash
nodetool clearsnapshot -t backup_20240115_120000 my_keyspace
```

---

## Snapshot for Schema Backup

Snapshots include `schema.cql` file containing the table definition:

```bash
cat /var/lib/cassandra/data/my_keyspace/users-*/snapshots/my_backup/schema.cql
```

---

## Common Issues

### "Snapshot already exists"

```
ERROR: Snapshot my_backup already exists
```

Solutions:
- Use a different tag name
- Clear existing snapshot: `nodetool clearsnapshot -t my_backup`

### Snapshot Takes Too Long

If snapshot is slow, it's likely waiting for flush:

```bash
# Check flush activity
nodetool tpstats | grep -i flush

# Use skip-flush if memtables already flushed
nodetool flush my_keyspace
nodetool snapshot -sf -t my_backup my_keyspace
```

### Disk Space Full

Snapshots may prevent space reclamation after compaction:

```bash
# Check snapshot sizes
nodetool listsnapshots

# Clear old snapshots
nodetool clearsnapshot -t old_backup
```

---

## Best Practices

!!! tip "Snapshot Guidelines"
    1. **Use meaningful tags** - Include date and purpose
    2. **Flush first** - Unless using skip-flush intentionally
    3. **Copy off-node** - Snapshots don't protect against disk failure
    4. **Clean up regularly** - Remove old snapshots to reclaim space
    5. **Document retention** - Define how long to keep snapshots
    6. **Automate** - Script snapshot creation and cleanup

### Naming Convention

```bash
# Include date, time, and purpose
nodetool snapshot -t pre_upgrade_20240115_1430
nodetool snapshot -t daily_backup_20240115
nodetool snapshot -t before_schema_change_users_20240115
```

---

## Restoring from Snapshots

Snapshots can be restored in two ways:

### Local Restore (Same Node, Same Schema)

Copy snapshot files back to the table's data directory and refresh:

```bash
# 1. Stop writes to the table (optional but recommended)
# 2. Copy snapshot files to table directory
cp /var/lib/cassandra/data/my_keyspace/users-*/snapshots/my_backup/*.db \
   /var/lib/cassandra/data/my_keyspace/users-*/

# 3. Refresh to load the restored files
nodetool refresh my_keyspace users
```

### Cross-Node Restore (Different Topology)

Use `sstableloader` to stream snapshot data to any cluster:

```bash
sstableloader -d node1,node2,node3 \
  /backup/my_keyspace/users-*/snapshots/my_backup/
```

For complete restore procedures, see [Backup and Restore](../backup-restore/index.md).

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [clearsnapshot](clearsnapshot.md) | Remove snapshots |
| [listsnapshots](listsnapshots.md) | List existing snapshots |
| [flush](flush.md) | Flush memtables before snapshot |
| [tablestats](tablestats.md) | Check snapshot space usage |
| [refresh](refresh.md) | Load restored SSTable files |

## Related Documentation

- [Backup and Restore Overview](../backup-restore/index.md) - Complete backup strategies
- [Restore Procedures](../backup-restore/restore.md) - Detailed restore scenarios
