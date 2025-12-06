# nodetool ring

Displays the token ring topology, showing token ownership for each node.

## Synopsis

```bash
nodetool [connection_options] ring [keyspace]
```

## Description

The `ring` command displays the token ring topology, showing which nodes own which token ranges. This provides visibility into data distribution across the cluster.

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| keyspace | No | Display ownership based on keyspace replication strategy |

## Examples

```bash
# Display token ring
nodetool ring

# For specific keyspace
nodetool ring my_keyspace
```

**Output:**
```
Datacenter: dc1
==========
Address        Rack   Status State   Load           Owns   Token
                                                           9223372036854775807
10.0.0.1       rack1  Up     Normal  156.23 GiB     33.2%  -9223372036854775808
10.0.0.2       rack2  Up     Normal  152.87 GiB     33.5%  -6148914691236517206
10.0.0.3       rack3  Up     Normal  158.44 GiB     33.3%  -3074457345618258604
```

## Related Commands

- [status](status.md) - Cluster status overview
- [describecluster](describecluster.md) - Cluster configuration

## Related Documentation

- [Architecture - Data Distribution](../../../architecture/data-distribution.md)
