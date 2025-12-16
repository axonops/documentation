---
title: "Elasticsearch Sink Connector"
description: "Kafka Connect Elasticsearch Sink connector. Configuration, index mapping, and search integration."
meta:
  - name: keywords
    content: "Kafka Elasticsearch connector, Elasticsearch sink, search indexing, Kafka to Elasticsearch"
---

# Elasticsearch Sink Connector

Stream Kafka events to Elasticsearch for full-text search, log analytics, and real-time dashboards.

---

## Overview

The Elasticsearch Sink Connector writes Kafka records to Elasticsearch indices, supporting:

- Automatic index creation and mapping
- Document ID generation from record keys
- Bulk indexing for performance
- Schema-less and schema-aware modes

---

## Installation

```bash
# Confluent Hub
confluent-hub install confluentinc/kafka-connect-elasticsearch:latest

# Manual installation
curl -O https://packages.confluent.io/archive/7.5/kafka-connect-elasticsearch-7.5.0.zip
unzip kafka-connect-elasticsearch-7.5.0.zip -d /usr/share/kafka/plugins/
```

---

## Basic Configuration

```json
{
  "name": "elasticsearch-sink",
  "config": {
    "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
    "tasks.max": "3",
    "topics": "events",

    "connection.url": "http://elasticsearch:9200",
    "type.name": "_doc",

    "key.ignore": "false",
    "schema.ignore": "true"
  }
}
```

---

## Connection Settings

### Single Node

```json
{
  "connection.url": "http://elasticsearch:9200"
}
```

### Cluster

```json
{
  "connection.url": "http://es1:9200,http://es2:9200,http://es3:9200"
}
```

### Authentication

```json
{
  "connection.url": "https://elasticsearch:9200",
  "connection.username": "${secrets:es/username}",
  "connection.password": "${secrets:es/password}"
}
```

### SSL/TLS

```json
{
  "elastic.security.protocol": "SSL",
  "elastic.https.ssl.keystore.location": "/path/to/keystore.jks",
  "elastic.https.ssl.keystore.password": "${secrets:ssl/keystore-password}",
  "elastic.https.ssl.truststore.location": "/path/to/truststore.jks",
  "elastic.https.ssl.truststore.password": "${secrets:ssl/truststore-password}"
}
```

---

## Index Configuration

### Index Naming

```json
{
  "topics": "events",
  "index.name.format": "${topic}"
}
```

Records from topic `events` write to index `events`.

### Custom Index Names

```json
{
  "topics": "user-events,system-events",
  "index.name.format": "logs-${topic}"
}
```

### Time-Based Indices

```json
{
  "index.name.format": "${topic}-${timestamp}",
  "index.name.format.datetime.pattern": "yyyy-MM-dd"
}
```

Creates indices like `events-2024-01-15`.

---

## Document ID

### From Record Key

```json
{
  "key.ignore": "false"
}
```

Uses the Kafka record key as the Elasticsearch document `_id`.

### Auto-Generated

```json
{
  "key.ignore": "true"
}
```

Elasticsearch generates document IDs automatically.

### From Record Field

Use SMT to extract document ID:

```json
{
  "transforms": "extractId",
  "transforms.extractId.type": "org.apache.kafka.connect.transforms.ValueToKey",
  "transforms.extractId.fields": "event_id"
}
```

---

## Schema Handling

### Schema-less Mode

For schemaless JSON data:

```json
{
  "schema.ignore": "true",
  "value.converter": "org.apache.kafka.connect.json.JsonConverter",
  "value.converter.schemas.enable": "false"
}
```

### Schema-Aware Mode

With Schema Registry:

```json
{
  "schema.ignore": "false",
  "value.converter": "io.confluent.connect.avro.AvroConverter",
  "value.converter.schema.registry.url": "http://schema-registry:8081"
}
```

---

## Mapping Configuration

### Dynamic Mapping

Elasticsearch creates mappings automatically based on data types.

### Explicit Mapping

Create index mapping before starting connector:

```json
PUT /events
{
  "mappings": {
    "properties": {
      "event_id": {"type": "keyword"},
      "event_type": {"type": "keyword"},
      "timestamp": {"type": "date", "format": "epoch_millis"},
      "user_id": {"type": "keyword"},
      "message": {"type": "text"},
      "metadata": {"type": "object", "dynamic": true}
    }
  }
}
```

---

## Bulk Operations

### Batch Settings

```json
{
  "batch.size": "2000",
  "max.buffered.records": "20000",
  "linger.ms": "1000"
}
```

| Property | Description | Default |
|----------|-------------|:-------:|
| `batch.size` | Records per bulk request | 2000 |
| `max.buffered.records` | Max records in memory | 20000 |
| `linger.ms` | Wait time before flush | 1 |

### Flush Settings

```json
{
  "flush.timeout.ms": "180000",
  "max.in.flight.requests": "5"
}
```

---

## Error Handling

### Retry Configuration

```json
{
  "max.retries": "5",
  "retry.backoff.ms": "100"
}
```

### Dead Letter Queue

```json
{
  "errors.tolerance": "all",
  "errors.deadletterqueue.topic.name": "dlq-elasticsearch-sink",
  "errors.deadletterqueue.topic.replication.factor": 3,
  "errors.deadletterqueue.context.headers.enable": true
}
```

### Drop Invalid Records

```json
{
  "behavior.on.malformed.documents": "warn",
  "behavior.on.null.values": "delete"
}
```

| Behavior | Description |
|----------|-------------|
| `fail` | Stop connector on error |
| `warn` | Log warning and skip |
| `ignore` | Silently skip |
| `delete` | Delete document (null values) |

---

## Performance Tuning

### Parallelism

```json
{
  "tasks.max": "6"
}
```

Match number of topic partitions.

### Bulk Optimization

```json
{
  "batch.size": "5000",
  "max.buffered.records": "50000",
  "linger.ms": "5000",
  "max.in.flight.requests": "10"
}
```

### Compression

```json
{
  "compression.type": "gzip"
}
```

---

## Complete Example

```json
{
  "name": "events-to-elasticsearch",
  "config": {
    "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
    "tasks.max": "6",
    "topics": "events,logs",

    "connection.url": "https://es1:9200,https://es2:9200,https://es3:9200",
    "connection.username": "${secrets:es/username}",
    "connection.password": "${secrets:es/password}",

    "type.name": "_doc",
    "key.ignore": "false",
    "schema.ignore": "true",

    "index.name.format": "${topic}-${timestamp}",
    "index.name.format.datetime.pattern": "yyyy-MM-dd",

    "batch.size": "5000",
    "max.buffered.records": "50000",
    "linger.ms": "5000",
    "flush.timeout.ms": "180000",

    "max.retries": "5",
    "retry.backoff.ms": "100",

    "behavior.on.malformed.documents": "warn",
    "behavior.on.null.values": "delete",

    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",

    "errors.tolerance": "all",
    "errors.deadletterqueue.topic.name": "dlq-elasticsearch-sink",
    "errors.deadletterqueue.topic.replication.factor": 3
  }
}
```

---

## Index Lifecycle Management

Configure ILM policy in Elasticsearch:

```json
PUT _ilm/policy/logs-policy
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": {"max_size": "50gb", "max_age": "1d"}
        }
      },
      "warm": {
        "min_age": "7d",
        "actions": {
          "shrink": {"number_of_shards": 1},
          "forcemerge": {"max_num_segments": 1}
        }
      },
      "delete": {
        "min_age": "30d",
        "actions": {"delete": {}}
      }
    }
  }
}
```

---

## Monitoring

### Connector Metrics

```bash
# Check connector status
curl http://connect:8083/connectors/elasticsearch-sink/status

# Check task status
curl http://connect:8083/connectors/elasticsearch-sink/tasks/0/status
```

### Elasticsearch Metrics

```bash
# Index stats
curl http://elasticsearch:9200/events/_stats

# Cluster health
curl http://elasticsearch:9200/_cluster/health
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Connection refused | Network/firewall | Verify Elasticsearch is reachable |
| Authentication failed | Invalid credentials | Check username/password |
| Mapping conflict | Type mismatch | Review index mapping |
| Bulk rejection | Queue full | Reduce batch size or add nodes |
| High latency | Slow indexing | Tune bulk settings |

---

## Related Documentation

- [Connectors Overview](index.md) - All connectors
- [Kafka Connect](../index.md) - Connect framework
- [Transforms](../transforms.md) - Single Message Transforms
