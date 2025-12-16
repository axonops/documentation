---
title: "Exactly-Once Semantics"
description: "Kafka exactly-once semantics (EOS). Idempotent producers, transactions, read-process-write patterns, and Kafka Streams EOS."
meta:
  - name: keywords
    content: "Kafka exactly-once, EOS, idempotent producer, transactional messaging"
---

# Exactly-Once Semantics

Exactly-once semantics (EOS) guarantee that messages are processed exactly once, even in the presence of failures. Kafka achieves this through idempotent producers, transactions, and transactional consumers.

---

## Semantic Definition

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Exactly-Once Guarantee" {
    rectangle "Messages Sent: 100" as sent
    rectangle "Messages Delivered: 100" as delivered
    rectangle "Unique Processed: 100" as processed

    sent -down-> delivered : all delivered
    delivered -down-> processed : each exactly once
}

note right of processed
  Achieved through:
  - Idempotent producer
  - Transactions
  - read_committed isolation
end note

@enduml
```

| Property | Guarantee |
|----------|-----------|
| **Delivery count** | Exactly 1 |
| **Message loss** | Never |
| **Duplicates** | Never (within Kafka) |
| **Atomicity** | Yes (transactions) |

---

## EOS Components

### Architecture Overview

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Exactly-Once Components" {

    rectangle "Idempotent Producer" as idempotent {
        card "Producer ID (PID)" as pid
        card "Sequence Numbers" as seq
        card "Epoch" as epoch

        pid -right-> seq
        seq -right-> epoch
    }

    rectangle "Transactions" as tx {
        card "Transactional ID" as txid
        card "Transaction Coordinator" as coord
        card "Atomic Commits" as atomic

        txid -right-> coord
        coord -right-> atomic
    }

    rectangle "Transactional Consumer" as txcons {
        card "read_committed" as iso
        card "Consumer Group Offset" as offset

        iso -right-> offset
    }

    idempotent -down-> tx : enables
    tx -down-> txcons : completes
}

@enduml
```

### Component Responsibilities

| Component | Responsibility |
|-----------|----------------|
| **Idempotent Producer** | Prevent duplicate writes from retries |
| **Transaction Coordinator** | Manage transaction state |
| **Transactional Consumer** | Read only committed data |
| **Consumer Group Coordinator** | Atomic offset commits |

---

## Idempotent Producer

### How It Works

The idempotent producer assigns each producer instance a unique Producer ID (PID) and tracks sequence numbers per partition.

```plantuml
@startuml

skinparam backgroundColor transparent

participant "Producer\n(PID: 1000)" as P
participant "Broker\n(Partition Leader)" as B

note over P: Idempotent producer enabled

P -> B : InitProducerId
B --> P : PID=1000, epoch=0

P -> B : Produce(partition=0, seq=0, data=A)
B -> B : Store: PID=1000, seq=0
B --> P : ack

P -> B : Produce(partition=0, seq=1, data=B)
note right of B: Network timeout

P -> B : Retry Produce(partition=0, seq=1, data=B)
B -> B : seq=1 exists for PID=1000
B --> P : ack (DuplicateSequenceException logged, no duplicate written)

P -> B : Produce(partition=0, seq=2, data=C)
B --> P : ack

@enduml
```

### Sequence Number Tracking

| State | Action |
|-------|--------|
| `seq == expected` | Accept record, increment expected |
| `seq < expected` | Duplicate; reject with DuplicateSequenceException |
| `seq > expected` | Out of order; reject with OutOfOrderSequenceException |

### Configuration

```properties
# Enable idempotent producer
enable.idempotence=true

# Automatically enforced:
# acks=all
# retries=Integer.MAX_VALUE
# max.in.flight.requests.per.connection <= 5
```

### Java Example

```java
Properties props = new Properties();
props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka:9092");
props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class);

Producer<String, String> producer = new KafkaProducer<>(props);

// Retries are deduplicated automatically
for (int i = 0; i < 1000; i++) {
    producer.send(new ProducerRecord<>("events", "key-" + i, "value-" + i));
}

producer.flush();
producer.close();
```

### Idempotent Producer Scope

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Idempotent Producer Coverage" {
    rectangle "Single Session" as single #lightgreen {
        card "Retries deduplicated" as r1
        card "Network failures handled" as r2
    }

    rectangle "Not Covered" as notcov #pink {
        card "Producer restart" as n1
        card "Multiple producers" as n2
        card "Application crashes" as n3
    }
}

note bottom of single
  ✅ Within producer lifecycle
  PID + sequence provides dedup
end note

note bottom of notcov
  ❌ New PID on restart
  Need transactions for cross-session
end note

@enduml
```

---

## Transactions

### Transaction Lifecycle

```plantuml
@startuml

skinparam backgroundColor transparent

participant "Producer" as P
participant "Transaction\nCoordinator" as TC
participant "Partition\nLeaders" as PL
participant "Consumer\nCoordinator" as CC

== Initialization ==
P -> TC : InitProducerId(transactional.id)
TC --> P : PID=1000, epoch=0

== Transaction ==
P -> TC : AddPartitionsToTxn(topic-0, topic-1)
TC --> P : OK

P -> PL : Produce(topic-0, txn marker)
P -> PL : Produce(topic-1, txn marker)
PL --> P : ack

P -> CC : AddOffsetsToTxn(group-id)
CC --> P : OK

P -> CC : TxnOffsetCommit(offsets)
CC --> P : OK

== Commit ==
P -> TC : EndTxn(COMMIT)
TC -> PL : WriteTxnMarkers(COMMIT)
TC -> CC : WriteTxnMarkers(COMMIT)
TC --> P : COMMIT complete

@enduml
```

### Transaction States

```plantuml
@startuml

skinparam backgroundColor transparent

state "Empty" as Empty
state "Ongoing" as Ongoing
state "PrepareCommit" as PrepCommit
state "PrepareAbort" as PrepAbort
state "CompleteCommit" as CompleteCommit
state "CompleteAbort" as CompleteAbort
state "Dead" as Dead

[*] --> Empty : InitProducerId

Empty --> Ongoing : beginTransaction()
Ongoing --> Ongoing : send(), addPartition()
Ongoing --> PrepCommit : commitTransaction()
Ongoing --> PrepAbort : abortTransaction()
Ongoing --> PrepAbort : error/timeout

PrepCommit --> CompleteCommit : markers written
PrepAbort --> CompleteAbort : markers written

CompleteCommit --> Empty : transaction complete
CompleteAbort --> Empty : transaction complete

Empty --> Dead : transactional.id expires

@enduml
```

### Configuration

```properties
# Producer configuration
transactional.id=my-app-instance-1
enable.idempotence=true             # Required for transactions

# Consumer configuration
isolation.level=read_committed       # Only see committed transactions
enable.auto.commit=false            # Manual offset management
```

### Java Transaction Example

```java
Properties props = new Properties();
props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka:9092");
props.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "order-processor-1");
props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class);

KafkaProducer<String, String> producer = new KafkaProducer<>(props);

// Initialize transactions (call once on startup)
producer.initTransactions();

try {
    producer.beginTransaction();

    // Send to multiple partitions atomically
    producer.send(new ProducerRecord<>("orders", "order-1", "data-1"));
    producer.send(new ProducerRecord<>("audit", "order-1", "audit-1"));
    producer.send(new ProducerRecord<>("notifications", "user-1", "notify-1"));

    // All writes commit together
    producer.commitTransaction();
} catch (ProducerFencedException | OutOfOrderSequenceException e) {
    // Fatal errors - cannot recover
    producer.close();
    throw e;
} catch (KafkaException e) {
    // Abort and retry
    producer.abortTransaction();
}
```

---

## Read-Process-Write Pattern

### Canonical EOS Pattern

The read-process-write pattern consumes from input topics, processes, and produces to output topics atomically.

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Read-Process-Write" {
    rectangle "Input Topic" as input
    rectangle "Processing\n(Application)" as proc
    rectangle "Output Topic" as output
    rectangle "Consumer\nOffsets" as offsets

    input --> proc : read
    proc --> output : write
    proc --> offsets : commit
}

note bottom of proc
  Transaction includes:
  1. Output records
  2. Consumer offset commit
  Atomic: all succeed or none
end note

@enduml
```

### Implementation

```java
// Configure producer for transactions
Properties producerProps = new Properties();
producerProps.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka:9092");
producerProps.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "stream-processor-1");
producerProps.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);

// Configure consumer for read_committed
Properties consumerProps = new Properties();
consumerProps.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka:9092");
consumerProps.put(ConsumerConfig.GROUP_ID_CONFIG, "stream-processors");
consumerProps.put(ConsumerConfig.ISOLATION_LEVEL_CONFIG, "read_committed");
consumerProps.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);

KafkaProducer<String, String> producer = new KafkaProducer<>(producerProps);
KafkaConsumer<String, String> consumer = new KafkaConsumer<>(consumerProps);

producer.initTransactions();
consumer.subscribe(Collections.singletonList("input-topic"));

while (running) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));

    if (records.isEmpty()) continue;

    producer.beginTransaction();
    try {
        // Process and produce
        for (ConsumerRecord<String, String> record : records) {
            String output = process(record.value());
            producer.send(new ProducerRecord<>("output-topic", record.key(), output));
        }

        // Commit offsets as part of transaction
        Map<TopicPartition, OffsetAndMetadata> offsets = new HashMap<>();
        for (TopicPartition partition : records.partitions()) {
            List<ConsumerRecord<String, String>> partitionRecords = records.records(partition);
            long lastOffset = partitionRecords.get(partitionRecords.size() - 1).offset();
            offsets.put(partition, new OffsetAndMetadata(lastOffset + 1));
        }

        producer.sendOffsetsToTransaction(offsets, consumer.groupMetadata());
        producer.commitTransaction();

    } catch (ProducerFencedException | OutOfOrderSequenceException e) {
        // Fatal - close and restart
        throw e;
    } catch (KafkaException e) {
        // Recoverable - abort and retry
        producer.abortTransaction();
        // Consumer will re-read uncommitted records
    }
}
```

### Failure Scenarios

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Failure Handling" {

    rectangle "Success" as success #lightgreen {
        card "1. Read records" as s1
        card "2. Process" as s2
        card "3. Produce output" as s3
        card "4. Commit offsets" as s4
        card "5. Commit transaction" as s5
        s1 --> s2 --> s3 --> s4 --> s5
    }

    rectangle "Failure → Abort" as failure #lightyellow {
        card "1. Read records" as f1
        card "2. Process" as f2
        card "3. Produce output" as f3
        card "4. Error occurs" as f4
        card "5. Abort transaction" as f5
        card "6. Re-read records" as f6
        f1 --> f2 --> f3 --> f4 --> f5 --> f6
    }

    rectangle "Zombie Fencing" as zombie #lightpink {
        card "Old producer continues" as z1
        card "New producer starts" as z2
        card "Old producer fenced" as z3
        z1 --> z2 --> z3
    }
}

@enduml
```

---

## Transactional Consumer

### Isolation Levels

| Isolation Level | Behavior |
|-----------------|----------|
| `read_uncommitted` | See all records including aborted transactions |
| `read_committed` | See only committed records; aborted filtered |

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Topic: orders" as topic {
    card "Record A (committed)" as a
    card "Record B (txn in progress)" as b
    card "Record C (aborted)" as c
    card "Record D (committed)" as d
}

rectangle "read_uncommitted\nConsumer" as uncommit {
    card "Sees: A, B, C, D" as u1
}

rectangle "read_committed\nConsumer" as commit {
    card "Sees: A, D" as c1
    note right: B filtered (in progress)\nC filtered (aborted)
}

topic --> uncommit
topic --> commit

@enduml
```

### Consumer Configuration

```properties
# Transactional consumer
isolation.level=read_committed
enable.auto.commit=false
auto.offset.reset=earliest
```

### Last Stable Offset (LSO)

The LSO is the offset up to which all transactions are complete.

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Partition Log" {
    card "0: A (committed)" as r0
    card "1: B (committed)" as r1
    card "2: C (txn-1 ongoing)" as r2
    card "3: D (committed)" as r3
    card "4: E (txn-1 ongoing)" as r4
    card "5: F (committed)" as r5
}

r0 -right-> r1
r1 -right-> r2
r2 -right-> r3
r3 -right-> r4
r4 -right-> r5

note bottom of r1
  LSO = 2
  Consumer sees 0, 1
end note

note bottom of r5
  HW = 6
  After txn-1 commits:
  LSO = 6
  Consumer sees 0, 1, 2, 3, 4, 5
  (C and E now visible)
end note

@enduml
```

---

## Kafka Streams EOS

### Processing Guarantee Configuration

```java
Properties props = new Properties();
props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka:9092");
props.put(StreamsConfig.APPLICATION_ID_CONFIG, "order-processor");

// Enable exactly-once v2 (Kafka 2.5+)
props.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG,
    StreamsConfig.EXACTLY_ONCE_V2);

KafkaStreams streams = new KafkaStreams(topology, props);
streams.start();
```

### EOS Versions

| Version | Kafka Version | Description |
|---------|---------------|-------------|
| `exactly_once` | 0.11.0+ | Original EOS; one producer per task |
| `exactly_once_v2` | 2.5.0+ | Optimized; one producer per thread |

### Streams EOS Internals

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Kafka Streams EOS" {
    rectangle "Stream Task" as task {
        rectangle "Source" as src
        rectangle "Processor" as proc
        rectangle "Sink" as sink
        rectangle "State Store" as state

        src --> proc
        proc --> sink
        proc --> state
    }

    rectangle "Transaction" as txn {
        card "Output records" as out
        card "State changelog" as changelog
        card "Consumer offsets" as offsets
    }

    sink --> out
    state --> changelog

    task --> txn : atomic commit
}

note bottom of txn
  All three committed atomically:
  - Output to downstream topics
  - State store changelog
  - Input consumer offsets
end note

@enduml
```

---

## Performance Considerations

### Latency Impact

```plantuml
@startuml

skinparam backgroundColor transparent

concise "At-Least-Once" as ALO
concise "Exactly-Once" as EOS

@0
ALO is "Send"
EOS is "Send"

@5
ALO is "Ack"
EOS is "TxnInit"

@10
ALO is "Done"
EOS is "Produce"

@15
EOS is "Commit"

@20
EOS is "Done"

@enduml
```

| Metric | At-Least-Once | Exactly-Once | Overhead |
|--------|:-------------:|:------------:|:--------:|
| **Latency (p50)** | ~5ms | ~20ms | +15ms |
| **Latency (p99)** | ~20ms | ~100ms | +80ms |
| **Throughput** | High | Moderate | -30-50% |

### Throughput Optimization

```properties
# Batch transactions for better throughput
# Process multiple records per transaction
max.poll.records=1000

# Longer commit intervals
transaction.timeout.ms=60000

# Increase producer batch size
batch.size=65536
linger.ms=10
```

### When EOS Overhead is Acceptable

| Scenario | Recommendation |
|----------|----------------|
| Financial calculations | Use EOS; correctness critical |
| Billing/metering | Use EOS; duplicates costly |
| Stream aggregations | Use EOS; state must be consistent |
| High-throughput logging | Use at-least-once; EOS overhead too high |

---

## Zombie Fencing

### Producer Fencing

When a producer crashes and restarts (or a new instance starts with the same transactional.id), the old producer is "fenced."

```plantuml
@startuml

skinparam backgroundColor transparent

participant "Producer A\n(epoch=0)" as A
participant "Coordinator" as C
participant "Producer A'\n(epoch=1)" as A2

A -> C : InitProducerId(txn.id=app-1)
C --> A : PID=100, epoch=0

A -> A : Processing...

note over A: Crash/Restart

A2 -> C : InitProducerId(txn.id=app-1)
C -> C : Increment epoch
C --> A2 : PID=100, epoch=1

note over A2: A' is now the valid producer

A -> C : Produce (epoch=0)
C --> A : ProducerFencedException
note right of A: Old producer fenced

@enduml
```

### Handling ProducerFencedException

```java
try {
    producer.commitTransaction();
} catch (ProducerFencedException e) {
    // Another instance with same transactional.id is active
    // This instance must shut down
    log.error("Producer fenced - another instance is active", e);
    producer.close();
    System.exit(1);
}
```

---

## EOS Scope and Limitations

### What EOS Covers

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "EOS Coverage" {
    rectangle "Kafka Internal" as internal #lightgreen {
        card "Topic A → Topic B" as t1
        card "Consumer offsets" as t2
        card "State store changelog" as t3
    }

    rectangle "External Systems" as external #lightyellow {
        database "Database" as db
        database "Cache" as cache
        cloud "API" as api
    }
}

note bottom of internal
  ✅ Full exactly-once guarantee
end note

note bottom of external
  ⚠️ Requires additional patterns:
  - Idempotent writes
  - Two-phase commit
  - Outbox pattern
end note

@enduml
```

### External System Integration

| Pattern | Description | Use Case |
|---------|-------------|----------|
| **Idempotent sink** | Sink handles duplicates | Database with unique constraints |
| **Outbox pattern** | Write to Kafka via outbox table | Database + Kafka consistency |
| **Saga pattern** | Compensating transactions | Distributed workflow |

### Idempotent Database Sink

```java
// Use idempotency key for external writes
producer.beginTransaction();
try {
    for (ConsumerRecord<String, String> record : records) {
        // Database write with idempotency
        String idempotencyKey = record.topic() + "-" +
            record.partition() + "-" + record.offset();

        database.upsert(
            "INSERT INTO events (idempotency_key, data) VALUES (?, ?) " +
            "ON CONFLICT (idempotency_key) DO NOTHING",
            idempotencyKey, record.value()
        );
    }

    producer.sendOffsetsToTransaction(offsets, consumer.groupMetadata());
    producer.commitTransaction();
} catch (Exception e) {
    producer.abortTransaction();
}
```

---

## Version Requirements

| Feature | Minimum Kafka Version |
|---------|:---------------------:|
| Idempotent producer | 0.11.0 |
| Transactions | 0.11.0 |
| Exactly-once (original) | 0.11.0 |
| Exactly-once v2 | 2.5.0 |
| Kafka Connect EOS | 3.3.0 |

---

## Configuration Reference

### Producer

| Configuration | Required | Default | Description |
|---------------|:--------:|:-------:|-------------|
| `enable.idempotence` | Yes | false | Enable idempotent producer |
| `transactional.id` | For txn | - | Unique transaction identifier |
| `transaction.timeout.ms` | No | 60000 | Transaction timeout |
| `max.in.flight.requests.per.connection` | No | 5 | Must be ≤ 5 for idempotence |

### Consumer

| Configuration | Required | Default | Description |
|---------------|:--------:|:-------:|-------------|
| `isolation.level` | Yes | read_uncommitted | Set to read_committed for EOS |
| `enable.auto.commit` | Yes | true | Set to false for EOS |

### Broker

| Configuration | Default | Description |
|---------------|:-------:|-------------|
| `transaction.state.log.replication.factor` | 3 | Transaction log replication |
| `transaction.state.log.min.isr` | 2 | Minimum ISR for transaction log |
| `transactional.id.expiration.ms` | 604800000 | Transaction ID expiration |

---

## Related Documentation

- [Delivery Semantics Overview](index.md) - Semantic comparison
- [At-Most-Once](at-most-once.md) - Fire and forget patterns
- [At-Least-Once](at-least-once.md) - Retry with idempotent consumers
- [Choosing Semantics](choosing-semantics.md) - Decision guide
- [Transactions](../../producers/index.md) - Transaction API details
