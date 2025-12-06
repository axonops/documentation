# nodetool listsnapshots

Lists all snapshots on the local node.

## Synopsis

```bash
nodetool [connection_options] listsnapshots
```

## Description

The `listsnapshots` command displays all snapshots present on the local node, including size and creation time.

## Examples

```bash
nodetool listsnapshots
```

**Output:**
```
Snapshot Details:
Snapshot name       Keyspace name  Column family name  True size  Size on disk  Creation time
daily_backup        my_keyspace    users              1.5 GiB     1.8 GiB       2024-01-15T10:30:00Z
daily_backup        my_keyspace    orders             2.3 GiB     2.8 GiB       2024-01-15T10:30:00Z

Total TrueDiskSpaceUsed: 3.8 GiB
```

## Output Fields

| Field | Description |
|-------|-------------|
| Snapshot name | Tag assigned to the snapshot |
| True size | Actual data size |
| Size on disk | Disk space used |
| Creation time | When snapshot was created |

## Related Commands

- [snapshot](snapshot.md) - Create snapshots
- [clearsnapshot](clearsnapshot.md) - Remove snapshots

## Related Documentation

- [Operations - Backup & Restore](../../../operations/backup-restore/index.md)
