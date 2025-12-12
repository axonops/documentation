# Compaction

Compaction is the process of merging SSTables to reduce read amplification, reclaim space from tombstones, and maintain manageable file counts. Selecting an appropriate strategy and configuration is critical for cluster performance.

---

## SSTable Accumulation

As described in the **[Write Path](../write-path.md)**, Cassandra writes first go to the commit log and memtable. When a memtable reaches its threshold, it flushes to disk as an immutable SSTable. This append-only design enables fast writes but creates a side effect: SSTables accumulate continuously.

```plantuml
@startuml
skinparam backgroundColor transparent

rectangle "Writes" as writes
rectangle "Memtable" as memtable

package "Disk (SSTables accumulate over time)" {
    rectangle "SSTable 1\n(Day 1)" as ss1
    rectangle "SSTable 2\n(Day 2)" as ss2
    rectangle "SSTable 3\n(Day 3)" as ss3
    rectangle "..." as dots
    rectangle "SSTable N\n(Day N)" as ssN
}

writes --> memtable : write
memtable ..> ss1 : flush
memtable ..> ss2 : flush
memtable ..> ss3 : flush
memtable ..> ssN : flush

@enduml
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

```plantuml
@startuml
skinparam backgroundColor transparent

rectangle "Read 'user123'" as query

package "After 100 Days: 100 SSTables" {
    rectangle "SSTable 1" as ss1
    rectangle "SSTable 2" as ss2
    rectangle "SSTable 3" as ss3
    rectangle "..." as dots
    rectangle "SSTable 100" as ss100
}

rectangle "Potentially 100\ndisk seeks" as result

query --> ss1 : check
query --> ss2 : check
query --> ss3 : check
query ..> dots
query --> ss100 : check

ss1 ..> result
ss2 ..> result
ss3 ..> result
ss100 ..> result

@enduml
```

Each read must check bloom filters across all SSTables. Even with bloom filter optimization, false positives accumulate—potentially requiring disk seeks to dozens of SSTables for a single partition read.

---

## The Compaction Process

```plantuml
@startuml
skinparam backgroundColor transparent

package "Before Compaction" {
    rectangle "SSTable 1\nuser123→A\nuser789→D" as s1
    rectangle "SSTable 2\nuser123→B\nuser456→Y" as s2
    rectangle "SSTable 3\nuser456→X" as s3
    rectangle "SSTable 4\nuser123→C\n(deleted)" as s4
}

package "Compaction Process" {
    rectangle "1. Merge-sort all SSTables\n2. Keep newest timestamp per cell\n3. Apply tombstones\n4. Discard expired tombstones" as merge
}

package "After Compaction" {
    rectangle "New SSTable\nuser123→C (newest)\nuser456→X (merged)\nuser789→D\n(deletion applied)" as new
}

s1 --> merge
s2 --> merge
s3 --> merge
s4 --> merge
merge --> new

@enduml
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

```plantuml
@startuml
skinparam backgroundColor transparent

start

if (Is the data time-series with TTL?) then (YES)
    :TWCS;
    stop
else (NO)
endif

if (Is the workload >70% reads?) then (YES)
    if (Are SSDs available?) then (YES)
        :LCS;
        stop
    else (NO)
        :STCS;
        stop
    endif
else (NO)
    :STCS;
    stop
endif

note right
  Using Cassandra 5.0+?
  Consider UCS for new deployments
end note

@enduml
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
- **[Compaction Management](../../../operations/compaction-management/index.md)** - Tuning, troubleshooting, and maintenance
- **[Tombstones](../tombstones.md)** - How compaction removes deleted data
- **[SSTable Reference](../sstables.md)** - SSTable file format
