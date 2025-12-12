---
description: "Upgrade SSTables to current Cassandra version format using nodetool upgradesstables."
meta:
  - name: keywords
    content: "nodetool upgradesstables, upgrade SSTables, SSTable version, Cassandra upgrade"
---

# nodetool upgradesstables

Rewrites SSTables to the SSTable format version supported by the running Cassandra instance.

---

## Synopsis

```bash
nodetool [connection_options] upgradesstables [options] [--] [keyspace [table ...]]
```

## Description

`nodetool upgradesstables` rewrites SSTables that were created by older Cassandra versions into the SSTable format corresponding to the currently running Cassandra version. The target format is determined automatically by the Cassandra instance—each major Cassandra release introduces a new SSTable format version with improvements to encoding, compression, and metadata storage.

This operation is recommended after upgrading Cassandra to ensure all SSTables benefit from the latest format's features and optimizations. SSTables already in the current format are skipped unless the `-a` flag is specified.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | Keyspace to upgrade. If omitted, upgrades all keyspaces |
| `table` | Specific table(s) to upgrade |

---

## Options

| Option | Description |
|--------|-------------|
| `-a, --include-all-sstables` | Upgrade all SSTables, even if already current version |
| `-j, --jobs <jobs>` | Number of concurrent upgrade jobs (default: 2) |

---

## When to Run

### After Cassandra Upgrade

```bash
# After upgrading from 4.0 to 4.1
nodetool upgradesstables
```

### Check SSTable Versions First

```bash
# See which versions exist
ls /var/lib/cassandra/data/my_keyspace/my_table-*/
# Look for version prefixes: mc-, nb-, etc.
```

| Prefix | Cassandra Version |
|--------|-------------------|
| `mc-` | 3.0+ |
| `nb-` | 4.0+ |
| `nc-` | 5.0+ |

---

## Examples

### Upgrade All SSTables

```bash
nodetool upgradesstables
```

### Upgrade Specific Keyspace

```bash
nodetool upgradesstables my_keyspace
```

### Upgrade Specific Table

```bash
nodetool upgradesstables my_keyspace my_table
```

### Force Upgrade All (Including Current)

```bash
nodetool upgradesstables -a my_keyspace
```

### Parallel Upgrade

```bash
nodetool upgradesstables -j 4 my_keyspace
```

---

## Process

1. Identify SSTables with older format version
2. Read data from old SSTable
3. Write data to new SSTable in current format
4. Replace old SSTable with new one
5. Remove old SSTable files

---

## Disk Space Requirements

!!! warning "Space Needed"
    Like compaction, upgradesstables needs temporary space:

    ```
    Space needed ≈ Size of largest SSTable being upgraded
    ```

Check available space:

```bash
df -h /var/lib/cassandra/data
```

---

## Monitoring Progress

### Check Running Upgrades

```bash
nodetool compactionstats
```

Upgrade appears as a compaction operation with type "Upgrade".

### Watch Progress

```bash
watch -n 5 'nodetool compactionstats | grep -i upgrade'
```

---

## Performance Impact

!!! info "I/O Intensive"
    - Reads all qualifying SSTables
    - Writes new SSTables
    - Similar to major compaction
    - Run during low-traffic periods

### Recommended Approach

```bash
# 1. Run on one node at a time
# 2. Start with smaller keyspaces
nodetool upgradesstables system_schema
nodetool upgradesstables system

# 3. Then production keyspaces
nodetool upgradesstables production_ks
```

---

## Upgrade Order After Version Upgrade

```bash
# 1. System keyspaces first
nodetool upgradesstables system_schema
nodetool upgradesstables system
nodetool upgradesstables system_auth
nodetool upgradesstables system_distributed
nodetool upgradesstables system_traces

# 2. Application keyspaces
nodetool upgradesstables my_app_keyspace
```

---

## Common Issues

### Upgrade Takes Too Long

Large tables take significant time:

```bash
# Check progress
nodetool compactionstats

# Consider upgrading table by table
nodetool upgradesstables my_keyspace small_table
nodetool upgradesstables my_keyspace medium_table
nodetool upgradesstables my_keyspace large_table
```

### Not Enough Disk Space

```bash
# Free space first
nodetool clearsnapshot

# Or upgrade one table at a time
nodetool upgradesstables my_keyspace table1
# Wait for completion
nodetool upgradesstables my_keyspace table2
```

### SSTables Already Current

If all SSTables are already current version:

```
Nothing to upgrade for my_keyspace.my_table
```

This is expected and not an error.

---

## Skipping Upgradesstables

!!! danger "Not Recommended"
    Skipping upgradesstables after a major version upgrade may cause:

    - Reduced performance (old format not optimized)
    - Compatibility issues
    - Problems during repair
    - Issues with new features

---

## Automation Script

```bash
#!/bin/bash
# upgrade_all_sstables.sh

LOG="/var/log/cassandra/upgrade_sstables_$(date +%Y%m%d).log"

echo "Starting SSTable upgrade at $(date)" >> $LOG

# System keyspaces first
for ks in system_schema system system_auth system_distributed system_traces; do
    echo "Upgrading $ks..." >> $LOG
    nodetool upgradesstables $ks >> $LOG 2>&1
done

# Then all user keyspaces
for ks in $(nodetool tablestats 2>/dev/null | grep "Keyspace:" | awk '{print $2}' | grep -v "^system"); do
    echo "Upgrading $ks..." >> $LOG
    nodetool upgradesstables $ks >> $LOG 2>&1
done

echo "Completed at $(date)" >> $LOG
```

---

## Best Practices

!!! tip "Upgrade Guidelines"
    1. **Run after every major upgrade** - Essential for compatibility
    2. **System keyspaces first** - They're smaller and critical
    3. **One node at a time** - Reduce cluster impact
    4. **Check disk space** - Ensure sufficient room
    5. **Monitor progress** - Watch compactionstats
    6. **Run during maintenance window** - High I/O impact

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [compactionstats](compactionstats.md) | Monitor upgrade progress |
| [scrub](scrub.md) | Rewrite SSTables (for corruption) |
| [compact](compact.md) | Force compaction |
| [tablestats](tablestats.md) | View SSTable counts |
