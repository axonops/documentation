---
title: "nodetool invalidatecredentialscache"
description: "Clear credentials cache in Cassandra using nodetool invalidatecredentialscache."
meta:
  - name: keywords
    content: "nodetool invalidatecredentialscache, credentials cache, authentication, Cassandra"
---

# nodetool invalidatecredentialscache

Invalidates the credentials cache on the node.

---

## Synopsis

```bash
nodetool [connection_options] invalidatecredentialscache
```

## Description

`nodetool invalidatecredentialscache` clears all cached credential entries on the node. The credentials cache stores authentication information (username/password hashes), allowing Cassandra to validate login attempts without querying the `system_auth.roles` table for every connection.

After invalidation, subsequent login attempts trigger fresh credential lookups from the system_auth tables.

!!! info "Authentication Required"
    The credentials cache is only relevant when authentication is enabled (PasswordAuthenticator or custom authenticator). If running with AllowAllAuthenticator, this cache is not used.

---

## Examples

### Basic Usage

```bash
nodetool invalidatecredentialscache
```

### After Password Change

```bash
# After changing a user's password
nodetool invalidatecredentialscache
```

### On Remote Node

```bash
nodetool -h 192.168.1.100 invalidatecredentialscache
```

---

## Credentials Cache Overview

### What the Cache Stores

| Cached Data | Description |
|-------------|-------------|
| Username | The role/user name |
| Password hash | Bcrypt hash of the password |
| Login status | Whether the role can login |

### How It Improves Performance

```
Without Credentials Cache:
  Login Attempt → Query system_auth.roles → Verify password → Establish session

With Credentials Cache:
  Login Attempt → Check cached credentials → Establish session
  (Avoids auth table query on every login)
```

---

## When to Use

### After Password Changes

When password changes don't immediately take effect:

```bash
# Change password
cqlsh -e "ALTER ROLE user_name WITH PASSWORD = 'new_password';"

# Force cache refresh
nodetool invalidatecredentialscache
```

### After Disabling a User

When disabling login access:

```bash
# Disable login
cqlsh -e "ALTER ROLE compromised_user WITH LOGIN = false;"

# Immediate effect required
nodetool invalidatecredentialscache
```

### Security Incident Response

When immediate credential invalidation is critical:

```bash
#!/bin/bash
# emergency_credential_revoke.sh

USER="$1"

# Change password to random value
NEW_PASS=$(openssl rand -base64 32)
cqlsh -e "ALTER ROLE $USER WITH PASSWORD = '$NEW_PASS';"

# Disable login
cqlsh -e "ALTER ROLE $USER WITH LOGIN = false;"

# Clear cache on all nodes
for node in $(nodetool status | grep "^UN" | awk '{print $2}'); do
    nodetool -h $node invalidatecredentialscache
done

echo "User $USER credentials invalidated cluster-wide."
```

### Troubleshooting Authentication Issues

When authentication appears incorrect:

```bash
# Clear potentially stale credentials
nodetool invalidatecredentialscache

# Retry login
```

---

## Impact Assessment

### Immediate Effects

| Aspect | Impact |
|--------|--------|
| Cached credentials | All cleared |
| Next logins | Require auth table lookups |
| Existing connections | Not affected |

### Security Effects

| Scenario | Behavior |
|----------|----------|
| Password change | New password required immediately |
| Login disabled | Cannot establish new connections |
| Role deleted | Cannot login |

!!! note "Existing Connections"
    Invalidating credentials cache only affects new login attempts. Existing connections remain valid until they are closed or timeout.

---

## Configuration

### Cache Settings

```yaml
# cassandra.yaml
credentials_validity_in_ms: 2000     # How long entries are valid
credentials_update_interval_in_ms: 1000  # Background refresh interval
credentials_cache_max_entries: 1000  # Maximum cached entries
```

### Automatic Refresh

Credentials are automatically refreshed based on `credentials_validity_in_ms`. Invalidation forces immediate refresh for new connections.

---

## Cluster-Wide Operations

### Invalidate on All Nodes

For credential changes to take effect cluster-wide immediately:

```bash
#!/bin/bash
# invalidate_credentials_cluster.sh

echo "Invalidating credentials cache cluster-wide..."

nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo -n "$node: "
    nodetool -h $node invalidatecredentialscache 2>/dev/null && echo "invalidated" || echo "FAILED"
done

echo "Credentials cache cleared on all nodes."
```

### Password Rotation Workflow

```bash
#!/bin/bash
# rotate_password.sh

USER="$1"
NEW_PASSWORD="$2"

if [ -z "$USER" ] || [ -z "$NEW_PASSWORD" ]; then
    echo "Usage: $0 <username> <new_password>"
    exit 1
fi

echo "=== Password Rotation ==="

# 1. Change password
echo "1. Changing password for $USER..."
cqlsh -e "ALTER ROLE $USER WITH PASSWORD = '$NEW_PASSWORD';"

# 2. Invalidate cache cluster-wide
echo "2. Invalidating credentials cache..."
nodes=$(nodetool status | grep "^UN" | awk '{print $2}')
for node in $nodes; do
    nodetool -h $node invalidatecredentialscache 2>/dev/null
done

echo "3. Password changed. New password takes effect immediately."
echo ""
echo "NOTE: Existing connections continue to work."
echo "For complete session termination, restart affected applications."
```

---

## Security Considerations

### Immediate Lockout

```bash
#!/bin/bash
# lockout_user.sh

USER="$1"

echo "=== Immediate User Lockout ==="

# 1. Disable login
cqlsh -e "ALTER ROLE $USER WITH LOGIN = false;"

# 2. Clear cache on all nodes
for node in $(nodetool status | grep "^UN" | awk '{print $2}'); do
    nodetool -h $node invalidatecredentialscache
done

echo "User $USER locked out."
echo ""
echo "NOTE: To terminate existing connections, may need to:"
echo "  - Restart client applications"
echo "  - Or wait for connection timeout"
```

### Password Compromise Response

```bash
#!/bin/bash
# password_compromise_response.sh

USER="$1"

echo "=== Password Compromise Response ==="

# 1. Generate new random password
NEW_PASS=$(openssl rand -base64 24)

# 2. Change password
cqlsh -e "ALTER ROLE $USER WITH PASSWORD = '$NEW_PASS';"

# 3. Invalidate cache cluster-wide
for node in $(nodetool status | grep "^UN" | awk '{print $2}'); do
    nodetool -h $node invalidatecredentialscache
done

# 4. Log the incident
echo "$(date): Password compromised for $USER - password reset" >> /var/log/security_incidents.log

echo "Password reset complete."
echo "New temporary password: $NEW_PASS"
echo "User should change this password immediately."
```

---

## Troubleshooting

### Password Change Not Taking Effect

```bash
# Invalidate on all nodes
for node in $(nodetool status | grep "^UN" | awk '{print $2}'); do
    nodetool -h $node invalidatecredentialscache
done

# Verify the change was stored
cqlsh -e "SELECT role, salted_hash FROM system_auth.roles WHERE role = 'username';"
```

### Login Still Working After Disable

```bash
# Ensure LOGIN = false is set
cqlsh -e "SELECT role, can_login FROM system_auth.roles WHERE role = 'username';"

# Invalidate cache
nodetool invalidatecredentialscache

# Note: Existing connections remain until closed
```

### Cannot Connect After Invalidation

```bash
# Check if auth tables are accessible
nodetool status

# Check for auth errors
grep -i "auth" /var/log/cassandra/system.log | tail -20

# Verify superuser still exists
cqlsh -u cassandra -p cassandra -e "SELECT * FROM system_auth.roles;"
```

---

## Best Practices

!!! tip "Credentials Cache Guidelines"

    1. **Always invalidate cluster-wide** - For password/login changes
    2. **Use short validity periods** - For security-sensitive environments
    3. **Immediate response** - Invalidate immediately for security incidents
    4. **Test changes** - Verify authentication works as expected
    5. **Document procedures** - Have runbooks for credential management

!!! warning "Security Best Practices"

    - Invalidate cache immediately when revoking access
    - Use strong passwords (Cassandra uses bcrypt)
    - Monitor failed login attempts
    - Consider shorter `credentials_validity_in_ms` for sensitive environments
    - Remember existing connections are not affected

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [invalidatepermissionscache](invalidatepermissionscache.md) | Invalidate permissions cache |
| [invalidaterolescache](invalidaterolescache.md) | Invalidate roles cache |
