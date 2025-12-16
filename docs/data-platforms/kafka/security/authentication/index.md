---
title: "Kafka Authentication"
description: "Apache Kafka authentication configuration. SASL/SCRAM, SASL/PLAIN, mTLS, and OAuth authentication mechanisms."
meta:
  - name: keywords
    content: "Kafka authentication, SASL, SCRAM, mTLS, Kafka security"
---

# Kafka Authentication

Authentication mechanisms for verifying client and broker identities in Apache Kafka.

---

## Authentication Mechanisms

| Mechanism | Description | Use Case |
|-----------|-------------|----------|
| **SASL/PLAIN** | Username/password | Development, simple setups |
| **SASL/SCRAM** | Salted challenge-response | Production without Kerberos |
| **SASL/GSSAPI** | Kerberos | Enterprise with KDC |
| **SASL/OAUTHBEARER** | OAuth 2.0 tokens | Cloud-native environments |
| **mTLS** | Mutual TLS certificates | Certificate-based auth |

---

## SASL/SCRAM

SCRAM (Salted Challenge Response Authentication Mechanism) provides secure password-based authentication.

### Broker Configuration

```properties
# server.properties

# Listeners
listeners=SASL_SSL://0.0.0.0:9093
advertised.listeners=SASL_SSL://kafka1:9093

# Inter-broker communication
security.inter.broker.protocol=SASL_SSL
sasl.mechanism.inter.broker.protocol=SCRAM-SHA-512

# Enabled mechanisms
sasl.enabled.mechanisms=SCRAM-SHA-512

# JAAS configuration
listener.name.sasl_ssl.scram-sha-512.sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required \
  username="kafka-broker" \
  password="broker-password";

# TLS (required for SASL_SSL)
ssl.keystore.location=/etc/kafka/ssl/kafka.keystore.jks
ssl.keystore.password=keystore-password
ssl.key.password=key-password
ssl.truststore.location=/etc/kafka/ssl/kafka.truststore.jks
ssl.truststore.password=truststore-password
```

### Create SCRAM Credentials

```bash
# Create broker user
kafka-configs.sh --bootstrap-server kafka:9092 \
  --alter \
  --add-config 'SCRAM-SHA-512=[password=broker-password]' \
  --entity-type users \
  --entity-name kafka-broker

# Create application user
kafka-configs.sh --bootstrap-server kafka:9092 \
  --alter \
  --add-config 'SCRAM-SHA-512=[password=app-password]' \
  --entity-type users \
  --entity-name my-application

# List users
kafka-configs.sh --bootstrap-server kafka:9092 \
  --describe \
  --entity-type users
```

### Client Configuration

```properties
# client.properties
security.protocol=SASL_SSL
sasl.mechanism=SCRAM-SHA-512
sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required \
  username="my-application" \
  password="app-password";

ssl.truststore.location=/etc/kafka/ssl/client.truststore.jks
ssl.truststore.password=truststore-password
```

### Java Client

```java
Properties props = new Properties();
props.put("bootstrap.servers", "kafka:9093");
props.put("security.protocol", "SASL_SSL");
props.put("sasl.mechanism", "SCRAM-SHA-512");
props.put("sasl.jaas.config",
    "org.apache.kafka.common.security.scram.ScramLoginModule required " +
    "username=\"my-application\" " +
    "password=\"app-password\";");
props.put("ssl.truststore.location", "/path/to/truststore.jks");
props.put("ssl.truststore.password", "truststore-password");
```

---

## SASL/PLAIN

Simple username/password authentication. Should only be used with TLS encryption.

### Broker Configuration

```properties
# server.properties
listeners=SASL_SSL://0.0.0.0:9093
sasl.enabled.mechanisms=PLAIN

# JAAS configuration with users
listener.name.sasl_ssl.plain.sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required \
  username="admin" \
  password="admin-password" \
  user_admin="admin-password" \
  user_producer="producer-password" \
  user_consumer="consumer-password";
```

### Client Configuration

```properties
security.protocol=SASL_SSL
sasl.mechanism=PLAIN
sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required \
  username="producer" \
  password="producer-password";
```

!!! warning "Security Note"
    SASL/PLAIN transmits credentials in plain text. Always use with TLS (SASL_SSL).

---

## mTLS (Mutual TLS)

Certificate-based authentication where both client and server present certificates.

### Broker Configuration

```properties
# server.properties
listeners=SSL://0.0.0.0:9093
advertised.listeners=SSL://kafka1:9093

security.inter.broker.protocol=SSL

# Keystore (broker identity)
ssl.keystore.location=/etc/kafka/ssl/kafka.keystore.jks
ssl.keystore.password=keystore-password
ssl.key.password=key-password

# Truststore (trusted CAs)
ssl.truststore.location=/etc/kafka/ssl/kafka.truststore.jks
ssl.truststore.password=truststore-password

# Require client certificates
ssl.client.auth=required

# Principal mapping
ssl.principal.mapping.rules=RULE:^CN=([^,]+),.*$/$1/
```

### Client Configuration

```properties
security.protocol=SSL

# Client keystore (client identity)
ssl.keystore.location=/etc/kafka/ssl/client.keystore.jks
ssl.keystore.password=keystore-password
ssl.key.password=key-password

# Truststore (trusted CAs)
ssl.truststore.location=/etc/kafka/ssl/client.truststore.jks
ssl.truststore.password=truststore-password
```

### Certificate Generation

```bash
# Generate CA
openssl req -new -x509 -keyout ca-key -out ca-cert -days 365 \
  -subj "/CN=Kafka-CA" -nodes

# Generate broker keystore
keytool -keystore kafka.keystore.jks -alias kafka-broker \
  -validity 365 -genkey -keyalg RSA -storepass changeit \
  -dname "CN=kafka1.example.com"

# Create CSR
keytool -keystore kafka.keystore.jks -alias kafka-broker \
  -certreq -file kafka-broker.csr -storepass changeit

# Sign certificate
openssl x509 -req -CA ca-cert -CAkey ca-key \
  -in kafka-broker.csr -out kafka-broker-signed.crt \
  -days 365 -CAcreateserial

# Import CA cert
keytool -keystore kafka.keystore.jks -alias CARoot \
  -import -file ca-cert -storepass changeit -noprompt

# Import signed cert
keytool -keystore kafka.keystore.jks -alias kafka-broker \
  -import -file kafka-broker-signed.crt -storepass changeit

# Create truststore with CA
keytool -keystore kafka.truststore.jks -alias CARoot \
  -import -file ca-cert -storepass changeit -noprompt
```

---

## SASL/OAUTHBEARER

OAuth 2.0 token-based authentication for modern identity systems.

### Broker Configuration

```properties
# server.properties
listeners=SASL_SSL://0.0.0.0:9093
sasl.enabled.mechanisms=OAUTHBEARER

# Custom callback handler for token validation
listener.name.sasl_ssl.oauthbearer.sasl.server.callback.handler.class=\
  com.example.OAuthBearerValidatorCallbackHandler

# OIDC settings
listener.name.sasl_ssl.oauthbearer.sasl.oauthbearer.jwks.endpoint.url=\
  https://identity-provider/.well-known/jwks.json
listener.name.sasl_ssl.oauthbearer.sasl.oauthbearer.expected.audience=kafka
```

### Client Configuration

```properties
security.protocol=SASL_SSL
sasl.mechanism=OAUTHBEARER
sasl.login.callback.handler.class=\
  org.apache.kafka.common.security.oauthbearer.secured.OAuthBearerLoginCallbackHandler
sasl.oauthbearer.token.endpoint.url=https://identity-provider/oauth2/token
sasl.jaas.config=org.apache.kafka.common.security.oauthbearer.OAuthBearerLoginModule required \
  clientId="kafka-client" \
  clientSecret="client-secret";
```

---

## Multiple Listeners

Configure different authentication per listener.

```properties
# Different auth for internal vs external
listeners=INTERNAL://0.0.0.0:9092,EXTERNAL://0.0.0.0:9093
listener.security.protocol.map=INTERNAL:SASL_PLAINTEXT,EXTERNAL:SASL_SSL

# Internal uses PLAIN
listener.name.internal.sasl.enabled.mechanisms=PLAIN
listener.name.internal.plain.sasl.jaas.config=...

# External uses SCRAM
listener.name.external.sasl.enabled.mechanisms=SCRAM-SHA-512
listener.name.external.scram-sha-512.sasl.jaas.config=...

inter.broker.listener.name=INTERNAL
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Authentication failed | Invalid credentials | Verify username/password |
| SSL handshake failed | Certificate mismatch | Check truststore contains CA |
| SCRAM user not found | User not created | Run kafka-configs to create user |
| Principal mapping failed | Invalid mapping rule | Check ssl.principal.mapping.rules |

---

## Related Documentation

- [Security Overview](../index.md) - Security concepts
- [Authorization](../authorization/index.md) - ACL configuration
- [Encryption](../encryption/index.md) - TLS setup
