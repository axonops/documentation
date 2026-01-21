---
title: "Kafka Connect Connectors"
description: "Kafka Connect connector guides. Source and sink connectors for Cassandra, S3, Elasticsearch, and more."
meta:
  - name: keywords
    content: "Kafka Connect connectors, Cassandra sink, S3 sink, Elasticsearch sink"
search:
  boost: 3
---

# Kafka Connect Connectors

Connector guides for common Kafka Connect integrations.

---

## Connector Overview

| Connector | Type | Use Case |
|-----------|------|----------|
| [Cassandra Sink](cassandra.md) | Sink | Persist events to Cassandra |
| [S3 Sink](s3.md) | Sink | Data lake ingestion |
| [Elasticsearch Sink](elasticsearch.md) | Sink | Search indexing |
| [HTTP Source](http-source.md) | Source | REST API ingestion |
| [File Source](file-source.md) | Source | Log file streaming |

---

## Sink Connectors

### Cassandra Sink

Persist Kafka events to Apache Cassandra tables.

```json
{
  "name": "cassandra-sink",
  "config": {
    "connector.class": "com.datastax.oss.kafka.sink.CassandraSinkConnector",
    "tasks.max": "3",
    "topics": "events",
    "contactPoints": "cassandra1,cassandra2,cassandra3",
    "loadBalancing.localDc": "datacenter1",
    "topic.events.keyspace.table.mapping": "analytics.events",
    "topic.events.keyspace.table.consistencyLevel": "LOCAL_QUORUM"
  }
}
```

→ [Cassandra Sink Guide](cassandra.md)

### S3 Sink

Stream events to Amazon S3 in Parquet, Avro, or JSON format.

```json
{
  "name": "s3-sink",
  "config": {
    "connector.class": "io.confluent.connect.s3.S3SinkConnector",
    "tasks.max": "3",
    "topics": "events",
    "s3.bucket.name": "data-lake",
    "s3.region": "us-east-1",
    "format.class": "io.confluent.connect.s3.format.parquet.ParquetFormat",
    "partitioner.class": "io.confluent.connect.storage.partitioner.TimeBasedPartitioner",
    "flush.size": "10000"
  }
}
```

→ [S3 Sink Guide](s3.md)

### Elasticsearch Sink

Index events for search and analytics.

```json
{
  "name": "elasticsearch-sink",
  "config": {
    "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
    "tasks.max": "3",
    "topics": "events",
    "connection.url": "http://elasticsearch:9200",
    "type.name": "_doc",
    "key.ignore": "true",
    "schema.ignore": "true"
  }
}
```

→ [Elasticsearch Sink Guide](elasticsearch.md)

---

## Source Connectors

### HTTP Source

Poll REST APIs and stream responses to Kafka.

```json
{
  "name": "http-source",
  "config": {
    "connector.class": "io.confluent.connect.http.HttpSourceConnector",
    "tasks.max": "1",
    "http.url": "https://api.example.com/events",
    "http.method": "GET",
    "http.headers": "Authorization: Bearer ${token}",
    "kafka.topic": "api-events",
    "http.timer.interval.ms": "60000"
  }
}
```

→ [HTTP Source Guide](http-source.md)

### File Source

Stream log files to Kafka topics.

```json
{
  "name": "file-source",
  "config": {
    "connector.class": "org.apache.kafka.connect.file.FileStreamSourceConnector",
    "tasks.max": "1",
    "file": "/var/log/application.log",
    "topic": "application-logs"
  }
}
```

→ [File Source Guide](file-source.md)

---

## Common Configuration

### Error Handling

```json
{
  "errors.tolerance": "all",
  "errors.deadletterqueue.topic.name": "dlq-connector-name",
  "errors.deadletterqueue.topic.replication.factor": 3,
  "errors.deadletterqueue.context.headers.enable": true,
  "errors.log.enable": true,
  "errors.log.include.messages": true
}
```

### Exactly-Once (Kafka 3.3+)

```json
{
  "exactly.once.support": "required",
  "transaction.boundary": "poll"
}
```

### Schema Registry

```json
{
  "key.converter": "io.confluent.connect.avro.AvroConverter",
  "key.converter.schema.registry.url": "http://schema-registry:8081",
  "value.converter": "io.confluent.connect.avro.AvroConverter",
  "value.converter.schema.registry.url": "http://schema-registry:8081"
}
```

---

## Connector Management

### Create Connector

```bash
curl -X POST http://connect:8083/connectors \
  -H "Content-Type: application/json" \
  -d @connector-config.json
```

### List Connectors

```bash
curl http://connect:8083/connectors
```

### Check Status

```bash
curl http://connect:8083/connectors/my-connector/status
```

### Restart Connector

```bash
curl -X POST http://connect:8083/connectors/my-connector/restart
```

### Delete Connector

```bash
curl -X DELETE http://connect:8083/connectors/my-connector
```

---

## Related Documentation

- [Kafka Connect](../index.md) - Connect framework
- [Kafka Connect Concepts](../../concepts/kafka-connect/index.md) - Conceptual overview
- [Schema Registry](../../schema-registry/index.md) - Schema management
