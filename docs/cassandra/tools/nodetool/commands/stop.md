# nodetool stop

Stops a running compaction operation.

## Synopsis

```bash
nodetool [connection_options] stop <type>
```

## Description

The `stop` command halts a running compaction or other background operation.

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| type | Yes | Operation type to stop |

## Operation Types

| Type | Description |
|------|-------------|
| COMPACTION | Stop compaction |
| CLEANUP | Stop cleanup |
| SCRUB | Stop scrub |
| UPGRADE_SSTABLES | Stop SSTable upgrade |
| VERIFY | Stop verification |

## Examples

```bash
# Stop compaction
nodetool stop COMPACTION

# Stop cleanup
nodetool stop CLEANUP
```

## Note

Stopping compaction may leave partially written SSTables that will be cleaned up on restart.

## Related Commands

- [compact](compact.md) - Force compaction
- [compactionstats](compactionstats.md) - View active compactions

## Related Documentation

- [Architecture - Compaction](../../../architecture/compaction/index.md)
