# nodetool rebuild_index

Rebuilds secondary indexes for a table.

---

## Synopsis

```bash
nodetool [connection_options] rebuild_index <keyspace> <table> [index_name...]
```

---

## Description

`nodetool rebuild_index` reconstructs one or more secondary indexes on a table by scanning all data in the base table and regenerating the index entries. This operation is necessary when indexes become corrupted, out of sync with the base data, or after certain recovery scenarios.

!!! danger "Critical: Index Unavailability During Rebuild"

    **The index becomes unavailable for queries during the rebuild process.** Any queries that rely on the index will either:

    - Return incomplete/partial results
    - Fall back to inefficient full table scans (if `ALLOW FILTERING` is used)
    - Fail with an error

    **Plan accordingly for production systems.** See [Application Impact](#application-impact) for details.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | Target keyspace name (required) |
| `table` | Target table name (required) |
| `index_name` | Optional: specific index names to rebuild. If omitted, rebuilds ALL indexes on the table |

---

## What Happens During Index Rebuild

Understanding the rebuild process helps in planning and risk assessment:

### Step-by-Step Process

```
1. Index Marked as Building
   └── Index queries return incomplete results or fail

2. Full Table Scan Begins
   └── Every SSTable is read sequentially
   └── Each row's indexed column is extracted

3. New Index Entries Created
   └── Index SSTables are written
   └── Compaction may occur on index SSTables

4. Index Marked as Built
   └── Index queries resume normal operation
   └── New index is fully available
```

### Timeline Visualization

```
Time ────────────────────────────────────────────────────────────►

│ Normal    │◄──── Index Unavailable ────►│ Normal Operation │
│ Operation │     (Rebuild in Progress)    │   (Rebuild Done) │

             ▲                              ▲
             │                              │
        rebuild_index                  Rebuild Complete
          command                      (logged in system.log)
```

---

## Application Impact

### What Happens to Queries During Rebuild

| Query Type | Behavior During Rebuild |
|------------|------------------------|
| Query using the rebuilding index | **Returns incomplete results or fails** |
| Query using `ALLOW FILTERING` | Works but extremely slow (full scan) |
| Queries not using the index | Unaffected |
| Writes to the table | Continue normally, indexed in new index |

### Error Messages Applications May See

```
# Common error during rebuild
Unable to execute query: Index 'my_index' is not ready for use

# Or queries may silently return partial results
# (more dangerous - appears to work but data is incomplete)
```

### Application Preparation Checklist

Before running `rebuild_index` in production:

- [ ] **Notify application teams** - They need to handle index unavailability
- [ ] **Implement fallback logic** - Applications should handle missing index gracefully
- [ ] **Consider circuit breakers** - Disable features that depend on the index
- [ ] **Plan maintenance window** - If possible, rebuild during low-traffic periods
- [ ] **Estimate rebuild time** - See [Duration Estimation](#duration-estimation)

---

## Duration Estimation

Rebuild time depends on several factors:

### Factors Affecting Duration

| Factor | Impact |
|--------|--------|
| Table size (data volume) | Linear - 2x data = ~2x time |
| Number of SSTables | More SSTables = more I/O overhead |
| Disk speed | SSD vs HDD makes significant difference |
| Concurrent operations | Other compactions/repairs slow rebuild |
| Index type | SASI indexes take longer than regular 2i |

### Rough Estimation Formula

```
Estimated Time ≈ (Table Size in GB) × (1-5 minutes per GB)

Examples:
- 10 GB table, SSD: ~10-20 minutes
- 100 GB table, SSD: ~2-4 hours
- 100 GB table, HDD: ~4-8 hours
- 1 TB table: ~1-2 days
```

!!! warning "Estimates Are Approximate"
    Actual times vary significantly based on hardware, cluster load, and data characteristics. Always test in a non-production environment first.

### Checking Progress

```bash
# Watch rebuild progress (shows as "Secondary index build")
watch -n 10 'nodetool compactionstats'

# Check system log for progress
tail -f /var/log/cassandra/system.log | grep -i "index"

# Detailed progress
nodetool compactionstats | grep -A 5 "Secondary index"
```

**Sample compactionstats output during rebuild:**

```
pending tasks: 1
- Secondary index build   my_keyspace   my_table   45678901234   42%
Active compaction remaining time :   0h15m32s
```

---

## Examples

### Rebuild All Indexes on a Table

```bash
# Rebuilds every index on the table
nodetool rebuild_index my_keyspace users

# Equivalent to rebuilding: users_email_idx, users_status_idx, etc.
```

### Rebuild Specific Index

```bash
# Rebuild only the email index
nodetool rebuild_index my_keyspace users users_email_idx
```

### Rebuild Multiple Specific Indexes

```bash
# Rebuild two specific indexes
nodetool rebuild_index my_keyspace users users_email_idx users_status_idx
```

### Find Index Names First

```bash
# List indexes on a table
cqlsh -e "DESCRIBE TABLE my_keyspace.users;" | grep INDEX

# Or query schema directly
cqlsh -e "SELECT index_name FROM system_schema.indexes
          WHERE keyspace_name = 'my_keyspace' AND table_name = 'users';"
```

---

## When to Use

### Scenario 1: Index Returning Incorrect Results

**Symptoms:**

- Queries using the index return fewer results than expected
- Results don't match direct queries with `ALLOW FILTERING`
- Index appears to be missing data

```bash
# Verify index inconsistency
cqlsh -e "SELECT COUNT(*) FROM my_keyspace.users WHERE email = 'test@example.com';"
# Returns 0

cqlsh -e "SELECT COUNT(*) FROM my_keyspace.users WHERE email = 'test@example.com' ALLOW FILTERING;"
# Returns 5 (correct)

# Rebuild to fix
nodetool rebuild_index my_keyspace users users_email_idx
```

### Scenario 2: After Restoring from Backup

**Why needed:** Snapshots include index SSTables, but they may not be consistent with the restored data state.

```bash
# After restoring a table from snapshot
nodetool refresh my_keyspace users

# Rebuild all indexes to ensure consistency
nodetool rebuild_index my_keyspace users
```

### Scenario 3: After Node Replacement

**Why needed:** New node may have index entries without corresponding base data or vice versa.

```bash
# After replacing a node and streaming data
nodetool rebuild_index my_keyspace users
```

### Scenario 4: Upgrading Index Type

**Why needed:** After changing from regular secondary index to SASI or SAI.

```bash
# After altering index configuration
nodetool rebuild_index my_keyspace users new_index_name
```

### Scenario 5: Corruption Detected in Logs

**Symptoms in logs:**

```
ERROR - Corrupt index segment detected for users_email_idx
WARN  - Index users_email_idx may be inconsistent
```

```bash
# Rebuild the corrupted index
nodetool rebuild_index my_keyspace users users_email_idx
```

---

## When NOT to Use

!!! warning "Avoid These Situations"

    **Don't use rebuild_index when:**

    1. **Index is working correctly** - Rebuilding a healthy index wastes resources
    2. **During peak traffic** - Causes performance degradation and query failures
    3. **Without notifying application teams** - Will cause application errors
    4. **On very large tables without estimation** - Could take days
    5. **When simpler fixes exist** - Sometimes repair or compaction is sufficient

---

## Safe Execution Workflow

### Pre-Rebuild Checklist

```bash
#!/bin/bash
# pre_rebuild_check.sh

KEYSPACE="$1"
TABLE="$2"
INDEX="$3"

echo "=== Pre-Rebuild Safety Check ==="

# 1. Check table size
echo ""
echo "1. Table size estimation:"
nodetool tablestats $KEYSPACE.$TABLE | grep "Space used"

# 2. List indexes
echo ""
echo "2. Indexes on table:"
cqlsh -e "SELECT index_name FROM system_schema.indexes
          WHERE keyspace_name = '$KEYSPACE' AND table_name = '$TABLE';"

# 3. Check current cluster load
echo ""
echo "3. Current cluster load:"
nodetool tpstats | head -20

# 4. Check pending compactions
echo ""
echo "4. Pending compactions:"
nodetool compactionstats

# 5. Estimate time
size_bytes=$(nodetool tablestats $KEYSPACE.$TABLE 2>/dev/null | grep "Space used (live)" | awk '{print $4}')
size_gb=$((size_bytes / 1073741824))
echo ""
echo "5. Estimated rebuild time: $((size_gb * 2)) - $((size_gb * 5)) minutes"

echo ""
echo "=== Review above before proceeding ==="
echo "Command to execute: nodetool rebuild_index $KEYSPACE $TABLE $INDEX"
```

### Controlled Rebuild with Monitoring

```bash
#!/bin/bash
# safe_rebuild_index.sh

KEYSPACE="$1"
TABLE="$2"
INDEX="$3"

echo "=== Safe Index Rebuild ==="
echo "Target: $KEYSPACE.$TABLE ${INDEX:-'(all indexes)'}"
echo ""

# Confirm
read -p "This will make the index unavailable. Continue? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

# Record start time
START_TIME=$(date +%s)
echo ""
echo "Started at: $(date)"

# Start rebuild
echo ""
echo "Initiating rebuild..."
nodetool rebuild_index $KEYSPACE $TABLE $INDEX &
REBUILD_PID=$!

# Monitor progress
echo ""
echo "Monitoring progress (Ctrl+C to stop monitoring, rebuild continues)..."
while kill -0 $REBUILD_PID 2>/dev/null; do
    progress=$(nodetool compactionstats 2>/dev/null | grep -i "secondary index" | tail -1)
    if [ -n "$progress" ]; then
        echo "$(date '+%H:%M:%S') - $progress"
    else
        echo "$(date '+%H:%M:%S') - Waiting for rebuild to appear in compactionstats..."
    fi
    sleep 30
done

# Calculate duration
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
echo ""
echo "=== Rebuild Complete ==="
echo "Duration: $((DURATION / 60)) minutes $((DURATION % 60)) seconds"

# Verify index is ready
echo ""
echo "Verifying index is ready..."
# Test query (modify for your schema)
echo "Run a test query to verify index is working"
```

---

## Impact Assessment

### Resource Usage During Rebuild

| Resource | Impact Level | Notes |
|----------|--------------|-------|
| Disk I/O | **HIGH** | Full table scan reads all SSTables |
| CPU | Moderate | Index entry creation and sorting |
| Memory | Low-Moderate | Buffers for reading and writing |
| Network | None | Local operation only |
| Disk Space | Temporary increase | Old + new index until compaction |

### Impact on Other Operations

| Operation | Affected? | Details |
|-----------|-----------|---------|
| Normal reads (no index) | Minimal | May compete for I/O |
| Normal writes | Minimal | Writes continue, new data indexed |
| Compaction | Slowed | Competes for resources |
| Repair | Should avoid | Don't run simultaneously |
| Backup/Snapshot | Can proceed | But indexes may be mid-rebuild |

---

## Cluster-Wide Considerations

### Must Run on Each Node

!!! important "Node-Local Operation"
    `rebuild_index` only rebuilds indexes **on the node where it's executed**. For complete cluster-wide rebuild, run on every node.

```bash
#!/bin/bash
# rebuild_index_cluster.sh

KEYSPACE="$1"
TABLE="$2"
INDEX="$3"
DELAY_BETWEEN_NODES=300  # 5 minutes

echo "=== Cluster-Wide Index Rebuild ==="
echo "Target: $KEYSPACE.$TABLE ${INDEX:-'(all indexes)'}"

nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo ""
    echo "$(date): Starting rebuild on $node..."
    nodetool -h $node rebuild_index $KEYSPACE $TABLE $INDEX

    # Wait for completion
    while nodetool -h $node compactionstats 2>/dev/null | grep -qi "secondary index"; do
        echo "  Waiting for rebuild to complete on $node..."
        sleep 60
    done

    echo "$(date): Rebuild complete on $node"

    # Wait before next node (optional, allows cache warming)
    echo "Waiting ${DELAY_BETWEEN_NODES}s before next node..."
    sleep $DELAY_BETWEEN_NODES
done

echo ""
echo "=== Cluster-wide rebuild complete ==="
```

### Rolling vs Parallel Rebuild

| Approach | Pros | Cons |
|----------|------|------|
| **Rolling (one at a time)** | Lower cluster impact, safer | Takes longer |
| **Parallel (all at once)** | Faster total time | Higher cluster stress, all indexes unavailable |

**Recommendation:** Use rolling rebuild for production systems.

---

## Verification After Rebuild

### Confirm Rebuild Completed

```bash
# Check logs for completion message
grep -i "index build complete\|finished building" /var/log/cassandra/system.log | tail -5

# Verify no pending index builds
nodetool compactionstats | grep -i "secondary index"
# Should return empty
```

### Test Index Functionality

```bash
# Run a query that uses the index
cqlsh -e "TRACING ON; SELECT * FROM my_keyspace.users WHERE email = 'test@example.com';"

# Verify the trace shows index usage, not full scan
# Look for: "Index scan" rather than "Seq scan"
```

### Compare Results

```bash
# Query with index
cqlsh -e "SELECT COUNT(*) FROM my_keyspace.users WHERE email = 'test@example.com';"

# Query with ALLOW FILTERING (bypasses index)
cqlsh -e "SELECT COUNT(*) FROM my_keyspace.users WHERE email = 'test@example.com' ALLOW FILTERING;"

# Results should match
```

---

## Troubleshooting

### Rebuild Taking Too Long

```bash
# Check if rebuild is actually progressing
watch -n 30 'nodetool compactionstats | grep -i index'

# Check for resource contention
nodetool tpstats | grep -i blocked

# Consider pausing other operations
nodetool disableautocompaction my_keyspace my_table
# ... rebuild ...
nodetool enableautocompaction my_keyspace my_table
```

### Rebuild Appears Stuck

```bash
# Check Cassandra logs for errors
tail -100 /var/log/cassandra/system.log | grep -i "error\|exception\|index"

# Check thread pools for issues
nodetool tpstats

# If truly stuck, may need to restart (use with caution)
# The rebuild will restart from the beginning
```

### Index Still Returning Bad Results After Rebuild

```bash
# Verify rebuild completed on ALL nodes
for node in $(nodetool status | grep "^UN" | awk '{print $2}'); do
    echo "Checking $node..."
    nodetool -h $node compactionstats | grep -i "secondary index" || echo "  No active rebuilds"
done

# If already complete everywhere, may need to drop and recreate
cqlsh -e "DROP INDEX my_keyspace.users_email_idx;"
cqlsh -e "CREATE INDEX users_email_idx ON my_keyspace.users (email);"
```

### Out of Disk Space During Rebuild

```bash
# Rebuild creates new index files before removing old ones
# Need approximately 2x index size temporarily

# Check disk space
df -h /var/lib/cassandra

# If space is tight, rebuild indexes one at a time
# and run compaction between each
nodetool rebuild_index my_keyspace users idx1
nodetool compact my_keyspace users
nodetool rebuild_index my_keyspace users idx2
```

---

## Best Practices

!!! tip "Index Rebuild Guidelines"

    1. **Estimate first** - Know how long it will take before starting
    2. **Communicate** - Notify all stakeholders about index unavailability
    3. **Maintenance window** - Prefer low-traffic periods
    4. **One at a time** - Rebuild indexes sequentially, not in parallel
    5. **Monitor throughout** - Watch compactionstats and logs
    6. **Verify after** - Test queries to confirm index is working
    7. **Document** - Record when and why rebuilds were performed

!!! warning "Production Precautions"

    - **Never rebuild without planning** - Applications will see failures
    - **Test in staging first** - Understand timing and behavior
    - **Have rollback plan** - Know what to do if rebuild fails
    - **Consider alternatives** - Sometimes repair or compaction is enough
    - **Check disk space** - Need ~2x index size temporarily

!!! info "Alternative Approaches"

    Before rebuilding, consider if these alternatives might help:

    - **Run repair** - Fixes consistency issues that might affect index
    - **Run compaction** - May resolve some index inconsistencies
    - **Drop and recreate** - Sometimes faster for small tables
    - **SAI indexes** - Consider migrating to Storage Attached Indexes (Cassandra 4.0+)

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [compactionstats](compactionstats.md) | Monitor rebuild progress |
| [tablestats](tablestats.md) | Check table size before rebuild |
| [repair](repair.md) | Alternative for some consistency issues |
| [compact](compact.md) | May help with some index issues |
| [disableautocompaction](disableautocompaction.md) | Reduce resource contention |
| [enableautocompaction](enableautocompaction.md) | Re-enable after rebuild |
