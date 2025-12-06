# nodetool bootstrap

Manages bootstrap operations for nodes joining the cluster.

## Synopsis

```bash
nodetool [connection_options] bootstrap resume
```

## Description

The `bootstrap` command manages the bootstrap process when a new node joins the cluster. The `resume` subcommand continues a failed or interrupted bootstrap.

## Subcommands

| Subcommand | Description |
|------------|-------------|
| resume | Resume an interrupted bootstrap |

## Examples

```bash
# Resume interrupted bootstrap
nodetool bootstrap resume
```

## Related Commands

- [netstats](netstats.md) - Monitor streaming progress
- [status](status.md) - Check node join status

## Related Documentation

- [Operations - Cluster Management](../../../operations/cluster-management/index.md)
- [Operations - Adding Nodes](../../../operations/cluster-management/adding-nodes.md)
