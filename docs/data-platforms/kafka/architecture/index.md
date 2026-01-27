---
title: "Kafka Architecture"
description: "Apache Kafka architecture internals: brokers, partitions, replication, KRaft consensus, storage engine, and performance characteristics."
meta:
  - name: keywords
    content: "Kafka architecture, Kafka internals, KRaft, broker architecture, Kafka replication, partition leader"
---

# Kafka Architecture

Apache Kafka is a distributed commit log designed for high-throughput, fault-tolerant, real-time data streaming.

---

## Architectural Overview

Kafka's architecture consists of brokers forming a cluster, with data organized into topics and partitions. Producers write to topic partitions, and consumers read from them.

```plantuml
@startuml
skinparam componentStyle rectangle

package "Kafka Cluster" {
  rectangle "Broker 1\n(Controller)" as b1 {
    rectangle "P0 Leader" as b1_p0
    rectangle "P1 Follower" as b1_p1
    rectangle "P2 Follower" as b1_p2
  }

  rectangle "Broker 2" as b2 {
    rectangle "P0 Follower" as b2_p0
    rectangle "P1 Leader" as b2_p1
    rectangle "P2 Follower" as b2_p2
  }

  rectangle "Broker 3" as b3 {
    rectangle "P0 Follower" as b3_p0
    rectangle "P1 Follower" as b3_p1
    rectangle "P2 Leader" as b3_p2
  }
}

rectangle "Producers" as prod {
  rectangle "Producer 1" as prod1
  rectangle "Producer 2" as prod2
}

rectangle "Consumers" as cons {
  rectangle "Consumer Group A" as cg_a {
    rectangle "C1" as c1
    rectangle "C2" as c2
  }
}

prod1 --> b1_p0 : write
prod2 --> b2_p1 : write
prod2 --> b3_p2 : write

b1_p0 --> c1 : read
b2_p1 --> c2 : read
b3_p2 --> c2 : read

b1_p0 ..> b2_p0 : replicate
b1_p0 ..> b3_p0 : replicate

note bottom of b1
  Controller coordinates
  cluster metadata
end note

@enduml
```

### Core Components

| Component | Description |
|-----------|-------------|
| **Broker** | Server that stores data and serves client requests |
| **Controller** | Broker responsible for cluster coordination (leader election, partition assignment) |
| **Topic** | Named category of records; logical grouping of related events |
| **Partition** | Ordered, immutable sequence of records within a topic |
| **Replica** | Copy of a partition for fault tolerance |
| **Producer** | Client that publishes records to topics |
| **Consumer** | Client that subscribes to topics and processes records |
| **Consumer Group** | Set of consumers that coordinate to consume a topic |

---

## Brokers

Brokers are the servers that form a Kafka cluster. Each broker:

- Stores partition data on disk
- Handles produce and fetch requests from clients
- Replicates data to other brokers
- Participates in cluster coordination

### Broker Architecture

```plantuml
@startuml

rectangle "Kafka Broker" {
  rectangle "Network Layer" as net {
    rectangle "Acceptor\nThreads" as acceptor
    rectangle "Network\nThreads" as network
    rectangle "Request\nQueue" as req_queue
  }

  rectangle "Request Processing" as proc {
    rectangle "I/O Threads\n(num.io.threads)" as io
    rectangle "Response\nQueue" as resp_queue
  }

  rectangle "Storage Layer" as storage {
    rectangle "Log Manager" as log_mgr
    database "Partition\nLogs" as logs
    database "Index\nFiles" as indexes
  }

  rectangle "Replication" as repl {
    rectangle "Replica\nFetcher" as fetcher
    rectangle "Replica\nManager" as replica_mgr
  }
}

acceptor --> network : connections
network --> req_queue : requests
req_queue --> io : process
io --> log_mgr : read/write
log_mgr --> logs
log_mgr --> indexes
io --> resp_queue : response
resp_queue --> network : send

fetcher --> replica_mgr : sync

@enduml
```

### Key Broker Configurations

| Configuration | Default | Description |
|---------------|---------|-------------|
| `broker.id` | -1 (auto) | Unique identifier for this broker |
| `log.dirs` | /tmp/kafka-logs | Directories for partition data |
| `num.network.threads` | 3 | Threads for network I/O |
| `num.io.threads` | 8 | Threads for disk I/O |
| `socket.send.buffer.bytes` | 102400 | Socket send buffer |
| `socket.receive.buffer.bytes` | 102400 | Socket receive buffer |
| `socket.request.max.bytes` | 104857600 | Maximum request size (100MB) |

→ [Broker Deep Dive](brokers/index.md)

---

## Controller

The controller manages cluster-wide metadata operations. In KRaft mode, controllers are a dedicated process role; in ZooKeeper mode, a broker is elected as controller.

### Controller Responsibilities

| Responsibility | Description |
|----------------|-------------|
| **Leader election** | Elect new partition leaders when leaders fail |
| **Partition assignment** | Assign partitions to brokers |
| **Broker registration** | Track broker membership in cluster |
| **Topic management** | Create and delete topics |
| **Metadata propagation** | Distribute cluster metadata to all brokers |

### KRaft vs ZooKeeper

Kafka is transitioning from ZooKeeper to KRaft (Kafka Raft) for cluster coordination.

```plantuml
@startuml

rectangle "ZooKeeper Mode" as zk_mode {
  rectangle "ZooKeeper Ensemble" as zk {
    rectangle "ZK 1" as zk1
    rectangle "ZK 2" as zk2
    rectangle "ZK 3" as zk3
  }

  rectangle "Kafka Brokers" as zk_brokers {
    rectangle "Controller" as zk_ctrl #lightgreen
    rectangle "Broker 2" as zk_b2
    rectangle "Broker 3" as zk_b3
  }

  zk_ctrl --> zk : leader election,\nmetadata
  zk_b2 --> zk : registration
  zk_b3 --> zk : registration
}

rectangle "KRaft Mode" as kraft_mode {
  rectangle "Controller Quorum" as ctrl_quorum {
    rectangle "Controller 1\n(Leader)" as k_ctrl1 #lightgreen
    rectangle "Controller 2" as k_ctrl2
    rectangle "Controller 3" as k_ctrl3
  }

  rectangle "Kafka Brokers" as kraft_brokers {
    rectangle "Broker 1" as k_b1
    rectangle "Broker 2" as k_b2
    rectangle "Broker 3" as k_b3
  }

  k_ctrl1 <--> k_ctrl2 : Raft
  k_ctrl2 <--> k_ctrl3 : Raft
  k_ctrl1 <--> k_ctrl3 : Raft

  k_ctrl1 --> k_b1 : metadata
  k_ctrl1 --> k_b2 : metadata
  k_ctrl1 --> k_b3 : metadata
}

zk_mode -[hidden]right- kraft_mode

@enduml
```

| Aspect | ZooKeeper Mode | KRaft Mode |
|--------|----------------|------------|
| **External dependency** | ZooKeeper cluster required | None |
| **Metadata storage** | Split (ZK + broker logs) | Unified (__cluster_metadata topic) |
| **Failover time** | Seconds to minutes | Milliseconds to seconds |
| **Partition scale** | Higher metadata overhead; lower practical limits | Higher practical partition counts |
| **Operational complexity** | Two systems to manage | Single system |
| **Version** | Removed in Kafka 4.0 | Kafka 3.3+ (production ready) |

→ [KRaft Deep Dive](kraft/index.md)

---

## Partitions and Replication

### Partitions

A topic is divided into partitions—ordered, append-only logs. Partitions enable:

- **Parallelism**: Multiple consumers can read different partitions concurrently
- **Ordering**: Records within a partition maintain strict order
- **Scalability**: Partitions can be distributed across brokers

```plantuml
@startuml

rectangle "Topic: orders (3 partitions, RF=3)" {
  rectangle "Partition 0" as p0 {
    card "Offset 0" as p0_0
    card "Offset 1" as p0_1
    card "Offset 2" as p0_2
    card "..." as p0_n
    p0_0 -right-> p0_1
    p0_1 -right-> p0_2
    p0_2 -right-> p0_n
  }

  rectangle "Partition 1" as p1 {
    card "Offset 0" as p1_0
    card "Offset 1" as p1_1
    card "..." as p1_n
    p1_0 -right-> p1_1
    p1_1 -right-> p1_n
  }

  rectangle "Partition 2" as p2 {
    card "Offset 0" as p2_0
    card "Offset 1" as p2_1
    card "Offset 2" as p2_2
    card "Offset 3" as p2_3
    card "..." as p2_n
    p2_0 -right-> p2_1
    p2_1 -right-> p2_2
    p2_2 -right-> p2_3
    p2_3 -right-> p2_n
  }
}

note bottom
  Each partition is independent
  Offsets are partition-local
  No ordering across partitions
end note

@enduml
```

### Replication

Each partition has multiple replicas distributed across brokers. One replica is the leader; others are followers.

```plantuml
@startuml
skinparam sequenceMessageAlign center

participant "Producer" as prod
participant "Broker 1\n(Leader)" as leader
participant "Broker 2\n(Follower)" as f1
participant "Broker 3\n(Follower)" as f2

prod -> leader : produce(key, value)
activate leader

leader -> leader : append to log
leader -> f1 : replicate
leader -> f2 : replicate

f1 -> leader : ack
f2 -> leader : ack

leader -> prod : ack (acks=all)
deactivate leader

note over leader, f2
  ISR (In-Sync Replicas): {leader, f1, f2}
  High Watermark advances after all ISR ack
end note

@enduml
```

### Replication Concepts

For complete ISR mechanics, leader election protocol, and acknowledgment configuration, see [Replication](replication/index.md).

| Concept | Description |
|---------|-------------|
| **Leader** | Replica that handles all reads and writes for a partition |
| **Follower** | Replica that replicates from leader; can become leader if current leader fails |
| **ISR (In-Sync Replicas)** | Set of replicas that are fully caught up with leader |
| **High Watermark** | Offset up to which all ISR have replicated; consumers can only read up to HW |
| **LEO (Log End Offset)** | Latest offset in the leader's log |

### Replication Factor

The replication factor determines how many copies of each partition exist:

| RF | Behavior | Use Case |
|----|----------|----------|
| **1** | No redundancy; data loss on broker failure | Development only |
| **2** | Tolerates 1 broker failure with `min.insync.replicas=1` | Limited production use |
| **3** | Tolerates 1 broker failure with `min.insync.replicas=2` | Production standard |
| **4+** | Higher durability; rarely needed | Critical data |

→ [Replication Deep Dive](replication/index.md)

---

## Storage Engine

Kafka stores data in log segments on disk. The storage design prioritizes sequential I/O for maximum throughput. For complete storage internals including indexes, compaction, and retention policies, see [Storage Engine](storage-engine/index.md).

```plantuml
@startuml

rectangle "Partition Directory" as partition {
  rectangle "Active Segment" as active {
    file "00000000000000012345.log" as log_active
    file "00000000000000012345.index" as idx_active
    file "00000000000000012345.timeindex" as time_active
  }

  rectangle "Closed Segments" as closed {
    file "00000000000000000000.log" as log1
    file "00000000000000000000.index" as idx1
    file "00000000000000005000.log" as log2
    file "00000000000000005000.index" as idx2
  }
}

note right of active
  Active segment receives
  new writes (append-only)
end note

note right of closed
  Closed segments are immutable
  Subject to retention/compaction
end note

@enduml
```

### Log Segment Files

| File | Purpose |
|------|---------|
| `.log` | Message data (key, value, headers, metadata) |
| `.index` | Offset-to-position index for efficient seeking |
| `.timeindex` | Timestamp-to-offset index for time-based seeking |
| `.txnindex` | Transaction index (for transactional messages) |
| `.snapshot` | Producer state snapshots |

### Retention Policies

| Policy | Configuration | Behavior |
|--------|---------------|----------|
| **Time-based** | `retention.ms` | Delete segments older than threshold |
| **Size-based** | `retention.bytes` | Delete oldest segments when partition exceeds size |
| **Compaction** | `cleanup.policy=compact` | Keep only latest value per key |

→ [Storage Engine Deep Dive](storage-engine/index.md)

---

## Performance Architecture

Kafka achieves high throughput through several design choices. For detailed performance tuning, benchmarking, and optimization techniques, see [Performance Internals](performance-internals/index.md).

### Sequential I/O

```plantuml
@startuml

rectangle "Random I/O (Traditional DB)" as random {
  rectangle "Seek" as r_seek
  rectangle "Read" as r_read
  rectangle "Seek" as r_seek2
  rectangle "Write" as r_write
  rectangle "Seek" as r_seek3
  r_seek --> r_read
  r_read --> r_seek2
  r_seek2 --> r_write
  r_write --> r_seek3
}

rectangle "Sequential I/O (Kafka)" as seq {
  rectangle "Append" as s_append
  rectangle "Append" as s_append2
  rectangle "Append" as s_append3
  rectangle "Read batch" as s_read
  s_append --> s_append2
  s_append2 --> s_append3
  s_append3 --> s_read
}

note bottom of random
  ~100 IOPS on HDD
  Random seeks dominate
end note

note bottom of seq
  ~100 MB/s on HDD
  No seek overhead
end note

random -[hidden]right- seq

@enduml
```

### Zero-Copy Transfers

Kafka uses `sendfile()` to transfer data directly from disk to network, bypassing user-space copies.

```plantuml
@startuml

rectangle "Traditional Copy" as trad {
  rectangle "Disk" as t_disk
  rectangle "Kernel Buffer" as t_kernel1
  rectangle "User Buffer" as t_user
  rectangle "Kernel Buffer" as t_kernel2
  rectangle "Network" as t_network

  t_disk --> t_kernel1 : 1. read
  t_kernel1 --> t_user : 2. copy
  t_user --> t_kernel2 : 3. copy
  t_kernel2 --> t_network : 4. send
}

rectangle "Zero-Copy (sendfile)" as zero {
  rectangle "Disk" as z_disk
  rectangle "Page Cache" as z_cache
  rectangle "Network" as z_network

  z_disk --> z_cache : 1. read
  z_cache --> z_network : 2. sendfile()
}

note bottom of trad
  4 copies
  2 context switches
end note

note bottom of zero
  0 copies to user space
  Direct kernel transfer
end note

trad -[hidden]right- zero

@enduml
```

!!! warning "TLS Disables Zero-Copy"
    When TLS encryption is enabled, zero-copy is not possible because data must be encrypted in user space. Throughput impact depends on CPU and workload.

### Batching

Producers batch messages before sending, and consumers fetch in batches:

| Batching Point | Configuration | Benefit |
|----------------|---------------|---------|
| **Producer** | `batch.size`, `linger.ms` | Amortize network overhead, enable compression |
| **Broker** | Internal batching | Efficient disk writes |
| **Consumer** | `fetch.min.bytes`, `fetch.max.wait.ms` | Reduce fetch requests |

### OS Page Cache

Kafka relies on the OS page cache rather than managing its own cache:

| Benefit | Description |
|---------|-------------|
| **Automatic management** | OS handles cache eviction |
| **Warm restarts** | Cache survives broker restarts |
| **Memory efficiency** | Avoids double-buffering in JVM |
| **Read-ahead** | OS prefetches sequential reads |

→ [Performance Internals](performance-internals/index.md)

---

## Fault Tolerance

Kafka survives failures at multiple levels. For complete failure scenarios, recovery procedures, and monitoring strategies, see [Fault Tolerance](fault-tolerance/index.md).

| Failure | Kafka Response |
|---------|----------------|
| **Single broker** | Leader election; ISR continues serving |
| **Multiple brokers** | Service continues if enough replicas remain |
| **Rack failure** | Rack-aware placement ensures cross-rack replicas |
| **Network partition** | ISR shrinks; `acks=all` writes fail if ISR < `min.insync.replicas` |
| **Disk failure** | Replicas on failed log dirs go offline; leaders move to healthy replicas |

### Data Durability Configuration

| Setting | Value | Behavior |
|---------|-------|----------|
| `acks=all` | Producer waits for all ISR | Strongest durability |
| `min.insync.replicas=2` | Require 2 replicas for writes | Prevents single-replica writes |
| `unclean.leader.election.enable=false` | Only ISR can become leader | Prevents data loss on failover |

→ [Fault Tolerance Guide](fault-tolerance/index.md)

---

## Related Documentation

- [Topics and Partitions](topics/index.md) - Partitions, leaders, ISR, replication
- [Transaction Coordinator](transactions/index.md) - Exactly-once semantics, two-phase commit
- [Brokers](brokers/index.md) - Broker architecture and configuration
- [KRaft](kraft/index.md) - KRaft consensus mode
- [Replication](replication/index.md) - ISR, leader election, durability
- [Storage Engine](storage-engine/index.md) - Log segments, indexes, compaction
- [Performance Internals](performance-internals/index.md) - Zero-copy, batching, tuning
- [Fault Tolerance](fault-tolerance/index.md) - Failure scenarios and recovery
- [Topology](topology/index.md) - Rack awareness, network design