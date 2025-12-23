---
title: "Kafka Connect"
description: "Kafka Connect architecture, deployment modes, connector configuration, transforms, converters, and operational guidance for data integration."
meta:
  - name: keywords
    content: "Kafka Connect, connectors, source connector, sink connector, distributed mode, SMT, data integration"
---

# Kafka Connect

Kafka Connect is a framework for streaming data between Apache Kafka and external systems using pre-built or custom connectors.

---

## Overview

Kafka Connect eliminates the need to write custom integration code for common data sources and sinks. The framework handles:

- Parallelization and scaling
- Offset management and exactly-once delivery
- Schema integration with Schema Registry
- Fault tolerance and automatic recovery
- Standardized monitoring and operations

```plantuml
@startuml

rectangle "Event Sources" as sources {
  cloud "REST APIs" as api
  node "MQTT Devices" as mqtt
  collections "Log Files" as files
}

rectangle "Kafka Connect Cluster" as connect {
  rectangle "Worker 1" as w1
  rectangle "Worker 2" as w2
  rectangle "Worker 3" as w3
}

rectangle "Kafka Cluster" as kafka {
  rectangle "Topics" as topics
}

rectangle "Data Sinks" as sinks {
  storage "S3" as s3
  database "Cassandra" as cass
  database "Elasticsearch" as es
}

api --> w1 : HTTP Source
mqtt --> w2 : MQTT Source
files --> w3 : FileStream

w1 --> topics
w2 --> topics
w3 --> topics

topics --> w1
topics --> w2
topics --> w3

w1 --> s3 : S3 Sink
w2 --> cass : Cassandra Sink
w3 --> es : ES Sink

@enduml
```

---

## Architecture

### Components

| Component | Description |
|-----------|-------------|
| **Worker** | JVM process that executes connectors and tasks |
| **Connector** | Plugin that defines how to connect to external system |
| **Task** | Unit of work; connectors are divided into tasks for parallelism |
| **Converter** | Serializes/deserializes data between Connect and Kafka |
| **Transform** | Modifies records in-flight (Single Message Transforms) |

### Worker Architecture

```plantuml
@startuml

rectangle "Connect Worker" {
  rectangle "REST API\n(:8083)" as rest

  rectangle "Herder" as herder {
    rectangle "Connector\nManagement" as conn_mgmt
    rectangle "Task\nManagement" as task_mgmt
  }

  rectangle "Connectors & Tasks" as tasks {
    rectangle "Source Task 1" as st1
    rectangle "Source Task 2" as st2
    rectangle "Sink Task 1" as sk1
  }

  rectangle "Converters" as conv {
    rectangle "Key\nConverter" as key_conv
    rectangle "Value\nConverter" as val_conv
  }

  rectangle "Offset Storage" as offsets
}

rest --> herder : manage
herder --> tasks : coordinate
tasks <--> conv : serialize/deserialize
tasks <--> offsets : track position

@enduml
```

### Data Flow

```plantuml
@startuml

rectangle "Source Connector Flow" as source_flow {
  database "External\nSystem" as ext_src
  rectangle "Source\nTask" as src_task
  rectangle "Converter" as src_conv
  rectangle "Transform\n(SMT)" as src_smt
  queue "Kafka\nTopic" as src_topic

  ext_src -> src_task : poll
  src_task -> src_conv : SourceRecord
  src_conv -> src_smt : serialized
  src_smt -> src_topic : produce
}

rectangle "Sink Connector Flow" as sink_flow {
  queue "Kafka\nTopic" as sink_topic
  rectangle "Transform\n(SMT)" as sink_smt
  rectangle "Converter" as sink_conv
  rectangle "Sink\nTask" as sink_task
  database "External\nSystem" as ext_sink

  sink_topic -> sink_smt : consume
  sink_smt -> sink_conv : transformed
  sink_conv -> sink_task : SinkRecord
  sink_task -> ext_sink : write
}

source_flow -[hidden]down- sink_flow

@enduml
```

---

## Deployment Modes

### Standalone Mode

Single worker process—suitable for development and simple use cases.

```bash
# Start standalone worker
connect-standalone.sh \
  config/connect-standalone.properties \
  config/file-source.properties \
  config/file-sink.properties
```

**Standalone properties:**
```properties
bootstrap.servers=localhost:9092
key.converter=org.apache.kafka.connect.json.JsonConverter
value.converter=org.apache.kafka.connect.json.JsonConverter

# Offset storage (local file)
offset.storage.file.filename=/tmp/connect.offsets

# REST API
rest.port=8083
```

| Characteristic | Standalone Mode |
|----------------|-----------------|
| **Workers** | Single process |
| **Offset storage** | Local file |
| **Fault tolerance** | None |
| **Scaling** | Not supported |
| **Use case** | Development, testing |

### Distributed Mode

Multiple workers forming a cluster—required for production.

```bash
# Start distributed worker (on each node)
connect-distributed.sh config/connect-distributed.properties
```

**Distributed properties:**
```properties
bootstrap.servers=kafka1:9092,kafka2:9092,kafka3:9092

# Group coordination
group.id=connect-cluster

# Offset storage (Kafka topics)
offset.storage.topic=connect-offsets
offset.storage.replication.factor=3
offset.storage.partitions=25

# Config storage
config.storage.topic=connect-configs
config.storage.replication.factor=3

# Status storage
status.storage.topic=connect-status
status.storage.replication.factor=3
status.storage.partitions=5

# Converters
key.converter=io.confluent.connect.avro.AvroConverter
key.converter.schema.registry.url=http://schema-registry:8081
value.converter=io.confluent.connect.avro.AvroConverter
value.converter.schema.registry.url=http://schema-registry:8081

# REST API
rest.advertised.host.name=connect-worker-1
rest.port=8083
```

| Characteristic | Distributed Mode |
|----------------|------------------|
| **Workers** | Multiple processes (cluster) |
| **Offset storage** | Kafka topic (`connect-offsets`) |
| **Fault tolerance** | Automatic task redistribution |
| **Scaling** | Add workers to scale |
| **Use case** | Production |

### Internal Topics

| Topic | Purpose | Recommended Config |
|-------|---------|-------------------|
| `connect-offsets` | Source connector offsets | RF=3, partitions=25 |
| `connect-configs` | Connector configurations | RF=3, partitions=1, compacted |
| `connect-status` | Connector/task status | RF=3, partitions=5, compacted |

---

## Deployment Architectures

### Standalone Architecture

Single worker process for development and simple integrations.

```plantuml
@startuml

rectangle "Single Host" {
  rectangle "Connect Worker\n(Standalone)" as worker {
    rectangle "Connector A" as conn_a
    rectangle "Task 1" as task1
  }
  file "Offset File\n(/tmp/connect.offsets)" as offset_file
}

rectangle "Kafka Cluster" as kafka {
  queue "Topics" as topics
}

database "External\nSystem" as ext

worker --> offset_file : persist offsets
task1 <--> topics : produce/consume
task1 <--> ext : read/write

note bottom of worker
  - No fault tolerance
  - No scaling
  - Dev/test only
end note

@enduml
```

### Distributed Architecture

Multi-worker cluster for production deployments.

```plantuml
@startuml

rectangle "Connect Cluster" as cluster {
  rectangle "Worker 1" as w1 {
    rectangle "Connector A\nTask 1" as t1
    rectangle "Connector B\nTask 1" as t2
  }
  rectangle "Worker 2" as w2 {
    rectangle "Connector A\nTask 2" as t3
    rectangle "Connector C\nTask 1" as t4
  }
  rectangle "Worker 3" as w3 {
    rectangle "Connector A\nTask 3" as t5
    rectangle "Connector B\nTask 2" as t6
  }
}

rectangle "Kafka Cluster" as kafka {
  queue "Data Topics" as data
  queue "connect-offsets" as offsets
  queue "connect-configs" as configs
  queue "connect-status" as status
}

rectangle "Load Balancer\n(:8083)" as lb

lb --> w1 : REST API
lb --> w2 : REST API
lb --> w3 : REST API

w1 <--> data
w2 <--> data
w3 <--> data

w1 <--> offsets
w1 <--> configs
w1 <--> status

note bottom of kafka
  Internal topics provide:
  - Distributed offset storage
  - Configuration sync
  - Status coordination
end note

@enduml
```

### Co-located Deployment

Connect workers on Kafka broker nodes—suitable for smaller clusters.

```plantuml
@startuml

rectangle "Node 1" as n1 {
  rectangle "Kafka Broker" as b1
  rectangle "Connect Worker" as c1
}

rectangle "Node 2" as n2 {
  rectangle "Kafka Broker" as b2
  rectangle "Connect Worker" as c2
}

rectangle "Node 3" as n3 {
  rectangle "Kafka Broker" as b3
  rectangle "Connect Worker" as c3
}

c1 --> b1 : localhost
c2 --> b2 : localhost
c3 --> b3 : localhost

b1 <--> b2 : replication
b2 <--> b3 : replication
b3 <--> b1 : replication

note bottom
  Pros:
  - Lower latency (localhost)
  - Fewer nodes to manage

  Cons:
  - Resource contention
  - Failure affects both services
  - Harder to scale independently
end note

@enduml
```

### Dedicated Connect Cluster

Separate Connect cluster—recommended for production.

```plantuml
@startuml

rectangle "Connect Cluster" as connect {
  rectangle "Connect\nWorker 1" as c1
  rectangle "Connect\nWorker 2" as c2
  rectangle "Connect\nWorker 3" as c3
}

rectangle "Kafka Cluster" as kafka {
  rectangle "Broker 1" as b1
  rectangle "Broker 2" as b2
  rectangle "Broker 3" as b3
}

rectangle "External Systems" as ext {
  database "Databases" as db
  storage "Object Storage" as s3
  cloud "APIs" as api
}

c1 --> b1
c1 --> b2
c2 --> b2
c2 --> b3
c3 --> b1
c3 --> b3

c1 <--> db
c2 <--> s3
c3 <--> api

note bottom of connect
  Pros:
  - Independent scaling
  - Isolated failures
  - Dedicated resources
  - Easier capacity planning
end note

@enduml
```

### Sidecar Pattern

Connect worker per application—useful for application-specific integrations.

```plantuml
@startuml

rectangle "Application Pod 1" as pod1 {
  rectangle "Application" as app1
  rectangle "Connect\nWorker" as c1
}

rectangle "Application Pod 2" as pod2 {
  rectangle "Application" as app2
  rectangle "Connect\nWorker" as c2
}

rectangle "Application Pod 3" as pod3 {
  rectangle "Application" as app3
  rectangle "Connect\nWorker" as c3
}

rectangle "Kafka Cluster" as kafka {
  queue "Topics" as topics
}

app1 --> c1 : local config
app2 --> c2 : local config
app3 --> c3 : local config

c1 --> topics
c2 --> topics
c3 --> topics

note bottom
  Use cases:
  - Application-owned connectors
  - Isolation requirements
  - Local file ingestion

  Note: Each can be standalone
  or join distributed cluster
end note

@enduml
```

### Kubernetes Deployment

Connect cluster on Kubernetes with horizontal scaling.

```plantuml
@startuml

rectangle "Kubernetes Cluster" {
  rectangle "Connect Deployment" as deploy {
    rectangle "Pod 1\nConnect Worker" as p1
    rectangle "Pod 2\nConnect Worker" as p2
    rectangle "Pod 3\nConnect Worker" as p3
  }

  rectangle "Service\nconnect-svc:8083" as svc
  rectangle "Ingress" as ingress

  rectangle "ConfigMap\nconnect-config" as cm
  rectangle "Secret\nconnect-secrets" as secret
}

rectangle "Kafka\n(internal or external)" as kafka

ingress --> svc
svc --> p1
svc --> p2
svc --> p3

cm --> deploy : mount
secret --> deploy : mount

p1 --> kafka
p2 --> kafka
p3 --> kafka

note right of deploy
  HPA can scale workers
  based on CPU/memory
  or custom metrics
end note

@enduml
```

**Kubernetes manifest example:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kafka-connect
spec:
  replicas: 3
  selector:
    matchLabels:
      app: kafka-connect
  template:
    metadata:
      labels:
        app: kafka-connect
    spec:
      containers:
      - name: connect
        image: confluentinc/cp-kafka-connect:7.5.0
        ports:
        - containerPort: 8083
        env:
        - name: CONNECT_BOOTSTRAP_SERVERS
          value: "kafka:9092"
        - name: CONNECT_GROUP_ID
          value: "connect-cluster"
        - name: CONNECT_REST_ADVERTISED_HOST_NAME
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
---
apiVersion: v1
kind: Service
metadata:
  name: kafka-connect
spec:
  ports:
  - port: 8083
  selector:
    app: kafka-connect
```

### Multi-Region Deployment

Separate Connect clusters per region for geo-distributed workloads.

```plantuml
@startuml

rectangle "Region A (US-East)" as region_a {
  rectangle "Connect Cluster A" as connect_a {
    rectangle "Worker" as w_a1
    rectangle "Worker" as w_a2
  }
  rectangle "Kafka Cluster A" as kafka_a
  database "Local Systems" as local_a
}

rectangle "Region B (EU-West)" as region_b {
  rectangle "Connect Cluster B" as connect_b {
    rectangle "Worker" as w_b1
    rectangle "Worker" as w_b2
  }
  rectangle "Kafka Cluster B" as kafka_b
  database "Local Systems" as local_b
}

w_a1 --> kafka_a
w_a2 --> kafka_a
w_a1 --> local_a
w_a2 --> local_a

w_b1 --> kafka_b
w_b2 --> kafka_b
w_b1 --> local_b
w_b2 --> local_b

kafka_a <--> kafka_b : MirrorMaker 2\n(cross-region)

note bottom
  Each region has independent:
  - Connect cluster
  - Kafka cluster
  - Local integrations

  Cross-region via MM2
end note

@enduml
```

### Deployment Comparison

| Pattern | Scaling | Fault Tolerance | Resource Isolation | Use Case |
|---------|---------|-----------------|-------------------|----------|
| **Standalone** | None | None | N/A | Development |
| **Co-located** | With brokers | Shared | Poor | Small clusters |
| **Dedicated cluster** | Independent | Independent | Good | Production |
| **Sidecar** | Per application | Per application | Excellent | App-specific |
| **Kubernetes** | HPA/VPA | Pod replacement | Good | Cloud-native |
| **Multi-region** | Per region | Regional | Excellent | Global deployments |

### Sizing Guidelines

| Workload | Workers | Memory per Worker | CPU per Worker |
|----------|---------|-------------------|----------------|
| **Light** (< 10 connectors) | 2-3 | 2-4 GB | 1-2 cores |
| **Medium** (10-50 connectors) | 3-5 | 4-8 GB | 2-4 cores |
| **Heavy** (50+ connectors) | 5-10+ | 8-16 GB | 4-8 cores |

!!! note "Worker Sizing"
    Worker memory depends on:

    - Number of tasks per worker
    - Message size and throughput
    - Converter complexity (Avro/Protobuf vs JSON)
    - Transform chain depth

---

## Connector Configuration

### Creating Connectors via REST API

```bash
# Create a Cassandra Sink connector
curl -X POST http://connect:8083/connectors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "cassandra-sink",
    "config": {
      "connector.class": "com.datastax.oss.kafka.sink.CassandraSinkConnector",
      "tasks.max": "1",
      "topics": "events",
      "contactPoints": "cassandra1,cassandra2,cassandra3",
      "loadBalancing.localDc": "datacenter1",
      "port": "9042",
      "topic.events.keyspace.table.mapping": "events.events_by_time",
      "topic.events.keyspace.table.consistencyLevel": "LOCAL_QUORUM"
    }
  }'
```

### Common Configuration Properties

| Property | Description |
|----------|-------------|
| `name` | Unique connector name |
| `connector.class` | Fully qualified connector class |
| `tasks.max` | Maximum number of tasks |
| `key.converter` | Key converter (overrides worker default) |
| `value.converter` | Value converter (overrides worker default) |
| `transforms` | Comma-separated list of transforms |
| `errors.tolerance` | Error handling: none, all |
| `errors.deadletterqueue.topic.name` | Dead letter queue topic |

### Connector Lifecycle

```plantuml
@startuml

[*] --> UNASSIGNED : create

UNASSIGNED --> RUNNING : task assigned
RUNNING --> PAUSED : pause
PAUSED --> RUNNING : resume
RUNNING --> FAILED : error
FAILED --> RUNNING : restart
RUNNING --> UNASSIGNED : rebalance

RUNNING --> [*] : delete
PAUSED --> [*] : delete
FAILED --> [*] : delete

@enduml
```

---

## REST API Reference

### Connector Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/connectors` | GET | List all connectors |
| `/connectors` | POST | Create connector |
| `/connectors/{name}` | GET | Get connector info |
| `/connectors/{name}` | DELETE | Delete connector |
| `/connectors/{name}/config` | GET | Get connector config |
| `/connectors/{name}/config` | PUT | Update connector config |
| `/connectors/{name}/status` | GET | Get connector status |
| `/connectors/{name}/restart` | POST | Restart connector |
| `/connectors/{name}/pause` | PUT | Pause connector |
| `/connectors/{name}/resume` | PUT | Resume connector |
| `/connectors/{name}/stop` | PUT | Stop connector (deallocate resources) |

### Task Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/connectors/{name}/tasks` | GET | List tasks |
| `/connectors/{name}/tasks/{id}/status` | GET | Get task status |
| `/connectors/{name}/tasks/{id}/restart` | POST | Restart task |

### Offset Management

Manage connector offsets (connector must be stopped):

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/connectors/{name}/offsets` | GET | Get current offsets |
| `/connectors/{name}/offsets` | DELETE | Reset offsets |
| `/connectors/{name}/offsets` | PATCH | Alter offsets |

**Alter source connector offsets:**

```bash
# Stop connector first
curl -X PUT http://connect:8083/connectors/my-connector/stop

# Alter offsets
curl -X PATCH http://connect:8083/connectors/my-connector/offsets \
  -H "Content-Type: application/json" \
  -d '{
    "offsets": [
      {
        "partition": {"filename": "test.txt"},
        "offset": {"position": 30}
      }
    ]
  }'

# Resume connector
curl -X PUT http://connect:8083/connectors/my-connector/resume
```

**Reset sink connector offsets:**

```bash
# Stop and reset to re-consume from beginning
curl -X PUT http://connect:8083/connectors/my-sink/stop
curl -X DELETE http://connect:8083/connectors/my-sink/offsets
curl -X PUT http://connect:8083/connectors/my-sink/resume
```

### Cluster Information

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Cluster info |
| `/connector-plugins` | GET | List installed plugins |
| `/connector-plugins/{plugin}/config/validate` | PUT | Validate config |

### Admin Logging

Dynamically adjust log levels:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/admin/loggers` | GET | List loggers with explicit levels |
| `/admin/loggers/{name}` | GET | Get logger level |
| `/admin/loggers/{name}` | PUT | Set logger level |

```bash
# Enable debug logging for connector
curl -X PUT http://connect:8083/admin/loggers/org.apache.kafka.connect \
  -H "Content-Type: application/json" \
  -d '{"level": "DEBUG"}'
```

---

## Converters

Converters serialize and deserialize data between Connect's internal format and Kafka.

### Available Converters

| Converter | Format | Schema Support |
|-----------|--------|----------------|
| `JsonConverter` | JSON | Optional (schemas.enable) |
| `AvroConverter` | Avro binary | Yes (Schema Registry) |
| `ProtobufConverter` | Protobuf binary | Yes (Schema Registry) |
| `JsonSchemaConverter` | JSON with schema | Yes (Schema Registry) |
| `StringConverter` | Plain string | No |
| `ByteArrayConverter` | Raw bytes | No |

### Converter Configuration

```properties
# JSON without schemas (simple)
key.converter=org.apache.kafka.connect.json.JsonConverter
key.converter.schemas.enable=false
value.converter=org.apache.kafka.connect.json.JsonConverter
value.converter.schemas.enable=false

# Avro with Schema Registry (production)
key.converter=io.confluent.connect.avro.AvroConverter
key.converter.schema.registry.url=http://schema-registry:8081
value.converter=io.confluent.connect.avro.AvroConverter
value.converter.schema.registry.url=http://schema-registry:8081
```

### Converter Selection Guide

| Use Case | Recommended Converter |
|----------|----------------------|
| Development/debugging | JsonConverter (schemas.enable=false) |
| Production with schema evolution | AvroConverter or ProtobufConverter |
| Existing JSON consumers | JsonConverter or JsonSchemaConverter |
| Maximum compatibility | StringConverter (manual serialization) |

→ [Converters Guide](converters.md)

---

## Single Message Transforms (SMTs)

SMTs modify records as they flow through Connect—useful for simple transformations without custom code.

### Built-in Transforms

| Transform | Description |
|-----------|-------------|
| `InsertField` | Add field with static or metadata value |
| `ReplaceField` | Rename, include, or exclude fields |
| `MaskField` | Replace field value with valid null |
| `ValueToKey` | Copy fields from value to key |
| `ExtractField` | Extract single field from struct |
| `SetSchemaMetadata` | Set schema name and version |
| `TimestampRouter` | Route to topic based on timestamp |
| `RegexRouter` | Route to topic based on regex |
| `Flatten` | Flatten nested structures |
| `Cast` | Cast field to different type |
| `HeaderFrom` | Copy field to header |
| `InsertHeader` | Add static header |
| `DropHeaders` | Remove headers |
| `Filter` | Drop records matching predicate |

### Transform Configuration

```json
{
  "name": "my-connector",
  "config": {
    "connector.class": "...",
    "transforms": "addTimestamp,route",

    "transforms.addTimestamp.type": "org.apache.kafka.connect.transforms.InsertField$Value",
    "transforms.addTimestamp.timestamp.field": "processed_at",

    "transforms.route.type": "org.apache.kafka.connect.transforms.RegexRouter",
    "transforms.route.regex": "(.*)_raw",
    "transforms.route.replacement": "$1_processed"
  }
}
```

### Transform Chain

```plantuml
@startuml

rectangle "SMT Chain" {
  rectangle "Original\nRecord" as orig
  rectangle "Transform 1\n(InsertField)" as t1
  rectangle "Transform 2\n(ReplaceField)" as t2
  rectangle "Transform 3\n(RegexRouter)" as t3
  rectangle "Final\nRecord" as final

  orig --> t1 : record
  t1 --> t2 : modified
  t2 --> t3 : modified
  t3 --> final : modified
}

note bottom
  Transforms execute in order
  Each receives output of previous
end note

@enduml
```

### Predicates

Apply transforms conditionally based on message properties:

**Built-in Predicates:**

| Predicate | Description |
|-----------|-------------|
| `TopicNameMatches` | Match records where topic name matches regex |
| `HasHeaderKey` | Match records with specific header key |
| `RecordIsTombstone` | Match tombstone records (null value) |

**Predicate Configuration:**

```json
{
  "name": "my-connector",
  "config": {
    "connector.class": "...",
    "transforms": "FilterFoo,ExtractBar",

    "transforms.FilterFoo.type": "org.apache.kafka.connect.transforms.Filter",
    "transforms.FilterFoo.predicate": "IsFoo",

    "transforms.ExtractBar.type": "org.apache.kafka.connect.transforms.ExtractField$Key",
    "transforms.ExtractBar.field": "other_field",
    "transforms.ExtractBar.predicate": "IsBar",
    "transforms.ExtractBar.negate": "true",

    "predicates": "IsFoo,IsBar",

    "predicates.IsFoo.type": "org.apache.kafka.connect.transforms.predicates.TopicNameMatches",
    "predicates.IsFoo.pattern": "foo",

    "predicates.IsBar.type": "org.apache.kafka.connect.transforms.predicates.TopicNameMatches",
    "predicates.IsBar.pattern": "bar"
  }
}
```

| Property | Description |
|----------|-------------|
| `predicate` | Associate predicate alias with transform |
| `negate` | Invert predicate match (apply when NOT matched) |

→ [Transforms Guide](transforms.md)

---

## Error Handling

### Error Tolerance

```json
{
  "name": "my-connector",
  "config": {
    "connector.class": "...",
    "errors.tolerance": "all",
    "errors.deadletterqueue.topic.name": "my-connector-dlq",
    "errors.deadletterqueue.topic.replication.factor": 3,
    "errors.deadletterqueue.context.headers.enable": true,
    "errors.log.enable": true,
    "errors.log.include.messages": true
  }
}
```

| Configuration | Description |
|---------------|-------------|
| `errors.tolerance=none` | Fail on first error (default) |
| `errors.tolerance=all` | Log errors and continue |
| `errors.deadletterqueue.topic.name` | Topic for failed records |
| `errors.deadletterqueue.context.headers.enable` | Include error context in headers |
| `errors.log.enable` | Log errors to Connect log |
| `errors.log.include.messages` | Include record content in logs |

### Dead Letter Queue

```plantuml
@startuml

rectangle "Sink Connector" as connector {
  rectangle "Task" as task
}

queue "Source Topic" as source
queue "Dead Letter Queue" as dlq
database "External System" as ext

source -> task : consume

task -> ext : write (success)
task -> dlq : write (failure)

note right of dlq
  Failed records include:
  - Original key/value
  - Error message header
  - Exception stack trace
  - Source topic/partition/offset
end note

@enduml
```

→ [Error Handling Guide](error-handling.md)

---

## Exactly-Once Delivery

Kafka Connect supports exactly-once semantics for source connectors (Kafka 3.3+).

### Source Connector EOS

```properties
# Worker configuration
exactly.once.source.support=enabled
transaction.boundary=poll  # or connector, interval

# Connector configuration (automatically uses transactions)
```

| Transaction Boundary | Behavior |
|---------------------|----------|
| `poll` | Transaction per poll() call |
| `connector` | Connector defines boundaries |
| `interval` | Transaction every N milliseconds |

### Sink Connector EOS

Sink connectors achieve exactly-once through idempotent writes to external systems:

| Strategy | Implementation |
|----------|----------------|
| **Upsert** | Use primary key for idempotent updates |
| **Deduplication** | Track processed offsets in sink |
| **Transactions** | Commit offset with sink transaction |

→ [Exactly-Once Guide](exactly-once.md)

---

## Monitoring

### Key Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `connector-count` | Number of connectors | Expected count |
| `task-count` | Number of running tasks | Expected count |
| `connector-startup-failure-total` | Connector startup failures | > 0 |
| `task-startup-failure-total` | Task startup failures | > 0 |
| `source-record-poll-total` | Records polled by source | Depends on workload |
| `sink-record-send-total` | Records sent by sink | Depends on workload |
| `offset-commit-failure-total` | Offset commit failures | > 0 |
| `deadletterqueue-produce-total` | Records sent to DLQ | > 0 (investigate) |

### JMX MBeans

```
kafka.connect:type=connector-metrics,connector={connector}
kafka.connect:type=connector-task-metrics,connector={connector},task={task}
kafka.connect:type=source-task-metrics,connector={connector},task={task}
kafka.connect:type=sink-task-metrics,connector={connector},task={task}
```

→ [Operations Guide](operations.md)

---

## Scaling

### Horizontal Scaling

Add workers to the Connect cluster to distribute load:

```plantuml
@startuml

rectangle "Before Scaling" as before {
  rectangle "Worker 1" as w1_before {
    rectangle "Task 1" as t1_b
    rectangle "Task 2" as t2_b
    rectangle "Task 3" as t3_b
    rectangle "Task 4" as t4_b
  }
}

rectangle "After Scaling" as after {
  rectangle "Worker 1" as w1_after {
    rectangle "Task 1" as t1_a
    rectangle "Task 2" as t2_a
  }
  rectangle "Worker 2" as w2_after {
    rectangle "Task 3" as t3_a
    rectangle "Task 4" as t4_a
  }
}

before -[hidden]down- after

note bottom of after
  Tasks automatically
  redistributed on
  worker join/leave
end note

@enduml
```

### Task Parallelism

Increase `tasks.max` for connectors that support parallelism:

```json
{
  "name": "jdbc-source",
  "config": {
    "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",
    "tasks.max": "10",
    "table.whitelist": "orders,customers,products"
  }
}
```

| Connector Type | Parallelism Model |
|----------------|-------------------|
| **HTTP Source** | One task per endpoint (typically) |
| **File Source** | One task per file or directory |
| **S3 Sink** | Tasks share topic partitions |
| **Cassandra Sink** | Tasks share topic partitions |

---

## Connector Development

Building custom connectors to integrate Kafka with proprietary or unsupported systems.

### Connector Components

| Component | Interface | Purpose |
|-----------|-----------|---------|
| **SourceConnector** | `SourceConnector` | Configuration and task distribution for imports |
| **SourceTask** | `SourceTask` | Read data from external system |
| **SinkConnector** | `SinkConnector` | Configuration and task distribution for exports |
| **SinkTask** | `SinkTask` | Write data to external system |

### Source Connector Structure

```java
public class MySourceConnector extends SourceConnector {
    private Map<String, String> configProps;

    @Override
    public void start(Map<String, String> props) {
        this.configProps = props;
    }

    @Override
    public Class<? extends Task> taskClass() {
        return MySourceTask.class;
    }

    @Override
    public List<Map<String, String>> taskConfigs(int maxTasks) {
        // Distribute work across tasks
        List<Map<String, String>> configs = new ArrayList<>();
        for (int i = 0; i < maxTasks; i++) {
            Map<String, String> taskConfig = new HashMap<>(configProps);
            taskConfig.put("task.id", String.valueOf(i));
            configs.add(taskConfig);
        }
        return configs;
    }

    @Override
    public void stop() {
        // Clean up resources
    }

    @Override
    public ConfigDef config() {
        return new ConfigDef()
            .define("connection.url", Type.STRING, Importance.HIGH, "Connection URL");
    }

    @Override
    public String version() {
        return "1.0.0";
    }
}
```

### Source Task Implementation

```java
public class MySourceTask extends SourceTask {
    private String connectionUrl;

    @Override
    public void start(Map<String, String> props) {
        connectionUrl = props.get("connection.url");
        // Initialize connection
    }

    @Override
    public List<SourceRecord> poll() throws InterruptedException {
        List<SourceRecord> records = new ArrayList<>();

        // Read from external system
        List<DataItem> items = fetchData();

        for (DataItem item : items) {
            Map<String, ?> sourcePartition = Collections.singletonMap("source", connectionUrl);
            Map<String, ?> sourceOffset = Collections.singletonMap("position", item.getOffset());

            records.add(new SourceRecord(
                sourcePartition,
                sourceOffset,
                "target-topic",
                Schema.STRING_SCHEMA,
                item.getKey(),
                Schema.STRING_SCHEMA,
                item.getValue()
            ));
        }
        return records;
    }

    @Override
    public void stop() {
        // Close connections
    }

    @Override
    public String version() {
        return "1.0.0";
    }
}
```

### Sink Task Implementation

```java
public class MySinkTask extends SinkTask {
    private ErrantRecordReporter reporter;

    @Override
    public void start(Map<String, String> props) {
        // Initialize connection
        try {
            reporter = context.errantRecordReporter();
        } catch (NoSuchMethodError e) {
            reporter = null; // Older Connect runtime
        }
    }

    @Override
    public void put(Collection<SinkRecord> records) {
        for (SinkRecord record : records) {
            try {
                writeToDestination(record);
            } catch (Exception e) {
                if (reporter != null) {
                    reporter.report(record, e);  // Send to DLQ
                } else {
                    throw new ConnectException("Write failed", e);
                }
            }
        }
    }

    @Override
    public void flush(Map<TopicPartition, OffsetAndMetadata> offsets) {
        // Ensure all data is persisted before offset commit
    }

    @Override
    public void stop() {
        // Close connections
    }

    @Override
    public String version() {
        return "1.0.0";
    }
}
```

### Plugin Discovery

Register connector class in `META-INF/services/`:

```
# META-INF/services/org.apache.kafka.connect.source.SourceConnector
com.example.MySourceConnector

# META-INF/services/org.apache.kafka.connect.sink.SinkConnector
com.example.MySinkConnector
```

### Resume from Offset

```java
@Override
public void start(Map<String, String> props) {
    Map<String, Object> partition = Collections.singletonMap("source", connectionUrl);
    Map<String, Object> offset = context.offsetStorageReader().offset(partition);

    if (offset != null) {
        Long lastPosition = (Long) offset.get("position");
        seekToPosition(lastPosition);
    }
}
```

---

## Related Documentation

- [Connectors](connectors/index.md) - Connector guides (Cassandra, S3, HTTP)
- [Transforms](transforms.md) - Single Message Transforms
- [Converters](converters.md) - Serialization configuration
- [Error Handling](error-handling.md) - DLQ and error tolerance
- [Exactly-Once](exactly-once.md) - EOS configuration
- [Operations](operations.md) - Monitoring and management
- [Kafka Connect Concepts](../concepts/kafka-connect/index.md) - Conceptual overview
