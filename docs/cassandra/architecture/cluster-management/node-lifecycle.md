# Node Lifecycle

This section describes the complete lifecycle of a Cassandra node from initial cluster join through eventual removal. Understanding these state transitions is essential for operational management, troubleshooting, and capacity planning.

---

## Lifecycle State Machine

Cassandra nodes progress through well-defined states during their lifecycle:

```graphviz dot lifecycle-state-machine.svg
digraph LifecycleStateMachine {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=LR;

    label="Node Lifecycle State Machine";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    new [label="NEW\n(unconfigured)", fillcolor="#E8E8E8", fontcolor="black"];
    starting [label="STARTING", fillcolor="#FFC000", fontcolor="black"];
    joining [label="JOINING\n(bootstrap)", fillcolor="#FFC000", fontcolor="black"];
    normal [label="NORMAL\n(operational)", fillcolor="#70AD47", fontcolor="white"];
    leaving [label="LEAVING\n(decommission)", fillcolor="#FFC000", fontcolor="black"];
    moving [label="MOVING\n(rebalance)", fillcolor="#FFC000", fontcolor="black"];
    left [label="LEFT\n(removed)", fillcolor="#7F7F7F", fontcolor="white"];
    down [label="DOWN\n(failed)", fillcolor="#C00000", fontcolor="white"];

    new -> starting [label="start"];
    starting -> joining [label="contact seeds"];
    joining -> normal [label="bootstrap complete"];
    normal -> leaving [label="decommission"];
    leaving -> left [label="streaming complete"];
    normal -> moving [label="move token"];
    moving -> normal [label="move complete"];
    normal -> down [label="failure detected", style=dashed];
    down -> normal [label="recovery", style=dashed];
    down -> left [label="removenode"];
}
```

### State Definitions

| State | Gossip STATUS | Description |
|-------|---------------|-------------|
| **STARTING** | - | Node process started, not yet joined cluster |
| **JOINING** | `BOOT` | Bootstrapping, streaming data from existing nodes |
| **NORMAL** | `NORMAL` | Fully operational, serving client requests |
| **LEAVING** | `LEAVING` | Decommissioning, streaming data to remaining nodes |
| **MOVING** | `MOVING` | Token reassignment in progress |
| **LEFT** | `LEFT` | Removed from cluster, no longer participating |
| **DOWN** | - | Failure detected (local determination, not gossiped) |

---

## Joining the Cluster

### Bootstrap Process

Bootstrap is the process by which a new node joins an existing cluster and receives its share of data.

```graphviz dot bootstrap-process.svg
digraph BootstrapProcess {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Bootstrap Process";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    subgraph cluster_phase1 {
        label="Phase 1: Discovery";
        style="rounded,filled";
        fillcolor="#E8E8E8";
        color="#999999";

        start [label="Node Starts\nReads cassandra.yaml", fillcolor="#5B9BD5", fontcolor="white"];
        seed [label="Contact Seeds\nRequest cluster state", fillcolor="#5B9BD5", fontcolor="white"];
        state [label="Receive Gossip State\nLearn all endpoints", fillcolor="#5B9BD5", fontcolor="white"];
    }

    subgraph cluster_phase2 {
        label="Phase 2: Token Allocation";
        style="rounded,filled";
        fillcolor="#FFE8E8";
        color="#CC9999";

        vnodes [label="Calculate Tokens\n(vnodes: automatic)", fillcolor="#C55A11", fontcolor="white"];
        ranges [label="Determine Ranges\nIdentify data to receive", fillcolor="#C55A11", fontcolor="white"];
    }

    subgraph cluster_phase3 {
        label="Phase 3: Streaming";
        style="rounded,filled";
        fillcolor="#E8F4E8";
        color="#99CC99";

        announce [label="Announce JOINING\nGossip to cluster", fillcolor="#70AD47", fontcolor="white"];
        stream [label="Stream Data\nReceive SSTables", fillcolor="#70AD47", fontcolor="white"];
    }

    subgraph cluster_phase4 {
        label="Phase 4: Activation";
        style="rounded,filled";
        fillcolor="#E8E8F4";
        color="#9999CC";

        ready [label="Announce NORMAL\nAccept client traffic", fillcolor="#5B9BD5", fontcolor="white"];
    }

    start -> seed -> state;
    state -> vnodes -> ranges;
    ranges -> announce -> stream;
    stream -> ready;
}
```

### Bootstrap Configuration

```yaml
# cassandra.yaml - Bootstrap settings

# Enable/disable automatic bootstrap
# Set to false for first node in cluster or when using replace_address
auto_bootstrap: true

# Number of virtual nodes per physical node
num_tokens: 256

# Initial token (only if num_tokens = 1, not recommended)
# initial_token:

# Allocate tokens using random or algorithm-based approach
allocate_tokens_for_keyspace: <keyspace_name>  # Optional, for better distribution
```

### Bootstrap Streaming

During bootstrap, the new node streams data from existing replicas:

| Aspect | Description |
|--------|-------------|
| **Source selection** | Prefers local datacenter, least-loaded nodes |
| **Range calculation** | Based on new node's tokens and RF |
| **Parallelism** | Concurrent streams from multiple sources |
| **Resume capability** | Can resume after failures (Cassandra 4.0+) |

**Streaming source selection algorithm:**

1. Identify all ranges new node should own
2. For each range, identify replica set
3. Select replica based on:
   - Prefer same datacenter
   - Prefer least-loaded node
   - Avoid nodes already streaming

### Bootstrap Duration

Bootstrap time depends on:

| Factor | Impact |
|--------|--------|
| Data volume | Linear with total data size |
| Network bandwidth | Limited by `stream_throughput_outbound_megabits_per_sec` |
| Number of ranges | More ranges = more coordination overhead |
| Compaction during streaming | May delay completion |

**Estimation formula:**
```
Time ≈ (Data per node × RF) / Stream throughput
Example: (500GB × 3) / 200Mbps ≈ 1.7 hours
```

### Monitoring Bootstrap

```bash
# Check bootstrap progress
nodetool netstats

# Sample output during bootstrap:
# Mode: JOINING
#     /10.0.1.2
#         Receiving 234 files, 45GB total. Already received 156 files, 30GB.

# Check node status
nodetool status
# Shows UJ (Up Joining) during bootstrap

# View detailed streaming
nodetool netstats -H
```

---

## Normal Operation

### NORMAL State

A node in NORMAL state:

- Owns specific token ranges
- Serves as replica for data within RF
- Accepts client read/write requests
- Participates in gossip protocol
- Reports metrics and health status

### Token Ownership

Each node owns ranges of the token ring:

```graphviz dot token-ownership.svg
digraph TokenOwnership {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];

    label="Token Ring Ownership (3 nodes, 4 tokens each)";
    labelloc="t";
    fontsize=12;

    node [shape=circle, style="filled", width=0.8];

    // Ring representation
    t0 [label="0", fillcolor="#5B9BD5", fontcolor="white"];
    t25 [label="25", fillcolor="#70AD47", fontcolor="white"];
    t50 [label="50", fillcolor="#C55A11", fontcolor="white"];
    t75 [label="75", fillcolor="#5B9BD5", fontcolor="white"];
    t100 [label="100", fillcolor="#70AD47", fontcolor="white"];
    t125 [label="125", fillcolor="#C55A11", fontcolor="white"];

    t0 -> t25 -> t50 -> t75 -> t100 -> t125 -> t0;

    legend [shape=none, label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
        <TR><TD BGCOLOR="#5B9BD5"><FONT COLOR="white">Node A</FONT></TD></TR>
        <TR><TD BGCOLOR="#70AD47"><FONT COLOR="white">Node B</FONT></TD></TR>
        <TR><TD BGCOLOR="#C55A11"><FONT COLOR="white">Node C</FONT></TD></TR>
    </TABLE>>];
}
```

### Operational Health Indicators

| Indicator | Healthy | Warning | Critical |
|-----------|---------|---------|----------|
| Gossip state | NORMAL | JOINING/MOVING | DOWN |
| Pending compactions | < 20 | 20-100 | > 100 |
| Dropped messages | 0 | < 1% | > 1% |
| GC pause | < 500ms | 500ms-1s | > 1s |

---

## Leaving the Cluster

### Decommission Process

Decommission is the orderly removal of a node, ensuring all data is transferred to remaining nodes.

```graphviz dot decommission-process.svg
digraph DecommissionProcess {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Decommission Process";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    initiate [label="1. Initiate Decommission\nnodetool decommission", fillcolor="#E8E8E8", fontcolor="black"];
    announce [label="2. Announce LEAVING\nGossip to cluster", fillcolor="#5B9BD5", fontcolor="white"];
    calculate [label="3. Calculate Targets\nDetermine new owners", fillcolor="#5B9BD5", fontcolor="white"];
    stream [label="4. Stream Data\nTransfer to new owners", fillcolor="#FFC000", fontcolor="black"];
    complete [label="5. Announce LEFT\nRemove from ring", fillcolor="#70AD47", fontcolor="white"];
    shutdown [label="6. Shutdown\nProcess terminates", fillcolor="#7F7F7F", fontcolor="white"];

    initiate -> announce -> calculate -> stream -> complete -> shutdown;
}
```

### Decommission Command

```bash
# Initiate decommission (run on node being removed)
nodetool decommission

# This command:
# - Blocks until complete
# - Cannot be cancelled once started
# - Requires RF nodes remain after removal
```

### Decommission Prerequisites

| Requirement | Verification |
|-------------|--------------|
| Sufficient remaining capacity | Check disk usage on remaining nodes |
| Replication factor satisfied | N - 1 ≥ RF for all keyspaces |
| No pending repairs | `nodetool repair_admin list` |
| Gossip healthy | `nodetool gossipinfo` shows all nodes |

### Data Redistribution

During decommission, data transfers to new replica owners:

```graphviz dot data-redistribution.svg
digraph DataRedistribution {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=LR;

    label="Data Redistribution During Decommission";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    subgraph cluster_before {
        label="Before (RF=3)";
        style="rounded,filled";
        fillcolor="#E8E8E8";
        color="#999999";

        range [label="Range X", fillcolor="#FFC000", fontcolor="black"];
        a1 [label="Node A\n(leaving)", fillcolor="#C00000", fontcolor="white"];
        b1 [label="Node B", fillcolor="#5B9BD5", fontcolor="white"];
        c1 [label="Node C", fillcolor="#5B9BD5", fontcolor="white"];

        range -> a1 [label="replica 1"];
        range -> b1 [label="replica 2"];
        range -> c1 [label="replica 3"];
    }

    subgraph cluster_after {
        label="After";
        style="rounded,filled";
        fillcolor="#E8F4E8";
        color="#99CC99";

        range2 [label="Range X", fillcolor="#FFC000", fontcolor="black"];
        b2 [label="Node B", fillcolor="#5B9BD5", fontcolor="white"];
        c2 [label="Node C", fillcolor="#5B9BD5", fontcolor="white"];
        d2 [label="Node D\n(new replica)", fillcolor="#70AD47", fontcolor="white"];

        range2 -> b2 [label="replica 1"];
        range2 -> c2 [label="replica 2"];
        range2 -> d2 [label="replica 3"];
    }

    a1 -> d2 [label="stream data", style=dashed, color="#70AD47"];
}
```

### Monitoring Decommission

```bash
# Check decommission progress
nodetool netstats

# Sample output:
# Mode: LEAVING
#     /10.0.1.4
#         Sending 456 files, 89GB total. Already sent 234 files, 45GB.

# Node status shows UL (Up Leaving)
nodetool status
```

---

## Token Movement

### Move Operation

The move operation reassigns a node's token position without removing it from the cluster:

```bash
# Move node to new token (single-token nodes only)
nodetool move <new_token>

# Not recommended with vnodes (num_tokens > 1)
```

!!! warning "Move Limitations"
    Token movement is generally discouraged with vnodes. For capacity rebalancing, add/remove nodes instead of moving tokens.

---

## Failure Scenarios

### Node Failure Detection

When a node fails, the cluster detects and responds:

```graphviz dot failure-detection.svg
digraph FailureDetection {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Node Failure Detection and Response";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    failure [label="Node Fails\n(crash, network, etc.)", fillcolor="#C00000", fontcolor="white"];
    phi [label="Phi Accrual Detection\nφ exceeds threshold", fillcolor="#FFC000", fontcolor="black"];
    shadow [label="Shadow Round\nVerify with other nodes", fillcolor="#5B9BD5", fontcolor="white"];
    convict [label="Mark as DOWN\nLocal determination", fillcolor="#C00000", fontcolor="white"];
    hints [label="Store Hints\nFor failed node", fillcolor="#5B9BD5", fontcolor="white"];
    route [label="Route Around\nExclude from reads", fillcolor="#5B9BD5", fontcolor="white"];

    failure -> phi -> shadow -> convict;
    convict -> hints;
    convict -> route;
}
```

### Response to Node Failure

| Response | Description |
|----------|-------------|
| **Hints stored** | Coordinator stores writes destined for failed node |
| **Reads rerouted** | Failed node excluded from read replica selection |
| **Writes continue** | If CL satisfied by remaining replicas |
| **No automatic replacement** | Manual intervention required |

### Node Recovery

When a failed node recovers:

1. **Gossip reconnection**: Node contacts seeds/peers
2. **State synchronization**: Receives current cluster state
3. **Hint replay**: Receives stored hints from other nodes
4. **Gradual inclusion**: Phi detector marks as UP after successful communication

```bash
# After node restart, verify recovery
nodetool status       # Should show UN (Up Normal)
nodetool gossipinfo   # Verify gossip state
nodetool tpstats      # Check for hint replay activity
```

---

## Operational Commands

### Status Commands

```bash
# View cluster status
nodetool status

# Status output interpretation:
# UN = Up Normal (healthy)
# UJ = Up Joining (bootstrapping)
# UL = Up Leaving (decommissioning)
# UM = Up Moving (token movement)
# DN = Down Normal (failed)

# Detailed gossip state
nodetool gossipinfo

# Ring ownership
nodetool ring
```

### State Transition Commands

| Command | Effect | Use Case |
|---------|--------|----------|
| `nodetool decommission` | NORMAL → LEAVING → LEFT | Orderly node removal |
| `nodetool removenode <host_id>` | Force remove dead node | Node permanently failed |
| `nodetool assassinate <ip>` | Force remove stuck node | Emergency only |
| `nodetool move <token>` | Change token assignment | Rebalancing (not recommended with vnodes) |

### Force Operations

!!! danger "Destructive Operations"
    The following commands can cause data loss if used incorrectly.

```bash
# Force remove a dead node (use when node is unrecoverable)
nodetool removenode <host_id>

# Force remove a stuck node (emergency only)
nodetool assassinate <ip_address>

# These commands:
# - Do NOT stream data
# - May require subsequent repair
# - Should be last resort
```

---

## Best Practices

### Before Any Topology Change

1. **Verify cluster health**: `nodetool status` shows all UN
2. **Check pending operations**: No ongoing repairs, bootstraps
3. **Ensure sufficient capacity**: Remaining nodes can handle load
4. **Backup if critical**: Consider snapshots before major changes

### During Bootstrap

- Schedule during low-traffic periods
- Monitor streaming progress
- Watch for compaction backlog on existing nodes

### During Decommission

- Verify RF nodes will remain
- Allow sufficient time for completion
- Do not force-kill the process

### After Any Change

- Verify `nodetool status` shows expected state
- Run repair on affected ranges if needed
- Monitor for any performance degradation

---

## Related Documentation

- **[Gossip Protocol](gossip.md)** - State propagation and failure detection
- **[Seeds and Discovery](seeds.md)** - Bootstrap discovery process
- **[Node Replacement](node-replacement.md)** - Handling permanently failed nodes
- **[Data Streaming](../distributed-data/streaming.md)** - Bootstrap and decommission data transfer
