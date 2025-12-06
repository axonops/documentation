# Unified Compaction Strategy (UCS)

UCS (Cassandra 5.0+) is an adaptive compaction strategy that combines concepts from STCS, LCS, and TWCS. It uses sharding and density-based triggering to provide flexible, efficient compaction across varying workloads.

## How UCS Works

```
┌─────────────────────────────────────────────────────────────────────┐
│ UNIFIED COMPACTION STRATEGY                                          │
│                                                                      │
│ Key innovations:                                                     │
│                                                                      │
│ 1. SHARDING: Divides token range into independent shards            │
│    ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                                 │
│    │Shard│ │Shard│ │Shard│ │Shard│  Parallel compaction per shard  │
│    │ 1   │ │ 2   │ │ 3   │ │ 4   │                                 │
│    └─────┘ └─────┘ └─────┘ └─────┘                                 │
│                                                                      │
│ 2. ADAPTIVE STRATEGY: Configurable behavior per table               │
│    - T (Tiered): Like STCS, for write-heavy workloads              │
│    - L (Leveled): Like LCS, for read-heavy workloads               │
│    - N (None): No compaction                                        │
│                                                                      │
│ 3. DENSITY-BASED TRIGGERING:                                        │
│    - Compaction triggered by data density, not file count          │
│    - More intelligent resource allocation                           │
└─────────────────────────────────────────────────────────────────────┘
```

### Sharding

UCS divides the token range into shards, enabling:

- **Parallel compaction**: Different shards compact independently
- **Reduced compaction scope**: Smaller units of work
- **Better resource utilization**: Multiple CPU cores used effectively

```
Token range: -2^63 to 2^63
With 4 base shards:

Shard 1: tokens -2^63 to -2^61
Shard 2: tokens -2^61 to 0
Shard 3: tokens 0 to 2^61
Shard 4: tokens 2^61 to 2^63

Each shard compacts independently with its own SSTable hierarchy
```

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
    -- N = None (no compaction)
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

| Parameter | Default | Description |
|-----------|---------|-------------|
| `scaling_parameters` | T4 | Strategy behavior: T (tiered), L (leveled), N (none) with fanout |
| `target_sstable_size` | 1GiB | Target size for output SSTables |
| `base_shard_count` | 4 | Number of token range shards |
| `min_sstable_size` | 100MiB | Minimum size before sharding applies |
| `max_sstables_to_compact` | 32 | Maximum SSTables per compaction |
| `expired_sstable_check_frequency_seconds` | 600 | TTL expiration check interval |

---

## Scaling Parameters

The `scaling_parameters` option controls compaction behavior:

### Format

```
[T|L|N][number]

T = Tiered (STCS-like behavior)
L = Leveled (LCS-like behavior)
N = None (disable compaction)

number = fanout/threshold
```

### Examples

| Parameter | Behavior | Use Case |
|-----------|----------|----------|
| `T4` | Tiered with 4 SSTables per tier | Write-heavy (like STCS min_threshold=4) |
| `T8` | Tiered with 8 SSTables per tier | Very write-heavy |
| `L4` | Leveled with 4x size between levels | Read-heavy, lower write amp than L10 |
| `L10` | Leveled with 10x size between levels | Read-heavy (like classic LCS) |
| `N` | No compaction | Special cases only |

### Tiered Mode (T)

```
T4 behavior:

Within each shard:
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│ SS1 │ │ SS2 │ │ SS3 │ │ SS4 │  4 similar-sized SSTables
└─────┘ └─────┘ └─────┘ └─────┘
              │
              ▼ Compact when 4 accumulate
         ┌─────────┐
         │ Merged  │
         └─────────┘

Lower write amplification, higher read amplification
Best for: Write-heavy workloads
```

### Leveled Mode (L)

```
L10 behavior:

Within each shard, levels with 10x size increase:
L0: [flush] [flush] [flush] [flush]
          │
          ▼
L1: [──────────────────────────]
          │
          ▼
L2: [────────────────────────────────────────────]

Lower read amplification, higher write amplification
Best for: Read-heavy workloads
```

---

## When to Use UCS

### Recommended For

| Use Case | Configuration | Rationale |
|----------|---------------|-----------|
| New Cassandra 5.0+ deployments | `T4` or `L10` | Modern, well-tested default |
| Mixed read/write workloads | `T4` | Balanced trade-offs |
| High-core-count servers | `base_shard_count: 8` | Parallel compaction |
| Workloads that change over time | Start with `T4` | Easy to adjust |

### Consider Alternatives When

| Situation | Alternative |
|-----------|-------------|
| Pure time-series with TTL | TWCS may still be more efficient |
| Migrating existing production | Test thoroughly before switching |
| Very specific, well-understood workload | Existing tuned strategy may be better |

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
| Parallelism | Limited | Limited | Limited | High (sharding) |
| Adaptability | Fixed | Fixed | Fixed | Configurable |
| Cassandra version | All | All | 3.0+ | 5.0+ |

### UCS Advantages

1. **Single strategy for multiple workloads**: Adjust `scaling_parameters` instead of switching strategies
2. **Better parallelism**: Sharding enables multi-core utilization
3. **Density-based triggering**: More intelligent than fixed thresholds
4. **Unified codebase**: Simplified maintenance and fewer edge cases

### UCS Considerations

1. **Newer strategy**: Less production experience than STCS/LCS
2. **Migration complexity**: Existing clusters need careful transition
3. **Learning curve**: Different configuration model

---

## Related Documentation

- **[Compaction Overview](index.md)** - Concepts and strategy selection
- **[Size-Tiered Compaction (STCS)](stcs.md)** - Traditional write-heavy strategy
- **[Leveled Compaction (LCS)](lcs.md)** - Traditional read-heavy strategy
- **[Compaction Operations](operations.md)** - Tuning and troubleshooting
