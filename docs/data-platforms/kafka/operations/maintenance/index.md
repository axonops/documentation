---
title: "Kafka Maintenance"
description: "Apache Kafka maintenance procedures. Log cleanup, compaction, disk management, and routine operations."
meta:
  - name: keywords
    content: "Kafka maintenance, log cleanup, compaction, disk management, Kafka operations"
search:
  boost: 3
---

# Kafka Maintenance

Routine maintenance procedures for Apache Kafka clusters.

---

## Maintenance Overview

| Frequency | Tasks |
|-----------|-------|
| **Daily** | Health checks, log monitoring |
| **Weekly** | Disk usage review, consumer lag review |
| **Monthly** | Partition balancing, configuration review |
| **Quarterly** | Capacity planning, security audit |

---

## Log Cleanup

### Retention-Based Cleanup

Kafka automatically deletes log segments based on retention settings.

```properties
# Time-based retention (default 7 days)
log.retention.hours=168

# Size-based retention (per partition)
log.retention.bytes=107374182400

# Check interval
log.retention.check.interval.ms=300000

# Segment settings
log.segment.bytes=1073741824
log.segment.ms=604800000
```

### Manual Log Cleanup

```bash
# Delete records before offset
kafka-delete-records.sh --bootstrap-server kafka:9092 \
  --offset-json-file delete-records.json

# delete-records.json content:
# {
#   "partitions": [
#     {"topic": "my-topic", "partition": 0, "offset": 1000000},
#     {"topic": "my-topic", "partition": 1, "offset": 1000000}
#   ],
#   "version": 1
# }
```

### Viewing Log Segment Information

```bash
# List log directories
kafka-log-dirs.sh --bootstrap-server kafka:9092 \
  --describe --broker-list 1,2,3

# Dump log segment
kafka-dump-log.sh --files /var/kafka-logs/my-topic-0/00000000000000000000.log \
  --print-data-log
```

---

## Log Compaction

### Compaction Configuration

```properties
# Enable compaction for topic
cleanup.policy=compact

# Compaction settings
log.cleaner.enable=true
log.cleaner.threads=2
log.cleaner.io.buffer.size=524288
log.cleaner.dedupe.buffer.size=134217728
log.cleaner.io.max.bytes.per.second=1.7976931348623157E308
log.cleaner.min.cleanable.ratio=0.5
log.cleaner.min.compaction.lag.ms=0
log.cleaner.max.compaction.lag.ms=9223372036854775807
```

### Creating Compacted Topic

```bash
kafka-topics.sh --bootstrap-server kafka:9092 \
  --create \
  --topic compacted-topic \
  --partitions 12 \
  --replication-factor 3 \
  --config cleanup.policy=compact \
  --config min.cleanable.dirty.ratio=0.5 \
  --config segment.ms=86400000
```

### Monitoring Compaction

| Metric | Description |
|--------|-------------|
| `log-cleaner-recopy-percent` | Percentage of log recopy |
| `max-clean-time-secs` | Maximum clean time |
| `max-buffer-utilization-percent` | Buffer utilization |

---

## Disk Management

### Monitoring Disk Usage

```bash
#!/bin/bash
# check-disk-usage.sh

KAFKA_LOG_DIR="/var/kafka-logs"
THRESHOLD=80

usage=$(df -h "$KAFKA_LOG_DIR" | tail -1 | awk '{print $5}' | tr -d '%')

echo "Disk usage for $KAFKA_LOG_DIR: ${usage}%"

if [ "$usage" -gt "$THRESHOLD" ]; then
  echo "WARNING: Disk usage exceeds ${THRESHOLD}%"

  # Show largest topics
  echo "Largest topics:"
  du -sh "$KAFKA_LOG_DIR"/*-* | sort -rh | head -10
fi
```

### Adding Log Directory

```properties
# Multiple log directories
log.dirs=/data1/kafka-logs,/data2/kafka-logs,/data3/kafka-logs
```

### Moving Partitions Between Disks

```bash
# Generate plan to use new disk
kafka-reassign-partitions.sh --bootstrap-server kafka:9092 \
  --topics-to-move-json-file topics.json \
  --broker-list "1,2,3" \
  --generate

# Verify disk distribution
kafka-log-dirs.sh --bootstrap-server kafka:9092 \
  --describe --broker-list 1
```

---

## Consumer Group Maintenance

### Dead Consumer Groups

```bash
# List groups with state
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --list --state

# Find empty groups
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --list --state | grep "Empty"

# Delete empty group
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --delete --group dead-group
```

### Reset Consumer Offsets

```bash
# Dry run first
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --group my-group \
  --reset-offsets \
  --to-earliest \
  --all-topics \
  --dry-run

# Execute reset
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --group my-group \
  --reset-offsets \
  --to-earliest \
  --all-topics \
  --execute
```

---

## Broker Maintenance

### Graceful Restart

```bash
#!/bin/bash
# graceful-restart.sh

BROKER=$1
BOOTSTRAP="kafka:9092"

echo "Restarting broker: $BROKER"

# Trigger controlled shutdown
ssh $BROKER "sudo systemctl stop kafka"

# Wait for leadership to transfer
sleep 10

# Check under-replicated partitions
URP=$(kafka-topics.sh --bootstrap-server $BOOTSTRAP \
  --describe --under-replicated-partitions 2>/dev/null | wc -l)

echo "Under-replicated partitions: $URP"

# Start broker
ssh $BROKER "sudo systemctl start kafka"

# Wait for recovery
echo "Waiting for broker to rejoin..."
sleep 30

# Verify health
kafka-broker-api-versions.sh --bootstrap-server $BROKER:9092

# Wait for ISR to recover
while true; do
  URP=$(kafka-topics.sh --bootstrap-server $BOOTSTRAP \
    --describe --under-replicated-partitions 2>/dev/null | wc -l)
  if [ "$URP" -eq 0 ]; then
    echo "All partitions in sync"
    break
  fi
  echo "Waiting for ISR recovery... ($URP under-replicated)"
  sleep 10
done

echo "Restart complete"
```

### Preferred Leader Election

```bash
# Rebalance leaders after maintenance
kafka-leader-election.sh --bootstrap-server kafka:9092 \
  --election-type preferred \
  --all-topic-partitions
```

---

## Certificate Rotation

### Rotation Process

1. **Generate new certificates**
2. **Add new CA to truststores**
3. **Deploy updated truststores**
4. **Generate new keystores with new certs**
5. **Deploy new keystores**
6. **Remove old CA from truststores**

```bash
#!/bin/bash
# rotate-certs.sh

# 1. Add new CA to existing truststore
keytool -keystore kafka.truststore.jks \
  -alias NewCARoot \
  -import \
  -file new-ca-cert.pem \
  -storepass changeit \
  -noprompt

# 2. Deploy truststores to all brokers
for broker in broker1 broker2 broker3; do
  scp kafka.truststore.jks $broker:/etc/kafka/ssl/
done

# 3. Rolling restart (truststores only - no downtime)
for broker in broker1 broker2 broker3; do
  ./graceful-restart.sh $broker
done

# 4. Generate new keystores and deploy
# ... (similar process for keystores)
```

---

## Index Maintenance

### Index Verification

```bash
# Verify index integrity
kafka-dump-log.sh \
  --files /var/kafka-logs/my-topic-0/00000000000000000000.log \
  --index-sanity-check

# Deep iteration check
kafka-dump-log.sh \
  --files /var/kafka-logs/my-topic-0/00000000000000000000.log \
  --deep-iteration
```

### Rebuilding Indexes

Kafka automatically rebuilds indexes on broker startup if they are missing or corrupt.

```bash
# Force index rebuild by removing index files
# (broker must be stopped)
rm /var/kafka-logs/my-topic-0/*.index
rm /var/kafka-logs/my-topic-0/*.timeindex

# Start broker - indexes will be rebuilt
```

---

## Maintenance Scripts

### Daily Health Check

```bash
#!/bin/bash
# daily-health-check.sh

BOOTSTRAP="kafka:9092"
DATE=$(date +%Y-%m-%d)
LOG_FILE="/var/log/kafka-health/health-$DATE.log"

{
  echo "=== Kafka Daily Health Check ==="
  echo "Date: $DATE"
  echo ""

  # Broker connectivity
  echo "--- Broker Status ---"
  kafka-broker-api-versions.sh --bootstrap-server $BOOTSTRAP 2>/dev/null | head -5

  # Offline partitions
  echo ""
  echo "--- Offline Partitions ---"
  kafka-topics.sh --bootstrap-server $BOOTSTRAP \
    --describe --unavailable-partitions 2>/dev/null || echo "None"

  # Under-replicated
  echo ""
  echo "--- Under-replicated Partitions ---"
  kafka-topics.sh --bootstrap-server $BOOTSTRAP \
    --describe --under-replicated-partitions 2>/dev/null || echo "None"

  # Consumer lag
  echo ""
  echo "--- Consumer Groups with Lag ---"
  kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP --list 2>/dev/null | \
  while read group; do
    kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP \
      --describe --group "$group" 2>/dev/null | \
    awk -v g="$group" '$6 > 0 {print g, $2, $3, $6}'
  done

} >> "$LOG_FILE"
```

---

## Related Documentation

- [Operations Overview](../index.md) - Operations guide
- [Monitoring](../monitoring/index.md) - Metrics and alerting
- [Cluster Management](../cluster-management/index.md) - Cluster operations
- [Backup and Restore](../backup-restore/index.md) - DR procedures
