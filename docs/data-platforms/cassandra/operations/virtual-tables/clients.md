---
title: "Clients"
description: "Cassandra clients and queries virtual tables. Monitor connected clients, drivers, and active queries."
meta:
  - name: keywords
    content: "Cassandra clients, connected clients, active queries, driver monitoring"
---

# Clients

The client-related virtual tables provide visibility into connected CQL clients and currently executing queries.

---

## clients

Shows all currently connected CQL clients with connection details.

### Schema

```sql
VIRTUAL TABLE system_views.clients (
    address inet,
    port int,
    authentication_metadata map<text, text>,
    authentication_mode text,
    client_options map<text, text>,
    connection_stage text,
    driver_name text,
    driver_version text,
    hostname text,
    keyspace_name text,
    protocol_version int,
    request_count bigint,
    ssl_cipher_suite text,
    ssl_enabled boolean,
    ssl_protocol text,
    username text,
    PRIMARY KEY (address, port)
) WITH CLUSTERING ORDER BY (port ASC)
```

| Column | Type | Description |
|--------|------|-------------|
| `address` | inet | Client IP address |
| `port` | int | Client source port |
| `hostname` | text | Client hostname (if resolvable) |
| `username` | text | Authenticated username |
| `authentication_mode` | text | Authentication mode used |
| `authentication_metadata` | map | Additional authentication metadata |
| `keyspace_name` | text | Current keyspace |
| `driver_name` | text | Client driver name |
| `driver_version` | text | Driver version |
| `protocol_version` | int | Native protocol version (3, 4, 5) |
| `request_count` | bigint | Total requests from this connection |
| `connection_stage` | text | Connection state |
| `ssl_enabled` | boolean | TLS encryption enabled |
| `ssl_protocol` | text | TLS protocol version (TLSv1.2, TLSv1.3) |
| `ssl_cipher_suite` | text | TLS cipher suite |
| `client_options` | map | Driver-reported connection options |

**Equivalent nodetool command:** `nodetool clientstats`

### Basic Queries

```sql
-- All connected clients
SELECT address, port, username, driver_name, driver_version, request_count
FROM system_views.clients;

-- Clients with username
SELECT address, username, keyspace_name, request_count
FROM system_views.clients;

-- All connections
SELECT address, port, username
FROM system_views.clients;
```

### Security Monitoring

```sql
-- All connections with TLS status
SELECT address, port, username, ssl_enabled, ssl_protocol, ssl_cipher_suite
FROM system_views.clients;
```

Filter results in application for non-TLS connections (`ssl_enabled = false`) or weak ciphers.

### Driver Version Monitoring

```sql
-- All driver versions in use
SELECT address, driver_name, driver_version, protocol_version
FROM system_views.clients;
```

Aggregate driver versions in application logic.

### High-Activity Clients

```sql
-- All connections with request counts
SELECT address, port, username, request_count
FROM system_views.clients;

-- Connections with no activity (potentially stale)
SELECT address, port, username, request_count
FROM system_views.clients
WHERE request_count < 10;
```

---

## queries

Shows currently executing queries on this node.

### Schema

```sql
VIRTUAL TABLE system_views.queries (
    thread_id text PRIMARY KEY,
    queued_micros bigint,
    running_micros bigint,
    task text
)
```

| Column | Type | Description |
|--------|------|-------------|
| `thread_id` | text | Executing thread identifier |
| `task` | text | Query description |
| `running_micros` | bigint | Time executing (microseconds) |
| `queued_micros` | bigint | Time spent waiting in queue (microseconds) |

### Basic Queries

```sql
-- All active queries
SELECT thread_id, task, running_micros / 1000 AS running_ms
FROM system_views.queries;

-- Long-running queries (> 1 second)
SELECT thread_id, task, running_micros / 1000000 AS running_seconds
FROM system_views.queries
WHERE running_micros > 1000000;

-- Queries that waited in queue
SELECT thread_id, task,
       queued_micros / 1000 AS queued_ms,
       running_micros / 1000 AS running_ms
FROM system_views.queries
WHERE queued_micros > 10000;
```

### Identifying Slow Queries

```sql
-- Find queries running > 5 seconds (potential problems)
SELECT thread_id, task, running_micros / 1000000.0 AS running_seconds
FROM system_views.queries
WHERE running_micros > 5000000;
```

!!! note "Query Visibility"
    The `queries` table shows point-in-time active queries. Fast queries may complete before being captured. For historical query analysis, use query tracing or full query logging.

---

## Monitoring Use Cases

### Connection Pool Health

```sql
-- All connections with hostname for categorization
SELECT address, hostname, username, request_count
FROM system_views.clients;
```

Group by hostname pattern in application logic to categorize connections.

### Security Audit

```sql
-- All clients with usernames
SELECT address, username, driver_name, request_count
FROM system_views.clients;

-- All client addresses
SELECT address, port, username
FROM system_views.clients;
```

Filter in application for non-application users and unexpected network ranges.

### Capacity Planning

```sql
-- All connections with request counts
SELECT address, port, request_count
FROM system_views.clients;
```

Use `COUNT(*)` in application to get total connections. Sum request_count values in application for total requests.

---

## Alerting Rules

### Unencrypted Connections

```sql
-- Alert: Non-TLS connections in production
SELECT address, username
FROM system_views.clients
WHERE ssl_enabled = false;
```

### Outdated Drivers

```sql
-- All driver versions
SELECT address, driver_name, driver_version
FROM system_views.clients;
```

Check driver versions in application for outdated clients.

### Long-Running Queries

```sql
-- Active queries with execution time
SELECT thread_id, task, running_micros
FROM system_views.queries;
```

Alert when `running_micros > 30000000` (30 seconds).

### Connection Spike

```sql
-- Compare against baseline (application logic needed)
SELECT COUNT(*) AS current_connections
FROM system_views.clients;
-- Alert if significantly above normal
```

---

## Security Cache Tables

Related tables show cached authentication/authorization state:

### credentials_cache_keys

```sql
-- Roles with cached credentials
SELECT role FROM system_views.credentials_cache_keys;
```

### permissions_cache_keys

```sql
-- Cached permission entries
SELECT role, resource FROM system_views.permissions_cache_keys;
```

### roles_cache_keys

```sql
-- Roles in the role cache
SELECT role FROM system_views.roles_cache_keys;
```

### network_permissions_cache_keys

```sql
-- Network permission cache entries
SELECT role FROM system_views.network_permissions_cache_keys;
```

### jmx_permissions_cache_keys

```sql
-- JMX permission cache entries
SELECT role FROM system_views.jmx_permissions_cache_keys;
```

These tables are useful for:
- Verifying cache population after authentication changes
- Debugging permission issues
- Understanding cache invalidation behavior

---

## Related Documentation

- **[Virtual Tables Overview](index.md)** - Introduction to virtual tables
- **[Thread Pools](thread-pools.md)** - Request processing capacity
- **[Security - Authentication](../../security/authentication/index.md)** - Authentication configuration
- **[nodetool clientstats](../nodetool/clientstats.md)** - Command-line equivalent
