---
description: "Cassandra storage virtual tables. Monitor disk usage, partition sizes, snapshots, and SSTable tasks."
meta:
  - name: keywords
    content: "Cassandra disk usage, partition size, snapshots, compaction tasks, SSTable"
---

# Storage

The storage virtual tables provide visibility into disk usage, partition sizes, snapshots, and running SSTable operations like compaction.

---

## disk_usage

Shows disk space used per table on this node.

### Schema

```sql
VIRTUAL TABLE system_views.disk_usage (
    keyspace_name text,
    table_name text,
    mebibytes bigint,
    PRIMARY KEY ((keyspace_name, table_name))
)
```

| Column | Type | Description |
|--------|------|-------------|
| `keyspace_name` | text | Keyspace name |
| `table_name` | text | Table name |
| `mebibytes` | bigint | Disk space used (MiB) |

### Example Queries

```sql
-- Disk usage by table
SELECT keyspace_name, table_name, mebibytes
FROM system_views.disk_usage;

-- Tables over 10 GB (10240 MiB)
SELECT keyspace_name, table_name, mebibytes
FROM system_views.disk_usage
WHERE mebibytes > 10240;
```

---

## max_partition_size

Shows the largest partition size per table. Critical for identifying oversized partitions.

### Schema

```sql
VIRTUAL TABLE system_views.max_partition_size (
    keyspace_name text,
    table_name text,
    mebibytes bigint,
    PRIMARY KEY ((keyspace_name, table_name))
)
```

| Column | Type | Description |
|--------|------|-------------|
| `keyspace_name` | text | Keyspace name |
| `table_name` | text | Table name |
| `mebibytes` | bigint | Largest partition size (MiB) |

### Example Queries

```sql
-- Tables with large partitions
SELECT keyspace_name, table_name, mebibytes
FROM system_views.max_partition_size
WHERE mebibytes > 100;
```

!!! warning "Large Partition Impact"
    | Size | Status | Impact |
    |------|--------|--------|
    | < 100 MiB | Normal | Healthy |
    | 100-500 MiB | Warning | May cause GC pressure, slow repairs |
    | 500 MiB - 1 GiB | Critical | Performance degradation likely |
    | > 1 GiB | Severe | Requires data model redesign |

---

## max_sstable_size

Shows the largest SSTable size per table.

### Schema

```sql
VIRTUAL TABLE system_views.max_sstable_size (
    keyspace_name text,
    table_name text,
    mebibytes bigint,
    PRIMARY KEY ((keyspace_name, table_name))
)
```

### Example Queries

```sql
-- Tables with large SSTables
SELECT keyspace_name, table_name, mebibytes
FROM system_views.max_sstable_size
WHERE mebibytes > 1000;
```

---

## max_sstable_duration

Shows the age of the oldest SSTable per table. Useful for identifying compaction issues.

### Schema

```sql
VIRTUAL TABLE system_views.max_sstable_duration (
    keyspace_name text,
    table_name text,
    max_sstable_duration bigint,
    PRIMARY KEY ((keyspace_name, table_name))
)
```

| Column | Type | Description |
|--------|------|-------------|
| `max_sstable_duration` | bigint | Age of oldest SSTable (milliseconds) |

### Example Queries

```sql
-- Tables with old SSTables (potential compaction issues)
SELECT keyspace_name, table_name,
       max_sstable_duration / 86400000 AS days_old
FROM system_views.max_sstable_duration
WHERE max_sstable_duration > 604800000;  -- > 7 days
```

!!! note "Old SSTables"
    Old SSTables may indicate:
    - Compaction falling behind
    - TWCS windows not expiring
    - Data written once and never updated

---

## snapshots

Lists all snapshots on this node with size information.

### Schema

```sql
VIRTUAL TABLE system_views.snapshots (
    name text,
    keyspace_name text,
    table_name text,
    created_at timestamp,
    ephemeral boolean,
    expires_at timestamp,
    size_on_disk bigint,
    true_size bigint,
    PRIMARY KEY (name, keyspace_name, table_name)
) WITH CLUSTERING ORDER BY (keyspace_name ASC, table_name ASC)
```

| Column | Type | Description |
|--------|------|-------------|
| `name` | text | Snapshot name |
| `keyspace_name` | text | Keyspace |
| `table_name` | text | Table |
| `created_at` | timestamp | Creation timestamp |
| `true_size` | bigint | Actual data size (bytes) |
| `size_on_disk` | bigint | Disk space used (may differ due to hardlinks) |
| `expires_at` | timestamp | Auto-expiration time (if TTL set) |
| `ephemeral` | boolean | Auto-cleanup snapshot |

**Equivalent nodetool command:** `nodetool listsnapshots`

### Example Queries

```sql
-- All snapshots
SELECT name, keyspace_name, table_name, created_at, true_size
FROM system_views.snapshots;
```

Filter by `created_at` in application to find old snapshots for cleanup.

---

## sstable_tasks

Shows currently running SSTable operations (compaction, cleanup, scrub, etc.).

### Schema

```sql
VIRTUAL TABLE system_views.sstable_tasks (
    keyspace_name text,
    table_name text,
    task_id timeuuid,
    completion_ratio double,
    kind text,
    progress bigint,
    total bigint,
    sstables int,
    target_directory text,
    unit text,
    PRIMARY KEY (keyspace_name, table_name, task_id)
) WITH CLUSTERING ORDER BY (table_name ASC, task_id ASC)
```

| Column | Type | Description |
|--------|------|-------------|
| `keyspace_name` | text | Keyspace |
| `table_name` | text | Table |
| `task_id` | timeuuid | Unique task identifier |
| `kind` | text | Operation type (Compaction, Cleanup, Scrub, etc.) |
| `progress` | bigint | Bytes/rows processed |
| `total` | bigint | Total bytes/rows to process |
| `completion_ratio` | double | Progress percentage (0.0-1.0) |
| `sstables` | int | Number of SSTables involved |
| `unit` | text | Unit of progress (bytes, keys, etc.) |
| `target_directory` | text | Output directory |

**Equivalent nodetool command:** `nodetool compactionstats`

### Example Queries

```sql
-- All running tasks
SELECT keyspace_name, table_name, kind, completion_ratio, sstables
FROM system_views.sstable_tasks;

-- Compaction progress
SELECT keyspace_name, table_name, kind,
       progress, total,
       completion_ratio * 100 AS percent_complete
FROM system_views.sstable_tasks
WHERE kind = 'Compaction';

-- Large compaction operations
SELECT keyspace_name, table_name, sstables, total / 1073741824 AS total_gb
FROM system_views.sstable_tasks
WHERE total > 10737418240;  -- > 10 GB
```

---

## Alerting Rules

### Large Partitions

```sql
-- Alert: Partitions exceeding threshold
SELECT keyspace_name, table_name, mebibytes
FROM system_views.max_partition_size
WHERE mebibytes > 100;
```

### Old Snapshots

```sql
-- Alert: Snapshots older than 7 days
SELECT name, created_at
FROM system_views.snapshots
WHERE created_at < toTimestamp(now()) - 604800s;
```

### Stalled Compactions

```sql
-- Alert: Long-running compactions (> 1 hour with < 50% progress)
-- Requires application logic to track over time
SELECT keyspace_name, table_name, kind, completion_ratio
FROM system_views.sstable_tasks
WHERE kind = 'Compaction';
```

### Disk Usage Growth

```sql
-- Current disk usage for trending
SELECT keyspace_name, table_name, mebibytes
FROM system_views.disk_usage;
```

---

## Monitoring Dashboard Query

```sql
-- Disk usage by table
SELECT keyspace_name, table_name, mebibytes
FROM system_views.disk_usage;

-- Largest partitions by table
SELECT keyspace_name, table_name, mebibytes
FROM system_views.max_partition_size;

-- Largest SSTables by table
SELECT keyspace_name, table_name, mebibytes
FROM system_views.max_sstable_size;
```

Filter out system keyspaces in application if needed.

---

## Related Documentation

- **[Virtual Tables Overview](index.md)** - Introduction to virtual tables
- **[Metrics Tables](metrics.md)** - Performance metrics
- **[Backup & Restore](../backup-restore/index.md)** - Snapshot procedures
- **[Compaction](../compaction-management/index.md)** - Compaction tuning
