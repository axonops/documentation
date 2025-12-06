# nodetool flush

Flushes memtables to SSTables on disk for specified tables.

## Synopsis

```bash
nodetool [connection_options] flush [keyspace [table ...]]
```

## Description

The `flush` command forces the immediate write of in-memory data (memtables) to disk as SSTables. While Cassandra automatically flushes memtables based on memory thresholds and time intervals, manual flushing is useful for specific operational scenarios.

Data durability is not affected by flushing since all writes are also recorded in the commitlog. Flushing primarily impacts read performance (data becomes available in SSTables) and prepares data for snapshot operations.

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| keyspace | No | Keyspace to flush. If omitted, flushes all keyspaces. |
| table | No | Specific table(s) to flush within the keyspace |

## Examples

### Flush All Keyspaces

```bash
nodetool flush
```

### Flush Specific Keyspace

```bash
nodetool flush my_keyspace
```

### Flush Specific Table

```bash
nodetool flush my_keyspace users
```

### Flush Multiple Tables

```bash
nodetool flush my_keyspace users orders sessions
```

## When to Use

### Appropriate Use Cases

| Scenario | Reason |
|----------|--------|
| Before taking a snapshot | Ensures all data is captured in the snapshot |
| Before graceful shutdown | Reduces commitlog replay time on restart |
| Before measuring table size | Accurate tablestats for flushed data |
| Before disabling autocompaction | Prepares data for manual compaction control |
| Before rolling restart | Minimizes recovery time |

### When Not Necessary

| Scenario | Reason |
|----------|--------|
| Normal operations | Automatic flushing handles this |
| Data durability | Commitlog already provides durability |
| Routine maintenance | Generally unnecessary |

## Flush Process

### What Happens During Flush

1. Current memtable is frozen (no new writes accepted to it)
2. New memtable is created for incoming writes
3. Frozen memtable is written to SSTable(s)
4. Commitlog segments for flushed data become eligible for deletion
5. Memory is reclaimed

### Flush Triggers (Automatic)

Cassandra automatically flushes when:

| Trigger | Configuration |
|---------|--------------|
| Memory threshold | `memtable_heap_space_in_mb` / `memtable_offheap_space_in_mb` |
| Time interval | `memtable_flush_period_in_ms` |
| Commitlog full | `commitlog_total_space_in_mb` |
| Before compaction | When SSTables are needed |

## Monitoring Flush Status

### Check Pending Flushes

```bash
nodetool tpstats | grep MemtableFlushWriter
```

**Output:**
```
MemtableFlushWriter                    1         0          12345         0                 0
```

- `Active: 1` - One flush in progress
- `Pending: 0` - No flushes waiting

### Check Table Memtable Status

```bash
nodetool tablestats my_keyspace.users | grep -i memtable
```

**Output:**
```
Memtable cell count: 125000
Memtable data size: 48500000
Memtable off heap memory used: 0
Memtable switch count: 234
Pending flushes: 0
```

## Common Use Cases

### Pre-Snapshot Flush

```bash
#!/bin/bash
# Flush before snapshot to capture all data
KEYSPACE="my_keyspace"
TAG="backup_$(date +%Y%m%d)"

# Flush to disk
nodetool flush $KEYSPACE

# Take snapshot
nodetool snapshot -t $TAG $KEYSPACE
```

### Graceful Shutdown Procedure

```bash
#!/bin/bash
# Graceful shutdown with flush

# Flush all keyspaces
nodetool flush

# Drain the node
nodetool drain

# Stop the service
sudo systemctl stop cassandra
```

### Memory Pressure Relief

```bash
#!/bin/bash
# Flush to free heap memory during high memory usage

HEAP_USAGE=$(nodetool info | grep "Heap Memory" | awk '{print $4/$6 * 100}')

if (( $(echo "$HEAP_USAGE > 80" | bc -l) )); then
    echo "High heap usage detected ($HEAP_USAGE%). Flushing..."
    nodetool flush
fi
```

## Impact

### Performance Considerations

| Aspect | Impact |
|--------|--------|
| Write latency | Minimal - new memtable immediately available |
| Read latency | May slightly improve for flushed data |
| Disk I/O | Temporary spike during flush |
| Compaction | May trigger compaction of new SSTable |

### Resource Usage

| Resource | Impact |
|----------|--------|
| Memory | Freed after flush completes |
| Disk space | Increases (new SSTable created) |
| CPU | Moderate (serialization, compression) |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Flush completed successfully |
| 1 | Error occurred |
| 2 | Invalid arguments |

## Related Commands

- [nodetool drain](drain.md) - Flush and prepare for shutdown
- [nodetool snapshot](snapshot.md) - Create backup snapshot
- [nodetool tablestats](tablestats.md) - Check memtable statistics
- [nodetool tpstats](tpstats.md) - Monitor flush thread pool

## Related Documentation

- [Architecture - Storage Engine](../../../architecture/storage-engine/index.md) - Memtable and SSTable concepts
- [Operations - Backup & Restore](../../../operations/backup-restore/index.md) - Backup procedures
- [Operations - Maintenance](../../../operations/maintenance/index.md) - Routine maintenance
- [Configuration - cassandra.yaml](../../../configuration/cassandra-yaml/index.md) - Memtable settings

## Version Information

Available in all Apache Cassandra versions with consistent behavior.
