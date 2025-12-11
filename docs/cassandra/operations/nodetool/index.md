# Nodetool Reference

Nodetool is the primary command-line interface for managing and monitoring Apache Cassandra nodes. It communicates with the Cassandra process via JMX (Java Management Extensions) to perform administrative operations.

---

## Overview

### Connection

Nodetool connects to a Cassandra node via JMX:

```bash
# Default connection (localhost:7199)
nodetool status

# Remote connection
nodetool -h 192.168.1.100 -p 7199 status

# With authentication
nodetool -h 192.168.1.100 -u admin -pw password status
```

### Common Options

| Option | Description |
|--------|-------------|
| `-h, --host` | Remote host (default: localhost) |
| `-p, --port` | JMX port (default: 7199) |
| `-u, --username` | JMX username |
| `-pw, --password` | JMX password |
| `-pwf, --password-file` | File containing JMX password |
| `--ssl` | Use SSL for JMX connection |

!!! warning "JMX Security"
    In production environments, JMX should be secured with authentication and SSL. Never expose JMX ports to untrusted networks.

---

## Command Categories

### Cluster Information

Commands for viewing cluster state and metadata.

| Command | Description |
|---------|-------------|
| [status](status.md) | Display cluster status and load information |
| [ring](ring.md) | Display token ring information |
| [info](info.md) | Display node information |
| [describecluster](describecluster.md) | Display cluster name, snitch, and partitioner |
| [describering](describering.md) | Display token ranges for a keyspace |
| [gossipinfo](gossipinfo.md) | Display gossip information |
| [version](version.md) | Display Cassandra version |
| [getendpoints](getendpoints.md) | Display endpoints for a key |

### Data Management

Commands for managing data and SSTables.

| Command | Description |
|---------|-------------|
| [flush](flush.md) | Flush memtables to SSTables |
| [compact](compact.md) | Force compaction |
| [cleanup](cleanup.md) | Remove data not belonging to this node |
| [scrub](scrub.md) | Rebuild SSTables, fixing corruption |
| [verify](verify.md) | Verify SSTable integrity |
| [upgradesstables](upgradesstables.md) | Upgrade SSTables to current version |
| [garbagecollect](garbagecollect.md) | Remove deleted data from SSTables |
| [import](import.md) | Import SSTables from directory |
| [refresh](refresh.md) | Load newly placed SSTables |

### Repair

Commands for anti-entropy repair operations.

| Command | Description |
|---------|-------------|
| [repair](repair.md) | Run anti-entropy repair |
| [repair_admin](repair_admin.md) | Manage repair sessions |

### Snapshots and Backup

Commands for backup and snapshots.

| Command | Description |
|---------|-------------|
| [snapshot](snapshot.md) | Create a snapshot |
| [clearsnapshot](clearsnapshot.md) | Remove snapshots |
| [listsnapshots](listsnapshots.md) | List existing snapshots |
| [enablebackup](enablebackup.md) | Enable incremental backup |
| [disablebackup](disablebackup.md) | Disable incremental backup |
| [statusbackup](statusbackup.md) | Check incremental backup status |

### Compaction Management

Commands for controlling compaction.

| Command | Description |
|---------|-------------|
| [compactionstats](compactionstats.md) | Display compaction statistics |
| [compactionhistory](compactionhistory.md) | Display compaction history |
| [setcompactionthroughput](setcompactionthroughput.md) | Set compaction throughput |
| [getcompactionthroughput](getcompactionthroughput.md) | Get compaction throughput |
| [stop](stop.md) | Stop compaction operations |

### Streaming and Hinted Handoff

Commands for data streaming and hints.

| Command | Description |
|---------|-------------|
| [netstats](netstats.md) | Display network statistics and streaming |
| [setstreamthroughput](setstreamthroughput.md) | Set streaming throughput |
| [truncatehints](truncatehints.md) | Truncate all hints |

### Cluster Topology

Commands for managing cluster membership.

| Command | Description |
|---------|-------------|
| [decommission](decommission.md) | Remove node from cluster |
| [removenode](removenode.md) | Remove a dead node |
| [assassinate](assassinate.md) | Force remove an unresponsive node |
| [rebuild](rebuild.md) | Rebuild data from other DCs |
| [drain](drain.md) | Drain the node |
| [stopdaemon](stopdaemon.md) | Stop Cassandra daemon |

### Gossip

Commands for gossip protocol management.

| Command | Description |
|---------|-------------|
| [enablegossip](enablegossip.md) | Enable gossip |
| [disablegossip](disablegossip.md) | Disable gossip |
| [statusgossip](statusgossip.md) | Check gossip status |

### Client Connections

Commands for managing client connections.

| Command | Description |
|---------|-------------|
| [enablebinary](enablebinary.md) | Enable CQL native transport |
| [disablebinary](disablebinary.md) | Disable CQL native transport |
| [statusbinary](statusbinary.md) | Check native transport status |

### Diagnostics and Monitoring

Commands for diagnostics and performance analysis.

| Command | Description |
|---------|-------------|
| [tpstats](tpstats.md) | Display thread pool statistics |
| [proxyhistograms](proxyhistograms.md) | Display coordinator read/write latencies |
| [tablehistograms](tablehistograms.md) | Display table latency histograms |
| [tablestats](tablestats.md) | Display table statistics |
| [toppartitions](toppartitions.md) | Sample top partitions |
| [gcstats](gcstats.md) | Display garbage collection statistics |

### Configuration

Commands for runtime configuration.

| Command | Description |
|---------|-------------|
| [setlogginglevel](setlogginglevel.md) | Set logging level |
| [getlogginglevels](getlogginglevels.md) | Get logging levels |
| [reloadssl](reloadssl.md) | Reload SSL certificates |

---

## Command Usage Patterns

### Daily Operations

| Task | Command |
|------|---------|
| Check cluster health | `nodetool status` |
| Monitor compactions | `nodetool compactionstats` |
| Check thread pools | `nodetool tpstats` |
| View table metrics | `nodetool tablestats <keyspace>` |

### Maintenance Tasks

| Task | Command |
|------|---------|
| Flush before backup | `nodetool flush` |
| Create snapshot | `nodetool snapshot -t <name>` |
| Run repair | `nodetool repair -pr` |
| Clean up after topology change | `nodetool cleanup` |

### Troubleshooting

| Task | Command |
|------|---------|
| Check streaming | `nodetool netstats` |
| View latencies | `nodetool proxyhistograms` |
| Check gossip state | `nodetool gossipinfo` |
| Find hot partitions | `nodetool toppartitions <ks> <table> 60000` |

---

## Best Practices

!!! tip "Operational Guidelines"
    1. **Always check status first** - Run `nodetool status` before any operation
    2. **One node at a time** - For heavy operations, run on one node at a time
    3. **Monitor during operations** - Watch `tpstats` and `compactionstats`
    4. **Schedule during low traffic** - Run maintenance during off-peak hours
    5. **Document changes** - Log all nodetool commands run on production

!!! warning "Production Precautions"
    - Never run `assassinate` without understanding the consequences
    - Always `drain` before stopping Cassandra
    - Test commands in non-production first
    - Have rollback plans for topology changes
