# nodetool clearsnapshot

Removes snapshot files to reclaim disk space.

## Synopsis

```bash
nodetool [connection_options] clearsnapshot [options]
```

## Description

The `clearsnapshot` command removes snapshot files, freeing disk space used by hard-linked SSTable copies.

## Options

| Option | Description |
|--------|-------------|
| -t, --tag &lt;name&gt; | Remove specific snapshot by tag |
| -- keyspace | Remove snapshots from specific keyspace |
| --all | Remove all snapshots |

## Examples

```bash
# Clear specific snapshot
nodetool clearsnapshot -t backup_20240115

# Clear all snapshots for keyspace
nodetool clearsnapshot -- my_keyspace

# Clear all snapshots
nodetool clearsnapshot --all
```

## Related Commands

- [snapshot](snapshot.md) - Create snapshots
- [listsnapshots](listsnapshots.md) - List snapshots

## Related Documentation

- [Operations - Backup & Restore](../../../operations/backup-restore/index.md)
