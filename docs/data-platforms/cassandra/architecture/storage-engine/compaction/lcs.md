---
title: "Cassandra Leveled Compaction Strategy (LCS)"
description: "Leveled Compaction Strategy (LCS) in Cassandra. Level-based compaction for read-heavy workloads."
meta:
  - name: keywords
    content: "LCS, Leveled Compaction, Cassandra compaction, read-heavy workloads"
---

# Leveled Compaction Strategy (LCS)

!!! note "Cassandra 5.0+"
    Starting with Cassandra 5.0, [Unified Compaction Strategy (UCS)](ucs.md) is the recommended compaction strategy for most workloads, including read-heavy patterns traditionally suited to LCS. UCS provides similar read amplification benefits with more adaptive behavior. LCS remains fully supported and is a proven choice for production deployments on earlier versions.

LCS organizes SSTables into levels where each level is 10x larger than the previous. Within each level (except L0), SSTables have non-overlapping token ranges, providing predictable read performance at the cost of higher write amplification.

---

## Background and History

### Origins

Leveled Compaction Strategy was introduced to Cassandra in version 1.0 to address read amplification problems inherent in the original Size-Tiered Compaction Strategy. It follows the general LSM-tree leveled compaction approach used by systems such as LevelDB and RocksDB.

The core insight from LevelDB was that organizing SSTables into levels with non-overlapping key ranges within each level dramatically reduces the number of files that must be consulted during reads.

### Design Motivation

STCS groups SSTables by size and compacts similar-sized files together. While this minimizes write amplification, it creates a fundamental problem: any partition key might exist in any SSTable. A point query must potentially check every SSTable.

LCS inverts this trade-off. By ensuring that SSTables within each level (except L0) cover disjoint key ranges, a point query needs to consider at most one SSTable per non-empty L1+ level that could contain the key. The cost is higher write amplification, as data is rewritten each time it progresses through levels.

| Aspect | STCS | LCS |
|--------|------|-----|
| SSTable organization | By size similarity | By key range per level |
| Read amplification | High (check many SSTables) | Low (one per level) |
| Write amplification | Lower | Higher (compounds across levels) |
| Space amplification | Medium-High | Low |
| Compaction predictability | Variable | Consistent |

---

## How LCS Works in Theory

### Level Structure

LCS organizes SSTables into numbered levels (L0 through L8) with specific properties. The maximum level count is 9 (`MAX_LEVEL_COUNT = 9` in the source code).

**Level 0 (L0):**

- Receives memtable flushes directly
- SSTables may have overlapping key ranges
- Target size: 4 × `sstable_size_in_mb` (default: 640MB)
- Stored in a HashSet (unordered by token range)
- Conceptually acts as a buffer between memory and the leveled structure

**Level 1+ (L1, L2, L3, ... L8):**

- SSTables have non-overlapping, contiguous key ranges
- Stored in TreeSets sorted by first token (with SSTable ID as tiebreaker)
- Each level has a target total size calculated as: `fanout_size^level × sstable_size_in_mb`
- Individual SSTable size is fixed (default 160MB)

**Level Size Targets (with defaults):**

| Level | Target Size Formula | Default Size |
|-------|---------------------|--------------|
| L0 | 4 × sstable_size | 640 MB |
| L1 | fanout × sstable_size | 1.6 GB |
| L2 | fanout² × sstable_size | 16 GB |
| L3 | fanout³ × sstable_size | 160 GB |
| L4 | fanout⁴ × sstable_size | 1.6 TB |
| L5 | fanout⁵ × sstable_size | 16 TB |
| L6 | fanout⁶ × sstable_size | 160 TB |
| L7 | fanout⁷ × sstable_size | 1.6 PB |
| L8 | fanout⁸ × sstable_size | 16 PB |

```plantuml
@startuml
skinparam backgroundColor white
title Leveled Compaction Strategy (LCS)

package "Level 0 (L0) - many small, overlapping SSTables" #F9E5FF {
    rectangle "SSTable" as L0_1 #7B4B96
    rectangle "SSTable" as L0_2 #7B4B96
    rectangle "SSTable" as L0_3 #7B4B96
    rectangle "SSTable" as L0_4 #7B4B96
    rectangle "SSTable" as L0_5 #7B4B96
    rectangle "SSTable" as L0_6 #7B4B96
}

package "Level 1 (L1) - non-overlapping by key range" #F5DCF9 {
    rectangle "SSTable\n[key A-M]" as L1_1 #7B4B96
    rectangle "SSTable\n[key N-T]" as L1_2 #7B4B96
    rectangle "SSTable\n[key U-Z]" as L1_3 #7B4B96
}

package "Level 2 (L2) - 10x size of L1, disjoint ranges" #F2D3F5 {
    rectangle "SSTable\n[key A-L]" as L2_1 #7B4B96
    rectangle "SSTable\n[key M-Z]" as L2_2 #7B4B96
}

L0_1 --> L1_1 : compaction\n(merge overlapping)
L0_2 --> L1_1
L0_3 --> L1_2
L0_4 --> L1_2
L0_5 --> L1_3
L0_6 --> L1_3

L1_1 --> L2_1 : compaction\n(when L1 > target)
L1_2 --> L2_1
L1_3 --> L2_2

note right of L2_2
    LCS properties:
    * Only L0 has overlapping SSTables
    * Each level has a target size
    * Higher levels have larger, fewer files
      with disjoint key ranges
end note

@enduml
```

### Compaction Mechanics

```plantuml
@startuml
skinparam backgroundColor white
skinparam ActivityBackgroundColor #F9E5FF
skinparam ActivityBorderColor #7B4B96
skinparam ActivityDiamondBackgroundColor #E8F5E9
skinparam ActivityDiamondBorderColor #4CAF50

title LCS Compaction Decision Flow

start

:Check level scores\n(highest level first);

if (Any level score > 1.001?) then (yes)
    :Select first level (highest to lowest)\nwhere score > 1.001;

    if (Level == L0?) then (yes)
        if (L0 count > 32?) then (yes)
            #FFE0E0:May run STCS within L0\n(fallback mode);
        else (no)
            :Select eligible L0 SSTables\n(by max timestamp ascending);
            :Add overlapping L0 SSTables;
            :Add overlapping L1 SSTables\n(if size > sstable_size);
        endif
    else (no)
        :Select next SSTable\n(round-robin from lastCompacted);
        :Find overlapping L(n+1) SSTables;
    endif

    :Execute compaction;
    :Update lastCompactedSSTables;

else (no)
    if (Tombstone compaction needed?) then (yes)
        :Find SSTable with\ndroppable tombstones > threshold;
        :Run single-SSTable compaction;
    else (no)
        :No compaction needed;
    endif
endif

stop
@enduml
```

#### Level Score and Compaction Triggering

Compaction priority is determined by calculating a score for each level:

$$\text{score} = \frac{\text{non-compacting bytes in level}}{\text{max bytes for level}}$$

Compaction is triggered when $\text{score} > 1.001$. The score is calculated using only the bytes from SSTables not currently involved in compaction. The compaction scheduler iterates from the highest level (L8) to the lowest, and selects the **first** level that exceeds the threshold — it does not compare scores across levels.

#### L0 → L1 Compaction

L0 compaction is triggered as part of the standard compaction selection process when no higher-priority levels require compaction. Unlike higher levels, L0 compaction is not driven directly by a score threshold. The candidate selection algorithm:

1. Sorts eligible L0 SSTables by max timestamp ascending
2. Iterates through sorted SSTables, adding each and its overlapping L0 peers into the candidate set
3. Caps candidate count at `max_threshold` (default: 32)
4. If the resulting L0 candidate set exceeds `maxSSTableSizeInBytes`, overlapping L1 SSTables are added and the compaction targets promotion out of L0; otherwise the compaction remains within L0
5. Requires minimum 2 SSTables to proceed with compaction

All selected SSTables are merged. Output is written to L1 when compaction size exceeds `maxSSTableSizeInBytes`; otherwise the result remains in L0.

#### L0 STCS Fallback

When L0 contains more than 32 SSTables (`MAX_COMPACTING_L0 = 32`) and STCS-in-L0 is not disabled, Cassandra may perform STCS-style compaction within L0, provided `getSSTablesForSTCS(...)` returns a non-empty bucket. This compacts similarly-sized L0 SSTables together, reducing SSTable count more quickly than waiting for L1 capacity. This behavior can be disabled with `-Dcassandra.disable_stcs_in_l0=true`.

#### L(n) → L(n+1) Compaction

When a level exceeds its size target (score > 1.001), the compaction process:

1. Selects the next SSTable in round-robin order from `lastCompactedSSTables[level]` position
2. Skips SSTables that are currently compacting or marked as suspect
3. Identifies all overlapping SSTables in L(n+1)
4. Merges and rewrites all selected SSTables to L(n+1)
5. Updates `lastCompactedSSTables[level]` to track position for next round

This round-robin approach ensures fair distribution of compaction work across the token range.

#### Starvation Prevention

The manifest tracks rounds without high-level compaction using `NO_COMPACTION_LIMIT = 25`. If 25 consecutive compaction rounds occur without selecting SSTables from higher levels, starved SSTables may be pulled into lower-level compactions to ensure data eventually progresses through levels.

#### Single SSTable Uplevel

When `single_sstable_uplevel` is enabled (default: false), and the compaction task contains exactly one SSTable and is not a tombstone compaction, Cassandra may create a `SingleSSTableLCSTask` that promotes the SSTable to a higher level without rewriting, subject to level placement rules enforced by the manifest.


### Write Amplification Calculation

Write amplification in LCS is determined by how many times data is rewritten as it moves through levels:

**Write path for one piece of data:**

1. Written to memtable (memory)
2. Flushed to L0 (1 write)
3. Compacted L0 → L1 (1 write)
4. Compacted L1 → L2 (potentially 10 writes, merging with ~10 L2 files)
5. Compacted L2 → L3 (potentially 10 writes)
6. Continue through higher levels...

The conceptual worst-case write amplification is approximately:

$$\text{WA} \approx f \times L$$

Where $f$ = fanout (default 10) and $L$ = number of populated levels. This is a theoretical approximation, not a code-defined contract. Actual write amplification depends on workload characteristics, data distribution, overlap patterns, and whether optimizations like `single_sstable_uplevel` are enabled.

### Read Amplification

L1+ levels are maintained as non-overlapping by token range, so a point read needs to consider at most one SSTable per non-empty level that could contain the key. Bloom filters and range pruning further reduce actual I/O.

**Structural upper bound from levels alone:**

- L0: overlap set (variable count, typically low under normal compaction)
- L1–L8: at most one SSTable per non-empty level

Under healthy conditions with timely compaction, L0 typically contains only a few SSTables. The bounded nature of L1–L8 provides more predictable read latency than STCS, where a point query may need to check many SSTables.

---

## Benefits

### Predictable Read Latency

The bounded number of SSTables per read provides consistent latency:

- Bounded SSTable checks per level reduces read latency variance
- Read performance is less sensitive to data age than with STCS

### Low Space Amplification

Unlike STCS, which may temporarily require 2× space during large compactions, LCS operates incrementally:

- Compactions involve small, bounded sets of files
- Temporary space overhead is minimal
- Easier capacity planning

### Tombstone Compaction

When no standard compaction candidate is found, LCS may attempt single-SSTable tombstone compaction. It scans levels from highest to lowest, looking for SSTables with droppable tombstone ratio exceeding `tombstone_threshold`, subject to safety checks via `worthDroppingTombstones(...)`.

- Data moves through levels, giving tombstones opportunities to be purged
- Dedicated tombstone compaction path exists as a fallback

### Consistent Compaction Load

Compaction work is distributed evenly over time:

- No massive compaction events
- More predictable I/O patterns
- Easier to provision for sustained throughput

---

## Drawbacks

### High Write Amplification

The primary cost of LCS is rewriting data multiple times:

- Each level transition involves merging with existing data
- Actual write amplification depends on workload characteristics, data distribution, and configuration
- SSD endurance is consumed faster

### Compaction Throughput Limits

Write rate is bounded by how fast compaction can promote data:

- If writes exceed L0→L1 compaction rate, L0 backs up
- L0 backlog increases read amplification (defeating LCS purpose)
- May require throttling writes

### Inefficient for Write-Heavy Workloads

Write-heavy workloads may experience:

- Compaction unable to keep pace
- Growing pending compaction tasks
- Disk I/O saturated by compaction

### Poor Fit for Time-Series

Time-series data has sequential writes and time-based queries:

- LCS wastes effort organizing by key range
- TWCS or UCS with tiered configuration may be more suitable
- LCS key-range organization does not align with time-based access patterns

### Large Partition Problems

Large partitions may produce SSTables larger than `sstable_size_in_mb`, which can degrade compaction efficiency:

- May stall compaction progress
- Require data model changes to address

---

## When to Use LCS

### Ideal Use Cases

| Workload Pattern | Why LCS Works |
|------------------|---------------|
| Read-heavy workloads | Low read amplification pays for write cost |
| Point queries | Bounded SSTable checks per query |
| Frequently updated rows | Versions consolidated quickly |
| Latency-sensitive reads | Predictable, consistent response times |
| SSD storage | Handles write amplification efficiently |

### Avoid LCS When

| Workload Pattern | Why LCS Is Wrong |
|------------------|------------------|
| Write-heavy workloads | Write amplification overwhelms I/O |
| Time-series data | TWCS is more efficient |
| Append-only logs | STCS or TWCS better suited |
| HDD storage | Random I/O from compaction is slow |
| Very large datasets | Compaction may not keep pace |

---

## Configuration

```sql
CREATE TABLE my_table (
    id uuid PRIMARY KEY,
    data text
) WITH compaction = {
    'class': 'LeveledCompactionStrategy',

    -- Target size for each SSTable
    -- Smaller = more SSTables, more compaction overhead
    -- Larger = bigger compaction operations
    'sstable_size_in_mb': 160,  -- Default: 160MB

    -- Size multiplier between levels (fanout)
    -- Default 10 means L2 is 10x L1
    'fanout_size': 10  -- Default: 10
};
```

### Configuration Parameters

#### LCS-Specific Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `sstable_size_in_mb` | 160 | Target size for individual SSTables in megabytes. Smaller values increase SSTable count and compaction frequency; larger values reduce compaction overhead but increase individual compaction duration. |
| `fanout_size` | 10 | Size multiplier between adjacent levels. Level L(n+1) has a target capacity of fanout_size × L(n). Higher values reduce the number of levels but increase write amplification per level transition. |
| `single_sstable_uplevel` | false | When enabled, allows a single SSTable compaction task to be handled as a `SingleSSTableLCSTask` instead of a standard `LeveledCompactionTask`, provided the task is not a tombstone compaction and contains exactly one SSTable. Resulting level placement remains subject to manifest rules. |

#### Common Compaction Options

These options apply to all compaction strategies:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `enabled` | true | Enables background compaction. When set to false, automatic compaction is disabled but the strategy configuration is retained. |
| `tombstone_threshold` | 0.2 | Ratio of garbage-collectable tombstones to total columns that triggers single-SSTable compaction. A value of 0.2 means compaction is triggered when 20% of the SSTable consists of droppable tombstones. |
| `tombstone_compaction_interval` | 86400 | Minimum time in seconds between tombstone compaction attempts for the same SSTable. Prevents continuous recompaction of SSTables that cannot yet drop tombstones. |
| `unchecked_tombstone_compaction` | false | When true, bypasses pre-checking for tombstone compaction eligibility. Tombstones are still only dropped when safe to do so. |
| `only_purge_repaired_tombstones` | false | When true, tombstones are only purged from SSTables that have been marked as repaired. Useful for preventing data resurrection in clusters with inconsistent repair schedules. |
| `log_all` | false | Enables detailed compaction logging to a separate log file in the log directory. Useful for debugging compaction behavior. |

### Startup Options

The following JVM option affects LCS behavior:

| Option | Description |
|--------|-------------|
| `-Dcassandra.disable_stcs_in_l0=true` | Disables STCS-style compaction in L0. By default, when L0 accumulates more than 32 SSTables, Cassandra may perform STCS compaction within L0 if an eligible STCS bucket is found, to reduce the SSTable count more quickly. This option disables that behavior. |

### Level Size Calculation

The target size for each level is calculated using the formula:

$$\text{maxBytesForLevel}(L) = f^L \times s$$

Where:

- $L$ = level number (1-8)
- $f$ = `fanout_size` (default: 10)
- $s$ = `sstable_size_in_mb` (default: 160 MB)

**Special case for L0:**

$$\text{maxBytesForLevel}(0) = 4 \times s$$

**With default values ($s = 160\text{MB}$, $f = 10$):**

| Level | Formula | Target Size |
|-------|---------|-------------|
| L0 | $4 \times 160\text{MB}$ | 640 MB |
| L1 | $10^1 \times 160\text{MB}$ | 1.6 GB |
| L2 | $10^2 \times 160\text{MB}$ | 16 GB |
| L3 | $10^3 \times 160\text{MB}$ | 160 GB |
| L4 | $10^4 \times 160\text{MB}$ | 1.6 TB |
| L5 | $10^5 \times 160\text{MB}$ | 16 TB |
| L6 | $10^6 \times 160\text{MB}$ | 160 TB |
| L7 | $10^7 \times 160\text{MB}$ | 1.6 PB |
| L8 | $10^8 \times 160\text{MB}$ | 16 PB |

The maximum dataset size per table with default settings is theoretically 16+ PB, though practical limits are reached well before this due to compaction throughput constraints.

---

## Write Amplification Analysis

LCS has high write amplification due to the promotion process. The following figures are theoretical maximums; actual amplification depends on workload characteristics, data distribution, update patterns, and configuration.

**Per-level amplification (theoretical):**

- L0 → L1: SSTable overlaps with potentially all L1 SSTables → up to $\sim 10\times$
- L1 → L2: Same process with L2 overlaps → up to $\sim 10\times$
- Each subsequent level: up to $\sim f\times$ where $f$ = fanout

**Total write amplification (theoretical maximum):**

$$W_{\text{total}} \approx f \times L$$

Where:

- $f$ = fanout (default: 10)
- $L$ = number of levels data traverses

**Example:** 100GB dataset with 5 levels (worst case):

$$W = 10 \times 5 = 50\times$$

In practice, write amplification is often lower due to factors like non-uniform key distribution, `single_sstable_uplevel` optimization, and varying overlap patterns. However, the high theoretical amplification makes LCS generally unsuitable for write-heavy workloads.

---

## Read Path Analysis

LCS provides predictable, low read amplification through its non-overlapping level structure:

**For a single partition read:**

1. Check L0 SSTables (overlapping, count varies with write rate)
2. Check at most 1 SSTable per level L1-L8 (non-overlapping)

**Structural bound from leveled layout:**

- L0: all overlapping SSTables that must be considered
- L1–L8: at most one SSTable per non-empty level that could contain the key

The key advantage is predictability: LCS bounds the number of SSTables that must be consulted per read, while STCS SSTable count can grow unbounded.

---

## Production Issues

### Issue 1: L0 Compaction Backlog

**Symptoms:**

- L0 SSTable count growing (warning at 5+, critical at 32+)
- Read latency increasing proportionally to L0 count
- Compaction pending tasks growing
- At 32+ L0 SSTables, STCS fallback may be triggered

**Diagnosis:**

```bash
nodetool tablestats keyspace.table | grep "SSTables in each level"
# Output: [15, 10, 100, 1000, ...]
# 15 L0 SSTables indicates moderate backlog

# Check if L0 size exceeds target (4 × sstable_size = 640MB default)
nodetool tablestats keyspace.table | grep -E "Space used|SSTable"
```

**Causes:**

- Write rate exceeds L0→L1 compaction throughput
- Insufficient compaction threads
- Disk I/O bottleneck
- Large L1 causing extensive overlap during L0→L1 compaction

**Solutions:**

1. Increase compaction throughput:
   ```bash
   nodetool setcompactionthroughput 128  # MB/s
   ```

2. Add concurrent compactors:
   ```bash
   nodetool setconcurrentcompactors 4
   ```

3. Reduce write rate temporarily

4. Consider switching to STCS if write-heavy

5. If L0 exceeds 32 SSTables, STCS fallback may be triggered (can be disabled with `-Dcassandra.disable_stcs_in_l0=true` if necessary)

### Issue 2: Large Partitions Stalling Compaction

**Symptoms:**

- Compaction stuck at same percentage
- One SSTable significantly larger than `sstable_size_in_mb`

**Diagnosis:**

```bash
nodetool tablestats keyspace.table | grep "Compacted partition maximum"
# Output: Compacted partition maximum bytes: 2147483648
# 2GB partition exceeds 160MB target
```

**Cause:**

When a single partition exceeds `sstable_size_in_mb`, the resulting SSTable is "oversized" and may not compact efficiently.

**Solutions:**

1. Fix data model to break up large partitions:
   ```sql
   -- Add time bucket to partition key
   PRIMARY KEY ((user_id, date_bucket), event_time)
   ```

2. Increase SSTable size (affects all compaction):
   ```sql
   ALTER TABLE keyspace.table WITH compaction = {
       'class': 'LeveledCompactionStrategy',
       'sstable_size_in_mb': 320
   };
   ```

### Issue 3: Write Amplification Overwhelming Disks

**Symptoms:**

- Disk throughput at 100%
- High iowait in system metrics
- Write latency increasing

**Diagnosis:**

```bash
iostat -x 1
# Check %util approaching 100%

nodetool compactionstats
# Check bytes compacted vs. bytes written
```

**Solutions:**

1. Switch to STCS for write-heavy tables:
   ```sql
   ALTER TABLE keyspace.table WITH compaction = {
       'class': 'SizeTieredCompactionStrategy'
   };
   ```

2. Throttle compaction to reduce I/O competition:
   ```bash
   nodetool setcompactionthroughput 32
   ```

3. Add more nodes to spread write load

---

## Tuning Recommendations

### Read-Heavy, Low Latency

```sql
ALTER TABLE keyspace.table WITH compaction = {
    'class': 'LeveledCompactionStrategy',
    'sstable_size_in_mb': 160  -- Default, good for most cases
};
```

### Larger Partitions

```sql
ALTER TABLE keyspace.table WITH compaction = {
    'class': 'LeveledCompactionStrategy',
    'sstable_size_in_mb': 320  -- Accommodate larger partitions
};
```

### Reduce Compaction Overhead

```sql
ALTER TABLE keyspace.table WITH compaction = {
    'class': 'LeveledCompactionStrategy',
    'sstable_size_in_mb': 256,
    'fanout_size': 10
};
```

---

## Monitoring LCS

### Key Indicators

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| L0 SSTable count | ≤4 | 5-15 | >32 (STCS fallback may be triggered) |
| Pending compactions | <20 | 20-50 | >50 |
| Level distribution | Pyramid shape | L0 growing | L0 >> L1 |
| Write latency | Stable | Increasing | Spiking |
| Level score (any level) | <1.0 | 1.0-1.5 | >1.5 |

### Commands

```bash
# SSTable count per level
nodetool tablestats keyspace.table | grep "SSTables in each level"

# Expected output for healthy LCS:
# SSTables in each level: [2, 10, 100, 500, 0, 0, 0, 0, 0]
#                          L0  L1  L2   L3  L4 L5 L6 L7 L8

# Warning (L0 building up):
# SSTables in each level: [12, 10, 100, 500, 0, 0, 0, 0, 0]

# Critical (L0 backlog, STCS will kick in):
# SSTables in each level: [45, 10, 100, 500, 0, 0, 0, 0, 0]

# Check compaction pending tasks
nodetool compactionstats

# View detailed level information
nodetool cfstats keyspace.table
```

### JMX Metrics

```
# Per-level SSTable counts
org.apache.cassandra.metrics:type=Table,keyspace=*,scope=*,name=SSTablesPerLevel

# Compaction bytes written
org.apache.cassandra.metrics:type=Table,keyspace=*,scope=*,name=BytesCompacted

# Pending compaction bytes estimate
org.apache.cassandra.metrics:type=Table,keyspace=*,scope=*,name=PendingCompactions

# Compaction throughput
org.apache.cassandra.metrics:type=Compaction,name=BytesCompacted
```

### Level Health Check

A healthy LCS table should show:

1. **L0**: Small count (typically 0-4 SSTables)
2. **L1**: Multiple SSTables up to its configured capacity; exact count depends on SSTable sizes and compaction progress
3. **Higher levels**: Level capacity increases geometrically with depth; SSTable distribution often trends that way under steady-state compaction

---

## Implementation Internals

This section documents implementation details from the Cassandra source code that affect operational behavior.

### SSTable Level Assignment

When an SSTable is added to the manifest (e.g., after streaming or compaction), the level assignment follows these rules:

1. **Recorded level check**: Each SSTable stores its intended level in metadata via `getSSTableLevel()`
2. **Overlap verification for L1+**: Before placing an SSTable in L1 or higher, the manifest checks for overlaps with existing SSTables in that level
3. **Demotion to L0**: If overlap is detected (`before.last >= newsstable.first` or `after.first <= newsstable.last`), the SSTable is demoted to L0 regardless of its recorded level

This behavior ensures the non-overlapping invariant is maintained even when SSTables arrive from external sources (streaming, sstableloader).

### Internal Data Structures

```
LeveledGenerations:
├── L0: HashSet<SSTableReader>        // Unordered, overlapping allowed
└── levels[0-7]: TreeSet<SSTableReader>  // L1-L8, sorted by first token
    └── Comparator: firstKey, then SSTableId (tiebreaker)

LeveledManifest:
├── generations: LeveledGenerations
├── lastCompactedSSTables[]: SSTableReader  // Round-robin tracking per level
├── compactionCounter: int                  // For starvation prevention
└── levelFanoutSize: int                    // Default: 10
```

### Compaction Writer Selection

The compaction task selects its writer based on the operation type. Based on compaction writer implementation (not shown in the LCS strategy source):

| Condition | Writer | Behavior |
|-----------|--------|----------|
| Major compaction | `MajorLeveledCompactionWriter` | Full reorganization, respects level structure |
| Standard compaction | `MaxSSTableSizeWriter` | Outputs SSTables at target size, assigned to destination level |

### Anti-Compaction Behavior

During streaming operations that require anti-compaction (splitting SSTables by token range), LCS groups SSTables in batches of 2 per level to maintain level-specific guarantees while processing.

### Constants Reference

| Constant | Value | Description |
|----------|-------|-------------|
| `MAX_LEVEL_COUNT` | 9 | L0 through L8 |
| `MAX_COMPACTING_L0` | 32 | Threshold for L0 STCS fallback |
| `NO_COMPACTION_LIMIT` | 25 | Rounds before starvation prevention |
| Minimum SSTable size | 1 MiB | Validation constraint |
| Minimum fanout size | 1 | Validation constraint |
| Default fanout | 10 | Level size multiplier |
| Default SSTable size | 160 MiB | Target per-SSTable size |

---

## Related Documentation

- **[Compaction Overview](index.md)** - Concepts and strategy selection
- **[Size-Tiered Compaction (STCS)](stcs.md)** - Alternative for write-heavy workloads
- **[Time-Window Compaction (TWCS)](twcs.md)** - Optimized for time-series data with TTL
- **[Unified Compaction (UCS)](ucs.md)** - Recommended strategy for Cassandra 5.0+
- **[Compaction Management](../../../operations/compaction-management/index.md)** - Tuning and troubleshooting