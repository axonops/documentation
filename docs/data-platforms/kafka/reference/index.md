---
title: "Kafka Reference"
description: "Apache Kafka reference documentation. Configuration reference, protocol specification, and API documentation."
meta:
  - name: keywords
    content: "Kafka reference, Kafka configuration, Kafka protocol, Kafka API"
search:
  boost: 3
---

# Kafka Reference

Quick reference documentation for Apache Kafka.

---

## Configuration Quick Reference

### Broker (server.properties)

| Configuration | Default | Description |
|---------------|---------|-------------|
| `broker.id` | -1 | Unique broker identifier |
| `log.dirs` | /tmp/kafka-logs | Log directory paths |
| `num.partitions` | 1 | Default partition count |
| `default.replication.factor` | 1 | Default replication factor |
| `min.insync.replicas` | 1 | Minimum ISR for writes |
| `log.retention.hours` | 168 | Log retention time |
| `log.retention.bytes` | -1 | Log retention size |
| `log.segment.bytes` | 1073741824 | Segment file size |
| `num.network.threads` | 3 | Network I/O threads |
| `num.io.threads` | 8 | Disk I/O threads |

### Producer

| Configuration | Default | Description |
|---------------|---------|-------------|
| `acks` | all | Acknowledgment level |
| `retries` | MAX_INT | Retry attempts |
| `batch.size` | 16384 | Batch size bytes |
| `linger.ms` | 0 | Batching delay |
| `buffer.memory` | 33554432 | Total buffer memory |
| `compression.type` | none | Compression algorithm |
| `max.in.flight.requests.per.connection` | 5 | In-flight requests |
| `enable.idempotence` | true | Idempotent producer |

### Consumer

| Configuration | Default | Description |
|---------------|---------|-------------|
| `group.id` | null | Consumer group ID |
| `auto.offset.reset` | latest | Offset reset policy |
| `enable.auto.commit` | true | Auto commit offsets |
| `auto.commit.interval.ms` | 5000 | Auto commit interval |
| `fetch.min.bytes` | 1 | Minimum fetch bytes |
| `fetch.max.wait.ms` | 500 | Maximum fetch wait |
| `max.poll.records` | 500 | Records per poll |
| `session.timeout.ms` | 45000 | Session timeout |
| `heartbeat.interval.ms` | 3000 | Heartbeat interval |

---

## CLI Commands

### kafka-topics.sh

```bash
# List topics
kafka-topics.sh --bootstrap-server kafka:9092 --list

# Create topic
kafka-topics.sh --bootstrap-server kafka:9092 \
  --create --topic my-topic --partitions 12 --replication-factor 3

# Describe topic
kafka-topics.sh --bootstrap-server kafka:9092 \
  --describe --topic my-topic

# Delete topic
kafka-topics.sh --bootstrap-server kafka:9092 \
  --delete --topic my-topic

# Alter partitions
kafka-topics.sh --bootstrap-server kafka:9092 \
  --alter --topic my-topic --partitions 24
```

### kafka-consumer-groups.sh

```bash
# List groups
kafka-consumer-groups.sh --bootstrap-server kafka:9092 --list

# Describe group
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --describe --group my-group

# Reset offsets
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --group my-group --reset-offsets --to-earliest --topic my-topic --execute

# Delete group
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --delete --group my-group
```

### kafka-configs.sh

```bash
# Describe topic config
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type topics --entity-name my-topic --describe

# Alter topic config
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type topics --entity-name my-topic \
  --alter --add-config retention.ms=86400000

# Delete topic config
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type topics --entity-name my-topic \
  --alter --delete-config retention.ms
```

### kafka-acls.sh

```bash
# List ACLs
kafka-acls.sh --bootstrap-server kafka:9092 --list

# Add ACL
kafka-acls.sh --bootstrap-server kafka:9092 \
  --add --allow-principal User:producer \
  --operation Write --topic my-topic

# Remove ACL
kafka-acls.sh --bootstrap-server kafka:9092 \
  --remove --allow-principal User:producer \
  --operation Write --topic my-topic
```

---

## Metrics Reference

### Broker Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `kafka.server:type=BrokerTopicMetrics,name=MessagesInPerSec` | Rate | Messages produced |
| `kafka.server:type=BrokerTopicMetrics,name=BytesInPerSec` | Rate | Bytes produced |
| `kafka.server:type=BrokerTopicMetrics,name=BytesOutPerSec` | Rate | Bytes consumed |
| `kafka.controller:type=KafkaController,name=ActiveControllerCount` | Gauge | Active controllers |
| `kafka.controller:type=KafkaController,name=OfflinePartitionsCount` | Gauge | Offline partitions |
| `kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions` | Gauge | Under-replicated |

### Request Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `kafka.network:type=RequestMetrics,name=TotalTimeMs` | Histogram | Request latency |
| `kafka.network:type=RequestMetrics,name=RequestQueueTimeMs` | Histogram | Queue time |
| `kafka.network:type=RequestMetrics,name=LocalTimeMs` | Histogram | Processing time |
| `kafka.network:type=RequestMetrics,name=RemoteTimeMs` | Histogram | Replication time |

### Consumer Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `kafka.consumer:type=consumer-fetch-manager-metrics,records-lag` | Gauge | Consumer lag |
| `kafka.consumer:type=consumer-fetch-manager-metrics,fetch-rate` | Rate | Fetch rate |
| `kafka.consumer:type=consumer-coordinator-metrics,commit-rate` | Rate | Commit rate |

---

## Error Codes

| Code | Name | Retriable | Description |
|------|------|-----------|-------------|
| 0 | UNKNOWN_SERVER_ERROR | Yes | Unknown error |
| 1 | OFFSET_OUT_OF_RANGE | No | Invalid offset |
| 2 | CORRUPT_MESSAGE | No | CRC check failed |
| 3 | UNKNOWN_TOPIC_OR_PARTITION | Yes | Topic/partition not found |
| 5 | LEADER_NOT_AVAILABLE | Yes | Leader election in progress |
| 6 | NOT_LEADER_OR_FOLLOWER | Yes | Stale metadata |
| 7 | REQUEST_TIMED_OUT | Yes | Request timeout |
| 19 | NOT_ENOUGH_REPLICAS | Yes | ISR too small |
| 29 | TOPIC_AUTHORIZATION_FAILED | No | No topic ACL |
| 30 | GROUP_AUTHORIZATION_FAILED | No | No group ACL |

---

## Protocol Reference

### Record Batch Format

| Field | Size | Description |
|-------|------|-------------|
| baseOffset | int64 | First offset in batch |
| batchLength | int32 | Batch size bytes |
| partitionLeaderEpoch | int32 | Leader epoch |
| magic | int8 | Version (2) |
| crc | int32 | CRC32-C |
| attributes | int16 | Compression, timestamp type |
| lastOffsetDelta | int32 | Offset of last record |
| firstTimestamp | int64 | First record timestamp |
| maxTimestamp | int64 | Maximum timestamp |
| producerId | int64 | Producer ID |
| producerEpoch | int16 | Producer epoch |
| baseSequence | int32 | First sequence number |
| records | [Record] | Record array |

### API Keys

| Key | Name | Description |
|-----|------|-------------|
| 0 | Produce | Produce messages |
| 1 | Fetch | Fetch messages |
| 2 | ListOffsets | Get offsets |
| 3 | Metadata | Get cluster metadata |
| 8 | OffsetCommit | Commit consumer offsets |
| 9 | OffsetFetch | Fetch consumer offsets |
| 10 | FindCoordinator | Find group coordinator |
| 11 | JoinGroup | Join consumer group |
| 12 | Heartbeat | Consumer heartbeat |
| 13 | LeaveGroup | Leave consumer group |
| 14 | SyncGroup | Sync group state |

---

## Related Documentation

- [Configuration](../operations/configuration/index.md) - Full configuration guide
- [CLI Tools](../operations/cli-tools/index.md) - CLI reference
- [Monitoring](../operations/monitoring/index.md) - Metrics guide
- [Troubleshooting](../troubleshooting/index.md) - Error reference
