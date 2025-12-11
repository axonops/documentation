# nodetool invalidatepermissionscache

Invalidates the permissions cache on the node.

---

## Synopsis

```bash
nodetool [connection_options] invalidatepermissionscache
```

## Description

`nodetool invalidatepermissionscache` clears all cached permission entries on the node. The permissions cache stores authorization information, allowing Cassandra to avoid querying the `system_auth.role_permissions` table for every operation.

After invalidation, subsequent operations trigger fresh permission lookups from the system tables, which are then re-cached.

!!! info "Authentication Required"
    The permissions cache is only relevant when authentication and authorization are enabled. If running with default settings (no auth), this cache is not used.

---

## Examples

### Basic Usage

```bash
nodetool invalidatepermissionscache
```

### After Permission Changes

```bash
# After GRANT or REVOKE operations
nodetool invalidatepermissionscache
```

### On Remote Node

```bash
nodetool -h 192.168.1.100 invalidatepermissionscache
```

---

## Permissions Cache Overview

### What the Cache Stores

| Cached Data | Description |
|-------------|-------------|
| Role | The authenticated role/user |
| Resource | The protected resource (keyspace, table) |
| Permissions | Granted permissions (SELECT, MODIFY, etc.) |

### How It Improves Performance

```
Without Permissions Cache:
  Every Operation → Query system_auth.role_permissions → Check permission → Execute

With Permissions Cache:
  Operation → Check cached permission → Execute
  (Avoids repeated auth table queries)
```

### Permission Types

| Permission | Operations |
|------------|------------|
| SELECT | Read data |
| MODIFY | Write data (INSERT, UPDATE, DELETE) |
| CREATE | Create resources |
| ALTER | Modify resources |
| DROP | Delete resources |
| AUTHORIZE | Grant/revoke permissions |

---

## When to Use

### After Permission Changes

When `GRANT` or `REVOKE` statements don't immediately take effect:

```bash
# Permission change
cqlsh -e "GRANT SELECT ON my_keyspace.my_table TO analyst_role;"

# If permission not immediately effective
nodetool invalidatepermissionscache
```

### During Security Incident Response

When immediate permission revocation is critical:

```bash
# Revoke access immediately
cqlsh -e "REVOKE ALL ON ALL KEYSPACES FROM compromised_user;"

# Force cache refresh on all nodes
for node in $(nodetool status | grep "^UN" | awk '{print $2}'); do
    nodetool -h $node invalidatepermissionscache
done
```

### After Role Modifications

When role hierarchies change:

```bash
# After modifying role membership
cqlsh -e "REVOKE admin_role FROM former_admin;"

# Invalidate to ensure changes take effect
nodetool invalidatepermissionscache
```

### Troubleshooting Access Issues

When permissions appear incorrect:

```bash
# Clear potentially stale permissions
nodetool invalidatepermissionscache

# Retry operation
```

---

## Impact Assessment

### Immediate Effects

| Aspect | Impact |
|--------|--------|
| Cached permissions | All cleared |
| Next operations | Require auth table lookups |
| Operation latency | Slight increase until cache warms |

### Security Effects

| Scenario | Behavior |
|----------|----------|
| Permission revocation | Takes effect immediately |
| New grants | Available immediately |
| Role changes | Reflected immediately |

---

## Configuration

### Cache Settings

```yaml
# cassandra.yaml
permissions_validity_in_ms: 2000     # How long entries are valid
permissions_update_interval_in_ms: 1000  # Background refresh interval
permissions_cache_max_entries: 1000  # Maximum cached entries
```

### Automatic Refresh

Permissions are automatically refreshed based on `permissions_validity_in_ms`. Invalidation forces immediate refresh.

---

## Cluster-Wide Operations

### Invalidate on All Nodes

For permission changes to take effect cluster-wide immediately:

```bash
#!/bin/bash
# invalidate_permissions_cluster.sh

echo "Invalidating permissions cache cluster-wide..."

nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo -n "$node: "
    nodetool -h $node invalidatepermissionscache 2>/dev/null && echo "invalidated" || echo "FAILED"
done

echo "Permissions cache cleared on all nodes."
```

### Security Emergency Response

```bash
#!/bin/bash
# emergency_permission_revoke.sh

USER_TO_REVOKE="$1"

if [ -z "$USER_TO_REVOKE" ]; then
    echo "Usage: $0 <username>"
    exit 1
fi

echo "=== Emergency Permission Revocation ==="
echo "Revoking all permissions for: $USER_TO_REVOKE"

# 1. Revoke permissions
cqlsh -e "REVOKE ALL PERMISSIONS ON ALL KEYSPACES FROM $USER_TO_REVOKE;"

# 2. Invalidate cache on all nodes
nodes=$(nodetool status | grep "^UN" | awk '{print $2}')
for node in $nodes; do
    nodetool -h $node invalidatepermissionscache 2>/dev/null
done

echo "Permissions revoked and cache cleared."
```

---

## Workflow: Permission Change with Validation

```bash
#!/bin/bash
# permission_change_validated.sh

ROLE="$1"
RESOURCE="$2"
PERMISSION="$3"

echo "=== Permission Change Workflow ==="

# 1. Show current permissions
echo "1. Current permissions for $ROLE:"
cqlsh -e "LIST ALL PERMISSIONS OF $ROLE;"

# 2. Make change
echo ""
echo "2. Granting $PERMISSION on $RESOURCE to $ROLE..."
cqlsh -e "GRANT $PERMISSION ON $RESOURCE TO $ROLE;"

# 3. Invalidate cache
echo ""
echo "3. Invalidating permissions cache..."
nodetool invalidatepermissionscache

# 4. Verify change
echo ""
echo "4. Permissions after change:"
cqlsh -e "LIST ALL PERMISSIONS OF $ROLE;"

echo ""
echo "=== Complete ==="
```

---

## Troubleshooting

### Permission Changes Not Taking Effect

```bash
# Invalidate on the specific node handling the request
nodetool invalidatepermissionscache

# Or invalidate cluster-wide
for node in $(nodetool status | grep "^UN" | awk '{print $2}'); do
    nodetool -h $node invalidatepermissionscache
done
```

### Authentication Errors After Invalidation

```bash
# Check system_auth tables are accessible
cqlsh -e "SELECT * FROM system_auth.roles LIMIT 1;"

# Check for auth-related errors in logs
grep -i "auth\|permission" /var/log/cassandra/system.log | tail -20
```

### High Latency After Invalidation

```bash
# Temporary increase in auth lookups is expected
# Cache will warm up quickly with normal operations

# Monitor auth-related metrics
nodetool tpstats | grep -i auth
```

---

## Best Practices

!!! tip "Permissions Cache Guidelines"

    1. **Invalidate after critical changes** - Don't wait for cache expiry for security-sensitive changes
    2. **Cluster-wide for security** - Always invalidate all nodes when revoking access
    3. **Test permission changes** - Verify changes took effect
    4. **Document procedures** - Have runbooks for permission-related incidents
    5. **Monitor auth performance** - Watch for auth-related latency

!!! warning "Security Considerations"

    - Always invalidate cluster-wide when revoking permissions
    - Consider the cache validity period for security-sensitive environments
    - Shorter `permissions_validity_in_ms` = more responsive but higher overhead
    - Log all permission changes for audit purposes

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [invalidatecredentialscache](invalidatecredentialscache.md) | Invalidate credentials cache |
| [invalidaterolescache](invalidaterolescache.md) | Invalidate roles cache |
| [invalidatenetworkpermissionscache](invalidatenetworkpermissionscache.md) | Invalidate network permissions |
