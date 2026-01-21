---
title: "Cassandra Drivers"
description: "Cassandra drivers overview. Official drivers for Java, Python, Node.js, Go, and other languages."
meta:
  - name: keywords
    content: "Cassandra drivers, Java driver, Python driver, DataStax drivers"
search:
  boost: 3
---

# Cassandra Drivers

Cassandra drivers provide the interface between applications and the Cassandra cluster. Unlike traditional database connectors, Cassandra drivers are topology-aware—they maintain knowledge of all nodes in the cluster and make intelligent decisions about request routing, connection management, and failure handling.

---

## Architecture Overview

### Asynchronous Protocol

Cassandra uses the CQL Native Protocol, a binary protocol designed for high-throughput asynchronous communication. Key characteristics:

| Feature | Description |
|---------|-------------|
| Multiplexed connections | Multiple concurrent requests share a single TCP connection |
| Stream IDs | Each request tagged with ID; responses matched asynchronously |
| Non-blocking I/O | Driver does not block threads waiting for responses |
| Configurable concurrency | Limit in-flight requests per connection (default typically 1024-2048) |

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam sequenceArrowThickness 1
skinparam sequenceParticipantBorderColor #666666
skinparam sequenceParticipantBackgroundColor #E8E8E8
skinparam sequenceLifeLineBorderColor #999999

participant "Application" as App
participant "Driver" as Drv
participant "Cassandra Node" as Node

App -> Drv: Request A
Drv -> Node: [Stream 1] Request A
App -> Drv: Request B
Drv -> Node: [Stream 2] Request B
App -> Drv: Request C
Drv -> Node: [Stream 3] Request C

Node --> Drv: [Stream 2] Response B
Drv --> App: Response B
Node --> Drv: [Stream 1] Response A
Drv --> App: Response A
Node --> Drv: [Stream 3] Response C
Drv --> App: Response C

note right of Node: Responses return in\ncompletion order,\nnot request order
@enduml
```

Responses return in completion order, not request order. A single TCP connection handles thousands of concurrent requests.

This design allows a single connection to handle thousands of concurrent requests without thread-per-request overhead. Applications benefit from:

- **Efficient resource usage** — Few connections support high throughput
- **Natural back-pressure** — When stream IDs exhaust, driver queues or rejects requests
- **Simplified connection pooling** — Fewer connections to manage and monitor

### Cluster Metadata

The driver maintains a live view of cluster topology:

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Driver Cluster Metadata

package "Nodes" #F5F5F5 {
    rectangle "10.0.1.1\ndc1/rack1 | UP" as n1 #90EE90
    rectangle "10.0.1.2\ndc1/rack2 | UP" as n2 #90EE90
    rectangle "10.0.1.3\ndc1/rack3 | UP" as n3 #90EE90
    rectangle "10.0.2.1\ndc2/rack1 | DOWN" as n4 #FFB6C1
}

package "Keyspaces" #F5F5F5 {
    rectangle "system\nRF=1" as ks1 #E6E6FA
    rectangle "my_app\nNTS: dc1=3, dc2=3" as ks2 #E6E6FA
    rectangle "analytics\nNTS: dc1=2" as ks3 #E6E6FA
}

package "Token Map" #F5F5F5 {
    rectangle "partition_key → token → replicas" as tm #FFFACD
}

@enduml
```

The driver discovers this information through:

1. **Control connection** — Dedicated connection to one node for metadata queries
2. **System tables** — Queries `system.local`, `system.peers`, `system_schema.*`
3. **Event subscription** — Receives push notifications for topology and schema changes

This metadata enables token-aware routing (sending requests directly to replica nodes) and informed load balancing decisions.

### Connection Pooling

Each driver maintains connection pools to cluster nodes:

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Driver Session

rectangle "Application" as app #E8E8E8

package "Driver Session" #F5F5F5 {
    rectangle "Control Connection\n(metadata, events)" as control #FFE4B5

    package "Connection Pools" #FFFFFF {
        rectangle "Node 1: [conn, conn]" as node1 #90EE90
        rectangle "Node 2: [conn, conn]" as node2 #90EE90
        rectangle "Node 3: [conn, conn]" as node3 #90EE90
        rectangle "Node 4: (DOWN)" as node4 #FFB6C1
    }
}

app --> control

@enduml
```

Pool configuration parameters:

| Parameter | Description | Typical Default |
|-----------|-------------|-----------------|
| Core connections per host | Minimum connections maintained | 1 |
| Max connections per host | Maximum connections allowed | 2-8 |
| Max requests per connection | Concurrent requests before opening new connection | 1024-2048 |
| Heartbeat interval | Frequency of idle connection health checks | 30 seconds |

---

## Request Lifecycle

A typical request flows through these stages:

```plantuml
@startuml
skinparam backgroundColor transparent

rectangle "**1. ROUTING**" as R {
    (session.execute) as A
    (Load Balancing Policy) as B
}

rectangle "**2. CONNECTION**" as C {
    (Acquire Connection) as AC
}

rectangle "**3. EXECUTE**" as E {
    (Serialize & Send) as D
    (Wait for Response) as W
}

rectangle "**4. HANDLE**" as H {
    (Deserialize & Return) as G
    (Retry Policy) as RP
    (Return Error) as ERR
}

A --> B : select nodes
B --> AC : target node
AC --> D : from pool
D --> W : stream ID
W --> G : success
W --> RP : error
RP --> B : retry
RP --> ERR : no retry

@enduml
```


---

## Available Drivers

Official and community-maintained drivers exist for most languages:

| Language | Driver | Maintainer | Repository |
|----------|--------|------------|------------|
| Java | Apache Cassandra Java Driver | Apache | [cassandra-java-driver](https://github.com/apache/cassandra-java-driver) |
| Python | Apache Cassandra Python Driver | Apache | [cassandra-python-driver](https://github.com/apache/cassandra-python-driver) |
| Node.js | DataStax Node.js Driver | DataStax | [nodejs-driver](https://github.com/datastax/nodejs-driver) |
| C# | DataStax C# Driver | DataStax | [csharp-driver](https://github.com/datastax/csharp-driver) |
| Go | Apache Cassandra GoCQL Driver | Apache | [cassandra-gocql-driver](https://github.com/apache/cassandra-gocql-driver) |
| Rust | ScyllaDB Rust Driver | ScyllaDB | [scylla-rust-driver](https://github.com/scylladb/scylla-rust-driver) |
| C/C++ | Apache Cassandra C++ Driver | Apache | [cassandra-cpp-driver](https://github.com/apache/cassandra-cpp-driver) |

All major drivers implement similar concepts (policies, connection pooling, prepared statements) though APIs and configuration details vary.

---

## Section Contents

- **[Connection Management](connection-management.md)** — Connection lifecycle, pooling, and health monitoring
- **[Policies](policies/index.md)** — Load balancing, retry, reconnection, and speculative execution
- **[Prepared Statements](prepared-statements.md)** — Efficient query execution with prepared statements
- **[Best Practices](best-practices.md)** — Production configuration recommendations

