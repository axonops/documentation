# nodetool compact

Forces compaction on specified tables, merging SSTables and removing obsolete data.

## Synopsis

```bash
nodetool [connection_options] compact [options] [keyspace [table ...]]
```

## Description

The `compact` command triggers compaction operations outside the normal automated compaction process. Compaction merges multiple SSTables into fewer, larger SSTables while removing deleted data (tombstones), expired TTL data, and superseded cell values.

Use this command sparingly in production environments, as forced compaction can consume significant I/O resources and temporarily impact cluster performance.

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| keyspace | No | Keyspace containing tables to compact |
| table | No | Specific table(s) to compact |

## Options

| Option | Description |
|--------|-------------|
| -s, --split-output | Produce multiple output SSTables based on sstable_size target |
| --user-defined | Perform major compaction (all SSTables into one or few) |
| -st, --start-token &lt;token&gt; | Compact only SSTables covering this start token |
| -et, --end-token &lt;token&gt; | Compact only SSTables covering this end token |

## Compaction Types

### Normal Compaction

Compacts SSTables according to the table's configured compaction strategy rules.

```bash
nodetool compact my_keyspace my_table
```

### Major Compaction (--user-defined)

Forces all SSTables to be compacted together, typically producing a single large SSTable per table.

```bash
nodetool compact --user-defined my_keyspace my_table
```

**Caution:** Major compaction has significant implications:
- Creates very large SSTables
- Requires up to 2x disk space during operation
- Resets SSTable timestamps, affecting TWCS
- Reduces efficiency of SizeTiered compaction
- Can cause extended GC pauses during subsequent reads

### Subrange Compaction

Compacts only SSTables covering a specific token range.

```bash
nodetool compact -st -9223372036854775808 -et 0 my_keyspace my_table
```

## Examples

### Compact Specific Table

```bash
nodetool compact my_keyspace users
```

### Compact All Tables in Keyspace

```bash
nodetool compact my_keyspace
```

### Compact All Tables (All Keyspaces)

```bash
nodetool compact
```

### Major Compaction with Split Output

```bash
# Major compaction producing multiple SSTables at target size
nodetool compact --user-defined -s my_keyspace users
```

### Token Range Compaction

```bash
# Compact SSTables in first half of token range
nodetool compact -st -9223372036854775808 -et 0 my_keyspace users
```

## When to Use

### Appropriate Use Cases

| Scenario | Recommended Approach |
|----------|---------------------|
| After bulk delete | Force compaction to reclaim space |
| After bulk TTL expiration | Force compaction to remove expired data |
| Before snapshot | Reduce SSTable count for smaller backup |
| Testing compaction behavior | Trigger controlled compaction |
| Resolving high SSTable count | When automatic compaction is behind |

### When to Avoid

| Scenario | Reason |
|----------|--------|
| Routine maintenance | Let automatic compaction handle it |
| Production peak hours | I/O impact on performance |
| With TWCS strategy | Disrupts time-windowed buckets |
| Low disk space | Compaction needs temporary space |

## Monitoring Compaction Progress

### Check Active Compactions

```bash
nodetool compactionstats
```

**Output:**
```
pending tasks: 3
- my_keyspace.users: 1
- my_keyspace.orders: 2

id                                   compaction type keyspace    table   completed/total   unit    progress
a1b2c3d4-e5f6-7890-abcd-ef1234567890 Compaction     my_keyspace  users   1234567890/2345678901 bytes  52.65%
Active compaction remaining time :   0h15m32s
```

### Stop Running Compaction

```bash
nodetool stop COMPACTION
```

**Note:** Stopping compaction may leave partially written SSTables that will be cleaned up on restart.

## Impact Analysis

### Resource Consumption

| Resource | Impact |
|----------|--------|
| Disk I/O | High - reads and writes SSTables |
| Disk Space | Up to 2x table size temporarily |
| CPU | Moderate - compression/decompression |
| Memory | Moderate - bloom filter construction |

### Performance Impact

| Metric | Expected Change |
|--------|-----------------|
| Read latency | May increase during compaction |
| Write latency | Usually unaffected |
| Pending compactions | Increases then decreases |
| Disk utilization | Spikes during operation |

## Strategy-Specific Behavior

### SizeTieredCompactionStrategy (STCS)

- Compacts SSTables of similar size
- Major compaction creates oversized SSTable, reducing future efficiency
- Avoid major compaction with STCS

### LeveledCompactionStrategy (LCS)

- Maintains SSTables at fixed sizes in levels
- Major compaction disrupts level structure
- Recovery can take extended time

### TimeWindowCompactionStrategy (TWCS)

- Groups SSTables by time window
- Major compaction destroys time-based grouping
- **Strongly avoid** major compaction with TWCS

### UnifiedCompactionStrategy (UCS)

- Cassandra 5.0+ adaptive strategy
- Handles forced compaction appropriately
- Preferred for most workloads in 5.x

## Common Use Cases

### Reclaim Space After Bulk Delete

```bash
#!/bin/bash
# After large delete operation, force compaction to reclaim space
KEYSPACE="my_keyspace"
TABLE="users"

echo "Current space usage:"
nodetool tablestats $KEYSPACE.$TABLE | grep "Space used"

echo "Starting compaction..."
nodetool compact $KEYSPACE $TABLE

echo "Waiting for compaction to complete..."
while nodetool compactionstats | grep -q "$TABLE"; do
    sleep 10
done

echo "Final space usage:"
nodetool tablestats $KEYSPACE.$TABLE | grep "Space used"
```

### Pre-Backup Compaction

```bash
#!/bin/bash
# Reduce SSTable count before taking snapshot
KEYSPACE="my_keyspace"

# Compact all tables
nodetool compact $KEYSPACE

# Wait for completion
while nodetool compactionstats | grep -q "pending tasks: [1-9]"; do
    echo "Waiting for compaction..."
    sleep 30
done

# Take snapshot
nodetool snapshot -t pre_backup_$(date +%Y%m%d) $KEYSPACE
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Compaction initiated successfully |
| 1 | Error occurred |
| 2 | Invalid arguments |

## Related Commands

- [nodetool compactionstats](compactionstats.md) - Monitor compaction progress
- [nodetool garbagecollect](garbagecollect.md) - Remove only tombstones
- [nodetool setcompactionthroughput](setcompactionthroughput.md) - Adjust compaction speed
- [nodetool enableautocompaction](enableautocompaction.md) - Control automatic compaction
- [nodetool disableautocompaction](disableautocompaction.md) - Disable automatic compaction

## Related Documentation

- [Architecture - Compaction](../../../architecture/compaction/index.md) - Compaction strategies and concepts
- [Troubleshooting - Compaction Backlog](../../../troubleshooting/playbooks/compaction-backlog.md) - Resolving compaction issues
- [Operations - Maintenance](../../../operations/maintenance/index.md) - Routine maintenance procedures
- [Configuration - cassandra.yaml](../../../configuration/cassandra-yaml/index.md) - Compaction configuration

## Version Information

Available in all Apache Cassandra versions. The `--user-defined` option replaced the older major compaction syntax. Token range options provide finer control in Cassandra 4.0+.
