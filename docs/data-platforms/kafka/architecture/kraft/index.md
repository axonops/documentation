---
title: "KRaft: Kafka Raft Consensus"
description: "Deep dive into KRaft, Kafka's built-in consensus protocol. Raft mechanics, metadata management, controller quorum, and migration from ZooKeeper."
search:
  boost: 3
---

# KRaft: Kafka Raft Consensus

KRaft (Kafka Raft) is Kafka's built-in consensus protocol that replaced Apache ZooKeeper for metadata management. Introduced in Kafka 2.8 and production-ready since Kafka 3.3, KRaft simplifies Kafka's architecture by eliminating the external ZooKeeper dependency.

---

## Why KRaft Replaced ZooKeeper

### Architectural Simplification

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam rectangle {
    BackgroundColor #F5F5F5
    BorderColor #333333
}

title Before and After: ZooKeeper vs KRaft

rectangle "ZooKeeper Mode (Legacy)" as zk #FFCDD2 {
    rectangle "Kafka Cluster" as kc1 {
        rectangle "Broker 1" as b1
        rectangle "Broker 2" as b2
        rectangle "Broker 3" as b3
    }

    rectangle "ZooKeeper Ensemble" as zke {
        rectangle "ZK 1" as z1
        rectangle "ZK 2" as z2
        rectangle "ZK 3" as z3
    }

    b1 --> zke
    b2 --> zke
    b3 --> zke
}

rectangle "KRaft Mode" as kraft #C8E6C9 {
    rectangle "Kafka Cluster" as kc2 {
        rectangle "Controller 1" as c1
        rectangle "Controller 2" as c2
        rectangle "Controller 3" as c3
        rectangle "Broker 1" as kb1
        rectangle "Broker 2" as kb2
    }

    c1 <--> c2
    c2 <--> c3
    c1 <--> c3

    c1 --> kb1
    c1 --> kb2
}

note bottom of zk
Two separate systems to operate
Different failure modes
Split-brain risks between Kafka and ZK
end note

note bottom of kraft
Single system
Unified failure handling
No external dependencies
end note
@enduml
```

### Benefits of KRaft

| Aspect | ZooKeeper Mode | KRaft Mode |
|--------|----------------|------------|
| **Operational complexity** | Two systems to manage | Single system |
| **Scaling** | Higher metadata overhead; lower practical limits | Higher practical partition counts |
| **Recovery time** | Minutes (controller failover) | Seconds |
| **Metadata propagation** | Pull-based, eventually consistent | Fetch-based, ordered |
| **Security** | Separate auth for ZK | Unified Kafka security |
| **Monitoring** | Two metric systems | Single metric system |

---

## Raft Consensus Protocol

KRaft implements the Raft consensus algorithm for leader election and log replication among controllers.

### Raft Fundamentals

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam state {
    BackgroundColor #F5F5F5
    BorderColor #333333
}

title Raft Node States

[*] --> Follower : Start

state Follower {
    Follower : Receives log entries from leader
    Follower : Responds to leader heartbeats
    Follower : Votes in elections
}

state Candidate {
    Candidate : Requests votes from peers
    Candidate : Votes for itself
    Candidate : Waits for election result
}

state Leader {
    Leader : Sends heartbeats
    Leader : Replicates log entries
    Leader : Commits entries when quorum reached
}

Follower --> Candidate : Election timeout\n(no heartbeat received)
Candidate --> Leader : Receives majority votes
Candidate --> Follower : Discovers leader\nor higher term
Candidate --> Candidate : Election timeout\n(split vote)
Leader --> Follower : Discovers higher term

@enduml
```

### Leader Election

When the controller leader fails, remaining controllers elect a new leader:

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam sequence {
    ArrowColor #333333
    LifeLineBorderColor #666666
    ParticipantBackgroundColor #F5F5F5
}

title KRaft Leader Election

participant "Controller 1\n(Leader)" as c1
participant "Controller 2\n(Follower)" as c2
participant "Controller 3\n(Follower)" as c3

== Normal Operation ==
c1 -> c2 : Heartbeat (term=5)
c1 -> c3 : Heartbeat (term=5)
c2 --> c1 : Ack
c3 --> c1 : Ack

== Leader Failure ==
c1 -> c1 : CRASH
note over c1 : No more heartbeats

c2 -> c2 : Election timeout
c2 -> c2 : Increment term to 6\nBecome candidate

== Election ==
c2 -> c3 : RequestVote(term=6, lastLogIndex, lastLogTerm)
c3 -> c3 : Grant vote\n(candidate log up-to-date)
c3 --> c2 : VoteGranted

c2 -> c2 : Received majority (2/3)\nBecome leader

== New Leader ==
c2 -> c3 : Heartbeat (term=6)
note over c2 : Controller 2 is now leader

@enduml
```

**Election rules:**

1. **Term** — Logical clock incremented on each election
2. **Vote** — Each controller votes once per term
3. **Log completeness** — Only vote for candidates with up-to-date logs
4. **Majority** — Candidate needs `(n/2) + 1` votes to become leader

### Log Replication

The leader replicates metadata log entries to followers:

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam sequence {
    ArrowColor #333333
    LifeLineBorderColor #666666
    ParticipantBackgroundColor #F5F5F5
}

title Log Replication and Commit

participant "Controller 1\n(Leader)" as c1
participant "Controller 2\n(Follower)" as c2
participant "Controller 3\n(Follower)" as c3

== Client Request ==
c1 <- c1 : CreateTopic request

c1 -> c1 : Append to local log\n(index=100, uncommitted)

== Replication ==
c1 -> c2 : AppendEntries(entries=[100])
c1 -> c3 : AppendEntries(entries=[100])

c2 -> c2 : Append to log
c2 --> c1 : Success(matchIndex=100)

c3 -> c3 : Append to log
c3 --> c1 : Success(matchIndex=100)

== Commit ==
c1 -> c1 : Quorum reached (3/3)\nCommit index=100

c1 -> c2 : Heartbeat(commitIndex=100)
c1 -> c3 : Heartbeat(commitIndex=100)

note over c1, c3
Entry 100 now committed
Applied to state machine
Topic creation complete
end note

@enduml
```

**Commit rules:**

- Entry is committed when replicated to a majority of controllers
- Only entries from the current term can be committed directly
- Committing an entry commits all prior entries

### Quorum and Fault Tolerance

| Controllers | Quorum | Tolerated Failures |
|-------------|--------|-------------------|
| 1 | 1 | 0 (no fault tolerance) |
| 3 | 2 | 1 |
| 5 | 3 | 2 |
| 7 | 4 | 3 |

**Recommendation:** Use 3 controllers for most deployments. Use 5 for large clusters requiring higher availability.

---

## Metadata Log

All cluster metadata is stored in a replicated log, not in an external system.

### Log Structure

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Metadata Log Structure

rectangle "Metadata Log" as log {
    rectangle "Offset 0: FeatureLevelRecord" as o0 #E3F2FD
    rectangle "Offset 1: RegisterBrokerRecord(broker=1)" as o1 #E3F2FD
    rectangle "Offset 2: RegisterBrokerRecord(broker=2)" as o2 #E3F2FD
    rectangle "Offset 3: TopicRecord(name=orders)" as o3 #E3F2FD
    rectangle "Offset 4: PartitionRecord(topic=orders, p=0)" as o4 #E3F2FD
    rectangle "Offset 5: PartitionChangeRecord(leader=1)" as o5 #E3F2FD
    rectangle "..." as dots
    rectangle "Offset N: ConfigRecord(retention.ms=...)" as on #FFF9C4
}

o0 -[hidden]-> o1
o1 -[hidden]-> o2
o2 -[hidden]-> o3
o3 -[hidden]-> o4
o4 -[hidden]-> o5
o5 -[hidden]-> dots
dots -[hidden]-> on

note bottom of log
Append-only log
Each entry is a metadata change
Replicated across all controllers
end note
@enduml
```

### Record Types

| Category | Record Types (non-exhaustive) |
|----------|--------------|
| **Cluster** | `FeatureLevelRecord`, `ZkMigrationStateRecord` |
| **Brokers** | `RegisterBrokerRecord`, `UnregisterBrokerRecord`, `BrokerRegistrationChangeRecord`, `FenceBrokerRecord`, `UnfenceBrokerRecord` |
| **Topics** | `TopicRecord`, `RemoveTopicRecord` |
| **Partitions** | `PartitionRecord`, `PartitionChangeRecord` |
| **Configuration** | `ConfigRecord`, `RemoveConfigRecord` |
| **Security** | `ClientQuotaRecord`, `UserScramCredentialRecord`, `AccessControlEntryRecord` |
| **Producers** | `ProducerIdsRecord` |

### Snapshots

To prevent unbounded log growth, controllers periodically create snapshots:

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Snapshot and Log Compaction

rectangle "Before Snapshot" as before {
    rectangle "Log Segment 1\n(offsets 0-999)" as s1 #E3F2FD
    rectangle "Log Segment 2\n(offsets 1000-1999)" as s2 #E3F2FD
    rectangle "Log Segment 3\n(offsets 2000-2500)" as s3 #FFF9C4
}

rectangle "After Snapshot" as after {
    rectangle "Snapshot @ offset 2000\n(full state)" as snap #C8E6C9
    rectangle "Log Segment 3\n(offsets 2000-2500)" as s3b #FFF9C4
}

before -[hidden]-> after

note bottom of snap
Snapshot contains:
- All broker registrations
- All topics and partitions
- All configurations
- Current leader/ISR state
end note
@enduml
```

**Snapshot configuration:**

```properties
# Minimum records between snapshots
metadata.log.max.record.bytes.between.snapshots=20971520

# Maximum time between snapshots
metadata.log.max.snapshot.interval.ms=3600000
```

### Storage Location

```bash
# Metadata log directory structure
/var/kafka-logs/__cluster_metadata-0/
├── 00000000000000000000.log      # Log segment
├── 00000000000000000000.index    # Offset index
├── 00000000000000000000.timeindex
├── 00000000000000001000.log      # Next segment
├── 00000000000000001000-checkpoint.snapshot  # Snapshot
└── leader-epoch-checkpoint
```

---

## Controller Communication

### Controller-to-Controller (Raft)

Controllers communicate using the Raft protocol over a dedicated listener:

```properties
# Controller listener configuration
controller.listener.names=CONTROLLER
listeners=CONTROLLER://0.0.0.0:9093

# Inter-controller security
listener.security.protocol.map=CONTROLLER:SSL
```

### Controller-to-Broker (Metadata Fetch)

In KRaft, brokers fetch metadata updates from the controller log (unlike ZooKeeper watch-based updates):

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam sequence {
    ArrowColor #333333
    LifeLineBorderColor #666666
    ParticipantBackgroundColor #F5F5F5
}

title Metadata Fetch by Brokers

participant "Controller\n(Leader)" as ctrl
participant "Broker 1" as b1
participant "Broker 2" as b2

== Broker Registration ==
b1 -> ctrl : BrokerRegistrationRequest
ctrl --> b1 : BrokerRegistrationResponse

b1 -> ctrl : BrokerHeartbeatRequest
ctrl --> b1 : BrokerHeartbeatResponse

== Metadata Fetch ==
b1 -> ctrl : FetchRequest(__cluster_metadata)
note right: Broker fetches from\nits last known offset

ctrl --> b1 : FetchResponse\n(new metadata records)

b1 -> b1 : Apply metadata updates

== Continuous Sync ==
loop Every fetch interval
    b1 -> ctrl : FetchRequest(offset=N)
    ctrl --> b1 : FetchResponse(records N+1...)
end

@enduml
```

**Key difference from ZooKeeper:**

| Aspect | ZooKeeper Mode | KRaft Mode |
|--------|----------------|------------|
| **Propagation** | Watch-based, async | Fetch-based, controlled |
| **Consistency** | Eventual | Offset-based, ordered |
| **Latency** | Variable | Predictable |

---

## Quorum Configuration

### Controller Quorum Voters

```properties
# Define the controller quorum
controller.quorum.voters=1@controller1:9093,2@controller2:9093,3@controller3:9093

# Format: node.id@host:port
# All controllers must have the same voter list
```

### Deployment Modes

#### Combined Mode (Development/Small Clusters)

Controllers and brokers run in the same JVM:

```properties
# server.properties for combined mode
process.roles=broker,controller
node.id=1
controller.quorum.voters=1@node1:9093,2@node2:9093,3@node3:9093
```

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Combined Mode

rectangle "Node 1" as n1 #E3F2FD {
    rectangle "Controller" as c1
    rectangle "Broker" as b1
}

rectangle "Node 2" as n2 #E3F2FD {
    rectangle "Controller" as c2
    rectangle "Broker" as b2
}

rectangle "Node 3" as n3 #E3F2FD {
    rectangle "Controller" as c3
    rectangle "Broker" as b3
}

c1 <--> c2 : Raft
c2 <--> c3 : Raft
c1 <--> c3 : Raft

note bottom
Simpler deployment
Shared resources
Suitable for < 10 brokers
end note
@enduml
```

#### Isolated Mode (Production/Large Clusters)

Dedicated controller nodes separate from brokers:

```properties
# controller.properties (controller-only nodes)
process.roles=controller
node.id=1
controller.quorum.voters=1@ctrl1:9093,2@ctrl2:9093,3@ctrl3:9093

# broker.properties (broker-only nodes)
process.roles=broker
node.id=101
controller.quorum.voters=1@ctrl1:9093,2@ctrl2:9093,3@ctrl3:9093
```

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Isolated Mode

rectangle "Controller Tier" as ct #FFF9C4 {
    rectangle "Controller 1" as c1
    rectangle "Controller 2" as c2
    rectangle "Controller 3" as c3
}

rectangle "Broker Tier" as bt #E3F2FD {
    rectangle "Broker 101" as b1
    rectangle "Broker 102" as b2
    rectangle "Broker 103" as b3
    rectangle "Broker 104" as b4
    rectangle "Broker 105" as b5
}

c1 <--> c2 : Raft
c2 <--> c3 : Raft
c1 <--> c3 : Raft

c1 --> b1
c1 --> b2
c1 --> b3
c1 --> b4
c1 --> b5

note bottom of ct
Dedicated resources
Independent scaling
Recommended for > 10 brokers
end note
@enduml
```

### Controller Sizing

Kafka controllers keep cluster metadata in memory and on disk.

| Cluster Size | Controller Count | Controller Resources |
|--------------|------------------|---------------------|
| Development | 1 (no HA) | 1 CPU, 1GB RAM |
| Small (< 10 brokers) | 3 (combined mode) | 2 CPU, 4GB RAM |
| Medium (10-50 brokers) | 3 (isolated) | 4 CPU, 8GB RAM |
| Large (50+ brokers) | 5 (isolated) | 8 CPU, 16GB RAM |

!!! note "Sourcing"
    The table above reflects repository guidance. Kafka's KRaft ops docs note that typical clusters can use ~5 GB memory and ~5 GB disk for the metadata log directory.

---

## Failover Behavior

### Controller Leader Failure

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Controller Failover Timeline

concise "Controller 1" as c1
concise "Controller 2" as c2
concise "Controller 3" as c3
concise "Cluster State" as state

@0
c1 is Leader
c2 is Follower
c3 is Follower
state is Normal

@100
c1 is {-}
state is "Election"

@150
c2 is Candidate

@200
c2 is Leader
c3 is Follower
state is Normal

@0 <-> @100 : Leader serving
@100 <-> @200 : Failover (~100-200ms)

@enduml
```

**Failover characteristics:**

| Metric | Typical Value |
|--------|---------------|
| Detection time | ≤ `controller.quorum.fetch.timeout.ms` (default 2000ms) |
| Election time | ≤ `controller.quorum.election.timeout.ms` (default 1000ms) |
| Total failover | Detection + election + metadata catch-up |

### Broker Behavior During Failover

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam sequence {
    ArrowColor #333333
    LifeLineBorderColor #666666
    ParticipantBackgroundColor #F5F5F5
}

title Broker Behavior During Controller Failover

participant "Broker" as broker
participant "Controller 1\n(Old Leader)" as c1
participant "Controller 2\n(New Leader)" as c2

== Normal Operation ==
broker -> c1 : BrokerHeartbeatRequest
c1 --> broker : BrokerHeartbeatResponse

== Controller Failure ==
broker -> c1 : BrokerHeartbeatRequest
note right: No response (timeout)

broker -> broker : Retry with backoff

== New Leader Elected ==
broker -> c2 : BrokerHeartbeatRequest
c2 --> broker : BrokerHeartbeatResponse

broker -> c2 : FetchRequest(__cluster_metadata)
c2 --> broker : FetchResponse

note over broker
Broker continues serving clients
throughout controller failover.
Metadata updates delayed but
read/write operations continue.
end note

@enduml
```

**Key point:** Broker data operations (produce/consume) continue during controller failover. Only metadata operations (topic creation, leader election) are temporarily blocked.

### Split-Brain Prevention

Raft's quorum requirement prevents split-brain:

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Split-Brain Prevention

rectangle "Network Partition" as np {
    rectangle "Partition A" as pa #C8E6C9 {
        rectangle "Controller 1" as c1
        rectangle "Controller 2" as c2
        note bottom: Quorum (2/3)\nCan elect leader
    }

    rectangle "Partition B" as pb #FFCDD2 {
        rectangle "Controller 3" as c3
        note bottom: No quorum (1/3)\nCannot elect leader
    }
}

c1 <--> c2 : Raft OK
c1 <..> c3 : Network partition
c2 <..> c3 : Network partition

note bottom of np
Only the partition with quorum
can elect a leader and make progress.
Minority partition is read-only.
end note
@enduml
```

---

## Migration from ZooKeeper

### Migration Modes

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam state {
    BackgroundColor #F5F5F5
    BorderColor #333333
}

title ZooKeeper to KRaft Migration

[*] --> ZooKeeper : Initial state

state ZooKeeper {
    ZooKeeper : Brokers use ZK
    ZooKeeper : Controller in ZK mode
}

state "KRaft (Migration)" as migration {
    migration : Controllers running
    migration : ZK still authoritative
    migration : Dual-write mode
}

state KRaft {
    KRaft : ZK removed
    KRaft : Controllers authoritative
    KRaft : Full KRaft mode
}

ZooKeeper --> migration : Start migration
migration --> KRaft : Complete migration
migration --> ZooKeeper : Rollback (if needed)

@enduml
```

### Migration Steps

1. **Deploy controller quorum:**

```bash
# Format controller storage
kafka-storage.sh format -t $(kafka-storage.sh random-uuid) \
  -c controller.properties
```

2. **Enable migration mode:**

```properties
# In broker server.properties
zookeeper.metadata.migration.enable=true
controller.quorum.voters=1@ctrl1:9093,2@ctrl2:9093,3@ctrl3:9093
```

3. **Start controllers and migrate:**

```bash
# Controllers will sync metadata from ZooKeeper
# Monitor migration progress
kafka-metadata-shell.sh --snapshot /var/kafka-logs/__cluster_metadata-0/*.log \
  describe
```

4. **Restart brokers in KRaft mode:**

```properties
# Remove ZK config, enable KRaft
process.roles=broker
controller.quorum.voters=1@ctrl1:9093,2@ctrl2:9093,3@ctrl3:9093
# Remove: zookeeper.connect=...
```

### Rollback Capability

During migration, rollback is possible until finalization:

| Phase | Rollback Possible | Data Safe |
|-------|-------------------|-----------|
| Controllers deployed | Yes | Yes |
| Dual-write mode | Yes | Yes |
| Brokers migrated | Yes (restart with ZK) | Yes |
| Migration finalized | No | N/A |

---

## Troubleshooting

### Common Issues

| Issue | Symptom | Resolution |
|-------|---------|------------|
| **No leader elected** | `LEADER_NOT_AVAILABLE` errors | Check controller connectivity, verify quorum voters |
| **Metadata out of sync** | Brokers have stale topic info | Check broker fetch lag from controllers |
| **Controller OOM** | Controller crashes | Increase heap, check for partition explosion |
| **Slow elections** | Long failover time | Check network latency between controllers |

### Diagnostic Commands

```bash
# Check controller quorum status
kafka-metadata-quorum.sh --bootstrap-controller ctrl1:9093 \
  describe --status

# View current controller leader
kafka-metadata-quorum.sh --bootstrap-controller ctrl1:9093 \
  describe --status | rg -i leader

# Check metadata log lag
kafka-metadata-shell.sh --snapshot /var/kafka-logs/__cluster_metadata-0/*.log \
  log | tail -20

# Verify broker registration
kafka-broker-api-versions.sh --bootstrap-server broker1:9092
```

### Key Metrics

| Metric | Description | Alert Condition |
|--------|-------------|-----------------|
| `kafka.controller:type=KafkaController,name=ActiveControllerCount` | Active controllers | ≠ 1 |
| `kafka.controller:type=ControllerEventManager,name=EventQueueSize` | Pending controller events | > 1000 |
| `kafka.server:type=MetadataLoader,name=CurrentMetadataOffset` | Broker metadata offset | Lag > 1000 |
| `kafka.raft:type=RaftMetrics,name=CommitLatencyAvg` | Raft commit latency | > 100ms |

---

## Summary

| Aspect | Detail |
|--------|--------|
| **What** | Built-in consensus replacing ZooKeeper |
| **Protocol** | Raft (leader election, log replication) |
| **Storage** | `__cluster_metadata` topic |
| **Quorum** | 3 or 5 controllers recommended |
| **Failover** | 2-5 seconds typical |
| **Deployment** | Combined (small) or isolated (large) mode |

---

## Related Documentation

- [Cluster Management](../cluster-management/index.md) - Controller operations
- [Fault Tolerance](../fault-tolerance/index.md) - Failure handling
- [Brokers](../brokers/index.md) - Broker internals
- [Architecture Overview](../index.md) - System architecture
