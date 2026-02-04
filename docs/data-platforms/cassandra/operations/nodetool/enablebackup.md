---
title: "nodetool enablebackup"
description: "Enable incremental backup in Cassandra using nodetool enablebackup command."
meta:
  - name: keywords
    content: "nodetool enablebackup, enable backup, Cassandra backup, incremental backup"
---

# nodetool enablebackup

Enables incremental backup.

---

## Synopsis

```bash
nodetool [connection_options] enablebackup
```
See [connection options](index.md#connection-options) for connection options.

## Description

`nodetool enablebackup` enables incremental backup mode. When enabled, Cassandra creates hard links to newly flushed SSTables in a `backups` subdirectory. This allows continuous backup of data as it's written.

!!! warning "Non-Persistent Setting"
    This setting is applied at runtime only and does not persist across node restarts. After a restart, incremental backup reverts to the `incremental_backups` setting in `cassandra.yaml` (default: `false`).

    To make the change permanent, update `cassandra.yaml`:

    ```yaml
    incremental_backups: true
    ```

---

## How Incremental Backup Works

When incremental backup is enabled:

1. Each time new SSTables are created (during flush, compaction, or other operations), a hard link is created
2. Hard links go to: `<data_dir>/<keyspace>/<table>/backups/`
3. Links point to the same data blocks (no extra disk space initially)
4. Backup files remain even after compaction removes the original

---

## Example

```bash
nodetool enablebackup
```

Verify:

```bash
nodetool statusbackup
# Expected: running
```

---

## Backup Location

```
/var/lib/cassandra/data/<keyspace>/<table>-<uuid>/backups/
```

Example:
```
/var/lib/cassandra/data/my_keyspace/my_table-abc123/backups/
├── nb-1-big-Data.db
├── nb-1-big-Index.db
├── nb-1-big-Filter.db
└── ...
```

---

## Use Cases

### Continuous Backup Strategy

```bash
# 1. Enable incremental backup
nodetool enablebackup

# 2. Periodically copy backup files to external storage
rsync -av /var/lib/cassandra/data/*/*/backups/ /backup/incremental/

# 3. Clear processed backups
rm -rf /var/lib/cassandra/data/*/*/backups/*
```

### Combined with Snapshots

```bash
# Weekly full backup (snapshot)
nodetool snapshot -t weekly_$(date +%Y%m%d)

# Daily incremental backup
nodetool enablebackup
# ... copy backups daily ...
```

---

## Incremental vs Snapshot Backup

| Aspect | Incremental | Snapshot |
|--------|-------------|----------|
| Trigger | Automatic on flush | Manual command |
| Content | New SSTables only | All current SSTables |
| Disk usage | Grows over time | Point-in-time |
| Recovery | Need base + incrementals | Self-contained |
| Overhead | Continuous | On-demand |

---

## Workflow: Incremental Backup

```bash
# 1. Take initial snapshot (baseline)
nodetool snapshot -t baseline

# 2. Enable incremental backup
nodetool enablebackup

# 3. Application writes data...

# 4. Periodically copy incrementals
rsync -av /var/lib/cassandra/data/*/*/backups/ /backup/server/

# 5. Clear processed incrementals
find /var/lib/cassandra/data -path "*/backups/*" -delete

# 6. Repeat steps 4-5
```

---

## Restoration Process

To restore from incremental backups:

```bash
# 1. Restore baseline snapshot
cp -r /backup/snapshots/baseline/* /var/lib/cassandra/data/

# 2. Layer incremental backups
cp -r /backup/incremental/* /var/lib/cassandra/data/

# 3. Start Cassandra or refresh
nodetool refresh keyspace table
```

---

## Disk Space Considerations

!!! warning "Space Growth"
    Incremental backups consume disk space:

    - Hard links share data initially
    - After compaction, backup files use real space
    - Old backup files not automatically deleted

### Monitoring Space

```bash
# Check backup directory size
du -sh /var/lib/cassandra/data/*/*/backups/

# Total backup size
find /var/lib/cassandra/data -path "*/backups/*" -type f -exec du -ch {} + | tail -1
```

### Cleanup

```bash
# Remove processed backups
find /var/lib/cassandra/data -path "*/backups/*" -delete
```

---

## Configuration

### cassandra.yaml Setting

```yaml
incremental_backups: true  # Or use nodetool enablebackup
```

### Runtime vs Configuration

| Method | Persistence |
|--------|-------------|
| `nodetool enablebackup` | Until restart |
| `cassandra.yaml` | Permanent |

---

## Automation Script

```bash
#!/bin/bash
# incremental_backup.sh - Copy and clear incrementals

BACKUP_DIR="/backup/cassandra/incremental/$(date +%Y%m%d_%H%M)"
DATA_DIR="/var/lib/cassandra/data"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Copy incremental backups
for backup_path in $(find $DATA_DIR -type d -name "backups"); do
    if [ "$(ls -A $backup_path 2>/dev/null)" ]; then
        # Get relative path for organization
        rel_path=$(echo $backup_path | sed "s|$DATA_DIR/||")
        mkdir -p "$BACKUP_DIR/$rel_path"
        mv "$backup_path"/* "$BACKUP_DIR/$rel_path/"
    fi
done

echo "Incremental backup completed: $BACKUP_DIR"
```

---

## Best Practices

!!! tip "Incremental Backup Guidelines"
    1. **Start with a snapshot** - Need baseline for recovery
    2. **Regular cleanup** - Move and delete processed backups
    3. **Monitor disk space** - Backups grow continuously
    4. **Test restoration** - Verify backup/restore process
    5. **Document retention** - Know what's backed up and when

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [disablebackup](disablebackup.md) | Disable incremental backup |
| [statusbackup](statusbackup.md) | Check backup status |
| [snapshot](snapshot.md) | Create full backup |
| [listsnapshots](listsnapshots.md) | List snapshots |