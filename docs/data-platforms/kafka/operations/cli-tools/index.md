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

## kafka-share-groups.sh

Share groups (KIP-932) allow multiple consumers to share partition consumption.

### List Share Groups

```bash
kafka-share-groups.sh --bootstrap-server kafka:9092 --list
```

### Describe Share Group

```bash
# Show current state
kafka-share-groups.sh --bootstrap-server kafka:9092 \
  --describe --group my-share-group

# Show members
kafka-share-groups.sh --bootstrap-server kafka:9092 \
  --describe --group my-share-group --members

# Show state summary
kafka-share-groups.sh --bootstrap-server kafka:9092 \
  --describe --group my-share-group --state
```

### Reset Share Group Offsets

```bash
# Reset to latest (dry run)
kafka-share-groups.sh --bootstrap-server kafka:9092 \
  --reset-offsets --group my-share-group \
  --topic my-topic --to-latest --dry-run

# Reset to latest (execute)
kafka-share-groups.sh --bootstrap-server kafka:9092 \
  --reset-offsets --group my-share-group \
  --topic my-topic --to-latest --execute
```

### Delete Share Group

```bash
kafka-share-groups.sh --bootstrap-server kafka:9092 \
  --delete --group my-share-group
```

---

## kafka-groups.sh

List all group types (consumer, share, streams).

```bash
# List all groups with type
kafka-groups.sh --bootstrap-server kafka:9092 --list

# Output shows group type
# GROUP                    TYPE                     PROTOCOL
# my-consumer-group        Consumer                 consumer
# my-share-group           Share                    share
```

---

## Partition Reassignment with Throttling

Limit bandwidth during data migration to reduce impact on production traffic.

### Execute with Throttle

```bash
# Throttle inter-broker replication to 50 MB/s
kafka-reassign-partitions.sh --bootstrap-server kafka:9092 \
  --reassignment-json-file reassignment.json \
  --throttle 50000000 \
  --execute

# Also throttle disk-to-disk moves
kafka-reassign-partitions.sh --bootstrap-server kafka:9092 \
  --reassignment-json-file reassignment.json \
  --throttle 50000000 \
  --replica-alter-log-dirs-throttle 100000000 \
  --execute
```

### Adjust Throttle During Migration

```bash
# Increase throttle if migration is too slow
kafka-reassign-partitions.sh --bootstrap-server kafka:9092 \
  --reassignment-json-file reassignment.json \
  --throttle 100000000 \
  --additional \
  --execute
```

### Verify and Remove Throttle

```bash
# Verify completion - this also removes throttle
kafka-reassign-partitions.sh --bootstrap-server kafka:9092 \
  --reassignment-json-file reassignment.json \
  --verify
```

!!! warning "Throttle Removal"
    Always run `--verify` after reassignment completes. Failing to remove the throttle can limit normal replication traffic.

### View Current Throttle Settings

```bash
# View broker throttle
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type brokers --describe

# View topic throttle
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type topics --entity-name my-topic --describe
```

---

## Increasing Replication Factor

### Create Reassignment Plan

```bash
cat > increase-rf.json << 'EOF'
{
  "version": 1,
  "partitions": [
    {"topic": "my-topic", "partition": 0, "replicas": [1, 2, 3]}
  ]
}
EOF
```

### Execute and Verify

```bash
# Execute
kafka-reassign-partitions.sh --bootstrap-server kafka:9092 \
  --reassignment-json-file increase-rf.json \
  --execute

# Verify
kafka-reassign-partitions.sh --bootstrap-server kafka:9092 \
  --reassignment-json-file increase-rf.json \
  --verify

# Confirm new replication factor
kafka-topics.sh --bootstrap-server kafka:9092 \
  --topic my-topic --describe
```

---

## Quota Management

### Set User Quotas

```bash
# Set producer and consumer byte rate for user
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type users --entity-name my-user \
  --alter --add-config 'producer_byte_rate=1048576,consumer_byte_rate=2097152'

# Set request rate quota (percentage of broker capacity)
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type users --entity-name my-user \
  --alter --add-config 'request_percentage=50'
```

### Set Client-ID Quotas

```bash
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type clients --entity-name my-client \
  --alter --add-config 'producer_byte_rate=1048576,consumer_byte_rate=2097152'
```

### Set Combined User+Client Quotas

```bash
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type users --entity-name my-user \
  --entity-type clients --entity-name my-client \
  --alter --add-config 'producer_byte_rate=1048576'
```

### Set Default Quotas

```bash
# Default for all users
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type users --entity-default \
  --alter --add-config 'producer_byte_rate=1048576'

# Default for all clients
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type clients --entity-default \
  --alter --add-config 'producer_byte_rate=1048576'
```

### Describe Quotas

```bash
# Describe user quota
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type users --entity-name my-user --describe

# Describe all user quotas
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type users --describe

# Describe combined user+client quotas
kafka-configs.sh --bootstrap-server kafka:9092 \
  --entity-type users --entity-type clients --describe
```

---

## Cluster Operations

### Graceful Shutdown

Enable controlled shutdown for graceful broker restarts:

```properties
# server.properties
controlled.shutdown.enable=true
```

With controlled shutdown enabled, the broker:

1. Syncs all logs to disk (avoiding recovery on restart)
2. Migrates leadership to other replicas before stopping
3. Minimizes partition unavailability to milliseconds

### Preferred Leader Election

```bash
# Trigger preferred leader election for all partitions
kafka-leader-election.sh --bootstrap-server kafka:9092 \
  --election-type preferred \
  --all-topic-partitions

# Auto-rebalance can also be enabled in broker config
# auto.leader.rebalance.enable=true
```

### Rack Awareness

Configure brokers for rack-aware replica placement:

```properties
# server.properties on each broker
broker.rack=rack-1
```

When rack awareness is configured:

- Replicas of each partition spread across different racks
- Partition spans `min(#racks, replication-factor)` racks
- Survives rack-level failures

---

## Broker API Versions

Check supported API versions for compatibility:

```bash
kafka-broker-api-versions.sh --bootstrap-server kafka:9092
```

---

## Log Verification

### Verify Log Integrity

```bash
# Verify indexes
kafka-dump-log.sh --files /var/kafka-logs/my-topic-0/00000000000000000000.log \
  --index-sanity-check

# Dump transaction state
kafka-dump-log.sh --files /var/kafka-logs/__transaction_state-0/00000000000000000000.log \
  --print-data-log
```

### Offset Explorer

```bash
# Get offsets for all partitions
kafka-get-offsets.sh --bootstrap-server kafka:9092 \
  --topic my-topic

# Get earliest and latest offsets
kafka-get-offsets.sh --bootstrap-server kafka:9092 \
  --topic my-topic --time -2  # earliest

kafka-get-offsets.sh --bootstrap-server kafka:9092 \
  --topic my-topic --time -1  # latest
```

---

## Related Documentation

- [Operations](../index.md) - Operations guide
- [Configuration](../configuration/index.md) - Configuration reference
- [Monitoring](../monitoring/index.md) - Monitoring guide
