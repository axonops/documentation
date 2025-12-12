# Enterprise Recommendations

This section provides security hardening guidelines and certificate lifecycle management procedures for production Cassandra deployments.

## Certificate Lifecycle Management

### Certificate Validity Periods

| Certificate Type | Recommended Validity | Rationale |
|------------------|---------------------|-----------|
| Root CA | 10-20 years | Rarely changed, offline storage |
| Intermediate CA | 3-5 years | Balance between security and operational overhead |
| Server/Client | 1 year | Compliance requirements, security best practice |

### Certificate Inventory

Maintain a certificate inventory tracking:

| Field | Description |
|-------|-------------|
| Certificate CN/SAN | Identity |
| Serial Number | Unique identifier |
| Issue Date | When issued |
| Expiration Date | When expires |
| Issuing CA | Which CA signed |
| Node/Application | Where deployed |
| Keystore Location | File path |

### Expiration Monitoring

Implement automated monitoring for certificate expiration:

```bash
#!/bin/bash
# check-cert-expiry.sh

CERT_FILE=$1
WARN_DAYS=30
CRIT_DAYS=7

EXPIRY=$(openssl x509 -in "$CERT_FILE" -noout -enddate | cut -d= -f2)
EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s)
NOW_EPOCH=$(date +%s)
DAYS_LEFT=$(( (EXPIRY_EPOCH - NOW_EPOCH) / 86400 ))

if [ $DAYS_LEFT -lt $CRIT_DAYS ]; then
    echo "CRITICAL: Certificate expires in $DAYS_LEFT days"
    exit 2
elif [ $DAYS_LEFT -lt $WARN_DAYS ]; then
    echo "WARNING: Certificate expires in $DAYS_LEFT days"
    exit 1
else
    echo "OK: Certificate expires in $DAYS_LEFT days"
    exit 0
fi
```

---

## Certificate Rotation

### Pre-Rotation Checklist

- [ ] New certificates generated and validated
- [ ] Certificate chain verified
- [ ] SANs match all required identities
- [ ] Keystores and truststores created
- [ ] Backup of current certificates
- [ ] Rollback procedure documented
- [ ] Maintenance window scheduled

### Rotation Procedure (Cassandra 4.0+)

Cassandra 4.0+ supports hot reloading of certificates without restart.

**Step 1: Prepare New Certificates**

```bash
# Generate new certificates
./generate-node-cert.sh cassandra-node-1

# Verify new certificate
openssl verify -CAfile ca-chain.pem new-cert.pem
```

**Step 2: Update Truststore (If CA Changed)**

If using a new CA or intermediate, update truststores first:

```bash
# Add new CA to truststore
keytool -import \
    -file new-ca-cert.pem \
    -keystore truststore.jks \
    -storepass changeit \
    -alias new-ca \
    -noprompt
```

Deploy updated truststore to all nodes and reload:

```bash
nodetool reloadssl
```

**Step 3: Update Keystores**

Replace keystore files and reload:

```bash
# Backup current keystore
cp /etc/cassandra/certs/keystore.jks /etc/cassandra/certs/keystore.jks.bak

# Deploy new keystore
cp new-keystore.jks /etc/cassandra/certs/keystore.jks

# Reload SSL context
nodetool reloadssl
```

**Step 4: Verify**

```bash
# Check new certificate is active
openssl s_client -connect localhost:9042 2>/dev/null | \
    openssl x509 -noout -dates -serial
```

### Rotation Procedure (Pre-4.0)

Requires rolling restart:

1. Update truststore with new CA (if changed)
2. Rolling restart all nodes
3. Update keystores with new certificates
4. Rolling restart all nodes

### Client Certificate Rotation

1. Generate new client certificates
2. Update client applications with new certificates
3. Deploy client updates during maintenance window
4. Remove old client CA from Cassandra truststore (if applicable)

---

## Security Hardening

### TLS Configuration

```yaml
# Production hardened configuration
server_encryption_options:
    internode_encryption: all
    require_client_auth: true
    require_endpoint_verification: true

    accepted_protocols:
        - TLSv1.3
        - TLSv1.2

    cipher_suites:
        # TLS 1.3 ciphers (preferred)
        - TLS_AES_256_GCM_SHA384
        - TLS_AES_128_GCM_SHA256
        # TLS 1.2 fallback (forward secrecy required)
        - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
        - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
```

### JVM Security Options

Add to `jvm.options` or `cassandra-env.sh`:

```bash
# Disable weak TLS versions at JVM level
-Djdk.tls.disabledAlgorithms=SSLv3,TLSv1,TLSv1.1,RC4,DES,MD5withRSA,DH keySize < 2048,EC keySize < 224,3DES_EDE_CBC,anon,NULL

# Disable TLS session tickets (if not needed)
-Djdk.tls.server.enableSessionTicketExtension=false

# Ephemeral DH key size
-Djdk.tls.ephemeralDHKeySize=2048
```

### Key Size Requirements

| Key Type | Minimum | Recommended |
|----------|---------|-------------|
| RSA | 2048 bits | 4096 bits (CA), 2048 bits (server) |
| ECDSA | 256 bits | 384 bits |
| DH Parameters | 2048 bits | 4096 bits |

### File Permissions

```bash
# Private keys: owner read only
chmod 400 /etc/cassandra/certs/*-key.pem
chown cassandra:cassandra /etc/cassandra/certs/*-key.pem

# Keystores: owner read only
chmod 400 /etc/cassandra/certs/*.jks
chmod 400 /etc/cassandra/certs/*.p12
chown cassandra:cassandra /etc/cassandra/certs/*.jks
chown cassandra:cassandra /etc/cassandra/certs/*.p12

# Public certificates and truststores: owner read, group read
chmod 440 /etc/cassandra/certs/*-cert.pem
chmod 440 /etc/cassandra/certs/truststore.*
```

---

## Private Key Protection

### Hardware Security Modules (HSM)

For high-security environments, store CA private keys in HSMs:

- AWS CloudHSM
- Azure Dedicated HSM
- HashiCorp Vault with HSM backend
- Thales Luna HSM

### Encrypted Private Keys

Encrypt private keys at rest:

```bash
# Encrypt private key with AES-256
openssl rsa -aes256 -in key.pem -out key-encrypted.pem

# Cassandra requires unencrypted keys in keystore
# Decrypt at deployment time only
```

### Key Escrow

Implement key escrow for disaster recovery:

- Store encrypted backup of CA private keys
- Use multiple custodians with key shares
- Document recovery procedure
- Test recovery annually

---

## Compliance Considerations

### PCI-DSS

Requirements for cardholder data environments:

- TLS 1.2 minimum (TLS 1.0/1.1 prohibited)
- Strong cryptography (AES-128 minimum)
- Certificate management procedures documented
- Quarterly vulnerability scans
- Annual penetration testing

### HIPAA

Requirements for protected health information:

- Encryption in transit required
- Access controls implemented
- Audit logging enabled
- Risk assessment documented

### SOC 2

Common Criteria requirements:

- CC6.1: Logical access security
- CC6.6: System boundaries protection
- CC6.7: Data transmission encryption

### Documentation Requirements

Maintain documentation for:

| Document | Contents |
|----------|----------|
| Certificate Policy | Issuance rules, validity periods, revocation |
| Certificate Practice Statement | Operational procedures |
| Key Management Policy | Key generation, storage, rotation, destruction |
| Incident Response | Certificate compromise procedures |

---

## Disaster Recovery

### Certificate Backup

```bash
#!/bin/bash
# backup-certs.sh

BACKUP_DIR="/backup/cassandra-certs/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Backup keystores and truststores
cp /etc/cassandra/certs/*.jks "$BACKUP_DIR/"
cp /etc/cassandra/certs/*.p12 "$BACKUP_DIR/"
cp /etc/cassandra/certs/*.pem "$BACKUP_DIR/"

# Encrypt backup
tar czf - "$BACKUP_DIR" | \
    openssl enc -aes-256-cbc -salt -out "${BACKUP_DIR}.tar.gz.enc"

# Store encryption key separately
```

### CA Key Recovery

Root CA private key recovery procedure:

1. Retrieve encrypted key backup from secure storage
2. Assemble key custodians (minimum 2)
3. Decrypt key using combined credentials
4. Verify key integrity
5. Use for emergency certificate issuance
6. Re-encrypt and return to secure storage

### Certificate Revocation

If certificates are compromised:

1. Generate new certificates immediately
2. Deploy new certificates via hot reload
3. Update truststores to remove compromised CA (if applicable)
4. Publish Certificate Revocation List (CRL)
5. Notify affected parties
6. Conduct incident review

---

## Monitoring and Alerting

### Certificate Expiration Alerts

| Days to Expiry | Alert Level |
|----------------|-------------|
| 60 days | Info |
| 30 days | Warning |
| 14 days | Critical |
| 7 days | Emergency |

### TLS Connection Monitoring

Monitor for:

- TLS handshake failures
- Certificate validation errors
- Cipher suite negotiation failures
- Protocol version mismatches

### Audit Logging

Enable TLS-related audit events:

```yaml
# cassandra.yaml
audit_logging_options:
    enabled: true
    included_categories: AUTH, ERROR
```

---

## Related Documentation

- [Encryption Overview](index.md) - Why encryption is essential
- [Certificate Types](certificates.md) - Certificate generation
- [Cassandra Configuration](configuration.md) - Server configuration
- [Troubleshooting](troubleshooting.md) - Common issues
