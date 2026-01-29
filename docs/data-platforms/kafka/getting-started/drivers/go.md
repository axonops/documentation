---
title: "Kafka Go Driver"
description: "Kafka Go client. Installation, configuration, producer and consumer examples with confluent-kafka-go."
meta:
  - name: keywords
    content: "Kafka Go quickstart, Golang Kafka tutorial, Go producer consumer, confluent-kafka-go getting started"
---

# Kafka Go Driver

The confluent-kafka-go library provides a high-performance Go client based on librdkafka.

---

## Installation

```bash
go get github.com/confluentinc/confluent-kafka-go/v2/kafka
```

### Build Requirements

The library requires librdkafka. On most systems, a pre-built version is included.

For custom builds:

```bash
# macOS
brew install librdkafka

# Ubuntu/Debian
apt-get install librdkafka-dev

# RHEL/CentOS
yum install librdkafka-devel
```

---

## Producer

### Basic Producer

```go
package main

import (
    "fmt"
    "github.com/confluentinc/confluent-kafka-go/v2/kafka"
)

func main() {
    producer, err := kafka.NewProducer(&kafka.ConfigMap{
        "bootstrap.servers": "localhost:9092",
    })
    if err != nil {
        panic(err)
    }
    defer producer.Close()

    topic := "events"

    // Delivery report handler
    go func() {
        for e := range producer.Events() {
            switch ev := e.(type) {
            case *kafka.Message:
                if ev.TopicPartition.Error != nil {
                    fmt.Printf("Delivery failed: %v\n", ev.TopicPartition.Error)
                } else {
                    fmt.Printf("Delivered to %v\n", ev.TopicPartition)
                }
            }
        }
    }()

    // Produce message
    producer.Produce(&kafka.Message{
        TopicPartition: kafka.TopicPartition{Topic: &topic, Partition: kafka.PartitionAny},
        Key:            []byte("key"),
        Value:          []byte("value"),
    }, nil)

    // Wait for delivery
    producer.Flush(15 * 1000)
}
```

### Reliable Producer

```go
producer, err := kafka.NewProducer(&kafka.ConfigMap{
    "bootstrap.servers":            "localhost:9092",
    "acks":                         "all",
    "retries":                      10,
    "retry.backoff.ms":             100,
    "enable.idempotence":           true,
    "max.in.flight.requests.per.connection": 5,
    "linger.ms":                    5,
    "batch.size":                   16384,
    "compression.type":             "lz4",
})
```

### Synchronous Produce

```go
func produceSyncWithTimeout(producer *kafka.Producer, msg *kafka.Message, timeout time.Duration) error {
    deliveryChan := make(chan kafka.Event)

    err := producer.Produce(msg, deliveryChan)
    if err != nil {
        return err
    }

    select {
    case e := <-deliveryChan:
        m := e.(*kafka.Message)
        if m.TopicPartition.Error != nil {
            return m.TopicPartition.Error
        }
        return nil
    case <-time.After(timeout):
        return fmt.Errorf("produce timeout")
    }
}
```

---

## Consumer

### Basic Consumer

```go
package main

import (
    "fmt"
    "github.com/confluentinc/confluent-kafka-go/v2/kafka"
)

func main() {
    consumer, err := kafka.NewConsumer(&kafka.ConfigMap{
        "bootstrap.servers": "localhost:9092",
        "group.id":          "my-group",
        "auto.offset.reset": "earliest",
    })
    if err != nil {
        panic(err)
    }
    defer consumer.Close()

    consumer.SubscribeTopics([]string{"events"}, nil)

    for {
        msg, err := consumer.ReadMessage(-1)
        if err != nil {
            fmt.Printf("Consumer error: %v\n", err)
            continue
        }
        fmt.Printf("Received: %s\n", string(msg.Value))
    }
}
```

### Manual Commit

```go
consumer, err := kafka.NewConsumer(&kafka.ConfigMap{
    "bootstrap.servers":  "localhost:9092",
    "group.id":           "my-group",
    "enable.auto.commit": false,
    "auto.offset.reset":  "earliest",
})

consumer.SubscribeTopics([]string{"events"}, nil)

for {
    msg, err := consumer.ReadMessage(time.Second)
    if err != nil {
        if err.(kafka.Error).Code() == kafka.ErrTimedOut {
            continue
        }
        fmt.Printf("Error: %v\n", err)
        continue
    }

    // Process message
    process(msg)

    // Commit offset
    _, err = consumer.CommitMessage(msg)
    if err != nil {
        fmt.Printf("Commit error: %v\n", err)
    }
}
```

### Batch Processing

```go
for {
    ev := consumer.Poll(100)
    if ev == nil {
        continue
    }

    switch e := ev.(type) {
    case *kafka.Message:
        batch = append(batch, e)

        if len(batch) >= 100 {
            processBatch(batch)
            consumer.Commit()
            batch = batch[:0]
        }

    case kafka.Error:
        fmt.Printf("Error: %v\n", e)
    }
}
```

---

## Admin Client

### Create Topic

```go
package main

import (
    "context"
    "fmt"
    "github.com/confluentinc/confluent-kafka-go/v2/kafka"
)

func main() {
    admin, err := kafka.NewAdminClient(&kafka.ConfigMap{
        "bootstrap.servers": "localhost:9092",
    })
    if err != nil {
        panic(err)
    }
    defer admin.Close()

    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()

    results, err := admin.CreateTopics(ctx, []kafka.TopicSpecification{
        {
            Topic:             "my-topic",
            NumPartitions:     3,
            ReplicationFactor: 3,
        },
    })
    if err != nil {
        panic(err)
    }

    for _, result := range results {
        fmt.Printf("Topic: %s, Error: %v\n", result.Topic, result.Error)
    }
}
```

### Describe Topics

```go
metadata, err := admin.GetMetadata(nil, true, 5000)
if err != nil {
    panic(err)
}

for _, topic := range metadata.Topics {
    fmt.Printf("Topic: %s, Partitions: %d\n", topic.Topic, len(topic.Partitions))
}
```

---

## Configuration Reference

### Producer

| Property | Description | Default |
|----------|-------------|:-------:|
| `acks` | Acknowledgments | 1 |
| `retries` | Retry count | 2147483647 |
| `batch.size` | Batch bytes | 16384 |
| `linger.ms` | Batch delay | 5 |
| `enable.idempotence` | Idempotent | false |
| `compression.type` | Compression | none |

### Consumer

| Property | Description | Default |
|----------|-------------|:-------:|
| `group.id` | Consumer group | Required |
| `auto.offset.reset` | Reset behavior | latest |
| `enable.auto.commit` | Auto commit | true |
| `max.poll.interval.ms` | Max poll interval | 300000 |
| `session.timeout.ms` | Session timeout | 45000 |

---

## Error Handling

```go
msg, err := consumer.ReadMessage(time.Second)
if err != nil {
    kafkaErr, ok := err.(kafka.Error)
    if !ok {
        log.Printf("Unknown error: %v", err)
        continue
    }

    switch kafkaErr.Code() {
    case kafka.ErrTimedOut:
        // Normal timeout, continue
        continue
    case kafka.ErrUnknownTopicOrPart:
        log.Printf("Topic doesn't exist")
    case kafka.ErrAllBrokersDown:
        log.Printf("All brokers down")
        time.Sleep(5 * time.Second)
    default:
        log.Printf("Kafka error: %v", kafkaErr)
    }
    continue
}
```

---

## Graceful Shutdown

```go
package main

import (
    "os"
    "os/signal"
    "syscall"
)

func main() {
    consumer, _ := kafka.NewConsumer(&kafka.ConfigMap{
        "bootstrap.servers": "localhost:9092",
        "group.id":          "my-group",
    })

    consumer.SubscribeTopics([]string{"events"}, nil)

    sigchan := make(chan os.Signal, 1)
    signal.Notify(sigchan, syscall.SIGINT, syscall.SIGTERM)

    run := true
    for run {
        select {
        case <-sigchan:
            run = false
        default:
            ev := consumer.Poll(100)
            if ev == nil {
                continue
            }

            switch e := ev.(type) {
            case *kafka.Message:
                process(e)
            case kafka.Error:
                log.Printf("Error: %v", e)
            }
        }
    }

    consumer.Close()
}
```

---

## JSON Serialization

```go
import (
    "encoding/json"
)

type Event struct {
    ID        string `json:"id"`
    Timestamp int64  `json:"timestamp"`
    Data      string `json:"data"`
}

func produceJSON(producer *kafka.Producer, topic string, event Event) error {
    value, err := json.Marshal(event)
    if err != nil {
        return err
    }

    return producer.Produce(&kafka.Message{
        TopicPartition: kafka.TopicPartition{Topic: &topic, Partition: kafka.PartitionAny},
        Value:          value,
    }, nil)
}

func consumeJSON(msg *kafka.Message) (*Event, error) {
    var event Event
    err := json.Unmarshal(msg.Value, &event)
    return &event, err
}
```

---

## Related Documentation

- [Drivers Overview](index.md) - All client drivers
- [Producer Guide](../../application-development/producers/index.md) - Producer patterns
- [Consumer Guide](../../application-development/consumers/index.md) - Consumer patterns
- [Schema Registry](../../schema-registry/index.md) - Schema management