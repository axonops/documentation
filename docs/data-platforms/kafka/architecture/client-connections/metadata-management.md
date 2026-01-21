---
title: "Kafka Metadata Management"
description: "Apache Kafka metadata management. Cluster discovery, topic metadata, partition leadership, and metadata caching."
meta:
  - name: keywords
    content: "Kafka metadata, topic metadata, partition metadata, metadata refresh, metadata cache"
search:
  boost: 3
---

# Kafka Metadata Management

Kafka clients maintain metadata about the cluster topology, including broker addresses, topic partitions, and partition leaders. Proper metadata management is essential for efficient request routing and handling topology changes.

## Metadata Overview

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Client Metadata Cache" {
    rectangle "Cluster Info" as Cluster {
        rectangle "Cluster ID" as CID
        rectangle "Controller ID" as Controller
    }

    rectangle "Broker List" as Brokers {
        rectangle "Broker 1: host1:9092" as B1
        rectangle "Broker 2: host2:9092" as B2
        rectangle "Broker 3: host3:9092" as B3
    }

    rectangle "Topic Metadata" as Topics {
        rectangle "orders" as T1 {
            rectangle "P0: leader=1, ISR=[1,2,3]" as P0
            rectangle "P1: leader=2, ISR=[2,3,1]" as P1
            rectangle "P2: leader=3, ISR=[3,1,2]" as P2
        }
    }
}

note right of Topics
  Updated on:
  - Startup
  - NotLeaderOrFollower error
  - metadata.max.age.ms expiry
  - New topic access
end note

@enduml
```

---

## Metadata Contents

### Cluster Metadata

| Field | Description |
|-------|-------------|
| `cluster_id` | Unique cluster identifier |
| `controller_id` | Current controller broker ID |
| `brokers` | List of all brokers with host/port/rack |

### Broker Information

| Field | Description |
|-------|-------------|
| `node_id` | Unique broker identifier |
| `host` | Broker hostname or IP |
| `port` | Broker port (default 9092) |
| `rack` | Rack identifier (optional) |

### Topic Metadata

| Field | Description |
|-------|-------------|
| `name` | Topic name |
| `partitions` | Number of partitions |
| `is_internal` | Internal topic flag |

Replication factor is derived from the partition replica lists, not returned directly in the metadata response.

### Partition Metadata

| Field | Description |
|-------|-------------|
| `partition` | Partition index |
| `leader` | Current leader broker ID |
| `leader_epoch` | Leader election epoch |
| `replicas` | All replica broker IDs |
| `isr` | In-sync replica broker IDs |
| `offline_replicas` | Offline replica broker IDs |

---

## Bootstrap Process

### Initial Discovery

```plantuml
@startuml

skinparam backgroundColor transparent

participant "Client" as C
participant "Bootstrap\nBroker 1" as B1
participant "Bootstrap\nBroker 2" as B2

C -> B1 : Connect (bootstrap.servers)
activate B1

alt Connection Success
    B1 --> C : Connected

    C -> B1 : MetadataRequest\n(topics=[])
    B1 --> C : MetadataResponse\n(full cluster metadata)
    deactivate B1

    note over C
      Cache metadata:
      - All brokers
      - All topics (if authorized)
      - Partition leaders
    end note

else Connection Failed
    C -> B2 : Connect (next bootstrap)
    B2 --> C : Connected
    C -> B2 : MetadataRequest
    B2 --> C : MetadataResponse
end

@enduml
```

### Bootstrap Configuration

```properties
# Multiple brokers for redundancy
bootstrap.servers=kafka1:9092,kafka2:9092,kafka3:9092

# Client will try brokers in random order
# Only needs ONE successful connection for discovery
```

**Best Practices:**

| Guideline | Rationale |
|-----------|-----------|
| List 3+ brokers | Redundancy during broker failures |
| Use DNS names | Easier maintenance than IPs |
| Include brokers from different racks | Survive rack failures |
| Don't list all brokers | Unnecessary, any broker returns full metadata |

---

## Metadata Requests

### MetadataRequest Structure

```
MetadataRequest {
    topics: [TopicName]       // Empty for all topics
    allow_auto_topic_creation: bool
    include_cluster_authorized_operations: bool
    include_topic_authorized_operations: bool
}
```

### MetadataResponse Structure

```
MetadataResponse {
    throttle_time_ms: int32
    brokers: [Broker]
    cluster_id: string
    controller_id: int32
    topics: [TopicMetadata]
}

Broker {
    node_id: int32
    host: string
    port: int32
    rack: string (nullable)
}

TopicMetadata {
    error_code: int16
    name: string
    is_internal: bool
    partitions: [PartitionMetadata]
}

PartitionMetadata {
    error_code: int16
    partition_index: int32
    leader_id: int32
    leader_epoch: int32
    replica_nodes: [int32]
    isr_nodes: [int32]
    offline_replicas: [int32]
}
```

---

## Metadata Refresh

### Refresh Triggers

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Metadata Refresh Triggers" {
    rectangle "Scheduled" as Scheduled {
        rectangle "metadata.max.age.ms\nexpiry" as Age
    }

    rectangle "Error-Driven" as Errors {
        rectangle "NOT_LEADER_OR_FOLLOWER" as NL
        rectangle "UNKNOWN_TOPIC_OR_PARTITION\n(topic expected)" as UT
        rectangle "LEADER_NOT_AVAILABLE" as LNA
    }

    rectangle "Explicit" as Explicit {
        rectangle "New topic access" as NewTopic
        rectangle "awaitUpdate() call" as Await
    }
}

@enduml
```

### Configuration

```properties
# Maximum age before forced refresh
metadata.max.age.ms=300000  # 5 minutes (default)
```

### Refresh Flow

```plantuml
@startuml

skinparam backgroundColor transparent

start

:Check metadata age;

if (Age > metadata.max.age.ms?) then (yes)
    :Schedule refresh;
else (no)
    if (Error triggers refresh?) then (yes)
        :Immediate refresh;
    else (no)
        :Use cached metadata;
        stop
    endif
endif

:Select broker for request;
note right: Prefer least-loaded broker

:Send MetadataRequest;

if (Request successful?) then (yes)
    :Update cache;
    :Notify waiters;
else (no)
    :Apply backoff;
    :Retry with different broker;
endif

stop

@enduml
```

---

## Metadata Caching

### Cache Structure

```plantuml
@startuml

skinparam backgroundColor transparent

package "Metadata Cache" {
    rectangle "Cluster" as ClusterCache {
        rectangle "nodes: Map<Integer, Node>" as Nodes
        rectangle "controller: Node" as ControllerNode
        rectangle "clusterId: String" as ClusterIdCache
    }

    rectangle "Topics" as TopicsCache {
        rectangle "Map<String, TopicMetadata>" as TopicMap
    }

    rectangle "Partitions" as PartitionsCache {
        rectangle "Map<TopicPartition, PartitionInfo>" as PartitionMap
    }

    rectangle "Timestamps" as Timestamps {
        rectangle "lastRefreshMs: long" as LastRefresh
        rectangle "lastSuccessfulRefreshMs: long" as LastSuccess
    }
}

@enduml
```

### Cache Invalidation

| Event | Action |
|-------|--------|
| `metadata.max.age.ms` expiry | Mark stale, refresh |
| `NOT_LEADER_OR_FOLLOWER` | Invalidate partition |
| `UNKNOWN_TOPIC_OR_PARTITION` | Invalidate topic |
| Node disconnect | Invalidate node |

### Partition Leader Lookup

```java
// Find leader for partition
public Node leader(TopicPartition partition) {
    PartitionInfo info = partitionsByTopicPartition.get(partition);
    if (info == null) {
        return null;
    }
    return info.leader();
}

// Find all partitions for topic
public List<PartitionInfo> partitionsForTopic(String topic) {
    return partitionsByTopic.get(topic);
}
```

---

## Handling Metadata Errors

### Common Metadata Errors

| Error Code | Name | Cause | Client Action |
|:----------:|------|-------|---------------|
| 3 | `UNKNOWN_TOPIC_OR_PARTITION` | Topic/partition doesn't exist | Refresh only if the topic is expected to exist |
| 5 | `LEADER_NOT_AVAILABLE` | Leader election in progress | Wait and retry |
| 6 | `NOT_LEADER_OR_FOLLOWER` | Stale leader info | Refresh metadata |
| 29 | `COORDINATOR_NOT_AVAILABLE` | Group coordinator unavailable | Retry FindCoordinator |

### Error Handling Flow

```plantuml
@startuml

skinparam backgroundColor transparent

start

:Receive error response;

switch (Error type?)
case (NOT_LEADER_OR_FOLLOWER)
    :Refresh metadata immediately;
    :Retry request to new leader;
case (UNKNOWN_TOPIC_OR_PARTITION)
    :Refresh metadata (if topic expected);
    :Wait for topic creation (if auto-create);
case (LEADER_NOT_AVAILABLE)
    :Wait (leader election);
    :Refresh metadata;
    :Retry request;
case (Other retriable)
    :Apply backoff;
    :Retry request;
case (Non-retriable)
    :Return error to caller;
endswitch

stop

@enduml
```

---

## Leader Epoch

### What is Leader Epoch?

Leader epoch is a monotonically increasing number that identifies the term of a partition leader. It prevents issues from stale leadership information.

```plantuml
@startuml

skinparam backgroundColor transparent

title Leader Epoch Timeline

concise "Partition Leader" as Leader
concise "Leader Epoch" as Epoch

@0
Leader is "Broker 1"
Epoch is "0"

@100
Leader is "Broker 2"
Epoch is "1"

@200
Leader is "Broker 1"
Epoch is "2"

@250
Leader is "Broker 3"
Epoch is "3"

@enduml
```

### Epoch Validation

```plantuml
@startuml

skinparam backgroundColor transparent

participant "Producer" as P
participant "Old Leader\n(epoch 5)" as OL
participant "New Leader\n(epoch 6)" as NL

note over P: Client has stale metadata\n(leader = old, epoch = 5)

P -> OL : ProduceRequest\n(partition, epoch=5)
OL --> P : NOT_LEADER_OR_FOLLOWER\n(current_epoch=6)

note over P: Refresh metadata

P -> NL : ProduceRequest\n(partition, epoch=6)
NL --> P : Success

@enduml
```

---

## Rack-Aware Metadata

### Rack Information

```properties
# Client rack (for follower fetching)
client.rack=rack-a

# Enables rack-aware replica selection
```

### Rack-Aware Consumption

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Rack A" {
    rectangle "Consumer" as C
    rectangle "Follower\n(Broker 2)" as F
}

rectangle "Rack B" {
    rectangle "Leader\n(Broker 1)" as L
}

C --> F : Fetch from\nrack-local follower
F --> L : Replicate

note bottom of C
  Consumer in rack-a fetches
  from follower in rack-a
  (Kafka 2.4+, KIP-392)
end note

@enduml
```

---

## Metadata for Specific Use Cases

### Producer Metadata Usage

```plantuml
@startuml

skinparam backgroundColor transparent

participant "Producer" as P
participant "Metadata Cache" as MC
participant "Partitioner" as Part

P -> MC : Get topic metadata
MC --> P : TopicMetadata

P -> Part : Select partition\n(key, numPartitions)
Part --> P : partition=2

P -> MC : Get leader for partition 2
MC --> P : Broker 3

P -> P : Send to Broker 3

@enduml
```

### Consumer Metadata Usage

```plantuml
@startuml

skinparam backgroundColor transparent

participant "Consumer" as C
participant "Metadata Cache" as MC
participant "Coordinator" as Coord

C -> MC : Get partitions for topics
MC --> C : [P0, P1, P2, ...]

C -> Coord : JoinGroup(topics)
Coord --> C : Assignment(P0, P2)

C -> MC : Get leaders for P0, P2
MC --> C : P0→Broker1, P2→Broker3

C -> C : Fetch from assigned partitions

@enduml
```

---

## Performance Optimization

### Reducing Metadata Overhead

| Optimization | Configuration |
|-------------|---------------|
| Increase refresh interval | `metadata.max.age.ms=600000` |
| Request specific topics | Don't request all topics |
| Cache locally | Avoid redundant lookups |

### Metadata Request Batching

Kafka batches metadata requests when multiple threads need updates:

```plantuml
@startuml

skinparam backgroundColor transparent

participant "Thread 1" as T1
participant "Thread 2" as T2
participant "Metadata Manager" as MM
participant "Broker" as B

T1 -> MM : requestUpdate()
T2 -> MM : requestUpdate()

note over MM
  Coalesce requests
  into single batch
end note

MM -> B : MetadataRequest
B --> MM : MetadataResponse

MM --> T1 : Metadata updated
MM --> T2 : Metadata updated

@enduml
```

---

## Monitoring Metadata

### Key Metrics

Producer client metrics are reported under the `producer-metrics` group.

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `metadata-age` | Age in seconds of the current producer metadata | > 2 × metadata.max.age.ms / 1000 |
| `metadata-wait-time-ns-total` | Cumulative time spent waiting for metadata (ns) | Sustained increase in rate |

### Debugging Metadata Issues

```properties
# Enable metadata debug logging
log4j.logger.org.apache.kafka.clients.Metadata=DEBUG
log4j.logger.org.apache.kafka.clients.NetworkClient=DEBUG
```

Common issues:

| Symptom | Cause | Solution |
|---------|-------|----------|
| Frequent refreshes | Many `NOT_LEADER` errors | Check cluster stability |
| Stale metadata | Long `metadata.max.age.ms` | Reduce refresh interval |
| Missing topics | Authorization issues | Check ACLs |
| Wrong broker count | Partial visibility | Check bootstrap servers |

---

## Version Compatibility

| Feature | Minimum Version |
|---------|-----------------|
| Basic metadata | 0.8.0 |
| Rack information | 0.10.0 |
| Leader epoch | 0.11.0 |
| Offline replicas | 1.0.0 |
| Authorized operations | 2.3.0 |

---

## Related Documentation

- [Kafka Protocol](kafka-protocol.md) - Wire protocol details
- [Connection Pooling](connection-pooling.md) - Connection management
- [Load Balancing](load-balancing.md) - Request routing
- [Topology](../topology/index.md) - Cluster topology
