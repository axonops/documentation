---
title: "nodetool getcidrgroupsofip"
description: "Find CIDR groups containing an IP address using nodetool getcidrgroupsofip command."
meta:
  - name: keywords
    content: "nodetool getcidrgroupsofip, CIDR groups, IP address, Cassandra network"
search:
  boost: 3
---

# nodetool getcidrgroupsofip

!!! info "Cassandra 5.0+"
    This command is available in Cassandra 5.0 and later.

Finds which CIDR groups contain a specific IP address.

---

## Synopsis

```bash
nodetool [connection_options] getcidrgroupsofip <ip_address>
```

---

## Description

`nodetool getcidrgroupsofip` determines which CIDR groups include the specified IP address. This command is useful for troubleshooting authorization issues and verifying that IP addresses are correctly categorized.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `ip_address` | The IP address to look up (IPv4 or IPv6) |

---

## Examples

### Basic Usage

```bash
nodetool getcidrgroupsofip 10.1.50.100
```

**Sample output:**

```
CIDR groups containing IP 10.1.50.100:
  - internal_network
  - datacenter_us
```

### Check External IP

```bash
nodetool getcidrgroupsofip 203.0.113.50
```

**Sample output (if not in any group):**

```
CIDR groups containing IP 203.0.113.50:
  (none)
```

### IPv6 Address

```bash
nodetool getcidrgroupsofip 2001:db8::1
```

---

## When to Use

### Troubleshoot Connection Issues

```bash
# Check if client IP is in expected groups
nodetool getcidrgroupsofip 10.5.20.100
```

When clients receive authorization errors, use this command to verify the client's IP address belongs to the expected CIDR groups.

### Verify CIDR Configuration

```bash
# Verify IP categorization after changes
nodetool updatecidrgroup new_subnet '10.5.0.0/16'
nodetool getcidrgroupsofip 10.5.20.100
```

After modifying CIDR groups, verify that IP addresses are categorized correctly.

### Security Auditing

```bash
# Check what groups an IP belongs to
nodetool getcidrgroupsofip 192.168.1.100
```

Audit which access groups apply to specific IP addresses during security reviews.

---

## Best Practices

!!! tip "Troubleshooting Tips"

    1. **Test from client perspective** - Use the actual client IP address
    2. **Consider NAT** - The IP address must be what Cassandra sees, not the original source
    3. **Check overlapping groups** - An IP may belong to multiple groups
    4. **Verify after changes** - Always verify IP categorization after modifying CIDR groups

!!! info "IP Address Format"

    - Use standard notation for IPv4 (e.g., `192.168.1.100`)
    - Use standard notation for IPv6 (e.g., `2001:db8::1`)
    - Do not include port numbers
    - Do not include CIDR notation (this looks up a single IP)

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [listcidrgroups](listcidrgroups.md) | List all CIDR groups |
| [cidrfilteringstats](cidrfilteringstats.md) | View filtering statistics |
| [updatecidrgroup](updatecidrgroup.md) | Modify CIDR groups |
| [dropcidrgroup](dropcidrgroup.md) | Remove CIDR groups |
| [invalidatecidrpermissionscache](invalidatecidrpermissionscache.md) | Clear CIDR cache |
