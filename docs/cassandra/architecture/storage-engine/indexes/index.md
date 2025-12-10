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

```graphviz dot index-concept.svg
digraph IndexConcept {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];

    label="Secondary Index Concept: Value → Partition Key Mapping";
    labelloc="t";
    fontsize=14;

    node [shape=box, style="rounded,filled", fillcolor="#7B4B96", fontcolor="white"];

    subgraph cluster_base {
        label="Base Table: users";
        style="rounded,filled";
        fillcolor="#F9E5FF";
        color="#CC99CC";

        row1 [label="pk=user1 | name='Alice' | city='NYC'"];
        row2 [label="pk=user2 | name='Bob' | city='LA'"];
        row3 [label="pk=user3 | name='Carol' | city='NYC'"];
    }

    subgraph cluster_index {
        label="Index on city";
        style="rounded,filled";
        fillcolor="#E8F4E8";
        color="#99CC99";

        idx1 [label="'NYC' → [user1, user3]", fillcolor="#4B964B"];
        idx2 [label="'LA' → [user2]", fillcolor="#4B964B"];
    }

    row1 -> idx1 [style=dashed, color="#555555"];
    row3 -> idx1 [style=dashed, color="#555555"];
    row2 -> idx2 [style=dashed, color="#555555"];
}
```

### Storage Location Differences

The primary architectural distinction between index types is where index data is stored:

```graphviz dot index-storage.svg
digraph IndexStorage {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];

    label="Index Storage Architecture Comparison";
    labelloc="t";
    fontsize=14;

    node [shape=box, style="rounded,filled"];

    subgraph cluster_2i {
        label="Secondary Index (2i)\nSeparate Hidden Tables";
        style="rounded,filled";
        fillcolor="#FFE8E8";
        color="#CC9999";

        base2i [label="Base Table\nSSTable", fillcolor="#7B4B96", fontcolor="white"];
        idx2i [label="Index Table\n(hidden)\nSSTable", fillcolor="#964B4B", fontcolor="white"];

        base2i -> idx2i [label="separate\ncompaction", style=dashed];
    }

    subgraph cluster_sasi {
        label="SASI\nSSTable-Attached";
        style="rounded,filled";
        fillcolor="#E8FFE8";
        color="#99CC99";

        baseSASI [label="Base Table\nSSTable", fillcolor="#7B4B96", fontcolor="white"];
        idxSASI [label="Index Component\n(attached to SSTable)", fillcolor="#4B964B", fontcolor="white"];

        baseSASI -> idxSASI [label="same\nSSTable", style=solid];
    }

    subgraph cluster_sai {
        label="SAI\nSSTable-Attached";
        style="rounded,filled";
        fillcolor="#E8E8FF";
        color="#9999CC";

        baseSAI [label="Base Table\nSSTable", fillcolor="#7B4B96", fontcolor="white"];
        idxSAI [label="Index Component\n(attached to SSTable)", fillcolor="#4B4B96", fontcolor="white"];

        baseSAI -> idxSAI [label="same\nSSTable", style=solid];
    }
}
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

```graphviz dot index-selection.svg
digraph IndexSelection {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];

    label="Index Type Selection Guide";
    labelloc="t";
    fontsize=14;

    node [shape=diamond, style="filled", fillcolor="#F9E5FF", color="#CC99CC"];
    edge [color="#555555"];

    q1 [label="Using\nCassandra 5.0+?"];
    q2 [label="Need text search\n(LIKE, CONTAINS)?"];
    q3 [label="Need numeric\nrange queries?"];
    q4 [label="High cardinality\ncolumn?"];

    node [shape=box, style="rounded,filled", fillcolor="#7B4B96", fontcolor="white"];

    sai [label="Use SAI\n(recommended)"];
    sasi [label="Use SASI (3.4+)\nor external search"];
    sasi2 [label="Use SASI (3.4+)\nor redesign model"];
    redesign [label="Avoid 2i\nRedesign model or use SAI"];
    si [label="Secondary Index (2i)\nacceptable"];

    q1 -> sai [label="YES", fontcolor="#006600"];
    q1 -> q2 [label="NO", fontcolor="#660000"];

    q2 -> sasi [label="YES", fontcolor="#006600"];
    q2 -> q3 [label="NO", fontcolor="#660000"];

    q3 -> sasi2 [label="YES", fontcolor="#006600"];
    q3 -> q4 [label="NO", fontcolor="#660000"];

    q4 -> redesign [label="YES", fontcolor="#006600"];
    q4 -> si [label="NO", fontcolor="#660000"];
}
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
