---
title: "Kafka Ecosystem"
description: "Apache Kafka ecosystem components: Kafka Brokers, Kafka Connect, Schema Registry, and Kafka Streams explained."
meta:
  - name: keywords
    content: "Kafka ecosystem, Kafka Connect, Schema Registry, Kafka Streams, Kafka components"
---

# Kafka Ecosystem

The Apache Kafka platform consists of multiple components that work together to provide a complete event streaming infrastructure.

---

## Ecosystem Overview

Modern Kafka deployments typically include multiple components beyond the core broker cluster. Understanding the role of each component clarifies architectural decisions and deployment patterns.

```plantuml
@startuml
skinparam componentStyle rectangle

package "Kafka Platform" {
  [Kafka Brokers] as brokers
  [Schema Registry] as sr
  [Kafka Connect] as connect
  [Kafka Streams] as streams
}

package "Data Sources" {
  [Databases] as db
  [Applications] as apps
  [Files/Logs] as files
  [IoT/Sensors] as iot
}

package "Data Sinks" {
  [Data Lakes] as lakes
  [Search/Analytics] as search
  [Downstream Apps] as downstream
  [Data Warehouses] as warehouse
}

package "Clients" {
  [Producers] as producers
  [Consumers] as consumers
}

db --> connect : CDC
apps --> producers
files --> connect
iot --> producers

producers --> brokers : produce
brokers --> consumers : consume

connect <--> brokers : source/sink
streams <--> brokers : read/write

producers <--> sr : schema registration
consumers <--> sr : schema lookup

connect --> lakes
connect --> search
connect --> warehouse
consumers --> downstream

@enduml
```

| Component | Purpose | Deployment |
|-----------|---------|------------|
| **Kafka Brokers** | Distributed commit log storage and serving | Cluster of 3+ nodes |
| **Schema Registry** | Schema management and compatibility enforcement | Separate service |
| **Kafka Connect** | Data integration framework with 200+ connectors | Distributed workers |
| **Kafka Streams** | Stream processing library | Embedded in applications |

---

## Kafka Brokers

Kafka brokers form the core of the platform: a distributed cluster that stores and serves event streams.

### Broker Responsibilities

| Responsibility | Description |
|----------------|-------------|
| **Message storage** | Persist messages to disk in log segments |
| **Replication** | Maintain copies across brokers for fault tolerance |
| **Leader election** | Coordinate partition leadership |
| **Client protocol** | Handle produce and fetch requests |
| **Cluster coordination** | Participate in cluster membership (via KRaft or ZooKeeper) |

### KRaft vs ZooKeeper

Kafka is transitioning from ZooKeeper-based coordination to KRaft (Kafka Raft), a built-in consensus protocol.

```plantuml
@startuml

rectangle "ZooKeeper Mode (Legacy)" as zk_mode {
  rectangle "ZooKeeper Ensemble" as zk {
    rectangle "ZK 1" as zk1
    rectangle "ZK 2" as zk2
    rectangle "ZK 3" as zk3
  }

  rectangle "Kafka Brokers" as zk_brokers {
    rectangle "Broker 1" as b1
    rectangle "Broker 2" as b2
    rectangle "Broker 3" as b3
  }

  zk_brokers --> zk : metadata, leader election
}

rectangle "KRaft Mode (Modern)" as kraft_mode {
  rectangle "Kafka Cluster" as kraft_cluster {
    rectangle "Controller 1" as c1
    rectangle "Controller 2" as c2
    rectangle "Controller 3" as c3
    rectangle "Broker 1" as kb1
    rectangle "Broker 2" as kb2
    rectangle "Broker 3" as kb3
  }

  c1 -[hidden]- c2
  c2 -[hidden]- c3

  note right of kraft_cluster
    Controllers use Raft
    for metadata consensus
  end note
}

zk_mode -[hidden]down- kraft_mode

@enduml
```

| Aspect | ZooKeeper Mode | KRaft Mode |
|--------|----------------|------------|
| **External dependency** | Requires ZooKeeper cluster | Self-contained |
| **Metadata storage** | Split between ZK and brokers | Unified in Kafka |
| **Operational complexity** | Two systems to manage | Single system |
| **Recovery time** | Slower (ZK sync required) | Faster failover |
| **Scale limits** | Lower metadata scale vs KRaft (varies by hardware/config) | Millions of partitions |
| **Version support** | All versions | Kafka 3.3+ production ready |

KRaft mode is the recommended deployment model for new clusters (Kafka 3.3+). Kafka 4.x brokers are KRaft-only.

---

## Schema Registry

Schema Registry provides centralized schema management for Kafka data, ensuring producers and consumers agree on data formats.

### Why Schema Registry?

Without schema management:

- Producers can change data format without warning
- Consumers fail when they encounter unexpected formats
- Schema evolution becomes dangerous
- Documentation becomes the only contract (and quickly becomes stale)

```plantuml
@startuml

rectangle "Without Schema Registry" as without {
  rectangle "Producer" as w_prod
  rectangle "Kafka" as w_kafka
  rectangle "Consumer" as w_cons

  w_prod -> w_kafka : {"user":"john","age":"25"}
  w_kafka -> w_cons : ❌ expects age as integer

  note bottom of w_cons
    Consumer crashes on
    unexpected format
  end note
}

rectangle "With Schema Registry" as with {
  rectangle "Producer" as s_prod
  rectangle "Schema\nRegistry" as sr
  rectangle "Kafka" as s_kafka
  rectangle "Consumer" as s_cons

  s_prod -> sr : register schema
  sr -> s_prod : ✅ compatible
  s_prod -> s_kafka : validated data
  s_kafka -> s_cons : deserialize with schema
}

without -[hidden]down- with

@enduml
```

### Schema Registry Features

| Feature | Description |
|---------|-------------|
| **Schema storage** | Schemas stored in a Kafka topic (`_schemas`) |
| **Compatibility checking** | Validates new schemas against compatibility rules |
| **Schema evolution** | Supports backward, forward, and full compatibility |
| **Multiple formats** | Avro, Protobuf, JSON Schema |
| **Subject management** | Schemas organized by subject (typically topic-based) |

### Compatibility Modes

| Mode | Rule | Safe Changes |
|------|------|--------------|
| **BACKWARD** | New schema can read old data | Add optional fields, remove fields |
| **FORWARD** | Old schema can read new data | Remove optional fields, add fields |
| **FULL** | Both backward and forward | Add/remove optional fields only |
| **NONE** | No checking | Any change (dangerous) |

Schema Registry is critical for production deployments where multiple teams produce and consume data independently.

→ [Schema Registry Guide](../schema-registry/index.md)

---

## Kafka Connect

Kafka Connect is a framework for streaming data between Kafka and external systems. It is the primary integration mechanism for most Kafka deployments.

### Why Kafka Connect?

| Without Connect | With Connect |
|-----------------|--------------|
| Write custom producer/consumer for each system | Use pre-built connectors |
| Implement offset tracking, error handling, retry logic | Framework handles operational concerns |
| Build and maintain integration infrastructure | Focus on configuration |
| Different code for each data source/sink | Consistent operational model |

### Connect Architecture

```plantuml
@startuml

rectangle "Kafka Connect Cluster" as cluster {
  rectangle "Worker 1" as w1 {
    rectangle "Task 1a" as t1a
    rectangle "Task 2a" as t2a
  }

  rectangle "Worker 2" as w2 {
    rectangle "Task 1b" as t1b
    rectangle "Task 3a" as t3a
  }

  rectangle "Worker 3" as w3 {
    rectangle "Task 2b" as t2b
    rectangle "Task 3b" as t3b
  }
}

cloud "REST APIs" as api
queue "Kafka" as kafka
database "Cassandra" as cass

api --> t1a : HTTP Source
api --> t1b : (parallelized)

t2a --> kafka
t2b --> kafka

kafka --> t3a
kafka --> t3b

t3a --> cass
t3b --> cass

note bottom of cluster
  Workers distribute tasks
  automatically for scaling
  and fault tolerance
end note

@enduml
```

### Connector Types

| Type | Direction | Example Use Cases |
|------|-----------|-------------------|
| **Source connectors** | External → Kafka | Database CDC, file ingestion, API polling |
| **Sink connectors** | Kafka → External | Data lake writes, search indexing, notifications |

### Connector Ecosystem

200+ production-grade connectors are available:

| Category | Examples |
|----------|----------|
| **Event Sources** | HTTP/REST, MQTT, File/Syslog, JMS/MQ |
| **Cloud Storage Sinks** | S3, GCS, Azure Blob, HDFS |
| **Database Sinks** | Cassandra, Elasticsearch, OpenSearch |
| **Data Warehouse Sinks** | Snowflake, BigQuery, Redshift |

Kafka Connect is often the most valuable component of a Kafka deployment—it eliminates thousands of lines of integration code.

→ [Kafka Connect Guide](../kafka-connect/index.md)

---

## Kafka Streams

Kafka Streams is a client library for building stream processing applications. Unlike Connect, Streams is embedded in applications rather than deployed as a separate cluster.

### Streams Characteristics

| Aspect | Description |
|--------|-------------|
| **Deployment** | Library embedded in application (JAR dependency) |
| **Scaling** | Add application instances to scale |
| **State management** | Local state stores with changelog topics for recovery |
| **Processing semantics** | Exactly-once processing supported |
| **Fault tolerance** | Automatic state recovery from changelog topics |

### When to Use Streams

| Use Case | Why Streams |
|----------|-------------|
| **Stateful transformations** | Aggregations, joins, windowing |
| **Application-embedded processing** | No separate cluster to manage |
| **Microservice event processing** | Natural fit for event-driven services |
| **Real-time enrichment** | Stream-table joins for lookups |

### Streams vs Connect

| Aspect | Kafka Streams | Kafka Connect |
|--------|---------------|---------------|
| **Purpose** | Data processing and transformation | Data movement between systems |
| **Deployment** | Application library | Separate worker cluster |
| **Custom logic** | Full programming model | Configuration + SMTs |
| **State** | Built-in state stores | Stateless (connector-dependent) |
| **Scaling** | Add application instances | Add workers |

```plantuml
@startuml

rectangle "Kafka Streams Application" as app {
  rectangle "Stream\nTopology" as topology
  database "State\nStore" as state
  rectangle "Application\nLogic" as logic

  topology <-> state
  topology <-> logic
}

database "Input Topic" as input
database "Output Topic" as output
database "Changelog Topic" as changelog

input --> app : consume
app --> output : produce
state <--> changelog : backup/restore

note right of app
  Streams is a library
  inside your application
end note

@enduml
```

→ [Kafka Streams Guide](../application-development/kafka-streams/index.md)

---

## Component Selection Guide

| Requirement | Recommended Component |
|-------------|----------------------|
| Stream events from APIs to Kafka | Kafka Connect + HTTP/MQTT Source |
| Move data from Kafka to data lake | Kafka Connect + S3/GCS connector |
| Transform and enrich events | Kafka Streams |
| Custom application logic | Kafka Streams or custom consumer |
| Schema enforcement | Schema Registry |
| Real-time dashboards | Kafka Streams + external visualization |

### Typical Production Architecture

```plantuml
@startuml

package "Source Systems" {
  database "PostgreSQL" as pg
  database "MySQL" as mysql
  rectangle "Applications" as apps
}

package "Kafka Platform" {
  rectangle "Kafka Connect\n(Source)" as connect_source
  rectangle "Kafka Brokers" as brokers
  rectangle "Schema Registry" as sr
  rectangle "Kafka Streams\nApplications" as streams
  rectangle "Kafka Connect\n(Sink)" as connect_sink
}

package "Downstream Systems" {
  database "S3 Data Lake" as s3
  database "Elasticsearch" as es
  rectangle "Analytics\nApplications" as analytics
}

pg --> connect_source : CDC
mysql --> connect_source : CDC
apps --> brokers : produce

connect_source --> brokers
brokers <--> sr
brokers <--> streams
brokers --> connect_sink

connect_sink --> s3
connect_sink --> es
streams --> analytics

@enduml
```

---

## Version Compatibility

| Component | Kafka 2.x | Kafka 3.x | Kafka 4.x |
|-----------|:---------:|:---------:|:---------:|
| Kafka Brokers | ✅ | ✅ | ✅ |
| Schema Registry | ✅ | ✅ | ✅ |
| Kafka Connect | ✅ | ✅ | ✅ |
| Kafka Streams | ✅ | ✅ | ✅ |
| KRaft (production) | ❌ | ✅ (3.3+) | ✅ |

---

## Related Documentation

- [Event Streaming Fundamentals](index.md) - Core concepts
- [Kafka Connect](kafka-connect/index.md) - Data integration deep-dive
- [Delivery Semantics](delivery-semantics/index.md) - Message delivery guarantees
- [Schema Registry](../schema-registry/index.md) - Schema management guide
- [Kafka Streams](../application-development/kafka-streams/index.md) - Stream processing library