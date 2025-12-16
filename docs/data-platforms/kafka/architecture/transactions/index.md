---
title: "Kafka Transaction Coordinator"
description: "Apache Kafka transaction coordinator architecture. Transaction manager, producer IDs, epochs, two-phase commit, and exactly-once semantics internals."
meta:
  - name: keywords
    content: "Kafka transactions, transaction coordinator, producer ID, epoch, exactly-once, two-phase commit, transactional.id"
---

# Transaction Coordinator

The transaction coordinator enables atomic writes across multiple partitions and exactly-once semantics in Kafka. It manages producer identities, transaction state, and coordinates the two-phase commit protocol.

---

## Transaction Architecture Overview

Kafka transactions provide atomicity—a set of writes either all succeed or all fail. The transaction coordinator is a broker-side component that manages transaction state and coordinates commits.

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Transactional Producer" as producer {
    card "transactional.id" as txn_id
    card "Producer ID (PID)" as pid
    card "Epoch" as epoch
}

rectangle "Kafka Cluster" {
    rectangle "Transaction\nCoordinator" as tc {
        database "__transaction_state" as txn_log
    }

    rectangle "Partition Leaders" as leaders {
        rectangle "topic-A-0" as p1
        rectangle "topic-A-1" as p2
        rectangle "topic-B-0" as p3
    }

    rectangle "Group\nCoordinator" as gc {
        database "__consumer_offsets" as offset_log
    }
}

producer --> tc : InitProducerId\nAddPartitionsToTxn\nEndTxn
producer --> leaders : Produce (transactional)
producer --> gc : TxnOffsetCommit

tc --> txn_log : persist state
tc --> leaders : WriteTxnMarkers
tc --> gc : WriteTxnMarkers

@enduml
```

### Key Components

| Component | Responsibility |
|-----------|----------------|
| **Transaction Coordinator** | Manages transaction state and coordinates commit/abort |
| **`__transaction_state`** | Internal topic storing transaction metadata |
| **Producer ID (PID)** | Unique identifier for producer instance |
| **Epoch** | Fencing mechanism to prevent zombie producers |
| **Transaction Markers** | Control records marking transaction boundaries |

---

## Producer Identity

### Producer ID (PID)

Every producer is assigned a unique 64-bit Producer ID. For idempotent producers, this enables deduplication. For transactional producers, it identifies the transaction owner.

```plantuml
@startuml

skinparam backgroundColor transparent

participant "Producer" as P
participant "Transaction\nCoordinator" as TC

== Non-Transactional (Idempotent) ==
P -> TC : InitProducerId(transactional_id=null)
TC -> TC : generate new PID
TC --> P : PID=1000, epoch=0

note right: PID generated each time\nNo persistence

== Transactional ==
P -> TC : InitProducerId(transactional_id="order-service-1")
TC -> TC : lookup or create PID\nfor transactional.id
TC --> P : PID=2000, epoch=0

note right: PID persisted in\n__transaction_state

@enduml
```

### Epoch and Fencing

The epoch is a 16-bit counter that increments each time a producer with the same `transactional.id` initializes. This enables "zombie fencing"—preventing old producers from causing inconsistencies.

```plantuml
@startuml

skinparam backgroundColor transparent

participant "Producer A\n(epoch=0)" as PA
participant "Transaction\nCoordinator" as TC
participant "Producer A'\n(epoch=1)" as PA2
participant "Partition\nLeader" as PL

note over PA: Original producer

PA -> TC : InitProducerId("order-svc")
TC --> PA : PID=100, epoch=0

PA -> PL : Produce(PID=100, epoch=0)
PL --> PA : ack

note over PA: Crash / Network partition

PA2 -> TC : InitProducerId("order-svc")
TC -> TC : increment epoch
TC --> PA2 : PID=100, epoch=1

note over PA2: New producer instance\nwith same transactional.id

PA -> PL : Produce(PID=100, epoch=0)
PL --> PA : ProducerFencedException

note over PA: Old producer is fenced\nmust shut down

@enduml
```

### Fencing Scenarios

| Scenario | Behavior |
|----------|----------|
| Producer restart | New epoch assigned; old instance fenced |
| Network partition | First to re-initialize gets new epoch |
| Horizontal scaling | Each instance needs unique `transactional.id` |
| Zombie producer | Rejected with `ProducerFencedException` |

---

## Transaction Coordinator

### Coordinator Assignment

Each `transactional.id` maps to a specific coordinator via hashing:

```
coordinator = hash(transactional.id) % num_partitions(__transaction_state)
```

The broker hosting that partition of `__transaction_state` is the coordinator.

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "__transaction_state topic (50 partitions)" as txn_topic {
    rectangle "Partition 0\n(Broker 1)" as p0
    rectangle "Partition 1\n(Broker 2)" as p1
    rectangle "Partition 2\n(Broker 3)" as p2
    rectangle "..." as pn
    rectangle "Partition 49\n(Broker 1)" as p49
}

card "transactional.id = 'order-svc-1'" as tid1
card "transactional.id = 'payment-svc-1'" as tid2

tid1 --> p1 : hash % 50 = 1
tid2 --> p2 : hash % 50 = 2

note bottom
  Coordinator is the leader of the
  assigned __transaction_state partition
end note

@enduml
```

### Transaction State Storage

The `__transaction_state` topic stores:

| Field | Description |
|-------|-------------|
| `transactional.id` | Producer's transaction identifier |
| `producer_id` | Assigned PID |
| `producer_epoch` | Current epoch |
| `transaction_state` | Current state (Empty, Ongoing, etc.) |
| `topic_partitions` | Partitions participating in transaction |
| `transaction_timeout_ms` | Timeout for this transaction |
| `transaction_start_time` | When transaction began |

### Coordinator Configuration

| Configuration | Default | Description |
|---------------|---------|-------------|
| `transaction.state.log.replication.factor` | 3 | Replication factor for `__transaction_state` |
| `transaction.state.log.num.partitions` | 50 | Partitions in `__transaction_state` |
| `transaction.state.log.min.isr` | 2 | Minimum ISR for transaction log |
| `transaction.state.log.segment.bytes` | 104857600 | Segment size |

---

## Transaction Lifecycle

### State Machine

```plantuml
@startuml

skinparam backgroundColor transparent

state "Empty" as Empty : No active transaction
state "Ongoing" as Ongoing : Transaction in progress
state "PrepareCommit" as PrepareCommit : Commit initiated
state "PrepareAbort" as PrepareAbort : Abort initiated
state "CompleteCommit" as CompleteCommit : Commit markers written
state "CompleteAbort" as CompleteAbort : Abort markers written
state "Dead" as Dead : transactional.id expired

[*] --> Empty : InitProducerId

Empty --> Ongoing : AddPartitionsToTxn
Ongoing --> Ongoing : AddPartitionsToTxn\nProduce\nAddOffsetsToTxn

Ongoing --> PrepareCommit : EndTxn(COMMIT)
Ongoing --> PrepareAbort : EndTxn(ABORT)
Ongoing --> PrepareAbort : timeout

PrepareCommit --> CompleteCommit : markers written
PrepareAbort --> CompleteAbort : markers written

CompleteCommit --> Empty : cleanup
CompleteAbort --> Empty : cleanup

Empty --> Dead : transactional.id.expiration.ms

@enduml
```

### State Descriptions

| State | Description |
|-------|-------------|
| **Empty** | Producer initialized; no active transaction |
| **Ongoing** | Transaction active; partitions being written |
| **PrepareCommit** | Commit requested; writing markers |
| **PrepareAbort** | Abort requested; writing markers |
| **CompleteCommit** | All commit markers written |
| **CompleteAbort** | All abort markers written |
| **Dead** | `transactional.id` expired due to inactivity |

---

## Two-Phase Commit Protocol

Kafka transactions use a variant of two-phase commit to ensure atomicity across partitions.

### Phase 1: Prepare

```plantuml
@startuml

skinparam backgroundColor transparent

participant "Producer" as P
participant "Transaction\nCoordinator" as TC
participant "topic-A Leader" as LA
participant "topic-B Leader" as LB

P -> TC : beginTransaction()
note right: Local only

P -> TC : AddPartitionsToTxn([topic-A-0])
TC -> TC : record partition
TC --> P : OK

P -> LA : Produce(txn records)
LA --> P : ack

P -> TC : AddPartitionsToTxn([topic-B-0])
TC -> TC : record partition
TC --> P : OK

P -> LB : Produce(txn records)
LB --> P : ack

note over TC
  Transaction state: Ongoing
  Partitions: [topic-A-0, topic-B-0]
end note

@enduml
```

### Phase 2: Commit

```plantuml
@startuml

skinparam backgroundColor transparent

participant "Producer" as P
participant "Transaction\nCoordinator" as TC
participant "topic-A Leader" as LA
participant "topic-B Leader" as LB

P -> TC : EndTxn(COMMIT)

TC -> TC : state = PrepareCommit
TC -> TC : persist to __transaction_state

TC -> LA : WriteTxnMarkers(COMMIT, PID, epoch)
LA -> LA : write COMMIT marker
LA --> TC : ack

TC -> LB : WriteTxnMarkers(COMMIT, PID, epoch)
LB -> LB : write COMMIT marker
LB --> TC : ack

TC -> TC : state = CompleteCommit
TC --> P : COMMIT success

note over LA, LB
  Transaction markers written
  Records now visible to consumers
  with isolation.level=read_committed
end note

@enduml
```

### Transaction Markers

Transaction markers are special control records written to each partition:

| Marker Type | Meaning |
|-------------|---------|
| `COMMIT` | Transaction committed; records are valid |
| `ABORT` | Transaction aborted; records should be ignored |

Markers contain:
- Producer ID
- Producer epoch
- Coordinator epoch
- Control type (COMMIT/ABORT)

---

## Consumer Integration

### Transactional Consumer Offsets

When using read-process-write patterns, consumer offsets can be committed as part of the transaction:

```plantuml
@startuml

skinparam backgroundColor transparent

participant "Producer/Consumer" as PC
participant "Transaction\nCoordinator" as TC
participant "Group\nCoordinator" as GC
participant "Output Topic" as OT

PC -> TC : beginTransaction()
PC -> PC : poll() from input topic

PC -> TC : AddPartitionsToTxn([output-0])
PC -> OT : Produce(processed records)

PC -> TC : AddOffsetsToTxn(group.id)
TC -> TC : record group coordinator
TC --> PC : OK

PC -> GC : TxnOffsetCommit(offsets)
GC -> GC : write pending offsets
GC --> PC : OK

PC -> TC : EndTxn(COMMIT)
TC -> OT : WriteTxnMarkers(COMMIT)
TC -> GC : WriteTxnMarkers(COMMIT)

note over GC
  Offsets now committed
  Consumer won't re-read
  these records
end note

@enduml
```

### Isolation Levels

| `isolation.level` | Behavior |
|-------------------|----------|
| `read_uncommitted` | Read all records including aborted transactions |
| `read_committed` | Read only committed records; aborted filtered |

### Last Stable Offset (LSO)

The LSO is the offset below which all transactions are complete:

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Partition Log" {
    card "0\ncommitted" as o0 #lightgreen
    card "1\ncommitted" as o1 #lightgreen
    card "2\ntxn-A" as o2 #lightyellow
    card "3\ncommitted" as o3 #lightgreen
    card "4\ntxn-A" as o4 #lightyellow
    card "5\ncommitted" as o5 #lightgreen

    o0 -right-> o1
    o1 -right-> o2
    o2 -right-> o3
    o3 -right-> o4
    o4 -right-> o5
}

note bottom
  LSO = 2 (txn-A still ongoing)

  read_committed consumers see: 0, 1
  read_uncommitted consumers see: 0, 1, 2, 3, 4, 5

  After txn-A commits: LSO = 6
  read_committed now sees all records
end note

@enduml
```

---

## Failure Handling

### Producer Failure During Transaction

| Scenario | Coordinator Action |
|----------|-------------------|
| Producer crashes before EndTxn | Transaction times out; coordinator aborts |
| Producer crashes during EndTxn | New producer instance completes or aborts |
| Network partition | Transaction times out if no progress |

### Coordinator Failure

```plantuml
@startuml

skinparam backgroundColor transparent

participant "Producer" as P
participant "Old Coordinator\n(Broker 1)" as OC
participant "New Coordinator\n(Broker 2)" as NC

P -> OC : EndTxn(COMMIT)
note over OC: Broker 1 fails

... leader election for __transaction_state ...

NC -> NC : become coordinator
NC -> NC : load transaction state\nfrom __transaction_state

alt Transaction in PrepareCommit
    NC -> NC : complete commit\n(write markers)
else Transaction in Ongoing
    NC -> NC : wait for producer\nor timeout
end

P -> NC : retry EndTxn(COMMIT)
NC --> P : OK (already committed)\nor complete commit

@enduml
```

### Transaction Timeout

If a transaction exceeds `transaction.timeout.ms`, the coordinator aborts it:

| Configuration | Default | Description |
|---------------|---------|-------------|
| `transaction.timeout.ms` | 60000 (1 min) | Max transaction duration |
| `transactional.id.expiration.ms` | 604800000 (7 days) | Expiration for inactive transactional.id |

---

## Idempotent vs Transactional Producers

| Feature | Idempotent | Transactional |
|---------|------------|---------------|
| **Deduplication** | Within single session | Across sessions |
| **Scope** | Single partition | Multiple partitions |
| **Atomicity** | Per-record | Multi-record |
| **Configuration** | `enable.idempotence=true` | `transactional.id` required |
| **Overhead** | Low | Higher (coordinator RPCs) |

### When to Use Each

| Use Case | Recommendation |
|----------|----------------|
| Prevent duplicate writes | Idempotent producer |
| Atomic multi-partition writes | Transactional producer |
| Read-process-write exactly-once | Transactional producer |
| High-throughput, no atomicity needed | Idempotent producer |

---

## Performance Considerations

### Transaction Overhead

| Operation | Overhead |
|-----------|----------|
| InitProducerId | One-time per producer start |
| AddPartitionsToTxn | Per new partition in transaction |
| EndTxn | Two-phase commit across partitions |
| Transaction markers | Additional records in each partition |

### Batching Transactions

Larger transactions amortize overhead:

| Pattern | Transactions/sec | Throughput |
|---------|------------------|------------|
| 1 record per transaction | Low | Low |
| 100 records per transaction | Medium | Medium |
| 1000+ records per transaction | High | High |

### Configuration Tuning

| Configuration | Default | Tuning Guidance |
|---------------|---------|-----------------|
| `transaction.timeout.ms` | 60000 | Increase for long-running transactions |
| `max.block.ms` | 60000 | Time to wait for transaction coordinator |
| `delivery.timeout.ms` | 120000 | Must exceed `transaction.timeout.ms` |

---

## Exactly-Once Semantics (EOS)

Kafka's EOS combines idempotent producers, transactions, and transactional consumers:

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Exactly-Once Components" {
    rectangle "Idempotent Producer" as idem {
        card "PID + sequence numbers"
        card "Deduplication per partition"
    }

    rectangle "Transactions" as txn {
        card "Atomic multi-partition writes"
        card "Consumer offset + output atomic"
    }

    rectangle "Transactional Consumer" as cons {
        card "read_committed isolation"
        card "Filter aborted records"
    }
}

idem --> txn : enables
txn --> cons : completes

note bottom
  Together: exactly-once processing
  Record processed exactly once
  from input to output
end note

@enduml
```

### EOS in Kafka Streams

Kafka Streams uses transactions internally for exactly-once:

| `processing.guarantee` | Behavior |
|------------------------|----------|
| `at_least_once` | No transactions; duplicates possible on failure |
| `exactly_once_v2` | Transactions per task; atomic state + output |

---

## Version Compatibility

| Feature | Minimum Version |
|---------|-----------------|
| Idempotent producer | 0.11.0 |
| Transactions | 0.11.0 |
| `exactly_once_v2` (Streams) | 2.5.0 |
| Transaction protocol improvements | 2.5.0 |

---

## Configuration Reference

### Producer Configuration

| Configuration | Default | Description |
|---------------|---------|-------------|
| `enable.idempotence` | true (2.8+) | Enable idempotent producer |
| `transactional.id` | null | Transaction identifier (enables transactions) |
| `transaction.timeout.ms` | 60000 | Transaction timeout |
| `max.in.flight.requests.per.connection` | 5 | Must be ≤5 for idempotence |

### Broker Configuration

| Configuration | Default | Description |
|---------------|---------|-------------|
| `transaction.state.log.replication.factor` | 3 | `__transaction_state` replication |
| `transaction.state.log.num.partitions` | 50 | `__transaction_state` partitions |
| `transaction.state.log.min.isr` | 2 | Minimum ISR |
| `transactional.id.expiration.ms` | 604800000 | Expiration for inactive IDs |

### Consumer Configuration

| Configuration | Default | Description |
|---------------|---------|-------------|
| `isolation.level` | read_uncommitted | `read_committed` for transactional |
| `enable.auto.commit` | true | Set to `false` for transactional |

---

## Related Documentation

- [Topics and Partitions](../topics/index.md) - Partition architecture
- [Transaction Protocol APIs](../client-connections/protocol-apis-transaction.md) - Wire protocol
- [Exactly-Once Semantics](../../concepts/delivery-semantics/exactly-once.md) - EOS patterns
- [Kafka Streams EOS](../../application-development/kafka-streams/index.md) - Streams transactions
