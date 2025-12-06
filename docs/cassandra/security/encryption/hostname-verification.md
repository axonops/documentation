# Hostname Verification

Hostname verification ensures that the certificate presented by a peer matches the expected identity. Without hostname verification, an attacker with any valid certificate signed by a trusted CA could impersonate any node.

## How Hostname Verification Works

During TLS handshake, the client performs these steps:

1. Receive server certificate
2. Validate certificate chain against truststore
3. **Verify hostname matches certificate identity**

Step 3 is hostname verification. It compares the hostname used to connect against identities in the certificate.

### Identity Matching

The verifier checks these certificate fields in order:

1. **Subject Alternative Name (SAN)** - Preferred method
   - DNS names (e.g., `cassandra-node-1.example.com`)
   - IP addresses (e.g., `10.0.1.1`)

2. **Common Name (CN)** - Legacy fallback
   - Only checked if no SAN extension exists
   - Deprecated by RFC 6125

---

## Subject Alternative Names (SAN)

SANs allow a single certificate to be valid for multiple identities.

### SAN Types

| Type | Format | Example |
|------|--------|---------|
| DNS | `DNS:hostname` | `DNS:cassandra-node-1.example.com` |
| IP | `IP:address` | `IP:10.0.1.1` |
| URI | `URI:identifier` | `URI:spiffe://cluster/node/1` |
| Email | `email:address` | `email:admin@example.com` |

### Recommended SANs for Cassandra Nodes

Include all identities that clients or other nodes might use to connect:

```
DNS.1 = cassandra-node-1
DNS.2 = cassandra-node-1.example.com
DNS.3 = cassandra-node-1.dc1.example.com
IP.1 = 10.0.1.1
IP.2 = 192.168.1.1
```

### Generating Certificates with SANs

```bash
# Create SAN configuration file
cat > san.cnf << EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req

[req_distinguished_name]
CN = cassandra-node-1

[v3_req]
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth, clientAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = cassandra-node-1
DNS.2 = cassandra-node-1.example.com
DNS.3 = localhost
IP.1 = 10.0.1.1
IP.2 = 127.0.0.1
EOF

# Generate CSR with SANs
openssl req -new \
    -key node-key.pem \
    -out node.csr \
    -config san.cnf \
    -subj "/CN=cassandra-node-1"

# Sign certificate preserving SANs
openssl x509 -req \
    -in node.csr \
    -CA ca-cert.pem \
    -CAkey ca-key.pem \
    -CAcreateserial \
    -out node-cert.pem \
    -days 365 \
    -extensions v3_req \
    -extfile san.cnf
```

### Verify SANs in Certificate

```bash
# View SANs
openssl x509 -in node-cert.pem -noout -ext subjectAltName

# Output example:
# X509v3 Subject Alternative Name:
#     DNS:cassandra-node-1, DNS:cassandra-node-1.example.com, IP Address:10.0.1.1
```

---

## Cassandra Configuration

### Enabling Hostname Verification (Cassandra 4.0+)

```yaml
# cassandra.yaml

# Internode encryption
server_encryption_options:
    internode_encryption: all
    require_endpoint_verification: true
    # ... keystore and truststore settings

# Client encryption
client_encryption_options:
    enabled: true
    require_endpoint_verification: true
    # ... keystore and truststore settings
```

### Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `require_endpoint_verification` | false | Enable hostname verification |

### Pre-Cassandra 4.0

Earlier versions do not support hostname verification natively. Options include:

- Upgrade to Cassandra 4.0+
- Rely on certificate chain validation only
- Implement custom SSL context factory

---

## Wildcard Certificates

Wildcard certificates match multiple hostnames with a single certificate.

### Wildcard Rules

| Pattern | Matches | Does Not Match |
|---------|---------|----------------|
| `*.example.com` | `node1.example.com` | `node1.dc1.example.com` |
| `*.example.com` | `node2.example.com` | `example.com` |

Wildcards only match a single label (between dots).

### Wildcard Certificate Generation

```bash
# Generate certificate with wildcard SAN
cat > wildcard-san.cnf << EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req

[req_distinguished_name]
CN = *.cassandra.example.com

[v3_req]
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = *.cassandra.example.com
DNS.2 = cassandra.example.com
EOF
```

### Wildcard Considerations

**Advantages:**
- Simplified certificate management
- Single certificate for all nodes in a domain

**Disadvantages:**
- Compromised certificate affects all nodes
- Cannot use IP address SANs with wildcards
- May not meet compliance requirements

**Recommendation:** Use individual certificates per node in production environments.

---

## Cloud and Kubernetes Environments

### Dynamic IP Addresses

Cloud instances may have changing IP addresses. Strategies:

1. **DNS-based identity**: Use DNS names instead of IP addresses
2. **Service discovery**: Configure clients to resolve hostnames dynamically
3. **IP SANs at provisioning**: Generate certificates during instance creation

### Kubernetes

Pods have multiple identities:

```
DNS.1 = pod-name
DNS.2 = pod-name.service-name
DNS.3 = pod-name.service-name.namespace
DNS.4 = pod-name.service-name.namespace.svc.cluster.local
IP.1 = <pod-ip>
```

### Example: Kubernetes Certificate SANs

```yaml
[alt_names]
DNS.1 = cassandra-0
DNS.2 = cassandra-0.cassandra-headless
DNS.3 = cassandra-0.cassandra-headless.default
DNS.4 = cassandra-0.cassandra-headless.default.svc.cluster.local
DNS.5 = *.cassandra-headless.default.svc.cluster.local
```

---

## Troubleshooting Hostname Verification

### Common Errors

**Certificate does not match hostname:**

```
javax.net.ssl.SSLPeerUnverifiedException: Hostname verification failed
```

**Causes:**
- Certificate CN/SAN does not include the connection hostname
- Client connecting via IP but certificate only has DNS names
- DNS resolution returning unexpected hostname

### Diagnostic Commands

```bash
# Check what hostname the client is using
nslookup 10.0.1.1

# Verify certificate SANs
openssl x509 -in node-cert.pem -noout -ext subjectAltName

# Test TLS connection with hostname
openssl s_client -connect cassandra-node-1.example.com:9042 \
    -servername cassandra-node-1.example.com

# Test hostname verification explicitly
openssl s_client -connect cassandra-node-1.example.com:9042 \
    -verify_hostname cassandra-node-1.example.com
```

### Resolution Steps

1. Identify the hostname used by connecting clients
2. Verify that hostname exists in certificate SANs
3. Regenerate certificate with correct SANs if needed
4. Ensure DNS resolves correctly

---

## Related Documentation

- [Encryption Overview](index.md) - Why encryption is essential
- [Certificate Types](certificates.md) - Certificate generation
- [Cassandra Configuration](configuration.md) - Full configuration reference
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
