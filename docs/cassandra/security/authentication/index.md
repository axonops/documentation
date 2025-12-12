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
