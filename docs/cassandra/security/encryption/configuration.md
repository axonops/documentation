---
description: "Configure TLS encryption in Cassandra. cassandra.yaml SSL settings for clients and internode."
meta:
  - name: keywords
    content: "TLS configuration, SSL settings, cassandra.yaml, encryption setup"
---

# Cassandra Encryption Configuration

This section covers the complete encryption configuration options in cassandra.yaml for both internode and client-to-node encryption.

## Configuration Overview

Cassandra provides two separate encryption configurations:

| Section | Purpose | Port |
|---------|---------|------|
| `server_encryption_options` | Node-to-node communication | 7000 (7001 legacy SSL) |
| `client_encryption_options` | Client-to-node communication | 9042 |

---

## Internode Encryption

### Full Configuration Reference

```yaml
# cassandra.yaml

server_encryption_options:
    # Encryption scope
    # Options: none, dc, rack, all
    internode_encryption: all

    # Enable legacy SSL storage port (7001)
    # Set to true during migration from unencrypted
    enable_legacy_ssl_storage_port: false

    # Keystore containing node's private key and certificate
    keystore: /etc/cassandra/certs/node-keystore.jks
    keystore_password: changeit

    # Truststore containing CA certificates
    truststore: /etc/cassandra/certs/truststore.jks
    truststore_password: changeit

    # Require client certificate for internode connections
    require_client_auth: true

    # Hostname verification (Cassandra 4.0+)
    require_endpoint_verification: true

    # TLS protocol version
    protocol: TLS

    # Accepted protocol versions
    accepted_protocols:
        - TLSv1.2
        - TLSv1.3

    # Cipher suites (in preference order)
    cipher_suites:
        - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
        - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
        - TLS_AES_256_GCM_SHA384
        - TLS_AES_128_GCM_SHA256

    # Algorithm for secure random number generation
    # algorithm: SunX509

    # Keystore type (JKS, PKCS12, or PEM for Cassandra 4.0+)
    # store_type: JKS

    # SSL context factory (advanced)
    # ssl_context_factory:
    #     class_name: org.apache.cassandra.security.DefaultSslContextFactory
```

### Encryption Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `none` | No encryption | Development only |
| `dc` | Encrypt cross-datacenter only | WAN traffic encryption |
| `rack` | Encrypt cross-rack and cross-datacenter | Physical rack isolation |
| `all` | Encrypt all internode traffic | Recommended for production |

### Migration to Encrypted Internode

Rolling migration from unencrypted to encrypted internode communication:

**Phase 1: Enable Optional Encryption**

```yaml
# On all nodes
server_encryption_options:
    internode_encryption: all
    enable_legacy_ssl_storage_port: true
    optional: true  # Accept both encrypted and unencrypted
```

Perform rolling restart.

**Phase 2: Require Encryption**

```yaml
# On all nodes
server_encryption_options:
    internode_encryption: all
    enable_legacy_ssl_storage_port: false
    optional: false
```

Perform rolling restart.

### Internode Authentication with Mutual TLS (Cassandra 5.0+)

The `MutualTlsInternodeAuthenticator` provides certificate-based authentication for internode connections by extracting identities from certificates and verifying them against a list of authorized peers.

```yaml
# cassandra.yaml
internode_authenticator:
  class_name: org.apache.cassandra.auth.MutualTlsInternodeAuthenticator
  parameters:
    validator_class_name: org.apache.cassandra.auth.SpiffeCertificateValidator
    # Optional: restrict to specific peer identities
    trusted_peer_identities: "spiffe://testdomain.com/cassandra/node1,spiffe://testdomain.com/cassandra/node2"
    # Optional: validate outbound keystore identity
    node_identity: "spiffe://testdomain.com/cassandra/this-node"
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `validator_class_name` | Yes | Certificate validator implementation class |
| `trusted_peer_identities` | No | Comma-separated list of authorized peer identities |
| `node_identity` | No | Expected identity from outbound keystore for validation |

**Prerequisites:**

- `server_encryption_options.internode_encryption` must be set to `all`
- `server_encryption_options.require_client_auth` must be `true`

When `trusted_peer_identities` is configured, only nodes presenting certificates with matching identities can establish internode connections. When omitted, any certificate signed by a trusted CA is accepted.

The `node_identity` parameter validates the local node's keystore identity at startup, catching configuration errors early.

---

## Client Encryption

### Full Configuration Reference

```yaml
# cassandra.yaml

client_encryption_options:
    # Enable client encryption
    enabled: true

    # Accept unencrypted connections alongside encrypted
    # Set to false in production
    optional: false

    # Keystore containing node's private key and certificate
    keystore: /etc/cassandra/certs/node-keystore.jks
    keystore_password: changeit

    # Truststore for validating client certificates
    # Required when require_client_auth is true
    truststore: /etc/cassandra/certs/truststore.jks
    truststore_password: changeit

    # Require client certificates (mutual TLS)
    require_client_auth: false

    # Hostname verification (Cassandra 4.0+)
    require_endpoint_verification: false

    # TLS protocol version
    protocol: TLS

    # Accepted protocol versions
    accepted_protocols:
        - TLSv1.2
        - TLSv1.3

    # Cipher suites
    cipher_suites:
        - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
        - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
        - TLS_AES_256_GCM_SHA384
        - TLS_AES_128_GCM_SHA256
```

### Mutual TLS (mTLS)

Mutual TLS requires clients to present certificates, providing two-way authentication.

```yaml
client_encryption_options:
    enabled: true
    require_client_auth: true
    truststore: /etc/cassandra/certs/client-truststore.jks
    truststore_password: changeit
```

With mTLS enabled:
- Clients must present valid certificates
- Certificates must be signed by a CA in the truststore
- Connection fails if client certificate is invalid or missing

---

## PEM File Configuration (Cassandra 4.0+)

Cassandra 4.0+ supports PEM files directly, eliminating JKS/PKCS12 conversion.

### Server Encryption with PEM

```yaml
server_encryption_options:
    internode_encryption: all
    keystore: /etc/cassandra/certs/node-key.pem
    keystore_password: ""
    truststore: /etc/cassandra/certs/ca-chain.pem
    truststore_password: ""
```

### Client Encryption with PEM

```yaml
client_encryption_options:
    enabled: true
    keystore: /etc/cassandra/certs/node-key.pem
    keystore_password: ""
    truststore: /etc/cassandra/certs/ca-cert.pem
    truststore_password: ""
```

### PEM File Format

Keystore PEM should contain private key followed by certificate chain:

```
-----BEGIN PRIVATE KEY-----
...
-----END PRIVATE KEY-----
-----BEGIN CERTIFICATE-----
... (node certificate)
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
... (intermediate CA, if applicable)
-----END CERTIFICATE-----
```

Truststore PEM should contain CA certificates:

```
-----BEGIN CERTIFICATE-----
... (root CA)
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
... (intermediate CA, if applicable)
-----END CERTIFICATE-----
```

---

## Hot Reloading (Cassandra 4.0+)

Cassandra 4.0+ can reload certificates without restart when files change.

### Requirements

- Keystore and truststore file paths remain the same
- New certificates must be valid
- File modification triggers reload

### Monitoring Reload

Check logs for reload messages:

```
INFO  [main] SSLFactory.java:... - Loaded renewed keystore
INFO  [main] SSLFactory.java:... - Loaded renewed truststore
```

### Forcing Reload via JMX

```bash
# Force SSL context reload
nodetool reloadssl
```

---

## Configuration Validation

### Verify Configuration Before Restart

```bash
# Check cassandra.yaml syntax
python3 -c "import yaml; yaml.safe_load(open('/etc/cassandra/cassandra.yaml'))"

# Verify keystore is readable
keytool -list -keystore /etc/cassandra/certs/node-keystore.jks -storepass changeit

# Verify truststore is readable
keytool -list -keystore /etc/cassandra/certs/truststore.jks -storepass changeit

# Verify certificate validity
openssl x509 -in /etc/cassandra/certs/node-cert.pem -noout -dates
```

### Test TLS Connection

After restart, verify TLS is working:

```bash
# Test client port
openssl s_client -connect localhost:9042 -tls1_2

# Test internode port
openssl s_client -connect localhost:7000 -tls1_2

# Check negotiated cipher
openssl s_client -connect localhost:9042 2>/dev/null | grep "Cipher is"
```

---

## Common Configurations

### Development (Self-Signed)

```yaml
server_encryption_options:
    internode_encryption: none

client_encryption_options:
    enabled: false
```

### Production (Full Encryption)

```yaml
server_encryption_options:
    internode_encryption: all
    keystore: /etc/cassandra/certs/node-keystore.p12
    keystore_password: ${KEYSTORE_PASSWORD}
    truststore: /etc/cassandra/certs/truststore.p12
    truststore_password: ${TRUSTSTORE_PASSWORD}
    require_client_auth: true
    require_endpoint_verification: true
    accepted_protocols:
        - TLSv1.2
        - TLSv1.3
    cipher_suites:
        - TLS_AES_256_GCM_SHA384
        - TLS_AES_128_GCM_SHA256
        - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
        - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256

client_encryption_options:
    enabled: true
    optional: false
    keystore: /etc/cassandra/certs/node-keystore.p12
    keystore_password: ${KEYSTORE_PASSWORD}
    truststore: /etc/cassandra/certs/truststore.p12
    truststore_password: ${TRUSTSTORE_PASSWORD}
    require_client_auth: false
    accepted_protocols:
        - TLSv1.2
        - TLSv1.3
    cipher_suites:
        - TLS_AES_256_GCM_SHA384
        - TLS_AES_128_GCM_SHA256
        - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
        - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
```

### Mutual TLS (Zero Trust)

```yaml
client_encryption_options:
    enabled: true
    optional: false
    require_client_auth: true
    keystore: /etc/cassandra/certs/node-keystore.p12
    keystore_password: ${KEYSTORE_PASSWORD}
    truststore: /etc/cassandra/certs/client-ca-truststore.p12
    truststore_password: ${TRUSTSTORE_PASSWORD}
```

---

## Related Documentation

- [Encryption Overview](index.md) - Why encryption is essential
- [Certificate Types](certificates.md) - Generating certificates
- [Client Configuration](client-configuration.md) - Configuring client applications
- [Troubleshooting](troubleshooting.md) - Common issues
