---
title: "Kafka Performance Internals"
description: "Apache Kafka performance architecture. Zero-copy, batching, compression, and I/O optimization."
meta:
  - name: keywords
    content: "Kafka performance, zero-copy, batching, compression, I/O optimization"
---

# Kafka Performance Internals

Deep dive into Kafka's performance architecture and optimization techniques.

---

## Performance Design Principles

```plantuml
@startuml


rectangle "Kafka Performance Stack" {
  rectangle "Batching" as batch
  rectangle "Compression" as compress
  rectangle "Sequential I/O" as seqio
  rectangle "Zero-Copy" as zerocopy
  rectangle "Page Cache" as cache
  rectangle "Efficient Serialization" as serial
}

batch --> compress : reduces\nmessages
compress --> seqio : smaller\nwrites
seqio --> cache : optimal\ndisk use
cache --> zerocopy : memory\nefficiency
zerocopy --> serial : minimal\ncopies

note bottom
  Each layer multiplies
  performance benefits
end note

@enduml
```

---

## Sequential I/O

For complete log segment structure, indexes, and retention policies, see [Storage Engine](../storage-engine/index.md).

### Write Path

Kafka appends all writes to the end of log segments, achieving sequential disk access.

```plantuml
@startuml


rectangle "Traditional Database" as db {
  rectangle "Random Writes" as random {
    card "Page 1" as p1
    card "Page 5" as p5
    card "Page 2" as p2
    card "Page 8" as p8
  }
}

rectangle "Kafka" as kafka {
  rectangle "Sequential Append" as seq {
    card "Offset 0" as o0
    card "Offset 1" as o1
    card "Offset 2" as o2
    card "Offset 3" as o3
    o0 --> o1
    o1 --> o2
    o2 --> o3
  }
}

note bottom of db
  Seeks between pages
  ~100 IOPS on HDD
end note

note bottom of kafka
  Single sequential stream
  ~100+ MB/s on HDD
end note

@enduml
```

### Performance Comparison

| Access Pattern | HDD Performance | SSD Performance |
|----------------|-----------------|-----------------|
| Random 4KB | ~100 IOPS | ~100K IOPS |
| Sequential | ~100 MB/s | ~500 MB/s |
| **Kafka advantage** | **1000x better** | **5x better** |

---

## Zero-Copy Transfers

### Traditional Copy Path

```plantuml
@startuml


rectangle "Application Read/Send" as trad {
  rectangle "Disk" as t_disk
  rectangle "Kernel\nBuffer" as t_k1
  rectangle "User\nBuffer" as t_user
  rectangle "Socket\nBuffer" as t_sock
  rectangle "NIC" as t_nic

  t_disk --> t_k1 : 1. DMA read
  t_k1 --> t_user : 2. CPU copy
  t_user --> t_sock : 3. CPU copy
  t_sock --> t_nic : 4. DMA send
}

note bottom of trad
  4 data copies
  2 context switches
  CPU overhead
end note

@enduml
```

### Zero-Copy Path (sendfile)

```plantuml
@startuml


rectangle "Kafka sendfile()" as zero {
  rectangle "Disk" as z_disk
  rectangle "Page\nCache" as z_cache
  rectangle "NIC" as z_nic

  z_disk --> z_cache : 1. DMA read
  z_cache --> z_nic : 2. DMA send
}

note bottom of zero
  0 CPU copies
  Direct kernel transfer
  Minimal CPU usage
end note

@enduml
```

### Implementation

```java
// Kafka uses FileChannel.transferTo()
// which maps to sendfile() system call
fileChannel.transferTo(position, count, socketChannel);
```

### Limitations

| Condition | Zero-Copy Available |
|-----------|---------------------|
| Plaintext | Yes |
| TLS/SSL enabled | No (encryption requires user-space) |
| Compression | Only for already-compressed data |

!!! warning "TLS Impact"
    Enabling TLS disables zero-copy, potentially reducing throughput by 30-50%.

---

## Batching

### Producer Batching

```plantuml
@startuml


rectangle "Producer" {
  rectangle "Record\nAccumulator" as accum {
    rectangle "Topic-Partition\nBatches" as batches {
      rectangle "P0 Batch" as b0
      rectangle "P1 Batch" as b1
      rectangle "P2 Batch" as b2
    }
  }

  rectangle "Sender" as sender
}

rectangle "Broker" as broker

b0 --> sender : batch ready
b1 --> sender : batch ready
sender --> broker : single request\nmultiple batches

@enduml
```

### Batching Configuration

| Parameter | Default | Effect |
|-----------|---------|--------|
| `batch.size` | 16384 | Maximum bytes per batch |
| `linger.ms` | 0 | Time to wait for more records |
| `buffer.memory` | 33554432 | Total memory for batching |

### Batching Benefits

```
Without batching (1000 messages):
  1000 network round-trips
  1000 small disk writes
  High overhead per message

With batching (1000 messages in 10 batches):
  10 network round-trips
  10 larger disk writes
  Amortized overhead
```

### Consumer Fetch Batching

```properties
# Minimum data to fetch
fetch.min.bytes=1

# Maximum time to wait
fetch.max.wait.ms=500

# Maximum data per request
fetch.max.bytes=52428800
```

---

## Compression

### Compression Algorithms

| Algorithm | Compression Ratio | CPU Usage | Speed |
|-----------|-------------------|-----------|-------|
| **none** | 1.0x | None | Fastest |
| **gzip** | ~5-8x | High | Slow |
| **snappy** | ~2-3x | Low | Fast |
| **lz4** | ~3-4x | Low | Fastest |
| **zstd** | ~4-6x | Medium | Fast |

### Compression Flow

```plantuml
@startuml


rectangle "Producer" {
  rectangle "Batch\n(uncompressed)" as raw
  rectangle "Compressed\nBatch" as comp
  raw --> comp : compress
}

rectangle "Broker" {
  rectangle "Stored\n(compressed)" as stored
}

rectangle "Consumer" {
  rectangle "Decompressed\nBatch" as decomp
}

comp --> stored : store as-is
stored --> decomp : decompress

note bottom
  Broker stores compressed data
  No compression/decompression on broker
end note

@enduml
```

### Configuration

```properties
# Producer compression
compression.type=lz4

# Topic-level compression (broker will recompress if different)
compression.type=producer  # Keep producer compression
compression.type=gzip      # Force specific compression
```

### Compression Selection Guide

| Use Case | Recommended |
|----------|-------------|
| **High throughput, low latency** | lz4 |
| **Balanced** | zstd |
| **Maximum compression** | gzip |
| **Minimal CPU** | snappy |
| **Already compressed data** | none |

---

## Request Pipelining

### In-Flight Requests

```plantuml
@startuml


participant "Producer" as prod
participant "Broker" as broker

prod -> broker : Request 1
prod -> broker : Request 2
prod -> broker : Request 3

broker -> prod : Response 1
broker -> prod : Response 2
broker -> prod : Response 3

note over prod, broker
  Multiple requests in flight
  without waiting for responses
end note

@enduml
```

```properties
# Maximum in-flight requests
max.in.flight.requests.per.connection=5
```

### Ordering Considerations

| Setting | Ordering | Throughput |
|---------|----------|------------|
| `max.in.flight=1` | Guaranteed | Lower |
| `max.in.flight=5` | May reorder on retry | Higher |
| `max.in.flight=5` + idempotent | Guaranteed | Higher |

---

## Thread Model

### Broker Threads

```plantuml
@startuml


rectangle "Broker Thread Model" {
  rectangle "Network Threads\n(num.network.threads)" as net {
    rectangle "Accept" as accept
    rectangle "Read" as read
    rectangle "Write" as write
  }

  rectangle "Request Queue" as queue

  rectangle "I/O Threads\n(num.io.threads)" as io {
    rectangle "IO-1" as io1
    rectangle "IO-2" as io2
    rectangle "IO-N" as ion
  }

  rectangle "Response Queue" as resp

  net --> queue : enqueue
  queue --> io : process
  io --> resp : enqueue
  resp --> net : send
}

@enduml
```

### Thread Configuration

| Parameter | Default | Recommendation |
|-----------|---------|----------------|
| `num.network.threads` | 3 | CPU cores / 4 |
| `num.io.threads` | 8 | CPU cores |
| `num.replica.fetchers` | 1 | 2-4 for high partition counts |
| `num.recovery.threads.per.data.dir` | 1 | 2-4 for faster recovery |

---

## Page Cache Optimization

### Warm Cache Benefits

```plantuml
@startuml


rectangle "Read Scenarios" {
  rectangle "Hot Read\n(cache hit)" as hot {
    card "0.1 ms" as hot_time
  }

  rectangle "Warm Read\n(partial hit)" as warm {
    card "1-5 ms" as warm_time
  }

  rectangle "Cold Read\n(cache miss)" as cold {
    card "10+ ms" as cold_time
  }
}

note bottom
  Recent data served from memory
  Consumer lag = more cache misses
end note

@enduml
```

### Optimal Memory Allocation

```
Total RAM: 64 GB

JVM Heap: 6 GB (enough for metadata)
OS/System: 2 GB
Page Cache: 56 GB (for log data)

If hourly throughput = 50 GB
Page cache covers ~1 hour of data
```

---

## Benchmarking

### Producer Performance Test

```bash
# Throughput test
kafka-producer-perf-test.sh \
  --topic test-topic \
  --num-records 10000000 \
  --record-size 1024 \
  --throughput -1 \
  --producer-props \
    bootstrap.servers=kafka:9092 \
    batch.size=65536 \
    linger.ms=10 \
    compression.type=lz4
```

### Consumer Performance Test

```bash
# Throughput test
kafka-consumer-perf-test.sh \
  --bootstrap-server kafka:9092 \
  --topic test-topic \
  --messages 10000000 \
  --threads 4
```

### End-to-End Latency Test

```bash
kafka-run-class.sh kafka.tools.EndToEndLatency \
  kafka:9092 \
  test-topic \
  10000 \
  all \
  1024
```

---

## Performance Metrics

### Key Metrics

| Metric | Healthy Range |
|--------|---------------|
| `RequestsPerSec` | Depends on workload |
| `TotalTimeMs (P99)` | < 100 ms |
| `RequestQueueTimeMs` | < 10 ms |
| `LocalTimeMs` | < 50 ms |
| `RemoteTimeMs` | < 50 ms |
| `ThrottleTimeMs` | 0 |

### Bottleneck Identification

| Symptom | Likely Bottleneck |
|---------|-------------------|
| High RequestQueueTimeMs | Network threads saturated |
| High LocalTimeMs | Disk I/O or I/O threads saturated |
| High RemoteTimeMs | Replication lag |
| High ResponseQueueTimeMs | Network threads saturated |

---

## Related Documentation

- [Architecture Overview](../index.md) - System architecture
- [Memory Management](../memory-management/index.md) - Memory tuning
- [Storage Engine](../storage-engine/index.md) - Disk I/O optimization
- [Operations](../../operations/index.md) - Operational procedures
