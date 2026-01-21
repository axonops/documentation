---
title: "Kafka Operations Troubleshooting"
description: "Apache Kafka operational troubleshooting. Quick diagnosis, common issues, and resolution procedures."
meta:
  - name: keywords
    content: "Kafka troubleshooting, Kafka operations, Kafka diagnosis, operational issues"
search:
  boost: 3
---

# Kafka Operations Troubleshooting

Quick troubleshooting guide for operational issues.

---

## Quick Diagnosis

### Health Check

```bash
#!/bin/bash
# quick-health-check.sh

BOOTSTRAP=${1:-"localhost:9092"}

echo "=== Kafka Quick Health Check ==="

# Connectivity
echo -n "Connectivity: "
kafka-broker-api-versions.sh --bootstrap-server $BOOTSTRAP > /dev/null 2>&1 \
  && echo "OK" || echo "FAILED"

# Offline partitions
OFFLINE=$(kafka-topics.sh --bootstrap-server $BOOTSTRAP \
  --describe --unavailable-partitions 2>/dev/null | grep -c "Topic:")
echo "Offline partitions: $OFFLINE"

# Under-replicated
URP=$(kafka-topics.sh --bootstrap-server $BOOTSTRAP \
  --describe --under-replicated-partitions 2>/dev/null | grep -c "Topic:")
echo "Under-replicated: $URP"
```

---

## Common Issues

### Issue: Under-Replicated Partitions

**Symptoms:** `UnderReplicatedPartitions > 0`

**Quick Check:**
```bash
kafka-topics.sh --bootstrap-server kafka:9092 \
  --describe --under-replicated-partitions
```

**Common Causes:**

| Cause | Check | Resolution |
|-------|-------|------------|
| Broker down | Broker connectivity | Restart broker |
| Slow broker | Disk I/O, CPU | Address bottleneck |
| Network issues | ping, netstat | Fix connectivity |
| Large messages | Message size | Increase replica.fetch.max.bytes |

---

### Issue: Consumer Lag Growing

**Symptoms:** Lag increasing over time

**Quick Check:**
```bash
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --describe --group my-group
```

**Common Causes:**

| Cause | Check | Resolution |
|-------|-------|------------|
| Slow processing | Consumer metrics | Optimize processing |
| Too few consumers | Consumer count | Add consumers |
| Rebalancing | Group state | Fix rebalance storms |
| External dependency | External latency | Add buffering |

---

### Issue: Producer Timeouts

**Symptoms:** `TimeoutException` in producer

**Quick Check:**
```bash
# Check broker health
kafka-broker-api-versions.sh --bootstrap-server kafka:9092

# Check partition leaders
kafka-topics.sh --bootstrap-server kafka:9092 \
  --describe --topic my-topic
```

**Common Causes:**

| Cause | Check | Resolution |
|-------|-------|------------|
| Broker unavailable | Broker status | Restart broker |
| No leader | Partition describe | Wait for election |
| ISR too small | min.insync.replicas | Fix broker health |
| Network issues | Connectivity | Fix network |

---

### Issue: Frequent Rebalances

**Symptoms:** Consumers constantly rebalancing

**Quick Check:**
```bash
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --describe --group my-group --state
```

**Common Causes:**

| Cause | Check | Resolution |
|-------|-------|------------|
| Session timeout | Processing time | Increase max.poll.interval.ms |
| Consumer crashes | Consumer logs | Fix stability |
| Heartbeat issues | Network | Check connectivity |
| GC pauses | GC logs | Tune JVM |

**Resolution:**
```properties
# Increase timeouts
max.poll.interval.ms=600000
session.timeout.ms=45000
heartbeat.interval.ms=3000

# Use cooperative rebalancing
partition.assignment.strategy=org.apache.kafka.clients.consumer.CooperativeStickyAssignor

# Static membership
group.instance.id=consumer-1
```

---

### Issue: High Latency

**Symptoms:** Request latency exceeds SLA

**Quick Check:**
```bash
# Check broker metrics
# kafka.network:type=RequestMetrics,name=TotalTimeMs
```

**Common Causes:**

| Cause | Check | Resolution |
|-------|-------|------------|
| Disk I/O | iostat | Faster disks |
| Network | netstat, ping | Fix network |
| GC pauses | GC logs | Tune JVM |
| Request queue | RequestQueueTimeMs | More network threads |

---

### Issue: Disk Full

**Symptoms:** `No space left on device`

**Quick Check:**
```bash
df -h /var/kafka-logs
du -sh /var/kafka-logs/*
```

**Resolution:**
```bash
# Reduce retention
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type topics --entity-name big-topic \
  --alter --add-config retention.ms=86400000

# Delete old topics
kafka-topics.sh --bootstrap-server kafka:9092 \
  --delete --topic unused-topic

# Add storage
# Mount additional disk
```

---

## Log Analysis

### Find Errors

```bash
# Recent errors
grep "ERROR" /var/log/kafka/server.log | tail -50

# Specific exception
grep "OutOfMemoryError" /var/log/kafka/server.log

# Time-based search
grep "2024-01-15 10:" /var/log/kafka/server.log | grep ERROR
```

### Key Patterns

| Pattern | Meaning | Action |
|---------|---------|--------|
| `OutOfMemoryError` | Heap exhausted | Increase heap |
| `KafkaStorageException` | Disk failure | Check disk |
| `NotLeaderOrFollower` | Stale metadata | Usually transient |
| `ISR shrunk` | Replica fell behind | Check broker |

---

## Emergency Procedures

### Broker Won't Start

```bash
# Check for port conflict
netstat -tlnp | grep 9092

# Check log for errors
tail -100 /var/log/kafka/server.log | grep -E "ERROR|FATAL"

# Verify disk space
df -h /var/kafka-logs

# Check file descriptors
ulimit -n
```

### Offline Partitions

```bash
# Identify offline partitions
kafka-topics.sh --bootstrap-server kafka:9092 \
  --describe --unavailable-partitions

# Check replica status
kafka-topics.sh --bootstrap-server kafka:9092 \
  --describe --topic affected-topic

# If broker recoverable, restart it
# If not, consider unclean election (data loss risk)
kafka-leader-election.sh --bootstrap-server kafka:9092 \
  --election-type unclean \
  --topic affected-topic --partition 0
```

### Consumer Group Stuck

```bash
# Check group state
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --describe --group stuck-group --state

# Force delete (consumers must be stopped)
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --delete --group stuck-group

# Recreate with offset reset if needed
```

---

## Related Documentation

- [Troubleshooting Guide](../../troubleshooting/index.md) - Complete troubleshooting
- [Common Errors](../../troubleshooting/common-errors/index.md) - Error reference
- [Log Analysis](../../troubleshooting/log-analysis/index.md) - Log interpretation
- [Monitoring](../monitoring/index.md) - Metrics and alerting
