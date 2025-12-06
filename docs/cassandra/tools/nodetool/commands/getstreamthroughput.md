# nodetool getstreamthroughput

Gets the current streaming throughput limit.

## Synopsis

```bash
nodetool [connection_options] getstreamthroughput
```

## Description

The `getstreamthroughput` command displays the current maximum throughput setting for streaming operations.

## Examples

```bash
nodetool getstreamthroughput
```

**Output:**
```
Current stream throughput: 200 Mb/s
```

## Related Commands

- [setstreamthroughput](setstreamthroughput.md) - Set throughput
- [netstats](netstats.md) - Monitor streaming

## Related Documentation

- [Operations - Repair](../../../operations/repair/index.md)
