# nodetool version

Displays the Cassandra version running on the node.

## Synopsis

```bash
nodetool [connection_options] version
```

## Description

The `version` command displays the Apache Cassandra version running on the connected node.

## Examples

```bash
nodetool version
```

**Output:**
```
ReleaseVersion: 4.1.3
```

## Related Commands

- [info](info.md) - Detailed node information
- [describecluster](describecluster.md) - Cluster-wide version info
