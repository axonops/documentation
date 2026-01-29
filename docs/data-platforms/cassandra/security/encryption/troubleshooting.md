---
title: "Cassandra TLS Troubleshooting"
description: "Troubleshoot Cassandra TLS issues. Common SSL errors and debugging techniques."
meta:
  - name: keywords
    content: "TLS troubleshooting, SSL errors, certificate debugging, Cassandra"
---

# TLS Troubleshooting

This section covers common TLS configuration issues and their resolution.

## Diagnostic Tools

### OpenSSL Commands

```bash
# Test TLS connection
openssl s_client -connect cassandra-node:9042 -tls1_2

# Show server certificate
openssl s_client -connect cassandra-node:9042 2>/dev/null | \
    openssl x509 -noout -text

# Test specific cipher suite
openssl s_client -connect cassandra-node:9042 \
    -cipher ECDHE-RSA-AES256-GCM-SHA384

# Verify certificate chain
openssl verify -CAfile ca-chain.pem server-cert.pem

# Check certificate expiration
openssl x509 -in cert.pem -noout -dates

# View certificate SANs
openssl x509 -in cert.pem -noout -ext subjectAltName
```

### Keytool Commands

```bash
# List keystore contents
keytool -list -v -keystore keystore.jks -storepass changeit

# Check specific alias
keytool -list -v -keystore keystore.jks -storepass changeit -alias node1

# Export certificate from keystore
keytool -exportcert -keystore keystore.jks -storepass changeit \
    -alias node1 -file exported-cert.pem -rfc

# Verify keystore password
keytool -list -keystore keystore.jks -storepass wrongpassword
```

### Cassandra Logs

Check logs for TLS-related errors:

```bash
# Grep for SSL/TLS errors
grep -i "ssl\|tls\|certificate\|keystore\|truststore" /var/log/cassandra/system.log

# Recent errors
tail -1000 /var/log/cassandra/system.log | grep -i "error\|exception"
```

---

## Common Errors

### Keystore/Truststore Not Found

**Error:**
```
java.io.FileNotFoundException: /etc/cassandra/certs/keystore.jks (No such file or directory)
```

**Causes:**
- Incorrect file path in cassandra.yaml
- File does not exist
- Cassandra user lacks read permission

**Resolution:**
```bash
# Verify file exists
ls -la /etc/cassandra/certs/keystore.jks

# Check permissions
stat /etc/cassandra/certs/keystore.jks

# Fix permissions
chown cassandra:cassandra /etc/cassandra/certs/keystore.jks
chmod 400 /etc/cassandra/certs/keystore.jks
```

---

### Incorrect Keystore Password

**Error:**
```
java.io.IOException: Keystore was tampered with, or password was incorrect
```

**Causes:**
- Wrong password in cassandra.yaml
- Keystore corrupted
- Wrong keystore type specified

**Resolution:**
```bash
# Test password
keytool -list -keystore keystore.jks -storepass your_password

# If password is correct but error persists, check keystore type
keytool -list -keystore keystore.jks -storetype PKCS12 -storepass your_password
```

---

### Certificate Chain Validation Failed

**Error:**
```
sun.security.validator.ValidatorException: PKIX path building failed
sun.security.provider.certpath.SunCertPathBuilderException: unable to find valid certification path to requested target
```

**Causes:**
- CA certificate missing from truststore
- Intermediate CA certificate missing
- Certificate chain incomplete

**Resolution:**
```bash
# Verify certificate chain
openssl verify -CAfile ca-chain.pem server-cert.pem

# Check truststore contains CA
keytool -list -keystore truststore.jks -storepass changeit

# Add missing CA certificate
keytool -import -file ca-cert.pem -keystore truststore.jks \
    -storepass changeit -alias ca -noprompt

# If intermediate CA is missing, add it too
keytool -import -file intermediate-ca.pem -keystore truststore.jks \
    -storepass changeit -alias intermediate-ca -noprompt
```

---

### Certificate Expired

**Error:**
```
javax.net.ssl.SSLHandshakeException: PKIX path validation failed: java.security.cert.CertPathValidatorException: validity check failed
```

**Causes:**
- Server certificate expired
- CA certificate expired

**Resolution:**
```bash
# Check certificate expiration
openssl x509 -in cert.pem -noout -dates

# Check all certificates in chain
openssl x509 -in server-cert.pem -noout -dates
openssl x509 -in intermediate-ca.pem -noout -dates
openssl x509 -in root-ca.pem -noout -dates

# Generate and deploy new certificates
```

---

### Hostname Verification Failed

**Error:**
```
javax.net.ssl.SSLPeerUnverifiedException: Hostname cassandra-node-1 not verified
java.security.cert.CertificateException: No subject alternative names matching IP address 10.0.1.1 found
```

**Causes:**
- Certificate CN/SAN does not match connection hostname
- Connecting via IP but certificate only has DNS names
- Connecting via hostname not in SAN list

**Resolution:**
```bash
# Check certificate SANs
openssl x509 -in cert.pem -noout -ext subjectAltName

# Check what hostname is being used
nslookup 10.0.1.1

# Options:
# 1. Regenerate certificate with correct SANs
# 2. Connect using hostname that matches certificate
# 3. Disable hostname verification (not recommended for production)
```

**Regenerate certificate with IP SAN:**
```bash
# In san.cnf
[alt_names]
DNS.1 = cassandra-node-1
DNS.2 = cassandra-node-1.example.com
IP.1 = 10.0.1.1
IP.2 = 192.168.1.1
```

---

### No Cipher Suites in Common

**Error:**
```
javax.net.ssl.SSLHandshakeException: no cipher suites in common
```

**Causes:**
- Server and client have incompatible cipher suites
- TLS version mismatch
- Weak ciphers disabled on one side

**Resolution:**
```bash
# Check server's supported ciphers
nmap --script ssl-enum-ciphers -p 9042 cassandra-node

# Check client's available ciphers
openssl ciphers -v

# Update cassandra.yaml to include compatible ciphers
# Or update client configuration
```

**Example fix in cassandra.yaml:**
```yaml
server_encryption_options:
    cipher_suites:
        - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
        - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
        - TLS_RSA_WITH_AES_256_GCM_SHA384  # Fallback if needed
```

---

### Protocol Version Mismatch

**Error:**
```
javax.net.ssl.SSLHandshakeException: No appropriate protocol (protocol is disabled or cipher suites are inappropriate)
```

**Causes:**
- Client requires TLS 1.3 but server only supports TLS 1.2
- Server requires TLS 1.2 but client only supports TLS 1.0

**Resolution:**
```bash
# Test supported protocols
openssl s_client -connect cassandra-node:9042 -tls1_2
openssl s_client -connect cassandra-node:9042 -tls1_3

# Update cassandra.yaml
```

```yaml
server_encryption_options:
    accepted_protocols:
        - TLSv1.2
        - TLSv1.3
```

---

### Private Key Does Not Match Certificate

**Error:**
```
java.security.UnrecoverableKeyException: Cannot recover key
```

**Causes:**
- Private key in keystore does not match certificate
- Keystore corrupted during creation

**Resolution:**
```bash
# Verify key matches certificate
openssl x509 -noout -modulus -in cert.pem | openssl md5
openssl rsa -noout -modulus -in key.pem | openssl md5
# Both should output identical hashes

# Recreate keystore with matching key and certificate
openssl pkcs12 -export \
    -in cert.pem \
    -inkey key.pem \
    -out keystore.p12 \
    -name alias \
    -password pass:changeit
```

---

### Internode Connection Failures

**Error in logs:**
```
ERROR [MessagingService-Outgoing] OutboundConnection.java: Failed to connect
javax.net.ssl.SSLHandshakeException: Received fatal alert: certificate_unknown
```

**Causes:**
- Peer node's certificate not trusted
- Truststore missing CA certificate
- Certificate CN/SAN mismatch

**Resolution:**
```bash
# Test internode connection
openssl s_client -connect other-node:7000 -CAfile truststore.pem

# Verify both nodes have same truststore
md5sum /etc/cassandra/certs/truststore.jks  # Run on both nodes

# Check certificate is signed by trusted CA
openssl verify -CAfile ca-chain.pem peer-cert.pem
```

---

### Client Connection Failures

**cqlsh Error:**
```
Connection error: ('Unable to connect to any servers', {'cassandra-node': error(...)})
```

**Resolution:**
```bash
# Test with OpenSSL first
openssl s_client -connect cassandra-node:9042 -CAfile ca-cert.pem

# Check cqlshrc configuration
cat ~/.cassandra/cqlshrc

# Try with explicit certificate
cqlsh --ssl --ssl-certfile=/path/to/ca-cert.pem cassandra-node
```

---

## Node Startup Failures

### Node Fails to Start After Enabling TLS

**Diagnostic Steps:**

1. Check logs for specific error:
```bash
tail -100 /var/log/cassandra/system.log
```

2. Verify keystore/truststore accessible:
```bash
sudo -u cassandra cat /etc/cassandra/certs/keystore.jks > /dev/null
```

3. Test keystore password:
```bash
keytool -list -keystore /etc/cassandra/certs/keystore.jks -storepass $(grep keystore_password cassandra.yaml | awk '{print $2}')
```

4. Validate configuration syntax:
```bash
python3 -c "import yaml; yaml.safe_load(open('/etc/cassandra/cassandra.yaml'))"
```

### Rolling Back

If TLS configuration prevents cluster operation:

```bash
# Temporarily disable encryption
sed -i 's/internode_encryption: all/internode_encryption: none/' /etc/cassandra/cassandra.yaml
sed -i 's/enabled: true/enabled: false/' /etc/cassandra/cassandra.yaml

# Restart node
systemctl restart cassandra

# Fix certificates, then re-enable
```

---

## Performance Issues

### High CPU Usage

TLS adds CPU overhead. If experiencing performance degradation:

```bash
# Check if AES-NI is available
grep aes /proc/cpuinfo

# Use AES-GCM ciphers (hardware accelerated)
cipher_suites:
    - TLS_AES_256_GCM_SHA384
    - TLS_AES_128_GCM_SHA256
```

### Connection Latency

TLS handshake adds latency. Mitigations:

- Enable TLS session resumption
- Use TLS 1.3 (faster handshake)
- Monitor handshake times

---

## Debug Logging

### Enable SSL Debug Output

Add to `jvm.options`:

```bash
# Full SSL debug (verbose)
-Djavax.net.debug=ssl

# Handshake only
-Djavax.net.debug=ssl:handshake

# Certificate chain
-Djavax.net.debug=ssl:trustmanager
```

**Warning:** SSL debug output is extremely verbose. Enable temporarily for troubleshooting only.

### Interpret Debug Output

Key messages to look for:

```
# Successful handshake
"ServerHello" with cipher suite
"Certificate chain" showing peer's certificates
"Finished" indicating successful handshake

# Failures
"alert: fatal" indicates handshake failure
"certificate_unknown" means cert not trusted
"handshake_failure" general failure
```

---

## Related Documentation

- [Encryption Overview](index.md) - Why encryption is essential
- [Certificate Types](certificates.md) - Certificate generation
- [Cassandra Configuration](configuration.md) - Server configuration
- [Enterprise Recommendations](enterprise-recommendations.md) - Best practices