# nodetool cleanup

Removes data from the local node that no longer belongs to it according to the current token ring.

## Synopsis

```bash
nodetool [connection_options] cleanup [options] [keyspace [table ...]]
```

## Description

The `cleanup` command scans local SSTables and removes any partitions for which the local node is no longer responsible. This operation is essential after adding new nodes to a cluster, as the existing nodes will have data that now belongs to the new nodes.

Cleanup is a local operation that does not affect other nodes and does not require coordination.

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| keyspace | No | Keyspace to clean. If omitted, cleans all keyspaces. |
| table | No | Specific table(s) to clean within the keyspace |

## Options

| Option | Description |
|--------|-------------|
| -j, --jobs &lt;count&gt; | Number of tables to clean simultaneously (default: 1) |

## When to Run

### Required After

| Event | Reason |
|-------|--------|
| Adding new node(s) | Data redistributed; old nodes have excess data |
| Changing `num_tokens` | Token ownership changed |
| Altering keyspace replication | Replica placement changed |

### Cleanup Order

After adding nodes to a cluster:

1. Wait for the new node(s) to complete bootstrap
2. Run cleanup on **existing** nodes (not the new ones)
3. Clean one node at a time to minimize cluster impact
4. Verify disk space recovery on each node

## Examples

### Cleanup All Keyspaces

```bash
nodetool cleanup
```

### Cleanup Specific Keyspace

```bash
nodetool cleanup my_keyspace
```

### Cleanup Specific Table

```bash
nodetool cleanup my_keyspace users
```

### Parallel Cleanup (Multiple Tables)

```bash
nodetool cleanup -j 2 my_keyspace
```

## Process

### What Happens During Cleanup

1. For each SSTable in the specified scope:
   a. Read partition keys
   b. Check if local node is responsible for each partition
   c. Write new SSTable excluding non-local partitions
   d. Replace old SSTable with new one

2. Disk space is reclaimed after old SSTables are deleted

### Resource Impact

| Resource | Impact |
|----------|--------|
| Disk I/O | High - reads and writes SSTables |
| Disk space | Temporarily increases (old + new SSTables) |
| CPU | Moderate - decompression/compression |
| Network | None - local operation only |

## Monitoring Progress

### Check Active Cleanup

```bash
nodetool compactionstats
```

Cleanup appears as a compaction operation.

### Monitor Disk Space

```bash
# Before cleanup
df -h /var/lib/cassandra

# Monitor during cleanup
watch -n 30 'df -h /var/lib/cassandra'
```

## Common Use Cases

### Post-Node-Addition Cleanup Script

```bash
#!/bin/bash
# Run on each existing node after new node joins

KEYSPACE="my_keyspace"

echo "Starting cleanup at $(date)"
echo "Disk usage before:"
df -h /var/lib/cassandra

nodetool cleanup $KEYSPACE

echo "Disk usage after:"
df -h /var/lib/cassandra
echo "Cleanup completed at $(date)"
```

### Cluster-Wide Cleanup Orchestration

```bash
#!/bin/bash
# Run from control node to clean entire cluster

NODES="10.0.0.1 10.0.0.2 10.0.0.3"
KEYSPACE="my_keyspace"

for node in $NODES; do
    echo "Cleaning up $node..."
    ssh $node "nodetool cleanup $KEYSPACE"

    if [ $? -eq 0 ]; then
        echo "$node cleanup completed"
    else
        echo "ERROR: Cleanup failed on $node"
        exit 1
    fi

    # Wait between nodes to avoid cluster-wide I/O spike
    sleep 60
done

echo "Cluster cleanup complete"
```

## Duration Estimation

Cleanup duration depends on:

| Factor | Impact |
|--------|--------|
| Data volume | Primary factor |
| Percentage to remove | More data to remove = longer |
| Disk I/O speed | Read and write performance |
| SSTable count | More SSTables = longer |

**Rough estimation:** Similar to full compaction time for affected tables.

## Disk Space Requirements

Cleanup requires temporary disk space because:

1. New SSTables are written before old ones are deleted
2. Peak usage occurs when an SSTable is being rewritten

**Requirement:** At least 50% free disk space before starting cleanup.

**Monitor during cleanup:**
```bash
while nodetool compactionstats | grep -q Cleanup; do
    df -h /var/lib/cassandra | tail -1
    sleep 30
done
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Cleanup completed successfully |
| 1 | Error occurred |
| 2 | Invalid arguments |

## Related Commands

- [nodetool status](status.md) - Verify cluster topology
- [nodetool compact](compact.md) - Force compaction
- [nodetool compactionstats](compactionstats.md) - Monitor cleanup progress
- [nodetool decommission](decommission.md) - Remove node from cluster

## Related Documentation

- [Operations - Cluster Management](../../../operations/cluster-management/index.md) - Adding and removing nodes
- [Operations - Adding Nodes](../../../operations/cluster-management/adding-nodes.md) - Node addition procedures
- [Architecture - Data Distribution](../../../architecture/data-distribution.md) - Token ownership

## Version Information

Available in all Apache Cassandra versions. The `-j` parallel jobs option provides control over concurrent cleanup operations.
