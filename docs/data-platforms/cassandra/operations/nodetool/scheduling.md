---
title: "Scheduling nodetool Commands Across Clusters"
description: "Orchestrate nodetool command execution across Cassandra clusters, datacenters, and racks. Coordinated rolling operations with AxonOps."
meta:
  - name: keywords
    content: "nodetool scheduling, Cassandra operations orchestration, rolling nodetool, multi-datacenter operations, nodetool automation, AxonOps operations"
---

# Scheduling nodetool Commands

nodetool operates on a single node. In production Cassandra deployments spanning multiple nodes, datacenters, and racks, most operational tasks require executing nodetool commands across every node in a coordinated sequence. Manual orchestration introduces significant operational risk.

---

## The Orchestration Challenge

### Single-Node Limitation

nodetool connects to one Cassandra node at a time via JMX. A command like `nodetool repair -pr` only affects the node where it is executed. Achieving cluster-wide coverage requires repeating the command on every node — in the correct order, with appropriate health verification between steps.

### What Can Go Wrong

| Risk | Consequence |
|------|-------------|
| Executing on too many nodes simultaneously | Loss of quorum availability; potential data unavailability |
| Skipping a node | Incomplete repair; risk of data resurrection from missed tombstone propagation |
| No health verification between steps | Cascading failures if a node does not recover before proceeding |
| Ignoring rack/datacenter topology | Multiple replicas for the same data taken offline simultaneously |
| No error handling | Silent failures leave the cluster in an inconsistent maintenance state |
| No audit trail | Impossible to verify what ran, when, and whether it succeeded |
| Script interruption | No way to resume from where the operation stopped |

### Coordination Requirements Vary by Operation

Different nodetool commands have different safety constraints:

| Operation | Constraint |
|-----------|-----------|
| `repair -pr` | Must run on every node within `gc_grace_seconds`; may parallelize on non-overlapping ranges |
| `cleanup` | Must run on every existing node after topology change; sequential recommended |
| `compact` | Avoid concurrent execution on nodes sharing replicas |
| `upgradesstables` | Must run on every node after version upgrade; sequential |
| `drain` + restart | Rolling: one node at a time with health gates between steps |
| `decommission` | Single node; verify cluster health before and after |
| `flush` | Safe to run concurrently |
| `setcompactionthroughput` | Apply to all nodes; safe to run concurrently |

### Multi-Datacenter Complexity

Clusters spanning multiple datacenters introduce additional constraints:

- Some operations should complete in the local datacenter before proceeding to remote datacenters
- Rack awareness is required to avoid taking down multiple replicas for the same token range
- Different datacenters may have different maintenance windows
- Coordination state must persist across long-running operations that span hours or days

---

## Orchestration with AxonOps

[AxonOps Operations](https://axonops.com/cassandra-features/operations/) provides purpose-built orchestration for nodetool commands across Cassandra clusters, with native understanding of Cassandra topology, health, and operational constraints.

### Topology-Aware Execution

AxonOps understands the cluster topology — nodes, racks, datacenters, and token ownership — and uses this to coordinate command execution safely:

- **Rack-aware rolling**: Only one node per rack is affected at a time, maintaining quorum availability
- **Datacenter ordering**: Operations complete in one datacenter before proceeding to the next
- **Token-range awareness**: For operations like repair, coordination is based on token ownership to avoid redundant work

### Health-Gated Execution

Each step in a rolling operation is gated by cluster health checks:

- Verify all expected nodes are in UN (Up/Normal) state before proceeding
- Check that pending compaction backlog is below threshold
- Monitor streaming activity from previous steps
- Configurable stabilization wait time between nodes

### Scheduling and Automation

Operations can be scheduled to run automatically:

- **Recurring schedules**: Repair cycles, routine maintenance
- **Maintenance windows**: Restrict execution to off-peak hours
- **Dependency chains**: Flush before snapshot, repair after topology change
- **Adaptive timing**: Adjust execution speed based on cluster load

### Progress Tracking and Audit

- Real-time progress visibility across all nodes
- Persistent state — if interrupted, operations resume from where they stopped
- Complete audit log of every command executed, on which node, with output and exit status
- Alerting on failures with configurable retry policies

### Supported Operations

| Operation | AxonOps Orchestration |
|-----------|----------------------|
| Repair | Adaptive scheduling with `gc_grace_seconds` compliance |
| Rolling restart | Drain, restart, health-gate per node with rack awareness |
| Cleanup | Triggered automatically after topology changes |
| Compaction tuning | Apply throughput changes across all nodes |
| Schema changes | Verify schema agreement after each change |
| Upgrades | Coordinated rolling upgrade with version verification |

---

## Related Documentation

- **[nodetool Reference](index.md)** — Complete command reference
- **[Maintenance Guide](../maintenance/index.md)** — Routine maintenance procedures
- **[Repair Strategies](../repair/strategies.md)** — Repair planning for different cluster sizes
- **[Repair Scheduling](../repair/scheduling.md)** — Repair schedule planning and compliance
