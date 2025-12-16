---
title: "Kafka ACL Configuration"
description: "Apache Kafka Access Control List (ACL) configuration. Authorization, resource types, operations, and ACL management."
meta:
  - name: keywords
    content: "Kafka ACL, access control list, authorization, Kafka permissions, security rules"
---

# ACL Configuration

Access Control Lists (ACLs) control authorization in Kafka. ACLs define which principals can perform which operations on which resources.

---

## Enabling Authorization

### Broker Configuration

```properties
# server.properties

# Enable authorizer (KRaft mode)
authorizer.class.name=org.apache.kafka.metadata.authorizer.StandardAuthorizer

# Super users (bypass ACL checks)
super.users=User:admin;User:kafka

# Default behavior when no ACL matches
allow.everyone.if.no.acl.found=false
```

| Setting | Default | Description |
|---------|---------|-------------|
| `authorizer.class.name` | (none) | Authorizer implementation |
| `super.users` | (none) | Principals that bypass ACL checks |
| `allow.everyone.if.no.acl.found` | false | Allow access when no ACL exists |

### Authorizer Classes

| Mode | Authorizer Class |
|------|------------------|
| KRaft | `org.apache.kafka.metadata.authorizer.StandardAuthorizer` |
| ZooKeeper | `kafka.security.authorizer.AclAuthorizer` |

!!! warning "allow.everyone.if.no.acl.found"
    Setting this to `true` creates an open cluster where any authenticated user can access resources without explicit ACLs. In production, this should be `false`.

---

## ACL Components

### Resource Types

| Resource | Description | Example |
|----------|-------------|---------|
| `TOPIC` | Kafka topic | `orders`, `events.*` |
| `GROUP` | Consumer group | `my-consumer-group` |
| `CLUSTER` | Cluster operations | Cluster-wide actions |
| `TRANSACTIONAL_ID` | Transactional producer | `my-transactional-id` |
| `DELEGATION_TOKEN` | Delegation tokens | Token operations |
| `USER` | User quotas and SCRAM | User management |

### Operations

| Operation | Applicable Resources | Description |
|-----------|---------------------|-------------|
| `READ` | Topic, Group | Consume messages, fetch offsets |
| `WRITE` | Topic | Produce messages |
| `CREATE` | Topic, Cluster | Create topics |
| `DELETE` | Topic, Group | Delete topics, consumer groups |
| `ALTER` | Topic, Cluster | Modify configuration |
| `DESCRIBE` | Topic, Group, Cluster | View metadata |
| `CLUSTER_ACTION` | Cluster | Inter-broker operations |
| `DESCRIBE_CONFIGS` | Topic, Cluster | View configuration |
| `ALTER_CONFIGS` | Topic, Cluster | Modify configuration |
| `IDEMPOTENT_WRITE` | Cluster | Idempotent producer |
| `ALL` | All | All operations |

### Permission Types

| Permission | Description |
|------------|-------------|
| `ALLOW` | Explicitly permit the operation |
| `DENY` | Explicitly forbid the operation |

!!! note "DENY Precedence"
    DENY rules take precedence over ALLOW rules. If both exist for the same principal/resource/operation, access is denied.

---

## Managing ACLs

### Adding ACLs

```bash
# Allow producer to write to topic
kafka-acls.sh --bootstrap-server kafka:9092 \
  --command-config admin.properties \
  --add \
  --allow-principal User:producer-app \
  --operation Write \
  --operation Describe \
  --topic orders

# Allow consumer to read from topic and commit offsets
kafka-acls.sh --bootstrap-server kafka:9092 \
  --command-config admin.properties \
  --add \
  --allow-principal User:consumer-app \
  --operation Read \
  --operation Describe \
  --topic orders \
  --group order-consumers
```

### Removing ACLs

```bash
# Remove specific ACL
kafka-acls.sh --bootstrap-server kafka:9092 \
  --command-config admin.properties \
  --remove \
  --allow-principal User:producer-app \
  --operation Write \
  --topic orders

# Remove all ACLs for a topic
kafka-acls.sh --bootstrap-server kafka:9092 \
  --command-config admin.properties \
  --remove \
  --topic orders
```

### Listing ACLs

```bash
# List all ACLs
kafka-acls.sh --bootstrap-server kafka:9092 \
  --command-config admin.properties \
  --list

# List ACLs for specific topic
kafka-acls.sh --bootstrap-server kafka:9092 \
  --command-config admin.properties \
  --list \
  --topic orders

# List ACLs for specific principal
kafka-acls.sh --bootstrap-server kafka:9092 \
  --command-config admin.properties \
  --list \
  --principal User:producer-app
```

---

## Common ACL Patterns

### Producer Application

```bash
# Minimum permissions for producer
kafka-acls.sh --bootstrap-server kafka:9092 \
  --command-config admin.properties \
  --add \
  --allow-principal User:my-producer \
  --operation Write \
  --operation Describe \
  --topic my-topic
```

### Idempotent Producer

```bash
# Idempotent producer requires cluster-level permission
kafka-acls.sh --bootstrap-server kafka:9092 \
  --command-config admin.properties \
  --add \
  --allow-principal User:my-producer \
  --operation IdempotentWrite \
  --cluster

kafka-acls.sh --bootstrap-server kafka:9092 \
  --command-config admin.properties \
  --add \
  --allow-principal User:my-producer \
  --operation Write \
  --operation Describe \
  --topic my-topic
```

### Transactional Producer

```bash
# Transactional producer permissions
kafka-acls.sh --bootstrap-server kafka:9092 \
  --command-config admin.properties \
  --add \
  --allow-principal User:my-producer \
  --operation Write \
  --operation Describe \
  --transactional-id my-tx-id

kafka-acls.sh --bootstrap-server kafka:9092 \
  --command-config admin.properties \
  --add \
  --allow-principal User:my-producer \
  --operation Write \
  --operation Describe \
  --topic my-topic
```

### Consumer Application

```bash
# Consumer with consumer group
kafka-acls.sh --bootstrap-server kafka:9092 \
  --command-config admin.properties \
  --add \
  --allow-principal User:my-consumer \
  --operation Read \
  --operation Describe \
  --topic my-topic

kafka-acls.sh --bootstrap-server kafka:9092 \
  --command-config admin.properties \
  --add \
  --allow-principal User:my-consumer \
  --operation Read \
  --operation Describe \
  --group my-consumer-group
```

### Kafka Streams Application

```bash
# Kafka Streams requires internal topic permissions
kafka-acls.sh --bootstrap-server kafka:9092 \
  --command-config admin.properties \
  --add \
  --allow-principal User:streams-app \
  --operation Read \
  --operation Write \
  --operation Create \
  --operation Describe \
  --topic input-topic

kafka-acls.sh --bootstrap-server kafka:9092 \
  --command-config admin.properties \
  --add \
  --allow-principal User:streams-app \
  --operation All \
  --topic 'streams-app-*' \
  --resource-pattern-type prefixed

kafka-acls.sh --bootstrap-server kafka:9092 \
  --command-config admin.properties \
  --add \
  --allow-principal User:streams-app \
  --operation All \
  --group 'streams-app-*' \
  --resource-pattern-type prefixed
```

### Kafka Connect

```bash
# Connect worker permissions
kafka-acls.sh --bootstrap-server kafka:9092 \
  --command-config admin.properties \
  --add \
  --allow-principal User:connect-worker \
  --operation All \
  --topic connect-configs

kafka-acls.sh --bootstrap-server kafka:9092 \
  --command-config admin.properties \
  --add \
  --allow-principal User:connect-worker \
  --operation All \
  --topic connect-offsets

kafka-acls.sh --bootstrap-server kafka:9092 \
  --command-config admin.properties \
  --add \
  --allow-principal User:connect-worker \
  --operation All \
  --topic connect-status

kafka-acls.sh --bootstrap-server kafka:9092 \
  --command-config admin.properties \
  --add \
  --allow-principal User:connect-worker \
  --operation All \
  --group connect-cluster
```

---

## Wildcard and Prefix Patterns

### Resource Pattern Types

| Pattern Type | Syntax | Description |
|--------------|--------|-------------|
| `LITERAL` | `--topic orders` | Exact match (default) |
| `PREFIXED` | `--resource-pattern-type prefixed` | Prefix match |

### Prefix ACLs

```bash
# Allow access to all topics starting with "events-"
kafka-acls.sh --bootstrap-server kafka:9092 \
  --command-config admin.properties \
  --add \
  --allow-principal User:events-processor \
  --operation Read \
  --operation Write \
  --topic events- \
  --resource-pattern-type prefixed
```

### Wildcard Principal

```bash
# Allow all users to read from public topic
kafka-acls.sh --bootstrap-server kafka:9092 \
  --command-config admin.properties \
  --add \
  --allow-principal 'User:*' \
  --operation Read \
  --operation Describe \
  --topic public-events
```

---

## Deny Rules

DENY rules explicitly forbid access and take precedence over ALLOW rules.

```bash
# Deny specific user even if group allows
kafka-acls.sh --bootstrap-server kafka:9092 \
  --command-config admin.properties \
  --add \
  --deny-principal User:restricted-user \
  --operation All \
  --topic sensitive-data
```

### ACL Evaluation Order

1. If a DENY rule matches, access is denied
2. If an ALLOW rule matches, access is granted
3. If no rules match, check `allow.everyone.if.no.acl.found`
4. If false (default), access is denied

---

## Host-Based Restrictions

```bash
# Allow access only from specific hosts
kafka-acls.sh --bootstrap-server kafka:9092 \
  --command-config admin.properties \
  --add \
  --allow-principal User:my-app \
  --allow-host 10.0.0.100 \
  --allow-host 10.0.0.101 \
  --operation Read \
  --topic my-topic

# Deny access from specific hosts
kafka-acls.sh --bootstrap-server kafka:9092 \
  --command-config admin.properties \
  --add \
  --deny-principal 'User:*' \
  --deny-host 192.168.1.0 \
  --operation All \
  --cluster
```

---

## Operation Requirements

### Operations by Use Case

| Use Case | Required Operations | Resource |
|----------|---------------------|----------|
| Produce | Write, Describe | Topic |
| Consume | Read, Describe | Topic, Group |
| Idempotent produce | IdempotentWrite | Cluster |
| Transactional produce | Write, Describe | TransactionalId, Topic |
| Create topic | Create | Cluster or Topic |
| Delete topic | Delete, Describe | Topic |
| List topics | Describe | Topic |
| Alter topic config | AlterConfigs | Topic |
| View topic config | DescribeConfigs | Topic |
| List consumer groups | Describe | Group |
| Delete consumer group | Delete | Group |

### Minimum Producer Permissions

```bash
# Non-idempotent producer
kafka-acls.sh --add --allow-principal User:producer \
  --operation Write --operation Describe --topic my-topic

# Idempotent producer (recommended)
kafka-acls.sh --add --allow-principal User:producer \
  --operation IdempotentWrite --cluster
kafka-acls.sh --add --allow-principal User:producer \
  --operation Write --operation Describe --topic my-topic
```

### Minimum Consumer Permissions

```bash
kafka-acls.sh --add --allow-principal User:consumer \
  --operation Read --operation Describe --topic my-topic
kafka-acls.sh --add --allow-principal User:consumer \
  --operation Read --operation Describe --group my-group
```

---

## Admin Client Configuration

The `admin.properties` file for ACL management:

```properties
# admin.properties
bootstrap.servers=kafka:9092
security.protocol=SASL_SSL
sasl.mechanism=SCRAM-SHA-512
sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required \
  username="admin" \
  password="admin-secret";
ssl.truststore.location=/etc/kafka/ssl/truststore.jks
ssl.truststore.password=truststore-password
```

---

## Troubleshooting

### Authorization Failures

Check broker logs for authorization errors:

```bash
grep -i "authorization" /var/log/kafka/server.log
```

Example log entry:
```
Principal = User:my-app is Denied Operation = Write from host = 10.0.0.1
on resource = Topic:LITERAL:orders for request = Produce
```

### Listing Effective Permissions

```bash
# List all ACLs to understand effective permissions
kafka-acls.sh --bootstrap-server kafka:9092 \
  --command-config admin.properties \
  --list \
  --principal User:my-app
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Producer denied | Missing Write or Describe | Add both operations |
| Consumer denied | Missing Group permission | Add Read on consumer group |
| Idempotent denied | Missing cluster permission | Add IdempotentWrite on cluster |
| Transactional denied | Missing transactional-id permission | Add Write on transactional-id |

---

## Related Documentation

- [Configuration Overview](index.md) - Configuration guide
- [Security Overview](../../security/index.md) - Security architecture
- [Authentication](../../security/authentication/index.md) - SASL and SSL
- [Authorization](../../security/authorization/index.md) - Authorization concepts
