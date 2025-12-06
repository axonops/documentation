# nodetool getcompactionthroughput

Gets the current compaction throughput limit.

## Synopsis

```bash
nodetool [connection_options] getcompactionthroughput
```

## Description

The `getcompactionthroughput` command displays the current maximum throughput setting for compaction operations.

## Examples

```bash
nodetool getcompactionthroughput
```

**Output:**
```
Current compaction throughput: 64 MB/s
```

## Related Commands

- [setcompactionthroughput](setcompactionthroughput.md) - Set throughput
- [compactionstats](compactionstats.md) - Monitor compaction

## Related Documentation

- [Architecture - Compaction](../../../architecture/compaction/index.md)
