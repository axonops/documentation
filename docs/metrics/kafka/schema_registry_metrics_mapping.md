---
title: "AxonOps Kafka Schema Registry Dashboard Metrics Mapping"
description: "Kafka Schema Registry dashboard metrics mapping. Schema counts, request performance, and Kafka store operations."
meta:
  - name: keywords
    content: "Kafka Schema Registry metrics, schema monitoring, registry dashboard"
---

# AxonOps Kafka Schema Registry Dashboard Metrics Mapping

## Overview

The Schema Registry Dashboard provides monitoring of your Kafka Schema Registry service, including schema counts and types, request performance, and underlying Kafka store operations. This dashboard is available when the AxonOps agent is configured with Schema Registry metrics scraping enabled.

For setup instructions, see [Schema Registry (AxonOps)](../../kafka/schema-registry/overview.md).

## Metrics Mapping

| Dashboard Metric | Description | Attributes |
|-----------------|-----------|-------------|
| **Schema Counts** |
| `kafka_schema_registry_registered_count_registered_count` | Total number of registered schemas | `dc`, `rack`, `hostname` |
| `kafka_schema_registry_deleted_count_deleted_count` | Number of deleted schemas | `dc`, `rack`, `hostname` |
| `kafka_schema_registry_master_slave_role_master_slave_role` | Node role (1 = primary, 0 = replica) | `dc`, `rack`, `hostname`, `host_id` |
| **Schema Types** |
| `kafka_schema_registry_avro_schemas_created_avro_schemas` | Count of Avro format schemas | `dc`, `rack`, `hostname` |
| `kafka_schema_registry_json_schemas_created_json_schemas` | Count of JSON format schemas | `dc`, `rack`, `hostname` |
| `kafka_schema_registry_protobuf_schemas_created_protobuf_schemas` | Count of Protobuf format schemas | `dc`, `rack`, `hostname` |
| **Request Metrics** |
| `kafka_schema_registry_jersey_metrics_request_rate` | Requests per second | `dc`, `rack`, `hostname` |
| `kafka_schema_registry_jersey_metrics_request_latency_95` | 95th percentile request latency (ms) | `dc`, `rack`, `hostname` |
| `kafka_schema_registry_jersey_metrics_request_error_count` | Error responses by HTTP status code | `dc`, `rack`, `hostname`, `http_status_code` |
| **Kafka Store Operations** |
| `kafka_producer_producer_metrics_connection_count` | Active producer connections to Kafka | `dc`, `rack`, `hostname` |
| `kafka_consumer_consumer_metrics_connection_count` | Active consumer connections to Kafka | `dc`, `rack`, `hostname` |
| `kafka_producer_producer_metrics_flush_time_ns` | Time to flush data to Kafka store (ns) | `dc`, `rack`, `hostname`, `client_id` |
| `kafka_producer_producer_metrics_failed_authentication_rate` | Rate of failed authentication attempts | `dc`, `rack`, `hostname` |
| `kafka_consumer_consumer_fetch_manager_metrics_records_consumed_rate` | Rate of records consumed from Kafka | `dc`, `rack`, `hostname` |
| `kafka_consumer_consumer_fetch_manager_metrics_fetch_latency_avg` | Average consumer fetch latency (ms) | `dc`, `rack`, `hostname` |
| `kafka_consumer_consumer_fetch_manager_metrics_records_lag` | Consumer lag in records | `dc`, `rack`, `hostname` |

## Query Examples

### Schema Counts
```promql
// Total registered schemas
kafka_schema_registry_registered_count_registered_count{dc=~'$dc',rack=~'$rack',hostname=~'$hostname'}

// Deleted schemas
kafka_schema_registry_deleted_count_deleted_count{dc=~'$dc',rack=~'$rack',hostname=~'$hostname'}

// Primary vs replica role
kafka_schema_registry_master_slave_role_master_slave_role{dc=~'$dc',rack=~'$rack',hostname=~'$hostname'}
```

### Schema Types
```promql
// Avro schemas
kafka_schema_registry_avro_schemas_created_avro_schemas{dc=~'$dc',rack=~'$rack',hostname=~'$hostname'}

// JSON schemas
kafka_schema_registry_json_schemas_created_json_schemas{dc=~'$dc',rack=~'$rack',hostname=~'$hostname'}

// Protobuf schemas
kafka_schema_registry_protobuf_schemas_created_protobuf_schemas{dc=~'$dc',rack=~'$rack',hostname=~'$hostname'}
```

### Request Performance
```promql
// Request rate
kafka_schema_registry_jersey_metrics_request_rate{dc=~'$dc',rack=~'$rack',hostname=~'$hostname'}

// Request latency (p95)
kafka_schema_registry_jersey_metrics_request_latency_95{dc=~'$dc',rack=~'$rack',hostname=~'$hostname'}

// Error counts by HTTP status code
kafka_schema_registry_jersey_metrics_request_error_count{dc=~'$dc',rack=~'$rack',hostname=~'$hostname'}
```

### Kafka Store Operations
```promql
// Total connections (producers + consumers)
sum(kafka_producer_producer_metrics_connection_count{dc=~'$dc',rack=~'$rack',hostname=~'$hostname'})
sum(kafka_consumer_consumer_metrics_connection_count{dc=~'$dc',rack=~'$rack',hostname=~'$hostname'})

// Store flush time
kafka_producer_producer_metrics_flush_time_ns{dc=~'$dc',rack=~'$rack',hostname=~'$hostname'}

// Failed authentication rate
kafka_producer_producer_metrics_failed_authentication_rate{dc=~'$dc',rack=~'$rack',hostname=~'$hostname'}

// Consumer records consumed rate
sum(kafka_consumer_consumer_fetch_manager_metrics_records_consumed_rate{dc=~'$dc',rack=~'$rack',hostname=~'$hostname'})

// Consumer fetch latency
avg(kafka_consumer_consumer_fetch_manager_metrics_fetch_latency_avg{dc=~'$dc',rack=~'$rack',hostname=~'$hostname'})

// Consumer lag
sum(kafka_consumer_consumer_fetch_manager_metrics_records_lag{dc=~'$dc',rack=~'$rack',hostname=~'$hostname'})
```

## Panel Organization

**Schema Counts**

   - Total registered schemas
   - Deleted schemas count
   - Master vs Slave role

**Schema Types**

   - Avro schemas
   - JSON schemas
   - Protobuf schemas

**Requests**

   - Request latency (p95)
   - Request rate
   - Error codes (by HTTP status)

**Kafka Store Operations**

   - Failed authentication rate
   - Store flush time (ns)
   - Connection count (producers and consumers)
   - Consumer fetch latency (avg)
   - Consumer records consumed rate
   - Consumer lag

## Filters

- **dc**: Filter by datacenter

- **rack**: Filter by rack

- **hostname**: Filter by specific Schema Registry node

## Best Practices

**Schema Growth Monitoring**

   - Track registered schema count over time for capacity planning
   - A rising deleted count may indicate schema churn or cleanup activity
   - Monitor schema type distribution to understand format adoption

**Request Performance**

   - p95 latency should remain low (typically under 50ms)
   - Rising error counts may indicate compatibility violations or client issues
   - Monitor request rate to understand API usage patterns

**Kafka Store Health**

   - Consumer lag should remain near zero for a healthy registry
   - High flush times may indicate Kafka broker issues
   - Failed authentication rate should be zero under normal operation
   - Connection count changes may indicate registry restarts or scaling events

**Troubleshooting**

   - No metrics appearing: Verify `SCHEMA_REGISTRY_METRICS_URL` is configured and reachable
   - High consumer lag: Check Kafka broker health and Schema Registry logs
   - Rising error counts: Review Schema Registry logs for compatibility or serialization errors
