---
title: "Cassandra Security Guide"
description: "Apache Cassandra security guide covering authentication, authorization, encryption, and audit logging."
meta:
  - name: keywords
    content: "Cassandra security, authentication, authorization, encryption, audit logging"
search:
  boost: 3
---

# Cassandra Security Guide

A fresh Cassandra install has no security. Anyone who can reach port 9042 can read and write any data. There is no authentication, no authorization, no encryption. This is convenient for development but dangerous for anything else.

Cassandra has the expected security features—password, role-based access control, TLS encryption for client and internode traffic, audit logging—but they must be enabled. Each feature requires configuration changes and, for some, a rolling restart.

This guide covers enabling authentication, setting up roles and permissions, configuring encryption, and turning on audit logging.

## Security Overview

### Security Layers

| Layer | Scope |
|-------|-------|
| Application | Input validation, credential management, audit logging |
| Cassandra | Authentication, authorization, encryption |
| Network | Firewalls, VPNs, network isolation |
| Infrastructure | OS hardening, access controls, patching |

### Security Components

| Component | Purpose | Default State |
|-----------|---------|---------------|
| Authentication | Verify identity | Disabled |
| Authorization | Control access | Disabled |
| Client Encryption | Encrypt client traffic | Disabled |
| Internode Encryption | Encrypt cluster traffic | Disabled |
| Audit Logging | Track operations | Disabled |

---

---

## Authentication

### Enabling Authentication

```yaml
# cassandra.yaml

# Enable password authentication
authenticator: PasswordAuthenticator

# Alternative authenticators:
# authenticator: AllowAllAuthenticator  # No authentication (default)
# authenticator: com.example.LdapAuthenticator  # Custom LDAP
```

### Default Superuser

After enabling authentication, use the default superuser:

```sql
-- Default credentials (CHANGE IMMEDIATELY)
-- Username: cassandra
-- Password: cassandra

cqlsh -u cassandra -p cassandra

-- Create new superuser
CREATE ROLE admin WITH PASSWORD = 'strong_password_here'
    AND SUPERUSER = true
    AND LOGIN = true;

-- Disable default superuser
ALTER ROLE cassandra WITH SUPERUSER = false AND LOGIN = false;
```

### Creating Users

```sql
-- Create application user
CREATE ROLE app_user WITH PASSWORD = 'app_password'
    AND LOGIN = true;

-- Create read-only user
CREATE ROLE readonly_user WITH PASSWORD = 'readonly_pass'
    AND LOGIN = true;

-- Create user with role inheritance
CREATE ROLE analyst WITH LOGIN = true AND PASSWORD = 'analyst_pass';
GRANT readonly_role TO analyst;

-- List all roles
LIST ROLES;
```

### Authentication Cache

```yaml
# cassandra.yaml
credentials_validity_in_ms: 2000
credentials_update_interval_in_ms: 2000
credentials_cache_max_entries: 1000
```

---

## Authorization

### Enabling Authorization

```yaml
# cassandra.yaml

# Enable role-based authorization
authorizer: CassandraAuthorizer

# Role management
role_manager: CassandraRoleManager
```

### Permission Types

| Permission | Applies To | Description |
|------------|------------|-------------|
| `ALL` | All | All permissions |
| `ALTER` | Keyspace, Table, Function | Modify schema |
| `AUTHORIZE` | All | Grant/revoke permissions |
| `CREATE` | Keyspace, Table, Function, Role | Create objects |
| `DESCRIBE` | All | DESCRIBE operations |
| `DROP` | Keyspace, Table, Function, Role | Delete objects |
| `EXECUTE` | Function | Execute functions |
| `MODIFY` | Keyspace, Table | INSERT, UPDATE, DELETE |
| `SELECT` | Keyspace, Table, MBean | Read data |

### Granting Permissions

```sql
-- Grant full access to keyspace
GRANT ALL PERMISSIONS ON KEYSPACE my_keyspace TO app_user;

-- Grant read-only access
GRANT SELECT ON KEYSPACE my_keyspace TO readonly_user;

-- Grant access to specific table
GRANT SELECT, MODIFY ON TABLE my_keyspace.users TO app_user;

-- Grant permission to create keyspaces
GRANT CREATE ON ALL KEYSPACES TO admin_user;

-- List permissions
LIST ALL PERMISSIONS OF app_user;
LIST ALL PERMISSIONS ON KEYSPACE my_keyspace;
```

### Role Hierarchy

```sql
-- Create role hierarchy
CREATE ROLE base_role;
CREATE ROLE extended_role;

-- Grant permissions to base role
GRANT SELECT ON KEYSPACE analytics TO base_role;

-- Grant additional permissions to extended role
GRANT MODIFY ON KEYSPACE analytics TO extended_role;

-- Extended role inherits from base
GRANT base_role TO extended_role;

-- Users can be assigned roles
GRANT extended_role TO analyst_user;
```

### Resource Permissions

```sql
-- All keyspaces
GRANT CREATE ON ALL KEYSPACES TO developer;

-- Specific keyspace
GRANT ALL ON KEYSPACE production TO admin;

-- All tables in keyspace
GRANT SELECT ON ALL TABLES IN KEYSPACE analytics TO analyst;

-- Specific table
GRANT SELECT, MODIFY ON TABLE production.orders TO app_user;

-- Functions
GRANT EXECUTE ON FUNCTION my_keyspace.my_function(int, text) TO app_user;
GRANT EXECUTE ON ALL FUNCTIONS IN KEYSPACE my_keyspace TO app_user;

-- JMX MBeans (for management)
GRANT SELECT ON MBEAN 'org.apache.cassandra.db:*' TO monitoring_user;
```

### Revoking Permissions

```sql
-- Revoke specific permission
REVOKE MODIFY ON KEYSPACE my_keyspace FROM app_user;

-- Revoke all permissions
REVOKE ALL PERMISSIONS ON KEYSPACE my_keyspace FROM app_user;

-- Remove role assignment
REVOKE admin_role FROM user;
```

---

## Client-to-Node Encryption

### Generate Certificates

```bash
#!/bin/bash
# generate_certs.sh

# Create CA key and certificate
openssl genrsa -out ca-key.pem 4096
openssl req -x509 -new -nodes -key ca-key.pem -days 3650 \
    -out ca-cert.pem -subj "/CN=CassandraCA"

# For each node, create key and certificate
for NODE in node1 node2 node3; do
    # Generate private key
    openssl genrsa -out ${NODE}-key.pem 4096

    # Generate certificate signing request
    openssl req -new -key ${NODE}-key.pem -out ${NODE}.csr \
        -subj "/CN=${NODE}"

    # Sign certificate with CA
    openssl x509 -req -in ${NODE}.csr -CA ca-cert.pem \
        -CAkey ca-key.pem -CAcreateserial -out ${NODE}-cert.pem -days 365

    # Create keystore (PKCS12)
    openssl pkcs12 -export -in ${NODE}-cert.pem -inkey ${NODE}-key.pem \
        -out ${NODE}-keystore.p12 -name ${NODE} -password pass:keystorepass

    # Convert to JKS (if needed)
    keytool -importkeystore -srckeystore ${NODE}-keystore.p12 \
        -srcstoretype PKCS12 -srcstorepass keystorepass \
        -destkeystore ${NODE}-keystore.jks -deststorepass keystorepass
done

# Create truststore with CA certificate
keytool -import -file ca-cert.pem -keystore truststore.jks \
    -storepass truststorepass -noprompt -alias ca
```

### Configure Client Encryption

```yaml
# cassandra.yaml

client_encryption_options:
    # Enable encryption
    enabled: true

    # Optional: Allow unencrypted connections
    optional: false

    # Keystore containing server certificate
    keystore: /etc/cassandra/certs/node1-keystore.jks
    keystore_password: keystorepass

    # Truststore for client certificate validation
    # Required if require_client_auth is true
    truststore: /etc/cassandra/certs/truststore.jks
    truststore_password: truststorepass

    # Require client certificates (mutual TLS)
    require_client_auth: false

    # TLS protocol versions
    protocol: TLS
    accepted_protocols:
      - TLSv1.2
      - TLSv1.3

    # Cipher suites (strong ciphers only)
    cipher_suites:
      - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
      - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
      - TLS_AES_256_GCM_SHA384
      - TLS_AES_128_GCM_SHA256
```

### Client Connection with SSL

```bash
# cqlsh with SSL
cqlsh --ssl node1.example.com

# With explicit certificate
cqlsh --ssl --ssl-certfile=/path/to/ca-cert.pem node1.example.com

# cqlshrc configuration
# ~/.cassandra/cqlshrc
[ssl]
certfile = /path/to/ca-cert.pem
validate = true
userkey = /path/to/client-key.pem
usercert = /path/to/client-cert.pem
```

```java
// Java driver with SSL
SSLContext sslContext = SSLContext.getInstance("TLS");
TrustManagerFactory tmf = TrustManagerFactory.getInstance("SunX509");
KeyStore ts = KeyStore.getInstance("JKS");
ts.load(new FileInputStream("/path/to/truststore.jks"), "truststorepass".toCharArray());
tmf.init(ts);
sslContext.init(null, tmf.getTrustManagers(), null);

CqlSession session = CqlSession.builder()
    .addContactPoint(new InetSocketAddress("node1.example.com", 9042))
    .withSslContext(sslContext)
    .build();
```

---

## Internode Encryption

### Configure Node-to-Node Encryption

```yaml
# cassandra.yaml

server_encryption_options:
    # Encryption mode:
    # none: No encryption
    # dc: Encrypt only cross-datacenter traffic
    # rack: Encrypt only cross-rack traffic
    # all: Encrypt all internode traffic
    internode_encryption: all

    # Keystore with node certificate
    keystore: /etc/cassandra/certs/node1-keystore.jks
    keystore_password: keystorepass

    # Truststore with CA certificate
    truststore: /etc/cassandra/certs/truststore.jks
    truststore_password: truststorepass

    # Require peer certificates
    require_client_auth: true

    # TLS settings
    protocol: TLS
    accepted_protocols:
      - TLSv1.2
      - TLSv1.3

    cipher_suites:
      - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
      - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256

    # Enable for legacy SSL port (optional)
    enable_legacy_ssl_storage_port: false
```

### Encryption Modes

| Mode | Same Rack | Cross-Rack | Cross-DC |
|------|-----------|------------|----------|
| `none` | Plain | Plain | Plain |
| `dc` | Plain | Plain | Encrypted |
| `rack` | Plain | Encrypted | Encrypted |
| `all` | Encrypted | Encrypted | Encrypted |

---

## Network Security

### Firewall Rules

```bash
# Required ports for Cassandra

# Client CQL port
iptables -A INPUT -p tcp --dport 9042 -s 10.0.0.0/8 -j ACCEPT

# Internode communication
iptables -A INPUT -p tcp --dport 7000 -s 10.0.0.0/8 -j ACCEPT

# SSL internode (if legacy enabled)
iptables -A INPUT -p tcp --dport 7001 -s 10.0.0.0/8 -j ACCEPT

# JMX (restrict to management network)
iptables -A INPUT -p tcp --dport 7199 -s 10.0.1.0/24 -j ACCEPT

# Drop all other Cassandra ports
iptables -A INPUT -p tcp --dport 9042 -j DROP
iptables -A INPUT -p tcp --dport 7000 -j DROP
iptables -A INPUT -p tcp --dport 7001 -j DROP
iptables -A INPUT -p tcp --dport 7199 -j DROP
```

### Binding Interfaces

```yaml
# cassandra.yaml

# Listen only on specific interface
listen_address: 10.0.0.1

# Or listen on all interfaces
# listen_address: 0.0.0.0
# listen_interface: eth0

# RPC (client) address
rpc_address: 10.0.0.1

# Broadcast addresses (for NAT/cloud)
broadcast_address: 10.0.0.1
broadcast_rpc_address: 10.0.0.1
```

### JMX Security

```yaml
# cassandra-env.sh

# Enable JMX authentication
JVM_OPTS="$JVM_OPTS -Dcom.sun.management.jmxremote.authenticate=true"

# JMX access file
JVM_OPTS="$JVM_OPTS -Dcom.sun.management.jmxremote.password.file=/etc/cassandra/jmxremote.password"
JVM_OPTS="$JVM_OPTS -Dcom.sun.management.jmxremote.access.file=/etc/cassandra/jmxremote.access"

# Enable JMX SSL
JVM_OPTS="$JVM_OPTS -Dcom.sun.management.jmxremote.ssl=true"
JVM_OPTS="$JVM_OPTS -Dcom.sun.management.jmxremote.registry.ssl=true"
JVM_OPTS="$JVM_OPTS -Djavax.net.ssl.keyStore=/etc/cassandra/certs/node1-keystore.jks"
JVM_OPTS="$JVM_OPTS -Djavax.net.ssl.keyStorePassword=keystorepass"
```

```bash
# /etc/cassandra/jmxremote.access
admin readwrite
monitor readonly

# /etc/cassandra/jmxremote.password (chmod 400)
admin admin_password
monitor monitor_password
```

---

## Audit Logging (Cassandra 4.0+)

### Enable Audit Logging

```yaml
# cassandra.yaml

audit_logging_options:
    enabled: true

    # Logger implementation
    logger:
      - class_name: BinAuditLogger

    # Audit categories
    included_categories: QUERY, DML, DDL, AUTH, ERROR

    # Excluded categories
    # excluded_categories:

    # Include specific keyspaces (empty = all)
    included_keyspaces:
      - production
      - sensitive_data

    # Exclude system keyspaces
    excluded_keyspaces:
      - system
      - system_schema
      - system_auth
      - system_distributed

    # Include specific users (empty = all)
    # included_users:

    # Exclude service accounts
    excluded_users:
      - cassandra
      - monitoring
```

### Audit Categories

| Category | Description |
|----------|-------------|
| `QUERY` | SELECT statements |
| `DML` | INSERT, UPDATE, DELETE |
| `DDL` | CREATE, ALTER, DROP |
| `DCL` | GRANT, REVOKE |
| `AUTH` | Login attempts |
| `ADMIN` | Administrative operations |
| `ERROR` | Failed operations |
| `PREPARE` | Prepared statements |

### View Audit Logs

```bash
# Binary logs require auditlogviewer
auditlogviewer /var/log/cassandra/audit/

# Or configure file-based logger
# class_name: FileAuditLogger
# parameters:
#   log_dir: /var/log/cassandra/audit
```

---

## Security Best Practices

### Production Checklist

**Authentication & Authorization**:
- [ ] Enable PasswordAuthenticator
- [ ] Enable CassandraAuthorizer
- [ ] Create dedicated superuser
- [ ] Disable default cassandra user
- [ ] Create application-specific roles
- [ ] Apply least-privilege permissions
- [ ] Enable password complexity requirements

**Encryption**:
- [ ] Enable client-to-node encryption
- [ ] Enable internode encryption
- [ ] Use TLS 1.2 or higher
- [ ] Use strong cipher suites
- [ ] Implement certificate rotation plan
- [ ] Use mutual TLS where appropriate

**Network**:
- [ ] Restrict access with firewalls
- [ ] Bind to specific interfaces
- [ ] Secure JMX access
- [ ] Use VPN for cross-DC traffic
- [ ] Disable unused ports

**Monitoring & Audit**:
- [ ] Enable audit logging
- [ ] Monitor authentication failures
- [ ] Alert on permission changes
- [ ] Regular security reviews

### Common Mistakes

| Mistake | Risk | Solution |
|---------|------|----------|
| Default cassandra user | Full access for attackers | Disable after creating new superuser |
| No encryption | Data interception | Enable TLS for all connections |
| GRANT ALL to apps | Over-privileged access | Apply least-privilege |
| JMX open to network | Remote management access | Restrict with firewall + auth |
| Weak passwords | Credential attacks | Enforce complexity policies |
| No audit logging | No visibility into access | Enable audit logging |

---

## Next Steps

- **[Configuration Reference](../operations/configuration/index.md)** - Cassandra configuration
