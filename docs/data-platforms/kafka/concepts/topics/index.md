---
title: "Kafka Topics"
description: "Apache Kafka topics - partitions, replication, ordering guarantees, retention policies, and behavioral contracts."
meta:
  - name: keywords
    content: "Kafka topics, topic configuration, partitions, replication factor, topic management"
---

# Kafka Topics

Topics are the fundamental unit of organization in Kafka. The topic architecture directly addresses the core problems Kafka was designed to solve: **horizontal scalability** through partitioning and **high availability** through replication.

---

## Design Rationale

Traditional message queues impose fundamental constraints: a single queue creates a throughput ceiling, and broker failure causes data loss or unavailability. Kafka's topic architecture eliminates both limitations.

| Constraint | Traditional Queue | Kafka Topic |
|------------|-------------------|-------------|
| Throughput | Single broker bottleneck | Partitions distribute across brokers |
| Availability | Single point of failure | Replicas on multiple brokers |
| Scaling | Vertical only | Horizontal via partition count |
| Retention | Deleted after consumption | Configurable time/size-based retention |

---

## Partitions

Partitions are the unit of parallelism in Kafka. A single log cannot scale beyond one broker's capacity—partitioning solves this by splitting a topic into independent segments that can be distributed across the cluster.

The partition count is specified when creating a topic and determines the topic's maximum parallelism. Each partition is an ordered, append-only sequence of records stored on a single broker. By distributing partitions across brokers:

- **Write throughput scales horizontally**: Producers write to different partitions in parallel
- **Read throughput scales horizontally**: Consumers in a group read from different partitions in parallel
- **Storage scales horizontally**: Each broker stores only a subset of the topic's data
- **Failure isolation improves**: A broker failure affects only its partitions, not the entire topic

### Behavioral Guarantees

| Guarantee | Scope | Behavior |
|-----------|-------|----------|
| **Ordering** | Within partition | Records must be read in the order written |
| **Ordering** | Across partitions | Undefined—no ordering relationship exists between partitions |
| **Immutability** | Record | Records must not be modified after being written |
| **Offset assignment** | Partition | Offsets must be sequential integers starting from 0 |
| **Offset uniqueness** | Partition | Each offset must be assigned to exactly one record |

!!! warning "Undefined Behavior"
    The relative ordering of records across different partitions is undefined and must not be relied upon. A consumer reading from multiple partitions may observe records in any interleaving. Applications requiring total ordering must use a single partition.

### Partition-Key Contract

When a record key is provided, the default partitioner guarantees:

```
partition = murmur2(keyBytes) & 0x7FFFFFFF % numPartitions
```

| Condition | Guarantee |
|-----------|-----------|
| Same key, same partition count | Records must be assigned to the same partition |
| Same key, different partition count | Partition assignment is undefined |
| Null key (Kafka 2.4+) | Sticky partitioning—records batch to one partition until `batch.size` or `linger.ms` triggers send |
| Null key (pre-2.4) | Round-robin distribution across available partitions |

!!! danger "Partition Count Changes"
    Increasing partition count changes the key-to-partition mapping. Records with the same key may be assigned to different partitions before and after the change. Applications depending on key-based ordering must either:

    - Never increase partition count
    - Drain the topic before increasing partitions
    - Accept ordering discontinuity during transition

### Partition Count Selection

The partition count must be chosen at topic creation. It may be increased but must not be decreased without recreating the topic.

| Factor | Guidance |
|--------|----------|
| Consumer parallelism | Partition count should be ≥ expected consumer count |
| Throughput | Each partition adds ~10 MB/s write capacity (varies by hardware) |
| Ordering requirements | Fewer partitions = broader ordering scope |
| Broker memory | Each partition consumes ~1-2 MB of broker heap |
| Recovery time | More partitions increases leader election and rebalance time |

---

## Replication

Each partition may be replicated across multiple brokers. Replication provides fault tolerance—the cluster continues operating when brokers fail.

### Replication Roles

| Role | Behavior |
|------|----------|
| **Leader** | Must handle all produce and consume requests for the partition |
| **Follower** | Must replicate records from leader; may not serve client requests (prior to Kafka 2.4) |
| **ISR member** | Follower that has fully caught up with the leader within `replica.lag.time.max.ms` |

Changed in Kafka 2.4 (KIP-392): Followers may serve read requests when `replica.selector.class` is configured.

### Replication Factor Constraints

| Constraint | Behavior |
|------------|----------|
| Minimum | Replication factor must be ≥ 1 |
| Maximum | Replication factor must be ≤ broker count |
| Modification | Replication factor may be changed via partition reassignment |

### Durability Guarantees

Durability depends on the producer's `acks` setting and the topic's `min.insync.replicas`:

| `acks` | `min.insync.replicas` | Guarantee |
|:------:|:---------------------:|-----------|
| `0` | Any | No durability—record may be lost before any broker persists it |
| `1` | Any | Leader must persist before acknowledging; data lost if leader fails before replication |
| `all` | 1 | Leader must persist; equivalent to `acks=1` |
| `all` | 2 | At least 2 replicas (including leader) must persist before acknowledging |
| `all` | N | At least N replicas must persist; produces fail if ISR < N |

!!! warning "ISR Shrinkage"
    When ISR size falls below `min.insync.replicas`, producers with `acks=all` receive `NotEnoughReplicasException`. The topic remains readable but writes are blocked until ISR recovers.

### Fault Tolerance

| Replication Factor | Tolerated Failures | Production Suitability |
|:------------------:|:------------------:|------------------------|
| 1 | 0 | Development only—must not be used in production |
| 2 | 1 | Minimal production; single failure causes unavailability during leader election |
| 3 | 2 | Standard production; recommended minimum |
| 5 | 4 | Critical data requiring extended failure tolerance |

---

## Retention

Kafka retains records based on time, size, or key-based compaction. Retention is configured per-topic and enforced per-partition.

### Retention Policies

| Policy | `cleanup.policy` | Behavior |
|--------|------------------|----------|
| **Delete** | `delete` | Segments older than `retention.ms` or exceeding `retention.bytes` are deleted |
| **Compact** | `compact` | Only the latest record per key is retained; older duplicates are removed |
| **Both** | `delete,compact` | Compaction runs first; then time/size-based deletion applies |

### Delete Policy Guarantees

| Configuration | Default | Guarantee |
|---------------|:-------:|-----------|
| `retention.ms` | 604800000 (7d) | Records older than this value may be deleted |
| `retention.bytes` | -1 (unlimited) | Per-partition; oldest segments deleted when exceeded |
| `segment.ms` | 604800000 (7d) | Active segment rolls after this interval |
| `segment.bytes` | 1073741824 (1GB) | Active segment rolls when size exceeded |

!!! note "Retention Timing"
    Retention applies to closed segments only. The active segment is not eligible for deletion regardless of age or size until it rolls.

### Log Compaction Guarantees

For topics with `cleanup.policy=compact`:

| Guarantee | Behavior |
|-----------|----------|
| **Latest value** | The most recent record for each key must be retained |
| **Ordering** | Record order within a key must be preserved |
| **Tombstone retention** | Tombstones (null values) must be retained for at least `delete.retention.ms` |
| **Head of log** | Records in the active segment are not eligible for compaction |

!!! warning "Compaction Timing"
    Compaction is not immediate. Records may exist in duplicate until the log cleaner processes the segment. Applications must not assume instantaneous compaction.

| Configuration | Default | Purpose |
|---------------|:-------:|---------|
| `min.cleanable.dirty.ratio` | 0.5 | Minimum dirty/total ratio before compaction eligible |
| `min.compaction.lag.ms` | 0 | Minimum time before record eligible for compaction |
| `max.compaction.lag.ms` | ∞ | Maximum time before compaction is forced |
| `delete.retention.ms` | 86400000 (1d) | Tombstone retention period |

---

## Topic Naming

Topic names must conform to the following constraints:

| Constraint | Rule |
|------------|------|
| Length | Must be 1-249 characters |
| Characters | Must contain only `[a-zA-Z0-9._-]` |
| Reserved prefixes | Names starting with `__` are reserved for internal topics |
| Uniqueness | Must be unique within the cluster |

!!! danger "Period and Underscore Collision"
    Kafka uses `.` and `_` interchangeably in some metric names. Topics `my.topic` and `my_topic` may collide in metrics. A cluster should use one convention consistently.

---

## Internal Topics

Kafka creates and manages internal topics for cluster operations. These topics must not be modified directly.

| Topic | Purpose | Created By |
|-------|---------|------------|
| `__consumer_offsets` | Consumer group offset storage | Kafka (automatic) |
| `__transaction_state` | Transaction coordinator state | Kafka (automatic) |
| `_schemas` | Schema storage | Schema Registry |
| `connect-offsets` | Connector offset tracking | Kafka Connect |
| `connect-configs` | Connector configurations | Kafka Connect |
| `connect-status` | Connector and task status | Kafka Connect |

---

## Failure Semantics

### Leader Failure

When a partition leader fails:

1. Controller detects failure via ZooKeeper session timeout (ZK mode) or heartbeat timeout (KRaft mode)
2. Controller selects new leader from ISR
3. New leader must have all committed records
4. Producers receive `NotLeaderOrFollowerException` and must refresh metadata
5. In-flight requests with `acks=all` may timeout; clients should retry

| Scenario | Outcome |
|----------|---------|
| ISR contains eligible replicas | New leader elected; brief unavailability during election |
| ISR empty, `unclean.leader.election.enable=false` | Partition unavailable until replica recovers |
| ISR empty, `unclean.leader.election.enable=true` | Data loss possible; out-of-sync replica becomes leader |

!!! danger "Unclean Leader Election"
    Setting `unclean.leader.election.enable=true` allows data loss. An out-of-sync replica may become leader, discarding records not yet replicated. This setting should remain `false` for production topics.

### Broker Failure

| Failure Mode | Impact |
|--------------|--------|
| Single broker, RF ≥ 2 | Affected partitions elect new leaders; cluster remains available |
| Multiple brokers, failures < RF | Cluster remains available if each partition has ≥ 1 ISR member |
| Failures ≥ RF for any partition | Affected partitions become unavailable |

---

## Version Compatibility

| Feature | Minimum Version | Notes |
|---------|:---------------:|-------|
| Topic creation via Admin API | 0.10.1.0 | `kafka-topics.sh` available earlier |
| Log compaction | 0.8.1 | |
| Follower fetching (KIP-392) | 2.4.0 | Requires `replica.selector.class` configuration |
| Tiered storage (KIP-405) | 3.6.0 | Early access; production readiness varies |
| KRaft mode (no ZooKeeper) | 3.3.0 | Production-ready in 3.3+; recommended in 3.6+ |

---

## Topic Configuration Reference

### Core Settings

| Configuration | Default | Description |
|---------------|:-------:|-------------|
| `partitions` | 1 | Number of partitions |
| `replication.factor` | - | Number of replicas (broker default: `default.replication.factor`) |
| `min.insync.replicas` | 1 | Minimum ISR for `acks=all` produces |

### Retention Settings

| Configuration | Default | Description |
|---------------|:-------:|-------------|
| `retention.ms` | 604800000 | Time-based retention (ms) |
| `retention.bytes` | -1 | Size-based retention per partition (-1 = unlimited) |
| `cleanup.policy` | delete | `delete`, `compact`, or `delete,compact` |

### Segment Settings

| Configuration | Default | Description |
|---------------|:-------:|-------------|
| `segment.bytes` | 1073741824 | Segment file size |
| `segment.ms` | 604800000 | Time before rolling segment |
| `segment.index.bytes` | 10485760 | Index file size |

### Compaction Settings

| Configuration | Default | Description |
|---------------|:-------:|-------------|
| `min.cleanable.dirty.ratio` | 0.5 | Dirty ratio threshold for compaction |
| `min.compaction.lag.ms` | 0 | Minimum age before compaction |
| `max.compaction.lag.ms` | - | Maximum age before forced compaction |
| `delete.retention.ms` | 86400000 | Tombstone retention |

---

## Related Documentation

- [Concepts Overview](../index.md) - Kafka fundamentals
- [Producers](../../producers/index.md) - Writing to topics
- [Consumers](../../consumers/index.md) - Reading from topics
- [Replication](../../architecture/replication/index.md) - Replication architecture
- [Operations](../../operations/index.md) - Topic operations
