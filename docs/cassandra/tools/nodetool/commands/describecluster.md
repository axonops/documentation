# nodetool describecluster

Displays cluster configuration and schema version information.

## Synopsis

```bash
nodetool [connection_options] describecluster
```

## Description

The `describecluster` command shows cluster-wide configuration including the cluster name, snitch, and schema versions across all nodes. This is essential for detecting schema disagreements.

## Examples

```bash
nodetool describecluster
```

**Output:**
```
Cluster Information:
	Name: ProductionCluster
	Snitch: org.apache.cassandra.locator.GossipingPropertyFileSnitch
	DynamicEndPointSnitch: enabled
	DatabaseVersion: 4.1.3
Schema versions:
	a1b2c3d4-e5f6-7890-abcd-ef1234567890: [10.0.0.1, 10.0.0.2, 10.0.0.3]
```

## Interpreting Results

- All nodes should report the same schema version UUID
- Multiple schema versions indicate a schema disagreement
- `UNREACHABLE` nodes cannot participate in schema changes

## Related Commands

- [status](status.md) - Cluster status
- [gossipinfo](gossipinfo.md) - Gossip state

## Related Documentation

- [Troubleshooting - Schema Disagreement](../../../troubleshooting/playbooks/schema-disagreement.md)
