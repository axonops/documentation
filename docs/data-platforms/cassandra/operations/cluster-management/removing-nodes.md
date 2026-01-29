---
title: "Cassandra Removing Nodes"
description: "Remove nodes from Cassandra cluster. Decommission, removenode, and assassinate procedures with behavioral contracts."
meta:
  - name: keywords
    content: "Cassandra decommission, removenode, assassinate, remove node from cluster"
---

# Removing Nodes

This guide covers procedures for removing nodes from a Cassandra cluster. The appropriate method depends on whether the node is healthy and responsive.

---

## Operation Selection

| Node State | Recommended Operation | Data Safety |
|------------|----------------------|-------------|
| Up and healthy | [Decommission](#decommission) | Full data redistribution |
| Down but recoverable | Fix issue, node rejoins | No data loss |
| Down, unrecoverable | [Removenode](#removenode) | Relies on replica data |
| Stuck in gossip | [Assassinate](#assassinate) | No redistribution |

---

## Rack-Aware Removal

When using `NetworkTopologyStrategy` with multiple racks, nodes must be removed evenly across racks to maintain balanced data distribution.

### The Imbalance Problem

Cassandra places one replica per rack (when RF ≤ rack count). Uneven removal causes remaining nodes to handle disproportionate load:

```
RF=3, 3 racks, starting with 6 nodes (2 per rack):

Before: Each node handles 50% of its rack's replica load

After removing 1 node from rack1:
Rack1: 1 node  → handles 100% of rack's replica load ← OVERLOADED
Rack2: 2 nodes → each handles 50% of rack's replica load
Rack3: 2 nodes → each handles 50% of rack's replica load
```

### Balanced Removal Rules

| Current State | Correct Removal | Incorrect Removal |
|---------------|-----------------|-------------------|
| 9 nodes (3 per rack) | Remove 3 (1 from each rack) | Remove 1 or 2 |
| 6 nodes (2 per rack) | Remove 3 (1 from each rack) | Remove 1 or 2 |
| 3 nodes (1 per rack) | Cannot remove (minimum for RF=3) | Any removal |

**Formula:** When removing nodes from a cluster with R racks, remove in multiples of R to maintain balance.

### Pre-Removal Verification

Check current rack distribution:

```bash
nodetool status

# Count nodes per rack
nodetool status | grep UN | awk '{print $8}' | sort | uniq -c
```

### Minimum Node Constraints

| RF | Minimum Nodes per Rack | Minimum Total (3 racks) |
|----|------------------------|-------------------------|
| 1 | 1 | 3 |
| 2 | 1 | 3 |
| 3 | 1 | 3 |

### Handling Forced Imbalanced Removal

If a node fails and cannot be recovered, creating an imbalance:

1. Use [removenode](#removenode) or [replace](replacing-nodes.md) to handle the failed node
2. Plan to add a replacement node to the same rack
3. Or remove nodes from other racks to restore balance

---

## Decommission

Decommission gracefully removes a healthy node by streaming all its data to remaining nodes before leaving the cluster.

### Prerequisites

The following conditions must be met before decommissioning:

| Requirement | Verification |
|-------------|--------------|
| Node must be in `UN` state | `nodetool status` |
| Remaining nodes must have capacity | Disk usage < 70% after redistribution |
| Remaining nodes must satisfy RF | At least RF nodes per DC remain |
| No other topology changes in progress | `nodetool netstats` shows no streaming |

### Behavioral Contract

**Guarantees:**

- All data owned by the decommissioning node is streamed to new owners before removal
- The node transitions through states: `UN` → `UL` (Leaving) → removed from ring
- The node continues serving client requests while streaming (state `UL`); coordinator routing shifts as streaming completes
- Hints destined for this node are cleared from other nodes

**Failure Semantics:**

!!! warning "Decommission Cannot Be Cancelled"
    Once decommission begins, it must not be interrupted. Stopping the process mid-stream leaves the cluster in an inconsistent state requiring manual recovery.

| Failure Scenario | Outcome | Recovery |
|------------------|---------|----------|
| Decommission completes | Node removed from ring | None required |
| Process killed mid-stream | Partial data on remaining nodes | Restart node, run repair, then re-decommission |
| Target node unavailable | Streaming stalls | Wait for target recovery or restart |
| Network partition | Streaming fails | Resolve partition, streaming resumes |

### Procedure

**Step 1: Verify cluster health**

```bash
# All nodes must be UN
nodetool status

# Schema must be in agreement
nodetool describecluster

# No active streaming
nodetool netstats
```

**Step 2: Calculate post-decommission capacity**

```bash
# Check current disk usage per node
nodetool status

# Example: 6 nodes at 50% = 300% total
# After removing 1: 300% / 5 = 60% per node
# This is acceptable (< 70%)
```

**Step 3: Initiate decommission**

Execute on the node being removed:

```bash
nodetool decommission
```

The command blocks until completion. For background execution:

```bash
nohup nodetool decommission &> /var/log/cassandra/decommission.log &
```

**Step 4: Monitor progress**

From any other node:

```bash
# Watch node state transition
watch -n 10 'nodetool status'

# Monitor streaming progress
nodetool netstats

# Check streaming rate
nodetool getstreamthroughput
```

**Step 5: Verify completion**

```bash
# Node should no longer appear
nodetool status

# Verify ring ownership redistributed
nodetool ring | head -20
```

### Duration Estimates

| Data on Node | Approximate Duration |
|--------------|---------------------|
| 100 GB | 30 min - 1 hour |
| 500 GB | 2-4 hours |
| 1 TB | 4-8 hours |
| 2 TB+ | 8-24 hours |

### Performance Tuning

To accelerate decommission (at cost of client latency):

```bash
# Increase streaming throughput (MB/s)
nodetool setstreamthroughput 400

# On Cassandra 4.0+, enable entire SSTable streaming
# In cassandra.yaml:
# stream_entire_sstables: true
```

---

## Removenode

Removenode forcibly removes a dead node by redistributing its token ranges among surviving replicas.

### Prerequisites

| Requirement | Verification |
|-------------|--------------|
| Node must be down (`DN` state) | `nodetool status` |
| Node must not be reachable | Confirmed hardware failure or permanent loss |
| Sufficient replicas must exist | RF > 1 for affected data |
| No other topology changes in progress | `nodetool netstats` |

!!! danger "Data Loss Risk"
    Removenode relies on replica data. If RF=1 or multiple replicas are lost, data loss occurs. Verify replication factor and replica availability before proceeding.

### Behavioral Contract

**Guarantees:**

- Token ranges owned by the dead node are reassigned to surviving nodes
- Surviving replicas stream data to new owners
- The dead node's host ID is removed from gossip
- Operation can be run from any surviving node

**Failure Semantics:**

| Failure Scenario | Outcome | Recovery |
|------------------|---------|----------|
| Removenode completes | Node removed, data redistributed | None required |
| Target node unavailable | Streaming stalls | `nodetool removenode status` to check; `removenode force` if stuck |
| All replicas unavailable | Data loss for affected ranges | Cannot recover without backup |
| Network issues | Streaming may retry or fail | Resolve network, re-run removenode |

### Procedure

**Step 1: Confirm node is permanently down**

```bash
# Verify node shows DN (Down, Normal)
nodetool status

# Confirm node is unreachable
ping <dead_node_ip>
nc -zv <dead_node_ip> 7000
```

**Step 2: Get the dead node's host ID**

```bash
nodetool status
# Note the Host ID (UUID) of the DN node
# Example: 5a5b1c2d-3e4f-5a6b-7c8d-9e0f1a2b3c4d
```

**Step 3: Initiate removal**

From any surviving node:

```bash
nodetool removenode <host_id>
```

**Step 4: Monitor progress**

```bash
# Check removal status
nodetool removenode status

# Monitor streaming
nodetool netstats
```

**Step 5: Handle stalled removal**

If removenode stalls for extended periods (> 1 hour with no progress):

```bash
# Force removal (skips waiting for streaming)
nodetool removenode force <host_id>
```

!!! warning "Force Removal"
    Force removal completes immediately without waiting for data streaming. Run `nodetool repair` on affected token ranges afterward to ensure data consistency.

**Step 6: Verify and repair**

```bash
# Confirm node removed
nodetool status

# Run repair to ensure consistency
nodetool repair -full
```

### Removenode vs Decommission

| Aspect | Decommission | Removenode |
|--------|--------------|------------|
| Node state | Must be up | Must be down |
| Data source | Departing node | Other replicas |
| Execution location | On departing node | Any surviving node |
| Cancellation | Not safe | Can use `force` |
| Post-operation | Complete | Run repair recommended |

---

## Assassinate

Assassinate immediately removes a node from gossip without data redistribution. This is a last-resort operation.

### When to Use

Assassinate should only be used when:

- Removenode has failed or is stuck indefinitely
- The node cannot be recovered
- The cluster must proceed despite the stuck node
- Data loss is acceptable or recoverable via repair

!!! danger "Assassinate Risks"

    **No data redistribution occurs.** Token ranges owned by the assassinated node become unavailable until repair redistributes data from replicas.

    **Potential data loss.** If RF=1 or other replicas are unavailable, data may be permanently lost.

    **Gossip inconsistency.** In rare cases, assassinate can cause gossip state issues requiring cluster-wide restart.

### Behavioral Contract

**Guarantees:**

- Node is immediately marked as dead in gossip
- All nodes stop attempting to contact the assassinated node
- Token ownership is recalculated (but data is not streamed)

**Failure Semantics:**

| Outcome | Consequence |
|---------|-------------|
| Assassinate succeeds | Node removed from gossip; data unavailable until repair |
| Assassinate on wrong node | Must restart the node to rejoin |
| Repeated assassinate | No additional effect |

### Procedure

**Step 1: Exhaust other options**

Assassinate should only be used after:

1. Node confirmed permanently unreachable
2. `nodetool removenode` attempted and failed
3. `nodetool removenode force` attempted and failed

**Step 2: Execute assassinate**

From any surviving node:

```bash
nodetool assassinate <dead_node_ip>
```

**Step 3: Verify removal**

```bash
nodetool status
nodetool gossipinfo | grep <dead_node_ip>
```

**Step 4: Run full repair**

```bash
# Critical: repair to redistribute data from replicas
nodetool repair -full
```

---

## Post-Removal Tasks

After any node removal operation:

### Verify Cluster Health

```bash
# All remaining nodes UN
nodetool status

# Schema agreement
nodetool describecluster

# Token distribution
nodetool ring | head -30
```

### Update Infrastructure

| Task | Action |
|------|--------|
| Monitoring | Remove node from monitoring systems |
| Alerting | Update alert configurations |
| Seed list | Remove from seed lists if applicable |
| Load balancers | Remove from client-facing pools |
| Documentation | Update cluster inventory |

### Run Repair

For `removenode` and `assassinate`, run repair to ensure data consistency:

```bash
# Full repair after removal
nodetool repair -full
```

---

## Troubleshooting

### Decommission Stuck

**Symptoms:** Node remains in `UL` state for extended time

```bash
# Check streaming progress
nodetool netstats

# Look for errors
grep -i "stream\|error" /var/log/cassandra/system.log | tail -50
```

**Causes and solutions:**

| Cause | Solution |
|-------|----------|
| Target node overloaded | Reduce `stream_throughput_outbound` on decommissioning node |
| Network issues | Resolve connectivity problems |
| Disk full on targets | Free disk space on target nodes |
| Large partitions | Increase `streaming_socket_timeout_in_ms` |

### Removenode Not Progressing

**Symptoms:** `nodetool removenode status` shows no progress

```bash
# Check if streaming is occurring
nodetool netstats

# Check for errors
grep -i "remove\|stream" /var/log/cassandra/system.log | tail -50
```

**Resolution:**

1. Wait at least 30 minutes for initial progress
2. Check target node health and disk space
3. If truly stuck, use `nodetool removenode force <host_id>`
4. Run repair afterward

### Node Reappears After Removal

**Symptoms:** Removed node shows up again in `nodetool status`

**Causes:**

- Node was restarted before data directory was cleared
- Gossip state inconsistency

**Resolution:**

```bash
# On the problematic node (if accessible)
sudo systemctl stop cassandra
rm -rf /var/lib/cassandra/data/*
rm -rf /var/lib/cassandra/commitlog/*
rm -rf /var/lib/cassandra/saved_caches/*

# If node is not accessible, assassinate from another node
nodetool assassinate <node_ip>
```

---

## Related Documentation

- **[Cluster Management Overview](index.md)** - Operation selection guide
- **[Adding Nodes](adding-nodes.md)** - Bootstrap procedures
- **[Replacing Nodes](replacing-nodes.md)** - Node replacement
- **[Node Lifecycle](../../architecture/cluster-management/node-lifecycle.md)** - State transitions
- **[Repair Operations](../repair/index.md)** - Post-removal repair