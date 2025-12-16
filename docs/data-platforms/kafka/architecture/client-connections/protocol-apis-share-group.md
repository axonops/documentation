---
title: "Kafka Share Group Protocol APIs"
description: "Apache Kafka Share Group protocol APIs. ShareGroupHeartbeat, ShareFetch, ShareAcknowledge, and state management specifications."
meta:
  - name: keywords
    content: "Kafka share groups, KIP-932, shared consumption, queue semantics"
---

# Kafka Share Group Protocol APIs

This document specifies the Kafka protocol APIs used for Share Groups, a new consumer model introduced in KIP-932 (Kafka 4.0+). Share Groups provide queue-like semantics where messages are distributed among consumers without partition assignment.

---

## Share Group Overview

Share Groups differ fundamentally from traditional Consumer Groups:

| Aspect | Consumer Groups | Share Groups |
|--------|-----------------|--------------|
| **Partition assignment** | Each partition assigned to one consumer | No partition assignment |
| **Message delivery** | All messages in partition to assigned consumer | Messages distributed across consumers |
| **Ordering** | Per-partition ordering guaranteed | No ordering guarantee |
| **Acknowledgment** | Offset-based | Per-record acknowledgment |
| **Use case** | Stream processing | Work queue, task distribution |

---

## Share Group API Reference

### Group Coordination

| API Key | Name | Purpose |
|:-------:|------|---------|
| 76 | ShareGroupHeartbeat | Maintain membership and get assignments |
| 77 | ShareGroupDescribe | Describe share group state |

### Data Operations

| API Key | Name | Purpose |
|:-------:|------|---------|
| 78 | ShareFetch | Fetch records from share group |
| 79 | ShareAcknowledge | Acknowledge record processing |

### State Management

| API Key | Name | Purpose |
|:-------:|------|---------|
| 83 | InitializeShareGroupState | Initialize share partition state |
| 84 | ReadShareGroupState | Read share partition state |
| 85 | WriteShareGroupState | Write share partition state |
| 86 | DeleteShareGroupState | Delete share partition state |
| 87 | ReadShareGroupStateSummary | Read share partition state summary |

### Offset Management

| API Key | Name | Purpose |
|:-------:|------|---------|
| 90 | DescribeShareGroupOffsets | Describe share group offsets |
| 91 | AlterShareGroupOffsets | Alter share group offsets |
| 92 | DeleteShareGroupOffsets | Delete share group offsets |

---

## ShareGroupHeartbeat API (Key 76)

### Overview

The ShareGroupHeartbeat API maintains share group membership. Unlike consumer groups which use separate JoinGroup/SyncGroup/Heartbeat APIs, share groups use a single heartbeat API for all coordination.

### Request Schema

```
ShareGroupHeartbeatRequest =>
    group_id: STRING
    member_id: STRING
    member_epoch: INT32
    instance_id: NULLABLE_STRING
    rack_id: NULLABLE_STRING
    rebalance_timeout_ms: INT32
    subscribed_topic_names: [STRING]
    server_assignor: NULLABLE_STRING
    topic_partitions: [TopicPartition]

TopicPartition =>
    topic_id: UUID
    partitions: [INT32]
```

| Field | Type | Description |
|-------|------|-------------|
| `group_id` | STRING | Share group identifier |
| `member_id` | STRING | Member ID (empty on first join) |
| `member_epoch` | INT32 | Member epoch for fencing |
| `subscribed_topic_names` | ARRAY | Topics to subscribe to |
| `topic_partitions` | ARRAY | Current partition assignments |

### Response Schema

```
ShareGroupHeartbeatResponse =>
    throttle_time_ms: INT32
    error_code: INT16
    error_message: NULLABLE_STRING
    member_id: NULLABLE_STRING
    member_epoch: INT32
    heartbeat_interval_ms: INT32
    assignment: Assignment

Assignment =>
    topic_partitions: [TopicPartition]

TopicPartition =>
    topic_id: UUID
    partitions: [INT32]
```

### Behavioral Contract

| Aspect | Guarantee |
|--------|-----------|
| **Epoch fencing** | Stale members rejected via epoch |
| **Assignment** | Server-side assignment, no leader election |
| **Heartbeat interval** | Server specifies next heartbeat timing |

---

## ShareGroupDescribe API (Key 77)

### Overview

The ShareGroupDescribe API retrieves detailed information about share groups.

### Request Schema

```
ShareGroupDescribeRequest =>
    group_ids: [STRING]
    include_authorized_operations: BOOLEAN
```

### Response Schema

```
ShareGroupDescribeResponse =>
    throttle_time_ms: INT32
    groups: [Group]

Group =>
    error_code: INT16
    error_message: NULLABLE_STRING
    group_id: STRING
    group_state: STRING
    group_epoch: INT32
    assignment_epoch: INT32
    assignor_name: STRING
    members: [Member]
    authorized_operations: INT32

Member =>
    member_id: STRING
    rack_id: NULLABLE_STRING
    member_epoch: INT32
    client_id: STRING
    client_host: STRING
    subscribed_topic_names: [STRING]
    assignment: Assignment
```

---

## ShareFetch API (Key 78)

### Overview

The ShareFetch API retrieves records from a share group. Unlike regular Fetch, records are distributed across consumers and require acknowledgment.

### Request Schema

```
ShareFetchRequest =>
    group_id: NULLABLE_STRING
    member_id: NULLABLE_STRING
    share_session_epoch: INT32
    max_wait_ms: INT32
    min_bytes: INT32
    max_bytes: INT32
    topics: [Topic]
    forgotten_topics_data: [ForgottenTopic]

Topic =>
    topic_id: UUID
    partitions: [Partition]

Partition =>
    partition_index: INT32
    partition_max_bytes: INT32
    acknowledgement_batches: [AcknowledgementBatch]

AcknowledgementBatch =>
    first_offset: INT64
    last_offset: INT64
    acknowledge_types: [INT8]
```

| Field | Type | Description |
|-------|------|-------------|
| `group_id` | STRING | Share group identifier |
| `share_session_epoch` | INT32 | Session epoch for incremental fetch |
| `acknowledgement_batches` | ARRAY | Inline acknowledgments (optional) |

### Response Schema

```
ShareFetchResponse =>
    throttle_time_ms: INT32
    error_code: INT16
    error_message: NULLABLE_STRING
    responses: [Response]
    node_endpoints: [NodeEndpoint]

Response =>
    topic_id: UUID
    partitions: [Partition]

Partition =>
    partition_index: INT32
    error_code: INT16
    error_message: NULLABLE_STRING
    current_leader: LeaderIdAndEpoch
    records: RECORDS
    acquired_records: [AcquiredRecords]

AcquiredRecords =>
    first_offset: INT64
    last_offset: INT64
    delivery_count: INT16
```

| Field | Type | Description |
|-------|------|-------------|
| `acquired_records` | ARRAY | Records acquired by this consumer |
| `delivery_count` | INT16 | Number of delivery attempts |

### Behavioral Contract

| Aspect | Guarantee |
|--------|-----------|
| **Record locking** | Fetched records locked to consumer |
| **Delivery tracking** | Delivery count tracks retries |
| **Timeout** | Unacknowledged records released after timeout |

---

## ShareAcknowledge API (Key 79)

### Overview

The ShareAcknowledge API acknowledges processing of records fetched via ShareFetch.

### Request Schema

```
ShareAcknowledgeRequest =>
    group_id: NULLABLE_STRING
    member_id: NULLABLE_STRING
    share_session_epoch: INT32
    topics: [Topic]

Topic =>
    topic_id: UUID
    partitions: [Partition]

Partition =>
    partition_index: INT32
    acknowledgement_batches: [AcknowledgementBatch]

AcknowledgementBatch =>
    first_offset: INT64
    last_offset: INT64
    acknowledge_types: [INT8]
```

### Acknowledge Types

| Value | Type | Description |
|:-----:|------|-------------|
| 1 | ACCEPT | Successfully processed |
| 2 | RELEASE | Release for redelivery |
| 3 | REJECT | Reject permanently (DLQ) |

### Response Schema

```
ShareAcknowledgeResponse =>
    throttle_time_ms: INT32
    error_code: INT16
    error_message: NULLABLE_STRING
    responses: [Response]
    node_endpoints: [NodeEndpoint]

Response =>
    topic_id: UUID
    partitions: [Partition]

Partition =>
    partition_index: INT32
    error_code: INT16
    error_message: NULLABLE_STRING
```

### Behavioral Contract

| Aspect | Guarantee |
|--------|-----------|
| **ACCEPT** | Record marked complete, not redelivered |
| **RELEASE** | Record released for another consumer |
| **REJECT** | Record sent to dead letter queue (if configured) |

---

## State Management APIs

### InitializeShareGroupState API (Key 83)

Initializes the share partition state when a share group first accesses a partition.

```
InitializeShareGroupStateRequest =>
    group_id: STRING
    topics: [Topic]

Topic =>
    topic_id: UUID
    partitions: [Partition]

Partition =>
    partition: INT32
    state_epoch: INT32
    start_offset: INT64
```

### ReadShareGroupState API (Key 84)

Reads the current state of share partitions.

```
ReadShareGroupStateRequest =>
    group_id: STRING
    topics: [Topic]

Topic =>
    topic_id: UUID
    partitions: [INT32]
```

### WriteShareGroupState API (Key 85)

Writes updated share partition state.

```
WriteShareGroupStateRequest =>
    group_id: STRING
    topics: [Topic]

Topic =>
    topic_id: UUID
    partitions: [Partition]

Partition =>
    partition: INT32
    state_epoch: INT32
    leader_epoch: INT32
    start_offset: INT64
    state_batches: [StateBatch]
```

### DeleteShareGroupState API (Key 86)

Deletes share partition state when cleaning up a share group.

```
DeleteShareGroupStateRequest =>
    group_id: STRING
    topics: [Topic]

Topic =>
    topic_id: UUID
    partitions: [INT32]
```

### ReadShareGroupStateSummary API (Key 87)

Reads a summary of share partition state for monitoring.

```
ReadShareGroupStateSummaryRequest =>
    group_id: STRING
    topics: [Topic]

Topic =>
    topic_id: UUID
    partitions: [INT32]
```

---

## Offset Management APIs

### DescribeShareGroupOffsets API (Key 90)

Describes the current offsets for a share group.

```
DescribeShareGroupOffsetsRequest =>
    group_id: STRING
    topics: [Topic]

Topic =>
    topic_name: STRING
    partitions: [INT32]
```

### AlterShareGroupOffsets API (Key 91)

Alters the offsets for a share group (administrative operation).

```
AlterShareGroupOffsetsRequest =>
    group_id: STRING
    topics: [Topic]

Topic =>
    topic_name: STRING
    partitions: [Partition]

Partition =>
    partition_index: INT32
    start_offset: INT64
```

### DeleteShareGroupOffsets API (Key 92)

Deletes offset information for a share group.

```
DeleteShareGroupOffsetsRequest =>
    group_id: STRING
    topics: [Topic]

Topic =>
    topic_name: STRING
    partitions: [INT32]
```

---

## Version Compatibility

| Feature | Minimum Kafka Version |
|---------|----------------------|
| Share Groups | 4.0.0 |
| All Share Group APIs | 4.0.0 |

!!! note "Kafka 4.0+ Feature"
    Share Groups are a new feature in Kafka 4.0. These APIs are not available in earlier versions.

---

## Related Documentation

- [Protocol Consumer APIs](protocol-apis-consumer.md) - Traditional consumer group APIs
- [Protocol Core APIs](protocol-apis-core.md) - Core Produce/Fetch APIs
- [Protocol Errors](protocol-errors.md) - Error code reference
