# nodetool setcompactionthroughput

Sets the compaction throughput limit.

## Synopsis

```bash
nodetool [connection_options] setcompactionthroughput <value>
```

## Description

The `setcompactionthroughput` command sets the maximum throughput for compaction operations in megabytes per second. This limits I/O impact during normal operations.

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| value | Yes | Throughput in MB/s (0 = unlimited) |

## Examples

```bash
# Set to 64 MB/s
nodetool setcompactionthroughput 64

# Set unlimited (not recommended for production)
nodetool setcompactionthroughput 0
```

## Recommended Values

| Scenario | Value |
|----------|-------|
| Production (mixed) | 64-128 MB/s |
| Maintenance window | 256-512 MB/s |
| SSD storage | 128-256 MB/s |
| HDD storage | 32-64 MB/s |

## Related Commands

- [getcompactionthroughput](getcompactionthroughput.md) - Get current value
- [compactionstats](compactionstats.md) - Monitor compaction

## Related Documentation

- [Architecture - Compaction](../../../architecture/storage-engine/compaction/index.md)
- [Configuration - cassandra.yaml](../../../operations/configuration/cassandra-yaml/index.md)
