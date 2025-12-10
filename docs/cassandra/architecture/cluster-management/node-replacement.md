# Node Replacement

This section examines the architectural considerations for handling failed nodes in a Cassandra cluster. Understanding failure classification, recovery strategies, and the mechanics of node replacement is essential for designing resilient cluster topologies.

For operational procedures and step-by-step instructions, see **[Operations: Cluster Management](../../operations/cluster-management/index.md)**.

---

## Failure Classification

### Types of Node Failures

Node failures fall into distinct categories, each requiring different recovery approaches:

```graphviz dot failure-types.svg
digraph FailureTypes {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Node Failure Classification";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    failure [label="Node Failure", fillcolor="#C00000", fontcolor="white"];

    transient [label="Transient Failure\n• Temporary outage\n• Restart recovers\n• Data intact", fillcolor="#FFC000", fontcolor="black"];
    permanent [label="Permanent Failure\n• Hardware failure\n• Data loss\n• Node unrecoverable", fillcolor="#C00000", fontcolor="white"];

    restart [label="Recovery: Restart\nHints replay automatically", fillcolor="#70AD47", fontcolor="white"];
    replace [label="Recovery: Replace\nNew node assumes identity", fillcolor="#5B9BD5", fontcolor="white"];
    remove [label="Recovery: Remove\nReduce cluster size", fillcolor="#7F7F7F", fontcolor="white"];

    failure -> transient;
    failure -> permanent;
    transient -> restart;
    permanent -> replace;
    permanent -> remove;
}
```

| Failure Type | Characteristics | Recovery Approach |
|--------------|-----------------|-------------------|
| **Transient** | Node temporarily unavailable, data intact | Wait for restart, hints replay |
| **Recoverable** | Node can restart, possible data issues | Restart + repair |
| **Permanent** | Hardware failed, node cannot return | Replace or remove |

### Failure Detection

Cassandra detects node failures through the gossip protocol's Phi Accrual Failure Detector. When a node stops responding to gossip messages, other nodes independently calculate a suspicion level (φ). Once φ exceeds the configured threshold (default: 8), the node is marked DOWN locally.

Key characteristics:
- **Local determination**: Each node independently decides if a peer is DOWN
- **Not gossiped**: DOWN status is not propagated; each node must observe failure directly
- **Adaptive**: Phi Accrual adjusts to network latency variations

See **[Gossip Protocol](gossip.md)** for failure detection mechanics.

---

## Decision Framework

### Replace vs Remove

When a node permanently fails, the architectural decision between replacement and removal affects cluster capacity, data distribution, and recovery time:

```graphviz dot replace-vs-remove.svg
digraph ReplaceVsRemove {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Replace vs Remove Decision";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    start [label="Node Permanently Failed", fillcolor="#C00000", fontcolor="white"];

    q1 [label="Need to maintain\ncluster capacity?", shape=diamond, fillcolor="#E8E8E8", fontcolor="black"];
    q2 [label="Have replacement\nhardware available?", shape=diamond, fillcolor="#E8E8E8", fontcolor="black"];

    replace [label="REPLACE\nNew node assumes\nfailed node's tokens", fillcolor="#70AD47", fontcolor="white"];
    remove [label="REMOVE\nRedistribute data\nto remaining nodes", fillcolor="#5B9BD5", fontcolor="white"];
    add_later [label="REMOVE now\nADD new node later", fillcolor="#FFC000", fontcolor="black"];

    start -> q1;
    q1 -> q2 [label="Yes"];
    q1 -> remove [label="No\n(reducing capacity)"];
    q2 -> replace [label="Yes"];
    q2 -> add_later [label="No\n(hardware pending)"];
}
```

### Comparison of Approaches

| Factor | Replace | Remove |
|--------|---------|--------|
| **Cluster capacity** | Maintained | Reduced |
| **Data movement** | Stream to new node only | Redistribute across all remaining nodes |
| **Token ownership** | New node assumes dead node's tokens | Tokens redistributed to existing nodes |
| **Disk usage impact** | Isolated to new node | Increased on all remaining nodes |
| **Time to complete** | Longer (full data stream to one node) | Shorter (parallel redistribution) |
| **Network impact** | Concentrated streaming | Distributed streaming |

### Capacity Constraints

Before choosing an approach, verify capacity constraints:

| Constraint | Replace | Remove |
|------------|---------|--------|
| **Minimum nodes** | N ≥ RF after operation | N - 1 ≥ RF after operation |
| **Disk headroom** | New node needs capacity for its share | Remaining nodes need capacity for redistributed data |
| **Network bandwidth** | Streaming to single node | Parallel streaming between remaining nodes |

---

## Replacement Architecture

### Token Assumption Model

Node replacement operates on the principle of **token assumption**—the new node takes ownership of the failed node's token ranges without redistributing tokens across the cluster:

```graphviz dot token-assumption.svg
digraph TokenAssumption {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=LR;

    label="Token Assumption During Replacement";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    subgraph cluster_before {
        label="Before Failure";
        style="rounded,filled";
        fillcolor="#E8E8E8";
        color="#999999";

        ring1 [label="Token Ring\n\nNode A: tokens 0-33\nNode B: tokens 34-66\nNode C: tokens 67-100", fillcolor="#5B9BD5", fontcolor="white"];
    }

    subgraph cluster_failed {
        label="Node B Failed";
        style="rounded,filled";
        fillcolor="#FFE8E8";
        color="#CC9999";

        ring2 [label="Token Ring\n\nNode A: tokens 0-33\nNode B: DOWN\nNode C: tokens 67-100", fillcolor="#C00000", fontcolor="white"];
    }

    subgraph cluster_after {
        label="After Replacement";
        style="rounded,filled";
        fillcolor="#E8F4E8";
        color="#99CC99";

        ring3 [label="Token Ring\n\nNode A: tokens 0-33\nNode D: tokens 34-66\nNode C: tokens 67-100", fillcolor="#70AD47", fontcolor="white"];
    }

    ring1 -> ring2 [label="failure"];
    ring2 -> ring3 [label="replace"];
}
```

**Advantages of token assumption:**
- No token recalculation required
- Other nodes unaffected
- Predictable data movement
- Faster recovery than full rebalance

### Replacement Process Flow

```graphviz dot replacement-process.svg
digraph ReplacementProcess {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Node Replacement Process";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    subgraph cluster_prep {
        label="Preparation";
        style="rounded,filled";
        fillcolor="#E8E8E8";
        color="#999999";

        identify [label="Identify Dead Node\nObtain IP and Host ID", fillcolor="#5B9BD5", fontcolor="white"];
        provision [label="Provision New Node\nSame Cassandra version", fillcolor="#5B9BD5", fontcolor="white"];
        config [label="Configure Replacement\nSet replace_address_first_boot", fillcolor="#5B9BD5", fontcolor="white"];
    }

    subgraph cluster_exec {
        label="Execution";
        style="rounded,filled";
        fillcolor="#FFE8E8";
        color="#CC9999";

        start [label="New Node Starts\nContacts seeds", fillcolor="#C55A11", fontcolor="white"];
        assume [label="Token Assumption\nClaims dead node's ranges", fillcolor="#C55A11", fontcolor="white"];
        stream [label="Data Streaming\nReceives from replicas", fillcolor="#C55A11", fontcolor="white"];
    }

    subgraph cluster_complete {
        label="Completion";
        style="rounded,filled";
        fillcolor="#E8F4E8";
        color="#99CC99";

        normal [label="NORMAL State\nServes client traffic", fillcolor="#70AD47", fontcolor="white"];
        repair [label="Repair\nEnsures consistency", fillcolor="#70AD47", fontcolor="white"];
    }

    identify -> provision -> config -> start -> assume -> stream -> normal -> repair;
}
```

### Replace Address Mechanism

The `replace_address_first_boot` JVM option instructs a new node to assume a dead node's identity:

| Option | Behavior | Recommendation |
|--------|----------|----------------|
| `replace_address_first_boot` | Cleared after successful first boot | Preferred—prevents accidental re-replacement |
| `replace_address` | Persists across restarts | Legacy—can cause issues on restart |

**Architectural behavior:**
1. New node contacts seeds with replacement intent
2. Cluster validates dead node is actually DOWN
3. New node receives dead node's token assignments
4. Streaming begins from surviving replicas
5. Upon completion, new node announces NORMAL status
6. Dead node's gossip state is eventually purged

### Same-IP vs Different-IP Replacement

| Scenario | Token Handling | Host ID | Configuration |
|----------|---------------|---------|---------------|
| **Same IP** | Assumed from dead node | New ID generated | `replace_address_first_boot` with same IP |
| **Different IP** | Assumed from dead node | New ID generated | `replace_address_first_boot` with dead node's IP |

Both scenarios require the `replace_address_first_boot` option—the IP in the option always refers to the **dead node's address**, regardless of the new node's IP.

---

## Removal Architecture

### Token Redistribution Model

Node removal triggers token redistribution—the dead node's token ranges are reassigned to remaining nodes:

```graphviz dot removal-process.svg
digraph RemovalProcess {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Node Removal - Token Redistribution";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    dead [label="Dead Node Identified\nHost ID known", fillcolor="#5B9BD5", fontcolor="white"];
    initiate [label="Removal Initiated\nFrom any live node", fillcolor="#5B9BD5", fontcolor="white"];
    recalc [label="Token Recalculation\nRanges redistributed", fillcolor="#FFC000", fontcolor="black"];
    stream [label="Data Streaming\nBetween remaining nodes", fillcolor="#C55A11", fontcolor="white"];
    complete [label="Removal Complete\nNode purged from ring", fillcolor="#70AD47", fontcolor="white"];

    dead -> initiate -> recalc -> stream -> complete;
}
```

### Removal vs Decommission

| Aspect | removenode | decommission |
|--------|------------|--------------|
| **Precondition** | Node is DOWN | Node is UP and operational |
| **Initiated from** | Any live node | The departing node itself |
| **Data source** | Remaining replicas stream to each other | Departing node streams its data out |
| **Coordination** | Distributed among remaining nodes | Centralized on departing node |
| **Use case** | Unplanned failure | Planned capacity reduction |

### Assassinate Operation

The `assassinate` operation forcibly removes a node from gossip state without data redistribution:

| Characteristic | Description |
|----------------|-------------|
| **Purpose** | Emergency removal of stuck nodes |
| **Data handling** | None—no streaming occurs |
| **Risk** | Potential data loss if replicas insufficient |
| **Post-action** | Full repair required on all nodes |

**Use only when:**
- Node is unresponsive but not fully DOWN
- `removenode` fails or hangs indefinitely
- Emergency cluster recovery is required

---

## Multiple Failure Scenarios

### Concurrent Failure Analysis

When multiple nodes fail, data availability depends on the relationship between failures and replication:

```graphviz dot multiple-failures.svg
digraph MultipleFailures {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Multiple Failure Impact Analysis";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    assess [label="Assess Failure Scope\nCount failed nodes per token range", fillcolor="#5B9BD5", fontcolor="white"];

    check [label="Surviving Replicas ≥ 1\nfor all ranges?", shape=diamond, fillcolor="#E8E8E8", fontcolor="black"];

    recoverable [label="Data Recoverable\nSequential replacement possible", fillcolor="#70AD47", fontcolor="white"];
    critical [label="Data At Risk\nBackup restoration may be required", fillcolor="#C00000", fontcolor="white"];

    sequential [label="Replace One at a Time\nRepair between each", fillcolor="#70AD47", fontcolor="white"];
    restore [label="Restore from Backup\nThen rebuild cluster", fillcolor="#C00000", fontcolor="white"];

    assess -> check;
    check -> recoverable [label="Yes"];
    check -> critical [label="No"];
    recoverable -> sequential;
    critical -> restore;
}
```

### Quorum Impact Matrix

| Failed Nodes | RF=3 Availability | Recovery Strategy |
|--------------|-------------------|-------------------|
| 1 | QUORUM available (2 of 3) | Standard replacement |
| 2 | ONE available only | Urgent replacement, sequential |
| 3 (same range) | Data unavailable | Backup restoration required |

### Recovery Ordering

When multiple nodes require replacement:

1. **Assess scope**: Identify which token ranges are affected
2. **Prioritize**: Replace nodes affecting most-critical ranges first
3. **Sequential execution**: Complete one replacement before starting next
4. **Repair between**: Run repair after each replacement to ensure consistency
5. **Verify coverage**: Confirm all ranges have sufficient replicas before proceeding

---

## Data Consistency Considerations

### Streaming During Replacement

During replacement, the new node receives data from surviving replicas:

| Source Selection | Criteria |
|------------------|----------|
| **Prefer local DC** | Minimize cross-datacenter traffic |
| **Prefer least loaded** | Distribute streaming impact |
| **Avoid concurrent streamers** | Prevent resource contention |

### Post-Replacement Consistency

After replacement completes, data consistency may require repair:

| Scenario | Repair Recommendation |
|----------|----------------------|
| Short downtime (< hint window) | Hints cover gap; repair optional |
| Extended downtime (> hint window) | Repair required for missed writes |
| Multiple failures | Full repair recommended |
| Consistency-critical data | Always run repair |

The hint window (default: 3 hours) determines whether hinted handoff can cover writes during downtime. Beyond this window, hints expire and repair becomes necessary.

---

## Related Documentation

- **[Node Lifecycle](node-lifecycle.md)** - Bootstrap, decommission, and state transitions
- **[Gossip Protocol](gossip.md)** - Failure detection mechanics
- **[Data Streaming](../distributed-data/streaming.md)** - Streaming architecture during replacement
- **[Scaling Operations](scaling.md)** - Capacity planning after node removal
- **[Fault Tolerance](../fault-tolerance/index.md)** - Failure scenarios and recovery patterns
- **[Operations: Cluster Management](../../operations/cluster-management/index.md)** - Step-by-step procedures

