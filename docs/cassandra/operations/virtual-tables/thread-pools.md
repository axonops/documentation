---
description: "Cassandra thread_pools virtual table reference. Monitor thread pool utilization and backpressure."
meta:
  - name: keywords
    content: "Cassandra thread pools, tpstats, thread pool monitoring, backpressure"
---

# Thread Pools

The `thread_pools` virtual table shows the current state of all Cassandra thread pools, providing visibility into request processing capacity and backpressure.

---

## Overview

Cassandra uses staged event-driven architecture (SEDA) with separate thread pools for different operation types. Monitoring these pools reveals bottlenecks and capacity issues.

```sql
SELECT name, active_tasks, pending_tasks, blocked_tasks, completed_tasks
FROM system_views.thread_pools;
```

**Equivalent nodetool command:** `nodetool tpstats`

---

## Schema

```sql
VIRTUAL TABLE system_views.thread_pools (
    name text PRIMARY KEY,
    active_tasks int,
    active_tasks_limit int,
    blocked_tasks bigint,
    blocked_tasks_all_time bigint,
    completed_tasks bigint,
    pending_tasks int
)
```

| Column | Type | Description |
|--------|------|-------------|
| `name` | text | Thread pool name |
| `active_tasks` | int | Currently executing tasks |
| `active_tasks_limit` | int | Maximum concurrent tasks (pool size) |
| `pending_tasks` | int | Tasks queued waiting for execution |
| `blocked_tasks` | bigint | Tasks currently blocked due to backpressure |
| `blocked_tasks_all_time` | bigint | Total blocked tasks since node startup |
| `completed_tasks` | bigint | Total completed tasks since startup |

---

## Key Thread Pools

### Request Processing

| Pool Name | Purpose | Warning Signs |
|-----------|---------|---------------|
| `Native-Transport-Requests` | CQL client requests | `pending > 1000` indicates client backpressure |
| `RequestResponseStage` | Inter-node request/response | `blocked > 0` indicates network issues |

### Read/Write Operations

| Pool Name | Purpose | Warning Signs |
|-----------|---------|---------------|
| `ReadStage` | Local read operations | `pending > 100` indicates disk bottleneck |
| `MutationStage` | Local write operations | `pending > 0`, `blocked > 0` critical |
| `CounterMutationStage` | Counter write operations | Same as MutationStage |
| `ViewMutationStage` | Materialized view updates | `pending > 0` indicates MV lag |

### Storage Operations

| Pool Name | Purpose | Warning Signs |
|-----------|---------|---------------|
| `MemtableFlushWriter` | Memtable to SSTable flush | `pending > 0` indicates flush backpressure |
| `MemtablePostFlush` | Post-flush cleanup | Should stay near zero |
| `CompactionExecutor` | Compaction tasks | `pending > 100` indicates compaction falling behind |
| `ValidationExecutor` | Repair validation | High during repair operations |

### Cluster Communication

| Pool Name | Purpose | Warning Signs |
|-----------|---------|---------------|
| `GossipStage` | Gossip protocol | `pending > 0` indicates network issues |
| `AntiEntropyStage` | Repair coordination | Active during repairs |
| `MigrationStage` | Schema changes | Usually idle |
| `HintsDispatcher` | Hint delivery | Active when catching up offline nodes |

### Background Tasks

| Pool Name | Purpose | Warning Signs |
|-----------|---------|---------------|
| `SecondaryIndexManagement` | Index maintenance | Should be low |
| `CacheCleanupExecutor` | Cache eviction | Usually idle |
| `InternalResponseStage` | Internal coordination | Should be low |
| `Sampler` | Query sampling | Always low |

---

## Monitoring Queries

### Critical Health Check

```sql
-- Find pools with problems
SELECT name, active_tasks, pending_tasks, blocked_tasks
FROM system_views.thread_pools
WHERE pending_tasks > 0 OR blocked_tasks > 0;
```

### Pool Utilization

```sql
-- Check pool capacity usage
SELECT
    name,
    active_tasks,
    active_tasks_limit,
    CAST(active_tasks AS double) / active_tasks_limit * 100 AS utilization_pct,
    pending_tasks
FROM system_views.thread_pools
WHERE active_tasks_limit > 0;
```

### Historical Blocked Tasks

```sql
-- Pools that have experienced blocking
SELECT name, blocked_tasks_all_time, completed_tasks,
       CAST(blocked_tasks_all_time AS double) / completed_tasks * 100 AS block_rate_pct
FROM system_views.thread_pools
WHERE blocked_tasks_all_time > 0;
```

### Request Path Health

```sql
-- Monitor critical request path pools
SELECT name, active_tasks, pending_tasks, blocked_tasks
FROM system_views.thread_pools
WHERE name IN (
    'Native-Transport-Requests',
    'ReadStage',
    'MutationStage',
    'RequestResponseStage',
    'MemtableFlushWriter',
    'CompactionExecutor'
);
```

---

## Interpreting Results

### Healthy State

```
 name                       | active_tasks | pending_tasks | blocked_tasks
----------------------------+--------------+---------------+---------------
 Native-Transport-Requests  |           45 |             0 |             0
 ReadStage                  |           12 |             0 |             0
 MutationStage              |            8 |             0 |             0
 CompactionExecutor         |            2 |             3 |             0
 MemtableFlushWriter        |            0 |             0 |             0
```

### Warning State

```
 name                       | active_tasks | pending_tasks | blocked_tasks
----------------------------+--------------+---------------+---------------
 Native-Transport-Requests  |          128 |           500 |             0  ← Client backpressure
 ReadStage                  |           32 |           150 |             0  ← Disk bottleneck
 MutationStage              |           32 |             0 |             0
 CompactionExecutor         |            4 |           200 |             0  ← Compaction behind
 MemtableFlushWriter        |            2 |             5 |             0  ← Flush pressure
```

### Critical State

```
 name                       | active_tasks | pending_tasks | blocked_tasks
----------------------------+--------------+---------------+---------------
 Native-Transport-Requests  |          128 |          5000 |            50  ← CRITICAL
 MutationStage              |           32 |           100 |            10  ← CRITICAL
 MemtableFlushWriter        |            2 |            20 |             5  ← CRITICAL
```

---

## Alerting Rules

### Blocked Tasks Alert (Critical)

```sql
-- Any blocked tasks is critical
SELECT name, blocked_tasks, blocked_tasks_all_time
FROM system_views.thread_pools
WHERE blocked_tasks > 0;
```

**Action:** Immediate investigation required. Blocked tasks indicate the system cannot keep up with load.

### High Pending Tasks Alert

```sql
-- Sustained pending tasks
SELECT name, pending_tasks
FROM system_views.thread_pools
WHERE (name = 'MutationStage' AND pending_tasks > 10)
   OR (name = 'ReadStage' AND pending_tasks > 100)
   OR (name = 'CompactionExecutor' AND pending_tasks > 50)
   OR (name = 'MemtableFlushWriter' AND pending_tasks > 2);
```

### Flush Backpressure Alert

```sql
-- Memtable flush falling behind
SELECT name, pending_tasks
FROM system_views.thread_pools
WHERE name LIKE 'Memtable%' AND pending_tasks > 0;
```

**Action:** Check disk I/O, consider increasing `memtable_flush_writers`.

---

## Troubleshooting

### MutationStage Blocked

**Symptoms:**
- `MutationStage` shows `blocked_tasks > 0`
- Write latency spikes

**Common Causes:**
1. Memtable flush backpressure (check `MemtableFlushWriter`)
2. Commit log sync bottleneck
3. Disk I/O saturation

**Resolution:**
- Check disk utilization: `iostat -x 1`
- Verify commit log on fast disk
- Consider increasing `concurrent_writes`

### ReadStage High Pending

**Symptoms:**
- `ReadStage` shows high `pending_tasks`
- Read latency increases

**Common Causes:**
1. Disk I/O bottleneck
2. Large partitions causing slow reads
3. Tombstone scanning
4. Cold cache causing excessive disk reads

**Resolution:**
- Check `tombstones_per_read` for tombstone issues
- Review partition sizes
- Verify key cache hit ratio
- Consider adding read capacity

### CompactionExecutor Backlog

**Symptoms:**
- `CompactionExecutor` shows `pending_tasks > 100`
- Disk usage growing
- Read latency increasing

**Common Causes:**
1. Write rate exceeding compaction throughput
2. Large SSTables taking long to compact
3. Insufficient compaction threads

**Resolution:**
- Check `nodetool compactionstats` for details
- Consider increasing `concurrent_compactors`
- Review compaction strategy settings
- Verify disk throughput capacity

---

## Configuration Tuning

Thread pool sizes can be adjusted in `cassandra.yaml`:

```yaml
# Read/write stages
concurrent_reads: 32      # ReadStage size
concurrent_writes: 32     # MutationStage size
concurrent_counter_writes: 32

# Compaction
concurrent_compactors: 4

# Memtable flush
memtable_flush_writers: 2

# Native transport
native_transport_max_threads: 128
```

!!! warning "Tuning Considerations"
    Increasing thread pool sizes:
    - Consumes more memory per thread
    - May increase contention under load
    - Should be tested before production deployment

    Default values are appropriate for most workloads.

---

## Related Documentation

- **[Virtual Tables Overview](index.md)** - Introduction to virtual tables
- **[Metrics Tables](metrics.md)** - Latency monitoring
- **[Performance Tuning](../performance/index.md)** - Optimization strategies
- **[nodetool tpstats](../nodetool/tpstats.md)** - Command-line equivalent
