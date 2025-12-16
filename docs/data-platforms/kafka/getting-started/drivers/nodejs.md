---
title: "Kafka Node.js Driver"
description: "Kafka Node.js client. Installation, configuration, producer and consumer examples with KafkaJS."
meta:
  - name: keywords
    content: "Kafka Node.js quickstart, JavaScript Kafka tutorial, KafkaJS getting started, Node producer consumer"
---

# Kafka Node.js Driver

KafkaJS is a modern Apache Kafka client for Node.js, written entirely in JavaScript with no native dependencies.

---

## Installation

```bash
npm install kafkajs
```

Or with Yarn:

```bash
yarn add kafkajs
```

---

## Client Setup

```javascript
const { Kafka } = require('kafkajs');

const kafka = new Kafka({
  clientId: 'my-app',
  brokers: ['localhost:9092']
});
```

### With Authentication

```javascript
const kafka = new Kafka({
  clientId: 'my-app',
  brokers: ['localhost:9092'],
  ssl: true,
  sasl: {
    mechanism: 'plain',
    username: 'user',
    password: 'password'
  }
});
```

---

## Producer

### Basic Producer

```javascript
const { Kafka } = require('kafkajs');

const kafka = new Kafka({
  clientId: 'my-app',
  brokers: ['localhost:9092']
});

const producer = kafka.producer();

async function produce() {
  await producer.connect();

  await producer.send({
    topic: 'events',
    messages: [
      { key: 'key1', value: 'value1' },
      { key: 'key2', value: 'value2' }
    ]
  });

  await producer.disconnect();
}

produce().catch(console.error);
```

### Reliable Producer

```javascript
const producer = kafka.producer({
  idempotent: true,
  maxInFlightRequests: 5,
  transactionalId: 'my-transactional-id'  // For transactions
});

await producer.connect();

await producer.send({
  topic: 'events',
  acks: -1,  // all
  messages: [{ value: 'message' }]
});
```

### Batch Producer

```javascript
async function produceBatch(messages) {
  await producer.sendBatch({
    topicMessages: [
      {
        topic: 'events',
        messages: messages.map(m => ({ value: JSON.stringify(m) }))
      }
    ]
  });
}
```

### Transactional Producer

```javascript
const producer = kafka.producer({
  transactionalId: 'my-transactional-id',
  idempotent: true
});

await producer.connect();

const transaction = await producer.transaction();

try {
  await transaction.send({
    topic: 'topic1',
    messages: [{ value: 'message1' }]
  });

  await transaction.send({
    topic: 'topic2',
    messages: [{ value: 'message2' }]
  });

  await transaction.commit();
} catch (e) {
  await transaction.abort();
  throw e;
}
```

---

## Consumer

### Basic Consumer

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
        key: message.key?.toString(),
        value: message.value.toString()
      });
    }
  });
}

consume().catch(console.error);
```

### Manual Commit

```javascript
const consumer = kafka.consumer({
  groupId: 'my-group',
  autoCommit: false
});

await consumer.connect();
await consumer.subscribe({ topic: 'events' });

await consumer.run({
  eachMessage: async ({ topic, partition, message }) => {
    await processMessage(message);

    await consumer.commitOffsets([
      {
        topic,
        partition,
        offset: (parseInt(message.offset, 10) + 1).toString()
      }
    ]);
  }
});
```

### Batch Processing

```javascript
await consumer.run({
  eachBatch: async ({ batch, resolveOffset, heartbeat, commitOffsetsIfNecessary }) => {
    for (const message of batch.messages) {
      await processMessage(message);
      resolveOffset(message.offset);
      await heartbeat();
    }

    await commitOffsetsIfNecessary();
  }
});
```

### Pause and Resume

```javascript
// Pause consumption
consumer.pause([{ topic: 'events' }]);

// Resume consumption
consumer.resume([{ topic: 'events' }]);
```

---

## Admin Client

### Create Topic

```javascript
const admin = kafka.admin();

await admin.connect();

await admin.createTopics({
  topics: [
    {
      topic: 'my-topic',
      numPartitions: 3,
      replicationFactor: 3
    }
  ]
});

await admin.disconnect();
```

### List Topics

```javascript
const admin = kafka.admin();
await admin.connect();

const topics = await admin.listTopics();
console.log('Topics:', topics);

const metadata = await admin.fetchTopicMetadata({ topics: ['my-topic'] });
console.log('Metadata:', metadata);

await admin.disconnect();
```

### Delete Topic

```javascript
await admin.deleteTopics({
  topics: ['my-topic']
});
```

---

## Configuration Reference

### Producer Options

| Option | Description | Default |
|--------|-------------|:-------:|
| `acks` | Acknowledgments (-1, 0, 1) | -1 |
| `timeout` | Request timeout ms | 30000 |
| `idempotent` | Idempotent producer | false |
| `maxInFlightRequests` | Max in-flight | 5 |
| `transactionalId` | Transaction ID | null |

### Consumer Options

| Option | Description | Default |
|--------|-------------|:-------:|
| `groupId` | Consumer group | Required |
| `sessionTimeout` | Session timeout ms | 30000 |
| `heartbeatInterval` | Heartbeat ms | 3000 |
| `maxBytesPerPartition` | Max bytes per partition | 1048576 |
| `autoCommit` | Auto commit | true |
| `autoCommitInterval` | Commit interval ms | 5000 |

---

## Error Handling

```javascript
const { Kafka, logLevel } = require('kafkajs');

const kafka = new Kafka({
  clientId: 'my-app',
  brokers: ['localhost:9092'],
  logLevel: logLevel.ERROR,
  retry: {
    initialRetryTime: 100,
    retries: 8
  }
});

const producer = kafka.producer();

producer.on('producer.disconnect', () => {
  console.log('Producer disconnected');
});

try {
  await producer.send({
    topic: 'events',
    messages: [{ value: 'message' }]
  });
} catch (error) {
  if (error.type === 'UNKNOWN_TOPIC_OR_PARTITION') {
    console.error('Topic does not exist');
  } else if (error.type === 'REQUEST_TIMED_OUT') {
    console.error('Request timed out');
  } else {
    console.error('Error:', error);
  }
}
```

---

## Graceful Shutdown

```javascript
const { Kafka } = require('kafkajs');

const kafka = new Kafka({
  clientId: 'my-app',
  brokers: ['localhost:9092']
});

const consumer = kafka.consumer({ groupId: 'my-group' });

const shutdown = async () => {
  console.log('Shutting down...');
  await consumer.disconnect();
  process.exit(0);
};

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);

async function run() {
  await consumer.connect();
  await consumer.subscribe({ topic: 'events' });

  await consumer.run({
    eachMessage: async ({ message }) => {
      console.log(message.value.toString());
    }
  });
}

run().catch(console.error);
```

---

## TypeScript Support

```typescript
import { Kafka, Producer, Consumer, Message } from 'kafkajs';

interface Event {
  id: string;
  timestamp: number;
  data: string;
}

const kafka = new Kafka({
  clientId: 'my-app',
  brokers: ['localhost:9092']
});

const producer: Producer = kafka.producer();

async function produceEvent(event: Event): Promise<void> {
  await producer.send({
    topic: 'events',
    messages: [{ value: JSON.stringify(event) }]
  });
}
```

---

## Compression

```javascript
const { CompressionTypes } = require('kafkajs');

await producer.send({
  topic: 'events',
  compression: CompressionTypes.GZIP,
  messages: [{ value: 'message' }]
});
```

Available compression types:
- `CompressionTypes.None`
- `CompressionTypes.GZIP`
- `CompressionTypes.Snappy`
- `CompressionTypes.LZ4`
- `CompressionTypes.ZSTD`

---

## Related Documentation

- [Drivers Overview](index.md) - All client drivers
- [Producer Guide](../../producers/index.md) - Producer patterns
- [Consumer Guide](../../consumers/index.md) - Consumer patterns
- [Schema Registry](../../schema-registry/index.md) - Schema management
