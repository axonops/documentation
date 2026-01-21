---
title: "Kafka Python Client"
description: "Apache Kafka Python client guide using confluent-kafka-python. Producer, consumer, and admin client usage with configuration and best practices."
meta:
  - name: keywords
    content: "Kafka Python, confluent-kafka, kafka-python, Python Kafka producer, Python Kafka consumer, pip kafka"
search:
  boost: 3
---

# Kafka Python Client

The `confluent-kafka-python` library provides a high-performance Python client built on librdkafka. This guide covers installation, configuration, and usage patterns.

---

## Client Information

| | |
|---|---|
| **Library** | `confluent-kafka` |
| **Repository** | [github.com/confluentinc/confluent-kafka-python](https://github.com/confluentinc/confluent-kafka-python) |
| **Documentation** | [docs.confluent.io/platform/current/clients/confluent-kafka-python](https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html) |
| **Package** | [PyPI](https://pypi.org/project/confluent-kafka/) |
| **Current Version** | 2.12.x (as of 2025) |
| **Maintainer** | Confluent |
| **License** | Apache License 2.0 |
| **Base** | librdkafka (C library) |

### History

The confluent-kafka-python library was first released by Confluent in 2016 as a Python wrapper around librdkafka using C extensions. It was created to provide significantly higher performance than pure-Python alternatives like kafka-python. The library provides a Pythonic API while delegating the heavy lifting to the battle-tested librdkafka implementation. In 2019, Confluent added Schema Registry integration with support for Avro, Protobuf, and JSON Schema serializers. The library remains the recommended Python client for production Kafka deployments.

### Alternative: kafka-python (Pure Python)

For environments where native compilation is problematic (serverless, some containers), the pure-Python `kafka-python` library is a popular alternative:

| | |
|---|---|
| **Library** | `kafka-python` |
| **Repository** | [github.com/dpkp/kafka-python](https://github.com/dpkp/kafka-python) |
| **Documentation** | [kafka-python.readthedocs.io](https://kafka-python.readthedocs.io/) |
| **Package** | [PyPI](https://pypi.org/project/kafka-python/) |
| **Current Version** | 2.2.x (as of 2025) |
| **Maintainer** | Dana Powers (dpkp) |
| **License** | Apache License 2.0 |
| **Base** | Pure Python (no native dependencies) |

kafka-python is designed to mirror the official Java client API while incorporating Pythonic features like consumer iterators. It supports consumer groups, transactions, all compression types (gzip, LZ4, Snappy, Zstandard), and message headers. With 5.9k GitHub stars and use by 35,000+ projects, it's the most popular pure-Python option.

### Client Comparison

| Feature | confluent-kafka | kafka-python |
|---------|-----------------|--------------|
| Implementation | librdkafka (C) | Pure Python |
| Performance | Highest | Lower |
| Installation | Requires build tools | `pip install` only |
| Serverless | Difficult | Easy |
| Transactions | ✅ | ✅ |
| Compression | All types | All types |
| Consumer groups | ✅ | ✅ |

### Version Compatibility

| Client Version | librdkafka | Minimum Kafka Broker |
|----------------|------------|---------------------|
| 2.12.x | 2.12.x | 0.8.0+ |
| 2.10.x | 2.10.x | 0.8.0+ |
| 2.6.x | 2.6.x | 0.8.0+ |

### External Resources

- [Confluent Developer Python Guide](https://developer.confluent.io/get-started/python/)
- [API Reference](https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html)
- [librdkafka Configuration](https://github.com/confluentinc/librdkafka/blob/master/CONFIGURATION.md)
- [GitHub Examples](https://github.com/confluentinc/confluent-kafka-python/tree/master/examples)

---

## Installation

### pip

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

### Poetry

```bash
poetry add confluent-kafka
```

---

## Producer

### Basic Producer

```python
from confluent_kafka import Producer

config = {
    'bootstrap.servers': 'kafka:9092',
    'client.id': 'order-service'
}

producer = Producer(config)

def delivery_callback(err, msg):
    if err:
        print(f'Delivery failed: {err}')
    else:
        print(f'Delivered to {msg.topic()} [{msg.partition()}] @ {msg.offset()}')

# Asynchronous send
producer.produce(
    topic='orders',
    key='order-123',
    value='{"id": 123, "amount": 99.99}',
    callback=delivery_callback
)

# Trigger delivery reports
producer.poll(0)

# Wait for all messages to be delivered
producer.flush()
```

### Production Configuration

```python
config = {
    # Connection
    'bootstrap.servers': 'kafka-1:9092,kafka-2:9092,kafka-3:9092',
    'client.id': 'order-service-producer',

    # Durability
    'acks': 'all',
    'enable.idempotence': True,

    # Retries
    'retries': 2147483647,
    'delivery.timeout.ms': 120000,
    'max.in.flight.requests.per.connection': 5,

    # Batching
    'batch.size': 65536,
    'linger.ms': 10,
    'queue.buffering.max.messages': 100000,
    'queue.buffering.max.kbytes': 1048576,

    # Compression
    'compression.type': 'lz4',

    # Error handling
    'error_cb': error_callback,
}

producer = Producer(config)
```

### Send with Headers

```python
producer.produce(
    topic='orders',
    key='order-123',
    value='{"id": 123}',
    headers=[
        ('correlation-id', b'abc-123'),
        ('source', b'order-service'),
    ],
    callback=delivery_callback
)
```

### Synchronous Send

```python
from confluent_kafka import KafkaException

def sync_produce(producer, topic, key, value):
    """Synchronous produce with error handling."""
    result = {'delivered': False, 'error': None, 'metadata': None}

    def callback(err, msg):
        if err:
            result['error'] = err
        else:
            result['delivered'] = True
            result['metadata'] = {
                'topic': msg.topic(),
                'partition': msg.partition(),
                'offset': msg.offset()
            }

    producer.produce(topic, key=key, value=value, callback=callback)
    producer.flush()

    if result['error']:
        raise KafkaException(result['error'])

    return result['metadata']
```

### Context Manager Pattern

```python
from contextlib import contextmanager
from confluent_kafka import Producer

@contextmanager
def kafka_producer(config):
    producer = Producer(config)
    try:
        yield producer
    finally:
        producer.flush()

# Usage
with kafka_producer(config) as producer:
    producer.produce('orders', key='123', value='data')
```

---

## Consumer

### Basic Consumer

```python
from confluent_kafka import Consumer, KafkaError

config = {
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'order-processors',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
}

consumer = Consumer(config)
consumer.subscribe(['orders'])

try:
    while True:
        msg = consumer.poll(timeout=1.0)

        if msg is None:
            continue

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                print(f'End of partition {msg.partition()}')
            else:
                raise KafkaException(msg.error())
        else:
            print(f'Received: key={msg.key()} value={msg.value()}')
            process_message(msg)
            consumer.commit(asynchronous=False)

finally:
    consumer.close()
```

### Production Configuration

```python
config = {
    # Connection
    'bootstrap.servers': 'kafka-1:9092,kafka-2:9092,kafka-3:9092',
    'group.id': 'order-processors',
    'client.id': 'order-processor-1',

    # Offset management
    'enable.auto.commit': False,
    'auto.offset.reset': 'earliest',

    # Session management
    'session.timeout.ms': 45000,
    'heartbeat.interval.ms': 15000,
    'max.poll.interval.ms': 300000,

    # Fetch configuration
    'fetch.min.bytes': 1,
    'fetch.max.bytes': 52428800,
    'max.partition.fetch.bytes': 1048576,

    # Assignment strategy
    'partition.assignment.strategy': 'cooperative-sticky',

    # Callbacks
    'error_cb': error_callback,
    'stats_cb': stats_callback,
    'statistics.interval.ms': 60000,
}

consumer = Consumer(config)
```

### Batch Processing

```python
def consume_batch(consumer, batch_size=100, timeout=1.0):
    """Consume messages in batches."""
    messages = consumer.consume(num_messages=batch_size, timeout=timeout)

    valid_messages = []
    for msg in messages:
        if msg is None:
            continue
        if msg.error():
            handle_error(msg.error())
        else:
            valid_messages.append(msg)

    return valid_messages

# Usage
while running:
    batch = consume_batch(consumer, batch_size=500)
    if batch:
        process_batch(batch)
        consumer.commit(asynchronous=False)
```

### Rebalance Callback

```python
def on_assign(consumer, partitions):
    print(f'Assigned: {partitions}')
    # Initialize state for partitions

def on_revoke(consumer, partitions):
    print(f'Revoked: {partitions}')
    # Commit offsets, cleanup state
    consumer.commit(asynchronous=False)

def on_lost(consumer, partitions):
    print(f'Lost: {partitions}')
    # Handle unexpected partition loss

consumer.subscribe(
    ['orders'],
    on_assign=on_assign,
    on_revoke=on_revoke,
    on_lost=on_lost
)
```

### Manual Partition Assignment

```python
from confluent_kafka import TopicPartition

# Assign specific partitions (no consumer group)
consumer.assign([
    TopicPartition('orders', 0),
    TopicPartition('orders', 1),
])

# Seek to specific offset
consumer.seek(TopicPartition('orders', 0, 1000))

# Seek to beginning
consumer.seek(TopicPartition('orders', 0, OFFSET_BEGINNING))
```

### Graceful Shutdown

```python
import signal
import sys

running = True

def shutdown_handler(signum, frame):
    global running
    running = False

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

consumer = Consumer(config)
consumer.subscribe(['orders'])

try:
    while running:
        msg = consumer.poll(timeout=1.0)
        if msg and not msg.error():
            process_message(msg)
            consumer.commit()
except Exception as e:
    print(f'Error: {e}')
finally:
    print('Closing consumer...')
    consumer.close()
    sys.exit(0)
```

---

## Admin Client

### Create Topics

```python
from confluent_kafka.admin import AdminClient, NewTopic

admin = AdminClient({'bootstrap.servers': 'kafka:9092'})

topics = [
    NewTopic(
        topic='orders',
        num_partitions=6,
        replication_factor=3,
        config={
            'retention.ms': '604800000',
            'cleanup.policy': 'delete'
        }
    )
]

futures = admin.create_topics(topics)

for topic, future in futures.items():
    try:
        future.result()
        print(f'Topic {topic} created')
    except Exception as e:
        print(f'Failed to create topic {topic}: {e}')
```

### Describe Topics

```python
from confluent_kafka.admin import AdminClient

admin = AdminClient({'bootstrap.servers': 'kafka:9092'})

topics = admin.list_topics(timeout=10)

for topic in topics.topics.values():
    print(f'Topic: {topic.topic}')
    for partition in topic.partitions.values():
        print(f'  Partition {partition.id}: leader={partition.leader}')
```

### List Consumer Groups

```python
from confluent_kafka.admin import AdminClient

admin = AdminClient({'bootstrap.servers': 'kafka:9092'})

groups = admin.list_consumer_groups()
result = groups.result()

for group in result.valid:
    print(f'Group: {group.group_id} ({group.group_type})')
```

### Describe Consumer Group

```python
from confluent_kafka.admin import AdminClient

admin = AdminClient({'bootstrap.servers': 'kafka:9092'})

group_metadata = admin.describe_consumer_groups(['order-processors'])

for group_id, future in group_metadata.items():
    try:
        group = future.result()
        print(f'Group: {group.group_id}')
        print(f'State: {group.state}')
        for member in group.members:
            print(f'  Member: {member.member_id}')
            print(f'  Client: {member.client_id}')
    except Exception as e:
        print(f'Error: {e}')
```

---

## Schema Registry Integration

### Avro Producer

```python
from confluent_kafka import SerializingProducer
from confluent_kafka.serialization import StringSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

schema_registry_conf = {'url': 'http://schema-registry:8081'}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

value_schema_str = """
{
    "type": "record",
    "name": "Order",
    "fields": [
        {"name": "id", "type": "string"},
        {"name": "amount", "type": "double"},
        {"name": "customer_id", "type": "string"}
    ]
}
"""

avro_serializer = AvroSerializer(
    schema_registry_client,
    value_schema_str,
    lambda obj, ctx: obj  # to_dict function
)

producer_conf = {
    'bootstrap.servers': 'kafka:9092',
    'key.serializer': StringSerializer('utf_8'),
    'value.serializer': avro_serializer
}

producer = SerializingProducer(producer_conf)

order = {
    'id': 'order-123',
    'amount': 99.99,
    'customer_id': 'cust-456'
}

producer.produce(topic='orders', key='order-123', value=order)
producer.flush()
```

### Avro Consumer

```python
from confluent_kafka import DeserializingConsumer
from confluent_kafka.serialization import StringDeserializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer

schema_registry_conf = {'url': 'http://schema-registry:8081'}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

avro_deserializer = AvroDeserializer(
    schema_registry_client,
    lambda obj, ctx: obj  # from_dict function
)

consumer_conf = {
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'order-processors',
    'key.deserializer': StringDeserializer('utf_8'),
    'value.deserializer': avro_deserializer,
    'auto.offset.reset': 'earliest'
}

consumer = DeserializingConsumer(consumer_conf)
consumer.subscribe(['orders'])

while True:
    msg = consumer.poll(1.0)
    if msg and not msg.error():
        order = msg.value()
        print(f"Order: {order['id']} - ${order['amount']}")
```

---

## Error Handling

### Error Callback

```python
from confluent_kafka import KafkaError

def error_callback(err):
    """Handle Kafka errors."""
    if err.code() == KafkaError._ALL_BROKERS_DOWN:
        print('All brokers are down')
    elif err.code() == KafkaError._AUTHENTICATION:
        print('Authentication failed')
    elif err.code() == KafkaError.TOPIC_AUTHORIZATION_FAILED:
        print('Topic authorization failed')
    else:
        print(f'Error: {err}')

config = {
    'bootstrap.servers': 'kafka:9092',
    'error_cb': error_callback
}
```

### Delivery Error Handling

```python
def delivery_callback(err, msg):
    if err is None:
        return

    # Check if retriable
    if err.retriable():
        print(f'Retriable error: {err}')
        # Producer will retry automatically
    elif err.code() == KafkaError.MSG_SIZE_TOO_LARGE:
        print('Message too large, sending to error topic')
        send_to_error_topic(msg)
    elif err.code() == KafkaError.TOPIC_AUTHORIZATION_FAILED:
        print('Authorization failed')
        raise Exception(f'Authorization error: {err}')
    else:
        print(f'Fatal error: {err}')
        raise Exception(f'Delivery failed: {err}')
```

### Consumer Error Handling

```python
from confluent_kafka import KafkaError, KafkaException

while running:
    try:
        msg = consumer.poll(timeout=1.0)

        if msg is None:
            continue

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition - not an error
                continue
            elif msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                print('Topic does not exist')
                continue
            else:
                raise KafkaException(msg.error())

        # Process message
        try:
            process_message(msg)
        except ProcessingError as e:
            send_to_dead_letter_queue(msg, e)

        consumer.commit()

    except KafkaException as e:
        print(f'Kafka error: {e}')
        if not e.args[0].retriable():
            raise
```

---

## Async/Await Pattern

### With asyncio

```python
import asyncio
from confluent_kafka import Producer, Consumer

class AsyncKafkaProducer:
    def __init__(self, config):
        self.producer = Producer(config)
        self.loop = asyncio.get_event_loop()

    async def produce(self, topic, key, value):
        future = self.loop.create_future()

        def callback(err, msg):
            if err:
                self.loop.call_soon_threadsafe(future.set_exception, KafkaException(err))
            else:
                self.loop.call_soon_threadsafe(future.set_result, msg)

        self.producer.produce(topic, key=key, value=value, callback=callback)
        self.producer.poll(0)

        return await future

    async def flush(self):
        self.producer.flush()

# Usage
async def main():
    producer = AsyncKafkaProducer(config)
    await producer.produce('orders', 'key', 'value')
    await producer.flush()

asyncio.run(main())
```

---

## Testing

### MockProducer Pattern

```python
class MockProducer:
    def __init__(self):
        self.messages = []

    def produce(self, topic, key=None, value=None, callback=None, headers=None):
        msg = {'topic': topic, 'key': key, 'value': value, 'headers': headers}
        self.messages.append(msg)
        if callback:
            callback(None, MockMessage(topic, 0, 0, key, value))

    def flush(self):
        pass

    def poll(self, timeout):
        pass

# Usage in tests
def test_order_producer():
    mock = MockProducer()
    service = OrderService(producer=mock)
    service.create_order({'id': '123'})

    assert len(mock.messages) == 1
    assert mock.messages[0]['topic'] == 'orders'
```

### Integration Testing

```python
import pytest
from testcontainers.kafka import KafkaContainer

@pytest.fixture(scope='module')
def kafka_container():
    with KafkaContainer() as kafka:
        yield kafka

def test_produce_consume(kafka_container):
    config = {'bootstrap.servers': kafka_container.get_bootstrap_server()}

    # Produce
    producer = Producer(config)
    producer.produce('test', key='key', value='value')
    producer.flush()

    # Consume
    consumer_config = {**config, 'group.id': 'test', 'auto.offset.reset': 'earliest'}
    consumer = Consumer(consumer_config)
    consumer.subscribe(['test'])

    msg = consumer.poll(10.0)
    assert msg is not None
    assert msg.value() == b'value'

    consumer.close()
```

---

## Related Documentation

- [Producer Development](../producers/index.md) - Producer patterns
- [Consumer Development](../consumers/index.md) - Consumer patterns
- [Schema Registry](../../schema-registry/index.md) - Schema management
