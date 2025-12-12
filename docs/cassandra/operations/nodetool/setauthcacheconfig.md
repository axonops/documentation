---
description: "Configure authentication cache settings in Cassandra using nodetool setauthcacheconfig."
meta:
  - name: keywords
    content: "nodetool setauthcacheconfig, auth cache, authentication cache, Cassandra"
---

# nodetool setauthcacheconfig

Modifies authentication cache configuration settings.

---

## Synopsis

```bash
nodetool [connection_options] setauthcacheconfig [options]
```

---

## Description

`nodetool setauthcacheconfig` modifies the configuration of Cassandra's authentication and authorization caches at runtime. This allows tuning cache behavior without restarting the node.

!!! warning "Non-Persistent Setting"

    Settings modified with this command are **not persisted** to configuration files. Changes will be lost on node restart. Update `cassandra.yaml` to make changes permanent.

---

## Options

| Option | Description |
|--------|-------------|
| `--credentials-validity <ms>` | Set credentials cache validity period |
| `--credentials-update-interval <ms>` | Set credentials cache update interval |
| `--credentials-max-entries <n>` | Set maximum credentials cache entries |
| `--permissions-validity <ms>` | Set permissions cache validity period |
| `--permissions-update-interval <ms>` | Set permissions cache update interval |
| `--permissions-max-entries <n>` | Set maximum permissions cache entries |
| `--roles-validity <ms>` | Set roles cache validity period |
| `--roles-update-interval <ms>` | Set roles cache update interval |
| `--roles-max-entries <n>` | Set maximum roles cache entries |

---

## Examples

### Increase Permissions Cache Validity

```bash
nodetool setauthcacheconfig --permissions-validity 5000
```

### Set Larger Credentials Cache

```bash
nodetool setauthcacheconfig --credentials-max-entries 5000
```

### Tune All Cache Settings

```bash
nodetool setauthcacheconfig \
    --credentials-validity 5000 \
    --credentials-update-interval 3000 \
    --credentials-max-entries 2000 \
    --permissions-validity 5000 \
    --permissions-update-interval 3000 \
    --permissions-max-entries 2000 \
    --roles-validity 5000 \
    --roles-update-interval 3000 \
    --roles-max-entries 2000
```

### Fast Permission Propagation

```bash
# Shorter validity for quick permission changes
nodetool setauthcacheconfig \
    --permissions-validity 1000 \
    --permissions-update-interval 500
```

### Performance-Optimized Settings

```bash
# Longer validity for reduced system_auth load
nodetool setauthcacheconfig \
    --credentials-validity 60000 \
    --credentials-update-interval 30000 \
    --permissions-validity 60000 \
    --permissions-update-interval 30000
```

---

## When to Use

### Performance Tuning

```bash
# Reduce system_auth load
nodetool setauthcacheconfig --credentials-validity 30000
```

Increase cache validity when:

- Authentication queries are causing high load
- system_auth keyspace is under pressure
- Quick permission propagation is not critical

### Security Response

```bash
# Decrease validity for faster permission revocation
nodetool setauthcacheconfig --permissions-validity 1000

# Invalidate existing cache
nodetool invalidatepermissionscache
```

During security incidents, reduce cache validity to ensure permission changes take effect quickly.

### High-Connection Scenarios

```bash
# Increase cache size for many concurrent connections
nodetool setauthcacheconfig \
    --credentials-max-entries 10000 \
    --permissions-max-entries 10000
```

When handling many concurrent authenticated connections, increase cache size to maintain hit rates.

---

## Configuration Guidelines

### Update Interval vs Validity

The update interval should be less than the validity period:

```bash
# Good: Update happens before expiry
nodetool setauthcacheconfig \
    --permissions-validity 5000 \
    --permissions-update-interval 3000

# Bad: Update interval >= validity (no background refresh)
nodetool setauthcacheconfig \
    --permissions-validity 5000 \
    --permissions-update-interval 6000
```

### Cache Sizing

Calculate max entries based on:

- Expected concurrent authenticated users
- Number of distinct roles/permissions
- Memory available for caching

```bash
# For 5000 concurrent users
nodetool setauthcacheconfig \
    --credentials-max-entries 6000 \
    --roles-max-entries 1000
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

    For persistent configuration, update these settings in `cassandra.yaml`:

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
