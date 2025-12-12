---
description: "Cassandra network security. Firewall rules, port configuration, and network isolation."
meta:
  - name: keywords
    content: "network security, Cassandra firewall, port security, network isolation"
---

# Network Authorization

Cassandra provides network-level authorization to restrict client access based on datacenter location or IP address ranges.

## Overview

| Feature | Version | Purpose |
|---------|---------|---------|
| `network_authorizer` | Cassandra 4.0+ | Restrict role access to specific datacenters |
| `cidr_authorizer` | Cassandra 5.0+ | Restrict role access based on client IP ranges |

---

## Datacenter Authorization (Cassandra 4.0+)

The `network_authorizer` setting controls which datacenters a role can access. This feature restricts client connections to specific datacenters within a cluster.

### Configuration

```yaml
# cassandra.yaml

# Options:
# - AllowAllNetworkAuthorizer: No restrictions (default)
# - CassandraNetworkAuthorizer: Datacenter-based restrictions
network_authorizer: CassandraNetworkAuthorizer
```

**Requirements:**

- `authenticator` must be set to `PasswordAuthenticator`
- Increase `system_auth` keyspace replication factor for high availability

### Granting Datacenter Access

```sql
-- Grant access to all datacenters
CREATE ROLE app_user WITH PASSWORD = 'password'
    AND LOGIN = true
    AND ACCESS TO ALL DATACENTERS;

-- Restrict to specific datacenters
CREATE ROLE dc1_user WITH PASSWORD = 'password'
    AND LOGIN = true
    AND ACCESS TO DATACENTERS {'dc1'};

-- Multiple datacenters
CREATE ROLE multi_dc_user WITH PASSWORD = 'password'
    AND LOGIN = true
    AND ACCESS TO DATACENTERS {'dc1', 'dc2'};
```

### Modifying Datacenter Access

```sql
-- Grant access to additional datacenters
ALTER ROLE app_user WITH ACCESS TO DATACENTERS {'dc1', 'dc2', 'dc3'};

-- Grant access to all datacenters
ALTER ROLE app_user WITH ACCESS TO ALL DATACENTERS;
```

### Default Behavior

Omitting the datacenter clause from `CREATE ROLE` grants access to all datacenters by default.

---

## CIDR Authorization (Cassandra 5.0+)

The `cidr_authorizer` setting restricts database access based on client IP address ranges defined using CIDR notation. This feature prevents unauthorized access from unexpected network locations.

### Configuration

```yaml
# cassandra.yaml

# Options:
# - AllowAllCIDRAuthorizer: No restrictions (default)
# - CassandraCIDRAuthorizer: CIDR-based restrictions
cidr_authorizer: CassandraCIDRAuthorizer

# Enable CIDR checks for superusers (default: false)
cidr_checks_for_superusers: false

# Authorizer mode:
# - MONITOR: Log violations without enforcement
# - ENFORCE: Reject unauthorized access
cidr_authorizer_mode: MONITOR

# Cache settings
cidr_groups_cache_refresh_interval: 5
ip_cache_max_size: 100
```

**Requirements:**

- `authenticator` must be set to `PasswordAuthenticator`
- Increase `system_auth` keyspace replication factor for high availability
- CIDR checks do not apply to JMX connections

### Authorizer Modes

| Mode | Behavior |
|------|----------|
| `MONITOR` | Log unauthorized access attempts without blocking (default) |
| `ENFORCE` | Reject connections from unauthorized CIDR groups |

The `MONITOR` mode allows validation of CIDR rules before enforcement.

### Managing CIDR Groups

CIDR groups are stored in the `system_auth.cidr_groups` table.

```sql
-- View existing CIDR groups
SELECT * FROM system_auth.cidr_groups;
```

Use `nodetool` to manage CIDR groups:

```bash
# List available CIDR groups
nodetool listcidrgroups

# Reload CIDR groups cache
nodetool reloadcidrgroupscache

# Get CIDR groups for an IP address
nodetool getcidrgroupsofip 192.168.1.100

# View CIDR filtering statistics
nodetool cidrfilteringstats
```

### Granting CIDR Access

```sql
-- Grant access from specific CIDR groups
CREATE ROLE regional_user WITH PASSWORD = 'password'
    AND LOGIN = true
    AND ACCESS FROM CIDRS {'region1', 'region2'};

-- Grant access from all CIDR groups
CREATE ROLE global_user WITH PASSWORD = 'password'
    AND LOGIN = true
    AND ACCESS FROM ALL CIDRS;
```

### Modifying CIDR Access

```sql
-- Update CIDR access
ALTER ROLE regional_user WITH ACCESS FROM CIDRS {'region1'};

-- Grant access from all CIDR groups
ALTER ROLE regional_user WITH ACCESS FROM ALL CIDRS;
```

### Default Behavior

Omitting the CIDR clause from `CREATE ROLE` grants access from all CIDR groups by default.

---

## Combining Network Authorizers

Datacenter authorization and CIDR authorization can be used together for defense in depth.

```sql
-- Restrict by both datacenter and CIDR
CREATE ROLE restricted_user WITH PASSWORD = 'password'
    AND LOGIN = true
    AND ACCESS TO DATACENTERS {'dc1'}
    AND ACCESS FROM CIDRS {'office_network'};
```

---

## System Tables

| Table | Purpose |
|-------|---------|
| `system_auth.network_permissions` | Datacenter access permissions |
| `system_auth.cidr_groups` | CIDR group definitions |
| `system_auth.cidr_permissions` | CIDR access permissions |

---

## Best Practices

- **Test in MONITOR mode**: Validate CIDR rules before switching to ENFORCE mode
- **Increase replication**: Set `system_auth` keyspace replication factor to match cluster size
- **Plan for failover**: Ensure roles have access to disaster recovery datacenters
- **Document CIDR groups**: Maintain clear documentation of IP ranges per group
- **Regular audits**: Review network permissions periodically

---

## Next Steps

- **[Authentication](../authentication/index.md)** - User authentication
- **[Authorization](../authorization/index.md)** - Role-based access control
- **[Encryption](../encryption/index.md)** - SSL/TLS configuration
- **[Security Overview](../index.md)** - Security guide
