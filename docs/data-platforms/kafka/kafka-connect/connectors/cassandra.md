---
title: "Cassandra Sink Connector"
description: "Kafka Connect Cassandra Sink connector. Configuration, table mapping, and production deployment."
meta:
  - name: keywords
    content: "Kafka Cassandra connector, Cassandra sink, DataStax connector"
search:
  boost: 3
---

# Cassandra Sink Connector

Stream Kafka events to Apache Cassandra tables using the DataStax Kafka Connector.

---

## Overview

The Cassandra Sink Connector writes Kafka records to Cassandra tables, supporting:

- Automatic table mapping from topic structure
- Multiple consistency levels
- TTL configuration
- Batch writes for performance
- Exactly-once semantics (idempotent upserts)

---

## Installation

### Download

```bash
# Download connector
curl -O https://downloads.datastax.com/kafka/kafka-connect-cassandra-sink.tar.gz
tar -xzf kafka-connect-cassandra-sink.tar.gz

# Copy to Connect plugin path
cp -r kafka-connect-cassandra-sink /usr/share/kafka/plugins/
```

### Docker

```yaml
services:
  kafka-connect:
    image: confluentinc/cp-kafka-connect:7.5.0
    environment:
      CONNECT_PLUGIN_PATH: /usr/share/kafka/plugins
    volumes:
      - ./kafka-connect-cassandra-sink:/usr/share/kafka/plugins/cassandra-sink
```

---

## Basic Configuration

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
    "topic.events.keyspace.table.consistencyLevel": "LOCAL_QUORUM"
  }
}
```

---

## Connection Settings

| Property | Description | Default |
|----------|-------------|---------|
| `contactPoints` | Cassandra contact points | Required |
| `port` | CQL native port | 9042 |
| `loadBalancing.localDc` | Local datacenter for routing | Required |
| `maxConcurrentRequests` | Max concurrent requests | 500 |
| `maxNumberOfRecordsInBatch` | Batch size | 32 |

### Authentication

```json
{
  "auth.provider": "PLAIN",
  "auth.username": "cassandra_user",
  "auth.password": "cassandra_password"
}
```

### SSL/TLS

```json
{
  "ssl.provider": "JDK",
  "ssl.hostnameValidation": true,
  "ssl.keystore.path": "/path/to/keystore.jks",
  "ssl.keystore.password": "keystore_password",
  "ssl.truststore.path": "/path/to/truststore.jks",
  "ssl.truststore.password": "truststore_password"
}
```

---

## Table Mapping

### Simple Mapping

Map topic fields directly to table columns.

**Kafka Message:**
```json
{
  "event_id": "abc123",
  "event_type": "click",
  "timestamp": 1705312800000,
  "user_id": "user456"
}
```

**Cassandra Table:**
```sql
CREATE TABLE analytics.events_by_time (
    event_date date,
    event_time timestamp,
    event_id text,
    event_type text,
    user_id text,
    PRIMARY KEY ((event_date), event_time, event_id)
) WITH CLUSTERING ORDER BY (event_time DESC);
```

**Configuration:**
```json
{
  "topic.events.keyspace.table.mapping": "analytics.events_by_time",
  "topic.events.analytics.events_by_time.mapping": "event_id=value.event_id, event_type=value.event_type, event_time=value.timestamp, user_id=value.user_id, event_date=now()"
}
```

### Mapping Functions

| Function | Description | Example |
|----------|-------------|---------|
| `value.field` | Extract from value | `value.user_id` |
| `key.field` | Extract from key | `key.partition_key` |
| `header.field` | Extract from header | `header.trace_id` |
| `now()` | Current timestamp | `event_time=now()` |

### Time-Based Partitioning

```json
{
  "topic.events.analytics.events_by_time.mapping": "event_date=value.timestamp:toDate, event_time=value.timestamp, event_id=value.event_id"
}
```

---

## Consistency Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| `LOCAL_ONE` | One replica in local DC | High throughput, lower durability |
| `LOCAL_QUORUM` | Majority in local DC | Balanced durability/performance |
| `QUORUM` | Majority across all DCs | Strong consistency |
| `ALL` | All replicas | Maximum durability |

```json
{
  "topic.events.keyspace.table.consistencyLevel": "LOCAL_QUORUM"
}
```

---

## TTL Configuration

Automatically expire records after a specified time.

```json
{
  "topic.events.keyspace.table.ttl": "86400",
  "topic.events.keyspace.table.ttlTimeUnit": "SECONDS"
}
```

| Time Unit | Description |
|-----------|-------------|
| `SECONDS` | TTL in seconds |
| `MINUTES` | TTL in minutes |
| `HOURS` | TTL in hours |
| `DAYS` | TTL in days |

---

## Error Handling

### Dead Letter Queue

```json
{
  "errors.tolerance": "all",
  "errors.deadletterqueue.topic.name": "dlq-cassandra-sink",
  "errors.deadletterqueue.topic.replication.factor": 3,
  "errors.deadletterqueue.context.headers.enable": true
}
```

### Retry Configuration

```json
{
  "maxNumberOfRecordsInBatch": 32,
  "queryExecutionTimeout": 30,
  "connectionPoolLocalSize": 4
}
```

---

## Performance Tuning

### Batch Settings

```json
{
  "maxNumberOfRecordsInBatch": 100,
  "maxConcurrentRequests": 1000
}
```

### Task Parallelism

```json
{
  "tasks.max": "6"
}
```

Recommendation: Set `tasks.max` equal to or greater than the number of topic partitions for maximum parallelism.

### Connection Pool

```json
{
  "connectionPoolLocalSize": 4,
  "connectionPoolRemoteSize": 2
}
```

---

## Complete Example

```json
{
  "name": "events-to-cassandra",
  "config": {
    "connector.class": "com.datastax.oss.kafka.sink.CassandraSinkConnector",
    "tasks.max": "6",
    "topics": "events",

    "contactPoints": "cass1.example.com,cass2.example.com,cass3.example.com",
    "loadBalancing.localDc": "datacenter1",
    "port": "9042",

    "auth.provider": "PLAIN",
    "auth.username": "${secrets:cassandra/username}",
    "auth.password": "${secrets:cassandra/password}",

    "ssl.provider": "JDK",
    "ssl.truststore.path": "/etc/kafka-connect/ssl/truststore.jks",
    "ssl.truststore.password": "${secrets:ssl/truststore-password}",

    "topic.events.keyspace.table.mapping": "analytics.events_by_time",
    "topic.events.analytics.events_by_time.mapping": "event_date=value.timestamp:toDate, event_time=value.timestamp, event_id=value.event_id, event_type=value.event_type, user_id=value.user_id, payload=value.payload",
    "topic.events.keyspace.table.consistencyLevel": "LOCAL_QUORUM",
    "topic.events.keyspace.table.ttl": "365",
    "topic.events.keyspace.table.ttlTimeUnit": "DAYS",

    "maxNumberOfRecordsInBatch": 100,
    "maxConcurrentRequests": 1000,

    "errors.tolerance": "all",
    "errors.deadletterqueue.topic.name": "dlq-cassandra-sink",
    "errors.deadletterqueue.topic.replication.factor": 3
  }
}
```

---

## Monitoring

### Connector Metrics

| Metric | Description |
|--------|-------------|
| `connector-metrics/record-send-rate` | Records sent per second |
| `connector-metrics/record-error-rate` | Error rate |
| `connector-metrics/batch-size-avg` | Average batch size |

### Health Check

```bash
# Check connector status
curl http://connect:8083/connectors/cassandra-sink/status

# Check task status
curl http://connect:8083/connectors/cassandra-sink/tasks/0/status
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Connection timeout | Network/firewall | Verify connectivity to contact points |
| Authentication failed | Invalid credentials | Check username/password |
| WriteTimeoutException | Slow cluster | Increase `queryExecutionTimeout` |
| High error rate | Schema mismatch | Verify table mapping |

---

## Related Documentation

- [Connectors Overview](index.md) - All connectors
- [Kafka Connect](../index.md) - Connect framework
- [Schema Registry](../../schema-registry/index.md) - Schema management
