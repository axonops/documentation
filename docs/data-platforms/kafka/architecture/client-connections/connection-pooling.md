---
title: "Kafka Connection Pooling"
description: "Apache Kafka connection pooling architecture. NetworkClient, Selector, connection management, and multiplexing."
meta:
  - name: keywords
    content: "Kafka connection pooling, connection management, max.connections, connection reuse"
---

# Kafka Connection Pooling

Kafka clients maintain a pool of TCP connections to brokers, with sophisticated management for connection lifecycle, multiplexing, and failure recovery. Understanding connection pooling is essential for optimizing client performance and resource utilization.

## Connection Architecture

```plantuml
@startuml

skinparam backgroundColor transparent

package "KafkaProducer" {
    rectangle "Application Threads" as AppThreads {
        rectangle "Thread 1" as T1
        rectangle "Thread 2" as T2
        rectangle "Thread N" as TN
    }

    rectangle "Sender Thread" as Sender {
        rectangle "NetworkClient" as NC {
            rectangle "ClusterConnectionStates" as CCS
            rectangle "InFlightRequests" as IFR
        }
        rectangle "Selector" as Sel {
            rectangle "KafkaChannel\n(Broker 1)" as KC1
            rectangle "KafkaChannel\n(Broker 2)" as KC2
            rectangle "KafkaChannel\n(Broker 3)" as KC3
        }
    }
}

rectangle "Kafka Cluster" {
    node "Broker 1" as B1
    node "Broker 2" as B2
    node "Broker 3" as B3
}

T1 --> NC : send()
T2 --> NC : send()
TN --> NC : send()

NC --> CCS : connection state
NC --> IFR : track requests
NC --> Sel : poll()

KC1 <--> B1 : TCP
KC2 <--> B2 : TCP
KC3 <--> B3 : TCP

@enduml
```

---

## Connection Model

### One Connection Per Broker

Kafka clients maintain exactly one TCP connection per broker they need to communicate with. This differs from connection pooling in databases:

| Aspect | Kafka | Traditional DB Pools |
|--------|-------|---------------------|
| **Connections per server** | 1 | Multiple |
| **Connection reuse** | Multiplexed | Sequential |
| **Request ordering** | Maintained | Not guaranteed |
| **Resource scaling** | Linear with brokers | Configurable |

### Connection Multiplexing

Multiple requests share a single connection through stream multiplexing:

```plantuml
@startuml

skinparam backgroundColor transparent

participant "App Thread 1" as T1
participant "App Thread 2" as T2
participant "NetworkClient" as NC
participant "Connection\n(Broker 1)" as Conn
participant "Broker 1" as B1

T1 -> NC : send(ProduceRequest, corrId=1)
activate NC
NC -> Conn : queue(corrId=1)

T2 -> NC : send(MetadataRequest, corrId=2)
NC -> Conn : queue(corrId=2)

Conn -> B1 : ProduceRequest(corrId=1)
Conn -> B1 : MetadataRequest(corrId=2)

B1 --> Conn : MetadataResponse(corrId=2)
note right: Responses may arrive\nout of order
B1 --> Conn : ProduceResponse(corrId=1)

Conn --> NC : response(corrId=2)
NC --> T2 : MetadataResponse

Conn --> NC : response(corrId=1)
NC --> T1 : ProduceResponse
deactivate NC

@enduml
```

---

## NetworkClient Component

The `NetworkClient` is the core connection management component in Kafka clients.

### Responsibilities

| Function | Description |
|----------|-------------|
| **Connection Management** | Establish, maintain, and close connections |
| **Request Dispatch** | Route requests to appropriate broker connections |
| **Response Correlation** | Match responses to pending requests |
| **Metadata Management** | Track cluster topology changes |
| **Backpressure** | Limit in-flight requests per connection |

### Internal Structure

```plantuml
@startuml

skinparam backgroundColor transparent

package "NetworkClient" {
    rectangle "ClusterConnectionStates" as CCS {
        rectangle "Node 1: READY" as N1
        rectangle "Node 2: CONNECTING" as N2
        rectangle "Node 3: DISCONNECTED" as N3
    }

    rectangle "InFlightRequests" as IFR {
        rectangle "Queue per Node" as QPM
        rectangle "Timeout Tracking" as TT
    }

    rectangle "MetadataUpdater" as MU

    rectangle "Selector" as Sel
}

CCS --> Sel : manage channels
IFR --> Sel : pending sends
MU --> Sel : metadata requests

@enduml
```

### Connection States

```plantuml
@startuml

skinparam backgroundColor transparent

state "DISCONNECTED" as Disconnected
state "CONNECTING" as Connecting
state "CHECKING_API_VERSIONS" as Checking
state "AUTHENTICATING" as Authenticating
state "READY" as Ready

[*] --> Disconnected

Disconnected --> Connecting : initiateConnect()
Connecting --> Checking : TCP connected
Checking --> Authenticating : versions received
Checking --> Ready : no auth required
Authenticating --> Ready : auth success
Authenticating --> Disconnected : auth failure

Ready --> Disconnected : connection closed
Connecting --> Disconnected : timeout/failure
Checking --> Disconnected : timeout/failure

Ready --> Ready : send/receive

@enduml
```

---

## Selector and KafkaChannel

### Java NIO Selector

Kafka uses Java NIO for non-blocking I/O:

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Selector" {
    rectangle "SelectionKeys" as Keys {
        rectangle "Key 1\n(OP_READ)" as K1
        rectangle "Key 2\n(OP_WRITE)" as K2
        rectangle "Key 3\n(OP_CONNECT)" as K3
    }

    rectangle "Completed Sends" as CS
    rectangle "Completed Receives" as CR
    rectangle "Disconnected" as Disc
}

rectangle "poll() Loop" as Poll {
    rectangle "1. select(timeout)" as Step1
    rectangle "2. Process ready keys" as Step2
    rectangle "3. Handle connects" as Step3
    rectangle "4. Handle reads" as Step4
    rectangle "5. Handle writes" as Step5
}

Poll --> Keys : monitor
Keys --> CS : send complete
Keys --> CR : receive complete
Keys --> Disc : connection lost

@enduml
```

### KafkaChannel Structure

Each broker connection is wrapped in a `KafkaChannel`:

```java
// Conceptual KafkaChannel structure
public class KafkaChannel {
    private final String id;                    // Node ID
    private final TransportLayer transportLayer; // TCP/SSL
    private final Authenticator authenticator;   // SASL auth
    private final int maxReceiveSize;           // Max message size

    private NetworkReceive receive;             // Current incoming message
    private NetworkSend send;                   // Current outgoing message
    private ChannelState state;                 // Connection state

    // Buffered operations
    private final Deque<NetworkSend> sendQueue;
}
```

### Transport Layers

| Layer | Class | Protocol |
|-------|-------|----------|
| **Plaintext** | `PlaintextTransportLayer` | TCP |
| **SSL** | `SslTransportLayer` | TLS |
| **SASL Plaintext** | `SaslChannelBuilder` | TCP + SASL |
| **SASL SSL** | `SaslChannelBuilder` | TLS + SASL |

---

## Connection Configuration

### Connection Timing

| Configuration | Default | Description |
|--------------|---------|-------------|
| `reconnect.backoff.ms` | 50 | Initial reconnection backoff |
| `reconnect.backoff.max.ms` | 1000 | Maximum reconnection backoff |
| `socket.connection.setup.timeout.ms` | 10000 | TCP connection timeout |
| `socket.connection.setup.timeout.max.ms` | 30000 | Maximum connection timeout |
| `connections.max.idle.ms` | 540000 (9 min) | Close idle connections |

### Backoff Strategy

```plantuml
@startuml

skinparam backgroundColor transparent

title Exponential Backoff for Reconnection

start

:Connection Failed;
:backoff = reconnect.backoff.ms;

repeat
    :Wait(backoff);
    :Attempt Connection;

    if (Connected?) then (yes)
        :Reset backoff;
        stop
    else (no)
        :backoff = min(backoff * 2, max_backoff);
    endif

repeat while (More attempts?) is (yes)

:Connection exhausted;
stop

@enduml
```

### Buffer Configuration

| Configuration | Default | Description |
|--------------|---------|-------------|
| `send.buffer.bytes` | 131072 (128KB) | TCP send buffer (SO_SNDBUF) |
| `receive.buffer.bytes` | 65536 (64KB) | TCP receive buffer (SO_RCVBUF) |
| `request.timeout.ms` | 30000 | Request completion timeout |

!!! tip "Buffer Sizing"
    For high-latency networks, increase buffer sizes to allow more data in flight. The bandwidth-delay product formula can guide sizing: `buffer_size = bandwidth × RTT`.

---

## In-Flight Request Management

### Request Tracking

```plantuml
@startuml

skinparam backgroundColor transparent

package "InFlightRequests" {
    rectangle "Per-Node Queues" as Queues {
        rectangle "Node 1 Queue" as Q1 {
            rectangle "Req 101" as R1
            rectangle "Req 102" as R2
        }
        rectangle "Node 2 Queue" as Q2 {
            rectangle "Req 201" as R3
        }
        rectangle "Node 3 Queue" as Q3
    }
}

note bottom of Q1
  max.in.flight.requests.per.connection = 5
  Current: 2 in-flight
  Can send: 3 more
end note

@enduml
```

### Configuration

```properties
# Maximum concurrent requests per connection
max.in.flight.requests.per.connection=5

# For idempotent producers (ordering guaranteed)
max.in.flight.requests.per.connection=5
enable.idempotence=true

# For strict ordering without idempotence (legacy)
max.in.flight.requests.per.connection=1
```

### Ordering Guarantees

| Configuration | Ordering | Throughput |
|--------------|----------|------------|
| `max.in.flight=1` | Strict | Lower |
| `max.in.flight=5, idempotent=true` | Guaranteed | Higher |
| `max.in.flight=5, idempotent=false` | May reorder on retry | Highest |

---

## Connection Lifecycle

### Producer Connection Flow

```plantuml
@startuml

skinparam backgroundColor transparent

participant "Producer" as P
participant "NetworkClient" as NC
participant "MetadataUpdater" as MU
participant "Selector" as Sel
participant "Broker" as B

== Initialization ==
P -> NC : new NetworkClient()
NC -> MU : new DefaultMetadataUpdater()

== First Send ==
P -> NC : send(ProduceRequest)
NC -> MU : fetch metadata
MU -> Sel : initiateConnect(bootstrap)
Sel -> B : TCP SYN

B --> Sel : TCP SYN-ACK
Sel --> NC : connected

NC -> Sel : send(ApiVersionsRequest)
Sel -> B : ApiVersionsRequest
B --> Sel : ApiVersionsResponse
Sel --> NC : versions received

NC -> Sel : send(MetadataRequest)
Sel -> B : MetadataRequest
B --> Sel : MetadataResponse
Sel --> MU : metadata updated

NC -> Sel : send(ProduceRequest)
Sel -> B : ProduceRequest
B --> Sel : ProduceResponse
Sel --> NC : response
NC --> P : result

@enduml
```

### Consumer Connection Flow

```plantuml
@startuml

skinparam backgroundColor transparent

participant "Consumer" as C
participant "ConsumerNetworkClient" as CNC
participant "Coordinator" as Coord
participant "Fetcher" as F
participant "Broker" as B
participant "Group Coordinator" as GC

== Group Join ==
C -> CNC : subscribe(topics)
CNC -> B : FindCoordinatorRequest
B --> CNC : coordinator = GC

CNC -> GC : JoinGroupRequest
GC --> CNC : JoinGroupResponse (leader/follower)

CNC -> GC : SyncGroupRequest
GC --> CNC : SyncGroupResponse (assignment)

== Steady State ==
loop poll()
    C -> CNC : poll()

    par Heartbeat
        CNC -> GC : HeartbeatRequest
        GC --> CNC : HeartbeatResponse
    and Fetch
        CNC -> F : fetch()
        F -> B : FetchRequest
        B --> F : FetchResponse
        F --> CNC : records
    end

    CNC --> C : ConsumerRecords
end

@enduml
```

---

## Connection Health Monitoring

### Health Check Mechanisms

| Mechanism | Frequency | Purpose |
|-----------|-----------|---------|
| **TCP Keepalive** | OS-dependent | Detect dead connections |
| **Heartbeat** | `heartbeat.interval.ms` | Consumer liveness |
| **Metadata Refresh** | `metadata.max.age.ms` | Topology freshness |
| **Request Timeout** | Per-request | Detect hung requests |

### Connection Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `connection-count` | Active connections | Unexpected changes |
| `connection-creation-rate` | New connections/sec | > 10/min |
| `connection-close-rate` | Closed connections/sec | > 10/min |
| `failed-connection-rate` | Failed connections/sec | > 0 |
| `successful-authentication-rate` | Auth success/sec | < expected |
| `failed-authentication-rate` | Auth failures/sec | > 0 |

### Diagnosing Connection Issues

```plantuml
@startuml

skinparam backgroundColor transparent

start

:Connection Issue Detected;

if (Connection refused?) then (yes)
    :Check broker status;
    :Verify port configuration;
    :Check firewall rules;
else (no)
    if (Connection timeout?) then (yes)
        :Check network connectivity;
        :Verify DNS resolution;
        :Check load balancer;
    else (no)
        if (Auth failure?) then (yes)
            :Verify credentials;
            :Check SASL config;
            :Verify ACLs;
        else (no)
            if (SSL error?) then (yes)
                :Verify certificates;
                :Check trust store;
                :Verify hostname;
            else (no)
                :Check broker logs;
                :Enable debug logging;
            endif
        endif
    endif
endif

stop

@enduml
```

---

## Multi-Threaded Considerations

### Thread Safety

| Component | Thread Safe | Notes |
|-----------|:-----------:|-------|
| `KafkaProducer` | ✅ | Safe to share across threads |
| `KafkaConsumer` | ❌ | One consumer per thread |
| `NetworkClient` | ❌ | Used by single I/O thread |
| `Selector` | ❌ | Used by single I/O thread |

### Producer Threading Model

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "KafkaProducer (Thread-Safe)" as KP {
    rectangle "RecordAccumulator" as RA {
        rectangle "Thread-Safe\nPartition Queues" as PQ
    }

    rectangle "Sender Thread\n(Single)" as ST {
        rectangle "NetworkClient" as NC
        rectangle "Selector" as Sel
    }
}

rectangle "Application Threads" as AT {
    rectangle "Thread 1" as T1
    rectangle "Thread 2" as T2
    rectangle "Thread N" as TN
}

T1 --> RA : send()
T2 --> RA : send()
TN --> RA : send()

ST --> RA : drain()
ST --> NC : send batches

note right of ST
  Single thread handles
  all network I/O
end note

@enduml
```

### Consumer Threading Model

```plantuml
@startuml

skinparam backgroundColor transparent

rectangle "Option 1: One Consumer Per Thread" as Opt1 {
    rectangle "Thread 1" as T1a
    rectangle "Consumer 1" as C1a
    rectangle "Thread 2" as T1b
    rectangle "Consumer 2" as C1b

    T1a --> C1a
    T1b --> C1b
}

rectangle "Option 2: Consumer + Worker Pool" as Opt2 {
    rectangle "Consumer Thread" as CT
    rectangle "Consumer" as C2
    rectangle "Worker Pool" as WP {
        rectangle "Worker 1" as W1
        rectangle "Worker 2" as W2
        rectangle "Worker N" as WN
    }

    CT --> C2 : poll()
    C2 --> WP : dispatch records
}

@enduml
```

---

## Resource Management

### Connection Cleanup

```java
// Proper producer cleanup
try {
    producer.flush();  // Send pending records
    producer.close(Duration.ofSeconds(30));  // Graceful shutdown
} catch (Exception e) {
    producer.close(Duration.ZERO);  // Force close on error
}

// Proper consumer cleanup
try {
    consumer.commitSync();  // Commit final offsets
    consumer.close(Duration.ofSeconds(30));
} catch (WakeupException e) {
    // Expected on shutdown
} finally {
    consumer.close();
}
```

### File Descriptor Limits

Each connection consumes file descriptors:

| Resource | FDs per Connection | Typical Client |
|----------|-------------------|----------------|
| TCP Socket | 1 | - |
| SSL Context | 1-2 | If TLS enabled |
| Total per Broker | 1-3 | - |
| 10-Broker Cluster | 10-30 | Per client |

!!! warning "FD Limits"
    Monitor file descriptor usage with `lsof` or `/proc/<pid>/fd`. The default Linux limit of 1024 FDs per process may be insufficient for applications with many Kafka clients.

---

## Performance Optimization

### Connection Reuse

Maximize connection efficiency:

```properties
# Keep connections alive longer
connections.max.idle.ms=900000  # 15 minutes

# Increase in-flight for throughput
max.in.flight.requests.per.connection=5

# Larger buffers for high-bandwidth
send.buffer.bytes=262144
receive.buffer.bytes=262144
```

### Reducing Connection Churn

| Issue | Solution |
|-------|----------|
| Frequent reconnects | Increase `connections.max.idle.ms` |
| Auth failures | Verify credentials, check token expiry |
| Broker restarts | Implement graceful client handling |
| Load balancer timeouts | Configure LB to match idle timeout |

---

## Related Documentation

- [Kafka Protocol](kafka-protocol.md) - Wire protocol details
- [Authentication](authentication.md) - Security protocols
- [Metadata Management](metadata-management.md) - Cluster discovery
- [Failure Handling](failure-handling.md) - Error recovery
