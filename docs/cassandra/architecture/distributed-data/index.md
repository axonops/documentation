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
| Gossip protocol | Failure detection, membership | [Gossip protocol](../gossip/index.md) |

Cassandra implements most Dynamo concepts but makes different trade-offs in some areas. Most notably, Cassandra uses timestamps for conflict resolution rather than vector clocks, choosing simplicity over preserving all conflicting versions.

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

```
RF = 3: Each partition exists on 3 nodes

        Node A          Node B          Node C
       ┌──────┐        ┌──────┐        ┌──────┐
       │ Copy │        │ Copy │        │ Copy │
       │  1   │        │  2   │        │  3   │
       └──────┘        └──────┘        └──────┘
           │               │               │
           └───────────────┴───────────────┘
                    Same partition
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

The formula `R + W > N` (reads + writes > replication factor) guarantees that reads see the latest writes.

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

## CAP Theorem Position

Cassandra is often described as "AP" (Availability + Partition tolerance) in CAP theorem terms, but this oversimplifies its capabilities. Cassandra allows choosing a position on the consistency-availability spectrum per operation:

| Consistency Level | CAP Position | Trade-off |
|-------------------|--------------|-----------|
| ONE | AP | High availability, eventual consistency |
| QUORUM | CP | Strong consistency, reduced availability |
| ALL | CP | Strongest consistency, lowest availability |

Unlike traditional CP databases (which reject operations during partitions) or AP databases (which always accept operations), Cassandra allows per-request tuning based on the specific requirements of each operation.

---

## Documentation Structure

| Section | Description |
|---------|-------------|
| [Partitioning](partitioning.md) | Consistent hashing, token ring, partitioners |
| [Replication](replication.md) | Strategies, snitches, replication factor |
| [Consistency](consistency.md) | Consistency levels, guarantees, LWT |
| [Replica Synchronization](replica-synchronization.md) | Hinted handoff, read reconciliation, Merkle trees |
| [Counters](counters.md) | Distributed counting, CRDTs, counter operations |

---

## Related Documentation

- **[Gossip Protocol](../gossip/index.md)** - Cluster membership and failure detection
- **[Storage Engine](../storage-engine/index.md)** - How data is stored on each node
- **[Operations](../../operations/index.md)** - Maintenance and operational procedures
