---
title: "Configuration"
description: "Cassandra configuration virtual tables. Query runtime settings, system properties, and system logs via CQL."
meta:
  - name: keywords
    content: "Cassandra settings, system properties, cassandra.yaml, runtime configuration, system logs"
---

# Configuration

The configuration virtual tables provide CQL access to runtime settings, JVM system properties, and system logs without requiring shell access.

---

## Overview

These tables expose Cassandra's configuration state:

| Table | Purpose |
|-------|---------|
| `settings` | Current cassandra.yaml settings (runtime values) |
| `system_properties` | JVM system properties |
| `system_logs` | Recent Cassandra log entries |

---

## settings

Exposes current Cassandra configuration settings as key-value pairs. This reflects the active runtime configuration, which may differ from cassandra.yaml if settings were changed dynamically.

### Schema

```sql
VIRTUAL TABLE system_views.settings (
    name text PRIMARY KEY,
    value text
) WITH comment = 'current settings';
```

| Column | Type | Description |
|--------|------|-------------|
| `name` | text | Configuration parameter name |
| `value` | text | Current value (as string) |

**Equivalent nodetool command:** `nodetool getconfig` (Cassandra 5.0+)

### Example Queries

```sql
-- All settings
SELECT name, value FROM system_views.settings;
```

Filter in application by name pattern (e.g., names containing 'compaction', 'timeout', 'heap').

### Common Configuration Checks

```sql
-- Cluster identification
SELECT name, value FROM system_views.settings
WHERE name IN ('cluster_name', 'num_tokens', 'partitioner');

-- Network configuration
SELECT name, value FROM system_views.settings
WHERE name IN ('listen_address', 'rpc_address', 'broadcast_address',
               'native_transport_port', 'storage_port');

-- Compaction settings
SELECT name, value FROM system_views.settings
WHERE name IN ('compaction_throughput_mb_per_sec', 'concurrent_compactors',
               'compaction_large_partition_warning_threshold_mb');

-- Read/write settings
SELECT name, value FROM system_views.settings
WHERE name IN ('read_request_timeout', 'write_request_timeout',
               'range_request_timeout', 'counter_write_request_timeout');

-- Hinted handoff
SELECT name, value FROM system_views.settings
WHERE name IN ('hinted_handoff_enabled', 'max_hint_window',
               'hinted_handoff_throttle_in_kb', 'max_hints_delivery_threads');

-- Commit log
SELECT name, value FROM system_views.settings
WHERE name IN ('commitlog_sync', 'commitlog_sync_period',
               'commitlog_segment_size', 'commitlog_total_space');

-- Memtable configuration
SELECT name, value FROM system_views.settings
WHERE name IN ('memtable_heap_space', 'memtable_offheap_space',
               'memtable_allocation_type', 'memtable_flush_writers');
```

### Configuration Audit

```sql
-- Check authentication/authorization settings
SELECT name, value FROM system_views.settings
WHERE name IN ('authenticator', 'authorizer', 'role_manager',
               'server_encryption_options', 'client_encryption_options');
```

**Security check:** Verify `authenticator` is not `AllowAllAuthenticator` and `authorizer` is not `AllowAllAuthorizer` in production.

---

## system_properties

Exposes JVM system properties relevant to Cassandra. Useful for verifying JVM configuration without shell access.

### Schema

```sql
VIRTUAL TABLE system_views.system_properties (
    name text PRIMARY KEY,
    value text
) WITH comment = 'Cassandra relevant system properties';
```

| Column | Type | Description |
|--------|------|-------------|
| `name` | text | System property name |
| `value` | text | Property value |

### Example Queries

```sql
-- All system properties
SELECT name, value FROM system_views.system_properties;
```

Filter in application by name prefix (e.g., 'java.', 'cassandra.', 'os.').

### Common Property Checks

```sql
-- JVM version
SELECT name, value FROM system_views.system_properties
WHERE name IN ('java.version', 'java.vendor', 'java.vm.name', 'java.vm.version');

-- Cassandra paths
SELECT name, value FROM system_views.system_properties
WHERE name IN ('cassandra.config', 'cassandra.storagedir', 'cassandra.logdir');

-- Operating system
SELECT name, value FROM system_views.system_properties
WHERE name IN ('os.name', 'os.version', 'os.arch');

-- User and file encoding
SELECT name, value FROM system_views.system_properties
WHERE name IN ('user.name', 'user.home', 'user.dir', 'file.encoding');
```

For GC settings and heap configuration, query all properties and filter in application.

---

## system_logs

Provides access to recent Cassandra log entries via CQL. Available in Cassandra 5.0+.

### Schema

```sql
VIRTUAL TABLE system_views.system_logs (
    timestamp timestamp,
    order_in_millisecond int,
    level text,
    logger text,
    message text,
    PRIMARY KEY (timestamp, order_in_millisecond)
) WITH CLUSTERING ORDER BY (order_in_millisecond ASC)
    AND comment = 'Cassandra logs';
```

| Column | Type | Description |
|--------|------|-------------|
| `timestamp` | timestamp | Log entry timestamp |
| `order_in_millisecond` | int | Ordering within same millisecond |
| `level` | text | Log level (ERROR, WARN, INFO, DEBUG, TRACE) |
| `logger` | text | Logger name (class/component) |
| `message` | text | Log message content |

### Example Queries

```sql
-- All log entries
SELECT timestamp, level, logger, message
FROM system_views.system_logs;

-- Error messages
SELECT timestamp, logger, message
FROM system_views.system_logs
WHERE level = 'ERROR';

-- Warnings and errors
SELECT timestamp, level, logger, message
FROM system_views.system_logs
WHERE level IN ('ERROR', 'WARN');
```

### Troubleshooting Queries

```sql
-- All log entries
SELECT timestamp, level, logger, message
FROM system_views.system_logs;
```

Filter in application by logger name or message content (e.g., 'Compaction', 'OutOfMemory').

---

## Monitoring Use Cases

### Configuration Drift Detection

```sql
-- Export current settings for comparison
-- Run on each node and compare results
SELECT name, value FROM system_views.settings;
```

Exclude node-specific values (containing 'address') when comparing across nodes.

### Security Audit

```sql
-- Authentication configuration
SELECT name, value FROM system_views.settings
WHERE name IN ('authenticator', 'authorizer', 'role_manager',
               'permissions_validity', 'credentials_validity');

-- Encryption settings
SELECT name, value FROM system_views.settings
WHERE name IN ('server_encryption_options', 'client_encryption_options',
               'native_transport_port_ssl');

-- Audit settings (Cassandra 4.0+)
SELECT name, value FROM system_views.settings
WHERE name IN ('audit_logging_options');
```

### Performance Configuration Review

```sql
-- Thread pool sizing (compare with thread_pools table)
SELECT name, value FROM system_views.settings
WHERE name IN ('concurrent_reads', 'concurrent_writes',
               'concurrent_counter_writes', 'concurrent_compactors');

-- Cache settings (compare with caches table)
SELECT name, value FROM system_views.settings
WHERE name IN ('key_cache_size_in_mb', 'row_cache_size_in_mb',
               'counter_cache_size_in_mb');

-- Throughput settings
SELECT name, value FROM system_views.settings
WHERE name IN ('compaction_throughput_mb_per_sec',
               'stream_throughput_outbound_megabits_per_sec',
               'inter_dc_stream_throughput_outbound_megabits_per_sec');
```

---

## Alerting Rules

### Configuration Warnings

```sql
-- Security concerns
SELECT name, value FROM system_views.settings
WHERE (name = 'authenticator' AND value = 'AllowAllAuthenticator')
   OR (name = 'authorizer' AND value = 'AllowAllAuthorizer');
```

### Error Log Monitoring

```sql
-- Recent errors (for alerting integration)
SELECT timestamp, logger, message
FROM system_views.system_logs
WHERE level = 'ERROR';
```

Filter in application for entries within the last 5 minutes.

---

## Comparison with nodetool

| Information | nodetool Command | Virtual Table Query |
|-------------|------------------|-------------------|
| View settings | `nodetool getconfig` | `SELECT * FROM system_views.settings` |
| Specific setting | `nodetool getconfig <name>` | `SELECT value FROM system_views.settings WHERE name = '<name>'` |
| System properties | N/A (check JVM) | `SELECT * FROM system_views.system_properties` |
| Logs | Filesystem access | `SELECT * FROM system_views.system_logs` |

---

## Limitations

1. **Settings table**
   - Read-only; use `nodetool setconfig` for runtime changes
   - Values are strings; type conversion may be needed
   - Some settings require restart to change

2. **System properties**
   - Reflects JVM startup properties
   - Cannot be modified at runtime

3. **System logs**
   - Limited retention (recent entries only)
   - May not include all log levels depending on configuration
   - For full log history, use filesystem access or log aggregation

---

## Related Documentation

- **[Virtual Tables Overview](index.md)** - Introduction to virtual tables
- **[Thread Pools](thread-pools.md)** - Thread pool configuration and metrics
- **[Caches](caches.md)** - Cache configuration and hit ratios
- **[Cassandra Configuration](../configuration/cassandra-yaml/index.md)** - Full configuration reference
