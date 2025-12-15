---
title: "nodetool flush"
description: "Flush memtables to SSTables on disk in Cassandra using nodetool flush command."
meta:
  - name: keywords
    content: "nodetool flush, flush memtables, Cassandra flush, write to disk"
---

# nodetool flush

Flushes memtables from memory to SSTables on disk for one or more tables.

---

## Synopsis

```bash
nodetool [connection_options] flush [--] [keyspace [table ...]]
```

## Description

`nodetool flush` forces an immediate flush of memtable data to disk as SSTables. Memtables hold recent writes in memory; flushing writes this data to immutable SSTable files.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | Keyspace to flush. If omitted, flushes all keyspaces |
| `table` | Specific table(s) to flush. If omitted, flushes all tables in keyspace |

---

## Examples

### Flush All Keyspaces

```bash
nodetool flush
```

Flushes all memtables for all keyspaces on the node.

### Flush Specific Keyspace

```bash
nodetool flush my_keyspace
```

Flushes all tables in `my_keyspace`.

### Flush Specific Table

```bash
nodetool flush my_keyspace my_table
```

Flushes only `my_table` in `my_keyspace`.

### Flush Multiple Tables

```bash
nodetool flush my_keyspace table1 table2 table3
```

Flushes multiple specific tables.

---

## When to Use

### Before Taking Snapshots

!!! tip "Required Before Backups"
    Always flush before creating snapshots to ensure all data is on disk:

    ```bash
    nodetool flush my_keyspace
    nodetool snapshot -t backup_$(date +%Y%m%d) my_keyspace
    ```

    Without flushing, recent writes in memtables will not be included in the snapshot.

### Before Stopping Cassandra

```bash
nodetool flush
nodetool drain
sudo systemctl stop cassandra
```

!!! info "Drain Includes Flush"
    `nodetool drain` automatically flushes all memtables. Explicit flush before drain is optional but makes the drain faster.

### Before Major Compaction

```bash
nodetool flush my_keyspace
nodetool compact my_keyspace
```

Ensures all data is in SSTables before compaction.

### Before Upgrading SSTables

```bash
nodetool flush
nodetool upgradesstables
```

Ensures no data remains in memtables before SSTable upgrade.

---

## When NOT to Use

!!! warning "Unnecessary Flushing"
    Avoid excessive flushing:

    - **Frequent flushes**: Creates many small SSTables, increasing compaction overhead
    - **During normal operations**: Let Cassandra manage memtable flushes automatically
    - **Under heavy write load**: Adds disk I/O pressure

### Cassandra's Automatic Flushing

Cassandra automatically flushes memtables when:

| Condition | Configuration |
|-----------|---------------|
| Memtable size threshold | `memtable_heap_space` |
| Commit log segment full | `commitlog_segment_size` |
| Time-based | `memtable_flush_period_in_ms` (if configured) |
| Memory pressure | When approaching heap limits |

---

## Impact on Operations

### Resource Usage

| Resource | Impact |
|----------|--------|
| Disk I/O | Write burst during flush |
| Memory | Temporary increase while flushing |
| CPU | Compression during SSTable write |

### During Flush

- Write operations continue to new memtable
- Read operations may read from both memtable and SSTables
- Flush is generally quick for reasonably-sized memtables

### SSTable Creation

Each flush creates new SSTable files:

```
/var/lib/cassandra/data/my_keyspace/my_table-<uuid>/
├── nb-1-big-Data.db
├── nb-1-big-Index.db
├── nb-1-big-Filter.db
└── ...
```

!!! info "Compaction Follows"
    New SSTables from flushes eventually get compacted according to the table's compaction strategy.

---

## Monitoring Flush Operations

### Check Pending Flushes

```bash
nodetool tpstats | grep -i flush
```

Shows flush-related thread pool activity.

### Check Memtable Status

```bash
nodetool tablestats my_keyspace.my_table | grep -i memtable
```

Shows current memtable size and flush statistics.

---

## Flush vs. Drain

| Operation | Scope | Additional Actions |
|-----------|-------|-------------------|
| `flush` | Memtables only | None |
| `drain` | Memtables + connections | Disables gossip and native transport, stops accepting writes |

Use `drain` for graceful shutdown; use `flush` for data persistence while keeping node operational.

---

## Common Issues

### Flush Takes Too Long

Large memtables increase flush time:

| Cause | Solution |
|-------|----------|
| Large memtable size | Reduce `memtable_heap_space` |
| Slow disk I/O | Improve storage performance |
| Heavy write load | Consider flush during lower traffic |

### Out of Disk Space During Flush

!!! danger "Disk Space Required"
    Ensure sufficient disk space before flushing:

    - Flush creates new SSTable files
    - Space needed: approximately memtable size × compression ratio
    - Monitor disk usage: `df -h /var/lib/cassandra`

### Many Small SSTables After Flush

Frequent flushes create fragmented SSTables:

```bash
# Check SSTable count
nodetool tablestats my_keyspace.my_table | grep "SSTable count"
```

Let compaction consolidate files, or investigate why flushes are frequent.

---

## Best Practices

!!! tip "Flush Guidelines"
    1. **Before backups**: Always flush before snapshots
    2. **Before shutdown**: Use `drain` which includes flush
    3. **One node at a time**: For cluster-wide operations
    4. **Monitor disk space**: Ensure capacity for new SSTables
    5. **Avoid in scripts loops**: Don't repeatedly flush same tables

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [drain](drain.md) | Flush + disable node |
| [snapshot](snapshot.md) | Create backup after flush |
| [compact](compact.md) | Consolidate SSTables |
| [tablestats](tablestats.md) | Check memtable and SSTable stats |
| [tpstats](tpstats.md) | Monitor flush thread pool |
