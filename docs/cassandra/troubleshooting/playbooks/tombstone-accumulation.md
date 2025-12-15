---
title: "Cassandra Tombstone Accumulation"
description: "Tombstone accumulation troubleshooting playbook. Handle tombstone warnings."
meta:
  - name: keywords
    content: "tombstone troubleshooting, tombstone accumulation, delete markers"
---

# Tombstone Accumulation

Tombstones are markers for deleted data in Cassandra. Excessive tombstones degrade read performance and can cause `TombstoneOverwhelmingException`.

---

## Symptoms

- `TombstoneOverwhelmingException` in logs or client errors
- Slow read performance on specific tables
- High "Tombstones scanned" in `nodetool tablestats`
- Read timeouts on range queries
- Increasing read latency over time

---

## Diagnosis

### Step 1: Check Tombstone Counts

```bash
nodetool tablestats my_keyspace.my_table | grep -i tombstone
```

**Key metrics:**
- `Average tombstones per slice (last five minutes)`: Should be < 100
- `Maximum tombstones per slice (last five minutes)`: Alerts if > 1000

### Step 2: Identify Problematic Tables

```bash
# Check all tables
for ks in $(nodetool tablestats 2>/dev/null | grep "Keyspace:" | awk '{print $2}'); do
    echo "=== $ks ==="
    nodetool tablestats $ks 2>/dev/null | grep -E "Table:|tombstones per slice" | head -20
done
```

### Step 3: Check Tombstone Warning Threshold

```bash
grep tombstone_warn_threshold /etc/cassandra/cassandra.yaml
# Default: 1000
```

### Step 4: Analyze Access Patterns

```bash
# Check recent warnings
grep -i "tombstone" /var/log/cassandra/system.log | tail -50

# Look for specific queries hitting tombstones
grep "Scanned over" /var/log/cassandra/system.log | tail -20
```

### Step 5: Check gc_grace_seconds

```bash
cqlsh -e "SELECT table_name, gc_grace_seconds FROM system_schema.tables WHERE keyspace_name = 'my_keyspace';"
```

---

## Resolution

### Immediate: Run Compaction

Force compaction to purge eligible tombstones:

```bash
# Compact specific table
nodetool compact my_keyspace my_table

# Or use garbagecollect for tombstone-only cleanup
nodetool garbagecollect my_keyspace my_table
```

!!! info "Tombstone Eligibility"
    Tombstones are only purged after `gc_grace_seconds` (default 10 days) has passed AND the data has been repaired.

### Short-term: Adjust Thresholds

Increase tombstone thresholds to prevent query failures (temporary fix):

```bash
# In cassandra.yaml
tombstone_warn_threshold: 10000
tombstone_failure_threshold: 100000
```

Or per-query in CQL (Cassandra 4.0+):

```sql
SELECT * FROM my_table WHERE ... BYPASS TOMBSTONE THRESHOLD;
```

### Long-term: Fix Data Model

**Problem Pattern 1: Deleting from wide partitions**

```sql
-- Bad: Creates tombstone per deletion
DELETE FROM events WHERE user_id = ? AND event_time < ?;
```

**Solution: Use TTL instead**

```sql
-- Good: Data expires automatically, fewer tombstones
INSERT INTO events (...) VALUES (...) USING TTL 604800;
```

**Problem Pattern 2: Null columns creating tombstones**

```sql
-- Bad: Setting column to null creates tombstone
UPDATE users SET email = null WHERE id = ?;
```

**Solution: Use separate table or don't update to null**

**Problem Pattern 3: Range deletes on time-series**

**Solution: Use Time-Window Compaction Strategy (TWCS)**

```sql
ALTER TABLE events WITH compaction = {
    'class': 'TimeWindowCompactionStrategy',
    'compaction_window_unit': 'DAYS',
    'compaction_window_size': 1
};
```

### Reduce gc_grace_seconds (With Caution)

If repairs run frequently, reduce gc_grace_seconds:

```sql
-- Only if repairs run more frequently than this value
ALTER TABLE my_table WITH gc_grace_seconds = 259200;  -- 3 days
```

!!! warning "Risk"
    Setting `gc_grace_seconds` too low risks resurrecting deleted data if repairs don't complete in time.

---

## Recovery

### Verify Tombstone Reduction

```bash
# After compaction
nodetool tablestats my_keyspace.my_table | grep -i tombstone

# Should see reduced counts
```

### Monitor Going Forward

Set up alerting on:
- `Tombstones per read > 1000`
- `TombstoneOverwhelmingException` count > 0

---

## Prevention

| Strategy | Implementation |
|----------|----------------|
| Use TTLs instead of deletes | `INSERT ... USING TTL 86400` |
| TWCS for time-series data | Change compaction strategy |
| Avoid null updates | Use default values or separate tables |
| Regular compaction | Monitor pending compactions |
| Proper data modeling | Avoid wide partitions with deletions |
| Run repairs | Enables tombstone purging |

---

## Related Commands

| Command | Purpose |
|---------|---------|
| `nodetool tablestats` | Check tombstone metrics |
| `nodetool compact` | Force compaction |
| `nodetool garbagecollect` | Targeted tombstone cleanup |

## Related Documentation

- [Compaction Management](../../operations/compaction-management/index.md) - Compaction strategies
- [Data Modeling](../../data-modeling/index.md) - Best practices
