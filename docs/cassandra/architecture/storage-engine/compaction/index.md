# Compaction

Compaction is the process of merging SSTables to reduce read amplification, reclaim space from tombstones, and maintain manageable file counts. Selecting an appropriate strategy and configuration is critical for cluster performance.

---

## SSTable Accumulation

As described in the **[Write Path](../write-path.md)**, Cassandra writes first go to the commit log and memtable. When a memtable reaches its threshold, it flushes to disk as an immutable SSTable. This append-only design enables fast writes but creates a side effect: SSTables accumulate continuously.

```graphviz dot sstable-accumulation.svg
digraph sstable_accumulation {
    rankdir=LR;
    node [fontname="Helvetica", fontsize=11];
    edge [fontname="Helvetica", fontsize=10];

    writes [label="Writes", shape=box, style=filled, fillcolor="#fff3cd"];
    memtable [label="Memtable", shape=box, style=filled, fillcolor="#d4edda"];

    subgraph cluster_disk {
        label="Disk (SSTables accumulate over time)";
        style=filled;
        fillcolor="#f8f9fa";

        ss1 [label="SSTable 1\n(Day 1)", shape=box, style=filled, fillcolor="#e8f4f8"];
        ss2 [label="SSTable 2\n(Day 2)", shape=box, style=filled, fillcolor="#e8f4f8"];
        ss3 [label="SSTable 3\n(Day 3)", shape=box, style=filled, fillcolor="#e8f4f8"];
        dots [label="...", shape=plaintext];
        ssN [label="SSTable N\n(Day N)", shape=box, style=filled, fillcolor="#e8f4f8"];
    }

    writes -> memtable [label="write"];
    memtable -> ss1 [label="flush", style=dashed];
    memtable -> ss2 [label="flush", style=dashed];
    memtable -> ss3 [label="flush", style=dashed];
    memtable -> ssN [label="flush", style=dashed];
}
```

Each flush creates a new SSTable containing:

- Data from the memtable at flush time
- Potentially overlapping partition keys with existing SSTables
- Updated values for previously written rows
- Tombstones for deleted data

Without intervention, a table receiving continuous writes accumulates hundreds or thousands of SSTables. This creates problems for both reads and disk management.

---

## Why Compaction is Necessary

Without compaction, SSTable accumulation degrades read performance:

```graphviz dot read-amplification-problem.svg
digraph read_amplification {
    rankdir=LR;
    node [fontname="Helvetica", fontsize=11];
    edge [fontname="Helvetica", fontsize=10];

    subgraph cluster_sstables {
        label="After 100 Days: 100 SSTables";
        style=filled;
        fillcolor="#f8f9fa";

        ss1 [label="SSTable 1", shape=box, style=filled, fillcolor="#e8f4f8"];
        ss2 [label="SSTable 2", shape=box, style=filled, fillcolor="#e8f4f8"];
        ss3 [label="SSTable 3", shape=box, style=filled, fillcolor="#e8f4f8"];
        dots [label="...", shape=plaintext];
        ss100 [label="SSTable 100", shape=box, style=filled, fillcolor="#e8f4f8"];
    }

    query [label="Read 'user123'", shape=box, style=filled, fillcolor="#fff3cd"];
    result [label="Potentially 100\ndisk seeks", shape=box, style=filled, fillcolor="#f8d7da"];

    query -> ss1 [label="check"];
    query -> ss2 [label="check"];
    query -> ss3 [label="check"];
    query -> dots [style=dashed];
    query -> ss100 [label="check"];

    ss1 -> result [style=dashed];
    ss2 -> result [style=dashed];
    ss3 -> result [style=dashed];
    ss100 -> result [style=dashed];
}
```

Each read must check bloom filters across all SSTables. Even with bloom filter optimization, false positives accumulate—potentially requiring disk seeks to dozens of SSTables for a single partition read.

---

## The Compaction Process

```graphviz dot compaction-process.svg
digraph compaction_process {
    rankdir=LR;
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    compound=true;

    subgraph cluster_before {
        label="Before Compaction";
        style=filled;
        fillcolor="#f8f9fa";

        s1 [label="SSTable 1\nuser123→A\nuser789→D", shape=box, style=filled, fillcolor="#e8f4f8"];
        s2 [label="SSTable 2\nuser123→B\nuser456→Y", shape=box, style=filled, fillcolor="#e8f4f8"];
        s3 [label="SSTable 3\nuser456→X", shape=box, style=filled, fillcolor="#e8f4f8"];
        s4 [label="SSTable 4\nuser123→C\n(deleted)", shape=box, style=filled, fillcolor="#f8d7da"];
    }

    subgraph cluster_process {
        label="Compaction Process";
        style=filled;
        fillcolor="#fff3cd";

        merge [label="1. Merge-sort all SSTables\n2. Keep newest timestamp per cell\n3. Apply tombstones\n4. Discard expired tombstones", shape=box, style=filled, fillcolor="#ffeeba"];
    }

    subgraph cluster_after {
        label="After Compaction";
        style=filled;
        fillcolor="#f8f9fa";

        new [label="New SSTable\nuser123→C (newest)\nuser456→X (merged)\nuser789→D\n(deletion applied)", shape=box, style=filled, fillcolor="#d4edda"];
    }

    s1 -> merge [lhead=cluster_process];
    s2 -> merge [lhead=cluster_process];
    s3 -> merge [lhead=cluster_process];
    s4 -> merge [lhead=cluster_process];
    merge -> new [ltail=cluster_process];
}
```

### Benefits

| Benefit | Description |
|---------|-------------|
| Reduces read amplification | Fewer SSTables to check per read |
| Reclaims space | Removes tombstones after `gc_grace_seconds` |
| Removes obsolete data | Discards old versions of updated cells |
| Improves compression | Larger, consolidated data compresses better |
| Updates statistics | Refreshes min/max values, partition sizes |

---

## Amplification Factors

Every compaction strategy involves trade-offs between three types of amplification.

### Write Amplification

How many times data is written to disk over its lifetime.

```
Write Amplification = Total Bytes Written to Disk / Bytes Received from Client

Example:
- Client writes 1GB of data
- Data is written once to commit log
- Data is written once to SSTable (memtable flush)
- Data is rewritten 3x during compaction
- Write amplification = (1 + 1 + 3) / 1 = 5x
```

**Impact:**

- Higher write amplification increases disk I/O
- SSD lifetime is measured in total bytes written
- Write amplification of 10x means SSD wears 10x faster

### Read Amplification

How many SSTables must be checked per read.

```
Read Amplification = Number of SSTables Touched per Read

Ideal: 1 SSTable per read (data is fully consolidated)
Worst: N SSTables (one per flush, no compaction)
```

**Impact:**

- Higher read amplification increases disk seeks and latency
- With HDDs: Each SSTable check ≈ 10ms seek time
- With SSDs: Each SSTable check ≈ 0.1ms
- Significantly affects P99 latency

### Space Amplification

How much extra disk space is needed beyond raw data size.

```
Space Amplification = Disk Space Used / Actual Data Size

Example:
- Raw data: 100GB
- Tombstones pending cleanup: 10GB
- Old SSTable versions during compaction: 100GB (temporary)
- Space amplification = 210GB / 100GB = 2.1x
```

**Impact:**

- Determines required disk headroom
- Some strategies need 2x space temporarily during compaction
- Running out of disk during compaction causes failures

---

## Strategy Comparison

| Strategy | Write Amp | Read Amp | Space Amp | Best For |
|----------|-----------|----------|-----------|----------|
| [STCS](stcs.md) | Low | High | Medium | Write-heavy workloads |
| [LCS](lcs.md) | High | Low | Low | Read-heavy workloads |
| [TWCS](twcs.md) | Low | Low | Low | Time-series with TTL |
| [UCS](ucs.md) | Varies | Varies | Low | Adaptive (Cassandra 5.0+) |

---

## Strategy Selection

```
┌─────────────────────────────────────────────────────────────────────┐
│ COMPACTION STRATEGY DECISION GUIDE                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ Is the data time-series with TTL?                                   │
│   YES → TWCS                                                        │
│   NO  → Continue...                                                 │
│                                                                      │
│ Is the workload >70% reads?                                         │
│   YES → Are SSDs available?                                         │
│          YES → LCS                                                  │
│          NO  → STCS                                                 │
│   NO  → STCS                                                        │
│                                                                      │
│ Using Cassandra 5.0+?                                               │
│   Consider UCS for new deployments                                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Strategy by Workload Pattern

| Workload | Recommended | Rationale |
|----------|-------------|-----------|
| Write-heavy (>90% writes) | STCS | Low write amplification |
| Read-heavy (>70% reads) | LCS | Low read amplification |
| Time-series with TTL | TWCS | Efficient TTL expiration |
| Mixed workload | STCS or UCS | Balance of trade-offs |
| Frequently updated data | LCS | Consolidates versions quickly |
| Append-only logs | STCS or TWCS | Minimal rewrites |

---

## Monitoring

### Key Metrics

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Pending compactions | >50 | >200 | Increase throughput |
| SSTable count (STCS) | >20 | >50 | Check compaction progress |
| L0 SSTable count (LCS) | >8 | >32 | Throttle writes or switch strategy |
| Compaction throughput | <50% configured | <25% configured | Check disk I/O |
| Disk space free | <30% | <20% | Add storage or run compaction |

### Commands

```bash
# Current compaction activity
nodetool compactionstats

# Per-table SSTable count and sizes
nodetool tablestats keyspace.table

# Compaction history
nodetool compactionhistory

# SSTable count per level (LCS)
nodetool tablestats keyspace.table | grep "SSTables in each level"
```

### JMX Metrics

```
# Pending compactions
org.apache.cassandra.metrics:type=Compaction,name=PendingTasks

# Compaction throughput (bytes/second)
org.apache.cassandra.metrics:type=Compaction,name=BytesCompacted

# Per-table metrics
org.apache.cassandra.metrics:type=Table,keyspace=*,scope=*,name=LiveSSTableCount
org.apache.cassandra.metrics:type=Table,keyspace=*,scope=*,name=PendingCompactions
```

---

## Best Practices

### General

1. **Never disable auto-compaction** unless there is a specific operational reason
2. **Avoid major compaction** during normal production operations
3. **Monitor pending tasks** - sustained growth indicates a problem
4. **Maintain 30%+ free disk space** for compaction headroom
5. **Run repair regularly** to prevent zombie data after tombstone removal

### Configuration

```yaml
# cassandra.yaml

# Maximum compaction throughput per node (MB/s)
# Higher = faster compaction, more disk I/O competition
# 0 = unlimited
compaction_throughput_mb_per_sec: 64

# Number of concurrent compaction threads
# Default: min(4, number_of_disks)
concurrent_compactors: 4
```

```bash
# Adjust at runtime
nodetool setcompactionthroughput 128
nodetool setconcurrentcompactors 4
```

---

## Related Documentation

- **[Size-Tiered Compaction (STCS)](stcs.md)** - Default strategy for write-heavy workloads
- **[Leveled Compaction (LCS)](lcs.md)** - Optimized for read-heavy workloads
- **[Time-Window Compaction (TWCS)](twcs.md)** - Designed for time-series data
- **[Unified Compaction (UCS)](ucs.md)** - Adaptive strategy in Cassandra 5.0+
- **[Compaction Management](../../../../operations/compaction-management/index.md)** - Tuning, troubleshooting, and maintenance
- **[Tombstones](../tombstones.md)** - How compaction removes deleted data
- **[SSTable Reference](../sstables.md)** - SSTable file format
