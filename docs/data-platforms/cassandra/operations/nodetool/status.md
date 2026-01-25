---
title: "nodetool status"
description: "Display cluster status showing all nodes, their state, load, and ownership using nodetool status."
meta:
  - name: keywords
    content: "nodetool status, cluster status, node status, Cassandra cluster health"
---

# nodetool status

Displays the status of all nodes in the cluster, including their state, load, token ownership, and datacenter/rack placement.

---

## Synopsis

```bash
nodetool [connection_options] status [keyspace]
```

## Description

`nodetool status` provides a quick overview of cluster health by showing each node's:

- **State** (Up/Down, Normal/Leaving/Joining/Moving)
- **Load** (data size on disk)
- **Token ownership** percentage
- **Host ID** (unique identifier)
- **IP address**
- **Rack** placement

This is typically the first command run when checking cluster health.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | Optional. Show ownership percentages for specific keyspace |

## Options

| Option | Description |
|--------|-------------|
| `-r, --resolve-ip` | Show hostnames instead of IP addresses |
| `-s, --sort` | Sort output by a column (address, state, load, owns, host_id) |
| `-o, --order` | Order direction: `asc` or `desc` (default: asc) |

---

## Output Format

```
Datacenter: dc1
===============
Status=Up/Down
|/ State=Normal/Leaving/Joining/Moving
--  Address        Load       Tokens  Owns (effective)  Host ID                               Rack
UN  192.168.1.101  256.12 GiB  256    33.3%             a1b2c3d4-e5f6-7890-abcd-ef1234567890  rack1
UN  192.168.1.102  248.87 GiB  256    33.4%             b2c3d4e5-f6a7-8901-bcde-f12345678901  rack2
UN  192.168.1.103  251.44 GiB  256    33.3%             c3d4e5f6-a7b8-9012-cdef-123456789012  rack3
```

### Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| `U` | Up | Node is responding to gossip |
| `D` | Down | Node is not responding |

### State Codes

| Code | Meaning | Description |
|------|---------|-------------|
| `N` | Normal | Node is operating normally |
| `L` | Leaving | Node is being decommissioned |
| `J` | Joining | Node is bootstrapping |
| `M` | Moving | Node is moving to new token |

### Status Combinations

| Status | Meaning | Action |
|--------|---------|--------|
| `UN` | Up and Normal | Healthy state |
| `DN` | Down and Normal | Node is down, investigate |
| `UL` | Up and Leaving | Decommission in progress |
| `UJ` | Up and Joining | Bootstrap in progress |
| `UM` | Up and Moving | Token move in progress |

---

## Examples

### Basic Usage

```bash
nodetool status
```

Displays status for all keyspaces.

### Keyspace-Specific Ownership

```bash
nodetool status my_keyspace
```

Shows token ownership percentages calculated for the specified keyspace's replication factor.

!!! info "Ownership Calculation"
    Without a keyspace, ownership is calculated assuming RF=1. With a keyspace, ownership reflects effective ownership based on that keyspace's replication strategy.

### Scripting with Status

Check if all nodes are up:

```bash
nodetool status | grep -c "^UN"
```

Check for any down nodes:

```bash
nodetool status | grep "^DN"
```

---

## Output Fields

| Field | Description |
|-------|-------------|
| Address | IP address of the node |
| Load | Total data size on the node (all keyspaces) |
| Tokens | Number of tokens (vnodes) assigned |
| Owns | Percentage of data this node is responsible for |
| Host ID | UUID uniquely identifying this node |
| Rack | Rack name from snitch configuration |

---

## Interpreting Results

### Healthy Cluster

```
Datacenter: dc1
===============
UN  192.168.1.101  256.12 GiB  256    33.3%  ...  rack1
UN  192.168.1.102  248.87 GiB  256    33.4%  ...  rack2
UN  192.168.1.103  251.44 GiB  256    33.3%  ...  rack3
```

- All nodes `UN` (Up/Normal)
- Load relatively balanced (within ~5% variation)
- Ownership evenly distributed

### Unbalanced Load

```
UN  192.168.1.101  512.00 GiB  256    33.3%  ...  rack1
UN  192.168.1.102  128.00 GiB  256    33.4%  ...  rack2
UN  192.168.1.103  256.00 GiB  256    33.3%  ...  rack3
```

!!! warning "Load Imbalance"
    Significant load variation (>20%) with similar ownership percentages may indicate:

    - Large partitions on some nodes
    - Uneven data distribution from hot partition keys
    - Different compaction states across nodes

### Node Down

```
UN  192.168.1.101  256.12 GiB  256    33.3%  ...  rack1
DN  192.168.1.102  248.87 GiB  256    33.4%  ...  rack2
UN  192.168.1.103  251.44 GiB  256    33.3%  ...  rack3
```

!!! danger "Node Down"
    A `DN` status requires immediate investigation:

    1. Check if Cassandra process is running on the node
    2. Check system logs (`/var/log/cassandra/system.log`)
    3. Verify network connectivity
    4. Check disk space and I/O errors

### Bootstrap in Progress

```
UN  192.168.1.101  256.12 GiB  256    25.0%  ...  rack1
UN  192.168.1.102  248.87 GiB  256    25.0%  ...  rack2
UN  192.168.1.103  251.44 GiB  256    25.0%  ...  rack3
UJ  192.168.1.104  64.00 GiB   256    25.0%  ...  rack1
```

The `UJ` node is joining the cluster and streaming data.

---

## Common Issues

### "Owns" Shows Question Marks

```
UN  192.168.1.101  256.12 GiB  256    ?      ...  rack1
```

!!! info "Unknown Ownership"
    Question marks appear when:

    - No keyspace is specified and effective ownership cannot be calculated
    - Schema disagreement exists between nodes

    Specify a keyspace: `nodetool status my_keyspace`

### Load Shows Zero

```
UN  192.168.1.101  0 bytes     256    33.3%  ...  rack1
```

Possible causes:

- Node just started and hasn't loaded data
- All data was dropped
- Metrics not yet available

### Inconsistent Token Counts

```
UN  192.168.1.101  256.12 GiB  256    33.3%  ...  rack1
UN  192.168.1.102  248.87 GiB  128    16.7%  ...  rack2
```

!!! warning "Token Count Mismatch"
    Different token counts indicate nodes were configured with different `num_tokens` values. This causes uneven data distribution.

---

## When to Use

| Scenario | Use Case |
|----------|----------|
| Health check | First command for any cluster investigation |
| Before maintenance | Verify all nodes are UN before operations |
| After adding nodes | Confirm new node reaches UN state |
| Capacity planning | Review load distribution |
| Incident response | Quick cluster state assessment |

---

## When NOT to Use

!!! note "Limitations"
    `nodetool status` shows point-in-time state. For:

    - **Continuous monitoring**: Use metrics (Prometheus, AxonOps)
    - **Detailed diagnostics**: Use `nodetool info`, `tpstats`, `tablestats`
    - **Historical analysis**: Use logging and metrics collection

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [info](info.md) | Detailed information for a single node |
| [ring](ring.md) | Token ring details |
| [gossipinfo](gossipinfo.md) | Gossip state details |
| [describecluster](describecluster.md) | Cluster metadata |
| [tpstats](tpstats.md) | Thread pool statistics |
