# nodetool updatecidrgroup

Creates or updates a CIDR group with specified IP ranges.

---

## Synopsis

```bash
nodetool [connection_options] updatecidrgroup <group_name> <cidr_ranges>
```

---

## Description

`nodetool updatecidrgroup` creates a new CIDR group or updates an existing one with the specified IP address ranges. CIDR groups define network ranges that can be associated with roles for IP-based access control.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `group_name` | Name for the CIDR group (alphanumeric and underscores) |
| `cidr_ranges` | Comma-separated list of CIDR ranges |

---

## CIDR Notation

CIDR (Classless Inter-Domain Routing) notation specifies IP ranges:

| CIDR | Range | Addresses |
|------|-------|-----------|
| `10.0.0.0/8` | 10.0.0.0 - 10.255.255.255 | 16,777,216 |
| `172.16.0.0/12` | 172.16.0.0 - 172.31.255.255 | 1,048,576 |
| `192.168.0.0/16` | 192.168.0.0 - 192.168.255.255 | 65,536 |
| `192.168.1.0/24` | 192.168.1.0 - 192.168.1.255 | 256 |
| `10.0.0.1/32` | 10.0.0.1 only | 1 |

---

## Examples

### Create New CIDR Group

```bash
nodetool updatecidrgroup office_network '192.168.1.0/24,192.168.2.0/24'
```

### Add Private Network Ranges

```bash
nodetool updatecidrgroup internal_network '10.0.0.0/8,172.16.0.0/12,192.168.0.0/16'
```

### Create Datacenter-Specific Group

```bash
nodetool updatecidrgroup dc_us_east '10.1.0.0/16,10.2.0.0/16'
```

### Single IP Address

```bash
nodetool updatecidrgroup admin_workstation '10.0.0.50/32'
```

### IPv6 Ranges

```bash
nodetool updatecidrgroup ipv6_network '2001:db8::/32,fd00::/8'
```

### Update Existing Group

```bash
# Add new range by redefining the group
nodetool updatecidrgroup office_network '192.168.1.0/24,192.168.2.0/24,192.168.3.0/24'
```

---

## When to Use

### Initial Setup

```bash
# Define network groups during cluster setup
nodetool updatecidrgroup app_servers '10.100.0.0/16'
nodetool updatecidrgroup monitoring '10.200.0.0/24'
nodetool updatecidrgroup admin '10.0.0.0/24'
```

### Network Expansion

```bash
# Add new subnet to existing group
nodetool listcidrgroups  # Check current ranges
nodetool updatecidrgroup app_servers '10.100.0.0/16,10.101.0.0/16'
```

### Security Segmentation

```bash
# Create groups for different access levels
nodetool updatecidrgroup readonly_apps '10.50.0.0/16'
nodetool updatecidrgroup write_apps '10.60.0.0/16'
nodetool updatecidrgroup admin_access '10.0.1.0/24'
```

---

## Best Practices

!!! tip "Naming Conventions"

    Use descriptive, consistent names:

    - `dc_<datacenter>` for datacenter-specific groups
    - `app_<application>` for application groups
    - `env_<environment>` for environment groups (prod, staging, dev)
    - `role_<role>` for access-level groups

!!! warning "Important Considerations"

    1. **Updates replace all ranges** - When updating, specify ALL desired ranges, not just new ones
    2. **Test before production** - Verify CIDR ranges in non-production environments
    3. **Document changes** - Maintain records of CIDR group modifications
    4. **Coordinate with network team** - Ensure CIDR ranges match actual network topology

!!! info "After Creating Groups"

    After creating CIDR groups, associate them with roles using CQL:
    ```sql
    ALTER ROLE app_user WITH ACCESS TO CIDR GROUP 'app_servers';
    ```

!!! danger "Broad Ranges"

    Avoid overly broad CIDR ranges that could allow unintended access:
    ```bash
    # Too broad - avoid
    nodetool updatecidrgroup all_access '0.0.0.0/0'

    # Better - specific ranges
    nodetool updatecidrgroup app_access '10.100.0.0/16'
    ```

---

## Verification

After creating or updating a CIDR group:

```bash
# List all groups to verify
nodetool listcidrgroups

# Test specific IP membership
nodetool getcidrgroupsofip 10.100.50.25

# Clear cache if needed
nodetool invalidatecidrpermissionscache
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [listcidrgroups](listcidrgroups.md) | List all CIDR groups |
| [getcidrgroupsofip](getcidrgroupsofip.md) | Check IP group membership |
| [dropcidrgroup](dropcidrgroup.md) | Remove CIDR groups |
| [invalidatecidrpermissionscache](invalidatecidrpermissionscache.md) | Clear CIDR cache |
| [reloadcidrgroupscache](reloadcidrgroupscache.md) | Reload from storage |
| [cidrfilteringstats](cidrfilteringstats.md) | View filtering statistics |
