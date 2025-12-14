---
description: "system_virtual_schema keyspace reference. Query virtual table metadata in Cassandra."
meta:
  - name: keywords
    content: "system_virtual_schema, virtual table schema, Cassandra metadata"
---

# system_virtual_schema

The `system_virtual_schema` keyspace contains metadata about virtual keyspaces and tables. It is a meta-keyspace that describes the virtual table system itself.

---

## Overview

This keyspace provides introspection capabilities for virtual tables, similar to how `system_schema` describes regular tables.

```sql
-- List all virtual keyspaces
SELECT * FROM system_virtual_schema.keyspaces;

-- List all virtual tables
SELECT keyspace_name, table_name, comment
FROM system_virtual_schema.tables;

-- Describe a specific virtual table
SELECT column_name, type, kind, position
FROM system_virtual_schema.columns
WHERE keyspace_name = 'system_views'
  AND table_name = 'thread_pools';
```

---

## Tables

### keyspaces

Lists available virtual keyspaces.

```sql
VIRTUAL TABLE system_virtual_schema.keyspaces (
    keyspace_name text PRIMARY KEY
)
```

| Column | Type | Description |
|--------|------|-------------|
| `keyspace_name` | text | Virtual keyspace name |

**Example:**

```sql
SELECT * FROM system_virtual_schema.keyspaces;
```

```
 keyspace_name
-----------------------
 system_virtual_schema
 system_views
```

### tables

Lists all virtual tables with descriptions.

```sql
VIRTUAL TABLE system_virtual_schema.tables (
    keyspace_name text,
    table_name text,
    comment text,
    PRIMARY KEY (keyspace_name, table_name)
) WITH CLUSTERING ORDER BY (table_name ASC)
```

| Column | Type | Description |
|--------|------|-------------|
| `keyspace_name` | text | Parent keyspace |
| `table_name` | text | Table name |
| `comment` | text | Description of the table's purpose |

**Example:**

```sql
-- List all tables in system_views
SELECT table_name, comment
FROM system_virtual_schema.tables
WHERE keyspace_name = 'system_views';
```

```
 table_name                  | comment
-----------------------------+------------------------------------------
 batch_metrics               | Metrics specific to batch statements
 caches                      | system caches
 clients                     | currently connected clients
 coordinator_read_latency    |
 coordinator_scan_latency    |
 coordinator_write_latency   |
 ...
```

### columns

Describes columns in each virtual table.

```sql
VIRTUAL TABLE system_virtual_schema.columns (
    keyspace_name text,
    table_name text,
    column_name text,
    clustering_order text,
    column_name_bytes blob,
    kind text,
    position int,
    type text,
    PRIMARY KEY (keyspace_name, table_name, column_name)
) WITH CLUSTERING ORDER BY (table_name ASC, column_name ASC)
```

| Column | Type | Description |
|--------|------|-------------|
| `keyspace_name` | text | Parent keyspace |
| `table_name` | text | Parent table |
| `column_name` | text | Column name |
| `type` | text | CQL data type |
| `kind` | text | `partition_key`, `clustering`, or `regular` |
| `position` | int | Position in primary key (0-indexed) |
| `clustering_order` | text | `asc` or `desc` for clustering columns |
| `column_name_bytes` | blob | Binary representation of column name |

**Example:**

```sql
-- Get schema for thread_pools table
SELECT column_name, type, kind, position
FROM system_virtual_schema.columns
WHERE keyspace_name = 'system_views'
  AND table_name = 'thread_pools';
```

Sort by position in application.

```
 column_name          | type   | kind          | position
----------------------+--------+---------------+----------
 name                 | text   | partition_key |        0
 active_tasks         | int    | regular       |       -1
 active_tasks_limit   | int    | regular       |       -1
 blocked_tasks        | bigint | regular       |       -1
 blocked_tasks_all_time | bigint | regular     |       -1
 completed_tasks      | bigint | regular       |       -1
 pending_tasks        | int    | regular       |       -1
```

---

## Use Cases

### Discovering Available Virtual Tables

```sql
-- All virtual tables in system_views
SELECT table_name, comment
FROM system_virtual_schema.tables
WHERE keyspace_name = 'system_views';
```

Filter in application by table_name pattern (e.g., tables containing 'repair').

### Programmatic Schema Discovery

```python
from cassandra.cluster import Cluster

cluster = Cluster()
session = cluster.connect()

# Get all virtual tables
tables = session.execute("""
    SELECT keyspace_name, table_name
    FROM system_virtual_schema.tables
""")

for table in tables:
    # Get columns for each table
    columns = session.execute("""
        SELECT column_name, type
        FROM system_virtual_schema.columns
        WHERE keyspace_name = %s AND table_name = %s
    """, (table.keyspace_name, table.table_name))

    print(f"\n{table.keyspace_name}.{table.table_name}")
    for col in columns:
        print(f"  {col.column_name}: {col.type}")
```

### Validating Virtual Table Availability

```sql
-- Check if a specific virtual table exists (version compatibility)
SELECT table_name
FROM system_virtual_schema.tables
WHERE keyspace_name = 'system_views'
  AND table_name = 'sai_column_indexes';

-- If empty result, SAI tables not available (pre-5.0)
```

---

## Related Documentation

- **[Virtual Tables Overview](index.md)** - Introduction to virtual tables
- **[Metrics Tables](metrics.md)** - Latency and performance metrics
- **[Configuration Tables](configuration.md)** - Runtime settings
