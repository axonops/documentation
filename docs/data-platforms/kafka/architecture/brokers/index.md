---
title: "Kafka Brokers"
description: "Apache Kafka broker architecture. What a broker does, how it stores data, serves clients, and coordinates with the cluster."
meta:
  - name: keywords
    content: "Kafka broker, Kafka server, broker architecture, KRaft, partition leader"
---

# Kafka Brokers

A Kafka broker is a server process that stores messages and serves client requests. Each broker in a cluster handles a portion of the data, enabling horizontal scaling and fault tolerance.

---

## What a Broker Does

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam rectangle {
    RoundCorner 5
}

rectangle "**Kafka Broker**" as broker #E3F2FD {
    rectangle "Receive produce requests" as recv #C8E6C9
    rectangle "Store to disk (commit log)" as store #C8E6C9
    rectangle "Replicate to followers" as repl #C8E6C9
    rectangle "Serve fetch requests" as serve #C8E6C9
}

rectangle "Producer" as prod
rectangle "Consumer" as cons
rectangle "Other Brokers" as other

prod -down-> recv
store -down-> repl
repl -down-> other
serve -right-> cons

recv -[hidden]down-> store
store -[hidden]down-> serve

@enduml
```

| Responsibility | Description |
|----------------|-------------|
| **Store messages** | Persist records to disk as log segments |
| **Serve producers** | Accept writes, acknowledge based on `acks` setting |
| **Serve consumers** | Return records from requested offsets |
| **Replicate data** | Send records to follower replicas |
| **Receive replicas** | Accept records from leader replicas |
| **Report metadata** | Register with controller, report partition state |

---

## Broker Identity

Each broker has a unique identity within the cluster:

```properties
# Unique broker ID (must be unique across cluster)
node.id=1

# Listeners for client and inter-broker communication
listeners=PLAINTEXT://:9092,CONTROLLER://:9093
advertised.listeners=PLAINTEXT://broker1.example.com:9092

# Data directory
log.dirs=/var/kafka-logs
```

Clients discover brokers through the bootstrap servers, then connect directly to the broker hosting each partition's leader.

---

## Partitions and Leadership

Brokers don't own topics—they own **partition replicas**. Each partition has one leader and zero or more followers:

```plantuml
@startuml
skinparam backgroundColor transparent

rectangle "Topic: orders (3 partitions, RF=3)" as topic {

    rectangle "Broker 1" as b1 {
        rectangle "P0 Leader" as p0l #C8E6C9
        rectangle "P1 Follower" as p1f #FFF9C4
        rectangle "P2 Follower" as p2f #FFF9C4
    }

    rectangle "Broker 2" as b2 {
        rectangle "P0 Follower" as p0f1 #FFF9C4
        rectangle "P1 Leader" as p1l #C8E6C9
        rectangle "P2 Follower" as p2f2 #FFF9C4
    }

    rectangle "Broker 3" as b3 {
        rectangle "P0 Follower" as p0f2 #FFF9C4
        rectangle "P1 Follower" as p1f2 #FFF9C4
        rectangle "P2 Leader" as p2l #C8E6C9
    }
}

note bottom of topic
  Leaders (green) handle all reads/writes
  Followers (yellow) replicate from leaders
end note

@enduml
```

| Role | Responsibilities |
|------|------------------|
| **Leader** | Handle all produce and fetch requests for the partition |
| **Follower** | Fetch records from leader, ready to become leader if needed |

A single broker typically hosts hundreds or thousands of partition replicas, some as leader, others as follower.

---

## KRaft Mode (Kafka 3.3+)

Modern Kafka clusters use KRaft (Kafka Raft) for metadata management, eliminating the ZooKeeper dependency.

```plantuml
@startuml
skinparam backgroundColor transparent

rectangle "Controller Quorum" as cq #E8F5E9 {
    rectangle "Controller 1\n(Leader)" as c1 #C8E6C9
    rectangle "Controller 2" as c2 #FFF9C4
    rectangle "Controller 3" as c3 #FFF9C4
}

rectangle "Broker 1" as b1 #BBDEFB
rectangle "Broker 2" as b2 #BBDEFB
rectangle "Broker 3" as b3 #BBDEFB

c1 --> c2 : Raft replication
c1 --> c3 : Raft replication

c1 --> b1 : metadata push
c1 --> b2 : metadata push
c1 --> b3 : metadata push

note right of cq
  Stores cluster metadata in
  __cluster_metadata topic
end note

@enduml
```

### Process Roles

| Role | Configuration | Description |
|------|---------------|-------------|
| **broker** | `process.roles=broker` | Handles client requests only |
| **controller** | `process.roles=controller` | Manages metadata only |
| **combined** | `process.roles=broker,controller` | Both roles in one process |

| Deployment | Best For | Trade-off |
|------------|----------|-----------|
| **Combined** | Small clusters (≤10 brokers) | Simpler, but resource contention |
| **Dedicated** | Large clusters | More servers, but better isolation |

---

## Broker Lifecycle

```plantuml
@startuml
skinparam backgroundColor transparent

[*] --> Starting

Starting --> LogRecovery : load configuration
LogRecovery --> Registering : recover partitions
Registering --> CatchingUp : register with controller
CatchingUp --> Active : replicas in sync

Active --> Active : serving requests

Active --> ControlledShutdown : SIGTERM
ControlledShutdown --> [*] : leadership transferred

Active --> Crashed : process killed
Crashed --> Starting : restart

note right of LogRecovery
  May take minutes if
  many partitions or
  unclean shutdown
end note

note right of ControlledShutdown
  1. Stop accepting new connections
  2. Transfer partition leadership
  3. Complete in-flight requests
  4. Deregister from controller
end note

@enduml
```

### Controlled Shutdown

A controlled shutdown ensures no data loss and minimal disruption:

```bash
# Graceful shutdown (recommended)
kafka-server-stop.sh

# Or send SIGTERM
kill <broker-pid>
```

The broker will:

1. Notify the controller
2. Transfer leadership of all partitions to other brokers
3. Wait for in-flight requests to complete
4. Deregister and exit

!!! warning "Avoid kill -9"
    `kill -9` causes unclean shutdown, requiring full log recovery on restart and potentially causing under-replication.

---

## Key Metrics

| Metric | What It Tells You |
|--------|-------------------|
| `UnderReplicatedPartitions` | Partitions with fewer replicas than expected (should be 0) |
| `OfflinePartitionsCount` | Partitions without a leader (should be 0) |
| `ActiveControllerCount` | Whether this broker is the controller (1 or 0) |
| `MessagesInPerSec` | Throughput of incoming messages |
| `BytesInPerSec` / `BytesOutPerSec` | Network throughput |
| `RequestHandlerAvgIdlePercent` | Handler thread utilization (low = overloaded) |
| `NetworkProcessorAvgIdlePercent` | Network thread utilization |

```bash
# Quick health check via JMX
kafka-run-class.sh kafka.tools.JmxTool \
  --object-name 'kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions' \
  --jmx-url service:jmx:rmi:///jndi/rmi://localhost:9999/jmxrmi
```

---

## Failure Scenarios

| Scenario | Impact | Recovery |
|----------|--------|----------|
| **Single broker failure** | Partitions fail over to other brokers | Automatic leader election |
| **Minority of brokers down** | Cluster continues with reduced capacity | Restart failed brokers |
| **Majority of brokers down** | Some partitions unavailable | Restart brokers, may need manual intervention |
| **Controller failure** | New controller elected | Automatic (KRaft quorum) |
| **Disk failure** | Partitions on that disk unavailable | Replace disk, broker recovers from replicas |

### High Availability Settings

```properties
# Survive 2 broker failures
default.replication.factor=3

# Require 2 replicas to acknowledge writes
min.insync.replicas=2

# Never elect out-of-sync replica as leader
unclean.leader.election.enable=false
```

---

## Configuration Quick Reference

### Identity and Networking

```properties
node.id=1
listeners=PLAINTEXT://:9092
advertised.listeners=PLAINTEXT://broker1.example.com:9092
```

### Storage

```properties
log.dirs=/var/kafka-logs
log.retention.hours=168
log.segment.bytes=1073741824
```

### Threading

```properties
num.network.threads=3
num.io.threads=8
num.replica.fetchers=1
```

### Replication

```properties
default.replication.factor=3
min.insync.replicas=2
replica.lag.time.max.ms=30000
```

For complete configuration reference, see [Broker Configuration](../../operations/configuration/index.md).

---

## Section Contents

### Deep Dives

- **[Broker Internals](internals.md)** - Network layer, request processing, log subsystem, replica manager, purgatory, group coordinator, startup and recovery

### Related Topics

- **[Replication](../replication/index.md)** - How data is replicated between brokers
- **[Fault Tolerance](../fault-tolerance/index.md)** - Failure detection and recovery
- **[KRaft](../kraft/index.md)** - KRaft consensus protocol internals
- **[Cluster Management](../cluster-management/index.md)** - Metadata management and coordination
