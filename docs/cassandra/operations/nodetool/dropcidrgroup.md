---
title: "nodetool dropcidrgroup"
description: "Remove a CIDR group from Cassandra using nodetool dropcidrgroup command."
meta:
  - name: keywords
    content: "nodetool dropcidrgroup, CIDR group, network security, Cassandra"
---

# nodetool dropcidrgroup

Removes a CIDR group from the cluster.

---

## Synopsis

```bash
nodetool [connection_options] dropcidrgroup <group_name>
```

---

## Description

`nodetool dropcidrgroup` removes a CIDR group definition from the cluster. Once dropped, the group can no longer be used for IP-based access control.

!!! info "Persistent Change"
    Unlike many nodetool commands, this change **is persistent** across node restarts. CIDR groups are stored in the `system_auth.cidr_groups` table, which is replicated across the cluster. Once a group is dropped, it remains deleted until explicitly recreated.

!!! danger "Irreversible Operation"

    Dropping a CIDR group immediately removes it from all role associations. This may cause authorization failures for clients currently relying on that group for access. Ensure no roles depend on the group before dropping.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `group_name` | The name of the CIDR group to remove |

---

## Examples

### Basic Usage

```bash
nodetool dropcidrgroup deprecated_network
```

### Safe Removal Process

```bash
# 1. Check current groups
nodetool listcidrgroups

# 2. Verify the group to be removed
nodetool getcidrgroupsofip 10.99.0.1

# 3. Remove the group
nodetool dropcidrgroup old_office_network

# 4. Invalidate cache to ensure immediate effect
nodetool invalidatecidrpermissionscache

# 5. Verify removal
nodetool listcidrgroups
```

---

## When to Use

### Decommission Network Ranges

```bash
# Remove CIDR group for decommissioned network
nodetool dropcidrgroup legacy_datacenter
```

Use when network ranges are no longer valid or have been decommissioned.

### Clean Up Unused Groups

```bash
# Remove unused CIDR groups
nodetool dropcidrgroup test_network
```

Remove groups created for testing or that are no longer needed.

### Security Response

```bash
# Remove compromised network range
nodetool dropcidrgroup compromised_subnet
nodetool invalidatecidrpermissionscache
```

Quickly revoke access from a network range during a security incident.

---

## Best Practices

!!! warning "Pre-Drop Checklist"

    Before dropping a CIDR group:

    1. **Identify dependent roles** - Check which roles reference this group
    2. **Update role permissions** - Remove group references from roles first
    3. **Notify stakeholders** - Inform teams that may be affected
    4. **Test in staging** - Verify impact in non-production first
    5. **Plan for rollback** - Document group configuration for recovery if needed

!!! tip "Safe Removal Process"

    ```bash
    # Document current configuration
    nodetool listcidrgroups > cidr_groups_backup.txt

    # Remove group
    nodetool dropcidrgroup <group_name>

    # Clear cache for immediate effect
    nodetool invalidatecidrpermissionscache
    ```

!!! info "Recovery"

    If a group is dropped accidentally, recreate it using:
    ```bash
    nodetool updatecidrgroup <group_name> '<cidr_range>'
    ```

    Restore each CIDR range that was part of the original group.

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [listcidrgroups](listcidrgroups.md) | List all CIDR groups |
| [updatecidrgroup](updatecidrgroup.md) | Create or modify groups |
| [getcidrgroupsofip](getcidrgroupsofip.md) | Check IP group membership |
| [invalidatecidrpermissionscache](invalidatecidrpermissionscache.md) | Clear CIDR cache |
| [cidrfilteringstats](cidrfilteringstats.md) | View filtering statistics |
