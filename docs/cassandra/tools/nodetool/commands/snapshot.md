# nodetool snapshot

Creates a hard-link-based snapshot of data files for backup purposes.

## Synopsis

```bash
nodetool [connection_options] snapshot [options] [keyspace ...]
```

## Description

The `snapshot` command creates a point-in-time backup of table data by creating hard links to SSTable files. Since snapshots use hard links, they are created instantaneously without copying data, and the original data files cannot be deleted while snapshots reference them.

Snapshots capture only flushed SSTable data. Data in memtables is automatically flushed before the snapshot unless `--skip-flush` is specified.

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| keyspace | No | Keyspace(s) to snapshot. If omitted, snapshots all keyspaces. |

## Options

| Option | Description |
|--------|-------------|
| -t, --tag &lt;name&gt; | Snapshot name/tag (required for identification) |
| -cf, --column-family &lt;table&gt; | Snapshot specific table within keyspace |
| -kt, --kt-list &lt;ksp.tbl,...&gt; | Comma-separated list of keyspace.table pairs |
| -sf, --skip-flush | Do not flush memtables before snapshot |

## Snapshot Storage

Snapshots are stored within the data directory structure:

```
/var/lib/cassandra/data/<keyspace>/<table>-<uuid>/snapshots/<tag>/
```

Each snapshot directory contains hard links to:
- SSTable data files (`*-Data.db`)
- SSTable index files (`*-Index.db`)
- Filter files (`*-Filter.db`)
- Statistics files (`*-Statistics.db`)
- Compression info files (`*-CompressionInfo.db`)
- Summary files (`*-Summary.db`)
- TOC files (`*-TOC.txt`)
- Schema CQL file (`schema.cql`)
- Manifest file (`manifest.json`)

## Examples

### Snapshot All Keyspaces

```bash
nodetool snapshot -t full_backup_$(date +%Y%m%d_%H%M%S)
```

### Snapshot Specific Keyspace

```bash
nodetool snapshot -t daily_backup my_keyspace
```

### Snapshot Specific Table

```bash
nodetool snapshot -t users_backup -cf users my_keyspace
```

### Snapshot Multiple Tables

```bash
nodetool snapshot -t multi_table_backup -kt my_keyspace.users,my_keyspace.orders
```

### Snapshot Without Flush (Testing)

```bash
nodetool snapshot -sf -t test_snapshot my_keyspace
```

**Caution:** Skipping flush means in-memory data is not included in the snapshot.

## Snapshot Management

### List Existing Snapshots

```bash
nodetool listsnapshots
```

**Output:**
```
Snapshot Details:
Snapshot name       Keyspace name  Column family name  True size  Size on disk  Creation time
daily_backup        my_keyspace    users              1.5 GiB     1.8 GiB       2024-01-15T10:30:00Z
daily_backup        my_keyspace    orders             2.3 GiB     2.8 GiB       2024-01-15T10:30:00Z
full_backup_20240114 my_keyspace   users              1.5 GiB     1.8 GiB       2024-01-14T06:00:00Z

Total TrueDiskSpaceUsed: 5.3 GiB
```

### Clear Specific Snapshot

```bash
nodetool clearsnapshot -t daily_backup
```

### Clear All Snapshots

```bash
nodetool clearsnapshot --all
```

### Clear Snapshots for Keyspace

```bash
nodetool clearsnapshot -- my_keyspace
```

## Backup Procedures

### Full Backup Script

```bash
#!/bin/bash
# Complete backup procedure

KEYSPACE="my_keyspace"
BACKUP_TAG="backup_$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="/backup/cassandra/$BACKUP_TAG"

# Flush and snapshot
echo "Creating snapshot..."
nodetool snapshot -t $BACKUP_TAG $KEYSPACE

# Copy snapshot files to backup location
echo "Copying snapshot files..."
mkdir -p $BACKUP_DIR

for dir in /var/lib/cassandra/data/$KEYSPACE/*/snapshots/$BACKUP_TAG; do
    if [ -d "$dir" ]; then
        table=$(basename $(dirname $(dirname $dir)))
        mkdir -p "$BACKUP_DIR/$table"
        cp -al "$dir"/* "$BACKUP_DIR/$table/"
    fi
done

# Copy schema
echo "Exporting schema..."
cqlsh -e "DESC KEYSPACE $KEYSPACE" > "$BACKUP_DIR/schema.cql"

# Clear snapshot
echo "Clearing snapshot..."
nodetool clearsnapshot -t $BACKUP_TAG

echo "Backup complete: $BACKUP_DIR"
```

### Incremental Backup Note

For incremental backups between snapshots, enable `incremental_backups: true` in cassandra.yaml. This creates hard links in a `backups/` directory for each flushed SSTable.

## Restore Procedure

### Basic Restore Steps

1. Stop Cassandra on the target node
2. Clear existing data for the table
3. Copy snapshot files to the table data directory
4. Refresh the table after starting Cassandra

```bash
# On target node
sudo systemctl stop cassandra

# Clear existing table data
rm -rf /var/lib/cassandra/data/my_keyspace/users-*/

# Create table directory with correct UUID
mkdir -p /var/lib/cassandra/data/my_keyspace/users-<uuid>/

# Copy snapshot files
cp /backup/users/* /var/lib/cassandra/data/my_keyspace/users-<uuid>/

# Fix ownership
chown -R cassandra:cassandra /var/lib/cassandra/data/

# Start Cassandra
sudo systemctl start cassandra

# Refresh the table to load new SSTables
nodetool refresh my_keyspace users
```

## Disk Space Considerations

### True Size vs Size on Disk

| Metric | Description |
|--------|-------------|
| True size | Actual data size if snapshot files were real copies |
| Size on disk | Disk blocks used (initially 0 for hard links) |

Snapshot disk usage increases when:
- Original SSTable is modified (copy-on-write)
- Original SSTable is compacted away
- New writes occur to the table

### Monitoring Snapshot Space

```bash
# Check snapshot disk usage
du -sh /var/lib/cassandra/data/*/*/snapshots/*/

# List all snapshots with sizes
nodetool listsnapshots
```

### Preventing Disk Full

```bash
#!/bin/bash
# Clean up old snapshots
RETENTION_DAYS=7

for snapshot_dir in /var/lib/cassandra/data/*/*/snapshots/*; do
    if [ -d "$snapshot_dir" ]; then
        snapshot_name=$(basename $snapshot_dir)
        # Check if snapshot is older than retention
        find "$snapshot_dir" -maxdepth 0 -mtime +$RETENTION_DAYS -exec \
            nodetool clearsnapshot -t "$snapshot_name" \;
    fi
done
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Snapshot created successfully |
| 1 | Error occurred |
| 2 | Invalid arguments |

## Related Commands

- [nodetool listsnapshots](listsnapshots.md) - List existing snapshots
- [nodetool clearsnapshot](clearsnapshot.md) - Remove snapshots
- [nodetool flush](flush.md) - Flush memtables before snapshot
- [nodetool refresh](refresh.md) - Load restored SSTables

## Related Documentation

- [Operations - Backup & Restore](../../../operations/backup-restore/index.md) - Complete backup guide
- [Architecture - Storage Engine](../../../architecture/storage-engine/index.md) - Understanding SSTables
- [Configuration - cassandra.yaml](../../../configuration/cassandra-yaml/index.md) - Backup configuration

## Version Information

Available in all Apache Cassandra versions. The `--kt-list` option for multiple table snapshots was enhanced in Cassandra 4.0.
