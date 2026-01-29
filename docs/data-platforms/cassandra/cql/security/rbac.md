---
title: "Cassandra CQL Role-Based Access Control"
description: "Cassandra CQL role-based access control: CREATE ROLE, GRANT, REVOKE, and permission management."
meta:
  - name: keywords
    content: "CQL RBAC, CREATE ROLE, GRANT, REVOKE, Cassandra permissions, roles"
---

# Role-Based Access Control

Role-Based Access Control (RBAC) manages authentication and authorization through roles and permissions.

---

## Behavioral Guarantees

### What RBAC Operations Guarantee

- CREATE ROLE creates a role definition stored in `system_auth.roles`
- GRANT permission immediately takes effect for new operations
- REVOKE permission immediately takes effect for new operations
- Role inheritance is resolved at authorization time (transitive permissions)
- DROP ROLE removes the role and cascades to revoke all grants
- Superuser roles bypass all permission checks

### What RBAC Operations Do NOT Guarantee

!!! warning "Undefined Behavior"
    The following behaviors are undefined and must not be relied upon:

    - **Immediate enforcement across all nodes**: Permission changes propagate asynchronously; brief windows of inconsistent enforcement may occur
    - **Existing connection state**: Permission changes may not affect already-authenticated connections immediately
    - **Cache invalidation timing**: Permission cache (`roles_validity_in_ms`) may delay enforcement
    - **Concurrent modification safety**: Simultaneous role modifications may produce unexpected results
    - **Recovery of dropped roles**: Dropped roles and their permissions are not recoverable

### Permission Enforcement Contract

| Operation | Check Location | Caching |
|-----------|----------------|---------|
| Authentication | Any node | `credentials_validity_in_ms` |
| Authorization | Coordinator | `roles_validity_in_ms` |
| Permission resolution | Coordinator | `permissions_validity_in_ms` |

### Role Hierarchy Contract

| Scenario | Permission Resolution |
|----------|----------------------|
| Direct grant | Permission applies |
| Inherited via GRANT role | Permission applies (transitive) |
| Multiple inheritance paths | Permission applies if any path grants it |
| Revoked from parent | Permission revoked unless granted via another path |

### Cache Configuration

```yaml
# cassandra.yaml
roles_validity_in_ms: 2000      # Role information cache
permissions_validity_in_ms: 2000 # Permission cache
credentials_validity_in_ms: 2000 # Authentication cache
```

### Failure Semantics

| Failure Mode | Outcome | Client Action |
|--------------|---------|---------------|
| `UnauthorizedException` | Operation denied | Request appropriate permissions |
| `InvalidRequestException` | Invalid role or permission | Fix request syntax |
| Role not found | Operation fails | Create role or fix name |
| Circular grant attempt | Operation rejected | Redesign role hierarchy |

### Version-Specific Behavior

| Version | Behavior |
|---------|----------|
| 2.2+ | RBAC introduced (CASSANDRA-7653), replaces per-user model |
| 3.0+ | Network authorization, improved role management |
| 5.0+ | Data masking permissions (UNMASK, SELECT_MASKED) |
| 5.0+ | Enhanced CIDR-based authorization |

---

## History and Development

### Background

Prior to Cassandra 2.2, authentication and authorization operated on a per-user model. Administrators created users with `CREATE USER`, granted permissions directly to individual users, and had no mechanism for grouping permissions or creating hierarchical access structures.


### Design Goals

The [CASSANDRA-7653](https://issues.apache.org/jira/browse/CASSANDRA-7653) proposal established several requirements:

1. **Role Unification** - A single "role" concept replaces the separate notions of users and groups
2. **Role Inheritance** - Roles can be granted to other roles, enabling hierarchical permission structures
3. **Backward Compatibility** - Existing `CREATE USER` and `ALTER USER` syntax continues to function
4. **Centralized Management** - Permissions defined once on a role apply to all members

### Implementation Details

The RBAC implementation introduced:

| Component | Description |
|-----------|-------------|
| `IRoleManager` | New pluggable interface for role management |
| `CassandraRoleManager` | Default implementation storing roles in `system_auth` |
| `system_auth.roles` | Replaces `system_auth.users` for role definitions |
| `system_auth.role_members` | Tracks role-to-role grants |
| `system_auth.role_permissions` | Stores permission grants |

### Migration from Users to Roles

When upgrading from pre-2.2 versions:

- Existing users are automatically converted to roles with `LOGIN = true`
- `CREATE USER` statements internally execute `CREATE ROLE ... WITH LOGIN = true`
- Permissions granted to users remain intact on the converted roles

---

## Concepts

### Roles

Cassandra uses roles for both authentication (users) and authorization (permission groups):

| Role Type | LOGIN | Purpose |
|-----------|-------|---------|
| User account | `true` | Authenticates to the cluster |
| Permission group | `false` | Groups permissions for assignment |

### Permissions

Permissions control what actions a role can perform:

| Permission | Description | Applicable Resources |
|------------|-------------|---------------------|
| `ALL` | All applicable permissions | Any |
| `ALTER` | Modify schema | Keyspace, Table, Role |
| `AUTHORIZE` | Grant/revoke permissions | Any |
| `CREATE` | Create objects | Keyspace, Table, Function, Role |
| `DESCRIBE` | View role details | Role |
| `DROP` | Delete objects | Keyspace, Table, Function, Role |
| `EXECUTE` | Execute functions | Function |
| `MODIFY` | INSERT, UPDATE, DELETE | Keyspace, Table |
| `SELECT` | Read data | Keyspace, Table |
| `UNMASK` | View unmasked data | Keyspace, Table |
| `SELECT_MASKED` | View masked data | Keyspace, Table |

### Resources

Permissions are granted on resources:

| Resource | Syntax |
|----------|--------|
| All keyspaces | `ALL KEYSPACES` |
| Keyspace | `KEYSPACE keyspace_name` |
| Table | `[keyspace_name.]table_name` |
| All functions | `ALL FUNCTIONS [IN KEYSPACE keyspace_name]` |
| Function | `FUNCTION [keyspace_name.]func_name(arg_types)` |
| All roles | `ALL ROLES` |
| Role | `ROLE role_name` |
| All MBeans | `ALL MBEANS` |
| MBean | `MBEAN mbean_name` / `MBEANS pattern` |

---

## CREATE ROLE

Create a role for authentication and/or authorization.

### Syntax

```cql
CREATE ROLE [ IF NOT EXISTS ] role_name
    [ WITH option [ AND option ... ] ]
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `PASSWORD` | string | - | Authentication password |
| `HASHED PASSWORD` | string | - | Pre-hashed password |
| `LOGIN` | boolean | `false` | Whether role can authenticate |
| `SUPERUSER` | boolean | `false` | Whether role has all permissions |
| `OPTIONS` | map | `{}` | Authentication plugin options |

### Examples

```sql
-- User account
CREATE ROLE app_service
    WITH PASSWORD = 'secret123'
    AND LOGIN = true;

-- Superuser
CREATE ROLE admin
    WITH PASSWORD = 'admin_secret'
    AND LOGIN = true
    AND SUPERUSER = true;

-- Permission group (no login)
CREATE ROLE read_only_access;

-- Idempotent creation
CREATE ROLE IF NOT EXISTS developer
    WITH PASSWORD = 'dev_pwd'
    AND LOGIN = true;

-- With hashed password (for migration)
CREATE ROLE migrated_user
    WITH HASHED PASSWORD = '$2a$10$...'
    AND LOGIN = true;
```

### Requirements

- `CREATE` permission on `ALL ROLES`, or superuser
- `PASSWORD` required when `LOGIN = true`

---

## ALTER ROLE

Modify role properties.

### Syntax

```cql
ALTER ROLE role_name
    WITH option [ AND option ... ]
```

Accepts same options as `CREATE ROLE`.

### Examples

```sql
-- Change password
ALTER ROLE app_service WITH PASSWORD = 'new_password';

-- Disable login (lock account)
ALTER ROLE compromised_user WITH LOGIN = false;

-- Grant superuser
ALTER ROLE senior_dba WITH SUPERUSER = true;

-- Revoke superuser
ALTER ROLE former_admin WITH SUPERUSER = false;
```

### Requirements

- `ALTER` permission on the role, or superuser
- Non-superusers can only change their own password
- Cannot demote the last superuser

---

## DROP ROLE

Remove a role.

### Syntax

```cql
DROP ROLE [ IF EXISTS ] role_name
```

### Examples

```sql
DROP ROLE former_employee;
DROP ROLE IF EXISTS temp_user;
```

### Requirements

- `DROP` permission on the role, or superuser
- Cannot drop the last superuser
- Active sessions continue but re-authentication fails

---

## GRANT (Permission)

Grant permissions on resources to a role.

### Syntax

```cql
GRANT permission ON resource TO role_name
```

### Examples

```sql
-- Read access to keyspace
GRANT SELECT ON KEYSPACE production TO analyst;

-- Read/write to table
GRANT SELECT ON orders TO app_service;
GRANT MODIFY ON orders TO app_service;

-- Full access to keyspace
GRANT ALL PERMISSIONS ON KEYSPACE dev TO developer;

-- Schema management (no data access)
GRANT CREATE ON ALL KEYSPACES TO schema_admin;
GRANT ALTER ON ALL KEYSPACES TO schema_admin;
GRANT DROP ON ALL KEYSPACES TO schema_admin;

-- Function execution
GRANT EXECUTE ON FUNCTION my_ks.my_func(int) TO app_user;

-- Role management
GRANT ALTER ON ROLE app_user TO team_lead;
GRANT AUTHORIZE ON ALL ROLES TO security_admin;

-- MBean access (JMX)
GRANT SELECT ON ALL MBEANS TO monitoring;
GRANT EXECUTE ON MBEAN 'org.apache.cassandra.db:type=StorageService' TO ops;
```

### Requirements

- `AUTHORIZE` permission on the resource, or superuser

---

## GRANT (Role to Role)

Grant a role to another role, creating role membership.

### Syntax

```cql
GRANT role_name TO role_name
```

### Examples

```sql
-- Create permission groups
CREATE ROLE prod_read;
CREATE ROLE prod_write;
GRANT SELECT ON KEYSPACE production TO prod_read;
GRANT MODIFY ON KEYSPACE production TO prod_write;

-- Assign groups to user
CREATE ROLE app_service WITH PASSWORD = 'secret' AND LOGIN = true;
GRANT prod_read TO app_service;
GRANT prod_write TO app_service;

-- Hierarchical roles
CREATE ROLE junior_dev;
CREATE ROLE senior_dev;
GRANT junior_dev TO senior_dev;  -- senior inherits junior's permissions
```

### Requirements

- `AUTHORIZE` permission on both roles, or superuser
- Circular grants not allowed

---

## REVOKE (Permission)

Remove permissions from a role.

### Syntax

```cql
REVOKE permission ON resource FROM role_name
```

### Examples

```sql
-- Revoke specific permission
REVOKE MODIFY ON KEYSPACE production FROM app_service;

-- Revoke all permissions on resource
REVOKE ALL PERMISSIONS ON KEYSPACE sensitive FROM former_employee;

-- Revoke function execution
REVOKE EXECUTE ON FUNCTION my_ks.my_func(int) FROM app_user;
```

### Requirements

- `AUTHORIZE` permission on the resource, or superuser
- Revoking non-existent permission succeeds silently

---

## REVOKE (Role from Role)

Remove role membership.

### Syntax

```cql
REVOKE role_name FROM role_name
```

### Examples

```sql
-- Remove role membership
REVOKE prod_write FROM restricted_user;

-- Demote from senior to junior
REVOKE senior_dev FROM demoted_user;
```

---

## LIST ROLES

Display roles and their properties.

### Syntax

```cql
LIST ROLES [ OF role_name ] [ NORECURSIVE ]
```

### Options

| Option | Description |
|--------|-------------|
| `OF role_name` | Show roles granted to specified role |
| `NORECURSIVE` | Show only direct grants, not inherited |

### Examples

```sql
-- All roles
LIST ROLES;

-- Roles granted to user (including inherited)
LIST ROLES OF developer;

-- Direct grants only
LIST ROLES OF app_user NORECURSIVE;
```

### Output

```
 role       | super | login | options
------------+-------+-------+---------
 cassandra  | True  | True  | {}
 admin      | True  | True  | {}
 app_user   | False | True  | {}
 readers    | False | False | {}
```

---

## LIST PERMISSIONS

Display granted permissions.

### Syntax

```cql
LIST permission [ ON resource ] [ OF role_name ] [ NORECURSIVE ]
```

### Options

| Option | Description |
|--------|-------------|
| `permission` | Filter by permission type (or `ALL`) |
| `ON resource` | Filter by resource |
| `OF role_name` | Filter by role |
| `NORECURSIVE` | Show only direct grants |

### Examples

```sql
-- All permissions in cluster
LIST ALL PERMISSIONS;

-- Permissions for role (including inherited)
LIST ALL PERMISSIONS OF app_service;

-- Direct grants only
LIST ALL PERMISSIONS OF app_user NORECURSIVE;

-- Specific permission type
LIST SELECT ON KEYSPACE production;

-- Permissions on specific table
LIST ALL PERMISSIONS ON TABLE production.orders;
```

### Output

```
 role      | username   | resource              | permission
-----------+------------+-----------------------+------------
 app_user  | app_user   | <keyspace production> | SELECT
 app_user  | app_user   | <keyspace production> | MODIFY
```

---

## ADD IDENTITY

Associate a certificate identity with a role. Requires `MutualTlsAuthenticator`.

*Available in Cassandra 5.0+*

### Syntax

```cql
ADD IDENTITY 'identity_string' TO ROLE role_name
```

### Examples

```sql
-- SPIFFE identity
ADD IDENTITY 'spiffe://cluster.local/ns/default/sa/app-service' TO ROLE app_service;

-- Certificate subject
ADD IDENTITY 'CN=app-client,O=MyOrg' TO ROLE app_client;
```

See [Mutual TLS Authentication](../../security/authentication/index.md#mutual-tls-authentication) for configuration.

---

## DROP IDENTITY

Remove a certificate identity mapping.

*Available in Cassandra 5.0+*

### Syntax

```cql
DROP IDENTITY 'identity_string'
```

### Examples

```sql
DROP IDENTITY 'spiffe://cluster.local/ns/default/sa/app-service';
```

---

## System Tables

Role and permission data is stored in `system_auth`:

| Table | Contents |
|-------|----------|
| `roles` | Role definitions |
| `role_permissions` | Permission grants |
| `role_members` | Role-to-role grants |
| `identity_to_role` | Certificate identity mappings (5.0+) |

```sql
-- View all roles
SELECT * FROM system_auth.roles;

-- View permissions for a role
SELECT * FROM system_auth.role_permissions
WHERE role = 'app_service';

-- View role memberships
SELECT * FROM system_auth.role_members;
```

---

## References

### JIRA Tickets

| Ticket | Description |
|--------|-------------|
| [CASSANDRA-547](https://issues.apache.org/jira/browse/CASSANDRA-547) | Original pluggable authentication framework (0.6) |
| [CASSANDRA-7653](https://issues.apache.org/jira/browse/CASSANDRA-7653) | Role-based access control implementation (2.2) |
| [CASSANDRA-8394](https://issues.apache.org/jira/browse/CASSANDRA-8394) | Cassandra 3.0 auth subsystem rework |
| [CASSANDRA-7557](https://issues.apache.org/jira/browse/CASSANDRA-7557) | UDF permissions |
| [CASSANDRA-8082](https://issues.apache.org/jira/browse/CASSANDRA-8082) | Fine-grained permissions |
| [CASSANDRA-10091](https://issues.apache.org/jira/browse/CASSANDRA-10091) | JMX authentication/authorization |
| [CASSANDRA-18554](https://issues.apache.org/jira/browse/CASSANDRA-18554) | mTLS authenticators (5.0) |

### CEPs

| CEP | Description |
|-----|-------------|
| [CEP-16](https://cwiki.apache.org/confluence/display/CASSANDRA/CEP-16%3A+Auth+Plugin+Support+for+CQLSH) | CQLSH authentication plugin support |
| [CEP-34](https://cwiki.apache.org/confluence/display/CASSANDRA/CEP-34%3A+mTLS+based+client+and+internode+authenticators) | mTLS client and internode authenticators |
| [CEP-50](https://cwiki.apache.org/confluence/display/CASSANDRA/CEP-50:+Authentication+Negotiation) | Authentication negotiation (in progress) |

---

## Related Documentation

| Topic | Description |
|-------|-------------|
| [CQL Security Overview](index.md) | Security features summary |
| [Dynamic Data Masking](dynamic-data-masking.md) | Column-level data masking |
| [Authentication](../../security/authentication/index.md) | Authenticator configuration |
| [Authorization](../../security/authorization/index.md) | Authorizer configuration |