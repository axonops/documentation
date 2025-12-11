# nodetool enableautocompaction

Re-enables automatic compaction for specified keyspaces and tables.

---

## Synopsis

```bash
nodetool [connection_options] enableautocompaction [--] [<keyspace> <tables>...]
```

## Description

`nodetool enableautocompaction` restores automatic compaction behavior for one or more tables after it was temporarily disabled with `disableautocompaction`. When auto-compaction is enabled, Cassandra's compaction strategy continuously evaluates SSTables and triggers compaction operations based on configured thresholds and policies.

Automatic compaction is essential for:

- **Maintaining read performance** - Merging SSTables reduces the number of files to scan
- **Reclaiming disk space** - Removing tombstones and expired data
- **Data consistency** - Ensuring deleted data is eventually purged
- **Preventing SSTable proliferation** - Keeping file counts manageable

!!! info "Default State"
    Auto-compaction is **enabled by default** on all tables. This command is only needed after explicitly disabling it with `disableautocompaction`.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | Target keyspace name. If omitted, applies to all keyspaces |
| `tables` | Space-separated list of table names. If omitted, applies to all tables in the keyspace |

---

## Examples

### Enable for All Keyspaces and Tables

```bash
# Re-enable compaction cluster-wide on this node
nodetool enableautocompaction
```

### Enable for Specific Keyspace

```bash
# Re-enable for all tables in a keyspace
nodetool enableautocompaction my_keyspace
```

### Enable for Specific Tables

```bash
# Re-enable for specific tables only
nodetool enableautocompaction my_keyspace users orders products
```

### With Verification

```bash
# Enable and verify
nodetool enableautocompaction my_keyspace my_table
nodetool statusautocompaction my_keyspace my_table
# Expected: running=true
```

---

## When to Use

### After Bulk Data Loading

Re-enable compaction after loading large amounts of data:

```bash
# 1. Disable compaction before bulk load
nodetool disableautocompaction my_keyspace my_table

# 2. Load data (sstableloader, COPY, etc.)
sstableloader -d node1,node2 /path/to/sstables/

# 3. Re-enable compaction
nodetool enableautocompaction my_keyspace my_table

# 4. Optionally force immediate compaction
nodetool compact my_keyspace my_table
```

### After Maintenance Operations

Restore normal operation after maintenance:

```bash
# After repair or other maintenance
nodetool enableautocompaction my_keyspace

# Monitor compaction activity
watch nodetool compactionstats
```

### After Troubleshooting

When compaction was disabled to investigate issues:

```bash
# Issue identified and resolved
nodetool enableautocompaction

# Verify compaction resumes
nodetool compactionstats
```

### After Node Recovery

When bringing a node back to normal operation:

```bash
# Node recovered, restore full functionality
nodetool enableautocompaction

# Check for compaction backlog
nodetool compactionstats
```

---

## Behavior

### What Happens When Enabled

1. The table is marked as eligible for automatic compaction
2. The compaction strategy begins evaluating SSTables
3. Compaction tasks are scheduled based on strategy rules
4. Pending compaction backlog begins processing

### Compaction Strategy Interaction

The enabled auto-compaction respects the table's configured compaction strategy:

| Strategy | Behavior After Enable |
|----------|----------------------|
| SizeTieredCompactionStrategy (STCS) | Compacts SSTables of similar sizes |
| LeveledCompactionStrategy (LCS) | Promotes SSTables through levels |
| TimeWindowCompactionStrategy (TWCS) | Compacts within time windows |
| UnifiedCompactionStrategy (UCS) | Adaptive compaction (Cassandra 5.0+) |

---

## Impact Assessment

### Immediate Effects

| Aspect | Impact |
|--------|--------|
| Compaction scheduling | Resumes immediately |
| Disk I/O | May increase as backlog processes |
| CPU usage | Compaction threads become active |
| Pending tasks | Begin processing |

### Short-term Effects

| Aspect | Impact |
|--------|--------|
| SSTable count | Begins decreasing |
| Read latency | Improves as SSTables merge |
| Disk usage | May spike during compaction |
| Write amplification | Normal levels resume |

!!! warning "Compaction Backlog"
    If auto-compaction was disabled for an extended period, there may be a significant backlog. Monitor disk space and I/O during catch-up.

---

## Workflow: Complete Bulk Load Procedure

```bash
#!/bin/bash
# bulk_load_with_compaction_control.sh

KEYSPACE="my_keyspace"
TABLE="my_table"
DATA_PATH="/path/to/sstables"

echo "=== Bulk Load with Compaction Control ==="

# 1. Check current state
echo "1. Current compaction status:"
nodetool statusautocompaction $KEYSPACE $TABLE

# 2. Disable auto-compaction
echo "2. Disabling auto-compaction..."
nodetool disableautocompaction $KEYSPACE $TABLE

# 3. Verify disabled
echo "3. Verifying disabled:"
nodetool statusautocompaction $KEYSPACE $TABLE

# 4. Load data
echo "4. Loading data..."
sstableloader -d localhost $DATA_PATH

# 5. Re-enable auto-compaction
echo "5. Re-enabling auto-compaction..."
nodetool enableautocompaction $KEYSPACE $TABLE

# 6. Verify enabled
echo "6. Verifying enabled:"
nodetool statusautocompaction $KEYSPACE $TABLE

# 7. Check compaction activity
echo "7. Current compaction activity:"
nodetool compactionstats

echo "=== Complete ==="
```

---

## Monitoring After Enable

### Check Compaction Activity

```bash
# View active and pending compactions
nodetool compactionstats
```

Example output showing compaction resuming:
```
pending tasks: 15
- my_keyspace.my_table: 15

Active compaction remaining time :   0h00m45s
        compaction type   keyspace         table   completed      total    unit   progress
         Compaction   my_keyspace      my_table   524288000   1048576000   bytes     50.00%
```

### Monitor Over Time

```bash
# Watch compaction progress
watch -n 5 'nodetool compactionstats'
```

### Check SSTable Counts

```bash
# Before re-enabling (many SSTables)
nodetool tablestats my_keyspace.my_table | grep "SSTable count"
# SSTable count: 47

# After compaction catches up (fewer SSTables)
nodetool tablestats my_keyspace.my_table | grep "SSTable count"
# SSTable count: 8
```

---

## Troubleshooting

### Compaction Not Starting After Enable

If compaction doesn't start after enabling:

```bash
# Verify status is enabled
nodetool statusautocompaction my_keyspace my_table

# Check for pending tasks
nodetool compactionstats

# If no pending tasks, may need to wait for strategy evaluation
# Or force compaction
nodetool compact my_keyspace my_table
```

### High I/O After Enable

If I/O is too high after enabling:

```bash
# Reduce compaction throughput temporarily
nodetool setcompactionthroughput 32

# Let backlog process gradually
watch nodetool compactionstats

# Restore normal throughput later
nodetool setcompactionthroughput 64
```

### Disk Space Issues

If disk space is critical:

```bash
# Check current usage
df -h /var/lib/cassandra

# May need to process compaction slowly
nodetool setcompactionthroughput 16

# Clear snapshots if needed
nodetool clearsnapshot --all
```

---

## Cluster-Wide Operations

### Enable on All Nodes

```bash
#!/bin/bash
# enable_autocompaction_cluster.sh

KEYSPACE="my_keyspace"
TABLE="my_table"

nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo "Enabling auto-compaction on $node..."
    nodetool -h $node enableautocompaction $KEYSPACE $TABLE
done

echo "Verification:"
for node in $nodes; do
    echo -n "$node: "
    nodetool -h $node statusautocompaction $KEYSPACE $TABLE
done
```

---

## Best Practices

!!! tip "Auto-Compaction Guidelines"

    1. **Re-enable promptly** - Don't leave auto-compaction disabled for extended periods
    2. **Verify after enabling** - Always check with `statusautocompaction`
    3. **Monitor the backlog** - Watch `compactionstats` for catch-up progress
    4. **Control throughput** - Adjust compaction throughput if I/O impact is too high
    5. **Check disk space** - Ensure sufficient space for compaction to proceed
    6. **Document changes** - Log when and why auto-compaction was disabled/enabled
    7. **Apply consistently** - Enable on all nodes if disabled cluster-wide

!!! warning "Long-term Disable Risks"
    Keeping auto-compaction disabled for extended periods causes:

    - SSTable proliferation (many small files)
    - Degraded read performance
    - Increased memory usage for bloom filters
    - Tombstone accumulation
    - Potential disk space issues

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [disableautocompaction](disableautocompaction.md) | Disable auto-compaction |
| [statusautocompaction](statusautocompaction.md) | Check auto-compaction status |
| [compact](compact.md) | Force manual compaction |
| [compactionstats](compactionstats.md) | View active compactions |
| [setcompactionthroughput](setcompactionthroughput.md) | Control compaction rate |
| [tablestats](tablestats.md) | View SSTable counts |
