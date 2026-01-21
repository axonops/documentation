---
title: "nodetool ring"
description: "Display token ring information for Cassandra cluster using nodetool ring command."
meta:
  - name: keywords
    content: "nodetool ring, token ring, Cassandra ring, cluster topology"
search:
  boost: 3
---

# nodetool ring

Displays the token ring information showing token assignments for each node in the cluster.

---

## Synopsis

```bash
nodetool [connection_options] ring [keyspace]
```

## Description

`nodetool ring` displays detailed token ring information including:

- Token values assigned to each node
- Node addresses and their datacenter/rack placement
- Load and ownership statistics

This command is useful for understanding data distribution and troubleshooting token-related issues.

### Understanding Virtual Nodes (vnodes)

In modern Cassandra deployments, each node owns multiple **virtual nodes (vnodes)** rather than a single token. The number of vnodes per node is configured in `cassandra.yaml`:

```yaml
num_tokens: 16    # Default in Cassandra 4.0+
                   # Older versions defaulted to 256, some used 16
```

With vnodes enabled, `nodetool ring` output shows one row per token, meaning a 3-node cluster with `num_tokens: 256` displays 768 rows (256 × 3 nodes). Each row represents a token range boundary owned by a node.

```bash
# Count tokens per node
nodetool ring | grep -c "192.168.1.101"
# Output: 16 (if num_tokens: 16)
```

**Why vnodes matter:**

| Aspect | Single Token (Legacy) | Virtual Nodes |
|--------|----------------------|---------------|
| Tokens per node | 1 | Typically 16-256 |
| Data distribution | Can be uneven | More uniform |
| Adding nodes | Large data movement | Smaller, distributed transfers |
| Removing nodes | Large data movement | Smaller, distributed transfers |
| Streaming impact | High (all data at once) | Lower (distributed) |
| Hot spots | More likely | Less likely |

!!! tip "Checking vnode Configuration"
    ```bash
    # Check num_tokens setting
    grep num_tokens /etc/cassandra/cassandra.yaml

    # Verify tokens per node in the cluster
    nodetool ring | awk '{print $1}' | sort | uniq -c | sort -rn
    ```

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | Optional. Show ownership for specific keyspace's replication strategy |

---

## Output Format

```
Datacenter: dc1
==========
Address          Rack        Status  State   Load            Owns                Token
                                                                                 9223372036854775807
192.168.1.101    rack1       Up      Normal  256.12 GiB      33.33%              -9223372036854775808
192.168.1.102    rack2       Up      Normal  248.87 GiB      33.34%              -6148914691236517206
192.168.1.103    rack3       Up      Normal  251.44 GiB      33.33%              -3074457345618258604
192.168.1.101    rack1       Up      Normal  256.12 GiB      33.33%              -2
192.168.1.102    rack2       Up      Normal  248.87 GiB      33.34%              3074457345618258600
192.168.1.103    rack3       Up      Normal  251.44 GiB      33.33%              6148914691236517202
```

---

## Output Fields

| Field | Description |
|-------|-------------|
| Address | IP address of the node |
| Rack | Rack assignment from snitch |
| Status | Up or Down |
| State | Normal, Leaving, Joining, or Moving |
| Load | Data size on this node |
| Owns | Percentage ownership of data |
| Token | Token value (end of range owned) |

---

## Examples

### Basic Usage

```bash
nodetool ring
```

Displays all tokens for all nodes.

### Keyspace-Specific

```bash
nodetool ring my_keyspace
```

Shows ownership percentages based on the keyspace's replication factor.

### Count Tokens Per Node

```bash
nodetool ring | grep "192.168.1.101" | wc -l
```

Counts the number of tokens (vnodes) for a specific node.

### Extract Token List for a Node

```bash
nodetool ring | grep "192.168.1.101" | awk '{print $NF}'
```

Lists all tokens owned by a specific node.

---

## Understanding Token Ranges

### Token Distribution

Each token value represents the **end** of a range that a node owns:

| Node | Token | Range Owned |
|------|-------|-------------|
| Node A | -3074... | From previous token to -3074... |
| Node B | -6148... | From previous token to -6148... |
| Node C | -4611... | From previous token to -4611... |

With vnodes, each node owns multiple non-contiguous ranges distributed around the ring for better load balancing.

### How Tokens Work

Each token value represents the **end** of a range that a node owns. Data with partition tokens up to and including this value is stored on this node.

```
Node A owns token -3074457345618258604
Node B owns token -6148914691236517206

Range for Node A: -6148914691236517206 < token <= -3074457345618258604
```

---

## Interpreting Results

### Healthy Distribution

With vnodes enabled (recommended), tokens should be:

- Evenly distributed across nodes
- Each node has the same number of tokens (typically 256)
- Ownership percentages roughly equal

### Single-Token Setup (Legacy)

```
192.168.1.101    rack1       Up      Normal  256.12 GiB      33.33%   0
192.168.1.102    rack2       Up      Normal  248.87 GiB      33.34%   3074457345618258602
192.168.1.103    rack3       Up      Normal  251.44 GiB      33.33%   6148914691236517204
```

!!! warning "Single Token Nodes"
    Single-token setups (one token per node) are legacy configurations. They:

    - Make adding/removing nodes very disruptive
    - Can cause uneven data distribution
    - Should be migrated to vnodes for new clusters

### Uneven Token Distribution

If ownership percentages vary significantly (>5%):

| Cause | Solution |
|-------|----------|
| Different `num_tokens` settings | Standardize configuration |
| Manual token assignment issues | Use vnode auto-assignment |
| Recent topology changes | Wait for streaming to complete |

---

## When to Use

| Scenario | Purpose |
|----------|---------|
| Debugging data distribution | Understand which nodes own what ranges |
| Planning node additions | See current token landscape |
| Investigating hot spots | Identify if specific ranges are overloaded |
| Migration planning | Document current token assignments |
| Troubleshooting queries | Understand why queries hit specific nodes |

---

## When NOT to Use

!!! note "Prefer Other Commands"
    - **For quick health checks**: Use `nodetool status` instead
    - **For replica locations**: Use `nodetool getendpoints` for specific keys
    - **For continuous monitoring**: Use metrics, not manual commands

---

## Ring Output with Multiple Datacenters

```
Datacenter: dc1
==========
Address          Rack        Status  State   Load            Owns    Token
192.168.1.101    rack1       Up      Normal  256.12 GiB      16.67%  -9223372036854775808
192.168.1.102    rack2       Up      Normal  248.87 GiB      16.67%  -3074457345618258604

Datacenter: dc2
==========
Address          Rack        Status  State   Load            Owns    Token
192.168.2.101    rack1       Up      Normal  256.12 GiB      16.67%  -9223372036854775808
192.168.2.102    rack2       Up      Normal  248.87 GiB      16.67%  -3074457345618258604
```

With `NetworkTopologyStrategy` and multiple datacenters:

- Tokens may overlap across DCs (same token in different DCs)
- Each DC manages its own replica set
- Ownership percentages reflect global distribution

---

## Verbose Output

For more detailed output including Host IDs:

```bash
nodetool describering my_keyspace
```

This shows token ranges with start and end tokens plus replica endpoints.

---

## Common Issues

### Ring Shows Wrong Ownership

```
Owns: ?
```

Ownership calculation requires a keyspace with defined replication:

```bash
nodetool ring my_keyspace
```

### Missing Nodes in Ring

If a node doesn't appear in the ring output:

1. Check if node is running
2. Verify `nodetool status` shows the node
3. Check for gossip issues with `nodetool gossipinfo`

### Duplicate Tokens

Duplicate tokens across nodes (same DC) indicate configuration errors:

!!! danger "Duplicate Tokens"
    Duplicate tokens cause data inconsistency. Never manually assign the same token to multiple nodes in the same datacenter.

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [status](status.md) | Simpler cluster overview |
| [getendpoints](getendpoints.md) | Find replicas for specific key |
| [info](info.md) | Single node details |
