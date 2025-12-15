---
title: "Kafka KRaft Mode"
description: "Apache Kafka KRaft architecture. Raft consensus, controller quorum, metadata log, and migration from ZooKeeper."
---

# Kafka KRaft Mode

KRaft (Kafka Raft) is Kafka's built-in consensus protocol that eliminates the ZooKeeper dependency. This document covers KRaft architecture, the Raft consensus implementation, metadata management, and operational procedures.

---

## KRaft Overview

### Architecture Comparison

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "ZooKeeper Mode (Legacy)" as zk {
    rectangle "ZooKeeper Ensemble" as zk_ens {
        rectangle "ZK 1" as z1
        rectangle "ZK 2" as z2
        rectangle "ZK 3" as z3
    }

    rectangle "Kafka Brokers" as zk_brokers {
        rectangle "Broker 1\n(Controller)" as zb1
        rectangle "Broker 2" as zb2
        rectangle "Broker 3" as zb3
    }

    z1 <--> z2
    z2 <--> z3
    z1 <--> z3

    zb1 --> z1 : metadata
    zb2 --> z2 : metadata
    zb3 --> z3 : metadata
}

rectangle "KRaft Mode" as kraft {
    rectangle "Controller Quorum" as ctrl {
        rectangle "Controller 1\n(Leader)" as c1
        rectangle "Controller 2" as c2
        rectangle "Controller 3" as c3
    }

    rectangle "Brokers" as kraft_brokers {
        rectangle "Broker 4" as kb1
        rectangle "Broker 5" as kb2
        rectangle "Broker 6" as kb3
    }

    c1 --> c2 : Raft replication
    c1 --> c3 : Raft replication

    c1 --> kb1 : metadata push
    c1 --> kb2 : metadata push
    c1 --> kb3 : metadata push
}

@enduml
```

### Key Benefits

| Aspect | ZooKeeper Mode | KRaft Mode |
|--------|----------------|------------|
| **Dependencies** | External ZooKeeper cluster | Self-contained |
| **Metadata storage** | ZooKeeper znodes | Internal `__cluster_metadata` topic |
| **Scalability** | Limited by ZK watches | Scales to millions of partitions |
| **Recovery time** | Minutes (full metadata read) | Seconds (incremental) |
| **Operational complexity** | Two systems to manage | Single system |
| **Metadata propagation** | Push-based via controller | Pull-based with caching |

---

## Raft Consensus Protocol

### Protocol Fundamentals

KRaft implements the Raft consensus algorithm with Kafka-specific optimizations.

```plantuml
@startuml

skinparam backgroundColor transparent

state "Follower" as Follower
state "Candidate" as Candidate
state "Leader" as Leader

[*] --> Follower : startup

Follower --> Candidate : election timeout\n(no heartbeat received)
Candidate --> Follower : discover leader\nor higher term
Candidate --> Candidate : election timeout\n(split vote)
Candidate --> Leader : receive majority votes
Leader --> Follower : discover higher term

note right of Follower
  - Responds to RPCs
  - Redirects clients to leader
  - Votes in elections
end note

note right of Leader
  - Handles all client requests
  - Replicates log entries
  - Sends heartbeats
end note

@enduml
```

### Raft Properties

| Property | Guarantee |
|----------|-----------|
| **Election safety** | At most one leader per term |
| **Leader append-only** | Leader never overwrites or deletes entries |
| **Log matching** | If logs contain entry with same index/term, logs are identical up to that point |
| **Leader completeness** | Committed entries appear in all future leaders' logs |
| **State machine safety** | All servers apply same log entries in same order |

### Term and Epoch

```plantuml
@startuml

skinparam backgroundColor transparent

concise "Leader" as L
concise "Term" as T

@0
L is "Controller-1"
T is "Term 1"

@10
L is "(election)"
T is "Term 2"

@12
L is "Controller-2"
T is "Term 2"

@25
L is "(election)"
T is "Term 3"

@28
L is "Controller-1"
T is "Term 3"

@enduml
```

| Concept | Description |
|---------|-------------|
| **Term** | Monotonically increasing logical clock |
| **Leader epoch** | Term in which current leader was elected |
| **High watermark** | Highest committed offset in metadata log |
| **End offset** | Highest offset in local log (may be uncommitted) |

---

## Controller Quorum

### Quorum Configuration

```properties
# Controller quorum voters
# Format: {node.id}@{host}:{port}
controller.quorum.voters=1@controller1:9093,2@controller2:9093,3@controller3:9093

# Controller listener
controller.listener.names=CONTROLLER
listeners=CONTROLLER://:9093

# Node identity
node.id=1
process.roles=controller
```

### Quorum Size Recommendations

| Cluster Size | Controller Count | Fault Tolerance |
|:------------:|:----------------:|:---------------:|
| Development | 1 | 0 failures |
| Small (< 10 brokers) | 3 | 1 failure |
| Medium (10-50 brokers) | 3 | 1 failure |
| Large (50+ brokers) | 5 | 2 failures |

!!! warning "Quorum Sizing"
    Controller quorum must have an odd number of voters. Even numbers provide no additional fault tolerance but increase coordination overhead.

### Leader Election Process

```plantuml
@startuml

skinparam backgroundColor transparent

participant "Controller-1\n(Follower)" as C1
participant "Controller-2\n(Follower)" as C2
participant "Controller-3\n(Follower)" as C3

note over C1, C3: Leader (Controller-0) failed

== Election Timeout on C1 ==
C1 -> C1 : Increment term to 5\nBecome candidate
C1 -> C2 : VoteRequest(term=5, lastOffset=1000)
C1 -> C3 : VoteRequest(term=5, lastOffset=1000)

C2 --> C1 : VoteResponse(granted=true)
C3 --> C1 : VoteResponse(granted=true)

note over C1: Received majority (3/3)\nBecome leader

C1 -> C1 : Become Leader
C1 -> C2 : BeginQuorumEpoch(term=5)
C1 -> C3 : BeginQuorumEpoch(term=5)

== Normal Operation ==
loop Heartbeat
    C1 -> C2 : Fetch(term=5)
    C1 -> C3 : Fetch(term=5)
end

@enduml
```

### Vote Request Criteria

A controller must grant a vote if:

| Criterion | Requirement |
|-----------|-------------|
| **Term** | Candidate's term ≥ voter's current term |
| **Log completeness** | Candidate's log is at least as up-to-date |
| **Vote status** | Voter has not voted for another candidate this term |

Log comparison (up-to-date check):

```
candidate_log_up_to_date =
    (candidate.lastLogTerm > voter.lastLogTerm) OR
    (candidate.lastLogTerm == voter.lastLogTerm AND
     candidate.lastLogOffset >= voter.lastLogOffset)
```

---

## Metadata Log

### `__cluster_metadata` Topic

The controller quorum stores all cluster metadata in a single-partition internal topic.

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "__cluster_metadata-0" as topic {
    rectangle "Segment 0\n(00000000000000000000.log)" as seg0
    rectangle "Segment 1\n(00000000000000001000.log)" as seg1
    rectangle "Segment 2\n(00000000000000002000.log)" as seg2
    rectangle "Active Segment" as active
}

rectangle "Snapshot\n(00000000000000002000-\n0000000005.checkpoint)" as snapshot

seg0 -right-> seg1
seg1 -right-> seg2
seg2 -right-> active

snapshot -up-> seg2 : snapshot at offset 2000

note bottom of topic
  Single partition replicated
  across controller quorum
  using Raft consensus
end note

@enduml
```

### Metadata Record Types

| Record Type | Description |
|-------------|-------------|
| `TopicRecord` | Topic creation with UUID |
| `PartitionRecord` | Partition assignment and replicas |
| `PartitionChangeRecord` | ISR and leader changes |
| `BrokerRegistrationChangeRecord` | Broker registration updates |
| `ConfigRecord` | Dynamic configuration changes |
| `ClientQuotaRecord` | Client quota settings |
| `ProducerIdsRecord` | Producer ID allocation |
| `AccessControlEntryRecord` | ACL entries |
| `RemoveTopicRecord` | Topic deletion |
| `FeatureLevelRecord` | Cluster feature flags |
| `NoOpRecord` | Leader election marker |

### Metadata Log Format

```
MetadataRecordBatch =>
    BaseOffset => INT64
    BatchLength => INT32
    PartitionLeaderEpoch => INT32
    Magic => INT8 (2)
    CRC => INT32
    Attributes => INT16
    LastOffsetDelta => INT32
    BaseTimestamp => INT64
    MaxTimestamp => INT64
    ProducerId => INT64 (-1)
    ProducerEpoch => INT16 (-1)
    BaseSequence => INT32 (-1)
    Records => [Record]

Record =>
    Length => VARINT
    Attributes => INT8
    TimestampDelta => VARLONG
    OffsetDelta => VARINT
    KeyLength => VARINT
    Key => BYTES
    ValueLength => VARINT
    Value => BYTES  # Serialized metadata record
```

---

## Metadata Snapshots

### Snapshot Purpose

Snapshots compact the metadata log by capturing the full cluster state at a point in time.

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Without Snapshots" as without {
    rectangle "Log Entry 1\nCreate topic-a" as l1
    rectangle "Log Entry 2\nCreate topic-b" as l2
    rectangle "Log Entry 3\nDelete topic-a" as l3
    rectangle "Log Entry 4\nUpdate topic-b" as l4
    rectangle "Log Entry 5\nCreate topic-c" as l5
}

rectangle "With Snapshot" as with_snap {
    rectangle "Snapshot @ offset 3\n- topic-b (updated)\n- (topic-a deleted)" as snap
    rectangle "Log Entry 4\nUpdate topic-b" as s4
    rectangle "Log Entry 5\nCreate topic-c" as s5
}

l1 -right-> l2
l2 -right-> l3
l3 -right-> l4
l4 -right-> l5

snap -right-> s4
s4 -right-> s5

note bottom of with_snap
  Snapshot contains materialized
  state; log entries before
  snapshot offset are discarded
end note

@enduml
```

### Snapshot Configuration

```properties
# Snapshot generation interval (bytes of log since last snapshot)
metadata.log.max.record.bytes.between.snapshots=20971520

# Maximum metadata log size before forcing snapshot
metadata.log.max.snapshot.interval.ms=3600000

# Snapshot directory
metadata.log.dir=/var/kafka-logs/__cluster_metadata-0
```

### Snapshot Operations

```bash
# List metadata snapshots
ls -la /var/kafka-logs/__cluster_metadata-0/*.checkpoint

# Describe snapshot contents
kafka-metadata.sh --snapshot /var/kafka-logs/__cluster_metadata-0/00000000000000001000-0000000003.checkpoint \
  --command describe

# Read specific records from snapshot
kafka-metadata.sh --snapshot /var/kafka-logs/__cluster_metadata-0/00000000000000001000-0000000003.checkpoint \
  --command topics
```

---

## Broker Registration

### Registration Flow

```plantuml
@startuml

skinparam backgroundColor transparent

participant "New Broker" as Broker
participant "Active Controller" as Controller
participant "Metadata Log" as Log

Broker -> Controller : BrokerRegistrationRequest\n(node.id, listeners, rack, features)

Controller -> Controller : Validate registration

Controller -> Log : Append BrokerRegistrationChangeRecord

Log --> Controller : Committed at offset N

Controller --> Broker : BrokerRegistrationResponse\n(broker_epoch)

loop Heartbeat
    Broker -> Controller : BrokerHeartbeatRequest\n(broker_epoch, current_state)
    Controller --> Broker : BrokerHeartbeatResponse\n(should_fence, should_shutdown)
end

note over Broker, Controller
  Broker must send heartbeats
  within broker.session.timeout.ms
  to remain active
end note

@enduml
```

### Broker States

```plantuml
@startuml

skinparam backgroundColor transparent

state "Fenced" as Fenced
state "Unfenced" as Unfenced
state "Controlled Shutdown" as Shutdown

[*] --> Fenced : registration accepted

Fenced --> Unfenced : heartbeat accepted\n(all replicas caught up)
Unfenced --> Fenced : heartbeat timeout\n(broker.session.timeout.ms)
Unfenced --> Shutdown : controlled shutdown\nrequest
Shutdown --> [*] : deregistration complete

note right of Fenced
  Cannot be leader
  Can be follower
end note

note right of Unfenced
  Normal operation
  Can be leader
end note

@enduml
```

### Registration Configuration

```properties
# Broker heartbeat interval
broker.heartbeat.interval.ms=2000

# Session timeout (broker considered dead)
broker.session.timeout.ms=18000

# Initial broker registration timeout
initial.broker.registration.timeout.ms=60000
```

---

## Metadata Propagation

### Push-Based Propagation

The active controller pushes metadata updates to all brokers.

```plantuml
@startuml

skinparam backgroundColor transparent

participant "Controller\n(Leader)" as Controller
participant "Broker 1" as B1
participant "Broker 2" as B2
participant "Broker 3" as B3

note over Controller: Topic created\nMetadata offset: 1000 -> 1001

Controller -> B1 : UpdateMetadataRequest\n(offset=1001, records=[TopicRecord])
Controller -> B2 : UpdateMetadataRequest\n(offset=1001, records=[TopicRecord])
Controller -> B3 : UpdateMetadataRequest\n(offset=1001, records=[TopicRecord])

B1 --> Controller : UpdateMetadataResponse
B2 --> Controller : UpdateMetadataResponse
B3 --> Controller : UpdateMetadataResponse

note over B1, B3
  Brokers cache metadata locally
  for fast client responses
end note

@enduml
```

### Metadata Caching

| Cache Component | Description |
|-----------------|-------------|
| **Topic metadata** | Topic IDs, partition counts, configs |
| **Partition metadata** | Leaders, ISR, replicas |
| **Broker metadata** | Endpoints, rack, features |
| **Controller metadata** | Active controller location |

### Broker Fetch Optimization

```plantuml
@startuml

skinparam backgroundColor transparent

participant "Broker" as Broker
participant "Controller" as Controller

note over Broker: Needs metadata\n(local offset: 950)

Broker -> Controller : FetchRequest\n(fetchOffset=950)

alt Offset in log
    Controller --> Broker : FetchResponse\n(records 950-1000)
    Broker -> Broker : Apply records\nUpdate local offset
else Offset before snapshot
    Controller --> Broker : FetchResponse\n(snapshotId, error=OFFSET_OUT_OF_RANGE)
    Broker -> Controller : FetchSnapshotRequest\n(snapshotId)
    Controller --> Broker : FetchSnapshotResponse\n(snapshot data)
    Broker -> Broker : Load snapshot\nResume from snapshot offset
end

@enduml
```

---

## KRaft Operations

### Cluster Initialization

```bash
# Generate cluster ID
CLUSTER_ID=$(kafka-storage.sh random-uuid)
echo $CLUSTER_ID

# Format storage on each controller/broker
kafka-storage.sh format \
  --config /etc/kafka/kraft/server.properties \
  --cluster-id $CLUSTER_ID

# Start controllers first, then brokers
kafka-server-start.sh /etc/kafka/kraft/controller.properties
kafka-server-start.sh /etc/kafka/kraft/broker.properties
```

### Describe Quorum

```bash
# Check quorum status
kafka-metadata.sh --snapshot /var/kafka-logs/__cluster_metadata-0/00000000000000000000.log \
  --command "describe"

# Or use admin client
kafka-metadata-quorum.sh --bootstrap-controller controller1:9093 describe

# Output includes:
# - Current leader
# - Current term/epoch
# - High watermark
# - Voter states and lag
```

### Controller Failover

```plantuml
@startuml

skinparam backgroundColor transparent

concise "Controller-1" as C1
concise "Controller-2" as C2
concise "Controller-3" as C3
concise "Active" as Active

@0
C1 is "Leader"
C2 is "Follower"
C3 is "Follower"
Active is "Controller-1"

@5
C1 is "Failed"
C2 is "Candidate"
C3 is "Candidate"
Active is "(electing)"

@7
C1 is "Failed"
C2 is "Leader"
C3 is "Follower"
Active is "Controller-2"

@15
C1 is "Follower"
C2 is "Leader"
C3 is "Follower"
Active is "Controller-2"

@enduml
```

### Metadata Recovery

```bash
# If metadata is corrupted, recover from other controllers
# Stop the affected controller
kafka-server-stop.sh

# Clear metadata directory
rm -rf /var/kafka-logs/__cluster_metadata-0/*

# Restart - will fetch from leader
kafka-server-start.sh /etc/kafka/kraft/controller.properties
```

---

## ZooKeeper Migration

### Migration Overview

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Phase 1: Dual-Write" as phase1 {
    rectangle "ZooKeeper" as zk1
    rectangle "KRaft Controllers" as kraft1
    rectangle "Brokers" as brokers1

    zk1 <-- brokers1 : read/write
    kraft1 <-- brokers1 : mirror writes
}

rectangle "Phase 2: KRaft Primary" as phase2 {
    rectangle "ZooKeeper" as zk2
    rectangle "KRaft Controllers" as kraft2
    rectangle "Brokers" as brokers2

    zk2 <.. brokers2 : read only
    kraft2 <-- brokers2 : read/write
}

rectangle "Phase 3: KRaft Only" as phase3 {
    rectangle "KRaft Controllers" as kraft3
    rectangle "Brokers" as brokers3

    kraft3 <-- brokers3 : read/write
}

phase1 -down-> phase2 : enable migration
phase2 -down-> phase3 : finalize migration

@enduml
```

### Migration Steps

1. **Deploy controller quorum**
   ```bash
   # On each controller node
   kafka-storage.sh format \
     --config /etc/kafka/kraft/controller.properties \
     --cluster-id $(kafka-cluster.sh cluster-id --bootstrap-server broker:9092)

   kafka-server-start.sh /etc/kafka/kraft/controller.properties
   ```

2. **Enable migration mode on brokers**
   ```properties
   # Add to existing broker config
   controller.quorum.voters=1@controller1:9093,2@controller2:9093,3@controller3:9093
   zookeeper.metadata.migration.enable=true
   ```

3. **Rolling restart brokers**
   ```bash
   # Restart each broker with new config
   kafka-server-stop.sh
   kafka-server-start.sh /etc/kafka/server.properties
   ```

4. **Verify migration readiness**
   ```bash
   kafka-metadata.sh --snapshot /var/kafka-logs/__cluster_metadata-0/00000000000000000000.log \
     --command migration-state
   ```

5. **Finalize migration**
   ```bash
   # Trigger final migration (irreversible)
   kafka-metadata-quorum.sh --bootstrap-controller controller1:9093 \
     finalize-migration
   ```

### Migration Validation

| Check | Command | Expected |
|-------|---------|----------|
| Broker migration state | `kafka-metadata.sh ... --command brokers` | All in KRAFT mode |
| Controller quorum | `kafka-metadata-quorum.sh describe` | Leader elected, voters healthy |
| Topic metadata | `kafka-topics.sh --describe` | All topics visible |
| Consumer groups | `kafka-consumer-groups.sh --list` | All groups visible |

!!! danger "Migration is One-Way"
    Once migration is finalized, rollback to ZooKeeper mode is not supported. Ensure thorough testing in non-production environments before production migration.

---

## KRaft Configuration Reference

### Controller Settings

| Configuration | Default | Description |
|---------------|:-------:|-------------|
| `process.roles` | - | Must include `controller` |
| `node.id` | - | Unique controller identifier |
| `controller.quorum.voters` | - | Voter list: `id@host:port,...` |
| `controller.listener.names` | - | Controller listener name |

### Metadata Settings

| Configuration | Default | Description |
|---------------|:-------:|-------------|
| `metadata.log.dir` | log.dirs | Metadata log directory |
| `metadata.log.segment.bytes` | 1073741824 | Segment size |
| `metadata.log.max.record.bytes.between.snapshots` | 20971520 | Bytes before snapshot |
| `metadata.max.retention.bytes` | 104857600 | Max metadata log size |

### Quorum Settings

| Configuration | Default | Description |
|---------------|:-------:|-------------|
| `controller.quorum.election.timeout.ms` | 1000 | Election timeout |
| `controller.quorum.fetch.timeout.ms` | 2000 | Fetch timeout |
| `controller.quorum.election.backoff.max.ms` | 1000 | Max election backoff |
| `controller.quorum.retry.backoff.ms` | 20 | Retry backoff |

---

## Monitoring KRaft

### Key Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `kafka.controller:type=KafkaController,name=ActiveControllerCount` | Active controllers | ≠ 1 |
| `kafka.controller:type=QuorumController,name=LastAppliedRecordOffset` | Applied metadata offset | Lag |
| `kafka.controller:type=QuorumController,name=LastAppliedRecordTimestamp` | Last apply time | Stale |
| `kafka.controller:type=QuorumController,name=MetadataErrorCount` | Metadata errors | > 0 |
| `kafka.raft:type=RaftManager,name=CurrentLeader` | Current leader ID | Changes |
| `kafka.raft:type=RaftManager,name=HighWatermark` | Committed offset | Lag |

### Health Checks

```bash
# Check controller is active
kafka-metadata-quorum.sh --bootstrap-controller controller1:9093 describe --status

# Verify all voters are online
kafka-metadata-quorum.sh --bootstrap-controller controller1:9093 describe --replication

# Check metadata lag across brokers
kafka-metadata.sh --snapshot /var/kafka-logs/__cluster_metadata-0/*.log \
  --command "broker-state"
```

---

## Version Compatibility

| Feature | Kafka Version |
|---------|---------------|
| KRaft preview | 2.8.0 |
| KRaft production-ready | 3.3.0 |
| ZooKeeper migration | 3.4.0 |
| Migration finalization | 3.5.0 |
| ZooKeeper removal | 4.0 (planned) |

---

## Related Documentation

- [Brokers Overview](index.md) - Broker architecture
- [Cluster Management](../cluster-management/index.md) - Cluster operations
- [Fault Tolerance](../fault-tolerance/index.md) - Failure handling
- [Replication](../replication/index.md) - Replication protocol
