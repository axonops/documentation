---
title: "Cassandra CQL Security"
description: "Cassandra CQL security features: role-based access control (RBAC) and dynamic data masking (DDM)."
meta:
  - name: keywords
    content: "CQL security, RBAC, data masking, Cassandra permissions, access control"
---

# CQL Security

CQL provides two categories of security features for controlling access to data:

---

## History and Evolution

Cassandra's security model has evolved significantly since its early releases, progressing from basic pluggable authentication to a comprehensive role-based system with fine-grained data protection.

### Timeline

| Version | Year | Feature | Reference |
|---------|------|---------|-----------|
| 0.6 | 2010 | Pluggable authentication framework (`IAuthenticator`) | [CASSANDRA-547](https://issues.apache.org/jira/browse/CASSANDRA-547) |
| 1.2 | 2012 | CQL-based authentication (`CREATE USER`, `GRANT`), `system_auth` keyspace | - |
| 2.2 | 2015 | Role-based access control (RBAC), `CREATE ROLE` replaces `CREATE USER` | [CASSANDRA-7653](https://issues.apache.org/jira/browse/CASSANDRA-7653) |
| 2.2 | 2015 | Auth subsystem rework (SASL, caching, UDF permissions) | [CASSANDRA-8394](https://issues.apache.org/jira/browse/CASSANDRA-8394) |
| 4.1 | 2022 | CQLSH authentication plugin support | [CEP-16](https://cwiki.apache.org/confluence/display/CASSANDRA/CEP-16%3A+Auth+Plugin+Support+for+CQLSH) |
| 5.0 | 2024 | Dynamic Data Masking (DDM) | [CEP-20](https://cwiki.apache.org/confluence/display/CASSANDRA/CEP-20%3A+Dynamic+Data+Masking), [CASSANDRA-17940](https://issues.apache.org/jira/browse/CASSANDRA-17940) |
| 5.0 | 2024 | Mutual TLS authentication (`MutualTlsAuthenticator`) | [CEP-34](https://cwiki.apache.org/confluence/display/CASSANDRA/CEP-34%3A+mTLS+based+client+and+internode+authenticators), [CASSANDRA-18554](https://issues.apache.org/jira/browse/CASSANDRA-18554) |

### Architecture Evolution

| Era | Versions | Model | Key Components |
|-----|----------|-------|----------------|
| Thrift | 0.6 – 1.1 | File-based | `SimpleAuthenticator`, properties files |
| CQL Users | 1.2 – 2.1 | User-based | `PasswordAuthenticator`, `CassandraAuthorizer`, `system_auth` keyspace, `CREATE USER` |
| RBAC | 2.2 – 4.x | Role-based | `CREATE ROLE`, role inheritance, UDF permissions, SASL |
| Enhanced | 5.0+ | Role + masking | Dynamic Data Masking, mTLS, SPIFFE identities, `ADD IDENTITY` |

### Key Design Decisions

The evolution reflects several architectural principles:

1. **Pluggability** - All components (authenticator, authorizer, role manager) are pluggable interfaces
2. **CQL Integration** - Security management through CQL statements rather than configuration files
3. **Role Unification** - Cassandra 2.2 unified users and groups into a single "role" concept
4. **Backward Compatibility** - `CREATE USER` syntax remains functional, internally creating roles
5. **Permission Granularity** - Progressive addition of resource types (keyspaces, tables, functions, MBeans)

---

## Features Overview

| Feature | Description | Version | Reference |
|---------|-------------|---------|-----------|
| [Role-Based Access Control](rbac.md) | Roles, permissions, and grants | 2.2+ | [CASSANDRA-7653](https://issues.apache.org/jira/browse/CASSANDRA-7653) |
| [Dynamic Data Masking](dynamic-data-masking.md) | Column-level data obfuscation | 5.0+ | [CEP-20](https://cwiki.apache.org/confluence/display/CASSANDRA/CEP-20%3A+Dynamic+Data+Masking) |

---

## Role-Based Access Control (RBAC)

RBAC controls who can access what resources through roles and permissions.

**Key concepts:**

- **Roles** - Represent users (with login) or permission groups (without login)
- **Permissions** - Actions allowed on resources (SELECT, MODIFY, CREATE, etc.)
- **Grants** - Associate permissions with roles, or roles with other roles

**Commands:**

| Command | Purpose |
|---------|---------|
| `CREATE ROLE` | Create user or permission group |
| `ALTER ROLE` | Modify role properties |
| `DROP ROLE` | Remove a role |
| `GRANT` | Assign permissions or role membership |
| `REVOKE` | Remove permissions or role membership |
| `LIST ROLES` | Display roles |
| `LIST PERMISSIONS` | Display permission grants |

See [Role-Based Access Control](rbac.md) for syntax and examples.

---

## Dynamic Data Masking (DDM)

DDM automatically obfuscates sensitive column data at read time based on user permissions.

**Key concepts:**

- **Masking functions** - Transform column values (mask_inner, mask_hash, etc.)
- **UNMASK permission** - Allows viewing original unmasked data
- **SELECT_MASKED permission** - Allows querying tables with masked columns

**Built-in masking functions:**

| Function | Effect |
|----------|--------|
| `mask_null()` | Replace with null |
| `mask_default()` | Replace with type default |
| `mask_replace(value)` | Replace with constant |
| `mask_inner(prefix, suffix)` | Mask inner characters |
| `mask_outer(prefix, suffix)` | Mask outer characters |
| `mask_hash([algorithm])` | Replace with hash |

See [Dynamic Data Masking](dynamic-data-masking.md) for syntax and examples.

---

## Configuration

Both RBAC and DDM require configuration in `cassandra.yaml`:

```yaml
# RBAC (required for role-based security)
authenticator: PasswordAuthenticator
authorizer: CassandraAuthorizer
role_manager: CassandraRoleManager

# DDM (optional, Cassandra 5.0+)
dynamic_data_masking_enabled: true
```

For detailed configuration guidance, see [Security Configuration](../../security/index.md).

---

## References

### JIRA Tickets

| Ticket | Description |
|--------|-------------|
| [CASSANDRA-547](https://issues.apache.org/jira/browse/CASSANDRA-547) | Original pluggable authentication framework (0.6) |
| [CASSANDRA-7653](https://issues.apache.org/jira/browse/CASSANDRA-7653) | Role-based access control (2.2) |
| [CASSANDRA-8394](https://issues.apache.org/jira/browse/CASSANDRA-8394) | Auth subsystem rework (2.2/3.0) |
| [CASSANDRA-17940](https://issues.apache.org/jira/browse/CASSANDRA-17940) | Dynamic Data Masking (5.0) |
| [CASSANDRA-18554](https://issues.apache.org/jira/browse/CASSANDRA-18554) | mTLS authenticators (5.0) |

### CEPs

| CEP | Description |
|-----|-------------|
| [CEP-16](https://cwiki.apache.org/confluence/display/CASSANDRA/CEP-16%3A+Auth+Plugin+Support+for+CQLSH) | CQLSH authentication plugin support |
| [CEP-20](https://cwiki.apache.org/confluence/display/CASSANDRA/CEP-20%3A+Dynamic+Data+Masking) | Dynamic Data Masking |
| [CEP-34](https://cwiki.apache.org/confluence/display/CASSANDRA/CEP-34%3A+mTLS+based+client+and+internode+authenticators) | mTLS authenticators |
| [CEP-50](https://cwiki.apache.org/confluence/display/CASSANDRA/CEP-50:+Authentication+Negotiation) | Authentication negotiation (in progress) |

---

## Related Documentation

| Topic | Description |
|-------|-------------|
| [Security Overview](../../security/index.md) | Security architecture and configuration |
| [Authentication](../../security/authentication/index.md) | Authenticator setup |
| [Authorization](../../security/authorization/index.md) | Authorizer setup and RBAC patterns |
