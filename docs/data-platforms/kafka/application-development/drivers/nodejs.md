---
title: "Kafka Node.js Client"
description: "Apache Kafka Node.js client guide using KafkaJS. Producer, consumer, and admin client usage with configuration, error handling, and best practices."
meta:
  - name: keywords
    content: "Kafka Node.js, KafkaJS, node-rdkafka, JavaScript Kafka, npm kafka, Kafka TypeScript"
---

# Kafka Node.js Client

The KafkaJS library provides a pure JavaScript Kafka client with full protocol support. This guide covers installation, configuration, and usage patterns for Node.js applications.

---

## Client Information

### KafkaJS (Recommended)

| | |
|---|---|
| **Library** | `kafkajs` |
| **Repository** | [github.com/tulios/kafkajs](https://github.com/tulios/kafkajs) |
| **Documentation** | [kafka.js.org](https://kafka.js.org/) |
| **Package** | [npm](https://www.npmjs.com/package/kafkajs) |
| **Current Version** | 2.2.x (as of 2025) |
| **Maintainer** | Tulio Ornelas and community |
| **License** | MIT |
| **Base** | Pure JavaScript (no native dependencies) |

### History

KafkaJS was created by Tulio Ornelas in 2018 as a pure JavaScript implementation of the Kafka protocol. Unlike librdkafka-based clients, KafkaJS requires no native compilation, making it ideal for serverless environments (AWS Lambda, Google Cloud Functions), containerized deployments, and situations where native compilation is problematic. It gained rapid adoption due to its modern async/await API and zero-dependency installation. KafkaJS implements the Kafka wire protocol directly in JavaScript, supporting transactions, idempotent producers, and most Kafka features.

### Alternative: node-rdkafka

For maximum performance at the cost of native dependencies:

| | |
|---|---|
| **Library** | `node-rdkafka` |
| **Repository** | [github.com/Blizzard/node-rdkafka](https://github.com/Blizzard/node-rdkafka) |
| **Documentation** | [blizzard.github.io/node-rdkafka](https://blizzard.github.io/node-rdkafka/current/) |
| **Package** | [npm](https://www.npmjs.com/package/node-rdkafka) |
| **Current Version** | 3.6.x (as of 2025) |
| **Maintainer** | Blizzard Entertainment |
| **License** | MIT |
| **Base** | librdkafka (C library) |

node-rdkafka was developed by Blizzard Entertainment and first released in 2016. It provides native Node.js bindings to librdkafka, offering higher throughput than KafkaJS at the cost of requiring native compilation. Best suited for high-throughput applications running in environments where native builds are manageable.

### Client Comparison

| Feature | KafkaJS | node-rdkafka |
|---------|---------|--------------|
| Installation | npm install | Requires build tools |
| Performance | Good | Excellent |
| Serverless | Excellent | Difficult |
| Memory footprint | Moderate | Lower |
| Docker builds | Simple | Complex |
| Cooperative rebalancing | No | Yes |

### Version Compatibility

| KafkaJS Version | Minimum Kafka Broker | Node.js |
|-----------------|---------------------|---------|
| 2.2.x | 0.10.0+ | 14+ |
| 2.1.x | 0.10.0+ | 12+ |
| 2.0.x | 0.10.0+ | 12+ |

### External Resources

- [KafkaJS Documentation](https://kafka.js.org/)
- [KafkaJS GitHub Examples](https://github.com/tulios/kafkajs/tree/master/examples)
- [node-rdkafka Documentation](https://blizzard.github.io/node-rdkafka/current/)
- [Confluent Developer Node.js Guide](https://developer.confluent.io/get-started/nodejs/)

---

## Installation

### npm

```bash
npm install kafkajs
```

### yarn

```bash
yarn add kafkajs
```

### pnpm

```bash
pnpm add kafkajs
```

### Alternative: node-rdkafka

For applications requiring maximum performance, `node-rdkafka` provides a librdkafka-based client:

```bash
npm install node-rdkafka
```

Note: `node-rdkafka` requires native dependencies and may have installation complexities. KafkaJS is recommended for most use cases.

---

## Producer

### Basic Producer

```javascript
const { Kafka } = require('kafkajs');

const kafka = new Kafka({
  clientId: 'order-service',
  brokers: ['kafka:9092']
});

const producer = kafka.producer();

async function run() {
  await producer.connect();

  await producer.send({
    topic: 'orders',
    messages: [
      {
        key: 'order-123',
        value: JSON.stringify({ id: 123, amount: 99.99 })
      }
    ]
  });

  await producer.disconnect();
}

run().catch(console.error);
```

### Production Producer Configuration

```javascript
const kafka = new Kafka({
  clientId: 'order-service-producer',
  brokers: ['kafka-1:9092', 'kafka-2:9092', 'kafka-3:9092'],

  // Connection timeout
  connectionTimeout: 30000,
  requestTimeout: 30000,

  // Retry configuration
  retry: {
    initialRetryTime: 100,
    retries: 8,
    maxRetryTime: 30000,
    multiplier: 2,
    factor: 0.2
  }
});

const producer = kafka.producer({
  // Durability
  allowAutoTopicCreation: false,
  transactionTimeout: 30000,

  // Idempotence
  idempotent: true,
  maxInFlightRequests: 5,

  // Batching
  compression: CompressionTypes.LZ4,

  // Retries - handled at client level
  retry: {
    maxRetryTime: 30000,
    initialRetryTime: 300,
    retries: 2147483647
  }
});

await producer.connect();
```

### Send with Headers

```javascript
await producer.send({
  topic: 'orders',
  messages: [
    {
      key: 'order-123',
      value: JSON.stringify({ id: 123 }),
      headers: {
        'correlation-id': 'abc-123',
        'source': 'order-service'
      }
    }
  ]
});
```

### Batch Send

```javascript
await producer.sendBatch({
  topicMessages: [
    {
      topic: 'orders',
      messages: [
        { key: '1', value: JSON.stringify({ id: 1 }) },
        { key: '2', value: JSON.stringify({ id: 2 }) }
      ]
    },
    {
      topic: 'audit',
      messages: [
        { value: JSON.stringify({ event: 'order_created' }) }
      ]
    }
  ]
});
```

### Custom Partitioner

```javascript
const producer = kafka.producer({
  createPartitioner: () => {
    return ({ topic, partitionMetadata, message }) => {
      const numPartitions = partitionMetadata.length;

      // Custom logic: route by region prefix
      if (message.key) {
        const key = message.key.toString();
        if (key.startsWith('US-')) return 0;
        if (key.startsWith('EU-')) return 1;
      }

      // Default: hash-based partitioning
      const hash = murmur3(message.key || '');
      return Math.abs(hash) % numPartitions;
    };
  }
});
```

### Producer with Error Handling

```javascript
class ProducerService {
  constructor(kafka) {
    this.producer = kafka.producer();
    this.connected = false;
  }

  async connect() {
    if (!this.connected) {
      await this.producer.connect();
      this.connected = true;
    }
  }

  async send(topic, messages) {
    try {
      await this.connect();

      const result = await this.producer.send({
        topic,
        messages,
        acks: -1,
        timeout: 30000
      });

      return result;
    } catch (error) {
      console.error('Send failed:', error);

      if (error.name === 'KafkaJSNumberOfRetriesExceeded') {
        // All retries exhausted
        throw new Error('Failed to send after retries');
      }

      if (error.type === 'TOPIC_AUTHORIZATION_FAILED') {
        throw new Error('Not authorized to write to topic');
      }

      throw error;
    }
  }

  async disconnect() {
    if (this.connected) {
      await this.producer.disconnect();
      this.connected = false;
    }
  }
}
```

---

## Consumer

### Basic Consumer

```javascript
const { Kafka } = require('kafkajs');

const kafka = new Kafka({
  clientId: 'order-service',
  brokers: ['kafka:9092']
});

const consumer = kafka.consumer({ groupId: 'order-processors' });

async function run() {
  await consumer.connect();
  await consumer.subscribe({ topic: 'orders', fromBeginning: true });

  await consumer.run({
    eachMessage: async ({ topic, partition, message }) => {
      console.log({
        topic,
        partition,
        offset: message.offset,
        key: message.key?.toString(),
        value: message.value?.toString()
      });
    }
  });
}

run().catch(console.error);
```

### Production Consumer Configuration

```javascript
const consumer = kafka.consumer({
  groupId: 'order-processors',

  // Session management
  sessionTimeout: 45000,
  heartbeatInterval: 15000,

  // Rebalancing
  rebalanceTimeout: 60000,
  partitionAssigners: [PartitionAssigners.cooperativeSticky],

  // Offset management
  allowAutoTopicCreation: false,

  // Fetch configuration
  minBytes: 1,
  maxBytes: 10485760,
  maxWaitTimeInMs: 5000,

  // Retry
  retry: {
    retries: 10,
    initialRetryTime: 300,
    maxRetryTime: 30000
  }
});

await consumer.connect();
```

### Manual Offset Commit

```javascript
await consumer.run({
  autoCommit: false,
  eachMessage: async ({ topic, partition, message }) => {
    await processMessage(message);

    // Commit after processing
    await consumer.commitOffsets([
      {
        topic,
        partition,
        offset: (parseInt(message.offset) + 1).toString()
      }
    ]);
  }
});
```

### Batch Processing

```javascript
await consumer.run({
  eachBatchAutoResolve: false,
  eachBatch: async ({
    batch,
    resolveOffset,
    heartbeat,
    isRunning,
    isStale
  }) => {
    const { topic, partition } = batch;

    for (const message of batch.messages) {
      if (!isRunning() || isStale()) break;

      await processMessage(message);

      // Resolve offset to commit
      resolveOffset(message.offset);

      // Send heartbeat to avoid rebalance
      await heartbeat();
    }
  }
});
```

### Rebalance Listener

```javascript
const consumer = kafka.consumer({
  groupId: 'order-processors'
});

consumer.on(consumer.events.GROUP_JOIN, ({ payload }) => {
  console.log('Joined group:', payload);
});

consumer.on(consumer.events.REBALANCING, ({ payload }) => {
  console.log('Rebalancing:', payload);
  // Prepare for partition reassignment
});

consumer.on(consumer.events.CONNECT, ({ payload }) => {
  console.log('Connected:', payload);
});

consumer.on(consumer.events.DISCONNECT, ({ payload }) => {
  console.log('Disconnected:', payload);
});

consumer.on(consumer.events.CRASH, ({ payload }) => {
  console.error('Consumer crashed:', payload.error);
  // Handle crash - may need to restart
});
```

### Graceful Shutdown

```javascript
const consumer = kafka.consumer({ groupId: 'order-processors' });

const signals = ['SIGTERM', 'SIGINT'];
const shutdown = async () => {
  console.log('Shutting down...');
  await consumer.disconnect();
  process.exit(0);
};

signals.forEach(signal => {
  process.on(signal, shutdown);
});

async function run() {
  await consumer.connect();
  await consumer.subscribe({ topic: 'orders' });

  await consumer.run({
    eachMessage: async ({ message }) => {
      await processMessage(message);
    }
  });
}

run().catch(async (error) => {
  console.error('Error:', error);
  await shutdown();
});
```

### Seek and Pause/Resume

```javascript
// Seek to specific offset
await consumer.seek({
  topic: 'orders',
  partition: 0,
  offset: '1000'
});

// Seek to beginning
await consumer.seek({
  topic: 'orders',
  partition: 0,
  offset: '-2'  // Kafka's OFFSET_BEGINNING
});

// Pause consumption
consumer.pause([
  { topic: 'orders', partitions: [0, 1] }
]);

// Resume consumption
consumer.resume([
  { topic: 'orders', partitions: [0, 1] }
]);
```

---

## Admin Client

### Create Topics

```javascript
const kafka = new Kafka({
  clientId: 'admin',
  brokers: ['kafka:9092']
});

const admin = kafka.admin();

await admin.connect();

await admin.createTopics({
  topics: [
    {
      topic: 'orders',
      numPartitions: 6,
      replicationFactor: 3,
      configEntries: [
        { name: 'retention.ms', value: '604800000' },
        { name: 'cleanup.policy', value: 'delete' }
      ]
    }
  ],
  waitForLeaders: true,
  timeout: 30000
});

await admin.disconnect();
```

### Describe Topics

```javascript
const topics = await admin.fetchTopicMetadata({ topics: ['orders'] });

for (const topic of topics.topics) {
  console.log(`Topic: ${topic.name}`);
  for (const partition of topic.partitions) {
    console.log(`  Partition ${partition.partitionId}:`);
    console.log(`    Leader: ${partition.leader}`);
    console.log(`    Replicas: ${partition.replicas}`);
    console.log(`    ISR: ${partition.isr}`);
  }
}
```

### List Topics

```javascript
const topics = await admin.listTopics();
console.log('Topics:', topics);
```

### Delete Topics

```javascript
await admin.deleteTopics({
  topics: ['old-topic'],
  timeout: 30000
});
```

### List Consumer Groups

```javascript
const groups = await admin.listGroups();

for (const group of groups.groups) {
  console.log(`Group: ${group.groupId} (protocol: ${group.protocolType})`);
}
```

### Describe Consumer Group

```javascript
const descriptions = await admin.describeGroups(['order-processors']);

for (const group of descriptions.groups) {
  console.log(`Group: ${group.groupId}`);
  console.log(`State: ${group.state}`);
  console.log(`Protocol: ${group.protocol}`);

  for (const member of group.members) {
    console.log(`  Member: ${member.memberId}`);
    console.log(`    Client: ${member.clientId}`);
  }
}
```

### Reset Consumer Group Offsets

```javascript
await admin.resetOffsets({
  groupId: 'order-processors',
  topic: 'orders',
  earliest: true  // or specify offset: '1000'
});
```

---

## Transactions

### Transactional Producer

```javascript
const producer = kafka.producer({
  transactionalId: 'order-processor-txn',
  maxInFlightRequests: 1,
  idempotent: true
});

await producer.connect();

const transaction = await producer.transaction();

try {
  await transaction.send({
    topic: 'orders',
    messages: [{ key: '1', value: 'order data' }]
  });

  await transaction.send({
    topic: 'audit',
    messages: [{ value: 'order created' }]
  });

  await transaction.commit();
} catch (error) {
  await transaction.abort();
  throw error;
}
```

### Consume-Transform-Produce

```javascript
const consumer = kafka.consumer({
  groupId: 'processor',
  isolation: 'read_committed'
});

const producer = kafka.producer({
  transactionalId: 'processor-txn',
  idempotent: true
});

await consumer.connect();
await producer.connect();
await consumer.subscribe({ topic: 'input' });

await consumer.run({
  eachBatch: async ({
    batch,
    resolveOffset,
    heartbeat,
    commitOffsetsIfNecessary
  }) => {
    const transaction = await producer.transaction();

    try {
      for (const message of batch.messages) {
        const transformed = transform(message.value.toString());

        await transaction.send({
          topic: 'output',
          messages: [{ key: message.key, value: transformed }]
        });

        resolveOffset(message.offset);
        await heartbeat();
      }

      // Commit consumer offsets in transaction
      await transaction.sendOffsets({
        consumerGroupId: 'processor',
        topics: [
          {
            topic: batch.topic,
            partitions: [
              {
                partition: batch.partition,
                offset: (parseInt(batch.lastOffset()) + 1).toString()
              }
            ]
          }
        ]
      });

      await transaction.commit();
    } catch (error) {
      await transaction.abort();
      throw error;
    }
  }
});
```

---

## Error Handling

### Producer Error Handling

```javascript
try {
  await producer.send({
    topic: 'orders',
    messages: [{ key: 'key', value: 'value' }]
  });
} catch (error) {
  if (error.name === 'KafkaJSProtocolError') {
    // Protocol-level error
    if (error.type === 'TOPIC_AUTHORIZATION_FAILED') {
      console.error('Not authorized to write to topic');
    } else if (error.type === 'MESSAGE_TOO_LARGE') {
      console.error('Message exceeds max size');
      sendToDeadLetterQueue(message);
    }
  } else if (error.name === 'KafkaJSNumberOfRetriesExceeded') {
    console.error('All retries exhausted');
  } else if (error.name === 'KafkaJSConnectionError') {
    console.error('Connection error:', error.message);
  } else {
    console.error('Unknown error:', error);
  }
}
```

### Consumer Error Handling

```javascript
await consumer.run({
  eachMessage: async ({ topic, partition, message }) => {
    try {
      await processMessage(message);
    } catch (error) {
      console.error('Processing error:', error);

      // Send to dead letter queue
      await deadLetterProducer.send({
        topic: 'orders-dlq',
        messages: [
          {
            key: message.key,
            value: message.value,
            headers: {
              ...message.headers,
              'original-topic': topic,
              'original-partition': partition.toString(),
              'original-offset': message.offset,
              'error': error.message
            }
          }
        ]
      });
    }
  }
});

// Consumer-level error handling
consumer.on(consumer.events.CRASH, async ({ payload: { error } }) => {
  console.error('Consumer crashed:', error);

  // Restart consumer
  await consumer.disconnect();
  await consumer.connect();
  await consumer.subscribe({ topic: 'orders' });
});
```

### Retry with Exponential Backoff

```javascript
async function sendWithRetry(producer, message, maxRetries = 3) {
  let lastError;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await producer.send(message);
    } catch (error) {
      lastError = error;

      if (error.type === 'TOPIC_AUTHORIZATION_FAILED') {
        // Don't retry authorization errors
        throw error;
      }

      const backoff = Math.min(1000 * Math.pow(2, attempt), 30000);
      await new Promise(resolve => setTimeout(resolve, backoff));
    }
  }

  throw lastError;
}
```

---

## Testing

### Mock Producer

```javascript
class MockProducer {
  constructor() {
    this.messages = [];
    this.connected = false;
  }

  async connect() {
    this.connected = true;
  }

  async send({ topic, messages }) {
    if (!this.connected) {
      throw new Error('Not connected');
    }

    for (const message of messages) {
      this.messages.push({ topic, ...message });
    }

    return messages.map((_, index) => ({
      topicName: topic,
      partition: 0,
      offset: String(index)
    }));
  }

  async disconnect() {
    this.connected = false;
  }

  getMessages() {
    return this.messages;
  }

  clear() {
    this.messages = [];
  }
}

// Usage in tests
describe('OrderService', () => {
  it('should send order to Kafka', async () => {
    const mockProducer = new MockProducer();
    const service = new OrderService(mockProducer);

    await mockProducer.connect();
    await service.createOrder({ id: 123, amount: 99.99 });

    const messages = mockProducer.getMessages();
    expect(messages).toHaveLength(1);
    expect(messages[0].topic).toBe('orders');
    expect(JSON.parse(messages[0].value)).toEqual({ id: 123, amount: 99.99 });
  });
});
```

### Integration Testing with Testcontainers

```javascript
const { Kafka } = require('kafkajs');
const { GenericContainer } = require('testcontainers');

describe('Kafka Integration', () => {
  let container;
  let kafka;

  beforeAll(async () => {
    container = await new GenericContainer('confluentinc/cp-kafka')
      .withExposedPorts(9093)
      .withEnvironment({
        'KAFKA_BROKER_ID': '1',
        'KAFKA_LISTENER_SECURITY_PROTOCOL_MAP': 'PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT',
        'KAFKA_ADVERTISED_LISTENERS': 'PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9093',
        'KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR': '1'
      })
      .start();

    const host = container.getHost();
    const port = container.getMappedPort(9093);

    kafka = new Kafka({
      clientId: 'test',
      brokers: [`${host}:${port}`]
    });
  }, 60000);

  afterAll(async () => {
    await container.stop();
  });

  it('should produce and consume messages', async () => {
    const producer = kafka.producer();
    const consumer = kafka.consumer({ groupId: 'test' });

    await producer.connect();
    await consumer.connect();

    await consumer.subscribe({ topic: 'test', fromBeginning: true });

    const messages = [];
    await consumer.run({
      eachMessage: async ({ message }) => {
        messages.push(message.value.toString());
      }
    });

    await producer.send({
      topic: 'test',
      messages: [{ value: 'test message' }]
    });

    // Wait for message
    await new Promise(resolve => setTimeout(resolve, 1000));

    expect(messages).toContain('test message');

    await producer.disconnect();
    await consumer.disconnect();
  });
});
```

### Unit Testing with Jest

```javascript
jest.mock('kafkajs');

const { Kafka } = require('kafkajs');
const OrderService = require('./order-service');

describe('OrderService', () => {
  let mockProducer;
  let mockSend;

  beforeEach(() => {
    mockSend = jest.fn().mockResolvedValue([
      { topicName: 'orders', partition: 0, offset: '0' }
    ]);

    mockProducer = {
      connect: jest.fn().mockResolvedValue(undefined),
      disconnect: jest.fn().mockResolvedValue(undefined),
      send: mockSend
    };

    Kafka.mockImplementation(() => ({
      producer: () => mockProducer
    }));
  });

  it('should send order message', async () => {
    const service = new OrderService();
    await service.connect();

    await service.createOrder({ id: 123, amount: 99.99 });

    expect(mockSend).toHaveBeenCalledWith({
      topic: 'orders',
      messages: [
        expect.objectContaining({
          key: '123',
          value: expect.any(String)
        })
      ]
    });
  });
});
```

---

## Related Documentation

- [Producer Development](../producers/index.md) - Producer patterns
- [Consumer Development](../consumers/index.md) - Consumer patterns
- [Transactions](../producers/transactions.md) - Transaction patterns