---
title: "Cassandra Unified Compaction Strategy (UCS)"
description: "Unified Compaction Strategy (UCS) in Cassandra 5.0. Next-generation adaptive compaction."
meta:
  - name: keywords
    content: "UCS, Unified Compaction, Cassandra 5.0, adaptive compaction"
---

# Unified Compaction Strategy (UCS)

UCS (Cassandra 5.0+) is an adaptive compaction strategy that unifies tiered and leveled compaction, using sharding and density-based triggering to provide flexible compaction behavior across varying workloads.

---

## Background and History

### Origins

Unified Compaction Strategy was introduced in Cassandra 5.0 (CEP-26). The key observation driving UCS, as stated in the [design document](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/db/compaction/UnifiedCompactionStrategy.md), is that tiered and leveled compaction can be generalized as the same density-based framework: both form exponentially-growing levels based on SSTable density and trigger compaction when a threshold number of SSTables are present on one level. UCS provides a unified framework where this trade-off is configurable through `scaling_parameters`.

### Design Motivation

Each traditional strategy has fundamental limitations:

**STCS limitations:**
- No upper bound on read amplification
- Large SSTables accumulate without compacting
- Space amplification during major compactions

**LCS limitations:**
- High write amplification (~10× per level)
- L0 backlog under write pressure
- Cannot keep pace with write-heavy workloads

**TWCS limitations:**
- Only suitable for append-only time-series
- Breaks with out-of-order writes or updates
- Tombstone handling issues

UCS addresses these by:

1. **Unifying the compaction model**: A single configurable strategy unifies tiered and leveled compaction within one implementation
2. **Sharding**: Shard-aligned token boundaries used to split output and improve parallelism
3. **Density-based triggering**: Compaction decisions based on data density, not just counts
4. **Configurable read/write trade-off**: `scaling_parameters` adjusts behavior

---

## How UCS Works in Theory

### Core Concepts

UCS introduces several concepts that differ from traditional strategies:

**Shards**: UCS uses shard-aligned token boundaries to split flush and compaction output. The effective number of shards is density-dependent, and sharding helps bound SSTable size and improve parallelism.

**Runs**: A sequence of SSTables that collectively represent one "generation" of data. Runs replace the concept of levels (LCS) or tiers (STCS).

**Density**: The amount of data per token range unit. UCS triggers compaction when density reaches thresholds, not when SSTable counts reach thresholds.

**Scaling Parameters**: One or more values (for example `T4` or `T4, T4, L10`) that determine whether UCS behaves more tiered or more leveled at each level.



### Shard Structure

```plantuml
@startuml
skinparam backgroundColor white
title Token Range Sharding (base_shard_count = 4)

skinparam packageBackgroundColor #F9E5FF
skinparam packageBorderColor #7B4B96

skinparam rectangle {
    BackgroundColor #7B4B96
    FontColor white
    BorderColor #5A3670
    roundCorner 10
}

package "Shard 0\n[-2^63, -2^61)" as S0 #F4E5FF {
    rectangle "SSTable" as s0a
    rectangle "SSTable" as s0b
    rectangle "SSTable" as s0c
    rectangle "Shard-aligned\noutput" as comp0
}

package "Shard 1\n[-2^61, 0)" as S1 #F1DBFA {
    rectangle "SSTable" as s1a
    rectangle "SSTable" as s1b
    rectangle "SSTable" as s1c
    rectangle "Shard-aligned\noutput" as comp1
}

package "Shard 2\n[0, 2^61)" as S2 #EED0F5 {
    rectangle "SSTable" as s2a
    rectangle "SSTable" as s2b
    rectangle "SSTable" as s2c
    rectangle "Shard-aligned\noutput" as comp2
}

package "Shard 3\n[2^61, 2^63]" as S3 #E8C4F1 {
    rectangle "SSTable" as s3a
    rectangle "SSTable" as s3b
    rectangle "SSTable" as s3c
    rectangle "Shard-aligned\noutput" as comp3
}

s0a -down-> comp0
s0b -down-> comp0
s0c -down-> comp0

s1a -down-> comp1
s1b -down-> comp1
s1c -down-> comp1

s2a -down-> comp2
s2b -down-> comp2
s2c -down-> comp2

s3a -down-> comp3
s3b -down-> comp3
s3c -down-> comp3

S0 -[hidden]right- S1
S1 -[hidden]right- S2
S2 -[hidden]right- S3

note as N1 #FFFDE7
  Output is split at shard boundaries
  enabling parallelism and
  bounded SSTable size
end note
@enduml
```

UCS uses shard boundaries to split output SSTables at token boundaries. This helps:

- **Parallelism**: Output can be split across multiple shard-aligned writers
- **Bounded scope**: Output SSTables are constrained by shard boundaries
- **Consistent layout**: Lower-level split points remain valid for higher-density levels

!!! note "Example Only"
    The diagram above illustrates a fixed base shard count. In practice, UCS shard count is determined dynamically from density and may be below, equal to, or above `base_shard_count`.

### Tiered Mode (T)

When `scaling_parameters` starts with `T` (e.g., T4), UCS behaves similarly to STCS:

```plantuml
@startuml
skinparam backgroundColor white
title T4 Behavior Within a Shard

skinparam rectangle {
    BackgroundColor #7B4B96
    FontColor white
    BorderColor #5A3670
    roundCorner 10
}

rectangle "1 MB" as s1
rectangle "1 MB" as s2
rectangle "1 MB" as s3
rectangle "1 MB" as s4

rectangle "4 MB" as big #9B6BB6

s1 -[hidden]right- s2
s2 -[hidden]right- s3
s3 -[hidden]right- s4

s1 -down-> big : compact when\n4 accumulate
s2 -down-> big
s3 -down-> big
s4 -down-> big

note bottom of big #FFFDE7
  Write amplification: ~log4(data_size)
  Read amplification: multiple SSTables per query
end note
@enduml
```

The number after `T` specifies the fanout—how many SSTables accumulate before compaction. Higher values (T8, T16) reduce write amplification but increase read amplification.

### Leveled Mode (L)

When `scaling_parameters` starts with `L` (e.g., L10), UCS behaves similarly to LCS:

```plantuml
@startuml
skinparam backgroundColor white
title L10 Behavior Within a Shard

skinparam rectangle {
    BackgroundColor #7B4B96
    FontColor white
    BorderColor #5A3670
    roundCorner 10
}

package "Level 0" as L0 #F9E5FF {
    rectangle "flush" as l0_1
    rectangle "flush" as l0_2
    rectangle "flush" as l0_3
    rectangle "flush" as l0_4
}

package "Level 1" as L1 #F3DAFA {
    rectangle "~10x L0 size" as L1Box
}

package "Level 2" as L2 #EED0F5 {
    rectangle "~10x L1 size" as L2Box
}

l0_1 -[hidden]right- l0_2
l0_2 -[hidden]right- l0_3
l0_3 -[hidden]right- l0_4

L0 -[hidden]down- L1
L1 -[hidden]down- L2

l0_3 -down-> L1Box : compact to L1\nwhen threshold reached
L1Box -down-> L2Box : promote when L1 full

note bottom of L2 #FFFDE7
  Write amplification: ~10x per level
  Read amplification: bounded (one SSTable per level per shard)
end note
@enduml
```


The number after `L` specifies the size ratio between levels. L10 means each level is 10× larger than the previous, matching classic LCS behavior.

### Density-Based Triggering

Unlike traditional strategies that trigger on SSTable count, UCS uses density:

$$d = \frac{s}{v}$$

Where:

- $d$ = density
- $s$ = SSTable size
- $v$ = fraction of token space covered by the SSTable

**Traditional (count-based):** Trigger when $\text{SSTable count} \geq \text{min threshold}$

- Problem: Doesn't account for SSTable sizes or overlap

**UCS (density-based):** Trigger when density exceeds threshold for shard

- Advantage: Considers actual data distribution

**Example:**

- Shard covers 25% of token range ($v = 0.25$)
- Shard contains 10GB of data ($s = 10\text{GB}$)
- Density $d = \frac{10\text{GB}}{0.25} = 40\text{GB}$ effective
- If target density is 32GB, compaction triggers

This approach prevents the "large SSTable accumulation" problem of STCS while avoiding unnecessary compaction of sparse data.

### Level Assignment

SSTables are assigned to levels based on their size relative to the memtable flush size:

$$L = \begin{cases} \left\lfloor \log_f \frac{s}{m} \right\rfloor & \text{if } s \geq m \\ 0 & \text{otherwise} \end{cases}$$

Where:

- $L$ = level number
- $f$ = fanout (derived from scaling parameter)
- $s$ = SSTable size (or density in sharded mode)
- $m$ = memtable flush size (observed or overridden via `flush_size_override`)

This creates exponentially-growing size ranges per level:

| Level | Min SSTable size | Max SSTable size |
|-------|-----------------|-----------------|
| 0 | 0 | $m \cdot f$ |
| 1 | $m \cdot f$ | $m \cdot f^2$ |
| 2 | $m \cdot f^2$ | $m \cdot f^3$ |
| n | $m \cdot f^n$ | $m \cdot f^{n+1}$ |

Level 0 contains SSTables below $m \times f$, level 1 contains SSTables from $m \times f$ up to $m \times f^2$, level 2 from $m \times f^2$ up to $m \times f^3$, and so on.

The maximal number of levels for a dataset is inversely proportional to $\log f$ — substituting the maximal dataset size $D$ into the level formula above gives the upper bound.

---

## Benefits

### Configurable Trade-offs

The primary advantage of UCS is tunable behavior:

- **T4**: STCS-like, optimize for writes
- **L10**: LCS-like, optimize for reads
- **T8, L4, etc.**: Intermediate points on the spectrum
- Change with ALTER TABLE—no data rewrite needed

### Parallel Compaction

Sharding enables efficient use of modern hardware:

- Output split across shard-aligned writers enables concurrent work
- Shard boundaries provide consistent split points across density levels
- Scales with CPU core count
- Reduces wall-clock time for compaction

### Bounded Read Amplification

Even in tiered mode, UCS provides better bounds than STCS:

- Shard-bounded output and overlap-based selection help keep read amplification more predictable
- Density-based triggering prevents unbounded accumulation
- More predictable read performance

### Unified Codebase

Single strategy implementation simplifies Cassandra:

- A single implementation reduces the complexity of maintaining separate compaction strategies
- Consistent behavior across configurations
- Easier to test and maintain
- Bug fixes benefit all configurations

### Smooth Migration

Transitioning from traditional strategies is straightforward:

- ALTER TABLE to enable UCS immediately
- Existing SSTables remain valid
- Gradual transition as compaction runs
- No major compaction required

---

## Drawbacks

### Newer Strategy

UCS has less production history than traditional strategies:

- Introduced in Cassandra 5.0
- Less community experience with edge cases
- Fewer tuning guides and best practices available
- Some workloads may have undiscovered issues

### Learning Curve

Different conceptual model requires adjustment:

- Shards and runs vs levels and tiers
- Density-based vs count-based triggering
- New configuration parameters to understand
- Existing STCS/LCS expertise doesn't directly transfer

### Time-Series Trade-offs

TWCS and UCS each have strengths for time-series workloads:

- TWCS drops entire SSTables on TTL expiry (efficient for pure append-only data)
- UCS handles out-of-order writes and updates more gracefully than TWCS
- UCS can be configured for time-series using higher tiered fanout (e.g., T8) with `expired_sstable_check_frequency_seconds` tuned for the TTL pattern
- The Apache Cassandra documentation recommends UCS for most workloads, including time-series

### Shard Overhead

Sharding adds some overhead:

- Minimum SSTable size per shard
- More metadata to track
- Very small tables may not benefit
- Configuration requires understanding data size

### Major Compaction Behavior

!!! warning "Major Compaction Behavior"
    When maximal compaction is requested, UCS groups SSTables into non-overlapping sets and creates one compaction task per set, with output split across shard boundaries. The number of tasks depends on the overlap structure of the data, not directly on `base_shard_count`. Verify actual behavior in the target environment before assuming a specific level of parallelism.

### Migration Considerations

While migration is smooth, considerations exist:

- Existing tuning may not transfer directly
- Monitoring dashboards need updates
- Operational procedures may need revision
- Testing required before production migration

---

## When to Use UCS

### Ideal Use Cases

| Workload Pattern | Configuration | Why UCS Works |
|------------------|---------------|---------------|
| New Cassandra 5.0+ clusters | T4 (default) | Modern, unified approach |
| Mixed read/write workloads | T4 | Balanced trade-offs |
| High-core-count servers | base_shard_count=16 | Parallel compaction |
| Workloads that evolve | T4, then adjust | Easy reconfiguration |
| Large datasets | T4, target_sstable_size=5GiB | Efficient compaction |

### Consider Alternatives When

| Workload Pattern | Alternative | Rationale |
|------------------|-------------|-----------|
| Cassandra < 5.0 | STCS/LCS | UCS not available |
| Well-tuned existing cluster | Keep current | Migration has risk |
| Very small tables | STCS | Shard overhead not justified |

!!! note "UCS and Time-Series Workloads"
    The Apache Cassandra 5.0 documentation recommends UCS for most workloads including time-series, and provides a time-series configuration example using `T8` with `expired_sstable_check_frequency_seconds=300`. TWCS remains a valid choice for pure append-only time-series with TTL, but UCS should not be ruled out without testing.

---

## Sharding

UCS divides the token range into shards, enabling:

- **Output splitting**: Compaction output is split across shard boundaries, allowing parallelism and better size control
- **Bounded SSTable size**: Output SSTables are constrained by shard boundaries
- **Consistent split points**: Shard boundaries for a given density are also boundaries for all higher densities

```
Token range: -2^63 to 2^63
With 4 base shards:

Shard 0: tokens -2^63 to -2^61
Shard 1: tokens -2^61 to 0
Shard 2: tokens 0 to 2^61
Shard 3: tokens 2^61 to 2^63

Output SSTables are written according to shard boundaries, while
compaction selection is driven by density levels and overlap relationships.
```

### Shard Count Calculation

The number of shards scales dynamically with data density using a four-case formula:

$$S = \begin{cases} 1 & \text{if } d < m \\ \min\left(2^{\lfloor \log_2 \frac{d}{m} \rfloor}, x\right) & \text{if } d < m \cdot b \text{, where } x \text{ is the largest power-of-2 divisor of } b \\ b & \text{if } d < t \cdot b \\ 2^{\lfloor (1-\lambda) \cdot \log_2 (\frac{d}{t} \cdot \frac{1}{b}) \rceil} \cdot b & \text{otherwise} \end{cases}$$

Where:

- $S$ = number of shards
- $d$ = density (data size / token fraction)
- $m$ = `min_sstable_size` (default: 100 MiB)
- $b$ = `base_shard_count` (default: 4)
- $x$ = largest power-of-2 divisor of $b$ (e.g. if $b = 12$, then $x = 4$)
- $t$ = `target_sstable_size` (default: 1 GiB)
- $\lambda$ = `sstable_growth` (default: 0.333)
- $\lfloor \cdot \rceil$ = round to nearest integer

**Case breakdown:**

1. **Very small data** ($d < m$): Single shard, no splitting
2. **Small data** ($d < m \cdot b$): Shard count grows up to base count
3. **Medium data** ($d < t \cdot b$): Fixed at base shard count
4. **Large data**: Shard count doubles as density increases, modulated by growth factor $\lambda$

This ensures power-of-two boundaries for efficient token range splitting while preventing over-sharding of small datasets.

### Growth Component ($\lambda$) Effects

The `sstable_growth` parameter ($\lambda$) controls the trade-off between increasing shard count vs. increasing SSTable size:

| $\lambda$ Value | Shard Growth | SSTable Size | Use Case |
|---------|--------------|--------------|----------|
| 0 | Grows with density | Fixed at target | Many small SSTables, maximum parallelism |
| 0.333 (default) | Intermediate growth | SSTable size grows as the cubic root of density growth | Balanced: both grow moderately |
| 0.5 | Square-root growth | Square-root growth | Equal growth for both |
| 1 | Fixed at base count | Grows with density | Fewer large SSTables, less parallelism |

*Note: Actual behavior depends on data distribution and may not match theoretical growth patterns exactly.*

**Detailed effects:**

- **$\lambda = 0$**: Shard count grows proportionally with density; SSTable size stays fixed at `target_sstable_size`
- **$\lambda = 0.333$**: SSTable size growth is the cubic root of density growth; equivalently, SSTable size grows with the square root of the growth of the shard count
- **$\lambda = 0.5$**: When density quadruples, both SSTable size and shard count double
- **$\lambda = 1$**: Shard count fixed at `base_shard_count`; SSTable size grows linearly with density

### Output SSTable Sizing

Compaction output SSTables target sizes between:

$$\frac{s_t}{\sqrt{2}} \leq \text{output size} \leq s_t \times \sqrt{2}$$

Where $s_t$ = `target_sstable_size`.

With default 1 GiB target:

- Minimum: $\frac{1024}{\sqrt{2}} \approx 724$ MiB
- Maximum: $1024 \times \sqrt{2} \approx 1448$ MiB

SSTables are split at predefined power-of-two shard boundaries, ensuring consistent boundaries across all density levels.

---

## Configuration

```sql
CREATE TABLE my_table (
    id uuid PRIMARY KEY,
    data text
) WITH compaction = {
    'class': 'UnifiedCompactionStrategy',

    -- Scaling parameter (strategy behavior)
    -- T = Tiered (STCS-like), number is fanout
    -- L = Leveled (LCS-like), number is fanout
    -- N = Balanced (midpoint between tiered and leveled, equivalent to T2/L2)
    'scaling_parameters': 'T4',

    -- Target SSTable size
    'target_sstable_size': '1GiB',

    -- Base shard count
    'base_shard_count': 4,

    -- Minimum SSTable size (prevents over-sharding small data)
    'min_sstable_size': '100MiB'
};
```

### Configuration Parameters

#### UCS-Specific Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `scaling_parameters` | T4 | Strategy behavior: T (tiered), L (leveled), N (balanced) with fanout. Controls the read/write trade-off. Multiple comma-separated values can specify different behavior per level. |
| `target_sstable_size` | 1 GiB | Target size for output SSTables. Actual sizes may vary between √0.5 and √2 times this value based on sharding calculations. |
| `base_shard_count` | 4 | Base shard count used by UCS when determining output sharding. Actual shard count scales with data density using the `sstable_growth` modifier. Must be a positive integer. |
| `min_sstable_size` | 100 MiB | Minimum SSTable size before sharding applies. Data below this threshold is not split into shards. A value of 0 disables this limit. |
| `sstable_growth` | 0.333 | Controls how shard count grows with data density. Range 0-1. Value of 0 maintains fixed target size; 1 prevents splitting beyond base count. At the default of 0.333, SSTable size growth is the cubic root of density growth (equivalently, SSTable size grows with the square root of the growth of the shard count). |
| `flush_size_override` | 0 | Override for expected flush size. When 0, derived automatically from observed flush operations (rounded to whole MB). |
| `max_sstables_to_compact` | 0 | Maximum SSTables per compaction. Value of 0 defaults to Integer.MAX_VALUE (effectively unlimited). |
| `expired_sstable_check_frequency_seconds` | 600 | How often to check for fully expired SSTables that can be dropped. |
| `unsafe_aggressive_sstable_expiration` | false | Drop SSTables without tombstone checking. Same semantics as TWCS. |
| `overlap_inclusion_method` | TRANSITIVE | How to identify overlapping SSTables. TRANSITIVE uses transitive closure; alternatives available for specific use cases. |

#### Common Compaction Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `enabled` | true | Enables background compaction. |
| `tombstone_threshold` | 0.2 | Ratio of droppable tombstones that triggers single-SSTable compaction. |
| `tombstone_compaction_interval` | 86400 | Minimum seconds between tombstone compaction attempts. |
| `unchecked_tombstone_compaction` | false | Bypasses tombstone compaction eligibility pre-checking. |
| `only_purge_repaired_tombstones` | false | Only purge tombstones from repaired SSTables. |
| `log_all` | false | Enables detailed compaction logging. |

#### Validation Rules

The following constraints are enforced during configuration:

| Parameter | Constraint |
|-----------|------------|
| `target_sstable_size` | Minimum 1 MiB |
| `min_sstable_size` | Must be >= 0; if nonzero, must be < `target_sstable_size × √0.5` (approximately 70% of target) |
| `base_shard_count` | Must be positive integer |
| `sstable_growth` | Must be between 0.0 and 1.0 (inclusive) |
| `flush_size_override` | If specified, minimum 1 MiB |
| `expired_sstable_check_frequency_seconds` | Must be positive |
| `scaling_parameters` | Must match format: N, L[2+], T[2+], or signed integer |

---

## Scaling Parameters

The `scaling_parameters` option controls compaction behavior through an internal scaling factor `W`.

### Format

```
T<number>  = Tiered (STCS-like behavior), number is fanout (must be ≥ 2)
L<number>  = Leveled (LCS-like behavior), number is fanout (must be ≥ 2)
N          = Balanced (midpoint between tiered and leveled, equivalent to T2/L2)
<integer>  = Raw W value (signed integer, positive = tiered, negative = leveled)
```

### Internal Calculation

The scaling parameter is converted to an internal value $W$:

$$W = \begin{cases} n - 2 & \text{for } T_n \text{ (e.g., } T_4 \rightarrow W = 2\text{)} \\ 2 - n & \text{for } L_n \text{ (e.g., } L_{10} \rightarrow W = -8\text{)} \\ 0 & \text{for } N \text{ (balanced)} \end{cases}$$

From $W$, the fanout ($f$) and threshold ($t$) are calculated:

$$f = \begin{cases} 2 - W & \text{if } W < 0 \\ 2 + W & \text{otherwise} \end{cases}$$

$$t = \begin{cases} 2 & \text{if } W \leq 0 \\ 2 + W & \text{otherwise} \end{cases}$$

### Examples

| Parameter | $W$ | $f$ | $t$ | Behavior |
|-----------|-----|-----|-----|----------|
| `T4` | 2 | 4 | 4 | Tiered: 4 SSTables trigger compaction, $4\times$ size growth |
| `T8` | 6 | 8 | 8 | Very tiered: higher threshold, more write-optimized |
| `N` | 0 | 2 | 2 | Balanced: minimal fanout and threshold |
| `L4` | -2 | 4 | 2 | Leveled: low threshold, more read-optimized |
| `L10` | -8 | 10 | 2 | Very leveled: $10\times$ fanout, aggressive compaction |

### Per-Level Configuration

Multiple values can be specified for different levels:

```sql
'scaling_parameters': 'T4, T4, L10'
-- Level 0: T4 behavior
-- Level 1: T4 behavior
-- Level 2+: L10 behavior (last value repeats)
```

This enables hybrid strategies where upper levels are tiered (write-optimized) and lower levels are leveled (read-optimized).



---

## Migration from Other Strategies

### From STCS

```sql
-- STCS with min_threshold=4 equivalent
ALTER TABLE keyspace.table WITH compaction = {
    'class': 'UnifiedCompactionStrategy',
    'scaling_parameters': 'T4'
};
```

### From LCS

```sql
-- LCS equivalent
ALTER TABLE keyspace.table WITH compaction = {
    'class': 'UnifiedCompactionStrategy',
    'scaling_parameters': 'L10',
    'target_sstable_size': '160MiB'
};
```

### Migration Process

1. UCS takes effect immediately on ALTER
2. Existing SSTables are not rewritten
3. New compactions follow UCS rules
4. Gradual transition as old SSTables compact

```bash
# Monitor migration
watch 'nodetool compactionstats && nodetool tablestats keyspace.table'
```

---

## Tuning UCS

### Write-Heavy Workload

```sql
ALTER TABLE keyspace.table WITH compaction = {
    'class': 'UnifiedCompactionStrategy',
    'scaling_parameters': 'T8',          -- Higher threshold, less frequent compaction
    'target_sstable_size': '2GiB',       -- Larger SSTables
    'base_shard_count': 4
};
```

### Read-Heavy Workload

```sql
ALTER TABLE keyspace.table WITH compaction = {
    'class': 'UnifiedCompactionStrategy',
    'scaling_parameters': 'L10',         -- Leveled for low read amp
    'target_sstable_size': '256MiB',     -- Smaller SSTables for faster compaction
    'base_shard_count': 8                -- More parallelism
};
```

### Large Dataset

```sql
ALTER TABLE keyspace.table WITH compaction = {
    'class': 'UnifiedCompactionStrategy',
    'scaling_parameters': 'T4',
    'target_sstable_size': '5GiB',       -- Larger to reduce SSTable count
    'base_shard_count': 16               -- More shards for parallelism
};
```

### High-Core Server

```sql
ALTER TABLE keyspace.table WITH compaction = {
    'class': 'UnifiedCompactionStrategy',
    'scaling_parameters': 'T4',
    'base_shard_count': 16,              -- Match available cores
    'target_sstable_size': '1GiB'
};
```

---

## Monitoring UCS

### Key Metrics

| Metric | Healthy | Investigate |
|--------|---------|-------------|
| Pending compactions | <20 | >50 |
| SSTable count per shard | Consistent | Highly variable |
| Compaction throughput | Steady | Dropping |

### Commands

```bash
# Compaction activity
nodetool compactionstats

# Table statistics
nodetool tablestats keyspace.table

# JMX metrics for detailed shard info
# org.apache.cassandra.metrics:type=Table,name=*
```

### JMX Metrics

```
# Pending compactions
org.apache.cassandra.metrics:type=Compaction,name=PendingTasks

# Per-table compaction metrics
org.apache.cassandra.metrics:type=Table,keyspace=*,scope=*,name=PendingCompactions
org.apache.cassandra.metrics:type=Table,keyspace=*,scope=*,name=LiveSSTableCount
```

---

## Comparison with Traditional Strategies

| Aspect | STCS | LCS | TWCS | UCS |
|--------|------|-----|------|-----|
| Write amplification | Low | High | Low | Configurable |
| Read amplification | High | Low | Low | Configurable |
| Space amplification | Medium | Low | Low | Low |
| Parallelism | Limited | Limited | Limited | Improved (shard-enabled) |
| Adaptability | Fixed | Fixed | Fixed | Configurable |
| Cassandra version | All | All | 3.0+ | 5.0+ |

### UCS Advantages

1. **Single strategy for multiple workloads**: Adjust `scaling_parameters` instead of switching strategies
2. **Better parallelism**: Sharding enables multi-core utilization
3. **Density-based triggering**: More intelligent than fixed thresholds
4. **Unified codebase**: Simplified maintenance through a single configurable implementation

### UCS Considerations

1. **Newer strategy**: Less production experience than STCS/LCS
2. **Migration complexity**: Existing clusters need careful transition
3. **Learning curve**: Different configuration model

---

## Overlap Inclusion Methods

The `overlap_inclusion_method` parameter controls how UCS extends the set of SSTables selected for compaction:

### TRANSITIVE (Recommended)

When an SSTable is selected for compaction, all transitively overlapping SSTables are included:

```
If A overlaps B and B overlaps C:
  → A, B, and C are all included in the same compaction
  (even if A and C don't directly overlap)

Algorithm: O(n log n) time complexity
Forms minimal disjoint lists where overlapping SSTables belong together
```

This is the default and recommended setting. It ensures compaction fully resolves overlaps, reducing future read amplification.

### SINGLE (Experimental)

!!! warning "Experimental"
    SINGLE is implemented for experimentation purposes only and is not recommended for production use with UCS sharding.

Extension occurs only once from the initially selected SSTables:

```
If A is selected and overlaps B and C:
  → A, B, and C are included
But if B also overlaps D:
  → D is NOT included (no transitive extension)
```

Use this when compaction scope needs to be limited, at the cost of potentially leaving some overlaps unresolved.

### NONE (Experimental)

!!! warning "Experimental"
    NONE is implemented for experimentation purposes only and is not recommended for production use with UCS sharding.

No overlap extension occurs. Only directly selected SSTables are compacted:

```
Only the initially selected bucket is compacted
Overlapping SSTables in other buckets are not included
```

**Not recommended** for most use cases as it may leave significant overlaps, degrading read performance.

---

## Implementation Internals

This section documents implementation details from the Cassandra source code.

### Level Structure

UCS supports up to 32 levels (`MAX_LEVELS = 32`), sufficient for petabytes of data. This accommodates 2^32 SSTables at minimum 1MB each.

### Shard Management

`ShardManager` provides shard boundaries and density-aware comparisons used by UCS. The effective number of output shards is derived from density through the controller (and may be below, equal to, or above `base_shard_count`), and output is split using `ShardTracker`.

### Compaction Candidate Selection

The selection algorithm prioritizes efficiency and coverage:

```
Selection process:
1. Filter unsuitable SSTables (suspect, early-open)
2. Exclude currently compacting SSTables
3. Organize remaining SSTables by density into levels (up to 32)
4. Form buckets by overlap relationships within each level
5. Find buckets with highest overlap count
6. Among equal candidates:
   - Prioritize LOWEST levels (cover larger token fraction for same work)
   - Random uniform selection within same level (reservoir sampling)
7. Extend selection using overlap_inclusion_method
```

**Level prioritization rationale**: Lower levels cover a larger fraction of the token space for the same amount of compaction work, making them more efficient targets.

### Major Compaction Behavior

When maximal compaction is requested, UCS groups SSTables into non-overlapping sets and creates one compaction task per set. The output of those tasks is then split across shard boundaries according to density. This can provide parallelism, but the number of tasks should not be assumed to equal `base_shard_count`.

### Output Sharding

Compaction output is split at power-of-two shard boundaries, with shard count derived from density through the controller.

### Overlap Set Formation

The overlap detection algorithm forms a minimal list of overlap sets satisfying three properties:

1. **Non-overlapping SSTables never share a set**
2. **Overlapping SSTables exist together in at least one set**
3. **SSTables occupy consecutive positions within sets**

```
Algorithm:
1. Sort SSTables by first token
2. Iterate through sorted list
3. Extend current set while SSTables overlap
4. Close set and start new when gap found
5. Result: minimal lists where all overlapping SSTables are grouped

Time complexity: O(n log n)
```

**Example:** If SSTables A, B, C, D cover tokens 0-3, 2-7, 6-9, 1-8 respectively:
- Overlap sets computed: {A, B, D} and {B, C, D}
- A and C don't overlap, so they're in separate sets
- A, B, D overlap at token 2 → must be in at least one set together
- B, C, D overlap at token 7 → must be in at least one set together

The overlap sets determine read amplification: any key lookup touches at most one SSTable per non-overlapping set.

### Constants Reference

| Constant | Value | Description |
|----------|-------|-------------|
| `MAX_LEVELS` | 32 | Maximum hierarchy depth |
| Default scaling_parameters | T4 | Tiered with fanout/threshold of 4 |
| Default target_sstable_size | 1 GiB | Target output SSTable size |
| Default base_shard_count | 4 | Initial token range divisions |
| Default sstable_growth | 0.333 | SSTable size growth = cubic root of density growth |
| Default expired check | 600 seconds | TTL expiration check frequency |
| Output size range | target/√2 to target×√2 | Actual output SSTable size bounds |

---

## Related Documentation

- **[Compaction Overview](index.md)** - Concepts and strategy selection
- **[Size-Tiered Compaction (STCS)](stcs.md)** - Traditional write-heavy strategy
- **[Leveled Compaction (LCS)](lcs.md)** - Traditional read-heavy strategy
- **[Time-Window Compaction (TWCS)](twcs.md)** - Optimized for time-series with TTL
- **[Compaction Management](../../../operations/compaction-management/index.md)** - Tuning and troubleshooting