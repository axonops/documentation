---
description: "Gracefully remove a Cassandra node from the cluster using nodetool decommission. Streams data to remaining nodes."
meta:
  - name: keywords
    content: "nodetool decommission, remove node, Cassandra cluster, data streaming"
---

# nodetool decommission

Gracefully removes the local node from the cluster, streaming its data to remaining nodes.

---

## Synopsis

```bash
nodetool [connection_options] decommission [-f, --force]
```

## Description

`nodetool decommission` initiates a graceful removal of the current node from the cluster. Unlike `removenode` (which operates on dead nodes from a remote node), decommission runs locally on the node being removed and leverages the node's own data to stream to new owners.

This is the preferred method for removing healthy nodes from a cluster.

### What Decommission Does

When `decommission` executes, Cassandra performs the following operations:

1. **Sets node state to LEAVING** - The node announces via gossip that it is leaving the cluster. Other nodes see status change from UN (Up/Normal) to UL (Up/Leaving).

2. **Stops accepting coordinator requests** - The node stops accepting new client write requests as a coordinator, though it continues to accept replica writes from other coordinators during streaming.

3. **Calculates token range transfers** - The node determines which other nodes should receive its token ranges based on the replication strategy and token allocation.

4. **Streams data to new owners** - For each token range the node owns, data is streamed directly from this node's SSTables to the nodes that will assume ownership. This is more efficient than `removenode` because the data is read locally rather than reconstructed from replicas.

5. **Relinquishes token ownership** - Once streaming completes, the node's tokens are removed from the ring and reassigned to the nodes that received the data.

6. **Updates cluster topology** - The ring topology is updated across all nodes via gossip. The node's entry is removed from `system.peers` on other nodes.

7. **Shuts down** - The Cassandra process exits. The node no longer appears in `nodetool status`.

!!! info "Decommission vs Removenode"
    The key difference from `removenode` is that decommission streams data directly from the departing node's local storage, while `removenode` must reconstruct data from other replicas. This makes decommission faster and more reliable when the node is healthy.

---

## Options

| Option | Description |
|--------|-------------|
| `-f, --force` | Force decommission even if it would violate replication constraints |

---

## When to Use

### Scaling Down

When reducing cluster capacity:

```bash
# On the node to be removed
nodetool decommission
```

### Hardware Replacement

When replacing a server with data migration:

```bash
# Add new node first
# Wait for bootstrap to complete
# Then decommission old node
nodetool decommission
```

### Datacenter Removal

When removing nodes from a datacenter:

```bash
# Decommission nodes one at a time
# Start with nodes that have fewer token ranges
nodetool decommission
```

---

## When NOT to Use

### For Dead Nodes

!!! danger "Don't Decommission Dead Nodes"
    `decommission` must be run **on the node being removed**. For dead nodes, use:

    ```bash
    # From any live node
    nodetool removenode <host-id>
    ```

### Last Node in Datacenter

If this is the last node in a DC that still has RF defined:

```bash
# First, reduce RF for all keyspaces
ALTER KEYSPACE my_keyspace WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3,
    'dc2': 0  -- Removing dc2
};

# Then decommission
nodetool decommission
```

### During Active Operations

!!! warning "Avoid During"
    - Active repairs
    - Other streaming operations
    - Bootstrap in progress elsewhere
    - High traffic periods

---

## Decommission Process

1. Stop accepting new writes
2. Calculate token ranges to stream
3. Stream data to remaining nodes (monitor with `nodetool netstats`)
4. Wait for streaming to complete
5. Update cluster topology
6. Remove node from ring
7. Shutdown

### Duration Estimate

| Data Size | Network Speed | Approximate Time |
|-----------|---------------|------------------|
| 100 GB | 1 Gbps | 15-20 minutes |
| 500 GB | 1 Gbps | 1-2 hours |
| 1 TB | 1 Gbps | 2-4 hours |
| 1 TB | 10 Gbps | 15-30 minutes |

Actual time depends on network, disk speed, and concurrent operations.

---

## Before Decommissioning

### Check Cluster Status

```bash
nodetool status
```

Ensure all nodes are UN (Up/Normal).

### Check for Active Operations

```bash
# Check for repairs
nodetool repair_admin list

# Check for streaming
nodetool netstats

# Check for compactions
nodetool compactionstats
```

### Verify Replication Requirements

Ensure remaining nodes can satisfy RF:

```bash
# Check keyspace RF
DESCRIBE KEYSPACE my_keyspace;

# Verify node count per DC
nodetool status
```

!!! danger "Replication Constraint"
    If decommissioning would leave fewer nodes than RF in any DC, the operation fails unless `-f` is used.

---

## During Decommission

### Monitor Progress

```bash
# Watch streaming progress
nodetool netstats

# Check status (node shows UL = Up/Leaving)
nodetool status
```

### Node States

| Status | Meaning |
|--------|---------|
| UN | Normal operation |
| UL | Leaving (decommission in progress) |
| Removed | No longer appears in status |

### Do NOT

!!! danger "During Decommission"
    - Do NOT restart the node
    - Do NOT run other streaming operations
    - Do NOT modify schema
    - Do NOT start other decommissions

---

## After Decommission

### Verify Removal

```bash
# From any remaining node
nodetool status
```

The decommissioned node should no longer appear.

### Clean Up Data on Removed Node

After decommission completes, you may delete data directories on the removed server:

```bash
# ONLY on the decommissioned server
rm -rf /var/lib/cassandra/data/*
rm -rf /var/lib/cassandra/commitlog/*
rm -rf /var/lib/cassandra/saved_caches/*
```

### Run Cleanup on Remaining Nodes (Not Required)

Unlike adding nodes, cleanup is not necessary after decommission. The decommissioned node's data was streamed to appropriate owners.

---

## Monitoring Decommission

### From the Decommissioning Node

```bash
# Streaming progress
nodetool netstats

# Shows "Mode: LEAVING" in output
nodetool info
```

### From Other Nodes

```bash
# Shows UL (Up/Leaving) status
nodetool status

# Shows incoming streams
nodetool netstats
```

### Logs

```bash
# On decommissioning node
tail -f /var/log/cassandra/system.log | grep -i decommission
```

---

## Canceling Decommission

!!! warning "Cannot Cancel Gracefully"
    Once started, decommission cannot be cleanly canceled. If you must stop:

    1. Kill Cassandra process (last resort)
    2. Node will be in inconsistent state
    3. Will need to re-bootstrap or removenode

---

## Common Issues

### "Not enough live nodes"

```
ERROR: Not enough live nodes to decommission
```

The cluster cannot maintain RF after removal:

- Check that enough nodes remain in each DC
- Verify no other nodes are down
- May need to reduce RF first

### Decommission Stuck

If decommission appears hung:

```bash
# Check streaming progress
nodetool netstats

# Check for pending tasks
nodetool tpstats
```

Common causes:
- Network issues
- Disk I/O bottleneck
- Target nodes overloaded

### Node Still Appears After Decommission

If the node completed decommission but still shows in `status`:

```bash
# Allow time for gossip propagation
# If persists, may need to assassinate the gossip state
nodetool assassinate <ip_address>
```

---

## Force Decommission

```bash
nodetool decommission -f
```

!!! danger "Force Flag Warning"
    Using `-f` allows decommission even if it violates RF constraints:

    - May cause data unavailability
    - May lose data if RF drops below 1
    - Only use when you understand the consequences

---

## Best Practices

!!! tip "Decommission Guidelines"
    1. **Check cluster health first** - All nodes should be UN
    2. **Run during low traffic** - Reduces streaming impact
    3. **One node at a time** - Don't decommission multiple simultaneously
    4. **Monitor progress** - Watch netstats and logs
    5. **Plan for duration** - Large data sets take hours
    6. **Have rollback plan** - Know how to handle failures

---

## Decommission vs. Other Removal Methods

| Method | Use When |
|--------|----------|
| `decommission` | Node is alive and healthy |
| `removenode` | Node is dead/unreachable |
| `assassinate` | Node is dead and removenode fails |

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [removenode](removenode.md) | Remove dead node |
| [assassinate](assassinate.md) | Force remove unresponsive node |
| [status](status.md) | Check cluster state |
| [netstats](netstats.md) | Monitor streaming progress |
| [cleanup](cleanup.md) | Clean up after adding nodes |
