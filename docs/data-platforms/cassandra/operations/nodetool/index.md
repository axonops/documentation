---
title: "Cassandra nodetool Reference"
description: "Complete nodetool command reference for Apache Cassandra cluster management and operations."
meta:
  - name: keywords
    content: "nodetool commands, Cassandra nodetool, cluster management, operations reference"
search:
  boost: 3
---

# nodetool Reference

nodetool is the primary command-line interface for managing and monitoring Apache Cassandra nodes. It communicates with the Cassandra process via JMX (Java Management Extensions) to perform administrative operations.

---

## Overview

### Connection

nodetool connects to the local Cassandra node via JMX on port 7199:

```bash
# Default connection (localhost:7199)
nodetool status

# With authentication (when JMX authentication is enabled)
nodetool -u admin -pw password status

# With password file (recommended for scripts)
nodetool -u admin -pwf /path/to/jmx_password_file status
```

!!! tip "Local Execution Recommended"
    By default, Cassandra binds the JMX port (7199) to localhost only. This is the recommended configuration for security reasons. All nodetool commands should be executed locally on each Cassandra node rather than remotely. This approach:

    - Eliminates JMX network exposure and associated security risks
    - Removes the need for complex JMX-over-network authentication setup
    - Simplifies firewall configurations
    - Aligns with security best practices for JMX management

    For cluster-wide operations, use SSH to execute nodetool commands on each node, or use orchestration tools like Ansible.

### Common Options

| Option | Description |
|--------|-------------|
| `-h, --host` | Target host (default: localhost). Use only when JMX is bound to a non-localhost interface. |
| `-p, --port` | JMX port (default: 7199) |
| `-u, --username` | JMX username |
| `-pw, --password` | JMX password |
| `-pwf, --password-file` | File containing JMX password |
| `--ssl` | Use SSL for JMX connection |

!!! warning "JMX Security"
    - The default JMX binding to localhost is intentional and should not be changed unless absolutely necessary
    - If remote JMX access is required, enable JMX authentication and SSL encryption
    - Never expose unauthenticated JMX ports to untrusted networks
    - Consider using SSH tunneling instead of exposing JMX ports directly

---

## Version Compatibility

Most nodetool commands are available across all Cassandra 4.x and 5.x versions. The tables below list commands introduced in specific versions.

### Commands Added in Cassandra 4.1

| Command | Description |
|---------|-------------|
| [datapaths](datapaths.md) | Display data file locations |
| [getauditlog](getauditlog.md) | Get audit log configuration |
| [getauthcacheconfig](getauthcacheconfig.md) | Get auth cache configuration |
| [getcolumnindexsize](getcolumnindexsize.md) | Get column index size |
| [getdefaultrf](getdefaultrf.md) | Get default replication factor |
| [invalidatecredentialscache](invalidatecredentialscache.md) | Invalidate credentials cache |
| [invalidatejmxpermissionscache](invalidatejmxpermissionscache.md) | Invalidate JMX permissions cache |
| [invalidatenetworkpermissionscache](invalidatenetworkpermissionscache.md) | Invalidate network permissions cache |
| [invalidaterolescache](invalidaterolescache.md) | Invalidate roles cache |
| [listpendinghints](listpendinghints.md) | List pending hints |
| [recompress_sstables](recompress_sstables.md) | Recompress SSTables |
| [setauthcacheconfig](setauthcacheconfig.md) | Set auth cache configuration |
| [setcolumnindexsize](setcolumnindexsize.md) | Set column index size |
| [setdefaultrf](setdefaultrf.md) | Set default replication factor |

### Commands Added in Cassandra 5.0

| Command | Description |
|---------|-------------|
| [checktokenmetadata](checktokenmetadata.md) | Check token metadata for inconsistencies |
| [cidrfilteringstats](cidrfilteringstats.md) | Display CIDR filtering statistics |
| [dropcidrgroup](dropcidrgroup.md) | Remove CIDR group |
| [forcecompact](forcecompact.md) | Force user-defined compaction |
| [getcidrgroupsofip](getcidrgroupsofip.md) | Get CIDR groups for an IP |
| [getguardrailsconfig](getguardrailsconfig.md) | Get guardrails configuration |
| [invalidatecidrpermissionscache](invalidatecidrpermissionscache.md) | Invalidate CIDR permissions cache |
| [listcidrgroups](listcidrgroups.md) | List all CIDR groups |
| [reloadcidrgroupscache](reloadcidrgroupscache.md) | Reload CIDR groups cache |
| [setguardrailsconfig](setguardrailsconfig.md) | Set guardrails configuration |
| [updatecidrgroup](updatecidrgroup.md) | Create or update CIDR group |

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
| [datapaths](datapaths.md) | Display data file locations |
| [help](help.md) | Display help information |

### Cluster Topology

Commands for managing cluster membership.

| Command | Description |
|---------|-------------|
| [decommission](decommission.md) | Remove node from cluster gracefully |
| [removenode](removenode.md) | Remove a dead node from cluster |
| [assassinate](assassinate.md) | Force remove an unresponsive node |
| [rebuild](rebuild.md) | Rebuild data from other datacenters |
| [drain](drain.md) | Drain the node before shutdown |
| [stopdaemon](stopdaemon.md) | Stop Cassandra daemon |
| [bootstrap](bootstrap.md) | Resume bootstrap operation |
| [join](join.md) | Join the ring after bootstrap |
| [move](move.md) | Move node to new token |
| [failuredetector](failuredetector.md) | Display failure detector information |
| [checktokenmetadata](checktokenmetadata.md) | Check token metadata for inconsistencies |

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

### SSTable Management

Commands for advanced SSTable operations.

| Command | Description |
|---------|-------------|
| [getsstables](getsstables.md) | List SSTables for a partition key |
| [relocatesstables](relocatesstables.md) | Move SSTables to correct disk |
| [recompress_sstables](recompress_sstables.md) | Recompress SSTables with new settings |
| [rebuild_index](rebuild_index.md) | Rebuild secondary indexes |

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
| [getcompactionthreshold](getcompactionthreshold.md) | Get compaction thresholds |
| [setcompactionthreshold](setcompactionthreshold.md) | Set compaction thresholds |
| [enableautocompaction](enableautocompaction.md) | Enable automatic compaction |
| [disableautocompaction](disableautocompaction.md) | Disable automatic compaction |
| [statusautocompaction](statusautocompaction.md) | Check auto-compaction status |
| [forcecompact](forcecompact.md) | Force user-defined compaction |
| [stop](stop.md) | Stop compaction operations |

### Streaming and Hinted Handoff

Commands for data streaming and hints.

| Command | Description |
|---------|-------------|
| [netstats](netstats.md) | Display network statistics and streaming |
| [setstreamthroughput](setstreamthroughput.md) | Set streaming throughput |
| [getstreamthroughput](getstreamthroughput.md) | Get streaming throughput |
| [setinterdcstreamthroughput](setinterdcstreamthroughput.md) | Set inter-DC streaming throughput |
| [getinterdcstreamthroughput](getinterdcstreamthroughput.md) | Get inter-DC streaming throughput |
| [truncatehints](truncatehints.md) | Truncate all hints |
| [enablehandoff](enablehandoff.md) | Enable hinted handoff |
| [disablehandoff](disablehandoff.md) | Disable hinted handoff |
| [statushandoff](statushandoff.md) | Check hinted handoff status |
| [pausehandoff](pausehandoff.md) | Pause hint delivery |
| [resumehandoff](resumehandoff.md) | Resume hint delivery |
| [enablehintsfordc](enablehintsfordc.md) | Enable hints for datacenter |
| [disablehintsfordc](disablehintsfordc.md) | Disable hints for datacenter |
| [listpendinghints](listpendinghints.md) | List pending hints |
| [sethintedhandoffthrottlekb](sethintedhandoffthrottlekb.md) | Set hint delivery throttle |
| [getmaxhintwindow](getmaxhintwindow.md) | Get maximum hint window |
| [setmaxhintwindow](setmaxhintwindow.md) | Set maximum hint window |

### Gossip and Binary Protocol

Commands for gossip and client protocol management.

| Command | Description |
|---------|-------------|
| [enablegossip](enablegossip.md) | Enable gossip |
| [disablegossip](disablegossip.md) | Disable gossip |
| [statusgossip](statusgossip.md) | Check gossip status |
| [enablebinary](enablebinary.md) | Enable CQL native transport |
| [disablebinary](disablebinary.md) | Disable CQL native transport |
| [statusbinary](statusbinary.md) | Check native transport status |
| [enableoldprotocolversions](enableoldprotocolversions.md) | Enable old protocol versions |
| [disableoldprotocolversions](disableoldprotocolversions.md) | Disable old protocol versions |

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
| [clientstats](clientstats.md) | Display client connection statistics |
| [profileload](profileload.md) | Profile read/write operations |
| [sjk](sjk.md) | Swiss Java Knife diagnostic tool |
| [rangekeysample](rangekeysample.md) | Sample range keys |
| [viewbuildstatus](viewbuildstatus.md) | Check materialized view build status |
| [refreshsizeestimates](refreshsizeestimates.md) | Refresh size estimates |
| [replaybatchlog](replaybatchlog.md) | Replay pending batches |

### Configuration

Commands for runtime configuration.

| Command | Description |
|---------|-------------|
| [setlogginglevel](setlogginglevel.md) | Set logging level |
| [getlogginglevels](getlogginglevels.md) | Get logging levels |
| [reloadssl](reloadssl.md) | Reload SSL certificates |
| [gettimeout](gettimeout.md) | Get operation timeout |
| [settimeout](settimeout.md) | Set operation timeout |
| [setcachecapacity](setcachecapacity.md) | Set cache capacity |
| [setcachekeystosave](setcachekeystosave.md) | Set cache keys to save |
| [getconcurrentcompactors](getconcurrentcompactors.md) | Get concurrent compactors |
| [setconcurrentcompactors](setconcurrentcompactors.md) | Set concurrent compactors |
| [getconcurrentviewbuilders](getconcurrentviewbuilders.md) | Get concurrent view builders |
| [setconcurrentviewbuilders](setconcurrentviewbuilders.md) | Set concurrent view builders |
| [getconcurrency](getconcurrency.md) | Get thread concurrency |
| [setconcurrency](setconcurrency.md) | Set thread concurrency |
| [getdefaultrf](getdefaultrf.md) | Get default replication factor |
| [setdefaultrf](setdefaultrf.md) | Set default replication factor |
| [getsnapshotthrottle](getsnapshotthrottle.md) | Get snapshot throttle |
| [setsnapshotthrottle](setsnapshotthrottle.md) | Set snapshot throttle |
| [getcolumnindexsize](getcolumnindexsize.md) | Get column index size |
| [setcolumnindexsize](setcolumnindexsize.md) | Set column index size |
| [getseeds](getseeds.md) | Get seed nodes |
| [reloadseeds](reloadseeds.md) | Reload seed nodes |
| [gettraceprobability](gettraceprobability.md) | Get trace probability |
| [settraceprobability](settraceprobability.md) | Set trace probability |
| [getbatchlogreplaythrottle](getbatchlogreplaythrottle.md) | Get batch log replay throttle |
| [setbatchlogreplaythrottle](setbatchlogreplaythrottle.md) | Set batch log replay throttle |
| [reloadtriggers](reloadtriggers.md) | Reload triggers |
| [reloadlocalschema](reloadlocalschema.md) | Reload local schema |
| [resetlocalschema](resetlocalschema.md) | Reset local schema |
| [getauthcacheconfig](getauthcacheconfig.md) | Get auth cache configuration |
| [setauthcacheconfig](setauthcacheconfig.md) | Set auth cache configuration |
| [getguardrailsconfig](getguardrailsconfig.md) | Get guardrails configuration |
| [setguardrailsconfig](setguardrailsconfig.md) | Set guardrails configuration |

### Cache Management

Commands for cache invalidation.

| Command | Description |
|---------|-------------|
| [invalidatekeycache](invalidatekeycache.md) | Invalidate key cache |
| [invalidaterowcache](invalidaterowcache.md) | Invalidate row cache |
| [invalidatecountercache](invalidatecountercache.md) | Invalidate counter cache |
| [invalidatepermissionscache](invalidatepermissionscache.md) | Invalidate permissions cache |
| [invalidatecredentialscache](invalidatecredentialscache.md) | Invalidate credentials cache |
| [invalidaterolescache](invalidaterolescache.md) | Invalidate roles cache |
| [invalidatenetworkpermissionscache](invalidatenetworkpermissionscache.md) | Invalidate network permissions cache |
| [invalidatejmxpermissionscache](invalidatejmxpermissionscache.md) | Invalidate JMX permissions cache |

### CIDR Filtering

Commands for IP-based access control.

| Command | Description |
|---------|-------------|
| [cidrfilteringstats](cidrfilteringstats.md) | Display CIDR filtering statistics |
| [listcidrgroups](listcidrgroups.md) | List all CIDR groups |
| [getcidrgroupsofip](getcidrgroupsofip.md) | Get CIDR groups for an IP |
| [updatecidrgroup](updatecidrgroup.md) | Create or update CIDR group |
| [dropcidrgroup](dropcidrgroup.md) | Remove CIDR group |
| [invalidatecidrpermissionscache](invalidatecidrpermissionscache.md) | Invalidate CIDR permissions cache |
| [reloadcidrgroupscache](reloadcidrgroupscache.md) | Reload CIDR groups cache |

### Audit Logging

Commands for audit log management.

| Command | Description |
|---------|-------------|
| [enableauditlog](enableauditlog.md) | Enable audit logging |
| [disableauditlog](disableauditlog.md) | Disable audit logging |
| [getauditlog](getauditlog.md) | Get audit log configuration |

### Full Query Logging

Commands for full query log management.

| Command | Description |
|---------|-------------|
| [enablefullquerylog](enablefullquerylog.md) | Enable full query logging |
| [disablefullquerylog](disablefullquerylog.md) | Disable full query logging |
| [getfullquerylog](getfullquerylog.md) | Get full query log configuration |
| [resetfullquerylog](resetfullquerylog.md) | Reset full query log |

---

## Command Usage Patterns

### Daily Operations

| Task | Command |
|------|---------|
| Check cluster health | `nodetool status` |
| Monitor compactions | `nodetool compactionstats` |
| Check thread pools | `nodetool tpstats` |
| View table metrics | `nodetool tablestats <keyspace>` |
| Check client connections | `nodetool clientstats` |

### Maintenance Tasks

| Task | Command |
|------|---------|
| Flush before backup | `nodetool flush` |
| Create snapshot | `nodetool snapshot -t <name>` |
| Run repair | `nodetool repair -pr` |
| Clean up after topology change | `nodetool cleanup` |
| Rebuild secondary indexes | `nodetool rebuild_index <ks> <table> <index>` |

### Troubleshooting

| Task | Command |
|------|---------|
| Check streaming | `nodetool netstats` |
| View latencies | `nodetool proxyhistograms` |
| Check gossip state | `nodetool gossipinfo` |
| Find hot partitions | `nodetool toppartitions <ks> <table> 60000` |
| Check pending hints | `nodetool listpendinghints` |
| Verify SSTables | `nodetool verify <keyspace>` |

### Security Operations

| Task | Command |
|------|---------|
| Enable audit logging | `nodetool enableauditlog` |
| Check CIDR filtering | `nodetool cidrfilteringstats` |
| Invalidate auth cache | `nodetool invalidatepermissionscache` |
| Reload SSL certificates | `nodetool reloadssl` |

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

!!! info "Runtime vs Persistent Settings"
    Many `set*` commands modify settings at runtime only. These changes are lost on node restart. To make settings persistent, also update `cassandra.yaml`. Commands that modify persistent data (like CIDR groups) are noted in their documentation.
