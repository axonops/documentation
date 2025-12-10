# nodetool decommission

Gracefully removes the local node from the cluster by streaming its data to remaining nodes.

## Synopsis

```bash
nodetool [connection_options] decommission
```

## Description

The `decommission` command initiates a controlled removal of the current node from the cluster. The node streams all of its locally stored data to the nodes that will assume ownership of its token ranges, then removes itself from the cluster topology.

This is the recommended method for permanently removing a healthy node from the cluster while preserving data availability.

## Prerequisites

Before decommissioning a node, verify:

| Requirement | Check Command | Expected Result |
|-------------|---------------|-----------------|
| All nodes are up | `nodetool status` | All nodes show `UN` |
| No other topology operations | `nodetool netstats` | No streaming operations |
| Sufficient capacity | `nodetool status` | Remaining nodes can absorb data |
| Replication factor allows removal | Check keyspace RF | RF > 1 for availability |

## Process

### Decommission Steps

1. Node announces intention to leave the cluster
2. Token ownership is transferred to remaining nodes
3. Data is streamed to new owners
4. Node removes itself from the ring
5. Node stops accepting client connections

### Execution

```bash
# Run on the node being removed
nodetool decommission
```

The command blocks until decommission completes or fails.

## Monitoring Progress

### Check Streaming Status

```bash
# On the decommissioning node
nodetool netstats
```

**Output during decommission:**
```
Mode: DECOMMISSIONING
Streaming to: /10.0.0.2
    /var/lib/cassandra/data/my_keyspace/users-abc123
        Sending 45/123 files, 2.5 GiB / 12.5 GiB (20%)
    /var/lib/cassandra/data/my_keyspace/orders-def456
        Sending 12/45 files, 1.2 GiB / 5.3 GiB (22%)

Streaming to: /10.0.0.3
    /var/lib/cassandra/data/my_keyspace/users-abc123
        Sending 38/112 files, 3.1 GiB / 11.2 GiB (27%)
```

### Monitor from Other Nodes

```bash
# From any other node
nodetool status
```

The decommissioning node will show status `UL` (Up, Leaving).

### Continuous Monitoring

```bash
# Watch progress
watch -n 5 'nodetool netstats | head -30'
```

## Duration Estimation

Decommission time depends on:

| Factor | Impact |
|--------|--------|
| Data volume | Primary factor |
| Stream throughput | `stream_throughput_outbound_megabits_per_sec` |
| Number of receiving nodes | Parallelism of streams |
| Network bandwidth | Physical limitation |
| Disk I/O | Read speed of source node |

**Estimation formula:**
```
Time (hours) ≈ Data_Size_GB / (Stream_Throughput_MBps × 3.6)
```

For example, with 500 GiB data and 200 MBps throughput:
```
500 / (200 × 3.6) ≈ 0.7 hours
```

## Common Issues

### Decommission Hangs

**Symptoms:** Progress stops, no streaming activity.

**Investigation:**
```bash
# Check for errors
tail -f /var/log/cassandra/system.log | grep -i stream

# Check network connectivity
nodetool netstats
```

**Possible causes:**
- Network issues to receiving nodes
- Receiving node disk full
- Memory pressure on either side

### Cannot Proceed with Decommission

```
Cannot decommission: node is already leaving or missing from ring
```

**Cause:** Node is in inconsistent state.

**Resolution:**
```bash
# Check node state
nodetool netstats

# If stuck, may need to restart and retry
sudo systemctl restart cassandra
# Wait for node to be UN again
nodetool decommission
```

### Insufficient Replicas

```
Unable to decommission: replication factor exceeds number of remaining nodes
```

**Cause:** Removing this node would leave fewer nodes than the replication factor requires.

**Resolution:**
- Reduce replication factor first
- Add replacement nodes before decommissioning

## Post-Decommission

### Verify Removal

```bash
# From any remaining node
nodetool status
```

The decommissioned node should no longer appear.

### Clean Up Decommissioned Node

```bash
# On the decommissioned node (now stopped)
sudo systemctl stop cassandra
sudo systemctl disable cassandra

# Optionally remove data
sudo rm -rf /var/lib/cassandra/data/*
sudo rm -rf /var/lib/cassandra/commitlog/*
sudo rm -rf /var/lib/cassandra/saved_caches/*
```

### Run Cleanup on Remaining Nodes

After decommission, remaining nodes may have data that should have been on the removed node. Run cleanup:

```bash
# On each remaining node
nodetool cleanup
```

## Aborting Decommission

Decommission cannot be cleanly aborted once started. If interrupted:

1. The node remains in `LEAVING` state
2. Manual intervention is required
3. Contact support or follow recovery procedures

**Emergency stop (not recommended):**
```bash
# This will leave cluster in inconsistent state
sudo systemctl stop cassandra
```

## Alternative: removenode

Use `removenode` instead of `decommission` when:

| Scenario | Command |
|----------|---------|
| Node is healthy and running | `nodetool decommission` (on the node) |
| Node is dead/unreachable | `nodetool removenode` (from another node) |
| Node data already lost | `nodetool removenode` or `assassinate` |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Decommission completed successfully |
| 1 | Error occurred during decommission |

## Related Commands

- [nodetool removenode](removenode.md) - Remove dead node
- [nodetool assassinate](assassinate.md) - Force remove from gossip
- [nodetool netstats](netstats.md) - Monitor streaming
- [nodetool status](status.md) - Check cluster state
- [nodetool cleanup](cleanup.md) - Clean up after topology changes

## Version Information

Available in all Apache Cassandra versions. Streaming performance improvements were added in Cassandra 4.0.
