# nodetool move

Moves the node to a new token position in the ring.

---

## Synopsis

```bash
nodetool [connection_options] move <new_token>
```

## Description

`nodetool move` reassigns a node's token position in the cluster ring. This causes the node to stream data to/from other nodes to match its new token ownership. Moving a token changes which data the node is responsible for.

!!! warning "Disruptive Operation"
    Moving a node causes significant data streaming and temporarily affects cluster performance. Plan carefully and execute during maintenance windows.

!!! info "Single Token Only"
    This command only works with single-token nodes. Clusters using vnodes (virtual nodes, the modern default) cannot use this command.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `new_token` | The new token value for this node |

---

## Examples

### Move to New Token

```bash
nodetool move 1234567890
```

### On Remote Node

```bash
nodetool -h 192.168.1.100 move 1234567890
```

---

## Prerequisites

### Single Token Configuration

This command requires single-token configuration:

```yaml
# cassandra.yaml
num_tokens: 1
initial_token: <token_value>
```

### Not Compatible with vnodes

If using vnodes (num_tokens > 1), you'll see:

```
Error: Cannot move a node with vnodes
```

---

## When to Use

### Rebalancing Token Ring

To redistribute data more evenly:

```bash
# Check current token distribution
nodetool ring

# Calculate new token for better distribution
# Move node to new position
nodetool move <calculated_token>
```

### Correcting Token Placement

After incorrect initial token assignment:

```bash
# View current token
nodetool info | grep Token

# Move to correct position
nodetool move <correct_token>
```

---

## Process Flow

```
Token Move Process:

1. Execute move command
2. Node calculates new token ranges
3. Streams out data no longer owned
4. Streams in data now owned
5. Updates token in gossip
6. Move complete
```

---

## Monitoring

### During Move

```bash
# Watch streaming progress
watch -n 5 'nodetool netstats'

# Check node status
nodetool status
```

### Verify Completion

```bash
# Check new token
nodetool info | grep Token

# Verify ring
nodetool ring
```

---

## Impact Assessment

| Aspect | Impact |
|--------|--------|
| Disk I/O | High (streaming) |
| Network | High (data transfer) |
| CPU | Moderate |
| Query latency | May increase during move |
| Duration | Minutes to hours |

---

## Troubleshooting

### Move Fails with vnodes

```
Error: Cannot move a node with vnodes
```

Cannot use move with vnodes. For vnode clusters, use `nodetool decommission` and add new node, or use `nodetool rebuild`.

### Move Interrupted

```bash
# Check streaming status
nodetool netstats

# Node may be in inconsistent state
# May need to decommission and rejoin
```

### Data Inconsistency After Move

```bash
# Run repair after move completes
nodetool repair -pr
```

---

## Best Practices

!!! tip "Move Guidelines"

    1. **Plan token values** - Calculate optimal distribution
    2. **Maintenance window** - Perform during low traffic
    3. **Monitor streaming** - Watch netstats during move
    4. **Repair after** - Run repair to ensure consistency
    5. **One at a time** - Move one node before starting another

!!! warning "Considerations"

    - Only works with single-token configuration
    - High network and disk impact
    - May take extended time for large datasets
    - Consider decommission/add instead for major changes

---

## Token Calculation

### Even Distribution Formula

For N nodes with single tokens:

```
Token for node i = (i * (2^63 * 2)) / N
```

### Example: 4 Node Cluster

```
Node 0: 0
Node 1: 4611686018427387904
Node 2: 9223372036854775808
Node 3: 13835058055282163712
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [ring](ring.md) | View token ring |
| [info](info.md) | View node's current token |
| [decommission](decommission.md) | Remove node from cluster |
| [netstats](netstats.md) | Monitor streaming |
| [status](status.md) | View cluster status |
