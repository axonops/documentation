---
title: "Kafka Producer Error Handling"
description: "Kafka producer error handling. Retriable vs fatal errors, timeout configuration, and failure recovery patterns."
meta:
  - name: keywords
    content: "Kafka producer error handling, delivery callback, retry, producer exception, send failure"
search:
  boost: 3
---

# Kafka Producer Error Handling

Proper error handling ensures reliable message delivery. This document covers error types, timeout configuration, and recovery patterns.

---

## Error Classification

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Producer Errors" {
    rectangle "Retriable" as ret #lightyellow {
        card "NetworkException" as r1
        card "NotEnoughReplicasException" as r2
        card "TimeoutException" as r3
    }

    rectangle "Non-Retriable" as nonret #lightpink {
        card "SerializationException" as n1
        card "RecordTooLargeException" as n2
        card "InvalidTopicException" as n3
    }

    rectangle "Fatal" as fatal #pink {
        card "ProducerFencedException" as f1
        card "OutOfOrderSequenceException" as f2
        card "AuthorizationException" as f3
    }
}

@enduml
```

| Type | Producer Behavior | Application Action |
|------|-------------------|-------------------|
| **Retriable** | Automatic retry | Wait or handle timeout |
| **Non-Retriable** | Fail immediately | Fix data or config |
| **Fatal** | Cannot recover | Close producer |

---

## Timeout Configuration

```properties
# Total time to deliver message
delivery.timeout.ms=120000

# Per-request timeout
request.timeout.ms=30000

# Retry backoff
retry.backoff.ms=100
retry.backoff.max.ms=1000
```

```plantuml
@startuml

skinparam backgroundColor transparent

concise "Timeline" as T

@0
T is "Send"

@100
T is "Retry 1"

@300
T is "Retry 2"

@700
T is "Retry 3"

@120000
T is "delivery.timeout.ms"

@enduml
```

---

## Handling Patterns

### Callback-Based

```java
producer.send(record, (metadata, exception) -> {
    if (exception == null) {
        log.info("Sent to {} @ {}", metadata.partition(), metadata.offset());
        return;
    }

    if (exception instanceof RetriableException) {
        // Already retried and failed
        log.error("Retriable error exhausted", exception);
        deadLetterQueue.send(record);
    } else if (exception instanceof SerializationException) {
        // Bad data
        log.error("Serialization failed", exception);
        metrics.increment("serialization_errors");
    } else {
        // Other error
        log.error("Send failed", exception);
        alertService.notify(exception);
    }
});
```

### Synchronous with Retry

```java
int maxRetries = 3;
for (int attempt = 0; attempt < maxRetries; attempt++) {
    try {
        RecordMetadata metadata = producer.send(record).get();
        log.info("Sent to {} @ {}", metadata.partition(), metadata.offset());
        break;
    } catch (ExecutionException e) {
        Throwable cause = e.getCause();
        if (cause instanceof RetriableException && attempt < maxRetries - 1) {
            log.warn("Retry {} of {}", attempt + 1, maxRetries);
            Thread.sleep(100 * (attempt + 1));
        } else {
            throw e;
        }
    }
}
```

---

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `TimeoutException` | Broker slow or unreachable | Check broker health, increase timeout |
| `NotEnoughReplicasException` | ISR too small | Wait for replicas to catch up |
| `RecordTooLargeException` | Message > max.request.size | Increase limit or reduce message size |
| `SerializationException` | Serializer failure | Fix serialization logic |
| `ProducerFencedException` | Another producer with same txn.id | Ensure single instance |

---

## Dead Letter Queue Pattern

```java
public void sendWithDLQ(ProducerRecord<String, String> record) {
    producer.send(record, (metadata, exception) -> {
        if (exception != null) {
            // Send to DLQ
            ProducerRecord<String, String> dlqRecord = new ProducerRecord<>(
                "dead-letter-queue",
                record.key(),
                record.value()
            );
            dlqRecord.headers()
                .add("original-topic", record.topic().getBytes())
                .add("error", exception.getMessage().getBytes());

            dlqProducer.send(dlqRecord);
        }
    });
}
```

---

## Best Practices

| Practice | Rationale |
|----------|-----------|
| Always handle callbacks | Detect delivery failures |
| Use appropriate timeouts | Balance reliability and latency |
| Log errors with context | Enable debugging |
| Implement DLQ for critical data | Prevent data loss |
| Monitor error rates | Detect systemic issues |

---

## Related Documentation

- [Producer Guide](index.md) - Producer overview
- [Configuration](configuration.md) - Timeout settings
- [Protocol Errors](../../architecture/client-connections/protocol-errors.md) - Error code reference
