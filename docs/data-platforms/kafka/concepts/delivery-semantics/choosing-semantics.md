---
title: "Choosing Delivery Semantics"
description: "Guide to selecting appropriate Kafka delivery semantics. Decision framework, use case analysis, and migration strategies."
---

# Choosing Delivery Semantics

Selecting the appropriate delivery semantic involves balancing reliability requirements against performance and complexity costs. This document provides a decision framework for choosing between at-most-once, at-least-once, and exactly-once semantics.

---

## Decision Framework

### Primary Decision Tree

```plantuml
@startuml

skinparam backgroundColor transparent

start

:Evaluate data criticality;

if (Data loss acceptable?) then (yes)
    if (High throughput priority?) then (yes)
        :At-Most-Once;
        note right
          Telemetry
          Logs
          Metrics
        end note
        stop
    else (no)
        :At-Least-Once\n(simple config);
        stop
    endif
else (no)
    if (Duplicates acceptable?) then (yes)
        :At-Least-Once +\nIdempotent Consumer;
        note right
          Most production
          workloads
        end note
        stop
    else (no)
        if (Kafka-to-Kafka only?) then (yes)
            :Exactly-Once;
            note right
              Kafka Streams
              Internal pipelines
            end note
            stop
        else (no)
            if (External system\nidempotent?) then (yes)
                :At-Least-Once +\nIdempotent Sink;
                stop
            else (no)
                :At-Least-Once +\nDeduplication Layer;
                note right
                  Add dedup table
                  or outbox pattern
                end note
                stop
            endif
        endif
    endif
endif

@enduml
```

### Decision Matrix

| Requirement | At-Most-Once | At-Least-Once | Exactly-Once |
|-------------|:------------:|:-------------:|:------------:|
| No data loss | ❌ | ✅ | ✅ |
| No duplicates | ✅ | ❌ | ✅ |
| High throughput | ✅ | ✅ | ⚠️ |
| Low latency | ✅ | ✅ | ⚠️ |
| Simple implementation | ✅ | ✅ | ❌ |
| Kafka-only | ✅ | ✅ | ✅ |
| External systems | ✅ | ✅ | ⚠️ |

**Legend:** ✅ Supported | ⚠️ With constraints | ❌ Not supported

---

## Use Case Analysis

### At-Most-Once Use Cases

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "At-Most-Once Suitable" #lightgreen {
    rectangle "Telemetry" as tel {
        card "IoT sensors" as t1
        card "Application metrics" as t2
        card "Health checks" as t3
    }

    rectangle "Logging" as log {
        card "Application logs" as l1
        card "Access logs" as l2
        card "Debug traces" as l3
    }

    rectangle "Real-time Updates" as rt {
        card "Game state" as r1
        card "Location tracking" as r2
        card "Price feeds" as r3
    }
}

note bottom of tel
  High volume
  Individual loss acceptable
  Aggregates matter
end note

note bottom of rt
  Stale data worse
  than missing data
end note

@enduml
```

| Use Case | Why At-Most-Once |
|----------|------------------|
| **IoT telemetry** | 1M+ msgs/sec; individual readings expendable |
| **Application metrics** | Statistical accuracy preserved with 99.9% delivery |
| **Real-time gaming** | Next update arrives in milliseconds |
| **Log streaming** | Missing log lines rarely impact debugging |

### At-Least-Once Use Cases

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "At-Least-Once Suitable" #lightyellow {
    rectangle "Business Events" as bus {
        card "Order placed" as b1
        card "User registered" as b2
        card "Payment initiated" as b3
    }

    rectangle "Data Pipelines" as dp {
        card "ETL processes" as d1
        card "Data warehousing" as d2
        card "Analytics ingestion" as d3
    }

    rectangle "Notifications" as notif {
        card "Email triggers" as n1
        card "Push notifications" as n2
        card "Webhook delivery" as n3
    }
}

note bottom of bus
  Cannot lose events
  Duplicates handled
  by idempotent design
end note

@enduml
```

| Use Case | Why At-Least-Once | Duplicate Handling |
|----------|-------------------|-------------------|
| **Order processing** | Orders must not be lost | Order ID deduplication |
| **User events** | User actions must be captured | Event ID + timestamp |
| **Financial transactions** | Money movement must be recorded | Transaction ID |
| **Email notifications** | Users must receive communications | Email dedup by user+type |

### Exactly-Once Use Cases

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Exactly-Once Required" #lightpink {
    rectangle "Stream Processing" as sp {
        card "Kafka Streams aggregations" as s1
        card "Stateful transformations" as s2
        card "Window computations" as s3
    }

    rectangle "Financial Calculations" as fin {
        card "Balance computations" as f1
        card "Portfolio valuation" as f2
        card "Risk calculations" as f3
    }

    rectangle "Billing/Metering" as bill {
        card "Usage counting" as m1
        card "API call metering" as m2
        card "Resource consumption" as m3
    }
}

note bottom of sp
  Aggregates must be
  exactly correct
end note

note bottom of fin
  Duplicate transactions
  = incorrect balances
end note

@enduml
```

| Use Case | Why Exactly-Once | Alternative |
|----------|------------------|-------------|
| **Kafka Streams aggregates** | SUM/COUNT must be exact | None (use EOS) |
| **Balance calculations** | Duplicate credits/debits cause errors | Strong idempotency |
| **Usage metering** | Billing must be accurate | Dedup with strong guarantees |
| **Vote counting** | Each vote counted once | Dedup table with unique constraint |

---

## Semantic Selection by Data Type

### Classification Guide

| Data Type | Typical Semantic | Rationale |
|-----------|------------------|-----------|
| **Metrics/telemetry** | At-most-once | Volume, expendability |
| **Logs** | At-most-once | Volume, non-critical |
| **User activity** | At-least-once | Cannot lose, naturally deduped |
| **Business transactions** | At-least-once | Critical, idempotent design |
| **Financial records** | Exactly-once or strong at-least-once | Accuracy critical |
| **Aggregated state** | Exactly-once | Correctness required |

### Data Criticality Assessment

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Data Criticality Spectrum" {
    rectangle "Low Criticality" as low #lightgreen {
        card "Debug logs" as l1
        card "Heartbeats" as l2
        card "Cache warmers" as l3
    }

    rectangle "Medium Criticality" as med #lightyellow {
        card "Analytics events" as m1
        card "User clicks" as m2
        card "Search queries" as m3
    }

    rectangle "High Criticality" as high #lightpink {
        card "Orders" as h1
        card "Payments" as h2
        card "Audit logs" as h3
    }

    low -right-> med : At-Most-Once\nto At-Least-Once
    med -right-> high : At-Least-Once\nto Exactly-Once
}

@enduml
```

---

## Cost-Benefit Analysis

### Performance Cost

| Semantic | Latency Overhead | Throughput Impact | Resource Usage |
|----------|:----------------:|:-----------------:|:--------------:|
| At-most-once | Baseline | 100% | Low |
| At-least-once | +5-10ms | 90-95% | Medium |
| Exactly-once | +15-50ms | 50-70% | High |

### Implementation Cost

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Implementation Complexity" {
    rectangle "At-Most-Once" as amo {
        card "Producer: acks=0" as a1
        card "Consumer: commit first" as a2
        card "Monitoring: basic" as a3
    }

    rectangle "At-Least-Once" as alo {
        card "Producer: acks=all, retries" as b1
        card "Consumer: process first" as b2
        card "Dedup: idempotent design" as b3
        card "Monitoring: duplicates" as b4
    }

    rectangle "Exactly-Once" as eos {
        card "Producer: transactional" as c1
        card "Consumer: read_committed" as c2
        card "Coordination: complex" as c3
        card "Error handling: extensive" as c4
        card "Monitoring: transactions" as c5
    }
}

@enduml
```

| Aspect | At-Most-Once | At-Least-Once | Exactly-Once |
|--------|:------------:|:-------------:|:------------:|
| **Code complexity** | Simple | Moderate | Complex |
| **Testing effort** | Low | Medium | High |
| **Debugging difficulty** | Easy | Moderate | Challenging |
| **Operational overhead** | Low | Medium | High |

### Total Cost of Ownership

| Semantic | Development | Operations | Infrastructure |
|----------|:-----------:|:----------:|:--------------:|
| At-most-once | Low | Low | Low |
| At-least-once | Medium | Medium | Medium |
| Exactly-once | High | High | High |

---

## Migration Strategies

### Upgrading Semantics

```plantuml
@startuml

skinparam backgroundColor transparent

state "At-Most-Once" as AMO
state "At-Least-Once" as ALO
state "Exactly-Once" as EOS

AMO --> ALO : Enable acks, retries
ALO --> EOS : Enable transactions

note right of AMO
  acks=0
  retries=0
end note

note right of ALO
  acks=all
  retries=MAX
  idempotent consumer
end note

note right of EOS
  transactional.id
  read_committed
end note

@enduml
```

### At-Most-Once → At-Least-Once

**Producer changes:**
```properties
# Before
acks=0
retries=0

# After
acks=all
retries=2147483647
enable.idempotence=true
```

**Consumer changes:**
```java
// Before: commit first
consumer.poll(timeout);
consumer.commitSync();
for (record : records) process(record);

// After: process first
consumer.poll(timeout);
for (record : records) process(record);
consumer.commitSync();
```

**Additional requirements:**
- Implement idempotent consumer logic
- Add message ID tracking or natural idempotence

### At-Least-Once → Exactly-Once

**Producer changes:**
```properties
# Before
acks=all
enable.idempotence=true

# After
acks=all
enable.idempotence=true
transactional.id=my-app-instance-1
```

**Consumer changes:**
```properties
# Before
enable.auto.commit=false

# After
enable.auto.commit=false
isolation.level=read_committed
```

**Code changes:**
```java
// Before
for (record : records) {
    process(record);
    producer.send(output);
}
consumer.commitSync();

// After
producer.initTransactions();

producer.beginTransaction();
for (record : records) {
    process(record);
    producer.send(output);
}
producer.sendOffsetsToTransaction(offsets, consumer.groupMetadata());
producer.commitTransaction();
```

---

## Hybrid Approaches

### Topic-Level Semantics

Different topics may require different semantics within the same application.

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Multi-Semantic Application" {
    rectangle "Application" as app

    rectangle "Topics" as topics {
        rectangle "metrics-topic\n(at-most-once)" as t1 #lightgreen
        rectangle "orders-topic\n(at-least-once)" as t2 #lightyellow
        rectangle "payments-topic\n(exactly-once)" as t3 #lightpink
    }

    app --> t1 : acks=0
    app --> t2 : acks=all
    app --> t3 : transactions
}

@enduml
```

```java
// Multiple producers with different configurations
Producer<String, String> metricsProducer = createProducer(acks=0);
Producer<String, String> ordersProducer = createProducer(acks=all);
Producer<String, String> paymentsProducer = createTransactionalProducer();

// Route by data type
switch (eventType) {
    case METRIC:
        metricsProducer.send(record);  // Fire and forget
        break;
    case ORDER:
        ordersProducer.send(record, callback);  // With retry
        break;
    case PAYMENT:
        paymentsProducer.beginTransaction();
        paymentsProducer.send(record);
        paymentsProducer.commitTransaction();
        break;
}
```

### Tiered Processing

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Tiered Processing" {
    rectangle "Ingestion Layer\n(at-most-once)" as ingest {
        card "High volume" as i1
        card "Quick acceptance" as i2
    }

    rectangle "Processing Layer\n(at-least-once)" as process {
        card "Validation" as p1
        card "Enrichment" as p2
    }

    rectangle "Output Layer\n(exactly-once)" as output {
        card "Aggregation" as o1
        card "Final state" as o2
    }

    ingest --> process : filter
    process --> output : transform
}

@enduml
```

---

## Anti-Patterns

### Over-Engineering

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Anti-Pattern: EOS for Logs" #pink {
    card "Application logs" as logs
    card "Exactly-once pipeline" as eos
    card "High latency" as lat
    card "Complex operations" as ops
    card "High cost" as cost

    logs --> eos
    eos --> lat
    eos --> ops
    eos --> cost
}

note bottom
  Logs don't need EOS
  At-most-once sufficient
  Massive cost/complexity overhead
end note

@enduml
```

### Under-Engineering

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Anti-Pattern: AMO for Payments" #pink {
    card "Payment events" as pay
    card "At-most-once" as amo
    card "Lost payments" as lost
    card "Customer complaints" as complaints
    card "Revenue loss" as revenue

    pay --> amo
    amo --> lost
    lost --> complaints
    lost --> revenue
}

note bottom
  Payments require at-least-once
  or exactly-once
  Data loss unacceptable
end note

@enduml
```

### Inconsistent Semantics

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Anti-Pattern: Mixed Producers" #pink {
    rectangle "Same Topic" as topic {
        card "Producer A (acks=0)" as pa
        card "Producer B (acks=all)" as pb
    }

    card "Inconsistent reliability" as inc
    card "Confusing behavior" as conf

    topic --> inc
    inc --> conf
}

note bottom
  All producers to same topic
  should use same semantics
end note

@enduml
```

---

## Decision Checklist

### Before Choosing

- [ ] What is the business impact of losing a message?
- [ ] What is the business impact of processing duplicates?
- [ ] What is the acceptable latency?
- [ ] What is the required throughput?
- [ ] Does the consumer have natural idempotence?
- [ ] Are external systems involved?
- [ ] What is the team's operational capability?

### Semantic Selection

| If... | Then use... |
|-------|-------------|
| Loss acceptable, throughput critical | At-most-once |
| Loss unacceptable, can handle duplicates | At-least-once |
| Loss and duplicates unacceptable, Kafka-only | Exactly-once |
| Loss and duplicates unacceptable, external systems | At-least-once + idempotent sink |

### Post-Selection Validation

- [ ] Performance tested under expected load
- [ ] Failure scenarios tested
- [ ] Monitoring in place for semantic violations
- [ ] Runbooks for common issues
- [ ] Team trained on operational procedures

---

## Summary Table

| Semantic | Best For | Avoid For |
|----------|----------|-----------|
| **At-most-once** | Telemetry, logs, real-time updates | Transactions, orders, critical events |
| **At-least-once** | Most business events, general purpose | When duplicates cause financial impact |
| **Exactly-once** | Aggregations, billing, financial calculations | Logs, metrics, non-critical data |

---

## Related Documentation

- [At-Most-Once](at-most-once.md) - Fire and forget patterns
- [At-Least-Once](at-least-once.md) - Retry with idempotent consumers
- [Exactly-Once](exactly-once.md) - Transactional processing
- [Delivery Semantics Overview](index.md) - Semantic definitions
