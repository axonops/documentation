---
title: "nodetool disableautocompaction"
description: "Disable automatic compaction for Cassandra tables using nodetool disableautocompaction."
meta:
  - name: keywords
    content: "nodetool disableautocompaction, disable compaction, Cassandra compaction, manual compaction"
---

# nodetool disableautocompaction

Disables automatic compaction for specified keyspaces and tables.

---

## Synopsis

```bash
nodetool [connection_options] disableautocompaction [--] [<keyspace> <tables>...]
```

## Description

`nodetool disableautocompaction` prevents automatic compaction from running on specified tables. While disabled, no new compaction tasks will be scheduled by the compaction strategy, though currently running compactions will complete.

!!! warning "Non-Persistent Setting"
    This setting is applied at runtime only and does not persist across node restarts. After a restart, auto-compaction is re-enabled based on the table's compaction strategy configuration.

    There is no `cassandra.yaml` setting to globally disable auto-compaction. To persistently disable compaction for a specific table, set the compaction strategy's `enabled` option to `false`:

    ```cql
    ALTER TABLE my_keyspace.my_table
    WITH compaction = {
        'class': 'LeveledCompactionStrategy',
        'enabled': 'false'
    };
    ```

    This schema change persists across restarts but is generally not recommended for production use.

Disabling auto-compaction is useful for:

- **Bulk data loading** - Avoid compaction overhead during large imports
- **Troubleshooting** - Isolate compaction as a source of issues
- **Controlled maintenance** - Prevent compaction during specific operations
- **Resource management** - Temporarily free I/O and CPU resources

!!! danger "Use with Caution"
    Disabling auto-compaction for extended periods leads to serious performance degradation. SSTable counts grow unbounded, read performance suffers, and tombstones accumulate. Always re-enable promptly.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | Target keyspace name. If omitted, applies to all keyspaces |
| `tables` | Space-separated list of table names. If omitted, applies to all tables in the keyspace |

---

## Examples

### Disable for All Keyspaces and Tables

```bash
# Disable compaction on all tables (use carefully!)
nodetool disableautocompaction
```

### Disable for Specific Keyspace

```bash
# Disable for all tables in a keyspace
nodetool disableautocompaction my_keyspace
```

### Disable for Specific Tables

```bash
# Disable for specific tables only
nodetool disableautocompaction my_keyspace users orders
```

### With Verification

```bash
# Disable and verify
nodetool disableautocompaction my_keyspace my_table
nodetool statusautocompaction my_keyspace my_table
# Expected: running=false
```

---

## When to Use

### Before Bulk Data Loading

Disable compaction to avoid overhead during large imports:

```bash
# 1. Disable auto-compaction
nodetool disableautocompaction my_keyspace my_table

# 2. Load data using sstableloader
sstableloader -d node1,node2,node3 /path/to/sstables/

# 3. Re-enable after load completes
nodetool enableautocompaction my_keyspace my_table

# 4. Force major compaction to consolidate
nodetool compact my_keyspace my_table
```

### During Troubleshooting

Isolate compaction when investigating performance issues:

```bash
# Stop compaction to see if it's the cause
nodetool disableautocompaction my_keyspace

# Monitor system behavior
# ...

# Re-enable when done
nodetool enableautocompaction my_keyspace
```

### Before Repair Operations

Some administrators disable during repair to reduce I/O contention:

```bash
# Disable compaction
nodetool disableautocompaction my_keyspace

# Run repair
nodetool repair -pr my_keyspace

# Re-enable compaction
nodetool enableautocompaction my_keyspace
```

### During Disk Space Emergency

Temporarily halt compaction when disk is critically full:

```bash
# Stop compaction (prevents additional space usage)
nodetool disableautocompaction

# Free space
nodetool clearsnapshot --all
rm -rf /var/lib/cassandra/data/*/*/backups/*

# Re-enable carefully
nodetool enableautocompaction
```

---

## Behavior

### What Happens When Disabled

1. No new compaction tasks are scheduled for the table
2. Currently running compactions complete normally
3. SSTables accumulate without merging
4. Tombstones are not purged through compaction
5. Disk space is not reclaimed from deleted data

### What Continues to Work

| Feature | Status |
|---------|--------|
| Reads | Continue (but may slow down) |
| Writes | Continue normally |
| Memtable flushes | Continue creating new SSTables |
| Streaming | Continues |
| Repair | Continues |
| Manual compaction | Can still be triggered with `compact` |

---

## Impact Assessment

### Immediate Effects

| Aspect | Impact |
|--------|--------|
| Compaction I/O | Stops (after current completes) |
| CPU from compaction | Reduces |
| New compaction tasks | None scheduled |

### Accumulating Effects Over Time

| Duration | Impact |
|----------|--------|
| Minutes | Minimal impact |
| Hours | SSTable count begins growing |
| Days | Noticeable read performance degradation |
| Weeks | Severe performance issues, high SSTable counts |

!!! warning "SSTable Proliferation"
    Without compaction, each memtable flush creates a new SSTable. For write-heavy workloads, this can mean hundreds or thousands of SSTables accumulating quickly.

### Performance Degradation Indicators

| Metric | Normal | After Extended Disable |
|--------|--------|----------------------|
| SSTable count per table | 4-20 (LCS) / varies (STCS) | 100+ |
| Read latency p99 | < 50ms | 200ms+ |
| Bloom filter memory | Normal | Elevated |
| Partition index memory | Normal | Elevated |

---

## Workflow: Controlled Bulk Load

```bash
#!/bin/bash
# bulk_load_controlled.sh

KEYSPACE="my_keyspace"
TABLE="my_table"
DATA_DIR="/data/to/load"

echo "=== Pre-Load Checks ==="
echo "SSTable count before:"
nodetool tablestats $KEYSPACE.$TABLE | grep "SSTable count"

echo ""
echo "=== Disabling Auto-Compaction ==="
nodetool disableautocompaction $KEYSPACE $TABLE

echo "Verifying disabled:"
nodetool statusautocompaction $KEYSPACE $TABLE

echo ""
echo "=== Loading Data ==="
# Your data loading method here
sstableloader -d localhost $DATA_DIR/$KEYSPACE/$TABLE

echo ""
echo "=== Post-Load ==="
echo "SSTable count after load:"
nodetool tablestats $KEYSPACE.$TABLE | grep "SSTable count"

echo ""
echo "=== Re-enabling Auto-Compaction ==="
nodetool enableautocompaction $KEYSPACE $TABLE

echo ""
echo "=== Triggering Major Compaction ==="
nodetool compact $KEYSPACE $TABLE

echo ""
echo "=== Final SSTable Count ==="
nodetool tablestats $KEYSPACE.$TABLE | grep "SSTable count"
```

---

## Monitoring While Disabled

### Track SSTable Growth

```bash
# Check SSTable count periodically
watch -n 60 'nodetool tablestats my_keyspace.my_table | grep "SSTable count"'
```

### Monitor Read Performance

```bash
# Watch read latencies
watch -n 10 'nodetool tablehistograms my_keyspace my_table | head -20'
```

### Check Compaction Status

```bash
# Verify still disabled
nodetool statusautocompaction my_keyspace my_table
```

### Set Reminders

```bash
# Create a reminder to re-enable
echo "nodetool enableautocompaction my_keyspace my_table" | at now + 2 hours
```

---

## Risks and Mitigations

### Risk: Forgot to Re-enable

**Symptom:** Degraded read performance, high SSTable counts

**Mitigation:**
```bash
# Check all tables for disabled auto-compaction
for ks in $(nodetool tablestats | grep "Keyspace:" | awk '{print $2}'); do
    nodetool statusautocompaction $ks 2>/dev/null | grep "false"
done

# Re-enable where needed
nodetool enableautocompaction
```

### Risk: Disk Space Exhaustion

**Symptom:** No space left on device errors

**Cause:** Without compaction, tombstones aren't purged, deleted data isn't reclaimed

**Mitigation:**
```bash
# Check disk usage
df -h /var/lib/cassandra

# Clear snapshots
nodetool clearsnapshot --all

# Re-enable compaction immediately
nodetool enableautocompaction

# May need to reduce throughput if space is critical
nodetool setcompactionthroughput 16
```

### Risk: Tombstone Accumulation

**Symptom:** Read timeouts, TombstoneOverwhelmingException

**Mitigation:**
```bash
# Re-enable compaction
nodetool enableautocompaction my_keyspace my_table

# Run garbagecollect to specifically target tombstones
nodetool garbagecollect my_keyspace my_table
```

---

## Troubleshooting

### Compaction Still Running After Disable

Currently active compactions complete; only new ones are prevented:

```bash
# Check active compactions
nodetool compactionstats

# Wait for completion or stop explicitly
nodetool stop COMPACTION
```

### Cannot Disable (Command Fails)

```bash
# Check JMX connectivity
nodetool info

# Verify keyspace/table names
nodetool tablestats my_keyspace.my_table

# Check logs for errors
tail -100 /var/log/cassandra/system.log | grep -i compaction
```

### Status Shows Enabled After Disable

```bash
# Retry the command
nodetool disableautocompaction my_keyspace my_table

# Verify with specific table
nodetool statusautocompaction my_keyspace my_table

# If still enabled, check for typos in keyspace/table names
```

---

## Cluster-Wide Operations

### Disable on All Nodes

```bash
#!/bin/bash
# disable_autocompaction_cluster.sh

KEYSPACE="my_keyspace"
TABLE="my_table"# Get list of node IPs from local nodetool status


nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

echo "Disabling auto-compaction cluster-wide..."
for node in $nodes; do
    echo -n "$node: "
    ssh "$node" "nodetool disableautocompaction $KEYSPACE $TABLE && echo "disabled" || echo "FAILED""
done

echo ""
echo "Verification:"
for node in $nodes; do
    echo -n "$node: "
    ssh "$node" "nodetool statusautocompaction $KEYSPACE $TABLE 2>/dev/null"
done
```

---

## Recovery Procedure

If auto-compaction has been disabled too long:

```bash
#!/bin/bash
# recover_from_disabled_compaction.sh

echo "=== Compaction Recovery Procedure ==="

# 1. Check current state
echo "1. Current SSTable counts (top 10 highest):"
nodetool tablestats | grep -E "Table:|SSTable count" | paste - - | sort -t: -k3 -nr | head -10

# 2. Check disk space
echo ""
echo "2. Disk space:"
df -h /var/lib/cassandra

# 3. Re-enable auto-compaction
echo ""
echo "3. Re-enabling auto-compaction..."
nodetool enableautocompaction

# 4. Reduce throughput to prevent overwhelming the system
echo ""
echo "4. Setting conservative compaction throughput..."
nodetool setcompactionthroughput 32

# 5. Monitor
echo ""
echo "5. Current compaction status:"
nodetool compactionstats

echo ""
echo "Monitor with: watch -n 5 'nodetool compactionstats'"
echo "Increase throughput gradually: nodetool setcompactionthroughput 64"
```

---

## Best Practices

!!! tip "Disable Guidelines"

    1. **Document the reason** - Note why and when you disabled
    2. **Set a reminder** - Schedule re-enablement
    3. **Monitor SSTable counts** - Watch for accumulation
    4. **Limit scope** - Disable only specific tables, not entire cluster
    5. **Limit duration** - Keep disable period as short as possible
    6. **Have a plan** - Know when and how you'll re-enable
    7. **Inform the team** - Others should know compaction is disabled

!!! danger "Never Do"

    - Leave auto-compaction disabled in production for days
    - Disable cluster-wide without a specific reason
    - Forget to re-enable after maintenance
    - Disable without monitoring SSTable growth

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [enableautocompaction](enableautocompaction.md) | Re-enable auto-compaction |
| [statusautocompaction](statusautocompaction.md) | Check auto-compaction status |
| [compact](compact.md) | Force manual compaction |
| [compactionstats](compactionstats.md) | View active compactions |
| [stop](stop.md) | Stop running compactions |
| [tablestats](tablestats.md) | View SSTable counts |
| [garbagecollect](garbagecollect.md) | Remove tombstones |
