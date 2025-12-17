---
title: "Cassandra Repair Options Reference"
description: "Cassandra repair options reference. All nodetool repair flags and settings."
meta:
  - name: keywords
    content: "Cassandra repair options, nodetool repair flags, repair settings"
---

# Repair Options Reference

This page provides detailed explanations of all repair command options, including visual diagrams showing how each option affects repair behavior.

## Command Syntax

```bash
nodetool repair [options] [keyspace [table ...]]
```

## Scope Options

### -pr, --partitioner-range (Primary Range)

Repairs only the token ranges for which this node is the primary owner.

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Primary Range Repair (-pr)

rectangle "4-Node Cluster (RF=3)" as cluster {
    rectangle "Node 1 (tokens 0-25)" as N1 #LightBlue
    rectangle "Node 2 (tokens 25-50)" as N2 #LightGreen
    rectangle "Node 3 (tokens 50-75)" as N3 #LightYellow
    rectangle "Node 4 (tokens 75-100)" as N4 #LightPink
}

rectangle "Repair WITHOUT -pr on Node 1" as without {
    rectangle "Range 0-25" as W1 #90EE90
    rectangle "Range 75-100" as W2 #90EE90
    rectangle "Range 50-75" as W3 #90EE90
}

note bottom of without
  Repairs ALL ranges Node 1 holds
  (primary + replicas) = 3x work per node
end note

rectangle "Repair WITH -pr on Node 1" as withpr {
    rectangle "Range 0-25" as P1 #90EE90
    rectangle "Range 75-100" as P2 #CCCCCC
    rectangle "Range 50-75" as P3 #CCCCCC
}

note bottom of withpr
  Repairs ONLY primary range
  Other nodes repair their primaries
  = 1x work per node
end note
@enduml
```

**Usage:**
```bash
# Recommended for routine maintenance
nodetool repair -pr my_keyspace
```

**When to use:**
- Regular scheduled repairs
- Running repair on every node in sequence
- Minimizing redundant work

**When NOT to use:**
- Single-node recovery scenarios
- Verifying specific replica consistency

### -full (Full Repair)

Forces full repair instead of incremental repair, validating all data regardless of repair status.

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Full Repair vs Incremental (Default)

rectangle "Incremental Repair (Default)" as inc {
    rectangle "Repaired SSTable 1\n(repairedAt: timestamp)" as IR1 #CCCCCC
    rectangle "Repaired SSTable 2\n(repairedAt: timestamp)" as IR2 #CCCCCC
    rectangle "Unrepaired SSTable 3\n(repairedAt: 0)" as IU1 #90EE90
    rectangle "Unrepaired SSTable 4\n(repairedAt: 0)" as IU2 #90EE90
}

note bottom of inc
  Only unrepaired SSTables
  are validated (green)
end note

rectangle "Full Repair (-full)" as full {
    rectangle "SSTable 1" as FR1 #90EE90
    rectangle "SSTable 2" as FR2 #90EE90
    rectangle "SSTable 3" as FU1 #90EE90
    rectangle "SSTable 4" as FU2 #90EE90
}

note bottom of full
  ALL SSTables validated
  regardless of repair status
end note
@enduml
```

**Usage:**
```bash
# Full repair of all data
nodetool repair -full my_keyspace

# Combine with -pr for full primary-range repair
nodetool repair -full -pr my_keyspace
```

**When to use:**
- After node replacement or rebuild
- After data corruption recovery
- When incremental repair state is suspect
- Before major version upgrades

### -st, -et (Subrange Repair)

Repairs only a specific token range, enabling parallel repair operations or targeted recovery.

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Subrange Repair (-st, -et)

rectangle "Full Token Range" as full {
    rectangle "-9223372036854775808" as min
    rectangle "0" as zero
    rectangle "9223372036854775807" as max
}
min -right-> zero
zero -right-> max

rectangle "Subrange Repair Example" as sub {
    rectangle "Start Token" as st #LightBlue
    rectangle "End Token" as et #LightBlue
}

note bottom of sub
  Only the specified range is repaired
  -st -9223372036854775808 -et -3074457345618258603
end note

rectangle "Parallel Subrange Strategy" as parallel {
    rectangle "Range 1" as R1 #LightBlue
    rectangle "Range 2" as R2 #LightGreen
    rectangle "Range 3" as R3 #LightYellow
    rectangle "Range 4" as R4 #LightPink
}

note bottom of parallel
  Split into N subranges
  Repair each in parallel
  on different threads/nodes
end note
@enduml
```

**Usage:**
```bash
# Repair specific token range
nodetool repair -st -9223372036854775808 -et -3074457345618258603 my_keyspace

# Get token ranges for a node
nodetool describering my_keyspace
```

**Use cases:**
- Parallel repair across multiple sessions
- Targeted repair of specific token ranges
- Recovery of specific data segments

---

## Parallelism Options

### --parallel vs -seq, --sequential

Controls whether replicas validate data simultaneously or one at a time. Parallel is the default in Cassandra 4.0+.

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Sequential Repair (-seq)

participant "Replica A\n(Repair Coordinator)" as A
participant "Replica B" as B
participant "Replica C" as C

A -> A : Validate
A -> B : Validate
B --> A : Complete
A -> C : Validate
C --> A : Complete

note over A,C
  One replica at a time
  Lower resource usage
  Longer total duration
end note
@enduml
```

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Parallel Repair (--parallel)

participant "Replica A\n(Repair Coordinator)" as A
participant "Replica B" as B
participant "Replica C" as C

A -> A : Validate
A -> B : Validate
A -> C : Validate
B --> A : Complete
C --> A : Complete

note over A,C
  All replicas simultaneously
  Higher resource usage
  Shorter total duration
end note
@enduml
```

**Usage:**
```bash
# Sequential (lower impact, slower)
nodetool repair -pr -seq my_keyspace

# Parallel (faster, higher resource usage)
nodetool repair -pr --parallel my_keyspace
```

| Aspect | Sequential (`-seq`) | Parallel (`--parallel`) |
|--------|------------|----------|
| Default (4.0+) | No | Yes |
| Duration | Longer | Shorter |
| Resource usage | Lower | Higher |
| Network impact | Distributed over time | Concentrated |
| Production safety | Higher | Lower |
| Recommended for | Production hours | Off-peak maintenance |

### -dcpar, --dc-parallel

A middle ground between fully sequential and fully parallel repair.

**The problem `-dcpar` solves:**

- `-seq` (sequential): Safe but slow—only one replica builds its Merkle tree at a time across the entire cluster
- `--parallel`: Fast but resource-intensive—all replicas build Merkle trees simultaneously, which can overwhelm nodes if many ranges are repairing at once
- `-dcpar`: Balances both—allows parallelism across datacenters while limiting load within each datacenter

**How it works:**

During Merkle tree validation, each replica must read its data to build the tree. This is I/O and CPU intensive. With `-dcpar`:

1. Within each datacenter, only one replica validates at a time (sequential)
2. Across datacenters, validation happens in parallel

This means if a token range has replicas in DC1 and DC2, both datacenters can validate simultaneously, but each DC only has one replica active at a time.

**Example: 2 DCs, RF=2 per DC (4 replicas total for each range)**

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Comparison: -seq vs -dcpar vs --parallel

participant "DC1: Replica A" as A
participant "DC1: Replica B" as B
participant "DC2: Replica C" as C
participant "DC2: Replica D" as D

== -seq (fully sequential) ==
A -> A : Validate
A -> B : Validate
A -> C : Validate
A -> D : Validate
note right: 4 steps total\nSlowest, lowest impact

== -dcpar (DC parallel) ==
A -> A : Validate
A -> B : Validate
note right of B: DC1 sequential
A -> C : Validate
note right of C: DC2 in parallel with DC1
A -> D : Validate
note right: 2 steps total\nBalanced

== --parallel (fully parallel) ==
A -> A : Validate
A -> B : Validate
A -> C : Validate
A -> D : Validate
note right: 1 step total\nFastest, highest impact
@enduml
```

| Option | Replicas validating simultaneously | Use case |
|--------|-----------------------------------|----------|
| `-seq` | 1 | Minimize impact during peak hours |
| `-dcpar` | 1 per DC | Balance speed and safety in multi-DC clusters |
| `--parallel` | All | Fastest repair during maintenance windows |

**Usage:**
```bash
nodetool repair -pr -dcpar my_keyspace
```

### -j, --jobs (Parallel Table Repair)

Controls how many tables are repaired simultaneously on the node.

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Parallel Jobs (-j) for Table Repair

rectangle "Default: -j 1 (Sequential Tables)" as seq {
    rectangle "Table A" as T1A #LightBlue
    rectangle "Table B" as T1B #LightGreen
    rectangle "Table C" as T1C #LightYellow
    rectangle "Table D" as T1D #LightPink
}
T1A --> T1B : wait
T1B --> T1C : wait
T1C --> T1D : wait

note bottom of seq
  Tables repaired one at a time
  Longer total duration
  Lower resource usage
end note

rectangle "With -j 4 (Parallel Tables)" as par {
    rectangle "Table A" as T4A #LightBlue
    rectangle "Table B" as T4B #LightGreen
    rectangle "Table C" as T4C #LightYellow
    rectangle "Table D" as T4D #LightPink
}

note bottom of par
  4 tables repaired simultaneously
  Shorter total duration
  Higher CPU/memory/network usage
end note
@enduml
```

**Usage:**
```bash
# Repair 2 tables in parallel
nodetool repair -pr -j 2 my_keyspace

# Repair 4 tables in parallel
nodetool repair -pr -j 4 my_keyspace
```

**Guidelines for -j value:**

| Factor | Lower -j (1-2) | Higher -j (4+) |
|--------|----------------|----------------|
| CPU cores | < 8 cores | 16+ cores |
| Memory | < 16 GB heap | 32+ GB heap |
| Disk I/O | HDD or saturated | Fast SSD with headroom |
| Network | Limited bandwidth | High bandwidth |
| Table count | Few large tables | Many small tables |

**Memory impact:**
```
Memory per repair session ≈ repair_session_space_in_mb × number of concurrent tables
With -j 4 and 256 MB per session = ~1 GB additional memory
```

---

## Scope Limiting Options

### -dc, --in-dc (Single Datacenter)

Restricts repair to nodes within a specific datacenter.

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Datacenter-Specific Repair (-dc)

rectangle "dc1 (US-East)" as dc1 {
    rectangle "dc1-node1" as D1N1 #90EE90
    rectangle "dc1-node2" as D1N2 #90EE90
    rectangle "dc1-node3" as D1N3 #90EE90
}

rectangle "dc2 (US-West)" as dc2 {
    rectangle "dc2-node1" as D2N1 #CCCCCC
    rectangle "dc2-node2" as D2N2 #CCCCCC
    rectangle "dc2-node3" as D2N3 #CCCCCC
}

rectangle "dc3 (EU)" as dc3 {
    rectangle "dc3-node1" as D3N1 #CCCCCC
    rectangle "dc3-node2" as D3N2 #CCCCCC
    rectangle "dc3-node3" as D3N3 #CCCCCC
}

note bottom
  nodetool repair -dc dc1 my_keyspace
  Only dc1 nodes participate in repair
  Cross-DC network traffic avoided
end note
@enduml
```

**Usage:**
```bash
# Repair only within dc1
nodetool repair -pr -dc dc1 my_keyspace
```

**Use cases:**
- Minimize cross-datacenter network traffic
- Repair after DC-specific outage
- Staged rollout of repairs

### -local, --in-local-dc

Repairs only with replicas in the same datacenter as the coordinator node.

```bash
# Repair within local DC only (run from node in target DC)
nodetool repair -pr -local my_keyspace
```

### -hosts, --in-hosts

Limits repair to specific hosts, useful for targeted recovery.

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Host-Specific Repair (-hosts)

rectangle "Cluster" as cluster {
    rectangle "node1\n10.0.0.1" as N1 #90EE90
    rectangle "node2\n10.0.0.2" as N2 #90EE90
    rectangle "node3\n10.0.0.3" as N3 #CCCCCC
    rectangle "node4\n10.0.0.4" as N4 #CCCCCC
    rectangle "node5\n10.0.0.5" as N5 #CCCCCC
}

N1 <--> N2 : Repair only\nbetween these hosts

note bottom
  nodetool repair -hosts 10.0.0.1,10.0.0.2 my_keyspace
  Only specified hosts participate
  Useful for targeted recovery
end note
@enduml
```

**Usage:**
```bash
# Repair only between specific nodes
nodetool repair -pr -hosts 10.0.0.1,10.0.0.2,10.0.0.3 my_keyspace
```

---

## Operational Options

### --preview

Estimates repair work without executing, useful for planning.

```bash
nodetool repair -pr --preview my_keyspace
```

**Output example:**
```
Previewing repair for keyspace my_keyspace
  Ranges to repair: 256
  Estimated data to stream: 12.5 GiB
  Mismatched ranges: 12 (4.7%)
  Estimated duration: 45 minutes
```

### --trace

Enables detailed tracing for repair sessions, useful for debugging.

```bash
nodetool repair -pr --trace my_keyspace
```

Trace output appears in `system_traces` keyspace and system logs.

### -os, --optimise-streams (Cassandra 4.0+)

Optimizes streaming by calculating minimal data transfer paths.

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Stream Optimization (-os)

rectangle "Without Optimization" as without {
    rectangle "Node A" as WA
    rectangle "Node B" as WB
    rectangle "Node C" as WC
}
WA --> WB : Stream 100MB
WA --> WC : Stream 100MB
WB --> WC : Stream 80MB

note bottom of without
  Total: 280MB transferred
  Redundant data sent
end note

rectangle "With --optimise-streams" as withopt {
    rectangle "Node A" as OA
    rectangle "Node B" as OB
    rectangle "Node C" as OC
}
OA --> OB : Stream 100MB
OB --> OC : Forward 80MB

note bottom of withopt
  Total: 180MB transferred
  Optimized transfer paths
end note
@enduml
```

**Usage:**
```bash
nodetool repair -pr -os my_keyspace
```

### --force

Proceeds with repair even if some replicas are unavailable. **Use with caution.**

```bash
# Force repair with unavailable replicas
nodetool repair -pr --force my_keyspace
```

**Warning:** This can lead to inconsistent repair state. Only use when:
- A replica is permanently gone and being replaced
- Repair must proceed despite temporary unavailability
- Understanding that full consistency is not guaranteed

### --ignore-unreplicated-keyspaces

Skips keyspaces with replication factor of 1.

```bash
nodetool repair --ignore-unreplicated-keyspaces
```

---

## Option Combinations

### Recommended Combinations

| Scenario | Command | Description |
|----------|---------|-------------|
| Daily maintenance | `nodetool repair -pr my_keyspace` | Incremental, primary range only |
| Weekly full check | `nodetool repair -pr -full my_keyspace` | Full repair, primary range |
| Fast maintenance | `nodetool repair -pr --parallel -j 2 my_keyspace` | Parallel with 2 table threads |
| Conservative repair | `nodetool repair -pr -seq my_keyspace` | Sequential, minimal impact |
| Multi-DC cluster | `nodetool repair -pr -dcpar my_keyspace` | DC-parallel mode |
| Single DC repair | `nodetool repair -pr -dc dc1 my_keyspace` | Limit to specific DC |
| After node recovery | `nodetool repair -full my_keyspace` | Full repair, all ranges |

### Options Compatibility Matrix

| Option | -pr | -full | -seq | --parallel | -j | -dc | --paxos-only | --skip-paxos |
|--------|-----|-------|------|------------|-----|-----|--------------|--------------|
| -pr | - | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ |
| -full | ✓ | - | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ |
| -seq | ✓ | ✓ | - | ✗ | ✓ | ✓ | ✗ | ✓ |
| --parallel | ✓ | ✓ | ✗ | - | ✓ | ✓ | ✗ | ✓ |
| -j | ✓ | ✓ | ✓ | ✓ | - | ✓ | ✗ | ✓ |
| -dc | ✓ | ✓ | ✓ | ✓ | ✓ | - | ✗ | ✓ |
| --paxos-only | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | - | ✗ |
| --skip-paxos | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | - |

---

## Paxos Repair Options

### --paxos-only

Repairs only the Paxos state used by [lightweight transactions (LWTs)](../../cql/dml/lightweight-transactions.md), without repairing user table data.

```bash
# Repair Paxos state for all keyspaces
nodetool repair --paxos-only

# Repair Paxos state for a specific keyspace
nodetool repair --paxos-only my_keyspace
```

**How it works:**

Paxos repairs synchronize the Paxos commit log entries stored in `system.paxos` across replicas. This ensures that all nodes agree on the outcome of previous LWT operations, which is essential for maintaining linearizability guarantees.

**When to use:**

- **Pre-4.1 clusters**: Operators **MUST** schedule `--paxos-only` repairs manually (typically hourly) since automatic Paxos repairs are not available
- **Before topology changes**: Run on all nodes before bootstrap, decommission, replace, or move operations to reduce the risk of Paxos cleanup timeouts
- **After disabling automatic Paxos repairs**: If `paxos_repair_enabled` is set to `false`, manual Paxos repairs **MUST** be scheduled regularly for clusters using LWTs
- **Troubleshooting LWT issues**: When LWTs are timing out or behaving unexpectedly

**Automatic Paxos repairs (Cassandra 4.1+):**

In Cassandra 4.1 and later, Paxos repairs run automatically every 5 minutes by default when `paxos_repair_enabled` is `true`. Manual `--paxos-only` repairs are typically only needed for:

- Pre-4.1 clusters
- Clusters where automatic Paxos repairs have been disabled
- Proactive cleanup before topology changes

**Operational guidance:**

- Running without a keyspace argument repairs Paxos state for **all keyspaces**. This is often **RECOMMENDED** because operators frequently do not know which keyspaces developers are using for LWTs.
- Paxos repairs are lightweight compared to full data repairs and complete quickly

For more details on Paxos repair strategy and configuration, see [Paxos Repairs](strategies.md#paxos-repairs) in the Repair Strategies guide.

### --skip-paxos

Skips the Paxos repair step during regular repairs, allowing data repair to proceed without checking Paxos state consistency.

```bash
# Skip Paxos repair, repair table data only
nodetool repair --skip-paxos my_keyspace
```

**How it relates to `--paxos-only`:**

| Option | Table Data | Paxos State |
|--------|------------|-------------|
| (no flag) | ✓ Repaired | ✓ Repaired |
| `--paxos-only` | ✗ Skipped | ✓ Repaired |
| `--skip-paxos` | ✓ Repaired | ✗ Skipped |

**When to use:**

- **Emergency topology changes**: When Paxos cleanup is failing (timing out, `CANCELLED`) during bootstrap/decommission, you **MAY** skip Paxos repair temporarily to allow the topology change to proceed
- **Pre-4.1 clusters with manual Paxos repair**: If running separate `--paxos-only` repairs on a schedule, you **MAY** skip Paxos during regular data repairs to avoid redundant work
- **Troubleshooting**: To isolate whether issues are data-related or Paxos-related

**Important caveat:**

If you use `--skip-paxos`, Paxos state **MUST** be reconciled separately via `--paxos-only` repairs. Skipping Paxos repair without a replacement schedule **WILL** lead to LWT inconsistencies.

```bash
# Data repair only, skip Paxos (use when Paxos repairs are failing)
nodetool repair --skip-paxos my_keyspace

# Then run Paxos repairs separately once cluster is healthy
nodetool repair --paxos-only my_keyspace
```

## Next Steps

- **[Repair Concepts](concepts.md)** - Understanding how repair works
- **[Repair Strategies](strategies.md)** - Real-world implementation scenarios
- **[Scheduling Guide](scheduling.md)** - Planning repair schedules
