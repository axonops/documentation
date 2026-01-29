---
title: "nodetool compact"
description: "Force major compaction in Cassandra using nodetool compact. Merge SSTables and reclaim disk space."
meta:
  - name: keywords
    content: "nodetool compact, major compaction, Cassandra compaction, merge SSTables"
---

# nodetool compact

Forces a major compaction on one or more tables, merging all SSTables into a single SSTable.

---

## Synopsis

```bash
nodetool [connection_options] compact [options] [--] [keyspace [table ...]]
```

## Description

`nodetool compact` triggers an immediate compaction operation, consolidating SSTables. By default, it performs a major compaction that merges all SSTables for a table into one.

!!! danger "Major Compaction Warning"
    Major compaction creates a single large SSTable. This can cause:

    - Significant disk space usage (temporarily doubles space needed)
    - High I/O impact on production workloads
    - Long-running operations that cannot be easily stopped
    - Interference with normal compaction strategies

    **Use with extreme caution in production.**

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | Keyspace to compact. If omitted, compacts all keyspaces |
| `table` | Specific table(s) to compact. If omitted, compacts all tables |

---

## Options

| Option | Description |
|--------|-------------|
| `-s, --split-output` | Don't create single SSTable; output multiple based on strategy |
| `--user-defined` | Run user-defined compaction (provide SSTable files) |
| `-st, --start-token` | Start token for compaction range |
| `-et, --end-token` | End token for compaction range |

---

## Examples

### Compact Specific Table

```bash
nodetool compact my_keyspace my_table
```

Major compaction of single table.

### Compact with Split Output

```bash
nodetool compact -s my_keyspace my_table
```

!!! tip "Recommended Over Major Compaction"
    The `-s` flag prevents creating one giant SSTable:

    - Respects compaction strategy's target SSTable sizes
    - Reduces disk space spike
    - Better for subsequent compaction operations

### Compact Token Range

```bash
nodetool compact -st 0 -et 1000000000000 my_keyspace my_table
```

Compacts only SSTables containing data in the specified token range.

### Compact All Tables in Keyspace

```bash
nodetool compact my_keyspace
```

### Compact Everything

```bash
nodetool compact
```

!!! danger "Use With Caution"
    Running `nodetool compact` without arguments compacts every table on the node. This is rarely appropriate in production and should only be performed during planned maintenance windows with careful monitoring.

---

## When to Use

### Legitimate Use Cases

| Scenario | Reason |
|----------|--------|
| After bulk delete | Remove tombstones (with caution) |
| Before decommission | Reduce data to stream |
| Test/dev environments | Simplify SSTable state |
| Preparing for backup | Consolidate for smaller backup |

### After Bulk Deletes

If a large amount of data was deleted and tombstones need cleanup:

```bash
# First, check tombstone warnings in logs
# Then, if gc_grace_seconds has passed:
nodetool compact -s my_keyspace my_table
```

!!! warning "Tombstone Considerations"
    - Tombstones older than `gc_grace_seconds` will be removed
    - Ensure repair completed before bulk delete compaction
    - Consider `garbagecollect` instead for tombstone cleanup

---

## When NOT to Use

!!! danger "Avoid Major Compaction"
    Do not run major compaction:

    - **As routine maintenance** - Let compaction strategies work
    - **On large tables** - Can take hours/days
    - **Under production load** - Severe I/O impact
    - **When disk space is limited** - Requires ~2x table size
    - **On TWCS tables** - Destroys time-window boundaries

### Compaction Strategies Handle This

Modern compaction strategies (LCS, TWCS, UCS) are designed to maintain optimal SSTable layouts. Manual major compaction often works against these strategies.

---

## Impact Analysis

### Disk Space

```
Before: 10 SSTables × 10 GB = 100 GB
During: Original 100 GB + New merged SSTable (growing to ~100 GB) = ~200 GB peak
After: 1 SSTable × ~95 GB (after compression/tombstone removal)
```

!!! danger "Disk Space Requirement"
    Ensure at least **2× the table size** in free disk space before major compaction.

### I/O Impact

| Phase | I/O Pattern |
|-------|-------------|
| Read | Sequential reads of all SSTables |
| Write | Sequential write of new SSTable |
| Duration | Hours for large tables |

### Effect on Queries

- Read latency increases during compaction (more disk I/O)
- Write latency generally unaffected
- Coordinator operations may timeout more frequently

---

## Monitoring Compaction

### Check Progress

```bash
nodetool compactionstats
```

Shows:
- Active compactions
- Progress percentage
- Bytes processed
- Estimated completion time

### Check History

```bash
nodetool compactionhistory
```

Shows completed compaction operations.

### Stop If Necessary

```bash
nodetool stop COMPACTION
```

!!! warning "Stopping Compaction"
    Stopping a compaction leaves partial results. The incomplete SSTable will be cleaned up, but the operation will need to restart from scratch.

---

## Alternatives to Major Compaction

### For Tombstone Cleanup

```bash
nodetool garbagecollect my_keyspace my_table
```

Removes only tombstones without full compaction.

### For Regular Maintenance

Let the compaction strategy handle it. Monitor with:

```bash
nodetool tablestats my_keyspace.my_table | grep -i "compacted\|sstable"
```

### For Specific SSTables

```bash
nodetool compact --user-defined /path/to/sstable-Data.db
```

Compacts specific SSTables rather than all.

---

## Strategy-Specific Behavior

### Size-Tiered (STCS)

Major compaction creates one SSTable, which STCS then treats as a single tier. Subsequent writes create new small SSTables, and the cycle begins again.

### Leveled (LCS)

Major compaction places all data in L0, forcing a cascade of compactions to redistribute to proper levels. This is very disruptive.

### Time-Window (TWCS)

!!! danger "Never Major Compact TWCS Tables"
    Major compaction merges time windows together, destroying the time-based organization that TWCS depends on. This severely impacts:

    - TTL-based expiration
    - Time-range query efficiency
    - Future compaction behavior

### Unified (UCS)

Similar considerations to LCS; major compaction disrupts the density-based organization.

---

## Best Practices

!!! tip "Compaction Guidelines"
    1. **Prefer `-s` flag** - Split output respects strategy
    2. **Limit scope** - Specify keyspace and table
    3. **Check disk space** - Ensure 2× table size available
    4. **Off-peak hours** - Run during low traffic
    5. **Monitor progress** - Use `compactionstats`
    6. **Consider alternatives** - `garbagecollect` for tombstones
    7. **Never on TWCS** - Destroys time windows

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [compactionstats](compactionstats.md) | Monitor compaction progress |
| [tablestats](tablestats.md) | Check SSTable counts |
| [flush](flush.md) | Flush memtables before compaction |