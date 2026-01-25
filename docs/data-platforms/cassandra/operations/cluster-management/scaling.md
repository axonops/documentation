---
title: "Cassandra Scaling Operations"
description: "Scale Cassandra clusters up and down. Capacity planning, node addition and removal procedures."
meta:
  - name: keywords
    content: "Cassandra scaling, scale up, scale down, capacity planning, cluster sizing"
---

# Scaling Operations

This guide covers procedures for scaling Cassandra cluster capacity by adding or removing multiple nodes.

---

## Capacity Planning

### Current Capacity Assessment

Before scaling, assess current cluster state:

```bash
# Per-node disk usage
nodetool status

# Example output:
# Datacenter: dc1
# Status=Up/Down  State=Normal  Load       Tokens
# UN  10.0.1.1    245.5 GB      256        ...
# UN  10.0.1.2    238.2 GB      256        ...
# UN  10.0.1.3    251.8 GB      256        ...

# Total cluster data (approximate)
# = Sum of loads / RF
# = (245.5 + 238.2 + 251.8) / 3 = 245 GB actual data
```

### Utilization Thresholds

| Disk Utilization | Status | Action |
|------------------|--------|--------|
| < 50% | Healthy | Normal operations |
| 50-70% | Monitor | Plan scaling |
| 70-85% | Warning | Scale soon |
| > 85% | Critical | Scale immediately |

!!! warning "Headroom Requirement"
    Disk utilization should generally not exceed 50-70% under normal operations (depending on compaction strategy and workload). This provides headroom for:

    - Compaction (temporary 2x space requirement)
    - Streaming during topology changes
    - Unexpected data growth
    - Node failure scenarios

### Rack-Aware Scaling

When using multiple racks with `NetworkTopologyStrategy`, nodes must be added or removed in multiples of the rack count to maintain balanced distribution.

```
RF=3, 3 racks:
- Add/remove in multiples of 3 (one per rack)
- Imbalanced distribution causes hot spots
```

| Racks | Add/Remove Multiple |
|-------|---------------------|
| 2 | 2 nodes (1 per rack) |
| 3 | 3 nodes (1 per rack) |
| 4 | 4 nodes (1 per rack) |

See [Adding Nodes - Rack-Aware Scaling](adding-nodes.md#rack-aware-scaling) for detailed guidance.

### Calculating Nodes Needed

**Scale-up calculation:**

```
Current: N nodes at U% utilization
Target: T% utilization

New node count = N × (U / T)
Nodes to add = New node count - N
```

**Example:**

```
Current: 6 nodes at 75% utilization
Target: 50% utilization

New node count = 6 × (75 / 50) = 9 nodes
Nodes to add = 9 - 6 = 3 nodes
```

**Scale-down calculation:**

```
Current: N nodes at U% utilization
Target: T% utilization (should not exceed 70%)

Minimum nodes = N × (U / T)
Nodes to remove = N - Minimum nodes
```

---

## Scaling Up

Adding multiple nodes to increase cluster capacity.

### Prerequisites

| Requirement | Verification |
|-------------|--------------|
| All nodes must be `UN` | `nodetool status` |
| No topology changes in progress | `nodetool netstats` |
| New hardware provisioned | Same specs as existing |
| Network configured | Firewall rules, DNS |

### Behavioral Contract

**Constraints:**

- Nodes should be added sequentially for reduced resource contention (concurrent bootstraps are supported but increase streaming load)
- Each node must complete bootstrap (`UN` status) before adding the next
- Cleanup should run on all original nodes after additions to reclaim space (recommended but not required for correctness)

**Failure Semantics:**

| Scenario | Impact | Recovery |
|----------|--------|----------|
| Bootstrap interrupted | Partial data on new node | Clear data, restart |
| Bootstrap slow | Cluster operational, elevated load | Wait or tune streaming |
| Existing node fails during bootstrap | Bootstrap may stall | Pause, fix issue, resume |

### Procedure

**Step 1: Pre-flight verification**

```bash
# All nodes healthy
nodetool status

# No pending operations
nodetool netstats
nodetool compactionstats

# Schema agreement
nodetool describecluster
```

**Step 2: Add nodes sequentially**

For each new node:

```bash
# 1. Configure new node (see Adding Nodes guide)

# 2. Start new node
sudo systemctl start cassandra

# 3. Monitor bootstrap
watch -n 30 'nodetool status'

# 4. Wait for UN status before proceeding to next node
```

**Step 3: Wait between additions**

| Cluster Size | Recommended Wait |
|--------------|------------------|
| < 10 nodes | Until bootstrap complete |
| 10-50 nodes | Bootstrap + 1 hour stabilization |
| 50+ nodes | Bootstrap + 2-4 hours stabilization |

**Step 4: Run cleanup on original nodes**

After all new nodes show `UN`:

```bash
# On each ORIGINAL node (not new nodes)
nodetool cleanup

# Run one node at a time to limit I/O impact
# Monitor progress
nodetool compactionstats
```

!!! warning "Cleanup is Mandatory"
    Original nodes retain copies of data that moved to new nodes. Cleanup reclaims this space. Without cleanup, disk usage remains elevated.

**Step 5: Verify final state**

```bash
# All nodes UN with balanced load
nodetool status

# Token distribution reasonable
nodetool ring | awk '{print $1}' | sort | uniq -c

# Disk utilization at target
df -h /var/lib/cassandra
```

### Timing Estimates

| Nodes to Add | Data per Node | Approximate Duration |
|--------------|---------------|---------------------|
| 1 | 500 GB | 4-8 hours |
| 3 | 500 GB | 12-24 hours (sequential) |
| 6 | 500 GB | 24-48 hours (sequential) |

Add cleanup time: approximately 50% of bootstrap time per original node.

---

## Scaling Down

Removing nodes to reduce cluster capacity.

### Prerequisites

| Requirement | Verification |
|-------------|--------------|
| All nodes must be `UN` | `nodetool status` |
| Remaining nodes must have capacity | Post-removal utilization < 70% |
| RF constraint must be satisfied | At least RF nodes remain per DC |
| No topology changes in progress | `nodetool netstats` |

### Pre-Removal Capacity Check

**Calculate post-removal utilization:**

```
Current: N nodes, total data = D
Removing: R nodes
Remaining: N - R nodes

Post-removal utilization = D / (N - R) / node_capacity × 100%
```

**Example:**

```
Current: 9 nodes, 1.8 TB total data, 500 GB disks
Removing: 3 nodes
Remaining: 6 nodes

Data per remaining node = 1.8 TB / 6 = 300 GB
Post-removal utilization = 300 GB / 500 GB = 60% ✓
```

!!! danger "Replication Factor Constraint"
    The remaining cluster must have at least RF nodes per datacenter. Removing below RF makes writes at QUORUM consistency impossible.

    ```
    Example: RF=3, DC has 4 nodes
    Maximum removable = 4 - 3 = 1 node
    ```

### Procedure

**Step 1: Identify nodes to remove**

Select nodes for removal considering:

- Even distribution across racks
- Not all seeds
- Lowest priority hardware

**Step 2: Remove nodes sequentially**

For each node to remove:

```bash
# 1. On the node being removed
nodetool decommission

# 2. Monitor progress
watch -n 30 'nodetool status'

# 3. Wait for node to disappear from status
# 4. Proceed to next node
```

**Step 3: Verify between removals**

After each decommission completes:

```bash
# Verify cluster health
nodetool status

# Check utilization trending
nodetool status | awk '/UN/ {print $3}'
```

**Step 4: Final verification**

```bash
# All remaining nodes UN
nodetool status

# Utilization within limits
df -h /var/lib/cassandra

# Ring distribution balanced
nodetool ring
```

### Timing Estimates

| Nodes to Remove | Data per Node | Approximate Duration |
|-----------------|---------------|---------------------|
| 1 | 500 GB | 4-8 hours |
| 3 | 500 GB | 12-24 hours (sequential) |

---

## Scaling Best Practices

### Planning

| Practice | Rationale |
|----------|-----------|
| Scale during low-traffic periods | Streaming competes with client requests |
| Communicate maintenance windows | Users expect potential latency increase |
| Have rollback plan | Document how to reverse if issues arise |
| Monitor throughout | Catch problems early |

### Execution

| Practice | Rationale |
|----------|-----------|
| One node at a time | Prevents overload |
| Wait for completion | Concurrent operations cause issues |
| Verify health between nodes | Catch problems before compounding |
| Document progress | Track what's done if interrupted |

### Post-Operation

| Practice | Rationale |
|----------|-----------|
| Run cleanup (scale-up) | Reclaim space |
| Update monitoring | Reflect new topology |
| Update documentation | Current cluster state |
| Consider repair | Ensure consistency |

---

## Emergency Scaling

When immediate capacity is needed:

### Fast Scale-Up

To accelerate bootstrap:

```yaml
# On new nodes - cassandra.yaml
stream_throughput_outbound_megabits_per_sec: 400

# Cassandra 4.0+
stream_entire_sstables: true
```

```bash
# On existing nodes
nodetool setstreamthroughput 400
```

!!! warning "Client Impact"
    Aggressive streaming settings impact client request latency. Use only when capacity is critical.

### Skip Cleanup (Temporary)

In emergencies, cleanup may be deferred:

1. Add nodes and wait for bootstrap
2. New nodes serve requests immediately
3. Schedule cleanup during next maintenance window

Risk: Original nodes retain extra data until cleanup.

---

## Related Documentation

- **[Adding Nodes](adding-nodes.md)** - Single node bootstrap procedure
- **[Removing Nodes](removing-nodes.md)** - Decommission procedure
- **[Cleanup Operations](cleanup.md)** - Post-addition cleanup
- **[Cluster Management Overview](index.md)** - Operation selection
