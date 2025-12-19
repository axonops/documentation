---
title: "Operating Dead Letter Queues"
description: "Operational procedures for Kafka Dead Letter Queues. Monitoring, alerting, reprocessing strategies, retention policies, and incident response for DLQ management."
meta:
  - name: keywords
    content: "Kafka DLQ operations, dead letter queue monitoring, DLQ reprocessing, Kafka error management, DLQ alerting"
---

# Operating Dead Letter Queues

This guide covers operational procedures for managing Dead Letter Queues in production Kafka environments. For conceptual background, see [Dead Letter Queue Concepts](../../concepts/dead-letter-queues/index.md). For implementation details, see [Implementing DLQs](../../application-development/error-handling/dead-letter-queues.md).

---

## DLQ Monitoring

### Key Metrics

Monitor DLQ topics for early detection of processing issues.

```plantuml
@startuml
skinparam backgroundColor transparent

rectangle "DLQ Monitoring Dashboard" {
    rectangle "Message Rate" as rate {
        card "messages/min into DLQ" as r1
        card "Spike = new failure pattern" as r2
    }

    rectangle "Queue Depth" as depth {
        card "Total messages in DLQ" as d1
        card "Growth trend over time" as d2
    }

    rectangle "Age Distribution" as age {
        card "Oldest unprocessed message" as a1
        card "Messages > 24h old" as a2
    }

    rectangle "Error Breakdown" as errors {
        card "By error class" as e1
        card "By source topic" as e2
        card "By consumer group" as e3
    }
}

@enduml
```

### Metric Collection

| Metric | Source | Alert Threshold |
|--------|--------|-----------------|
| `dlq.messages.in.rate` | Producer metrics | > 10/min (baseline dependent) |
| `dlq.messages.total` | Consumer lag on DLQ | > 1000 (application dependent) |
| `dlq.oldest.message.age` | Custom consumer | > 24 hours |
| `dlq.error.class.count` | Header aggregation | New error class detected |
| `dlq.source.topic.count` | Header aggregation | Spike from single topic |

### JMX Metrics

```bash
# Get DLQ topic message count
kafka-run-class.sh kafka.tools.JmxTool \
  --object-name 'kafka.server:type=BrokerTopicMetrics,name=MessagesInPerSec,topic=orders.dlq' \
  --jmx-url service:jmx:rmi:///jndi/rmi://broker1:9999/jmxrmi
```

---

## Alerting Strategy

### Alert Tiers

```plantuml
@startuml
skinparam backgroundColor transparent

rectangle "Alert Severity Levels" {
    rectangle "P1 - Critical" as p1 #FF6B6B {
        card "DLQ rate > 100/min" as p1a
        card "New poison error type" as p1b
        card "DLQ consumer stopped" as p1c
    }

    rectangle "P2 - High" as p2 #FFE66D {
        card "DLQ rate > 10/min" as p2a
        card "DLQ depth > 10,000" as p2b
        card "Messages > 48h old" as p2c
    }

    rectangle "P3 - Medium" as p3 #4ECDC4 {
        card "DLQ rate > 1/min" as p3a
        card "DLQ depth > 1,000" as p3b
        card "Messages > 24h old" as p3c
    }

    rectangle "P4 - Info" as p4 #95E1D3 {
        card "Any DLQ message" as p4a
        card "Daily DLQ summary" as p4b
    }
}

p1 -[hidden]down- p2
p2 -[hidden]down- p3
p3 -[hidden]down- p4

@enduml
```

### Alert Rules

Configure alerts based on the severity tiers above. Key alert conditions:

| Alert | Condition | Severity |
|-------|-----------|----------|
| **DLQHighMessageRate** | DLQ ingestion rate > 10 messages/min sustained for 5 minutes | High |
| **DLQDepthCritical** | Unprocessed DLQ messages > 10,000 for 10 minutes | Critical |
| **DLQConsumerStopped** | DLQ processor consumption rate = 0 for 15 minutes | Critical |
| **DLQMessageAgeWarning** | Oldest unprocessed message > 24 hours | Medium |
| **DLQNewErrorType** | Previously unseen error class detected | High |

For AxonOps alerting configuration, see [Setup Alert Rules](../../../../how-to/setup-alert-rules.md).

---

## DLQ Investigation

### Triage Workflow

```plantuml
@startuml
skinparam backgroundColor transparent

start
:DLQ alert triggered;

:Check DLQ message rate;
if (Spike or gradual?) then (spike)
    :Identify spike start time;
    :Correlate with deployments;
    :Check producer changes;
else (gradual)
    :Likely data quality issue;
    :Sample recent messages;
endif

:Analyze error patterns;
fork
    :Group by error class;
fork again
    :Group by source topic;
fork again
    :Group by consumer group;
end fork

:Identify root cause;

if (Code bug?) then (yes)
    :Deploy fix;
    :Reprocess DLQ;
elseif (Data issue?) then (yes)
    :Fix upstream data;
    :Decide: reprocess or discard;
elseif (Transient?) then (yes)
    :Verify recovery;
    :Auto-reprocess viable;
else (unknown)
    :Escalate to development;
endif

stop

@enduml
```

### Sampling DLQ Messages

```bash
# Read recent DLQ messages with headers
kafka-console-consumer.sh \
  --bootstrap-server broker1:9092 \
  --topic orders.dlq \
  --from-beginning \
  --max-messages 10 \
  --property print.headers=true \
  --property print.timestamp=true \
  --property print.key=true

# Filter by error type (requires header parsing)
kafka-console-consumer.sh \
  --bootstrap-server broker1:9092 \
  --topic orders.dlq \
  --from-beginning \
  --max-messages 100 \
  --property print.headers=true | \
  grep "dlq.error.class.*SerializationException"
```

### Error Analysis Script

```bash
#!/bin/bash
# analyze-dlq.sh - Analyze DLQ error distribution

DLQ_TOPIC=$1
BROKER=$2
SAMPLE_SIZE=${3:-1000}

echo "Analyzing $DLQ_TOPIC (sample: $SAMPLE_SIZE messages)"

# Extract error classes and count
kafka-console-consumer.sh \
  --bootstrap-server $BROKER \
  --topic $DLQ_TOPIC \
  --from-beginning \
  --max-messages $SAMPLE_SIZE \
  --property print.headers=true 2>/dev/null | \
  grep -oP 'dlq\.error\.class:\K[^,]+' | \
  sort | uniq -c | sort -rn

echo ""
echo "Error distribution by source topic:"
kafka-console-consumer.sh \
  --bootstrap-server $BROKER \
  --topic $DLQ_TOPIC \
  --from-beginning \
  --max-messages $SAMPLE_SIZE \
  --property print.headers=true 2>/dev/null | \
  grep -oP 'dlq\.original\.topic:\K[^,]+' | \
  sort | uniq -c | sort -rn
```

---

## Reprocessing Strategies

### Decision Framework

```plantuml
@startuml
skinparam backgroundColor transparent

start
:DLQ messages require reprocessing;

:Assess message volume;
if (< 100 messages?) then (yes)
    :Manual review viable;
    :Selective reprocessing;
else (no)
    if (Same error class?) then (yes)
        :Bulk reprocessing;
        :After fix deployed;
    else (no)
        :Categorize by error;
        :Prioritize by business impact;
    endif
endif

:Choose reprocessing method;

if (Original topic?) then (yes)
    :Replay to source topic;
    note right: Messages reprocessed\nby original consumer
elseif (Direct processing?) then (yes)
    :DLQ processor handles;
    note right: Specialized handler\nfor DLQ format
else (discard)
    :Archive and delete;
    note right: Unrecoverable or\nno longer relevant
endif

stop

@enduml
```

### Method 1: Replay to Original Topic

```plantuml
@startuml
skinparam backgroundColor transparent

participant "DLQ" as dlq
participant "Replay Tool" as replay
participant "Original Topic" as main
participant "Consumer" as cons
database "Database" as db

dlq -> replay : Read DLQ messages
replay -> replay : Strip DLQ headers
replay -> main : Produce to original topic
main -> cons : Normal processing
cons -> db : Success

note over replay
  Replay process:
  - Reads from DLQ
  - Strips dlq.* headers
  - Sends to original topic
  - Tracks replayed offsets
end note

@enduml
```

#### Replay Tool

```bash
#!/bin/bash
# replay-dlq.sh - Replay DLQ messages to original topic

DLQ_TOPIC=$1
BROKER=$2
MAX_MESSAGES=${3:-100}

# Create replay consumer group for tracking
GROUP_ID="dlq-replay-$(date +%s)"

echo "Replaying up to $MAX_MESSAGES messages from $DLQ_TOPIC"
echo "Consumer group: $GROUP_ID"

# Use kafkacat/kcat for replay (preserves headers, allows transformation)
kcat -C -b $BROKER -t $DLQ_TOPIC -G $GROUP_ID -c $MAX_MESSAGES -f '%h\n%k\n%s\n---\n' | \
while IFS= read -r headers && IFS= read -r key && IFS= read -r value && IFS= read -r sep; do
    # Extract original topic from headers
    original_topic=$(echo "$headers" | grep -oP 'dlq\.original\.topic=\K[^,]+')

    if [ -n "$original_topic" ]; then
        # Produce to original topic (without dlq headers)
        echo "$value" | kcat -P -b $BROKER -t "$original_topic" -k "$key"
        echo "Replayed to $original_topic: key=$key"
    fi
done
```

### Method 2: DLQ Processor Service

```java
@Service
public class DLQProcessor {

    @KafkaListener(topics = "orders.dlq", groupId = "dlq-processor")
    public void processDLQ(ConsumerRecord<String, byte[]> record) {
        String errorClass = getHeader(record, "dlq.error.class");
        String originalTopic = getHeader(record, "dlq.original.topic");
        int retryCount = Integer.parseInt(getHeader(record, "dlq.retry.count"));

        DLQAction action = determineAction(errorClass, retryCount);

        switch (action) {
            case REPLAY:
                replayToOriginalTopic(record, originalTopic);
                break;
            case MANUAL_REVIEW:
                storeForManualReview(record);
                break;
            case DISCARD:
                logAndDiscard(record);
                break;
        }
    }

    private DLQAction determineAction(String errorClass, int retryCount) {
        // Deserialization errors: likely need code fix, manual review
        if (errorClass.contains("SerializationException")) {
            return DLQAction.MANUAL_REVIEW;
        }

        // Transient errors that exceeded retry: try replay
        if (errorClass.contains("TimeoutException") && retryCount < 10) {
            return DLQAction.REPLAY;
        }

        // Validation errors: check if data was fixed upstream
        if (errorClass.contains("ValidationException")) {
            return DLQAction.REPLAY;  // Will fail again if not fixed
        }

        return DLQAction.MANUAL_REVIEW;
    }
}
```

### Method 3: Batch Reprocessing Job

```plantuml
@startuml
skinparam backgroundColor transparent

rectangle "Scheduled Batch Job" {
    rectangle "1. Query DLQ" as step1
    rectangle "2. Filter by criteria" as step2
    rectangle "3. Transform messages" as step3
    rectangle "4. Replay in batches" as step4
    rectangle "5. Track progress" as step5
    database "Progress\nTable" as progress
}

step1 --> step2
step2 --> step3
step3 --> step4
step4 --> step5
step5 --> progress

note right of step2
  Filter criteria:
  - Error class
  - Age range
  - Source topic
  - Retry count
end note

note right of step4
  Batch controls:
  - Rate limiting
  - Pause on errors
  - Progress checkpoints
end note

@enduml
```

---

## Retention and Cleanup

### Retention Policy

```plantuml
@startuml
skinparam backgroundColor transparent

rectangle "DLQ Lifecycle" {
    rectangle "Active\n(0-7 days)" as active #C8E6C9 {
        card "Immediate investigation" as a1
        card "Rapid reprocessing" as a2
    }

    rectangle "Review\n(7-30 days)" as review #FFF9C4 {
        card "Pending code fixes" as r1
        card "Batch reprocessing" as r2
    }

    rectangle "Archive\n(30-90 days)" as archive #E3F2FD {
        card "Compressed storage" as ar1
        card "Audit compliance" as ar2
    }

    rectangle "Expired\n(> 90 days)" as expired #FFCDD2 {
        card "Auto-deleted by retention" as e1
    }
}

active -right-> review : Age > 7d
review -right-> archive : Age > 30d
archive -right-> expired : Age > 90d

@enduml
```

### Topic Configuration

```bash
# Set DLQ retention to 30 days
kafka-configs.sh --bootstrap-server broker1:9092 \
  --alter --entity-type topics --entity-name orders.dlq \
  --add-config retention.ms=2592000000

# Set DLQ retention to 90 days for compliance
kafka-configs.sh --bootstrap-server broker1:9092 \
  --alter --entity-type topics --entity-name payments.dlq \
  --add-config retention.ms=7776000000

# Verify configuration
kafka-configs.sh --bootstrap-server broker1:9092 \
  --describe --entity-type topics --entity-name orders.dlq
```

### Archival Process

```bash
#!/bin/bash
# archive-dlq.sh - Archive old DLQ messages to cold storage

DLQ_TOPIC=$1
BROKER=$2
CUTOFF_DAYS=$3
S3_BUCKET=$4

CUTOFF_TS=$(($(date +%s) - ($CUTOFF_DAYS * 86400)))000

echo "Archiving messages older than $CUTOFF_DAYS days from $DLQ_TOPIC"

# Export old messages to file
kafka-console-consumer.sh \
  --bootstrap-server $BROKER \
  --topic $DLQ_TOPIC \
  --from-beginning \
  --property print.timestamp=true \
  --property print.headers=true \
  --property print.key=true \
  --timeout-ms 30000 | \
awk -v cutoff="$CUTOFF_TS" '
  /^CreateTime:/ {
    ts = $2
    if (ts < cutoff) { print; getline; print; getline; print }
  }
' > /tmp/dlq-archive-$(date +%Y%m%d).json

# Compress and upload to S3
gzip /tmp/dlq-archive-$(date +%Y%m%d).json
aws s3 cp /tmp/dlq-archive-$(date +%Y%m%d).json.gz \
  s3://$S3_BUCKET/dlq-archives/$DLQ_TOPIC/

echo "Archived to s3://$S3_BUCKET/dlq-archives/$DLQ_TOPIC/"
```

---

## Incident Response Playbook

### DLQ Spike Runbook

```plantuml
@startuml
skinparam backgroundColor transparent

|Operations|
start
:Receive DLQ spike alert;
:Check DLQ dashboard;
:Note: spike start time,\nrate, error types;

|Investigation|
:Sample 10 recent DLQ messages;
:Extract error class distribution;
:Identify source topic(s);

if (Single error type?) then (yes)
    :Likely code bug or\nupstream data change;
else (no)
    :Multiple failure modes;
    :Prioritize by volume;
endif

:Check recent deployments;
:Check upstream system changes;

|Resolution|
if (Code bug identified?) then (yes)
    :Create hotfix;
    :Deploy fix;
    :Monitor DLQ rate;
    if (Rate normalized?) then (yes)
        :Plan DLQ reprocessing;
    else (no)
        :Escalate to development;
    endif
elseif (Upstream data issue?) then (yes)
    :Contact upstream team;
    :Wait for data fix;
    :Reprocess after fix confirmed;
else (transient)
    :Monitor for recovery;
    :Auto-reprocess if stable;
endif

|Closure|
:Document incident;
:Update runbook if needed;
:Close alert;
stop

@enduml
```

### Quick Commands Reference

```bash
# Check DLQ depth
kafka-consumer-groups.sh --bootstrap-server broker1:9092 \
  --describe --group dlq-processor | grep "orders.dlq"

# Get DLQ message count
kafka-run-class.sh kafka.tools.GetOffsetShell \
  --broker-list broker1:9092 \
  --topic orders.dlq --time -1

# Sample recent errors
kafka-console-consumer.sh --bootstrap-server broker1:9092 \
  --topic orders.dlq --from-beginning --max-messages 5 \
  --property print.headers=true

# Pause DLQ consumer (for investigation)
kafka-consumer-groups.sh --bootstrap-server broker1:9092 \
  --group dlq-processor --topic orders.dlq \
  --reset-offsets --to-current --execute

# Count messages by error type (last 1000)
kafka-console-consumer.sh --bootstrap-server broker1:9092 \
  --topic orders.dlq --from-beginning --max-messages 1000 \
  --property print.headers=true 2>/dev/null | \
  grep -oP 'dlq\.error\.class:\K[^\s,]+' | sort | uniq -c | sort -rn
```

---

## Capacity Planning

### DLQ Sizing Guidelines

| Factor | Consideration |
|--------|---------------|
| **Expected error rate** | 0.1-1% of main topic volume typical |
| **Retention period** | 30-90 days for investigation window |
| **Message size** | Same as source + ~500 bytes headers |
| **Replication factor** | Match or exceed source topic RF |
| **Partition count** | 1-3 sufficient for most DLQs |

### Capacity Formula

```
DLQ Storage = Main Topic Volume × Error Rate × Retention Days × RF

Example:
- Main topic: 100 GB/day
- Error rate: 0.5%
- Retention: 30 days
- RF: 3

DLQ Storage = 100 GB × 0.005 × 30 × 3 = 45 GB
```

---

## Related Documentation

- [Dead Letter Queue Concepts](../../concepts/dead-letter-queues/index.md) - Conceptual overview
- [Implementing DLQs](../../application-development/error-handling/dead-letter-queues.md) - Code patterns
- [Monitoring Overview](../monitoring/index.md) - Kafka monitoring setup
- [Troubleshooting Guide](index.md) - General troubleshooting
