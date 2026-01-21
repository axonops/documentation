---
title: "Cassandra Inter-Node Data Streaming"
description: "Data streaming in Cassandra for bootstrap, rebuild, and repair operations. Stream throughput tuning."
meta:
  - name: keywords
    content: "Cassandra streaming, data streaming, bootstrap, rebuild, stream throughput"
search:
  boost: 3
---

# Inter-Node Data Streaming

Data streaming is the mechanism by which Cassandra nodes transfer SSTable data directly between each other. This inter-node data transfer occurs during cluster topology changes, repair operations, and failure recovery scenarios. Understanding the streaming subsystem is essential for capacity planning, operational troubleshooting, and performance optimization.

---

## Overview

### What is Streaming?

Streaming is Cassandra's bulk data transfer protocol for moving SSTable segments between nodes. Unlike the normal read/write path that operates on individual rows, streaming transfers entire SSTable files or portions thereof at the file level.

```plantuml
@startuml
skinparam backgroundColor transparent
title Streaming vs Normal Read/Write Path

package "Normal Path (row-level)" {
    rectangle "Client" as client
    rectangle "Coordinator" as coord
    rectangle "Replica" as replica

    client --> coord : CQL query
    coord --> replica : row mutation
}

package "Streaming Path (SSTable-level)" {
    rectangle "Source Node\nSSTable files" as source
    rectangle "Target Node\nSSTable files" as target

    source ==> target : SSTable segments\n(bulk transfer)
}

@enduml
```

### When Streaming Occurs

| Operation | Direction | Trigger |
|-----------|-----------|---------|
| Bootstrap | Existing → New node | New node joins cluster |
| Decommission | Leaving → Remaining nodes | Node removal initiated |
| Repair | Bidirectional between replicas | Manual or scheduled repair |
| Rebuild | Existing → Rebuilt node | `nodetool rebuild` command |
| Host replacement | Existing → Replacement node | Dead node replaced |
| Hinted handoff | Coordinator → Recovered node | Node recovers after failure |

---

## Streaming Architecture

### Protocol Stack

Cassandra's streaming protocol operates as a separate subsystem from the CQL protocol:

```plantuml
@startuml
skinparam backgroundColor transparent
title Streaming Protocol Stack

package "Streaming Session" {
    rectangle "Stream Coordinator\n• Identifies ranges\n• Selects SSTables\n• Manages transfers" as coord
    rectangle "Stream Receiver\n• Accepts connections\n• Receives file segments\n• Writes to local storage" as recv
}

rectangle "Messaging Layer\nStreamInitMessage | FileMessage | StreamReceivedMessage | StreamCompleteMessage" as messaging

rectangle "Transport Layer\n• Dedicated streaming port (default: storage_port)\n• Optionally encrypted (TLS)\n• Compression (LZ4)" as transport

coord -[hidden]down-> messaging
recv -[hidden]down-> messaging
messaging --> transport

@enduml
```

### Streaming Session Lifecycle

A streaming session progresses through distinct phases:

```plantuml
@startuml
skinparam backgroundColor transparent
title Streaming Session State Machine

[*] --> INITIALIZED
INITIALIZED --> PREPARING : session start
PREPARING --> STREAMING : plans exchanged
PREPARING --> FAILED : error
STREAMING --> COMPLETE : all files transferred
STREAMING --> FAILED : error/timeout
COMPLETE --> [*]
FAILED --> [*]

@enduml
```

**Phase descriptions:**

| Phase | Operations |
|-------|------------|
| **INITIALIZED** | Session created, peers identified |
| **PREPARING** | Token ranges calculated, SSTable selection, streaming plan exchanged |
| **STREAMING** | File transfers in progress, progress tracking |
| **COMPLETE** | All transfers successful, SSTables integrated |
| **FAILED** | Error occurred, partial cleanup, retry may follow |

### Zero-Copy Streaming (Cassandra 4.0+)

Cassandra 4.0 introduced zero-copy streaming, which transfers entire SSTable components without deserialization:

```plantuml
@startuml
skinparam backgroundColor transparent
title Traditional vs Zero-Copy Streaming

package "Traditional Streaming (pre-4.0)" {
    rectangle "SSTable\n(source)" as src1
    rectangle "Memory\n(heap)" as mem
    rectangle "SSTable\n(target)" as tgt1

    src1 --> mem : deserialize
    mem --> tgt1 : serialize

    note bottom of mem
      CPU + GC overhead
    end note
}

package "Zero-Copy Streaming (4.0+)" {
    rectangle "SSTable\n(source)" as src2
    rectangle "SSTable\n(target)" as tgt2

    src2 ==> tgt2 : direct file transfer\n(kernel buffer)

    note bottom of tgt2
      Minimal CPU/heap usage
    end note
}

@enduml
```

| Characteristic | Traditional | Zero-Copy |
|----------------|-------------|-----------|
| CPU usage | High (ser/deser) | Minimal |
| Heap pressure | Significant | Negligible |
| Throughput | Limited by CPU | Limited by network/disk |
| Compatibility | All SSTables | Same-version SSTables only |
| TLS support | Yes | No |

!!! warning "Zero-Copy Requirements and Limitations"
    Zero-copy streaming has specific requirements that, when not met, cause automatic fallback to traditional streaming:

    - **SSTable format compatibility**: Source and target nodes must use compatible SSTable formats. During rolling upgrades with format changes, traditional streaming is used.
    - **Inter-node encryption (TLS)**: Zero-copy streaming is **disabled** when inter-node encryption is enabled. TLS requires data to pass through the encryption layer, necessitating memory copies for encryption/decryption operations. Clusters with `server_encryption_options` enabled will always use traditional streaming.
    - **Configuration**: Zero-copy must be enabled via `stream_entire_sstables: true` (default in 4.0+).

    For security-conscious deployments requiring TLS, account for the additional CPU and memory overhead of traditional streaming during capacity planning for bootstrap, decommission, and repair operations.

---

## Bootstrap

Bootstrap is the process by which a new node joins the cluster and receives its share of data from existing nodes.

### Bootstrap Sequence

```plantuml
@startuml
skinparam backgroundColor transparent
title Bootstrap Process

rectangle "1. New Node Starts\nContacts seed nodes" as start
rectangle "2. Gossip Integration\nLearns cluster topology" as gossip
rectangle "3. Token Selection\nDetermines owned ranges" as token
rectangle "4. Stream Planning\nIdentifies source nodes" as plan
rectangle "5. Data Streaming\nReceives SSTables" as stream
rectangle "6. Bootstrap Complete\nAccepts client requests" as finish

start --> gossip
gossip --> token
token --> plan
plan --> stream
stream --> finish

@enduml
```

### Token Range Calculation

During bootstrap, the new node must determine which token ranges it will own:

```plantuml
@startuml
skinparam backgroundColor transparent
title Token Range Calculation During Bootstrap

rectangle "Before Bootstrap (4 nodes)" as before_box {
    card "Token 0 to 25: Node A" as a1
    card "Token 25 to 50: Node B" as b1
    card "Token 50 to 75: Node C" as c1
    card "Token 75 to 0: Node D" as d1
}

rectangle "After Bootstrap (5 nodes)" as after_box {
    card "Token 0 to 25: Node A" as a2
    card "Token 25 to 50: Node B" as b2
    card "Token 50 to 62: Node C" as c2
    card "Token 62 to 75: **Node E (new)**" as e2 #lightgreen
    card "Token 75 to 0: Node D" as d2
}

rectangle "Node E Must Receive" as receive_box {
    card "Primary range: 62-75 from Node D\nReplica ranges based on RF=3 topology" as receive
}

before_box -right-> after_box : Node E joins\nat token 62
after_box -down-> receive_box

@enduml
```

### Streaming Source Selection

The bootstrap coordinator selects source nodes based on:

1. **Token ownership**: Nodes currently owning required ranges
2. **Replica set**: For each range, any replica can serve as source
3. **Node state**: Only UP nodes considered
4. **Load balancing**: Distribute streaming load across sources

| Selection Criterion | Rationale |
|--------------------|-----------|
| Prefer local datacenter | Lower network latency |
| Prefer least-loaded nodes | Minimize impact on production |
| Avoid nodes already streaming | Prevent overload |
| Round-robin across replicas | Balance source load |

### Bootstrap Configuration

```yaml
# cassandra.yaml bootstrap parameters

# Number of concurrent streaming sessions per source
streaming_connections_per_host: 1

# Throughput limit (MB/s, 0 = unlimited)
stream_throughput_outbound_megabits_per_sec: 200

# Enable zero-copy streaming
stream_entire_sstables: true

# Bootstrap timeout
streaming_keep_alive_period_in_secs: 300
```

---

## Decommission

Decommission is the orderly removal of a node from the cluster, streaming all locally-owned data to remaining nodes before shutdown.

### Decommission Sequence

```plantuml
@startuml
skinparam backgroundColor transparent
title Decommission Process

rectangle "1. Decommission Initiated\nnodetool decommission" as start
rectangle "2. State Announcement\nGossip: LEAVING status" as announce
rectangle "3. Stream Planning\nCalculate target nodes" as plan
rectangle "4. Data Streaming\nTransfer all local data" as stream
rectangle "5. State: LEFT\nRemoved from ring" as left
rectangle "6. Node Shutdown\nProcess terminates" as shutdown

start --> announce
announce --> plan
plan --> stream
stream --> left
left --> shutdown

@enduml
```

### Range Redistribution

During decommission, the departing node's ranges must be redistributed:

```plantuml
@startuml
skinparam backgroundColor transparent
title Range Redistribution During Decommission

package "Before Decommission (RF=3, 5 nodes)" {
    rectangle "Range (40, 60]" as range1
    rectangle "Node C\n(primary)" as c1
    rectangle "Node D\n(replica)" as d1
    rectangle "Node E\n(replica)" as e1

    range1 --> c1
    range1 --> d1
    range1 --> e1
}

package "After Decommission (4 nodes)" {
    rectangle "Range (40, 60]" as range2
    rectangle "Node D\n(new primary)" as d2
    rectangle "Node E\n(replica)" as e2
    rectangle "Node A\n(new replica)" as a2

    range2 --> d2
    range2 --> e2
    range2 --> a2
}

package "Streaming Plan" {
    rectangle "Node C → Node A\nRange (40, 60] data\n\n(D and E already have replicas)" as stream
}

c1 ..> stream : decommission
stream ==> a2 : stream data

@enduml
```

### Decommission vs RemoveNode

| Operation | Use Case | Data Handling |
|-----------|----------|---------------|
| `decommission` | Node healthy, orderly removal | Streams data before leaving |
| `removenode` | Node dead/unrecoverable | No streaming; repair required after |
| `assassinate` | Force remove stuck node | Emergency only; data loss possible |

!!! warning "Decommission Requirements"
    Decommission can only proceed if the remaining cluster can satisfy the replication factor. Attempting to decommission when RF nodes would remain results in an error.

---

## Repair Streaming

Repair operations use streaming to synchronize data between replicas that have diverged.

### Repair Types and Streaming

| Repair Type | Streaming Behavior |
|-------------|-------------------|
| Full repair | Compare all data, stream differences |
| Incremental repair | Compare only unrepaired SSTables |
| Preview repair | Calculate differences only, no streaming |
| Subrange repair | Repair specific token ranges |

### Merkle Tree Exchange

Before streaming, repair uses Merkle trees to identify divergent ranges:

```plantuml
@startuml
skinparam backgroundColor transparent
title Merkle Tree Comparison for Repair

package "Replica A" {
    rectangle "1. Build Merkle Tree\nfrom local SSTables" as build1
    rectangle "Root: hash_A\n├─ L: hash_1\n└─ R: hash_2" as tree1
}

package "Replica B" {
    rectangle "1. Build Merkle Tree\nfrom local SSTables" as build2
    rectangle "Root: hash_B\n├─ L: hash_1\n└─ R: hash_3" as tree2
}

rectangle "2. Compare Trees\nhash_A ≠ hash_B\nhash_2 ≠ hash_3" as compare

rectangle "3. Stream Differing Range\nOnly R subtree data" as stream

tree1 --> compare
tree2 --> compare
compare --> stream

@enduml
```

### Streaming During Repair

```plantuml
@startuml
skinparam backgroundColor transparent
title Repair Streaming Flow

rectangle "1. Coordinator initiates repair\nfor keyspace/table" as init
rectangle "2. Each replica builds Merkle tree\nfor requested ranges" as build
rectangle "3. Trees exchanged and\ncompared pairwise" as exchange
rectangle "4. Differing ranges identified\n(may be small subset)" as diff
rectangle "5. Streaming sessions created\nfor each difference" as session
rectangle "6. Data streamed from authoritative\nreplica to divergent replica" as stream
rectangle "7. Received SSTables integrated\nrepair marked complete" as complete

init --> build
build --> exchange
exchange --> diff
diff --> session
session --> stream
stream --> complete

@enduml
```

### Incremental Repair Optimization

Incremental repair tracks which SSTables have been repaired, reducing future repair scope:

| SSTable State | Description | Repair Behavior |
|---------------|-------------|-----------------|
| Unrepaired | Never included in repair | Included in next repair |
| Pending | Currently being repaired | Excluded from new repairs |
| Repaired | Successfully repaired | Excluded from incremental repair |

---

## Hinted Handoff

Hinted handoff is a lightweight streaming mechanism that delivers missed writes to nodes that were temporarily unavailable.

### Hint Storage and Delivery

```plantuml
@startuml
skinparam backgroundColor transparent
title Hinted Handoff Mechanism

package "1. Write Arrives (Node B down)" {
    rectangle "Client Write\n(RF=3)" as write
    rectangle "Node A\n✓ Success" as a
    rectangle "Node B\n✗ Down" as b
    rectangle "Node C\n✓ Success" as c

    write --> a
    write ..> b
    write --> c
}

rectangle "2. Coordinator Stores Hint\nfor Node B" as hint

package "3. Node B Recovers" {
    rectangle "Node B\nBack Online" as recover
    rectangle "Hints Delivered\nto Node B" as deliver
}

b ..> hint : failure detected
hint --> deliver : gossip: B is UP
deliver --> recover

@enduml
```

### Hint Structure

Hints are stored locally on the coordinator node:

```plantuml
@startuml
skinparam backgroundColor transparent
title Hint Record Structure

rectangle "Hint Record" as hint {
    card "Target Host ID: uuid" as h1
    card "Hint ID: timeuuid" as h2
    card "Creation Time: timestamp" as h3
    card "Mutation: serialized write" as h4
    card "Message Version: protocol version" as h5
}

rectangle "Storage" as storage {
    card "Location: $CASSANDRA_HOME/data/hints/" as s1
    card "File Format: <host_id>-<timestamp>-<version>.hints" as s2
}

hint -[hidden]down-> storage

@enduml
```

### Hint Configuration

```yaml
# cassandra.yaml hint parameters

# Enable/disable hinted handoff
hinted_handoff_enabled: true

# Maximum time to store hints (default: 3 hours)
max_hint_window: 3h                    # 4.1+ (duration format)
# max_hint_window_in_ms: 10800000      # Pre-4.1

# Directory for hint files
hints_directory: /var/lib/cassandra/hints

# Hint delivery throttle per destination
hinted_handoff_throttle: 1024KiB       # 4.1+ (data size format)
# hinted_handoff_throttle_in_kb: 1024  # Pre-4.1

# Maximum hints delivery threads
max_hints_delivery_threads: 2

# Hint compression
hints_compression:
  - class_name: LZ4Compressor
```

| Parameter | Pre-4.1 | 4.1+ |
|-----------|---------|------|
| Hint window | `max_hint_window_in_ms` | `max_hint_window` (duration) |
| Delivery throttle | `hinted_handoff_throttle_in_kb` | `hinted_handoff_throttle` (data size) |
| Flush period | `hints_flush_period_in_ms` | `hints_flush_period` (duration) |

### Hint Delivery Streaming

Unlike full SSTable streaming used in bootstrap and repair, hint delivery uses a lighter-weight mutation replay mechanism. Hints are streamed as individual mutations rather than file segments.

```plantuml
@startuml
skinparam backgroundColor transparent
title Hint Delivery Streaming Flow

package "Hint Source (Coordinator)" {
    rectangle "1. Gossip Detects\nTarget Node UP" as gossip
    rectangle "2. HintsDispatcher\nSchedules Delivery" as dispatch
    rectangle "3. Read Hints from\nLocal Hint Files" as read
    rectangle "4. Apply Throttle\n(hinted_handoff_throttle_in_kb)" as throttle
}

package "Transfer" {
    rectangle "5. Send Mutation\nvia Messaging Service" as send
}

package "Hint Target (Recovered Node)" {
    rectangle "6. Receive Mutation" as receive
    rectangle "7. Apply to Memtable\n(normal write path)" as apply
    rectangle "8. Acknowledge\nReceipt" as ack
}

rectangle "9. Delete Hint\nfrom Source" as cleanup

gossip --> dispatch
dispatch --> read
read --> throttle
throttle --> send
send --> receive
receive --> apply
apply --> ack
ack ..> cleanup

@enduml
```

**Delivery mechanism details:**

| Aspect | Description |
|--------|-------------|
| **Transport** | Uses standard inter-node messaging (not dedicated streaming port) |
| **Serialization** | Hints deserialized and sent as mutation messages |
| **Ordering** | Delivered in timestamp order (oldest first) |
| **Batching** | Multiple hints may be batched per network round-trip |
| **Retries** | Failed deliveries retried with exponential backoff |

### Hint Streaming Parameters

The following parameters control hint delivery throughput and resource usage:

| Parameter (4.1+) | Parameter (Pre-4.1) | Default | Description |
|------------------|---------------------|---------|-------------|
| `hinted_handoff_throttle` | `hinted_handoff_throttle_in_kb` | 1024KiB | Max throughput per destination |
| `max_hints_delivery_threads` | `max_hints_delivery_threads` | 2 | Concurrent delivery threads |
| `hints_flush_period` | `hints_flush_period_in_ms` | 10s | How often hint buffers flush to disk |
| `max_hints_file_size` | `max_hints_file_size_in_mb` | 128MiB | Maximum size per hint file |

**Throttling calculation:**

```
Effective hint throughput = hinted_handoff_throttle × max_hints_delivery_threads

Example with defaults:
  1024 KiB/s × 2 threads = 2048 KiB/s = ~2 MiB/s total hint delivery capacity
```

```yaml
# cassandra.yaml - Hint delivery tuning (4.1+ syntax)

# Increase for faster hint delivery (impacts production traffic)
hinted_handoff_throttle: 2048KiB

# More threads for parallel delivery to multiple recovering nodes
max_hints_delivery_threads: 4

# Smaller files for more granular cleanup
max_hints_file_size: 64MiB
```

### Hint Delivery Process

| Phase | Operation |
|-------|-----------|
| **Detection** | Gossip announces target node UP |
| **Scheduling** | HintsDispatcher assigns delivery thread |
| **Reading** | Hints read from local hint files in timestamp order |
| **Throttling** | Delivery rate limited by `hinted_handoff_throttle` |
| **Streaming** | Mutations sent via messaging service |
| **Application** | Target node applies mutations to memtable |
| **Acknowledgment** | Target confirms receipt |
| **Cleanup** | Delivered hints deleted from source |

### Hint Delivery vs SSTable Streaming

| Characteristic | Hint Delivery | SSTable Streaming |
|----------------|---------------|-------------------|
| **Data unit** | Individual mutations | SSTable file segments |
| **Transport** | Messaging service | Dedicated streaming protocol |
| **Throughput** | KB/s (throttled) | MB/s to GB/s |
| **CPU usage** | Moderate (deserialization) | Low (zero-copy) or high (traditional) |
| **Use case** | Small data volumes, short outages | Large data volumes, topology changes |
| **Port** | `native_transport_port` / `storage_port` | `storage_port` |

!!! warning "Hint Window Limitations"
    Hints are only stored for `max_hint_window` duration (default: 3 hours). Nodes down longer than this window will not receive hints and require repair to restore consistency. For extended outages, full repair is necessary.

---

## Streaming Internals

### File Transfer Protocol

SSTable streaming operates on file segments:

```plantuml
@startuml
skinparam backgroundColor transparent
title SSTable File Transfer Protocol

package "Source Node" {
    rectangle "SSTable Components\n• Data.db\n• Index.db\n• Filter.db\n• Statistics.db\n• Summary.db\n• TOC.txt" as sstable
}

rectangle "FileMessage\n(segment)" as filemsg

package "Target Node" {
    rectangle "Receive Buffer" as buffer
    rectangle "Write to Disk" as disk

    buffer --> disk
}

rectangle "StreamReceived\n(acknowledgment)" as streamrecv

sstable ==> filemsg
filemsg ==> buffer
disk ..> streamrecv
streamrecv ..> sstable

@enduml
```

### Segment Size and Buffering

| Parameter | Default | Description |
|-----------|---------|-------------|
| Segment size | 64 KB | Chunk size for file transfer |
| Send buffer | 1 MB | Outbound buffering per session |
| Receive buffer | 4 MB | Inbound buffering per session |
| Max concurrent transfers | 1 per host | Parallelism limit |

### Compression

Streaming data is compressed in transit:

```plantuml
@startuml
skinparam backgroundColor transparent
title Streaming Compression Pipeline

rectangle "SSTable\nData" as data
rectangle "LZ4\nCompression" as compress
rectangle "Network\nTransfer" as network
rectangle "LZ4\nDecompression" as decompress
rectangle "Disk\nWrite" as disk

data --> compress
compress --> network
network --> decompress
decompress --> disk

note bottom of network
  Compression ratio: 2:1 to 10:1
  CPU overhead: ~10-20%
end note

@enduml
```

### Progress Tracking

Streaming progress is tracked at multiple granularities:

```bash
# View active streams
nodetool netstats

# Detailed streaming information
nodetool netstats -H

# Per-session progress
Mode: JOINING
    /10.0.1.2
        Receiving 15 files, 1.2 GB total. Already received 8 files, 650 MB
        /10.0.1.3
        Receiving 12 files, 980 MB total. Already received 12 files, 980 MB
```

### JMX Metrics

```
# Streaming metrics (JMX)
org.apache.cassandra.metrics:type=Streaming,name=TotalIncomingBytes
org.apache.cassandra.metrics:type=Streaming,name=TotalOutgoingBytes
org.apache.cassandra.metrics:type=Streaming,name=ActiveStreams
org.apache.cassandra.metrics:type=Streaming,name=StreamingTime
```

---

## Performance Considerations

### Network Impact

Streaming operations can saturate network capacity:

| Factor | Impact | Mitigation |
|--------|--------|------------|
| Bootstrap | Sustained high throughput | Schedule during low-traffic periods |
| Decommission | Sustained high throughput | Rate limit with `stream_throughput_outbound_megabits_per_sec` |
| Repair | Variable, depends on divergence | Use incremental repair |
| Hints | Lower throughput | Generally minimal impact |

### Disk I/O Impact

```plantuml
@startuml
skinparam backgroundColor transparent
title Streaming I/O Patterns

package "Source Node" {
    rectangle "• Sequential read from SSTable files\n• Minimal random I/O\n• May compete with normal reads" as src
}

package "Target Node" {
    rectangle "• Sequential write to new SSTables\n• Post-streaming compaction required\n• Temporary 2x space usage" as tgt
}

src ==> tgt : streaming

@enduml
```

### Memory Pressure

| Streaming Mode | Heap Usage | Recommendation |
|----------------|------------|----------------|
| Zero-copy | Minimal | Preferred when compatible |
| Traditional | Significant | Monitor GC during large operations |

### Throttling Configuration

```yaml
# Limit streaming to prevent impact on production workload

# Outbound throughput limit (Mb/s)
stream_throughput_outbound_megabits_per_sec: 200

# Inter-datacenter streaming limit
inter_dc_stream_throughput_outbound_megabits_per_sec: 25

# Compaction throughput (affects post-streaming compaction)
compaction_throughput_mb_per_sec: 64
```

---

## Operational Procedures

### Monitoring Streaming

```bash
# Active streams summary
nodetool netstats

# Streaming with progress
nodetool netstats -H

# Bootstrap progress
nodetool describecluster | grep -A5 "Bootstrapping"

# Repair progress
nodetool repair_admin list
```

### Troubleshooting

| Symptom | Possible Cause | Resolution |
|---------|----------------|------------|
| Streaming stuck | Network partition | Check connectivity between nodes |
| Slow streaming | Disk I/O saturation | Reduce throttle, check disk health |
| Streaming failures | Timeout | Increase `streaming_socket_timeout` (4.1+) or `streaming_socket_timeout_in_ms` (pre-4.1) |
| OOM during streaming | Traditional mode on large data | Enable zero-copy or increase heap |

### Recovery from Failed Streaming

```bash
# If bootstrap fails
# Option 1: Clear data and retry
sudo rm -rf /var/lib/cassandra/data/*
nodetool bootstrap resume

# Option 2: Wipe and start fresh
sudo rm -rf /var/lib/cassandra/*
# Edit cassandra.yaml: auto_bootstrap: true
# Restart node

# If decommission fails
nodetool decommission  # Retry

# If repair streaming fails
nodetool repair -pr keyspace  # Retry affected ranges
```

---

## Related Documentation

- **[Replica Synchronization](replica-synchronization.md)** - Anti-entropy repair details
- **[Consistency](consistency.md)** - Consistency levels and guarantees
- **[Gossip Protocol](../cluster-management/gossip.md)** - Cluster state dissemination
- **[Compaction](../storage-engine/compaction/index.md)** - Post-streaming compaction
