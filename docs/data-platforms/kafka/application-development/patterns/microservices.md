---
title: "Microservices with Kafka"
description: "Kafka architecture patterns for microservices. Topic ownership, consumer group strategies, schema governance, distributed tracing, and deployment patterns."
---

# Microservices with Kafka

Kafka serves as the messaging backbone for many microservices architectures, providing asynchronous communication, event-driven integration, and data streaming between services. This document covers Kafka-specific architectural decisions and patterns for microservices environments.

---

## Topic Ownership Models

How topics are owned and managed significantly impacts team autonomy, data governance, and operational complexity.

### Per-Service Topics (Recommended)

Each service owns its output topics. Services publish events about their domain; other services subscribe as needed.

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam rectangle {
    BackgroundColor #F5F5F5
    BorderColor #333333
}

title Per-Service Topic Ownership

rectangle "Order Service" as order #C8E6C9 {
}
rectangle "Inventory Service" as inv #C8E6C9 {
}
rectangle "Notification Service" as notif #C8E6C9 {
}

queue "orders.events" as q1 #E3F2FD
queue "inventory.events" as q2 #E3F2FD
queue "notifications.events" as q3 #E3F2FD

order --> q1 : owns/produces
inv --> q2 : owns/produces
notif --> q3 : owns/produces

order ..> q2 : subscribes
notif ..> q1 : subscribes
notif ..> q2 : subscribes

note bottom of q1
Topic naming: {domain}.{type}
Owner: Order team
Schema: Order team defines
end note
@enduml
```

**Benefits:**

- Clear ownership and accountability
- Teams control their own schemas
- Independent deployment and scaling
- Natural bounded context alignment

**Topic naming conventions:**

```
{service}.{entity}.{event-type}

Examples:
orders.order.created
orders.order.shipped
inventory.stock.reserved
inventory.stock.depleted
payments.payment.completed
```

### Shared Domain Topics

Multiple services collaborate on shared domain topics. Useful for cross-cutting concerns.

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Shared Domain Topics

rectangle "Service A" as a
rectangle "Service B" as b
rectangle "Service C" as c

queue "domain.customer.events" as q #FFF9C4

a --> q : produces CustomerCreated
b --> q : produces CustomerVerified
c --> q : produces CustomerSuspended

note bottom of q
Shared ownership requires:
- Schema compatibility rules
- Cross-team coordination
- Clear event type ownership
end note
@enduml
```

**When to use:**

- Aggregate events from multiple sources
- Cross-cutting audit/compliance streams
- Shared reference data

**Governance requirements:**

- Central schema registry with compatibility enforcement
- Clear documentation of which service owns which event types
- Breaking change coordination process

---

## Consumer Group Strategies

Consumer group design affects scaling, fault isolation, and message ordering guarantees.

### One Consumer Group Per Service

Each service instance joins the same consumer group, sharing partition load.

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam sequence {
    ArrowColor #333333
    ParticipantBackgroundColor #F5F5F5
}

title Consumer Group Per Service

collections "Order Service\n(3 instances)" as order
collections "Notification Service\n(2 instances)" as notif
queue "payments.events\n(6 partitions)" as topic

topic --> order : consumer-group:\norder-service\n(partitions 0-5)
topic --> notif : consumer-group:\nnotification-service\n(partitions 0-5)

note right of order
Each service has independent:
- Offset tracking
- Scaling
- Failure handling
end note
@enduml
```

**Configuration:**

```properties
# Order Service
group.id=order-service
client.id=order-service-${HOSTNAME}

# Notification Service
group.id=notification-service
client.id=notification-service-${HOSTNAME}
```

### Multiple Consumer Groups Within a Service

A service may need multiple consumption patterns for the same topic.

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Multiple Groups in One Service

rectangle "Analytics Service" as svc {
    rectangle "Real-time\nProcessor" as rt
    rectangle "Batch\nAggregator" as batch
    rectangle "Audit\nLogger" as audit
}

queue "orders.events" as topic

topic --> rt : analytics-realtime\n(latest offset)
topic --> batch : analytics-batch\n(periodic reset)
topic --> audit : analytics-audit\n(all events)

note bottom of svc
Same service, different processing needs:
- Different offset management
- Different scaling requirements
- Different failure handling
end note
@enduml
```

**Use cases:**

- Real-time vs batch processing
- Primary processing vs audit logging
- Different retention/replay requirements

---

## Schema Governance

Schema management becomes critical when multiple teams produce and consume events.

### Schema Registry Integration

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam sequence {
    ArrowColor #333333
    LifeLineBorderColor #666666
    ParticipantBackgroundColor #F5F5F5
}

title Schema Evolution Flow

participant "Producer\nService" as prod
participant "Schema\nRegistry" as sr
participant "Kafka" as kafka
participant "Consumer\nService" as cons

== Schema Registration ==
prod -> sr : Register schema v2
sr -> sr : Check compatibility\n(BACKWARD)
alt Compatible
    sr --> prod : Schema ID: 42
else Incompatible
    sr --> prod : 409 Conflict
    prod -> prod : Fix schema
end

== Message Flow ==
prod -> kafka : Message with\nschema ID: 42
kafka --> cons : Message
cons -> sr : Get schema 42
sr --> cons : Schema definition
cons -> cons : Deserialize

@enduml
```

### Compatibility Strategies Per Topic

| Strategy | Producer Changes | Consumer Changes | Use Case |
|----------|------------------|------------------|----------|
| BACKWARD | Add optional fields, remove fields | Must handle missing fields | Default for events |
| FORWARD | Remove fields, add required fields | Must ignore unknown fields | API responses |
| FULL | Only optional field additions | Handle missing + ignore unknown | Strict contracts |
| NONE | Any change allowed | Must coordinate | Development only |

**Recommended approach:**

```
# Production topics
orders.events: BACKWARD_TRANSITIVE
payments.events: BACKWARD_TRANSITIVE

# Internal/development
orders.internal.debug: NONE
```

### Cross-Team Schema Contracts

```java
// Shared schema module published as library
// teams depend on specific versions

// build.gradle
dependencies {
    implementation 'com.company:order-events-schema:2.3.0'
    implementation 'com.company:payment-events-schema:1.5.0'
}
```

**Schema ownership rules:**

1. Producing service owns the schema
2. Schema changes require PR review from known consumers
3. Breaking changes require deprecation period
4. Schema modules versioned with semantic versioning

---

## Distributed Tracing

Correlation across service boundaries is essential for debugging and monitoring.

### Trace Context Propagation

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam sequence {
    ArrowColor #333333
    LifeLineBorderColor #666666
    ParticipantBackgroundColor #F5F5F5
}

title Trace Propagation Through Kafka

participant "API Gateway" as gw
participant "Order Service" as order
queue "Kafka" as kafka
participant "Inventory Service" as inv
participant "Notification Service" as notif

gw -> order : HTTP Request\nX-Trace-ID: abc123
activate order

order -> kafka : ProducerRecord\nheader[trace-id]: abc123\nheader[span-id]: span-001
deactivate order

kafka -> inv : ConsumerRecord
activate inv
inv -> inv : Extract trace-id: abc123\nCreate child span: span-002
deactivate inv

kafka -> notif : ConsumerRecord
activate notif
notif -> notif : Extract trace-id: abc123\nCreate child span: span-003
deactivate notif

note over gw, notif
All operations visible under
single trace ID: abc123
end note
@enduml
```

### Implementation Pattern

```java
public class TracingProducerInterceptor implements ProducerInterceptor<String, Object> {

    @Override
    public ProducerRecord<String, Object> onSend(ProducerRecord<String, Object> record) {
        Span currentSpan = Tracer.currentSpan();
        if (currentSpan != null) {
            record.headers().add("trace-id",
                currentSpan.context().traceId().getBytes());
            record.headers().add("span-id",
                currentSpan.context().spanId().getBytes());
            record.headers().add("parent-span-id",
                currentSpan.context().parentSpanId().getBytes());
        }
        return record;
    }
}

public class TracingConsumerInterceptor implements ConsumerInterceptor<String, Object> {

    @Override
    public ConsumerRecords<String, Object> onConsume(ConsumerRecords<String, Object> records) {
        for (ConsumerRecord<String, Object> record : records) {
            String traceId = extractHeader(record, "trace-id");
            String parentSpanId = extractHeader(record, "span-id");

            // Create child span linked to producer
            Span span = Tracer.newChildSpan(traceId, parentSpanId)
                .name("kafka.consume")
                .tag("topic", record.topic())
                .tag("partition", record.partition())
                .start();

            // Store in thread-local for downstream use
            Tracer.setCurrentSpan(span);
        }
        return records;
    }
}
```

### Standard Headers for Tracing

| Header | Purpose | Example |
|--------|---------|---------|
| `trace-id` | Unique ID for entire request flow | `abc123def456` |
| `span-id` | ID for this specific operation | `span-001` |
| `parent-span-id` | ID of calling operation | `span-000` |
| `correlation-id` | Business correlation (order ID, etc.) | `order-789` |
| `causation-id` | ID of event that caused this event | `event-456` |

---

## Deployment Patterns

Kafka consumers require special consideration during deployments to avoid message loss or duplication.

### Rolling Deployment

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Rolling Deployment with Consumer Rebalance

rectangle "Before" as before {
    rectangle "v1" as v1a
    rectangle "v1" as v1b
    rectangle "v1" as v1c
}

rectangle "During" as during {
    rectangle "v2" as v2a #C8E6C9
    rectangle "v1" as v1d
    rectangle "v1" as v1e
}

rectangle "After" as after {
    rectangle "v2" as v2b #C8E6C9
    rectangle "v2" as v2c #C8E6C9
    rectangle "v2" as v2d #C8E6C9
}

before -[hidden]> during
during -[hidden]> after

note bottom of during
Rebalance triggered:
1. Instance removed from group
2. Partitions reassigned
3. New instance joins
4. Another rebalance
end note
@enduml
```

**Configuration for smooth rolling deploys:**

```properties
# Reduce rebalance disruption
session.timeout.ms=30000
heartbeat.interval.ms=10000
max.poll.interval.ms=300000

# Cooperative rebalancing (Kafka 2.4+)
partition.assignment.strategy=org.apache.kafka.clients.consumer.CooperativeStickyAssignor
```

### Blue/Green Deployment

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Blue/Green Consumer Deployment

rectangle "Blue (Current)" as blue #90CAF9 {
    rectangle "order-service-blue-1" as b1
    rectangle "order-service-blue-2" as b2
}

rectangle "Green (New)" as green #C8E6C9 {
    rectangle "order-service-green-1" as g1
    rectangle "order-service-green-2" as g2
}

queue "orders.commands" as topic

topic --> blue : group: order-service\n(active)
topic ..> green : group: order-service-green\n(standby, different group)

note bottom of green
Green uses different consumer group.
On cutover:
1. Stop blue consumers
2. Reset green offsets to blue position
3. Start green consumers
end note
@enduml
```

**Cutover procedure:**

```bash
# 1. Record blue's current offsets
kafka-consumer-groups.sh --describe --group order-service

# 2. Stop blue deployment
kubectl scale deployment order-service-blue --replicas=0

# 3. Reset green to blue's offsets
kafka-consumer-groups.sh --group order-service-green \
    --reset-offsets --to-current --execute

# 4. Rename green's group (or reconfigure)
# Application config: group.id=order-service

# 5. Start green
kubectl scale deployment order-service-green --replicas=3
```

### Canary Deployment

Route percentage of partitions to canary instances.

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Canary Consumer Deployment

queue "orders.events\n(12 partitions)" as topic

rectangle "Stable (v1)" as stable {
    rectangle "v1 instances (10)" as v1
}

rectangle "Canary (v2)" as canary #FFF9C4 {
    rectangle "v2 instances (2)" as v2
}

topic --> stable : partitions 0-9
topic --> canary : partitions 10-11

note bottom of canary
Same consumer group.
Canary gets ~17% traffic.
Monitor error rates before
scaling canary up.
end note
@enduml
```

---

## Service Communication Patterns

### Request-Reply Over Kafka

For cases requiring synchronous-style responses over async infrastructure.

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam sequence {
    ArrowColor #333333
    LifeLineBorderColor #666666
    ParticipantBackgroundColor #F5F5F5
}

title Request-Reply Pattern

participant "Client Service" as client
queue "requests" as req
queue "responses" as resp
participant "Server Service" as server

client -> req : Request\ncorrelation-id: req-123\nreply-to: responses

req -> server : Consume request
server -> server : Process
server -> resp : Response\ncorrelation-id: req-123

resp -> client : Consume response\nwhere correlation-id = req-123

note over client
Client creates temporary
consumer or filters by
correlation-id
end note
@enduml
```

**Implementation considerations:**

```java
public class KafkaRequestReply {

    private final Map<String, CompletableFuture<Response>> pending =
        new ConcurrentHashMap<>();

    public CompletableFuture<Response> request(Request request, Duration timeout) {
        String correlationId = UUID.randomUUID().toString();
        CompletableFuture<Response> future = new CompletableFuture<>();

        pending.put(correlationId, future);

        // Send request
        ProducerRecord<String, Request> record =
            new ProducerRecord<>("requests", request);
        record.headers().add("correlation-id", correlationId.getBytes());
        record.headers().add("reply-to", "responses".getBytes());

        producer.send(record);

        // Timeout handling
        future.orTimeout(timeout.toMillis(), TimeUnit.MILLISECONDS)
            .whenComplete((r, ex) -> pending.remove(correlationId));

        return future;
    }

    // Response consumer
    @KafkaListener(topics = "responses")
    public void handleResponse(ConsumerRecord<String, Response> record) {
        String correlationId = extractHeader(record, "correlation-id");
        CompletableFuture<Response> future = pending.remove(correlationId);
        if (future != null) {
            future.complete(record.value());
        }
    }
}
```

!!! warning "Anti-Pattern Alert"
    Request-reply over Kafka adds significant latency compared to direct HTTP/gRPC.
    Use only when:

    - Decoupling is more important than latency
    - Request must be durable (survives client restart)
    - Load leveling is required

### Event Notification vs Event-Carried State Transfer

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Event Styles Comparison

rectangle "Event Notification" as notif #E3F2FD {
    note as n1
    {
      "type": "OrderCreated",
      "orderId": "123"
    }

    Consumer must call back
    to get order details
    end note
}

rectangle "Event-Carried State Transfer" as state #C8E6C9 {
    note as n2
    {
      "type": "OrderCreated",
      "orderId": "123",
      "customerId": "456",
      "items": [...],
      "total": 99.99,
      "shippingAddress": {...}
    }

    Consumer has all needed data
    No callback required
    end note
}
@enduml
```

| Aspect | Event Notification | Event-Carried State |
|--------|-------------------|---------------------|
| Message size | Small | Large |
| Coupling | Higher (callback needed) | Lower (self-contained) |
| Freshness | Always current | Point-in-time snapshot |
| Consumer complexity | Higher | Lower |
| Producer complexity | Lower | Higher |

**Recommendation:** Prefer event-carried state transfer for microservices to reduce runtime coupling.

---

## Anti-Patterns

### Kafka as Synchronous RPC

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Anti-Pattern: Kafka as RPC

rectangle "Service A" as a #FFCDD2
rectangle "Service B" as b #FFCDD2
queue "Kafka" as k

a -> k : Request
k -> b : Process
b -> k : Response
k -> a : Wait for response

note bottom of k
Problems:
- High latency (100ms+ vs 10ms HTTP)
- Complex error handling
- Timeout management difficult
- Resource waste while waiting

Use HTTP/gRPC for sync calls
end note
@enduml
```

### Topic Proliferation

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Anti-Pattern: Topic Proliferation

rectangle "Problematic" as bad #FFCDD2 {
    queue "orders.created" as t1
    queue "orders.updated" as t2
    queue "orders.shipped" as t3
    queue "orders.delivered" as t4
    queue "orders.cancelled" as t5
    queue "orders.refunded" as t6
}

rectangle "Better" as good #C8E6C9 {
    queue "orders.events\n(event type in payload)" as t7
}

note bottom of bad
100s of topics = operational burden:
- Monitoring complexity
- ACL management
- Consumer group sprawl
end note

note bottom of good
Single topic, multiple event types:
- Ordered within partition
- Simpler operations
- Event type filtering in consumer
end note
@enduml
```

### Distributed Monolith

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Anti-Pattern: Distributed Monolith

rectangle "Service A" as a #FFCDD2
rectangle "Service B" as b #FFCDD2
rectangle "Service C" as c #FFCDD2
queue "Kafka" as k

a --> k
k --> b : Must process\nbefore C can start
b --> k
k --> c : Sequential\ndependency

note bottom
If services must process in strict order
and cannot function independently,
Kafka adds complexity without benefit.

Consider: Is this really microservices,
or a monolith with network hops?
end note
@enduml
```

---

## Operational Considerations

### Consumer Lag Monitoring Per Service

```yaml
# Prometheus alerts per service
groups:
  - name: kafka-consumer-lag
    rules:
      - alert: OrderServiceConsumerLag
        expr: kafka_consumer_group_lag{group="order-service"} > 10000
        for: 5m
        labels:
          service: order-service
          severity: warning

      - alert: NotificationServiceConsumerLag
        expr: kafka_consumer_group_lag{group="notification-service"} > 50000
        for: 10m
        labels:
          service: notification-service
          severity: warning
```

### Service-Level Topic ACLs

```bash
# Order service can produce to its own topics
kafka-acls.sh --add --allow-principal User:order-service \
    --producer --topic 'orders.*'

# Order service can consume from payment events
kafka-acls.sh --add --allow-principal User:order-service \
    --consumer --topic 'payments.events' --group 'order-service'

# Deny order service access to other service topics
kafka-acls.sh --add --deny-principal User:order-service \
    --producer --topic 'inventory.*'
```

### Circuit Breaker for Kafka Consumers

```java
@Component
public class ResilientKafkaConsumer {

    private final CircuitBreaker circuitBreaker = CircuitBreaker.ofDefaults("kafka-consumer");

    @KafkaListener(topics = "orders.events")
    public void consume(ConsumerRecord<String, OrderEvent> record) {
        circuitBreaker.executeRunnable(() -> {
            processEvent(record.value());
        });
    }

    private void processEvent(OrderEvent event) {
        // Call downstream service
        // If downstream fails repeatedly, circuit opens
        // Consumer pauses processing (backpressure)
    }
}
```

---

## Summary

| Concern | Recommendation |
|---------|----------------|
| Topic ownership | Per-service topics with clear naming conventions |
| Consumer groups | One group per service; multiple groups for different processing needs |
| Schema governance | Schema registry with BACKWARD compatibility; producing service owns schema |
| Tracing | Propagate trace context via headers; use standard correlation IDs |
| Deployment | Cooperative rebalancing; blue/green for zero-downtime |
| Communication | Event-carried state transfer; avoid Kafka for sync RPC |

---

## Related Documentation

- [Event Collaboration](event-collaboration.md) - Inter-service event patterns
- [Saga Pattern](saga.md) - Distributed transactions
- [Outbox Pattern](outbox.md) - Reliable event publishing
- [CQRS](cqrs.md) - Separating read and write models