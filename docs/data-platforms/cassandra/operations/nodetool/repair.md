---
title: "nodetool repair"
description: "Run anti-entropy repair to synchronize data across Cassandra replicas. Essential for data consistency."
meta:
  - name: keywords
    content: "nodetool repair, Cassandra repair, anti-entropy, data consistency, Merkle tree"
search:
  boost: 3
---

# nodetool repair

Runs anti-entropy repair to synchronize data across replicas, ensuring consistency and preventing data resurrection from expired tombstones.

---

## Synopsis

```bash
nodetool [connection_options] repair [options] [--] [keyspace [table ...]]
```

## Description

`nodetool repair` compares data between replica nodes using Merkle trees and streams any differences to ensure all replicas hold identical data. Repair is essential for:

- Maintaining data consistency
- Preventing tombstone resurrection (zombie data)
- Recovering from node failures or network partitions

!!! info "Comprehensive Repair Documentation"
    For detailed repair concepts, strategies, and scheduling guidance, see:

    - **[Repair Concepts](../repair/concepts.md)** - How repair works
    - **[Repair Options Reference](../repair/options-reference.md)** - All options explained
    - **[Repair Strategies](../repair/strategies.md)** - Implementation approaches
    - **[Repair Scheduling](../repair/scheduling.md)** - Planning repair cycles

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | Keyspace to repair. Required for targeted repairs |
| `table` | Specific table(s) to repair. If omitted, repairs all tables |

---

## Key Options

| Option | Description |
|--------|-------------|
| `-pr, --partitioner-range` | Repair only primary range (recommended) |
| `--full` | Full repair instead of incremental |
| `-seq, --sequential` | Repair one node at a time |
| `--parallel` | Repair all replicas simultaneously (default in 4.0+) |
| `-dcpar, --dc-parallel` | Parallel within DC, sequential across DCs |
| `-dc, --in-dc` | Repair only within specified datacenter(s) |
| `-local, --in-local-dc` | Repair only within local datacenter |
| `-st, --start-token` | Start token for repair range |
| `-et, --end-token` | End token for repair range |
| `-j, --job-threads` | Number of repair job threads |

---

## Common Usage Patterns

### Primary Range Repair (Recommended)

```bash
nodetool repair -pr my_keyspace
```

!!! tip "Always Use -pr"
    Without `-pr`, each node repairs all ranges it holds (primary + replica), causing redundant work. With `-pr`, run repair on every node to cover all ranges exactly once.

### Full vs Incremental Repair

```bash
# Full repair (default before 4.0)
nodetool repair --full -pr my_keyspace

# Incremental repair (default in 4.0+)
nodetool repair -pr my_keyspace
```

| Type | Behavior | Use Case |
|------|----------|----------|
| Full | Repairs all data | Recovery, initial sync |
| Incremental | Repairs only unrepaired data | Regular maintenance |

### Local Datacenter Only

```bash
nodetool repair -pr -local my_keyspace
```

Repairs only with replicas in the same datacenter.

### Specific Token Range

```bash
nodetool repair -pr -st 0 -et 1000000000 my_keyspace
```

Repairs only the specified token range (subrange repair).

---

## When to Use

### Routine Maintenance

!!! warning "gc_grace_seconds Constraint"
    Repair must complete on all nodes within `gc_grace_seconds` (default 10 days) to prevent tombstone resurrection.

    ```bash
    # Run on each node
    nodetool repair -pr my_keyspace
    ```

### After Node Recovery

After a node was down for extended time:

```bash
nodetool repair -pr my_keyspace
```

### After Network Partition

If nodes were isolated:

```bash
nodetool repair -pr my_keyspace
```

### Before Major Version Upgrade

Ensure consistency before upgrading:

```bash
nodetool repair --full my_keyspace
```

---

## When NOT to Use

!!! danger "Repair Considerations"
    Avoid repair:

    - **During high traffic** - Significant resource impact
    - **While streaming** - Interferes with bootstrap/decommission
    - **With down nodes** - Repair will fail or skip ranges
    - **Immediately after bulk load** - Wait for compaction

---

## Impact Analysis

### Resource Usage

| Resource | Impact |
|----------|--------|
| Network | High - streams data between nodes |
| Disk I/O | High - reads SSTables, writes repairs |
| CPU | Moderate - Merkle tree calculation |
| Memory | Merkle trees require heap space |

### Performance Impact

During repair, the following operations impact cluster performance:

| Operation | Description |
|-----------|-------------|
| Merkle Tree Build | Computes hash trees for data comparison |
| Data Comparison | Compares trees between replicas |
| Data Streaming | Streams differing data between nodes |

**Expected impact during repair:**

| Metric | Impact |
|--------|--------|
| Read latency | +10-30% |
| Write latency | +5-15% |
| Network utilization | +20-50% |

---

## Monitoring Repair

### Check Active Repairs

```bash
nodetool repair_admin list
```

Shows running repair sessions.

### Monitor Progress

```bash
nodetool netstats
```

Shows streaming activity from repair.

### Check Repair History

```bash
nodetool repair_admin list --all
```

Shows completed and failed repairs.

### Abort Repair

```bash
nodetool repair_admin cancel <repair_id>
```

!!! warning "Canceling Repair"
    Canceled repairs leave data partially synchronized. Restart repair to complete synchronization.

---

## Examples

### Standard Maintenance Repair

```bash
# Run on each node sequentially
nodetool repair -pr my_keyspace
```

### Repair Specific Table

```bash
nodetool repair -pr my_keyspace users
```

### Parallel Repair (Faster)

```bash
nodetool repair -pr --parallel my_keyspace
```

### Multi-DC Repair

```bash
# Repair with all DCs
nodetool repair -pr my_keyspace

# Repair specific DCs only
nodetool repair -pr -dc dc1 -dc dc2 my_keyspace
```

### Verbose Output

```bash
nodetool repair -pr --trace my_keyspace
```

---

## Common Issues

### Repair Fails with Timeout

```
ERROR: Repair failed with error: Repair job timed out
```

Solutions:
- Reduce repair scope (single table)
- Use subrange repair
- Increase `streaming_socket_timeout_in_ms`

### Repair Session Already Running

```
ERROR: Repair session already in progress
```

Check and wait for existing repair:

```bash
nodetool repair_admin list
```

### Out of Memory

```
ERROR: java.lang.OutOfMemoryError: Java heap space
```

Merkle trees consume heap. Solutions:
- Reduce repair parallelism
- Increase heap size
- Use subrange repair

### Inconsistent Data After Repair

If data still appears inconsistent:
1. Verify repair completed successfully
2. Check all nodes were repaired
3. Run `nodetool repair --full` for complete sync

---

## Best Practices

!!! tip "Repair Guidelines"
    1. **Use -pr flag** - Prevents redundant work
    2. **Complete within gc_grace_seconds** - Prevent zombies
    3. **One node at a time** - For sequential strategy
    4. **Off-peak hours** - Minimize production impact
    5. **Monitor progress** - Watch for failures
    6. **Automate** - Use AxonOps for scheduling

### Repair Schedule Example

| Cluster Size | Strategy | Frequency |
|--------------|----------|-----------|
| 3-6 nodes | Sequential | Weekly |
| 6-20 nodes | Parallel | Every 3-5 days |
| 20-50 nodes | DC-parallel | Every 2-3 days |
| 50+ nodes | Continuous (AxonOps) | Always running |

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [repair_admin](repair_admin.md) | Manage repair sessions |
| [netstats](netstats.md) | Monitor streaming |
| [status](status.md) | Check node states before repair |
| [scrub](scrub.md) | Fix local SSTable corruption |

## Related Documentation

- **[Repair Concepts](../repair/concepts.md)**
- **[Repair Options Reference](../repair/options-reference.md)**
- **[Repair Strategies](../repair/strategies.md)**
- **[Repair Scheduling](../repair/scheduling.md)**
