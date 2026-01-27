---
title: "Kafka Producer Batching"
description: "Apache Kafka producer batching. Record accumulator, batch configuration, linger.ms, and throughput optimization."
meta:
  - name: keywords
    content: "Kafka batching, batch.size, linger.ms, producer batching, batch optimization"
---

# Kafka Producer Batching

Kafka producers batch multiple messages together before sending to brokers, significantly improving throughput and efficiency. Understanding batching is essential for optimizing producer performance and balancing latency versus throughput trade-offs.

## Batching Overview

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Producer" {
    rectangle "Application Threads" as App {
        rectangle "send()" as Send1
        rectangle "send()" as Send2
        rectangle "send()" as Send3
    }

    rectangle "RecordAccumulator" as RA {
        rectangle "Topic: orders" as Topic {
            rectangle "P0 Batch\n[msg1, msg2]" as B0
            rectangle "P1 Batch\n[msg3]" as B1
            rectangle "P2 Batch\n[msg4, msg5, msg6]" as B2
        }
    }

    rectangle "Sender Thread" as Sender
}

rectangle "Broker" as Broker

Send1 --> RA
Send2 --> RA
Send3 --> RA

Sender --> RA : drain batches
Sender --> Broker : send

note right of RA
  Messages accumulated
  per partition until:
  - Batch is full
  - linger.ms expires
end note

@enduml
```

---

## Batching Benefits

### Efficiency Gains

| Aspect | Without Batching | With Batching |
|--------|-----------------|---------------|
| **Network requests** | 1 per message | 1 per batch |
| **Header overhead** | High (repeated headers) | Amortized |
| **Compression** | Per-message | Per-batch (better ratio) |
| **Broker I/O** | Many small writes | Fewer large writes |

### Throughput Impact

```plantuml
@startuml

skinparam backgroundColor transparent

title Throughput vs Batch Size

rectangle "100-byte messages" as M100 {
    rectangle "No batching: ~10K msg/s" as M100_0
    rectangle "16KB batch: ~100K msg/s" as M100_16
    rectangle "64KB batch: ~500K msg/s" as M100_64
}

note bottom of M100
  Larger batches = higher throughput
  (up to network/broker limits)
end note

@enduml
```

!!! note "Illustrative throughput"
    The throughput figures above are illustrative; actual results vary with message size, hardware, compression, and broker configuration.

---

## Record Accumulator

The `RecordAccumulator` is the internal component that manages message batching.

### Structure

```plantuml
@startuml

skinparam backgroundColor transparent

package "RecordAccumulator" {
    rectangle "Buffer Pool" as BufferPool {
        rectangle "Free Buffers" as Free
        rectangle "Allocated: batch.size × N" as Alloc
    }

    rectangle "Batches (per TopicPartition)" as Batches {
        rectangle "orders-0" as O0 {
            rectangle "Batch (building)" as O0B
        }
        rectangle "orders-1" as O1 {
            rectangle "Batch (ready)" as O1B
        }
        rectangle "orders-2" as O2 {
            rectangle "Batch (in-flight)" as O2B
        }
    }

    rectangle "Memory Tracking" as Memory {
        rectangle "Used: X bytes" as Used
        rectangle "Available: Y bytes" as Avail
    }
}

Free --> O0B : allocate
O1B --> Batches : ready to send
Memory --> Batches : track

@enduml
```

### Batch Lifecycle

```plantuml
@startuml

skinparam backgroundColor transparent

state "Empty" as Empty
state "Building" as Building
state "Ready" as Ready
state "In-Flight" as InFlight
state "Completed" as Completed
state "Failed" as Failed

[*] --> Empty : allocate buffer

Empty --> Building : first record appended
Building --> Building : append records

Building --> Ready : batch.size reached
Building --> Ready : linger.ms expired
Building --> Building : buffer exhausted (append blocks)

Ready --> InFlight : sender drains batch
InFlight --> Completed : ack received
InFlight --> Failed : timeout/error

Completed --> [*] : return buffer
Failed --> InFlight : retry (if retriable)
Failed --> [*] : return buffer + callback error

@enduml
```

---

## Batch Configuration

### Core Settings

```properties
# Maximum batch size in bytes
batch.size=16384  # 16 KB (default)

# Time to wait for batch to fill
linger.ms=0  # No wait (default)

# Total memory for buffering
buffer.memory=33554432  # 32 MB (default)

# Maximum time to block on send() when buffer full
max.block.ms=60000  # 60 seconds (default)
```

### Configuration Trade-offs

| Setting | Low Value | High Value |
|---------|-----------|------------|
| `batch.size` | Lower latency, lower throughput | Higher throughput, more memory |
| `linger.ms` | Immediate send, small batches | Larger batches, added latency |
| `buffer.memory` | Less memory, more blocking | Higher throughput, more memory |

---

## Linger Time

### How linger.ms Works

```plantuml
@startuml

skinparam backgroundColor transparent

concise "Batch State" as Batch
concise "Action" as Action

@0
Batch is "Empty"
Action is "First record"

@10
Batch is "Building"
Action is "linger timer starts"

@15
Batch is "Building"
Action is "More records"

@20
Batch is "Building"
Action is "(waiting)"

scale 1 as 50 pixels

@30
Batch is "Ready"
Action is "linger.ms expired"

@35
Batch is "Sent"
Action is "Sender drains"

@enduml
```

### linger.ms Examples

| linger.ms | Behavior | Use Case |
|:---------:|----------|----------|
| 0 | Send immediately (default) | Latency-sensitive |
| 5 | Wait up to 5ms | Low-latency with some batching |
| 20 | Wait up to 20ms | Balanced throughput/latency |
| 100+ | Wait up to 100ms+ | Maximum throughput |

### Batch Triggers

A batch is sent when ANY condition is met:

1. **Batch full**: `batch.size` reached
2. **Linger expired**: `linger.ms` elapsed since first record
3. **Explicit flush**: `producer.flush()` called
4. **Close**: `producer.close()` called

When the buffer is exhausted, `send()` blocks until memory is freed; it does not force a batch to send.

---

## Memory Management

### Buffer Pool

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "buffer.memory (32 MB)" {
    rectangle "Batch Buffer Pool" as Pool {
        rectangle "Used (16 MB)" as Used {
            rectangle "Batch 1" as B1
            rectangle "Batch 2" as B2
            rectangle "Batch 3" as B3
            rectangle "..." as Dots
        }
        rectangle "Free (16 MB)" as Free
    }
}

note right of Pool
  Buffers are recycled
  to avoid GC pressure
end note

@enduml
```

### Memory Exhaustion

```plantuml
@startuml

skinparam backgroundColor transparent

start

:send() called;

if (Buffer available?) then (yes)
    :Append to batch;
    :Return Future;
else (no)
    :Block thread;

    if (max.block.ms exceeded?) then (yes)
        :Throw TimeoutException;
        stop
    else (no)
        :Wait for buffer;
    endif
endif

stop

@enduml
```

### Monitoring Memory

```java
// Get producer metrics
Map<MetricName, ? extends Metric> metrics = producer.metrics();

// Key metrics
// - buffer-total-bytes: Total buffer memory
// - buffer-available-bytes: Available buffer memory
// - bufferpool-wait-time: Time blocked waiting for buffer
```

---

## Per-Partition Batching

### Partition Isolation

Each partition has its own batch queue:

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "RecordAccumulator" {
    rectangle "Topic: orders" {
        rectangle "Partition 0" as P0 {
            rectangle "Batch (75% full)" as P0B
        }
        rectangle "Partition 1" as P1 {
            rectangle "Batch (100% full, ready)" as P1B #lightgreen
        }
        rectangle "Partition 2" as P2 {
            rectangle "Batch (10% full)" as P2B
        }
    }
}

note bottom of P1B
  P1 batch ready
  (will send immediately)
  Other partitions continue filling
end note

@enduml
```

### Implications

| Behavior | Description |
|----------|-------------|
| **Independent batching** | Each partition fills independently |
| **Parallel sends** | Ready batches sent to different brokers in parallel |
| **Uneven filling** | Hot partitions batch faster |

---

## Batch Compression

### Compression at Batch Level

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Batch (uncompressed)" as Raw {
    rectangle "Record 1 (100 bytes)" as R1
    rectangle "Record 2 (100 bytes)" as R2
    rectangle "Record 3 (100 bytes)" as R3
    rectangle "..." as Dots
    rectangle "Record 100 (100 bytes)" as R100
    note bottom: 10 KB total
}

rectangle "Batch (compressed)" as Comp {
    rectangle "Compressed payload" as CP
    note bottom: ~3 KB (LZ4)
}

Raw --> Comp : compress()

note right of Comp
  Batch compression:
  - Better ratio than per-record
  - Single compress operation
  - Stored compressed on broker
end note

@enduml
```

### Compression + Batching

```properties
# Enable compression for better efficiency
compression.type=lz4

# Larger batches compress better
batch.size=65536  # 64 KB

# Allow time for batch accumulation
linger.ms=20
```

---

## Request Building

### From Batches to Requests

```plantuml
@startuml

skinparam backgroundColor transparent

participant "Sender" as S
participant "RecordAccumulator" as RA
participant "NetworkClient" as NC

S -> RA : ready(now)
RA --> S : ReadyCheckResult\n{readyNodes, nextReadyMs}

S -> RA : drain(readyNodes)
RA --> S : Map<Node, List<ProducerBatch>>

loop for each node
    S -> S : Group batches by topic-partition
    S -> NC : send(ProduceRequest)
end

@enduml
```

### Produce Request Structure

```
ProduceRequest {
    transactional_id: string (nullable)
    acks: int16
    timeout_ms: int32
    topic_data: [{
        topic: string
        partition_data: [{
            partition: int32
            records: RecordBatch  // Compressed batch
        }]
    }]
}
```

---

## Performance Tuning

### High Throughput Configuration

```properties
# Large batches
batch.size=131072  # 128 KB

# Wait for batch to fill
linger.ms=50

# Plenty of buffer memory
buffer.memory=134217728  # 128 MB

# Compression for network efficiency
compression.type=lz4

# Multiple in-flight for pipelining
max.in.flight.requests.per.connection=5
```

### Low Latency Configuration

```properties
# Smaller batches
batch.size=16384  # 16 KB

# Minimal wait
linger.ms=0

# Standard buffer
buffer.memory=33554432  # 32 MB

# No compression (fastest)
compression.type=none

# Still use multiple in-flight
max.in.flight.requests.per.connection=5
```

### Balanced Configuration

```properties
# Moderate batch size
batch.size=32768  # 32 KB

# Small wait for accumulation
linger.ms=10

# Adequate buffer
buffer.memory=67108864  # 64 MB

# Light compression
compression.type=lz4

max.in.flight.requests.per.connection=5
```

---

## Batching Metrics

### Key Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| `batch-size-avg` | Average batch size | Close to `batch.size` |
| `batch-size-max` | Maximum batch size | ≤ `batch.size` |
| `record-queue-time-avg` | Time in accumulator | Close to `linger.ms` |
| `records-per-request-avg` | Records per request | Higher = better batching |
| `bufferpool-wait-time` | Time waiting for buffer | Should be 0 |

### Diagnosing Poor Batching

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| Small `batch-size-avg` | Too many partitions | Consolidate or increase `linger.ms` |
| Small `batch-size-avg` | Low message rate | Increase `linger.ms` |
| High `bufferpool-wait-time` | Buffer exhaustion | Increase `buffer.memory` |
| High `record-queue-time-avg` | Slow broker response | Check broker health |

---

## Async vs Sync Behavior

### Asynchronous (Default)

```java
// Non-blocking - returns immediately
Future<RecordMetadata> future = producer.send(record);

// Optional callback
producer.send(record, (metadata, exception) -> {
    if (exception != null) {
        handleError(exception);
    }
});
```

### Synchronous Pattern

```java
// Blocking - waits for broker ack
try {
    RecordMetadata metadata = producer.send(record).get();
} catch (ExecutionException e) {
    handleError(e.getCause());
}
```

!!! warning "Synchronous Impact"
    Synchronous sends defeat batching benefits. Each send waits for response before next send can proceed. Use async with callbacks for production.

### Flush Behavior

```java
// Send accumulated batches immediately
producer.flush();  // Blocks until all batches sent

// Flush before close
producer.flush();
producer.close();
```

---

## Version Compatibility

| Feature | Minimum Version |
|---------|-----------------|
| Record batching | 0.8.0 |
| Compression per batch | 0.8.0 |
| Sticky partitioner | 2.4.0 |
| Idempotent batching | 0.11.0 |
| Transactional batching | 0.11.0 |

---

## Related Documentation

- [Kafka Protocol](kafka-protocol.md) - Wire protocol and record format
- [Compression](compression.md) - Batch compression
- [Producer Guide](../../application-development/producers/index.md) - Full producer configuration
- [Performance Internals](../performance-internals/index.md) - Throughput optimization