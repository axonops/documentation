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

```mermaid
sequenceDiagram
    participant App as Application
    participant Drv as Driver
    participant Node as Cassandra Node

    App->>Drv: Request A
    Drv->>Node: [Stream 1] Request A
    App->>Drv: Request B
    Drv->>Node: [Stream 2] Request B
    App->>Drv: Request C
    Drv->>Node: [Stream 3] Request C

    Node-->>Drv: [Stream 2] Response B
    Drv-->>App: Response B
    Node-->>Drv: [Stream 1] Response A
    Drv-->>App: Response A
    Node-->>Drv: [Stream 3] Response C
    Drv-->>App: Response C
```

Responses return in completion order, not request order. A single TCP connection handles thousands of concurrent requests.

This design allows a single connection to handle thousands of concurrent requests without thread-per-request overhead. Applications benefit from:

- **Efficient resource usage** — Few connections support high throughput
- **Natural back-pressure** — When stream IDs exhaust, driver queues or rejects requests
- **Simplified connection pooling** — Fewer connections to manage and monitor

### Cluster Metadata

The driver maintains a live view of cluster topology:

```dot
digraph ClusterMetadata {
    rankdir=TB
    node [shape=box, fontname="Helvetica", fontsize=10]
    edge [fontname="Helvetica", fontsize=9]

    subgraph cluster_metadata {
        label="Driver Cluster Metadata"
        style=rounded
        bgcolor="#f5f5f5"
        fontname="Helvetica-Bold"

        subgraph cluster_nodes {
            label="Nodes"
            style=dashed
            bgcolor="#ffffff"

            n1 [label="10.0.1.1\ndc1/rack1 | UP", shape=record, fillcolor="#90EE90", style=filled]
            n2 [label="10.0.1.2\ndc1/rack2 | UP", shape=record, fillcolor="#90EE90", style=filled]
            n3 [label="10.0.1.3\ndc1/rack3 | UP", shape=record, fillcolor="#90EE90", style=filled]
            n4 [label="10.0.2.1\ndc2/rack1 | DOWN", shape=record, fillcolor="#FFB6C1", style=filled]
        }

        subgraph cluster_keyspaces {
            label="Keyspaces"
            style=dashed
            bgcolor="#ffffff"

            ks1 [label="system\nRF=1", shape=record, fillcolor="#E6E6FA", style=filled]
            ks2 [label="my_app\nNTS: dc1=3, dc2=3", shape=record, fillcolor="#E6E6FA", style=filled]
            ks3 [label="analytics\nNTS: dc1=2", shape=record, fillcolor="#E6E6FA", style=filled]
        }

        subgraph cluster_tokenmap {
            label="Token Map"
            style=dashed
            bgcolor="#ffffff"

            tm [label="partition_key → token → replicas", shape=record, fillcolor="#FFFACD", style=filled]
        }
    }

    // Invisible edges for layout
    n1 -> n2 -> n3 -> n4 [style=invis]
    ks1 -> ks2 -> ks3 [style=invis]
}
```

The driver discovers this information through:

1. **Control connection** — Dedicated connection to one node for metadata queries
2. **System tables** — Queries `system.local`, `system.peers`, `system_schema.*`
3. **Event subscription** — Receives push notifications for topology and schema changes

This metadata enables token-aware routing (sending requests directly to replica nodes) and informed load balancing decisions.

### Connection Pooling

Each driver maintains connection pools to cluster nodes:

```dot
digraph ConnectionPool {
    rankdir=TB
    node [shape=box, fontname="Helvetica", fontsize=10]
    compound=true

    app [label="Application", fillcolor="#E8E8E8", style=filled]

    subgraph cluster_session {
        label="Driver Session"
        style=rounded
        bgcolor="#f5f5f5"
        fontname="Helvetica-Bold"

        control [label="Control Connection\n(metadata, events)", fillcolor="#FFE4B5", style=filled]

        subgraph cluster_pools {
            label="Connection Pools"
            style=dashed
            bgcolor="#ffffff"

            node1 [label="Node 1: [conn, conn]", fillcolor="#90EE90", style=filled]
            node2 [label="Node 2: [conn, conn]", fillcolor="#90EE90", style=filled]
            node3 [label="Node 3: [conn, conn]", fillcolor="#90EE90", style=filled]
            node4 [label="Node 4: (DOWN)", fillcolor="#FFB6C1", style=filled]
        }
    }

    app -> control [lhead=cluster_session]
    control -> node1 [style=invis]
}
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

```mermaid
flowchart TB
    A[Application calls session.execute] --> B[Load Balancing Policy]
    B --> |Select target nodes| C[Acquire Connection]
    C --> |From pool| D[Serialize & Send]
    D --> |Assign stream ID| E[Wait for Response]
    E --> F{Response?}
    F --> |Success| G[Deserialize & Return]
    F --> |Error| H{Retry Policy}
    H --> |Retry allowed| B
    H --> |No retry| I[Return Error]

    subgraph "1. ROUTING"
        B
    end

    subgraph "2. CONNECTION"
        C
    end

    subgraph "3. EXECUTE"
        D
        E
    end

    subgraph "4. HANDLE"
        F
        G
        H
        I
    end
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

