---
title: "Kafka Log Analysis"
description: "Apache Kafka log analysis guide. Log locations, patterns, debug logging, and interpretation."
meta:
  - name: keywords
    content: "Kafka logs, log analysis, Kafka debugging, log patterns, Kafka troubleshooting"
---

# Kafka Log Analysis

Guide to analyzing Apache Kafka logs for troubleshooting and diagnostics.

---

## Log File Locations

### Broker Logs

| Log File | Purpose | Key Information |
|----------|---------|-----------------|
| `server.log` | Main broker log | Errors, warnings, startup/shutdown |
| `controller.log` | Controller operations | Leader elections, partition assignments |
| `state-change.log` | Partition state changes | ISR changes, leadership changes |
| `kafka-authorizer.log` | Authorization decisions | ACL evaluations |
| `kafka-request.log` | Request logging | Client requests (if enabled) |
| `log-cleaner.log` | Log compaction | Compaction progress, errors |
| `kafkaServer-gc.log` | JVM GC logs | GC events, pause times |

### Default Locations

```
# Linux/Standard installation
/var/log/kafka/
/opt/kafka/logs/

# Kubernetes
/var/log/containers/kafka-*.log

# Docker
docker logs <kafka-container>
```

---

## Log Patterns

### Critical Patterns (Immediate Action)

| Pattern | Meaning | Action |
|---------|---------|--------|
| `FATAL` | Fatal error | Investigate immediately |
| `OutOfMemoryError` | Heap exhausted | Increase heap, check for leaks |
| `KafkaStorageException` | Disk failure | Check disk health |
| `OfflinePartitionsCount > 0` | Partitions offline | Restore brokers |

```bash
# Find critical errors
grep -E "FATAL|OutOfMemoryError|KafkaStorageException" server.log
```

### Error Patterns (Investigation Required)

| Pattern | Meaning | Action |
|---------|---------|--------|
| `ERROR` | Error condition | Investigate root cause |
| `NotLeaderForPartition` | Stale metadata | Usually transient |
| `UnknownTopicOrPartition` | Topic doesn't exist | Create topic or fix config |
| `Connection.*refused` | Network issue | Check connectivity |
| `Authentication failed` | Auth error | Check credentials |

```bash
# Find errors
grep "ERROR" server.log | tail -100

# Filter by component
grep "ERROR.*\[Controller\]" controller.log
```

### Warning Patterns (Monitor)

| Pattern | Meaning | Action |
|---------|---------|--------|
| `WARN` | Warning condition | Monitor frequency |
| `ISR shrunk` | Replica fell behind | Check replica health |
| `Connection.*timed out` | Slow network | Investigate latency |
| `Request.*too large` | Large request | Check client config |

```bash
# Count warnings by type
grep "WARN" server.log | cut -d: -f4 | sort | uniq -c | sort -rn
```

### State Change Patterns

| Pattern | Meaning |
|---------|---------|
| `Partition.*Leader` | Leadership change |
| `ISR.*expanded` | Replica rejoined ISR |
| `ISR.*shrunk` | Replica left ISR |
| `state.*OnlinePartition` | Partition came online |
| `state.*OfflinePartition` | Partition went offline |

```bash
# Track leadership changes
grep "Leader" state-change.log | tail -50

# Track ISR changes
grep "ISR" state-change.log | tail -50
```

---

## Log Analysis Commands

### Basic Search

```bash
# Search for pattern
grep "pattern" server.log

# Case-insensitive search
grep -i "error" server.log

# Search with context
grep -B 5 -A 5 "Exception" server.log

# Search multiple files
grep "ERROR" /var/log/kafka/*.log
```

### Time-Based Analysis

```bash
# Filter by time range
awk '/2024-01-15 10:/ && /2024-01-15 11:/' server.log

# Last hour
grep "$(date -d '1 hour ago' '+%Y-%m-%d %H')" server.log

# Count errors per hour
grep "ERROR" server.log | cut -d' ' -f1-2 | cut -d: -f1-2 | uniq -c
```

### Pattern Frequency

```bash
# Most common errors
grep "ERROR" server.log | \
  sed 's/.*ERROR/ERROR/' | \
  cut -d: -f1-2 | \
  sort | uniq -c | sort -rn | head -20

# Most common exceptions
grep -oE "[A-Z][a-zA-Z]+Exception" server.log | \
  sort | uniq -c | sort -rn
```

### Correlation Analysis

```bash
# Find events around a timestamp
grep "2024-01-15 10:30" server.log | head -50

# Correlate across files
timestamp="2024-01-15 10:30"
for log in server.log controller.log state-change.log; do
  echo "=== $log ==="
  grep "$timestamp" $log | head -10
done
```

---

## Debug Logging

### Enable Debug Dynamically

```bash
# Enable debug for specific logger
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type broker-loggers \
  --entity-name 0 \
  --alter \
  --add-config kafka.server=DEBUG

# Verify logger level
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type broker-loggers \
  --entity-name 0 \
  --describe

# Reset to default
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type broker-loggers \
  --entity-name 0 \
  --alter \
  --delete-config kafka.server
```

### Common Debug Loggers

| Logger | Purpose |
|--------|---------|
| `kafka.server` | Server operations |
| `kafka.controller` | Controller operations |
| `kafka.network` | Network/request handling |
| `kafka.log` | Log management |
| `kafka.request.logger` | Request details |
| `kafka.authorizer.logger` | ACL decisions |
| `kafka.coordinator.group` | Consumer group coordination |
| `kafka.coordinator.transaction` | Transaction coordination |

### Enable via Configuration

```properties
# log4j.properties

# Debug controller
log4j.logger.kafka.controller=DEBUG

# Debug network
log4j.logger.kafka.network=DEBUG

# Debug replication
log4j.logger.kafka.server.ReplicaManager=DEBUG
log4j.logger.kafka.server.ReplicaFetcherThread=DEBUG

# Debug authorization
log4j.logger.kafka.authorizer.logger=DEBUG

# Request logging (verbose)
log4j.logger.kafka.request.logger=DEBUG
```

---

## Request Logging

### Enable Request Logging

```properties
# log4j.properties
log4j.logger.kafka.request.logger=DEBUG

# Separate file for requests
log4j.appender.requestAppender=org.apache.log4j.RollingFileAppender
log4j.appender.requestAppender.File=${kafka.logs.dir}/kafka-request.log
log4j.appender.requestAppender.MaxFileSize=100MB
log4j.appender.requestAppender.MaxBackupIndex=10
log4j.logger.kafka.request.logger=DEBUG,requestAppender
log4j.additivity.kafka.request.logger=false
```

### Request Log Format

```
[timestamp] Completed request:[RequestType] with correlation id [id]
in queue time ms:[queue_time],
local time ms:[local_time],
remote time ms:[remote_time],
throttle time ms:[throttle_time],
response size:[size]
```

### Analyze Request Latency

```bash
# Extract latency metrics
grep "Completed request" kafka-request.log | \
  awk '{
    for(i=1;i<=NF;i++) {
      if($i ~ /local/) print $i, $(i+1), $(i+2), $(i+3)
    }
  }' | \
  sort -t: -k4 -rn | head -20
```

---

## Common Log Scenarios

### Leader Election

```
[2024-01-15 10:30:00,123] INFO [Controller id=1] Partition [topic,0]
has been elected as leader at epoch 5 (kafka.controller.KafkaController)

[2024-01-15 10:30:00,125] INFO [Partition topic-0 broker=1]
ISR updated to [1,2,3] (kafka.cluster.Partition)
```

**Interpretation:** Leadership change occurred. Check for broker failures if unexpected.

### ISR Shrink

```
[2024-01-15 10:30:00,123] WARN [Partition topic-0 broker=1]
Shrinking ISR from [1,2,3] to [1,2] (kafka.cluster.Partition)
```

**Interpretation:** Broker 3 fell behind and was removed from ISR. Check:
- Broker 3 health
- Network connectivity
- Disk I/O on broker 3

### Consumer Group Rebalance

```
[2024-01-15 10:30:00,123] INFO [GroupCoordinator 0]:
Member consumer-1 in group my-group has left (kafka.coordinator.group.GroupCoordinator)

[2024-01-15 10:30:01,456] INFO [GroupCoordinator 0]:
Preparing to rebalance group my-group (kafka.coordinator.group.GroupCoordinator)
```

**Interpretation:** Consumer left group, triggering rebalance. Check:
- Consumer health
- Session timeout settings
- Processing time

### Authentication Failure

```
[2024-01-15 10:30:00,123] INFO [SocketServer listenerType=BROKER, nodeId=1]
Failed authentication with /10.0.0.100
(Authentication failed during authentication due to:
Authentication failed: credentials do not match) (kafka.network.SocketServer)
```

**Interpretation:** Client failed to authenticate. Check:
- Client credentials
- SASL configuration
- User exists in SCRAM store

### Disk Error

```
[2024-01-15 10:30:00,123] ERROR [Log partition=topic-0 dir=/var/kafka-logs]
Error while flushing log (kafka.log.Log)
java.io.IOException: No space left on device
```

**Interpretation:** Disk full. Action:
- Add storage
- Reduce retention
- Delete old topics

---

## Log Rotation Configuration

### log4j.properties

```properties
# Configure rolling file appender
log4j.appender.kafkaAppender=org.apache.log4j.RollingFileAppender
log4j.appender.kafkaAppender.File=${kafka.logs.dir}/server.log
log4j.appender.kafkaAppender.MaxFileSize=100MB
log4j.appender.kafkaAppender.MaxBackupIndex=10
log4j.appender.kafkaAppender.layout=org.apache.log4j.PatternLayout
log4j.appender.kafkaAppender.layout.ConversionPattern=[%d] %p %m (%c)%n

# Root logger
log4j.rootLogger=INFO, kafkaAppender
```

### System logrotate

```bash
# /etc/logrotate.d/kafka
/var/log/kafka/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
```

---

## Log Aggregation

### Structured Logging

```properties
# JSON format for log aggregation
log4j.appender.kafkaAppender.layout=net.logstash.log4j.JSONEventLayoutV1
```

### Forwarding to Centralized System

```yaml
# Filebeat configuration
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/kafka/*.log
    multiline:
      pattern: '^\['
      negate: true
      match: after
    fields:
      service: kafka
      environment: production

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "kafka-logs-%{+yyyy.MM.dd}"
```

---

## Related Documentation

- [Troubleshooting Overview](../index.md) - Troubleshooting guide
- [Common Errors](../common-errors/index.md) - Error reference
- [Diagnosis](../diagnosis/index.md) - Diagnostic procedures
- [Monitoring](../../operations/monitoring/index.md) - Metrics and alerting
