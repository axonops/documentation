---
title: "Getting Started with Kafka"
description: "Quick start guide for Apache Kafka. Installation options, client driver setup, and first steps with producers and consumers."
meta:
  - name: keywords
    content: "Kafka getting started, Kafka installation, Kafka quickstart, Kafka setup"
---

# Getting Started with Kafka

This guide covers Kafka installation, client setup, and basic operations to begin working with event streaming.

---

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **Java** | JDK 11 (3.x) / JDK 17 (4.0) | JDK 17 or 21 |
| **Memory** | 4 GB | 8+ GB |
| **Disk** | 10 GB | SSD recommended |
| **OS** | Linux, macOS, Windows | Linux for production |

---

## Version Compatibility

### JDK Compatibility

Kafka components have different JDK support levels. Kafka 4.0 introduced significant changes to Java version requirements.

**Kafka 4.0:**

| Component | Java 11 | Java 17 | Java 21 |
|-----------|:-------:|:-------:|:-------:|
| **Kafka Clients** | ✅ | ✅ | ✅ |
| **Kafka Streams** | ✅ | ✅ | ✅ |
| **Kafka Connect** | ❌ | ✅ | ✅ |
| **Kafka Server** | ❌ | ✅ | ✅ |

Legend: ✅ Supported | ❌ Not Supported

!!! warning "Java 8 and 11 Changes in Kafka 4.0"
    - Java 8 support is completely removed in Kafka 4.0
    - Java 11 is no longer supported for Connect and Server components
    - Clients and Streams still support Java 11 for backward compatibility

**Kafka 3.x:**

| Component | Java 8 | Java 11 | Java 17 |
|-----------|:------:|:-------:|:-------:|
| **All Components** | ✅ | ✅ | ✅ |

### Client-Broker Compatibility

Kafka maintains bidirectional compatibility between clients and brokers within certain version ranges.

**Client/Broker forward compatibility with Kafka 4.0:**

| Client Version | Module | 4.0 Compatibility | Notes |
|---------------|--------|:-----------------:|-------|
| **0.x, 1.x, 2.0** | All | ❌ | Pre-0.10.x protocols removed ([KIP-896](https://cwiki.apache.org/confluence/x/K5sODg)) |
| **2.1 - 2.8** | Client | ⚠️ Partial | Some consumer/producer changes |
| **2.1 - 2.8** | Streams | ⚠️ Limited | API changes may affect applications |
| **2.1 - 2.8** | Connect | ⚠️ Limited | Connector compatibility varies |
| **3.x** | All | ✅ Full | Fully compatible |

Legend: ✅ Full | ⚠️ Partial | ❌ Not Compatible

!!! warning "Kafka 4.0 Protocol Changes"
    - Pre-0.10.x protocol versions are fully removed in Kafka 4.0 ([KIP-896](https://cwiki.apache.org/confluence/x/K5sODg))
    - The `--zookeeper` option in AdminClient commands has been removed; use `--bootstrap-server` instead
    - Clients older than 2.1 must be upgraded before connecting to Kafka 4.0 brokers

**General compatibility guarantees:**

- Clients can communicate with brokers of the same or adjacent major versions
- Protocol versioning allows automatic feature negotiation
- Older clients may not access features introduced in newer broker versions

### KRaft Version Compatibility

KRaft clusters have specific version requirements for controllers and brokers.

**Server compatibility with Kafka 4.0:**

| KRaft Cluster Version | 4.0 Dynamic Voter | 4.0 Static Voter |
|----------------------|:-----------------:|:----------------:|
| **Before 3.2.x** | ❌ | ❌ |
| **3.3.x - 3.8.x** | ❌ | ✅ |
| **3.9.x** | ✅ | ✅ |
| **4.0.x** | ✅ | ✅ |

!!! warning "Static to Dynamic Voter Migration"
    Upgrading a cluster from static voter to dynamic voter configuration is not supported. See [KAFKA-16538](https://issues.apache.org/jira/browse/KAFKA-16538) for details.

### Feature Version Requirements

| Feature | Minimum Version | Notes |
|---------|-----------------|-------|
| **KRaft (production)** | 3.3 | ZooKeeper still required for some features until 3.5 |
| **KRaft (full feature parity)** | 3.5 | All features available without ZooKeeper |
| **Tiered Storage** | 3.6 | Early access |
| **Share Groups** | 4.0 | KIP-932 |
| **ZooKeeper removal** | 4.0 | ZooKeeper mode deprecated |

---

## Installation Options

| Option | Use Case | Complexity |
|--------|----------|------------|
| [Local Installation](installation/index.md) | Development, learning | Low |
| [Docker](installation/docker.md) | Development, CI/CD | Low |
| [Kubernetes](../cloud/kubernetes/index.md) | Production, cloud-native | Medium |
| [Managed Service](installation/managed.md) | Production without operational overhead | Low |

---

## Quick Start

### 1. Download and Extract

```bash
# Download Kafka
curl -O https://downloads.apache.org/kafka/4.1.1/kafka_2.13-4.1.1.tgz

# Extract
tar -xzf kafka_2.13-4.1.1.tgz
cd kafka_2.13-4.1.1
```

### 2. Start Kafka (KRaft Mode)

Kafka 3.3+ supports KRaft mode, eliminating the ZooKeeper dependency.

```bash
# Generate cluster ID
KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"

# Format storage
bin/kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c config/kraft/server.properties

# Start Kafka
bin/kafka-server-start.sh config/kraft/server.properties
```

### 3. Create a Topic

```bash
bin/kafka-topics.sh --create \
  --topic quickstart-events \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1
```

### 4. Produce Messages

```bash
bin/kafka-console-producer.sh \
  --topic quickstart-events \
  --bootstrap-server localhost:9092
```

Type messages and press Enter to send each one. Press Ctrl+C to exit.

### 5. Consume Messages

```bash
bin/kafka-console-consumer.sh \
  --topic quickstart-events \
  --from-beginning \
  --bootstrap-server localhost:9092
```

---

## Client Drivers

Kafka provides official and community clients for multiple languages.

| Language | Client | Documentation |
|----------|--------|---------------|
| **Java** | Apache Kafka Client | [Driver Guide](drivers/java.md) |
| **Python** | confluent-kafka-python | [Driver Guide](drivers/python.md) |
| **Go** | confluent-kafka-go | [Driver Guide](drivers/go.md) |
| **Node.js** | kafkajs | [Driver Guide](drivers/nodejs.md) |
| **.NET** | confluent-kafka-dotnet | [Driver Guide](drivers/dotnet.md) |

→ [Client Drivers](drivers/index.md)

---

## Verification

After installation, verify the cluster is operational:

```bash
# Check broker status
bin/kafka-broker-api-versions.sh --bootstrap-server localhost:9092

# List topics
bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Describe cluster
bin/kafka-metadata.sh --snapshot /tmp/kraft-combined-logs/__cluster_metadata-0/00000000000000000000.log --command "describe"
```

---

## Configuration

### Essential Broker Settings

| Property | Description | Default |
|----------|-------------|---------|
| `broker.id` | Unique broker identifier | Required |
| `listeners` | Network listeners | `PLAINTEXT://:9092` |
| `log.dirs` | Data directory | `/tmp/kafka-logs` |
| `num.partitions` | Default partitions for new topics | 1 |
| `default.replication.factor` | Default replication factor | 1 |

### Production Recommendations

| Setting | Development | Production |
|---------|-------------|------------|
| `log.dirs` | Single directory | Multiple directories on separate disks |
| `num.partitions` | 1-3 | Based on throughput requirements |
| `default.replication.factor` | 1 | 3 |
| `min.insync.replicas` | 1 | 2 |

→ [Configuration Reference](../operations/configuration/index.md)

---

## Next Steps

| Goal | Documentation |
|------|---------------|
| Understand Kafka concepts | [Event Streaming Concepts](../concepts/index.md) |
| Build a producer application | [Producer Guide](../application-development/producers/index.md) |
| Build a consumer application | [Consumer Guide](../application-development/consumers/index.md) |
| Set up Kafka Connect | [Kafka Connect Guide](../kafka-connect/index.md) |
| Configure for production | [Operations Guide](../operations/index.md) |

---

## Related Documentation

- [Installation Guide](installation/index.md) - Detailed installation procedures
- [Client Drivers](drivers/index.md) - Language-specific client setup
- [Concepts](../concepts/index.md) - Kafka fundamentals
- [Operations](../operations/index.md) - Production configuration
