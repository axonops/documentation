---
title: "Cassandra Rolling Restart"
description: "Execute rolling restarts in Cassandra clusters. Node-by-node and rack-aware restart procedures with consistency guarantees."
meta:
  - name: keywords
    content: "Cassandra rolling restart, restart cluster, maintenance restart, rack-aware restart"
---

# Rolling Restart

A rolling restart cycles through cluster nodes, restarting each one while maintaining cluster availability. This procedure is used for configuration changes, JVM updates, and routine maintenance.

---

## Prerequisites

The following conditions must be met before starting a rolling restart:

| Requirement | Verification |
|-------------|--------------|
| All nodes must show `UN` status | `nodetool status` |
| No topology changes in progress | `nodetool netstats` |
| No active repairs | `nodetool netstats` |
| Schema agreement | `nodetool describecluster` |

```bash
# Pre-flight verification
nodetool status              # All nodes UN
nodetool describecluster     # Single schema version
nodetool netstats            # No active streaming
```

AxonOps performs these verification checks automatically before initiating any rolling restart operation.

---

## Behavioral Contract

### Guarantees

- Cluster remains available throughout the restart process
- No data loss occurs if procedure is followed correctly
- Client requests continue to be served (with potential latency increase)

### Consistency Requirements

For the cluster to maintain consistency during restarts:

| Consistency Level | Minimum Nodes Required | Restart Constraint |
|-------------------|------------------------|-------------------|
| ONE | 1 node up | N-1 nodes may be down |
| QUORUM (RF=3) | 2 nodes up | 1 node may be down |
| LOCAL_QUORUM (RF=3) | 2 nodes up per DC | 1 node per DC may be down |
| ALL | All nodes up | No restarts possible |

---

## Node-by-Node Restart

The standard approach for rolling restarts.

### Procedure

**Step 1: Select restart order**

Restart order considerations:

| Approach | Use Case |
|----------|----------|
| Rack-by-rack | Maintains rack fault tolerance |
| Any order | Acceptable when only one node is down at a time |

!!! note "Seed Nodes"
    Seed nodes do not require special treatment during rolling restarts. Seeds are only used during bootstrap for initial cluster discovery. Once nodes have joined the cluster, they maintain topology information through gossip and do not depend on seeds.

**Step 2: Verify all other nodes are UN**

Before taking any node down, confirm all other nodes are up and running:

```bash
nodetool status
```

All nodes except the one being restarted must show `UN` (Up, Normal). If any node shows `DN` or another state, resolve that issue before proceeding. Taking down a node while another is already down may violate consistency requirements.

**Step 3: Drain the node**

Before stopping, drain pending writes to disk:

```bash
nodetool drain
```

This flushes memtables and stops accepting writes. The node becomes unresponsive to clients.

**Step 4: Stop Cassandra**

```bash
sudo systemctl stop cassandra
```

**Step 5: Make configuration changes (if applicable)**

```bash
# Edit cassandra.yaml, jvm.options, etc.
sudo vim /etc/cassandra/cassandra.yaml
```

**Step 6: Start Cassandra**

```bash
sudo systemctl start cassandra
```

**Step 7: Wait for node to rejoin**

```bash
# Wait for UN status
watch -n 5 'nodetool status'

# Verify node is serving requests
nodetool info
```

**Step 8: Wait for hint delivery**

While the node was down, other nodes accumulated hints for it. These must be delivered before proceeding:

```bash
# Check hint delivery progress on OTHER nodes
nodetool tpstats | grep HintedHandoff

# Example output showing pending hints:
# HintedHandoff  0         0         0         0         0
#                Active    Pending   Completed Blocked   All time blocked
```

Wait until `Pending` column shows 0 on all nodes.

```bash
# Alternative: check hints directory size
du -sh /var/lib/cassandra/hints/
```

!!! note "Hint Delivery Time"
    Hint delivery typically completes within seconds for short outages. For longer outages or high write volumes, delivery may take several minutes. Proceeding before hints are delivered risks hint accumulation across multiple nodes. AxonOps monitors hint queue depth across all nodes and waits for delivery completion before proceeding.

**Step 9: Verify stability before proceeding**

```bash
# Check for pending compactions
nodetool compactionstats

# Verify gossip is stable
nodetool gossipinfo | grep STATUS
```

Wait for the node to stabilize (typically 1-2 minutes) before proceeding to the next node.

**Step 10: Repeat for remaining nodes**

Continue with each node until all have been restarted. Return to Step 2 for each subsequent node.

### Wait Time Between Restarts

| Cluster Size | Recommended Wait |
|--------------|------------------|
| < 10 nodes | Until node shows UN |
| 10-50 nodes | UN + 1-2 minutes |
| 50+ nodes | UN + 2-5 minutes |

AxonOps automatically calculates and enforces appropriate wait times based on cluster size and current load metrics.

---

## Rack-Aware Restart

When racks are configured to match the replication factor, entire racks may be restarted simultaneously while maintaining consistency.

### Rack-Level Restart Prerequisites

This approach requires:

| Requirement | Example |
|-------------|---------|
| Racks ≥ RF | RF=3 with 3 racks |
| Even node distribution | Same node count per rack |
| NetworkTopologyStrategy | Ensures one replica per rack |

### Why This Works

With RF=3 and 3 racks, Cassandra places exactly one replica in each rack:

```
Token Range X:
├── Replica 1 → Rack1 (Node A)
├── Replica 2 → Rack2 (Node B)
└── Replica 3 → Rack3 (Node C)
```

If Rack1 is completely down:
- 2 replicas remain (Rack2 and Rack3)
- QUORUM (2 of 3) is still achievable
- All reads and writes at QUORUM succeed

### Capacity Considerations

!!! warning "Capacity Impact"
    When an entire rack is down, remaining nodes handle 50% more load (for RF=3, 3 racks):

    - Normal: Each rack handles 1/3 of requests
    - One rack down: Each remaining rack handles 1/2 of requests
    - Throughput capacity must accommodate this increase

**Verify capacity before rack-level restart:**

```bash
# Check current load metrics
nodetool tpstats
nodetool proxyhistograms

# Ensure headroom exists for 50% load increase
```

### Rack-Level Restart Procedure

**Step 1: Verify all nodes are UN and identify rack to restart**

```bash
nodetool status

# ALL nodes must show UN before proceeding
# Note nodes in target rack
# Datacenter: dc1
# UN  10.0.1.1  rack1  ← Target
# UN  10.0.1.2  rack1  ← Target
# UN  10.0.1.3  rack2
# UN  10.0.1.4  rack2
# UN  10.0.1.5  rack3
# UN  10.0.1.6  rack3
```

All nodes in other racks must show `UN` before taking down any rack. If any node outside the target rack is down, resolve that issue first.

**Step 2: Drain all nodes in the rack**

```bash
# On all rack1 nodes simultaneously
nodetool drain
```

**Step 3: Stop all nodes in the rack**

```bash
# On all rack1 nodes
sudo systemctl stop cassandra
```

**Step 4: Make configuration changes**

Apply changes to all nodes in the rack.

**Step 5: Start all nodes in the rack**

```bash
# On all rack1 nodes
sudo systemctl start cassandra
```

**Step 6: Wait for rack to rejoin**

```bash
# All rack1 nodes should show UN
nodetool status
```

**Step 7: Wait for hint delivery**

While the rack was down, other racks accumulated hints. Wait for delivery to complete:

```bash
# On nodes in OTHER racks, check hint delivery
nodetool tpstats | grep HintedHandoff

# Wait until Pending = 0 on all nodes
```

With rack-level restarts, hint volume is higher since all nodes in the rack were down simultaneously.

**Step 8: Verify stability**

```bash
# Ensure all nodes are serving requests
nodetool info

# Check for streaming completion
nodetool netstats
```

**Step 9: Proceed to next rack**

Wait for stability, then repeat for remaining racks.

### Rack Restart Timing

| Rack Size | Approximate Restart Time |
|-----------|--------------------------|
| 2-3 nodes | 2-5 minutes |
| 5-10 nodes | 5-10 minutes |
| 10+ nodes | 10-15 minutes |

AxonOps detects rack topology automatically and can perform rack-level rolling restarts when the cluster configuration supports it.

---

## Restart Without Drain

In some scenarios, drain may be skipped:

| Scenario | Drain Required |
|----------|----------------|
| Configuration change | Recommended |
| JVM restart | Optional |
| Emergency restart | Skip |
| Version upgrade | Required |

### Skipping Drain

If drain is skipped:

```bash
# Stop without drain
sudo systemctl stop cassandra

# Cassandra flushes memtables on shutdown signal
# Commitlog replays on next start
```

**Trade-offs:**

| With Drain | Without Drain |
|------------|---------------|
| Clean shutdown | Commitlog replay on start |
| Faster restart | Slightly slower restart |
| No replay needed | May take 1-2 minutes longer |

---

## Monitoring During Rolling Restart

### Key Metrics

```bash
# On remaining nodes, monitor:

# Client request latency
nodetool proxyhistograms

# Thread pool status
nodetool tpstats

# Pending operations
nodetool compactionstats
```

### Alerting Considerations

During rolling restarts:

- Expect latency increase (fewer nodes serving requests)
- Expect elevated load on remaining nodes
- Suppress alerts for expected node-down events

AxonOps automatically suppresses node-down alerts during scheduled rolling restarts and provides a unified dashboard for monitoring restart progress across all nodes.

---

## Troubleshooting

### Node Won't Start After Restart

```bash
# Check logs for errors
tail -100 /var/log/cassandra/system.log | grep -i error

# Common causes:
# - Configuration syntax error
# - Port already in use
# - Insufficient memory
```

### Node Slow to Rejoin

```bash
# Check for commitlog replay
grep -i "replaying" /var/log/cassandra/system.log

# Check for schema sync
nodetool describecluster
```

### Cluster Unstable After Restart

If issues occur:

1. Stop the rolling restart
2. Wait for cluster to stabilize
3. Investigate the issue
4. Resume from the last successful node

AxonOps tracks restart progress and allows operations to be paused, investigated, and resumed from any point.

---

## Best Practices

### Do

| Practice | Rationale |
|----------|-----------|
| Verify cluster health before starting | Avoid compounding issues |
| Wait between nodes | Allow stabilization |
| Monitor throughout | Catch issues early |
| Restart during low-traffic periods | Minimize client impact |
| Keep configuration changes minimal | Easier troubleshooting |

### Don't

| Anti-Pattern | Risk |
|--------------|------|
| Restart multiple non-rack-aligned nodes | May break QUORUM |
| Skip health checks between nodes | Miss cascading failures |
| Rush through restarts | Cluster instability |
| Restart during repairs | Repair failures |

AxonOps enforces these best practices automatically, preventing operators from accidentally violating safety constraints during rolling restart operations.

---

## AxonOps Rolling Restart

AxonOps provides automated rolling restart with built-in safety checks:

- **Pre-flight validation**: Verifies cluster health before each node
- **Automatic pacing**: Waits for node stability and hint delivery before proceeding
- **Progress tracking**: Visual status of restart progress across all nodes
- **Abort capability**: Stop at any point if issues arise, resume later
- **Rack awareness**: Respects rack topology constraints automatically
- **Scheduling**: Schedule rolling restarts during maintenance windows
- **Configuration deployment**: Push configuration changes to nodes as part of the restart

See [AxonOps Operations](../../../../operations/cassandra/rollingrestart/overview.md) for configuration details.

---

## Related Documentation

- **[Cluster Management Overview](index.md)** - Operation selection
- **[Adding Nodes](adding-nodes.md)** - Node bootstrap procedures
- **[Maintenance](../maintenance/index.md)** - General maintenance procedures
