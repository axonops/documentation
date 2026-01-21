---
title: "What is Event Streaming?"
description: "Event streaming concepts, pub/sub versus message queues, and the distributed commit log model that underlies Apache Kafka."
meta:
  - name: keywords
    content: "event streaming, pub/sub, message queue, commit log, Apache Kafka, event-driven architecture"
---

# What is Event Streaming?

Event streaming is a data architecture paradigm where data is captured, stored, and processed as continuous streams of events.

---

## The Event-Driven Paradigm

Traditional application architectures are request-driven: a client sends a request, the server processes it, and returns a response. Data is stored in databases and queried on demand.

Event-driven architectures invert this model: systems emit events as things happen, and other systems react to those events. Events are stored in order and can be replayed, enabling new capabilities that request-response architectures cannot provide.

```plantuml
@startuml

rectangle "Request-Response Architecture" as rr {
  rectangle "Client" as rr_client
  database "Database" as rr_db
  rectangle "Server" as rr_server

  rr_client -> rr_server : request
  rr_server -> rr_db : query
  rr_db -> rr_server : data
  rr_server -> rr_client : response
}

rectangle "Event-Driven Architecture" as ed {
  rectangle "Producer" as ed_prod
  queue "Event Stream" as ed_stream
  rectangle "Consumer A" as ed_cons_a
  rectangle "Consumer B" as ed_cons_b
  database "Materialized\nView" as ed_view

  ed_prod -> ed_stream : emit event
  ed_stream -> ed_cons_a : react
  ed_stream -> ed_cons_b : react
  ed_cons_b -> ed_view : update
}

rr -[hidden]down- ed

@enduml
```

### Events vs Commands

| Concept | Definition | Example |
|---------|------------|---------|
| **Event** | Immutable fact that something occurred | "OrderPlaced", "PaymentReceived", "UserLoggedIn" |
| **Command** | Request for something to happen | "PlaceOrder", "ProcessPayment", "SendEmail" |

Events are named in past tense because they represent facts that have already happened. Commands are named in imperative form because they request future action.

Key distinction: Events describe what happened. Commands can be accepted or rejected based on business rules; if a command is rejected, no event is emitted (or a rejection event is emitted).

---

## The Commit Log Model

At its core, Kafka is a distributed commit log: an ordered, append-only sequence of records. This simple data structure provides powerful guarantees.

```plantuml
@startuml

rectangle "Commit Log" {
  card "0" as r0
  card "1" as r1
  card "2" as r2
  card "3" as r3
  card "4" as r4
  card "5" as r5
  card "..." as dots

  r0 -right-> r1 : append
  r1 -right-> r2 : only
  r2 -right-> r3
  r3 -right-> r4
  r4 -right-> r5
  r5 -right-> dots
}

rectangle "Writer" as writer
rectangle "Reader A\n(offset: 2)" as reader_a
rectangle "Reader B\n(offset: 5)" as reader_b

writer -down-> dots : append new records

reader_a -up-> r2 : read from position
reader_b -up-> r5 : read from position

note bottom of r0
  Records are immutable
  and never modified
end note

@enduml
```

### Commit Log Properties

| Property | Description |
|----------|-------------|
| **Append-only** | New records are only added to the end; existing records are never modified |
| **Immutable** | Once written, records cannot be changed |
| **Ordered** | Records have a strict sequence (offset) |
| **Durable** | Records are persisted to disk and replicated when configured |
| **Replayable** | Readers can start from any retained position and replay forward |

### Why Append-Only?

The append-only constraint enables:

1. **Sequential I/O**: Writing to the end of a file is orders of magnitude faster than random writes
2. **Easy replication**: Followers simply append whatever the leader appends
3. **Consumer independence**: Readers track their own position without modifying the log
4. **Point-in-time recovery**: Start from any offset to replay history

---

## Comparing Messaging Models

### Traditional Message Queues

Traditional message queues (RabbitMQ, ActiveMQ, IBM MQ) implement a push-based model where the broker actively delivers messages to consumers.

```plantuml
@startuml

rectangle "Message Queue Model" {
  rectangle "Producer" as mq_prod
  queue "Queue" as mq_queue
  rectangle "Consumer 1" as mq_c1
  rectangle "Consumer 2" as mq_c2

  mq_prod -> mq_queue : send
  mq_queue -> mq_c1 : push\n(deleted after ack)
  mq_queue ..> mq_c2 : waiting
}

note bottom of mq_queue
  Messages are removed
  after acknowledgment
end note

@enduml
```

**Queue characteristics:**

| Aspect | Behavior |
|--------|----------|
| Delivery | Push-based—broker sends to consumers |
| Lifetime | Message deleted after successful delivery |
| Consumers | Competing—each message goes to one consumer |
| Ordering | Usually FIFO across entire queue |
| Replay | Not possible—messages are deleted |

### Publish-Subscribe

Traditional pub/sub systems deliver messages to all subscribers of a topic.

```plantuml
@startuml

rectangle "Pub/Sub Model" {
  rectangle "Publisher" as ps_pub
  collections "Topic" as ps_topic
  rectangle "Subscriber 1" as ps_s1
  rectangle "Subscriber 2" as ps_s2
  rectangle "Subscriber 3" as ps_s3

  ps_pub -> ps_topic : publish
  ps_topic -> ps_s1 : copy
  ps_topic -> ps_s2 : copy
  ps_topic -> ps_s3 : copy
}

note bottom of ps_topic
  Each subscriber
  receives all messages
end note

@enduml
```

**Pub/sub characteristics:**

| Aspect | Behavior |
|--------|----------|
| Delivery | Push-based or pull-based depending on implementation |
| Lifetime | Often transient—no retention |
| Consumers | Independent—all subscribers receive everything |
| Ordering | Often not guaranteed |
| Replay | Limited or not supported |

### Kafka's Log Model

Kafka combines the best of both models through consumer groups.

```plantuml
@startuml

rectangle "Kafka Log Model" {
  rectangle "Producer" as kafka_prod
  database "Topic\n(partitioned log)" as kafka_log

  rectangle "Consumer Group A" as cg_a {
    rectangle "Consumer A1" as a1
    rectangle "Consumer A2" as a2
  }

  rectangle "Consumer Group B" as cg_b {
    rectangle "Consumer B1" as b1
  }

  kafka_prod -> kafka_log : append
  kafka_log -> a1 : pull (partitions 0-1)
  kafka_log -> a2 : pull (partitions 2-3)
  kafka_log -> b1 : pull (all partitions)
}

note bottom of kafka_log
  Messages retained
  regardless of consumption
end note

@enduml
```

**Kafka characteristics:**

| Aspect | Behavior |
|--------|----------|
| Delivery | Pull-based—consumers fetch at their own pace |
| Lifetime | Retained based on time or size policy |
| Consumers | Consumer groups enable both queue and pub/sub semantics |
| Ordering | Guaranteed per partition; per-producer order preserved |
| Replay | Full replay from any retained offset |

---

## Pull vs Push Delivery

Kafka uses a pull-based model where consumers request data from brokers, rather than brokers pushing data to consumers.

### Advantages of Pull

| Advantage | Explanation |
|-----------|-------------|
| **Consumer-controlled rate** | Consumers fetch only what they can process, preventing overload |
| **Batching efficiency** | Consumers can batch requests for efficient network utilization |
| **Simple broker** | Broker does not track consumer state or manage delivery retries |
| **Replay support** | Consumers control their position and can re-read data |

### Push Model Drawbacks

In push-based systems:

- Broker must track each consumer's state
- Slow consumers can back up the entire system
- Broker must implement complex flow control
- Replay requires special infrastructure

---

## Event Streaming Benefits

### Temporal Decoupling

Producers and consumers do not need to be online simultaneously. A consumer can process events hours or days after they were produced.

```plantuml
@startuml
skinparam sequenceMessageAlign center

participant "Producer" as prod
participant "Kafka" as kafka
participant "Consumer" as cons

prod -> kafka : produce (09:00)
activate kafka
note over kafka : event stored
prod -> kafka : produce (09:05)
note over kafka : event stored

... 2 hours later ...

cons -> kafka : fetch (11:00)
kafka -> cons : events from 09:00
cons -> kafka : commit offset
deactivate kafka

@enduml
```

### Replayability

Events can be replayed to:

- Rebuild materialized views
- Fix bugs in processing logic and reprocess
- Bootstrap new consumers with historical data
- Perform what-if analysis on historical events

### Multiple Consumer Patterns

The same topic can serve different use cases simultaneously:

| Consumer Group | Use Case | Processing Pattern |
|----------------|----------|-------------------|
| `analytics` | Real-time dashboards | Streaming aggregation |
| `search-indexer` | Search updates | Index on every event |
| `data-warehouse` | Batch analytics | Periodic bulk loads |
| `audit-log` | Compliance | Long-term archival |

### Loose Coupling

Producers and consumers are decoupled:

- Producers do not know who consumes their events
- Consumers do not know who produces events
- New consumers can be added without producer changes
- Processing logic can be changed without affecting producers

---

## Event Sourcing with Kafka

Event sourcing stores the sequence of events that led to current state, rather than just the current state itself.

```plantuml
@startuml

rectangle "Traditional: Store Current State" as trad {
  database "Account\nbalance: $500" as trad_db
}

rectangle "Event Sourcing: Store Events" as es {
  database "Event Log" as es_log {
    card "AccountOpened\n+$0" as e1
    card "Deposited\n+$1000" as e2
    card "Withdrawn\n-$200" as e3
    card "Withdrawn\n-$300" as e4
  }

  rectangle "Current State\n(derived)\nbalance: $500" as es_state
}

es_log -right-> es_state : replay\nto derive

note bottom of es_log
  Complete history
  Audit trail
  Replay to any point
end note

@enduml
```

### Event Sourcing Benefits

| Benefit | Description |
|---------|-------------|
| **Complete audit trail** | Every state change is recorded |
| **Temporal queries** | "What was the state at time T?" |
| **Debugging** | Replay events to understand what happened |
| **Flexibility** | Derive new views from historical events |

Kafka's log retention and compaction features make it suitable as an event store for event-sourced systems.

---

## Stream Processing Concepts

Event streaming enables stream processing: continuous computation over unbounded data.

### Bounded vs Unbounded Data

| Data Type | Characteristics | Processing |
|-----------|-----------------|------------|
| **Bounded** | Fixed size, complete | Batch processing |
| **Unbounded** | Infinite, never complete | Stream processing |

Traditional batch processing operates on bounded datasets. Stream processing operates on unbounded streams, processing events as they arrive.

### Windowing

Since streams are unbounded, aggregations require windows—bounded subsets of the stream.

```plantuml
@startuml

rectangle "Event Stream (time →)" as stream {
  card "10:00" as t1
  card "10:01" as t2
  card "10:02" as t3
  card "10:03" as t4
  card "10:04" as t5
  card "10:05" as t6

  t1 -right-> t2
  t2 -right-> t3
  t3 -right-> t4
  t4 -right-> t5
  t5 -right-> t6
}

rectangle "Tumbling Window\n(5 min, non-overlapping)" as tumbling {
  rectangle "[10:00-10:05)" as tw1
  rectangle "[10:05-10:10)" as tw2
}

rectangle "Hopping Window\n(5 min, advance 2 min)" as hopping {
  rectangle "[10:00-10:05)" as hw1
  rectangle "[10:02-10:07)" as hw2
  rectangle "[10:04-10:09)" as hw3
}

stream -[hidden]down- tumbling
tumbling -[hidden]down- hopping

@enduml
```

| Window Type | Description | Use Case |
|-------------|-------------|----------|
| **Tumbling** | Fixed size, non-overlapping | Hourly aggregations |
| **Hopping** | Fixed size, overlapping | Moving averages |
| **Sliding** | Fixed size, event-triggered | Continuous monitoring |
| **Session** | Activity-based, variable size | User session analytics |

---

## Related Documentation

- [Event Streaming Fundamentals](index.md) - Core concepts overview
- [Kafka Ecosystem](kafka-ecosystem.md) - Kafka platform components
- [Architecture Patterns](architecture-patterns/index.md) - Event sourcing, CQRS, CDC
- [Delivery Semantics](delivery-semantics/index.md) - Message delivery guarantees
