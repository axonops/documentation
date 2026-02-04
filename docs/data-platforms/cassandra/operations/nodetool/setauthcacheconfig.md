---
title: "nodetool setauthcacheconfig"
description: "Configure authentication cache settings in Cassandra using nodetool setauthcacheconfig."
meta:
  - name: keywords
    content: "nodetool setauthcacheconfig, auth cache, authentication cache, Cassandra"
---

# nodetool setauthcacheconfig

!!! info "Cassandra 4.1+"
    This command is available in Cassandra 4.1 and later.

Modifies authentication cache configuration settings.

---

## Synopsis

```bash
nodetool [connection_options] setauthcacheconfig --cache-name <cache> [options]
```
See [connection options](index.md#connection-options) for connection options.

---

## Description

`nodetool setauthcacheconfig` modifies the configuration of a specific authentication or authorization cache at runtime. This allows tuning cache behavior without restarting the node.

!!! warning "Non-Persistent Setting"

    Settings modified with this command are **not persisted** to configuration files. Changes will be lost on node restart. Update `cassandra.yaml` to make changes permanent.

---

## Options

| Option | Description |
|--------|-------------|
| `--cache-name <name>` | **Required.** Cache to configure: `CredentialsCache`, `PermissionsCache`, `RolesCache`, or `NetworkPermissionsCache` |
| `--validity-period <ms>` | Set cache validity period in milliseconds |
| `--update-interval <ms>` | Set cache update interval in milliseconds |
| `--max-entries <n>` | Set maximum cache entries |
| `--enable-active-update` | Enable active update for the cache |
| `--disable-active-update` | Disable active update for the cache |

---

## Examples

### Increase Permissions Cache Validity

```bash
nodetool setauthcacheconfig --cache-name PermissionsCache --validity-period 5000
```

### Set Larger Credentials Cache

```bash
nodetool setauthcacheconfig --cache-name CredentialsCache --max-entries 5000
```

### Tune Credentials Cache Settings

```bash
nodetool setauthcacheconfig --cache-name CredentialsCache \
    --validity-period 5000 \
    --update-interval 3000 \
    --max-entries 2000
```

### Fast Permission Propagation

```bash
# Shorter validity for quick permission changes
nodetool setauthcacheconfig --cache-name PermissionsCache \
    --validity-period 1000 \
    --update-interval 500
```

### Enable Active Update

```bash
# Enable background refresh before cache entries expire
nodetool setauthcacheconfig --cache-name CredentialsCache --enable-active-update
```

---

## When to Use

### Performance Tuning

```bash
# Reduce system_auth load
nodetool setauthcacheconfig --cache-name CredentialsCache --validity-period 30000
```

Increase cache validity when:

- Authentication queries are causing high load
- system_auth keyspace is under pressure
- Quick permission propagation is not critical

### Security Response

```bash
# Decrease validity for faster permission revocation
nodetool setauthcacheconfig --cache-name PermissionsCache --validity-period 1000

# Invalidate existing cache
nodetool invalidatepermissionscache
```

During security incidents, reduce cache validity to ensure permission changes take effect quickly.

### High-Connection Scenarios

```bash
# Increase cache size for many concurrent connections
nodetool setauthcacheconfig --cache-name CredentialsCache --max-entries 10000
nodetool setauthcacheconfig --cache-name PermissionsCache --max-entries 10000
```

When handling many concurrent authenticated connections, increase cache size to maintain hit rates.

---

## Configuration Guidelines

### Update Interval vs Validity

The update interval should be less than the validity period:

```bash
# Good: Update happens before expiry
nodetool setauthcacheconfig --cache-name PermissionsCache \
    --validity-period 5000 \
    --update-interval 3000

# Bad: Update interval >= validity (no background refresh)
nodetool setauthcacheconfig --cache-name PermissionsCache \
    --validity-period 5000 \
    --update-interval 6000
```

### Cache Sizing

Calculate max entries based on:

- Expected concurrent authenticated users
- Number of distinct roles/permissions
- Memory available for caching

```bash
# For 5000 concurrent users
nodetool setauthcacheconfig --cache-name CredentialsCache --max-entries 6000
nodetool setauthcacheconfig --cache-name RolesCache --max-entries 1000
```

---

## Best Practices

!!! tip "Tuning Recommendations"

    1. **Start conservative** - Begin with default values
    2. **Monitor metrics** - Track cache hit rates and latency
    3. **Adjust incrementally** - Make small changes and observe
    4. **Document changes** - Record why settings were modified

!!! warning "Important Considerations"

    - Changes apply only to the target node
    - Run on all nodes for cluster-wide consistency
    - Settings lost on restart unless also updated in `cassandra.yaml`
    - Very short validity periods increase system_auth load significantly

!!! info "Corresponding cassandra.yaml Settings"

    The configuration parameter names vary by Cassandra version:

    | Cassandra Version | Parameter Pattern | Example |
    |-------------------|-------------------|---------|
    | Pre-4.1 | `*_validity_in_ms`, `*_update_interval_in_ms`, `*_cache_max_entries` | `credentials_validity_in_ms: 2000` |
    | 4.1+ | `*_validity`, `*_update_interval`, `*_cache_max_entries`, `*_cache_active_update` | `credentials_validity: 2s` |

    **Pre-4.1 example:**

    ```yaml
    credentials_validity_in_ms: 5000
    credentials_update_interval_in_ms: 3000
    credentials_cache_max_entries: 1000
    permissions_validity_in_ms: 5000
    permissions_update_interval_in_ms: 3000
    permissions_cache_max_entries: 1000
    roles_validity_in_ms: 5000
    roles_update_interval_in_ms: 3000
    roles_cache_max_entries: 1000
    ```

    **4.1+ example (with duration literals):**

    ```yaml
    credentials_validity: 5s
    credentials_update_interval: 3s
    credentials_cache_max_entries: 1000
    credentials_cache_active_update: true
    permissions_validity: 5s
    permissions_update_interval: 3s
    permissions_cache_max_entries: 1000
    permissions_cache_active_update: true
    roles_validity: 5s
    roles_update_interval: 3s
    roles_cache_max_entries: 1000
    roles_cache_active_update: true
    ```

---

## Verification

After making changes:

```bash
# Verify new settings
nodetool getauthcacheconfig

# Monitor cache performance
nodetool info | grep -i cache
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [getauthcacheconfig](getauthcacheconfig.md) | View current settings |
| [invalidatecredentialscache](invalidatecredentialscache.md) | Clear credentials cache |
| [invalidatepermissionscache](invalidatepermissionscache.md) | Clear permissions cache |
| [invalidaterolescache](invalidaterolescache.md) | Clear roles cache |