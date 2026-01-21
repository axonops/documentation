---
title: "Kafka Streams Error Handling"
description: "Kafka Streams error handling patterns. Deserialization errors, production exceptions, uncaught exceptions, and recovery strategies."
meta:
  - name: keywords
    content: "Kafka Streams error handling, deserialization exception, production exception, dead letter queue, stream recovery"
search:
  boost: 3
---

# Error Handling

Kafka Streams applications must handle various error types gracefully. This guide covers exception handling strategies, dead letter queues, and recovery patterns.

---

## Error Types

| Error Type | Location | Cause |
|------------|----------|-------|
| **Deserialization** | Input | Invalid message format |
| **Processing** | Topology | Application logic failure |
| **Production** | Output | Broker unavailable, serialization error |
| **Uncaught** | Anywhere | Unhandled exception |

---

## Deserialization Errors

### Default Behavior

By default, deserialization errors cause the stream to fail:

```java
// Throws exception on bad message
KStream<String, Order> orders = builder.stream("orders");
// If any message fails to deserialize, stream thread dies
```

### LogAndContinue Handler

Skip bad records and continue processing:

```java
props.put(
    StreamsConfig.DEFAULT_DESERIALIZATION_EXCEPTION_HANDLER_CLASS_CONFIG,
    LogAndContinueExceptionHandler.class
);
```

### LogAndFail Handler (Default)

Fail the stream on deserialization error:

```java
props.put(
    StreamsConfig.DEFAULT_DESERIALIZATION_EXCEPTION_HANDLER_CLASS_CONFIG,
    LogAndFailExceptionHandler.class
);
```

### Custom Handler

Implement custom logic for deserialization errors:

```java
public class CustomDeserializationHandler implements DeserializationExceptionHandler {
    private final Producer<byte[], byte[]> dlqProducer;

    @Override
    public DeserializationHandlerResponse handle(ProcessorContext context,
                                                  ConsumerRecord<byte[], byte[]> record,
                                                  Exception exception) {
        // Log the error
        log.error("Deserialization failed for record at offset {} in {}-{}",
            record.offset(), record.topic(), record.partition(), exception);

        // Send to dead letter queue
        ProducerRecord<byte[], byte[]> dlqRecord = new ProducerRecord<>(
            record.topic() + ".dlq",
            record.key(),
            record.value()
        );
        dlqRecord.headers()
            .add("error.message", exception.getMessage().getBytes())
            .add("error.offset", Long.toString(record.offset()).getBytes());

        dlqProducer.send(dlqRecord);

        // Continue processing
        return DeserializationHandlerResponse.CONTINUE;
    }

    @Override
    public void configure(Map<String, ?> configs) {
        // Initialize DLQ producer
        dlqProducer = new KafkaProducer<>(configs);
    }
}
```

---

## Production Errors

### Default Handler

```java
props.put(
    StreamsConfig.DEFAULT_PRODUCTION_EXCEPTION_HANDLER_CLASS_CONFIG,
    DefaultProductionExceptionHandler.class  // Fails on error
);
```

### Custom Production Handler

```java
public class CustomProductionHandler implements ProductionExceptionHandler {

    @Override
    public ProductionExceptionHandlerResponse handle(ProducerRecord<byte[], byte[]> record,
                                                     Exception exception) {
        if (exception instanceof RecordTooLargeException) {
            // Skip oversized records
            log.warn("Record too large, skipping: {}", record.key());
            return ProductionExceptionHandlerResponse.CONTINUE;
        }

        if (isRetriable(exception)) {
            // Retry transient errors
            log.warn("Retriable production error, will retry: {}", exception.getMessage());
            return ProductionExceptionHandlerResponse.CONTINUE;
        }

        // Fail on non-retriable errors
        log.error("Non-retriable production error: {}", exception.getMessage());
        return ProductionExceptionHandlerResponse.FAIL;
    }

    private boolean isRetriable(Exception e) {
        return e instanceof TimeoutException ||
               e instanceof NotLeaderOrFollowerException;
    }
}
```

---

## Processing Errors

### Try-Catch in Processors

```java
stream.mapValues(value -> {
    try {
        return processValue(value);
    } catch (ProcessingException e) {
        log.error("Processing failed: {}", e.getMessage());
        return null;  // Or return error marker
    }
})
.filter((key, value) -> value != null);  // Filter out failures
```

### Branch Pattern for Error Handling

```java
// Split stream into success and failure branches
Map<String, KStream<String, ProcessingResult>> branches = stream
    .mapValues(value -> {
        try {
            return ProcessingResult.success(process(value));
        } catch (Exception e) {
            return ProcessingResult.failure(value, e);
        }
    })
    .split(Named.as("processing-"))
    .branch((key, result) -> result.isSuccess(), Branched.as("success"))
    .branch((key, result) -> !result.isSuccess(), Branched.as("failure"))
    .noDefaultBranch();

// Process successful records
branches.get("processing-success")
    .mapValues(ProcessingResult::getValue)
    .to("output");

// Send failures to DLQ
branches.get("processing-failure")
    .mapValues(ProcessingResult::toErrorRecord)
    .to("errors");
```

### Dead Letter Queue Pattern

```java
public class DlqProcessor implements Processor<String, Event, String, Event> {
    private ProcessorContext<String, Event> context;
    private final String dlqTopic;

    @Override
    public void process(Record<String, Event> record) {
        try {
            Event processed = processEvent(record.value());
            context.forward(record.withValue(processed));
        } catch (Exception e) {
            // Send to DLQ
            sendToDlq(record, e);
        }
    }

    private void sendToDlq(Record<String, Event> record, Exception e) {
        Record<String, Event> dlqRecord = record.withHeaders(
            record.headers()
                .add("error.message", e.getMessage().getBytes())
                .add("error.timestamp", Long.toString(System.currentTimeMillis()).getBytes())
                .add("error.class", e.getClass().getName().getBytes())
        );

        // Forward to DLQ sink
        context.forward(dlqRecord, "dlq-sink");
    }
}
```

---

## Uncaught Exception Handler

Handle any exception that escapes the topology:

```java
streams.setUncaughtExceptionHandler(exception -> {
    log.error("Uncaught exception in stream thread", exception);

    // Analyze exception type
    if (exception instanceof RetriableException) {
        // Replace the thread and continue
        return StreamsUncaughtExceptionHandler.StreamThreadExceptionResponse.REPLACE_THREAD;
    }

    if (exception instanceof FatalException) {
        // Shutdown the entire application
        return StreamsUncaughtExceptionHandler.StreamThreadExceptionResponse.SHUTDOWN_APPLICATION;
    }

    // Default: shutdown just this client
    return StreamsUncaughtExceptionHandler.StreamThreadExceptionResponse.SHUTDOWN_CLIENT;
});
```

### Exception Response Options

| Response | Behavior |
|----------|----------|
| `REPLACE_THREAD` | Replace failed thread, continue processing |
| `SHUTDOWN_CLIENT` | Shutdown this Streams instance |
| `SHUTDOWN_APPLICATION` | Shutdown all instances via protocol |

---

## State Restoration Errors

```java
// Handle state restoration failures
streams.setStateRestoreListener(new StateRestoreListener() {
    @Override
    public void onRestoreStart(TopicPartition partition, String storeName,
                               long startOffset, long endOffset) {
        log.info("Starting restoration of {} from {} to {}",
            storeName, startOffset, endOffset);
    }

    @Override
    public void onBatchRestored(TopicPartition partition, String storeName,
                                long batchEndOffset, long numRestored) {
        // Track progress
    }

    @Override
    public void onRestoreEnd(TopicPartition partition, String storeName, long totalRestored) {
        log.info("Completed restoration of {}: {} records", storeName, totalRestored);
    }
});
```

---

## Retry Patterns

### Simple Retry with Backoff

```java
public class RetryingProcessor implements Processor<String, Event, String, Event> {
    private static final int MAX_RETRIES = 3;
    private static final long INITIAL_BACKOFF_MS = 100;

    @Override
    public void process(Record<String, Event> record) {
        int attempt = 0;
        long backoff = INITIAL_BACKOFF_MS;

        while (attempt < MAX_RETRIES) {
            try {
                Event result = processEvent(record.value());
                context.forward(record.withValue(result));
                return;
            } catch (RetriableException e) {
                attempt++;
                if (attempt < MAX_RETRIES) {
                    log.warn("Attempt {} failed, retrying in {}ms", attempt, backoff);
                    sleep(backoff);
                    backoff *= 2;
                }
            }
        }

        // Max retries exceeded
        sendToDlq(record, new MaxRetriesExceededException());
    }
}
```

### External Service Circuit Breaker

```java
public class CircuitBreakerProcessor implements Processor<String, Event, String, Event> {
    private final CircuitBreaker circuitBreaker;
    private ProcessorContext<String, Event> context;

    @Override
    public void process(Record<String, Event> record) {
        try {
            Event result = circuitBreaker.executeSupplier(() -> callExternalService(record.value()));
            context.forward(record.withValue(result));
        } catch (CallNotPermittedException e) {
            // Circuit is open - send to retry topic
            context.forward(record, "retry-sink");
        } catch (Exception e) {
            // Other failures - send to DLQ
            sendToDlq(record, e);
        }
    }
}
```

---

## Error Monitoring

### Metrics

Key metrics to monitor:

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `skipped-records-rate` | Records skipped due to errors | > 0.1% |
| `failed-stream-threads` | Stream threads that failed | > 0 |
| `rebalance-rate` | Rebalance frequency | > 1/hour |
| `process-latency` | Processing time | > SLA |

### Custom Error Metrics

```java
public class MetricsProcessor implements Processor<String, Event, String, Event> {
    private final Counter successCounter;
    private final Counter errorCounter;
    private final Counter dlqCounter;

    @Override
    public void init(ProcessorContext<String, Event> context) {
        this.context = context;

        // Register metrics
        StreamsMetrics metrics = context.metrics();
        successCounter = metrics.addSensor("processing-success");
        errorCounter = metrics.addSensor("processing-error");
        dlqCounter = metrics.addSensor("dlq-sent");
    }

    @Override
    public void process(Record<String, Event> record) {
        try {
            Event result = processEvent(record.value());
            context.forward(record.withValue(result));
            successCounter.increment();
        } catch (Exception e) {
            errorCounter.increment();
            sendToDlq(record, e);
            dlqCounter.increment();
        }
    }
}
```

---

## Recovery Patterns

### Graceful Shutdown

```java
Runtime.getRuntime().addShutdownHook(new Thread(() -> {
    log.info("Shutting down streams application");
    streams.close(Duration.ofSeconds(30));
}));
```

### State Recovery

```java
// Configure for faster recovery
props.put(StreamsConfig.NUM_STANDBY_REPLICAS_CONFIG, 1);

// Monitor state
streams.setStateListener((newState, oldState) -> {
    log.info("State changed from {} to {}", oldState, newState);

    if (newState == KafkaStreams.State.ERROR) {
        // Alert and potentially restart
        alertOps("Streams application entered ERROR state");
    }
});
```

---

## Best Practices

### Error Handling Strategy

| Practice | Recommendation |
|----------|----------------|
| Define error types | Classify retriable vs fatal |
| Use DLQ | Never lose data |
| Log context | Include offset, key, error details |
| Monitor errors | Alert on error rate thresholds |

### Configuration

| Practice | Recommendation |
|----------|----------------|
| Set appropriate handlers | Custom handlers for production |
| Configure retries | `retries`, `retry.backoff.ms` |
| Enable standby replicas | Faster recovery |
| Set processing guarantees | Match business requirements |

### Testing

| Practice | Recommendation |
|----------|----------------|
| Test error paths | Inject failures in tests |
| Verify DLQ flow | Ensure errors reach DLQ |
| Test recovery | Verify state restoration |
| Load test errors | Ensure error handling scales |

---

## Related Documentation

- [Kafka Streams Overview](index.md) - Stream processing concepts
- [DSL Reference](dsl/index.md) - Stream operations
- [State Stores](state-stores.md) - State management
- [Consumer Error Handling](../consumers/error-handling.md) - Consumer patterns
