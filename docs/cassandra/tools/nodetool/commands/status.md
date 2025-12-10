# nodetool status

Displays the state of all nodes in the cluster, including ownership percentages, load distribution, and node health.

## Synopsis

```bash
nodetool [connection_options] status [keyspace]
```

## Description

The `status` command provides a comprehensive view of cluster topology and health. It displays each node's operational state, data load, token ownership, and datacenter/rack assignment. This command is typically the first diagnostic tool used when assessing cluster health.

The output is organized by datacenter, with each node represented on a single line showing its current status and key metrics.

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| keyspace | No | When specified, displays effective ownership percentages calculated using the keyspace's replication strategy. Without this parameter, ownership is calculated assuming uniform replication. |

## Connection Options

| Option | Description |
|--------|-------------|
| -h, --host | Hostname or IP address to connect to (default: localhost) |
| -p, --port | JMX port number (default: 7199) |
| -u, --username | JMX username for authentication |
| -pw, --password | JMX password for authentication |
| -pwf, --password-file | Path to file containing JMX password |

## Output Format

The output consists of a header section followed by node entries:

```
Datacenter: <datacenter_name>
=======================
Status=Up/Down
|/ State=Normal/Leaving/Joining/Moving
--  Address        Load       Tokens  Owns (effective)  Host ID                               Rack
```

### Output Fields

| Field | Description |
|-------|-------------|
| Status (U/D) | **U** = Up (node is responding to gossip), **D** = Down (node is not responding) |
| State (N/L/J/M) | **N** = Normal operation, **L** = Leaving cluster, **J** = Joining cluster, **M** = Moving tokens |
| Address | IP address of the node |
| Load | Total size of data stored on the node (compressed, on-disk size) |
| Tokens | Number of tokens (vnodes) assigned to the node |
| Owns | Percentage of the token ring owned by this node |
| Host ID | Universally unique identifier (UUID) for the node |
| Rack | Rack designation within the datacenter for topology awareness |

## Examples

### Basic Cluster Status

```bash
nodetool status
```

**Output:**
```
Datacenter: dc1
===============
Status=Up/Down
|/ State=Normal/Leaving/Joining/Moving
--  Address        Load        Tokens  Owns (effective)  Host ID                               Rack
UN  10.0.0.1       156.23 GiB  256     33.2%             a1b2c3d4-e5f6-7890-abcd-ef1234567890  rack1
UN  10.0.0.2       152.87 GiB  256     33.5%             b2c3d4e5-f6a7-8901-bcde-f12345678901  rack2
UN  10.0.0.3       158.44 GiB  256     33.3%             c3d4e5f6-a7b8-9012-cdef-123456789012  rack3
```

### Status for Specific Keyspace

```bash
nodetool status my_keyspace
```

When a keyspace is specified, the "Owns" column reflects effective ownership based on the keyspace's replication factor and strategy.

### Multi-Datacenter Cluster

```
Datacenter: dc1
===============
Status=Up/Down
|/ State=Normal/Leaving/Joining/Moving
--  Address        Load        Tokens  Owns (effective)  Host ID                               Rack
UN  10.0.0.1       156.23 GiB  256     33.2%             a1b2c3d4-e5f6-7890-abcd-ef1234567890  rack1
UN  10.0.0.2       152.87 GiB  256     33.5%             b2c3d4e5-f6a7-8901-bcde-f12345678901  rack2
UN  10.0.0.3       158.44 GiB  256     33.3%             c3d4e5f6-a7b8-9012-cdef-123456789012  rack3

Datacenter: dc2
===============
Status=Up/Down
|/ State=Normal/Leaving/Joining/Moving
--  Address        Load        Tokens  Owns (effective)  Host ID                               Rack
UN  10.0.1.1       148.92 GiB  256     33.1%             d4e5f6a7-b8c9-0123-defa-234567890123  rack1
UN  10.0.1.2       151.33 GiB  256     33.6%             e5f6a7b8-c9d0-1234-efab-345678901234  rack2
DN  10.0.1.3       N/A         256     33.3%             f6a7b8c9-d0e1-2345-fabc-456789012345  rack3
```

## Interpreting Results

### Status Codes

| Code | Meaning | Action Required |
|------|---------|-----------------|
| UN | Up and Normal | No action required - healthy state |
| DN | Down and Normal | Investigate immediately - node unreachable |
| UJ | Up and Joining | Node is bootstrapping - monitor progress |
| UL | Up and Leaving | Node is decommissioning - monitor progress |
| UM | Up and Moving | Token migration in progress |

### Warning Indicators

| Condition | Indication | Investigation |
|-----------|------------|---------------|
| Any node showing DN | Node failure or network partition | Check node logs, network connectivity |
| Load imbalance > 10% | Uneven data distribution | Review token allocation, check for hot partitions |
| Missing nodes | Nodes not appearing in output | Check gossip state with [gossipinfo](gossipinfo.md) |
| Multiple nodes in J/L/M state | Concurrent topology operations | Verify operations are intentional |

### Load Imbalance Calculation

Load imbalance can be calculated as:

```
imbalance = (max_load - min_load) / average_load * 100
```

A healthy cluster should maintain imbalance below 10%. Persistent imbalance may indicate:
- Uneven token distribution
- Hot partition keys directing traffic to specific nodes
- Misconfigured `num_tokens` across nodes

## Common Use Cases

### Health Check Script

```bash
#!/bin/bash
# Check for any down nodes
DOWN_NODES=$(nodetool status | grep "^DN" | wc -l)
if [ $DOWN_NODES -gt 0 ]; then
    echo "CRITICAL: $DOWN_NODES nodes are down"
    nodetool status | grep "^DN"
    exit 2
fi
echo "OK: All nodes operational"
```

### Monitoring Integration

```bash
# Extract node count by status for monitoring
nodetool status | awk '
    /^UN/ {up++}
    /^DN/ {down++}
    /^UJ/ {joining++}
    /^UL/ {leaving++}
    END {
        print "up=" up
        print "down=" down
        print "joining=" joining
        print "leaving=" leaving
    }
'
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Command executed successfully |
| 1 | Error connecting to JMX or executing command |
| 2 | Invalid arguments |

## Related Commands

- [nodetool info](info.md) - Detailed information about a single node
- [nodetool ring](ring.md) - Token ring topology details
- [nodetool describecluster](describecluster.md) - Cluster-wide configuration
- [nodetool gossipinfo](gossipinfo.md) - Gossip protocol state

## Version Information

This command is available in all Apache Cassandra versions. Output format is consistent across Cassandra 4.x and 5.x releases.
