# nodetool garbagecollect

Removes deleted data (tombstones) from SSTables without full compaction.

---

## Synopsis

```bash
nodetool [connection_options] garbagecollect [options] [--] [keyspace [table ...]]
```

## Description

`nodetool garbagecollect` performs a targeted cleanup of tombstones and expired data without triggering a full compaction. This is lighter weight than `compact` and specifically targets garbage collection of deleted data.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | Keyspace to garbage collect. If omitted, processes all keyspaces |
| `table` | Specific table(s) to garbage collect |

---

## Options

| Option | Description |
|--------|-------------|
| `-g, --granularity` | ROW or CELL level granularity |
| `-j, --jobs <jobs>` | Number of concurrent jobs (default: 2) |

---

## Granularity Levels

### ROW Granularity (Default)

```bash
nodetool garbagecollect -g ROW my_keyspace my_table
```

- Removes entire rows that are fully deleted
- More efficient for row-level deletes
- Less I/O intensive

### CELL Granularity

```bash
nodetool garbagecollect -g CELL my_keyspace my_table
```

- Removes individual deleted cells within rows
- More thorough cleanup
- Higher I/O cost

---

## When to Use

### After Bulk Deletes

```bash
# After deleting many rows
DELETE FROM my_keyspace.my_table WHERE partition_key IN (...);

# Clean up tombstones
nodetool garbagecollect my_keyspace my_table
```

### TTL-Heavy Tables

For tables with many expiring rows:

```bash
nodetool garbagecollect my_keyspace ttl_table
```

### Instead of Full Compaction

```bash
# Lighter alternative to:
# nodetool compact my_keyspace my_table

# Use garbage collect for tombstone cleanup only:
nodetool garbagecollect my_keyspace my_table
```

---

## Examples

### Garbage Collect Specific Table

```bash
nodetool garbagecollect my_keyspace my_table
```

### Garbage Collect All Tables in Keyspace

```bash
nodetool garbagecollect my_keyspace
```

### Cell-Level Garbage Collection

```bash
nodetool garbagecollect -g CELL my_keyspace my_table
```

### Parallel Garbage Collection

```bash
nodetool garbagecollect -j 4 my_keyspace
```

---

## Tombstone Eligibility

Tombstones are only removed when:

1. **Age > gc_grace_seconds** - Default 10 days
2. **All replicas have seen the tombstone** - Via repair or normal writes

```sql
-- Check table's gc_grace_seconds
SELECT gc_grace_seconds FROM system_schema.tables
WHERE keyspace_name = 'my_keyspace' AND table_name = 'my_table';
```

!!! warning "gc_grace_seconds"
    Tombstones younger than gc_grace_seconds cannot be removed. Running garbage collect on fresh deletes has no effect.

---

## Comparison with Compact

| Aspect | garbagecollect | compact |
|--------|----------------|---------|
| Purpose | Remove tombstones | Merge all SSTables |
| Scope | Targeted cleanup | Full rewrite |
| I/O Impact | Lower | Higher |
| Duration | Shorter | Longer |
| Space needed | Less | More |

Use `garbagecollect` when you only need tombstone cleanup.
Use `compact` when you need full SSTable consolidation.

---

## Monitoring

### Check Progress

```bash
nodetool compactionstats
```

Garbage collection appears as a compaction operation.

### Check Tombstone Counts Before/After

```bash
# Before
nodetool tablestats my_keyspace.my_table | grep "tombstones"

# Run garbage collect
nodetool garbagecollect my_keyspace my_table

# After
nodetool tablestats my_keyspace.my_table | grep "tombstones"
```

---

## Common Scenarios

### High Tombstone Warnings

If logs show tombstone warnings:

```
WARN  Read 5000 live rows and 100000 tombstone cells
```

```bash
# Clean up tombstones (after gc_grace_seconds has passed)
nodetool garbagecollect my_keyspace problematic_table
```

### Prepare for Major Compaction

```bash
# Clean tombstones first (faster)
nodetool garbagecollect my_keyspace

# Then compact if needed
nodetool compact my_keyspace
```

### After Range Deletes

Range deletes create many tombstones:

```bash
# Wait for gc_grace_seconds
# Then clean up
nodetool garbagecollect my_keyspace my_table
```

---

## Best Practices

!!! tip "Garbage Collection Guidelines"
    1. **Wait for gc_grace_seconds** - Tombstones must be old enough
    2. **Run repair first** - Ensure tombstones propagated to all replicas
    3. **Monitor disk space** - Some temporary space needed
    4. **Start with ROW granularity** - Less I/O, often sufficient
    5. **Use CELL for column deletes** - When updating individual columns

---

## Scripting Example

```bash
#!/bin/bash
# garbage_collect_old_tables.sh
# Clean tombstones from tables with high tombstone counts

THRESHOLD=10000

for ks_table in $(nodetool tablestats 2>/dev/null | grep -B5 "Tombstones" | \
    grep "Table:" | awk '{print $2}'); do

    tombstones=$(nodetool tablestats $ks_table | grep "tombstones" | \
        awk '{sum += $NF} END {print sum}')

    if [ "$tombstones" -gt "$THRESHOLD" ]; then
        echo "Garbage collecting $ks_table (tombstones: $tombstones)"
        nodetool garbagecollect $ks_table
    fi
done
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [compact](compact.md) | Full compaction (heavier) |
| [tablestats](tablestats.md) | Check tombstone counts |
| [scrub](scrub.md) | Rebuild SSTables |
| [cleanup](cleanup.md) | Remove non-local data |
