---
title: "Cassandra Cleanup Operations"
description: "Run nodetool cleanup after adding nodes. Reclaim disk space from obsolete data."
meta:
  - name: keywords
    content: "Cassandra cleanup, nodetool cleanup, reclaim disk space, post-bootstrap"
search:
  boost: 3
---

# Cleanup Operations

Cleanup removes data that a node no longer owns after topology changes. This operation must run on existing nodes after adding new nodes to the cluster.

---

## When Cleanup is Required

| Operation | Cleanup Required | Nodes to Clean |
|-----------|------------------|----------------|
| Add node (bootstrap) | **Yes** | All existing nodes |
| Decommission | No | None |
| Remove node | No | None |
| Replace node | No | None |
| Rebuild | No | None |

### Why Cleanup is Necessary

When a new node joins:

1. Existing nodes stream data to the new node
2. The new node now owns some token ranges
3. **Original nodes retain copies of data they streamed**
4. This data is now redundant—the new node is the owner

Without cleanup:

- Disk usage remains elevated on original nodes
- Extra data consumes backup storage
- Compaction processes unnecessary data

---

## Behavioral Contract

### Guarantees

- Only data outside the node's current token ranges is removed
- Data owned by the node is never deleted
- Operation is resumable if interrupted
- Does not affect cluster availability

### Operation Characteristics

| Aspect | Behavior |
|--------|----------|
| Blocking | Yes, runs synchronously |
| I/O impact | High—reads and rewrites SSTables |
| Duration | Proportional to data volume |
| Restartability | Safe to restart if interrupted |

### Failure Semantics

| Scenario | Outcome | Recovery |
|----------|---------|----------|
| Cleanup completes | Obsolete data removed | None required |
| Cleanup interrupted | Partial cleanup | Re-run cleanup |
| Disk fills during cleanup | Operation fails | Free space, re-run |
| Node restarts during cleanup | Cleanup aborted | Re-run cleanup |

---

## Prerequisites

Before running cleanup:

| Requirement | Verification |
|-------------|--------------|
| New nodes must show `UN` status | `nodetool status` |
| Bootstrap must be complete | No nodes in `UJ` state |
| Sufficient disk space for compaction | > 20% free recommended |
| No repairs running | `nodetool netstats` |

!!! warning "Timing Matters"
    Run cleanup **after** all new nodes have completed bootstrap. Running cleanup before bootstrap completes may remove data still being streamed.

---

## Procedure

### Basic Cleanup

Run on each existing node (not the new nodes):

```bash
# Full cleanup (all keyspaces)
nodetool cleanup
```

### Targeted Cleanup

Clean specific keyspaces:

```bash
# Single keyspace
nodetool cleanup my_keyspace

# Multiple keyspaces
nodetool cleanup keyspace1 keyspace2
```

Clean specific tables:

```bash
# Single table
nodetool cleanup my_keyspace my_table
```

### Sequential Execution

Run cleanup one node at a time to limit cluster-wide I/O impact:

```bash
# Node 1
ssh node1 "nodetool cleanup"
# Wait for completion

# Node 2
ssh node2 "nodetool cleanup"
# Wait for completion

# Continue for all original nodes...
```

### Parallel Execution (Advanced)

In large clusters with sufficient I/O capacity:

```bash
# Run on multiple nodes simultaneously
# Limit to one per rack to avoid overwhelming storage
parallel-ssh -h nodes_rack1.txt "nodetool cleanup"
# Wait
parallel-ssh -h nodes_rack2.txt "nodetool cleanup"
```

!!! warning "Parallel Cleanup Impact"
    Parallel cleanup increases cluster-wide I/O load. Monitor latency and throughput during execution.

---

## Monitoring Cleanup

### Progress Tracking

```bash
# Active compaction tasks (cleanup appears as compaction)
nodetool compactionstats

# Example output during cleanup:
# pending tasks: 3
# compaction type  keyspace  table  completed  total   unit  progress
# Cleanup          users     data   52428800   104857600  bytes  50.00%
```

### Completion Verification

```bash
# No cleanup tasks pending
nodetool compactionstats | grep -i cleanup

# Disk usage should decrease
df -h /var/lib/cassandra

# Compare before/after per node
nodetool status
```

### Log Monitoring

```bash
# Watch cleanup progress in logs
tail -f /var/log/cassandra/system.log | grep -i cleanup
```

---

## Performance Tuning

### Limit Concurrent Compactions

Reduce cleanup impact on client operations:

```bash
# Reduce concurrent compactors temporarily
nodetool setcompactionthroughput 32  # MB/s (default varies)

# After cleanup
nodetool setcompactionthroughput 0  # Reset to unlimited
```

### Schedule During Low Traffic

Cleanup is I/O intensive. Schedule during:

- Off-peak hours
- Maintenance windows
- Low-traffic periods

### Disk Space Management

Cleanup may temporarily increase disk usage during SSTable rewriting:

```bash
# Verify sufficient space before cleanup
df -h /var/lib/cassandra

# Rule: Need ~20% free space for compaction overhead
```

---

## Estimating Duration

Cleanup duration depends on:

- Data volume on the node
- I/O throughput
- Percentage of data that moved to new nodes

### Approximate Times

| Data per Node | Cleanup Duration |
|---------------|------------------|
| 100 GB | 30 min - 1 hour |
| 500 GB | 2-4 hours |
| 1 TB | 4-8 hours |
| 2 TB | 8-16 hours |

### Estimation Formula

```
Duration ≈ (Node data volume × Fraction moved) / I/O throughput

Example:
- Node has 500 GB
- Added 1 node to 4-node cluster (25% data moved)
- I/O throughput: 100 MB/s

Duration ≈ (500 GB × 0.25) / 100 MB/s = 125 GB / 100 MB/s ≈ 21 minutes
```

Actual times are typically 2-4x this estimate due to overhead.

---

## Troubleshooting

### Cleanup Slow

**Symptoms:** Cleanup takes much longer than expected

**Causes:**

| Cause | Solution |
|-------|----------|
| Disk I/O saturated | Reduce `compaction_throughput_mb_per_sec` |
| Many small SSTables | Run major compaction first |
| Competing operations | Wait for repairs/streaming to complete |

```bash
# Check I/O utilization
iostat -x 5

# Check competing tasks
nodetool compactionstats
```

### Cleanup Fails with Disk Full

**Symptoms:** Cleanup aborts with "No space left on device"

**Solution:**

```bash
# 1. Free disk space
#    - Delete old snapshots
nodetool clearsnapshot

#    - Remove old logs
sudo journalctl --vacuum-time=7d

# 2. Retry cleanup on specific keyspace
nodetool cleanup smallest_keyspace

# 3. Continue with larger keyspaces as space frees
```

### Cleanup Never Completes

**Symptoms:** Cleanup runs indefinitely

**Causes:**

- Continuous new data (cleanup processes existing SSTables)
- Very large SSTables

**Solution:**

```bash
# Run on specific tables
nodetool cleanup keyspace table

# If still slow, consider off-peak window
```

---

## Skipping Cleanup (Not Recommended)

Cleanup may be deferred in specific scenarios:

| Scenario | Consideration |
|----------|---------------|
| Emergency scale-up | Defer cleanup to next maintenance window |
| Time-critical operations | Complete urgent work first |
| Limited maintenance window | Partial cleanup (critical keyspaces first) |

**Risks of skipping cleanup:**

- Elevated disk usage (10-30% higher than necessary)
- Backup size inflation
- Wasted I/O on obsolete data

**Mitigation if skipped:**

- Schedule cleanup within 1-2 weeks
- Monitor disk usage closely
- Prioritize cleanup before next topology change

---

## Related Documentation

- **[Cluster Management Overview](index.md)** - Operation context
- **[Adding Nodes](adding-nodes.md)** - When cleanup is needed
- **[Scaling Operations](scaling.md)** - Multi-node additions
- **[Compaction](../../architecture/storage-engine/compaction/index.md)** - Cleanup internals
