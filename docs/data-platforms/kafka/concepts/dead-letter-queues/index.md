---
title: "Dead Letter Queues"
description: "Dead Letter Queue concepts for Apache Kafka. Understanding poison messages, error isolation, retry strategies, and DLQ patterns for building resilient event-driven systems."
meta:
  - name: keywords
    content: "Kafka dead letter queue, DLQ, poison message, error handling, retry pattern, Kafka error topic"
---

# Dead Letter Queues

A Dead Letter Queue (DLQ) is a separate topic that stores messages which cannot be processed successfully. Rather than blocking the consumer, losing the message, or retrying indefinitely, failed messages are moved to the DLQ for later analysis and reprocessing.

Kafka does not provide built-in DLQ functionality—it is an application-level pattern that must be implemented by producers or consumers. This follows Kafka's "dumb broker, smart consumer" architecture where error handling responsibility lies with client applications rather than the broker.

---

## Kafka DLQ vs Traditional Message Brokers

Traditional message brokers (JMS, RabbitMQ, IBM MQ) provide built-in DLQ functionality, typically routing messages based on:

- **TTL expiration** - message exceeded time-to-live
- **Delivery failures** - maximum delivery attempts exceeded
- **Queue capacity** - destination queue full

Kafka DLQs serve a different purpose. Since Kafka retains messages regardless of consumption and consumers control their own offsets, DLQs in Kafka primarily address:

- **Invalid message format** - deserialization failures, schema mismatches
- **Bad message content** - validation errors, missing required fields
- **Processing failures** - business logic exceptions, dependency errors

This distinction is important: Kafka DLQs are about **message quality**, not delivery mechanics.

---

## The Problem: Poison Messages

A poison message is a message that causes consumer failure repeatedly. Without proper handling, a single poison message can halt an entire consumer group.

```plantuml
@startuml
skinparam backgroundColor transparent

participant "Producer" as prod
queue "orders" as topic
participant "Consumer" as cons
database "Database" as db

prod -> topic : Order message
topic -> cons : Deliver message

cons -> cons : Parse message
cons -> cons : **FAIL** Deserialization fails

cons -> topic : Don't commit offset
topic -> cons : Redeliver same message

cons -> cons : **FAIL** Fails again

note over cons, topic
  Infinite loop: consumer stuck
  on poison message forever.
  No progress on partition.
end note

@enduml
```

### Common Causes of Poison Messages

| Cause | Description |
|-------|-------------|
| **Schema mismatch** | Producer schema incompatible with consumer's deserializer |
| **Corrupt data** | Malformed JSON, invalid Avro, truncated payload |
| **Business validation** | Data fails domain validation (negative price, invalid date) |
| **Missing dependencies** | Referenced entity doesn't exist in database |
| **Transient failures** | Database timeout, network error (may succeed on retry) |
| **Code bugs** | Consumer code throws exception for certain data patterns |

---

## DLQ Pattern

The DLQ pattern isolates failed messages so healthy messages continue processing.

```plantuml
@startuml
skinparam backgroundColor transparent

participant "Producer" as prod
queue "orders" as topic
participant "Consumer" as cons
queue "orders.dlq" as dlq
database "Database" as db

prod -> topic : Order message
topic -> cons : Deliver message

cons -> cons : Parse message
cons -> cons : **FAIL** Processing fails

cons -> dlq : Send to DLQ\n(with error metadata)
cons -> topic : Commit offset\n(move past poison message)

topic -> cons : Next message
cons -> db : Process successfully
cons -> topic : Commit offset

note over dlq
  DLQ contains:
  - Original message
  - Error details
  - Retry count
  - Timestamp
end note

@enduml
```

### DLQ Benefits

| Benefit | Description |
|---------|-------------|
| **Fault isolation** | One bad message doesn't block partition processing |
| **No data loss** | Failed messages preserved for analysis and reprocessing |
| **Visibility** | DLQ depth indicates system health issues |
| **Debugging** | Failed messages available for root cause analysis |
| **Controlled retry** | Messages can be reprocessed after fixes deployed |

---

## DLQ Architecture

### Basic DLQ Topology

```plantuml
@startuml
skinparam backgroundColor transparent

rectangle "Production Flow" {
    queue "orders" as main
    rectangle "Order\nConsumer" as cons
    database "Order DB" as db
}

rectangle "Error Flow" {
    queue "orders.dlq" as dlq
    rectangle "DLQ\nProcessor" as dlq_proc
    rectangle "Alert\nService" as alert
}

main --> cons : Normal processing
cons --> db : Success
cons --> dlq : Failure

dlq --> dlq_proc : Analyze failures
dlq_proc --> alert : Trigger alerts
dlq_proc --> main : Reprocess\n(after fix)

note bottom of dlq
  DLQ naming convention:
  {original-topic}.dlq
  or
  {original-topic}.dead-letter
end note

@enduml
```

### Multi-Stage DLQ (Retry Tiers)

For transient failures, implement multiple retry stages before final DLQ:

```plantuml
@startuml
skinparam backgroundColor transparent

queue "orders" as main
queue "orders.retry-1" as r1
queue "orders.retry-2" as r2
queue "orders.dlq" as dlq
rectangle "Consumer" as cons

main --> cons : Process
cons --> r1 : Fail (attempt 1)

r1 --> cons : Retry after 1 min
cons --> r2 : Fail (attempt 2)

r2 --> cons : Retry after 5 min
cons --> dlq : Fail (attempt 3)\nPermanent failure

note bottom of r1
  Retry topics use delayed
  consumption or time-based
  partition assignment
end note

note bottom of dlq
  DLQ: requires manual
  intervention or code fix
end note

@enduml
```

### Retry Timing Strategies

| Strategy | Implementation | Use Case |
|----------|----------------|----------|
| **Immediate retry** | Consumer retries N times in-memory | Transient network glitches |
| **Delayed retry** | Separate retry topics with consumer pause | Rate limiting, backpressure |
| **Exponential backoff** | Increasing delays (1s, 5s, 30s, 5m) | External service recovery |
| **Scheduled retry** | Time-windowed reprocessing | Batch reconciliation |

### DLQ Topic Strategy

Organizations must decide between dedicated DLQs per topic or a unified DLQ.

| Strategy | Approach | Trade-offs |
|----------|----------|------------|
| **Per-topic DLQ** | `orders.dlq`, `payments.dlq`, `users.dlq` | Targeted analysis, clear ownership; more topics to manage |
| **Unified DLQ** | Single `application.dlq` for all topics | Simpler operations, single dashboard; harder root cause analysis |
| **Per-service DLQ** | `order-service.dlq` handles multiple input topics | Balanced approach; requires header-based routing |

Most production deployments use per-topic DLQs for clear ownership and targeted alerting.

### DLQ Storage Options

DLQ messages can remain in Kafka or be moved to external storage for long-term retention and analysis.

```plantuml
@startuml
skinparam backgroundColor transparent

rectangle "Kafka-Native" as kafka {
    queue "orders.dlq" as dlq1
    note bottom of dlq1
      Pros: Simple, same tooling
      Cons: Kafka storage costs
    end note
}

rectangle "Hybrid" as hybrid {
    queue "orders.dlq" as dlq2
    database "S3 Archive" as s3
    dlq2 --> s3 : Archive after 7 days
    note bottom of s3
      Pros: Cost-effective long-term
      Cons: Reprocessing complexity
    end note
}

rectangle "External" as external {
    queue "orders" as main
    database "PostgreSQL\nDLQ Table" as pg
    rectangle "Review UI" as ui
    main --> pg : On failure
    pg --> ui : Manual review
    note bottom of pg
      Pros: SQL queries, UI tooling
      Cons: Operational complexity
    end note
}

@enduml
```

| Storage | Best For | Considerations |
|---------|----------|----------------|
| **Kafka topic** | Standard use cases, automated reprocessing | Set appropriate retention; monitor disk usage |
| **S3/GCS archive** | Compliance, long-term retention | Batch reprocessing; requires ETL tooling |
| **Database (PostgreSQL)** | Manual review workflows, complex remediation | Enables UI/CLI tooling; additional infrastructure |

---

## DLQ Message Structure

A DLQ message should contain the original message plus metadata for debugging and reprocessing.

```plantuml
@startuml
skinparam backgroundColor transparent

rectangle "DLQ Message" {
    rectangle "Headers" as headers {
        card "dlq.original.topic: orders" as h1
        card "dlq.original.partition: 3" as h2
        card "dlq.original.offset: 12847" as h3
        card "dlq.original.timestamp: 1705..." as h4
        card "dlq.error.message: NPE at..." as h5
        card "dlq.error.class: NullPointer..." as h6
        card "dlq.retry.count: 3" as h7
        card "dlq.consumer.group: order-svc" as h8
    }

    rectangle "Key" as key {
        card "order-123" as k1
    }

    rectangle "Value" as value {
        card "Original message payload\n(unchanged)" as v1
    }
}

@enduml
```

### Standard DLQ Headers

| Header | Purpose |
|--------|---------|
| `dlq.original.topic` | Source topic name |
| `dlq.original.partition` | Source partition |
| `dlq.original.offset` | Source offset (for replay tracking) |
| `dlq.original.timestamp` | Original message timestamp |
| `dlq.original.key` | Original message key (if key changed) |
| `dlq.error.message` | Exception message |
| `dlq.error.class` | Exception class name |
| `dlq.error.stacktrace` | Stack trace (optional, can be large) |
| `dlq.retry.count` | Number of processing attempts |
| `dlq.failed.timestamp` | When message was sent to DLQ |
| `dlq.consumer.group` | Consumer group that failed |
| `dlq.consumer.instance` | Specific consumer instance |

---

## Error Classification

Not all errors should go to the DLQ. Classify errors to determine the appropriate handling strategy.

```plantuml
@startuml
skinparam backgroundColor transparent

start
:Message processing\nfails;

if (Transient error?) then (yes)
    :Retry with backoff;
    if (Max retries exceeded?) then (yes)
        :Send to DLQ;
    else (no)
        :Retry;
        stop
    endif
else (no)
    if (Recoverable with fix?) then (yes)
        :Send to DLQ;
        note right
            Code fix needed.
            Reprocess later.
        end note
    else (no)
        if (Data corruption?) then (yes)
            :Send to DLQ;
            note right
                Log and alert.
                Manual cleanup.
            end note
        else (no)
            :Log and skip;
            note right
                Truly unprocessable.
                No value in keeping.
            end note
        endif
    endif
endif

stop

@enduml
```

### Error Categories

| Category | Examples | Strategy |
|----------|----------|----------|
| **Transient** | Connection timeout, rate limit, lock contention | Retry with backoff |
| **Recoverable** | Schema mismatch, validation failure, missing reference | DLQ → fix → reprocess |
| **Corrupt** | Invalid encoding, truncated message, wrong topic | DLQ → investigate → discard |
| **Poison** | Causes crash/OOM, infinite loop trigger | DLQ → immediate alert |

---

## DLQ Topic Configuration

DLQ topics should be configured for durability and long retention since messages may need reprocessing weeks later.

### Recommended Settings

```properties
# DLQ topic configuration
cleanup.policy=delete
retention.ms=2592000000        # 30 days (longer than main topics)
retention.bytes=-1             # No size limit
min.insync.replicas=2          # Durability
replication.factor=3           # Durability
compression.type=producer      # Preserve original compression
```

### Partitioning Strategy

| Strategy | Approach | Trade-off |
|----------|----------|-----------|
| **Single partition** | All DLQ messages in one partition | Simple, ordered review; limited throughput |
| **Match source** | Same partition count as source topic | Preserves key locality; complex reprocessing |
| **By error type** | Partition by error category | Easy triage; custom partitioner needed |
| **Round-robin** | Default partitioning | Balanced load; no ordering |

---

## DLQ vs Alternatives

### Comparison with Other Patterns

```plantuml
@startuml
skinparam backgroundColor transparent

rectangle "Error Handling Approaches" {

    rectangle "Retry In-Place" as retry {
        card "Pros: Simple" as r1
        card "Cons: Blocks partition" as r2
    }

    rectangle "Skip and Log" as skip {
        card "Pros: No blocking" as s1
        card "Cons: Data loss" as s2
    }

    rectangle "Dead Letter Queue" as dlq {
        card "Pros: No blocking,\nno data loss" as d1
        card "Cons: Complexity,\nextra topics" as d2
    }

    rectangle "Parking Lot" as park {
        card "Pros: Human review" as p1
        card "Cons: Manual process" as p2
    }
}

@enduml
```

| Approach | Blocking | Data Loss | Complexity | Best For |
|----------|----------|-----------|------------|----------|
| **Retry in-place** | Yes | No | Low | Transient errors only |
| **Skip and log** | No | Yes | Low | Non-critical data |
| **DLQ** | No | No | Medium | Production systems |
| **Parking lot** | No | No | High | Compliance, finance |

---

## Preventing DLQ Messages

The best DLQ strategy is minimizing messages that reach it. Schema Registry provides producer-side validation that catches bad messages before they enter Kafka.

```plantuml
@startuml
skinparam backgroundColor transparent

participant "Producer" as prod
participant "Schema Registry" as sr
queue "orders" as topic
participant "Consumer" as cons
queue "orders.dlq" as dlq

prod -> sr : Validate schema
alt Schema valid
    sr -> prod : OK
    prod -> topic : Send message
    topic -> cons : Consume
    cons -> cons : Process successfully
else Schema invalid
    sr -> prod : Reject
    prod -> prod : Handle error\nat source
    note right of prod
      Bad message never
      enters Kafka.
      No DLQ needed.
    end note
end

@enduml
```

### Prevention Strategies

| Strategy | Implementation | Effectiveness |
|----------|----------------|---------------|
| **Schema Registry** | Enforce Avro/Protobuf/JSON Schema at producer | Catches format errors before Kafka |
| **Producer validation** | Validate business rules before send | Catches domain errors at source |
| **Contract testing** | Verify producer/consumer compatibility in CI | Catches schema drift before deployment |
| **Input sanitization** | Clean/normalize data at ingestion boundary | Reduces malformed data |

Prevention reduces DLQ volume but cannot eliminate it entirely—runtime failures, dependency issues, and edge cases still require DLQ handling.

---

## When to Use DLQs

### Good Candidates

- Order processing where every message must be accounted for
- Financial transactions requiring audit trails
- Event sourcing where event loss corrupts state
- Multi-tenant systems where one tenant's bad data shouldn't affect others
- Integration pipelines where upstream data quality varies

### Poor Candidates

- Metrics/telemetry where occasional loss is acceptable
- Cache invalidation events (stale cache self-corrects)
- Heartbeats/health checks
- High-volume logs where DLQ would be overwhelmed

---

## DLQ Anti-Patterns

### Anti-Pattern: DLQ as Primary Error Handling

```plantuml
@startuml
skinparam backgroundColor transparent

rectangle "Anti-Pattern" as bad #FFCDD2 {
    queue "orders" as main1
    rectangle "Consumer\n(no retry logic)" as cons1
    queue "orders.dlq" as dlq1

    main1 --> cons1
    cons1 --> dlq1 : Any error\ngoes to DLQ
}

rectangle "Correct Pattern" as good #C8E6C9 {
    queue "orders" as main2
    rectangle "Consumer\n(retry + classify)" as cons2
    queue "orders.retry" as retry2
    queue "orders.dlq" as dlq2

    main2 --> cons2
    cons2 --> retry2 : Transient\nerrors
    retry2 --> cons2
    cons2 --> dlq2 : Permanent\nfailures only
}

bad -[hidden]down- good

@enduml
```

### Common Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| **No retry before DLQ** | Transient errors flood DLQ | Implement retry with backoff |
| **DLQ without monitoring** | Silent failures accumulate | Alert on DLQ depth |
| **No reprocessing plan** | DLQ becomes data graveyard | Build reprocessing tooling |
| **Infinite retry** | Poison messages never reach DLQ | Set max retry limit |
| **Losing error context** | Can't debug failures | Include error metadata in headers |
| **Same retention as source** | DLQ expires before review | Longer DLQ retention |
| **DLQ for backpressure** | Using DLQ to handle load spikes | Scale consumers or use quotas |
| **Connection errors to DLQ** | Network timeouts sent to DLQ | Retry in application; fix connectivity |
| **No DLQ ownership** | Nobody reviews DLQ messages | Assign data owners, not just infrastructure |
| **Ignoring DLQ entirely** | Messages accumulate indefinitely | Process or archive with defined SLA |

---

## DLQ Ownership

Effective DLQ management requires clear ownership and defined processes.

### Responsibility Model

| Role | Responsibility |
|------|----------------|
| **Data owner** | Review failed messages, determine if data fix needed |
| **Development team** | Fix code bugs causing failures, deploy fixes |
| **Operations** | Monitor DLQ depth, trigger alerts, manage retention |
| **Platform team** | Provide reprocessing tooling, maintain DLQ infrastructure |

### Process Considerations

- **SLA for review** - define maximum time messages can remain in DLQ unreviewed
- **Escalation path** - who gets notified when DLQ depth exceeds thresholds
- **Reprocessing authority** - who can trigger replay of DLQ messages
- **Discard policy** - criteria for permanently discarding unrecoverable messages

---

## Related Documentation

- [Error Handling Implementation](../../application-development/error-handling/dead-letter-queues.md) - Code patterns and implementation
- [DLQ Operations](../../operations/troubleshooting/dead-letter-queues.md) - Monitoring, alerting, and reprocessing
- [Schema Registry](../../schema-registry/index.md) - Producer-side validation to prevent bad messages
- [Delivery Semantics](../delivery-semantics/index.md) - At-least-once and exactly-once processing
- [Consumer Error Handling](../../application-development/consumers/index.md) - Consumer-side error strategies