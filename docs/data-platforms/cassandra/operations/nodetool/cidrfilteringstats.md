---
title: "nodetool cidrfilteringstats"
description: "Display CIDR filtering statistics in Cassandra using nodetool cidrfilteringstats command."
meta:
  - name: keywords
    content: "nodetool cidrfilteringstats, CIDR filtering, network security, Cassandra"
search:
  boost: 3
---

# nodetool cidrfilteringstats

!!! info "Cassandra 5.0+"
    This command is available in Cassandra 5.0 and later.

Displays CIDR filtering statistics for the node.

---

## Synopsis

```bash
nodetool [connection_options] cidrfilteringstats
```

---

## Description

`nodetool cidrfilteringstats` displays statistics about CIDR-based filtering on the node. CIDR filtering allows restricting client connections based on IP address ranges, providing network-level access control for the Cassandra cluster.

This command shows metrics about CIDR authorization checks, cache performance, and filtering decisions.

---

## Output Fields

| Field | Description |
|-------|-------------|
| `Total Checks` | Total number of CIDR authorization checks performed |
| `Allowed` | Number of connections allowed by CIDR rules |
| `Denied` | Number of connections denied by CIDR rules |
| `Cache Hits` | Number of authorization results served from cache |
| `Cache Misses` | Number of authorization checks requiring full evaluation |

---

## Examples

### Basic Usage

```bash
nodetool cidrfilteringstats
```

**Sample output:**

```
CIDR Filtering Statistics:
Total Checks: 15432
Allowed: 14891
Denied: 541
Cache Hits: 14200
Cache Misses: 1232
```

---

## When to Use

### Monitor Access Control

```bash
# Check CIDR filtering activity
nodetool cidrfilteringstats
```

Use this command to:

- Monitor connection authorization patterns
- Identify potential unauthorized access attempts
- Verify CIDR rules are working as expected
- Assess cache efficiency for authorization checks

### Security Auditing

```bash
# Regular security monitoring
nodetool cidrfilteringstats
```

Track denied connections to detect potential security issues or misconfigured clients.

---

## Best Practices

!!! tip "Monitoring Guidelines"

    1. **Baseline metrics** - Establish normal patterns for allowed/denied ratios
    2. **Alert on anomalies** - Monitor for unusual spikes in denied connections
    3. **Cache efficiency** - High cache hit rates indicate efficient authorization
    4. **Regular review** - Periodically review filtering statistics for security compliance

!!! info "CIDR Filtering Requirements"

    CIDR filtering requires proper configuration in `cassandra.yaml`:

    - `cidr_authorizer` must be configured
    - CIDR groups must be defined
    - Role-to-CIDR mappings must be established

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [listcidrgroups](listcidrgroups.md) | List defined CIDR groups |
| [getcidrgroupsofip](getcidrgroupsofip.md) | Find CIDR groups for an IP |
| [updatecidrgroup](updatecidrgroup.md) | Modify CIDR groups |
| [dropcidrgroup](dropcidrgroup.md) | Remove CIDR groups |
| [invalidatecidrpermissionscache](invalidatecidrpermissionscache.md) | Clear CIDR cache |
| [reloadcidrgroupscache](reloadcidrgroupscache.md) | Reload CIDR groups |
