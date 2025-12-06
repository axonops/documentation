# nodetool refresh

Loads new SSTables from the data directory without restart.

## Synopsis

```bash
nodetool [connection_options] refresh <keyspace> <table>
```

## Description

The `refresh` command loads SSTables that have been added to the table's data directory, making them available for queries without restarting Cassandra. This is useful after restoring data from snapshots.

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| keyspace | Yes | Keyspace name |
| table | Yes | Table name |

## Examples

```bash
# After copying SSTable files to data directory
nodetool refresh my_keyspace users
```

## Use Cases

- Loading restored snapshot data
- Loading SSTables from external sources
- Hot-loading bulk import data

## Related Commands

- [snapshot](snapshot.md) - Create snapshots
- [flush](flush.md) - Flush memtables

## Related Documentation

- [Operations - Backup & Restore](../../../operations/backup-restore/index.md)
