# Cassandra Authorization

Configure role-based access control (RBAC) for your Cassandra cluster.

## Enabling Authorization

```yaml
# cassandra.yaml
authorizer: CassandraAuthorizer
role_manager: CassandraRoleManager
```

## Permission Types

| Permission | Description |
|------------|-------------|
| `ALL` | All permissions |
| `ALTER` | Modify schema |
| `AUTHORIZE` | Grant/revoke permissions |
| `CREATE` | Create resources |
| `DESCRIBE` | Describe resources |
| `DROP` | Delete resources |
| `EXECUTE` | Execute functions |
| `MODIFY` | INSERT, UPDATE, DELETE |
| `SELECT` | Read data |

## Granting Permissions

```sql
-- Full access to keyspace
GRANT ALL PERMISSIONS ON KEYSPACE my_keyspace TO app_user;

-- Read-only access
GRANT SELECT ON KEYSPACE my_keyspace TO readonly_user;

-- Specific table access
GRANT SELECT, MODIFY ON TABLE my_keyspace.users TO app_user;

-- Create permission
GRANT CREATE ON ALL KEYSPACES TO developer;
```

## Revoking Permissions

```sql
-- Revoke specific permission
REVOKE MODIFY ON KEYSPACE my_keyspace FROM app_user;

-- Revoke all permissions
REVOKE ALL PERMISSIONS ON KEYSPACE my_keyspace FROM app_user;
```

## Listing Permissions

```sql
-- All permissions for role
LIST ALL PERMISSIONS OF app_user;

-- Permissions on resource
LIST ALL PERMISSIONS ON KEYSPACE my_keyspace;

-- All permissions
LIST ALL PERMISSIONS;
```

## Role Hierarchy

```sql
-- Create base role
CREATE ROLE base_readonly;
GRANT SELECT ON ALL KEYSPACES TO base_readonly;

-- Create extended role
CREATE ROLE analyst;
GRANT SELECT ON KEYSPACE analytics TO analyst;

-- Inherit permissions
GRANT base_readonly TO analyst;

-- Assign to user
GRANT analyst TO john;
```

## Best Practices

- **Least privilege**: Grant minimum required permissions
- **Use roles**: Create role hierarchy for manageability
- **Separate service accounts**: One per application
- **Audit regularly**: Review permissions periodically

---

## Next Steps

- **[Authentication](../authentication/index.md)** - User authentication
- **[Encryption](../encryption/index.md)** - Data encryption
- **[Security Overview](../index.md)** - Security guide
