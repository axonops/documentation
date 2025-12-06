# nodetool removenode

Removes a dead node from the cluster.

## Synopsis

```bash
nodetool [connection_options] removenode <host_id|status|force>
```

## Description

The `removenode` command removes a dead (unreachable) node from the cluster by reassigning its token ranges to remaining nodes. Run this from any surviving node.

## Parameters

| Parameter | Description |
|-----------|-------------|
| host_id | UUID of the node to remove |
| status | Show status of current removenode operation |
| force | Force removal even if replicas are unavailable |

## Examples

```bash
# Get host ID of dead node
nodetool status

# Remove the dead node
nodetool removenode a1b2c3d4-e5f6-7890-abcd-ef1234567890

# Check progress
nodetool removenode status

# Force remove if stuck
nodetool removenode force a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

## Prerequisites

- Node must be down (status DN)
- Sufficient replicas available
- Run from any surviving node

## Related Commands

- [decommission](decommission.md) - Remove live node
- [assassinate](assassinate.md) - Force remove from gossip
- [status](status.md) - Get host IDs

## Related Documentation

- [Operations - Cluster Management](../../../operations/cluster-management/index.md)
- [Troubleshooting - Replace Dead Node](../../../troubleshooting/playbooks/replace-dead-node.md)
