# nodetool garbagecollect

Removes tombstones and expired data that have passed gc_grace_seconds.

## Synopsis

```bash
nodetool [connection_options] garbagecollect [options] [keyspace [table ...]]
```

## Description

The `garbagecollect` command removes deleted data (tombstones) that have exceeded the gc_grace_seconds threshold. This is more targeted than full compaction.

## Options

| Option | Description |
|--------|-------------|
| -g, --granularity | ROW or CELL level collection |
| -j, --jobs | Number of parallel jobs |

## Examples

```bash
# Row-level garbage collection
nodetool garbagecollect my_keyspace users

# Cell-level garbage collection
nodetool garbagecollect -g CELL my_keyspace users
```

## Related Commands

- [compact](compact.md) - Force compaction
- [tablestats](tablestats.md) - Check tombstone metrics

## Related Documentation

- [Architecture - Compaction](../../../architecture/compaction/index.md)
- [Troubleshooting - Tombstone Accumulation](../../../troubleshooting/playbooks/tombstone-accumulation.md)
