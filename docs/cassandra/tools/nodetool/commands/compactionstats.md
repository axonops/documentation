# nodetool compactionstats

Displays current compaction activity and pending compaction tasks.

## Synopsis

```bash
nodetool [connection_options] compactionstats [options]
```

## Description

The `compactionstats` command shows real-time information about active compaction operations and pending compaction tasks. This is essential for monitoring compaction progress and identifying when compaction is falling behind.

## Options

| Option | Description |
|--------|-------------|
| -H, --human-readable | Display sizes in human-readable format |

## Output Format

The output consists of two sections:
1. **Pending tasks** - Compactions waiting to execute
2. **Active compactions** - Compactions currently running

## Examples

### Basic Compaction Status

```bash
nodetool compactionstats
```

**Output:**
```
pending tasks: 12
- my_keyspace.users: 5
- my_keyspace.orders: 4
- my_keyspace.sessions: 3

id                                   compaction type keyspace    table   completed/total    unit   progress
a1b2c3d4-e5f6-7890-abcd-ef1234567890 Compaction     my_keyspace  users   1234567890/2345678901 bytes  52.65%
b2c3d4e5-f6a7-8901-bcde-f12345678901 Compaction     my_keyspace  orders  987654321/1234567890  bytes  80.00%
Active compaction remaining time :   0h15m32s
```

### Human-Readable Format

```bash
nodetool compactionstats -H
```

**Output:**
```
pending tasks: 12
- my_keyspace.users: 5
- my_keyspace.orders: 4
- my_keyspace.sessions: 3

id                                   compaction type keyspace    table   completed/total  unit   progress
a1b2c3d4-e5f6-7890-abcd-ef1234567890 Compaction     my_keyspace  users   1.1 GiB/2.2 GiB  bytes  52.65%
Active compaction remaining time :   0h15m32s
```

## Output Fields

### Pending Tasks

| Field | Description |
|-------|-------------|
| pending tasks | Total number of compaction tasks waiting |
| keyspace.table | Per-table breakdown of pending tasks |

### Active Compactions

| Field | Description |
|-------|-------------|
| id | Unique identifier for the compaction operation |
| compaction type | Type of operation (Compaction, Cleanup, Scrub, Upgrade, etc.) |
| keyspace | Keyspace being compacted |
| table | Table being compacted |
| completed/total | Progress in bytes or keys |
| unit | Unit of measurement (bytes, keys) |
| progress | Percentage complete |
| remaining time | Estimated time to completion |

## Compaction Types

| Type | Description |
|------|-------------|
| Compaction | Normal SSTable compaction |
| Cleanup | Removing non-local data (nodetool cleanup) |
| Scrub | Rebuilding SSTables (nodetool scrub) |
| Upgrade | Upgrading SSTable format |
| Anticompaction | Splitting repaired/unrepaired data |
| Validation | Building Merkle trees for repair |
| Index_build | Building secondary indexes |
| Relocate | Moving SSTables between disks |

## Interpreting Results

### Healthy Indicators

| Condition | Status |
|-----------|--------|
| pending tasks: 0 | Compaction is keeping up |
| pending tasks: 1-4 | Normal operation |
| Active compaction showing progress | Compaction proceeding normally |

### Warning Indicators

| Condition | Threshold | Action |
|-----------|-----------|--------|
| pending tasks | > 32 | Compaction falling behind - investigate |
| pending tasks | > 100 | Critical - increase compaction throughput |
| No progress on active | Stalled | Check disk I/O, memory |
| Same compaction running for hours | Stalled | May need intervention |

## Common Use Cases

### Continuous Monitoring

```bash
# Watch compaction status every 5 seconds
watch -n 5 'nodetool compactionstats'
```

### Wait for Compaction Completion

```bash
#!/bin/bash
# Wait for pending compactions to complete

while [ $(nodetool compactionstats | grep "pending tasks" | awk '{print $3}') -gt 0 ]; do
    echo "Waiting for compaction... $(nodetool compactionstats | head -1)"
    sleep 30
done

echo "All compactions complete"
```

### Alert on Backlog

```bash
#!/bin/bash
# Alert if pending compactions exceed threshold

THRESHOLD=50
PENDING=$(nodetool compactionstats | grep "pending tasks" | awk '{print $3}')

if [ "$PENDING" -gt "$THRESHOLD" ]; then
    echo "CRITICAL: $PENDING pending compactions (threshold: $THRESHOLD)"
    exit 2
fi

echo "OK: $PENDING pending compactions"
exit 0
```

## Troubleshooting

### High Pending Task Count

**Causes:**
- Compaction throughput too low
- High write volume
- Disk I/O saturation
- Insufficient concurrent compactors

**Resolution:**
```bash
# Check current throughput
nodetool getcompactionthroughput

# Increase throughput temporarily
nodetool setcompactionthroughput 128

# Check concurrent compactors
grep concurrent_compactors /etc/cassandra/cassandra.yaml
```

### Compaction Not Progressing

**Investigation:**
```bash
# Check disk I/O
iostat -x 1 5

# Check if compaction is blocked
nodetool tpstats | grep CompactionExecutor

# Check for resource contention
top -p $(pgrep -f cassandra)
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Command executed successfully |
| 1 | Error occurred |

## Related Commands

- [nodetool compact](compact.md) - Force compaction
- [nodetool setcompactionthroughput](setcompactionthroughput.md) - Adjust throughput
- [nodetool stop](stop.md) - Stop compaction
- [nodetool tablestats](tablestats.md) - Check SSTable counts

## Version Information

Available in all Apache Cassandra versions.
