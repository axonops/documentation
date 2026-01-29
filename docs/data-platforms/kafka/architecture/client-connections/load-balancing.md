---
title: "Kafka Client Load Balancing"
description: "Apache Kafka client-side load balancing. Partition assignment, producer partitioning, consumer load distribution, and rack awareness."
meta:
  - name: keywords
    content: "Kafka load balancing, partition distribution, consumer load balancing, broker selection"
---

# Kafka Client Load Balancing

Unlike traditional databases where a load balancer routes requests, Kafka clients perform their own load balancing. The client determines which broker to contact based on partition ownership. This guide covers partition-based routing, producer partitioning strategies, and consumer load distribution.

## Load Balancing Model

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Traditional Model" as Trad {
    rectangle "Client" as TC
    rectangle "Load Balancer" as LB
    rectangle "Servers" as TS {
        rectangle "S1" as TS1
        rectangle "S2" as TS2
        rectangle "S3" as TS3
    }
    TC --> LB
    LB --> TS1
    LB --> TS2
    LB --> TS3
}

rectangle "Kafka Model" as Kafka {
    rectangle "Client\n(Partition-Aware)" as KC
    rectangle "Brokers" as KB {
        rectangle "B1\n(P0,P3)" as KB1
        rectangle "B2\n(P1,P4)" as KB2
        rectangle "B3\n(P2,P5)" as KB3
    }
    KC --> KB1 : P0,P3 requests
    KC --> KB2 : P1,P4 requests
    KC --> KB3 : P2,P5 requests
}

@enduml
```

---

## Producer Load Balancing

### Partitioner Role

Producers distribute messages across partitions using a partitioner. This determines which broker receives each message.

```plantuml
@startuml

skinparam backgroundColor transparent

participant "Producer" as P
participant "Partitioner" as Part
participant "Metadata" as M

P -> Part : partition(topic, key, value)

alt Key is not null
    Part -> Part : hash(key) % numPartitions
    Part --> P : partition based on key
else Key is null
    alt Sticky Partitioning (Kafka 2.4+)
        Part -> Part : stick to current partition\nuntil batch full
    else Round-Robin (Legacy)
        Part -> Part : next partition
    end
    Part --> P : partition
end

P -> M : getLeader(partition)
M --> P : broker

@enduml
```

### Partitioning Strategies

| Strategy | When Used | Distribution | Ordering |
|----------|-----------|--------------|----------|
| **Key-based** | Key provided | By key hash | Per-key ordering |
| **Sticky** | No key (Kafka 2.4+) | Batch-based | None |
| **Round-robin** | No key (legacy) | Even | None |
| **Custom** | Custom partitioner | User-defined | User-defined |

### Key-Based Partitioning

```java
// Messages with same key go to same partition
producer.send(new ProducerRecord<>("orders", "customer-123", orderJson));
producer.send(new ProducerRecord<>("orders", "customer-123", anotherOrder));
// Both go to same partition → ordering guaranteed for customer-123
```

**Hash Function:**

```java
// Default partitioner (murmur2)
partition = Utils.toPositive(Utils.murmur2(keyBytes)) % numPartitions;
```

!!! warning "Key Distribution"
    Poorly distributed keys cause hot partitions. Avoid using boolean values, enum values with few options, or timestamps as keys.

### Sticky Partitioning (Kafka 2.4+)

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Legacy Round-Robin" as Legacy {
    rectangle "Msg 1 → P0" as L1
    rectangle "Msg 2 → P1" as L2
    rectangle "Msg 3 → P2" as L3
    rectangle "Msg 4 → P0" as L4
    note bottom: Each message to\ndifferent partition\n= many small batches
}

rectangle "Sticky Partitioner" as Sticky {
    rectangle "Msgs 1-100 → P0" as S1
    rectangle "Msgs 101-200 → P1" as S2
    rectangle "Msgs 201-300 → P2" as S3
    note bottom: Fill batch before\nswitching partition\n= fewer, larger batches
}

@enduml
```

**Benefits of sticky partitioning:**

- Larger batches → better compression
- Fewer requests → lower overhead
- Higher throughput

### Custom Partitioner

```java
public class GeoPartitioner implements Partitioner {

    @Override
    public int partition(String topic, Object key, byte[] keyBytes,
                        Object value, byte[] valueBytes, Cluster cluster) {
        List<PartitionInfo> partitions = cluster.partitionsForTopic(topic);
        int numPartitions = partitions.size();

        // Route by geographic region
        String region = extractRegion(value);
        switch (region) {
            case "US": return 0;
            case "EU": return 1;
            case "APAC": return 2;
            default: return Math.abs(region.hashCode()) % numPartitions;
        }
    }
}
```

```properties
partitioner.class=com.example.GeoPartitioner
```

---

## Consumer Load Balancing

### Consumer Group Distribution

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Topic: orders (6 partitions)" {
    queue "P0" as P0
    queue "P1" as P1
    queue "P2" as P2
    queue "P3" as P3
    queue "P4" as P4
    queue "P5" as P5
}

rectangle "Consumer Group" {
    rectangle "Consumer 1" as C1
    rectangle "Consumer 2" as C2
    rectangle "Consumer 3" as C3
}

P0 --> C1
P1 --> C1
P2 --> C2
P3 --> C2
P4 --> C3
P5 --> C3

note bottom of C2
  Each partition assigned
  to exactly one consumer
  in the group
end note

@enduml
```

### Assignment Strategies

| Strategy | Class | Distribution | Rebalance Impact |
|----------|-------|--------------|------------------|
| **Range** | `RangeAssignor` | Consecutive per topic | May unbalance |
| **RoundRobin** | `RoundRobinAssignor` | Even distribution | Moderate movement |
| **Sticky** | `StickyAssignor` | Even + minimize movement | Minimal movement |
| **CooperativeSticky** | `CooperativeStickyAssignor` | Same + incremental | Lowest impact |

```properties
# Recommended for production
partition.assignment.strategy=org.apache.kafka.clients.consumer.CooperativeStickyAssignor
```

### Range Assignment

```plantuml
@startuml

skinparam backgroundColor transparent

title Range Assignment (2 topics × 3 partitions, 2 consumers)

rectangle "Topic A" as TA {
    rectangle "P0" as TA0
    rectangle "P1" as TA1
    rectangle "P2" as TA2
}

rectangle "Topic B" as TB {
    rectangle "P0" as TB0
    rectangle "P1" as TB1
    rectangle "P2" as TB2
}

rectangle "Consumer 1" as C1
rectangle "Consumer 2" as C2

TA0 --> C1
TA1 --> C1
TA2 --> C2

TB0 --> C1
TB1 --> C1
TB2 --> C2

note bottom of C1
  Consumer 1: 4 partitions
  Consumer 2: 2 partitions
  (unbalanced!)
end note

@enduml
```

### RoundRobin Assignment

```plantuml
@startuml

skinparam backgroundColor transparent

title RoundRobin Assignment (2 topics × 3 partitions, 2 consumers)

rectangle "All Partitions (sorted)" as All {
    rectangle "A-P0, A-P1, A-P2, B-P0, B-P1, B-P2" as List
}

rectangle "Consumer 1\nA-P0, A-P2, B-P1" as C1

rectangle "Consumer 2\nA-P1, B-P0, B-P2" as C2

All --> C1 : odd positions
All --> C2 : even positions

note bottom
  Evenly distributed:
  3 partitions each
end note

@enduml
```

### Sticky Assignment

Minimizes partition movement during rebalance:

```plantuml
@startuml

skinparam backgroundColor transparent

title Sticky Assignment During Rebalance

rectangle "Before: 2 consumers" as Before {
    rectangle "C1: P0, P1, P2" as BC1
    rectangle "C2: P3, P4, P5" as BC2
}

rectangle "C3 joins" as Event

rectangle "After: 3 consumers" as After {
    rectangle "C1: P0, P1" as AC1
    rectangle "C2: P3, P4" as AC2
    rectangle "C3: P2, P5" as AC3
}

Before --> Event
Event --> After

note right of After
  Only P2 and P5 moved
  (minimal disruption)
end note

@enduml
```

---

## Broker Load Distribution

### Partition Leader Distribution

Well-distributed leadership ensures even broker load:

```plantuml
@startuml

skinparam backgroundColor transparent

title Ideal Leader Distribution

rectangle "Broker 1" as B1 {
    rectangle "Leader: P0, P3, P6" as B1L
    rectangle "Follower: P1, P4, P7" as B1F
}

rectangle "Broker 2" as B2 {
    rectangle "Leader: P1, P4, P7" as B2L
    rectangle "Follower: P2, P5, P8" as B2F
}

rectangle "Broker 3" as B3 {
    rectangle "Leader: P2, P5, P8" as B3L
    rectangle "Follower: P0, P3, P6" as B3F
}

note bottom
  Each broker leads 3 partitions
  = Balanced read/write load
end note

@enduml
```

### Monitoring Broker Load

```bash
# Check partition distribution (leaders per broker)
kafka-topics.sh --describe --topic orders \
    --bootstrap-server localhost:9092

# Trigger preferred leader election
kafka-leader-election.sh --bootstrap-server localhost:9092 \
    --election-type PREFERRED --all-topic-partitions
```

---

## Rack-Aware Load Balancing

### Rack-Aware Consumer Fetching (Kafka 2.4+)

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Rack A" {
    rectangle "Consumer\n(client.rack=rack-a)" as C
    rectangle "Follower\nBroker 2" as F1
}

rectangle "Rack B" {
    rectangle "Leader\nBroker 1" as L
    rectangle "Follower\nBroker 3" as F2
}

C --> F1 : Fetch from\nlocal follower

F1 --> L : Replicate

note bottom of C
  KIP-392: Consumer fetches
  from rack-local replica
  = Lower latency
  = Reduced cross-rack traffic
end note

@enduml
```

### Configuration

**Consumer:**

```properties
# Consumer's rack identity
client.rack=rack-a
```

**Broker:**

```properties
# Broker's rack identity
broker.rack=rack-a

# Allow follower fetching
replica.selector.class=org.apache.kafka.common.replica.RackAwareReplicaSelector
```

---

## Connection Load Balancing

### Connection Distribution

Kafka clients don't use connection load balancing in the traditional sense. Instead:

| Aspect | Behavior |
|--------|----------|
| **Connection target** | Determined by partition leader |
| **Number of connections** | One per broker needed (per client instance) |
| **Request routing** | Client routes to correct broker |

### Avoiding External Load Balancers

```plantuml
@startuml

skinparam backgroundColor transparent

title Why Not Use External Load Balancers

rectangle "Client" as C

rectangle "Load Balancer" as LB

rectangle "Brokers" as B {
    rectangle "Broker 1\n(Leader P0)" as B1
    rectangle "Broker 2\n(Leader P1)" as B2
}

C --> LB : Write to P0
LB --> B2 : Routes to wrong broker!

note bottom of LB
  Load balancer doesn't know
  partition leaders
  → Requests go to wrong broker
  → Broker returns NOT_LEADER_OR_FOLLOWER
  → Client refreshes metadata and retries
  → Extra latency + overhead
end note

@enduml
```

**When load balancers may be needed:**

- Security boundary crossing
- Service discovery in Kubernetes
- Must be TCP (layer 4), not HTTP

---

## Hot Partition Handling

### Detecting Hot Partitions

```plantuml
@startuml

skinparam backgroundColor transparent

title Hot Partition Scenario

rectangle "Topic: events" {
    rectangle "P0: 100K msgs/s" as P0 #pink
    rectangle "P1: 10K msgs/s" as P1
    rectangle "P2: 10K msgs/s" as P2
    rectangle "P3: 10K msgs/s" as P3
}

rectangle "Brokers" {
    rectangle "Broker 1\n(P0 Leader)\nOverloaded!" as B1 #pink
    rectangle "Broker 2\n(P1 Leader)" as B2
    rectangle "Broker 3\n(P2,P3 Leader)" as B3
}

P0 --> B1
P1 --> B2
P2 --> B3
P3 --> B3

@enduml
```

### Causes and Solutions

| Cause | Solution |
|-------|----------|
| Single popular key | Add secondary key component |
| Timestamp as key | Use business key instead |
| Too few partitions | Increase partition count |
| Uneven custom partitioner | Fix partitioner logic |

### Key Salting

```java
// Problem: Single customer generates massive traffic
producer.send(new ProducerRecord<>("orders", "big-customer", order));

// Solution: Add salt to distribute load
int salt = random.nextInt(10); // 0-9
String saltedKey = "big-customer-" + salt;
producer.send(new ProducerRecord<>("orders", saltedKey, order));

// Note: Ordering now spread across 10 partitions
// May need aggregation on consumer side
```

---

## Metrics for Load Monitoring

### Producer Metrics

| Metric | Description | Imbalance Indicator |
|--------|-------------|---------------------|
| `record-send-rate` | Records sent/sec | By broker comparison |
| `byte-rate` | Bytes sent/sec | By broker comparison |
| `request-rate` | Requests/sec | By broker comparison |
| `batch-size-avg` | Average batch size | Low = partitioning issue |

### Consumer Metrics

| Metric | Description | Imbalance Indicator |
|--------|-------------|---------------------|
| `records-consumed-rate` | Records/sec | By partition comparison |
| `fetch-rate` | Fetches/sec | By broker comparison |
| `records-lag` | Messages behind | High on single partition |

### Broker Metrics

```bash
# Check messages per partition
kafka-run-class.sh kafka.tools.GetOffsetShell \
    --broker-list localhost:9092 \
    --topic orders

# Per-broker request rate
kafka-run-class.sh kafka.tools.JmxTool \
    --object-name kafka.network:type=RequestMetrics,name=RequestsPerSec,request=Produce
```

---

## Best Practices

### Producer Best Practices

| Practice | Rationale |
|----------|-----------|
| Choose meaningful keys | Enable key-based routing |
| Avoid low-cardinality keys | Prevent hot partitions |
| Use sticky partitioner for keyless | Better batching |
| Monitor partition distribution | Detect imbalances early |

### Consumer Best Practices

| Practice | Rationale |
|----------|-----------|
| Use CooperativeStickyAssignor | Minimize rebalance impact |
| Match consumers to partitions | Full parallelism |
| Configure `client.rack` | Enable local fetching |
| Monitor lag per partition | Detect bottlenecks |

### Partition Count Guidelines

| Throughput | Partitions per Topic |
|------------|---------------------|
| < 10 MB/s | 6-12 |
| 10-100 MB/s | 12-50 |
| > 100 MB/s | 50+ (consider multiple topics) |

---

## Related Documentation

- [Metadata Management](metadata-management.md) - Partition leader discovery
- [Consumer Guide](../../application-development/consumers/index.md) - Consumer group details
- [Producer Guide](../../application-development/producers/index.md) - Producer configuration
- [Replication](../replication/index.md) - Leader election