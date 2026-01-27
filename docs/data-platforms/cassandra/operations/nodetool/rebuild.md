---
title: "nodetool rebuild"
description: "Rebuild a Cassandra node by streaming data from other nodes using nodetool rebuild."
meta:
  - name: keywords
    content: "nodetool rebuild, rebuild node, data streaming, Cassandra recovery"
---

# nodetool rebuild

Rebuilds data on a node by streaming from other datacenters, used when adding nodes to a new datacenter.

---

## Synopsis

```bash
nodetool [connection_options] rebuild [options] [source_datacenter]
```

## Description

`nodetool rebuild` streams all data that belongs to this node from another datacenter. This is used when:

- Adding nodes to a new datacenter
- Recovering a node without using bootstrap
- Repopulating a datacenter after total loss

Unlike bootstrap, rebuild does not require the node to be in JOINING state and can be run on a node that's already part of the ring.

!!! warning "Rebuild Streams from One Replica Only"
    The `rebuild` command streams data from a single replica for each token range, not from all replicas. This means:

    - Data may be inconsistent if the source replica was not fully up-to-date
    - Deleted data (tombstones) that only existed on other replicas will not be streamed
    - The rebuilt node may have stale or missing data

    **Always run `nodetool repair` after rebuild completes** to ensure full consistency with all replicas. The recommended workflow is:

    1. Run `rebuild` to quickly populate the node with data
    2. Run `repair` to synchronize with all replicas and resolve inconsistencies

    This two-step approach is faster than repair alone for large datasets, as rebuild streams entire SSTables while repair performs merkle tree comparisons.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `source_datacenter` | Datacenter to stream data from. If omitted, streams from all DCs |

---

## Options

| Option | Description |
|--------|-------------|
| `-ks, --keyspace` | Specific keyspace to rebuild |
| `-ts, --tokens` | Specific token ranges to rebuild |
| `-s, --sources` | Specific source nodes to stream from |
| `--exclude-local-dc` | Exclude sources from the local datacenter |

---

## When to Use

### Adding New Datacenter

When expanding to a new datacenter:

```bash
# Step 1: Configure nodes in new DC
# Step 2: Update keyspace RF to include new DC
ALTER KEYSPACE my_keyspace WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3,
    'dc2': 3  -- New DC
};

# Step 3: On each node in new DC, rebuild from existing DC
nodetool rebuild dc1
```

### Node Recovery Without Bootstrap

If a node lost data but is still in the ring:

```bash
nodetool rebuild
```

!!! warning "Not a Substitute for Repair"
    Rebuild streams data from other DCs. For single-DC clusters or to sync from same-DC replicas, use `nodetool repair` instead.

### After Datacenter Recovery

After recovering all nodes in a datacenter that was completely down:

```bash
# On each recovered node
nodetool rebuild <source_dc>
```

---

## When NOT to Use

### Single Datacenter Clusters

!!! info "Single-DC Considerations"
    By default, `rebuild` can stream from any datacenter including the local one. However, for single-DC clusters where rebuild would stream from the same replicas as repair, using `nodetool repair` is typically more appropriate:

    ```bash
    # Use repair for single-DC consistency
    nodetool repair -pr
    ```

    Use `--exclude-local-dc` if sources from the local datacenter should not be used.

### Normal Bootstrap Scenarios

When adding nodes to an existing DC, use bootstrap (normal node startup) instead:

```bash
# Just start the node - bootstrap happens automatically
sudo systemctl start cassandra
```

### While Node is Bootstrapping

Don't run rebuild on a node that's currently bootstrapping.

---

## Rebuild Process

1. New DC node calculates token ranges to receive
2. New DC node requests data from Source DC nodes
3. Source DC nodes stream SSTables to new DC node
4. Once all data is received, new DC node resumes normal operations

!!! info "Rebuild Behavior"
    The node streams data for ALL token ranges it owns from the source datacenter.

---

## Examples

### Rebuild from Specific Datacenter

```bash
nodetool rebuild dc1
```

Streams all data this node should own from dc1.

### Rebuild Specific Keyspace

```bash
nodetool rebuild -ks my_keyspace dc1
```

### Rebuild from All DCs

```bash
nodetool rebuild
```

Streams from all available datacenters.

### Monitor Progress

```bash
# Watch streaming progress
nodetool netstats
```

---

## Multi-DC Expansion Workflow

### Complete Process

```bash
# 1. Add nodes to new DC (don't start Cassandra yet)

# 2. Configure cassandra.yaml on new nodes:
#    - Same cluster_name
#    - Different dc/rack in GossipingPropertyFileSnitch

# 3. Start first node in new DC
sudo systemctl start cassandra

# 4. Update keyspace replication
ALTER KEYSPACE my_keyspace WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3,
    'dc2': 3
};

# 5. Rebuild on first node
nodetool rebuild dc1

# 6. Start remaining nodes in new DC one at a time
# 7. Run rebuild on each after it joins
```

### Verification

```bash
# Check node status
nodetool status

# Verify data
nodetool tablestats my_keyspace | grep "Space used"

# Run repair to ensure consistency
nodetool repair -pr
```

---

## Monitoring Rebuild

### During Rebuild

```bash
# Streaming progress
nodetool netstats

# Thread pool activity
nodetool tpstats | grep -i stream
```

### Estimated Duration

| Data Size | Network | Approximate Time |
|-----------|---------|------------------|
| 100 GB | 1 Gbps | 15-30 minutes |
| 500 GB | 1 Gbps | 1-2 hours |
| 1 TB | 1 Gbps | 3-5 hours |
| 1 TB | 10 Gbps | 30-60 minutes |

### Logs

```bash
tail -f /var/log/cassandra/system.log | grep -i rebuild
```

---

## Common Issues

### "No such datacenter"

```
ERROR: No such datacenter: dc2
```

The specified datacenter doesn't exist:

```bash
# Check available DCs
nodetool status
```

### Rebuild Stuck

If rebuild doesn't progress:

1. Check streaming:
   ```bash
   nodetool netstats
   ```

2. Check source nodes are healthy:
   ```bash
   ssh <source_node> "nodetool status"
   ```

3. Check network connectivity between DCs

4. Check throughput settings:
   ```bash
   nodetool getstreamthroughput
   nodetool getinterdcstreamthroughput
   ```

### Insufficient Disk Space

Rebuild requires space for incoming data:

```bash
# Check disk space
df -h /var/lib/cassandra

# May need to clear old data or add storage
```

### Rebuild Fails Midway

If rebuild fails partway through:

1. Check logs for error cause
2. Fix the issue
3. Restart rebuild (it will re-stream needed data)

---

## Rebuild vs. Other Operations

| Operation | Use Case |
|-----------|----------|
| `rebuild` | Stream from other DCs to populate data |
| `repair` | Sync data between replicas |
| `bootstrap` | New node joining cluster for first time |
| `removenode` | Remove dead node from cluster |

### Bootstrap vs. Rebuild

| Aspect | Bootstrap | Rebuild |
|--------|-----------|---------|
| When | New node joining | Existing node needs data |
| Auto-trigger | On first start | Manual command |
| State | JOINING | NORMAL |
| Source | Same DC (primary) | Other DCs |

---

## Performance Considerations

### Throttling

Control rebuild speed:

```bash
# Check current settings
nodetool getstreamthroughput
nodetool getinterdcstreamthroughput

# Increase for faster rebuild
nodetool setstreamthroughput 400
nodetool setinterdcstreamthroughput 100
```

### Impact on Source DC

!!! warning "Source DC Load"
    Rebuild reads from source DC nodes, impacting their performance:

    - Run during off-peak hours
    - Consider throttling
    - Monitor source DC latencies

---

## Best Practices

!!! tip "Rebuild Guidelines"
    1. **Plan for duration** - Large datasets take hours
    2. **Off-peak timing** - Reduce impact on production
    3. **One node at a time** - Minimize cluster impact
    4. **Monitor progress** - Watch netstats continuously
    5. **Verify afterward** - Check tablestats and run repair
    6. **Consider throttling** - Balance speed vs. impact

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [repair](repair.md) | Sync replicas within/across DCs |
| [netstats](netstats.md) | Monitor streaming progress |
| [status](status.md) | Check node/DC status |
| [setstreamthroughput](setstreamthroughput.md) | Control streaming speed |