# nodetool assassinate

Forcibly removes a node from gossip.

## Synopsis

```bash
nodetool [connection_options] assassinate <ip_address>
```

## Description

The `assassinate` command forcibly removes a node from the gossip ring. Use only as a last resort when `removenode` fails.

**Warning:** This does not stream data. Data on the assassinated node may be lost if insufficient replicas exist.

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| ip_address | Yes | IP address of node to remove |

## Examples

```bash
nodetool assassinate 10.0.0.4
```

## When to Use

- `removenode` fails repeatedly
- Node cannot be recovered
- Data loss is acceptable

## Related Commands

- [removenode](removenode.md) - Remove dead node (preferred)
- [decommission](decommission.md) - Remove live node
- [status](status.md) - Check cluster state

## Related Documentation

- [Troubleshooting - Replace Dead Node](../../../troubleshooting/playbooks/replace-dead-node.md)
