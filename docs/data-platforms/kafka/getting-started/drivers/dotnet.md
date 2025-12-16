---
title: "Kafka .NET Driver"
description: "Kafka .NET client. Installation, configuration, producer and consumer examples with Confluent.Kafka."
meta:
  - name: keywords
    content: "Kafka .NET quickstart, C# Kafka tutorial, .NET producer consumer, Confluent.Kafka getting started"
---

# Kafka .NET Driver

The Confluent.Kafka library provides a high-performance .NET client based on librdkafka.

---

## Installation

### NuGet Package Manager

```powershell
Install-Package Confluent.Kafka
```

### .NET CLI

```bash
dotnet add package Confluent.Kafka
```

### With Avro Serialization

```bash
dotnet add package Confluent.SchemaRegistry.Serdes.Avro
```

---

## Producer

### Basic Producer

```csharp
using Confluent.Kafka;

var config = new ProducerConfig
{
    BootstrapServers = "localhost:9092"
};

using var producer = new ProducerBuilder<string, string>(config).Build();

var result = await producer.ProduceAsync("events",
    new Message<string, string>
    {
        Key = "key",
        Value = "value"
    });

Console.WriteLine($"Delivered to {result.TopicPartitionOffset}");
```

### Reliable Producer

```csharp
var config = new ProducerConfig
{
    BootstrapServers = "localhost:9092",
    Acks = Acks.All,
    EnableIdempotence = true,
    MaxInFlight = 5,
    MessageSendMaxRetries = 10,
    RetryBackoffMs = 100,
    LingerMs = 5,
    BatchSize = 16384,
    CompressionType = CompressionType.Lz4
};

using var producer = new ProducerBuilder<string, string>(config)
    .SetErrorHandler((_, e) => Console.WriteLine($"Error: {e.Reason}"))
    .Build();
```

### Fire and Forget

```csharp
producer.Produce("events", new Message<string, string>
{
    Key = "key",
    Value = "value"
}, deliveryReport =>
{
    if (deliveryReport.Error.Code != ErrorCode.NoError)
    {
        Console.WriteLine($"Delivery failed: {deliveryReport.Error.Reason}");
    }
});

// Flush before exit
producer.Flush(TimeSpan.FromSeconds(10));
```

### Transactional Producer

```csharp
var config = new ProducerConfig
{
    BootstrapServers = "localhost:9092",
    TransactionalId = "my-transactional-id",
    EnableIdempotence = true
};

using var producer = new ProducerBuilder<string, string>(config).Build();

producer.InitTransactions(TimeSpan.FromSeconds(30));

try
{
    producer.BeginTransaction();

    await producer.ProduceAsync("topic1", new Message<string, string> { Value = "msg1" });
    await producer.ProduceAsync("topic2", new Message<string, string> { Value = "msg2" });

    producer.CommitTransaction();
}
catch (Exception)
{
    producer.AbortTransaction();
    throw;
}
```

---

## Consumer

### Basic Consumer

```csharp
using Confluent.Kafka;

var config = new ConsumerConfig
{
    BootstrapServers = "localhost:9092",
    GroupId = "my-group",
    AutoOffsetReset = AutoOffsetReset.Earliest
};

using var consumer = new ConsumerBuilder<string, string>(config).Build();

consumer.Subscribe("events");

var cts = new CancellationTokenSource();

try
{
    while (true)
    {
        var result = consumer.Consume(cts.Token);
        Console.WriteLine($"Received: {result.Message.Value}");
    }
}
catch (OperationCanceledException)
{
    consumer.Close();
}
```

### Manual Commit

```csharp
var config = new ConsumerConfig
{
    BootstrapServers = "localhost:9092",
    GroupId = "my-group",
    EnableAutoCommit = false,
    AutoOffsetReset = AutoOffsetReset.Earliest
};

using var consumer = new ConsumerBuilder<string, string>(config).Build();
consumer.Subscribe("events");

while (true)
{
    var result = consumer.Consume(TimeSpan.FromMilliseconds(100));

    if (result == null) continue;

    // Process message
    ProcessMessage(result.Message);

    // Commit offset
    consumer.Commit(result);
}
```

### Batch Processing

```csharp
var batch = new List<ConsumeResult<string, string>>();

while (true)
{
    var result = consumer.Consume(TimeSpan.FromMilliseconds(100));

    if (result != null)
    {
        batch.Add(result);
    }

    if (batch.Count >= 100 || (batch.Count > 0 && result == null))
    {
        ProcessBatch(batch);
        consumer.Commit(batch.Last());
        batch.Clear();
    }
}
```

---

## Admin Client

### Create Topic

```csharp
using Confluent.Kafka.Admin;

var config = new AdminClientConfig
{
    BootstrapServers = "localhost:9092"
};

using var adminClient = new AdminClientBuilder(config).Build();

await adminClient.CreateTopicsAsync(new[]
{
    new TopicSpecification
    {
        Name = "my-topic",
        NumPartitions = 3,
        ReplicationFactor = 3
    }
});
```

### List Topics

```csharp
var metadata = adminClient.GetMetadata(TimeSpan.FromSeconds(10));

foreach (var topic in metadata.Topics)
{
    Console.WriteLine($"Topic: {topic.Topic}, Partitions: {topic.Partitions.Count}");
}
```

---

## Configuration Reference

### Producer

| Property | Description | Default |
|----------|-------------|:-------:|
| `Acks` | Acknowledgments | Leader |
| `MessageSendMaxRetries` | Retry count | 2147483647 |
| `BatchSize` | Batch bytes | 16384 |
| `LingerMs` | Batch delay | 5 |
| `EnableIdempotence` | Idempotent | false |
| `CompressionType` | Compression | None |

### Consumer

| Property | Description | Default |
|----------|-------------|:-------:|
| `GroupId` | Consumer group | Required |
| `AutoOffsetReset` | Reset behavior | Latest |
| `EnableAutoCommit` | Auto commit | true |
| `SessionTimeoutMs` | Session timeout | 45000 |
| `MaxPollIntervalMs` | Max poll interval | 300000 |

---

## Serialization

### JSON Serialization

```csharp
using System.Text.Json;

public class JsonSerializer<T> : ISerializer<T>
{
    public byte[] Serialize(T data, SerializationContext context)
    {
        return JsonSerializer.SerializeToUtf8Bytes(data);
    }
}

public class JsonDeserializer<T> : IDeserializer<T>
{
    public T Deserialize(ReadOnlySpan<byte> data, bool isNull, SerializationContext context)
    {
        return JsonSerializer.Deserialize<T>(data);
    }
}

// Usage
var producer = new ProducerBuilder<string, MyEvent>(config)
    .SetValueSerializer(new JsonSerializer<MyEvent>())
    .Build();
```

### Avro Serialization

```csharp
using Confluent.SchemaRegistry;
using Confluent.SchemaRegistry.Serdes;

var schemaRegistryConfig = new SchemaRegistryConfig
{
    Url = "http://localhost:8081"
};

var schemaRegistry = new CachedSchemaRegistryClient(schemaRegistryConfig);

var producer = new ProducerBuilder<string, MyEvent>(config)
    .SetValueSerializer(new AvroSerializer<MyEvent>(schemaRegistry))
    .Build();
```

---

## Error Handling

```csharp
var producer = new ProducerBuilder<string, string>(config)
    .SetErrorHandler((_, error) =>
    {
        if (error.IsFatal)
        {
            Console.WriteLine($"Fatal error: {error.Reason}");
            // Shut down
        }
        else
        {
            Console.WriteLine($"Error: {error.Reason}");
        }
    })
    .Build();

try
{
    var result = await producer.ProduceAsync("events",
        new Message<string, string> { Value = "message" });
}
catch (ProduceException<string, string> ex)
{
    Console.WriteLine($"Produce failed: {ex.Error.Reason}");

    if (ex.Error.Code == ErrorCode.Local_MsgTimedOut)
    {
        // Retry logic
    }
}
```

---

## Graceful Shutdown

```csharp
var cts = new CancellationTokenSource();

Console.CancelKeyPress += (_, e) =>
{
    e.Cancel = true;
    cts.Cancel();
};

AppDomain.CurrentDomain.ProcessExit += (_, _) =>
{
    cts.Cancel();
};

using var consumer = new ConsumerBuilder<string, string>(config).Build();
consumer.Subscribe("events");

try
{
    while (!cts.Token.IsCancellationRequested)
    {
        var result = consumer.Consume(cts.Token);
        ProcessMessage(result.Message);
    }
}
catch (OperationCanceledException)
{
    // Expected during shutdown
}
finally
{
    consumer.Close();
}
```

---

## Dependency Injection

```csharp
// Program.cs
builder.Services.AddSingleton<IProducer<string, string>>(sp =>
{
    var config = new ProducerConfig
    {
        BootstrapServers = "localhost:9092"
    };
    return new ProducerBuilder<string, string>(config).Build();
});

// Service
public class EventService
{
    private readonly IProducer<string, string> _producer;

    public EventService(IProducer<string, string> producer)
    {
        _producer = producer;
    }

    public async Task PublishAsync(string key, string value)
    {
        await _producer.ProduceAsync("events",
            new Message<string, string> { Key = key, Value = value });
    }
}
```

---

## Related Documentation

- [Drivers Overview](index.md) - All client drivers
- [Producer Guide](../../producers/index.md) - Producer patterns
- [Consumer Guide](../../consumers/index.md) - Consumer patterns
- [Schema Registry](../../schema-registry/index.md) - Schema management
