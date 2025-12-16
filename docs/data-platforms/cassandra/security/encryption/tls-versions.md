---
title: "TLS Versions and Cipher Suites"
description: "TLS version configuration for Cassandra. TLS 1.2, TLS 1.3, and cipher suite selection."
meta:
  - name: keywords
    content: "TLS versions, TLS 1.2, TLS 1.3, cipher suites, Cassandra"
---

# TLS Versions and Cipher Suites

Transport Layer Security (TLS) protocol versions and cipher suites determine the cryptographic algorithms used to secure Cassandra communications. Selecting appropriate versions and ciphers is critical for both security and interoperability.

## TLS Protocol Versions

### Version Comparison

| Version | Status | Java Requirement | Cassandra Support |
|---------|--------|------------------|-------------------|
| SSL 3.0 | Deprecated | - | Disabled by default |
| TLS 1.0 | Deprecated | Java 6+ | Supported, not recommended |
| TLS 1.1 | Deprecated | Java 7+ | Supported, not recommended |
| TLS 1.2 | Current | Java 7+ | Recommended minimum |
| TLS 1.3 | Current | Java 11+ | Recommended (Cassandra 4.0+) |

### Protocol Security Status

**TLS 1.3** (Recommended)
- Removed obsolete cryptographic algorithms
- Faster handshake (1-RTT, 0-RTT resumption)
- Forward secrecy mandatory
- Simplified cipher suite configuration

**TLS 1.2** (Acceptable)
- Widely supported
- Secure when configured with strong cipher suites
- Requires careful cipher suite selection

**TLS 1.0/1.1** (Deprecated)
- Vulnerable to BEAST, POODLE attacks
- PCI-DSS compliance prohibits use
- Disable in production environments

---

## Cipher Suites

A cipher suite defines the combination of algorithms used for:
- Key exchange (how keys are established)
- Authentication (how identity is verified)
- Encryption (how data is protected)
- Message authentication (how integrity is verified)

### TLS 1.3 Cipher Suites

TLS 1.3 simplified cipher suite naming. All TLS 1.3 suites use AEAD encryption and are considered secure.

| Cipher Suite | Encryption | Notes |
|--------------|------------|-------|
| `TLS_AES_256_GCM_SHA384` | AES-256-GCM | Recommended |
| `TLS_AES_128_GCM_SHA256` | AES-128-GCM | Good performance |
| `TLS_CHACHA20_POLY1305_SHA256` | ChaCha20-Poly1305 | Good for non-AES-NI CPUs |

### TLS 1.2 Cipher Suites

TLS 1.2 cipher suites require careful selection. Use only AEAD ciphers with forward secrecy.

**Recommended:**

| Cipher Suite | Key Exchange | Encryption |
|--------------|--------------|------------|
| `TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384` | ECDHE | AES-256-GCM |
| `TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256` | ECDHE | AES-128-GCM |
| `TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384` | ECDHE | AES-256-GCM |
| `TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256` | ECDHE | AES-128-GCM |
| `TLS_DHE_RSA_WITH_AES_256_GCM_SHA384` | DHE | AES-256-GCM |
| `TLS_DHE_RSA_WITH_AES_128_GCM_SHA256` | DHE | AES-128-GCM |

**Avoid:**

| Pattern | Reason |
|---------|--------|
| `*_CBC_*` | Vulnerable to padding oracle attacks |
| `*_RC4_*` | RC4 is broken |
| `*_DES_*` | DES is weak |
| `*_NULL_*` | No encryption |
| `*_EXPORT_*` | Weak export-grade cryptography |
| `TLS_RSA_*` | No forward secrecy |

---

## Forward Secrecy

Forward secrecy (also called perfect forward secrecy) ensures that session keys cannot be compromised even if the server's private key is later exposed.

### How It Works

Without forward secrecy (RSA key exchange):
- Session keys are encrypted with the server's RSA public key
- If the private key is compromised, all past sessions can be decrypted

With forward secrecy (ECDHE/DHE key exchange):
- Session keys are generated using ephemeral Diffie-Hellman
- Each session uses unique keys
- Compromised private key cannot decrypt past sessions

### Configuration

Enable forward secrecy by prioritizing ECDHE and DHE cipher suites:

```yaml
# cassandra.yaml
server_encryption_options:
    cipher_suites:
        - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
        - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
```

---

## Configuration Examples

### Cassandra 4.0+ with TLS 1.3

```yaml
# cassandra.yaml
server_encryption_options:
    internode_encryption: all
    protocol: TLS
    accepted_protocols:
        - TLSv1.3
        - TLSv1.2
    cipher_suites:
        - TLS_AES_256_GCM_SHA384
        - TLS_AES_128_GCM_SHA256
        - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
        - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
```

### TLS 1.2 Only (Java 8)

```yaml
# cassandra.yaml
server_encryption_options:
    internode_encryption: all
    protocol: TLS
    accepted_protocols:
        - TLSv1.2
    cipher_suites:
        - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
        - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
        - TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
        - TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
```

### Explicitly Disable Weak Protocols

```yaml
# cassandra.yaml
server_encryption_options:
    # Only allow TLS 1.2+
    accepted_protocols:
        - TLSv1.2
        - TLSv1.3
    # Explicitly exclude weak protocols (redundant but explicit)
    # SSLv3, TLSv1, TLSv1.1 are not listed
```

---

## Verifying TLS Configuration

### Check Supported Protocols

```bash
# Test TLS 1.3
openssl s_client -connect cassandra-node:9042 -tls1_3

# Test TLS 1.2
openssl s_client -connect cassandra-node:9042 -tls1_2

# Test TLS 1.1 (should fail if properly configured)
openssl s_client -connect cassandra-node:9042 -tls1_1
```

### Check Cipher Suites

```bash
# Show negotiated cipher suite
openssl s_client -connect cassandra-node:9042 -tls1_2 2>/dev/null | grep "Cipher is"

# Test specific cipher suite
openssl s_client -connect cassandra-node:9042 -cipher ECDHE-RSA-AES256-GCM-SHA384
```

### Using nmap for TLS Analysis

```bash
# Scan TLS configuration
nmap --script ssl-enum-ciphers -p 9042 cassandra-node
```

---

## Java Version Considerations

### Java 8

- TLS 1.2 supported
- TLS 1.3 not available
- Some GCM cipher suites may have performance issues

### Java 11+

- TLS 1.3 supported
- Improved TLS performance
- Recommended for production deployments

### JVM Options

```bash
# Disable weak protocols at JVM level
-Djdk.tls.disabledAlgorithms=SSLv3,TLSv1,TLSv1.1,RC4,DES,MD5withRSA,DH keySize < 1024,EC keySize < 224

# Enable TLS 1.3 (Java 11+)
-Djdk.tls.client.protocols=TLSv1.3,TLSv1.2
```

---

## Compliance Requirements

| Standard | Minimum TLS Version | Notes |
|----------|---------------------|-------|
| PCI-DSS 3.2+ | TLS 1.2 | TLS 1.0/1.1 prohibited since 2018 |
| HIPAA | TLS 1.2 | Strong encryption required |
| NIST SP 800-52 | TLS 1.2 | TLS 1.3 recommended |
| FedRAMP | TLS 1.2 | Federal systems requirement |

---

## Related Documentation

- [Encryption Overview](index.md) - Why encryption is essential
- [PKI Fundamentals](pki-fundamentals.md) - Certificate concepts
- [Cassandra Configuration](configuration.md) - Detailed configuration options
