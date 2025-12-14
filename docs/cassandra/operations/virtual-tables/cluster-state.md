---
description: "Cassandra cluster state virtual tables. Monitor gossip, pending hints, and internode communication."
meta:
  - name: keywords
    content: "Cassandra gossip, pending hints, internode communication, cluster state"
---

# Cluster State

The cluster state virtual tables provide visibility into gossip protocol state, pending hints, and internode communication metrics.

---

## gossip_info

Exposes gossip state for all known nodes in the cluster. Provides the same information as `nodetool gossipinfo` via CQL.

### Schema

```sql
VIRTUAL TABLE system_views.gossip_info (
    address inet,
    port int,
    dc text,
    rack text,
    status text,
    load text,
    host_id text,
    release_version text,
    "schema" text,
    generation int,
    heartbeat int,
    -- Additional columns for various gossip state values
    PRIMARY KEY (address, port)
) WITH CLUSTERING ORDER BY (port ASC)
```

| Column | Type | Description |
|--------|------|-------------|
| `address` | inet | Node IP address |
| `port` | int | Storage port |
| `dc` | text | Datacenter name |
| `rack` | text | Rack name |
| `status` | text | Node status (NORMAL, LEAVING, JOINING, MOVING) |
| `load` | text | Data load on node (bytes) |
| `host_id` | text | Unique node identifier (UUID) |
| `release_version` | text | Cassandra version |
| `schema` | text | Schema version UUID |
| `generation` | int | Gossip generation number |
| `heartbeat` | int | Current heartbeat version |

**Equivalent nodetool command:** `nodetool gossipinfo`

### Basic Queries

```sql
-- Cluster overview
SELECT address, dc, rack, status, release_version, load
FROM system_views.gossip_info;
```

Count nodes per datacenter in application.

### Health Monitoring

```sql
-- Find nodes not in NORMAL state
SELECT address, dc, rack, status
FROM system_views.gossip_info
WHERE status != 'NORMAL';

-- Schema versions (check for agreement)
SELECT address, "schema"
FROM system_views.gossip_info;

-- Cassandra versions
SELECT address, release_version
FROM system_views.gossip_info;
```

Group by schema version or release_version in application. Multiple schema versions indicate disagreement.

### Topology Information

```sql
-- Datacenter and rack layout
SELECT dc, rack, address, status
FROM system_views.gossip_info;

-- Node load distribution
SELECT address, dc, load
FROM system_views.gossip_info;
```

Sort by dc/rack or by load in application as needed.

---

## pending_hints

Shows pending hints this node holds for other nodes. Hints accumulate when target nodes are unreachable.

### Schema

```sql
VIRTUAL TABLE system_views.pending_hints (
    host_id uuid PRIMARY KEY,
    address inet,
    dc text,
    rack text,
    files int,
    oldest timestamp,
    newest timestamp,
    port int,
    status text
)
```

| Column | Type | Description |
|--------|------|-------------|
| `host_id` | uuid | Target node's host ID |
| `address` | inet | Target node's address |
| `dc` | text | Target datacenter |
| `rack` | text | Target rack |
| `files` | int | Number of hint files pending |
| `oldest` | timestamp | Timestamp of oldest pending hint |
| `newest` | timestamp | Timestamp of newest pending hint |
| `status` | text | Hint delivery status |

**Equivalent nodetool command:** `nodetool listpendinghints`

### Basic Queries

```sql
-- All pending hints
SELECT host_id, address, dc, files, oldest, newest, status
FROM system_views.pending_hints;

-- Hints accumulating (nodes potentially down)
SELECT address, dc, files, oldest
FROM system_views.pending_hints
WHERE files > 0;
```

### Age Analysis

```sql
-- Hints older than 1 hour (potential problem)
SELECT address, dc, files, oldest
FROM system_views.pending_hints
WHERE oldest < toTimestamp(now()) - 3600s;
```

!!! warning "Hint Window"
    Hints are only stored for `max_hint_window` (default: 3 hours). If a node is down longer:
    - Hints stop accumulating after the window
    - The node will need repair when it returns
    - Check `oldest` timestamp to understand hint coverage

---

## internode_inbound

Statistics for incoming connections from other nodes.

### Schema

```sql
VIRTUAL TABLE system_views.internode_inbound (
    address inet,
    port int,
    dc text,
    rack text,
    received_count bigint,
    received_bytes bigint,
    processed_count bigint,
    processed_bytes bigint,
    error_count bigint,
    error_bytes bigint,
    expired_count bigint,
    expired_bytes bigint,
    throttled_count bigint,
    throttled_nanos bigint,
    corrupt_frames_recovered bigint,
    corrupt_frames_unrecovered bigint,
    scheduled_count bigint,
    scheduled_bytes bigint,
    using_bytes bigint,
    using_reserve_bytes bigint,
    PRIMARY KEY ((address, port), dc, rack)
)
```

| Column | Type | Description |
|--------|------|-------------|
| `address` | inet | Remote node address |
| `received_count` | bigint | Messages received |
| `received_bytes` | bigint | Bytes received |
| `processed_count` | bigint | Messages successfully processed |
| `error_count` | bigint | Receive errors |
| `expired_count` | bigint | Messages expired before processing |
| `throttled_count` | bigint | Times throttled due to backpressure |
| `corrupt_frames_recovered` | bigint | Corrupted frames that were recovered |
| `corrupt_frames_unrecovered` | bigint | Unrecoverable corruptions |

### Monitoring Queries

```sql
-- Inbound traffic summary
SELECT address, dc,
       received_count,
       received_bytes / 1048576 AS received_mb,
       error_count,
       throttled_count
FROM system_views.internode_inbound;

-- Nodes with errors
SELECT address, error_count, corrupt_frames_unrecovered
FROM system_views.internode_inbound
WHERE error_count > 0;
```

---

## internode_outbound

Statistics for outgoing connections to other nodes.

### Schema

```sql
VIRTUAL TABLE system_views.internode_outbound (
    address inet,
    port int,
    dc text,
    rack text,
    sent_count bigint,
    sent_bytes bigint,
    pending_count bigint,
    pending_bytes bigint,
    error_count bigint,
    error_bytes bigint,
    expired_count bigint,
    expired_bytes bigint,
    overload_count bigint,
    overload_bytes bigint,
    active_connections bigint,
    connection_attempts bigint,
    successful_connection_attempts bigint,
    using_bytes bigint,
    using_reserve_bytes bigint,
    PRIMARY KEY ((address, port), dc, rack)
)
```

| Column | Type | Description |
|--------|------|-------------|
| `address` | inet | Remote node address |
| `sent_count` | bigint | Messages sent |
| `sent_bytes` | bigint | Bytes sent |
| `pending_count` | bigint | Messages waiting to send |
| `error_count` | bigint | Send errors |
| `expired_count` | bigint | Messages expired before sending |
| `overload_count` | bigint | Messages dropped due to overload |
| `active_connections` | bigint | Current active connections |
| `connection_attempts` | bigint | Total connection attempts |
| `successful_connection_attempts` | bigint | Successful connections |

### Monitoring Queries

```sql
-- Outbound traffic summary
SELECT address, dc,
       sent_count,
       sent_bytes / 1048576 AS sent_mb,
       pending_count,
       error_count
FROM system_views.internode_outbound;

-- Connection attempts
SELECT address, connection_attempts, successful_connection_attempts
FROM system_views.internode_outbound;

-- Backpressure indicators
SELECT address, pending_count, overload_count, expired_count
FROM system_views.internode_outbound
WHERE pending_count > 100;
```

Calculate failed attempts in application: `connection_attempts - successful_connection_attempts`.

---

## Alerting Rules

### Node Not Normal

```sql
-- Alert: Nodes in transitional states
SELECT address, dc, status
FROM system_views.gossip_info
WHERE status NOT IN ('NORMAL', 'NORMAL');
```

### Schema Disagreement

```sql
-- Check schema versions
SELECT address, "schema"
FROM system_views.gossip_info;
```

Count distinct schema values in application. Alert if more than one unique value.

### Hints Accumulating

```sql
-- Alert: Significant hints pending
SELECT address, dc, files, oldest
FROM system_views.pending_hints
WHERE files > 50;
```

### Internode Communication Issues

```sql
-- Alert: Communication errors
SELECT address, error_count, expired_count, overload_count
FROM system_views.internode_outbound
WHERE error_count > 0 OR expired_count > 0 OR overload_count > 0;
```

---

## Troubleshooting

### Schema Disagreement

**Symptoms:**
- Multiple schema versions in `gossip_info`
- DDL operations failing

**Resolution:**
```sql
-- Identify schema versions per node
SELECT address, "schema"
FROM system_views.gossip_info;
```

Group by schema in application to find disagreeing nodes. Then on the affected node(s):
```bash
nodetool resetlocalschema  # Last resort
```

### Hints Not Draining

**Symptoms:**
- Pending hints for online node
- `status` shows issues

**Resolution:**
1. Verify target node is healthy
2. Check internode connectivity
3. Review `internode_outbound` for that target

### High Internode Latency

**Symptoms:**
- High `pending_count` in `internode_outbound`
- Messages expiring

**Resolution:**
1. Check network between datacenters
2. Review `internode_inbound.throttled_count` on remote nodes
3. Consider `internode_compression` settings

---

## Related Documentation

- **[Virtual Tables Overview](index.md)** - Introduction to virtual tables
- **[Repair](repair.md)** - Repair tracking tables
- **[nodetool gossipinfo](../nodetool/gossipinfo.md)** - Command-line equivalent
- **[nodetool listpendinghints](../nodetool/listpendinghints.md)** - Hints command
