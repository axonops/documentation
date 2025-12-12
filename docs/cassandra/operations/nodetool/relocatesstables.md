# nodetool relocatesstables

Relocates SSTables to the correct disk based on the configured disk allocation strategy.

---

## Synopsis

```bash
nodetool [connection_options] relocatesstables [--jobs <jobs>] <keyspace> [tables...]
```

---

## Description

`nodetool relocatesstables` moves SSTables to their correct disk location according to Cassandra's disk allocation strategy. When Cassandra is configured with multiple data directories (JBOD - Just a Bunch of Disks), it distributes SSTables across these disks. Over time, SSTables can end up on "wrong" disks due to compaction, streaming, or configuration changes. This command corrects those misplacements.

!!! info "Multi-Disk Configuration Required"
    This command is only relevant when Cassandra is configured with **multiple data directories** in `cassandra.yaml`. With a single data directory, this command has no effect.

---

## Why Multiple Data Directories?

Before understanding `relocatesstables`, it helps to understand why Cassandra uses multiple data directories:

### JBOD (Just a Bunch of Disks) Architecture

```yaml
# cassandra.yaml - Multiple data directories
data_file_directories:
    - /mnt/disk1/cassandra/data
    - /mnt/disk2/cassandra/data
    - /mnt/disk3/cassandra/data
    - /mnt/disk4/cassandra/data
```

**Benefits of JBOD:**

| Benefit | Description |
|---------|-------------|
| Cost efficiency | No RAID overhead, use raw disk capacity |
| Parallel I/O | Multiple disks = more throughput |
| Failure isolation | One disk failure affects only some SSTables |
| Scalability | Easy to add more disks |

### Disk Allocation Strategies

Cassandra decides which disk to use for new SSTables based on the configured strategy:

```yaml
# cassandra.yaml
disk_access_mode: auto  # or mmap, mmap_index_only, standard
```

**How Cassandra places SSTables:**

1. **By available space** - Prefers disks with more free space
2. **By table** - Tries to keep a table's SSTables together
3. **Round-robin** - Distributes evenly when space is similar

---

## When SSTables End Up on "Wrong" Disks

Several scenarios cause SSTables to be on incorrect disks:

### Scenario 1: After Adding New Disks

When new disks are added to `data_file_directories`:

```
Before: 2 disks (disk1, disk2) - all SSTables here
After:  4 disks (disk1, disk2, disk3, disk4) - new disks empty

Problem: Unbalanced I/O - old disks overloaded, new disks idle
```

### Scenario 2: After Disk Replacement

When a failed disk is replaced:

```
Before: disk1 (100 SSTables), disk2 (100 SSTables), disk3 (100 SSTables)
Event:  disk2 fails, replaced with new disk2
After:  disk1 (100), disk2 (0 - empty!), disk3 (100)

Problem: New disk2 gets no read traffic, wasted capacity
```

### Scenario 3: After Compaction Anomalies

Compaction can create large SSTables on one disk when source SSTables were on multiple disks:

```
Before Compaction:
  disk1: sstable_a (10GB), sstable_b (10GB)
  disk2: sstable_c (10GB)

After Compaction:
  disk1: sstable_merged (30GB)  # All ended up on one disk!
  disk2: (empty for this table)
```

### Scenario 4: After Streaming/Repair

Streamed data during repair or bootstrap may land on whatever disk has space:

```
After heavy streaming:
  disk1: 40% used
  disk2: 95% used  # Received most streamed data
  disk3: 45% used
```

### Scenario 5: After Configuration Changes

Changing `data_file_directories` order or disk allocation settings:

```yaml
# Before
data_file_directories:
    - /mnt/disk1/data  # Table A SSTables here
    - /mnt/disk2/data  # Table B SSTables here

# After (order changed)
data_file_directories:
    - /mnt/disk2/data  # Cassandra now expects Table A here
    - /mnt/disk1/data  # Cassandra now expects Table B here
```

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | Target keyspace name (required) |
| `tables` | Optional: specific table names. If omitted, relocates all tables in the keyspace |

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--jobs`, `-j` | Number of parallel relocation jobs | 0 (sequential) |

---

## What Happens During Relocation

### Process Overview

```
1. Cassandra identifies "misplaced" SSTables
   └── Compares current disk to expected disk per allocation strategy

2. For each misplaced SSTable:
   └── Copy SSTable files to correct disk
   └── Update metadata to point to new location
   └── Delete old SSTable files

3. Operation completes when all SSTables are correctly placed
```

### Files Moved Per SSTable

Each SSTable consists of multiple files that are moved together:

```
my_table-abc123-Data.db        # Actual data
my_table-abc123-Index.db       # Partition index
my_table-abc123-Filter.db      # Bloom filter
my_table-abc123-Statistics.db  # SSTable metadata
my_table-abc123-Summary.db     # Index summary
my_table-abc123-TOC.txt        # List of components
# ... and others depending on version
```

---

## Examples

### Relocate All Tables in Keyspace

```bash
# Move all SSTables in my_keyspace to correct disks
nodetool relocatesstables my_keyspace
```

### Relocate Specific Table

```bash
# Move only the users table
nodetool relocatesstables my_keyspace users
```

### Relocate Multiple Tables

```bash
# Move specific tables
nodetool relocatesstables my_keyspace users orders products
```

### Parallel Relocation (Faster)

```bash
# Use 4 parallel jobs for faster relocation
nodetool relocatesstables --jobs 4 my_keyspace

# Maximum parallelism (use with caution)
nodetool relocatesstables --jobs 8 my_keyspace large_table
```

### Relocate All Keyspaces

```bash
#!/bin/bash
# relocate_all.sh - Relocate SSTables for all user keyspaces

for ks in $(nodetool tablestats 2>/dev/null | grep "Keyspace :" | awk '{print $3}' | grep -v "^system"); do
    echo "Relocating keyspace: $ks"
    nodetool relocatesstables $ks
done
```

---

## Real-World Scenarios

### Scenario A: Adding Storage Capacity

**Situation:** Cluster is running low on disk space. Added two new disks to each node.

```bash
# 1. Stop Cassandra
sudo systemctl stop cassandra

# 2. Update cassandra.yaml with new data directories
# data_file_directories:
#     - /mnt/disk1/cassandra/data
#     - /mnt/disk2/cassandra/data
#     - /mnt/disk3/cassandra/data  # NEW
#     - /mnt/disk4/cassandra/data  # NEW

# 3. Create directories with correct ownership
sudo mkdir -p /mnt/disk3/cassandra/data /mnt/disk4/cassandra/data
sudo chown -R cassandra:cassandra /mnt/disk3/cassandra /mnt/disk4/cassandra

# 4. Start Cassandra
sudo systemctl start cassandra

# 5. Wait for node to be fully up
sleep 60

# 6. Relocate SSTables to distribute across all disks
nodetool relocatesstables --jobs 2 my_keyspace

# 7. Verify distribution
du -sh /mnt/disk*/cassandra/data/my_keyspace/
```

**Expected result:**

```
Before relocation:
  /mnt/disk1: 450GB
  /mnt/disk2: 480GB
  /mnt/disk3: 0GB (new)
  /mnt/disk4: 0GB (new)

After relocation:
  /mnt/disk1: 230GB
  /mnt/disk2: 240GB
  /mnt/disk3: 225GB
  /mnt/disk4: 235GB
```

### Scenario B: Disk Failure Recovery

**Situation:** disk2 failed and was replaced. Data was rebuilt via repair but new disk has less data.

```bash
# After repair completes, check disk usage
df -h /mnt/disk*/cassandra

# Output shows imbalance:
# /mnt/disk1: 85% used
# /mnt/disk2: 20% used (new disk)
# /mnt/disk3: 82% used

# Relocate to rebalance
nodetool relocatesstables --jobs 2 my_keyspace

# Monitor progress
watch 'df -h /mnt/disk*/cassandra'
```

### Scenario C: Hot Disk Mitigation

**Situation:** One disk is experiencing high I/O because too many SSTables for hot tables ended up there.

```bash
# Check which disk has the hot table's SSTables
find /mnt/disk*/cassandra/data/my_keyspace/hot_table-* -name "*Data.db" | \
    xargs -I {} dirname {} | sort | uniq -c

# Output:
#   45 /mnt/disk1/cassandra/data/my_keyspace/hot_table-abc123
#    5 /mnt/disk2/cassandra/data/my_keyspace/hot_table-abc123
#    8 /mnt/disk3/cassandra/data/my_keyspace/hot_table-abc123

# Disk1 has too many - relocate to distribute
nodetool relocatesstables my_keyspace hot_table
```

### Scenario D: Post-Upgrade Cleanup

**Situation:** After Cassandra upgrade, SSTable locations may not match new allocation strategy.

```bash
# After upgrading Cassandra version
# Run relocate to ensure SSTables are where the new version expects them

nodetool upgradesstables my_keyspace
nodetool relocatesstables my_keyspace
```

---

## Impact Assessment

### Resource Usage

| Resource | Impact | Notes |
|----------|--------|-------|
| Disk I/O | **HIGH** | Reads from source disk, writes to target disk |
| CPU | Low | Minimal processing, mostly I/O |
| Memory | Low | Buffered I/O |
| Network | None | Local operation only |
| Disk Space | Temporary 2x | Needs space for copy before delete |

### Impact on Operations

| Operation | Impact |
|-----------|--------|
| Reads | Minimal - SSTables remain readable during move |
| Writes | Minimal - New writes go to appropriate disk |
| Compaction | May compete for I/O |
| Streaming | May compete for I/O |

!!! warning "Temporary Disk Space"
    Relocation copies files before deleting originals. Ensure sufficient free space on target disks before running. As a rule of thumb, need at least 1 SSTable's worth of free space.

---

## Monitoring Progress

### Watch Disk Usage Change

```bash
# Monitor disk usage during relocation
watch -n 5 'df -h /mnt/disk*/cassandra/data'
```

### Check Relocation Activity

```bash
# View active compaction/relocation tasks
nodetool compactionstats

# May show as "Relocate sstables" task type
```

### Log File Monitoring

```bash
# Watch for relocation messages
tail -f /var/log/cassandra/system.log | grep -i "relocat"
```

### Verify Distribution After

```bash
#!/bin/bash
# check_sstable_distribution.sh

KEYSPACE="$1"
TABLE="$2"

echo "=== SSTable Distribution for $KEYSPACE.$TABLE ==="

for dir in /mnt/disk*/cassandra/data; do
    count=$(find "$dir/$KEYSPACE/$TABLE-"* -name "*Data.db" 2>/dev/null | wc -l)
    size=$(du -sh "$dir/$KEYSPACE/$TABLE-"* 2>/dev/null | tail -1 | awk '{print $1}')
    echo "$(dirname $dir | xargs basename): $count SSTables, ${size:-0} total"
done
```

---

## Pre-Relocation Checklist

```bash
#!/bin/bash
# pre_relocate_check.sh

KEYSPACE="$1"

echo "=== Pre-Relocation Safety Check ==="

# 1. Check disk space on all data directories
echo ""
echo "1. Disk space (need room for temporary copies):"
df -h /mnt/disk*/cassandra/data

# 2. Check current SSTable distribution
echo ""
echo "2. Current SSTable distribution:"
for dir in /mnt/disk*/cassandra/data; do
    disk=$(dirname $dir | xargs basename)
    count=$(find "$dir/$KEYSPACE" -name "*Data.db" 2>/dev/null | wc -l)
    echo "  $disk: $count SSTables"
done

# 3. Check for running compactions
echo ""
echo "3. Active compactions (avoid running simultaneously):"
nodetool compactionstats | head -10

# 4. Check cluster health
echo ""
echo "4. Cluster status:"
nodetool status | grep -E "^UN|^DN"

echo ""
echo "=== Review above before proceeding ==="
```

---

## Best Practices

!!! tip "Relocation Guidelines"

    1. **Check disk space first** - Ensure target disks have sufficient free space
    2. **Run during low-traffic periods** - Relocation generates I/O
    3. **Use --jobs carefully** - Higher parallelism = more I/O load
    4. **Verify after completion** - Check SSTable distribution is balanced
    5. **One node at a time** - In production, relocate on nodes sequentially
    6. **Monitor throughout** - Watch disk I/O and space usage

!!! warning "Important Considerations"

    - **Don't change data_file_directories while relocating** - Can cause confusion
    - **Avoid during heavy operations** - Don't run with repair, major compaction
    - **Test in staging first** - Understand timing and impact
    - **Have disk space buffer** - Need temporary space for file copies

!!! info "When Relocation May Not Help"

    - **Single data directory** - Command has no effect
    - **Evenly distributed already** - May just shuffle without benefit
    - **Different table sizes** - Large tables may still dominate one disk

---

## Troubleshooting

### Relocation Not Moving Files

```bash
# Check if SSTables are actually misplaced
nodetool tablestats my_keyspace.my_table | grep -i "sstable"

# Verify data directories are configured
grep "data_file_directories" /etc/cassandra/cassandra.yaml -A 10
```

### Running Out of Disk Space

```bash
# If relocation fails due to space
# 1. Check which disk is full
df -h /mnt/disk*/cassandra

# 2. Run compaction to reduce SSTable count first
nodetool compact my_keyspace my_table

# 3. Retry relocation
nodetool relocatesstables my_keyspace my_table
```

### Relocation Taking Too Long

```bash
# Check progress
nodetool compactionstats

# If I/O bound, reduce parallelism
# Restart with --jobs 1 (sequential)
nodetool relocatesstables --jobs 1 my_keyspace

# Or pause and resume during maintenance window
```

### Imbalance After Relocation

```bash
# If still imbalanced, may need to run compaction first
nodetool compact my_keyspace

# Then relocate again
nodetool relocatesstables my_keyspace

# Some imbalance is normal due to different table sizes
```

---

## Configuration Reference

### cassandra.yaml Settings

```yaml
# Multiple data directories (required for relocatesstables)
data_file_directories:
    - /mnt/disk1/cassandra/data
    - /mnt/disk2/cassandra/data
    - /mnt/disk3/cassandra/data

# Disk failure policy (affects JBOD behavior)
disk_failure_policy: stop  # or ignore, stop_paranoid, best_effort, die

# Commit log separate from data (recommended)
commitlog_directory: /mnt/ssd/cassandra/commitlog
```

### Disk Failure Policies

| Policy | Behavior |
|--------|----------|
| `stop` | Stop gossip and client transports, leaving node in cluster but unavailable |
| `die` | Shut down Cassandra completely |
| `ignore` | Disable failed disk, continue with remaining disks |
| `best_effort` | Like ignore, but log errors |
| `stop_paranoid` | Stop even for corrupt SSTables |

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [datapaths](datapaths.md) | View configured data directories |
| [tablestats](tablestats.md) | View table statistics including SSTable info |
| [compact](compact.md) | May help before relocation |
| [compactionstats](compactionstats.md) | Monitor relocation progress |
| [info](info.md) | View node information including data directories |
