---
title: "Kafka Topics and Partitions"
description: "Apache Kafka topic architecture. Partitions, partition leaders, ISR, leader election, high watermark, and replication internals."
meta:
  - name: keywords
    content: "Kafka topics, Kafka partitions, partition leader, ISR, leader election, high watermark, Kafka replication"
---

# Topics and Partitions

Topics and partitions form the foundation of Kafka's distributed architecture. A topic is a logical channel for records; partitions provide horizontal scalability and fault tolerance through distributed, replicated logs.

---

## Topic Architecture

A topic is a named, append-only log that organizes related records. Unlike traditional message queues where messages are deleted after consumption, Kafka topics retain records based on configurable retention policies.

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Topic: orders" {
    rectangle "Partition 0" as p0 {
        card "0" as p0_0
        card "1" as p0_1
        card "2" as p0_2
        card "3" as p0_3
        p0_0 -right-> p0_1
        p0_1 -right-> p0_2
        p0_2 -right-> p0_3
    }

    rectangle "Partition 1" as p1 {
        card "0" as p1_0
        card "1" as p1_1
        card "2" as p1_2
        p1_0 -right-> p1_1
        p1_1 -right-> p1_2
    }

    rectangle "Partition 2" as p2 {
        card "0" as p2_0
        card "1" as p2_1
        card "2" as p2_2
        card "3" as p2_3
        card "4" as p2_4
        p2_0 -right-> p2_1
        p2_1 -right-> p2_2
        p2_2 -right-> p2_3
        p2_3 -right-> p2_4
    }
}

note bottom
  Each partition is an independent ordered log
  Offsets are partition-local (start at 0)
  No ordering guarantees across partitions
end note

@enduml
```

### Topic Properties

| Property | Description |
|----------|-------------|
| **Name** | Unique identifier within the cluster; immutable after creation |
| **Partition count** | Number of partitions; can be increased but not decreased |
| **Replication factor** | Number of replicas per partition; set at creation |
| **Retention** | How long records are kept (time or size based) |
| **Cleanup policy** | Delete old segments or compact by key |

### Topic Naming Constraints

| Constraint | Rule |
|------------|------|
| Length | 1-249 characters |
| Characters | `[a-zA-Z0-9._-]` only |
| Reserved | Names starting with `__` are internal topics |
| Collision | `.` and `_` are interchangeable in metrics; avoid mixing |

!!! warning "Internal Topics"
    Topics prefixed with `__` are managed by Kafka internally and must not be modified directly:

    - `__consumer_offsets` - Consumer group offset storage
    - `__transaction_state` - Transaction coordinator state
    - `__cluster_metadata` - KRaft metadata (KRaft mode only)

---

## Partitions

Partitions are the unit of parallelism and distribution in Kafka. Each partition is an ordered, immutable sequence of records stored on a single broker (with replicas on other brokers).

### Why Partitions Exist

| Problem | How Partitions Solve It |
|---------|-------------------------|
| Single broker throughput limit | Distribute writes across multiple brokers |
| Single consumer throughput limit | Enable parallel consumption within consumer groups |
| Storage capacity limit | Spread data across cluster storage |
| Single point of failure | Replicas on different brokers provide redundancy |

### Partition Structure

Each partition is stored as a directory containing log segments:

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Partition Directory: orders-0/" {
    rectangle "Segment 0 (closed)" as seg0 {
        file "00000000000000000000.log" as log0
        file "00000000000000000000.index" as idx0
        file "00000000000000000000.timeindex" as tidx0
    }

    rectangle "Segment 1 (closed)" as seg1 {
        file "00000000000000050000.log" as log1
        file "00000000000000050000.index" as idx1
        file "00000000000000050000.timeindex" as tidx1
    }

    rectangle "Segment 2 (active)" as seg2 #lightgreen {
        file "00000000000000100000.log" as log2
        file "00000000000000100000.index" as idx2
        file "00000000000000100000.timeindex" as tidx2
    }
}

note right of seg2
  Active segment receives
  new writes (append-only)

  Filename = base offset
end note

@enduml
```

### Partition Files

| File Extension | Purpose |
|----------------|---------|
| `.log` | Record data (keys, values, headers, timestamps) |
| `.index` | Sparse offset-to-file-position index |
| `.timeindex` | Sparse timestamp-to-offset index |
| `.txnindex` | Transaction abort index |
| `.snapshot` | Producer state snapshot for idempotence |
| `leader-epoch-checkpoint` | Leader epoch history |

### Offset Semantics

Offsets are 64-bit integers assigned sequentially within each partition:

| Concept | Description |
|---------|-------------|
| **Base offset** | First offset in a segment (used in filename) |
| **Log End Offset (LEO)** | Next offset to be assigned (last offset + 1) |
| **High Watermark (HW)** | Last offset replicated to all ISR; consumers read up to HW |
| **Last Stable Offset (LSO)** | HW excluding uncommitted transactions |

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Partition Log" {
    card "0" as o0
    card "1" as o1
    card "2" as o2
    card "3" as o3
    card "4" as o4
    card "5" as o5
    card "6" as o6
    card "7" as o7

    o0 -right-> o1
    o1 -right-> o2
    o2 -right-> o3
    o3 -right-> o4
    o4 -right-> o5
    o5 -right-> o6
    o6 -right-> o7
}

note bottom of o4
  High Watermark (HW) = 5
  Consumers can read 0-4
end note

note bottom of o7
  Log End Offset (LEO) = 8
  Leader has written 0-7
end note

@enduml
```

---

## Partition Leaders and Replicas

Each partition has one leader and zero or more follower replicas. The leader handles all read and write requests; followers replicate data from the leader.

### Leader Responsibilities

| Responsibility | Description |
|----------------|-------------|
| **Handle produces** | Accept and persist records from producers |
| **Handle fetches** | Serve records to consumers and followers |
| **Maintain ISR** | Track which followers are in-sync |
| **Advance HW** | Update high watermark as followers catch up |

### Follower Responsibilities

| Responsibility | Description |
|----------------|-------------|
| **Fetch from leader** | Continuously replicate new records |
| **Maintain LEO** | Track local log end offset |
| **Report position** | Include LEO in fetch requests for HW calculation |

### Replica States

```plantuml
@startuml

skinparam backgroundColor transparent

state "Online" as Online {
    state "Leader" as Leader
    state "Follower" as Follower
}

state "Offline" as Offline

[*] --> Follower : broker starts
Leader -right-> Follower : another replica\nbecomes leader
Follower -left-> Leader : elected leader
Follower --> Offline : broker fails
Leader --> Offline : broker fails
Offline --> Follower : broker recovers

@enduml
```

---

## In-Sync Replicas (ISR)

The ISR is the set of replicas that are fully caught up with the leader. Only ISR members are eligible to become leader if the current leader fails.

### ISR Membership Criteria

A replica remains in the ISR if it meets **both** conditions:

| Condition | Configuration | Default |
|-----------|---------------|---------|
| Caught up to leader's LEO | `replica.lag.time.max.ms` | 30000 (30s) |
| Heartbeat received | `replica.socket.timeout.ms` | 30000 (30s) |

!!! note "Lag Time vs Lag Messages"
    Prior to Kafka 0.9, ISR membership was based on message lag (`replica.lag.max.messages`). This was removed because burst writes would cause unnecessary ISR shrinkage. The current time-based approach is more stable.

### ISR Dynamics

```plantuml
@startuml

skinparam backgroundColor transparent

participant "Leader" as L
participant "Follower A" as FA
participant "Follower B" as FB

note over L, FB: ISR = {Leader, A, B}

L -> L : receive produce (offset 100)
L -> FA : replicate
L -> FB : replicate

FA -> L : fetch (caught up to 100)
note right: A remains in ISR

FB -> FB : slow disk I/O
note over FB: Falls behind

... 30 seconds pass ...

L -> L : check replica lag
note over L: B exceeded replica.lag.time.max.ms

L -> L : shrink ISR
note over L, FB: ISR = {Leader, A}

... B catches up ...

FB -> L : fetch (caught up to 100)
L -> L : expand ISR
note over L, FB: ISR = {Leader, A, B}

@enduml
```

### ISR Configuration

| Configuration | Default | Description |
|---------------|---------|-------------|
| `replica.lag.time.max.ms` | 30000 | Max time follower can lag before removal from ISR |
| `min.insync.replicas` | 1 | Minimum ISR size for `acks=all` produces |
| `unclean.leader.election.enable` | false | Allow non-ISR replicas to become leader |

### Min In-Sync Replicas

The `min.insync.replicas` setting determines the minimum number of replicas (including leader) that must acknowledge a write for `acks=all`:

| RF | min.insync.replicas | Behavior |
|:--:|:-------------------:|----------|
| 3 | 1 | Write succeeds if leader alone persists (weak durability) |
| 3 | 2 | Write requires leader + 1 follower (recommended) |
| 3 | 3 | Write requires all replicas (highest durability, lower availability) |

!!! warning "ISR Shrinkage Impact"
    If ISR size falls below `min.insync.replicas`, producers with `acks=all` receive `NotEnoughReplicasException`. The partition becomes read-only until ISR recovers.

---

## Leader Election

When a partition leader fails, Kafka elects a new leader from the ISR. The controller (or KRaft quorum) coordinates this process.

### Election Process

```plantuml
@startuml

skinparam backgroundColor transparent

participant "Controller" as C
participant "Broker 1\n(old leader)" as B1
participant "Broker 2\n(ISR)" as B2
participant "Broker 3\n(ISR)" as B3

note over B1: Broker 1 fails

C -> C : detect failure\n(ZK session / heartbeat timeout)

C -> C : select new leader from ISR\n(prefer in-sync, same rack)

C -> B2 : LeaderAndIsr(leader=B2, epoch=2)
C -> B3 : LeaderAndIsr(leader=B2, epoch=2)

B2 -> B2 : become leader
B3 -> B3 : follow B2

C -> C : update metadata

note over B2, B3
  New leader: Broker 2
  ISR: {B2, B3}
  Leader epoch: 2
end note

@enduml
```

### Leader Epoch

The leader epoch is a monotonically increasing number that identifies the leader's term. It prevents stale leaders from causing inconsistencies:

| Scenario | How Epoch Helps |
|----------|-----------------|
| Network partition | Old leader's writes rejected (stale epoch) |
| Split brain | Only current epoch accepted by followers |
| Log truncation | Followers truncate to epoch boundary on recovery |

### Preferred Leader Election

Kafka can automatically rebalance leadership to the "preferred" replica (first in the replica list):

| Configuration | Default | Description |
|---------------|---------|-------------|
| `auto.leader.rebalance.enable` | true | Automatically elect preferred leaders |
| `leader.imbalance.check.interval.seconds` | 300 | How often to check for imbalance |
| `leader.imbalance.per.broker.percentage` | 10 | Imbalance threshold to trigger rebalance |

### Unclean Leader Election

When all ISR members are unavailable, Kafka must choose between availability and consistency:

| `unclean.leader.election.enable` | Behavior |
|:--------------------------------:|----------|
| `false` (default) | Partition remains offline until ISR member recovers |
| `true` | Out-of-sync replica can become leader (potential data loss) |

!!! danger "Data Loss Risk"
    Enabling unclean leader election can cause data loss. Records written to the old leader but not replicated will be lost when an out-of-sync replica becomes leader.

---

## High Watermark and Log Consistency

The high watermark (HW) is the offset up to which all ISR replicas have replicated. Consumers can only read records up to the HW.

### HW Advancement

```plantuml
@startuml

skinparam backgroundColor transparent

participant "Producer" as P
participant "Leader\n(LEO=100)" as L
participant "Follower A\n(LEO=98)" as FA
participant "Follower B\n(LEO=99)" as FB

note over L: HW = min(LEO of all ISR) = 98

P -> L : produce record
L -> L : append (LEO=101)

FA -> L : fetch(offset=98)
L -> FA : records 98-100
FA -> FA : append (LEO=101)

FB -> L : fetch(offset=99)
L -> FB : records 99-100
FB -> FB : append (LEO=101)

note over L: All ISR at LEO=101
L -> L : advance HW to 101

L -> FA : HW=101 (in fetch response)
L -> FB : HW=101 (in fetch response)

@enduml
```

### Consumer Visibility

| Offset Range | Consumer Visibility |
|--------------|---------------------|
| `0` to `HW-1` | Visible to consumers |
| `HW` to `LEO-1` | Not visible (not yet replicated to all ISR) |

!!! note "Read-Your-Writes"
    A producer may not immediately read its own writes if consuming from the same topic. The record becomes visible only after HW advances (all ISR have replicated).

---

## Partition Assignment

When topics are created or partitions are added, the controller assigns partitions to brokers.

### Assignment Goals

| Goal | Strategy |
|------|----------|
| **Balance** | Distribute partitions evenly across brokers |
| **Rack awareness** | Place replicas in different racks |
| **Minimize movement** | Prefer keeping existing assignments |

### Rack-Aware Assignment

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Rack A" as rackA {
    rectangle "Broker 1" as b1 {
        card "P0 Leader" as p0_l
        card "P1 Follower" as p1_f1
    }
    rectangle "Broker 2" as b2 {
        card "P2 Follower" as p2_f1
    }
}

rectangle "Rack B" as rackB {
    rectangle "Broker 3" as b3 {
        card "P0 Follower" as p0_f1
        card "P1 Leader" as p1_l
    }
    rectangle "Broker 4" as b4 {
        card "P2 Leader" as p2_l
    }
}

rectangle "Rack C" as rackC {
    rectangle "Broker 5" as b5 {
        card "P0 Follower" as p0_f2
        card "P2 Follower" as p2_f2
    }
    rectangle "Broker 6" as b6 {
        card "P1 Follower" as p1_f2
    }
}

note bottom
  RF=3: Each partition has replicas
  in 3 different racks

  Survives complete rack failure
end note

@enduml
```

### Configuration

| Configuration | Default | Description |
|---------------|---------|-------------|
| `broker.rack` | null | Rack identifier for this broker |
| `default.replication.factor` | 1 | Default RF for auto-created topics |
| `num.partitions` | 1 | Default partition count for auto-created topics |

---

## Partition Count Selection

Choosing the right partition count involves trade-offs:

### Factors to Consider

| Factor | More Partitions | Fewer Partitions |
|--------|-----------------|------------------|
| **Consumer parallelism** | Higher (1 consumer per partition max) | Lower |
| **Throughput** | Higher (parallel I/O) | Lower |
| **Ordering scope** | Narrower (per-partition only) | Broader |
| **Broker memory** | Higher (~1-2 MB per partition) | Lower |
| **Leader election time** | Longer | Shorter |
| **End-to-end latency** | Can be higher (batching) | Can be lower |
| **Rebalance time** | Longer | Shorter |

### Guidelines

| Workload | Partition Count Guidance |
|----------|--------------------------|
| Low throughput (<10 MB/s) | 3-6 partitions |
| Medium throughput (10-100 MB/s) | 6-30 partitions |
| High throughput (100+ MB/s) | 30-100+ partitions |
| Ordering required across keys | 1 partition (limits throughput) |

!!! warning "Partition Count Cannot Be Decreased"
    Once a topic is created, the partition count can only be increased, not decreased. Increasing partitions also breaks key-based ordering guarantees for existing keys.

---

## Topic and Partition Metadata

Kafka maintains metadata about topics and partitions in the controller. Clients fetch this metadata to discover partition leaders.

### Metadata Contents

| Metadata | Description |
|----------|-------------|
| Topic list | All topics in cluster |
| Partition count | Number of partitions per topic |
| Replica assignment | Which brokers host each partition |
| Leader | Current leader for each partition |
| ISR | In-sync replicas for each partition |
| Controller | Current controller broker |

### Metadata Refresh

| Trigger | Description |
|---------|-------------|
| `metadata.max.age.ms` | Periodic refresh (default: 5 minutes) |
| `NOT_LEADER_OR_FOLLOWER` error | Immediate refresh |
| `UNKNOWN_TOPIC_OR_PARTITION` error | Immediate refresh |
| New producer/consumer | Initial fetch |

---

## Version Compatibility

| Feature | Minimum Version |
|---------|-----------------|
| Rack-aware assignment | 0.10.0 |
| Leader epoch | 0.11.0 |
| Follower fetching (KIP-392) | 2.4.0 |
| Tiered storage | 3.6.0 (early access) |
| KRaft mode | 3.3.0 (production) |

---

## Configuration Reference

### Topic Configuration

| Configuration | Default | Description |
|---------------|---------|-------------|
| `retention.ms` | 604800000 (7d) | Time-based retention |
| `retention.bytes` | -1 (unlimited) | Size-based retention per partition |
| `segment.bytes` | 1073741824 (1GB) | Log segment size |
| `segment.ms` | 604800000 (7d) | Time before rolling segment |
| `cleanup.policy` | delete | `delete`, `compact`, or both |
| `min.insync.replicas` | 1 | Minimum ISR for acks=all |
| `unclean.leader.election.enable` | false | Allow non-ISR leader election |

### Broker Configuration

| Configuration | Default | Description |
|---------------|---------|-------------|
| `num.partitions` | 1 | Default partitions for new topics |
| `default.replication.factor` | 1 | Default RF for new topics |
| `replica.lag.time.max.ms` | 30000 | Max lag before ISR removal |
| `replica.fetch.max.bytes` | 1048576 | Max bytes per replica fetch |
| `broker.rack` | null | Rack identifier |

---

## Related Documentation

- [Storage Engine](../storage-engine/index.md) - Log segments and compaction
- [Replication](../replication/index.md) - Replication protocol details
- [Fault Tolerance](../fault-tolerance/index.md) - Failure scenarios
- [Topics Concepts](../../concepts/topics/index.md) - Conceptual overview
- [Transaction Coordinator](../transactions/index.md) - Transactional writes
