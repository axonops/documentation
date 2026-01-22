---
title: "Kafka Client Drivers"
description: "Apache Kafka client drivers for Java, Python, Go, Node.js, and .NET. Installation, configuration, and usage examples."
meta:
  - name: keywords
    content: "Kafka client, Kafka driver, Kafka Java, Kafka Python, Kafka Go"
---

# Kafka Client Drivers

Client libraries for connecting applications to Apache Kafka clusters.

---

## Driver Overview

| Language | Recommended Client | Maintainer |
|----------|-------------------|------------|
| **Java** | Apache Kafka Client | Apache |
| **Python** | confluent-kafka-python | Confluent |
| **Go** | confluent-kafka-go | Confluent |
| **Node.js** | KafkaJS | Community |
| **.NET** | confluent-kafka-dotnet | Confluent |
| **Rust** | rdkafka | Community |

---

## Java

### Installation

**Maven:**
```xml
<dependency>
    <groupId>org.apache.kafka</groupId>
    <artifactId>kafka-clients</artifactId>
    <version>4.1.1</version>
</dependency>
```

**Gradle:**
```groovy
implementation 'org.apache.kafka:kafka-clients:4.1.1'
```

### Producer Example

```java
import org.apache.kafka.clients.producer.*;
import java.util.Properties;

public class SimpleProducer {
    public static void main(String[] args) {
        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG,
            "org.apache.kafka.common.serialization.StringSerializer");
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG,
            "org.apache.kafka.common.serialization.StringSerializer");

        // Reliability settings
        props.put(ProducerConfig.ACKS_CONFIG, "all");
        props.put(ProducerConfig.RETRIES_CONFIG, 3);
        props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);

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

### Consumer Example

```java
import org.apache.kafka.clients.consumer.*;
import java.time.Duration;
import java.util.Collections;
import java.util.Properties;

public class SimpleConsumer {
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

---

## Python

### Installation

```bash
pip install confluent-kafka
```

### Producer Example

```python
from confluent_kafka import Producer

conf = {
    'bootstrap.servers': 'localhost:9092',
    'acks': 'all',
    'retries': 3,
    'enable.idempotence': True
}

producer = Producer(conf)

def delivery_callback(err, msg):
    if err:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}] @ {msg.offset()}')

producer.produce('events', key='key', value='value', callback=delivery_callback)
producer.flush()
```

### Consumer Example

```python
from confluent_kafka import Consumer, KafkaException

conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)
consumer.subscribe(['events'])

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            raise KafkaException(msg.error())

        print(f'Received: {msg.value().decode("utf-8")}')
finally:
    consumer.close()
```

---

## Go

### Installation

```bash
go get github.com/confluentinc/confluent-kafka-go/v2/kafka
```

### Producer Example

```go
package main

import (
    "fmt"
    "github.com/confluentinc/confluent-kafka-go/v2/kafka"
)

func main() {
    producer, err := kafka.NewProducer(&kafka.ConfigMap{
        "bootstrap.servers": "localhost:9092",
        "acks":              "all",
        "retries":           3,
        "enable.idempotence": true,
    })
    if err != nil {
        panic(err)
    }
    defer producer.Close()

    topic := "events"

    // Delivery report handler
    go func() {
        for e := range producer.Events() {
            switch ev := e.(type) {
            case *kafka.Message:
                if ev.TopicPartition.Error != nil {
                    fmt.Printf("Delivery failed: %v\n", ev.TopicPartition.Error)
                } else {
                    fmt.Printf("Delivered to %v\n", ev.TopicPartition)
                }
            }
        }
    }()

    producer.Produce(&kafka.Message{
        TopicPartition: kafka.TopicPartition{Topic: &topic, Partition: kafka.PartitionAny},
        Key:            []byte("key"),
        Value:          []byte("value"),
    }, nil)

    producer.Flush(15 * 1000)
}
```

### Consumer Example

```go
package main

import (
    "fmt"
    "github.com/confluentinc/confluent-kafka-go/v2/kafka"
)

func main() {
    consumer, err := kafka.NewConsumer(&kafka.ConfigMap{
        "bootstrap.servers": "localhost:9092",
        "group.id":          "my-group",
        "auto.offset.reset": "earliest",
    })
    if err != nil {
        panic(err)
    }
    defer consumer.Close()

    consumer.SubscribeTopics([]string{"events"}, nil)

    for {
        msg, err := consumer.ReadMessage(-1)
        if err != nil {
            fmt.Printf("Consumer error: %v\n", err)
            continue
        }
        fmt.Printf("Received: %s\n", string(msg.Value))
    }
}
```

---

## Node.js

### Installation

```bash
npm install kafkajs
```

### Producer Example

```javascript
const { Kafka } = require('kafkajs');

const kafka = new Kafka({
  clientId: 'my-app',
  brokers: ['localhost:9092']
});

const producer = kafka.producer({
  idempotent: true,
  maxInFlightRequests: 5
});

async function produce() {
  await producer.connect();

  await producer.send({
    topic: 'events',
    messages: [
      { key: 'key', value: 'value' }
    ]
  });

  await producer.disconnect();
}

produce().catch(console.error);
```

### Consumer Example

```javascript
const { Kafka } = require('kafkajs');

const kafka = new Kafka({
  clientId: 'my-app',
  brokers: ['localhost:9092']
});

const consumer = kafka.consumer({ groupId: 'my-group' });

async function consume() {
  await consumer.connect();
  await consumer.subscribe({ topic: 'events', fromBeginning: true });

  await consumer.run({
    eachMessage: async ({ topic, partition, message }) => {
      console.log({
        partition,
        offset: message.offset,
        value: message.value.toString()
      });
    }
  });
}

consume().catch(console.error);
```

---

## Configuration Reference

### Common Producer Settings

| Property | Description | Recommended |
|----------|-------------|-------------|
| `acks` | Acknowledgment level | `all` for durability |
| `retries` | Retry count | 3+ |
| `enable.idempotence` | Exactly-once per partition | `true` |
| `batch.size` | Batch size in bytes | 16384-65536 |
| `linger.ms` | Batch wait time | 5-100 |
| `compression.type` | Compression algorithm | `lz4` or `zstd` |

### Common Consumer Settings

| Property | Description | Recommended |
|----------|-------------|-------------|
| `group.id` | Consumer group ID | Required |
| `auto.offset.reset` | Starting offset | `earliest` or `latest` |
| `enable.auto.commit` | Automatic offset commits | `false` for exactly-once |
| `max.poll.records` | Max records per poll | 500 |
| `session.timeout.ms` | Session timeout | 45000 |

---

## Related Documentation

- [Getting Started](../index.md) - Quick start guide
- [Producer Guide](../../application-development/producers/index.md) - Producer patterns
- [Consumer Guide](../../application-development/consumers/index.md) - Consumer patterns
- [Schema Registry](../../schema-registry/index.md) - Schema management
