# nodetool cleanup

Removes data that no longer belongs to this node after a topology change, such as adding new nodes to the cluster.

---

## Synopsis

```bash
nodetool [connection_options] cleanup [options] [--] [keyspace [table ...]]
```

## Description

`nodetool cleanup` scans SSTables and removes any data where the token is no longer owned by the local node. This is necessary after adding nodes to the cluster, as token ranges are redistributed and some data becomes redundant on existing nodes.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | Keyspace to clean up. If omitted, cleans all keyspaces |
| `table` | Specific table(s) to clean. If omitted, cleans all tables |

---

## Options

| Option | Description |
|--------|-------------|
| `-j, --jobs` | Number of concurrent cleanup jobs (default: 2) |

---

## When to Use

### After Adding Nodes

!!! tip "Required After Scaling Up"
    After adding nodes and bootstrap completes:

    ```bash
    # Run on each EXISTING node (not the new node)
    nodetool cleanup
    ```

    This reclaims disk space by removing data now owned by new nodes.

### Cleanup Workflow After Adding Nodes

| Step | Node | Action | Notes |
|------|------|--------|-------|
| 1 | New Node | Bootstrap completes | Node has streamed data for its token ranges |
| 2 | Existing Node 1 | `nodetool cleanup` | Removes data now owned by new node |
| 3 | Existing Node 2 | `nodetool cleanup` | Removes data now owned by new node |

!!! info "Sequential Execution"
    Run cleanup sequentially on each existing node (not in parallel).

### Before Decommissioning Source Cluster

When migrating data between clusters, run cleanup on the source after the target has received data.

---

## When NOT to Use

### After Removing Nodes

!!! warning "Not Needed After Node Removal"
    When nodes are **removed** (decommission or removenode), remaining nodes receive additional data—they don't have excess data to clean up.

### Before Bootstrap Completes

Never run cleanup while a new node is still bootstrapping. Wait for `nodetool status` to show the new node as `UN` (Up/Normal).

### On the New Node

The newly added node has only the data it should own—no cleanup needed.

---

## Impact Analysis

### Resource Usage

| Resource | Impact |
|----------|--------|
| Disk I/O | High - reads all SSTables |
| CPU | Moderate - token range calculations |
| Disk space | Temporary increase, then decrease |
| Duration | Proportional to data size |

### How Cleanup Works

1. Scans each SSTable
2. Checks each partition's token against current ring
3. Creates new SSTable with only locally-owned data
4. Removes old SSTable after completion

### Disk Space Requirements

!!! danger "Temporary Space Needed"
    During cleanup, both old and new SSTables exist temporarily:

    ```
    Before: 100 GB (original SSTables)
    During: Up to 200 GB (old + new being written)
    After: ~75 GB (assuming 25% of data moved to new node)
    ```

    Ensure sufficient free space before running cleanup.

---

## Examples

### Clean All Keyspaces

```bash
nodetool cleanup
```

Cleans all non-system keyspaces.

### Clean Specific Keyspace

```bash
nodetool cleanup my_keyspace
```

### Clean Specific Table

```bash
nodetool cleanup my_keyspace my_table
```

### Increase Parallelism

```bash
nodetool cleanup -j 4 my_keyspace
```

!!! warning "Parallelism Trade-offs"
    Higher parallelism speeds up cleanup but increases I/O load. On production systems, use default or lower values.

---

## Monitoring Cleanup

### Check Progress

```bash
nodetool compactionstats
```

Cleanup appears as a compaction operation in the output.

### Estimate Duration

```bash
# Check data size before cleanup
nodetool tablestats my_keyspace | grep "Space used"

# Monitor progress
watch -n 5 'nodetool compactionstats'
```

### After Cleanup

```bash
# Verify reduced data size
nodetool tablestats my_keyspace | grep "Space used"
```

---

## Operational Best Practices

### Run Sequentially Across Nodes

```bash
# Node 1
ssh node1 'nodetool cleanup'
# Wait for completion, then Node 2
ssh node2 'nodetool cleanup'
# Continue for all existing nodes
```

!!! tip "Sequential Execution"
    Running cleanup on all nodes simultaneously creates excessive I/O cluster-wide. Process nodes one at a time.

### Order of Operations After Adding Nodes

| Step | Action | Notes |
|------|--------|-------|
| 1 | Add new node | Bootstrap streams data |
| 2 | Wait for UN status | `nodetool status` |
| 3 | Run repair on new node | Ensure data consistency |
| 4 | Run cleanup on existing nodes | One at a time |

### Skip System Keyspaces

System keyspaces are cleaned automatically. Focus on user keyspaces:

```bash
nodetool cleanup my_keyspace1 my_keyspace2
```

---

## Common Issues

### Cleanup Takes Too Long

| Cause | Solution |
|-------|----------|
| Large data volume | Run during off-peak hours |
| Slow disks | Reduce `-j` parallelism |
| Heavy production load | Schedule for maintenance window |

### Disk Space Insufficient

```
ERROR: Not enough disk space for cleanup
```

Options:
1. Clean up one table at a time
2. Free disk space elsewhere
3. Add storage capacity

### Cleanup Not Removing Data

If disk usage doesn't decrease after cleanup:

1. Verify bootstrap actually completed
2. Check that cleanup ran on the correct nodes
3. Verify token ranges redistributed with `nodetool ring`

---

## Cleanup vs. Repair

| Operation | Purpose |
|-----------|---------|
| `cleanup` | Remove data not belonging to node |
| `repair` | Synchronize data across replicas |

These serve different purposes:
- Cleanup removes data from wrong location
- Repair ensures copies are consistent

After adding nodes, typically repair first (on new node), then cleanup (on existing nodes).

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [status](status.md) | Verify node states before cleanup |
| [ring](ring.md) | Check token distribution |
| [repair](repair.md) | Synchronize data after topology change |
| [compactionstats](compactionstats.md) | Monitor cleanup progress |
| [tablestats](tablestats.md) | Check data sizes |
