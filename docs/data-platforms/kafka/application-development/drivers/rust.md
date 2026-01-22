---
title: "Kafka Rust Client"
description: "Apache Kafka Rust client guide using rdkafka. Producer, consumer, and admin client usage with async support, configuration, and best practices."
meta:
  - name: keywords
    content: "Kafka Rust, rdkafka, Rust Kafka client, Tokio Kafka, async Kafka, Cargo kafka"
---

# Kafka Rust Client

The `rdkafka` library provides a high-performance Rust client built on librdkafka with native async/await support. This guide covers installation, configuration, and usage patterns for Rust applications.

---

## Client Information

| | |
|---|---|
| **Library** | `rdkafka` |
| **Repository** | [github.com/fede1024/rust-rdkafka](https://github.com/fede1024/rust-rdkafka) |
| **Documentation** | [docs.rs/rdkafka](https://docs.rs/rdkafka/latest/rdkafka/) |
| **Package** | [crates.io](https://crates.io/crates/rdkafka) |
| **Current Version** | 0.38.x (as of 2025) |
| **Maintainer** | Federico Giraud and community |
| **License** | MIT |
| **Base** | librdkafka (C library via FFI) |

### History

The rust-rdkafka library was created by Federico Giraud in 2016, providing Rust bindings to librdkafka through the Foreign Function Interface (FFI). It was designed to provide idiomatic Rust APIs while leveraging the performance and reliability of librdkafka. Async/await support via the Tokio runtime was added in 2019. The library remains at version 0.x, indicating ongoing API evolution, though the core APIs are stable and widely used in production. It is the de facto standard Kafka client for the Rust ecosystem.

### Feature Flags

The library supports various cargo features:

| Feature | Description |
|---------|-------------|
| `cmake-build` | Build librdkafka from source |
| `ssl` | Enable SSL/TLS support |
| `sasl` | Enable SASL authentication |
| `tokio` | Async runtime support (default) |
| `smol` | Alternative async runtime |

### Version Compatibility

| Client Version | librdkafka | Minimum Rust | Tokio |
|----------------|------------|--------------|-------|
| 0.38.x | 2.10.x+ | 1.70+ | 1.x |
| 0.36.x | 2.3.x+ | 1.70+ | 1.x |
| 0.34.x | 2.2.x+ | 1.65+ | 1.x |

### Alternative: kafka-rust

A pure Rust implementation without librdkafka dependency (less maintained):

| | |
|---|---|
| **Library** | `kafka` |
| **Repository** | [github.com/kafka-rust/kafka-rust](https://github.com/kafka-rust/kafka-rust) |
| **Note** | Pure Rust but less feature-complete and less maintained |

### External Resources

- [API Documentation](https://docs.rs/rdkafka/latest/rdkafka/)
- [GitHub Examples](https://github.com/fede1024/rust-rdkafka/tree/master/examples)
- [librdkafka Configuration](https://github.com/confluentinc/librdkafka/blob/master/CONFIGURATION.md)
- [Tokio Runtime](https://tokio.rs/)

---

## Installation

### Cargo.toml

```toml
[dependencies]
rdkafka = { version = "0.38", features = ["cmake-build"] }
tokio = { version = "1", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
```

### With SSL Support

```toml
[dependencies]
rdkafka = { version = "0.38", features = ["cmake-build", "ssl", "sasl"] }
```

### Native Dependencies

The library requires librdkafka. The `cmake-build` feature compiles librdkafka from source. For system librdkafka:

```toml
[dependencies]
rdkafka = "0.38"
```

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

```rust
use rdkafka::config::ClientConfig;
use rdkafka::producer::{FutureProducer, FutureRecord};
use std::time::Duration;

#[tokio::main]
async fn main() {
    let producer: FutureProducer = ClientConfig::new()
        .set("bootstrap.servers", "kafka:9092")
        .set("client.id", "order-service")
        .create()
        .expect("Failed to create producer");

    let topic = "orders";
    let key = "order-123";
    let payload = r#"{"id": 123, "amount": 99.99}"#;

    let delivery_result = producer
        .send(
            FutureRecord::to(topic)
                .key(key)
                .payload(payload),
            Duration::from_secs(5),
        )
        .await;

    match delivery_result {
        Ok((partition, offset)) => {
            println!("Delivered to partition {} at offset {}", partition, offset);
        }
        Err((err, _)) => {
            eprintln!("Delivery failed: {:?}", err);
        }
    }
}
```

### Production Producer Configuration

```rust
use rdkafka::config::ClientConfig;
use rdkafka::producer::FutureProducer;

let producer: FutureProducer = ClientConfig::new()
    // Connection
    .set("bootstrap.servers", "kafka-1:9092,kafka-2:9092,kafka-3:9092")
    .set("client.id", "order-service-producer")

    // Durability
    .set("acks", "all")
    .set("enable.idempotence", "true")

    // Retries
    .set("retries", "2147483647")
    .set("delivery.timeout.ms", "120000")
    .set("max.in.flight.requests.per.connection", "5")

    // Batching
    .set("batch.size", "65536")
    .set("linger.ms", "10")
    .set("queue.buffering.max.messages", "100000")
    .set("queue.buffering.max.kbytes", "1048576")

    // Compression
    .set("compression.type", "lz4")

    .create()
    .expect("Failed to create producer");
```

### Send with Headers

```rust
use rdkafka::message::{Header, OwnedHeaders};

let headers = OwnedHeaders::new()
    .insert(Header {
        key: "correlation-id",
        value: Some("abc-123"),
    })
    .insert(Header {
        key: "source",
        value: Some("order-service"),
    });

let delivery_result = producer
    .send(
        FutureRecord::to("orders")
            .key("order-123")
            .payload(r#"{"id": 123}"#)
            .headers(headers),
        Duration::from_secs(5),
    )
    .await;
```

### Async Producer with Error Handling

```rust
use rdkafka::error::KafkaError;
use rdkafka::producer::FutureProducer;
use std::time::Duration;

struct ProducerService {
    producer: FutureProducer,
}

impl ProducerService {
    fn new(bootstrap_servers: &str) -> Result<Self, KafkaError> {
        let producer = ClientConfig::new()
            .set("bootstrap.servers", bootstrap_servers)
            .set("client.id", "order-service")
            .set("acks", "all")
            .set("enable.idempotence", "true")
            .create()?;

        Ok(Self { producer })
    }

    async fn send(
        &self,
        topic: &str,
        key: &str,
        payload: &str,
    ) -> Result<(i32, i64), KafkaError> {
        let record = FutureRecord::to(topic).key(key).payload(payload);

        match self.producer.send(record, Duration::from_secs(5)).await {
            Ok((partition, offset)) => {
                println!("Delivered to partition {} at offset {}", partition, offset);
                Ok((partition, offset))
            }
            Err((err, _)) => {
                eprintln!("Delivery failed: {:?}", err);
                Err(err)
            }
        }
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let service = ProducerService::new("kafka:9092")?;
    service.send("orders", "123", r#"{"id": 123}"#).await?;
    Ok(())
}
```

### ThreadedProducer for Fire-and-Forget

```rust
use rdkafka::config::ClientConfig;
use rdkafka::producer::{BaseRecord, ThreadedProducer};

let producer: ThreadedProducer<_> = ClientConfig::new()
    .set("bootstrap.servers", "kafka:9092")
    .create()
    .expect("Failed to create producer");

// Fire-and-forget (callback-based)
producer
    .send(
        BaseRecord::to("orders")
            .key("order-123")
            .payload(r#"{"id": 123}"#),
    )
    .unwrap_or_else(|e| {
        eprintln!("Failed to send: {:?}", e.0);
    });

// Wait for all messages to be delivered
producer.flush(Duration::from_secs(10));
```

---

## Consumer

### Basic Consumer

```rust
use rdkafka::config::ClientConfig;
use rdkafka::consumer::{StreamConsumer, Consumer};
use rdkafka::message::Message;

#[tokio::main]
async fn main() {
    let consumer: StreamConsumer = ClientConfig::new()
        .set("bootstrap.servers", "kafka:9092")
        .set("group.id", "order-processors")
        .set("auto.offset.reset", "earliest")
        .set("enable.auto.commit", "false")
        .create()
        .expect("Failed to create consumer");

    consumer
        .subscribe(&["orders"])
        .expect("Failed to subscribe");

    loop {
        match consumer.recv().await {
            Ok(message) => {
                let key = message.key().map(|k| String::from_utf8_lossy(k));
                let payload = message.payload().map(|p| String::from_utf8_lossy(p));

                println!(
                    "Received: key={:?} value={:?} partition={} offset={}",
                    key,
                    payload,
                    message.partition(),
                    message.offset()
                );

                consumer.commit_message(&message, rdkafka::consumer::CommitMode::Async)
                    .expect("Failed to commit");
            }
            Err(e) => {
                eprintln!("Consumer error: {:?}", e);
            }
        }
    }
}
```

### Production Consumer Configuration

```rust
use rdkafka::config::ClientConfig;
use rdkafka::consumer::StreamConsumer;

let consumer: StreamConsumer = ClientConfig::new()
    // Connection
    .set("bootstrap.servers", "kafka-1:9092,kafka-2:9092,kafka-3:9092")
    .set("group.id", "order-processors")
    .set("client.id", "order-processor-1")

    // Offset management
    .set("enable.auto.commit", "false")
    .set("auto.offset.reset", "earliest")

    // Session management
    .set("session.timeout.ms", "45000")
    .set("heartbeat.interval.ms", "15000")
    .set("max.poll.interval.ms", "300000")

    // Fetch configuration
    .set("fetch.min.bytes", "1")
    .set("fetch.max.bytes", "52428800")
    .set("max.partition.fetch.bytes", "1048576")

    // Assignment strategy
    .set("partition.assignment.strategy", "cooperative-sticky")

    // Isolation level
    .set("isolation.level", "read_committed")

    .create()
    .expect("Failed to create consumer");
```

### Stream-based Consumer

```rust
use rdkafka::consumer::StreamConsumer;
use futures::StreamExt;

#[tokio::main]
async fn main() {
    let consumer: StreamConsumer = ClientConfig::new()
        .set("bootstrap.servers", "kafka:9092")
        .set("group.id", "order-processors")
        .set("enable.auto.commit", "false")
        .create()
        .expect("Failed to create consumer");

    consumer.subscribe(&["orders"]).expect("Failed to subscribe");

    let mut message_stream = consumer.stream();

    while let Some(message) = message_stream.next().await {
        match message {
            Ok(msg) => {
                if let Some(payload) = msg.payload() {
                    let value = String::from_utf8_lossy(payload);
                    println!("Received: {}", value);

                    process_message(&value).await;

                    consumer
                        .commit_message(&msg, rdkafka::consumer::CommitMode::Async)
                        .expect("Failed to commit");
                }
            }
            Err(e) => {
                eprintln!("Stream error: {:?}", e);
            }
        }
    }
}

async fn process_message(value: &str) {
    // Process message
    tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
}
```

### Consumer with Graceful Shutdown

```rust
use rdkafka::consumer::{Consumer, StreamConsumer};
use tokio::signal;
use futures::StreamExt;

#[tokio::main]
async fn main() {
    let consumer: StreamConsumer = ClientConfig::new()
        .set("bootstrap.servers", "kafka:9092")
        .set("group.id", "order-processors")
        .create()
        .expect("Failed to create consumer");

    consumer.subscribe(&["orders"]).expect("Failed to subscribe");

    let mut message_stream = consumer.stream();

    loop {
        tokio::select! {
            _ = signal::ctrl_c() => {
                println!("Shutting down...");
                break;
            }
            message = message_stream.next() => {
                match message {
                    Some(Ok(msg)) => {
                        process_message(&msg).await;
                        consumer.commit_message(&msg, rdkafka::consumer::CommitMode::Async)
                            .expect("Failed to commit");
                    }
                    Some(Err(e)) => {
                        eprintln!("Error: {:?}", e);
                    }
                    None => break,
                }
            }
        }
    }

    println!("Consumer stopped");
}

async fn process_message(msg: &rdkafka::message::BorrowedMessage<'_>) {
    if let Some(payload) = msg.payload() {
        let value = String::from_utf8_lossy(payload);
        println!("Processing: {}", value);
    }
}
```

### Batch Processing with Buffer

```rust
use rdkafka::consumer::StreamConsumer;
use futures::StreamExt;
use tokio::time::{Duration, timeout};

async fn consume_batch(
    consumer: &StreamConsumer,
    batch_size: usize,
    timeout_duration: Duration,
) -> Vec<rdkafka::message::OwnedMessage> {
    let mut batch = Vec::with_capacity(batch_size);
    let mut message_stream = consumer.stream();

    let batch_future = async {
        while batch.len() < batch_size {
            if let Some(Ok(msg)) = message_stream.next().await {
                batch.push(msg.detach());
            } else {
                break;
            }
        }
        batch
    };

    timeout(timeout_duration, batch_future)
        .await
        .unwrap_or_else(|_| batch)
}

#[tokio::main]
async fn main() {
    let consumer: StreamConsumer = ClientConfig::new()
        .set("bootstrap.servers", "kafka:9092")
        .set("group.id", "order-processors")
        .set("enable.auto.commit", "false")
        .create()
        .expect("Failed to create consumer");

    consumer.subscribe(&["orders"]).expect("Failed to subscribe");

    loop {
        let batch = consume_batch(&consumer, 500, Duration::from_secs(1)).await;

        if !batch.is_empty() {
            println!("Processing batch of {} messages", batch.len());

            for msg in &batch {
                process_owned_message(msg).await;
            }

            // Commit last message
            if let Some(last_msg) = batch.last() {
                consumer
                    .commit_consumer_state(rdkafka::consumer::CommitMode::Async)
                    .expect("Failed to commit");
            }
        }
    }
}

async fn process_owned_message(msg: &rdkafka::message::OwnedMessage) {
    if let Some(payload) = msg.payload() {
        let value = String::from_utf8_lossy(payload);
        println!("Processed: {}", value);
    }
}
```

### Manual Partition Assignment

```rust
use rdkafka::consumer::{Consumer, BaseConsumer};
use rdkafka::topic_partition_list::TopicPartitionList;
use rdkafka::Offset;

let consumer: BaseConsumer = ClientConfig::new()
    .set("bootstrap.servers", "kafka:9092")
    .set("group.id", "order-processors")
    .create()
    .expect("Failed to create consumer");

// Assign specific partitions
let mut tpl = TopicPartitionList::new();
tpl.add_partition("orders", 0);
tpl.add_partition("orders", 1);

consumer.assign(&tpl).expect("Failed to assign partitions");

// Seek to specific offset
let mut tpl_seek = TopicPartitionList::new();
tpl_seek.add_partition_offset("orders", 0, Offset::Offset(1000))
    .expect("Failed to add partition");

consumer.seek_partitions(tpl_seek, Duration::from_secs(5))
    .expect("Failed to seek");
```

---

## Error Handling

### Producer Error Handling

```rust
use rdkafka::error::{KafkaError, RDKafkaErrorCode};

async fn send_with_error_handling(
    producer: &FutureProducer,
    topic: &str,
    key: &str,
    payload: &str,
) -> Result<(i32, i64), String> {
    let record = FutureRecord::to(topic).key(key).payload(payload);

    match producer.send(record, Duration::from_secs(5)).await {
        Ok((partition, offset)) => Ok((partition, offset)),
        Err((err, _)) => {
            match err {
                KafkaError::MessageProduction(code) => {
                    match code {
                        RDKafkaErrorCode::MessageSizeTooLarge => {
                            eprintln!("Message too large, sending to DLQ");
                            Err("Message too large".to_string())
                        }
                        RDKafkaErrorCode::TopicAuthorizationFailed => {
                            eprintln!("Authorization failed");
                            Err("Not authorized".to_string())
                        }
                        _ => {
                            eprintln!("Production error: {:?}", code);
                            Err(format!("Production error: {:?}", code))
                        }
                    }
                }
                _ => {
                    eprintln!("Kafka error: {:?}", err);
                    Err(format!("Kafka error: {:?}", err))
                }
            }
        }
    }
}
```

### Consumer Error Handling

```rust
use rdkafka::error::KafkaError;
use rdkafka::consumer::ConsumerContext;
use rdkafka::client::ClientContext;

// Custom context for error handling
struct CustomContext;

impl ClientContext for CustomContext {}

impl ConsumerContext for CustomContext {
    fn commit_callback(&self, result: rdkafka::error::KafkaResult<()>, _offsets: &rdkafka::TopicPartitionList) {
        match result {
            Ok(_) => println!("Offset committed successfully"),
            Err(e) => eprintln!("Commit error: {:?}", e),
        }
    }
}

#[tokio::main]
async fn main() {
    let context = CustomContext;

    let consumer: StreamConsumer<CustomContext> = ClientConfig::new()
        .set("bootstrap.servers", "kafka:9092")
        .set("group.id", "order-processors")
        .create_with_context(context)
        .expect("Failed to create consumer");

    consumer.subscribe(&["orders"]).expect("Failed to subscribe");

    loop {
        match consumer.recv().await {
            Ok(msg) => {
                match process_message(&msg).await {
                    Ok(_) => {
                        consumer
                            .commit_message(&msg, rdkafka::consumer::CommitMode::Async)
                            .unwrap_or_else(|e| eprintln!("Commit error: {:?}", e));
                    }
                    Err(e) => {
                        eprintln!("Processing error: {:?}", e);
                        // Send to DLQ
                        send_to_dlq(&msg).await;
                        // Still commit to move forward
                        consumer
                            .commit_message(&msg, rdkafka::consumer::CommitMode::Async)
                            .unwrap_or_else(|e| eprintln!("Commit error: {:?}", e));
                    }
                }
            }
            Err(e) => {
                eprintln!("Consumer error: {:?}", e);
            }
        }
    }
}

async fn process_message(msg: &rdkafka::message::BorrowedMessage<'_>) -> Result<(), String> {
    // Process message
    Ok(())
}

async fn send_to_dlq(msg: &rdkafka::message::BorrowedMessage<'_>) {
    // Send to dead letter queue
}
```

### Retry with Exponential Backoff

```rust
use tokio::time::{sleep, Duration};

async fn send_with_retry(
    producer: &FutureProducer,
    topic: &str,
    key: &str,
    payload: &str,
    max_retries: u32,
) -> Result<(i32, i64), KafkaError> {
    let mut attempt = 0;

    loop {
        let record = FutureRecord::to(topic).key(key).payload(payload);

        match producer.send(record, Duration::from_secs(5)).await {
            Ok((partition, offset)) => return Ok((partition, offset)),
            Err((err, _)) => {
                attempt += 1;

                if attempt >= max_retries {
                    return Err(err);
                }

                // Exponential backoff
                let backoff = Duration::from_millis(100 * 2u64.pow(attempt));
                let backoff = backoff.min(Duration::from_secs(30));

                eprintln!("Retry attempt {} after {:?}", attempt, backoff);
                sleep(backoff).await;
            }
        }
    }
}
```

---

## Testing

### Mock Producer

```rust
#[cfg(test)]
mod tests {
    use std::sync::{Arc, Mutex};

    struct MockProducer {
        messages: Arc<Mutex<Vec<(String, String, String)>>>,
    }

    impl MockProducer {
        fn new() -> Self {
            Self {
                messages: Arc::new(Mutex::new(Vec::new())),
            }
        }

        async fn send(&self, topic: &str, key: &str, payload: &str) -> Result<(), String> {
            self.messages
                .lock()
                .unwrap()
                .push((topic.to_string(), key.to_string(), payload.to_string()));
            Ok(())
        }

        fn get_messages(&self) -> Vec<(String, String, String)> {
            self.messages.lock().unwrap().clone()
        }
    }

    #[tokio::test]
    async fn test_order_service() {
        let mock = MockProducer::new();

        mock.send("orders", "123", r#"{"id": 123}"#)
            .await
            .expect("Failed to send");

        let messages = mock.get_messages();
        assert_eq!(messages.len(), 1);
        assert_eq!(messages[0].0, "orders");
        assert_eq!(messages[0].1, "123");
    }
}
```

### Integration Testing

```rust
#[cfg(test)]
mod integration_tests {
    use super::*;
    use rdkafka::config::ClientConfig;
    use rdkafka::consumer::{Consumer, StreamConsumer};
    use rdkafka::producer::FutureProducer;
    use tokio::time::Duration;

    async fn setup_kafka() -> (FutureProducer, StreamConsumer) {
        let bootstrap_servers = "localhost:9092";

        let producer = ClientConfig::new()
            .set("bootstrap.servers", bootstrap_servers)
            .create()
            .expect("Failed to create producer");

        let consumer = ClientConfig::new()
            .set("bootstrap.servers", bootstrap_servers)
            .set("group.id", "test")
            .set("auto.offset.reset", "earliest")
            .create()
            .expect("Failed to create consumer");

        (producer, consumer)
    }

    #[tokio::test]
    #[ignore] // Run with: cargo test -- --ignored
    async fn test_produce_consume() {
        let (producer, consumer) = setup_kafka().await;

        consumer.subscribe(&["test"]).expect("Failed to subscribe");

        // Produce
        let record = FutureRecord::to("test")
            .key("key")
            .payload("value");

        producer
            .send(record, Duration::from_secs(5))
            .await
            .expect("Failed to produce");

        // Consume
        let msg = consumer.recv().await.expect("Failed to consume");

        assert_eq!(
            msg.payload().map(|p| String::from_utf8_lossy(p)),
            Some(std::borrow::Cow::from("value"))
        );
    }
}
```

### Property-based Testing with Proptest

```rust
#[cfg(test)]
mod proptests {
    use proptest::prelude::*;

    proptest! {
        #[test]
        fn test_message_serialization(
            id in 0u64..1000000,
            amount in 0.0f64..1000000.0
        ) {
            let json = serde_json::json!({
                "id": id,
                "amount": amount
            });

            let serialized = serde_json::to_string(&json).unwrap();
            let deserialized: serde_json::Value = serde_json::from_str(&serialized).unwrap();

            assert_eq!(deserialized["id"], id);
            assert_eq!(deserialized["amount"], amount);
        }
    }
}
```

---

## Tokio Integration

### Multi-threaded Runtime

```rust
use rdkafka::consumer::StreamConsumer;
use tokio::runtime::Runtime;
use futures::StreamExt;

fn main() {
    let runtime = Runtime::new().unwrap();

    runtime.block_on(async {
        let consumer: StreamConsumer = ClientConfig::new()
            .set("bootstrap.servers", "kafka:9092")
            .set("group.id", "order-processors")
            .create()
            .expect("Failed to create consumer");

        consumer.subscribe(&["orders"]).expect("Failed to subscribe");

        let mut message_stream = consumer.stream();

        while let Some(message) = message_stream.next().await {
            match message {
                Ok(msg) => {
                    tokio::spawn(async move {
                        process_message_async(&msg).await;
                    });
                }
                Err(e) => eprintln!("Error: {:?}", e),
            }
        }
    });
}

async fn process_message_async(msg: &rdkafka::message::BorrowedMessage<'_>) {
    // Async processing
}
```

### Concurrent Consumer Pool

```rust
use rdkafka::consumer::StreamConsumer;
use futures::StreamExt;
use std::sync::Arc;

#[tokio::main]
async fn main() {
    let num_consumers = 4;
    let mut handles = Vec::new();

    for i in 0..num_consumers {
        let handle = tokio::spawn(async move {
            let consumer: StreamConsumer = ClientConfig::new()
                .set("bootstrap.servers", "kafka:9092")
                .set("group.id", "order-processors")
                .set("client.id", &format!("consumer-{}", i))
                .create()
                .expect("Failed to create consumer");

            consumer.subscribe(&["orders"]).expect("Failed to subscribe");

            let mut message_stream = consumer.stream();

            while let Some(message) = message_stream.next().await {
                match message {
                    Ok(msg) => {
                        process_message(&msg).await;
                        consumer
                            .commit_message(&msg, rdkafka::consumer::CommitMode::Async)
                            .expect("Failed to commit");
                    }
                    Err(e) => eprintln!("Error: {:?}", e),
                }
            }
        });

        handles.push(handle);
    }

    // Wait for all consumers
    for handle in handles {
        handle.await.unwrap();
    }
}

async fn process_message(msg: &rdkafka::message::BorrowedMessage<'_>) {
    // Process message
}
```

---

## Related Documentation

- [Producer Development](../producers/index.md) - Producer patterns
- [Consumer Development](../consumers/index.md) - Consumer patterns
- [Transactions](../producers/transactions.md) - Transaction patterns
