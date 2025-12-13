---
description: "Cassandra authentication configuration. Password authenticator, LDAP integration, and custom providers."
meta:
  - name: keywords
    content: "Cassandra authentication, password authenticator, LDAP, login security"
---

# Cassandra Authentication

Configure authentication to control access to your Cassandra cluster.

## Enabling Authentication

```yaml
# cassandra.yaml
authenticator: PasswordAuthenticator
```

After enabling, restart all nodes in a rolling manner.

## Default Credentials

```
Username: cassandra
Password: cassandra
```

**Important**: Change immediately after enabling authentication.

## Creating Users

```sql
-- Connect with default credentials
cqlsh -u cassandra -p cassandra

-- Create new superuser
CREATE ROLE admin WITH PASSWORD = 'strong_password'
    AND SUPERUSER = true
    AND LOGIN = true;

-- Disable default superuser
ALTER ROLE cassandra WITH SUPERUSER = false AND LOGIN = false;

-- Create application user
CREATE ROLE app_user WITH PASSWORD = 'app_password'
    AND LOGIN = true;
```

## Role Management

```sql
-- List roles
LIST ROLES;

-- Create role without login
CREATE ROLE readonly_role;

-- Grant role to user
GRANT readonly_role TO app_user;

-- Revoke role
REVOKE readonly_role FROM app_user;

-- Drop role
DROP ROLE IF EXISTS old_role;
```

## Authentication Cache

```yaml
# cassandra.yaml
credentials_validity_in_ms: 2000
credentials_update_interval_in_ms: 2000
credentials_cache_max_entries: 1000
```

## Mutual TLS Authentication

!!! note "Cassandra 5.0+"
    MutualTlsAuthenticator is available in Apache Cassandra 5.0 and later.

MutualTlsAuthenticator performs certificate-based authentication for client connections by extracting identities from client certificates and verifying them against authorized identities in the `system_auth.identity_to_role` table.

### Prerequisites

Mutual TLS authentication requires client encryption with mandatory client certificate verification:

```yaml
# cassandra.yaml
client_encryption_options:
    enabled: true
    require_client_auth: true
    keystore: /path/to/keystore.jks
    keystore_password: keystorepass
    truststore: /path/to/truststore.jks
    truststore_password: truststorepass
```

### Configuration

```yaml
# cassandra.yaml
authenticator:
  class_name: org.apache.cassandra.auth.MutualTlsAuthenticator
  parameters:
    validator_class_name: org.apache.cassandra.auth.SpiffeCertificateValidator
```

The `validator_class_name` parameter specifies the certificate validator implementation. Cassandra includes `SpiffeCertificateValidator` for SPIFFE-based identity extraction.

### SPIFFE Certificate Validator

The `SpiffeCertificateValidator` extracts SPIFFE identities from the Subject Alternative Name (SAN) extension of client certificates. SPIFFE identities are URIs in the format `spiffe://trust-domain/path`.

The validator:

- Examines the SAN extension of the client certificate
- Searches for URI entries beginning with `spiffe://`
- Returns the SPIFFE URI as the client identity

### Identity Management

Identities extracted from certificates must be mapped to roles using the `ADD IDENTITY` statement:

```sql
-- Create role for the application
CREATE ROLE app_service WITH LOGIN = true;

-- Map certificate identity to role
ADD IDENTITY 'spiffe://testdomain.com/testIdentifier/testValue' TO ROLE 'app_service';

-- Use IF NOT EXISTS to avoid errors when identity already exists
ADD IDENTITY IF NOT EXISTS 'spiffe://testdomain.com/testIdentifier/testValue' TO ROLE 'app_service';

-- Grant permissions to the role
GRANT SELECT ON KEYSPACE myapp TO app_service;
```

To remove an identity mapping:

```sql
DROP IDENTITY 'spiffe://testdomain.com/testIdentifier/testValue';

-- Use IF EXISTS to avoid errors if identity does not exist
DROP IDENTITY IF EXISTS 'spiffe://testdomain.com/testIdentifier/testValue';
```

!!! note
    Only superusers or users with appropriate role management privileges can add or drop identities.

### Password Fallback Authenticator

For gradual migration from password-based to certificate-based authentication, use `MutualTlsWithPasswordFallbackAuthenticator`:

```yaml
# cassandra.yaml
authenticator:
  class_name: org.apache.cassandra.auth.MutualTlsWithPasswordFallbackAuthenticator
  parameters:
    validator_class_name: org.apache.cassandra.auth.SpiffeCertificateValidator
```

This authenticator accepts both certificate-based and username/password authentication, allowing clients to migrate incrementally.

### Custom Certificate Validators

Custom validators can be implemented by creating a class that implements the `MutualTlsCertificateValidator` interface:

```java
public interface MutualTlsCertificateValidator {
    void init(Map<String, String> parameters);
    String identity(Certificate[] certificateChain) throws CertificateException;
    boolean isValidCertificate(Certificate[] certificateChain);
}
```

## Client Configuration

### cqlsh

```bash
# Command line
cqlsh -u username -p password host

# Or use cqlshrc
# ~/.cassandra/cqlshrc
[authentication]
username = username
password = password
```

### Java Driver

```java
CqlSession session = CqlSession.builder()
    .addContactPoint(new InetSocketAddress("host", 9042))
    .withAuthCredentials("username", "password")
    .build();
```

### Python Driver

```python
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

auth = PlainTextAuthProvider('username', 'password')
cluster = Cluster(['host'], auth_provider=auth)
session = cluster.connect()
```

---

## Next Steps

- **[Authorization](../authorization/index.md)** - Permission management
- **[Encryption](../encryption/index.md)** - SSL/TLS setup
- **[Security Overview](../index.md)** - Security guide
