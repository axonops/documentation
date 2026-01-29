---
title: "nodetool clearsnapshot"
description: "Delete snapshot files from Cassandra nodes using nodetool clearsnapshot. Free disk space after backups."
meta:
  - name: keywords
    content: "nodetool clearsnapshot, delete snapshots, Cassandra backup, disk space"
---

# nodetool clearsnapshot

Removes one or more snapshots from the node to reclaim disk space.

---

## Synopsis

```bash
nodetool [connection_options] clearsnapshot [options] [--] [keyspace ...]
```

## Description

`nodetool clearsnapshot` deletes snapshot files from the local node. Since snapshots are hard links to SSTable files, they consume disk space when the original SSTables are compacted away. Regular cleanup of old snapshots is essential for disk space management.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | Keyspace(s) to clear snapshots from. If omitted, clears from all keyspaces |

---

## Options

| Option | Description |
|--------|-------------|
| `-t, --tag` | Snapshot tag to clear. Required unless using `--all` |
| `--all` | Clear all snapshots |

---

## Examples

### Clear Specific Snapshot

```bash
nodetool clearsnapshot -t my_backup
```

Removes the snapshot tagged `my_backup` from all keyspaces.

### Clear Snapshot from Specific Keyspace

```bash
nodetool clearsnapshot -t my_backup my_keyspace
```

### Clear All Snapshots

```bash
nodetool clearsnapshot --all
```

!!! danger "Use with Caution"
    `--all` removes every snapshot on the node. Verify no critical backups exist before running.

### Clear All Snapshots from Keyspace

```bash
nodetool clearsnapshot --all my_keyspace
```

---

## When to Use

### After Successful Backup

Once backup files have been copied off-node:

```bash
# After copying snapshot files to backup storage
nodetool clearsnapshot -t backup_20240115
```

### Reclaim Disk Space

When disk usage is high due to old snapshots:

```bash
# Check snapshot sizes first
nodetool listsnapshots

# Remove old snapshots
nodetool clearsnapshot -t old_backup
```

### Clean Up After Testing

Remove snapshots created during testing:

```bash
nodetool clearsnapshot -t test_snapshot
```

### Regular Maintenance

Scheduled cleanup of aged snapshots:

```bash
# Find snapshots older than 7 days and clear them
# (Requires scripting based on listsnapshots output)
nodetool clearsnapshot -t weekly_backup_$(date -d "7 days ago" +%Y%m%d)
```

---

## When NOT to Use

### Before Verifying Backup

!!! danger "Verify Before Clearing"
    Never clear snapshots until backup files are:

    - Copied to remote storage
    - Verified for integrity
    - Tested for recoverability

### On Active Snapshots

Don't clear snapshots that are currently being copied or used.

### Without Checking First

Always list snapshots before clearing:

```bash
nodetool listsnapshots
```

---

## Verification Before Clearing

### List All Snapshots

```bash
nodetool listsnapshots
```

Output:
```
Snapshot name    Keyspace name    Column family name    True size    Size on disk
backup_20240115  my_keyspace      users                 1.5 GB       1.5 GB
backup_20240115  my_keyspace      orders                2.3 GB       2.3 GB
backup_20240108  my_keyspace      users                 1.2 GB       0 bytes
```

### Check Specific Snapshot

```bash
nodetool listsnapshots | grep backup_20240115
```

### Verify Disk Usage

```bash
# Check total snapshot space
du -sh /var/lib/cassandra/data/*/*/snapshots/

# Check specific snapshot
du -sh /var/lib/cassandra/data/*/*/snapshots/backup_20240115/
```

---

## Space Reclamation

### How Space is Freed

| State | SSTable | Snapshot | Disk Usage |
|-------|---------|----------|------------|
| Before clearsnapshot | Active (new) | Hard link exists | Space shared via inode |
| After clearsnapshot | Active (new) | Deleted | Space freed if no other references |

!!! info "Space Reclamation"
    - Hard links are removed by clearsnapshot
    - Disk blocks are freed only if no other references exist
    - Space reclamation may not be immediate depending on filesystem

### Verifying Space Freed

```bash
# Before
df -h /var/lib/cassandra

# Clear snapshot
nodetool clearsnapshot -t old_backup

# After
df -h /var/lib/cassandra
```

---

## Automated Cleanup

### Script for Aged Snapshots

```bash
#!/bin/bash
# Clear snapshots older than specified days

DAYS_OLD=7
KEYSPACE="my_keyspace"

# List snapshots and filter by age
nodetool listsnapshots | while read line; do
    # Parse snapshot name and check date
    # Implementation depends on naming convention
done
```

### Using TTL Snapshots (4.0+)

Instead of manual cleanup, create snapshots with TTL:

```bash
# Snapshot auto-deletes after 24 hours
nodetool snapshot -t temp_backup --ttl 24h my_keyspace
```

---

## Common Issues

### "Snapshot does not exist"

```
ERROR: Snapshot 'my_backup' does not exist
```

The snapshot tag wasn't found:

```bash
# List actual snapshot names
nodetool listsnapshots
```

### Space Not Freed

If disk space doesn't decrease after clearing:

1. Check if files were actually removed:
   ```bash
   ls /var/lib/cassandra/data/*/*/snapshots/
   ```

2. Hard links may still exist (original SSTable not yet compacted)

3. Filesystem may not report freed space immediately

### Cannot Delete Snapshot Directory

Permission issues:

```bash
# Check ownership
ls -la /var/lib/cassandra/data/my_keyspace/users-*/snapshots/

# Cassandra user should own files
sudo chown -R cassandra:cassandra /var/lib/cassandra/data/
```

---

## Best Practices

!!! tip "Snapshot Cleanup Guidelines"
    1. **List before clearing** - Verify which snapshots exist
    2. **Use specific tags** - Avoid `--all` in production
    3. **Verify backups first** - Ensure data is safely stored elsewhere
    4. **Automate cleanup** - Use TTL or scheduled scripts
    5. **Monitor disk usage** - Track snapshot growth over time
    6. **Document retention** - Define snapshot retention policies

### Retention Policy Example

| Snapshot Type | Retention |
|---------------|-----------|
| Pre-maintenance | 24 hours after maintenance |
| Daily backup | 7 days |
| Weekly backup | 30 days |
| Monthly backup | 1 year |

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [snapshot](snapshot.md) | Create snapshots |
| [listsnapshots](listsnapshots.md) | List existing snapshots |
| [tablestats](tablestats.md) | Check snapshot space per table |