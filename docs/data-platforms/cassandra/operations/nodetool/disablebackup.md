---
title: "nodetool disablebackup"
description: "Disable incremental backup in Cassandra using nodetool disablebackup command."
meta:
  - name: keywords
    content: "nodetool disablebackup, disable backup, Cassandra backup, incremental backup"
---

# nodetool disablebackup

Disables incremental backup on the node.

---

## Synopsis

```bash
nodetool [connection_options] disablebackup
```

## Description

`nodetool disablebackup` disables incremental backup mode on the node. Once disabled, Cassandra stops creating hard links to newly flushed SSTables. Existing backup files in the `backups` directory are not removed—they must be cleaned up manually.

Incremental backup creates hard links to SSTables upon memtable flush, providing continuous backup capability. Disabling this feature stops the automatic link creation process.

!!! warning "Non-Persistent Setting"
    This setting is applied at runtime only and does not persist across node restarts. After a restart, incremental backup reverts to the `incremental_backups` setting in `cassandra.yaml` (default: `false`).

    To make the change permanent, update `cassandra.yaml`:

    ```yaml
    incremental_backups: false
    ```

---

## Behavior

When incremental backup is disabled:

1. No new hard links are created for flushed SSTables
2. Existing backup files remain in place (not deleted)
3. Disk space used by existing backups is retained
4. The change takes effect immediately
5. The setting reverts to the `cassandra.yaml` configuration on restart

---

## Examples

### Basic Usage

```bash
nodetool disablebackup
```

### Verify Disabled

```bash
nodetool disablebackup
nodetool statusbackup
# Expected output: not running
```

---

## When to Use

### Disk Space Management

When backup files consume too much space:

```bash
# Check current backup sizes
du -sh /var/lib/cassandra/data/*/*/backups/
# Total: 150GB

# Stop new backups
nodetool disablebackup

# Copy existing backups to external storage
rsync -av /var/lib/cassandra/data/*/*/backups/ /backup/server/

# Clean up local backups
find /var/lib/cassandra/data -path "*/backups/*" -type f -delete

# Verify cleanup
du -sh /var/lib/cassandra/data/*/*/backups/
```

### Temporary Maintenance Disable

During maintenance operations:

```bash
# Disable during heavy operations
nodetool disablebackup

# Perform maintenance (repair, compaction, etc.)
nodetool repair -pr my_keyspace

# Re-enable after maintenance
nodetool enablebackup

# Verify
nodetool statusbackup
```

### Switching Backup Strategy

When migrating to a different backup solution:

```bash
# Disable incremental backup
nodetool disablebackup

# Clean up existing backup files
find /var/lib/cassandra/data -path "*/backups/*" -delete

# (Configure new backup solution)
```

### I/O Reduction

During I/O-intensive operations:

```bash
# Disable to reduce I/O overhead
nodetool disablebackup

# Perform I/O-intensive operation
nodetool upgradesstables

# Re-enable
nodetool enablebackup
```

### Before Node Decommission

Remove unnecessary backup overhead before decommission:

```bash
# Disable backups (node is leaving)
nodetool disablebackup

# Clean up backup files
find /var/lib/cassandra/data -path "*/backups/*" -delete

# Proceed with decommission
nodetool decommission
```

---

## Impact Assessment

### What Changes

| Aspect | Before Disable | After Disable |
|--------|----------------|---------------|
| New backup links | Created on flush | Not created |
| Existing backups | Present | Still present |
| Disk overhead | Grows with flushes | No new growth |
| Recovery capability | Full incremental | Depends on existing files |

### What Does NOT Change

- Existing backup files remain (must clean manually)
- Snapshots are unaffected
- Compaction behavior unchanged
- Normal data operations continue

---

## Cleanup After Disable

Disabling backup does **not** remove existing files:

### Check Backup Size

```bash
# Per-keyspace backup sizes
du -sh /var/lib/cassandra/data/*/*/backups/

# Total backup size
find /var/lib/cassandra/data -path "*/backups/*" -type f -exec du -ch {} + | tail -1
```

### Copy Before Cleanup

```bash
# Back up to external storage first
rsync -av /var/lib/cassandra/data/*/*/backups/ /backup/final_incremental/
```

### Remove Backup Files

```bash
# Remove all backup files (careful!)
find /var/lib/cassandra/data -path "*/backups/*" -type f -delete

# Or remove per-keyspace
rm -rf /var/lib/cassandra/data/my_keyspace/*/backups/*

# Verify removal
find /var/lib/cassandra/data -path "*/backups/*" -type f | wc -l
# Should be 0
```

---

## Workflow: Complete Backup Disable and Cleanup

```bash
#!/bin/bash
# disable_and_cleanup_backup.sh

echo "=== Disable Incremental Backup ==="
echo ""

# 1. Check current state
echo "1. Current status: $(nodetool statusbackup)"

# 2. Check current backup size
echo "2. Current backup size:"
find /var/lib/cassandra/data -path "*/backups/*" -type f -exec du -ch {} + 2>/dev/null | tail -1

# 3. Disable backup
echo "3. Disabling incremental backup..."
nodetool disablebackup

# 4. Verify disabled
echo "4. New status: $(nodetool statusbackup)"

# 5. Optional: Clean up existing backups
read -p "5. Remove existing backup files? (y/n): " cleanup
if [ "$cleanup" = "y" ]; then
    echo "   Removing backup files..."
    find /var/lib/cassandra/data -path "*/backups/*" -type f -delete
    echo "   Done."
fi

echo ""
echo "=== Complete ==="
```

---

## Effects on Disk Space

### Hard Links Explained

When backup is enabled, SSTables have hard links in the backups directory:

```
SSTable: /data/keyspace/table/nb-1-big-Data.db
Backup:  /data/keyspace/table/backups/nb-1-big-Data.db
         (both point to same disk blocks)
```

After compaction removes the original SSTable:
- The backup file becomes the only reference
- Disk space is now exclusively used by backup

### Space Recovery

To reclaim space after disabling:

```bash
# Check space used by backups
du -sh /var/lib/cassandra/data/*/*/backups/

# Remove to reclaim
find /var/lib/cassandra/data -path "*/backups/*" -delete

# Verify space recovered
df -h /var/lib/cassandra
```

---

## Runtime vs Persistent Configuration

### Runtime (Temporary)

```bash
nodetool disablebackup
# Does not persist across restart
```

### Persistent (Permanent)

Edit `cassandra.yaml`:

```yaml
incremental_backups: false
```

Then either restart or use nodetool:

```bash
# For immediate effect without restart
nodetool disablebackup
```

### Comparison

| Method | Effect | Persistence |
|--------|--------|-------------|
| `nodetool disablebackup` | Immediate | Until restart |
| `cassandra.yaml: false` | After restart | Permanent |
| Both | Immediate + permanent | Best practice |

---

## Monitoring

### Verify Status

```bash
nodetool statusbackup
# Expected: not running
```

### Monitor Backup Directory Growth

Even after disable, verify no new files:

```bash
# Before operation
ls /var/lib/cassandra/data/my_keyspace/my_table-*/backups/ | wc -l
# Count: 50

# Force flush
nodetool flush my_keyspace

# After flush (should be same if disabled)
ls /var/lib/cassandra/data/my_keyspace/my_table-*/backups/ | wc -l
# Count: 50 (unchanged)
```

---

## Troubleshooting

### Status Still Shows "running"

```bash
# Retry disable
nodetool disablebackup

# Check JMX connectivity
nodetool info

# Verify
nodetool statusbackup
```

### Backup Files Still Appearing

If new backup files appear after disable:

```bash
# Verify disabled
nodetool statusbackup
# Should be: not running

# Check cassandra.yaml (might override on restart)
grep incremental_backups /etc/cassandra/cassandra.yaml

# If yaml says true, update it
vim /etc/cassandra/cassandra.yaml
# Set: incremental_backups: false
```

### Cannot Remove Backup Files

If deletion fails:

```bash
# Check file ownership
ls -la /var/lib/cassandra/data/my_keyspace/*/backups/

# Check if files are open
lsof +D /var/lib/cassandra/data/my_keyspace/my_table/backups/

# May need to run as cassandra user
sudo -u cassandra rm -rf /var/lib/cassandra/data/*/*/backups/*
```

---

## Cluster-Wide Disable

Disable backup across all nodes:

```bash
#!/bin/bash
# disable_backup_cluster.sh# Get list of node IPs from local nodetool status


nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

echo "Disabling incremental backup cluster-wide"
echo "==========================================="

for node in $nodes; do
    echo -n "$node: "
    ssh "$node" "nodetool disablebackup 2>/dev/null && echo "disabled" || echo "failed""
done

echo ""
echo "Verification:"
for node in $nodes; do
    echo -n "$node: "
    ssh "$node" "nodetool statusbackup"
done
```

---

## Best Practices

!!! tip "Disable Backup Guidelines"

    1. **Document the reason** - Note why backup was disabled
    2. **Copy before cleanup** - Always backup before deleting files
    3. **Update cassandra.yaml** - Make change persistent if intended
    4. **Verify status** - Confirm disabled with `statusbackup`
    5. **Clean up disk** - Remove old backup files to reclaim space
    6. **Cluster consistency** - Apply to all nodes if disabling cluster-wide
    7. **Re-enable after maintenance** - Don't forget to restore backup if temporary

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [enablebackup](enablebackup.md) | Enable incremental backup |
| [statusbackup](statusbackup.md) | Check backup status |
| [snapshot](snapshot.md) | Full point-in-time backup |
| [listsnapshots](listsnapshots.md) | List existing snapshots |
| [clearsnapshot](clearsnapshot.md) | Remove snapshots |
