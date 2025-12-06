# Time-Window Compaction Strategy (TWCS)

TWCS is designed for time-series data. It groups SSTables by time window and never compacts across window boundaries, enabling efficient space reclamation when data expires via TTL.

## How TWCS Works

```
┌─────────────────────────────────────────────────────────────────────┐
│ TIME-WINDOW COMPACTION                                               │
│                                                                      │
│ Key insight: Time-series data is usually:                           │
│ - Written once (append-only)                                        │
│ - Read by time range                                                │
│ - Deleted/expired after TTL                                         │
│                                                                      │
│ Window 1: 00:00-01:00       Window 2: 01:00-02:00                   │
│ ┌─────────────────────┐    ┌─────────────────────┐                  │
│ │ ┌───┐ ┌───┐ ┌───┐  │    │ ┌───┐ ┌───┐        │                  │
│ │ │SS1│ │SS2│ │SS3│  │    │ │SS4│ │SS5│        │                  │
│ │ └───┘ └───┘ └───┘  │    │ └───┘ └───┘        │                  │
│ │      Use STCS      │    │      Use STCS      │                  │
│ │      within        │    │      within        │                  │
│ │      window        │    │      window        │                  │
│ │         │          │    │                    │                  │
│ │         ▼          │    │                    │                  │
│ │    ┌─────────┐     │    │                    │                  │
│ │    │Combined │     │    │                    │                  │
│ │    │ SSTable │     │    │                    │                  │
│ │    └─────────┘     │    │                    │                  │
│ └─────────────────────┘    └─────────────────────┘                  │
│                                                                      │
│ CRITICAL: SSTables NEVER compact across window boundaries           │
│                                                                      │
│ When Window 1 data expires (TTL), entire SSTable is dropped         │
│ No compaction needed to reclaim space                               │
└─────────────────────────────────────────────────────────────────────┘
```

```mermaid
flowchart LR
    subgraph W1["Window 1: 00:00-01:00"]
        direction TB
        S1["SST1"] & S2["SST2"] & S3["SST3"]
        S1 & S2 & S3 -->|"STCS within window"| C1["Combined SSTable"]
    end

    subgraph W2["Window 2: 01:00-02:00"]
        direction TB
        S4["SST4"] & S5["SST5"]
    end

    W1 -.->|"Never compact across"| W2
    W1 -->|"TTL expires"| DROP["Drop entire SSTable"]
```

### Window Assignment

Each SSTable is assigned to a time window based on its maximum timestamp:

```
SSTable with data timestamps:
- Min timestamp: 2024-01-15 10:30:00
- Max timestamp: 2024-01-15 10:45:00

With 1-hour windows:
- Window: 2024-01-15 10:00:00 - 11:00:00
- SSTable assigned to this window
```

---

## Configuration

```sql
CREATE TABLE sensor_readings (
    sensor_id text,
    reading_time timestamp,
    value double,
    PRIMARY KEY ((sensor_id), reading_time)
) WITH CLUSTERING ORDER BY (reading_time DESC)
AND compaction = {
    'class': 'TimeWindowCompactionStrategy',

    -- Time window size
    'compaction_window_unit': 'HOURS',  -- MINUTES, HOURS, DAYS
    'compaction_window_size': 1,        -- 1 hour windows

    -- Expired SSTable handling
    'unsafe_aggressive_sstable_expiration': false
}
AND default_time_to_live = 86400  -- 24 hour TTL
AND gc_grace_seconds = 3600;      -- 1 hour (shorter for time-series)
```

### Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `compaction_window_unit` | DAYS | Time unit: MINUTES, HOURS, DAYS |
| `compaction_window_size` | 1 | Number of units per window |
| `unsafe_aggressive_sstable_expiration` | false | Drop SSTables without checking tombstones |

### Window Size Guidelines

| TTL | Recommended Window | Result |
|-----|-------------------|--------|
| 1 hour | 5-10 minutes | ~6-12 windows |
| 24 hours | 1 hour | 24 windows |
| 7 days | 1 day | 7 windows |
| 30 days | 1 day | 30 windows |
| 90 days | 1 week | ~13 windows |

**Rule of thumb:** Choose window size so that 10-30 windows exist before data expires.

---

## TTL Integration

The primary benefit of TWCS is efficient TTL expiration:

```
Why TWCS + TTL is efficient:

Day 1:
┌────────────┐ ┌────────────┐ ┌────────────┐
│ Window 1   │ │ Window 2   │ │ Window 3   │
│ TTL: 7 days│ │ TTL: 7 days│ │ TTL: 7 days│
└────────────┘ └────────────┘ └────────────┘

Day 8 (Window 1 TTL expires):
┌────────────┐ ┌────────────┐ ┌────────────┐
│ Window 1   │ │ Window 2   │ │ Window 3   │
│ [EXPIRED]  │ │ TTL: 2 more│ │ TTL: 3 more│
└────────────┘ days          │ days
     │
     └── Entire SSTable dropped without compaction

Space reclamation: O(1) vs O(n) with STCS/LCS
```

### gc_grace_seconds Consideration

For time-series with TWCS, `gc_grace_seconds` can often be reduced:

```sql
-- Traditional table: 10 days (default)
gc_grace_seconds = 864000

-- Time-series with frequent repair: 1 hour
gc_grace_seconds = 3600

-- Time-series with very frequent repair: 10 minutes
gc_grace_seconds = 600
```

**Warning:** Reducing `gc_grace_seconds` requires running repair at least that frequently to prevent zombie data resurrection.

---

## When to Use TWCS

### Recommended For

| Use Case | Rationale |
|----------|-----------|
| Time-series data (IoT, metrics, logs) | Natural time-based partitioning |
| Data with TTL | Efficient expiration |
| Append-only workloads | No cross-window updates |
| Time-range queries | Data locality by time |
| Immutable historical data | No modifications after write |

### Avoid When

| Use Case | Rationale |
|----------|-----------|
| Frequently updated data | Updates span windows |
| No TTL | Windows accumulate forever |
| Non-time-ordered data | Window assignment ineffective |
| Explicit deletes common | Tombstones span windows |
| Out-of-order writes | Old windows never fully compact |

---

## Production Issues

### Issue 1: Out-of-Order Writes

**Symptoms:**

- Old windows have multiple SSTables that never compact
- Space not reclaimed when TTL expires
- SSTable count growing unexpectedly

**Diagnosis:**

```bash
# List SSTables with timestamps
for f in /var/lib/cassandra/data/keyspace/table-*/*-Data.db; do
    echo "=== $f ==="
    tools/bin/sstablemetadata "$f" | grep -E "Minimum|Maximum"
done
```

**Cause:**

```
Current window: Hour 10
Write arrives for Hour 5 (5 hours late)

Result:
- Hour 5 window gets new SSTable
- That window cannot fully compact
- When TTL expires, old data persists
```

**Solutions:**

1. Ensure data arrives in order (fix data pipeline)
2. Use larger windows to accommodate expected delays:
   ```sql
   -- If data can arrive up to 2 hours late, use 4-hour windows
   'compaction_window_size': 4
   ```
3. Accept some space inefficiency for late-arriving data

### Issue 2: Updates to Old Data

**Symptoms:**

- Reads merging data across many windows
- Higher read latency than expected
- Multiple versions of same partition key

**Cause:**

TWCS assumes append-only. Updates violate this assumption:

```
Window 1 (old): [sensor1→reading_v1]
Window 5 (new): [sensor1→reading_v2]  ← Update to same key

Problem:
- v1 and v2 are in DIFFERENT windows
- TWCS never compacts across windows
- Both versions persist until TTL expires
- Reads must merge across windows
```

**Solution:**

TWCS is only appropriate for append-only time-series. If updates are required, consider:

1. LCS for frequently updated data
2. Redesign data model to avoid updates

### Issue 3: Tombstone Spread

**Symptoms:**

- Space not reclaimed after deletes
- Tombstones persisting beyond `gc_grace_seconds`

**Cause:**

```
DELETE FROM sensors WHERE sensor_id = 'x' AND reading_time < '2024-01-01';

Result: Range tombstone written to CURRENT window
Problem: Original data is in OLD windows
         Tombstone and data never meet in compaction
         Space not reclaimed efficiently
```

**Solution:**

Avoid explicit deletes with TWCS. Use TTL instead:

```sql
-- Instead of DELETE, let TTL handle expiration
INSERT INTO sensors (sensor_id, reading_time, value)
VALUES ('x', '2024-01-15 10:30:00', 42.5)
USING TTL 604800;  -- 7 days
```

### Issue 4: Window Not Compacting

**Symptoms:**

- Multiple SSTables in completed (old) windows
- Expected single SSTable per window not achieved

**Diagnosis:**

```bash
# Check SSTables per window
nodetool tablestats keyspace.table
```

**Causes:**

1. Insufficient similar-sized SSTables (STCS within window)
2. Out-of-order writes
3. Compaction not keeping pace

**Solutions:**

```sql
-- Lower threshold for intra-window compaction
ALTER TABLE keyspace.table WITH compaction = {
    'class': 'TimeWindowCompactionStrategy',
    'compaction_window_unit': 'HOURS',
    'compaction_window_size': 1,
    'min_threshold': 2  -- Compact with fewer SSTables
};
```

---

## Advanced Configuration

### Aggressive SSTable Expiration

When data has uniform TTL and no deletes, aggressive expiration can drop SSTables without full compaction:

```sql
ALTER TABLE keyspace.table WITH compaction = {
    'class': 'TimeWindowCompactionStrategy',
    'compaction_window_unit': 'HOURS',
    'compaction_window_size': 1,
    'unsafe_aggressive_sstable_expiration': true
};
```

**Warning:** "unsafe" means:

- Does not check for tombstones affecting other SSTables
- Only safe when:
  - All data has the same TTL
  - No explicit deletes
  - No range tombstones

### Window Size Selection

```
Factors to consider:

1. Query patterns:
   - If queries typically span 1 hour → windows ≤ 1 hour
   - If queries span 1 day → windows ≤ 1 day

2. Write rate:
   - High write rate → smaller windows (more SSTables, but manageable size)
   - Low write rate → larger windows (fewer SSTables)

3. TTL duration:
   - Short TTL (hours) → minute/hour windows
   - Long TTL (weeks) → day windows

4. Late-arriving data:
   - Data arrives up to X late → window > X
```

---

## Monitoring TWCS

### Key Indicators

| Metric | Healthy | Investigate |
|--------|---------|-------------|
| SSTables per window | 1-2 (completed) | >4 |
| Total SSTable count | ~windows × 2 | Much higher |
| Pending compactions | Low | Sustained growth |
| Space after TTL expiry | Decreasing | Not changing |

### Commands

```bash
# Check SSTable timestamps
for f in /var/lib/cassandra/data/keyspace/table-*/*-Data.db; do
    tools/bin/sstablemetadata "$f" | grep -E "Minimum|Maximum timestamp"
done

# Monitor space usage over time
watch 'nodetool tablestats keyspace.table | grep "Space used"'
```

---

## Related Documentation

- **[Compaction Overview](index.md)** - Concepts and strategy selection
- **[Tombstones](../tombstones.md)** - gc_grace_seconds and tombstone handling
- **[Compaction Operations](operations.md)** - Tuning and troubleshooting
