---
description: "Asynchronous connections in Cassandra drivers. Non-blocking I/O and request pipelining."
meta:
  - name: keywords
    content: "async connections, non-blocking, request pipelining, Cassandra driver"
---

# Asynchronous Connections

Cassandra drivers use asynchronous, non-blocking I/O to achieve high throughput with minimal resources. This architecture enables thousands of concurrent requests using a small number of connections.

---

## Traditional RDBMS Connection Model

### The Synchronous RPC Pattern

Traditional relational databases (PostgreSQL, MySQL, Oracle, SQL Server) use a synchronous, thread-per-connection model inherited from RPC (Remote Procedure Call) patterns:

```plantuml
@startuml
skinparam backgroundColor transparent
title Traditional RDBMS: Thread-per-Connection Model

skinparam rectangle {
    BackgroundColor #7B4B96
    FontColor white
    BorderColor #5A3670
    roundCorner 10
}

package "Application Server" as App #F9E5FF {
    rectangle "Thread 1\n(blocked)" as T1
    rectangle "Thread 2\n(blocked)" as T2
    rectangle "Thread 3\n(blocked)" as T3
    rectangle "Thread 4\n(blocked)" as T4
    rectangle "...\n(500+ threads)" as TN
}

package "Connection Pool" as Pool #F3DAFA {
    rectangle "Conn 1" as C1
    rectangle "Conn 2" as C2
    rectangle "Conn 3" as C3
    rectangle "Conn 4" as C4
    rectangle "..." as CN
}

package "Database Server" as DB #EED0F5 {
    rectangle "Worker 1" as W1
    rectangle "Worker 2" as W2
    rectangle "Worker 3" as W3
    rectangle "Worker 4" as W4
}

T1 --> C1
T2 --> C2
T3 --> C3
T4 --> C4

C1 --> W1
C2 --> W2
C3 --> W3
C4 --> W4

note bottom of App #FFCDD2
  Each thread blocked waiting
  for database response
  ~1MB stack per thread
end note

note bottom of DB #FFFDE7
  Server spawns worker
  process/thread per connection
end note
@enduml
```

In this model:

1. **One thread per request**: Each database query requires a dedicated application thread
2. **Thread blocks until response**: The thread cannot do other work while waiting
3. **One connection per active thread**: The connection is exclusively held during query execution
4. **Server-side resources**: Database creates a worker process/thread for each connection

### Problems with the Traditional Model

**Resource Exhaustion:**

| Resource | Consumption | Impact |
|----------|-------------|--------|
| Application threads | 1 per concurrent query | 500 queries = 500 threads = 500MB+ memory |
| TCP connections | 1 per thread | File descriptor limits, server connection limits |
| Database workers | 1 per connection | `max_connections` parameter limits concurrency |
| Context switches | 2 per request (app + DB) | CPU overhead scales with concurrency |

**Connection Pool Challenges:**

```
Pool size too small:
  - Threads block waiting for connections
  - Request queuing and timeouts
  - Underutilized server capacity

Pool size too large:
  - Memory wasted on idle connections
  - Database overwhelmed during bursts
  - Connection limits exhausted
```

**Stale Connection Problem:**

Traditional connection pools suffer from stale connections:

```plantuml
@startuml
skinparam backgroundColor transparent
title Stale Connection Detection

skinparam ActivityBackgroundColor #F9E5FF
skinparam ActivityBorderColor #7B4B96

start

:Application requests connection;

if (Connection in pool?) then (yes)
    if (Connection still valid?) then (unknown)
        :Send validation query;
        note right
          "SELECT 1" or similar
          Adds latency to every request
        end note
        if (Validation succeeds?) then (yes)
            :Use connection;
        else (no)
            :Discard connection;
            :Create new connection;
        endif
    endif
else (no)
    :Create new connection;
    note right
      TCP handshake
      TLS negotiation
      Authentication
      ~10-50ms overhead
    end note
endif

:Execute query;
:Return connection to pool;

stop
@enduml
```

Stale connections occur when:

- **Network interruption**: Firewall drops idle connection, load balancer timeout
- **Server restart**: Database recycled but client unaware
- **Idle timeout**: Connection exceeds server's `wait_timeout`
- **TCP keepalive failure**: Underlying socket becomes invalid

**Connection Recycling Overhead:**

| Operation | Typical Latency | Notes |
|-----------|-----------------|-------|
| TCP handshake | 0.5-1ms (same DC) | 3-way handshake |
| TLS negotiation | 2-5ms | Certificate exchange, key derivation |
| Authentication | 1-3ms | Credential validation |
| Session setup | 1-2ms | Set timezone, charset, schema |
| **Total** | **5-15ms** | Per new connection |

**Scaling Limitations:**

```
Traditional Scaling:
  1000 requests/sec @ 10ms latency = 10 connections needed
  10000 requests/sec @ 10ms latency = 100 connections needed
  100000 requests/sec @ 10ms latency = 1000 connections needed ← hits limits

Database limits:
  PostgreSQL: max_connections default 100
  MySQL: max_connections default 151
  Oracle: processes parameter limits

Application limits:
  Thread pool sizing
  Memory for thread stacks
  Context switch overhead
```

!!! danger "Connection Explosion Under Load"
    During traffic spikes, applications often exhaust connection pools. New connection creation adds latency, and if the database hits `max_connections`, requests fail entirely. This creates a cascading failure pattern where increased load leads to decreased capacity.

---

## Cassandra's Asynchronous Model

### Stream Multiplexing Architecture

Cassandra drivers use a fundamentally different approach: multiplexed asynchronous connections with stream IDs:

```plantuml
@startuml
skinparam backgroundColor transparent
title Cassandra: Stream Multiplexing Model

skinparam rectangle {
    BackgroundColor #7B4B96
    FontColor white
    BorderColor #5A3670
    roundCorner 10
}

package "Application Server" as App #E8F5E9 {
    rectangle "Event Loop\n(1-2 threads)" as EL
    rectangle "Request Queue" as RQ
}

package "Multiplexed Connection" as Conn #F9E5FF {
    rectangle "Stream 1" as S1
    rectangle "Stream 2" as S2
    rectangle "Stream 3" as S3
    rectangle "...\nStream 32768" as SN
}

package "Cassandra Node" as Cass #F3DAFA {
    rectangle "Native Transport\n(shared thread pool)" as NT
}

RQ --> EL
EL --> S1
EL --> S2
EL --> S3
EL --> SN

S1 --> NT
S2 --> NT
S3 --> NT
SN --> NT

note bottom of App #E8F5E9
  Single connection handles
  thousands of concurrent requests
  No thread-per-request
end note

note bottom of Conn #FFFDE7
  32,768 streams per connection
  Requests identified by stream ID
  Out-of-order responses
end note
@enduml
```

**Key Differences:**

| Aspect | Traditional RDBMS | Cassandra |
|--------|-------------------|-----------|
| Connection utilization | 1 query at a time | 32,768 concurrent queries |
| Threads required | 1 per query | 1-2 for all I/O |
| Connection count | 100s needed | 2-8 per node sufficient |
| Response ordering | Sequential | Multiplexed (any order) |
| Memory per connection | ~1MB (thread) | ~64KB (buffers) |
| New connection cost | Paid frequently | Paid rarely (persistent) |

### Why This Works for Cassandra

1. **No server-side session state**: Unlike RDBMS, Cassandra connections have no transaction context, cursors, or prepared statement binding that requires connection affinity

2. **Protocol-level multiplexing**: The CQL binary protocol includes stream IDs (0-32767), allowing response matching without connection-per-request

3. **Stateless request handling**: Each request contains all necessary context (consistency level, timestamp, etc.), enabling any server thread to handle any request

4. **Designed for distribution**: Cassandra expects many nodes, so minimizing per-node connection overhead is essential

### Asynchronous I/O Benefits

Traditional synchronous model:
```
Thread 1: send request → [blocked waiting 5ms] → receive response → process
Thread 2: send request → [blocked waiting 5ms] → receive response → process
Thread 3: send request → [blocked waiting 5ms] → receive response → process
```

Cassandra asynchronous model:
```
Event Loop: send Q1 → send Q2 → send Q3 → send Q4 → send Q5 →
            receive R3 → receive R1 → receive R5 → receive R2 → receive R4
```

| Aspect | Synchronous | Asynchronous |
|--------|-------------|--------------|
| Threads per request | 1 | 0 (shared) |
| Memory per connection | ~1MB (thread stack) | ~64KB (buffers) |
| Context switches | Per request | Per I/O event |
| Concurrent requests | Limited by threads | Limited by protocol (32K) |
| Latency overhead | Thread scheduling | Minimal |

!!! tip "Connection Efficiency"
    A single Cassandra connection can handle the same throughput that would require 100+ PostgreSQL connections. For a 9-node cluster, 8 connections per node (72 total) can sustain hundreds of thousands of requests per second.

---

## Connection Architecture

### Connection Components

```plantuml
@startuml
skinparam backgroundColor transparent
title Driver Connection Components

skinparam rectangle {
    BackgroundColor #7B4B96
    FontColor white
    BorderColor #5A3670
    roundCorner 10
}

package "Application" as AppPkg #E8F5E9 {
    rectangle "Application Code" as App
}

package "Driver" as DrvPkg #F9E5FF {
    rectangle "Request Queue" as RQ
    rectangle "Response Handler" as RH
    rectangle "Event Loop" as EL

    package "Connection" as ConnPkg #F3DAFA {
        rectangle "Stream Manager" as SM
        rectangle "Frame Codec" as FC
        rectangle "Write Buffer" as WB
        rectangle "Read Buffer" as RB
    }
}

package "Network" as NetPkg #EED0F5 {
    rectangle "TCP Socket" as Net
}

App -down-> RQ : 1. submit request
RQ -down-> SM : 2. allocate stream
SM -down-> FC : 3. encode frame
FC -down-> WB : 4. queue write
EL -right-> WB : 5. flush
WB -down-> Net : 6. TCP write
Net -up-> RB : 7. TCP read
EL -right-> RB : 8. read events
RB -up-> FC : 9. decode frame
FC -up-> SM : 10. match stream
SM -up-> RH : 11. complete future
RH -up-> App : 12. result
@enduml
```

### Event Loop

The event loop is the core of asynchronous I/O:

1. **Selector/Epoll** - Monitors sockets for read/write readiness
2. **Event Dispatch** - Routes I/O events to handlers
3. **Task Execution** - Runs callbacks and completions

Most drivers use platform-native I/O:
- Linux: epoll
- macOS: kqueue
- Windows: IOCP

### Non-Blocking Sockets

Connections use non-blocking TCP sockets:

```
Socket Configuration:
  - TCP_NODELAY: Disable Nagle's algorithm (reduce latency)
  - SO_KEEPALIVE: Detect dead connections
  - Non-blocking mode: Never block on read/write
```

---

## Stream Multiplexing

### Stream Allocation

The CQL protocol supports up to 32,768 concurrent streams per connection (protocol v3+). Stream allocation:

```plantuml
@startuml
skinparam backgroundColor transparent

participant "Application" as App
participant "Stream Manager" as SM
participant "Connection" as C
participant "Server" as S

App -> SM: allocate stream
SM --> App: stream ID 42
App -> C: send(stream=42, query)
C -> S: frame(stream=42)
S --> C: frame(stream=42)
C -> SM: response(stream=42)
SM -> App: complete future
SM -> SM: release stream 42

@enduml
```

### Stream Management Strategies

**Sequential Allocation:**
```
Streams: 1, 2, 3, 4, ... (wrap at max)
Pros: Simple, predictable
Cons: Head-of-line if stream stuck
```

**Pooled Allocation:**
```
Free list: [5, 12, 7, 23, ...]
Allocate: pop from list
Release: push to list
Pros: Fast allocation, no fragmentation
```

### In-Flight Request Limits

Drivers limit concurrent requests per connection:

| Configuration | Typical Value | Purpose |
|---------------|---------------|---------|
| Max requests per connection | 1024-2048 | Prevent overload |
| High watermark | 80% of max | Trigger backpressure |
| Low watermark | 50% of max | Resume after backpressure |

!!! note "Backpressure Behavior"
    When the high watermark is reached, new requests are queued or rejected until in-flight requests drop below the low watermark. This prevents overwhelming individual connections.

---

## Connection Pooling

### Pool Architecture

Each node maintains a connection pool:

```plantuml
@startuml
skinparam backgroundColor transparent

package "Connection Pool (Node A)" {
    [Connection 1\n847 in-flight] as C1
    [Connection 2\n923 in-flight] as C2
    [Connection 3\n156 in-flight] as C3
}

package "Connection Pool (Node B)" {
    [Connection 4\n412 in-flight] as C4
    [Connection 5\n678 in-flight] as C5
}

[Request Router] as RR

RR --> C3 : route (least loaded)
RR --> C4 : route (least loaded)

@enduml
```

### Pool Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| Core connections | Minimum maintained connections | 1 |
| Max connections | Maximum connections to create | 8 (local), 2 (remote) |
| Max requests/connection | Concurrent requests limit | 1024 |

!!! tip "Remote Datacenter Connections"
    Remote datacenter pools typically use fewer connections (1-2) since cross-DC requests should be rare in normal operation. This conserves resources while maintaining fallback capability.

### Connection Selection

When routing a request to a pool:

1. **Least-loaded selection** - Choose connection with fewest in-flight requests
2. **Round-robin** - Cycle through connections (simpler)
3. **Random** - Random selection (load spreads naturally)

### Pool Scaling

Pools grow and shrink based on demand:

**Scale Up:**
```
if (all_connections_at_max_requests && pool_size < max_connections):
    create_new_connection()
```

**Scale Down:**
```
if (connection_idle_time > threshold && pool_size > core_connections):
    close_idle_connection()
```

---

## Request Lifecycle

### Submission

```python
# Conceptual flow (not actual API)
async def execute(query):
    # 1. Select node via load balancer
    node = load_balancer.select(query)

    # 2. Get connection from pool
    connection = await pool.acquire(node)

    # 3. Allocate stream
    stream_id = connection.allocate_stream()

    # 4. Create response future
    future = Future()
    connection.register(stream_id, future)

    # 5. Encode and send
    frame = encode_query(stream_id, query)
    connection.write(frame)

    # 6. Return future (completes when response arrives)
    return future
```

### Response Handling

```python
# Conceptual flow
def on_data_received(connection, data):
    # 1. Decode frame
    frame = decode_frame(data)

    # 2. Find waiting future
    future = connection.get_pending(frame.stream_id)

    # 3. Release stream
    connection.release_stream(frame.stream_id)

    # 4. Complete future
    if frame.is_error():
        future.set_exception(decode_error(frame))
    else:
        future.set_result(decode_result(frame))
```

### Pipelining

Multiple requests can be sent before receiving responses:

```
Time →
Client: [Q1][Q2][Q3][Q4]----------------→
Server: ------[R2][R1][R4][R3]----------→

Without pipelining (would require):
Client: [Q1]----[Q2]----[Q3]----[Q4]---→
Server: ----[R1]----[R2]----[R3]----[R4]→
```

Pipelining benefits:
- Better network utilization
- Reduced per-request latency
- Amortized TCP overhead

---

## Backpressure

### Request-Side Backpressure

When the system is overloaded, drivers apply backpressure:

```plantuml
@startuml
skinparam backgroundColor transparent

start
:Submit request;
if (in_flight < high_watermark?) then (yes)
    :Send immediately;
else (no)
    if (in_flight < max_requests?) then (yes)
        :Queue request;
        :Wait for capacity;
    else (no)
        :Reject request;
        :Throw exception;
    endif
endif
stop

@enduml
```

### Response-Side Backpressure

If the application cannot process responses fast enough:

1. **Buffer responses** - Accumulate in memory (risky)
2. **Pause reading** - Stop reading from socket (TCP backpressure)
3. **Drop connection** - Last resort

### Backpressure Signals

| Signal | Meaning | Action |
|--------|---------|--------|
| Queue full | Too many pending requests | Slow down submissions |
| High in-flight | Approaching connection limit | Consider more connections |
| Read buffer full | Processing too slow | Increase consumer capacity |

!!! warning "Ignoring Backpressure"
    Applications that ignore backpressure signals risk memory exhaustion, request timeouts, and cascading failures. Design applications to handle BusyConnectionException or equivalent errors gracefully.

---

## Connection Health

### Heartbeats

Drivers send periodic heartbeats to detect dead connections:

```
Heartbeat interval: 30 seconds (typical)
Mechanism: OPTIONS request or protocol-level ping
Timeout: If no response, mark connection unhealthy
```

### Health Checks

| Check | Frequency | Failure Action |
|-------|-----------|----------------|
| Heartbeat | 30s | Mark unhealthy, reconnect |
| Read timeout | Per request | Retry on different connection |
| Write failure | Immediate | Close connection |
| Protocol error | Immediate | Close connection |

### Reconnection

When connections fail:

1. **Mark connection dead** - Remove from active pool
2. **Schedule reconnection** - Exponential backoff
3. **Notify load balancer** - May affect node status

```
Reconnection schedule:
  Attempt 1: immediate
  Attempt 2: 1 second
  Attempt 3: 2 seconds
  Attempt 4: 4 seconds
  ...
  Max delay: 60 seconds
```

---

## Memory Management

### Buffer Allocation

Efficient buffer management is critical for performance:

**Read Buffers:**
```
Per-connection read buffer: 64KB typical
Allocation: Pre-allocated or pooled
Growth: Expand for large frames
```

**Write Buffers:**
```
Per-connection write buffer: 64KB typical
Coalescing: Batch small writes
Flushing: On buffer full or explicit flush
```

### Object Pooling

Drivers pool frequently allocated objects:

| Object | Pooling Benefit |
|--------|-----------------|
| Frames | Avoid allocation per request |
| Byte buffers | Reduce GC pressure |
| Futures/Promises | Reuse completion objects |
| Row objects | Minimize allocation during iteration |

### Memory Budgeting

Total driver memory usage:

```
Memory = (connections × connection_overhead) +
         (in_flight_requests × request_overhead) +
         (result_sets × result_overhead)

Example:
  50 connections × 128KB = 6.4MB
  5000 in-flight × 2KB = 10MB
  Result buffers = variable
  Total: ~20-50MB typical
```

---

## Threading Models

### Single-Threaded Event Loop

Some drivers use a single I/O thread:

```
Pros: Simple, no synchronization needed
Cons: CPU-bound work blocks I/O
Pattern: Node.js driver
```

### Thread Pool

Others use thread pools:

```
I/O threads: Handle network operations
Worker threads: Execute callbacks
Pros: Better CPU utilization
Cons: Synchronization complexity
Pattern: Java driver
```

### Hybrid

Modern drivers often combine approaches:

```
I/O threads: 1 per N connections
Callback threads: Configurable pool
User code: Application threads
```

---

## Performance Characteristics

### Latency Components

| Component | Typical Range | Notes |
|-----------|---------------|-------|
| Stream allocation | <1 μs | Lock-free in good implementations |
| Frame encoding | 1-10 μs | Depends on query complexity |
| Buffer copy | 1-5 μs | Zero-copy when possible |
| Syscall overhead | 1-10 μs | Batching amortizes |
| Network latency | 100 μs - 10 ms | Same DC vs cross-DC |

### Throughput Factors

Maximum throughput depends on:

```
Max throughput = connections × streams_per_connection × (1 / avg_latency)

Example:
  8 connections × 1024 streams × (1 / 0.005s) = 1.6M requests/sec theoretical

Practical limits:
  - Server capacity
  - Network bandwidth
  - Serialization CPU
  - GC pauses
```

### Optimization Techniques

| Technique | Benefit |
|-----------|---------|
| Connection warming | Avoid cold start latency |
| Request coalescing | Reduce syscalls |
| Zero-copy buffers | Minimize CPU |
| Prepared statements | Reduce encoding |

---

## Related Documentation

- **[CQL Protocol](cql-protocol.md)** - Wire protocol details
- **[Load Balancing](load-balancing.md)** - Node selection strategies
- **[Failure Handling](failure-handling.md)** - Error recovery
