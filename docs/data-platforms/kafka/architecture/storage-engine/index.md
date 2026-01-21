---
title: "Kafka Storage Engine"
description: "Apache Kafka storage internals. Log segments, indexes, compaction, and retention policies."
meta:
  - name: keywords
    content: "Kafka storage, log segments, Kafka compaction, retention, Kafka indexes"
---

# Storage Engine

Kafka's storage engine provides durable, high-throughput message persistence through an append-only log structure.

---

## Log Structure

Each partition is stored as an ordered, append-only sequence of records in log segments.

```plantuml
@startuml

rectangle "Topic: orders, Partition: 0" as partition {
  rectangle "Segment 0\n(00000000000000000000.log)\noffsets 0-999" as seg0
  rectangle "Segment 1\n(00000000000000001000.log)\noffsets 1000-1999" as seg1
  rectangle "Segment 2 (Active)\n(00000000000000002000.log)\noffsets 2000-current" as seg2
}

seg0 -right-> seg1 : older
seg1 -right-> seg2 : newer

note bottom of seg2
  Active segment
  receives new writes
end note

@enduml
```

### Directory Structure

```
/var/kafka-logs/
├── orders-0/
│   ├── 00000000000000000000.log      # Segment file
│   ├── 00000000000000000000.index    # Offset index
│   ├── 00000000000000000000.timeindex # Timestamp index
│   ├── 00000000000000000000.txnindex  # Transaction index
│   ├── 00000000000000000000.snapshot  # Producer state
│   ├── 00000000000000001000.log
│   ├── 00000000000000001000.index
│   ├── 00000000000000001000.timeindex
│   ├── leader-epoch-checkpoint
│   └── partition.metadata
├── orders-1/
│   └── ...
└── orders-2/
    └── ...
```

---

## Log Segments

### Segment Files

| File | Purpose | Content |
|------|---------|---------|
| `.log` | Message data | Record batches |
| `.index` | Offset index | Offset → position mapping |
| `.timeindex` | Timestamp index | Timestamp → offset mapping |
| `.snapshot` | Producer state | Idempotency data |
| `.txnindex` | Transaction index | Aborted transactions |

### Segment Rolling

New segments are created when:

| Condition | Configuration |
|-----------|---------------|
| Size threshold | `log.segment.bytes` (default: 1GB) |
| Time threshold | `log.roll.ms` / `log.roll.hours` (broker defaults for `segment.ms`) |
| Index full | `log.index.size.max.bytes` |

```properties
# Segment configuration
log.segment.bytes=1073741824        # 1GB
log.roll.hours=168                  # 7 days
log.index.size.max.bytes=10485760  # 10MB
log.index.interval.bytes=4096      # Index entry every 4KB
```

---

## Record Format

### Record Batch Structure

```
RecordBatch:
├── baseOffset: int64
├── batchLength: int32
├── partitionLeaderEpoch: int32
├── magic: int8 (2 for current version)
├── crc: int32
├── attributes: int16
│   ├── compression (bits 0-2)
│   ├── timestampType (bit 3)
│   ├── isTransactional (bit 4)
│   └── isControlBatch (bit 5)
├── lastOffsetDelta: int32
├── firstTimestamp: int64
├── maxTimestamp: int64
├── producerId: int64
├── producerEpoch: int16
├── baseSequence: int32
├── records: [Record]
```

### Individual Record

```
Record:
├── length: varint
├── attributes: int8
├── timestampDelta: varlong
├── offsetDelta: varint
├── keyLength: varint
├── key: byte[]
├── valueLength: varint
├── value: byte[]
└── headers: [Header]
```

---

## Indexes

### Offset Index

Maps logical offsets to physical file positions for efficient seeking.

```plantuml
@startuml

rectangle "Offset Index\n(.index)" as index {
  rectangle "offset: 0 → position: 0" as e0
  rectangle "offset: 100 → position: 4096" as e1
  rectangle "offset: 200 → position: 8192" as e2
  rectangle "..." as e3
}

rectangle "Log Segment\n(.log)" as log {
  rectangle "Records 0-99" as r0
  rectangle "Records 100-199" as r1
  rectangle "Records 200-299" as r2
}

e0 --> r0
e1 --> r1
e2 --> r2

note right of index
  Sparse index
  One entry per
  log.index.interval.bytes
end note

@enduml
```

### Timestamp Index

Maps timestamps to offsets for time-based seeking.

```bash
# Seek to offset by timestamp
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --group my-group \
  --topic orders \
  --reset-offsets \
  --to-datetime 2024-01-15T10:00:00.000 \
  --execute
```

---

## Retention

### Time-Based Retention

Delete segments older than retention period.

```properties
log.retention.ms=604800000        # 7 days (default)
log.retention.check.interval.ms=300000  # Check every 5 min
```

!!! note "Retention aliases"
    `log.retention.hours` and `log.retention.minutes` are legacy aliases for `log.retention.ms`.

### Size-Based Retention

Delete oldest segments when partition exceeds size limit.

```properties
log.retention.bytes=107374182400  # 100GB per partition
```

### Retention Behavior

```plantuml
@startuml

rectangle "Partition" as partition {
  rectangle "Segment 0\n(7 days old)" as seg0 #red
  rectangle "Segment 1\n(5 days old)" as seg1
  rectangle "Segment 2\n(3 days old)" as seg2
  rectangle "Segment 3\n(active)" as seg3
}

seg0 --> seg0 : DELETE\n(exceeds retention)

note bottom of partition
  log.retention.hours=168 (7 days)
  Segment 0 eligible for deletion
end note

@enduml
```

---

## Log Compaction

Retains only the latest value for each key, useful for changelog/table semantics.

```plantuml
@startuml

rectangle "Before Compaction" as before {
  card "K1:V1" as k1v1
  card "K2:V1" as k2v1
  card "K1:V2" as k1v2
  card "K3:V1" as k3v1
  card "K1:V3" as k1v3
  card "K2:V2" as k2v2
}

rectangle "After Compaction" as after {
  card "K1:V3" as k1v3_after
  card "K2:V2" as k2v2_after
  card "K3:V1" as k3v1_after
}

before -down-> after : compact

note right of after
  Only latest value
  per key retained
end note

@enduml
```

### Compaction Configuration

```properties
# Enable compaction
log.cleanup.policy=compact

# Or both delete and compact
log.cleanup.policy=compact,delete

# Broker compaction defaults
log.cleaner.enable=true
log.cleaner.threads=1
log.cleaner.min.cleanable.ratio=0.5
log.cleaner.min.compaction.lag.ms=0
log.cleaner.delete.retention.ms=86400000  # 24h tombstone retention

# Segment eligibility
log.segment.bytes=1073741824
min.cleanable.dirty.ratio=0.5

!!! note "Scope"
    `log.cleaner.*` settings are broker defaults. `min.cleanable.dirty.ratio` is a topic-level override.
```

### Tombstones

Delete a key by producing a record with null value (tombstone).

```java
producer.send(new ProducerRecord<>("topic", "key-to-delete", null));
```

Tombstones are retained for `log.cleaner.delete.retention.ms` before removal.

---

## Performance Optimizations

For complete performance tuning including batching, compression selection, and thread model optimization, see [Performance Internals](../performance-internals/index.md).

### Zero-Copy

Kafka uses `sendfile()` to transfer data directly from page cache to network socket.

```plantuml
@startuml

rectangle "Traditional Copy" as trad {
  rectangle "Disk" as disk1
  rectangle "Page Cache" as pc1
  rectangle "Application Buffer" as app1
  rectangle "Socket Buffer" as sock1
  rectangle "Network" as net1

  disk1 -> pc1 : 1. read
  pc1 -> app1 : 2. copy
  app1 -> sock1 : 3. copy
  sock1 -> net1 : 4. send
}

rectangle "Zero-Copy (sendfile)" as zero {
  rectangle "Disk" as disk2
  rectangle "Page Cache" as pc2
  rectangle "Network" as net2

  disk2 -> pc2 : 1. read
  pc2 -> net2 : 2. sendfile()
}

note bottom of zero
  Eliminates 2 copies
  and context switches
  (disabled with TLS)
end note

@enduml
```

### Page Cache

Kafka relies heavily on OS page cache for read performance.

| Recommendation (Repository Guidance) | Rationale |
|----------------|-----------|
| Allocate 25-50% RAM to page cache | Caches active segments |
| Use SSDs | Faster random reads for index lookups |
| Separate disks for log.dirs | Parallel I/O |

---

## Monitoring Storage

### Key Metrics

| Metric | Description |
|--------|-------------|
| `kafka.log:type=Log,name=Size` | Partition size in bytes |
| `kafka.log:type=Log,name=NumLogSegments` | Segment count |
| `kafka.log:type=LogCleaner,name=cleaner-recopy-percent` | Compaction efficiency |
| `kafka.log:type=LogCleaner,name=max-clean-time-secs` | Compaction duration |

### Disk Commands

```bash
# Check partition sizes
du -sh /var/kafka-logs/*/

# List segment files
ls -la /var/kafka-logs/orders-0/

# Dump log segment
kafka-dump-log.sh --files /var/kafka-logs/orders-0/00000000000000000000.log \
  --print-data-log
```

---

## Related Documentation

- [Architecture Overview](../index.md) - Kafka architecture
- [Performance](../performance-internals/index.md) - Performance optimizations
- [Operations](../../operations/index.md) - Operational procedures
- [Configuration](../../operations/configuration/index.md) - Configuration reference
