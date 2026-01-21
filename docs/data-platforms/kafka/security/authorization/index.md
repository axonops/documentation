---
title: "Kafka Authorization"
description: "Apache Kafka authorization with ACLs. Configuring access control lists for topics, consumer groups, and cluster operations."
meta:
  - name: keywords
    content: "Kafka authorization, Kafka ACLs, access control, Kafka permissions"
search:
  boost: 3
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

AxonOps provides a dashboard interface for configuring authorization settings across all brokers without manual configuration file editing.

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

AxonOps provides a visual interface for managing ACLs without command-line operations. ACL changes are tracked in audit logs with the user who made the change, timestamp, and before/after state.

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

AxonOps correlates authorization errors with the specific ACLs in place, simplifying troubleshooting by showing which ACL rule caused the denial and what ACL would be needed to allow the operation.

---

## Principal Mapping

### SSL Principal Mapping

By default, SSL user names follow the full DN format:

```
CN=writeuser,OU=Unknown,O=Unknown,L=Unknown,ST=Unknown,C=Unknown
```

Configure `ssl.principal.mapping.rules` to extract short names:

```properties
# server.properties
ssl.principal.mapping.rules=\
  RULE:^CN=(.*?),OU=ServiceUsers.*$/$1/, \
  RULE:^CN=(.*?),OU=(.*?),O=(.*?),L=(.*?),ST=(.*?),C=(.*?)$/$1@$2/L, \
  DEFAULT
```

**Rule syntax:**

| Format | Description |
|--------|-------------|
| `RULE:pattern/replacement/` | Basic replacement |
| `RULE:pattern/replacement/L` | Lowercase result |
| `RULE:pattern/replacement/U` | Uppercase result |
| `DEFAULT` | Use full DN |

**Examples:**

| Input DN | Rule | Result |
|----------|------|--------|
| `CN=serviceuser,OU=ServiceUsers,O=Corp` | `RULE:^CN=(.*?),OU=ServiceUsers.*$/$1/` | `serviceuser` |
| `CN=AdminUser,OU=Admin,O=Corp` | `RULE:^CN=(.*?),OU=(.*?).*$/$1@$2/L` | `adminuser@admin` |

### SASL Kerberos Principal Mapping

Configure `sasl.kerberos.principal.to.local.rules` for Kerberos principals:

```properties
# server.properties
sasl.kerberos.principal.to.local.rules=\
  RULE:[1:$1@$0](.*@MYDOMAIN.COM)s/@.*//,\
  DEFAULT
```

**Rule syntax:**

| Format | Description |
|--------|-------------|
| `RULE:[n:string](regexp)s/pattern/replacement/` | Standard replacement |
| `RULE:[n:string](regexp)s/pattern/replacement/g` | Global replacement |
| `RULE:[n:string](regexp)s/pattern/replacement//L` | Lowercase result |
| `RULE:[n:string](regexp)s/pattern/replacement//U` | Uppercase result |

---

## Protocol ACL Requirements

Each Kafka protocol request requires specific ACL permissions:

### Produce and Consume

| Protocol | Operation | Resource | Notes |
|----------|-----------|----------|-------|
| PRODUCE | Write | Topic | Normal produce |
| PRODUCE | IdempotentWrite | Cluster | Idempotent producer |
| PRODUCE | Write | TransactionalId | Transactional producer |
| FETCH | Read | Topic | Consumer fetch |
| FETCH | ClusterAction | Cluster | Follower replication |

### Consumer Group Operations

| Protocol | Operation | Resource | Notes |
|----------|-----------|----------|-------|
| JOIN_GROUP | Read | Group | Join consumer group |
| SYNC_GROUP | Read | Group | Synchronize assignments |
| HEARTBEAT | Read | Group | Maintain membership |
| LEAVE_GROUP | Read | Group | Leave group |
| OFFSET_COMMIT | Read | Group, Topic | Commit offsets |
| OFFSET_FETCH | Describe | Group, Topic | Fetch committed offsets |
| FIND_COORDINATOR | Describe | Group | Find group coordinator |

### Topic Operations

| Protocol | Operation | Resource | Notes |
|----------|-----------|----------|-------|
| METADATA | Describe | Topic | Get topic metadata |
| METADATA | Create | Cluster or Topic | Auto-create topics |
| LIST_OFFSETS | Describe | Topic | Get partition offsets |
| CREATE_TOPICS | Create | Cluster | Create topics |
| DELETE_TOPICS | Delete | Topic | Delete topics |
| ALTER_CONFIGS | AlterConfigs | Topic | Modify topic config |
| DESCRIBE_CONFIGS | DescribeConfigs | Topic | Read topic config |

### Transaction Operations

| Protocol | Operation | Resource | Notes |
|----------|-----------|----------|-------|
| FIND_COORDINATOR | Describe | TransactionalId | Find txn coordinator |
| INIT_PRODUCER_ID | Write | TransactionalId | Initialize producer |
| ADD_PARTITIONS_TO_TXN | Write | TransactionalId, Topic | Add partitions |
| ADD_OFFSETS_TO_TXN | Write | TransactionalId, Group | Add offsets |
| END_TXN | Write | TransactionalId | Commit/abort txn |
| TXN_OFFSET_COMMIT | Read | Group, Topic | Commit txn offsets |
| WRITE_TXN_MARKERS | ClusterAction | Cluster | Inter-broker |

### Admin Operations

| Protocol | Operation | Resource | Notes |
|----------|-----------|----------|-------|
| CREATE_PARTITIONS | Alter | Topic | Add partitions |
| DELETE_RECORDS | Delete | Topic | Delete records |
| ELECT_LEADERS | ClusterAction | Cluster | Leader election |
| DESCRIBE_LOG_DIRS | Describe | Cluster | Log directory info |
| ALTER_REPLICA_LOG_DIRS | Alter | Cluster | Move replicas |
| CREATE_ACLS | Alter | Cluster | Manage ACLs |
| DESCRIBE_ACLS | Describe | Cluster | List ACLs |
| DELETE_ACLS | Alter | Cluster | Remove ACLs |

---

## KRaft Principal Forwarding

In KRaft mode, admin requests flow through brokers to controllers:

1. Client sends request to broker
2. Broker wraps request in `Envelope` with client principal
3. Controller authorizes broker (Envelope request)
4. Controller authorizes original request using forwarded principal

For custom principals to work with KRaft, the principal builder must implement `KafkaPrincipalSerde`:

```properties
# server.properties
principal.builder.class=com.example.CustomPrincipalBuilder
```

---

## AxonOps ACL Management

Managing Kafka ACLs through command-line tools becomes increasingly complex as clusters grow and teams expand. AxonOps provides enterprise-grade ACL management:

### Visual ACL Management

- **Topic ACL browser**: View and manage ACLs per topic with point-and-click interface
- **Principal view**: See all permissions granted to a specific user or service account
- **Bulk operations**: Apply ACL templates across multiple topics or consumer groups
- **ACL validation**: Preview ACL changes before applying to prevent misconfigurations

### Enterprise Security Controls

- **Role-based permissions**: Control which AxonOps users can view, create, or modify ACLs
- **Approval workflows**: Require approval for ACL changes in production environments
- **Segregation of duties**: Separate ACL management from other Kafka operations

### Audit Logging

- **Complete audit trail**: Every ACL change is logged with user, timestamp, and change details
- **Before/after state**: Full record of ACL state before and after each modification
- **Compliance reporting**: Export audit logs for security reviews and compliance requirements
- **Integration**: Forward audit events to SIEM systems

### API Access

- **REST API**: Programmatic ACL management for automation and CI/CD pipelines
- **Terraform provider**: Infrastructure-as-code support for ACL definitions
- **Idempotent operations**: Safe to re-apply ACL configurations

See **[AxonOps Kafka Security](../../../../kafka/acl/overview.md)** for configuration details.

---

## Related Documentation

- [Security Overview](../index.md) - Security concepts
- [Authentication](../authentication/index.md) - Authentication setup
- [Encryption](../encryption/index.md) - TLS configuration
