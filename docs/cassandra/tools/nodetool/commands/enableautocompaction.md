# nodetool enableautocompaction

Enables automatic compaction for specified tables.

## Synopsis

```bash
nodetool [connection_options] enableautocompaction [keyspace [table ...]]
```

## Description

The `enableautocompaction` command re-enables automatic compaction for tables where it was previously disabled.

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| keyspace | No | Keyspace to enable compaction for |
| table | No | Specific table(s) to enable |

## Examples

```bash
# Enable for specific table
nodetool enableautocompaction my_keyspace users

# Enable for all tables in keyspace
nodetool enableautocompaction my_keyspace

# Enable for all tables
nodetool enableautocompaction
```

## Related Commands

- [disableautocompaction](disableautocompaction.md) - Disable compaction
- [compactionstats](compactionstats.md) - Monitor compaction

## Related Documentation

- [Architecture - Compaction](../../../architecture/compaction/index.md)
