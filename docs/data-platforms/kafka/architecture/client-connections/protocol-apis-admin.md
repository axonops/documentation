---
title: "Kafka Administrative Protocol APIs"
description: "Apache Kafka administrative protocol APIs. CreateTopics, DeleteTopics, CreatePartitions, ACLs, Configs, and cluster management specifications."
meta:
  - name: keywords
    content: "Kafka admin API, AdminClient, topic management, broker admin, cluster administration"
---

# Kafka Administrative Protocol APIs

This document specifies the Kafka protocol APIs used for cluster administration, including topic management, configuration, ACL management, and cluster operations.

---

## Administrative API Reference

### Topic Management

| API Key | Name | Purpose |
|:-------:|------|---------|
| 19 | CreateTopics | Create new topics |
| 20 | DeleteTopics | Delete existing topics |
| 21 | DeleteRecords | Delete records before offset |
| 37 | CreatePartitions | Add partitions to topics |

### Configuration Management

| API Key | Name | Purpose |
|:-------:|------|---------|
| 32 | DescribeConfigs | Retrieve configurations |
| 33 | AlterConfigs | Replace configurations (deprecated) |
| 44 | IncrementalAlterConfigs | Modify configurations incrementally |

### ACL Management

| API Key | Name | Purpose |
|:-------:|------|---------|
| 29 | DescribeAcls | List ACL entries |
| 30 | CreateAcls | Create ACL entries |
| 31 | DeleteAcls | Delete ACL entries |

### Cluster Operations

| API Key | Name | Purpose |
|:-------:|------|---------|
| 34 | AlterReplicaLogDirs | Move replicas between directories |
| 35 | DescribeLogDirs | Query log directory usage |
| 43 | ElectLeaders | Trigger leader election |
| 45 | AlterPartitionReassignments | Reassign partitions |
| 46 | ListPartitionReassignments | Query reassignment status |
| 60 | DescribeCluster | Describe cluster metadata |

### KRaft Voter Management

| API Key | Name | Purpose |
|:-------:|------|---------|
| 80 | AddRaftVoter | Add voter to KRaft quorum |
| 81 | RemoveRaftVoter | Remove voter from KRaft quorum |
| 82 | UpdateRaftVoter | Update KRaft voter endpoints |

---

## CreateTopics API (Key 19)

### Overview

The CreateTopics API creates new topics with specified configurations.

### Version History

| Version | Kafka | Key Changes |
|:-------:|-------|-------------|
| 0 | 0.10.1 | Initial version (removed in 4.0) |
| 1 | 0.10.2 | Error message (removed in 4.0) |
| 2 | 0.11.0 | Throttle time (4.0 baseline) |
| 3 | 1.0.0 | Response before quota throttling |
| 4 | 2.0.0 | KIP-464 optional partitions/replication |
| 5 | 2.4.0 | Flexible versions; response configs (KIP-525) |
| 6 | 2.7.0 | KIP-599 THROTTLING_QUOTA_EXCEEDED |
| 7 | 3.0.0 | KIP-516 topic ID |

### Request Schema

```
CreateTopicsRequest =>
    topics: [Topic]
    timeout_ms: INT32
    validate_only: BOOLEAN

Topic =>
    name: STRING
    num_partitions: INT32
    replication_factor: INT16
    assignments: [Assignment]
    configs: [Config]

Assignment =>
    partition_index: INT32
    broker_ids: [INT32]

Config =>
    name: STRING
    value: NULLABLE_STRING
```

| Field | Type | Description |
|-------|------|-------------|
| `name` | STRING | Topic name |
| `num_partitions` | INT32 | Number of partitions (-1 for default) |
| `replication_factor` | INT16 | Replication factor (-1 for default) |
| `assignments` | ARRAY | Manual replica assignments (optional) |
| `configs` | ARRAY | Topic-level configurations |
| `timeout_ms` | INT32 | Operation timeout |
| `validate_only` | BOOLEAN | Only validate, do not create |

### Response Schema

```
CreateTopicsResponse =>
    throttle_time_ms: INT32
    topics: [Topic]

Topic =>
    name: STRING
    topic_id: UUID
    error_code: INT16
    error_message: NULLABLE_STRING
    topic_config_error_code: INT16
    num_partitions: INT32
    replication_factor: INT16
    configs: [Config]

Config =>
    name: STRING
    value: NULLABLE_STRING
    read_only: BOOLEAN
    config_source: INT8
    is_sensitive: BOOLEAN
```

### Behavioral Contract

| Aspect | Guarantee |
|--------|-----------|
| **Atomicity** | Each topic creation is independent |
| **Validation** | Configs validated before creation |
| **Timeout** | TIMEOUT error does not mean failure |
| **Idempotence** | TOPIC_ALREADY_EXISTS if topic exists |

!!! warning "Timeout Behavior"
    A REQUEST_TIMED_OUT response does not indicate failure. The topic may still be created. Clients should query metadata to verify topic state.

### Error Handling

| Error Code | Retriable | Cause | Recovery |
|:----------:|:---------:|-------|----------|
| TOPIC_ALREADY_EXISTS | ❌ | Topic exists | Skip or delete first |
| INVALID_TOPIC | ❌ | Invalid topic name | Fix name |
| INVALID_REPLICATION_FACTOR | ❌ | RF > available brokers | Reduce RF |
| INVALID_PARTITIONS | ❌ | Invalid partition count | Fix count |
| TOPIC_AUTHORIZATION_FAILED | ❌ | No Create permission | Check ACLs |
| REQUEST_TIMED_OUT | ✅ | Operation timeout | Check metadata, retry |

---

## DeleteTopics API (Key 20)

### Overview

The DeleteTopics API deletes topics and all their data.

### Version History

| Version | Kafka | Key Changes |
|:-------:|-------|-------------|
| 0 | 0.10.1 | Initial version (removed in 4.0) |
| 1 | 0.10.2 | Throttle time (4.0 baseline) |
| 2 | 0.11.0 | Response before quota throttling |
| 3 | 1.2.0 | TOPIC_DELETION_DISABLED error |
| 4 | 2.4.0 | Flexible versions |
| 5 | 2.8.0 | Error message; THROTTLING_QUOTA_EXCEEDED |
| 6 | 3.0.0 | Topic ID support |

### Request Schema

```
DeleteTopicsRequest =>
    topics: [Topic]
    topic_names: [STRING]
    timeout_ms: INT32

Topic =>
    name: NULLABLE_STRING
    topic_id: UUID
```

| Field | Type | Description |
|-------|------|-------------|
| `topics` | ARRAY | Topics to delete (v6+; by name or ID) |
| `topic_names` | ARRAY | Topic names to delete (v0-5) |
| `timeout_ms` | INT32 | Operation timeout |

### Response Schema

```
DeleteTopicsResponse =>
    throttle_time_ms: INT32
    responses: [Response]

Response =>
    name: NULLABLE_STRING
    topic_id: UUID
    error_code: INT16
    error_message: NULLABLE_STRING
```

### Behavioral Contract

| Aspect | Guarantee |
|--------|-----------|
| **Irreversibility** | Deletion cannot be undone |
| **Asynchronous** | Deletion may complete after response |
| **Data loss** | All partition data permanently lost |
| **Metadata** | Topic removed from cluster metadata |

!!! danger "Irreversible Operation"
    Topic deletion permanently destroys all data in the topic. There is no recovery mechanism.

---

## CreatePartitions API (Key 37)

### Overview

The CreatePartitions API adds partitions to existing topics.

### Version History

| Version | Kafka | Key Changes |
|:-------:|-------|-------------|
| 0 | 1.0.0 | Initial version |
| 1 | 2.0.0 | Response improvements |
| 2 | 2.4.0 | Flexible versions |
| 3 | 2.8.0 | KIP-516 |

### Request Schema

```
CreatePartitionsRequest =>
    topics: [Topic]
    timeout_ms: INT32
    validate_only: BOOLEAN

Topic =>
    name: STRING
    count: INT32
    assignments: [Assignment]

Assignment =>
    broker_ids: [INT32]
```

| Field | Type | Description |
|-------|------|-------------|
| `count` | INT32 | New total partition count |
| `assignments` | ARRAY | Manual replica assignments for new partitions |

### Response Schema

```
CreatePartitionsResponse =>
    throttle_time_ms: INT32
    results: [Result]

Result =>
    name: STRING
    error_code: INT16
    error_message: NULLABLE_STRING
```

### Behavioral Contract

| Aspect | Guarantee |
|--------|-----------|
| **Increase only** | Can only increase partition count |
| **Key distribution** | Existing key distribution changes |
| **Data preservation** | Existing partition data preserved |

!!! warning "Key Distribution Impact"
    Adding partitions changes key-to-partition mapping. Keys previously routing to partition N may route to new partitions. This affects ordering guarantees for keyed messages.

---

## DescribeConfigs API (Key 32)

### Overview

The DescribeConfigs API retrieves configuration for resources (brokers, topics, etc.).

### Version History

| Version | Kafka | Key Changes |
|:-------:|-------|-------------|
| 0 | 0.11.0 | Initial version |
| 1 | 1.0.0 | Include synonyms |
| 2 | 2.0.0 | Response improvements |
| 3 | 2.1.0 | Include documentation |
| 4 | 2.4.0 | Flexible versions |

### Request Schema

```
DescribeConfigsRequest =>
    resources: [Resource]
    include_synonyms: BOOLEAN
    include_documentation: BOOLEAN

Resource =>
    resource_type: INT8
    resource_name: STRING
    configuration_keys: [STRING]
```

| Field | Type | Description |
|-------|------|-------------|
| `resource_type` | INT8 | Resource type (see below) |
| `resource_name` | STRING | Resource name (topic/broker ID) |
| `configuration_keys` | ARRAY | Keys to fetch (null for all) |

### Resource Types

| Value | Type | Description |
|:-----:|------|-------------|
| 0 | UNKNOWN | Unknown (invalid) |
| 2 | TOPIC | Topic configuration |
| 4 | BROKER | Broker configuration |
| 8 | BROKER_LOGGER | Broker logger level |
| 16 | CLIENT_METRICS | Client metrics |
| 32 | GROUP | Group configuration |

### Response Schema

```
DescribeConfigsResponse =>
    throttle_time_ms: INT32
    results: [Result]

Result =>
    error_code: INT16
    error_message: NULLABLE_STRING
    resource_type: INT8
    resource_name: STRING
    configs: [Config]

Config =>
    name: STRING
    value: NULLABLE_STRING
    read_only: BOOLEAN
    is_default: BOOLEAN
    config_source: INT8
    is_sensitive: BOOLEAN
    synonyms: [Synonym]
    config_type: INT8
    documentation: NULLABLE_STRING
```

### Config Sources

| Value | Source | Description |
|:-----:|--------|-------------|
| 0 | UNKNOWN | Unknown source |
| 1 | TOPIC_CONFIG | Dynamic topic config |
| 2 | DYNAMIC_BROKER_CONFIG | Dynamic broker config |
| 3 | DYNAMIC_DEFAULT_BROKER_CONFIG | Dynamic broker default |
| 4 | STATIC_BROKER_CONFIG | Static broker config |
| 5 | DEFAULT_CONFIG | Built-in default |
| 6 | DYNAMIC_BROKER_LOGGER_CONFIG | Dynamic broker logger config |
| 7 | CLIENT_METRICS_CONFIG | Dynamic client metrics config |
| 8 | GROUP_CONFIG | Dynamic group config |

---

## IncrementalAlterConfigs API (Key 44)

### Overview

The IncrementalAlterConfigs API modifies configurations incrementally without replacing all values.

### Version History

| Version | Kafka | Key Changes |
|:-------:|-------|-------------|
| 0 | 2.3.0 | Initial version |
| 1 | 2.4.0 | Flexible versions |

### Request Schema

```
IncrementalAlterConfigsRequest =>
    resources: [Resource]
    validate_only: BOOLEAN

Resource =>
    resource_type: INT8
    resource_name: STRING
    configs: [Config]

Config =>
    name: STRING
    config_operation: INT8
    value: NULLABLE_STRING
```

| Field | Type | Description |
|-------|------|-------------|
| `config_operation` | INT8 | Operation type |

### Config Operations

| Value | Operation | Description |
|:-----:|-----------|-------------|
| 0 | SET | Set config value |
| 1 | DELETE | Remove config override |
| 2 | APPEND | Append to list config |
| 3 | SUBTRACT | Remove from list config |

### Response Schema

```
IncrementalAlterConfigsResponse =>
    throttle_time_ms: INT32
    responses: [Response]

Response =>
    error_code: INT16
    error_message: NULLABLE_STRING
    resource_type: INT8
    resource_name: STRING
```

---

## DescribeAcls API (Key 29)

### Overview

The DescribeAcls API queries ACL entries matching specified filters.

### Version History

| Version | Kafka | Key Changes |
|:-------:|-------|-------------|
| 0 | 0.11.0 | Initial version |
| 1 | 2.0.0 | Throttle time |
| 2 | 2.4.0 | Flexible versions |
| 3 | 3.0.0 | KIP-516 |

### Request Schema

```
DescribeAclsRequest =>
    resource_type_filter: INT8
    resource_name_filter: NULLABLE_STRING
    pattern_type_filter: INT8
    principal_filter: NULLABLE_STRING
    host_filter: NULLABLE_STRING
    operation: INT8
    permission_type: INT8
```

| Field | Type | Description |
|-------|------|-------------|
| `resource_type_filter` | INT8 | Resource type (ANY for all) |
| `pattern_type_filter` | INT8 | Pattern type (ANY for all) |
| `operation` | INT8 | Operation (ANY for all) |
| `permission_type` | INT8 | ALLOW or DENY (ANY for all) |

### ACL Resource Types

| Value | Type |
|:-----:|------|
| 0 | UNKNOWN |
| 1 | ANY |
| 2 | TOPIC |
| 3 | GROUP |
| 4 | CLUSTER |
| 5 | TRANSACTIONAL_ID |
| 6 | DELEGATION_TOKEN |
| 7 | USER |

### ACL Operations

| Value | Operation |
|:-----:|-----------|
| 0 | UNKNOWN |
| 1 | ANY |
| 2 | ALL |
| 3 | READ |
| 4 | WRITE |
| 5 | CREATE |
| 6 | DELETE |
| 7 | ALTER |
| 8 | DESCRIBE |
| 9 | CLUSTER_ACTION |
| 10 | DESCRIBE_CONFIGS |
| 11 | ALTER_CONFIGS |
| 12 | IDEMPOTENT_WRITE |
| 13 | CREATE_TOKENS |
| 14 | DESCRIBE_TOKENS |

### ACL Pattern Types

| Value | Type | Description |
|:-----:|------|-------------|
| 0 | UNKNOWN | Unknown (invalid) |
| 1 | ANY | Match any pattern |
| 2 | MATCH | Matches resource name pattern |
| 3 | LITERAL | Exact resource name match |
| 4 | PREFIXED | Resource name prefix match |

### Response Schema

```
DescribeAclsResponse =>
    throttle_time_ms: INT32
    error_code: INT16
    error_message: NULLABLE_STRING
    resources: [Resource]

Resource =>
    resource_type: INT8
    resource_name: STRING
    pattern_type: INT8
    acls: [Acl]

Acl =>
    principal: STRING
    host: STRING
    operation: INT8
    permission_type: INT8
```

---

## CreateAcls API (Key 30)

### Overview

The CreateAcls API creates new ACL entries.

### Version History

| Version | Kafka | Key Changes |
|:-------:|-------|-------------|
| 0 | 0.11.0 | Initial version |
| 1 | 2.0.0 | Response improvements |
| 2 | 2.4.0 | Flexible versions |
| 3 | 3.0.0 | KIP-516 |

### Request Schema

```
CreateAclsRequest =>
    creations: [Creation]

Creation =>
    resource_type: INT8
    resource_name: STRING
    resource_pattern_type: INT8
    principal: STRING
    host: STRING
    operation: INT8
    permission_type: INT8
```

| Field | Type | Description |
|-------|------|-------------|
| `principal` | STRING | Principal (e.g., "User:alice") |
| `host` | STRING | Host ("*" for any) |
| `permission_type` | INT8 | 2=DENY, 3=ALLOW |

### Response Schema

```
CreateAclsResponse =>
    throttle_time_ms: INT32
    results: [Result]

Result =>
    error_code: INT16
    error_message: NULLABLE_STRING
```

---

## DeleteAcls API (Key 31)

### Overview

The DeleteAcls API deletes ACL entries matching filters.

### Version History

| Version | Kafka | Key Changes |
|:-------:|-------|-------------|
| 0 | 0.11.0 | Initial version |
| 1 | 2.0.0 | Response improvements |
| 2 | 2.4.0 | Flexible versions |
| 3 | 3.0.0 | KIP-516 |

### Request Schema

```
DeleteAclsRequest =>
    filters: [Filter]

Filter =>
    resource_type_filter: INT8
    resource_name_filter: NULLABLE_STRING
    pattern_type_filter: INT8
    principal_filter: NULLABLE_STRING
    host_filter: NULLABLE_STRING
    operation: INT8
    permission_type: INT8
```

### Response Schema

```
DeleteAclsResponse =>
    throttle_time_ms: INT32
    filter_results: [FilterResult]

FilterResult =>
    error_code: INT16
    error_message: NULLABLE_STRING
    matching_acls: [MatchingAcl]

MatchingAcl =>
    error_code: INT16
    error_message: NULLABLE_STRING
    resource_type: INT8
    resource_name: STRING
    pattern_type: INT8
    principal: STRING
    host: STRING
    operation: INT8
    permission_type: INT8
```

---

## ElectLeaders API (Key 43)

### Overview

The ElectLeaders API triggers leader election for partitions.

### Version History

| Version | Kafka | Key Changes |
|:-------:|-------|-------------|
| 0 | 2.2.0 | Initial version (preferred leaders) |
| 1 | 2.4.0 | KIP-460 election types |
| 2 | 2.4.0 | Flexible versions |

### Request Schema

```
ElectLeadersRequest =>
    election_type: INT8
    topic_partitions: [TopicPartition]
    timeout_ms: INT32

TopicPartition =>
    topic: STRING
    partitions: [INT32]
```

| Field | Type | Description |
|-------|------|-------------|
| `election_type` | INT8 | 0=PREFERRED, 1=UNCLEAN |
| `topic_partitions` | ARRAY | Partitions (null for all) |

### Election Types

| Value | Type | Description |
|:-----:|------|-------------|
| 0 | PREFERRED | Elect preferred leader (must be in ISR) |
| 1 | UNCLEAN | Elect any available replica (data loss risk) |

!!! danger "Unclean Leader Election"
    Unclean leader election (type=1) may result in data loss if the elected replica is behind the previous leader.

### Response Schema

```
ElectLeadersResponse =>
    throttle_time_ms: INT32
    error_code: INT16
    replica_election_results: [ReplicaElectionResult]

ReplicaElectionResult =>
    topic: STRING
    partition_result: [PartitionResult]

PartitionResult =>
    partition_id: INT32
    error_code: INT16
    error_message: NULLABLE_STRING
```

---

## AlterPartitionReassignments API (Key 45)

### Overview

The AlterPartitionReassignments API reassigns partition replicas to different brokers.

### Version History

| Version | Kafka | Key Changes |
|:-------:|-------|-------------|
| 0 | 2.4.0 | Initial version |

### Request Schema

```
AlterPartitionReassignmentsRequest =>
    timeout_ms: INT32
    topics: [Topic]

Topic =>
    name: STRING
    partitions: [Partition]

Partition =>
    partition_index: INT32
    replicas: [INT32]
```

| Field | Type | Description |
|-------|------|-------------|
| `replicas` | ARRAY | New replica list (null to cancel) |

### Response Schema

```
AlterPartitionReassignmentsResponse =>
    throttle_time_ms: INT32
    error_code: INT16
    error_message: NULLABLE_STRING
    responses: [Response]

Response =>
    name: STRING
    partitions: [Partition]

Partition =>
    partition_index: INT32
    error_code: INT16
    error_message: NULLABLE_STRING
```

### Behavioral Contract

| Aspect | Guarantee |
|--------|-----------|
| **Progress** | Data copied before old replicas removed |
| **Availability** | Partition remains available during reassignment |
| **Cancellation** | Set replicas to null to cancel |

---

## DescribeLogDirs API (Key 35)

### Overview

The DescribeLogDirs API queries log directory usage on brokers.

### Version History

| Version | Kafka | Key Changes |
|:-------:|-------|-------------|
| 0 | 0.11.0 | Initial version (removed in 4.0) |
| 1 | 2.0.0 | Throttle time (4.0 baseline) |
| 2 | 2.4.0 | Flexible versions |
| 3 | 2.7.0 | Top-level error code |
| 4 | 3.5.0 | Total/usable bytes (KIP-827) |

### Request Schema

```
DescribeLogDirsRequest =>
    topics: [Topic]

Topic =>
    topic: STRING
    partitions: [INT32]
```

| Field | Type | Description |
|-------|------|-------------|
| `topics` | ARRAY | Topics to query (null for all) |

### Response Schema

```
DescribeLogDirsResponse =>
    throttle_time_ms: INT32
    error_code: INT16
    results: [Result]

Result =>
    error_code: INT16
    log_dir: STRING
    topics: [Topic]
    total_bytes: INT64
    usable_bytes: INT64

Topic =>
    name: STRING
    partitions: [Partition]

Partition =>
    partition_index: INT32
    partition_size: INT64
    offset_lag: INT64
    is_future_key: BOOLEAN
```

| Field | Type | Description |
|-------|------|-------------|
| `log_dir` | STRING | Log directory path |
| `total_bytes` | INT64 | Total size of the log volume (excludes remote storage) |
| `usable_bytes` | INT64 | Usable size of the log volume (excludes remote storage) |
| `partition_size` | INT64 | Partition data size |
| `offset_lag` | INT64 | Replication lag (future replicas) |

---

## DescribeCluster API (Key 60)

### Overview

The DescribeCluster API retrieves cluster metadata including controller and broker information.

### Version History

| Version | Kafka | Key Changes |
|:-------:|-------|-------------|
| 0 | 3.0.0 | Initial version |
| 1 | 3.4.0 | EndpointType (KIP-919) |
| 2 | 3.9.0 | IncludeFencedBrokers (KIP-1073) |

### Request Schema

```
DescribeClusterRequest =>
    include_cluster_authorized_operations: BOOLEAN
    endpoint_type: INT8
    include_fenced_brokers: BOOLEAN
```

### Response Schema

```
DescribeClusterResponse =>
    throttle_time_ms: INT32
    error_code: INT16
    error_message: NULLABLE_STRING
    endpoint_type: INT8
    cluster_id: STRING
    controller_id: INT32
    brokers: [Broker]
    cluster_authorized_operations: INT32

Broker =>
    broker_id: INT32
    host: STRING
    port: INT32
    rack: NULLABLE_STRING
    is_fenced: BOOLEAN
```

---

## Administrative Best Practices

### Topic Management

| Practice | Rationale |
|----------|-----------|
| Use validate_only before creation | Catch errors before commit |
| Verify topic state after timeout | Timeout does not mean failure |
| Plan partition count carefully | Cannot decrease partitions |
| Use rack-aware assignments | Improve fault tolerance |

### ACL Management

| Practice | Rationale |
|----------|-----------|
| Use PREFIXED patterns for hierarchy | Simplify permission management |
| Audit ACLs regularly | Detect permission drift |
| Test ACL changes in non-prod | Prevent access issues |
| Document ACL policies | Enable consistent management |

### Configuration Management

| Practice | Rationale |
|----------|-----------|
| Use IncrementalAlterConfigs | Avoid replacing all configs |
| Track config changes | Enable rollback |
| Test config changes | Prevent cluster issues |
| Use describe before alter | Understand current state |

---

## Related Documentation

- [Protocol Core APIs](protocol-apis-core.md) - Core APIs
- [Protocol Consumer APIs](protocol-apis-consumer.md) - Consumer group APIs
- [Protocol Transaction APIs](protocol-apis-transaction.md) - Transaction APIs
- [Protocol Errors](protocol-errors.md) - Error code reference
