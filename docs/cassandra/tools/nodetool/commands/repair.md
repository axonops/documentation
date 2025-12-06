# nodetool repair

Initiates anti-entropy repair to synchronize data across replicas and ensure consistency.

## Synopsis

```bash
nodetool [connection_options] repair [options] [keyspace [table ...]]
```

## Description

The `repair` command synchronizes data between replica nodes by comparing Merkle trees and streaming any differences. Repair is essential for maintaining data consistency in an eventually consistent system, particularly for data that has not been read recently (and thus not subject to read repair).

Cassandra supports two repair mechanisms:

- **Incremental repair** (default in 4.x+): Repairs only data written since the last repair, marking repaired data to avoid re-processing
- **Full repair**: Repairs all data regardless of previous repair status, useful for recovery scenarios

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| keyspace | No | Keyspace to repair. If omitted, repairs all keyspaces. |
| table | No | Specific table(s) to repair within the keyspace |

## Options

### Repair Scope Options

| Option | Description |
|--------|-------------|
| -pr, --partitioner-range | Repair only the primary range owned by this node. Recommended for routine maintenance as it avoids redundant work. |
| -full | Perform full repair instead of incremental. Re-repairs all data. |
| -st, --start-token &lt;token&gt; | Start token for subrange repair |
| -et, --end-token &lt;token&gt; | End token for subrange repair |

### Parallelism Options

| Option | Description |
|--------|-------------|
| --parallel | Repair with all replicas simultaneously (faster, higher resource usage) |
| -seq, --sequential | Repair one replica at a time (slower, lower impact) |
| -dcpar, --dc-parallel | Repair datacenters in parallel, nodes within DC sequentially |
| -j, --jobs &lt;count&gt; | Number of tables to repair simultaneously (default: 1) |

### Scope Limiting Options

| Option | Description |
|--------|-------------|
| -dc, --in-dc &lt;datacenter&gt; | Repair nodes in specified datacenter only |
| -dcall, --dc-all | Repair all datacenters (default when using NetworkTopologyStrategy) |
| -hosts, --in-hosts &lt;host1,host2,...&gt; | Repair only between specified hosts |
| -local, --in-local-dc | Repair only nodes in the local datacenter |

### Other Options

| Option | Description |
|--------|-------------|
| --trace | Enable tracing for the repair session |
| --preview | Estimate repair work without executing |
| -os, --optimise-streams | Optimize stream destinations (Cassandra 4.0+) |
| --ignore-unreplicated-keyspaces | Skip keyspaces with RF=1 |
| --force | Force repair even if some replicas are unavailable |

## Repair Types

### Incremental Repair (Default)

Repairs only unrepaired data. SSTables are marked as repaired after successful completion.

```bash
nodetool repair -pr my_keyspace
```

**Advantages:**
- Faster execution for routine maintenance
- Lower I/O overhead
- Repaired data is tracked

**Requirements:**
- All replicas must be available
- Should run regularly (within gc_grace_seconds)

### Full Repair

Re-repairs all data regardless of previous repair status.

```bash
nodetool repair -full my_keyspace
```

**Use cases:**
- After node replacement
- After data corruption recovery
- When incremental repair state is inconsistent
- Before major version upgrades

### Primary Range Repair

Repairs only ranges for which this node is the primary owner.

```bash
nodetool repair -pr my_keyspace
```

When running `-pr` on every node in the cluster, each range is repaired exactly once. This is the recommended approach for routine maintenance.

### Subrange Repair

Repairs a specific token range, useful for parallelizing repair or recovering specific data.

```bash
nodetool repair -st -9223372036854775808 -et -6148914691236517206 my_keyspace
```

## Examples

### Routine Maintenance Repair

```bash
# Primary range incremental repair (recommended daily/weekly)
nodetool repair -pr my_keyspace
```

### Full Cluster Repair Script

```bash
#!/bin/bash
# Run on each node sequentially
KEYSPACE="my_keyspace"

# Repair primary range only
nodetool repair -pr $KEYSPACE

# Check exit status
if [ $? -eq 0 ]; then
    echo "Repair completed successfully"
else
    echo "Repair failed - check logs"
    exit 1
fi
```

### Parallel Repair (Faster, Higher Impact)

```bash
nodetool repair -pr --parallel my_keyspace
```

### Full Repair After Node Replacement

```bash
# Run on the replacement node
nodetool repair -full my_keyspace
```

### Repair Preview

```bash
# Estimate work without executing
nodetool repair --preview my_keyspace
```

**Output:**
```
Repair preview for keyspace my_keyspace
  Total estimated ranges: 256
  Total estimated streaming: 12.5 GiB
  Mismatching ranges: 12
  Estimated repair time: 45 minutes
```

### Datacenter-Specific Repair

```bash
# Repair only within dc1
nodetool repair -dc dc1 my_keyspace

# Repair local DC only (run from node in target DC)
nodetool repair -local my_keyspace
```

### Multi-Table Parallel Repair

```bash
# Repair 4 tables simultaneously
nodetool repair -j 4 my_keyspace
```

## Monitoring Repair Progress

### Check Active Repairs

```bash
# View streaming operations
nodetool netstats

# View repair sessions (Cassandra 4.0+)
nodetool repair_admin list
```

### Cancel Running Repair

```bash
# List active repairs
nodetool repair_admin list

# Cancel specific repair
nodetool repair_admin cancel <repair_id>
```

### System Log Entries

Repair progress is logged to `system.log`:

```
INFO  [Repair#1] Starting repair command #1 (550e8400-e29b-41d4-a716-446655440000)
INFO  [Repair#1] Repair session 550e8400 for range (-9223372036854775808,9223372036854775807]
INFO  [Repair#1] Repair completed successfully
```

## Repair Frequency Guidelines

| Scenario | Recommended Frequency |
|----------|----------------------|
| High-write workloads | Daily |
| Read-heavy workloads | Weekly |
| Mixed workloads | Every 3-5 days |
| After node failures | Immediately |
| Before decommission | Before starting |

**Critical constraint:** Repair must complete within `gc_grace_seconds` (default: 10 days) to prevent resurrection of deleted data.

## Common Issues

### Repair Fails with "Cannot proceed"

```
Cannot proceed with repair: some replicas are not available
```

**Cause:** One or more replica nodes are down.

**Solution:**
- Wait for nodes to recover
- Use `--force` flag (risks consistency)
- Repair specific hosts with `-hosts`

### Repair Never Completes

**Possible causes:**
- Competing repairs on same ranges
- Insufficient streaming throughput
- Memory pressure causing GC pauses

**Investigation:**
```bash
# Check for blocked streams
nodetool netstats | grep -i stream

# Check streaming throughput
nodetool getstreamthroughput

# Increase if needed
nodetool setstreamthroughput 200
```

### Inconsistent Repair State

**Symptoms:** Incremental repair marks data as repaired but mismatches persist.

**Solution:** Run full repair to reset state:
```bash
nodetool repair -full my_keyspace
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Repair completed successfully |
| 1 | Repair failed or error occurred |
| 2 | Invalid arguments |

## Related Commands

- [nodetool repair_admin](repair_admin.md) - Manage running repairs
- [nodetool netstats](netstats.md) - Monitor streaming progress
- [nodetool setstreamthroughput](setstreamthroughput.md) - Adjust streaming speed
- [nodetool tablestats](tablestats.md) - Check percent repaired

## Related Documentation

- [Operations - Repair](../../../operations/repair/index.md) - Comprehensive repair guide
- [Architecture - Consistency](../../../architecture/consistency/index.md) - Understanding consistency and repair
- [Troubleshooting - Repair Failures](../../../troubleshooting/playbooks/repair-failures.md) - Diagnosing repair issues
- [Configuration - cassandra.yaml](../../../configuration/cassandra-yaml/index.md) - gc_grace_seconds and repair settings

## Version Information

| Feature | Version |
|---------|---------|
| Basic repair | All versions |
| Incremental repair (default) | 4.0+ |
| `repair_admin` command | 4.0+ |
| `--preview` option | 4.0+ |
| `--optimise-streams` | 4.0+ |
| Virtual table repair progress | 5.0+ |
