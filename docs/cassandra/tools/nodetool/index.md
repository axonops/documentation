# Nodetool Reference

Nodetool is the primary command-line administration utility for Apache Cassandra. It provides the interface through which operators monitor cluster health, perform maintenance operations, and manage cluster topology. All nodetool commands execute via JMX (Java Management Extensions) calls to the Cassandra daemon.

## Connection Options

All nodetool commands accept the following connection options:

| Option | Description | Default |
|--------|-------------|---------|
| -h, --host | Hostname or IP to connect to | localhost |
| -p, --port | JMX port number | 7199 |
| -u, --username | JMX authentication username | - |
| -pw, --password | JMX authentication password | - |
| -pwf, --password-file | File containing JMX password | - |
| --ssl | Use SSL for JMX connection | false |

### Connection Examples

```bash
# Local connection (default)
nodetool status

# Remote connection
nodetool -h 10.0.0.2 status

# With authentication
nodetool -u admin -pw secret status

# With SSL
nodetool --ssl status
```

---

## Command Reference

### Cluster Information

Commands for viewing cluster state and topology.

| Command | Description |
|---------|-------------|
| [status](commands/status.md) | Display cluster node status and ownership |
| [info](commands/info.md) | Display local node information |
| [ring](commands/ring.md) | Display token ring topology |
| [describecluster](commands/describecluster.md) | Display cluster configuration and schema versions |
| [gossipinfo](commands/gossipinfo.md) | Display gossip state for all nodes |
| [version](commands/version.md) | Display Cassandra version |

---

### Performance Monitoring

Commands for monitoring node and table performance.

| Command | Description |
|---------|-------------|
| [tpstats](commands/tpstats.md) | Display thread pool statistics |
| [tablestats](commands/tablestats.md) | Display table-level statistics |
| [tablehistograms](commands/tablehistograms.md) | Display latency histograms for a table |
| [proxyhistograms](commands/proxyhistograms.md) | Display coordinator-level latency histograms |
| [toppartitions](commands/toppartitions.md) | Sample and report hot partitions |
| [gcstats](commands/gcstats.md) | Display garbage collection statistics |

---

### Maintenance Operations

Commands for routine maintenance tasks.

| Command | Description |
|---------|-------------|
| [repair](commands/repair.md) | Run anti-entropy repair |
| [cleanup](commands/cleanup.md) | Remove data not belonging to this node |
| [compact](commands/compact.md) | Force compaction |
| [flush](commands/flush.md) | Flush memtables to SSTables |
| [drain](commands/drain.md) | Prepare node for shutdown |
| [garbagecollect](commands/garbagecollect.md) | Remove tombstones past gc_grace |
| [scrub](commands/scrub.md) | Rebuild SSTables |
| [verify](commands/verify.md) | Verify SSTable integrity |

---

### Backup and Restore

Commands for data protection.

| Command | Description |
|---------|-------------|
| [snapshot](commands/snapshot.md) | Create backup snapshot |
| [listsnapshots](commands/listsnapshots.md) | List all snapshots |
| [clearsnapshot](commands/clearsnapshot.md) | Remove snapshots |
| [refresh](commands/refresh.md) | Load new SSTables from data directory |

---

### Cluster Topology

Commands for managing cluster membership.

| Command | Description |
|---------|-------------|
| [decommission](commands/decommission.md) | Remove local node from cluster |
| [removenode](commands/removenode.md) | Remove dead node from cluster |
| [assassinate](commands/assassinate.md) | Force remove node from gossip |
| [rebuild](commands/rebuild.md) | Rebuild data from another datacenter |
| [move](commands/move.md) | Move node to new token |
| [bootstrap](commands/bootstrap.md) | Bootstrap operations |

---

### Compaction Management

Commands for controlling compaction.

| Command | Description |
|---------|-------------|
| [compactionstats](commands/compactionstats.md) | Display compaction activity |
| [setcompactionthroughput](commands/setcompactionthroughput.md) | Set compaction throughput limit |
| [getcompactionthroughput](commands/getcompactionthroughput.md) | Get compaction throughput limit |
| [enableautocompaction](commands/enableautocompaction.md) | Enable automatic compaction |
| [disableautocompaction](commands/disableautocompaction.md) | Disable automatic compaction |
| [stop](commands/stop.md) | Stop compaction |

---

### Streaming Control

Commands for controlling data streaming.

| Command | Description |
|---------|-------------|
| [netstats](commands/netstats.md) | Display network and streaming statistics |
| [setstreamthroughput](commands/setstreamthroughput.md) | Set streaming throughput limit |
| [getstreamthroughput](commands/getstreamthroughput.md) | Get streaming throughput limit |

---

### Configuration

Commands for runtime configuration changes.

| Command | Description |
|---------|-------------|
| [setlogginglevel](commands/setlogginglevel.md) | Change logging level dynamically |
| [getlogginglevels](commands/getlogginglevels.md) | Display current logging levels |
| [settraceprobability](commands/settraceprobability.md) | Set query tracing probability |
| [gettraceprobability](commands/gettraceprobability.md) | Get query tracing probability |
| [reloadtriggers](commands/reloadtriggers.md) | Reload trigger classes |
| [reloadlocalschema](commands/reloadlocalschema.md) | Reload local schema |
| [resetlocalschema](commands/resetlocalschema.md) | Reset local schema to cluster schema |

---

### Repair Management (Cassandra 4.0+)

Commands for managing repair sessions.

| Command | Description |
|---------|-------------|
| [repair_admin](commands/repair_admin.md) | Manage and monitor repair sessions |

---

## Quick Reference by Task

### Daily Health Checks

```bash
nodetool status              # Cluster state
nodetool tpstats             # Thread pools and dropped messages
nodetool compactionstats     # Compaction backlog
nodetool info                # Node memory and caches
```

### Before Maintenance

```bash
nodetool status              # Verify all nodes healthy
nodetool describecluster     # Check for schema disagreements
nodetool netstats            # Verify no streaming in progress
```

### Before Shutdown

```bash
nodetool drain               # Flush and stop connections
sudo systemctl stop cassandra
```

### After Adding Nodes

```bash
# On existing nodes (not new node)
nodetool cleanup             # Remove data now owned by new node
```

### Backup Procedure

```bash
nodetool flush my_keyspace
nodetool snapshot -t backup_$(date +%Y%m%d) my_keyspace
```

---

## Health Check Script

```bash
#!/bin/bash
# Comprehensive health check

echo "=== Cluster Status ==="
nodetool status

echo -e "\n=== Node Info ==="
nodetool info | grep -E "Load|Heap|Exceptions|Percent Repaired"

echo -e "\n=== Thread Pools (issues only) ==="
nodetool tpstats | awk 'NR==1 || $3>0 || $5>0 {print}'

echo -e "\n=== Dropped Messages ==="
nodetool tpstats | grep -A 20 "Message type" | awk 'NR==1 || $2>0 {print}'

echo -e "\n=== Compaction Status ==="
nodetool compactionstats

echo -e "\n=== Active Streaming ==="
nodetool netstats | grep -A 5 "Sending\|Receiving" || echo "No active streaming"
```

---

## Related Documentation

- [Operations Guide](../../operations/index.md) - Operational procedures
- [Monitoring - Key Metrics](../../monitoring/key-metrics/index.md) - Understanding metrics
- [Troubleshooting Guide](../../troubleshooting/index.md) - Problem resolution
- [JMX Reference](../../jmx-reference/index.md) - JMX metrics
- [cqlsh Reference](../cqlsh/index.md) - CQL shell

---

## Version Compatibility

Most nodetool commands are available across all Cassandra versions. Version-specific commands and options are noted in individual command documentation.

| Feature | Cassandra Version |
|---------|------------------|
| Basic commands | All versions |
| repair_admin | 4.0+ |
| JSON output format | 4.0+ |
| Virtual table integration | 4.0+ |

---

*Documentation covers Apache Cassandra 4.x and 5.x*
