---
title: "Kafka Architecture Patterns"
description: "Event-driven architecture patterns with Apache Kafka. Event sourcing, CQRS, saga patterns, and stream processing architectures."
meta:
  - name: keywords
    content: "Kafka patterns, event sourcing, CQRS, saga pattern, event-driven architecture"
---

# Architecture Patterns

Common architectural patterns for building event-driven systems with Apache Kafka.

---

## Pattern Overview

| Pattern | Use Case | Complexity |
|---------|----------|------------|
| **Event Notification** | Decoupled service communication | Low |
| **Event-Carried State Transfer** | Avoid synchronous queries | Medium |
| **Event Sourcing** | Audit, replay, temporal queries | High |
| **CQRS** | Separate read/write models | High |
| **Saga** | Distributed transactions | High |

---

## Event Notification

Services publish events when state changes occur. Consumers react to events independently.

```plantuml
@startuml

rectangle "Order Service" as order
rectangle "Kafka" as kafka
rectangle "Inventory Service" as inventory
rectangle "Shipping Service" as shipping
rectangle "Notification Service" as notify

order -> kafka : OrderCreated
kafka -> inventory : consume
kafka -> shipping : consume
kafka -> notify : consume

note bottom of kafka
  Event contains minimal data
  (e.g., order_id only)
  Consumers query for details
end note

@enduml
```

### Characteristics

| Aspect | Description |
|--------|-------------|
| **Coupling** | Loose—services only share event contracts |
| **Data** | Minimal—typically just identifiers |
| **Query pattern** | Consumers may need to query producer for details |
| **Consistency** | Eventually consistent |

### When to Use

- Simple notification requirements
- Consumers need fresh data on demand
- Low event volume

---

## Event-Carried State Transfer

Events carry complete state needed by consumers, eliminating synchronous queries.

```plantuml
@startuml

rectangle "Order Service" as order
rectangle "Kafka" as kafka
rectangle "Shipping Service" as shipping

order -> kafka : OrderCreated {\n  order_id\n  customer_name\n  shipping_address\n  items[]\n}

kafka -> shipping : consume

note right of shipping
  No need to query Order Service
  All required data in event
end note

@enduml
```

### Characteristics

| Aspect | Description |
|--------|-------------|
| **Coupling** | Medium—larger event contracts |
| **Data** | Complete—all data consumers need |
| **Query pattern** | No synchronous queries required |
| **Consistency** | Eventually consistent with local caching |

### When to Use

- Consumers need complete data for processing
- Reducing inter-service dependencies
- Building local read models

---

## Event Sourcing

Store all state changes as an immutable sequence of events. Current state is derived by replaying events.

```plantuml
@startuml

database "Event Store\n(Kafka topic)" as events

rectangle "Write Path" as write {
  rectangle "Command" as cmd
  rectangle "Aggregate" as agg
}

rectangle "Read Path" as read {
  rectangle "Projection" as proj
  database "Read Model" as rm
}

cmd -> agg : validate
agg -> events : append events

events -> proj : consume
proj -> rm : update

note bottom of events
  Events are immutable
  Topic uses log compaction
  or infinite retention
end note

@enduml
```

### Event Store Design

```
Topic: orders (compacted or infinite retention)

Key: order_id
Events:
  OrderCreated { order_id, customer_id, items }
  ItemAdded { order_id, item }
  ItemRemoved { order_id, item_id }
  OrderSubmitted { order_id, submitted_at }
  OrderCancelled { order_id, reason }
```

### Characteristics

| Aspect | Description |
|--------|-------------|
| **Audit** | Complete history of all changes |
| **Replay** | Rebuild state from any point in time |
| **Temporal queries** | Query state at any historical moment |
| **Complexity** | High—requires event versioning, snapshots |

### Implementation Considerations

| Concern | Solution |
|---------|----------|
| **Event versioning** | Include version in events, use upcasters |
| **Snapshots** | Periodically snapshot state to reduce replay time |
| **Compaction** | Use log compaction to retain latest per key |
| **Schema evolution** | Use Schema Registry with compatibility rules |

---

## CQRS (Command Query Responsibility Segregation)

Separate models for reading and writing data. Kafka connects the two.

```plantuml
@startuml

rectangle "Command Side" as cmd_side {
  rectangle "Command API" as cmd_api
  rectangle "Domain Model" as domain
  database "Write Store" as write_db
}

rectangle "Kafka" as kafka

rectangle "Query Side" as query_side {
  rectangle "Query API" as query_api
  rectangle "Projection" as proj
  database "Read Store\n(Cassandra)" as read_db
}

cmd_api -> domain : commands
domain -> write_db : persist
domain -> kafka : publish events

kafka -> proj : consume
proj -> read_db : update

query_api -> read_db : query

note bottom of kafka
  Events synchronize
  read and write models
end note

@enduml
```

### Read Model Optimization

| Read Pattern | Optimized Store | Example |
|--------------|-----------------|---------|
| Key-value lookup | Cassandra | User by ID |
| Full-text search | Elasticsearch | Product search |
| Aggregations | ClickHouse | Analytics |
| Graph queries | Neo4j | Recommendations |

### Characteristics

| Aspect | Description |
|--------|-------------|
| **Scalability** | Independent scaling of read/write |
| **Optimization** | Each model optimized for its access pattern |
| **Consistency** | Eventually consistent between models |
| **Complexity** | High—multiple data stores, synchronization |

---

## Saga Pattern

Coordinate distributed transactions across services using events.

```plantuml
@startuml

rectangle "Order Saga" as saga {
  rectangle "Order Service" as order
  rectangle "Payment Service" as payment
  rectangle "Inventory Service" as inventory
}

rectangle "Kafka" as kafka

order -> kafka : OrderCreated
kafka -> payment : reserve payment
payment -> kafka : PaymentReserved
kafka -> inventory : reserve items
inventory -> kafka : ItemsReserved
kafka -> order : complete order

note bottom of saga
  Choreography: Services react to events
  No central coordinator
end note

@enduml
```

### Saga Types

| Type | Description | Pros | Cons |
|------|-------------|------|------|
| **Choreography** | Services react to events | Loose coupling | Hard to track flow |
| **Orchestration** | Central coordinator | Clear flow | Single point of failure |

### Compensation

When a step fails, compensating events undo previous steps.

```
Happy Path:
  OrderCreated -> PaymentReserved -> ItemsReserved -> OrderCompleted

Failure (inventory unavailable):
  OrderCreated -> PaymentReserved -> ItemsUnavailable -> PaymentReleased -> OrderFailed
```

### Implementation with Kafka

| Concern | Solution |
|---------|----------|
| **Ordering** | Use order_id as partition key |
| **Idempotency** | Include saga_id, step_id in events |
| **Timeout** | Use Kafka Streams punctuators or external scheduler |
| **Dead letters** | Route failed events to DLQ for investigation |

---

## Streaming Patterns

### Stateless Stream Processing

Transform events without maintaining state.

```plantuml
@startuml

queue "Input Topic" as input
rectangle "Kafka Streams\n(stateless)" as streams
queue "Output Topic" as output

input -> streams : events
streams -> output : transformed

note right of streams
  Operations:
  - filter
  - map
  - flatMap
  - branch
end note

@enduml
```

### Stateful Stream Processing

Aggregate events maintaining state.

```plantuml
@startuml

queue "Input Topic" as input
rectangle "Kafka Streams\n(stateful)" as streams
database "State Store\n(RocksDB)" as state
queue "Output Topic" as output

input -> streams : events
streams <-> state : read/write
streams -> output : aggregated

note right of state
  Operations:
  - count
  - reduce
  - aggregate
  - join
end note

@enduml
```

---

## Pattern Selection Guide

| Requirement | Recommended Pattern |
|-------------|---------------------|
| Simple decoupling | Event Notification |
| Avoid inter-service queries | Event-Carried State Transfer |
| Complete audit trail | Event Sourcing |
| Separate read optimization | CQRS |
| Distributed transactions | Saga |
| Real-time transformations | Kafka Streams |

---

## Related Documentation

- [Event Streaming Concepts](../index.md) - Kafka fundamentals
- [Kafka Streams](../../application-development/kafka-streams/index.md) - Stream processing
- [Delivery Semantics](../delivery-semantics/index.md) - Consistency guarantees
- [Data Integration](../data-integration/index.md) - Integration patterns
