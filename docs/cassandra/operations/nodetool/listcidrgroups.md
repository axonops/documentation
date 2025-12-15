---
title: "nodetool listcidrgroups"
description: "List all CIDR groups configured in Cassandra using nodetool listcidrgroups."
meta:
  - name: keywords
    content: "nodetool listcidrgroups, CIDR groups, network security, Cassandra"
---

# nodetool listcidrgroups

Lists all defined CIDR groups in the cluster.

---

## Synopsis

```bash
nodetool [connection_options] listcidrgroups
```

---

## Description

`nodetool listcidrgroups` displays all CIDR groups defined in the cluster. CIDR groups are named collections of IP address ranges used for network-based access control.

CIDR groups can be assigned to roles to restrict which IP addresses can authenticate as those roles, providing an additional layer of security beyond username/password authentication.

---

## Output Format

The command displays each CIDR group with its associated IP ranges:

```
CIDR Group: <group_name>
  - <cidr_range_1>
  - <cidr_range_2>
```

---

## Examples

### Basic Usage

```bash
nodetool listcidrgroups
```

**Sample output:**

```
CIDR Groups:
  internal_network:
    - 10.0.0.0/8
    - 172.16.0.0/12
    - 192.168.0.0/16

  datacenter_us:
    - 10.1.0.0/16
    - 10.2.0.0/16

  datacenter_eu:
    - 10.3.0.0/16
    - 10.4.0.0/16

  vpn_clients:
    - 172.20.0.0/16
```

---

## When to Use

### Audit Access Control Configuration

```bash
# Review all CIDR-based access rules
nodetool listcidrgroups
```

Use this command to:

- Audit network-level access control configuration
- Verify CIDR groups before assigning to roles
- Document current security configuration
- Troubleshoot connection authorization issues

### Before Modifying CIDR Groups

```bash
# Check current groups before changes
nodetool listcidrgroups

# Then modify as needed
nodetool updatecidrgroup new_office '192.168.50.0/24'
```

---

## Best Practices

!!! tip "CIDR Group Management"

    1. **Use descriptive names** - Name groups by purpose (e.g., `datacenter_us`, `office_network`)
    2. **Document groups** - Maintain external documentation of CIDR group purposes
    3. **Review regularly** - Periodically audit groups for accuracy
    4. **Least privilege** - Define specific ranges rather than broad ones

!!! warning "Security Considerations"

    - CIDR groups are part of your security configuration
    - Changes affect which IPs can authenticate as specific roles
    - Test changes in non-production environments first
    - Coordinate with network team when defining ranges

---

## Configuration

CIDR groups are stored in the system tables and can be managed through:

- CQL commands (`CREATE CIDR GROUP`, `ALTER CIDR GROUP`)
- nodetool commands (`updatecidrgroup`, `dropcidrgroup`)

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [cidrfilteringstats](cidrfilteringstats.md) | View filtering statistics |
| [getcidrgroupsofip](getcidrgroupsofip.md) | Find groups containing an IP |
| [updatecidrgroup](updatecidrgroup.md) | Add or modify CIDR groups |
| [dropcidrgroup](dropcidrgroup.md) | Remove CIDR groups |
| [invalidatecidrpermissionscache](invalidatecidrpermissionscache.md) | Clear authorization cache |
| [reloadcidrgroupscache](reloadcidrgroupscache.md) | Reload groups from storage |
