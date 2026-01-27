---
title: "Kafka Java Client"
description: "Apache Kafka Java client guide. Producer, consumer, and admin client usage with configuration, error handling, and best practices."
meta:
  - name: keywords
    content: "Kafka Java client, kafka-clients, KafkaProducer, KafkaConsumer, Kafka Java API, Maven Kafka"
---

# Kafka Java Client

The official Apache Kafka Java client provides native protocol support with full feature coverage. This is the reference implementation for Kafka client behavior.

---

## Client Information

| | |
|---|---|
| **Library** | `org.apache.kafka:kafka-clients` |
| **Repository** | [github.com/apache/kafka](https://github.com/apache/kafka) |
| **Documentation** | [kafka.apache.org/documentation](https://kafka.apache.org/documentation/) |
| **Package** | [Maven Central](https://central.sonatype.com/artifact/org.apache.kafka/kafka-clients) |
| **Current Version** | 4.1.x (as of 2025) |
| **Maintainer** | Apache Software Foundation |
| **License** | Apache License 2.0 |

### History

The Java client is the reference implementation, developed as part of the core Apache Kafka project. Originally, Kafka included a Scala-based client (the "old consumer"). In Kafka 0.8.0 (December 2013), a new Java Producer was introduced. The new Java Consumer followed in Kafka 0.9.0 (November 2015), marking the deprecation of the Scala clients. The Java client supports all Kafka features immediately upon release, including Kafka Streams (introduced in 0.10.0), exactly-once semantics (0.11.0), and all subsequent protocol enhancements.

### Version Compatibility

| Client Version | Minimum Kafka Broker | Recommended Broker |
|----------------|---------------------|-------------------|
| 4.1.x | 0.10.0+ | 3.0+ |
| 4.0.x | 0.10.0+ | 3.0+ |
| 3.9.x | 0.10.0+ | 3.0+ |
| 3.7.x | 0.10.0+ | 3.0+ |

### External Resources

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Kafka Javadocs](https://kafka.apache.org/41/javadoc/index.html)
- [Confluent Developer Tutorials](https://developer.confluent.io/tutorials/)
- [Kafka Users Mailing List](https://kafka.apache.org/contact)

---

## Installation

### Maven

```xml
<dependency>
    <groupId>org.apache.kafka</groupId>
    <artifactId>kafka-clients</artifactId>
    <version>4.1.1</version>
</dependency>
```

### Gradle

```groovy
implementation 'org.apache.kafka:kafka-clients:4.1.1'
```

### With Schema Registry

```xml
<dependency>
    <groupId>io.confluent</groupId>
    <artifactId>kafka-avro-serializer</artifactId>
    <version>7.5.0</version>
</dependency>

<!-- Confluent Maven repository -->
<repositories>
    <repository>
        <id>confluent</id>
        <url>https://packages.confluent.io/maven/</url>
    </repository>
</repositories>
```

---

## Producer

### Basic Producer

```java
import org.apache.kafka.clients.producer.*;
import org.apache.kafka.common.serialization.StringSerializer;
import java.util.Properties;

public class SimpleProducer {
    public static void main(String[] args) {
        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka:9092");
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());

        try (KafkaProducer<String, String> producer = new KafkaProducer<>(props)) {
            ProducerRecord<String, String> record = new ProducerRecord<>(
                "orders",           // topic
                "order-123",        // key
                "{\"id\": 123}"     // value
            );

            // Asynchronous send with callback
            producer.send(record, (metadata, exception) -> {
                if (exception != null) {
                    System.err.println("Send failed: " + exception.getMessage());
                } else {
                    System.out.printf("Sent to partition %d offset %d%n",
                        metadata.partition(), metadata.offset());
                }
            });
        }
    }
}
```

### Production Producer Configuration

```java
Properties props = new Properties();

// Connection
props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka-1:9092,kafka-2:9092,kafka-3:9092");
props.put(ProducerConfig.CLIENT_ID_CONFIG, "order-service-producer");

// Serialization
props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());

// Durability
props.put(ProducerConfig.ACKS_CONFIG, "all");
props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);

// Retries
props.put(ProducerConfig.RETRIES_CONFIG, Integer.MAX_VALUE);
props.put(ProducerConfig.DELIVERY_TIMEOUT_MS_CONFIG, 120000);
props.put(ProducerConfig.MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION, 5);

// Batching
props.put(ProducerConfig.BATCH_SIZE_CONFIG, 65536);
props.put(ProducerConfig.LINGER_MS_CONFIG, 10);
props.put(ProducerConfig.BUFFER_MEMORY_CONFIG, 67108864);

// Compression
props.put(ProducerConfig.COMPRESSION_TYPE_CONFIG, "lz4");
```

### Synchronous Send

```java
try {
    RecordMetadata metadata = producer.send(record).get();
    System.out.printf("Sent to %s-%d@%d%n",
        metadata.topic(), metadata.partition(), metadata.offset());
} catch (ExecutionException e) {
    if (e.getCause() instanceof RetriableException) {
        // Retry logic
    } else {
        // Non-retriable error
        throw e;
    }
}
```

### Send with Headers

```java
ProducerRecord<String, String> record = new ProducerRecord<>("orders", "key", "value");
record.headers()
    .add("correlation-id", "abc-123".getBytes(StandardCharsets.UTF_8))
    .add("source", "order-service".getBytes(StandardCharsets.UTF_8));

producer.send(record);
```

### Custom Partitioner

```java
public class OrderPartitioner implements Partitioner {
    @Override
    public int partition(String topic, Object key, byte[] keyBytes,
                        Object value, byte[] valueBytes, Cluster cluster) {
        List<PartitionInfo> partitions = cluster.partitionsForTopic(topic);
        int numPartitions = partitions.size();

        if (key == null) {
            // Round-robin for null keys
            return ThreadLocalRandom.current().nextInt(numPartitions);
        }

        // Custom logic: route by region prefix
        String keyStr = (String) key;
        if (keyStr.startsWith("US-")) {
            return 0;
        } else if (keyStr.startsWith("EU-")) {
            return 1;
        }

        // Default: hash-based
        return Math.abs(key.hashCode()) % numPartitions;
    }

    @Override
    public void close() {}

    @Override
    public void configure(Map<String, ?> configs) {}
}

// Usage
props.put(ProducerConfig.PARTITIONER_CLASS_CONFIG, OrderPartitioner.class.getName());
```

---

## Consumer

### Basic Consumer

```java
import org.apache.kafka.clients.consumer.*;
import org.apache.kafka.common.serialization.StringDeserializer;
import java.time.Duration;
import java.util.Arrays;
import java.util.Properties;

public class SimpleConsumer {
    public static void main(String[] args) {
        Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka:9092");
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "order-processors");
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");

        try (KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props)) {
            consumer.subscribe(Arrays.asList("orders"));

            while (true) {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));

                for (ConsumerRecord<String, String> record : records) {
                    System.out.printf("Received: key=%s value=%s partition=%d offset=%d%n",
                        record.key(), record.value(), record.partition(), record.offset());
                }
            }
        }
    }
}
```

### Production Consumer Configuration

```java
Properties props = new Properties();

// Connection
props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka-1:9092,kafka-2:9092,kafka-3:9092");
props.put(ConsumerConfig.GROUP_ID_CONFIG, "order-processors");
props.put(ConsumerConfig.CLIENT_ID_CONFIG, "order-processor-1");

// Deserialization
props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());

// Offset management
props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);
props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");

// Session management
props.put(ConsumerConfig.SESSION_TIMEOUT_MS_CONFIG, 45000);
props.put(ConsumerConfig.HEARTBEAT_INTERVAL_MS_CONFIG, 15000);
props.put(ConsumerConfig.MAX_POLL_INTERVAL_MS_CONFIG, 300000);

// Fetch configuration
props.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, 500);
props.put(ConsumerConfig.FETCH_MIN_BYTES_CONFIG, 1);
props.put(ConsumerConfig.FETCH_MAX_WAIT_MS_CONFIG, 500);

// Assignment strategy
props.put(ConsumerConfig.PARTITION_ASSIGNMENT_STRATEGY_CONFIG,
    CooperativeStickyAssignor.class.getName());
```

### Manual Offset Commit

```java
try (KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props)) {
    consumer.subscribe(Arrays.asList("orders"));

    while (running) {
        ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));

        for (ConsumerRecord<String, String> record : records) {
            processRecord(record);
        }

        // Synchronous commit after processing batch
        consumer.commitSync();
    }
}
```

### Per-Partition Commit

```java
while (running) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));

    for (TopicPartition partition : records.partitions()) {
        List<ConsumerRecord<String, String>> partitionRecords = records.records(partition);

        for (ConsumerRecord<String, String> record : partitionRecords) {
            processRecord(record);
        }

        // Commit this partition's offset
        long lastOffset = partitionRecords.get(partitionRecords.size() - 1).offset();
        consumer.commitSync(Map.of(partition, new OffsetAndMetadata(lastOffset + 1)));
    }
}
```

### Rebalance Listener

```java
consumer.subscribe(Arrays.asList("orders"), new ConsumerRebalanceListener() {
    @Override
    public void onPartitionsRevoked(Collection<TopicPartition> partitions) {
        System.out.println("Partitions revoked: " + partitions);
        // Commit pending offsets before rebalance
        consumer.commitSync();
    }

    @Override
    public void onPartitionsAssigned(Collection<TopicPartition> partitions) {
        System.out.println("Partitions assigned: " + partitions);
        // Initialize state for new partitions
    }

    @Override
    public void onPartitionsLost(Collection<TopicPartition> partitions) {
        System.out.println("Partitions lost: " + partitions);
        // Handle unexpected partition loss (cooperative rebalancing)
    }
});
```

### Graceful Shutdown

```java
public class GracefulConsumer {
    private final AtomicBoolean running = new AtomicBoolean(true);
    private KafkaConsumer<String, String> consumer;

    public void consume() {
        try {
            consumer.subscribe(Arrays.asList("orders"));

            while (running.get()) {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
                processRecords(records);
                consumer.commitSync();
            }
        } catch (WakeupException e) {
            if (running.get()) throw e;
        } finally {
            consumer.close();
        }
    }

    public void shutdown() {
        running.set(false);
        consumer.wakeup();
    }
}

// Register shutdown hook
Runtime.getRuntime().addShutdownHook(new Thread(consumer::shutdown));
```

---

## Admin Client

### Create Topics

```java
import org.apache.kafka.clients.admin.*;
import java.util.Collections;
import java.util.Properties;

Properties props = new Properties();
props.put(AdminClientConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka:9092");

try (AdminClient admin = AdminClient.create(props)) {
    NewTopic topic = new NewTopic("orders", 6, (short) 3)
        .configs(Map.of(
            "retention.ms", "604800000",
            "cleanup.policy", "delete"
        ));

    CreateTopicsResult result = admin.createTopics(Collections.singleton(topic));
    result.all().get(); // Wait for completion
}
```

### Describe Topics

```java
try (AdminClient admin = AdminClient.create(props)) {
    DescribeTopicsResult result = admin.describeTopics(Arrays.asList("orders"));
    Map<String, TopicDescription> descriptions = result.allTopicNames().get();

    for (TopicDescription desc : descriptions.values()) {
        System.out.println("Topic: " + desc.name());
        for (TopicPartitionInfo partition : desc.partitions()) {
            System.out.printf("  Partition %d: leader=%d replicas=%s isr=%s%n",
                partition.partition(),
                partition.leader().id(),
                partition.replicas(),
                partition.isr());
        }
    }
}
```

### List Consumer Groups

```java
try (AdminClient admin = AdminClient.create(props)) {
    ListConsumerGroupsResult result = admin.listConsumerGroups();
    Collection<ConsumerGroupListing> groups = result.all().get();

    for (ConsumerGroupListing group : groups) {
        System.out.println("Group: " + group.groupId());
    }
}
```

---

## Transactions

### Transactional Producer

```java
Properties props = new Properties();
props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka:9092");
props.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "order-processor-txn");
props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());

KafkaProducer<String, String> producer = new KafkaProducer<>(props);
producer.initTransactions();

try {
    producer.beginTransaction();

    producer.send(new ProducerRecord<>("orders", "key1", "value1"));
    producer.send(new ProducerRecord<>("audit", "key1", "order created"));

    producer.commitTransaction();
} catch (ProducerFencedException | OutOfOrderSequenceException e) {
    // Fatal errors - close producer
    producer.close();
} catch (KafkaException e) {
    // Abort and retry
    producer.abortTransaction();
}
```

### Consume-Transform-Produce

```java
// Consumer configuration
Properties consumerProps = new Properties();
consumerProps.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka:9092");
consumerProps.put(ConsumerConfig.GROUP_ID_CONFIG, "processor");
consumerProps.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);
consumerProps.put(ConsumerConfig.ISOLATION_LEVEL_CONFIG, "read_committed");

// Producer configuration
Properties producerProps = new Properties();
producerProps.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka:9092");
producerProps.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "processor-txn");
producerProps.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);

KafkaConsumer<String, String> consumer = new KafkaConsumer<>(consumerProps);
KafkaProducer<String, String> producer = new KafkaProducer<>(producerProps);

producer.initTransactions();
consumer.subscribe(Arrays.asList("input"));

while (running) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));

    if (!records.isEmpty()) {
        producer.beginTransaction();

        try {
            for (ConsumerRecord<String, String> record : records) {
                String transformed = transform(record.value());
                producer.send(new ProducerRecord<>("output", record.key(), transformed));
            }

            // Commit offsets within transaction
            producer.sendOffsetsToTransaction(
                getOffsetsToCommit(records),
                consumer.groupMetadata()
            );

            producer.commitTransaction();
        } catch (Exception e) {
            producer.abortTransaction();
        }
    }
}
```

---

## Error Handling

### Producer Error Handling

```java
producer.send(record, (metadata, exception) -> {
    if (exception == null) {
        // Success
        return;
    }

    if (exception instanceof RetriableException) {
        // Network issues, leader election - producer will retry automatically
        log.warn("Retriable error, producer will retry: {}", exception.getMessage());
    } else if (exception instanceof SerializationException) {
        // Bad data - skip or dead letter queue
        sendToDeadLetterQueue(record, exception);
    } else if (exception instanceof AuthorizationException) {
        // Permission issue - requires intervention
        log.error("Authorization failed", exception);
        shutdown();
    } else {
        // Unknown error
        log.error("Send failed", exception);
    }
});
```

### Consumer Error Handling

```java
while (running) {
    try {
        ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));

        for (ConsumerRecord<String, String> record : records) {
            try {
                processRecord(record);
            } catch (ProcessingException e) {
                handleProcessingError(record, e);
            }
        }

        consumer.commitSync();

    } catch (WakeupException e) {
        if (running.get()) throw e;
    } catch (SerializationException e) {
        // Poison pill - skip offset
        log.error("Deserialization error", e);
        skipBadRecord();
    } catch (AuthorizationException e) {
        log.error("Authorization error", e);
        shutdown();
    }
}
```

---

## Testing

### Embedded Kafka (Spring)

```java
@EmbeddedKafka(partitions = 3, topics = {"orders"})
class KafkaIntegrationTest {
    @Autowired
    private EmbeddedKafkaBroker embeddedKafka;

    @Test
    void testProduceConsume() {
        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG,
            embeddedKafka.getBrokersAsString());
        // ... test implementation
    }
}
```

### Testcontainers

```java
@Testcontainers
class KafkaContainerTest {
    @Container
    static KafkaContainer kafka = new KafkaContainer(
        DockerImageName.parse("confluentinc/cp-kafka:7.5.0")
    );

    @Test
    void testWithRealKafka() {
        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, kafka.getBootstrapServers());

        try (KafkaProducer<String, String> producer = new KafkaProducer<>(props)) {
            producer.send(new ProducerRecord<>("test", "key", "value")).get();
        }
    }
}
```

### MockProducer

```java
@Test
void testProducerLogic() {
    MockProducer<String, String> mockProducer = new MockProducer<>(
        true, // autoComplete
        new StringSerializer(),
        new StringSerializer()
    );

    MyService service = new MyService(mockProducer);
    service.processOrder(new Order("123"));

    List<ProducerRecord<String, String>> records = mockProducer.history();
    assertEquals(1, records.size());
    assertEquals("orders", records.get(0).topic());
}
```

---

## Related Documentation

- [Producer Development](../producers/index.md) - Producer patterns
- [Consumer Development](../consumers/index.md) - Consumer patterns
- [Transactions](../producers/transactions.md) - Transaction patterns