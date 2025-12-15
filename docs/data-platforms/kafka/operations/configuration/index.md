---
title: "Kafka Configuration"
description: "Apache Kafka configuration reference. Broker, producer, consumer, and topic configurations."
meta:
  - name: keywords
    content: "Kafka configuration, server.properties, broker config, Kafka settings"
---

# Kafka Configuration

Comprehensive configuration reference for Apache Kafka.

---

## Configuration Levels

| Level | Scope | Persistence | Priority |
|-------|-------|-------------|----------|
| **Static** | Broker | server.properties | Lowest |
| **Cluster-wide dynamic** | All brokers | Metadata | Medium |
| **Per-broker dynamic** | Single broker | Metadata | High |
| **Per-topic** | Single topic | Metadata | Highest |

---

## Broker Configuration

### Essential Settings

```properties
# server.properties

# Node identity
node.id=1
broker.id=1

# KRaft controller configuration
process.roles=broker,controller
controller.quorum.voters=1@localhost:9093

# Listeners
listeners=PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
advertised.listeners=PLAINTEXT://broker1:9092
controller.listener.names=CONTROLLER
inter.broker.listener.name=PLAINTEXT

# Log storage
log.dirs=/var/kafka-logs
num.partitions=3
default.replication.factor=3
min.insync.replicas=2

# Log retention
log.retention.hours=168
log.retention.bytes=-1
log.segment.bytes=1073741824

# Network
num.network.threads=3
num.io.threads=8
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600

# Replication
num.replica.fetchers=1
replica.fetch.max.bytes=1048576
replica.fetch.wait.max.ms=500
```

### Performance Settings

```properties
# Threading
num.network.threads=8
num.io.threads=16
num.replica.fetchers=4
num.recovery.threads.per.data.dir=4

# Request handling
queued.max.requests=500
request.timeout.ms=30000

# Network buffers
socket.send.buffer.bytes=1048576
socket.receive.buffer.bytes=1048576

# Batching (for replication)
replica.fetch.max.bytes=10485760
replica.fetch.min.bytes=1
replica.fetch.wait.max.ms=500
```

### Security Settings

```properties
# TLS
ssl.keystore.location=/etc/kafka/ssl/kafka.keystore.jks
ssl.keystore.password=password
ssl.key.password=password
ssl.truststore.location=/etc/kafka/ssl/kafka.truststore.jks
ssl.truststore.password=password
ssl.client.auth=required

# SASL
sasl.enabled.mechanisms=SCRAM-SHA-512
sasl.mechanism.inter.broker.protocol=SCRAM-SHA-512

# Authorization
authorizer.class.name=org.apache.kafka.metadata.authorizer.StandardAuthorizer
super.users=User:admin
allow.everyone.if.no.acl.found=false
```

---

## Topic Configuration

### Common Settings

| Configuration | Default | Description |
|---------------|---------|-------------|
| `cleanup.policy` | delete | delete or compact |
| `compression.type` | producer | none, gzip, snappy, lz4, zstd |
| `retention.ms` | 604800000 (7 days) | Retention time |
| `retention.bytes` | -1 (unlimited) | Retention size per partition |
| `segment.bytes` | 1073741824 (1GB) | Segment file size |
| `min.insync.replicas` | 1 | Minimum ISR for writes |
| `max.message.bytes` | 1048588 | Maximum message size |

### Creating Topics with Configuration

```bash
kafka-topics.sh --bootstrap-server kafka:9092 \
  --create \
  --topic events \
  --partitions 12 \
  --replication-factor 3 \
  --config retention.ms=86400000 \
  --config cleanup.policy=delete \
  --config compression.type=lz4 \
  --config min.insync.replicas=2
```

### Modifying Topic Configuration

```bash
# Add or update
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type topics \
  --entity-name events \
  --alter \
  --add-config retention.ms=172800000,max.message.bytes=10485760

# Remove (revert to default)
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type topics \
  --entity-name events \
  --alter \
  --delete-config retention.ms

# View configuration
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type topics \
  --entity-name events \
  --describe
```

---

## Producer Configuration

### Essential Settings

```properties
# Connection
bootstrap.servers=kafka1:9092,kafka2:9092,kafka3:9092
client.id=my-producer

# Reliability
acks=all
retries=2147483647
delivery.timeout.ms=120000
enable.idempotence=true

# Batching
batch.size=65536
linger.ms=5
buffer.memory=33554432

# Compression
compression.type=lz4

# Serialization
key.serializer=org.apache.kafka.common.serialization.StringSerializer
value.serializer=org.apache.kafka.common.serialization.StringSerializer
```

### Performance Tuning

| Setting | Low Latency | High Throughput |
|---------|-------------|-----------------|
| `acks` | 1 | all |
| `batch.size` | 16384 | 131072 |
| `linger.ms` | 0 | 10-50 |
| `compression.type` | none | lz4 |
| `buffer.memory` | 33554432 | 67108864 |

### Idempotent Producer

```properties
# Required for exactly-once
enable.idempotence=true
acks=all
retries=2147483647
max.in.flight.requests.per.connection=5
```

### Transactional Producer

```properties
enable.idempotence=true
transactional.id=my-transactional-producer
transaction.timeout.ms=60000
```

---

## Consumer Configuration

### Essential Settings

```properties
# Connection
bootstrap.servers=kafka1:9092,kafka2:9092,kafka3:9092
client.id=my-consumer

# Group
group.id=my-consumer-group
group.instance.id=consumer-1

# Offset management
auto.offset.reset=earliest
enable.auto.commit=false

# Fetching
fetch.min.bytes=1
fetch.max.bytes=52428800
fetch.max.wait.ms=500
max.poll.records=500
max.partition.fetch.bytes=1048576

# Session
session.timeout.ms=45000
heartbeat.interval.ms=3000
max.poll.interval.ms=300000

# Deserialization
key.deserializer=org.apache.kafka.common.serialization.StringDeserializer
value.deserializer=org.apache.kafka.common.serialization.StringDeserializer
```

### Performance Tuning

| Setting | Low Latency | High Throughput |
|---------|-------------|-----------------|
| `fetch.min.bytes` | 1 | 65536 |
| `fetch.max.wait.ms` | 100 | 500 |
| `max.poll.records` | 100 | 1000 |
| `max.partition.fetch.bytes` | 262144 | 1048576 |

### Static Membership

```properties
# Reduce rebalancing
group.instance.id=consumer-host-1
session.timeout.ms=300000
```

### Cooperative Rebalancing

```properties
partition.assignment.strategy=org.apache.kafka.clients.consumer.CooperativeStickyAssignor
```

---

## Dynamic Configuration

### Broker-Level

```bash
# Update single broker
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type brokers \
  --entity-name 1 \
  --alter \
  --add-config log.cleaner.threads=4

# Update all brokers (cluster-wide default)
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type brokers \
  --entity-default \
  --alter \
  --add-config log.cleaner.threads=4
```

### Dynamically Configurable Broker Settings

| Setting | Description |
|---------|-------------|
| `log.cleaner.threads` | Log cleaner threads |
| `log.cleaner.io.buffer.size` | Cleaner buffer size |
| `log.cleaner.dedupe.buffer.size` | Dedup buffer size |
| `log.cleaner.io.max.bytes.per.second` | Cleaner I/O rate |
| `log.retention.ms` | Default retention |
| `log.retention.bytes` | Default retention bytes |
| `message.max.bytes` | Maximum message size |
| `num.io.threads` | I/O threads |
| `num.network.threads` | Network threads |
| `num.replica.fetchers` | Replica fetchers |

---

## Client Quotas

### User Quotas

```bash
# Producer quota (bytes/sec)
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type users \
  --entity-name producer-user \
  --alter \
  --add-config producer_byte_rate=10485760

# Consumer quota (bytes/sec)
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type users \
  --entity-name consumer-user \
  --alter \
  --add-config consumer_byte_rate=20971520

# Request rate quota (percentage)
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type users \
  --entity-name any-user \
  --alter \
  --add-config request_percentage=50
```

### Client ID Quotas

```bash
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type clients \
  --entity-name my-client-id \
  --alter \
  --add-config producer_byte_rate=5242880
```

### Combined Quotas

```bash
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type users \
  --entity-name producer-user \
  --entity-type clients \
  --entity-name producer-client \
  --alter \
  --add-config producer_byte_rate=10485760
```

---

## Configuration Best Practices

### Production Checklist

**Broker:**
- [ ] `min.insync.replicas=2` (with RF=3)
- [ ] `unclean.leader.election.enable=false`
- [ ] `auto.create.topics.enable=false`
- [ ] `default.replication.factor=3`

**Producer:**
- [ ] `acks=all`
- [ ] `enable.idempotence=true`
- [ ] `retries=MAX_INT`

**Consumer:**
- [ ] `enable.auto.commit=false` (manual commits)
- [ ] `auto.offset.reset=earliest` or `latest` as appropriate

---

## Related Documentation

- [Operations Overview](../index.md) - Operations guide
- [Monitoring](../monitoring/index.md) - Metrics and alerting
- [Security](../../security/index.md) - Security configuration
- [Performance](../performance/index.md) - Performance tuning
