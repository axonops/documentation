---
title: "Kafka CLI Tools"
description: "Apache Kafka command-line tools reference. kafka-topics, kafka-consumer-groups, kafka-configs, and administrative commands."
meta:
  - name: keywords
    content: "Kafka CLI, kafka-topics, kafka-consumer-groups, Kafka administration"
---

# Kafka CLI Tools

Command-line tools for Apache Kafka administration and operations.

---

## Tool Overview

| Tool | Purpose |
|------|---------|
| `kafka-topics.sh` | Topic management |
| `kafka-consumer-groups.sh` | Consumer group management |
| `kafka-configs.sh` | Configuration management |
| `kafka-acls.sh` | ACL management |
| `kafka-reassign-partitions.sh` | Partition reassignment |
| `kafka-leader-election.sh` | Leader election |
| `kafka-metadata.sh` | KRaft metadata inspection |
| `kafka-dump-log.sh` | Log segment inspection |

---

## kafka-topics.sh

### List Topics

```bash
# List all topics
kafka-topics.sh --bootstrap-server kafka:9092 --list

# List with details
kafka-topics.sh --bootstrap-server kafka:9092 --describe
```

### Create Topic

```bash
kafka-topics.sh --bootstrap-server kafka:9092 \
  --create \
  --topic my-topic \
  --partitions 12 \
  --replication-factor 3

# With configuration
kafka-topics.sh --bootstrap-server kafka:9092 \
  --create \
  --topic my-topic \
  --partitions 12 \
  --replication-factor 3 \
  --config retention.ms=604800000 \
  --config cleanup.policy=compact
```

### Describe Topic

```bash
# Single topic
kafka-topics.sh --bootstrap-server kafka:9092 \
  --describe --topic my-topic

# Show under-replicated partitions
kafka-topics.sh --bootstrap-server kafka:9092 \
  --describe --under-replicated-partitions

# Show unavailable partitions
kafka-topics.sh --bootstrap-server kafka:9092 \
  --describe --unavailable-partitions
```

### Alter Topic

```bash
# Increase partitions (cannot decrease)
kafka-topics.sh --bootstrap-server kafka:9092 \
  --alter --topic my-topic --partitions 24
```

### Delete Topic

```bash
kafka-topics.sh --bootstrap-server kafka:9092 \
  --delete --topic my-topic
```

---

## kafka-consumer-groups.sh

### List Consumer Groups

```bash
kafka-consumer-groups.sh --bootstrap-server kafka:9092 --list

# With state
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --list --state
```

### Describe Consumer Group

```bash
# Show members and offsets
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --describe --group my-group

# Show only members
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --describe --group my-group --members

# Show verbose member details
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --describe --group my-group --members --verbose

# Show state
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --describe --group my-group --state
```

### Reset Offsets

```bash
# Reset to earliest (dry run)
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --group my-group \
  --reset-offsets \
  --to-earliest \
  --topic my-topic \
  --dry-run

# Reset to earliest (execute)
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --group my-group \
  --reset-offsets \
  --to-earliest \
  --topic my-topic \
  --execute

# Reset to specific offset
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --group my-group \
  --reset-offsets \
  --to-offset 1000 \
  --topic my-topic:0 \
  --execute

# Reset to timestamp
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --group my-group \
  --reset-offsets \
  --to-datetime "2024-01-15T10:00:00.000" \
  --all-topics \
  --execute

# Reset by shifting
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --group my-group \
  --reset-offsets \
  --shift-by -100 \
  --topic my-topic \
  --execute
```

### Delete Consumer Group

```bash
# Group must be empty (no active members)
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --delete --group my-group
```

---

## kafka-configs.sh

### Describe Configuration

```bash
# Broker config
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type brokers --entity-name 1 --describe

# All brokers
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type brokers --describe --all

# Topic config
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type topics --entity-name my-topic --describe

# Client quotas
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type users --entity-name my-user --describe
```

### Alter Configuration

```bash
# Add/update broker config
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type brokers --entity-name 1 \
  --alter --add-config log.cleaner.threads=4

# Add/update topic config
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type topics --entity-name my-topic \
  --alter --add-config retention.ms=86400000

# Delete config (revert to default)
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type topics --entity-name my-topic \
  --alter --delete-config retention.ms
```

### Client Quotas

```bash
# Set producer quota
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type users --entity-name my-user \
  --alter --add-config producer_byte_rate=1048576

# Set consumer quota
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type users --entity-name my-user \
  --alter --add-config consumer_byte_rate=2097152
```

---

## kafka-acls.sh

### List ACLs

```bash
# All ACLs
kafka-acls.sh --bootstrap-server kafka:9092 --list

# For specific topic
kafka-acls.sh --bootstrap-server kafka:9092 \
  --list --topic my-topic

# For specific principal
kafka-acls.sh --bootstrap-server kafka:9092 \
  --list --principal User:my-user
```

### Add ACLs

```bash
# Producer access
kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:producer-app \
  --operation Write \
  --operation Describe \
  --topic my-topic

# Consumer access
kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:consumer-app \
  --operation Read \
  --operation Describe \
  --topic my-topic \
  --group my-group

# Wildcard topic access
kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:admin \
  --operation All \
  --topic '*'
```

### Remove ACLs

```bash
kafka-acls.sh --bootstrap-server kafka:9092 \
  --remove \
  --allow-principal User:producer-app \
  --operation Write \
  --topic my-topic
```

---

## kafka-reassign-partitions.sh

### Generate Reassignment Plan

```bash
# Create topics JSON file
cat > topics.json << 'EOF'
{
  "topics": [
    {"topic": "my-topic"}
  ],
  "version": 1
}
EOF

# Generate plan
kafka-reassign-partitions.sh --bootstrap-server kafka:9092 \
  --topics-to-move-json-file topics.json \
  --broker-list "1,2,3,4" \
  --generate
```

### Execute Reassignment

```bash
# Save generated plan to file, then execute
kafka-reassign-partitions.sh --bootstrap-server kafka:9092 \
  --reassignment-json-file reassignment.json \
  --execute

# With throttle
kafka-reassign-partitions.sh --bootstrap-server kafka:9092 \
  --reassignment-json-file reassignment.json \
  --throttle 50000000 \
  --execute
```

### Verify Reassignment

```bash
kafka-reassign-partitions.sh --bootstrap-server kafka:9092 \
  --reassignment-json-file reassignment.json \
  --verify
```

---

## kafka-leader-election.sh

```bash
# Preferred leader election for all partitions
kafka-leader-election.sh --bootstrap-server kafka:9092 \
  --election-type preferred \
  --all-topic-partitions

# For specific topic
kafka-leader-election.sh --bootstrap-server kafka:9092 \
  --election-type preferred \
  --topic my-topic

# Unclean election (data loss risk)
kafka-leader-election.sh --bootstrap-server kafka:9092 \
  --election-type unclean \
  --topic my-topic \
  --partition 0
```

---

## kafka-metadata.sh (KRaft)

```bash
# Describe cluster
kafka-metadata.sh --snapshot /var/kafka-logs/__cluster_metadata-0/*.log \
  --command "describe"

# List brokers
kafka-metadata.sh --snapshot /var/kafka-logs/__cluster_metadata-0/*.log \
  --command "brokers"

# Show topic details
kafka-metadata.sh --snapshot /var/kafka-logs/__cluster_metadata-0/*.log \
  --command "topic" --topic-name my-topic
```

---

## kafka-dump-log.sh

```bash
# Dump log segment
kafka-dump-log.sh --files /var/kafka-logs/my-topic-0/00000000000000000000.log \
  --print-data-log

# Dump index
kafka-dump-log.sh --files /var/kafka-logs/my-topic-0/00000000000000000000.index

# Verify indexes
kafka-dump-log.sh --files /var/kafka-logs/my-topic-0/00000000000000000000.log \
  --index-sanity-check
```

---

## Console Producer/Consumer

### Console Producer

```bash
kafka-console-producer.sh --bootstrap-server kafka:9092 \
  --topic my-topic

# With key
kafka-console-producer.sh --bootstrap-server kafka:9092 \
  --topic my-topic \
  --property "parse.key=true" \
  --property "key.separator=:"
```

### Console Consumer

```bash
# From beginning
kafka-console-consumer.sh --bootstrap-server kafka:9092 \
  --topic my-topic \
  --from-beginning

# With keys
kafka-console-consumer.sh --bootstrap-server kafka:9092 \
  --topic my-topic \
  --property print.key=true \
  --property print.timestamp=true

# Specific partition and offset
kafka-console-consumer.sh --bootstrap-server kafka:9092 \
  --topic my-topic \
  --partition 0 \
  --offset 100

# Max messages
kafka-console-consumer.sh --bootstrap-server kafka:9092 \
  --topic my-topic \
  --max-messages 10
```

---

## Related Documentation

- [Operations](../index.md) - Operations guide
- [Configuration](../configuration/index.md) - Configuration reference
- [Monitoring](../monitoring/index.md) - Monitoring guide
