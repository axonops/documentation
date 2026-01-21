---
title: "Cassandra Cluster Management Operations"
description: "Operational procedures for Cassandra cluster topology changes. Adding, removing, replacing nodes and scaling operations."
meta:
  - name: keywords
    content: "Cassandra cluster management, topology changes, bootstrap, decommission, node replacement"
search:
  boost: 3
---

# Cluster Management Operations

This section covers operational procedures for managing Cassandra cluster topology: adding capacity, removing nodes, replacing failed hardware, and managing multi-datacenter deployments.

!!! info "Architecture Reference"
    For conceptual details on how Cassandra manages cluster membership, see [Cluster Management Architecture](../../architecture/cluster-management/index.md).

---

## Operations Reference

| Operation | Use Case | Command | Impact |
|-----------|----------|---------|--------|
| [Add Node](adding-nodes.md) | Expand capacity | Start node with `auto_bootstrap: true` | Streaming to new node |
| [Decommission](removing-nodes.md#decommission) | Graceful removal (node up) | `nodetool decommission` | Streaming from departing node |
| [Remove Node](removing-nodes.md#removenode) | Forced removal (node down) | `nodetool removenode` | Streaming among remaining nodes |
| [Replace Node](replacing-nodes.md) | Hardware replacement | `replace_address_first_boot` | Streaming to replacement |
| [Scale Up](scaling.md#scaling-up) | Add multiple nodes | Sequential bootstrap | Multiple streaming operations |
| [Scale Down](scaling.md#scaling-down) | Reduce capacity | Sequential decommission | Multiple streaming operations |
| [Add Datacenter](multi-datacenter.md#adding-a-datacenter) | Geographic expansion | Rebuild from existing DC | Cross-DC streaming |
| [Remove Datacenter](multi-datacenter.md#removing-a-datacenter) | Consolidation | Decommission all DC nodes | Data redistribution |
| [Cleanup](cleanup.md) | Reclaim space after adding | `nodetool cleanup` | I/O intensive |
| [Assassinate](removing-nodes.md#assassinate) | Last resort removal | `nodetool assassinate` | Immediate, no streaming |

---

## Safety Requirements

The following requirements must be observed for all topology operations:

### Pre-Operation Requirements

| Requirement | Rationale |
|-------------|-----------|
| All nodes must show `UN` status | Topology changes with degraded nodes risk data loss |
| No pending repairs must be running | Concurrent operations cause unpredictable behavior |
| No other topology changes must be in progress | Only one topology change may occur at a time |
| Sufficient disk headroom must exist | Streaming requires temporary additional space |
| Schema agreement must be confirmed | Schema disagreement causes bootstrap failures |

```bash
# Pre-flight verification
nodetool status              # All nodes UN
nodetool describecluster     # Single schema version
nodetool compactionstats     # No heavy compaction
nodetool netstats            # No active streaming
```

### Operational Constraints

!!! danger "Critical Constraints"

    **One operation at a time:** Multiple concurrent topology changes must not be performed. The cluster must complete one operation before starting another.

    **Never bootstrap multiple nodes simultaneously** unless using manual token assignment. Concurrent bootstraps with vnodes cause token collisions.

    **Cleanup must run after adding nodes.** Existing nodes retain data they no longer own until cleanup executes.

---

## Operation Selection Guide

### Node is Healthy and Accessible

| Goal | Operation |
|------|-----------|
| Remove node permanently | [Decommission](removing-nodes.md#decommission) |
| Move node to different hardware | [Decommission](removing-nodes.md#decommission) → [Add Node](adding-nodes.md) |
| Replace with same IP | [Replace Node](replacing-nodes.md) (faster) |

### Node is Down or Unresponsive

| Scenario | Operation |
|----------|-----------|
| Node recoverable (disk/network issue) | Fix issue, node rejoins automatically |
| Node unrecoverable, data on other replicas | [Remove Node](removing-nodes.md#removenode) |
| Node unrecoverable, need same token range | [Replace Node](replacing-nodes.md) |
| Remove stuck in gossip | [Assassinate](removing-nodes.md#assassinate) (last resort) |

### Capacity Planning

| Goal | Operation |
|------|-----------|
| Increase capacity | [Scale Up](scaling.md#scaling-up) (add nodes) |
| Decrease capacity | [Scale Down](scaling.md#scaling-down) (decommission nodes) |
| Add geographic redundancy | [Add Datacenter](multi-datacenter.md#adding-a-datacenter) |
| Consolidate datacenters | [Remove Datacenter](multi-datacenter.md#removing-a-datacenter) |

---

## Streaming Behavior

All topology changes except assassinate involve data streaming between nodes.

### Streaming Direction by Operation

| Operation | Data Flows From | Data Flows To |
|-----------|-----------------|---------------|
| Add node | Existing nodes | New node |
| Decommission | Departing node | Remaining nodes |
| Remove node | Remaining replicas | Other replicas |
| Replace node | Remaining replicas | Replacement node |
| Rebuild | Source datacenter | Target datacenter |

### Estimated Duration

Streaming duration depends on data volume and network bandwidth:

| Data Volume | 1 Gbps Network | 10 Gbps Network |
|-------------|----------------|-----------------|
| 100 GB | 15-30 min | 5-10 min |
| 500 GB | 1-2 hours | 15-30 min |
| 1 TB | 2-4 hours | 30-60 min |
| 5 TB | 12-24 hours | 2-4 hours |

!!! tip "Streaming Throughput"
    Default streaming throughput is 200 Mbps. This may be increased for faster operations:
    ```bash
    nodetool setstreamthroughput 400  # MB/s
    ```
    Higher values increase operation speed but may impact client request latency.

---

## Monitoring Topology Operations

### Key Commands

```bash
# Cluster membership status
nodetool status

# Streaming progress
nodetool netstats

# Detailed streaming sessions
nodetool netstats -H

# Node state transitions
nodetool gossipinfo | grep STATUS
```

### Node States During Operations

| State | Code | Meaning |
|-------|------|---------|
| Normal | `UN` | Fully operational |
| Joining | `UJ` | Bootstrap in progress |
| Leaving | `UL` | Decommission in progress |
| Moving | `UM` | Token move in progress |
| Down | `DN` | Node unreachable |

### JMX Metrics

```
# Streaming progress
org.apache.cassandra.metrics:type=Streaming,scope=*,name=*

# Compaction (impacts streaming)
org.apache.cassandra.metrics:type=Compaction,name=PendingTasks
```

---

## Failure Handling

### Operation Interrupted

| Operation | If Interrupted | Recovery |
|-----------|----------------|----------|
| Bootstrap | Node partially populated | Clear data, restart bootstrap |
| Decommission | Node partially drained | Cannot resume; complete manually or restore |
| Remove | Partial redistribution | Re-run removenode |
| Replace | Replacement partially populated | Clear data, restart replacement |

### Streaming Failures

If streaming fails during an operation:

1. Check network connectivity between nodes
2. Verify disk space on source and target
3. Review `system.log` for specific errors
4. Increase `streaming_socket_timeout_in_ms` if timeouts occur

```yaml
# cassandra.yaml - increase for large partitions
streaming_socket_timeout_in_ms: 86400000  # 24 hours
```

---

## Procedures

- **[Adding Nodes](adding-nodes.md)** - Bootstrap new nodes into the cluster
- **[Removing Nodes](removing-nodes.md)** - Decommission, removenode, and assassinate
- **[Replacing Nodes](replacing-nodes.md)** - Replace failed nodes with new hardware
- **[Scaling Operations](scaling.md)** - Scale cluster capacity up or down
- **[Multi-Datacenter Operations](multi-datacenter.md)** - Add and remove datacenters
- **[Cleanup Operations](cleanup.md)** - Post-topology-change maintenance
- **[Troubleshooting](troubleshooting.md)** - Diagnose and resolve topology issues

---

## Related Documentation

- **[Gossip Protocol](../../architecture/cluster-management/gossip.md)** - How nodes discover cluster state
- **[Node Lifecycle](../../architecture/cluster-management/node-lifecycle.md)** - Node states and transitions
- **[Repair Operations](../repair/index.md)** - Post-topology repair procedures
- **[Backup & Restore](../backup-restore/index.md)** - Data protection during changes
