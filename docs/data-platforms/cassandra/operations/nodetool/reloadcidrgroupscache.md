---
title: "nodetool reloadcidrgroupscache"
description: "Reload CIDR groups cache from disk using nodetool reloadcidrgroupscache."
meta:
  - name: keywords
    content: "nodetool reloadcidrgroupscache, CIDR cache, reload cache, Cassandra"
---

# nodetool reloadcidrgroupscache

!!! info "Cassandra 5.0+"
    This command is available in Cassandra 5.0 and later.

Reloads the CIDR groups cache from system tables.

---

## Synopsis

```bash
nodetool [connection_options] reloadcidrgroupscache
```

---

## Description

`nodetool reloadcidrgroupscache` forces a reload of CIDR group definitions from the system tables into the node's cache. This ensures the node has the latest CIDR group configurations without requiring a restart.

Unlike `invalidatecidrpermissionscache` which clears authorization decisions, this command specifically reloads the CIDR group definitions themselves.

---

## Examples

### Basic Usage

```bash
nodetool reloadcidrgroupscache
```

### After Schema Changes

```bash
# After CIDR groups modified via CQL
# Force reload on this node
nodetool reloadcidrgroupscache
```

### Cluster-Wide Reload

```bash
# Ensure all nodes have latest CIDR groups
for host in node1 node2 node3; do
    ssh "$host" "nodetool reloadcidrgroupscache"
done
```

### Combined with Cache Invalidation

```bash
# Full refresh of CIDR configuration
nodetool reloadcidrgroupscache
nodetool invalidatecidrpermissionscache
```

---

## When to Use

### After CQL-Based CIDR Changes

```bash
# If CIDR groups modified via CQL
# Reload to ensure node sees changes
nodetool reloadcidrgroupscache
```

When CIDR groups are modified using CQL commands rather than nodetool, reload the cache to ensure changes are visible.

### Sync After Network Partition

```bash
# After network partition recovery
# Ensure CIDR groups are synchronized
nodetool reloadcidrgroupscache
```

After cluster recovery from network issues, reload to ensure CIDR group consistency.

### Troubleshooting CIDR Issues

```bash
# If CIDR authorization behaving unexpectedly
nodetool reloadcidrgroupscache
nodetool listcidrgroups
```

When CIDR authorization isn't working as expected, reload the cache and verify group definitions.

---

## Best Practices

!!! tip "Usage Guidelines"

    1. **Run after CQL changes** - Always reload after modifying CIDR groups via CQL
    2. **Include in maintenance** - Add to regular maintenance procedures
    3. **Verify after reload** - Use `listcidrgroups` to confirm loaded data
    4. **Consider all nodes** - Run on nodes that handle client connections

!!! info "Cache Behavior"

    - Reloads CIDR group definitions from `system_auth` tables
    - Does not affect cached authorization decisions
    - For complete refresh, combine with `invalidatecidrpermissionscache`
    - Changes are effective immediately on the target node

!!! warning "Multi-Node Consideration"

    This command affects only the node where it's executed. For cluster-wide consistency, run on all relevant nodes or include in automated procedures.

---

## Difference from invalidatecidrpermissionscache

| Command | Action |
|---------|--------|
| `reloadcidrgroupscache` | Reloads CIDR group definitions from system tables |
| `invalidatecidrpermissionscache` | Clears cached authorization decisions |

For a complete refresh after CIDR changes:

```bash
# Reload group definitions
nodetool reloadcidrgroupscache

# Clear cached authorization results
nodetool invalidatecidrpermissionscache
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [listcidrgroups](listcidrgroups.md) | Verify loaded groups |
| [invalidatecidrpermissionscache](invalidatecidrpermissionscache.md) | Clear authorization cache |
| [cidrfilteringstats](cidrfilteringstats.md) | View filtering statistics |
| [updatecidrgroup](updatecidrgroup.md) | Modify CIDR groups |
| [getcidrgroupsofip](getcidrgroupsofip.md) | Test IP group membership |