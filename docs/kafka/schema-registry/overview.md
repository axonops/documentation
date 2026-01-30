---
title: "Schema Registry"
description: "Use AxonOps to connect to your Kafka Schema Registry, browse subjects and versions, collect metrics, and monitor schema operations."
meta:
  - name: keywords
    content: "Schema Registry, Kafka schemas, Avro, Protobuf, JSON Schema, schema monitoring, AxonOps Kafka"
---

# Schema Registry

## What is Schema Registry

Schema Registry provides a centralized repository for managing and validating schemas used by Kafka producers and consumers. It ensures data compatibility and enables schema evolution across your streaming applications.

Common uses:

- Store and version Avro, Protobuf, and JSON schemas.
- Enforce compatibility rules when schemas evolve.
- Provide schema validation for producers and consumers.
- Enable schema discovery across teams and applications.

## Schema Registry in AxonOps

AxonOps connects to your existing Kafka Schema Registry so you can browse schemas, versions, and compatibility from the AxonOps UI. Additionally, AxonOps provides monitoring capabilities through Prometheus metrics scraping. Once configured, you can:

- Browse subjects and view schema versions and details.
- Register new schema versions.
- View Schema Registry metrics on dedicated dashboards.
- Monitor schema counts (registered, deleted).
- Track request rates and latencies.
- Monitor schema types (Avro, JSON, Protobuf).
- View Kafka store operations (consumer lag, flush times).
- Collect Schema Registry logs.

## Prerequisites

- A running Kafka Schema Registry service (Confluent or compatible).
- Network access from the AxonOps agent to the registry endpoint.
- Credentials or tokens if your registry is secured.

## Configure the agent

Enable Schema Registry in the AxonOps agent configuration.

### Environment variables

Configure Schema Registry via environment variables:

```bash
# Schema Registry connection (required for browsing subjects)
SCHEMA_REGISTRY_URL=http://schema-registry:8081

# Schema Registry metrics endpoint (required for monitoring)
SCHEMA_REGISTRY_METRICS_URL=http://schema-registry:8081/metrics

# Optional: Authentication for Schema Registry
SCHEMA_REGISTRY_USERNAME=schema_user
SCHEMA_REGISTRY_PASSWORD=schema_password

# Optional: Authentication for metrics endpoint
SCHEMA_REGISTRY_METRICS_USERNAME=metrics_user
SCHEMA_REGISTRY_METRICS_PASSWORD=metrics_password

# Optional: Scrape timing configuration
SCHEMA_REGISTRY_METRICS_TIMEOUT=30s
SCHEMA_REGISTRY_METRICS_INTERVAL=30s

# Optional: Log file location for log collection
SCHEMA_REGISTRY_LOG_LOCATION=/var/log/kafka/schema-registry.log
```

### YAML configuration

You can also configure Schema Registry in the agent YAML configuration:

```yaml
kafka:
  schema_registry_client:
    enabled: true
    url: "http://schema-registry:8081"
    # Use one of the authentication methods below:
    # username: "schema_user"
    # password: "schema_password"
    # bearerToken: "registry_bearer_token"
    log_location: "/var/log/kafka/schema-registry.log"
    metricsScrapeUrl:
      scrape_endpoint: "http://schema-registry:8081/metrics"
      scrape_username: "metrics_user"
      scrape_password: "metrics_password"
    # Optional TLS settings
    tls:
      enabled: false
      caFilepath: "/etc/ssl/certs/ca.pem"
      certFilepath: "/etc/ssl/certs/client.pem"
      keyFilepath: "/etc/ssl/private/client.key"
      insecureSkipTlsVerify: false
```

After saving the file, restart the AxonOps agent so it can connect.

## Use Schema Registry in AxonOps

1. Open **Kafka** in the AxonOps UI.
2. Select **Schema Registry**.
3. Choose the registry/cluster connection.
4. Monitor **metrics** and **logs** for the registry service.
5. Browse **subjects** and open a subject to view schema **versions** and details.
6. Use **Add schema** to register new schema versions.

Depending on your registry implementation and permissions, AxonOps may allow additional actions (such as changing compatibility or deleting versions). If your registry is read-only, AxonOps will still provide visibility into metrics, logs, subjects, and versions.

## Dashboard metrics

The Schema Registry dashboard displays the following metric categories:

### Schema counts

- **Total registered schemas** - Number of schemas currently registered.
- **Deleted schemas count** - Number of schemas that have been deleted.
- **Master vs Slave role** - Shows whether the node is the primary or replica.

### Schema types

- **Avro schemas** - Count of Avro format schemas.
- **JSON schemas** - Count of JSON format schemas.
- **Protobuf schemas** - Count of Protobuf format schemas.

### Request metrics

- **Request rate** - Number of requests per second.
- **Request latency** - 95th percentile request latency in milliseconds.
- **Error codes** - HTTP error response counts by status code.

### Kafka store operations

- **Connection count** - Number of active producer and consumer connections.
- **Store flush time** - Time taken to flush data to the Kafka store.
- **Failed authentication rate** - Rate of authentication failures.
- **Consumer records consumed rate** - Rate of records consumed from Kafka.
- **Consumer fetch latency** - Average latency for consumer fetch operations.
- **Consumer lag** - Lag in consuming records from Kafka.

## Log collection

When `SCHEMA_REGISTRY_LOG_LOCATION` or `log_location` is configured, AxonOps collects Schema Registry logs and makes them available in the logs viewer. This enables:

- Searching and filtering Schema Registry logs.
- Correlating log events with metrics.
- Troubleshooting schema compatibility issues.

## Troubleshooting

If you see no Schema Registry metrics:

- Confirm `SCHEMA_REGISTRY_METRICS_URL` is set and reachable from the agent host.
- Verify the Schema Registry exposes a `/metrics` endpoint (requires JMX exporter or native metrics).
- Check credentials if authentication is required.
- Ensure the agent is running in Kafka mode with `node_type` set appropriately.

If logs are not appearing:

- Verify `SCHEMA_REGISTRY_LOG_LOCATION` points to the correct log file path.
- Ensure the agent has read permissions for the log file.
- Check that the log file exists and is being written to.

If subjects are not appearing:

- Verify the Schema Registry URL is correct and reachable.
- Check authentication credentials (username/password or bearer token).
- Ensure TLS settings match your Schema Registry configuration.

## Related

- [Schema Registry concepts](../../data-platforms/kafka/schema-registry/index.md)
