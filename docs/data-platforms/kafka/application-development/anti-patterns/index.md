---
title: "Kafka Anti-Patterns"
description: "Common Apache Kafka mistakes and anti-patterns to avoid. Producer, consumer, topic design, and operational pitfalls with solutions."
meta:
  - name: keywords
    content: "Kafka anti-patterns, Kafka mistakes, Kafka best practices, common Kafka errors, Kafka pitfalls"
search:
  boost: 3
---

# Kafka Anti-Patterns

This section documents common mistakes in Kafka application development and operations. Avoiding these anti-patterns improves reliability, performance, and maintainability.

---

## Producer Anti-Patterns

### Ignoring Delivery Callbacks

!!! danger "Problem"
    Fire-and-forget producing without handling delivery results loses messages silently.

    ```java
    // BAD - No delivery confirmation
    producer.send(new ProducerRecord<>("topic", "key", "value"));
    // Message may have failed, but we don't know
    ```

**Symptoms:**

- Missing messages with no errors logged
- Data inconsistency between producer and consumers
- Silent data loss during broker failures

**Solution:**

```java
// GOOD - Handle delivery callback
producer.send(new ProducerRecord<>("topic", "key", "value"), (metadata, exception) -> {
    if (exception != null) {
        log.error("Delivery failed: {}", exception.getMessage());
        handleFailure(exception);
    } else {
        log.debug("Delivered to {}:{}", metadata.partition(), metadata.offset());
    }
});
```

---

### Synchronous Sends in Hot Path

!!! danger "Problem"
    Calling `.get()` on every send blocks the producer thread, destroying throughput.

    ```java
    // BAD - Blocking on every send
    for (Order order : orders) {
        producer.send(record).get();  // Blocks until acknowledged
    }
    // 1000 messages at 5ms latency = 5 seconds total
    ```

**Symptoms:**

- Very low producer throughput
- High latency for batch operations
- Thread pool exhaustion in concurrent applications

**Solution:**

```java
// GOOD - Async with callback
List<Future<RecordMetadata>> futures = new ArrayList<>();
for (Order order : orders) {
    futures.add(producer.send(record, callback));
}
producer.flush();  // Wait for batch
// Optionally verify futures
```

---

### Unbounded Message Sizes

!!! danger "Problem"
    Sending arbitrarily large messages without limits causes broker and consumer problems.

    ```java
    // BAD - No size checking
    String largePayload = fetchEntireDatabase();  // 500MB
    producer.send(new ProducerRecord<>("topic", largePayload));
    ```

**Symptoms:**

- `RecordTooLargeException` errors
- Broker memory pressure
- Consumer processing timeouts
- Uneven partition sizes

**Solution:**

```java
// GOOD - Validate and handle large data
private static final int MAX_MESSAGE_SIZE = 1_000_000;  // 1MB

public void sendOrder(Order order) {
    byte[] serialized = serialize(order);

    if (serialized.length > MAX_MESSAGE_SIZE) {
        // Option 1: Compress
        byte[] compressed = compress(serialized);
        if (compressed.length <= MAX_MESSAGE_SIZE) {
            sendCompressed(order.getId(), compressed);
            return;
        }

        // Option 2: Reference pattern
        String reference = storeInBlobStorage(serialized);
        sendReference(order.getId(), reference);
        return;
    }

    producer.send(new ProducerRecord<>("orders", order.getId(), serialized));
}
```

---

### Single Producer Instance Bottleneck

!!! danger "Problem"
    Using a single shared producer limits throughput to one thread's capacity.

**Symptoms:**

- Producer cannot saturate network bandwidth
- High latency under load
- Single point of failure

**Solution:**

Producer instances are thread-safe. One producer per application is typically sufficient, but ensure proper configuration:

```java
// GOOD - Properly configured producer handles concurrency
Properties props = new Properties();
props.put("batch.size", 65536);           // Larger batches
props.put("linger.ms", 10);               // Wait for batches
props.put("buffer.memory", 67108864);     // 64MB buffer
props.put("max.in.flight.requests.per.connection", 5);

// For extreme throughput, multiple producers with separate threads
ExecutorService executor = Executors.newFixedThreadPool(4);
List<Producer<String, String>> producers = IntStream.range(0, 4)
    .mapToObj(i -> new KafkaProducer<>(props))
    .toList();
```

---

## Consumer Anti-Patterns

### Processing Without Committing

!!! danger "Problem"
    Processing messages without committing offsets causes reprocessing after restarts.

    ```java
    // BAD - Never commits
    while (true) {
        ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
        for (ConsumerRecord<String, String> record : records) {
            process(record);  // Processed but offset not committed
        }
    }
    // On restart: reprocesses everything from last committed offset
    ```

**Symptoms:**

- Duplicate processing after restarts
- Unbounded reprocessing
- Inconsistent state

**Solution:**

```java
// GOOD - Commit after processing
while (true) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    for (ConsumerRecord<String, String> record : records) {
        process(record);
    }
    consumer.commitSync();  // Or commitAsync with callback
}
```

---

### Committing Before Processing

!!! danger "Problem"
    Committing offsets before processing loses messages on failures.

    ```java
    // BAD - Commits before processing
    while (true) {
        ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
        consumer.commitSync();  // Committed!

        for (ConsumerRecord<String, String> record : records) {
            process(record);  // Crash here = messages lost
        }
    }
    ```

**Symptoms:**

- Data loss on consumer crashes
- Inconsistent processing
- Missing events

**Solution:**

```java
// GOOD - Commit after successful processing
while (true) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    for (ConsumerRecord<String, String> record : records) {
        process(record);
    }
    consumer.commitSync();  // Only after processing
}
```

---

### Long Processing Without Poll

!!! danger "Problem"
    Processing for longer than `max.poll.interval.ms` causes consumer group rebalance.

    ```java
    // BAD - Long processing blocks poll
    while (true) {
        ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
        for (ConsumerRecord<String, String> record : records) {
            slowDatabaseOperation(record);  // Takes 10 minutes per record
        }
    }
    // Consumer removed from group after max.poll.interval.ms
    ```

**Symptoms:**

- Frequent rebalances
- `CommitFailedException` errors
- Duplicate processing from reassigned partitions

**Solution:**

```java
// Option 1: Increase max.poll.interval.ms and reduce batch size
props.put("max.poll.interval.ms", 600000);  // 10 minutes
props.put("max.poll.records", 10);          // Small batches

// Option 2: Process asynchronously and pause/resume
while (true) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));

    if (!records.isEmpty()) {
        consumer.pause(consumer.assignment());  // Stop fetching

        CompletableFuture<Void> processing = processAsync(records);

        while (!processing.isDone()) {
            consumer.poll(Duration.ZERO);  // Heartbeat only
            Thread.sleep(100);
        }

        consumer.commitSync();
        consumer.resume(consumer.assignment());
    }
}
```

---

### Auto-Commit with Manual Processing

!!! danger "Problem"
    Using auto-commit while processing messages asynchronously loses messages or causes duplicates.

    ```java
    // BAD - Auto-commit races with async processing
    props.put("enable.auto.commit", true);
    props.put("auto.commit.interval.ms", 5000);

    while (true) {
        ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
        for (ConsumerRecord<String, String> record : records) {
            executor.submit(() -> process(record));  // Async processing
        }
        // Auto-commit happens before async processing finishes
    }
    ```

**Symptoms:**

- Message loss when async processing fails after commit
- Duplicate processing when async processing succeeds after consumer restart

**Solution:**

```java
// GOOD - Manual commit with async processing
props.put("enable.auto.commit", false);

while (true) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    List<CompletableFuture<Void>> futures = new ArrayList<>();

    for (ConsumerRecord<String, String> record : records) {
        futures.add(CompletableFuture.runAsync(() -> process(record), executor));
    }

    // Wait for all processing to complete
    CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).join();

    // Then commit
    consumer.commitSync();
}
```

---

### Not Handling Rebalances

!!! danger "Problem"
    Ignoring rebalance events causes duplicate processing or lost progress.

    ```java
    // BAD - No rebalance handling
    consumer.subscribe(List.of("topic"));
    while (true) {
        ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
        // Process and accumulate in memory...
        // Rebalance happens - accumulated state is wrong
    }
    ```

**Symptoms:**

- Duplicate processing after rebalance
- Lost in-memory state
- Uncommitted offsets lost on revoke

**Solution:**

```java
// GOOD - Handle rebalances
consumer.subscribe(List.of("topic"), new ConsumerRebalanceListener() {
    @Override
    public void onPartitionsRevoked(Collection<TopicPartition> partitions) {
        // Flush in-flight work
        flushPendingWork();
        // Commit processed offsets
        consumer.commitSync();
    }

    @Override
    public void onPartitionsAssigned(Collection<TopicPartition> partitions) {
        // Initialize state for new partitions
        initializeState(partitions);
    }
});
```

---

## Topic Design Anti-Patterns

### Single Partition Topics

!!! danger "Problem"
    Creating topics with a single partition eliminates parallelism.

    ```bash
    # BAD - No parallelism possible
    kafka-topics.sh --create --topic events --partitions 1
    ```

**Symptoms:**

- Single consumer processes all messages
- Cannot scale consumer group
- Throughput limited to one consumer's capacity

**Solution:**

```bash
# GOOD - Enable parallelism
kafka-topics.sh --create --topic events --partitions 12

# Rule of thumb: partitions >= expected consumer instances × 2
```

---

### Too Many Partitions

!!! danger "Problem"
    Excessive partitions cause cluster overhead and ZooKeeper/KRaft pressure.

    ```bash
    # BAD - 1000 partitions for low-volume topic
    kafka-topics.sh --create --topic user-clicks --partitions 1000
    ```

**Symptoms:**

- Slow broker startup
- High memory usage
- Leader election delays
- Controller overload

**Guidelines:**

| Scenario | Recommended Partitions |
|----------|----------------------|
| Low volume (<1K msg/sec) | 6-12 |
| Medium volume (<100K msg/sec) | 12-50 |
| High volume (>100K msg/sec) | 50-200 |
| Maximum per broker | ~4000 total across all topics |

---

### Random Partition Keys

!!! danger "Problem"
    Using random or timestamp-based keys destroys ordering guarantees.

    ```java
    // BAD - Random keys scatter related events
    producer.send(new ProducerRecord<>("orders", UUID.randomUUID().toString(), orderEvent));
    // Order events for same order go to different partitions
    // Consumer sees events out of order
    ```

**Symptoms:**

- Related events processed out of order
- Stateful processing failures
- Race conditions in consumers

**Solution:**

```java
// GOOD - Use business key for ordering
producer.send(new ProducerRecord<>("orders", order.getOrderId(), orderEvent));
// All events for same order go to same partition
// Consumer processes in order
```

---

### Hot Partition Problem

!!! danger "Problem"
    Skewed key distribution causes hot partitions.

    ```java
    // BAD - Single customer generates 90% of traffic
    producer.send(new ProducerRecord<>("orders", customerId, order));
    // Partition with hot customer overloaded
    ```

**Symptoms:**

- One partition with high lag
- Uneven consumer utilization
- One consumer overwhelmed

**Solutions:**

```java
// Option 1: Compound key with random suffix
String key = customerId + "-" + (order.getSequence() % 10);

// Option 2: Custom partitioner
public class SkewAwarePartitioner implements Partitioner {
    private Set<String> hotKeys = Set.of("hot-customer-1", "hot-customer-2");

    @Override
    public int partition(String topic, Object key, byte[] keyBytes,
                         Object value, byte[] valueBytes, Cluster cluster) {
        if (hotKeys.contains(key)) {
            // Spread hot keys across partitions
            return Math.abs(key.hashCode() + ThreadLocalRandom.current().nextInt())
                   % cluster.partitionCountForTopic(topic);
        }
        return DefaultPartitioner.partition(key, cluster.partitionCountForTopic(topic));
    }
}
```

---

## Operational Anti-Patterns

### Ignoring Consumer Lag

!!! danger "Problem"
    Not monitoring consumer lag allows processing to fall behind undetected.

**Symptoms:**

- Old messages being processed
- Stale data in downstream systems
- Data retention expiring before consumption

**Solution:**

```bash
# Monitor lag regularly
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
    --describe --group my-consumer-group

# Alert when lag exceeds threshold
# Example: Alert if lag > 10000 messages or > 5 minutes
```

---

### Insufficient Retention

!!! danger "Problem"
    Setting retention too short loses data before it can be processed.

    ```properties
    # BAD - 1 hour retention
    retention.ms=3600000
    # Consumer outage > 1 hour = data loss
    ```

**Symptoms:**

- Messages expired before consumption
- Log compaction deletes needed records
- Recovery impossible after outages

**Solution:**

```properties
# GOOD - Retention based on recovery requirements
retention.ms=604800000  # 7 days

# Consider consumer lag + recovery time + safety margin
# retention = max_expected_outage + processing_time + buffer
```

---

### No Dead Letter Queue

!!! danger "Problem"
    Failing messages block processing without recovery mechanism.

    ```java
    // BAD - Fail and retry forever
    while (true) {
        try {
            process(record);
        } catch (Exception e) {
            // Stuck forever on bad message
        }
    }
    ```

**Symptoms:**

- Stuck consumers
- Infinite retry loops
- No visibility into failures

**Solution:**

```java
// GOOD - Dead letter queue pattern
int maxRetries = 3;

for (ConsumerRecord<String, String> record : records) {
    try {
        process(record);
    } catch (Exception e) {
        int attempts = getRetryCount(record);
        if (attempts >= maxRetries) {
            // Send to DLQ
            dlqProducer.send(new ProducerRecord<>("topic.dlq", record.key(), record.value()));
            log.error("Sent to DLQ after {} attempts: {}", attempts, record);
        } else {
            // Send to retry topic
            retryProducer.send(new ProducerRecord<>("topic.retry", record.key(), record.value()));
        }
    }
}
```

---

### Reprocessing Everything on Failure

!!! danger "Problem"
    Using `auto.offset.reset=earliest` without idempotency causes mass reprocessing.

    ```properties
    # Consumer crashes, offset lost, rejoins
    auto.offset.reset=earliest
    # Reprocesses entire topic from beginning
    ```

**Symptoms:**

- Hours of reprocessing after brief outage
- Duplicate data in downstream systems
- Resource exhaustion during recovery

**Solution:**

```java
// GOOD - Idempotent processing + latest offset
props.put("auto.offset.reset", "latest");  // Skip missed if needed

// Always implement idempotent processing
public void process(ConsumerRecord<String, String> record) {
    String eventId = extractEventId(record);

    if (processedEventRepository.exists(eventId)) {
        return;  // Already processed
    }

    // Process
    doProcess(record);

    // Mark as processed
    processedEventRepository.save(eventId);
}
```

---

## Serialization Anti-Patterns

### No Schema Enforcement

!!! danger "Problem"
    Producing JSON without schema allows incompatible changes.

    ```java
    // Version 1
    {"userId": "123", "name": "John"}

    // Version 2 - Breaking change, no validation
    {"user_id": 123, "fullName": "John Doe"}
    // Consumer fails: field not found
    ```

**Symptoms:**

- Consumer deserialization failures
- Silent data corruption
- Difficult debugging

**Solution:**

Use Schema Registry with Avro, Protobuf, or JSON Schema:

```java
// GOOD - Schema-enforced serialization
props.put("value.serializer", KafkaAvroSerializer.class);
props.put("schema.registry.url", "http://schema-registry:8081");

// Schema Registry enforces compatibility rules
// Breaking changes are rejected at produce time
```

---

### Large Serialized Objects

!!! danger "Problem"
    Serializing entire object graphs creates huge messages.

    ```java
    // BAD - Serialize entire object graph
    Order order = orderRepository.findById(orderId);
    // order.customer.orders.items.product.category... = 50MB
    producer.send(new ProducerRecord<>("orders", order));
    ```

**Symptoms:**

- Large message errors
- Slow serialization
- High network usage

**Solution:**

```java
// GOOD - Purpose-built event with only needed data
OrderCreatedEvent event = OrderCreatedEvent.builder()
    .orderId(order.getId())
    .customerId(order.getCustomer().getId())
    .items(order.getItems().stream()
        .map(i -> new OrderItemDto(i.getProductId(), i.getQuantity()))
        .toList())
    .total(order.getTotal())
    .build();

producer.send(new ProducerRecord<>("order-events", event));
```

---

## Summary

| Category | Anti-Pattern | Solution |
|----------|--------------|----------|
| **Producer** | Ignoring callbacks | Always handle delivery results |
| **Producer** | Sync sends in loop | Use async with flush |
| **Producer** | Unbounded messages | Validate size, use reference pattern |
| **Consumer** | No commits | Commit after processing |
| **Consumer** | Commit before process | Commit only after success |
| **Consumer** | Long processing | Tune timeouts, process async |
| **Consumer** | Auto-commit + async | Manual commit with async |
| **Topic** | Single partition | Use appropriate partition count |
| **Topic** | Too many partitions | Follow guidelines per broker |
| **Topic** | Random keys | Use business keys |
| **Operations** | No lag monitoring | Monitor and alert on lag |
| **Operations** | Short retention | Retention >= max outage + buffer |
| **Operations** | No DLQ | Implement dead letter pattern |
| **Serialization** | No schema | Use Schema Registry |

---

## Related Documentation

- [Producer Development](../producers/index.md) - Correct producer patterns
- [Consumer Development](../consumers/index.md) - Correct consumer patterns
- [Design Patterns](../patterns/index.md) - Recommended architectural patterns
- [Troubleshooting](../../troubleshooting/index.md) - Diagnosing problems
