# nodetool disableautocompaction

Disables automatic compaction for specified tables.

## Synopsis

```bash
nodetool [connection_options] disableautocompaction [keyspace [table ...]]
```

## Description

The `disableautocompaction` command stops automatic compaction for the specified tables. Use before bulk loading or during troubleshooting.

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| keyspace | No | Keyspace to disable compaction for |
| table | No | Specific table(s) to disable |

## Examples

```bash
# Disable for specific table
nodetool disableautocompaction my_keyspace users

# Disable for all tables in keyspace
nodetool disableautocompaction my_keyspace
```

## Use Cases

- Before bulk data loading
- During maintenance windows
- Troubleshooting compaction issues

## Related Commands

- [enableautocompaction](enableautocompaction.md) - Re-enable compaction
- [compact](compact.md) - Manual compaction
- [compactionstats](compactionstats.md) - Monitor status

## Related Documentation

- [Architecture - Compaction](../../../architecture/compaction/index.md)
