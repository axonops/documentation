---
description: "Clear roles cache in Cassandra using nodetool invalidaterolescache command."
meta:
  - name: keywords
    content: "nodetool invalidaterolescache, roles cache, authorization, Cassandra security"
---

# nodetool invalidaterolescache

Invalidates the roles cache on the node.

---

## Synopsis

```bash
nodetool [connection_options] invalidaterolescache
```

---

## Description

`nodetool invalidaterolescache` clears all cached role information on the node. The roles cache stores role definitions and role hierarchy relationships from the `system_auth.roles` and `system_auth.role_members` tables, allowing Cassandra to resolve role memberships without querying the auth tables for every operation.

Role caching is essential for performance in environments with complex role hierarchies, where a single user might inherit permissions from multiple nested roles. After invalidation, subsequent operations trigger fresh role lookups from the system_auth tables.

!!! info "Authentication Required"
    The roles cache is only relevant when authentication and authorization are enabled. If running with `AllowAllAuthenticator` and `AllowAllAuthorizer`, this cache is not used.

---

## Examples

### Basic Usage

```bash
nodetool invalidaterolescache
```

### After Role Hierarchy Changes

```bash
# After modifying role memberships
cqlsh -e "GRANT admin_role TO power_user;"

# Invalidate to ensure changes take effect immediately
nodetool invalidaterolescache
```

### On Remote Node

```bash
nodetool -h 192.168.1.100 invalidaterolescache
```

---

## Roles Cache Overview

### What the Cache Stores

| Cached Data | Description |
|-------------|-------------|
| Role name | The role identifier |
| Role properties | SUPERUSER, LOGIN capabilities |
| Role membership | Parent roles (inherited roles) |
| Membership graph | Complete hierarchy for permission resolution |

### How It Improves Performance

```
Without Roles Cache:
  Authorization Check → Resolve role membership → Query role_members recursively → Aggregate permissions

With Roles Cache:
  Authorization Check → Lookup cached membership → Aggregate permissions
  (Avoids recursive auth table queries)
```

### Role Hierarchy Example

```
                    superadmin
                    /        \
              admin_role    dba_role
               /     \          \
         developer  analyst    operator
```

When checking permissions for `developer`, Cassandra must resolve that it inherits from `admin_role`, which inherits from `superadmin`. The roles cache stores this complete hierarchy.

---

## When to Use

### After Role Creation or Deletion

```bash
# Create new role
cqlsh -e "CREATE ROLE analytics_team WITH LOGIN = false;"

# Invalidate cache
nodetool invalidaterolescache
```

### After Role Hierarchy Changes

When role memberships are modified:

```bash
# Grant role membership
cqlsh -e "GRANT analytics_team TO data_scientist;"

# Revoke role membership
cqlsh -e "REVOKE admin_role FROM former_admin;"

# Ensure changes take effect immediately
nodetool invalidaterolescache
```

### After Role Property Changes

When role properties are modified:

```bash
# Change superuser status
cqlsh -e "ALTER ROLE operator WITH SUPERUSER = true;"

# Change login capability
cqlsh -e "ALTER ROLE service_account WITH LOGIN = true;"

# Invalidate to reflect changes
nodetool invalidaterolescache
```

### Security Incident Response

When immediate role changes are critical:

```bash
#!/bin/bash
# emergency_role_revoke.sh

USER="$1"
ROLE_TO_REVOKE="$2"

# Revoke the role
cqlsh -e "REVOKE $ROLE_TO_REVOKE FROM $USER;"

# Invalidate cache on all nodes immediately
for node in $(nodetool status | grep "^UN" | awk '{print $2}'); do
    nodetool -h $node invalidaterolescache
    nodetool -h $node invalidatepermissionscache
done

echo "Role $ROLE_TO_REVOKE revoked from $USER on all nodes."
```

### Troubleshooting Permission Issues

When users have unexpected permissions:

```bash
# Clear all auth caches to ensure fresh resolution
nodetool invalidaterolescache
nodetool invalidatepermissionscache
nodetool invalidatecredentialscache

# Verify permissions
cqlsh -e "LIST ALL PERMISSIONS OF problem_user;"
```

---

## Impact Assessment

### Immediate Effects

| Aspect | Impact |
|--------|--------|
| Cached role data | All cleared |
| Next operations | Require auth table lookups |
| Role resolution | Temporarily slower |
| Permission checks | May have slight latency increase |

### Recovery Timeline

| Phase | Duration | Cache State |
|-------|----------|-------------|
| Immediately after | 0 | Empty |
| Initial operations | Seconds | Roles being cached |
| Normal operations | Minutes | Cache populated for active roles |

!!! note "Low Impact Operation"
    Role cache invalidation typically has minimal performance impact since role lookups are relatively fast and the cache repopulates quickly with normal operations.

---

## Configuration

### Cache Settings

```yaml
# cassandra.yaml
roles_validity_in_ms: 2000            # How long entries are valid
roles_update_interval_in_ms: 1000     # Background refresh interval
roles_cache_max_entries: 1000         # Maximum cached entries
```

### Tuning Considerations

| Setting | Low Value | High Value |
|---------|-----------|------------|
| `roles_validity_in_ms` | Faster permission propagation, more auth queries | Better performance, delayed propagation |
| `roles_cache_max_entries` | Lower memory, more cache misses | Higher memory, better hit rate |

---

## Cluster-Wide Operations

### Invalidate on All Nodes

For role changes to take effect cluster-wide immediately:

```bash
#!/bin/bash
# invalidate_roles_cluster.sh

echo "Invalidating roles cache cluster-wide..."

nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo -n "$node: "
    nodetool -h $node invalidaterolescache 2>/dev/null && echo "invalidated" || echo "FAILED"
done

echo "Roles cache cleared on all nodes."
```

### Complete Auth Cache Refresh

For comprehensive auth changes:

```bash
#!/bin/bash
# refresh_all_auth_caches.sh

echo "Refreshing all authentication caches cluster-wide..."

nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo "Processing $node..."
    nodetool -h $node invalidaterolescache 2>/dev/null
    nodetool -h $node invalidatepermissionscache 2>/dev/null
    nodetool -h $node invalidatecredentialscache 2>/dev/null
    echo "  Done"
done

echo "All auth caches cleared."
```

---

## Workflow: Role Modification with Validation

```bash
#!/bin/bash
# role_modification_workflow.sh

ROLE="$1"
ACTION="$2"  # create, delete, grant, revoke
TARGET="$3"  # target role for grant/revoke

echo "=== Role Modification Workflow ==="

# 1. Show current state
echo "1. Current roles:"
cqlsh -e "SELECT role, is_superuser, can_login, member_of FROM system_auth.roles WHERE role = '$ROLE';"

# 2. Perform action
echo ""
echo "2. Performing: $ACTION"
case $ACTION in
    create)
        cqlsh -e "CREATE ROLE $ROLE;"
        ;;
    delete)
        cqlsh -e "DROP ROLE $ROLE;"
        ;;
    grant)
        cqlsh -e "GRANT $TARGET TO $ROLE;"
        ;;
    revoke)
        cqlsh -e "REVOKE $TARGET FROM $ROLE;"
        ;;
esac

# 3. Invalidate cache
echo ""
echo "3. Invalidating roles cache..."
nodetool invalidaterolescache

# 4. Verify change
echo ""
echo "4. Role state after change:"
cqlsh -e "SELECT role, is_superuser, can_login, member_of FROM system_auth.roles WHERE role = '$ROLE';"

echo ""
echo "=== Complete ==="
```

---

## Troubleshooting

### Role Changes Not Taking Effect

```bash
# Invalidate on all nodes
for node in $(nodetool status | grep "^UN" | awk '{print $2}'); do
    nodetool -h $node invalidaterolescache
done

# Also clear permissions cache as they depend on roles
for node in $(nodetool status | grep "^UN" | awk '{print $2}'); do
    nodetool -h $node invalidatepermissionscache
done
```

### Inherited Permissions Not Working

```bash
# Check role hierarchy is correct
cqlsh -e "SELECT role, member_of FROM system_auth.roles;"

# Verify the grant was recorded
cqlsh -e "SELECT * FROM system_auth.role_members WHERE role = 'parent_role';"

# Clear cache and retry
nodetool invalidaterolescache
```

### Superuser Status Not Recognized

```bash
# Verify superuser flag in auth tables
cqlsh -e "SELECT role, is_superuser FROM system_auth.roles WHERE role = 'the_role';"

# Clear all auth caches
nodetool invalidaterolescache
nodetool invalidatepermissionscache
nodetool invalidatecredentialscache
```

### Cannot List Roles After Invalidation

```bash
# Check system_auth keyspace is healthy
nodetool status system_auth

# Check for auth-related errors
grep -i "auth\|role" /var/log/cassandra/system.log | tail -20

# Ensure superuser role exists
cqlsh -u cassandra -p cassandra -e "SELECT * FROM system_auth.roles;"
```

---

## Best Practices

!!! tip "Roles Cache Guidelines"

    1. **Invalidate after hierarchy changes** - Always invalidate when modifying role membership
    2. **Cluster-wide for security** - Invalidate all nodes when revoking role memberships
    3. **Combine with permissions cache** - Role changes often require both caches cleared
    4. **Test role changes** - Verify expected permissions after modifications
    5. **Document role hierarchy** - Maintain documentation of role relationships

!!! warning "Security Considerations"

    - Role hierarchy changes can have cascading effects on permissions
    - Always invalidate cluster-wide when revoking roles
    - Consider the full inheritance chain when troubleshooting
    - Audit role changes for compliance requirements

!!! info "Relationship to Other Caches"

    The roles cache works together with other auth caches:

    - **Credentials cache**: Validates login credentials
    - **Roles cache**: Resolves role memberships and hierarchy
    - **Permissions cache**: Determines allowed operations

    For complete auth refresh, invalidate all three caches.

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [invalidatecredentialscache](invalidatecredentialscache.md) | Clear credentials cache |
| [invalidatepermissionscache](invalidatepermissionscache.md) | Clear permissions cache |
| [getauthcacheconfig](getauthcacheconfig.md) | View auth cache settings |
| [setauthcacheconfig](setauthcacheconfig.md) | Modify auth cache settings |
