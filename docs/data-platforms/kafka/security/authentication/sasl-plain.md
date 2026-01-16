---
title: "Kafka SASL/PLAIN Authentication"
description: "SASL/PLAIN authentication in Apache Kafka. Configuration guide for development and testing environments with security considerations."
meta:
  - name: keywords
    content: "Kafka PLAIN, SASL PLAIN, Kafka authentication, Kafka security, username password"
---

# SASL/PLAIN Authentication

SASL/PLAIN provides simple username/password authentication for Kafka. While easy to configure, it transmits credentials in base64 encoding (not encrypted) and should only be used over TLS connections.

---

## Overview

### When to Use PLAIN

| Use Case | Recommendation |
|----------|----------------|
| Development environments | Acceptable |
| Testing/QA | Acceptable |
| Production without SCRAM support | Use with TLS only |
| Quick prototyping | Acceptable |
| Production (general) | **Prefer SCRAM** |

### PLAIN vs SCRAM

| Feature | PLAIN | SCRAM |
|---------|-------|-------|
| Password transmission | Base64 encoded | Never transmitted |
| Broker storage | Plaintext in config | Salted hash |
| Replay attack protection | None (relies on TLS) | Built-in nonces |
| Mutual authentication | No | Yes |
| Complexity | Simple | Moderate |

!!! danger "Security Warning"
    SASL/PLAIN transmits credentials in base64 encoding. Without TLS, credentials can be captured by network sniffers. **Always use SASL_SSL, never SASL_PLAINTEXT in production.**

### Version Requirements

| Feature | Kafka Version |
|---------|---------------|
| SASL/PLAIN | 0.9.0+ |
| Per-listener JAAS config | 1.0.0+ |
| Custom callbacks | 0.10.0+ |

---

## Broker Configuration

### Basic Setup

```properties
# server.properties

# Listener configuration
listeners=SASL_SSL://0.0.0.0:9093
advertised.listeners=SASL_SSL://kafka1.example.com:9093

# Security protocol for inter-broker communication
security.inter.broker.protocol=SASL_SSL
sasl.mechanism.inter.broker.protocol=PLAIN

# Enable PLAIN mechanism
sasl.enabled.mechanisms=PLAIN

# JAAS configuration with users
listener.name.sasl_ssl.plain.sasl.jaas.config=\
  org.apache.kafka.common.security.plain.PlainLoginModule required \
  username="kafka-broker" \
  password="broker-password" \
  user_kafka-broker="broker-password" \
  user_admin="admin-password" \
  user_producer="producer-password" \
  user_consumer="consumer-password";
```

### JAAS Configuration Format

The PLAIN module requires user definitions in the format `user_<username>="<password>"`:

```properties
listener.name.sasl_ssl.plain.sasl.jaas.config=\
  org.apache.kafka.common.security.plain.PlainLoginModule required \
  username="broker-user" \
  password="broker-password" \
  user_broker-user="broker-password" \
  user_alice="alice-secret" \
  user_bob="bob-secret" \
  user_service-account="service-password";
```

| Property | Purpose |
|----------|---------|
| `username` | Username for inter-broker authentication |
| `password` | Password for inter-broker authentication |
| `user_<name>` | Defines a valid user and password |

### TLS Configuration (Required)

```properties
# SSL/TLS settings
ssl.keystore.type=PKCS12
ssl.keystore.location=/etc/kafka/ssl/kafka.keystore.p12
ssl.keystore.password=${KEYSTORE_PASSWORD}
ssl.key.password=${KEY_PASSWORD}

ssl.truststore.type=PKCS12
ssl.truststore.location=/etc/kafka/ssl/kafka.truststore.p12
ssl.truststore.password=${TRUSTSTORE_PASSWORD}

# Require TLS 1.2 or higher
ssl.enabled.protocols=TLSv1.3,TLSv1.2
ssl.endpoint.identification.algorithm=HTTPS
```

### Static JAAS File (Alternative)

Instead of inline configuration, use a separate JAAS file:

**kafka_server_jaas.conf:**

```
KafkaServer {
    org.apache.kafka.common.security.plain.PlainLoginModule required
    username="kafka-broker"
    password="broker-password"
    user_kafka-broker="broker-password"
    user_alice="alice-secret"
    user_bob="bob-secret";
};
```

**JVM parameter:**

```bash
-Djava.security.auth.login.config=/etc/kafka/kafka_server_jaas.conf
```

---

## User Management

### Adding Users

PLAIN stores users in broker configuration. Adding users requires updating JAAS config and restarting brokers:

1. **Update JAAS configuration** with new `user_<name>` entries
2. **Rolling restart** all brokers
3. **Verify** client can authenticate

```properties
# Before: 2 users
listener.name.sasl_ssl.plain.sasl.jaas.config=\
  org.apache.kafka.common.security.plain.PlainLoginModule required \
  username="kafka-broker" \
  password="broker-password" \
  user_kafka-broker="broker-password" \
  user_alice="alice-secret";

# After: 3 users
listener.name.sasl_ssl.plain.sasl.jaas.config=\
  org.apache.kafka.common.security.plain.PlainLoginModule required \
  username="kafka-broker" \
  password="broker-password" \
  user_kafka-broker="broker-password" \
  user_alice="alice-secret" \
  user_newuser="newuser-secret";
```

### Removing Users

Remove the `user_<name>` entry and perform rolling restart:

```properties
# Remove user_alice entry
listener.name.sasl_ssl.plain.sasl.jaas.config=\
  org.apache.kafka.common.security.plain.PlainLoginModule required \
  username="kafka-broker" \
  password="broker-password" \
  user_kafka-broker="broker-password" \
  user_newuser="newuser-secret";
```

!!! warning "User Management Limitations"
    PLAIN requires broker restarts for user changes. For dynamic user management, use [SASL/SCRAM](sasl-scram.md) instead.

### Password Changes

1. Update password in JAAS configuration
2. Rolling restart brokers
3. Update client configuration
4. Restart clients

---

## Client Configuration

### Java Client

```java
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import java.util.Properties;

Properties props = new Properties();
props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka1:9093,kafka2:9093");
props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class);

// Security configuration
props.put("security.protocol", "SASL_SSL");
props.put("sasl.mechanism", "PLAIN");
props.put("sasl.jaas.config",
    "org.apache.kafka.common.security.plain.PlainLoginModule required " +
    "username=\"alice\" " +
    "password=\"alice-secret\";");

// TLS configuration
props.put("ssl.truststore.location", "/etc/kafka/ssl/client.truststore.p12");
props.put("ssl.truststore.password", "truststore-password");
props.put("ssl.truststore.type", "PKCS12");

KafkaProducer<String, String> producer = new KafkaProducer<>(props);
```

### Spring Boot

**application.yml:**

```yaml
spring:
  kafka:
    bootstrap-servers: kafka1:9093,kafka2:9093
    properties:
      security.protocol: SASL_SSL
      sasl.mechanism: PLAIN
      sasl.jaas.config: >
        org.apache.kafka.common.security.plain.PlainLoginModule required
        username="${KAFKA_USERNAME}"
        password="${KAFKA_PASSWORD}";
    ssl:
      trust-store-location: classpath:truststore.p12
      trust-store-password: ${TRUSTSTORE_PASSWORD}
      trust-store-type: PKCS12
```

### Python (confluent-kafka)

```python
from confluent_kafka import Producer

config = {
    'bootstrap.servers': 'kafka1:9093,kafka2:9093',
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': 'alice',
    'sasl.password': 'alice-secret',
    'ssl.ca.location': '/etc/kafka/ssl/ca-cert.pem',
}

producer = Producer(config)
```

### Go (confluent-kafka-go)

```go
import (
    "github.com/confluentinc/confluent-kafka-go/v2/kafka"
)

producer, err := kafka.NewProducer(&kafka.ConfigMap{
    "bootstrap.servers":  "kafka1:9093,kafka2:9093",
    "security.protocol":  "SASL_SSL",
    "sasl.mechanism":     "PLAIN",
    "sasl.username":      "alice",
    "sasl.password":      "alice-secret",
    "ssl.ca.location":    "/etc/kafka/ssl/ca-cert.pem",
})
```

### Command-Line Tools

**client.properties:**

```properties
security.protocol=SASL_SSL
sasl.mechanism=PLAIN
sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required \
  username="alice" \
  password="alice-secret";
ssl.truststore.location=/etc/kafka/ssl/client.truststore.p12
ssl.truststore.password=truststore-password
```

```bash
# Produce messages
kafka-console-producer.sh --bootstrap-server kafka:9093 \
  --topic my-topic \
  --producer.config client.properties

# Consume messages
kafka-console-consumer.sh --bootstrap-server kafka:9093 \
  --topic my-topic \
  --consumer.config client.properties \
  --from-beginning
```

---

## Custom Authentication Callback

For external user stores (LDAP, database), implement a custom callback handler:

### Callback Interface

```java
import org.apache.kafka.common.security.auth.AuthenticateCallbackHandler;
import javax.security.auth.callback.*;
import javax.security.sasl.AuthorizeCallback;

public class CustomPlainAuthCallback implements AuthenticateCallbackHandler {

    @Override
    public void configure(Map<String, ?> configs, String saslMechanism,
                          List<AppConfigurationEntry> jaasConfigEntries) {
        // Initialize connection to external user store
    }

    @Override
    public void handle(Callback[] callbacks) throws UnsupportedCallbackException {
        String username = null;
        String password = null;

        for (Callback callback : callbacks) {
            if (callback instanceof NameCallback) {
                username = ((NameCallback) callback).getDefaultName();
            } else if (callback instanceof PlainAuthenticateCallback) {
                PlainAuthenticateCallback plainCallback = (PlainAuthenticateCallback) callback;
                password = new String(plainCallback.password());
                boolean authenticated = validateCredentials(username, password);
                plainCallback.authenticated(authenticated);
            } else {
                throw new UnsupportedCallbackException(callback);
            }
        }
    }

    private boolean validateCredentials(String username, String password) {
        // Query external system (LDAP, database, etc.)
        return externalAuthService.authenticate(username, password);
    }

    @Override
    public void close() {
        // Cleanup resources
    }
}
```

### Broker Configuration for Custom Callback

```properties
# Register custom callback handler
listener.name.sasl_ssl.plain.sasl.server.callback.handler.class=\
  com.example.CustomPlainAuthCallback

# JAAS config (username/password for inter-broker only)
listener.name.sasl_ssl.plain.sasl.jaas.config=\
  org.apache.kafka.common.security.plain.PlainLoginModule required \
  username="kafka-broker" \
  password="broker-password";
```

---

## Security Considerations

### Risks of PLAIN Authentication

| Risk | Mitigation |
|------|------------|
| Credential exposure | Always use TLS (SASL_SSL) |
| Replay attacks | TLS provides session protection |
| Brute force | Implement rate limiting, monitoring |
| Credential in memory | Use short-lived credentials where possible |
| Credentials in config files | Restrict file permissions, use secrets management |

### Minimum Security Requirements

1. **Always use SASL_SSL** - Never SASL_PLAINTEXT
2. **TLS 1.2 or higher** - Disable older protocols
3. **Strong passwords** - Minimum 16 characters
4. **File permissions** - Restrict access to JAAS config files
5. **Network segmentation** - Limit broker exposure

### File Permission Hardening

```bash
# Restrict JAAS config file access
chmod 600 /etc/kafka/kafka_server_jaas.conf
chown kafka:kafka /etc/kafka/kafka_server_jaas.conf

# Restrict server.properties
chmod 600 /etc/kafka/server.properties
chown kafka:kafka /etc/kafka/server.properties
```

---

## Troubleshooting

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Authentication failed` | Wrong username/password | Verify credentials in JAAS config |
| `No JAAS configuration` | Missing JAAS config | Add `sasl.jaas.config` property |
| `Unknown user` | User not defined | Add `user_<name>` entry |
| `PLAIN not supported` | Mechanism not enabled | Add to `sasl.enabled.mechanisms` |

### Debug Logging

**Broker:**

```properties
# log4j.properties
log4j.logger.org.apache.kafka.common.security=DEBUG
log4j.logger.org.apache.kafka.common.security.plain=TRACE
```

**Client:**

```properties
log4j.logger.org.apache.kafka.clients=DEBUG
log4j.logger.org.apache.kafka.common.security=DEBUG
```

### Verify Authentication

```bash
# Test connection
kafka-broker-api-versions.sh --bootstrap-server kafka:9093 \
  --command-config client.properties

# Check broker logs for authentication attempts
grep -i "authentication\|plain\|sasl" /var/log/kafka/server.log | tail -50
```

---

## Migration to SCRAM

SCRAM provides stronger security than PLAIN. Migration steps:

1. **Create SCRAM credentials** for all users:

```bash
kafka-configs.sh --bootstrap-server kafka:9093 \
  --command-config admin.properties \
  --alter \
  --add-config 'SCRAM-SHA-512=[password=alice-secret]' \
  --entity-type users \
  --entity-name alice
```

2. **Enable both mechanisms**:

```properties
sasl.enabled.mechanisms=PLAIN,SCRAM-SHA-512
```

3. **Rolling restart** brokers

4. **Update clients** to use SCRAM:

```properties
sasl.mechanism=SCRAM-SHA-512
sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required \
  username="alice" \
  password="alice-secret";
```

5. **After migration, disable PLAIN**:

```properties
sasl.enabled.mechanisms=SCRAM-SHA-512
```

See [SASL/SCRAM Guide](sasl-scram.md) for detailed SCRAM configuration.

---

## Related Documentation

- [Authentication Overview](index.md) - Mechanism comparison
- [SASL/SCRAM](sasl-scram.md) - Secure password authentication
- [mTLS Authentication](mtls.md) - Certificate-based authentication
- [Authorization](../authorization/index.md) - ACL configuration
- [Encryption](../encryption/index.md) - TLS setup
