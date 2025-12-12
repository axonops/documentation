---
description: "List all snapshots on a Cassandra node using nodetool listsnapshots command."
meta:
  - name: keywords
    content: "nodetool listsnapshots, list snapshots, Cassandra backup, snapshot info"
---

# nodetool listsnapshots

Displays a list of all snapshots on the node with their sizes.

---

## Synopsis

```bash
nodetool [connection_options] listsnapshots [-e] [-n]
```

## Description

`nodetool listsnapshots` shows all snapshots on the local node, including:

- Snapshot tag name
- Keyspace and table names
- True data size
- Disk space consumed

Essential for monitoring backup state and managing disk space.

---

## Options

| Option | Description |
|--------|-------------|
| `-e, --ephemeral` | Include ephemeral snapshots |
| `-n, --no-ttl` | Exclude snapshots with TTL |

---

## Output Example

```
Snapshot Details:
Snapshot name       Keyspace name      Column family name   True size   Size on disk   Creation time
backup_20240115     my_keyspace        users                1.5 GB      1.5 GB         2024-01-15T10:30:00Z
backup_20240115     my_keyspace        orders               2.3 GB      2.3 GB         2024-01-15T10:30:00Z
backup_20240108     my_keyspace        users                1.2 GB      0 bytes        2024-01-08T10:30:00Z
backup_20240108     my_keyspace        orders               2.1 GB      0 bytes        2024-01-08T10:30:00Z
pre_upgrade         system_schema      tables               45 MB       45 MB          2024-01-14T22:00:00Z

Total TrueDiskSpaceUsed: 7.15 GB
```

---

## Output Fields

| Field | Description |
|-------|-------------|
| Snapshot name | Tag used when creating the snapshot |
| Keyspace name | Keyspace containing the table |
| Column family name | Table name |
| True size | Actual data size in the snapshot |
| Size on disk | Current disk space consumed |
| Creation time | When the snapshot was created |

### Understanding Size Fields

| True size | Size on disk | Meaning |
|-----------|--------------|---------|
| 1.5 GB | 1.5 GB | Original SSTables still exist (hard links) |
| 1.5 GB | 0 bytes | Original SSTables compacted away (space freed) |
| 1.5 GB | 500 MB | Partially compacted |

!!! info "Size on Disk"
    "Size on disk" shows actual disk blocks consumed. When original SSTables are compacted, the hard links become the only reference, and size on disk increases.

---

## Examples

### List All Snapshots

```bash
nodetool listsnapshots
```

### Include Ephemeral Snapshots

```bash
nodetool listsnapshots -e
```

### Exclude TTL Snapshots

```bash
nodetool listsnapshots -n
```

### Filter by Snapshot Name

```bash
nodetool listsnapshots | grep backup_20240115
```

### Total Snapshot Size

```bash
nodetool listsnapshots | tail -1
```

### Count Snapshots

```bash
nodetool listsnapshots | grep -c "^[a-zA-Z]"
```

---

## When to Use

### Before Creating New Snapshots

Check existing snapshots to avoid duplicates:

```bash
nodetool listsnapshots | grep my_new_tag
```

### Disk Space Investigation

When disk usage is high:

```bash
nodetool listsnapshots
# Check Total TrueDiskSpaceUsed at the bottom
```

### Backup Verification

Verify snapshot was created:

```bash
nodetool snapshot -t my_backup my_keyspace
nodetool listsnapshots | grep my_backup
```

### Cleanup Planning

Identify snapshots to remove:

```bash
nodetool listsnapshots
# Find old snapshots by creation time
```

---

## Interpreting Results

### Recently Created Snapshot

```
backup_20240115     my_keyspace     users     1.5 GB     1.5 GB     2024-01-15T10:30:00Z
```

- True size = Size on disk = Original SSTables still exist
- Hard links share disk blocks with active SSTables
- Minimal additional space used

### Aged Snapshot

```
backup_20240101     my_keyspace     users     1.5 GB     1.5 GB     2024-01-01T10:30:00Z
```

After compaction runs:

- Original SSTables removed
- Snapshot files become sole reference
- Now consuming full 1.5 GB

### No Snapshots

```
Snapshot Details:

Total TrueDiskSpaceUsed: 0 bytes
```

No snapshots exist on this node.

---

## Monitoring Snapshot Growth

### Check All Nodes

```bash
for node in node1 node2 node3; do
    echo "=== $node ==="
    nodetool -h $node listsnapshots | tail -3
done
```

### Track Over Time

```bash
# Log snapshot sizes daily
echo "$(date),$(nodetool listsnapshots | tail -1 | awk '{print $2}')" >> /var/log/snapshot_sizes.csv
```

### Alert on Large Snapshots

```bash
total=$(nodetool listsnapshots | tail -1 | awk '{print $2}' | sed 's/GB//')
if (( $(echo "$total > 100" | bc -l) )); then
    echo "WARNING: Snapshot usage exceeds 100GB"
fi
```

---

## Snapshot Location on Disk

Snapshots are stored in:

```
/var/lib/cassandra/data/<keyspace>/<table>-<uuid>/snapshots/<tag>/
```

To manually check sizes:

```bash
# All snapshots
du -sh /var/lib/cassandra/data/*/*/snapshots/*

# Specific snapshot
du -sh /var/lib/cassandra/data/*/*/snapshots/backup_20240115/
```

---

## Common Issues

### Empty Output

If no snapshots are shown but you expect them:

1. Check if snapshots were taken on this node
2. Verify snapshot directory exists:
   ```bash
   ls /var/lib/cassandra/data/*/*/snapshots/
   ```

### Incorrect Size Reported

Size reporting depends on filesystem support for hard links:

- Some filesystems may not accurately report shared blocks
- Use `du` for precise measurements if needed

### Very Large Total Size

Old snapshots consuming significant space:

```bash
# Identify largest snapshots
nodetool listsnapshots | sort -k4 -h

# Clear old snapshots
nodetool clearsnapshot -t old_snapshot_tag
```

---

## Best Practices

!!! tip "Snapshot Monitoring Guidelines"
    1. **Regular checks** - Include in daily monitoring
    2. **Set retention alerts** - Alert when snapshots age
    3. **Track total size** - Monitor growth trends
    4. **Clean up promptly** - Remove snapshots after backup verification
    5. **Use TTL snapshots** - Auto-delete when possible (4.0+)
    6. **Document naming** - Use consistent, dated snapshot names

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [snapshot](snapshot.md) | Create snapshots |
| [clearsnapshot](clearsnapshot.md) | Remove snapshots |
| [tablestats](tablestats.md) | Table-level statistics |
