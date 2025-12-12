# Distributed Data

Cassandra distributes data across multiple nodes to achieve fault tolerance and horizontal scalability. This section covers the three interconnected mechanisms that govern how data is distributed, replicated, and accessed consistently across the cluster.

---

## Theoretical Foundations

Cassandra's distributed architecture derives from Amazon's Dynamo paper ([DeCandia et al., 2007, "Dynamo: Amazon's Highly Available Key-value Store"](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)), which introduced techniques for building highly available distributed systems.

| Dynamo Concept | Purpose | Cassandra Implementation |
|----------------|---------|-------------------------|
| Consistent hashing | Distribute data across nodes | Token ring with partitioners |
| Virtual nodes | Even distribution, incremental scaling | vnodes (num_tokens) |
| Replication | Fault tolerance | Configurable replication factor |
| Sloppy quorum | Availability during failures | Hinted handoff |
| Vector clocks | Conflict resolution | Timestamps (last-write-wins) |
| Merkle trees | Efficient synchronization | Merkle tree synchronization |
| Gossip protocol | Failure detection, membership | [Gossip protocol](../cluster-management/gossip.md) |
| CAP theorem | Consistency/availability trade-off | Tunable consistency per operation |

Cassandra implements most Dynamo concepts but makes different trade-offs in some areas.

!!! info "Timestamps vs Vector Clocks"
    Cassandra uses timestamps for conflict resolution rather than vector clocks, choosing simplicity over preserving all conflicting versions. This means concurrent writes to the same key result in last-write-wins semantics based on timestamp, rather than preserving both versions for application-level resolution.

---

## Masterless Architecture

Cassandra's defining architectural characteristic is its **masterless** (or "peer-to-peer") design. Every node in a Cassandra cluster is identical in function—there is no primary, leader, master, or coordinator node that holds special responsibility for the cluster. Unlike systems that require distinct node roles (primary/replica, leader/follower, master/slave), Cassandra nodes are homogeneous: same configuration, same binary, same capabilities. This architectural simplicity translates directly to operational simplicity—adding capacity means deploying identical nodes, and any node can be replaced without special failover procedures.

### What Masterless Means

**Traditional Master-Based System:**

```graphviz dot master-based.svg
digraph MasterBased {
    bgcolor="transparent"
    rankdir=TB
    graph [fontname="Roboto Flex", fontsize=11, nodesep=0.8]
    node [fontname="Roboto Flex", fontsize=11]
    edge [fontname="Roboto Flex", fontsize=10]

    node [shape=box, style="rounded,filled"]

    Client [label="Client", fillcolor="#E8F4FD"]
    Primary [label="PRIMARY\n(Master)", fillcolor="#FFD699"]
    Replica1 [label="REPLICA 1\n(read-only)", fillcolor="#D4E6F1"]
    Replica2 [label="REPLICA 2\n(read-only)", fillcolor="#D4E6F1"]

    Client -> Primary [label="writes", color="#CC6600", penwidth=2]
    Primary -> Replica1 [label="replicates", style=dashed, color="#666666"]
    Primary -> Replica2 [label="replicates", style=dashed, color="#666666"]
    Replica1 -> Client [label="reads", color="#336699", style=dashed]
    Replica2 -> Client [label="reads", color="#336699", style=dashed]

    labelloc="b"
    label="• Writes MUST go to primary\n• Primary failure requires election/failover\n• Replicas are read-only"
}
```

**Cassandra Masterless Design:**

```graphviz circo masterless.svg
graph Masterless {
    bgcolor="transparent"
    graph [fontname="Roboto Flex", fontsize=11]
    node [fontname="Roboto Flex", fontsize=11]
    edge [fontname="Roboto Flex", fontsize=10]

    node [shape=circle, style=filled, fillcolor="#B8D4E8", width=1, fixedsize=true]

    A [label="Node A"]
    B [label="Node B"]
    C [label="Node C"]
    D [label="Node D"]
    E [label="Node E"]
    F [label="Node F"]

    A -- B -- C -- D -- E -- F -- A
    A -- C -- E -- A
    B -- D -- F -- B
    C -- F

    Client [label="Client", shape=box, style="rounded,filled", fillcolor="#E8F4FD", width=0.8, fixedsize=false]

    Client -- A [label="r/w", style=dashed]
    Client -- C [label="r/w", style=dashed]
    Client -- E [label="r/w", style=dashed]

    labelloc="b"
    label="• ANY node accepts reads AND writes\n• No election required on failure\n• All nodes are equal peers"
}
```

In Cassandra:
- Any node can serve as **coordinator** for any request
- The coordinator role is assigned per-request, not per-cluster
- No node holds special metadata or routing responsibility
- Cluster continues operating if any node (or multiple nodes) fails

### Comparison with Master-Based Systems

| System | Architecture | Write Path | Failure Behavior |
|--------|--------------|------------|------------------|
| **Cassandra** | Masterless | Any node accepts writes for any partition | No failover needed; remaining nodes continue |
| **MongoDB** | Primary/Secondary | Writes to primary only; primary replicates to secondaries | Election required; brief write unavailability |
| **MySQL (Group Replication)** | Single-primary or Multi-primary | Single-primary: one node; Multi-primary: any node | Primary election on failure |
| **PostgreSQL (Streaming)** | Primary/Standby | Primary only; standbys are read-only | Manual or automatic failover required |
| **CockroachDB** | Raft consensus | Leader per range; leader accepts writes | Raft leader election per range |
| **TiDB** | Raft consensus | Leader per region; leader accepts writes | Raft leader election per region |
| **Redis Cluster** | Primary/Replica per slot | Primary for each hash slot | Failover election per slot |

### How Coordinator Selection Works

Cassandra drivers establish connections to all nodes in the local datacenter (and optionally remote DCs). The driver maintains a connection pool to each node and load balances requests across them. For each request:

```
1. Driver selects a coordinator node (load balancing across all connected nodes)
2. That node becomes the COORDINATOR for this request
3. Coordinator determines which nodes hold the data (using token ring)
4. Coordinator forwards request to appropriate replica nodes
5. Coordinator collects responses and returns result to client

Request 1: Client → Node A (coordinator) → Nodes B, C, D (replicas)
Request 2: Client → Node C (coordinator) → Nodes A, E, F (replicas)
Request 3: Client → Node B (coordinator) → Nodes C, D, A (replicas)

Each request can use a different coordinator.
No node is "special" or required for cluster operation.
```

```graphviz dot coordinator-flow.svg
digraph CoordinatorFlow {
    bgcolor="transparent"
    rankdir=LR
    graph [fontname="Roboto Flex", fontsize=11, nodesep=0.6, ranksep=0.8]
    node [fontname="Roboto Flex", fontsize=10]
    edge [fontname="Roboto Flex", fontsize=9]

    node [shape=box, style="rounded,filled"]

    Client [label="Client", fillcolor=lightyellow]
    Coordinator [label="Node B\n(Coordinator\nfor this request)", fillcolor=lightgreen]

    subgraph cluster_replicas {
        label="Replica Nodes for partition"
        style=rounded
        bgcolor=white

        R1 [label="Node A\n(Replica 1)", fillcolor=lightblue]
        R2 [label="Node D\n(Replica 2)", fillcolor=lightblue]
        R3 [label="Node F\n(Replica 3)", fillcolor=lightblue]
    }

    Client -> Coordinator [label="1. Request"]
    Coordinator -> R1 [label="2. Forward"]
    Coordinator -> R2 [label="2. Forward"]
    Coordinator -> R3 [label="2. Forward"]
    R1 -> Coordinator [label="3. ACK", style=dashed]
    R2 -> Coordinator [label="3. ACK", style=dashed]
    Coordinator -> Client [label="4. Response\n(after quorum)", color=green, penwidth=2]
}
```

### Benefits of Masterless Design

| Benefit | Description |
|---------|-------------|
| **No single point of failure** | Any node can fail without affecting cluster availability |
| **No failover delay** | No election process; operations continue immediately |
| **Linear write scalability** | All nodes accept writes; adding nodes increases write capacity |
| **Simpler operations** | No primary/replica distinction to manage |
| **Geographic distribution** | Each datacenter is autonomous; no cross-DC leader election |

### Trade-offs of Masterless Design

| Trade-off | Description | Mitigation |
|-----------|-------------|------------|
| **Conflict resolution** | Concurrent writes to same key can conflict | Last-write-wins (timestamps); LWT for critical operations |
| **No single source of truth** | No authoritative primary for reads | Quorum reads; repair for convergence |
| **Coordination overhead** | Each request requires multi-node coordination | Token-aware routing; LOCAL_* consistency levels |
| **Complexity in ordering** | No global write ordering | Per-partition ordering; application-level sequencing |

### Consistency Guarantees: Master-Based vs Masterless

Master-based architectures achieve consistency through a single authoritative node—but at the cost of availability during failures and a write throughput ceiling. Cassandra provides the same guarantees when needed, while allowing flexibility to optimize for availability or performance when strong consistency is not required.

| Requirement | Master-Based Approach | Cassandra Approach |
|-------------|----------------------|-------------------|
| **Strong consistency** | All writes through primary (single point of failure, write bottleneck) | SERIAL consistency via Paxos (no single point of failure, scales horizontally) |
| **Conflict resolution** | Primary is authoritative (unavailable during failover) | Last-write-wins by default; LWT for compare-and-set when needed |
| **Read-your-writes** | Read from primary (adds latency, primary overload risk) | QUORUM reads + writes (R + W > N), load balanced across replicas |

!!! tip "Key Difference"
    Master-based systems force strong consistency at all times with corresponding availability trade-offs. Cassandra allows per-query tuning—strong consistency for financial transactions, eventual consistency for analytics or caching.

### Multi-Datacenter Masterless Operation

Cassandra's masterless design extends across datacenters:

- Single cluster spans multiple datacenters with topology-aware replication
- No cross-DC leader election required
- LOCAL_QUORUM enables DC-local consistency without cross-DC coordination
- Cluster continues operating if one DC fails entirely

```graphviz dot multi-dc-masterless.svg
digraph MultiDCMasterless {
    bgcolor="transparent"
    rankdir=LR
    compound=true
    graph [fontname="Roboto Flex", fontsize=11]
    node [fontname="Roboto Flex", fontsize=9]
    edge [fontname="Roboto Flex", fontsize=8]

    node [shape=circle, style=filled, fillcolor="white", color="#3B7FC4", width=0.5, fixedsize=true]

    subgraph cluster_dc1 {
        label="data center alpha\nRF = 3"
        style="rounded,dashed"
        color="#5B9A68"
        bgcolor="white"
        penwidth=2

        subgraph cluster_rack1_dc1 {
            label="rack 1"
            style="rounded,dotted"
            color="#5B9A68"
            fontcolor="#5B9A68"
            N1_1 [label="node 1", color="#5B9A68", penwidth=3]
            N1_2 [label="node 2"]
        }

        subgraph cluster_rack2_dc1 {
            label="rack 2"
            style="rounded,dotted"
            color="#5B9A68"
            fontcolor="#5B9A68"
            N1_6 [label="node 6"]
            N1_3 [label="node 3", color="#5B9A68", penwidth=3]
        }

        subgraph cluster_rack3_dc1 {
            label="rack 3"
            style="rounded,dotted"
            color="#5B9A68"
            fontcolor="#5B9A68"
            N1_5 [label="node 5"]
            N1_4 [label="node 4", color="#5B9A68", penwidth=3]
        }

        // Force racks horizontal within DC
        N1_1 -> N1_6 -> N1_5 [style=invis]
    }

    subgraph cluster_dc2 {
        label="data center omega\nRF = 3"
        style="rounded,dashed"
        color="#5B9A68"
        bgcolor="white"
        penwidth=2

        subgraph cluster_rack1_dc2 {
            label="rack 1"
            style="rounded,dotted"
            color="#5B9A68"
            fontcolor="#5B9A68"
            N2_1 [label="node 1", color="#5B9A68", penwidth=3]
            N2_2 [label="node 2"]
        }

        subgraph cluster_rack2_dc2 {
            label="rack 2"
            style="rounded,dotted"
            color="#5B9A68"
            fontcolor="#5B9A68"
            N2_6 [label="node 6"]
            N2_3 [label="node 3", color="#5B9A68", penwidth=3]
        }

        subgraph cluster_rack3_dc2 {
            label="rack 3"
            style="rounded,dotted"
            color="#5B9A68"
            fontcolor="#5B9A68"
            N2_5 [label="node 5"]
            N2_4 [label="node 4", color="#5B9A68", penwidth=3]
        }

        // Force racks horizontal within DC
        N2_1 -> N2_6 -> N2_5 [style=invis]
    }

    // Connect DC boxes from right edges
    N1_4 -> N2_4 [label="multi-DC\nreplication", style=bold, color="#5B9A68", dir=both, penwidth=2, ltail=cluster_dc1, lhead=cluster_dc2, tailport=e, headport=e]
}
```

!!! note "Multi-DC Latency Advantage"
    Systems using Raft or Paxos consensus across datacenters require cross-DC communication for every write, adding latency proportional to the distance between datacenters. Cassandra with LOCAL_QUORUM avoids this cross-DC round-trip for most operations.

---

## Core Concepts

### Partitioning

Partitioning determines which node stores a given piece of data. Cassandra uses consistent hashing to map partition keys to tokens, and tokens to nodes on a ring.

```
Partition Key → Hash Function → Token → Node(s)

Example:
"user:123" → Murmur3Hash → -7509452495886106294 → Node B
```

The partitioner (hash function) ensures even data distribution regardless of key patterns. This prevents hot spots where sequential keys would otherwise concentrate on a single node.

See [Partitioning](partitioning.md) for details on consistent hashing, the token ring, and partitioner options.

### Replication

Replication copies each partition to multiple nodes for fault tolerance. The replication factor (RF) determines how many copies exist.


```graphviz dot replication-rf3.svg
digraph ReplicationRF3 {
    bgcolor="transparent"
    rankdir=TB
    graph [fontname="Roboto Flex", fontsize=11, nodesep=1]
    node [fontname="Roboto Flex", fontsize=10]
    edge [fontname="Roboto Flex", fontsize=9]

    node [shape=box, style="rounded,filled"]

    subgraph cluster_nodes {
        label="RF = 3: Each partition exists on 3 nodes"
        style=invis

        NodeA [label="Node A\n(Copy 1)", fillcolor=lightblue]
        NodeB [label="Node B\n(Copy 2)", fillcolor=lightblue]
        NodeC [label="Node C\n(Copy 3)", fillcolor=lightblue]
    }

    Partition [label="Partition\n(user:123)", fillcolor=lightyellow, shape=ellipse]

    Partition -> NodeA [style=dashed]
    Partition -> NodeB [style=dashed]
    Partition -> NodeC [style=dashed]

    {rank=same; NodeA; NodeB; NodeC}
}
```

The replication strategy determines how replicas are placed—whether they respect datacenter and rack boundaries to survive infrastructure failures.

See [Replication](replication.md) for details on strategies, snitches, and configuration.

### Consistency

Consistency determines how many replicas must acknowledge reads and writes. Because replicas may temporarily diverge, the consistency level controls the trade-off between consistency, availability, and latency.

```
Write with QUORUM (RF=3):
  - Send write to all 3 replicas
  - Wait for 2 acknowledgments (majority)
  - Return success to client

Read with QUORUM (RF=3):
  - Contact 2 replicas
  - Compare responses, return newest
  - Propagate newest version to stale replicas
```

!!! tip "Strong Consistency Formula"
    The formula `R + W > N` (reads + writes > replication factor) guarantees that reads see the latest writes. With RF=3, using QUORUM (2) for both reads and writes satisfies this: 2 + 2 = 4 > 3.

See [Consistency](consistency.md) for details on consistency levels and guarantees.

### Replica Synchronization

When replicas diverge due to failures or timing differences, synchronization mechanisms detect the divergence and propagate missing data to restore convergence:

| Mechanism | Trigger | Function |
|-----------|---------|----------|
| Hinted handoff | Write to unavailable replica | Deferred delivery when replica recovers |
| Read reconciliation | Query execution | Propagates newest version to stale replicas |
| Merkle tree synchronization | Scheduled maintenance | Full dataset comparison and convergence |

See [Replica Synchronization](replica-synchronization.md) for details on convergence mechanisms.

---

## How They Work Together

A single write operation involves all three mechanisms:

```
INSERT INTO users (id, name) VALUES (123, 'Alice')
WITH CONSISTENCY QUORUM

1. PARTITIONING
   Coordinator hashes partition key:
   token(123) = -7509452495886106294

2. REPLICATION
   Look up replicas for this token:
   RF=3, NetworkTopologyStrategy → Nodes A, B, C (different racks)

3. CONSISTENCY
   Send write to all replicas, wait for QUORUM (2):
   Node A: ACK ✓
   Node B: ACK ✓
   Node C: (still writing, but QUORUM met)
   Return SUCCESS to client

4. ANTI-ENTROPY
   If Node C was temporarily down:
   - Coordinator stores hint
   - When C recovers, hint is delivered
   - If hints expire, scheduled synchronization restores convergence
```

---

## CAP Theorem

The CAP theorem, formulated by Eric Brewer in 2000 and proven by Gilbert and Lynch in 2002 ([Gilbert & Lynch, 2002, "Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services"](https://users.ece.cmu.edu/~adrian/731-sp04/readings/GL-cap.pdf)), states that a distributed data store can provide at most **two** of three guarantees simultaneously:

### The Three Properties

```graphviz dot cap-theorem.svg
digraph CAP {
    bgcolor="transparent"
    graph [fontname="Helvetica", fontsize=11, rankdir=TB]
    node [fontname="Helvetica", fontsize=10, fontcolor="black"]
    edge [fontname="Helvetica", fontsize=9, color="black", fontcolor="black", penwidth=1.5]

    node [shape=box, style="rounded,filled"]

    C [label="Consistency\n\nEvery read receives the most\nrecent write or an error", fillcolor="#ffcccc", width=2.5]
    A [label="Availability\n\nEvery request receives a\nresponse (no errors)", fillcolor="#ccffcc", width=2.5]
    P [label="Partition Tolerance\n\nSystem continues operating\ndespite network failures", fillcolor="#ccccff", width=2.5]

    CAP [label="CAP Theorem:\nChoose 2 of 3", shape=ellipse, fillcolor="#ffffcc"]

    CAP -> C
    CAP -> A
    CAP -> P

    {rank=same; C; A; P}
}
```

| Property | Definition | Implication |
|----------|------------|-------------|
| **Consistency (C)** | All nodes see the same data at the same time | Reads always return the most recent write |
| **Availability (A)** | Every request receives a non-error response | No request times out or returns failure |
| **Partition Tolerance (P)** | System continues operating despite network partitions | Nodes can be split into groups that cannot communicate |

### Partition Tolerance Is Not Optional

!!! warning "Network Partitions Are Inevitable"
    In real distributed systems, network partitions are inevitable—switches fail, cables are cut, datacenters lose connectivity. A system that cannot tolerate partitions is not a distributed system; it is a single-node system with remote storage.

Therefore, the practical choice is between:

- **CP (Consistency + Partition Tolerance)**: During a partition, reject operations that cannot guarantee consistency
- **AP (Availability + Partition Tolerance)**: During a partition, continue accepting operations even if nodes may diverge

```graphviz dot cap-choice.svg
digraph CAPChoice {
    bgcolor="transparent"
    graph [fontname="Helvetica", fontsize=11, rankdir=LR, nodesep=0.8]
    node [fontname="Helvetica", fontsize=10, fontcolor="black"]
    edge [fontname="Helvetica", fontsize=9, color="black", fontcolor="black", penwidth=1.5]

    node [shape=box, style="rounded,filled"]

    partition [label="Network\nPartition\nOccurs", fillcolor="#ffe0cc"]

    cp [label="CP Choice\n\nReject writes to maintain\nconsistency\n\n→ Some requests fail", fillcolor="#ffcccc"]
    ap [label="AP Choice\n\nAccept writes on both\nsides of partition\n\n→ Temporary inconsistency", fillcolor="#ccffcc"]

    partition -> cp [label="prioritize\nconsistency"]
    partition -> ap [label="prioritize\navailability"]
}
```

### Database Classification

| Category | Behavior During Partition | Examples |
|----------|---------------------------|----------|
| **CP** | Reject operations that cannot be consistently applied | PostgreSQL, MySQL, MongoDB (default), CockroachDB, Spanner |
| **AP** | Accept operations; resolve conflicts later | Cassandra (default), DynamoDB, Riak, CouchDB |

### Where Cassandra Sits

Cassandra is typically classified as **AP**—it prioritizes availability over consistency by default. However, this classification oversimplifies Cassandra's capabilities.

!!! note "Tunable, Not Fixed"
    Unlike most databases that are permanently CP or AP, Cassandra allows choosing the consistency-availability trade-off on a per-operation basis. The same cluster can serve AP workloads (analytics, caching) and CP workloads (transactions, user data) simultaneously.

**Default behavior (AP):**

- Writes succeed if any replica is available
- Reads return data even if replicas disagree
- Conflicts resolved by timestamp (last-write-wins)

**With tunable consistency, Cassandra can behave as CP:**

- `QUORUM` reads and writes ensure `R + W > N` (overlapping quorums)
- `ALL` requires all replicas to respond
- `SERIAL` provides linearizable consistency via Paxos

### Tunable Consistency: Per-Operation CAP Position

Unlike databases that enforce a single consistency model, Cassandra allows choosing the consistency-availability trade-off for each operation:

| Consistency Level | CAP Position | Behavior During Partition |
|-------------------|--------------|---------------------------|
| `ANY` | AP | Write succeeds if any node (including coordinator) receives it |
| `ONE` | AP | Write/read succeeds if one replica responds |
| `QUORUM` | CP | Requires majority of replicas; may reject if quorum unavailable |
| `ALL` | CP | Requires all replicas; rejects if any replica unavailable |
| `SERIAL` | CP | Linearizable via Paxos; rejects if consensus cannot be reached |

**Practical implications:**

```
Partition splits cluster: Nodes {A, B} | {C, D, E}
RF = 3, replicas on nodes A, C, E

With QUORUM (requires 2 of 3 replicas):
- Left side (A): Can reach 1 replica → QUORUM fails
- Right side (C, E): Can reach 2 replicas → QUORUM succeeds
- Result: CP behavior, partial availability

With ONE:
- Both sides can reach at least 1 replica
- Result: AP behavior, full availability, possible inconsistency
```

### CAP During Normal Operation

!!! info "CAP Only Applies During Partitions"
    The CAP theorem applies specifically during network partitions. During normal operation (no partitions), Cassandra provides both consistency and availability—the trade-off only manifests when partitions occur.

| State | Consistency | Availability | Notes |
|-------|-------------|--------------|-------|
| Normal operation | ✓ (with QUORUM) | ✓ | No trade-off required |
| During partition | Choose one | Choose one | CAP trade-off applies |
| After partition heals | ✓ (eventually) | ✓ | Repair restores consistency |

### PACELC: Beyond CAP

The PACELC theorem ([Abadi, 2012](https://cs-www.cs.yale.edu/homes/dna/papers/abadi-pacelc.pdf)) extends CAP to address behavior during normal operation:

**P**artition → **A**vailability vs **C**onsistency
**E**lse → **L**atency vs **C**onsistency

During normal operation, the trade-off is between latency and consistency:

| System | During Partition (PAC) | Normal Operation (ELC) |
|--------|------------------------|------------------------|
| Cassandra (ONE) | PA | EL (low latency, eventual consistency) |
| Cassandra (QUORUM) | PC | EC (higher latency, strong consistency) |
| PostgreSQL | PC | EC |
| DynamoDB | PA | EL |

Cassandra's tunable consistency allows choosing different PACELC positions for different operations within the same cluster.

---

## Documentation Structure

| Section | Description |
|---------|-------------|
| [Partitioning](partitioning.md) | Consistent hashing, token ring, partitioners |
| [Replication](replication.md) | Strategies, snitches, replication factor |
| [Consistency](consistency.md) | Consistency levels, guarantees, LWT |
| [Replica Synchronization](replica-synchronization.md) | Hinted handoff, read reconciliation, Merkle trees |
| [Secondary Index Queries](secondary-index-queries.md) | Distributed query execution with indexes |
| [Materialized Views](materialized-views.md) | Distributed MV coordination and consistency challenges |
| [Data Streaming](streaming.md) | Bootstrap, decommission, repair, and hinted handoff streaming |
| [Counters](counters.md) | Distributed counting, CRDTs, counter operations |

---

## Related Documentation

- **[Gossip Protocol](../cluster-management/gossip.md)** - Cluster membership and failure detection
- **[Storage Engine](../storage-engine/index.md)** - How data is stored on each node
- **[Indexes](../storage-engine/indexes/index.md)** - Secondary index types and selection
- **[Operations](../../operations/index.md)** - Maintenance and operational procedures
