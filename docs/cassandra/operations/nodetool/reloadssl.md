---
description: "Reload SSL certificates without restart using nodetool reloadssl command."
meta:
  - name: keywords
    content: "nodetool reloadssl, reload SSL, certificate reload, Cassandra security"
---

# nodetool reloadssl

Reloads SSL certificates without restarting Cassandra.

**Introduced in:** Cassandra 4.0

---

## Synopsis

```bash
nodetool [connection_options] reloadssl
```

## Description

`nodetool reloadssl` reloads the SSL/TLS certificates configured for client and inter-node encryption. This allows certificate rotation without downtime—essential for maintaining security while keeping the cluster operational.

!!! danger "Cassandra 3.x and Earlier: Certificate Expiration is Critical"
    The `reloadssl` command is not available in Cassandra versions prior to 4.0. In these versions, SSL certificate changes require a node restart.

    **This creates a critical operational risk:** If certificates expire before renewal, restarting a node with new certificates will fail to establish communication with other nodes still using expired certificates. This can result in:

    - Nodes unable to rejoin the cluster
    - Complete cluster communication failure if multiple nodes restart
    - Potential data unavailability

    **For Cassandra 3.x clusters:**

    - Implement certificate monitoring with alerts well before expiration (60+ days)
    - Perform rolling certificate replacements while certificates are still valid
    - Consider upgrading to Cassandra 4.0+ to enable hot certificate reloading

---

## When to Use

### Certificate Renewal

```bash
# 1. Copy new certificates to configured location
cp /new/certs/keystore.jks /etc/cassandra/conf/
cp /new/certs/truststore.jks /etc/cassandra/conf/

# 2. Reload certificates
nodetool reloadssl
```

### Certificate Rotation

During security certificate rotation:

```bash
# On each node, one at a time
nodetool reloadssl
```

### After Updating Truststore

When adding new CA certificates:

```bash
# Update truststore
keytool -import -alias newca -file /path/to/new-ca.crt -keystore /etc/cassandra/truststore.jks

# Reload
nodetool reloadssl
```

---

## Prerequisites

### Certificate Files

SSL configuration in `cassandra.yaml`:

```yaml
server_encryption_options:
    keystore: /etc/cassandra/conf/keystore.jks
    keystore_password: changeit
    truststore: /etc/cassandra/conf/truststore.jks
    truststore_password: changeit

client_encryption_options:
    enabled: true
    keystore: /etc/cassandra/conf/keystore.jks
    keystore_password: changeit
    truststore: /etc/cassandra/conf/truststore.jks
    truststore_password: changeit
```

### File Permissions

```bash
# Certificates must be readable by Cassandra user
chown cassandra:cassandra /etc/cassandra/conf/*.jks
chmod 640 /etc/cassandra/conf/*.jks
```

---

## What Gets Reloaded

| Component | Reloaded |
|-----------|----------|
| Server keystore | Yes |
| Server truststore | Yes |
| Client keystore | Yes |
| Client truststore | Yes |
| Internode encryption | Yes |

---

## Certificate Rotation Workflow

### Complete Rotation Process

```bash
# Phase 1: Update truststore with new CA (on all nodes)
keytool -import -alias newca -file new-ca.crt -keystore truststore.jks

# On each node:
nodetool reloadssl

# Phase 2: Update keystore with new cert (on each node)
# Copy new keystore
cp new-keystore.jks /etc/cassandra/conf/keystore.jks

nodetool reloadssl

# Phase 3: Remove old CA from truststore (after all nodes updated)
keytool -delete -alias oldca -keystore truststore.jks

nodetool reloadssl
```

### Rolling Update

```bash
#!/bin/bash
# rotate_certs.sh - Rotate certificates across cluster

NODES="node1 node2 node3"

for node in $NODES; do
    echo "Updating certificates on $node..."

    # Copy new certs (implement your copy mechanism)
    scp keystore.jks $node:/etc/cassandra/conf/
    scp truststore.jks $node:/etc/cassandra/conf/

    # Reload on node
    ssh $node "nodetool reloadssl"

    echo "Completed $node, waiting 30s..."
    sleep 30
done
```

---

## Verification

### Before Reload

```bash
# Check certificate expiration
keytool -list -v -keystore /etc/cassandra/conf/keystore.jks | grep "Valid"
```

### After Reload

```bash
# Test SSL connection
openssl s_client -connect localhost:9042 -showcerts

# Test CQL connection
cqlsh --ssl localhost
```

### Check Logs

```bash
tail -f /var/log/cassandra/system.log | grep -i ssl
```

---

## Common Issues

### Certificate File Not Found

```
ERROR: FileNotFoundException: /etc/cassandra/conf/keystore.jks
```

Solution:
```bash
# Verify file exists and permissions
ls -la /etc/cassandra/conf/*.jks
chown cassandra:cassandra /etc/cassandra/conf/*.jks
```

### Wrong Password

```
ERROR: Keystore was tampered with, or password was incorrect
```

Solution:
- Verify password in `cassandra.yaml` matches keystore password
- Recreate keystore with correct password

### Certificate Chain Invalid

```
ERROR: PKIX path building failed
```

Solution:
- Ensure truststore contains the CA that signed the certificate
- Check certificate chain is complete

### Existing Connections

!!! info "Connection Behavior"
    After `reloadssl`:

    - New connections use new certificates
    - Existing connections continue with old certificates
    - Full rotation requires client reconnection

---

## Best Practices

!!! tip "Certificate Rotation"
    1. **Test in staging first** - Verify certificates work
    2. **Update truststore before keystore** - Prevent connection failures
    3. **One node at a time** - Rolling update approach
    4. **Monitor after reload** - Check for SSL errors
    5. **Keep backups** - Save old certificates until verified
    6. **Document expiration** - Track when to rotate next

---

## Automation Example

```bash
#!/bin/bash
# check_cert_expiry.sh - Alert on expiring certificates

DAYS_WARNING=30
KEYSTORE="/etc/cassandra/conf/keystore.jks"

expiry=$(keytool -list -v -keystore $KEYSTORE -storepass changeit 2>/dev/null | \
    grep "Valid from" | head -1 | sed 's/.*until: //')

expiry_epoch=$(date -d "$expiry" +%s)
now_epoch=$(date +%s)
days_left=$(( (expiry_epoch - now_epoch) / 86400 ))

if [ $days_left -lt $DAYS_WARNING ]; then
    echo "WARNING: Certificate expires in $days_left days"
    echo "Run certificate rotation procedure"
fi
```

---

## Related Configuration

| Setting | File | Description |
|---------|------|-------------|
| `server_encryption_options` | cassandra.yaml | Internode SSL |
| `client_encryption_options` | cassandra.yaml | Client SSL |
| `native_transport_port_ssl` | cassandra.yaml | SSL-only CQL port |

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [info](info.md) | Node information including SSL status |
| [status](status.md) | Cluster status |
