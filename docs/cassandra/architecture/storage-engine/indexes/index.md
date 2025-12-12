---
description: "Cassandra index architecture covering secondary indexes, SASI, and SAI implementation details."
meta:
  - name: keywords
    content: "Cassandra indexes, secondary index architecture, SASI, SAI"
---

# Indexes

Indexes in Cassandra provide efficient data access patterns beyond partition key lookups. Understanding the available index types, their implementation differences, and appropriate use cases is essential for query optimization.

---

## Background

### The Primary Key Index

Every Cassandra table has an implicit primary key index. This index is fundamental to Cassandra's data model and requires no additional configuration.

**Partition Key Index**: Each SSTable contains an index mapping partition key tokens to their data positions. This enables O(log n) lookups within an SSTable.

**Clustering Column Ordering**: Within a partition, data is physically sorted by clustering columns. Range queries on clustering columns are efficient because they read contiguous disk regions.

```sql
-- Primary key enables these efficient queries:
CREATE TABLE events (
    sensor_id uuid,
    event_time timestamp,
    reading double,
    PRIMARY KEY (sensor_id, event_time)
);

-- Partition key lookup: O(log n) per SSTable
SELECT * FROM events WHERE sensor_id = ?;

-- Clustering range: sequential read within partition
SELECT * FROM events WHERE sensor_id = ? AND event_time > ?;
```

### The Need for Secondary Indexes

Primary key indexes only support queries that include the partition key. Without secondary indexes, queries on non-key columns require full table scans—scanning every partition across all nodes.

```sql
-- Without secondary index: requires ALLOW FILTERING (full scan)
SELECT * FROM events WHERE reading > 100.0 ALLOW FILTERING;

-- With secondary index: targeted lookup
CREATE INDEX ON events (reading);
SELECT * FROM events WHERE reading > 100.0;
```

### Evolution of Secondary Indexes in Cassandra

Cassandra has developed multiple secondary index implementations over time:

| Version | Index Type | Status |
|---------|------------|--------|
| 0.7 (2011) | Secondary Index (2i) | Legacy, still supported |
| 3.4 (2016) | SASI | Experimental, limited support |
| 5.0 (2023) | SAI | Recommended for new deployments |

Each generation addressed limitations of its predecessors while introducing new capabilities and trade-offs.

---

## Index Architecture Comparison

### How Secondary Indexes Work

All Cassandra secondary indexes share a common principle: they create a mapping from indexed column values to partition keys. The implementation of this mapping differs significantly between index types.

```plantuml
@startuml
skinparam backgroundColor transparent
title Secondary Index Concept: Value → Partition Key Mapping

package "Base Table: users" {
    rectangle "pk=user1 | name='Alice' | city='NYC'" as row1
    rectangle "pk=user2 | name='Bob' | city='LA'" as row2
    rectangle "pk=user3 | name='Carol' | city='NYC'" as row3
}

package "Index on city" {
    rectangle "'NYC' → [user1, user3]" as idx1
    rectangle "'LA' → [user2]" as idx2
}

row1 ..> idx1
row3 ..> idx1
row2 ..> idx2

@enduml
```

### Storage Location Differences

The primary architectural distinction between index types is where index data is stored:

```plantuml
@startuml
skinparam backgroundColor transparent
title Index Storage Architecture Comparison

package "Secondary Index (2i) - Separate Hidden Tables" {
    rectangle "Base Table\nSSTable" as base2i
    rectangle "Index Table\n(hidden)\nSSTable" as idx2i
    base2i ..> idx2i : separate\ncompaction
}

package "SASI - SSTable-Attached" {
    rectangle "Base Table\nSSTable" as baseSASI
    rectangle "Index Component\n(attached to SSTable)" as idxSASI
    baseSASI --> idxSASI : same\nSSTable
}

package "SAI - SSTable-Attached" {
    rectangle "Base Table\nSSTable" as baseSAI
    rectangle "Index Component\n(attached to SSTable)" as idxSAI
    baseSAI --> idxSAI : same\nSSTable
}

@enduml
```

**Separate Tables (2i)**: Legacy secondary indexes store index data in hidden tables. These tables have their own SSTables and compact independently from base table data.

**SSTable-Attached (SASI, SAI)**: Modern indexes attach index data directly to base table SSTables. Index data compacts together with base table data, maintaining consistency.

---

## Index Type Comparison

| Characteristic | Secondary Index (2i) | SASI | SAI |
|----------------|---------------------|------|-----|
| **Storage** | Separate hidden table | Attached to SSTable | Attached to SSTable |
| **Cassandra Version** | 0.7+ | 3.4+ | 5.0+ |
| **Status** | Legacy | Experimental | Recommended |
| **Query Types** | Equality only | Equality, range, LIKE | Equality, range, LIKE |
| **Numeric Range** | No | Yes | Yes |
| **Text Search** | No | PREFIX, CONTAINS | Yes |
| **AND Queries** | Scatter-gather | Single-pass | Single-pass |
| **Write Overhead** | Medium | Medium | Low |
| **Cardinality Handling** | Poor at extremes | Better | Best |
| **Production Ready** | Yes (with caveats) | No | Yes |

### Choosing an Index Type

```plantuml
@startuml
skinparam backgroundColor transparent
title Index Type Selection Guide

start

if (Using Cassandra 5.0+?) then (YES)
    :Use SAI\n(recommended);
    stop
else (NO)
endif

if (Need text search\n(LIKE, CONTAINS)?) then (YES)
    :Use SASI (3.4+)\nor external search;
    stop
else (NO)
endif

if (Need numeric\nrange queries?) then (YES)
    :Use SASI (3.4+)\nor redesign model;
    stop
else (NO)
endif

if (High cardinality\ncolumn?) then (YES)
    :Avoid 2i\nRedesign model or use SAI;
    stop
else (NO)
    :Secondary Index (2i)\nacceptable;
    stop
endif

@enduml
```

---

## Query Execution

### Single-Index Query

When a query uses one index, all index types follow a similar pattern:

1. Query coordinator identifies relevant nodes
2. Each node queries its local index
3. Index returns matching partition keys
4. Node reads base table partitions
5. Results returned to coordinator

### Multi-Index Query (AND)

Queries with multiple indexed predicates differ significantly:

**Secondary Index (2i)**: Executes each predicate separately, intersects results at coordinator. Creates scatter-gather pattern with potential for large intermediate result sets.

**SASI / SAI**: Intersects predicates within each SSTable before returning results. More efficient for multi-predicate queries.

```sql
-- Multi-predicate query
SELECT * FROM users WHERE city = 'NYC' AND age > 25;

-- 2i: Two separate index lookups, coordinator intersection
-- SAI: Single-pass intersection per SSTable
```

---

## Performance Considerations

### Write Path Impact

All secondary indexes add overhead to the write path:

| Index Type | Write Overhead | Reason |
|------------|---------------|--------|
| 2i | Medium | Separate table mutation |
| SASI | Medium | Index structure update |
| SAI | Low | Optimized append-only design |

### Read Path Characteristics

| Query Type | 2i | SASI | SAI |
|------------|-----|------|-----|
| Single equality | Fair | Good | Good |
| Multiple AND | Poor | Good | Good |
| Range | N/A | Good | Good |
| High selectivity | Poor | Fair | Good |
| Low selectivity | Poor | Fair | Fair |

### Anti-Patterns

Avoid secondary indexes when:

1. **Very high cardinality** (e.g., UUIDs, timestamps): Index becomes as large as data
2. **Very low cardinality** (e.g., boolean, status with 2-3 values): Each index entry points to many partitions
3. **Frequently updated columns**: Each update requires index maintenance
4. **Large partitions with few matching rows**: Must read entire partition for few results

---

## Operational Considerations

### Index Building

```bash
# Check index build progress
nodetool describecluster

# Rebuild index (SAI)
nodetool rebuild_index keyspace table index_name

# View index status
nodetool tablestats keyspace.table
```

### Monitoring

```
# JMX metrics for index performance
org.apache.cassandra.metrics:type=Index,scope=*,name=*

# Per-table index metrics
org.apache.cassandra.metrics:type=Table,keyspace=*,scope=*,name=IndexSummaryOffHeapMemoryUsed
```

---

## Related Documentation

- **[Secondary Indexes (2i)](secondary-indexes.md)** - Legacy index implementation
- **[SASI](sasi.md)** - SSTable Attached Secondary Index
- **[SAI](sai.md)** - Storage Attached Index (recommended)
- **[Read Path](../read-path.md)** - Query execution details
- **[Compaction](../compaction/index.md)** - Impact on index maintenance
