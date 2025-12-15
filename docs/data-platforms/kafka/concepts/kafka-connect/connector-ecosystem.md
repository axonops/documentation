---
title: "Kafka Connect Connector Ecosystem"
description: "Kafka Connect connector ecosystem. Available connectors for databases, cloud storage, search engines, and messaging systems."
---

# Connector Ecosystem

The Kafka Connect ecosystem includes hundreds of connectors for integrating Kafka with external systems.

---

## Overview

```plantuml
@startuml

skinparam backgroundColor transparent
skinparam componentStyle rectangle

rectangle "Kafka Connect Ecosystem" {

  package "Event Sources" as sources {
    [HTTP/REST]
    [MQTT]
    [JMS/ActiveMQ]
    [Amazon SQS]
    [Amazon Kinesis]
    [Azure Event Hubs]
    [File/Syslog]
  }

  package "Cloud Storage" as storage {
    [Amazon S3]
    [Google Cloud Storage]
    [Azure Blob Storage]
    [HDFS]
    [MinIO]
  }

  package "Database Sinks" as databases {
    [Cassandra]
    [Elasticsearch]
    [OpenSearch]
    [JDBC]
    [MongoDB]
  }

  package "Data Warehouses" as warehouses {
    [Snowflake]
    [BigQuery]
    [Redshift]
    [Databricks]
  }

  rectangle "Kafka" as kafka
}

sources --> kafka
kafka --> storage
kafka --> databases
kafka --> warehouses

@enduml
```

---

## Connector Sources

### Commercial Vendors

| Vendor | Focus | Licensing |
|--------|-------|-----------|
| **Confluent** | Comprehensive catalog | Community + Commercial |
| **Debezium** | CDC connectors | Apache 2.0 |
| **Lenses** | Stream processing | Commercial |
| **StreamSets** | Data integration | Apache 2.0 |

### Community

| Source | Description |
|--------|-------------|
| **Confluent Hub** | Curated connector marketplace |
| **GitHub** | Open source connectors |
| **Maven Central** | Java connector packages |

---

## Event Source Connectors

### HTTP/REST Source

Poll REST APIs and stream responses to Kafka.

| Connector | Maintainer | Features |
|-----------|------------|----------|
| Confluent HTTP Source | Confluent | Pagination, OAuth, rate limiting |
| kafka-connect-http | Community | Basic HTTP polling |

**Use Cases:**
- API data ingestion
- Webhook aggregation
- External service monitoring

### MQTT Source

Bridge MQTT messages to Kafka topics.

| Connector | Maintainer | Features |
|-----------|------------|----------|
| Confluent MQTT Source | Confluent | QoS support, topic mapping |
| kafka-connect-mqtt | Community | Basic MQTT bridge |

**Use Cases:**
- IoT device telemetry
- Sensor data ingestion
- Industrial automation

### JMS/Message Queue Sources

Connect enterprise messaging systems to Kafka.

| Connector | Source System | Features |
|-----------|---------------|----------|
| IBM MQ Source | IBM MQ | Transactional reads |
| ActiveMQ Source | ActiveMQ | JMS compliant |
| RabbitMQ Source | RabbitMQ | AMQP protocol |

**Use Cases:**
- Legacy system integration
- Message queue migration
- Hybrid messaging architectures

### Cloud Event Sources

| Connector | Source | Features |
|-----------|--------|----------|
| Amazon SQS Source | AWS SQS | FIFO support, visibility timeout |
| Amazon Kinesis Source | AWS Kinesis | Shard management |
| Azure Event Hubs Source | Azure | Partition handling |
| Google Pub/Sub Source | GCP | Subscription management |

---

## Cloud Storage Sinks

### Amazon S3

Stream Kafka data to S3 for data lake storage.

| Connector | Maintainer | Features |
|-----------|------------|----------|
| Confluent S3 Sink | Confluent | Parquet, Avro, time partitioning |
| kafka-connect-s3 | Community | Basic S3 writes |

**Capabilities:**
- Multiple output formats (Parquet, Avro, JSON)
- Time-based and field-based partitioning
- Exactly-once with idempotent writes
- Automatic file rotation

### Google Cloud Storage

| Connector | Maintainer | Features |
|-----------|------------|----------|
| Confluent GCS Sink | Confluent | Format support, partitioning |

### Azure Blob Storage

| Connector | Maintainer | Features |
|-----------|------------|----------|
| Confluent Azure Blob Sink | Confluent | Container management |

### HDFS

| Connector | Maintainer | Features |
|-----------|------------|----------|
| Confluent HDFS Sink | Confluent | Kerberos, partitioning |

---

## Database Sinks

### Apache Cassandra

Persist Kafka events to Cassandra tables.

| Connector | Maintainer | Features |
|-----------|------------|----------|
| DataStax Kafka Connector | DataStax | Table mapping, TTL, batching |

**Capabilities:**
- Automatic schema mapping
- Configurable consistency levels
- TTL support
- Batch optimization

### Elasticsearch/OpenSearch

Index Kafka data for search and analytics.

| Connector | Target | Features |
|-----------|--------|----------|
| Confluent Elasticsearch Sink | Elasticsearch | Bulk API, index management |
| OpenSearch Sink | OpenSearch | Index lifecycle |

**Capabilities:**
- Automatic index creation
- Bulk indexing
- Time-based index naming
- Schema detection

### JDBC Sink

Write to any JDBC-compatible database.

| Connector | Maintainer | Features |
|-----------|------------|----------|
| Confluent JDBC Sink | Confluent | Auto-create tables, upsert |

**Supported Databases:**
- PostgreSQL
- MySQL
- Oracle
- SQL Server
- Any JDBC-compliant database

### MongoDB

| Connector | Maintainer | Features |
|-----------|------------|----------|
| MongoDB Kafka Connector | MongoDB | Change streams, sink/source |

---

## Data Warehouse Sinks

### Snowflake

| Connector | Maintainer | Features |
|-----------|------------|----------|
| Snowflake Kafka Connector | Snowflake | Snowpipe, staging |

### Google BigQuery

| Connector | Maintainer | Features |
|-----------|------------|----------|
| Confluent BigQuery Sink | Confluent | Streaming inserts |

### Amazon Redshift

| Connector | Maintainer | Features |
|-----------|------------|----------|
| Confluent Redshift Sink | Confluent | S3 staging, COPY |

### Databricks

| Connector | Maintainer | Features |
|-----------|------------|----------|
| Databricks Connector | Databricks | Delta Lake integration |

---

## Connector Selection Criteria

### Evaluation Factors

| Factor | Considerations |
|--------|----------------|
| **Maintainer** | Vendor support vs community maintenance |
| **License** | Open source vs commercial |
| **Features** | Required capabilities (exactly-once, transforms) |
| **Maturity** | Production usage, known issues |
| **Performance** | Throughput, latency characteristics |
| **Documentation** | Quality of setup and operational guides |

### Licensing Models

| License | Implications |
|---------|--------------|
| **Apache 2.0** | Free for all use |
| **Confluent Community** | Free for self-managed |
| **Confluent Enterprise** | Requires Confluent Platform license |
| **Commercial** | Vendor-specific licensing |

---

## Connector Quality Indicators

### Production Readiness

| Indicator | What to Look For |
|-----------|------------------|
| **Version stability** | 1.0+ releases, semantic versioning |
| **Update frequency** | Regular releases, bug fixes |
| **Issue resolution** | Active issue tracker, responsive maintainers |
| **Documentation** | Configuration reference, examples |
| **Community usage** | Downloads, GitHub stars, Stack Overflow questions |

### Feature Completeness

| Capability | Production Requirement |
|------------|----------------------|
| Exactly-once support | Critical for financial data |
| Dead letter queue | Essential for error handling |
| Schema Registry integration | Required for governed deployments |
| SMT support | Flexibility for transformations |
| Monitoring metrics | Operational visibility |

---

## Finding Connectors

### Confluent Hub

Primary connector marketplace:

```bash
# Install from Confluent Hub
confluent-hub install confluentinc/kafka-connect-s3:latest
```

### Maven Dependencies

```xml
<dependency>
    <groupId>com.datastax.oss</groupId>
    <artifactId>kafka-connect-cassandra-sink</artifactId>
    <version>1.4.0</version>
</dependency>
```

### Manual Installation

```bash
# Download connector
curl -O https://connector-download-url/connector.zip
unzip connector.zip -d /usr/share/kafka/plugins/
```

---

## Related Documentation

- [Kafka Connect Concepts](index.md) - Connect overview
- [Cloud Storage](cloud-storage.md) - Data lake patterns
- [Build vs Buy](build-vs-buy.md) - Decision framework
- [Connectors Guide](../../kafka-connect/connectors/index.md) - Implementation guides
