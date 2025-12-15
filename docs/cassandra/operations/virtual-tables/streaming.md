---
title: "Streaming"
description: "Cassandra streaming virtual table. Monitor data streaming operations for repair, bootstrap, and decommission."
meta:
  - name: keywords
    content: "Cassandra streaming, data streaming, bootstrap, decommission, repair streaming"
---

# Streaming

The `streaming` virtual table provides real-time visibility into data streaming operations, including repair, bootstrap, decommission, and rebuild operations.

---

## Overview

Streaming is Cassandra's mechanism for bulk data transfer between nodes. It occurs during:

- **Repair** - Sending data to synchronize replicas
- **Bootstrap** - New node receiving data for its token ranges
- **Decommission** - Node transferring data before leaving cluster
- **Rebuild** - Node acquiring data from other replicas
- **Move** - Node transferring data during token rebalancing

The `streaming` virtual table exposes detailed progress metrics for all active and recent streaming sessions.

**Equivalent nodetool command:** `nodetool netstats`

---

## streaming

### Schema

```sql
VIRTUAL TABLE system_views.streaming (
    id timeuuid PRIMARY KEY,
    bytes_received bigint,
    bytes_sent bigint,
    bytes_to_receive bigint,
    bytes_to_send bigint,
    duration_millis bigint,
    failure_cause text,
    files_received bigint,
    files_sent bigint,
    files_to_receive bigint,
    files_to_send bigint,
    follower boolean,
    last_updated_at timestamp,
    operation text,
    peers frozen<list<text>>,
    progress_percentage float,
    status text,
    status_failure_timestamp timestamp,
    status_init_timestamp timestamp,
    status_start_timestamp timestamp,
    status_success_timestamp timestamp,
    success_message text
)
```

### Column Reference

| Column | Type | Description |
|--------|------|-------------|
| `id` | timeuuid | Unique streaming session identifier |
| `operation` | text | Type: Repair, Bootstrap, Decommission, Rebuild, Move |
| `status` | text | Current status (INIT, START, SUCCESS, FAILURE) |
| `peers` | list | Remote nodes involved in streaming |
| `follower` | boolean | True if this node is receiving; false if initiating |
| `progress_percentage` | float | Overall completion percentage (0.0-100.0) |
| `bytes_to_send` | bigint | Total bytes scheduled to send |
| `bytes_sent` | bigint | Bytes already sent |
| `bytes_to_receive` | bigint | Total bytes scheduled to receive |
| `bytes_received` | bigint | Bytes already received |
| `files_to_send` | bigint | Total files scheduled to send |
| `files_sent` | bigint | Files already sent |
| `files_to_receive` | bigint | Total files scheduled to receive |
| `files_received` | bigint | Files already received |
| `duration_millis` | bigint | Total duration (milliseconds) |
| `failure_cause` | text | Error message if failed |
| `success_message` | text | Completion message if successful |
| `status_*_timestamp` | timestamp | State transition timestamps |
| `last_updated_at` | timestamp | Last progress update time |

---

## Status Values

| Status | Description |
|--------|-------------|
| `INIT` | Streaming session initialized |
| `START` | Streaming in progress |
| `SUCCESS` | Streaming completed successfully |
| `FAILURE` | Streaming failed with error |

---

## Example Queries

### Active Streaming Operations

```sql
-- All active streaming sessions
SELECT id, operation, status, progress_percentage,
       bytes_sent / 1048576 AS sent_mb,
       bytes_to_send / 1048576 AS total_mb
FROM system_views.streaming
WHERE status IN ('INIT', 'START');

-- Streaming progress
SELECT id, operation, peers, progress_percentage,
       bytes_sent, bytes_received, duration_millis
FROM system_views.streaming
WHERE status = 'START';
```

Calculate throughput in application: `(bytes_sent + bytes_received) / duration_millis * 1000`.

### Bootstrap Monitoring

```sql
-- Monitor bootstrap progress
SELECT id, progress_percentage,
       bytes_received / 1073741824 AS received_gb,
       bytes_to_receive / 1073741824 AS total_gb,
       files_received, files_to_receive,
       duration_millis / 60000 AS minutes_elapsed
FROM system_views.streaming
WHERE operation = 'Bootstrap'
  AND status IN ('INIT', 'START');
```

### Decommission Monitoring

```sql
-- Monitor decommission progress
SELECT id, progress_percentage,
       bytes_sent / 1073741824 AS sent_gb,
       bytes_to_send / 1073741824 AS total_gb,
       peers
FROM system_views.streaming
WHERE operation = 'Decommission'
  AND status IN ('INIT', 'START');
```

### Repair Streaming

```sql
-- Repair streaming sessions
SELECT id, peers, progress_percentage,
       bytes_sent / 1048576 AS sent_mb,
       bytes_received / 1048576 AS received_mb,
       duration_millis / 1000 AS duration_sec
FROM system_views.streaming
WHERE operation = 'Repair';
```

### Historical Analysis

```sql
-- Recent streaming operations
SELECT operation, status, peers,
       bytes_sent / 1073741824 AS sent_gb,
       bytes_received / 1073741824 AS received_gb,
       duration_millis / 60000 AS duration_min,
       status_init_timestamp
FROM system_views.streaming;

-- Failed streaming sessions
SELECT id, operation, peers, failure_cause,
       status_failure_timestamp
FROM system_views.streaming
WHERE status = 'FAILURE';
```

### File vs Byte Progress

```sql
-- Detailed file and byte progress
SELECT id, operation,
       files_sent, files_to_send,
       files_received, files_to_receive,
       bytes_sent, bytes_to_send,
       bytes_received, bytes_to_receive
FROM system_views.streaming
WHERE status = 'START';
```

Format progress strings in application (e.g., `files_sent/files_to_send`).

---

## Monitoring Use Cases

### Bootstrap Progress Dashboard

```sql
-- Comprehensive bootstrap status
SELECT
    id,
    progress_percentage,
    bytes_received / 1073741824.0 AS received_gb,
    bytes_to_receive / 1073741824.0 AS total_gb,
    files_received, files_to_receive,
    duration_millis / 60000 AS elapsed_minutes
FROM system_views.streaming
WHERE operation = 'Bootstrap'
  AND status IN ('INIT', 'START');
```

Estimate remaining time in application: `duration_millis / progress_percentage * (100 - progress_percentage) / 60000` (when progress > 0).

### Throughput Analysis

```sql
-- Streaming throughput by peer
SELECT peers, operation,
       (bytes_sent + bytes_received) / 1048576 AS total_mb,
       duration_millis / 1000 AS duration_sec
FROM system_views.streaming
WHERE status = 'SUCCESS'
  AND duration_millis > 0;
```

Calculate MB/s in application: `total_mb / duration_sec`.

---

## Alerting Rules

### Stalled Streaming

```sql
-- Alert: Streaming not progressing
SELECT id, operation, progress_percentage,
       duration_millis / 60000 AS duration_minutes,
       last_updated_at
FROM system_views.streaming
WHERE status = 'START'
  AND duration_millis > 1800000;  -- > 30 minutes
```

Alert when `last_updated_at` shows no recent progress (> 5 minutes old).

### Failed Streaming

```sql
-- Alert: Recent streaming failures
SELECT id, operation, peers, failure_cause,
       status_failure_timestamp
FROM system_views.streaming
WHERE status = 'FAILURE';
```

Filter in application for failures within the last hour.

### Long-Running Operations

```sql
-- Alert: Operations running too long
SELECT id, operation, progress_percentage,
       duration_millis / 3600000 AS duration_hours
FROM system_views.streaming
WHERE status IN ('INIT', 'START');
```

Alert when `duration_millis > 14400000` (4 hours).

---

## Troubleshooting

### Slow Streaming

**Symptoms:**
- Low throughput (MB/s)
- High duration for data volume

**Investigation:**
```sql
-- Calculate effective throughput
SELECT operation, peers,
       (bytes_sent + bytes_received) / 1048576 AS total_mb,
       duration_millis / 1000 AS seconds
FROM system_views.streaming
WHERE status IN ('START', 'SUCCESS')
  AND duration_millis > 0;
```

Calculate MB/s as `total_mb / seconds`. Low values indicate slow streaming.

**Common Causes:**
- Network bandwidth constraints
- High disk I/O on source or target
- Cross-datacenter streaming
- Compaction competing for resources

**Resolution:**
- Check network connectivity between peers
- Review `stream_throughput_outbound` setting
- Consider `inter_dc_stream_throughput_outbound` for cross-DC
- Monitor disk I/O during streaming

### Streaming Failures

**Symptoms:**
- Status = 'FAILURE'
- `failure_cause` populated

**Investigation:**
```sql
SELECT id, operation, peers, failure_cause,
       progress_percentage, status_failure_timestamp
FROM system_views.streaming
WHERE status = 'FAILURE';
```

Sort by `status_failure_timestamp` in application to see most recent failures first.

**Common Causes:**
- Network timeouts (increase `streaming_socket_timeout_in_ms`)
- Out of disk space on receiving node
- Node restart during streaming
- SSL/TLS handshake failures

### Bootstrap Taking Too Long

**Symptoms:**
- Bootstrap operation running for hours
- Progress percentage increasing slowly

**Investigation:**
```sql
-- Estimate remaining time
SELECT
    progress_percentage,
    duration_millis / 60000 AS elapsed_minutes,
    bytes_received / 1073741824 AS received_gb,
    bytes_to_receive / 1073741824 AS total_gb
FROM system_views.streaming
WHERE operation = 'Bootstrap'
  AND status = 'START'
  AND bytes_received > 0;
```

Estimate remaining minutes in application: `(bytes_to_receive - bytes_received) / (bytes_received / (duration_millis / 1000)) / 60`.

**Resolution:**
- Verify network throughput limits
- Consider raising `stream_throughput_outbound`
- Ensure adequate disk I/O capacity
- Check for concurrent compaction load

---

## Related Configuration

Key settings that affect streaming performance:

| Setting | Default | Description |
|---------|---------|-------------|
| `stream_throughput_outbound` | 200 Mbps | Max throughput per node |
| `inter_dc_stream_throughput_outbound` | 200 Mbps | Max cross-DC throughput |
| `streaming_socket_timeout_in_ms` | 86400000 | Socket timeout (24h default) |
| `streaming_connections_per_host` | 1 | Parallel connections per peer |

Check current values:
```sql
SELECT name, value FROM system_views.settings
WHERE name IN ('stream_throughput_outbound',
               'inter_dc_stream_throughput_outbound',
               'streaming_socket_timeout_in_ms');
```

---

## Related Documentation

- **[Virtual Tables Overview](index.md)** - Introduction to virtual tables
- **[Repair](repair.md)** - Repair tracking tables
- **[Configuration](configuration.md)** - Runtime settings
- **[Cluster State](cluster-state.md)** - Internode communication metrics
