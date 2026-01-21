---
title: "Kafka Streams DSL"
description: "Kafka Streams DSL reference. KStream, KTable operations, joins, aggregations, and windowing."
meta:
  - name: keywords
    content: "Kafka Streams DSL, KStream, KTable, stream operations, Kafka aggregations"
search:
  boost: 3
---

# Kafka Streams DSL

Complete reference for Kafka Streams Domain Specific Language operations.

---

## Stream Operations

### Creating Streams

```java
StreamsBuilder builder = new StreamsBuilder();

// From topic
KStream<String, String> stream = builder.stream("topic");

// With specific serdes
KStream<String, Event> events = builder.stream(
    "events",
    Consumed.with(Serdes.String(), eventSerde)
);

// From multiple topics
KStream<String, String> merged = builder.stream(
    Arrays.asList("topic1", "topic2", "topic3")
);

// With pattern
KStream<String, String> pattern = builder.stream(
    Pattern.compile("events-.*")
);
```

### Transformations

| Operation | Input | Output | Description |
|-----------|-------|--------|-------------|
| `map` | (K, V) | (K', V') | Transform key and value |
| `mapValues` | V | V' | Transform value only |
| `flatMap` | (K, V) | Iterable<(K', V')> | One-to-many |
| `flatMapValues` | V | Iterable<V'> | One-to-many values |
| `filter` | (K, V) | boolean | Keep matching |
| `filterNot` | (K, V) | boolean | Keep non-matching |
| `selectKey` | (K, V) | K' | Change key |

```java
// map - transform key and value
KStream<String, Integer> mapped = stream.map(
    (key, value) -> KeyValue.pair(key.toUpperCase(), value.length())
);

// mapValues - transform value only (more efficient)
KStream<String, Integer> lengths = stream.mapValues(String::length);

// flatMap - one-to-many
KStream<String, String> words = stream.flatMap(
    (key, value) -> Arrays.stream(value.split(" "))
        .map(word -> KeyValue.pair(key, word))
        .collect(Collectors.toList())
);

// filter
KStream<String, String> filtered = stream.filter(
    (key, value) -> value != null && value.length() > 0
);

// selectKey - change the key
KStream<String, Order> rekeyed = orders.selectKey(
    (key, order) -> order.getCustomerId()
);
```

### Branching

Split a stream into multiple streams based on predicates.

```java
Map<String, KStream<String, Event>> branches = events.split(Named.as("branch-"))
    .branch((key, event) -> event.getType().equals("click"),
        Branched.as("clicks"))
    .branch((key, event) -> event.getType().equals("view"),
        Branched.as("views"))
    .defaultBranch(Branched.as("other"));

KStream<String, Event> clicks = branches.get("branch-clicks");
KStream<String, Event> views = branches.get("branch-views");
KStream<String, Event> other = branches.get("branch-other");
```

### Merging

Combine multiple streams.

```java
KStream<String, String> merged = stream1
    .merge(stream2)
    .merge(stream3);
```

---

## Table Operations

### Creating Tables

```java
// From topic (changelog semantics)
KTable<String, String> table = builder.table("topic");

// With materialized state store
KTable<String, User> users = builder.table(
    "users",
    Materialized.<String, User, KeyValueStore<Bytes, byte[]>>as("users-store")
        .withKeySerde(Serdes.String())
        .withValueSerde(userSerde)
);

// GlobalKTable (fully replicated)
GlobalKTable<String, Config> config = builder.globalTable("config");
```

### Table Transformations

```java
// mapValues
KTable<String, Integer> ages = users.mapValues(User::getAge);

// filter
KTable<String, User> activeUsers = users.filter(
    (key, user) -> user.isActive()
);

// Convert to stream
KStream<String, User> userStream = users.toStream();
```

---

## Grouping

### KStream Grouping

```java
// Group by existing key
KGroupedStream<String, Event> grouped = events.groupByKey();

// Group by new key
KGroupedStream<String, Event> groupedByType = events.groupBy(
    (key, event) -> event.getType(),
    Grouped.with(Serdes.String(), eventSerde)
);
```

### KTable Grouping

```java
// Group by existing key
KGroupedTable<String, User> grouped = users.groupBy(
    (key, user) -> KeyValue.pair(key, user),
    Grouped.with(Serdes.String(), userSerde)
);
```

---

## Aggregations

### Count

```java
KTable<String, Long> counts = grouped.count();

// With materialized store
KTable<String, Long> counts = grouped.count(
    Materialized.<String, Long, KeyValueStore<Bytes, byte[]>>as("counts-store")
);
```

### Reduce

```java
KTable<String, Long> maxValues = grouped.reduce(
    (value1, value2) -> Math.max(value1, value2)
);
```

### Aggregate

```java
KTable<String, Aggregate> aggregated = grouped.aggregate(
    // Initializer
    () -> new Aggregate(0, 0.0),
    // Aggregator
    (key, value, aggregate) -> aggregate.add(value),
    // Materialized
    Materialized.with(Serdes.String(), aggregateSerde)
);
```

---

## Windowed Aggregations

### Tumbling Windows

```java
KTable<Windowed<String>, Long> hourlyCount = events
    .groupByKey()
    .windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofHours(1)))
    .count();
```

### Hopping Windows

```java
KTable<Windowed<String>, Long> slidingCount = events
    .groupByKey()
    .windowedBy(
        TimeWindows.ofSizeAndGrace(Duration.ofMinutes(5), Duration.ofMinutes(1))
            .advanceBy(Duration.ofMinutes(1))
    )
    .count();
```

### Session Windows

```java
KTable<Windowed<String>, Long> sessionCount = events
    .groupByKey()
    .windowedBy(SessionWindows.ofInactivityGapWithNoGrace(Duration.ofMinutes(30)))
    .count();
```

### Suppress

Control when windowed results are emitted.

```java
KTable<Windowed<String>, Long> finalCounts = events
    .groupByKey()
    .windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofMinutes(1)))
    .count()
    .suppress(Suppressed.untilWindowCloses(BufferConfig.unbounded()));
```

---

## Joins

### KStream-KStream Join

```java
KStream<String, EnrichedClick> enriched = clicks.join(
    impressions,
    (click, impression) -> new EnrichedClick(click, impression),
    JoinWindows.ofTimeDifferenceWithNoGrace(Duration.ofMinutes(5)),
    StreamJoined.with(Serdes.String(), clickSerde, impressionSerde)
);
```

### KStream-KTable Join

```java
KStream<String, EnrichedOrder> enriched = orders.join(
    customers,
    (order, customer) -> new EnrichedOrder(order, customer)
);

// Left join (order always emitted)
KStream<String, EnrichedOrder> enriched = orders.leftJoin(
    customers,
    (order, customer) -> new EnrichedOrder(order, customer)
);
```

### KStream-GlobalKTable Join

```java
KStream<String, EnrichedOrder> enriched = orders.join(
    products,
    (orderId, order) -> order.getProductId(),  // Key mapper
    (order, product) -> new EnrichedOrder(order, product)
);
```

### KTable-KTable Join

```java
KTable<String, UserProfile> profiles = users.join(
    preferences,
    (user, pref) -> new UserProfile(user, pref)
);
```

---

## Output Operations

### To Topic

```java
// To single topic
stream.to("output-topic");

// With specific serdes
stream.to("output-topic", Produced.with(Serdes.String(), eventSerde));

// Dynamic topic selection
stream.to(
    (key, value, recordContext) -> "output-" + value.getType(),
    Produced.with(Serdes.String(), eventSerde)
);
```

### Through (Repartition)

```java
// Repartition through intermediate topic
KStream<String, Event> repartitioned = events.through("repartition-topic");
```

### Peek (Side Effects)

```java
stream.peek((key, value) -> logger.info("Processing: {}", key));
```

### Print (Debug)

```java
stream.print(Printed.toSysOut());
stream.print(Printed.<String, Event>toSysOut().withLabel("events"));
```

---

## Processor API

For advanced use cases requiring full control.

```java
stream.process(
    () -> new Processor<String, Event, String, ProcessedEvent>() {
        private ProcessorContext<String, ProcessedEvent> context;
        private KeyValueStore<String, Long> store;

        @Override
        public void init(ProcessorContext<String, ProcessedEvent> context) {
            this.context = context;
            this.store = context.getStateStore("my-store");
        }

        @Override
        public void process(Record<String, Event> record) {
            // Custom processing logic
            Long count = store.get(record.key());
            count = (count == null) ? 1L : count + 1;
            store.put(record.key(), count);

            context.forward(new Record<>(
                record.key(),
                new ProcessedEvent(record.value(), count),
                record.timestamp()
            ));
        }
    },
    Named.as("custom-processor"),
    "my-store"
);
```

---

## Related Documentation

- [Kafka Streams Overview](../index.md) - Concepts and architecture
- [Delivery Semantics](../../../concepts/delivery-semantics/index.md) - Processing guarantees
- [Architecture Patterns](../../../concepts/architecture-patterns/index.md) - Design patterns
