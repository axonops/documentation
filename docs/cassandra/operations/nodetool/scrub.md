# nodetool scrub

Rebuilds SSTables by rewriting them, validating data and optionally discarding corrupted partitions.

---

## Synopsis

```bash
nodetool [connection_options] scrub [options] [--] [keyspace [table ...]]
```

## Description

`nodetool scrub` reads SSTables and rewrites them, performing validation and cleanup. It can:

- Fix SSTable corruption
- Rewrite SSTables in current format
- Remove corrupt data (with `-s` flag)
- Validate partition ordering

Scrub operates locally and does not involve other nodes.

---

## Causes of SSTable Corruption

SSTable corruption is relatively rare but can occur due to several factors:

| Cause | Description |
|-------|-------------|
| **Hardware failures** | Failing disks, bad sectors, faulty RAID controllers, or memory errors (bit flips) can corrupt data during writes or reads |
| **Unexpected process termination** | If Cassandra is killed (SIGKILL) or crashes during SSTable writes or compaction, partially written files may be corrupted |
| **Power loss** | Sudden power failure without proper shutdown can leave SSTables in an inconsistent state, particularly if disk write caches were not flushed |
| **Filesystem issues** | Bugs in the filesystem, filesystem corruption, or running out of disk space during writes |
| **Network storage problems** | When using network-attached storage (NAS/SAN), network interruptions during writes can cause corruption |
| **Kernel or driver bugs** | Bugs in storage drivers, kernel I/O subsystems, or virtualization layers |
| **Manual file manipulation** | Accidental deletion, modification, or truncation of SSTable files |
| **Software bugs** | Rarely, bugs in Cassandra itself during compaction or SSTable generation |

!!! tip "Prevention"
    - Use ECC memory to prevent bit flips
    - Configure disk write caching appropriately (battery-backed or disabled)
    - Ensure proper shutdown procedures
    - Monitor disk health with S.M.A.R.T.
    - Use checksums (enabled by default in Cassandra)
    - Maintain adequate free disk space

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | Keyspace to scrub. If omitted, scrubs all keyspaces |
| `table` | Specific table(s) to scrub |

---

## Options

| Option | Description |
|--------|-------------|
| `-s, --skip-corrupted` | Skip corrupted partitions instead of failing |
| `-n, --no-validate` | Skip validation (faster but less thorough) |
| `-r, --reinsert-overflowed-ttl` | Reinsert rows with overflowed TTL |
| `-j, --jobs` | Number of concurrent scrub jobs |

---

## When to Use

### After Detecting Corruption

When logs show SSTable corruption:

```
ERROR [CompactionExecutor:1] CorruptSSTableException: Corrupted: /var/lib/cassandra/data/...
```

```bash
nodetool scrub my_keyspace my_table
```

### After Unexpected Shutdown

If Cassandra crashed or was killed:

```bash
# Check for corruption first
nodetool verify my_keyspace

# If issues found
nodetool scrub my_keyspace
```

### After Disk Errors

Following disk I/O errors that may have corrupted data:

```bash
nodetool scrub my_keyspace
```

### Rewriting SSTables After Format Changes

After modifying compression or other SSTable settings:

```bash
nodetool scrub my_keyspace my_table
```

---

## When NOT to Use

### As Routine Maintenance

!!! warning "Not for Regular Use"
    Scrub is a repair operation for corruption, not routine maintenance:

    - Rewrites all SSTables (resource intensive)
    - Should only be used when corruption is suspected
    - Normal compaction handles most SSTable maintenance

### On Healthy SSTables

```bash
# First verify if scrub is actually needed
nodetool verify my_keyspace my_table
```

If verify passes without errors, scrub is unnecessary.

### During High Load

!!! danger "Performance Impact"
    Scrub is I/O intensive:

    - Reads all SSTables
    - Writes new SSTables
    - Can impact production workloads

    Run during maintenance windows.

---

## Skip Corrupted Option

### Without Skip-Corrupted

```bash
nodetool scrub my_keyspace my_table
```

If corruption is found, scrub fails and stops:
```
ERROR: Scrub failed because of corrupted data at position X
```

### With Skip-Corrupted

```bash
nodetool scrub -s my_keyspace my_table
```

!!! danger "Data Loss Warning"
    The `-s` flag discards corrupted partitions:

    - Corrupted data is permanently lost
    - No way to recover skipped partitions
    - Use only when data loss is acceptable

    **After using -s, run repair to recover data from replicas:**
    ```bash
    nodetool repair my_keyspace my_table
    ```

---

## Process Flow

1. Read SSTable sequentially
2. Validate partition ordering
3. Check partition data integrity
4. If corruption found:
   - With `-s`: Log and skip corrupted partition
   - Without `-s`: Fail scrub immediately
5. Write valid partition to new SSTable
6. Repeat for all partitions
7. Replace old SSTable with new one

---

## Examples

### Scrub Specific Table

```bash
nodetool scrub my_keyspace my_table
```

### Scrub All Tables in Keyspace

```bash
nodetool scrub my_keyspace
```

### Scrub with Skip Corrupted

```bash
nodetool scrub -s my_keyspace my_table
```

### Scrub Without Validation (Faster)

```bash
nodetool scrub -n my_keyspace my_table
```

### Parallel Scrub

```bash
nodetool scrub -j 4 my_keyspace
```

---

## Monitoring Scrub

### Check Progress

```bash
nodetool compactionstats
```

Scrub appears as a compaction operation.

### Check Logs

```bash
tail -f /var/log/cassandra/system.log | grep -i scrub
```

Logs show:
- Progress
- Any corruption found
- Partitions skipped (if -s used)
- Completion status

---

## Disk Space Requirements

!!! danger "Space Needed"
    Scrub rewrites SSTables, requiring temporary space:

    ```
    Space needed ≈ Size of largest SSTable being scrubbed
    ```

    Ensure sufficient free space before running scrub.

Check space:
```bash
df -h /var/lib/cassandra/data
nodetool tablestats my_keyspace.my_table | grep "Space used"
```

---

## Recovery Workflow

### Complete Recovery Process

```bash
# Step 1: Identify corrupted table from logs
# Look for CorruptSSTableException in system.log

# Step 2: Verify corruption
nodetool verify my_keyspace my_table

# Step 3: Attempt scrub without skip (preserves data if possible)
nodetool scrub my_keyspace my_table

# Step 4: If scrub fails, use skip-corrupted
nodetool scrub -s my_keyspace my_table

# Step 5: Repair to recover lost data from replicas
nodetool repair -pr my_keyspace my_table
```

---

## Common Issues

### "Not enough space"

```
ERROR: Not enough space to scrub
```

Solutions:
- Free disk space
- Scrub one table at a time
- Move data files to larger volume

### Scrub Takes Too Long

Large tables take significant time:

| Table Size | Approximate Duration |
|------------|---------------------|
| 10 GB | 10-30 minutes |
| 100 GB | 1-3 hours |
| 1 TB | 10+ hours |

### Scrub Finds Corruption Repeatedly

If corruption keeps appearing:

1. Check disk health
2. Check for memory errors
3. Review system logs
4. May indicate hardware failure

---

## Scrub vs. Other Commands

| Command | Purpose |
|---------|---------|
| `scrub` | Fix corrupted SSTables |
| `verify` | Check for corruption (read-only) |
| `compact` | Merge SSTables (not for corruption) |
| `repair` | Sync data between replicas |
| `upgradesstables` | Convert SSTables to new format |

### Verification Before Scrub

```bash
# Check first
nodetool verify my_keyspace my_table

# Scrub only if verify fails
nodetool scrub my_keyspace my_table
```

---

## Best Practices

!!! tip "Scrub Guidelines"
    1. **Verify first** - Confirm corruption before scrubbing
    2. **Check disk space** - Ensure room for rewritten SSTables
    3. **Off-peak hours** - High I/O impact
    4. **One table at a time** - For large keyspaces
    5. **Repair after skip** - Recover data from replicas
    6. **Investigate root cause** - Corruption indicates underlying issues

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [compact](compact.md) | Merge SSTables |
| [repair](repair.md) | Sync replicas (run after scrub with -s) |
| [tablestats](tablestats.md) | Check table health |
