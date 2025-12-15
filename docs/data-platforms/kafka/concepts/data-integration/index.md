---
title: "Kafka Data Integration"
description: "Data integration patterns with Apache Kafka. ETL, ELT, event streaming pipelines, and Kafka Connect patterns."
meta:
  - name: keywords
    content: "Kafka integration, ETL, ELT, data pipeline, Kafka Connect, event streaming"
---

# Data Integration

Patterns for integrating Apache Kafka with data systems across the enterprise.

---

## Integration Approaches

| Approach | Description | Use Case |
|----------|-------------|----------|
| **Kafka Connect** | Declarative connectors | Standard integrations |
| **Custom Producers/Consumers** | Application code | Complex logic |
| **Kafka Streams** | Stream processing | Transformations |

---

## ETL vs ELT with Kafka

### Traditional ETL

```plantuml
@startuml

rectangle "Source" as src
rectangle "ETL Tool" as etl
database "Data Warehouse" as dw

src -> etl : Extract
etl -> etl : Transform
etl -> dw : Load

note bottom of etl
  Transform before loading
  Batch processing
  Tool-specific
end note

@enduml
```

### Kafka-Based Streaming ETL

```plantuml
@startuml

rectangle "Sources" as src {
  collections "Application Logs" as logs
  cloud "REST APIs" as api
}

rectangle "Kafka" as kafka {
  queue "Raw Events" as raw
  queue "Transformed" as transformed
}

rectangle "Kafka Streams" as streams
database "Cassandra" as sink

src -> raw : Kafka Connect
raw -> streams : consume
streams -> transformed : produce
transformed -> sink : Kafka Connect

note bottom of streams
  Transform in motion
  Real-time processing
  Scalable
end note

@enduml
```

### ELT Pattern

```plantuml
@startuml

rectangle "Sources" as src
queue "Kafka" as kafka
database "Data Lake\n(S3)" as lake
rectangle "Transform Engine\n(Spark/Trino)" as transform
database "Data Warehouse" as dw

src -> kafka : Extract
kafka -> lake : Load (raw)
lake -> transform : Transform
transform -> dw : Load (modeled)

note bottom of lake
  Store raw data first
  Transform on demand
  Schema-on-read
end note

@enduml
```

---

## Streaming Pipeline Architecture

```plantuml
@startuml

rectangle "Event Sources" as sources {
  collections "App Logs" as logs
  cloud "APIs" as api
  node "IoT" as iot
}

rectangle "Ingestion Layer" as ingest {
  rectangle "Kafka Connect\nSource Connectors" as src_conn
}

rectangle "Kafka Cluster" as kafka {
  queue "raw-events" as raw
  queue "enriched-events" as enriched
  queue "aggregated-events" as agg
}

rectangle "Processing Layer" as process {
  rectangle "Kafka Streams" as streams
}

rectangle "Serving Layer" as serve {
  rectangle "Kafka Connect\nSink Connectors" as sink_conn
}

rectangle "Data Sinks" as sinks {
  database "Cassandra" as cass
  storage "S3" as s3
  database "Elasticsearch" as es
}

sources -> src_conn
src_conn -> raw

raw -> streams
streams -> enriched
streams -> agg

enriched -> sink_conn
agg -> sink_conn

sink_conn -> cass
sink_conn -> s3
sink_conn -> es

@enduml
```

---

## Integration Patterns

### Fan-Out Pattern

One source feeds multiple sinks for different use cases.

```plantuml
@startuml

queue "events" as events

rectangle "Kafka Connect Sinks" as sinks {
  rectangle "S3 Sink\n(archive)" as s3
  rectangle "Cassandra Sink\n(operational)" as cass
  rectangle "ES Sink\n(search)" as es
}

events --> s3
events --> cass
events --> es

note bottom of sinks
  Same events serve
  multiple purposes
end note

@enduml
```

### Fan-In Pattern

Multiple sources aggregate into unified topics.

```plantuml
@startuml

rectangle "Regional Sources" as regions {
  collections "US Events" as us
  collections "EU Events" as eu
  collections "APAC Events" as apac
}

queue "global-events" as global

us --> global
eu --> global
apac --> global

note bottom of global
  Unified view of
  all regional data
end note

@enduml
```

### Enrichment Pattern

Enrich events with reference data.

```plantuml
@startuml

queue "raw-orders" as raw
queue "customer-table" as customers
rectangle "Kafka Streams\nJoin" as join
queue "enriched-orders" as enriched

raw -> join
customers -> join : KTable
join -> enriched

note right of join
  Join order events with
  customer reference data
end note

@enduml
```

---

## Kafka Connect Patterns

### Source Connector Patterns

| Pattern | Description | Example |
|---------|-------------|---------|
| **Polling** | Periodically fetch data | HTTP Source |
| **Push** | Receive pushed events | MQTT Source |
| **Log tailing** | Stream log files | FileStream Source |
| **Message bridge** | Bridge message systems | JMS Source |

### Sink Connector Patterns

| Pattern | Description | Example |
|---------|-------------|---------|
| **Upsert** | Insert or update records | Cassandra Sink |
| **Append** | Append-only writes | S3 Sink |
| **Index** | Update search index | Elasticsearch Sink |
| **Time-partitioned** | Partition by time | S3 Sink with partitioner |

### Exactly-Once Sink Pattern

```plantuml
@startuml

queue "events" as events
rectangle "Cassandra Sink\n(idempotent)" as sink
database "Cassandra" as cass

events -> sink : consume
sink -> cass : upsert by key

note right of sink
  Idempotent writes:
  Same key = same result
  regardless of retries
end note

@enduml
```

---

## Data Lake Integration

### S3 Sink Configuration

```json
{
  "name": "s3-sink",
  "config": {
    "connector.class": "io.confluent.connect.s3.S3SinkConnector",
    "tasks.max": "3",
    "topics": "events",
    "s3.bucket.name": "data-lake",
    "s3.region": "us-east-1",
    "storage.class": "io.confluent.connect.s3.storage.S3Storage",
    "format.class": "io.confluent.connect.s3.format.parquet.ParquetFormat",
    "partitioner.class": "io.confluent.connect.storage.partitioner.TimeBasedPartitioner",
    "partition.duration.ms": "3600000",
    "path.format": "'year'=YYYY/'month'=MM/'day'=dd/'hour'=HH",
    "rotate.interval.ms": "600000",
    "flush.size": "10000"
  }
}
```

### Resulting S3 Structure

```
s3://data-lake/topics/events/
  year=2024/
    month=01/
      day=15/
        hour=10/
          events+0+0000000000.parquet
          events+1+0000000000.parquet
        hour=11/
          events+0+0000000100.parquet
```

---

## Cassandra Integration

### Cassandra Sink Configuration

```json
{
  "name": "cassandra-sink",
  "config": {
    "connector.class": "com.datastax.oss.kafka.sink.CassandraSinkConnector",
    "tasks.max": "3",
    "topics": "events",
    "contactPoints": "cassandra1,cassandra2,cassandra3",
    "loadBalancing.localDc": "datacenter1",
    "port": "9042",
    "topic.events.keyspace.table.mapping": "analytics.events_by_time",
    "topic.events.keyspace.table.consistencyLevel": "LOCAL_QUORUM",
    "topic.events.keyspace.table.ttlTimeUnit": "DAYS",
    "topic.events.keyspace.table.ttl": "365"
  }
}
```

### Target Table Design

```sql
CREATE TABLE analytics.events_by_time (
    event_date date,
    event_time timestamp,
    event_id uuid,
    event_type text,
    payload text,
    PRIMARY KEY ((event_date), event_time, event_id)
) WITH CLUSTERING ORDER BY (event_time DESC);
```

---

## Best Practices

### Schema Management

| Practice | Rationale |
|----------|-----------|
| Use Schema Registry | Ensure compatibility across pipeline |
| Prefer Avro or Protobuf | Compact, schema evolution support |
| Version schemas explicitly | Track changes, enable rollback |

### Error Handling

| Strategy | Implementation |
|----------|----------------|
| Dead letter queue | Route failed records for investigation |
| Error tolerance | Configure `errors.tolerance=all` |
| Monitoring | Alert on DLQ growth |

### Performance

| Optimization | Configuration |
|--------------|---------------|
| Batching | Increase `batch.size`, `linger.ms` |
| Compression | Use `compression.type=lz4` |
| Parallelism | Increase `tasks.max` |
| Partitioning | Align with downstream partitioning |

---

## Related Documentation

- [Kafka Connect](../../kafka-connect/index.md) - Technical reference
- [Kafka Connect Concepts](../kafka-connect/index.md) - Connector ecosystem
- [Architecture Patterns](../architecture-patterns/index.md) - Event-driven patterns
- [Schema Registry](../../schema-registry/index.md) - Schema management
