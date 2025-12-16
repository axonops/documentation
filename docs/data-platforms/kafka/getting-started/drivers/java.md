---
title: "Kafka Java Driver"
description: "Apache Kafka Java client. Installation, configuration, producer and consumer examples."
meta:
  - name: keywords
    content: "Kafka Java quickstart, Java Kafka tutorial, Java producer consumer, kafka-clients getting started"
---

# Kafka Java Driver

The official Apache Kafka Java client provides producer, consumer, and admin APIs for JVM applications.

---

## Installation

### Maven

```xml
<dependency>
    <groupId>org.apache.kafka</groupId>
    <artifactId>kafka-clients</artifactId>
    <version>3.6.0</version>
</dependency>
```

### Gradle

```groovy
implementation 'org.apache.kafka:kafka-clients:3.6.0'
```

---

## Producer

### Basic Producer

```java
import org.apache.kafka.clients.producer.*;
import java.util.Properties;

public class BasicProducer {
    public static void main(String[] args) {
        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG,
            "org.apache.kafka.common.serialization.StringSerializer");
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG,
            "org.apache.kafka.common.serialization.StringSerializer");

        try (Producer<String, String> producer = new KafkaProducer<>(props)) {
            ProducerRecord<String, String> record =
                new ProducerRecord<>("events", "key", "value");

            producer.send(record, (metadata, exception) -> {
                if (exception == null) {
                    System.out.printf("Sent to partition %d offset %d%n",
                        metadata.partition(), metadata.offset());
                } else {
                    exception.printStackTrace();
                }
            });
        }
    }
}
```

### Reliable Producer

```java
Properties props = new Properties();
props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG,
    "org.apache.kafka.common.serialization.StringSerializer");
props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG,
    "org.apache.kafka.common.serialization.StringSerializer");

// Reliability settings
props.put(ProducerConfig.ACKS_CONFIG, "all");
props.put(ProducerConfig.RETRIES_CONFIG, Integer.MAX_VALUE);
props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
props.put(ProducerConfig.MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION, 5);

// Performance settings
props.put(ProducerConfig.BATCH_SIZE_CONFIG, 16384);
props.put(ProducerConfig.LINGER_MS_CONFIG, 5);
props.put(ProducerConfig.COMPRESSION_TYPE_CONFIG, "lz4");
```

### Transactional Producer

```java
Properties props = new Properties();
props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
props.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "my-transactional-id");
props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);

Producer<String, String> producer = new KafkaProducer<>(props);
producer.initTransactions();

try {
    producer.beginTransaction();
    producer.send(new ProducerRecord<>("topic1", "key", "value1"));
    producer.send(new ProducerRecord<>("topic2", "key", "value2"));
    producer.commitTransaction();
} catch (Exception e) {
    producer.abortTransaction();
    throw e;
} finally {
    producer.close();
}
```

---

## Consumer

### Basic Consumer

```java
import org.apache.kafka.clients.consumer.*;
import java.time.Duration;
import java.util.Collections;
import java.util.Properties;

public class BasicConsumer {
    public static void main(String[] args) {
        Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "my-group");
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG,
            "org.apache.kafka.common.serialization.StringDeserializer");
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG,
            "org.apache.kafka.common.serialization.StringDeserializer");
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");

        try (Consumer<String, String> consumer = new KafkaConsumer<>(props)) {
            consumer.subscribe(Collections.singletonList("events"));

            while (true) {
                ConsumerRecords<String, String> records =
                    consumer.poll(Duration.ofMillis(100));

                for (ConsumerRecord<String, String> record : records) {
                    System.out.printf("offset=%d key=%s value=%s%n",
                        record.offset(), record.key(), record.value());
                }
            }
        }
    }
}
```

### Manual Commit

```java
Properties props = new Properties();
props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
props.put(ConsumerConfig.GROUP_ID_CONFIG, "my-group");
props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);

Consumer<String, String> consumer = new KafkaConsumer<>(props);
consumer.subscribe(Collections.singletonList("events"));

try {
    while (true) {
        ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));

        for (ConsumerRecord<String, String> record : records) {
            processRecord(record);
        }

        // Synchronous commit after processing
        consumer.commitSync();
    }
} finally {
    consumer.close();
}
```

### At-Least-Once with Retry

```java
while (true) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));

    for (ConsumerRecord<String, String> record : records) {
        boolean processed = false;
        int attempts = 0;

        while (!processed && attempts < 3) {
            try {
                processRecord(record);
                processed = true;
            } catch (Exception e) {
                attempts++;
                if (attempts >= 3) {
                    sendToDeadLetterQueue(record);
                }
            }
        }
    }

    consumer.commitSync();
}
```

---

## Admin Client

### Create Topic

```java
import org.apache.kafka.clients.admin.*;
import java.util.Collections;
import java.util.Properties;

Properties props = new Properties();
props.put(AdminClientConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");

try (AdminClient admin = AdminClient.create(props)) {
    NewTopic topic = new NewTopic("my-topic", 3, (short) 3);
    admin.createTopics(Collections.singleton(topic)).all().get();
}
```

### Describe Topics

```java
DescribeTopicsResult result = admin.describeTopics(Collections.singletonList("my-topic"));
TopicDescription description = result.values().get("my-topic").get();

System.out.println("Partitions: " + description.partitions().size());
for (TopicPartitionInfo partition : description.partitions()) {
    System.out.printf("Partition %d: leader=%d replicas=%s%n",
        partition.partition(),
        partition.leader().id(),
        partition.replicas());
}
```

---

## Configuration Reference

### Producer

| Property | Description | Default |
|----------|-------------|:-------:|
| `acks` | Acknowledgment level | 1 |
| `retries` | Retry count | 2147483647 |
| `batch.size` | Batch size bytes | 16384 |
| `linger.ms` | Batch delay | 0 |
| `buffer.memory` | Buffer memory | 33554432 |
| `enable.idempotence` | Idempotent producer | false |
| `transactional.id` | Transaction ID | null |

### Consumer

| Property | Description | Default |
|----------|-------------|:-------:|
| `group.id` | Consumer group | Required |
| `auto.offset.reset` | Reset behavior | latest |
| `enable.auto.commit` | Auto commit | true |
| `auto.commit.interval.ms` | Commit interval | 5000 |
| `max.poll.records` | Max records per poll | 500 |
| `session.timeout.ms` | Session timeout | 45000 |
| `heartbeat.interval.ms` | Heartbeat interval | 3000 |

---

## Serialization

### JSON with Jackson

```java
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.kafka.common.serialization.Serializer;

public class JsonSerializer<T> implements Serializer<T> {
    private final ObjectMapper mapper = new ObjectMapper();

    @Override
    public byte[] serialize(String topic, T data) {
        try {
            return mapper.writeValueAsBytes(data);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}
```

### Avro with Schema Registry

```xml
<dependency>
    <groupId>io.confluent</groupId>
    <artifactId>kafka-avro-serializer</artifactId>
    <version>7.5.0</version>
</dependency>
```

```java
props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG,
    "io.confluent.kafka.serializers.KafkaAvroSerializer");
props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG,
    "io.confluent.kafka.serializers.KafkaAvroSerializer");
props.put("schema.registry.url", "http://localhost:8081");
```

---

## Error Handling

### Producer Errors

```java
producer.send(record, (metadata, exception) -> {
    if (exception != null) {
        if (exception instanceof RetriableException) {
            // Will be retried automatically
            log.warn("Retriable error", exception);
        } else {
            // Fatal error
            log.error("Fatal error", exception);
            // Handle: dead letter queue, alerting, etc.
        }
    }
});
```

### Consumer Errors

```java
try {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    // process records
} catch (WakeupException e) {
    // Shutdown signal
} catch (AuthorizationException e) {
    // Fatal - exit
    throw e;
} catch (KafkaException e) {
    // Log and continue
    log.error("Kafka error", e);
}
```

---

## Related Documentation

- [Drivers Overview](index.md) - All client drivers
- [Producer Guide](../../producers/index.md) - Producer patterns
- [Consumer Guide](../../consumers/index.md) - Consumer patterns
- [Schema Registry](../../schema-registry/index.md) - Schema management
