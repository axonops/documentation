---
title: "Kafka Python Driver"
description: "Kafka Python client. Installation, configuration, producer and consumer examples with confluent-kafka."
meta:
  - name: keywords
    content: "Kafka Python quickstart, Python Kafka tutorial, confluent-kafka getting started, Python producer consumer"
---

# Kafka Python Driver

The confluent-kafka-python library provides a high-performance Python client based on librdkafka.

---

## Installation

```bash
pip install confluent-kafka
```

### With Avro Support

```bash
pip install confluent-kafka[avro]
```

### With Schema Registry

```bash
pip install confluent-kafka[schemaregistry]
```

---

## Producer

### Basic Producer

```python
from confluent_kafka import Producer

conf = {
    'bootstrap.servers': 'localhost:9092'
}

producer = Producer(conf)

def delivery_callback(err, msg):
    if err:
        print(f'Delivery failed: {err}')
    else:
        print(f'Delivered to {msg.topic()} [{msg.partition()}] @ {msg.offset()}')

producer.produce('events', key='key', value='value', callback=delivery_callback)
producer.flush()
```

### Reliable Producer

```python
from confluent_kafka import Producer

conf = {
    'bootstrap.servers': 'localhost:9092',
    'acks': 'all',
    'retries': 10,
    'retry.backoff.ms': 100,
    'enable.idempotence': True,
    'max.in.flight.requests.per.connection': 5,
    'linger.ms': 5,
    'batch.size': 16384,
    'compression.type': 'lz4'
}

producer = Producer(conf)
```

### Async Producer with Polling

```python
from confluent_kafka import Producer
import time

producer = Producer({'bootstrap.servers': 'localhost:9092'})

def delivery_callback(err, msg):
    if err:
        print(f'Error: {err}')

# Produce messages
for i in range(1000):
    producer.produce('events', value=f'message-{i}', callback=delivery_callback)

    # Periodically poll for callbacks
    producer.poll(0)

# Wait for all messages to be delivered
producer.flush()
```

---

## Consumer

### Basic Consumer

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

        print(f'Received: key={msg.key()} value={msg.value().decode("utf-8")}')
finally:
    consumer.close()
```

### Manual Commit

```python
from confluent_kafka import Consumer

conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-group',
    'enable.auto.commit': False,
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
            continue

        # Process message
        process(msg)

        # Commit after processing
        consumer.commit(asynchronous=False)
finally:
    consumer.close()
```

### Batch Processing

```python
from confluent_kafka import Consumer

conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-group',
    'enable.auto.commit': False,
    'max.poll.interval.ms': 300000
}

consumer = Consumer(conf)
consumer.subscribe(['events'])

try:
    while True:
        messages = consumer.consume(num_messages=100, timeout=1.0)

        if not messages:
            continue

        batch = []
        for msg in messages:
            if msg.error():
                continue
            batch.append(msg.value())

        # Process batch
        process_batch(batch)

        # Commit after batch
        consumer.commit(asynchronous=False)
finally:
    consumer.close()
```

---

## Admin Client

### Create Topic

```python
from confluent_kafka.admin import AdminClient, NewTopic

admin = AdminClient({'bootstrap.servers': 'localhost:9092'})

new_topic = NewTopic('my-topic', num_partitions=3, replication_factor=3)
futures = admin.create_topics([new_topic])

for topic, future in futures.items():
    try:
        future.result()
        print(f'Topic {topic} created')
    except Exception as e:
        print(f'Failed to create topic {topic}: {e}')
```

### List Topics

```python
from confluent_kafka.admin import AdminClient

admin = AdminClient({'bootstrap.servers': 'localhost:9092'})

metadata = admin.list_topics(timeout=10)

for topic in metadata.topics.values():
    print(f'Topic: {topic.topic}, Partitions: {len(topic.partitions)}')
```

---

## Avro Serialization

### Producer with Avro

```python
from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

schema_registry_conf = {'url': 'http://localhost:8081'}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

schema_str = """
{
    "type": "record",
    "name": "Event",
    "fields": [
        {"name": "id", "type": "string"},
        {"name": "timestamp", "type": "long"},
        {"name": "data", "type": "string"}
    ]
}
"""

avro_serializer = AvroSerializer(schema_registry_client, schema_str)

producer_conf = {'bootstrap.servers': 'localhost:9092'}
producer = Producer(producer_conf)

event = {'id': '123', 'timestamp': 1699900000, 'data': 'test'}

producer.produce(
    topic='events',
    key='key',
    value=avro_serializer(event, SerializationContext('events', MessageField.VALUE)),
    callback=delivery_callback
)
producer.flush()
```

### Consumer with Avro

```python
from confluent_kafka import Consumer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer

schema_registry_client = SchemaRegistryClient({'url': 'http://localhost:8081'})
avro_deserializer = AvroDeserializer(schema_registry_client)

consumer_conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(consumer_conf)
consumer.subscribe(['events'])

while True:
    msg = consumer.poll(timeout=1.0)
    if msg is None:
        continue

    event = avro_deserializer(msg.value(), SerializationContext(msg.topic(), MessageField.VALUE))
    print(f'Received: {event}')
```

---

## Configuration Reference

### Producer

| Property | Description | Default |
|----------|-------------|:-------:|
| `acks` | Acknowledgments | 1 |
| `retries` | Retry count | 2147483647 |
| `batch.size` | Batch bytes | 16384 |
| `linger.ms` | Batch delay | 5 |
| `enable.idempotence` | Idempotent | false |
| `compression.type` | Compression | none |

### Consumer

| Property | Description | Default |
|----------|-------------|:-------:|
| `group.id` | Consumer group | Required |
| `auto.offset.reset` | Reset behavior | latest |
| `enable.auto.commit` | Auto commit | true |
| `max.poll.interval.ms` | Max poll interval | 300000 |
| `session.timeout.ms` | Session timeout | 45000 |

---

## Error Handling

```python
from confluent_kafka import KafkaException, KafkaError

try:
    msg = consumer.poll(timeout=1.0)

    if msg is None:
        continue

    if msg.error():
        if msg.error().code() == KafkaError._PARTITION_EOF:
            # End of partition
            continue
        elif msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
            # Topic doesn't exist
            raise KafkaException(msg.error())
        else:
            raise KafkaException(msg.error())

    # Process message
    process(msg)

except KafkaException as e:
    print(f'Kafka error: {e}')
except Exception as e:
    print(f'Error: {e}')
```

---

## Graceful Shutdown

```python
import signal
import sys
from confluent_kafka import Consumer

running = True

def shutdown(signum, frame):
    global running
    running = False

signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-group'
})
consumer.subscribe(['events'])

try:
    while running:
        msg = consumer.poll(timeout=1.0)
        if msg and not msg.error():
            process(msg)
finally:
    consumer.close()
```

---

## Related Documentation

- [Drivers Overview](index.md) - All client drivers
- [Producer Guide](../../application-development/producers/index.md) - Producer patterns
- [Consumer Guide](../../application-development/consumers/index.md) - Consumer patterns
- [Schema Registry](../../schema-registry/index.md) - Schema management