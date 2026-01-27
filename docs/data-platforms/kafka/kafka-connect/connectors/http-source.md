---
title: "HTTP Source Connector"
description: "Kafka Connect HTTP Source connector for polling REST APIs. Configure endpoints, authentication, pagination, rate limiting, and stream responses to Kafka."
meta:
  - name: keywords
    content: "Kafka HTTP source connector, REST API source, webhook connector, HTTP polling"
---

# HTTP Source Connector

Poll REST APIs and stream responses to Kafka topics for integration with external services.

---

## Overview

The HTTP Source Connector polls HTTP endpoints and writes responses to Kafka, supporting:

- Scheduled polling at configurable intervals
- Multiple authentication methods
- Pagination handling
- Response parsing and transformation

---

## Installation

```bash
# Confluent Hub
confluent-hub install confluentinc/kafka-connect-http:latest

# Manual installation
curl -O https://packages.confluent.io/archive/7.5/kafka-connect-http-7.5.0.zip
unzip kafka-connect-http-7.5.0.zip -d /usr/share/kafka/plugins/
```

---

## Basic Configuration

```json
{
  "name": "http-source",
  "config": {
    "connector.class": "io.confluent.connect.http.HttpSourceConnector",
    "tasks.max": "1",

    "http.url": "https://api.example.com/events",
    "http.method": "GET",
    "kafka.topic": "api-events",

    "http.timer.interval.ms": "60000"
  }
}
```

---

## HTTP Settings

### Request Configuration

```json
{
  "http.url": "https://api.example.com/data",
  "http.method": "GET",
  "http.headers": "Accept: application/json, X-API-Version: v2"
}
```

| Property | Description | Default |
|----------|-------------|:-------:|
| `http.url` | Endpoint URL | Required |
| `http.method` | HTTP method | GET |
| `http.headers` | Request headers | None |
| `http.request.body` | Request body (POST/PUT) | None |

### POST Request

```json
{
  "http.url": "https://api.example.com/query",
  "http.method": "POST",
  "http.headers": "Content-Type: application/json",
  "http.request.body": "{\"query\": \"SELECT * FROM events\"}"
}
```

---

## Authentication

### API Key

```json
{
  "http.headers": "Authorization: Bearer ${secrets:api/token}"
}
```

### Basic Authentication

```json
{
  "http.auth.type": "BASIC",
  "http.auth.user": "${secrets:api/username}",
  "http.auth.password": "${secrets:api/password}"
}
```

### OAuth 2.0

```json
{
  "http.auth.type": "OAUTH2",
  "http.oauth2.token.url": "https://auth.example.com/oauth/token",
  "http.oauth2.client.id": "${secrets:oauth/client-id}",
  "http.oauth2.client.secret": "${secrets:oauth/client-secret}",
  "http.oauth2.scope": "read:events"
}
```

---

## Polling Configuration

### Fixed Interval

```json
{
  "http.timer.interval.ms": "60000"
}
```

Poll every 60 seconds.

### Cron Schedule

```json
{
  "http.timer.type": "cron",
  "http.timer.cron.expression": "0 */5 * * * ?"
}
```

Poll every 5 minutes.

### Offset Tracking

Track last processed item for incremental polling:

```json
{
  "http.offset.mode": "TIMESTAMP",
  "http.offset.field": "updated_at",
  "http.initial.offset": "2024-01-01T00:00:00Z"
}
```

---

## Response Handling

### JSON Response

```json
{
  "http.response.format": "JSON",
  "http.response.records.path": "$.data[*]"
}
```

Extract records from JSON array at `$.data`.

### Array Response

```json
{
  "http.response.format": "JSON",
  "http.response.records.path": "$[*]"
}
```

Process top-level array elements.

### Single Record

```json
{
  "http.response.format": "JSON",
  "http.response.records.path": "$"
}
```

Treat entire response as single record.

---

## Pagination

### Offset-Based

```json
{
  "http.pagination.type": "OFFSET",
  "http.pagination.offset.param": "offset",
  "http.pagination.limit.param": "limit",
  "http.pagination.limit.value": "100"
}
```

URL: `https://api.example.com/events?offset=0&limit=100`

### Cursor-Based

```json
{
  "http.pagination.type": "CURSOR",
  "http.pagination.cursor.param": "cursor",
  "http.pagination.cursor.path": "$.next_cursor"
}
```

Extract cursor from response for next request.

### Link Header

```json
{
  "http.pagination.type": "LINK_HEADER"
}
```

Follow `Link` header for pagination (GitHub API style).

---

## Error Handling

### Retry Configuration

```json
{
  "http.retry.max.attempts": "5",
  "http.retry.backoff.ms": "1000",
  "http.retry.backoff.max.ms": "60000"
}
```

### Error Responses

```json
{
  "http.response.error.codes": "400,401,403,404,500,502,503",
  "behavior.on.error": "fail"
}
```

| Behavior | Description |
|----------|-------------|
| `fail` | Stop connector |
| `log` | Log and continue |
| `ignore` | Silently skip |

---

## SSL/TLS

```json
{
  "http.ssl.enabled": "true",
  "http.ssl.truststore.location": "/path/to/truststore.jks",
  "http.ssl.truststore.password": "${secrets:ssl/truststore-password}",
  "http.ssl.keystore.location": "/path/to/keystore.jks",
  "http.ssl.keystore.password": "${secrets:ssl/keystore-password}"
}
```

---

## Complete Example

```json
{
  "name": "github-events-source",
  "config": {
    "connector.class": "io.confluent.connect.http.HttpSourceConnector",
    "tasks.max": "1",

    "http.url": "https://api.github.com/repos/apache/kafka/events",
    "http.method": "GET",
    "http.headers": "Accept: application/vnd.github+json, Authorization: Bearer ${secrets:github/token}",

    "kafka.topic": "github-events",

    "http.timer.interval.ms": "300000",

    "http.response.format": "JSON",
    "http.response.records.path": "$[*]",

    "http.pagination.type": "LINK_HEADER",

    "http.retry.max.attempts": "3",
    "http.retry.backoff.ms": "5000",

    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",

    "errors.tolerance": "all",
    "errors.log.enable": "true"
  }
}
```

---

## Transforms

### Add Metadata

```json
{
  "transforms": "addSource,addTimestamp",
  "transforms.addSource.type": "org.apache.kafka.connect.transforms.InsertField$Value",
  "transforms.addSource.static.field": "source",
  "transforms.addSource.static.value": "github-api",
  "transforms.addTimestamp.type": "org.apache.kafka.connect.transforms.InsertField$Value",
  "transforms.addTimestamp.timestamp.field": "ingested_at"
}
```

### Extract Key

```json
{
  "transforms": "extractKey",
  "transforms.extractKey.type": "org.apache.kafka.connect.transforms.ValueToKey",
  "transforms.extractKey.fields": "id"
}
```

---

## Rate Limiting

### Throttling

```json
{
  "http.timer.interval.ms": "60000",
  "http.throttle.max.requests": "100",
  "http.throttle.window.ms": "60000"
}
```

Maximum 100 requests per minute.

### Respect Rate Limit Headers

```json
{
  "http.rate.limit.header": "X-RateLimit-Remaining",
  "http.rate.limit.reset.header": "X-RateLimit-Reset"
}
```

---

## Monitoring

### Connector Status

```bash
curl http://connect:8083/connectors/http-source/status
```

### Metrics

| Metric | Description |
|--------|-------------|
| `http-source-requests-total` | Total HTTP requests |
| `http-source-errors-total` | Failed requests |
| `http-source-records-polled` | Records retrieved |

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Connection timeout | Network/firewall | Verify endpoint accessibility |
| 401 Unauthorized | Invalid credentials | Check authentication config |
| 429 Too Many Requests | Rate limited | Increase polling interval |
| Empty response | Wrong JSON path | Verify `records.path` |
| Duplicate records | No offset tracking | Enable offset mode |

---

## Related Documentation

- [Connectors Overview](index.md) - All connectors
- [Kafka Connect](../index.md) - Connect framework
- [Transforms](../transforms.md) - Single Message Transforms