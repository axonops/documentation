---
title: "Kafka Go Client"
description: "Apache Kafka Go client guide using confluent-kafka-go. Producer, consumer, and admin client usage with configuration, error handling, and best practices."
meta:
  - name: keywords
    content: "Kafka Go, confluent-kafka-go, franz-go, segmentio kafka-go, Golang Kafka, Go Kafka producer"
---

# Kafka Go Client

The `confluent-kafka-go` library provides a high-performance Go client built on librdkafka. This guide covers installation, configuration, and usage patterns for Go applications.

---

## Client Information

| | |
|---|---|
| **Library** | `github.com/confluentinc/confluent-kafka-go` |
| **Repository** | [github.com/confluentinc/confluent-kafka-go](https://github.com/confluentinc/confluent-kafka-go) |
| **Documentation** | [docs.confluent.io/platform/current/clients/confluent-kafka-go](https://docs.confluent.io/platform/current/clients/confluent-kafka-go/index.html) |
| **Package** | [pkg.go.dev](https://pkg.go.dev/github.com/confluentinc/confluent-kafka-go/v2/kafka) |
| **Current Version** | v2.12.x (as of 2025) |
| **Maintainer** | Confluent |
| **License** | Apache License 2.0 |
| **Base** | librdkafka (C library via cgo) |

### History

The confluent-kafka-go library was first released by Confluent in 2017 as version 0.9.x. It uses cgo bindings to librdkafka, providing high performance while maintaining Go idioms. The v1.0 release (2019) brought API stability. The major v2.0 release in 2023 introduced Go modules support, improved APIs, and better error handling. The library requires cgo and either bundles a pre-built static librdkafka or links against a system-installed version.

### Pure Go Alternatives

For environments where cgo is problematic (cross-compilation, Alpine Linux, serverless), two popular pure Go implementations are available:

#### franz-go (Recommended Pure Go)

| | |
|---|---|
| **Library** | `github.com/twmb/franz-go` |
| **Repository** | [github.com/twmb/franz-go](https://github.com/twmb/franz-go) |
| **Documentation** | [pkg.go.dev](https://pkg.go.dev/github.com/twmb/franz-go/pkg/kgo) |
| **Current Version** | v1.20.x (as of 2025) |
| **Maintainer** | Travis Bischel (twmb) |
| **License** | BSD-3-Clause |

franz-go is a feature-complete, pure Go Kafka client supporting Kafka 0.8.0 through 4.1+. It implements the Kafka protocol directly in Go without any C dependencies. Features include full exactly-once semantics (EOS), transactions, all compression types (gzip, snappy, lz4, zstd), all SASL mechanisms, and consumer groups with eager and cooperative balancers. Used in production by Redpanda, Mux, Alpaca, and others.

#### segmentio/kafka-go

| | |
|---|---|
| **Library** | `github.com/segmentio/kafka-go` |
| **Repository** | [github.com/segmentio/kafka-go](https://github.com/segmentio/kafka-go) |
| **Documentation** | [pkg.go.dev](https://pkg.go.dev/github.com/segmentio/kafka-go) |
| **Current Version** | v0.4.x (as of 2025) |
| **Maintainer** | Segment |
| **License** | MIT |

kafka-go provides low and high level APIs mirroring Go standard library concepts. Pure Go implementation with no C dependencies. Supports consumer groups, TLS/SASL authentication, and all compression types.

### Client Comparison

| Feature | confluent-kafka-go | franz-go | segmentio/kafka-go |
|---------|-------------------|----------|-------------------|
| Implementation | librdkafka (cgo) | Pure Go | Pure Go |
| Performance | Highest | High | Good |
| Cross-compilation | Difficult | Easy | Easy |
| Transactions | ✅ | ✅ | ❌ |
| Exactly-once | ✅ | ✅ | ❌ |
| Alpine/musl | Requires setup | Works | Works |
| API style | librdkafka | Modern Go | Go stdlib |

### Version Compatibility

| Client Version | librdkafka | Minimum Kafka Broker |
|----------------|------------|---------------------|
| v2.12.x | 2.12.x | 0.8.0+ |
| v2.10.x | 2.10.x | 0.8.0+ |
| v2.6.x | 2.6.x | 0.8.0+ |
| v2.3.x | 2.3.x | 0.8.0+ |

### External Resources

- [Confluent Developer Go Guide](https://developer.confluent.io/get-started/go/)
- [GoDoc API Reference](https://pkg.go.dev/github.com/confluentinc/confluent-kafka-go/v2/kafka)
- [librdkafka Configuration](https://github.com/confluentinc/librdkafka/blob/master/CONFIGURATION.md)
- [GitHub Examples](https://github.com/confluentinc/confluent-kafka-go/tree/master/examples)

---

## Installation

### go get

```bash
go get github.com/confluentinc/confluent-kafka-go/v2/kafka
```

### go.mod

```go
require github.com/confluentinc/confluent-kafka-go/v2 v2.3.0
```

### Dependencies

The library requires librdkafka. On most systems, the library is statically linked and requires no additional installation. For custom builds:

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
    p, err := kafka.NewProducer(&kafka.ConfigMap{
        "bootstrap.servers": "kafka:9092",
        "client.id":        "order-service",
    })
    if err != nil {
        panic(err)
    }
    defer p.Close()

    // Delivery report handler for asynchronous sends
    go func() {
        for e := range p.Events() {
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

    // Asynchronous send
    topic := "orders"
    p.Produce(&kafka.Message{
        TopicPartition: kafka.TopicPartition{Topic: &topic, Partition: kafka.PartitionAny},
        Key:           []byte("order-123"),
        Value:         []byte(`{"id": 123, "amount": 99.99}`),
    }, nil)

    // Wait for outstanding messages to be delivered
    p.Flush(15 * 1000)
}
```

### Production Producer Configuration

```go
p, err := kafka.NewProducer(&kafka.ConfigMap{
    // Connection
    "bootstrap.servers": "kafka-1:9092,kafka-2:9092,kafka-3:9092",
    "client.id":        "order-service-producer",

    // Durability
    "acks":                "all",
    "enable.idempotence": true,

    // Retries
    "retries":                          2147483647,
    "delivery.timeout.ms":              120000,
    "max.in.flight.requests.per.connection": 5,

    // Batching
    "batch.size":                 65536,
    "linger.ms":                  10,
    "queue.buffering.max.messages": 100000,
    "queue.buffering.max.kbytes":   1048576,

    // Compression
    "compression.type": "lz4",
})
if err != nil {
    return err
}
```

### Synchronous Send

```go
func syncProduce(p *kafka.Producer, topic string, key, value []byte) error {
    deliveryChan := make(chan kafka.Event)
    defer close(deliveryChan)

    err := p.Produce(&kafka.Message{
        TopicPartition: kafka.TopicPartition{Topic: &topic, Partition: kafka.PartitionAny},
        Key:           key,
        Value:         value,
    }, deliveryChan)

    if err != nil {
        return err
    }

    e := <-deliveryChan
    m := e.(*kafka.Message)

    if m.TopicPartition.Error != nil {
        return m.TopicPartition.Error
    }

    fmt.Printf("Delivered to %s [%d] at offset %v\n",
        *m.TopicPartition.Topic,
        m.TopicPartition.Partition,
        m.TopicPartition.Offset)

    return nil
}
```

### Send with Headers

```go
topic := "orders"
err := p.Produce(&kafka.Message{
    TopicPartition: kafka.TopicPartition{Topic: &topic, Partition: kafka.PartitionAny},
    Key:           []byte("order-123"),
    Value:         []byte(`{"id": 123}`),
    Headers: []kafka.Header{
        {Key: "correlation-id", Value: []byte("abc-123")},
        {Key: "source", Value: []byte("order-service")},
    },
}, nil)
```

### Producer with Error Channel

```go
type ProducerService struct {
    producer *kafka.Producer
    done     chan bool
}

func NewProducerService(config *kafka.ConfigMap) (*ProducerService, error) {
    p, err := kafka.NewProducer(config)
    if err != nil {
        return nil, err
    }

    s := &ProducerService{
        producer: p,
        done:     make(chan bool),
    }

    go s.handleEvents()
    return s, nil
}

func (s *ProducerService) handleEvents() {
    for {
        select {
        case e := <-s.producer.Events():
            switch ev := e.(type) {
            case *kafka.Message:
                if ev.TopicPartition.Error != nil {
                    // Handle delivery error
                    log.Printf("Delivery failed: %v", ev.TopicPartition.Error)
                }
            case kafka.Error:
                // Handle producer errors
                log.Printf("Producer error: %v", ev)
                if ev.Code() == kafka.ErrAllBrokersDown {
                    // Critical error - may need to restart
                }
            }
        case <-s.done:
            return
        }
    }
}

func (s *ProducerService) Close() {
    s.done <- true
    s.producer.Flush(30 * 1000)
    s.producer.Close()
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
    "os"
    "os/signal"
    "syscall"
)

func main() {
    c, err := kafka.NewConsumer(&kafka.ConfigMap{
        "bootstrap.servers": "kafka:9092",
        "group.id":         "order-processors",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": false,
    })
    if err != nil {
        panic(err)
    }
    defer c.Close()

    c.SubscribeTopics([]string{"orders"}, nil)

    sigchan := make(chan os.Signal, 1)
    signal.Notify(sigchan, syscall.SIGINT, syscall.SIGTERM)

    run := true
    for run {
        select {
        case sig := <-sigchan:
            fmt.Printf("Caught signal %v: terminating\n", sig)
            run = false
        default:
            msg, err := c.ReadMessage(100 * time.Millisecond)
            if err != nil {
                // Timeout is not an error
                if err.(kafka.Error).Code() == kafka.ErrTimedOut {
                    continue
                }
                fmt.Printf("Consumer error: %v\n", err)
                continue
            }

            fmt.Printf("Received: key=%s value=%s partition=%d offset=%d\n",
                string(msg.Key), string(msg.Value), msg.TopicPartition.Partition, msg.TopicPartition.Offset)

            // Manual commit
            _, err = c.CommitMessage(msg)
            if err != nil {
                fmt.Printf("Commit error: %v\n", err)
            }
        }
    }
}
```

### Production Consumer Configuration

```go
c, err := kafka.NewConsumer(&kafka.ConfigMap{
    // Connection
    "bootstrap.servers": "kafka-1:9092,kafka-2:9092,kafka-3:9092",
    "group.id":         "order-processors",
    "client.id":        "order-processor-1",

    // Offset management
    "enable.auto.commit": false,
    "auto.offset.reset": "earliest",

    // Session management
    "session.timeout.ms":     45000,
    "heartbeat.interval.ms":  15000,
    "max.poll.interval.ms":   300000,

    // Fetch configuration
    "fetch.min.bytes":          1,
    "fetch.max.bytes":          52428800,
    "max.partition.fetch.bytes": 1048576,

    // Assignment strategy
    "partition.assignment.strategy": "cooperative-sticky",
})
if err != nil {
    return err
}
```

### Batch Processing

```go
func consumeBatch(c *kafka.Consumer, batchSize int, timeout time.Duration) ([]*kafka.Message, error) {
    messages := make([]*kafka.Message, 0, batchSize)
    deadline := time.Now().Add(timeout)

    for len(messages) < batchSize && time.Now().Before(deadline) {
        remaining := deadline.Sub(time.Now())
        if remaining <= 0 {
            break
        }

        msg, err := c.ReadMessage(remaining)
        if err != nil {
            if err.(kafka.Error).Code() == kafka.ErrTimedOut {
                break
            }
            return nil, err
        }

        messages = append(messages, msg)
    }

    return messages, nil
}

// Usage
for running {
    batch, err := consumeBatch(consumer, 500, 1*time.Second)
    if err != nil {
        log.Printf("Error consuming batch: %v", err)
        continue
    }

    if len(batch) > 0 {
        processBatch(batch)

        // Commit last message in batch
        lastMsg := batch[len(batch)-1]
        _, err = consumer.CommitMessage(lastMsg)
        if err != nil {
            log.Printf("Commit error: %v", err)
        }
    }
}
```

### Rebalance Listener

```go
func rebalanceCallback(c *kafka.Consumer, event kafka.Event) error {
    switch e := event.(type) {
    case kafka.AssignedPartitions:
        fmt.Printf("Partitions assigned: %v\n", e.Partitions)
        // Initialize state for new partitions
        err := c.Assign(e.Partitions)
        if err != nil {
            return err
        }

    case kafka.RevokedPartitions:
        fmt.Printf("Partitions revoked: %v\n", e.Partitions)
        // Commit offsets before rebalance
        _, err := c.Commit()
        if err != nil {
            log.Printf("Commit error during rebalance: %v", err)
        }
        err = c.Unassign()
        if err != nil {
            return err
        }

    case kafka.PartitionLoss:
        fmt.Printf("Partitions lost: %v\n", e.Partitions)
        // Handle unexpected partition loss
        err := c.Unassign()
        if err != nil {
            return err
        }
    }

    return nil
}

// Subscribe with rebalance callback
c.SubscribeTopics([]string{"orders"}, rebalanceCallback)
```

### Graceful Shutdown

```go
type Consumer struct {
    consumer *kafka.Consumer
    running  atomic.Bool
}

func NewConsumer(config *kafka.ConfigMap) (*Consumer, error) {
    c, err := kafka.NewConsumer(config)
    if err != nil {
        return nil, err
    }

    consumer := &Consumer{consumer: c}
    consumer.running.Store(true)
    return consumer, nil
}

func (c *Consumer) Consume(topics []string) error {
    err := c.consumer.SubscribeTopics(topics, nil)
    if err != nil {
        return err
    }

    sigchan := make(chan os.Signal, 1)
    signal.Notify(sigchan, syscall.SIGINT, syscall.SIGTERM)

    for c.running.Load() {
        select {
        case sig := <-sigchan:
            log.Printf("Caught signal %v: terminating\n", sig)
            c.running.Store(false)
        default:
            msg, err := c.consumer.ReadMessage(100 * time.Millisecond)
            if err != nil {
                if err.(kafka.Error).Code() == kafka.ErrTimedOut {
                    continue
                }
                log.Printf("Consumer error: %v\n", err)
                continue
            }

            c.processMessage(msg)

            _, err = c.consumer.CommitMessage(msg)
            if err != nil {
                log.Printf("Commit error: %v\n", err)
            }
        }
    }

    return nil
}

func (c *Consumer) Close() error {
    c.running.Store(false)
    return c.consumer.Close()
}
```

---

## Admin Client

### Create Topics

```go
import "github.com/confluentinc/confluent-kafka-go/v2/kafka"

a, err := kafka.NewAdminClient(&kafka.ConfigMap{
    "bootstrap.servers": "kafka:9092",
})
if err != nil {
    return err
}
defer a.Close()

topics := []kafka.TopicSpecification{
    {
        Topic:             "orders",
        NumPartitions:     6,
        ReplicationFactor: 3,
        Config: map[string]string{
            "retention.ms":   "604800000",
            "cleanup.policy": "delete",
        },
    },
}

ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
defer cancel()

results, err := a.CreateTopics(ctx, topics)
if err != nil {
    return err
}

for _, result := range results {
    if result.Error.Code() != kafka.ErrNoError {
        fmt.Printf("Failed to create topic %s: %v\n", result.Topic, result.Error)
    } else {
        fmt.Printf("Created topic %s\n", result.Topic)
    }
}
```

### Describe Topics

```go
ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
defer cancel()

metadata, err := a.GetMetadata(&"orders", false, int(30*time.Second/time.Millisecond))
if err != nil {
    return err
}

for _, topic := range metadata.Topics {
    fmt.Printf("Topic: %s\n", topic.Topic)
    for _, partition := range topic.Partitions {
        fmt.Printf("  Partition %d: leader=%d replicas=%v isr=%v\n",
            partition.ID,
            partition.Leader,
            partition.Replicas,
            partition.Isrs)
    }
}
```

### List Consumer Groups

```go
ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
defer cancel()

result, err := a.ListConsumerGroups(ctx)
if err != nil {
    return err
}

for _, group := range result.Valid {
    fmt.Printf("Group: %s (state: %s)\n", group.GroupID, group.State)
}
```

### Describe Consumer Groups

```go
ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
defer cancel()

results, err := a.DescribeConsumerGroups(ctx, []string{"order-processors"})
if err != nil {
    return err
}

for _, result := range results {
    if result.Error.Code() != kafka.ErrNoError {
        fmt.Printf("Error describing group: %v\n", result.Error)
        continue
    }

    fmt.Printf("Group: %s\n", result.GroupID)
    fmt.Printf("State: %s\n", result.State)
    fmt.Printf("Members:\n")
    for _, member := range result.Members {
        fmt.Printf("  %s (client: %s)\n", member.MemberID, member.ClientID)
    }
}
```

---

## Error Handling

### Producer Error Handling

```go
func handleProducerEvent(e kafka.Event) {
    switch ev := e.(type) {
    case *kafka.Message:
        if ev.TopicPartition.Error != nil {
            err := ev.TopicPartition.Error

            // Check if error is retriable
            if err.(kafka.Error).IsRetriable() {
                log.Printf("Retriable error, producer will retry: %v", err)
                return
            }

            switch err.(kafka.Error).Code() {
            case kafka.ErrMsgSizeTooLarge:
                log.Printf("Message too large, sending to DLQ")
                sendToDeadLetterQueue(ev)
            case kafka.ErrTopicAuthorizationFailed:
                log.Printf("Authorization failed for topic %s", *ev.TopicPartition.Topic)
                // Requires intervention
            case kafka.ErrBrokerNotAvailable:
                log.Printf("Broker not available: %v", err)
            default:
                log.Printf("Production error: %v", err)
            }
        }

    case kafka.Error:
        log.Printf("Producer error: %v (code: %v)", ev, ev.Code())
        if ev.Code() == kafka.ErrAllBrokersDown {
            log.Printf("All brokers down - critical error")
            // May need to restart or alert
        }
    }
}
```

### Consumer Error Handling

```go
for running {
    msg, err := consumer.ReadMessage(100 * time.Millisecond)

    if err != nil {
        kafkaErr, ok := err.(kafka.Error)
        if !ok {
            log.Printf("Non-Kafka error: %v", err)
            continue
        }

        switch kafkaErr.Code() {
        case kafka.ErrTimedOut:
            // Not an error, just no messages
            continue

        case kafka.ErrPartitionEOF:
            // End of partition, not an error
            continue

        case kafka.ErrUnknownTopicOrPart:
            log.Printf("Topic does not exist")
            continue

        case kafka.ErrTopicAuthorizationFailed:
            log.Printf("Authorization failed")
            return kafkaErr

        default:
            if kafkaErr.IsRetriable() {
                log.Printf("Retriable error: %v", kafkaErr)
                continue
            }
            log.Printf("Fatal consumer error: %v", kafkaErr)
            return kafkaErr
        }
    }

    // Process message
    if err := processMessage(msg); err != nil {
        log.Printf("Processing error: %v", err)
        sendToDeadLetterQueue(msg, err)
    }

    _, err = consumer.CommitMessage(msg)
    if err != nil {
        log.Printf("Commit error: %v", err)
    }
}
```

### Error Classification

```go
func classifyError(err error) string {
    kafkaErr, ok := err.(kafka.Error)
    if !ok {
        return "unknown"
    }

    if kafkaErr.IsRetriable() {
        return "retriable"
    }

    if kafkaErr.IsFatal() {
        return "fatal"
    }

    switch kafkaErr.Code() {
    case kafka.ErrTopicAuthorizationFailed,
         kafka.ErrGroupAuthorizationFailed,
         kafka.ErrClusterAuthorizationFailed:
        return "authorization"

    case kafka.ErrInvalidMsg,
         kafka.ErrMsgSizeTooLarge,
         kafka.ErrInvalidMsgSize:
        return "invalid_message"

    case kafka.ErrNetworkException,
         kafka.ErrAllBrokersDown,
         kafka.ErrBrokerNotAvailable:
        return "network"

    default:
        return "other"
    }
}
```

---

## Testing

### Mock Producer

```go
type MockProducer struct {
    messages []*kafka.Message
    mu       sync.Mutex
}

func (m *MockProducer) Produce(msg *kafka.Message, deliveryChan chan kafka.Event) error {
    m.mu.Lock()
    defer m.mu.Unlock()

    m.messages = append(m.messages, msg)

    if deliveryChan != nil {
        go func() {
            deliveryChan <- msg
        }()
    }

    return nil
}

func (m *MockProducer) Flush(timeoutMs int) int {
    return 0
}

func (m *MockProducer) Close() {}

func (m *MockProducer) GetMessages() []*kafka.Message {
    m.mu.Lock()
    defer m.mu.Unlock()
    return m.messages
}

// Usage in tests
func TestOrderService(t *testing.T) {
    mock := &MockProducer{}
    service := NewOrderService(mock)

    err := service.CreateOrder(Order{ID: "123", Amount: 99.99})
    assert.NoError(t, err)

    messages := mock.GetMessages()
    assert.Len(t, messages, 1)
    assert.Equal(t, "orders", *messages[0].TopicPartition.Topic)
    assert.Equal(t, []byte("123"), messages[0].Key)
}
```

### Integration Testing

```go
import (
    "testing"
    "github.com/testcontainers/testcontainers-go"
    "github.com/testcontainers/testcontainers-go/wait"
)

func setupKafkaContainer(t *testing.T) (string, func()) {
    ctx := context.Background()

    req := testcontainers.ContainerRequest{
        Image:        "confluentinc/cp-kafka:7.5.0",
        ExposedPorts: []string{"9093/tcp"},
        Env: map[string]string{
            "KAFKA_BROKER_ID":                        "1",
            "KAFKA_LISTENER_SECURITY_PROTOCOL_MAP":   "PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT",
            "KAFKA_ADVERTISED_LISTENERS":             "PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9093",
            "KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR": "1",
            "KAFKA_TRANSACTION_STATE_LOG_MIN_ISR":    "1",
            "KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR": "1",
        },
        WaitingFor: wait.ForLog("started (kafka.server.KafkaServer)"),
    }

    container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
        ContainerRequest: req,
        Started:          true,
    })
    if err != nil {
        t.Fatal(err)
    }

    host, err := container.Host(ctx)
    if err != nil {
        t.Fatal(err)
    }

    port, err := container.MappedPort(ctx, "9093")
    if err != nil {
        t.Fatal(err)
    }

    bootstrapServer := fmt.Sprintf("%s:%s", host, port.Port())

    cleanup := func() {
        container.Terminate(ctx)
    }

    return bootstrapServer, cleanup
}

func TestProduceConsume(t *testing.T) {
    bootstrapServer, cleanup := setupKafkaContainer(t)
    defer cleanup()

    // Test producer
    p, err := kafka.NewProducer(&kafka.ConfigMap{
        "bootstrap.servers": bootstrapServer,
    })
    assert.NoError(t, err)
    defer p.Close()

    topic := "test"
    err = p.Produce(&kafka.Message{
        TopicPartition: kafka.TopicPartition{Topic: &topic, Partition: kafka.PartitionAny},
        Key:           []byte("key"),
        Value:         []byte("value"),
    }, nil)
    assert.NoError(t, err)
    p.Flush(30 * 1000)

    // Test consumer
    c, err := kafka.NewConsumer(&kafka.ConfigMap{
        "bootstrap.servers": bootstrapServer,
        "group.id":         "test",
        "auto.offset.reset": "earliest",
    })
    assert.NoError(t, err)
    defer c.Close()

    c.SubscribeTopics([]string{"test"}, nil)

    msg, err := c.ReadMessage(10 * time.Second)
    assert.NoError(t, err)
    assert.Equal(t, []byte("value"), msg.Value)
}
```

### Table-Driven Tests

```go
func TestProducerSend(t *testing.T) {
    tests := []struct {
        name      string
        topic     string
        key       []byte
        value     []byte
        wantError bool
    }{
        {
            name:      "valid message",
            topic:     "orders",
            key:       []byte("123"),
            value:     []byte(`{"id": 123}`),
            wantError: false,
        },
        {
            name:      "empty value",
            topic:     "orders",
            key:       []byte("123"),
            value:     []byte(""),
            wantError: false,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            mock := &MockProducer{}
            err := mock.Produce(&kafka.Message{
                TopicPartition: kafka.TopicPartition{Topic: &tt.topic},
                Key:           tt.key,
                Value:         tt.value,
            }, nil)

            if tt.wantError {
                assert.Error(t, err)
            } else {
                assert.NoError(t, err)
            }
        })
    }
}
```

---

## Related Documentation

- [Producer Development](../producers/index.md) - Producer patterns
- [Consumer Development](../consumers/index.md) - Consumer patterns
- [Transactions](../producers/transactions.md) - Transaction patterns
