---
title: "Kafka .NET Client"
description: "Apache Kafka .NET client guide using confluent-kafka-dotnet. Producer, consumer, and admin client usage with configuration, error handling, and best practices."
meta:
  - name: keywords
    content: "Kafka .NET, Confluent.Kafka, C# Kafka, .NET Kafka producer, NuGet Kafka, Kafka ASP.NET"
---

# Kafka .NET Client

The `Confluent.Kafka` library provides a high-performance .NET client built on librdkafka. This guide covers installation, configuration, and usage patterns for .NET applications.

---

## Client Information

| | |
|---|---|
| **Library** | `Confluent.Kafka` |
| **Repository** | [github.com/confluentinc/confluent-kafka-dotnet](https://github.com/confluentinc/confluent-kafka-dotnet) |
| **Documentation** | [docs.confluent.io/platform/current/clients/confluent-kafka-dotnet](https://docs.confluent.io/platform/current/clients/confluent-kafka-dotnet/_site/api/Confluent.Kafka.html) |
| **Package** | [NuGet](https://www.nuget.org/packages/Confluent.Kafka/) |
| **Current Version** | 2.12.x (as of 2025) |
| **Maintainer** | Confluent |
| **License** | Apache License 2.0 |
| **Base** | librdkafka (C library via P/Invoke) |

### History

The .NET Kafka client was originally released as `RdKafka` in 2016 by Andreas Heider, providing P/Invoke bindings to librdkafka. Confluent acquired and rebranded the project to `Confluent.Kafka` in 2017, investing in improved APIs and documentation. The library uses Platform Invocation Services (P/Invoke) to call librdkafka, which is bundled as native binaries for Windows, Linux, and macOS. The library supports .NET Standard 2.0+, .NET Framework 4.6.2+, and .NET Core 2.0+, making it suitable for both legacy and modern .NET applications.

### Platform Support

| Platform | Architecture | Notes |
|----------|--------------|-------|
| Windows | x64, x86 | Native libraries bundled |
| Linux | x64, arm64 | Native libraries bundled |
| macOS | x64, arm64 | Native libraries bundled |

### Version Compatibility

| Client Version | librdkafka | .NET | .NET Framework |
|----------------|------------|------|----------------|
| 2.12.x | 2.12.x | 6.0+ | 4.6.2+ |
| 2.10.x | 2.10.x | 6.0+ | 4.6.2+ |
| 2.6.x | 2.6.x | 6.0+ | 4.6.2+ |
| 2.3.x | 2.3.x | 6.0+ | 4.6.2+ |

### External Resources

- [Confluent Developer .NET Guide](https://developer.confluent.io/get-started/dotnet/)
- [NuGet Package](https://www.nuget.org/packages/Confluent.Kafka/)
- [API Reference](https://docs.confluent.io/platform/current/clients/confluent-kafka-dotnet/_site/api/Confluent.Kafka.html)
- [librdkafka Configuration](https://github.com/confluentinc/librdkafka/blob/master/CONFIGURATION.md)
- [GitHub Examples](https://github.com/confluentinc/confluent-kafka-dotnet/tree/master/examples)

---

## Installation

### NuGet Package Manager

```bash
Install-Package Confluent.Kafka
```

### .NET CLI

```bash
dotnet add package Confluent.Kafka
```

### PackageReference

```xml
<!-- Use the current Confluent.Kafka version -->
<PackageReference Include="Confluent.Kafka" Version="2.12.0" />
```

### With Schema Registry

```bash
dotnet add package Confluent.SchemaRegistry
dotnet add package Confluent.SchemaRegistry.Serdes.Avro
```

---

## Producer

### Basic Producer

```csharp
using Confluent.Kafka;
using System;

class Program
{
    static void Main(string[] args)
    {
        var config = new ProducerConfig
        {
            BootstrapServers = "kafka:9092",
            ClientId = "order-service"
        };

        using (var producer = new ProducerBuilder<string, string>(config).Build())
        {
            try
            {
                var result = producer.ProduceAsync("orders",
                    new Message<string, string>
                    {
                        Key = "order-123",
                        Value = "{\"id\": 123, \"amount\": 99.99}"
                    }).GetAwaiter().GetResult();

                Console.WriteLine($"Delivered to {result.TopicPartitionOffset}");
            }
            catch (ProduceException<string, string> e)
            {
                Console.WriteLine($"Delivery failed: {e.Error.Reason}");
            }
        }
    }
}
```

### Production Producer Configuration

```csharp
var config = new ProducerConfig
{
    // Connection
    BootstrapServers = "kafka-1:9092,kafka-2:9092,kafka-3:9092",
    ClientId = "order-service-producer",

    // Durability
    Acks = Acks.All,
    EnableIdempotence = true,

    // Retries
    MessageSendMaxRetries = int.MaxValue,
    RequestTimeoutMs = 30000,
    MessageTimeoutMs = 120000,
    MaxInFlight = 5,

    // Batching
    BatchSize = 65536,
    LingerMs = 10,
    QueueBufferingMaxMessages = 100000,
    QueueBufferingMaxKbytes = 1048576,

    // Compression
    CompressionType = CompressionType.Lz4,

    // Error handling
    EnableDeliveryReports = true,
    DeliveryReportFields = "all"
};
```

### Asynchronous Send

```csharp
using var producer = new ProducerBuilder<string, string>(config).Build();

// Fire-and-forget (not recommended for production)
producer.Produce("orders",
    new Message<string, string> { Key = "key", Value = "value" },
    deliveryHandler: (deliveryReport) =>
    {
        if (deliveryReport.Error.Code != ErrorCode.NoError)
        {
            Console.WriteLine($"Delivery failed: {deliveryReport.Error.Reason}");
        }
        else
        {
            Console.WriteLine($"Delivered to {deliveryReport.TopicPartitionOffset}");
        }
    });

// Async/await pattern
var deliveryResult = await producer.ProduceAsync("orders",
    new Message<string, string> { Key = "key", Value = "value" });

Console.WriteLine($"Delivered to partition {deliveryResult.Partition} at offset {deliveryResult.Offset}");
```

### Send with Headers

```csharp
var message = new Message<string, string>
{
    Key = "order-123",
    Value = "{\"id\": 123}",
    Headers = new Headers
    {
        { "correlation-id", Encoding.UTF8.GetBytes("abc-123") },
        { "source", Encoding.UTF8.GetBytes("order-service") }
    }
};

await producer.ProduceAsync("orders", message);
```

### Custom Partitioner

```csharp
public class RegionPartitioner : IPartitioner
{
    public int Partition(string topic, int partitionCount, ReadOnlySpan<byte> keyData, bool keyIsNull)
    {
        if (keyIsNull)
        {
            return Random.Shared.Next(partitionCount);
        }

        var key = Encoding.UTF8.GetString(keyData);

        // Route by region prefix
        if (key.StartsWith("US-")) return 0;
        if (key.StartsWith("EU-")) return 1;

        // Default: hash-based
        return Math.Abs(key.GetHashCode()) % partitionCount;
    }

    public void Dispose() { }
}

// Usage
var config = new ProducerConfig
{
    BootstrapServers = "kafka:9092",
    Partitioner = Partitioner.Consistent
};

var producer = new ProducerBuilder<string, string>(config)
    .SetPartitioner(new RegionPartitioner())
    .Build();
```

### Producer Service with Dependency Injection

```csharp
public interface IKafkaProducer
{
    Task<DeliveryResult<string, string>> SendAsync(string topic, string key, string value);
}

public class KafkaProducer : IKafkaProducer, IDisposable
{
    private readonly IProducer<string, string> _producer;
    private readonly ILogger<KafkaProducer> _logger;

    public KafkaProducer(IConfiguration configuration, ILogger<KafkaProducer> logger)
    {
        _logger = logger;

        var config = new ProducerConfig
        {
            BootstrapServers = configuration["Kafka:BootstrapServers"],
            ClientId = configuration["Kafka:ClientId"],
            Acks = Acks.All,
            EnableIdempotence = true,
            CompressionType = CompressionType.Lz4
        };

        _producer = new ProducerBuilder<string, string>(config)
            .SetErrorHandler((_, error) =>
            {
                _logger.LogError("Producer error: {Error}", error.Reason);
            })
            .Build();
    }

    public async Task<DeliveryResult<string, string>> SendAsync(string topic, string key, string value)
    {
        try
        {
            var result = await _producer.ProduceAsync(topic,
                new Message<string, string> { Key = key, Value = value });

            _logger.LogInformation(
                "Message delivered to {Topic} [{Partition}] at offset {Offset}",
                result.Topic, result.Partition, result.Offset);

            return result;
        }
        catch (ProduceException<string, string> ex)
        {
            _logger.LogError(ex, "Failed to deliver message: {Reason}", ex.Error.Reason);
            throw;
        }
    }

    public void Dispose()
    {
        _producer?.Flush(TimeSpan.FromSeconds(10));
        _producer?.Dispose();
    }
}

// Startup.cs / Program.cs
services.AddSingleton<IKafkaProducer, KafkaProducer>();
```

---

## Consumer

### Basic Consumer

```csharp
using Confluent.Kafka;
using System;

class Program
{
    static void Main(string[] args)
    {
        var config = new ConsumerConfig
        {
            BootstrapServers = "kafka:9092",
            GroupId = "order-processors",
            AutoOffsetReset = AutoOffsetReset.Earliest,
            EnableAutoCommit = false
        };

        using (var consumer = new ConsumerBuilder<string, string>(config).Build())
        {
            consumer.Subscribe("orders");

            try
            {
                while (true)
                {
                    var cr = consumer.Consume(TimeSpan.FromMilliseconds(100));

                    if (cr != null)
                    {
                        Console.WriteLine($"Received: {cr.Message.Key} = {cr.Message.Value}");
                        Console.WriteLine($"Partition: {cr.Partition}, Offset: {cr.Offset}");

                        consumer.Commit(cr);
                    }
                }
            }
            catch (ConsumeException e)
            {
                Console.WriteLine($"Error: {e.Error.Reason}");
            }
            finally
            {
                consumer.Close();
            }
        }
    }
}
```

### Production Consumer Configuration

```csharp
var config = new ConsumerConfig
{
    // Connection
    BootstrapServers = "kafka-1:9092,kafka-2:9092,kafka-3:9092",
    GroupId = "order-processors",
    ClientId = "order-processor-1",

    // Offset management
    EnableAutoCommit = false,
    AutoOffsetReset = AutoOffsetReset.Earliest,

    // Session management
    SessionTimeoutMs = 45000,
    HeartbeatIntervalMs = 15000,
    MaxPollIntervalMs = 300000,

    // Fetch configuration
    FetchMinBytes = 1,
    FetchMaxBytes = 52428800,
    MaxPartitionFetchBytes = 1048576,

    // Assignment strategy
    PartitionAssignmentStrategy = PartitionAssignmentStrategy.CooperativeSticky,

    // Performance
    IsolationLevel = IsolationLevel.ReadCommitted
};
```

### Async Consumer Pattern

```csharp
public class ConsumerService : BackgroundService
{
    private readonly ILogger<ConsumerService> _logger;
    private readonly IConsumer<string, string> _consumer;

    public ConsumerService(IConfiguration configuration, ILogger<ConsumerService> logger)
    {
        _logger = logger;

        var config = new ConsumerConfig
        {
            BootstrapServers = configuration["Kafka:BootstrapServers"],
            GroupId = "order-processors",
            AutoOffsetReset = AutoOffsetReset.Earliest,
            EnableAutoCommit = false
        };

        _consumer = new ConsumerBuilder<string, string>(config)
            .SetErrorHandler((_, e) => _logger.LogError("Consumer error: {Reason}", e.Reason))
            .Build();
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _consumer.Subscribe("orders");

        try
        {
            while (!stoppingToken.IsCancellationRequested)
            {
                try
                {
                    var cr = _consumer.Consume(stoppingToken);

                    if (cr != null)
                    {
                        await ProcessMessageAsync(cr.Message, stoppingToken);
                        _consumer.Commit(cr);
                    }
                }
                catch (ConsumeException ex)
                {
                    _logger.LogError(ex, "Consume error: {Reason}", ex.Error.Reason);
                }
            }
        }
        finally
        {
            _consumer.Close();
        }
    }

    private async Task ProcessMessageAsync(Message<string, string> message, CancellationToken cancellationToken)
    {
        _logger.LogInformation("Processing message: {Key} = {Value}", message.Key, message.Value);
        await Task.Delay(100, cancellationToken); // Simulate processing
    }

    public override void Dispose()
    {
        _consumer?.Dispose();
        base.Dispose();
    }
}

// Program.cs
services.AddHostedService<ConsumerService>();
```

### Batch Processing

```csharp
var batch = new List<ConsumeResult<string, string>>();
var batchSize = 500;
var timeout = TimeSpan.FromSeconds(1);

while (!cancellationToken.IsCancellationRequested)
{
    batch.Clear();

    var deadline = DateTime.UtcNow.Add(timeout);

    while (batch.Count < batchSize && DateTime.UtcNow < deadline)
    {
        var remaining = deadline - DateTime.UtcNow;
        if (remaining <= TimeSpan.Zero) break;

        var cr = consumer.Consume(remaining);
        if (cr != null)
        {
            batch.Add(cr);
        }
    }

    if (batch.Count > 0)
    {
        await ProcessBatchAsync(batch);

        // Commit last message in batch
        consumer.Commit(batch[^1]);
    }
}
```

### Rebalance Callbacks

```csharp
var consumer = new ConsumerBuilder<string, string>(config)
    .SetPartitionsAssignedHandler((c, partitions) =>
    {
        _logger.LogInformation("Partitions assigned: {Partitions}",
            string.Join(", ", partitions));
        // Initialize state for new partitions
    })
    .SetPartitionsRevokedHandler((c, partitions) =>
    {
        _logger.LogInformation("Partitions revoked: {Partitions}",
            string.Join(", ", partitions));
        // Commit offsets before rebalance
        try
        {
            c.Commit(partitions);
        }
        catch (KafkaException ex)
        {
            _logger.LogError(ex, "Commit error during rebalance");
        }
    })
    .SetPartitionsLostHandler((c, partitions) =>
    {
        _logger.LogWarning("Partitions lost: {Partitions}",
            string.Join(", ", partitions));
        // Handle unexpected partition loss
    })
    .Build();
```

### Manual Partition Assignment

```csharp
using Confluent.Kafka;

var consumer = new ConsumerBuilder<string, string>(config).Build();

// Assign specific partitions
var partitions = new[]
{
    new TopicPartition("orders", 0),
    new TopicPartition("orders", 1)
};

consumer.Assign(partitions);

// Seek to specific offset
consumer.Seek(new TopicPartitionOffset("orders", 0, 1000));

// Seek to beginning
consumer.Seek(new TopicPartitionOffset("orders", 0, Offset.Beginning));
```

---

## Admin Client

### Create Topics

```csharp
using Confluent.Kafka.Admin;
using System.Collections.Generic;

var config = new AdminClientConfig
{
    BootstrapServers = "kafka:9092"
};

using var admin = new AdminClientBuilder(config).Build();

var topicSpec = new TopicSpecification
{
    Name = "orders",
    NumPartitions = 6,
    ReplicationFactor = 3,
    Configs = new Dictionary<string, string>
    {
        { "retention.ms", "604800000" },
        { "cleanup.policy", "delete" }
    }
};

try
{
    await admin.CreateTopicsAsync(new[] { topicSpec });
    Console.WriteLine("Topic created successfully");
}
catch (CreateTopicsException ex)
{
    Console.WriteLine($"Failed to create topic: {ex.Results[0].Error.Reason}");
}
```

### Describe Topics

```csharp
var metadata = admin.GetMetadata("orders", TimeSpan.FromSeconds(10));

foreach (var topic in metadata.Topics)
{
    Console.WriteLine($"Topic: {topic.Topic}");

    foreach (var partition in topic.Partitions)
    {
        Console.WriteLine($"  Partition {partition.PartitionId}:");
        Console.WriteLine($"    Leader: {partition.Leader}");
        Console.WriteLine($"    Replicas: {string.Join(", ", partition.Replicas)}");
        Console.WriteLine($"    ISR: {string.Join(", ", partition.InSyncReplicas)}");
    }
}
```

### Delete Topics

```csharp
try
{
    await admin.DeleteTopicsAsync(new[] { "old-topic" });
    Console.WriteLine("Topic deleted successfully");
}
catch (DeleteTopicsException ex)
{
    Console.WriteLine($"Failed to delete topic: {ex.Results[0].Error.Reason}");
}
```

### List Consumer Groups

```csharp
var groups = await admin.ListGroupsAsync(TimeSpan.FromSeconds(10));

foreach (var group in groups)
{
    Console.WriteLine($"Group: {group.Group} (Protocol: {group.ProtocolType})");
}
```

### Describe Consumer Group

```csharp
var groupInfo = await admin.DescribeConsumerGroupsAsync(
    new[] { "order-processors" },
    new DescribeConsumerGroupsOptions { RequestTimeout = TimeSpan.FromSeconds(10) });

foreach (var group in groupInfo)
{
    Console.WriteLine($"Group: {group.GroupId}");
    Console.WriteLine($"State: {group.State}");

    foreach (var member in group.Members)
    {
        Console.WriteLine($"  Member: {member.MemberId}");
        Console.WriteLine($"    Client: {member.ClientId}");
    }
}
```

---

## Error Handling

### Producer Error Handling

```csharp
var producer = new ProducerBuilder<string, string>(config)
    .SetErrorHandler((_, error) =>
    {
        _logger.LogError("Producer error: {Code} - {Reason}", error.Code, error.Reason);

        if (error.IsFatal)
        {
            _logger.LogCritical("Fatal producer error - requires restart");
        }

        if (error.IsLocalError)
        {
            _logger.LogWarning("Local error - may be transient");
        }
    })
    .Build();

// Delivery error handling
try
{
    var result = await producer.ProduceAsync("orders",
        new Message<string, string> { Key = "key", Value = "value" });
}
catch (ProduceException<string, string> ex)
{
    if (ex.Error.Code == ErrorCode.TopicAuthorizationFailed)
    {
        _logger.LogError("Authorization failed for topic");
    }
    else if (ex.Error.Code == ErrorCode.MsgSizeTooLarge)
    {
        _logger.LogError("Message too large");
        await SendToDeadLetterQueueAsync(ex.DeliveryResult.Message);
    }
    else if (ex.Error.IsRetriable)
    {
        _logger.LogWarning("Retriable error: {Reason}", ex.Error.Reason);
    }
    else
    {
        _logger.LogError(ex, "Fatal delivery error");
        throw;
    }
}
```

### Consumer Error Handling

```csharp
while (!stoppingToken.IsCancellationRequested)
{
    try
    {
        var cr = consumer.Consume(stoppingToken);

        if (cr == null) continue;

        try
        {
            await ProcessMessageAsync(cr.Message);
            consumer.Commit(cr);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Processing error for message at offset {Offset}", cr.Offset);

            // Send to dead letter queue
            await deadLetterProducer.ProduceAsync("orders-dlq",
                new Message<string, string>
                {
                    Key = cr.Message.Key,
                    Value = cr.Message.Value,
                    Headers = new Headers(cr.Message.Headers)
                    {
                        { "original-topic", Encoding.UTF8.GetBytes(cr.Topic) },
                        { "original-partition", BitConverter.GetBytes(cr.Partition.Value) },
                        { "original-offset", BitConverter.GetBytes(cr.Offset.Value) },
                        { "error", Encoding.UTF8.GetBytes(ex.Message) }
                    }
                });

            // Still commit to move forward
            consumer.Commit(cr);
        }
    }
    catch (ConsumeException ex)
    {
        _logger.LogError(ex, "Consume error: {Code} - {Reason}", ex.Error.Code, ex.Error.Reason);

        if (ex.Error.Code == ErrorCode.TopicAuthorizationFailed)
        {
            throw; // Fatal - can't recover
        }
    }
    catch (KafkaException ex)
    {
        _logger.LogError(ex, "Kafka error: {Reason}", ex.Error.Reason);

        if (ex.Error.IsFatal)
        {
            throw;
        }
    }
}
```

---

## Testing

### Mock Producer

```csharp
public class MockProducer<TKey, TValue> : IProducer<TKey, TValue>
{
    public List<Message<TKey, TValue>> Messages { get; } = new();

    public Handle Handle => throw new NotImplementedException();
    public string Name => "MockProducer";

    public Task<DeliveryResult<TKey, TValue>> ProduceAsync(
        string topic,
        Message<TKey, TValue> message,
        CancellationToken cancellationToken = default)
    {
        Messages.Add(message);

        var result = new DeliveryResult<TKey, TValue>
        {
            TopicPartitionOffset = new TopicPartitionOffset(topic, 0, 0),
            Message = message,
            Status = PersistenceStatus.Persisted
        };

        return Task.FromResult(result);
    }

    public void Produce(string topic, Message<TKey, TValue> message,
        Action<DeliveryReport<TKey, TValue>> deliveryHandler = null)
    {
        Messages.Add(message);
        deliveryHandler?.Invoke(new DeliveryReport<TKey, TValue>
        {
            TopicPartitionOffset = new TopicPartitionOffset(topic, 0, 0),
            Message = message,
            Status = PersistenceStatus.Persisted
        });
    }

    public int Flush(TimeSpan timeout) => 0;
    public void Flush(CancellationToken cancellationToken = default) { }
    public int Poll(TimeSpan timeout) => 0;
    public void Dispose() { }

    // Other interface methods omitted for brevity
}
```

### Unit Testing with xUnit

```csharp
public class OrderServiceTests
{
    [Fact]
    public async Task CreateOrder_ShouldSendMessageToKafka()
    {
        // Arrange
        var mockProducer = new MockProducer<string, string>();
        var service = new OrderService(mockProducer);

        var order = new Order { Id = "123", Amount = 99.99m };

        // Act
        await service.CreateOrderAsync(order);

        // Assert
        Assert.Single(mockProducer.Messages);

        var message = mockProducer.Messages[0];
        Assert.Equal("123", message.Key);

        var orderData = JsonSerializer.Deserialize<Order>(message.Value);
        Assert.Equal(99.99m, orderData.Amount);
    }

    [Fact]
    public async Task CreateOrder_WithHeaders_ShouldIncludeCorrelationId()
    {
        // Arrange
        var mockProducer = new MockProducer<string, string>();
        var service = new OrderService(mockProducer);

        // Act
        await service.CreateOrderAsync(new Order { Id = "123" }, correlationId: "abc-123");

        // Assert
        var message = mockProducer.Messages[0];
        Assert.NotNull(message.Headers);

        var header = message.Headers.FirstOrDefault(h => h.Key == "correlation-id");
        Assert.NotNull(header);
        Assert.Equal("abc-123", Encoding.UTF8.GetString(header.GetValueBytes()));
    }
}
```

### Integration Testing

```csharp
public class KafkaIntegrationTests : IClassFixture<KafkaFixture>
{
    private readonly KafkaFixture _fixture;

    public KafkaIntegrationTests(KafkaFixture fixture)
    {
        _fixture = fixture;
    }

    [Fact]
    public async Task ProduceConsume_ShouldWorkEndToEnd()
    {
        // Arrange
        var producerConfig = new ProducerConfig
        {
            BootstrapServers = _fixture.BootstrapServers
        };

        var consumerConfig = new ConsumerConfig
        {
            BootstrapServers = _fixture.BootstrapServers,
            GroupId = "test",
            AutoOffsetReset = AutoOffsetReset.Earliest
        };

        // Act - Produce
        using var producer = new ProducerBuilder<string, string>(producerConfig).Build();
        await producer.ProduceAsync("test",
            new Message<string, string> { Key = "key", Value = "value" });

        // Act - Consume
        using var consumer = new ConsumerBuilder<string, string>(consumerConfig).Build();
        consumer.Subscribe("test");

        var cr = consumer.Consume(TimeSpan.FromSeconds(10));

        // Assert
        Assert.NotNull(cr);
        Assert.Equal("value", cr.Message.Value);
    }
}

public class KafkaFixture : IDisposable
{
    // Use Testcontainers or Docker Compose for integration tests
    public string BootstrapServers { get; } = "localhost:9092";

    public void Dispose()
    {
        // Cleanup
    }
}
```

---

## Related Documentation

- [Producer Development](../producers/index.md) - Producer patterns
- [Consumer Development](../consumers/index.md) - Consumer patterns
- [Transactions](../producers/transactions.md) - Transaction patterns
