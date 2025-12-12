---
description: "Clear CIDR permissions cache in Cassandra using nodetool invalidatecidrpermissionscache."
meta:
  - name: keywords
    content: "nodetool invalidatecidrpermissionscache, CIDR cache, permissions cache, Cassandra"
---

# nodetool invalidatecidrpermissionscache

Invalidates the CIDR permissions cache on the node.

---

## Synopsis

```bash
nodetool [connection_options] invalidatecidrpermissionscache
```

---

## Description

`nodetool invalidatecidrpermissionscache` clears the cached CIDR authorization decisions on the node. This forces re-evaluation of CIDR-based permissions for subsequent connection attempts.

The CIDR permissions cache stores the results of IP-to-CIDR-group lookups to improve authorization performance. Invalidating this cache is necessary after modifying CIDR groups to ensure changes take effect immediately.

---

## Examples

### Basic Usage

```bash
nodetool invalidatecidrpermissionscache
```

### After CIDR Group Changes

```bash
# Update CIDR group
nodetool updatecidrgroup app_servers '10.100.0.0/16,10.101.0.0/16'

# Invalidate cache to apply changes immediately
nodetool invalidatecidrpermissionscache
```

### After Dropping a CIDR Group

```bash
# Remove CIDR group
nodetool dropcidrgroup deprecated_network

# Clear cache
nodetool invalidatecidrpermissionscache
```

### Cluster-Wide Invalidation

```bash
# Run on all nodes for cluster-wide effect
for host in node1 node2 node3; do
    nodetool -h $host invalidatecidrpermissionscache
done
```

---

## When to Use

### After CIDR Configuration Changes

```bash
# After any CIDR group modification
nodetool updatecidrgroup new_network '10.200.0.0/16'
nodetool invalidatecidrpermissionscache
```

Always invalidate the cache after:

- Creating new CIDR groups
- Updating CIDR group ranges
- Dropping CIDR groups
- Modifying role-to-CIDR associations

### Immediate Security Response

```bash
# Block compromised network immediately
nodetool dropcidrgroup compromised_subnet
nodetool invalidatecidrpermissionscache
```

During security incidents, invalidate the cache to ensure access revocations take effect immediately.

### Troubleshooting Authorization Issues

```bash
# Clear cache to rule out stale data
nodetool invalidatecidrpermissionscache

# Test connection from affected IP
nodetool getcidrgroupsofip 10.50.100.25
```

---

## Best Practices

!!! tip "Cache Invalidation Guidelines"

    1. **Run on affected nodes** - Execute on all nodes where clients connect
    2. **Include in change procedures** - Always invalidate after CIDR modifications
    3. **Monitor after invalidation** - Watch for authorization issues after cache clear
    4. **Consider timing** - Cache invalidation may briefly increase authorization latency

!!! warning "Non-Persistent Setting"

    This is a runtime operation only. The cache will automatically rebuild as new authorization checks occur. No configuration changes are persisted.

!!! info "Cache Behavior"

    - Cache entries expire based on `permissions_validity` setting
    - Invalidation clears all cached CIDR authorization decisions
    - New entries are cached as clients reconnect or new checks occur
    - High connection rates may see brief latency increase after invalidation

---

## Performance Considerations

After invalidating the cache:

- First authorization check for each IP requires full evaluation
- Cache rebuilds automatically as checks occur
- Brief increase in authorization latency is normal
- Monitor `cidrfilteringstats` for cache performance metrics

```bash
# Check cache performance after invalidation
nodetool cidrfilteringstats
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [cidrfilteringstats](cidrfilteringstats.md) | View cache statistics |
| [listcidrgroups](listcidrgroups.md) | List CIDR groups |
| [updatecidrgroup](updatecidrgroup.md) | Modify CIDR groups |
| [dropcidrgroup](dropcidrgroup.md) | Remove CIDR groups |
| [reloadcidrgroupscache](reloadcidrgroupscache.md) | Reload groups from storage |
| [invalidatepermissionscache](invalidatepermissionscache.md) | Clear role permissions cache |
