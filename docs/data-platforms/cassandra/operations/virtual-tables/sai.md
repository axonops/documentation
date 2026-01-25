---
title: "SAI Index Tables"
description: "Cassandra SAI (Storage-Attached Index) virtual tables. Monitor index state, build progress, and SSTable segments."
meta:
  - name: keywords
    content: "Cassandra SAI, Storage-Attached Index, index monitoring, SAI virtual tables"
---

# SAI Index Tables

The SAI (Storage-Attached Index) virtual tables provide introspection into index state, build progress, and per-SSTable index metadata. Available in Cassandra 5.0+.

---

## Overview

SAI indexes are tightly integrated with SSTable storage. These virtual tables expose:

- Index metadata and queryability status
- Per-SSTable index information
- Index segment details for debugging

| Table | Purpose |
|-------|---------|
| `sai_column_indexes` | Index metadata and build status |
| `sai_sstable_indexes` | Per-SSTable index info |
| `sai_sstable_index_segments` | Detailed segment metadata |

---

## sai_column_indexes

Metadata about SAI indexes including build status.

### Schema

```sql
VIRTUAL TABLE system_views.sai_column_indexes (
    keyspace_name text,
    index_name text,
    table_name text,
    column_name text,
    analyzer text,
    is_building boolean,
    is_queryable boolean,
    is_string boolean,
    PRIMARY KEY (keyspace_name, index_name)
) WITH CLUSTERING ORDER BY (index_name ASC)
```

| Column | Type | Description |
|--------|------|-------------|
| `keyspace_name` | text | Keyspace name |
| `index_name` | text | Index name |
| `table_name` | text | Base table name |
| `column_name` | text | Indexed column |
| `analyzer` | text | Text analyzer (for string indexes) |
| `is_building` | boolean | Index currently building |
| `is_queryable` | boolean | Index ready for queries |
| `is_string` | boolean | String-type index |

### Example Queries

```sql
-- All SAI indexes
SELECT keyspace_name, index_name, table_name, column_name,
       is_queryable, is_building
FROM system_views.sai_column_indexes;

-- Indexes currently building
SELECT keyspace_name, index_name, table_name, column_name
FROM system_views.sai_column_indexes
WHERE is_building = true;

-- Non-queryable indexes (building or failed)
SELECT keyspace_name, index_name, is_building
FROM system_views.sai_column_indexes
WHERE is_queryable = false;

-- String indexes (check analyzer column for configured analyzers)
SELECT keyspace_name, index_name, column_name, analyzer
FROM system_views.sai_column_indexes
WHERE is_string = true;
```

### Index States

| is_queryable | is_building | State |
|--------------|-------------|-------|
| true | false | Ready - normal operation |
| false | true | Building - queries may return partial results |
| false | false | Failed or not yet started |
| true | true | Queryable but rebuild in progress |

---

## sai_sstable_indexes

Per-SSTable SAI index information.

### Schema

```sql
VIRTUAL TABLE system_views.sai_sstable_indexes (
    keyspace_name text,
    index_name text,
    sstable_name text,
    table_name text,
    column_name text,
    cell_count bigint,
    min_row_id bigint,
    max_row_id bigint,
    start_token text,
    end_token text,
    format_version text,
    per_column_disk_size bigint,
    per_table_disk_size bigint,
    PRIMARY KEY (keyspace_name, index_name, sstable_name)
) WITH CLUSTERING ORDER BY (index_name ASC, sstable_name ASC)
```

| Column | Type | Description |
|--------|------|-------------|
| `keyspace_name` | text | Keyspace name |
| `index_name` | text | Index name |
| `sstable_name` | text | SSTable identifier |
| `table_name` | text | Base table |
| `column_name` | text | Indexed column |
| `cell_count` | bigint | Number of indexed cells |
| `min_row_id` | bigint | Minimum row ID in index |
| `max_row_id` | bigint | Maximum row ID in index |
| `start_token` | text | Start token range |
| `end_token` | text | End token range |
| `format_version` | text | Index format version |
| `per_column_disk_size` | bigint | Index size for this column |
| `per_table_disk_size` | bigint | Total index size for table |

### Example Queries

```sql
-- Index size per SSTable
SELECT index_name, sstable_name,
       per_column_disk_size / 1048576 AS index_size_mb,
       cell_count
FROM system_views.sai_sstable_indexes
WHERE keyspace_name = 'my_keyspace';

-- SSTables with large indexes (> 100 MB)
SELECT keyspace_name, index_name, sstable_name,
       per_column_disk_size / 1048576 AS size_mb
FROM system_views.sai_sstable_indexes
WHERE per_column_disk_size > 104857600;
```

---

## sai_sstable_index_segments

Detailed segment information within SAI indexes. Useful for advanced debugging.

### Schema

```sql
VIRTUAL TABLE system_views.sai_sstable_index_segments (
    keyspace_name text,
    index_name text,
    sstable_name text,
    segment_row_id_offset bigint,
    table_name text,
    column_name text,
    cell_count bigint,
    min_sstable_row_id bigint,
    max_sstable_row_id bigint,
    min_term text,
    max_term text,
    start_token text,
    end_token text,
    component_metadata map<text, map<text, text>>,
    PRIMARY KEY (keyspace_name, index_name, sstable_name, segment_row_id_offset)
) WITH CLUSTERING ORDER BY (index_name ASC, sstable_name ASC, segment_row_id_offset ASC)
```

| Column | Type | Description |
|--------|------|-------------|
| `segment_row_id_offset` | bigint | Segment offset within SSTable |
| `min_term` | text | Minimum indexed term |
| `max_term` | text | Maximum indexed term |
| `cell_count` | bigint | Cells in this segment |
| `component_metadata` | map | Detailed component info |

### Example Queries

```sql
-- Segment distribution for an index
SELECT sstable_name, segment_row_id_offset, cell_count,
       min_term, max_term
FROM system_views.sai_sstable_index_segments
WHERE keyspace_name = 'my_keyspace'
  AND index_name = 'my_index';

-- Term range analysis
SELECT index_name, min_term, max_term
FROM system_views.sai_sstable_index_segments
WHERE keyspace_name = 'my_keyspace';
```

---

## Monitoring Use Cases

### Index Build Monitoring

```sql
-- Monitor index build progress
SELECT keyspace_name, index_name, is_building, is_queryable
FROM system_views.sai_column_indexes
WHERE is_building = true;

-- Track build by watching SSTable coverage
SELECT index_name, sstable_name
FROM system_views.sai_sstable_indexes
WHERE keyspace_name = 'my_keyspace';
```

Count distinct SSTables per index in application.

### Index Size Analysis

```sql
-- SAI index sizes by table
SELECT table_name,
       per_column_disk_size / 1048576 AS index_mb
FROM system_views.sai_sstable_indexes
WHERE keyspace_name = 'my_keyspace';

-- Table sizes for comparison
SELECT table_name, mebibytes AS table_mb
FROM system_views.disk_usage
WHERE keyspace_name = 'my_keyspace';
```

Sum index_mb per table in application and compare to table_mb to calculate overhead percentage.

### Query Planning Insights

```sql
-- Term data for cardinality estimation
SELECT index_name, column_name, min_term
FROM system_views.sai_sstable_index_segments
WHERE keyspace_name = 'my_keyspace';
```

Count distinct terms per index/column in application for cardinality estimation.

---

## Alerting Rules

### Index Not Queryable

```sql
-- Alert: Index not ready for queries
SELECT keyspace_name, index_name, is_building
FROM system_views.sai_column_indexes
WHERE is_queryable = false;
```

### Large Index Size

```sql
-- Get index sizes for alerting
SELECT keyspace_name, index_name, per_column_disk_size
FROM system_views.sai_sstable_indexes;
```

Sum sizes per index in application. Alert when total exceeds 10 GB (10737418240 bytes).

---

## Troubleshooting

### Index Build Stuck

**Symptoms:**
- `is_building = true` for extended period
- `is_queryable = false`

**Investigation:**
```sql
-- Check indexed SSTables
SELECT sstable_name
FROM system_views.sai_sstable_indexes
WHERE index_name = 'problematic_index';
```

Count results in application to see how many SSTables are indexed.

**Resolution:**
- Check compaction status (builds happen during compaction)
- Review logs for errors
- Consider dropping and recreating the index

### Partial Query Results

**Symptoms:**
- Queries return fewer results than expected
- `is_queryable = true` but `is_building = true`

**Explanation:**
During index build, queries only search already-indexed SSTables.

```sql
-- Check build progress
SELECT index_name, is_queryable, is_building
FROM system_views.sai_column_indexes
WHERE keyspace_name = 'my_keyspace';
```

### High Index Overhead

**Symptoms:**
- Index size approaching or exceeding table size

**Investigation:**
```sql
-- Index to data ratio
SELECT index_name,
       per_column_disk_size / 1048576 AS index_mb
FROM system_views.sai_sstable_indexes
WHERE keyspace_name = 'my_keyspace';
```

Sum index_mb per index in application and compare to table size from `disk_usage`.

**Resolution:**
- Review if index is needed
- Consider more selective indexing
- Evaluate alternative data models

---

## Related Documentation

- **[Virtual Tables Overview](index.md)** - Introduction to virtual tables
- **[SAI Indexing](../../cql/indexing/index.md)** - SAI index creation and usage
- **[Storage Tables](storage.md)** - Disk usage monitoring
