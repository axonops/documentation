---
description: "PKI fundamentals for Cassandra TLS. Certificates, certificate authorities, and key management."
meta:
  - name: keywords
    content: "PKI, certificates, CA, key management, Cassandra TLS"
---

# PKI Fundamentals

Understanding Public Key Infrastructure (PKI) is essential for correctly implementing TLS in Cassandra. Misconfigured certificates are the primary cause of encryption-related deployment failures.

## Asymmetric Cryptography

PKI is built on asymmetric cryptography, which uses mathematically related key pairs:

### Private Key

A secret value that must be protected and never shared. The private key is used to:

- Decrypt data encrypted with the corresponding public key
- Create digital signatures that prove identity

### Public Key

A value that can be freely distributed. The public key is used to:

- Encrypt data that only the private key holder can decrypt
- Verify digital signatures created by the private key

The mathematical relationship ensures that data encrypted with one key can only be decrypted with the other, and the private key cannot be derived from the public key.

---

## Digital Certificates

A digital certificate binds a public key to an identity (such as a hostname or organization). Certificates are structured documents following the X.509 standard.

### Certificate Fields

| Field | Description |
|-------|-------------|
| Subject | The identity the certificate represents (CN=hostname, O=organization) |
| Public Key | The subject's public key |
| Issuer | The entity that signed the certificate |
| Validity Period | Not Before and Not After timestamps |
| Serial Number | Unique identifier assigned by the issuer |
| Signature | Cryptographic signature from the issuer's private key |
| Extensions | Additional attributes (Subject Alternative Names, Key Usage, etc.) |

### Certificate Extensions

Modern certificates use X.509v3 extensions to specify additional attributes:

| Extension | Purpose |
|-----------|---------|
| Subject Alternative Name (SAN) | Additional identities (hostnames, IP addresses) |
| Key Usage | Permitted uses (digitalSignature, keyEncipherment) |
| Extended Key Usage | Application-specific uses (serverAuth, clientAuth) |
| Basic Constraints | Whether the certificate can sign other certificates (CA) |
| Authority Key Identifier | Identifies the issuer's key |
| Subject Key Identifier | Identifies this certificate's key |

---

## Certificate Authority (CA)

A Certificate Authority is a trusted entity that issues and signs certificates. The CA's role is to verify the identity of certificate requesters before signing their certificates.

### Trust Model

When a system trusts a CA's certificate, it implicitly trusts all certificates signed by that CA. This creates a hierarchical trust chain:

```
Root CA Certificate (self-signed, trusted anchor)
    └── Intermediate CA Certificate (signed by Root)
            └── Server Certificate (signed by Intermediate)
```

### Types of Certificate Authorities

| Type | Use Case | Management |
|------|----------|------------|
| Public CA | External-facing services, browser trust | Purchased from vendors (DigiCert, Let's Encrypt) |
| Private/Internal CA | Internal services, databases | Operated by the organization |
| Self-Signed | Development, testing | No CA infrastructure required |

For Cassandra deployments, a private CA is typically appropriate since all clients and nodes are under organizational control.

### Root vs Intermediate CAs

**Root CA:**
- Self-signed certificate
- Private key kept offline in secure storage (HSM)
- Long validity period (10+ years)
- Signs intermediate CA certificates only

**Intermediate CA:**
- Signed by Root CA
- Private key can be online for automated signing
- Medium validity period (3-5 years)
- Signs end-entity certificates (server, client)

Using intermediate CAs provides security benefits:
- Root CA private key exposure is minimized
- Intermediate CA can be revoked without replacing root
- Different intermediates can be used for different purposes

---

## Certificate Signing Request (CSR)

A CSR is a message sent to a CA requesting certificate issuance. The CSR contains:

- The subject's public key
- The requested identity (subject name)
- Proof of private key possession (signature)

The CA verifies the request, then creates and signs the certificate.

### CSR Generation Example

```bash
# Generate private key
openssl genrsa -out server-key.pem 2048

# Generate CSR
openssl req -new \
    -key server-key.pem \
    -out server.csr \
    -subj "/C=US/ST=California/L=San Francisco/O=Example Corp/CN=cassandra-node-1.example.com"

# View CSR contents
openssl req -in server.csr -noout -text
```

---

## Certificate Chain Validation

When a TLS connection is established, the receiving party validates the presented certificate through a multi-step process:

### Validation Steps

1. **Signature Verification**
   Verify the certificate's signature using the issuer's public key

2. **Chain Building**
   Trace the chain from the certificate to a trusted root CA

3. **Validity Check**
   Confirm the current time falls within the certificate's validity period

4. **Revocation Check** (optional)
   Verify the certificate has not been revoked via CRL or OCSP

5. **Purpose Check**
   Verify the certificate is authorized for the intended use (Key Usage extension)

### Chain Building Process

```
Presented Certificate
    ↓ signed by
Intermediate CA Certificate (in chain or local store)
    ↓ signed by
Root CA Certificate (in truststore)
    ↓
TRUSTED
```

If any step fails, the connection is rejected.

---

## Keystores and Truststores

Java applications (including Cassandra) use keystore files to manage certificates and keys.

### Keystore

Contains the entity's own private key and certificate chain. Used to prove identity to peers.

**Contents:**
- Private key
- Entity's certificate
- Intermediate CA certificates (optional, for chain building)

### Truststore

Contains CA certificates that the entity trusts. Used to verify peer certificates.

**Contents:**
- Root CA certificate(s)
- Intermediate CA certificate(s) (optional)
- Do NOT include the entity's own certificate

### Supported Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| JKS | .jks | Java KeyStore (legacy, Java-specific) |
| PKCS12 | .p12, .pfx | Industry standard, recommended |
| PEM | .pem | Text-based, supported in Cassandra 4.0+ |

### Format Conversion

```bash
# Convert PEM to PKCS12
openssl pkcs12 -export \
    -in cert.pem \
    -inkey key.pem \
    -out keystore.p12 \
    -name alias \
    -password pass:changeit

# Convert PKCS12 to JKS
keytool -importkeystore \
    -srckeystore keystore.p12 \
    -srcstoretype PKCS12 \
    -srcstorepass changeit \
    -destkeystore keystore.jks \
    -deststoretype JKS \
    -deststorepass changeit

# Import CA certificate to truststore
keytool -import \
    -file ca-cert.pem \
    -keystore truststore.jks \
    -storepass changeit \
    -noprompt \
    -alias ca
```

---

## Certificate Inspection

### View Certificate Contents

```bash
# View PEM certificate
openssl x509 -in cert.pem -noout -text

# View certificate dates
openssl x509 -in cert.pem -noout -dates

# View certificate subject and issuer
openssl x509 -in cert.pem -noout -subject -issuer

# View Subject Alternative Names
openssl x509 -in cert.pem -noout -ext subjectAltName
```

### Verify Certificate Chain

```bash
# Verify certificate against CA
openssl verify -CAfile ca-cert.pem cert.pem

# Verify with intermediate CA
openssl verify -CAfile root-ca.pem -untrusted intermediate-ca.pem cert.pem
```

### View Keystore Contents

```bash
# List keystore entries (JKS)
keytool -list -keystore keystore.jks -storepass changeit

# List keystore entries with details
keytool -list -v -keystore keystore.jks -storepass changeit

# List PKCS12 contents
openssl pkcs12 -in keystore.p12 -info -nokeys -passin pass:changeit
```

---

## Related Documentation

- [Encryption Overview](index.md) - Why encryption is essential
- [TLS Versions](tls-versions.md) - Protocol versions and cipher suites
- [Certificate Types](certificates.md) - Server and client certificates for Cassandra
