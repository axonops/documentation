---
title: "nodetool removenode"
description: "Remove a dead node from Cassandra cluster using nodetool removenode command."
meta:
  - name: keywords
    content: "nodetool removenode, remove node, dead node, Cassandra cluster"
search:
  boost: 3
---

# nodetool removenode

Removes a dead or unreachable node from the cluster by streaming its data from remaining replicas.

---

## Synopsis

```bash
nodetool [connection_options] removenode <status | force | <host-id>>
```

## Description

`nodetool removenode` removes a node that cannot be decommissioned because it is dead or unreachable. Unlike decommission (which runs on the node being removed), removenode runs from any live node and reconstructs the dead node's data from other replicas.

### What Removenode Does

When `removenode` executes, Cassandra performs the following operations:

1. **Removes token ownership** - The dead node's tokens are removed from the cluster's token ring. These tokens defined which partition ranges the node was responsible for.

2. **Updates the ring topology** - The cluster recalculates token range assignments. The removed node's token ranges are redistributed to the remaining nodes based on the token allocation strategy (vnode or single-token).

3. **Streams data from replicas** - For each partition range the dead node owned, data is streamed from surviving replicas to the nodes now responsible for those ranges. This ensures the cluster maintains the configured replication factor.

4. **Updates system tables** - The node's entry is removed from `system.peers` and other system tables across all nodes in the cluster.

5. **Propagates via gossip** - The removal is disseminated to all nodes via the gossip protocol, ensuring every node updates its local view of the cluster topology.

!!! info "Data Reconstruction Requirement"
    Since the dead node's data is unavailable, `removenode` relies entirely on replica nodes to reconstruct the data. If the replication factor is 1 (no replicas), or if all replicas for a partition range are unavailable, that data cannot be recovered and will be lost.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `status` | Show status of current removenode operation |
| `force` | Force completion of a stuck removenode |
| `<host-id>` | UUID of the node to remove |

---

## Finding the Host ID

```bash
# From nodetool status - shows host ID for all nodes
nodetool status

# Output includes Host ID column
# Datacenter: dc1
# Status=Up/Down
# |/ State=Normal/Leaving/Joining/Moving
# --  Address        Load       Tokens  Owns   Host ID                               Rack
# DN  192.168.1.102  248.87 GiB  256    33.3%  b2c3d4e5-f6a7-8901-bcde-f12345678901  rack1
```

The dead node shows `DN` (Down/Normal). Copy its Host ID.

---

## When to Use

### Node Hardware Failure

When a node's hardware fails and cannot be recovered:

```bash
nodetool removenode b2c3d4e5-f6a7-8901-bcde-f12345678901
```

### Node Cannot Start

When Cassandra cannot start on a node due to corruption or configuration issues that cannot be resolved:

```bash
nodetool removenode <host-id>
```

### Unplanned Node Loss

When a node is permanently lost (datacenter issue, etc.):

```bash
nodetool removenode <host-id>
```

---

## When NOT to Use

### Node is Still Alive

!!! danger "Don't Removenode Live Nodes"
    If the node is running (even if unhealthy):

    1. Try to repair the issue
    2. If removal needed, use `decommission` instead
    3. Never removenode a live node - causes data inconsistency

### Multiple Nodes Down

!!! danger "Data Loss Risk"
    If multiple replica nodes are down, removenode cannot reconstruct all data:

    ```
    RF=3, 2 nodes down → Data on only 1 replica
    RF=3, 3 nodes down → Complete data loss for some ranges
    ```

    Bring nodes back online if possible before removing any.

### Node Was Not Fully Down

If the node was intermittently available:

1. Ensure it's completely stopped
2. Remove from network
3. Then run removenode

---

## Removenode Process

1. Identify dead node by Host ID
2. Verify node is actually down
3. Calculate token ranges owned by dead node
4. Find remaining replicas for each range
5. Stream data from replicas to new owners (monitor with `nodetool netstats` and `nodetool removenode status`)
6. Update ring topology
7. Complete removal

---

## Examples

### Remove Dead Node

```bash
# Get host ID
nodetool status | grep DN

# Remove the node
nodetool removenode b2c3d4e5-f6a7-8901-bcde-f12345678901
```

### Check Removenode Status

```bash
nodetool removenode status
```

Output:
```
RemovalStatus: InProgress
Progress: 45%
Streams: 12 active, 8 completed
```

### Force Completion

```bash
nodetool removenode force
```

!!! danger "Force Removal"
    Only use `force` if removenode is stuck and you accept potential data loss. This completes the removal without waiting for all streams.

---

## Before Removenode

### Verify Node is Dead

```bash
# Should show DN (Down/Normal)
nodetool status

# Try to reach the node
ping <node-ip>
ssh <node-ip> 'nodetool info'
```

### Check Replication Factor

```bash
DESCRIBE KEYSPACE my_keyspace;
```

Ensure RF > 1 for data availability during removal.

### Verify Other Nodes Healthy

```bash
nodetool status
```

All other nodes should be UN (Up/Normal).

### Consider Consequences

| RF | Nodes | After Remove 1 | Risk |
|----|-------|----------------|------|
| 3 | 6 | 5 nodes, RF 3 | Safe |
| 3 | 4 | 3 nodes, RF 3 | Minimum |
| 3 | 3 | 2 nodes, RF 3 | **Cannot maintain RF** |

---

## During Removenode

### Monitor Progress

```bash
# Check removenode status
nodetool removenode status

# Watch streaming
nodetool netstats

# Check system logs
tail -f /var/log/cassandra/system.log | grep -i remove
```

### Do NOT

!!! danger "During Removenode"
    - Do NOT start the dead node
    - Do NOT run other topology changes
    - Do NOT start repairs
    - Do NOT restart live nodes

---

## After Removenode

### Verify Completion

```bash
nodetool status
```

The removed node should no longer appear.

### Run Repair

After removenode, run repair to ensure consistency:

```bash
# On each remaining node
nodetool repair -pr my_keyspace
```

---

## Common Issues

### "This host ID is not part of the ring"

The node was already removed or the Host ID is incorrect:

```bash
# Double-check Host ID
nodetool ring | grep <host-id>
```

### "Cannot remove node - not enough replicas"

Not enough live replicas to reconstruct data:

```bash
# Check how many nodes are up
nodetool status | grep UN

# May need to bring another node back online first
```

### Removenode Stuck

```bash
# Check status
nodetool removenode status

# Check for issues
nodetool netstats
tail /var/log/cassandra/system.log
```

If truly stuck:
```bash
# Force complete (data loss risk)
nodetool removenode force
```

### "Cannot removenode while bootstrapping"

Another node is joining. Wait for bootstrap to complete:

```bash
# Check for joining nodes
nodetool status | grep UJ

# Wait for UN status
```

---

## Removenode vs. Decommission vs. Assassinate

| Operation | Runs On | Use When |
|-----------|---------|----------|
| `decommission` | Node being removed | Node is alive |
| `removenode` | Any live node | Node is dead, data can be reconstructed |
| `assassinate` | Any live node | Removenode fails, node gossip state stuck |

### Decision Flow

| Question | Yes | No |
|----------|-----|-----|
| Is node responding? | Use `decommission` | Continue to next question |
| RF > 1 and other replicas alive? | Use `removenode` | Continue to next question |
| Accept data loss? | Use `removenode force` or `assassinate` | Try to recover the node |

---

## Best Practices

!!! tip "Removenode Guidelines"
    1. **Verify node is truly dead** - Don't remove a node that might rejoin
    2. **Check replication first** - Ensure data can be reconstructed
    3. **One at a time** - Never remove multiple nodes simultaneously
    4. **Monitor progress** - Watch streaming and logs
    5. **Repair after** - Run repair on remaining nodes
    6. **Document** - Record which nodes were removed and when

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [decommission](decommission.md) | Remove live node |
| [assassinate](assassinate.md) | Force remove stuck node |
| [status](status.md) | Check cluster state |
| [netstats](netstats.md) | Monitor streaming |
| [repair](repair.md) | Run after removal |
