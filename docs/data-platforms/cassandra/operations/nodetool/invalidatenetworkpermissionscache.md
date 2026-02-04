---
title: "nodetool invalidatenetworkpermissionscache"
description: "Clear network permissions cache in Cassandra using nodetool invalidatenetworkpermissionscache."
meta:
  - name: keywords
    content: "nodetool invalidatenetworkpermissionscache, network cache, permissions, Cassandra"
---

# nodetool invalidatenetworkpermissionscache

!!! info "Cassandra 4.1+"
    This command is available in Cassandra 4.1 and later.

Invalidates the network permissions cache on the node.

---

## Synopsis

```bash
nodetool [connection_options] invalidatenetworkpermissionscache
```
See [connection options](index.md#connection-options) for connection options.

---

## Description

`nodetool invalidatenetworkpermissionscache` clears all cached network authorization decisions on the node. The network permissions cache stores the results of CIDR-based and network-level access control checks, allowing Cassandra to authorize client connections from specific IP addresses without re-evaluating network rules for every operation.

This cache is specifically for network-layer authorization that determines whether a client from a particular IP address or network range is allowed to connect and perform operations. It works in conjunction with CIDR filtering and network-based role restrictions.

!!! info "Network Authorization Required"
    This cache is only relevant when network-based authorization is configured. If CIDR filtering or network permissions are not enabled, this cache is not used.

---

## Examples

### Basic Usage

```bash
nodetool invalidatenetworkpermissionscache
```

### After Network Rule Changes

```bash
# After modifying network access rules
nodetool invalidatenetworkpermissionscache
```

---

## Network Permissions Cache Overview

### What the Cache Stores

| Cached Data | Description |
|-------------|-------------|
| Client IP address | The source IP of the connection |
| Network authorization result | Whether access is allowed or denied |
| Associated CIDR groups | Which network groups the IP belongs to |
| Role-network mappings | Which roles are allowed from which networks |

### How It Improves Performance

```
Without Network Permissions Cache:
  Connection Attempt → Evaluate CIDR rules → Check role-network mappings → Allow/Deny

With Network Permissions Cache:
  Connection Attempt → Lookup cached authorization → Allow/Deny
  (Avoids repeated network rule evaluation)
```

### Network Authorization Flow

```
Client Connection (IP: 10.1.50.100)
        │
        ▼
┌─────────────────────────┐
│ Check Network Cache     │
│ (Is IP authorized?)     │
└───────────┬─────────────┘
            │
    Cache Hit?
     /      \
   Yes       No
    │         │
    │         ▼
    │   ┌─────────────────┐
    │   │ Evaluate CIDR   │
    │   │ Rules & Groups  │
    │   └────────┬────────┘
    │            │
    │            ▼
    │   ┌─────────────────┐
    │   │ Cache Result    │
    │   └────────┬────────┘
    │            │
    ▼            ▼
  Allow/Deny Connection
```

---

## When to Use

### After CIDR Group Changes

When CIDR groups are modified:

```bash
# Update CIDR group
nodetool updatecidrgroup office_network '192.168.1.0/24,192.168.2.0/24'

# Invalidate network permissions cache
nodetool invalidatenetworkpermissionscache
```

### After Role-Network Binding Changes

When role access is restricted by network:

```bash
# After modifying which networks a role can connect from
# (via CQL or configuration)
nodetool invalidatenetworkpermissionscache
```

### Security Incident Response

When immediate network access revocation is critical:

```bash
#!/bin/bash
# emergency_network_block.sh

CIDR_GROUP="$1"

echo "=== Emergency Network Block ==="

# 1. Drop the CIDR group
nodetool dropcidrgroup $CIDR_GROUP

# 2. Invalidate all network-related caches on all nodes
for node in $(nodetool status | grep "^UN" | awk '{print $2}'); do
    echo "Processing $node..."
    ssh "$node" "nodetool invalidatenetworkpermissionscache"
    ssh "$node" "nodetool invalidatecidrpermissionscache"
done

echo "Network access revoked for CIDR group: $CIDR_GROUP"
```

### Troubleshooting Network Access Issues

When clients are unexpectedly allowed or denied:

```bash
# Clear cached network authorization decisions
nodetool invalidatenetworkpermissionscache

# Check which CIDR groups contain the client IP
nodetool getcidrgroupsofip 10.1.50.100

# Verify CIDR filtering statistics
nodetool cidrfilteringstats
```

### After Configuration Changes

When network authorization configuration changes:

```bash
# After modifying cassandra.yaml network settings
# and reloading configuration
nodetool invalidatenetworkpermissionscache
```

---

## Impact Assessment

### Immediate Effects

| Aspect | Impact |
|--------|--------|
| Cached network decisions | All cleared |
| Next connections | Require full network rule evaluation |
| Connection latency | Slight increase until cache warms |
| Existing connections | Not affected |

### Security Effects

| Scenario | Behavior |
|----------|----------|
| CIDR group removed | IP immediately blocked |
| New CIDR group added | IP immediately allowed |
| Role-network binding changed | Takes effect immediately |

### Recovery Timeline

| Phase | Duration | Cache State |
|-------|----------|-------------|
| Immediately after | 0 | Empty |
| First connections | Milliseconds | Being populated |
| Normal operations | Seconds | Active IPs cached |

!!! note "Minimal Performance Impact"
    Network permission cache invalidation typically has minimal impact since network rule evaluation is fast and the cache repopulates quickly with active connections.

---

## Configuration

### Related Settings

```yaml
# cassandra.yaml - Network authorization related settings

# CIDR authorizer (if using CIDR-based access control)
cidr_authorizer: CassandraCIDRAuthorizer

# Network permissions cache settings (when available)
network_permissions_validity_in_ms: 2000
network_permissions_update_interval_in_ms: 1000
network_permissions_cache_max_entries: 1000
```

---

## Cluster-Wide Operations

### Invalidate on All Nodes

For network permission changes to take effect cluster-wide:

```bash
#!/bin/bash
# invalidate_network_permissions_cluster.sh

echo "Invalidating network permissions cache cluster-wide..."# Get list of node IPs from local nodetool status


nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo -n "$node: "
    ssh "$node" "nodetool invalidatenetworkpermissionscache 2>/dev/null && echo "invalidated" || echo "FAILED""
done

echo "Network permissions cache cleared on all nodes."
```

### Combined Network Cache Refresh

Clear all network-related caches:

```bash
#!/bin/bash
# refresh_all_network_caches.sh

echo "Refreshing all network authorization caches cluster-wide..."# Get list of node IPs from local nodetool status


nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo "Processing $node..."
    ssh "$node" "nodetool invalidatenetworkpermissionscache 2>/dev/null"
    ssh "$node" "nodetool invalidatecidrpermissionscache 2>/dev/null"
    ssh "$node" "nodetool reloadcidrgroupscache 2>/dev/null"
    echo "  Done"
done

echo "All network caches cleared."
```

---

## Workflow: Network Access Change with Validation

```bash
#!/bin/bash
# network_access_change.sh

ACTION="$1"    # allow or block
CIDR="$2"      # CIDR range, e.g., "10.1.0.0/16"
GROUP="$3"     # CIDR group name

echo "=== Network Access Change Workflow ==="

# 1. Show current CIDR groups
echo "1. Current CIDR groups:"
nodetool listcidrgroups

# 2. Perform action
echo ""
echo "2. Action: $ACTION for $CIDR"
case $ACTION in
    allow)
        nodetool updatecidrgroup $GROUP "$CIDR"
        ;;
    block)
        # Get current group, remove the CIDR (requires manual handling)
        echo "Removing $CIDR from $GROUP..."
        nodetool dropcidrgroup $GROUP
        ;;
esac

# 3. Invalidate caches
echo ""
echo "3. Invalidating network caches..."
nodetool invalidatenetworkpermissionscache
nodetool invalidatecidrpermissionscache

# 4. Verify
echo ""
echo "4. Updated CIDR groups:"
nodetool listcidrgroups

# 5. Test an IP
echo ""
echo "5. Test IP membership:"
read -p "Enter IP to test: " test_ip
nodetool getcidrgroupsofip $test_ip

echo ""
echo "=== Complete ==="
```

---

## Troubleshooting

### Client Unexpectedly Blocked

```bash
# Check if IP is in expected CIDR groups
nodetool getcidrgroupsofip <client_ip>

# Verify CIDR groups exist
nodetool listcidrgroups

# Clear cache and retry
nodetool invalidatenetworkpermissionscache
```

### Client Unexpectedly Allowed

```bash
# Check CIDR group membership
nodetool getcidrgroupsofip <client_ip>

# If IP shouldn't be in any group, check CIDR ranges
nodetool listcidrgroups

# Clear cache and verify
nodetool invalidatenetworkpermissionscache
nodetool cidrfilteringstats
```

### Network Changes Not Taking Effect

```bash
# Invalidate on all nodes
for node in $(nodetool status | grep "^UN" | awk '{print $2}'); do
    ssh "$node" "nodetool invalidatenetworkpermissionscache"
    ssh "$node" "nodetool invalidatecidrpermissionscache"
done

# Reload CIDR groups from system tables
for node in $(nodetool status | grep "^UN" | awk '{print $2}'); do
    ssh "$node" "nodetool reloadcidrgroupscache"
done
```

### High Cache Miss Rate

```bash
# Check CIDR filtering statistics
nodetool cidrfilteringstats

# If miss rate is high with many unique IPs,
# consider increasing cache size or
# using broader CIDR ranges
```

---

## Best Practices

!!! tip "Network Permissions Cache Guidelines"

    1. **Invalidate after CIDR changes** - Always invalidate when modifying network rules
    2. **Cluster-wide for security** - Invalidate all nodes when blocking networks
    3. **Combine with CIDR cache** - Network permission changes often require both caches cleared
    4. **Test changes** - Verify network access after modifications
    5. **Monitor statistics** - Use `cidrfilteringstats` to verify behavior

!!! warning "Security Considerations"

    - Network rule changes can have immediate security implications
    - Always invalidate cluster-wide when blocking access
    - Test changes thoroughly before production deployment
    - Audit all network access changes for compliance

!!! info "Relationship to CIDR Filtering"

    The network permissions cache works with the CIDR filtering system:

    - **CIDR groups cache**: Stores CIDR group definitions
    - **CIDR permissions cache**: Stores IP-to-group mappings
    - **Network permissions cache**: Stores authorization decisions

    For complete network access refresh, consider invalidating all related caches.

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [invalidatecidrpermissionscache](invalidatecidrpermissionscache.md) | Clear CIDR permissions cache |
| [reloadcidrgroupscache](reloadcidrgroupscache.md) | Reload CIDR groups |
| [cidrfilteringstats](cidrfilteringstats.md) | View filtering statistics |
| [listcidrgroups](listcidrgroups.md) | List CIDR groups |
| [getcidrgroupsofip](getcidrgroupsofip.md) | Check IP group membership |
| [updatecidrgroup](updatecidrgroup.md) | Modify CIDR groups |
| [dropcidrgroup](dropcidrgroup.md) | Remove CIDR groups |
| [invalidatepermissionscache](invalidatepermissionscache.md) | Clear role permissions cache |