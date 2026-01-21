---
title: "nodetool invalidatejmxpermissionscache"
description: "Clear JMX permissions cache in Cassandra using nodetool invalidatejmxpermissionscache."
meta:
  - name: keywords
    content: "nodetool invalidatejmxpermissionscache, JMX cache, permissions, Cassandra"
search:
  boost: 3
---

# nodetool invalidatejmxpermissionscache

!!! info "Cassandra 4.1+"
    This command is available in Cassandra 4.1 and later.

Invalidates the JMX permissions cache on the node.

---

## Synopsis

```bash
nodetool [connection_options] invalidatejmxpermissionscache
```

---

## Description

`nodetool invalidatejmxpermissionscache` clears all cached JMX authorization information on the node. The JMX permissions cache stores authorization decisions for JMX (Java Management Extensions) operations, allowing Cassandra to determine whether a user can execute specific nodetool commands or access MBeans without querying the auth tables for every JMX call.

JMX authentication and authorization control access to administrative operations through nodetool and other JMX clients. When enabled, users must be granted specific JMX permissions to execute management commands.

!!! info "JMX Authorization Required"
    This cache is only relevant when JMX authentication and authorization are enabled. If JMX is configured without authorization (the default), this cache is not used.

---

## Examples

### Basic Usage

```bash
nodetool invalidatejmxpermissionscache
```

### After JMX Permission Grant

```bash
# After granting JMX permissions to a role
cqlsh -e "GRANT EXECUTE ON ALL MBEANS TO ops_team;"

# Invalidate JMX cache
nodetool invalidatejmxpermissionscache
```

---

## JMX Permissions Cache Overview

### What the Cache Stores

| Cached Data | Description |
|-------------|-------------|
| Role | The authenticated JMX user |
| MBean | The target MBean or MBean pattern |
| Permission | Allowed JMX operations (EXECUTE, DESCRIBE) |
| Method | Specific MBean methods if restricted |

### How It Improves Performance

```
Without JMX Permissions Cache:
  nodetool Command → JMX Call → Query auth tables → Check permission → Execute MBean operation

With JMX Permissions Cache:
  nodetool Command → JMX Call → Check cached permission → Execute MBean operation
  (Avoids auth table queries for every JMX call)
```

### JMX Permission Types

| Permission | Description | Example Operations |
|------------|-------------|-------------------|
| `EXECUTE` | Invoke MBean methods | nodetool commands |
| `DESCRIBE` | Read MBean attributes | Monitoring, metrics |
| `SELECT` | Read MBean values | JMX console access |
| `MODIFY` | Write MBean attributes | Configuration changes |

---

## When to Use

### After JMX Permission Changes

When JMX access is granted or revoked:

```bash
# Grant JMX permissions
cqlsh -e "GRANT EXECUTE ON MBEAN 'org.apache.cassandra.db:*' TO dba_role;"

# Invalidate JMX cache
nodetool invalidatejmxpermissionscache
```

### After Role Changes Affecting JMX

When role memberships that include JMX permissions change:

```bash
# Revoke role that had JMX permissions
cqlsh -e "REVOKE admin_role FROM former_dba;"

# Invalidate both roles and JMX caches
nodetool invalidaterolescache
nodetool invalidatejmxpermissionscache
```

### Security Incident Response

When immediate JMX access revocation is critical:

```bash
#!/bin/bash
# emergency_jmx_revoke.sh

USER="$1"

echo "=== Emergency JMX Access Revocation ==="

# 1. Revoke all JMX permissions
cqlsh -e "REVOKE ALL PERMISSIONS ON ALL MBEANS FROM $USER;"

# 2. Invalidate JMX cache on all nodes
for node in $(nodetool status | grep "^UN" | awk '{print $2}'); do
    echo "Processing $node..."
    ssh "$node" "nodetool invalidatejmxpermissionscache"
done

echo "JMX access revoked for user: $USER"
```

### Troubleshooting JMX Access Issues

When nodetool commands fail with permission errors:

```bash
# Clear JMX permissions cache
nodetool invalidatejmxpermissionscache

# Verify JMX permissions
cqlsh -e "LIST ALL PERMISSIONS ON ALL MBEANS OF problem_user;"
```

### After JMX Configuration Changes

When JMX authorization configuration changes:

```bash
# After modifying jmx authorization settings
nodetool invalidatejmxpermissionscache
```

---

## Impact Assessment

### Immediate Effects

| Aspect | Impact |
|--------|--------|
| Cached JMX permissions | All cleared |
| Next JMX operations | Require auth table lookups |
| nodetool command latency | Slight increase until cache warms |
| Existing JMX sessions | May require re-authorization |

### Security Effects

| Scenario | Behavior |
|----------|----------|
| JMX permission revoked | Access denied immediately |
| New JMX permission granted | Access allowed immediately |
| Role with JMX removed | Access revoked immediately |

### Recovery Timeline

| Phase | Duration | Cache State |
|-------|----------|-------------|
| Immediately after | 0 | Empty |
| First commands | Milliseconds | Being populated |
| Normal operations | Seconds | Active users cached |

!!! note "Minimal Performance Impact"
    JMX permissions cache invalidation typically has minimal impact since JMX authorization lookups are fast and most environments have few JMX users.

---

## Configuration

### JMX Authorization Settings

JMX authorization is configured in multiple files:

**cassandra-env.sh**:
```bash
# Enable JMX authentication
JVM_OPTS="$JVM_OPTS -Dcom.sun.management.jmxremote.authenticate=true"

# Enable JMX authorization
JVM_OPTS="$JVM_OPTS -Dcassandra.jmx.authorizer=org.apache.cassandra.auth.jmx.AuthorizationProxy"
```

**jmxremote.access** (traditional JMX):
```
monitorRole   readonly
controlRole   readwrite
```

**Cassandra Native JMX Auth** (cassandra.yaml):
```yaml
# Use Cassandra's internal authorization for JMX
jmx_authorizer: CassandraJMXAuthorizer
```

### Cache Settings

```yaml
# cassandra.yaml - JMX cache settings (when using native auth)
jmx_permissions_validity_in_ms: 2000
jmx_permissions_update_interval_in_ms: 1000
jmx_permissions_cache_max_entries: 1000
```

---

## Cluster-Wide Operations

### Invalidate on All Nodes

For JMX permission changes to take effect cluster-wide:

```bash
#!/bin/bash
# invalidate_jmx_permissions_cluster.sh

echo "Invalidating JMX permissions cache cluster-wide..."# Get list of node IPs from local nodetool status


nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo -n "$node: "
    ssh "$node" "nodetool invalidatejmxpermissionscache 2>/dev/null && echo "invalidated" || echo "FAILED""
done

echo "JMX permissions cache cleared on all nodes."
```

### Complete JMX Access Refresh

Clear all JMX-related caches:

```bash
#!/bin/bash
# refresh_jmx_access.sh

echo "Refreshing JMX access caches cluster-wide..."# Get list of node IPs from local nodetool status


nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo "Processing $node..."
    ssh "$node" "nodetool invalidatejmxpermissionscache 2>/dev/null"
    ssh "$node" "nodetool invalidatecredentialscache 2>/dev/null"
    ssh "$node" "nodetool invalidaterolescache 2>/dev/null"
    echo "  Done"
done

echo "All JMX access caches cleared."
```

---

## JMX Permission Management

### Granting JMX Permissions

```sql
-- Grant access to all MBeans
GRANT EXECUTE ON ALL MBEANS TO admin_role;

-- Grant access to specific MBean
GRANT EXECUTE ON MBEAN 'org.apache.cassandra.db:type=StorageService' TO ops_role;

-- Grant access to MBean pattern
GRANT EXECUTE ON MBEAN 'org.apache.cassandra.db:*' TO dba_role;

-- Grant read-only access
GRANT DESCRIBE ON ALL MBEANS TO monitoring_role;
```

### Revoking JMX Permissions

```sql
-- Revoke specific permission
REVOKE EXECUTE ON ALL MBEANS FROM former_admin;

-- Revoke all JMX permissions
REVOKE ALL PERMISSIONS ON ALL MBEANS FROM user_role;
```

### Listing JMX Permissions

```sql
-- List all JMX permissions for a role
LIST ALL PERMISSIONS ON ALL MBEANS OF admin_role;

-- List all JMX permissions
LIST ALL PERMISSIONS ON ALL MBEANS;
```

---

## Workflow: JMX Permission Change with Validation

```bash
#!/bin/bash
# jmx_permission_workflow.sh

ROLE="$1"
ACTION="$2"  # grant or revoke
MBEAN="$3"   # MBean pattern or "ALL MBEANS"

echo "=== JMX Permission Change Workflow ==="

# 1. Show current permissions
echo "1. Current JMX permissions for $ROLE:"
cqlsh -e "LIST ALL PERMISSIONS ON ALL MBEANS OF $ROLE;"

# 2. Perform action
echo ""
echo "2. Action: $ACTION EXECUTE ON $MBEAN"
if [ "$ACTION" = "grant" ]; then
    cqlsh -e "GRANT EXECUTE ON $MBEAN TO $ROLE;"
else
    cqlsh -e "REVOKE EXECUTE ON $MBEAN FROM $ROLE;"
fi

# 3. Invalidate cache
echo ""
echo "3. Invalidating JMX permissions cache..."
nodetool invalidatejmxpermissionscache

# 4. Verify change
echo ""
echo "4. JMX permissions after change:"
cqlsh -e "LIST ALL PERMISSIONS ON ALL MBEANS OF $ROLE;"

# 5. Test access (optional)
echo ""
echo "5. Testing JMX access..."
# This would require the user to attempt a nodetool command
echo "   Test by running: nodetool -u $ROLE status"

echo ""
echo "=== Complete ==="
```

---

## Troubleshooting

### nodetool Command Fails with Permission Error

```bash
# Check JMX permissions for the user
cqlsh -e "LIST ALL PERMISSIONS ON ALL MBEANS OF username;"

# Check role membership
cqlsh -e "SELECT role, member_of FROM system_auth.roles WHERE role = 'username';"

# Clear caches and retry
nodetool invalidatejmxpermissionscache
nodetool invalidaterolescache
```

### JMX Permission Grant Not Taking Effect

```bash
# Invalidate on all nodes
for node in $(nodetool status | grep "^UN" | awk '{print $2}'); do
    ssh "$node" "nodetool invalidatejmxpermissionscache"
done

# Verify the grant was recorded
cqlsh -e "SELECT * FROM system_auth.role_permissions WHERE role = 'the_role';"
```

### User Has Too Much JMX Access

```bash
# List all permissions
cqlsh -e "LIST ALL PERMISSIONS ON ALL MBEANS OF overprivileged_user;"

# Revoke excessive permissions
cqlsh -e "REVOKE EXECUTE ON ALL MBEANS FROM overprivileged_user;"

# Grant only needed permissions
cqlsh -e "GRANT EXECUTE ON MBEAN 'org.apache.cassandra.db:type=StorageService' TO overprivileged_user;"

# Invalidate cache
nodetool invalidatejmxpermissionscache
```

### Cannot Access JMX After Invalidation

```bash
# Check if JMX authentication is working
nodetool -u admin_user -pw password status

# Check for auth errors
grep -i "jmx\|auth" /var/log/cassandra/system.log | tail -20

# Verify JMX configuration
grep -i "jmx" /etc/cassandra/cassandra-env.sh
```

---

## Best Practices

!!! tip "JMX Permissions Cache Guidelines"

    1. **Invalidate after permission changes** - Always invalidate when modifying JMX access
    2. **Cluster-wide for security** - Invalidate all nodes when revoking JMX access
    3. **Least privilege** - Grant only necessary JMX permissions
    4. **Use role hierarchy** - Create JMX permission roles and grant to users
    5. **Audit JMX access** - Regularly review who has JMX permissions

!!! warning "Security Considerations"

    - JMX access provides powerful administrative control over Cassandra
    - `EXECUTE ON ALL MBEANS` is equivalent to full cluster administration
    - Always invalidate cluster-wide when revoking JMX access
    - Consider separate JMX credentials from CQL credentials
    - Monitor JMX access in audit logs

!!! info "JMX vs CQL Permissions"

    JMX and CQL permissions are separate:

    - **CQL permissions**: Control data access and DDL operations
    - **JMX permissions**: Control administrative operations (nodetool)

    A user may need both depending on their role:

    - DBAs typically need both CQL and JMX permissions
    - Application users typically need only CQL permissions
    - Operators may need only JMX permissions for monitoring

---

## Common MBean Patterns

| MBean Pattern | Description |
|--------------|-------------|
| `org.apache.cassandra.db:*` | Database operations |
| `org.apache.cassandra.db:type=StorageService` | Cluster management |
| `org.apache.cassandra.db:type=CompactionManager` | Compaction operations |
| `org.apache.cassandra.db:type=StreamManager` | Streaming operations |
| `org.apache.cassandra.net:*` | Network operations |
| `org.apache.cassandra.metrics:*` | Metrics access |

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [invalidatepermissionscache](invalidatepermissionscache.md) | Clear CQL permissions cache |
| [invalidatecredentialscache](invalidatecredentialscache.md) | Clear credentials cache |
| [invalidaterolescache](invalidaterolescache.md) | Clear roles cache |
| [getauthcacheconfig](getauthcacheconfig.md) | View auth cache settings |
| [setauthcacheconfig](setauthcacheconfig.md) | Modify auth cache settings |
