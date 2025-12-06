# nodetool setstreamthroughput

Sets the streaming throughput limit.

## Synopsis

```bash
nodetool [connection_options] setstreamthroughput <value>
```

## Description

The `setstreamthroughput` command sets the maximum throughput for streaming operations (repair, rebuild, bootstrap) in megabits per second.

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| value | Yes | Throughput in Mbps (0 = unlimited) |

## Examples

```bash
# Set to 200 Mbps
nodetool setstreamthroughput 200
```

## Related Commands

- [getstreamthroughput](getstreamthroughput.md) - Get current value
- [netstats](netstats.md) - Monitor streaming

## Related Documentation

- [Operations - Repair](../../../operations/repair/index.md)
- [Configuration - cassandra.yaml](../../../configuration/cassandra-yaml/index.md)
