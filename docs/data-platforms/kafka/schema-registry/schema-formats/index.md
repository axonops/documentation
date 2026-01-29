---
title: "Schema Formats"
description: "Schema Registry serialization formats. Avro, Protobuf, and JSON Schema configuration and usage."
meta:
  - name: keywords
    content: "Schema Registry formats, Avro, Protobuf, JSON Schema, Kafka serialization"
---

# Schema Formats

Schema Registry supports multiple serialization formats for data contracts in Kafka topics.

---

## Format Comparison

| Feature | Avro | Protobuf | JSON Schema |
|---------|------|----------|-------------|
| **Binary encoding** | Yes | Yes | No |
| **Schema evolution** | Excellent | Good | Limited |
| **Human readable** | No | No | Yes |
| **Code generation** | Yes | Yes | Optional |
| **Default values** | Yes | Yes | Yes |
| **Backward compatibility** | Native | Native | Manual |
| **Size efficiency** | High | Highest | Low |

---

## Avro

Apache Avro provides compact binary serialization with strong schema evolution support.

### Schema Definition

```json
{
  "type": "record",
  "name": "User",
  "namespace": "com.example.events",
  "fields": [
    {
      "name": "id",
      "type": "string",
      "doc": "Unique user identifier"
    },
    {
      "name": "email",
      "type": "string"
    },
    {
      "name": "created_at",
      "type": {
        "type": "long",
        "logicalType": "timestamp-millis"
      }
    },
    {
      "name": "status",
      "type": {
        "type": "enum",
        "name": "UserStatus",
        "symbols": ["ACTIVE", "INACTIVE", "PENDING"]
      },
      "default": "PENDING"
    },
    {
      "name": "metadata",
      "type": ["null", {
        "type": "map",
        "values": "string"
      }],
      "default": null
    }
  ]
}
```

### Avro Types

| Type | Description | Example |
|------|-------------|---------|
| `null` | No value | `null` |
| `boolean` | True/false | `true` |
| `int` | 32-bit signed | `42` |
| `long` | 64-bit signed | `1234567890` |
| `float` | 32-bit IEEE 754 | `3.14` |
| `double` | 64-bit IEEE 754 | `3.14159265` |
| `bytes` | Byte sequence | Binary data |
| `string` | UTF-8 string | `"hello"` |
| `array` | Ordered collection | `[1, 2, 3]` |
| `map` | Key-value pairs | `{"key": "value"}` |
| `record` | Named fields | Complex type |
| `enum` | Enumeration | `"ACTIVE"` |
| `fixed` | Fixed-size bytes | UUID, hash |
| `union` | Type alternatives | `["null", "string"]` |

### Logical Types

```json
{
  "type": "record",
  "name": "Transaction",
  "fields": [
    {
      "name": "amount",
      "type": {
        "type": "bytes",
        "logicalType": "decimal",
        "precision": 10,
        "scale": 2
      }
    },
    {
      "name": "transaction_date",
      "type": {
        "type": "int",
        "logicalType": "date"
      }
    },
    {
      "name": "transaction_time",
      "type": {
        "type": "long",
        "logicalType": "timestamp-millis"
      }
    },
    {
      "name": "transaction_id",
      "type": {
        "type": "fixed",
        "name": "uuid",
        "size": 16,
        "logicalType": "uuid"
      }
    }
  ]
}
```

| Logical Type | Underlying Type | Description |
|--------------|-----------------|-------------|
| `decimal` | bytes/fixed | Arbitrary precision decimal |
| `date` | int | Days from Unix epoch |
| `time-millis` | int | Milliseconds from midnight |
| `time-micros` | long | Microseconds from midnight |
| `timestamp-millis` | long | Milliseconds from epoch |
| `timestamp-micros` | long | Microseconds from epoch |
| `uuid` | string/fixed | UUID string or 16 bytes |

### Java Producer with Avro

```java
Properties props = new Properties();
props.put("bootstrap.servers", "kafka:9092");
props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
props.put("value.serializer", "io.confluent.kafka.serializers.KafkaAvroSerializer");
props.put("schema.registry.url", "http://schema-registry:8081");

KafkaProducer<String, User> producer = new KafkaProducer<>(props);

User user = User.newBuilder()
    .setId("user-123")
    .setEmail("user@example.com")
    .setCreatedAt(System.currentTimeMillis())
    .setStatus(UserStatus.ACTIVE)
    .build();

producer.send(new ProducerRecord<>("users", user.getId(), user));
```

### Python Consumer with Avro

```python
from confluent_kafka import Consumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer

schema_registry_client = SchemaRegistryClient({'url': 'http://schema-registry:8081'})
avro_deserializer = AvroDeserializer(schema_registry_client)

consumer = Consumer({
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'my-consumer-group',
    'value.deserializer': avro_deserializer
})

consumer.subscribe(['users'])

while True:
    msg = consumer.poll(1.0)
    if msg is not None:
        user = msg.value()
        print(f"User: {user['id']}, Email: {user['email']}")
```

---

## Protobuf

Protocol Buffers provide efficient binary serialization with strong typing and code generation.

### Schema Definition

```protobuf
syntax = "proto3";

package com.example.events;

import "google/protobuf/timestamp.proto";

message User {
  string id = 1;
  string email = 2;
  google.protobuf.Timestamp created_at = 3;
  UserStatus status = 4;
  map<string, string> metadata = 5;

  enum UserStatus {
    USER_STATUS_UNSPECIFIED = 0;
    USER_STATUS_ACTIVE = 1;
    USER_STATUS_INACTIVE = 2;
    USER_STATUS_PENDING = 3;
  }
}

message UserEvent {
  string event_id = 1;
  EventType event_type = 2;
  User user = 3;
  google.protobuf.Timestamp event_time = 4;

  enum EventType {
    EVENT_TYPE_UNSPECIFIED = 0;
    EVENT_TYPE_CREATED = 1;
    EVENT_TYPE_UPDATED = 2;
    EVENT_TYPE_DELETED = 3;
  }
}
```

### Protobuf Types

| Type | Description | Default Value |
|------|-------------|---------------|
| `double` | 64-bit float | 0.0 |
| `float` | 32-bit float | 0.0 |
| `int32` | Variable-length signed | 0 |
| `int64` | Variable-length signed | 0 |
| `uint32` | Variable-length unsigned | 0 |
| `uint64` | Variable-length unsigned | 0 |
| `sint32` | ZigZag encoded signed | 0 |
| `sint64` | ZigZag encoded signed | 0 |
| `fixed32` | Fixed 4 bytes unsigned | 0 |
| `fixed64` | Fixed 8 bytes unsigned | 0 |
| `sfixed32` | Fixed 4 bytes signed | 0 |
| `sfixed64` | Fixed 8 bytes signed | 0 |
| `bool` | Boolean | false |
| `string` | UTF-8 string | "" |
| `bytes` | Byte sequence | empty |

### Java Producer with Protobuf

```java
Properties props = new Properties();
props.put("bootstrap.servers", "kafka:9092");
props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
props.put("value.serializer", "io.confluent.kafka.serializers.protobuf.KafkaProtobufSerializer");
props.put("schema.registry.url", "http://schema-registry:8081");

KafkaProducer<String, User> producer = new KafkaProducer<>(props);

User user = User.newBuilder()
    .setId("user-123")
    .setEmail("user@example.com")
    .setCreatedAt(Timestamps.fromMillis(System.currentTimeMillis()))
    .setStatus(UserStatus.USER_STATUS_ACTIVE)
    .build();

producer.send(new ProducerRecord<>("users", user.getId(), user));
```

---

## JSON Schema

JSON Schema provides human-readable validation with broad tooling support.

### Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "com.example.events.User",
  "type": "object",
  "title": "User",
  "required": ["id", "email"],
  "properties": {
    "id": {
      "type": "string",
      "description": "Unique user identifier"
    },
    "email": {
      "type": "string",
      "format": "email"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "status": {
      "type": "string",
      "enum": ["ACTIVE", "INACTIVE", "PENDING"],
      "default": "PENDING"
    },
    "age": {
      "type": "integer",
      "minimum": 0,
      "maximum": 150
    },
    "tags": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "metadata": {
      "type": "object",
      "additionalProperties": {
        "type": "string"
      }
    }
  }
}
```

### JSON Schema Types

| Type | Description | Validation Keywords |
|------|-------------|---------------------|
| `string` | Text | minLength, maxLength, pattern, format |
| `number` | Floating point | minimum, maximum, multipleOf |
| `integer` | Whole number | minimum, maximum, multipleOf |
| `boolean` | True/false | - |
| `object` | Key-value | properties, required, additionalProperties |
| `array` | Ordered list | items, minItems, maxItems, uniqueItems |
| `null` | No value | - |

### Format Validation

| Format | Description |
|--------|-------------|
| `date-time` | ISO 8601 date-time |
| `date` | ISO 8601 date |
| `time` | ISO 8601 time |
| `email` | Email address |
| `hostname` | Hostname |
| `ipv4` | IPv4 address |
| `ipv6` | IPv6 address |
| `uri` | URI |
| `uuid` | UUID |

### Java Producer with JSON Schema

```java
Properties props = new Properties();
props.put("bootstrap.servers", "kafka:9092");
props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
props.put("value.serializer", "io.confluent.kafka.serializers.json.KafkaJsonSchemaSerializer");
props.put("schema.registry.url", "http://schema-registry:8081");
props.put("json.fail.invalid.schema", "true");

KafkaProducer<String, User> producer = new KafkaProducer<>(props);

User user = new User();
user.setId("user-123");
user.setEmail("user@example.com");
user.setStatus("ACTIVE");

producer.send(new ProducerRecord<>("users", user.getId(), user));
```

---

## Schema Registry API

### Register Schema

```bash
# Register Avro schema
curl -X POST http://schema-registry:8081/subjects/users-value/versions \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{
    "schemaType": "AVRO",
    "schema": "{\"type\":\"record\",\"name\":\"User\",\"fields\":[{\"name\":\"id\",\"type\":\"string\"},{\"name\":\"email\",\"type\":\"string\"}]}"
  }'

# Register Protobuf schema
curl -X POST http://schema-registry:8081/subjects/users-value/versions \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{
    "schemaType": "PROTOBUF",
    "schema": "syntax = \"proto3\"; message User { string id = 1; string email = 2; }"
  }'

# Register JSON Schema
curl -X POST http://schema-registry:8081/subjects/users-value/versions \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{
    "schemaType": "JSON",
    "schema": "{\"type\":\"object\",\"properties\":{\"id\":{\"type\":\"string\"},\"email\":{\"type\":\"string\"}}}"
  }'
```

### Get Schema

```bash
# Get latest schema
curl http://schema-registry:8081/subjects/users-value/versions/latest

# Get specific version
curl http://schema-registry:8081/subjects/users-value/versions/1

# Get schema by ID
curl http://schema-registry:8081/schemas/ids/1
```

### List Subjects

```bash
curl http://schema-registry:8081/subjects
```

---

## Serializer Configuration

### Avro Serializer

| Property | Description | Default |
|----------|-------------|---------|
| `schema.registry.url` | Registry URL | Required |
| `auto.register.schemas` | Auto-register schemas | true |
| `use.latest.version` | Use latest schema version | false |
| `avro.use.logical.type.converters` | Use logical type converters | false |

### Protobuf Serializer

| Property | Description | Default |
|----------|-------------|---------|
| `schema.registry.url` | Registry URL | Required |
| `auto.register.schemas` | Auto-register schemas | true |
| `reference.subject.name.strategy` | Reference naming strategy | - |

### JSON Schema Serializer

| Property | Description | Default |
|----------|-------------|---------|
| `schema.registry.url` | Registry URL | Required |
| `auto.register.schemas` | Auto-register schemas | true |
| `json.fail.invalid.schema` | Fail on invalid schema | false |
| `json.oneof.for.nullables` | Use oneOf for nullable | false |

---

## Related Documentation

- [Schema Registry Overview](../index.md) - Architecture and concepts
- [Schema Compatibility](../compatibility/index.md) - Evolution rules
- [Kafka Connect](../../kafka-connect/index.md) - Connector integration