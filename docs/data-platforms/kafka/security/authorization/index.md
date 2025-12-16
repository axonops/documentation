---
title: "Kafka Authorization"
description: "Apache Kafka authorization with ACLs. Configuring access control lists for topics, consumer groups, and cluster operations."
meta:
  - name: keywords
    content: "Kafka authorization, Kafka ACLs, access control, Kafka permissions"
---

# Kafka Authorization

Access Control Lists (ACLs) control which principals can perform which operations on which resources.

---

## ACL Concepts

### ACL Components

| Component | Description | Examples |
|-----------|-------------|----------|
| **Principal** | Identity performing action | `User:alice`, `User:CN=client.example.com` |
| **Permission** | Allow or Deny | `ALLOW`, `DENY` |
| **Operation** | Action to perform | `Read`, `Write`, `Create`, `Delete` |
| **Resource** | Kafka resource | `Topic:orders`, `Group:processors` |
| **Host** | Source IP | `*`, `192.168.1.100` |

### Resource Types

| Resource | Description | Operations |
|----------|-------------|------------|
| **Topic** | Kafka topic | Read, Write, Create, Delete, Describe, Alter |
| **Group** | Consumer group | Read, Describe, Delete |
| **Cluster** | Cluster-wide | Create, Alter, Describe, ClusterAction |
| **TransactionalId** | Transaction ID | Write, Describe |
| **DelegationToken** | Delegation tokens | Describe |

### Operations

| Operation | Description |
|-----------|-------------|
| `Read` | Consume from topic, read consumer group offsets |
| `Write` | Produce to topic |
| `Create` | Create topics |
| `Delete` | Delete topics, delete consumer groups |
| `Describe` | View topic/group metadata |
| `Alter` | Modify topic/broker configuration |
| `AlterConfigs` | Modify configurations |
| `DescribeConfigs` | View configurations |
| `ClusterAction` | Inter-broker communication |
| `IdempotentWrite` | Idempotent producer writes |
| `All` | All operations |

---

## Enabling Authorization

### Broker Configuration

```properties
# server.properties

# Enable ACL authorizer
authorizer.class.name=org.apache.kafka.metadata.authorizer.StandardAuthorizer

# Super users (bypass ACLs)
super.users=User:admin;User:kafka-broker

# Default behavior when no ACL matches
# false = deny (recommended for production)
# true = allow (for testing/migration)
allow.everyone.if.no.acl.found=false

# Principal builder for extracting identity
principal.builder.class=org.apache.kafka.common.security.authenticator.DefaultKafkaPrincipalBuilder
```

---

## Managing ACLs

### Create ACLs

```bash
# Producer access to topic
kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:producer-app \
  --operation Write \
  --operation Describe \
  --topic orders

# Consumer access to topic and group
kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:consumer-app \
  --operation Read \
  --operation Describe \
  --topic orders \
  --group order-processors

# Idempotent producer
kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:producer-app \
  --operation IdempotentWrite \
  --cluster

# Transactional producer
kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:producer-app \
  --operation Write \
  --transactional-id my-txn-id

kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:producer-app \
  --operation Describe \
  --transactional-id my-txn-id
```

### List ACLs

```bash
# All ACLs
kafka-acls.sh --bootstrap-server kafka:9092 --list

# For specific topic
kafka-acls.sh --bootstrap-server kafka:9092 \
  --list --topic orders

# For specific principal
kafka-acls.sh --bootstrap-server kafka:9092 \
  --list --principal User:producer-app
```

### Remove ACLs

```bash
kafka-acls.sh --bootstrap-server kafka:9092 \
  --remove \
  --allow-principal User:producer-app \
  --operation Write \
  --topic orders
```

---

## Common ACL Patterns

### Producer Application

```bash
# Basic producer
kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:my-producer \
  --operation Write \
  --operation Describe \
  --topic my-topic

# Idempotent producer (recommended)
kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:my-producer \
  --operation Write \
  --operation Describe \
  --topic my-topic

kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:my-producer \
  --operation IdempotentWrite \
  --cluster
```

### Consumer Application

```bash
kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:my-consumer \
  --operation Read \
  --operation Describe \
  --topic my-topic

kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:my-consumer \
  --operation Read \
  --group my-consumer-group
```

### Kafka Connect

```bash
# Connect worker
kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:kafka-connect \
  --operation Read \
  --operation Write \
  --operation Create \
  --topic connect-configs

kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:kafka-connect \
  --operation Read \
  --operation Write \
  --operation Create \
  --topic connect-offsets

kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:kafka-connect \
  --operation Read \
  --operation Write \
  --operation Create \
  --topic connect-status

kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:kafka-connect \
  --operation Read \
  --group connect-cluster

# Connector data topics
kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:kafka-connect \
  --operation Read \
  --operation Write \
  --operation Describe \
  --topic 'connector-*' \
  --resource-pattern-type prefixed
```

### Kafka Streams

```bash
# Internal topics
kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:streams-app \
  --operation All \
  --topic 'streams-app-*' \
  --resource-pattern-type prefixed

# Input/output topics
kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:streams-app \
  --operation Read \
  --topic input-topic

kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:streams-app \
  --operation Write \
  --topic output-topic

# Consumer group
kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:streams-app \
  --operation Read \
  --group streams-app
```

### Admin Operations

```bash
# Full admin access
kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:admin \
  --operation All \
  --cluster

kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:admin \
  --operation All \
  --topic '*'

kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:admin \
  --operation All \
  --group '*'
```

---

## Wildcard and Prefix Patterns

### Literal (Default)

```bash
# Exact match
kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:app \
  --operation Read \
  --topic orders \
  --resource-pattern-type literal
```

### Prefixed

```bash
# Match topics starting with "events-"
kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:app \
  --operation Read \
  --topic events- \
  --resource-pattern-type prefixed
```

### Wildcard

```bash
# All topics
kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:admin \
  --operation All \
  --topic '*'
```

---

## Deny Rules

Deny rules take precedence over allow rules.

```bash
# Allow all topics except sensitive
kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:app \
  --operation Read \
  --topic '*'

kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --deny-principal User:app \
  --operation Read \
  --topic sensitive-data
```

---

## Troubleshooting

### Enable Authorization Logging

```properties
# log4j.properties
log4j.logger.kafka.authorizer.logger=DEBUG
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `TopicAuthorizationException` | No Read/Write ACL | Add topic ACL |
| `GroupAuthorizationException` | No group Read ACL | Add group ACL |
| `ClusterAuthorizationException` | No cluster ACL | Add cluster ACL |
| `TransactionalIdAuthorizationException` | No txn ID ACL | Add transactional-id ACL |

---

## Related Documentation

- [Security Overview](../index.md) - Security concepts
- [Authentication](../authentication/index.md) - Authentication setup
- [Encryption](../encryption/index.md) - TLS configuration
