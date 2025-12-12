---
description: "CQL security commands for authentication, authorization, and role management in Cassandra."
meta:
  - name: keywords
    content: "CQL security, CREATE ROLE, GRANT, authentication, authorization, Cassandra"
---

# Security Commands

Security commands manage authentication and authorization in Cassandra through roles and permissions. Roles can represent users (with login capability) or permission groups (for organizing access control).

---

## Security Architecture

### Authentication and Authorization

Cassandra security consists of two components:

| Component | Purpose | Configuration |
|-----------|---------|---------------|
| **Authentication** | Verify identity (who are you?) | `authenticator` in cassandra.yaml |
| **Authorization** | Verify access rights (what can you do?) | `authorizer` in cassandra.yaml |

### Enabling Security

Security must be enabled in `cassandra.yaml`:

```yaml
# Authentication (default: AllowAllAuthenticator = no auth)
authenticator: PasswordAuthenticator

# Authorization (default: AllowAllAuthorizer = no permissions)
authorizer: CassandraAuthorizer

# Role management
role_manager: CassandraRoleManager
```

!!! danger "Default Credentials"
    When enabling authentication, Cassandra creates a default superuser:

    - Username: `cassandra`
    - Password: `cassandra`

    **Immediately change this password or create a new superuser and disable the default.**

### Role Hierarchy

Roles can be granted to other roles, creating hierarchical permission structures:

```
                    superuser
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
       admin        developer      analyst
          │             │             │
          │        ┌────┴────┐        │
          │        ▼         ▼        │
          │    dev_read   dev_write   │
          │        │         │        │
          └────────┴─────────┴────────┘
                       │
                       ▼
                 app_service_account
```

Permissions are inherited through role grants.

---

## CREATE ROLE

Create a role for authentication and/or authorization.

### Synopsis

```cqlsyntax
CREATE ROLE [ IF NOT EXISTS ] *role_name*
    [ WITH *role_option* [ AND *role_option* ... ] ]
```

**role_option**:

```cqlsyntax
PASSWORD = '*password*'
| LOGIN = { true | false }
| SUPERUSER = { true | false }
| OPTIONS = { *option_map* }
| HASHED PASSWORD = '*hashed_value*'
```

### Description

`CREATE ROLE` defines a new role for authentication (if `LOGIN = true`) and/or authorization (permission grouping). Roles can be granted permissions and can be granted to other roles.

### Parameters

#### *role_name*

Identifier for the role. Role names are case-sensitive when quoted.

```sql
-- Case-insensitive (stored lowercase)
CREATE ROLE app_user ...

-- Case-sensitive
CREATE ROLE "AppUser" ...
```

#### IF NOT EXISTS

Prevent error if role already exists.

#### PASSWORD

Password for authentication. Required if `LOGIN = true`.

```sql
CREATE ROLE app_user
    WITH PASSWORD = 'secure_password123'
    AND LOGIN = true;
```

!!! warning "Password Security"
    - Passwords are stored hashed (bcrypt by default)
    - Use strong passwords (12+ characters, mixed case, numbers, symbols)
    - Avoid passwords in CQL scripts (use secure credential management)
    - Passwords in CQL are visible in logs unless logging is configured to mask them

#### LOGIN

Whether the role can authenticate to the cluster:

| Value | Purpose |
|-------|---------|
| `true` | Role can log in (user account) |
| `false` (default) | Role cannot log in (permission group) |

```sql
-- User account
CREATE ROLE developer WITH PASSWORD = 'secret' AND LOGIN = true;

-- Permission group (no login)
CREATE ROLE read_only;
```

#### SUPERUSER

Whether the role has superuser privileges:

| Value | Capabilities |
|-------|--------------|
| `true` | All permissions on all resources, can manage other superusers |
| `false` (default) | Only explicitly granted permissions |

```sql
CREATE ROLE dba
    WITH PASSWORD = 'admin_pwd'
    AND LOGIN = true
    AND SUPERUSER = true;
```

!!! danger "Superuser Security"
    - Superusers bypass all permission checks
    - Limit superuser accounts to essential operations
    - Use regular roles for application access
    - Audit superuser usage

#### OPTIONS

Authentication plugin-specific options:

```sql
CREATE ROLE ldap_user
    WITH OPTIONS = {'ldap_dn': 'cn=user,dc=example,dc=com'};
```

#### HASHED PASSWORD

Pre-hashed password value (for migration or automation):

```sql
CREATE ROLE migrated_user
    WITH HASHED PASSWORD = '$2a$10$abc...'
    AND LOGIN = true;
```

### Examples

#### Application User

```sql
CREATE ROLE app_service
    WITH PASSWORD = 'app_secret_123'
    AND LOGIN = true;
```

#### Administrator

```sql
CREATE ROLE admin
    WITH PASSWORD = 'admin_secret'
    AND LOGIN = true
    AND SUPERUSER = true;
```

#### Permission Groups

```sql
-- Read-only access group
CREATE ROLE readers;

-- Read-write access group
CREATE ROLE writers;

-- Full access group
CREATE ROLE admins;
```

#### Developer with Group Membership

```sql
-- Create permission groups
CREATE ROLE dev_read;
CREATE ROLE dev_write;

-- Create developer role
CREATE ROLE developer
    WITH PASSWORD = 'dev_pwd'
    AND LOGIN = true;

-- Grant groups to developer (separate GRANT statements)
GRANT dev_read TO developer;
GRANT dev_write TO developer;
```

### Restrictions

!!! warning "Restrictions"
    - Role names must be unique
    - Cannot create roles with reserved names (`cassandra` if default superuser)
    - Requires CREATE permission on ALL ROLES (or superuser)
    - Password required if LOGIN = true

### Notes

- Roles are stored in `system_auth.roles`
- Role creation propagates via gossip
- New roles have no permissions by default
- Use `DESCRIBE ROLE` to view role details

---

## ALTER ROLE

Modify role properties.

### Synopsis

```cqlsyntax
ALTER ROLE *role_name*
    WITH *role_option* [ AND *role_option* ... ]
```

### Description

`ALTER ROLE` changes role properties such as password, login capability, or superuser status.

### Parameters

Same options as `CREATE ROLE`:

- `PASSWORD` - New password
- `LOGIN` - Enable/disable login
- `SUPERUSER` - Grant/revoke superuser
- `OPTIONS` - Plugin-specific options

### Examples

#### Change Password

```sql
ALTER ROLE app_user WITH PASSWORD = 'new_password_456';
```

#### Disable Login

```sql
ALTER ROLE compromised_account WITH LOGIN = false;
```

#### Promote to Superuser

```sql
ALTER ROLE senior_dba WITH SUPERUSER = true;
```

#### Demote from Superuser

```sql
ALTER ROLE former_admin WITH SUPERUSER = false;
```

### Restrictions

!!! warning "Restrictions"
    - Cannot alter non-existent roles
    - Non-superusers can only alter their own password
    - Cannot demote the last superuser
    - Requires ALTER permission on the role (or superuser)

---

## DROP ROLE

Remove a role.

### Synopsis

```cqlsyntax
DROP ROLE [ IF EXISTS ] *role_name*
```

### Description

`DROP ROLE` removes a role and revokes all its permissions. Roles granted to other roles are also revoked.

### Examples

```sql
DROP ROLE former_employee;
DROP ROLE IF EXISTS temp_user;
```

### Restrictions

!!! danger "Restrictions"
    - Cannot drop role with active sessions (sessions continue but re-auth fails)
    - Cannot drop the last superuser
    - Requires DROP permission on the role (or superuser)

---

## GRANT

Grant permissions or roles.

### Synopsis

**Grant permission:**

```cqlsyntax
GRANT *permission* ON *resource* TO *role_name*
```

**Grant role to role:**

```cqlsyntax
GRANT *role_name* TO *role_name*
```

**permission**:

```cqlsyntax
ALL [ PERMISSIONS ]
| ALTER
| AUTHORIZE
| CREATE
| DESCRIBE
| DROP
| EXECUTE
| MODIFY
| SELECT
| UNMASK
| SELECT_MASKED
```

**resource**:

```cqlsyntax
ALL KEYSPACES
| KEYSPACE *keyspace_name*
| [ TABLE ] [ *keyspace_name*. ] *table_name*
| ALL FUNCTIONS [ IN KEYSPACE *keyspace_name* ]
| FUNCTION [ *keyspace_name*. ] *function_name* ( [ *arg_type* [, ... ] ] )
| ALL ROLES
| ROLE *role_name*
| ALL MBEANS
| MBEAN *mbean_name*
| MBEANS *mbean_pattern*
```

### Description

`GRANT` assigns permissions to roles or creates role membership relationships.

### Permission Types

| Permission | Applicable Resources | Allows |
|------------|---------------------|--------|
| `ALL` | Any | All applicable permissions |
| `ALTER` | Keyspace, Table, Role | Schema modification |
| `AUTHORIZE` | Any | Grant/revoke permissions |
| `CREATE` | Keyspace, Table, Function, Role | Create new objects |
| `DESCRIBE` | Role | View role details |
| `DROP` | Keyspace, Table, Function, Role | Delete objects |
| `EXECUTE` | Function | Execute functions |
| `MODIFY` | Keyspace, Table | INSERT, UPDATE, DELETE |
| `SELECT` | Keyspace, Table | Read data |
| `UNMASK` | Keyspace, Table | View unmasked data (dynamic data masking) |
| `SELECT_MASKED` | Keyspace, Table | View masked data |

### Resource Scopes

```sql
-- All keyspaces
GRANT SELECT ON ALL KEYSPACES TO analyst;

-- Specific keyspace (all tables)
GRANT SELECT ON KEYSPACE production TO app_reader;

-- Specific table
GRANT MODIFY ON production.orders TO order_service;

-- All functions
GRANT EXECUTE ON ALL FUNCTIONS TO developer;

-- Specific function
GRANT EXECUTE ON FUNCTION my_ks.my_func(INT) TO app_user;

-- Role management
GRANT ALTER ON ROLE app_user TO team_lead;
GRANT AUTHORIZE ON ALL ROLES TO security_admin;
```

### Examples

#### Read-Only Access

```sql
-- Read access to specific keyspace
GRANT SELECT ON KEYSPACE analytics TO analyst;
```

#### Application Service Account

```sql
-- Read/write to application tables
GRANT SELECT ON KEYSPACE app_data TO app_service;
GRANT MODIFY ON KEYSPACE app_data TO app_service;
```

#### Schema Administrator

```sql
-- Schema management without data access
GRANT CREATE ON KEYSPACE dev_ks TO schema_admin;
GRANT ALTER ON KEYSPACE dev_ks TO schema_admin;
GRANT DROP ON KEYSPACE dev_ks TO schema_admin;
```

#### Full Access to Keyspace

```sql
GRANT ALL PERMISSIONS ON KEYSPACE production TO admin;
```

#### Role Hierarchy

```sql
-- Create permission groups
CREATE ROLE prod_read;
CREATE ROLE prod_write;
CREATE ROLE prod_admin;

-- Grant permissions to groups
GRANT SELECT ON KEYSPACE production TO prod_read;
GRANT MODIFY ON KEYSPACE production TO prod_write;
GRANT ALL PERMISSIONS ON KEYSPACE production TO prod_admin;

-- Create roles with group membership
CREATE ROLE app_service WITH PASSWORD = 'secret' AND LOGIN = true;
GRANT prod_read TO app_service;
GRANT prod_write TO app_service;

CREATE ROLE dba WITH PASSWORD = 'secret' AND LOGIN = true;
GRANT prod_admin TO dba;
```

### Restrictions

!!! warning "Restrictions"
    - Requires AUTHORIZE permission on the resource
    - Cannot grant permissions on non-existent resources
    - Circular role grants not allowed
    - Superuser can grant any permission

---

## REVOKE

Remove permissions or role membership.

### Synopsis

**Revoke permission:**

```cqlsyntax
REVOKE *permission* ON *resource* FROM *role_name*
```

**Revoke role from role:**

```cqlsyntax
REVOKE *role_name* FROM *role_name*
```

### Description

`REVOKE` removes permissions from roles or removes role membership.

### Examples

#### Revoke Permission

```sql
REVOKE MODIFY ON KEYSPACE production FROM app_service;
```

#### Revoke All Permissions

```sql
REVOKE ALL PERMISSIONS ON KEYSPACE sensitive_data FROM former_employee;
```

#### Revoke Role Membership

```sql
REVOKE prod_write FROM restricted_user;
```

### Restrictions

!!! warning "Restrictions"
    - Requires AUTHORIZE permission on the resource
    - Revoking non-existent permission succeeds silently
    - Cannot revoke from non-existent roles (error)

---

## LIST PERMISSIONS

Display granted permissions.

### Synopsis

```cqlsyntax
LIST *permission* [ ON *resource* ] [ OF *role_name* ] [ NORECURSIVE ]
```

### Description

`LIST PERMISSIONS` displays permission grants matching specified criteria.

### Parameters

#### NORECURSIVE

Show only directly granted permissions, not inherited through role membership:

```sql
-- All permissions including inherited
LIST ALL PERMISSIONS OF app_user;

-- Only directly granted permissions
LIST ALL PERMISSIONS OF app_user NORECURSIVE;
```

### Examples

#### All Permissions

```sql
LIST ALL PERMISSIONS;
```

#### Permissions for Role

```sql
LIST ALL PERMISSIONS OF app_service;
```

#### Specific Permission Type

```sql
LIST SELECT ON KEYSPACE production;
```

#### Permissions on Resource

```sql
LIST ALL PERMISSIONS ON TABLE production.orders;
```

### Output Format

```
 role      | username   | resource              | permission
-----------+------------+-----------------------+------------
 app_user  | app_user   | <keyspace production> | SELECT
 app_user  | app_user   | <keyspace production> | MODIFY
```

---

## LIST ROLES

Display roles.

### Synopsis

```cqlsyntax
LIST ROLES [ OF *role_name* ] [ NORECURSIVE ]
```

### Description

`LIST ROLES` displays roles and their properties.

### Examples

#### All Roles

```sql
LIST ROLES;
```

#### Roles Granted to Role

```sql
LIST ROLES OF developer;
```

#### Direct Grants Only

```sql
LIST ROLES OF app_user NORECURSIVE;
```

### Output Format

```
 role       | super | login | options
------------+-------+-------+---------
 cassandra  | True  | True  | {}
 admin      | True  | True  | {}
 app_user   | False | True  | {}
 readers    | False | False | {}
```

---

## Best Practices

### Role Design

!!! tip "Design Guidelines"
    1. **Principle of least privilege** - Grant minimum required permissions
    2. **Use role hierarchy** - Create permission groups, assign to users
    3. **Separate concerns** - Different roles for different functions
    4. **Avoid direct table grants** - Use keyspace-level grants when possible
    5. **Regular audits** - Review permissions periodically

### Security Hardening

!!! warning "Production Security"
    1. **Change default superuser** - Create new admin, disable `cassandra` role
    2. **Use strong passwords** - Enforce complexity requirements
    3. **Limit superusers** - Minimize accounts with full access
    4. **Enable audit logging** - Track authentication and authorization events
    5. **Network security** - Use SSL/TLS for client connections

### Common Patterns

#### Application Service Account

```sql
-- Minimal permissions for application
CREATE ROLE app_service WITH PASSWORD = 'secret' AND LOGIN = true;
GRANT SELECT ON KEYSPACE app_data TO app_service;
GRANT MODIFY ON app_data.user_events TO app_service;
```

#### Read-Only Analytics Access

```sql
CREATE ROLE analyst WITH PASSWORD = 'secret' AND LOGIN = true;
GRANT SELECT ON KEYSPACE production TO analyst;
GRANT SELECT ON KEYSPACE analytics TO analyst;
```

#### Schema-Only Administrator

```sql
CREATE ROLE schema_admin WITH PASSWORD = 'secret' AND LOGIN = true;
GRANT CREATE ON ALL KEYSPACES TO schema_admin;
GRANT ALTER ON ALL KEYSPACES TO schema_admin;
-- No SELECT/MODIFY = no data access
```

---

## Related Documentation

- **[Dynamic Data Masking](dynamic-data-masking.md)** - Automatic data obfuscation for sensitive columns
- **[DDL Commands](../ddl/index.md)** - Schema management commands
- **[DML Commands](../dml/index.md)** - Data manipulation commands
