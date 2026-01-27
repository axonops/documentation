---
title: "Kafka Installation"
description: "Apache Kafka installation guide. Local installation, Docker deployment, and production setup procedures."
meta:
  - name: keywords
    content: "Kafka installation, Kafka setup, KRaft mode, Kafka Docker"
---

# Kafka Installation

Installation procedures for Apache Kafka across different deployment scenarios.

---

## Installation Methods

| Method | Use Case | Prerequisites |
|--------|----------|---------------|
| **Binary Installation** | Development, production | Java 11+ |
| **Docker** | Development, testing | Docker |
| **Kubernetes** | Cloud-native production | Kubernetes cluster |
| **Package Manager** | Linux servers | apt/yum |

---

## Binary Installation

### Download

```bash
# Kafka 4.1.x (current stable)
curl -O https://downloads.apache.org/kafka/4.1.1/kafka_2.13-4.1.1.tgz
tar -xzf kafka_2.13-4.1.1.tgz
cd kafka_2.13-4.1.1
```

### KRaft Mode (Recommended)

KRaft mode eliminates the ZooKeeper dependency. This is the recommended deployment mode for Kafka 3.3+.

```bash
# Generate cluster ID
KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"

# Format storage directories
bin/kafka-storage.sh format \
  -t $KAFKA_CLUSTER_ID \
  -c config/kraft/server.properties

# Start broker
bin/kafka-server-start.sh config/kraft/server.properties
```

### KRaft Configuration

```properties
# config/kraft/server.properties

# Node configuration
node.id=1
process.roles=broker,controller
controller.quorum.voters=1@localhost:9093

# Listeners
listeners=PLAINTEXT://:9092,CONTROLLER://:9093
inter.broker.listener.name=PLAINTEXT
advertised.listeners=PLAINTEXT://localhost:9092
controller.listener.names=CONTROLLER

# Log directories
log.dirs=/var/kafka-logs

# Cluster settings
num.partitions=3
default.replication.factor=1
min.insync.replicas=1
```

---

## Docker Installation

### Single Broker

```yaml
# docker-compose.yml
version: '3.8'
services:
  kafka:
    image: apache/kafka:4.1.1
    hostname: kafka
    container_name: kafka
    ports:
      - "9092:9092"
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_LISTENERS: PLAINTEXT://:9092,CONTROLLER://:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka:9093
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_LOG_DIRS: /tmp/kraft-combined-logs
      CLUSTER_ID: MkU3OEVBNTcwNTJENDM2Qk
```

```bash
docker-compose up -d
```

### Multi-Broker Cluster

```yaml
# docker-compose-cluster.yml
version: '3.8'
services:
  kafka1:
    image: apache/kafka:4.1.1
    hostname: kafka1
    container_name: kafka1
    ports:
      - "9092:9092"
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_LISTENERS: PLAINTEXT://:9092,CONTROLLER://:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka1:9092
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka1:9093,2@kafka2:9093,3@kafka3:9093
      KAFKA_LOG_DIRS: /tmp/kraft-combined-logs
      CLUSTER_ID: MkU3OEVBNTcwNTJENDM2Qk
    volumes:
      - kafka1-data:/tmp/kraft-combined-logs

  kafka2:
    image: apache/kafka:4.1.1
    hostname: kafka2
    container_name: kafka2
    ports:
      - "9093:9092"
    environment:
      KAFKA_NODE_ID: 2
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_LISTENERS: PLAINTEXT://:9092,CONTROLLER://:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka2:9092
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka1:9093,2@kafka2:9093,3@kafka3:9093
      KAFKA_LOG_DIRS: /tmp/kraft-combined-logs
      CLUSTER_ID: MkU3OEVBNTcwNTJENDM2Qk
    volumes:
      - kafka2-data:/tmp/kraft-combined-logs

  kafka3:
    image: apache/kafka:4.1.1
    hostname: kafka3
    container_name: kafka3
    ports:
      - "9094:9092"
    environment:
      KAFKA_NODE_ID: 3
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_LISTENERS: PLAINTEXT://:9092,CONTROLLER://:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka3:9092
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka1:9093,2@kafka2:9093,3@kafka3:9093
      KAFKA_LOG_DIRS: /tmp/kraft-combined-logs
      CLUSTER_ID: MkU3OEVBNTcwNTJENDM2Qk
    volumes:
      - kafka3-data:/tmp/kraft-combined-logs

volumes:
  kafka1-data:
  kafka2-data:
  kafka3-data:
```

---

## Kubernetes

While the Docker container above can be deployed in Kubernetes, we recommend using [Strimzi](https://strimzi.io/docs/operators/latest/deploying) for
production-grade Kafka deployments on Kubernetes. Strimzi provides a complete operator-based solution with
native Kubernetes integration, automated management, and enhanced operational capabilities.

For detailed instructions on deploying Kafka with Strimzi and AxonOps monitoring integration, see the
[Kubernetes Strimzi Installation Guide](../../../../installation/kubernetes/strimzi/index.md).


## System Configuration

### Linux Kernel Tuning

```bash
# /etc/sysctl.conf

# Virtual memory
vm.swappiness=1
vm.dirty_ratio=80
vm.dirty_background_ratio=5

# Network
net.core.wmem_default=131072
net.core.rmem_default=131072
net.core.wmem_max=2097152
net.core.rmem_max=2097152
net.ipv4.tcp_wmem=4096 65536 2048000
net.ipv4.tcp_rmem=4096 65536 2048000

# File descriptors
fs.file-max=100000
```

### File Descriptor Limits

```bash
# /etc/security/limits.conf
kafka soft nofile 100000
kafka hard nofile 100000
kafka soft nproc 32768
kafka hard nproc 32768
```

### Disk Configuration

| Recommendation | Rationale |
|----------------|-----------|
| Use XFS or ext4 | Reliable filesystems for append-heavy workloads |
| Disable atime | Reduces unnecessary disk writes |
| Use separate disks for logs | Isolates I/O for different log directories |
| RAID 10 or JBOD | Balance between performance and redundancy |

```bash
# Mount options for Kafka data directory
/dev/sdb1 /var/kafka-logs xfs defaults,noatime 0 2
```

---

## Verification

```bash
# Check broker is running
bin/kafka-broker-api-versions.sh --bootstrap-server localhost:9092

# Create test topic
bin/kafka-topics.sh --create \
  --topic test \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1

# List topics
bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Produce test message
echo "test message" | bin/kafka-console-producer.sh \
  --topic test \
  --bootstrap-server localhost:9092

# Consume test message
bin/kafka-console-consumer.sh \
  --topic test \
  --from-beginning \
  --bootstrap-server localhost:9092 \
  --max-messages 1
```

---

## Related Documentation

- [Getting Started](../index.md) - Quick start guide
- [Configuration](../../operations/configuration/index.md) - Configuration reference
- [Kubernetes Deployment](../../cloud/kubernetes/index.md) - Kubernetes installation
- [Operations](../../operations/index.md) - Production operations