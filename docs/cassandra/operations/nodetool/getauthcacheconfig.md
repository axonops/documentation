---
description: "Display authentication cache configuration in Cassandra using nodetool getauthcacheconfig."
meta:
  - name: keywords
    content: "nodetool getauthcacheconfig, auth cache, authentication cache, Cassandra security"
---

# nodetool getauthcacheconfig

Displays authentication cache configuration settings.

---

## Synopsis

```bash
nodetool [connection_options] getauthcacheconfig
```

---

## Description

`nodetool getauthcacheconfig` displays the current configuration of Cassandra's authentication and authorization caches. These caches improve performance by storing authentication credentials and authorization decisions, reducing the need to query system tables for every operation.

---

## Output Fields

| Field | Description |
|-------|-------------|
| `credentials_validity` | How long credential cache entries remain valid (ms) |
| `credentials_update_interval` | Background refresh interval for credentials (ms) |
| `credentials_cache_max_entries` | Maximum entries in credentials cache |
| `permissions_validity` | How long permission cache entries remain valid (ms) |
| `permissions_update_interval` | Background refresh interval for permissions (ms) |
| `permissions_cache_max_entries` | Maximum entries in permissions cache |
| `roles_validity` | How long role cache entries remain valid (ms) |
| `roles_update_interval` | Background refresh interval for roles (ms) |
| `roles_cache_max_entries` | Maximum entries in roles cache |

---

## Examples

### Basic Usage

```bash
nodetool getauthcacheconfig
```

**Sample output:**

```
Auth Cache Configuration:
  Credentials:
    Validity: 2000 ms
    Update Interval: 1000 ms
    Max Entries: 1000
  Permissions:
    Validity: 2000 ms
    Update Interval: 1000 ms
    Max Entries: 1000
  Roles:
    Validity: 2000 ms
    Update Interval: 1000 ms
    Max Entries: 1000
```

---

## When to Use

### Performance Tuning

```bash
# Check current cache settings
nodetool getauthcacheconfig
```

Review cache configuration when:

- Experiencing authentication latency
- Seeing high load on system_auth keyspace
- Planning changes to authentication patterns
- Troubleshooting authorization delays

### Security Configuration Audit

```bash
# Document auth cache settings
nodetool getauthcacheconfig > auth_cache_config.txt
```

During security audits, document cache validity periods to understand how quickly permission changes take effect.

### Before Modifying Settings

```bash
# Check current config before changes
nodetool getauthcacheconfig

# Make changes
nodetool setauthcacheconfig --permissions-validity 5000

# Verify changes
nodetool getauthcacheconfig
```

---

## Configuration Parameters Explained

### Validity Period

The validity period determines how long cached entries are considered valid:

- **Short validity** (e.g., 2000ms): Permission changes take effect quickly, but higher load on system tables
- **Long validity** (e.g., 60000ms): Better performance, but permission changes are delayed

### Update Interval

Controls background refresh of cache entries:

- Entries are refreshed before they expire
- Should be less than validity period
- Prevents authentication storms when entries expire

### Max Entries

Limits cache size to prevent memory issues:

- Set based on expected number of unique credentials/roles
- Entries are evicted using LRU when limit is reached
- Monitor cache efficiency to tune appropriately

---

## Best Practices

!!! tip "Cache Tuning Guidelines"

    1. **Balance security and performance** - Shorter validity means faster permission propagation but more system_auth load
    2. **Monitor cache effectiveness** - Track hit rates and latency
    3. **Size appropriately** - Max entries should accommodate typical concurrent users
    4. **Consider workload patterns** - High connection rate applications may need larger caches

!!! info "Default Values"

    Default cache settings are conservative (2000ms validity). Production environments may benefit from tuning based on:

    - Number of authenticated users
    - Connection rate patterns
    - Acceptable delay for permission changes
    - System_auth keyspace capacity

!!! warning "Security Trade-Off"

    Longer cache validity improves performance but delays permission revocations. Consider:

    - How quickly must permission changes take effect?
    - What is acceptable risk window for revoked credentials?
    - Balance against system_auth query load

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [setauthcacheconfig](setauthcacheconfig.md) | Modify cache settings |
| [invalidatecredentialscache](invalidatecredentialscache.md) | Clear credentials cache |
| [invalidatepermissionscache](invalidatepermissionscache.md) | Clear permissions cache |
| [invalidaterolescache](invalidaterolescache.md) | Clear roles cache |
