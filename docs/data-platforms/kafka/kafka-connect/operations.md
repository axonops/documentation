---
title: "Kafka Connect Operations"
description: "Kafka Connect operations. Monitoring, scaling, troubleshooting, and management."
meta:
  - name: keywords
    content: "Kafka Connect operations, connector management, REST API, Connect cluster operations"
---

# Kafka Connect Operations

Operational guidance for running Kafka Connect in production.

---

## Monitoring

### Key Metrics

| Metric | Description | Alert |
|--------|-------------|-------|
| `connector-count` | Active connectors | ≠ expected |
| `task-count` | Running tasks | ≠ expected |
| `connector-startup-failure-total` | Startup failures | > 0 |
| `source-record-poll-total` | Records polled | Anomaly |
| `sink-record-send-total` | Records sent | Anomaly |
| `offset-commit-failure-total` | Commit failures | > 0 |
| `deadletterqueue-produce-total` | DLQ records | > 0 |

### JMX MBeans

```
kafka.connect:type=connector-metrics,connector={name}
kafka.connect:type=connector-task-metrics,connector={name},task={id}
kafka.connect:type=source-task-metrics,connector={name},task={id}
kafka.connect:type=sink-task-metrics,connector={name},task={id}
```

### Health Check

```bash
# Cluster info
curl http://connect:8083/

# List connectors
curl http://connect:8083/connectors

# Check connector status
curl http://connect:8083/connectors/my-connector/status
```

---

## REST API Operations

### Create Connector

```bash
curl -X POST http://connect:8083/connectors \
  -H "Content-Type: application/json" \
  -d @config.json
```

### Update Configuration

```bash
curl -X PUT http://connect:8083/connectors/my-connector/config \
  -H "Content-Type: application/json" \
  -d @updated-config.json
```

### Pause/Resume

```bash
# Pause
curl -X PUT http://connect:8083/connectors/my-connector/pause

# Resume
curl -X PUT http://connect:8083/connectors/my-connector/resume
```

### Restart

```bash
# Restart connector
curl -X POST http://connect:8083/connectors/my-connector/restart

# Restart specific task
curl -X POST http://connect:8083/connectors/my-connector/tasks/0/restart
```

### Delete

```bash
curl -X DELETE http://connect:8083/connectors/my-connector
```

---

## Scaling

### Add Workers

Start additional worker processes with same `group.id`:

```bash
# On new node
connect-distributed.sh config/connect-distributed.properties
```

Tasks automatically rebalance across workers.

### Increase Tasks

```bash
curl -X PUT http://connect:8083/connectors/my-connector/config \
  -H "Content-Type: application/json" \
  -d '{
    "connector.class": "...",
    "tasks.max": "6"
  }'
```

---

## Troubleshooting

### Common Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| Task failed | `FAILED` status | Check logs, fix config, restart |
| Connector not starting | `UNASSIGNED` tasks | Check worker logs |
| High lag | Slow processing | Scale tasks/workers |
| Memory issues | OOM errors | Increase heap, reduce batch size |

### Check Task Status

```bash
curl http://connect:8083/connectors/my-connector/status | jq
```

```json
{
  "name": "my-connector",
  "connector": {"state": "RUNNING", "worker_id": "worker1:8083"},
  "tasks": [
    {"id": 0, "state": "RUNNING", "worker_id": "worker1:8083"},
    {"id": 1, "state": "FAILED", "worker_id": "worker2:8083", "trace": "..."}
  ]
}
```

### View Worker Logs

```bash
# Check Connect worker logs
tail -f /var/log/kafka-connect/connect.log | grep ERROR
```

---

## Configuration Management

### Validate Before Deploy

```bash
curl -X PUT http://connect:8083/connector-plugins/MyConnector/config/validate \
  -H "Content-Type: application/json" \
  -d @config.json
```

### Export Configuration

```bash
curl http://connect:8083/connectors/my-connector/config > backup.json
```

---

## Internal Topics

| Topic | Purpose | Cleanup |
|-------|---------|---------|
| `connect-offsets` | Source offsets | Compacted |
| `connect-configs` | Configurations | Compacted |
| `connect-status` | Status updates | Compacted |

Verify topics exist with proper replication:

```bash
kafka-topics.sh --bootstrap-server kafka:9092 --describe \
  --topic connect-offsets
```

---

## Related Documentation

- [Kafka Connect](index.md) - Connect overview
- [Error Handling](error-handling.md) - Error tolerance
- [Connectors](connectors/index.md) - Connector guides
