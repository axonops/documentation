# nodetool rebuild

Streams all data from another datacenter.

## Synopsis

```bash
nodetool [connection_options] rebuild [options] <source_datacenter>
```

## Description

The `rebuild` command streams all data from an existing datacenter. Used when adding a new datacenter or replacing all nodes in a datacenter.

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| source_datacenter | Yes | Datacenter to stream data from |

## Options

| Option | Description |
|--------|-------------|
| -ks, --keyspace | Rebuild specific keyspace |
| -ts, --tokens | Rebuild specific token ranges |
| -m, --mode | Rebuild mode (normal, refetch, reset) |

## Examples

```bash
# Rebuild from existing datacenter
nodetool rebuild dc1

# Rebuild specific keyspace
nodetool rebuild -ks my_keyspace dc1
```

## Use Cases

- Adding a new datacenter
- Replacing all nodes in a datacenter
- Recovering from data loss

## Related Commands

- [netstats](netstats.md) - Monitor streaming progress
- [status](status.md) - Check cluster state

## Related Documentation

- [Multi-Datacenter](../../../multi-datacenter/index.md)
- [Operations - Cluster Management](../../../operations/cluster-management/index.md)
