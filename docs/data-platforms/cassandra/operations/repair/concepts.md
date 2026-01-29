---
title: "Cassandra Repair Concepts"
description: "Cassandra repair concepts. Anti-entropy repair and consistency maintenance."
meta:
  - name: keywords
    content: "Cassandra repair concepts, anti-entropy, Merkle trees"
---

# Repair Concepts

This page explains the fundamental concepts behind Cassandra repair operations, including how the repair process works internally, what triggers the need for repair, and the mechanisms Cassandra uses to detect and resolve data inconsistencies.

## What is Repair?

Repair is Cassandra's anti-entropy mechanism for synchronizing data across replica nodes. In a distributed system where writes may not reach all replicas (due to node failures, network partitions, or hint expiration), repair ensures that all replicas eventually contain identical data.

| | Node A | Node B | Node C |
|---|--------|--------|--------|
| **Before Repair** | Row 1: v1 | Row 1: v1 | Row 1: v1 |
| | Row 2: v2 | Row 2: v1 ⚠️ stale | Row 2: v2 |
| | Row 3: v3 | Row 3: v3 | Row 3: ❌ missing |
| **After Repair** | Row 1: v1 | Row 1: v1 | Row 1: v1 |
| | Row 2: v2 | Row 2: v2 ✓ | Row 2: v2 |
| | Row 3: v3 | Row 3: v3 | Row 3: v3 ✓ |

## Why Repair is Necessary

### Sources of Data Inconsistency

Data inconsistencies arise from several scenarios in distributed systems:

**Write Path Failures**

| Scenario | Description | Recovery Mechanism |
|----------|-------------|-------------------|
| Node unavailable during write | Write succeeds on available replicas only | Hinted handoff, read repair, anti-entropy repair |
| Network partition | Replicas in different partitions receive different writes | Anti-entropy repair |
| Coordinator timeout | Write acknowledged but some replicas slow | Read repair, anti-entropy repair |

**Recovery Limitations**

| Scenario | Description | Recovery Mechanism |
|----------|-------------|-------------------|
| Hints expired | Node was down longer than hint window (default 3 hours) | Anti-entropy repair only |

**Hint window configuration by version:**

| Version | Parameter | Default | Syntax |
|---------|-----------|---------|--------|
| 4.0 | `max_hint_window_in_ms` | `10800000` | Integer (milliseconds) |
| 4.1+ | `max_hint_window` | `3h` | Duration literal (`3h`, `180m`) |
| Hinted handoff disabled | Hints not stored for unavailable replicas | Anti-entropy repair only |

**Operational Events**

| Scenario | Description | Recovery Mechanism |
|----------|-------------|-------------------|
| New node bootstrap | Node joins but may not have all data | Streaming + repair |
| Node replacement | Replacement node needs data from replicas | Streaming + repair |

### The gc_grace_seconds Constraint

The most critical aspect of repair scheduling is the relationship with `gc_grace_seconds`. This parameter defines how long tombstones (deletion markers) are retained before garbage collection.

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Tombstone Lifecycle and gc_grace_seconds

actor Client
participant "Node A" as A
participant "Node B" as B
participant "Node C\n(DOWN)" as C

== T=0: Delete Operation ==
Client -> A : DELETE row X
A -> A : Create tombstone
A -> B : Replicate tombstone
A ->x C : Node C is down\nmisses DELETE

== T=10 days: gc_grace_seconds expires ==
A -> A : Garbage collect tombstone
B -> B : Garbage collect tombstone

== Node C recovers ==
C -> C : Still has original row X\n(no tombstone)

== Read Request ==
Client -> A : Read row X
A -> Client : Row X not found
Client -> C : Read row X
C -> Client : Row X exists!

note over A,C #FFAAAA
  ZOMBIE DATA
  Deleted row has resurrected!
end note
@enduml
```

**Zombie data resurrection scenario:**

1. Data is deleted on Node A, creating a tombstone
2. Tombstone replicates to Node B
3. Node C is down and misses the delete
4. After `gc_grace_seconds`, the tombstone is garbage collected from A and B
5. Node C comes back online with the original (pre-delete) data
6. Without the tombstone, the deleted data "resurrects" during read repair

**Prevention:** Run repair on all nodes within `gc_grace_seconds` to ensure tombstones propagate before deletion.

## How Repair Works

### The Merkle Tree Process

Cassandra uses Merkle trees (hash trees) to efficiently detect differences between replicas without comparing every row.

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Merkle Tree Comparison Process

participant "Replica A\n(Repair Coordinator)" as A
participant "Replica B" as B
participant "Replica C" as C

note over A : nodetool repair\nissued on this node

== Phase 1: Validation ==
A -> A : Build Merkle tree\nby hashing partitions
A -> B : Request Merkle tree for range
A -> C : Request Merkle tree for range

note over B : Build Merkle tree\nby hashing partitions
note over C : Build Merkle tree\nby hashing partitions

B --> A : Return tree (root hash: ABC123)
C --> A : Return tree (root hash: XYZ789)

== Phase 2: Comparison ==
note over A : Compare root hashes\nA=B ≠ C\nDrill down into C's tree
A -> A : Identify differing\nsubtrees recursively

== Phase 3: Streaming ==
A -> C : Stream differing partitions
note over C : Apply streamed data

note over A : Repair session complete
@enduml
```

**Merkle tree segments:**

The token range being repaired is divided into segments, with each segment represented as a leaf node in the Merkle tree. By default, Cassandra creates approximately 32,768 (2^15) segments per repair session.

**Merkle tree configuration by version:**

| Version | Parameter | Default | Description |
|---------|-----------|---------|-------------|
| 4.0 | `repair_session_max_tree_depth` | `20` | Maximum depth of Merkle tree |
| 4.1+ | `repair_session_space` | `16MiB` | Memory limit for Merkle trees (replaces depth) |

**Streaming granularity:**

When a mismatch is detected, the entire segment is streamed—not individual rows. This means a single differing row causes the entire segment to be transferred:

| Table Size / Node | Segments | Min Stream Unit (1 segment) |
|-------------------|----------|----------------------------|
| 100 GB | 32,768 | ~3 MB |
| 500 GB | 32,768 | ~15 MB |
| 1 TB | 32,768 | ~30 MB |

For example, with a 500 GB table, if one row is inconsistent, the entire ~15 MB segment containing that row must be streamed. If inconsistencies are spread across many segments, streaming volumes increase proportionally.

**Merkle tree comparison and streaming:**

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial
skinparam rectangleBorderColor #333333

title Merkle Tree Comparison Between Two Replicas

rectangle "Replica A (Repair Coordinator)" as RA {
    rectangle "Root: 0xABC123" as RA_root #90EE90
    rectangle "Hash: 0x111" as RA_L #90EE90
    rectangle "Hash: 0x222" as RA_R #FFB6C1
    rectangle "Seg 1" as RA_S1 #90EE90
    rectangle "Seg 2" as RA_S2 #90EE90
    rectangle "Seg 3" as RA_S3 #FFB6C1
    rectangle "Seg 4" as RA_S4 #90EE90
}

rectangle "Replica B" as RB {
    rectangle "Root: 0xDEF456" as RB_root #FFB6C1
    rectangle "Hash: 0x111" as RB_L #90EE90
    rectangle "Hash: 0x333" as RB_R #FFB6C1
    rectangle "Seg 1" as RB_S1 #90EE90
    rectangle "Seg 2" as RB_S2 #90EE90
    rectangle "Seg 3" as RB_S3 #FFB6C1
    rectangle "Seg 4" as RB_S4 #90EE90
}

RA_S1 --> RA_L
RA_S2 --> RA_L
RA_S3 --> RA_R
RA_S4 --> RA_R
RA_L --> RA_root
RA_R --> RA_root

RB_S1 --> RB_L
RB_S2 --> RB_L
RB_S3 --> RB_R
RB_S4 --> RB_R
RB_L --> RB_root
RB_R --> RB_root

RA_S3 -[#CC0000,bold]-> RB_S3 : Stream\nSegment 3

note bottom of RA
  Green = matching hash
  Pink = mismatching hash

  Root hashes differ → drill down
  Left subtrees match → skip
  Right subtrees differ → check segments
  Segment 3 differs → stream data
end note
@enduml
```

The comparison process:

1. Compare root hashes—if they match, replicas are identical (no streaming needed)
2. If root hashes differ, compare child hashes recursively
3. Drill down only into subtrees with mismatching hashes
4. At the leaf level, stream the entire segment for any mismatching hash

### Repair Session Lifecycle

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Repair Session Lifecycle

[*] --> Initiated : nodetool repair

Initiated --> Preparing : Acquire repair\nsession ID

Preparing --> Validating : Build Merkle\ntrees on replicas

Validating --> Comparing : Trees received\nfrom all replicas

Comparing --> Streaming : Differences\nidentified

Streaming --> Completing : All data\nstreamed

Completing --> [*] : Success

Validating --> Failed : Timeout or\nnode failure
Comparing --> Failed : Comparison\nerror
Streaming --> Failed : Stream\nfailure

Failed --> [*] : Error reported

note right of Validating
  Most resource-intensive phase:
  - Reads all data in range
  - Computes hashes
  - Memory for tree storage
end note

note right of Streaming
  Network-intensive phase:
  - Transfers differing data
  - Triggers compaction
end note
@enduml
```

## Repair Types

### Full Repair

Full repair is the original repair mechanism in Cassandra. It compares all data in the specified token ranges across all replicas, regardless of whether the data has been previously repaired.

**How it works:**

1. The repair coordinator builds a Merkle tree from all SSTables in the repair range
2. Each replica builds its own Merkle tree from all its SSTables
3. Trees are compared to identify differences
4. Differing data is streamed between replicas to synchronize

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial
skinparam rectangleBorderColor #333333
skinparam rectangleBackgroundColor #FAFAFA

title Full Repair: All SSTables Included in Comparison

rectangle "Replica A (Repair Coordinator)" as RA {
    rectangle "SSTable 1" as RA1 #87CEEB
    rectangle "SSTable 2" as RA2 #87CEEB
    rectangle "SSTable 3" as RA3 #87CEEB
    rectangle "SSTable 4" as RA4 #87CEEB
}

rectangle "Replica B" as RB {
    rectangle "SSTable 1" as RB1 #87CEEB
    rectangle "SSTable 2" as RB2 #87CEEB
    rectangle "SSTable 3" as RB3 #87CEEB
}

rectangle "Replica C" as RC {
    rectangle "SSTable 1" as RC1 #87CEEB
    rectangle "SSTable 2" as RC2 #87CEEB
    rectangle "SSTable 3" as RC3 #87CEEB
}

RA -[#0066CC]-> RB : Repair ALL SSTables
RA -[#0066CC]-> RC : Repair ALL SSTables

note bottom of RA
  Full repair ignores repaired/unrepaired status.
  All SSTables are validated and synchronized.
end note
@enduml
```

**Advantages:**

- Simple and reliable - no complex state tracking
- Guarantees complete consistency check across all data
- No risk of repaired/unrepaired state corruption
- Works correctly regardless of previous repair history
- Required after certain failure scenarios

**Disadvantages:**

- Re-validates already-consistent data unnecessarily
- Longer duration as data volume grows
- Higher resource consumption (CPU, memory, network, disk I/O)

**When to use full repair:**

- After node replacement or rebuild
- After recovering from data corruption
- When incremental repair state is suspect or corrupted
- Before major version upgrades
- As periodic validation (e.g., monthly) alongside incremental repairs

---

### Incremental Repair

Incremental repair was introduced in Cassandra 2.1 via [CASSANDRA-5351](https://issues.apache.org/jira/browse/CASSANDRA-5351) to address the scalability limitations of full repair. It tracks which SSTables have been previously repaired and only validates new (unrepaired) data.

**History and evolution:**

Incremental repair had a troubled history in early versions. While the concept was sound, the implementation suffered from numerous bugs that could lead to data inconsistency, silent corruption of the repaired/unrepaired state, and operational challenges. Many operators avoided incremental repair entirely in versions prior to 4.0, preferring the slower but more reliable full repair.

| Version | Status | Notes |
|---------|--------|-------|
| 2.1 | Introduced | Initial implementation; significant bugs and edge cases |
| 2.2 - 3.x | Problematic | Ongoing fixes but still unreliable for production use; many operators avoided it |
| 4.0+ | Production ready | Major rework; became default behavior; full repair requires `-full` flag |

**Recommendation:** For clusters running Cassandra 4.0 or later, incremental repair is the recommended approach for routine maintenance. For earlier versions, evaluate carefully and consider using full repair if stability is a concern.

**How it works:**

1. Each SSTable has a `repairedAt` metadata field (0 = unrepaired, timestamp = repaired)
2. During incremental repair, only SSTables with `repairedAt = 0` are included in Merkle tree generation
3. After successful repair, participating SSTables are marked with a `repairedAt` timestamp
4. Subsequent repairs skip already-repaired SSTables
5. Anti-compaction separates repaired and unrepaired data when SSTables contain both

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial
skinparam rectangleBorderColor #333333
skinparam rectangleBackgroundColor #FAFAFA

title Incremental Repair: Only Unrepaired SSTables Compared

rectangle "Replica A (Repair Coordinator)" as RA {
    rectangle "SSTable 1\n(repaired)\nSKIPPED" as RA1 #CCCCCC
    rectangle "SSTable 2\n(repaired)\nSKIPPED" as RA2 #CCCCCC
    rectangle "SSTable 3\n(unrepaired)\nINCLUDED" as RA3 #90EE90
    rectangle "SSTable 4\n(unrepaired)\nINCLUDED" as RA4 #90EE90
}

rectangle "Replica B" as RB {
    rectangle "SSTable 1\n(repaired)\nSKIPPED" as RB1 #CCCCCC
    rectangle "SSTable 2\n(repaired)\nSKIPPED" as RB2 #CCCCCC
    rectangle "SSTable 3\n(unrepaired)\nINCLUDED" as RB3 #90EE90
}

rectangle "Replica C" as RC {
    rectangle "SSTable 1\n(repaired)\nSKIPPED" as RC1 #CCCCCC
    rectangle "SSTable 2\n(unrepaired)\nINCLUDED" as RC2 #90EE90
    rectangle "SSTable 3\n(unrepaired)\nINCLUDED" as RC3 #90EE90
}

RA -[#0066CC]-> RB : Repair UNREPAIRED SSTables only
RA -[#0066CC]-> RC : Repair UNREPAIRED SSTables only

note bottom of RA
  After incremental repair:
  - Unrepaired SSTables marked as repaired
  - Next incremental skips already-repaired data
  - Smaller Merkle trees = faster validation
end note
@enduml
```

**Advantages:**

- Faster execution - only validates new data since last repair
- Lower resource consumption for routine maintenance
- Scales better with large datasets
- Enables more frequent repair cycles
- Reduces repair window, making it easier to complete within `gc_grace_seconds`

**Disadvantages:**

- Anti-compaction overhead after repair completion (see below)
- More complex operational model to understand and troubleshoot

**Anti-compaction considerations:**

After incremental repair completes, Cassandra runs anti-compaction to split SSTables that contain both repaired and unrepaired data. This process:

- Reads the SSTable and writes two new SSTables (one repaired, one unrepaired)
- Consumes disk I/O and temporary disk space (up to 2x the SSTable size during the split)
- Adds to compaction pending tasks
- Can delay the start of normal compaction work

Operational guidance:

- Monitor `CompactionManager` pending tasks during and after repair
- Ensure sufficient disk headroom (anti-compaction temporarily increases disk usage)
- On I/O-constrained systems, consider scheduling repairs during low-traffic periods
- The `nodetool compactionstats` command shows anti-compaction progress

**When to use incremental repair:**

- Routine scheduled maintenance (default choice for Cassandra 4.0+)
- Clusters with large data volumes where full repair is impractical
- When repair must complete within tight time windows

---

### Comparison Summary

| Aspect | Full Repair | Incremental Repair |
|--------|-------------|-------------------|
| Scope | All data in range | Only unrepaired SSTables |
| SSTable marking | Does not modify SSTable metadata | Marks SSTables with `repairedAt` timestamp |
| Duration | Longer (proportional to total data) | Shorter (proportional to new data) |
| Resource usage | Higher | Lower for routine runs |
| Complexity | Simple | Requires state tracking |
| Use case | Recovery, validation, periodic full check | Regular maintenance |
| Default (4.0+) | Must specify `-full` flag | Default behavior |

---

### Repaired vs Unrepaired SSTables

Incremental repair tracks repair state at the SSTable level:

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title SSTable Repair State Tracking

rectangle "New SSTable\nCreated" as new #87CEEB

rectangle "Flushed to Disk\n(unrepaired)\nrepairedAt = 0" as flushed #FFB6C1

rectangle "After Incremental\nRepair (repaired)\nrepairedAt = timestamp" as repaired #90EE90

rectangle "Compacted with\nother repaired" as compacted #90EE90

new --> flushed : flush/\ncompaction
flushed --> repaired : incremental\nrepair
repaired --> compacted : compaction

note right of repaired
  Repaired SSTables:
  - Have repairedAt timestamp
  - Excluded from future
    incremental repairs
  - Compacted separately
    from unrepaired
end note

note right of flushed
  Unrepaired SSTables:
  - repairedAt = 0
  - Included in next
    incremental repair
end note
@enduml
```

## Token Ranges and Repair Scope

### Understanding Token Ranges

Cassandra partitions data across nodes using a token ring. Each node is responsible for specific token ranges.

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Token Ring and Primary Ranges (RF=3)

rectangle "Node A\nTokens: 0-25" as A #LightBlue
rectangle "Node B\nTokens: 25-50" as B #LightGreen
rectangle "Node C\nTokens: 50-75" as C #LightYellow
rectangle "Node D\nTokens: 75-100" as D #LightPink

A --> B : clockwise
B --> C
C --> D
D --> A

note bottom of A
  Primary: 0-25
  Replicas: 75-100, 50-75
end note

note bottom of B
  Primary: 25-50
  Replicas: 0-25, 75-100
end note

note bottom of C
  Primary: 50-75
  Replicas: 25-50, 0-25
end note

note bottom of D
  Primary: 75-100
  Replicas: 50-75, 25-50
end note
@enduml
```

### Primary Range Repair (-pr)

The `-pr` flag limits repair to only the primary token ranges owned by the node:

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Primary Range Repair (-pr) Behavior

rectangle "Without -pr (Full Range)" as without {
    rectangle "Range 0-25\n(primary)" as W1 #90EE90
    rectangle "Range 75-100\n(replica)" as W2 #90EE90
    rectangle "Range 50-75\n(replica)" as W3 #90EE90
}

note bottom of without
  Repairs ALL ranges this
  node holds, causing
  redundant work
end note

rectangle "With -pr (Primary Only)" as withpr {
    rectangle "Range 0-25\n(primary)" as P1 #90EE90
    rectangle "Range 75-100\n(skipped)" as P2 #CCCCCC
    rectangle "Range 50-75\n(skipped)" as P3 #CCCCCC
}

note bottom of withpr
  Repairs ONLY primary
  range. Other nodes
  repair their primaries.
end note
@enduml
```

**Recommendation:** Always use `-pr` for routine maintenance. Running `-pr` on each node in sequence ensures every range is repaired exactly once.

## Repair Coordination

### Behavior Without Keyspace or Table Specification

When running repair without specifying tables, Cassandra iterates through all tables in the keyspace:

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Repair Iteration Behavior

start

if (Keyspace specified?) then (no)
  :Get all non-system keyspaces;
  note right: Iterates through\nall user keyspaces
else (yes)
  :Use specified keyspace;
endif

if (Tables specified?) then (no)
  :Get all tables in keyspace;
  note right
    For each table:
    1. Build Merkle trees
    2. Compare with replicas
    3. Stream differences

    Tables repaired sequentially
    unless -j specified
  end note

  while (More tables?) is (yes)
    :Repair next table;
    :Wait for completion;
  endwhile (no)
else (yes)
  :Repair specified tables only;
endif

stop
@enduml
```

**Important considerations:**

- Tables are repaired sequentially by default
- Use `-j <threads>` to repair multiple tables in parallel
- Large tables dominate repair duration
- Consider repairing critical tables separately

## Anti-Compaction

After incremental repair, Cassandra performs anti-compaction to separate repaired and unrepaired data:

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Anti-Compaction Process

rectangle "Before Anti-Compaction" as before {
    rectangle "SSTable A (mixed data)" as mixed {
        rectangle "Repaired partitions" as RP1 #90EE90
        rectangle "Unrepaired partitions" as UP1 #FFB6C1
    }
}

rectangle "After Anti-Compaction" as after {
    rectangle "SSTable A-repaired" as afterR #90EE90 {
        rectangle "Repaired only" as RP2
    }
    rectangle "SSTable A-unrepaired" as afterU #FFB6C1 {
        rectangle "Unrepaired only" as UP2
    }
}

before --> after : Split by\nrepair status

note bottom of afterR
  Marked with repairedAt
  timestamp. Excluded from
  future incremental repairs.
end note
@enduml
```

Anti-compaction ensures clean separation between repaired and unrepaired data, enabling efficient future incremental repairs.

## Paxos Repairs

While standard repairs reconcile user table data across replicas, **Paxos repairs** specifically reconcile the **Paxos state** used by **[lightweight transactions (LWTs)](../../cql/dml/lightweight-transactions.md)**. LWTs are statements that include `IF` conditions (such as `INSERT ... IF NOT EXISTS` or `UPDATE ... IF column = value`), which provide linearizable consistency guarantees.

Paxos repairs maintain LWT **linearizability** and correctness, especially across **topology changes** such as bootstrap, decommission, replace, and move operations.

### When Paxos Repairs Are Required

Paxos repairs are only relevant for **keyspaces that use LWTs**. For keyspaces that never use LWTs, Paxos state does not affect correctness, and operators **MAY** safely skip Paxos repairs for those keyspaces.

In Cassandra 4.1+, Paxos repairs run automatically every 5 minutes by default. Operators **SHOULD** ensure Paxos repairs run regularly on clusters where LWTs are in use. See [Paxos Repairs](strategies.md#paxos-repairs) in the Repair Strategies guide for operational details.

### Paxos Repairs and Topology Changes

In Cassandra 4.1 and later, a **Paxos repair gate** runs before certain topology changes complete (for example, node bootstrap). This gate ensures that Paxos state is consistent across all replicas for the affected token ranges before the topology change finalizes.

If Paxos repair cannot complete for the affected ranges and keyspaces—for example, because nodes are overloaded, have very large partitions, or some replicas are unavailable—the topology change **MUST** fail to avoid violating LWT correctness guarantees.

Operators **MAY** encounter errors such as `PaxosCleanupException` with message `CANCELLED` when overloaded replicas cannot finish Paxos cleanup within the allowed time. This typically indicates that the cluster is under too much load or that specific partitions are too large for Paxos cleanup to complete successfully.

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Paxos Repair Gate During Topology Change

participant "Joining Node" as JN
participant "Coordinator" as C
participant "Existing Replicas" as ER

JN -> C : Request bootstrap
C -> C : Identify affected\ntoken ranges

== Paxos Repair Gate ==
C -> ER : Initiate Paxos cleanup\nfor affected ranges
note right of ER
  Each replica must complete
  Paxos cleanup for LWT keyspaces
end note

alt All replicas complete cleanup
    ER --> C : Cleanup complete
    C -> JN : Proceed with bootstrap
    JN -> ER : Stream data
    JN -> C : Bootstrap complete
else Cleanup fails (timeout, overload, etc.)
    ER --> C : PaxosCleanupException\n(CANCELLED)
    C -> JN : Bootstrap FAILED
    note over JN,ER #FFAAAA
      Topology change blocked
      to preserve LWT correctness
    end note
end

@enduml
```

### Paxos v2

Cassandra 4.1+ introduces **Paxos v2**, an updated Paxos implementation for lightweight transactions. Paxos v2 provides several improvements:

- **Reduced network round-trips** for LWT reads and writes
- **Improved behavior under contention** when multiple clients compete for the same partition
- **Works in conjunction with regular Paxos repairs** and Paxos state purging

Paxos v2 is selected via the `paxos_variant` setting in `cassandra.yaml` (values: `v1` or `v2`).

To safely take full advantage of Paxos v2, operators **MUST** ensure:

1. **Regular Paxos repairs** are running on all nodes
2. **Paxos state purging** is configured appropriately (see [Paxos-related cassandra.yaml configuration](strategies.md#paxos-related-cassandrayaml-configuration) in the Repair Strategies guide)

Detailed configuration options and upgrade guidance are covered in the [Repair Strategies](strategies.md) documentation.

## Next Steps

- **[Options Reference](options-reference.md)** - Detailed explanation of all repair options
- **[Repair Strategies](strategies.md)** - Real-world implementation scenarios
- **[Scheduling Guide](scheduling.md)** - Planning repair schedules within gc_grace_seconds