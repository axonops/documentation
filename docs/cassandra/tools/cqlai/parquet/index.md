---
description: "CQLAI Parquet support. Import and export Parquet files with Cassandra."
meta:
  - name: keywords
    content: "CQLAI Parquet, Parquet import, columnar data"
---

# CQLAI Parquet Support

CQLAI provides comprehensive support for Apache Parquet format, enabling efficient data exchange between Cassandra and modern analytics ecosystems.

## Why Parquet?

| Benefit | Description |
|---------|-------------|
| **Efficient Storage** | Columnar format with 50-80% smaller file sizes than CSV |
| **Fast Analytics** | Optimized for analytical queries in Spark, Presto, DuckDB |
| **Type Preservation** | Maintains Cassandra data types including UDTs and collections |
| **ML Ready** | Direct compatibility with pandas, PyArrow, and ML frameworks |
| **Streaming** | Memory-efficient for large datasets |

## Quick Start

### Export to Parquet

```sql
-- Basic export (format auto-detected from extension)
COPY users TO 'users.parquet';

-- With compression
COPY events TO 'events.parquet' WITH COMPRESSION='ZSTD';

-- Explicit format specification
COPY orders TO 'data.parquet' WITH FORMAT='PARQUET';

-- Export specific columns
COPY users (id, name, email) TO 'users_partial.parquet';
```

### Import from Parquet

```sql
-- Basic import
COPY users FROM 'users.parquet';

-- Explicit format
COPY analytics FROM 'data.parquet' WITH FORMAT='PARQUET';
```

---

## Export Options

### COPY TO Syntax

```sql
COPY table_name [(column_list)] TO 'file.parquet'
[WITH option=value [AND option=value ...]]
```

### Available Options

| Option | Default | Description |
|--------|---------|-------------|
| `FORMAT` | auto | `PARQUET` or `CSV` (auto-detected from extension) |
| `COMPRESSION` | `SNAPPY` | Compression algorithm |
| `CHUNKSIZE` | 10000 | Rows per row group |
| `PAGESIZE` | 1000 | Rows to fetch per page from Cassandra |

### Compression Algorithms

| Algorithm | Speed | Ratio | Use Case |
|-----------|-------|-------|----------|
| `SNAPPY` | Fast | Good | General purpose (default) |
| `ZSTD` | Medium | Best | Archival, best compression |
| `GZIP` | Slow | Great | Compatibility |
| `LZ4` | Fastest | Moderate | High-speed requirements |
| `NONE` | N/A | None | When compression not needed |

### Examples

```sql
-- Best compression for archival
COPY events TO 'events_archive.parquet' WITH COMPRESSION='ZSTD';

-- Fast compression for streaming
COPY metrics TO 'metrics.parquet' WITH COMPRESSION='LZ4';

-- Large table with custom chunk size
COPY large_table TO 'data.parquet' WITH CHUNKSIZE=50000;
```

---

## Import Options

### COPY FROM Syntax

```sql
COPY table_name [(column_list)] FROM 'file.parquet'
[WITH option=value [AND option=value ...]]
```

### Available Options

| Option | Default | Description |
|--------|---------|-------------|
| `FORMAT` | auto | `PARQUET` or `CSV` |
| `MAXROWS` | -1 | Maximum rows to import (-1=unlimited) |
| `MAXINSERTERRORS` | 1000 | Max insert errors before stopping |
| `MAXBATCHSIZE` | 20 | Rows per batch insert |
| `CHUNKSIZE` | 5000 | Rows between progress updates |

### Examples

```sql
-- Import with row limit
COPY users FROM 'users.parquet' WITH MAXROWS=10000;

-- Import with error tolerance
COPY data FROM 'data.parquet' WITH MAXINSERTERRORS=100;
```

---

## Supported Data Types

CQLAI handles all Cassandra data types in Parquet format:

### Primitive Types

| Cassandra Type | Parquet Type | Notes |
|----------------|--------------|-------|
| `int` | INT32 | |
| `bigint` | INT64 | |
| `smallint` | INT32 | |
| `tinyint` | INT32 | |
| `float` | FLOAT | |
| `double` | DOUBLE | |
| `decimal` | BYTE_ARRAY (string) | Preserves precision |
| `varint` | BYTE_ARRAY (string) | |
| `boolean` | BOOLEAN | |
| `text` | BYTE_ARRAY (UTF8) | |
| `varchar` | BYTE_ARRAY (UTF8) | |
| `ascii` | BYTE_ARRAY (ASCII) | |
| `blob` | BYTE_ARRAY | |
| `uuid` | FIXED_LEN_BYTE_ARRAY[16] | |
| `timeuuid` | FIXED_LEN_BYTE_ARRAY[16] | |
| `timestamp` | INT64 (TIMESTAMP_MILLIS) | |
| `date` | INT32 (DATE) | |
| `time` | INT64 (TIME_MICROS) | |
| `duration` | BYTE_ARRAY (string) | ISO-8601 format |
| `inet` | BYTE_ARRAY (string) | IP address string |

### Collection Types

| Cassandra Type | Parquet Type |
|----------------|--------------|
| `list<T>` | LIST | Preserves element type |
| `set<T>` | LIST | Converted to sorted list |
| `map<K,V>` | MAP | Preserves key/value types |
| `frozen<...>` | Same as inner type | |

### Complex Types

| Cassandra Type | Parquet Type |
|----------------|--------------|
| User-Defined Type (UDT) | GROUP | Field structure preserved |
| `tuple<...>` | GROUP | Named field1, field2, etc. |
| `vector<T, N>` | LIST | Cassandra 5.0+ vector type |

---

## Working with Analytics Tools

### Python (pandas / PyArrow)

```python
import pandas as pd

# Read Parquet exported from CQLAI
df = pd.read_parquet('users.parquet')

# Process data
active_users = df[df['status'] == 'active']

# Write back to Parquet for CQLAI import
active_users.to_parquet('active_users.parquet', index=False)
```

### Apache Spark

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("CassandraAnalytics").getOrCreate()

# Read Parquet
df = spark.read.parquet("events.parquet")

# Process
df.groupBy("event_type").count().show()

# Write for CQLAI import
df.write.parquet("processed_events.parquet")
```

### DuckDB

```sql
-- Query Parquet directly
SELECT * FROM 'users.parquet' WHERE status = 'active';

-- Aggregate
SELECT date_trunc('month', created_at) as month, COUNT(*)
FROM 'events.parquet'
GROUP BY 1;
```

### Apache Drill

```sql
SELECT *
FROM dfs.`/path/to/users.parquet`
WHERE status = 'active';
```

---

## Best Practices

### Choosing Compression

| Scenario | Recommended |
|----------|-------------|
| General purpose | `SNAPPY` |
| Long-term storage | `ZSTD` |
| Maximum compatibility | `GZIP` |
| Real-time streaming | `LZ4` or `NONE` |

### Optimizing Chunk Size

```sql
-- Small tables (< 100K rows)
COPY small_table TO 'data.parquet' WITH CHUNKSIZE=5000;

-- Large tables (> 1M rows)
COPY large_table TO 'data.parquet' WITH CHUNKSIZE=50000;
```

Larger chunk sizes:
- Better compression ratio
- Faster reads for analytics
- Higher memory usage during export

### Handling Large Exports

For very large tables:

```sql
-- Use larger page size for faster export
COPY huge_table TO 'data.parquet' WITH PAGESIZE=5000 AND CHUNKSIZE=100000;
```

### Data Type Considerations

**Timestamps**: Parquet stores timestamps in milliseconds. CQLAI preserves Cassandra timestamp precision.

**Decimals**: Stored as strings to preserve arbitrary precision.

**UUIDs**: Stored as 16-byte fixed-length arrays for efficient storage.

---

## Troubleshooting

### Import Type Mismatches

If column types do not match:

```sql
-- Check table schema
DESCRIBE TABLE users;

-- Verify Parquet schema
-- (Use external tool like parquet-tools)
parquet-tools schema users.parquet
```

### Memory Issues with Large Files

For large files, adjust CQLAI memory settings:

```json
{
  "maxMemoryMB": 100
}
```

### Null Value Handling

Parquet preserves null values correctly. However, ensure your table allows nulls for imported columns:

```sql
-- Check column definitions
DESCRIBE TABLE my_table;
```

---

## Examples

### ETL Workflow

```sql
-- 1. Export from Cassandra
COPY events TO 'raw_events.parquet' WITH COMPRESSION='SNAPPY';

-- 2. Process in Python/Spark (external)

-- 3. Import processed data
COPY processed_events FROM 'enriched_events.parquet';
```

### Backup and Restore

```sql
-- Backup
COPY users TO 'backup/users_20240115.parquet' WITH COMPRESSION='ZSTD';
COPY orders TO 'backup/orders_20240115.parquet' WITH COMPRESSION='ZSTD';

-- Restore (to new cluster)
COPY users FROM 'backup/users_20240115.parquet';
COPY orders FROM 'backup/orders_20240115.parquet';
```

### Analytics Export

```sql
-- Export for analytics team
COPY events TO 'analytics/events.parquet'
  WITH COMPRESSION='SNAPPY' AND CHUNKSIZE=100000;
```

---

## Next Steps

- **[Commands Reference](../commands/index.md)** - Full COPY command syntax
- **[Configuration](../configuration/index.md)** - CQLAI settings
- **[Troubleshooting](../troubleshooting.md)** - Common issues
