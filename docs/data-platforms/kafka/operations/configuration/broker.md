---
title: "Kafka Broker Configuration"
description: "Apache Kafka broker configuration reference. server.properties settings for KRaft, networking, storage, replication, and performance tuning."
meta:
  - name: keywords
    content: "Kafka broker configuration, server.properties, broker settings, cluster configuration"
---

# Broker Configuration

Broker configuration controls the behavior of Kafka broker nodes. Configuration is defined in `server.properties` and through dynamic configuration updates.

---

## Configuration Categories

| Category | Description | Dynamic |
|----------|-------------|:-------:|
| **Node Identity** | Broker and controller identifiers | ❌ |
| **Listeners** | Network endpoints and protocols | ❌ |
| **Storage** | Log directories and retention | Partial |
| **Replication** | Replica fetching and ISR management | Partial |
| **Network** | Threading and buffer sizes | ✅ |
| **Security** | TLS, SASL, and authorization | ❌ |

---

## Node Identity

### KRaft Mode (Kafka 3.0+)

```properties
# Unique node identifier (required)
node.id=1

# Node roles: broker, controller, or both
process.roles=broker,controller

# Controller quorum voters (id@host:port)
controller.quorum.voters=1@controller1:9093,2@controller2:9093,3@controller3:9093

# Controller listener name
controller.listener.names=CONTROLLER
```

| Setting | Description | Required |
|---------|-------------|:--------:|
| `node.id` | Unique identifier for this node | ✅ |
| `process.roles` | Comma-separated roles: `broker`, `controller`, or both | ✅ |
| `controller.quorum.voters` | List of controller voters | ✅ |
| `controller.listener.names` | Listener name for controller communication | ✅ |

### ZooKeeper Mode (Legacy)

```properties
# Broker ID (must be unique in cluster)
broker.id=1

# ZooKeeper connection
zookeeper.connect=zk1:2181,zk2:2181,zk3:2181/kafka
zookeeper.connection.timeout.ms=18000
zookeeper.session.timeout.ms=18000
```

!!! warning "ZooKeeper Deprecation"
    ZooKeeper mode is deprecated as of Kafka 3.5 and will be removed in Kafka 4.0. New deployments should use KRaft mode.

---

## Listeners

Listeners define network endpoints where brokers accept client connections.

### Listener Configuration

```properties
# Define listeners (protocol://host:port)
listeners=PLAINTEXT://0.0.0.0:9092,SSL://0.0.0.0:9093,SASL_SSL://0.0.0.0:9094

# Advertised listeners (what clients see)
advertised.listeners=PLAINTEXT://broker1.example.com:9092,SSL://broker1.example.com:9093

# Map listener names to security protocols
listener.security.protocol.map=PLAINTEXT:PLAINTEXT,SSL:SSL,SASL_SSL:SASL_SSL,CONTROLLER:PLAINTEXT

# Inter-broker communication listener
inter.broker.listener.name=PLAINTEXT

# Controller listener (KRaft only)
controller.listener.names=CONTROLLER
```

### Listener Types

| Protocol | Encryption | Authentication | Use Case |
|----------|:----------:|:--------------:|----------|
| `PLAINTEXT` | ❌ | ❌ | Development, internal networks |
| `SSL` | ✅ | Optional (mTLS) | Encrypted communication |
| `SASL_PLAINTEXT` | ❌ | ✅ | Authentication without encryption |
| `SASL_SSL` | ✅ | ✅ | Production recommended |

### Multi-Network Configuration

```properties
# Separate internal and external listeners
listeners=INTERNAL://0.0.0.0:9092,EXTERNAL://0.0.0.0:9093

# Different advertised addresses per listener
advertised.listeners=INTERNAL://broker1.internal:9092,EXTERNAL://broker1.public.example.com:9093

# Security protocol mapping
listener.security.protocol.map=INTERNAL:PLAINTEXT,EXTERNAL:SASL_SSL

# Use internal listener for inter-broker communication
inter.broker.listener.name=INTERNAL
```

---

## Storage Configuration

### Log Directories

```properties
# Log directory (single)
log.dir=/var/kafka-logs

# Multiple log directories (comma-separated)
log.dirs=/data1/kafka-logs,/data2/kafka-logs,/data3/kafka-logs
```

!!! tip "Multiple Log Directories"
    Using multiple log directories across different disks improves I/O throughput. Kafka distributes partitions across directories.

### Segment Configuration

```properties
# Segment file size (default: 1GB)
log.segment.bytes=1073741824

# Time before segment is rolled (default: 7 days)
log.roll.hours=168
log.roll.ms=604800000

# Index file size
log.index.size.max.bytes=10485760

# Index interval (bytes between index entries)
log.index.interval.bytes=4096
```

### Retention Configuration

```properties
# Time-based retention (default: 7 days)
log.retention.hours=168
log.retention.minutes=10080
log.retention.ms=604800000

# Size-based retention per partition (default: unlimited)
log.retention.bytes=-1

# Check interval for retention policy
log.retention.check.interval.ms=300000

# Delete or compact
log.cleanup.policy=delete
```

| Setting | Default | Dynamic | Description |
|---------|---------|:-------:|-------------|
| `log.retention.ms` | 604800000 | ✅ | Retention time in ms |
| `log.retention.bytes` | -1 | ✅ | Max bytes per partition |
| `log.segment.bytes` | 1073741824 | ✅ | Segment file size |
| `log.cleanup.policy` | delete | ✅ | delete or compact |

### Log Compaction

```properties
# Enable compaction for specific topics via topic config
# Broker-level compaction settings:

# Compaction threads
log.cleaner.threads=1

# Compaction buffer size
log.cleaner.dedupe.buffer.size=134217728

# I/O buffer size per cleaner thread
log.cleaner.io.buffer.size=524288

# I/O throughput limit (bytes/sec, -1 = unlimited)
log.cleaner.io.max.bytes.per.second=-1

# Minimum ratio of dirty log to total log to trigger compaction
log.cleaner.min.cleanable.ratio=0.5

# Minimum time message remains uncompacted
log.cleaner.min.compaction.lag.ms=0

# Maximum time message remains uncompacted
log.cleaner.max.compaction.lag.ms=9223372036854775807

# Delete retention for tombstones
log.cleaner.delete.retention.ms=86400000
```

---

## Replication Configuration

```properties
# Default replication factor for auto-created topics
default.replication.factor=3

# Minimum ISR for writes when acks=all
min.insync.replicas=2

# Replica fetcher threads
num.replica.fetchers=1

# Replica fetch settings
replica.fetch.max.bytes=1048576
replica.fetch.min.bytes=1
replica.fetch.wait.max.ms=500

# Replica lag
replica.lag.time.max.ms=30000

# Allow unclean leader election
unclean.leader.election.enable=false
```

| Setting | Default | Recommended | Description |
|---------|---------|-------------|-------------|
| `default.replication.factor` | 1 | 3 | RF for auto-created topics |
| `min.insync.replicas` | 1 | 2 | Minimum ISR for acks=all |
| `unclean.leader.election.enable` | false | false | Allow out-of-sync replica as leader |
| `replica.lag.time.max.ms` | 30000 | 30000 | Max lag before removing from ISR |

!!! danger "Unclean Leader Election"
    Setting `unclean.leader.election.enable=true` may result in data loss. An out-of-sync replica becoming leader means committed messages on the previous leader may be lost.

---

## Network Configuration

### Thread Pool Sizing

```properties
# Network threads (handle connections)
num.network.threads=3

# I/O threads (handle requests)
num.io.threads=8

# Background threads
background.threads=10

# Request handler threads
num.recovery.threads.per.data.dir=1
```

**Sizing Guidelines:**

| Setting | Formula | Notes |
|---------|---------|-------|
| `num.network.threads` | 2-3 per listener | Handles connection I/O |
| `num.io.threads` | 2x CPU cores | Handles request processing |
| `num.recovery.threads.per.data.dir` | 1-2 per disk | Parallel log recovery on startup |

### Buffer Sizes

```properties
# Socket buffers
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400

# Maximum request size
socket.request.max.bytes=104857600

# Request queue
queued.max.requests=500
```

### Request Processing

```properties
# Request timeout
request.timeout.ms=30000

# Maximum time request can wait in queue
queued.max.request.bytes=104857600

# Connections per IP
max.connections.per.ip=100
max.connections.per.ip.overrides=10.0.0.1:200
```

---

## Topic Defaults

These settings apply to topics when not overridden at the topic level.

```properties
# Default partition count
num.partitions=3

# Auto-create topics
auto.create.topics.enable=false

# Delete topics
delete.topic.enable=true

# Compression
compression.type=producer

# Maximum message size
message.max.bytes=1048588

# Replication settings
default.replication.factor=3
min.insync.replicas=2
```

!!! warning "Auto-Create Topics"
    In production, `auto.create.topics.enable` should be `false`. Auto-created topics use default settings and bypass governance controls.

---

## Dynamic Configuration

Certain broker settings can be modified without restart.

### Applying Dynamic Configuration

```bash
# Per-broker configuration
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type brokers \
  --entity-name 1 \
  --alter \
  --add-config num.io.threads=16

# Cluster-wide default
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type brokers \
  --entity-default \
  --alter \
  --add-config log.retention.ms=86400000

# View configuration
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type brokers \
  --entity-name 1 \
  --describe
```

### Dynamically Configurable Settings

| Setting | Scope | Description |
|---------|-------|-------------|
| `log.cleaner.threads` | Broker | Compaction threads |
| `log.cleaner.io.buffer.size` | Broker | Cleaner buffer |
| `log.cleaner.io.max.bytes.per.second` | Broker | Cleaner I/O limit |
| `log.retention.ms` | Broker/Cluster | Retention time |
| `log.retention.bytes` | Broker/Cluster | Retention size |
| `message.max.bytes` | Broker/Cluster | Max message size |
| `num.io.threads` | Broker | I/O thread count |
| `num.network.threads` | Broker | Network thread count |
| `num.replica.fetchers` | Broker | Replica fetcher count |
| `ssl.keystore.location` | Broker | SSL keystore path |
| `ssl.keystore.password` | Broker | SSL keystore password |

---

## JVM and OS Tuning

### Recommended JVM Options

```bash
# jvm.options or KAFKA_HEAP_OPTS

# Heap size (typically 6-8GB max)
-Xms6g
-Xmx6g

# GC settings (G1GC recommended)
-XX:+UseG1GC
-XX:MaxGCPauseMillis=20
-XX:InitiatingHeapOccupancyPercent=35

# GC logging
-Xlog:gc*:file=/var/log/kafka/gc.log:time,level,tags:filecount=10,filesize=100M
```

### OS Tuning

```bash
# File descriptors (per process)
ulimit -n 100000

# sysctl settings
vm.swappiness=1
vm.dirty_background_ratio=5
vm.dirty_ratio=60
net.core.wmem_default=131072
net.core.rmem_default=131072
net.ipv4.tcp_wmem=4096 65536 2048000
net.ipv4.tcp_rmem=4096 65536 2048000
```

---

## Production Checklist

| Category | Setting | Recommended Value |
|----------|---------|-------------------|
| **Reliability** | `min.insync.replicas` | 2 (with RF=3) |
| | `unclean.leader.election.enable` | false |
| | `default.replication.factor` | 3 |
| **Security** | `auto.create.topics.enable` | false |
| | `allow.everyone.if.no.acl.found` | false |
| **Performance** | `num.io.threads` | 2× CPU cores |
| | `num.network.threads` | 2-3 per listener |
| **Monitoring** | `metric.reporters` | JMX or Prometheus |

---

## Related Documentation

- [Configuration Overview](index.md) - Configuration guide
- [Topic Configuration](topic.md) - Topic settings
- [Tiered Storage](tiered-storage.md) - Remote storage configuration
- [Performance](../performance/index.md) - Performance tuning
- [Security](../../security/index.md) - Security configuration
