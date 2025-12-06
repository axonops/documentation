# Cassandra Troubleshooting Guide

Most Cassandra problems have a small number of root causes. High read latency? Probably tombstones or large partitions—not CPU, despite what instincts might suggest. Out of memory? Usually a partition that grew too large for the heap to handle during compaction, not a sign that more RAM is needed. Timeouts? Check if compaction is falling behind.

The diagnosis process is consistent: check the logs for warnings, look at the metrics (especially p99 latency, pending compactions, and thread pool stats), and use nodetool to inspect specific tables. The symptoms point to the cause for those who know where to look.

This guide provides systematic procedures for diagnosing and resolving common issues.

## Troubleshooting Framework

We use the **SDRR Framework** for consistent problem resolution:

1. **Symptoms**: What observable behaviors indicate the problem?
2. **Diagnosis**: How to identify the root cause
3. **Resolution**: Step-by-step fix procedures
4. **Recovery**: Verification and prevention

---

## Quick Reference: Common Issues

### Performance Issues

| Symptom | Likely Cause | Quick Action |
|---------|--------------|--------------|
| High read latency | Data model, tombstones | Check `nodetool tablestats` |
| High write latency | Disk I/O, compaction | Check `nodetool compactionstats` |
| Request timeouts | Overload, disk issues | Check `nodetool tpstats` |
| Slow startup | Large commitlog | Check commitlog size |

### Availability Issues

| Symptom | Likely Cause | Quick Action |
|---------|--------------|--------------|
| Node down | OOM, disk full, crash | Check logs, `systemctl status` |
| Nodes not joining | Network, schema | Check gossip, firewalls |
| Inconsistent data | Repair needed | Run `nodetool repair` |

### Resource Issues

| Symptom | Likely Cause | Quick Action |
|---------|--------------|--------------|
| High CPU | GC, compaction | Check GC logs, compaction |
| High memory | Heap settings | Review JVM configuration |
| Disk full | Large tables, snapshots | Clean snapshots, add capacity |

---

## Documentation Structure

### Common Errors

Detailed documentation for specific exceptions:

- **[ReadTimeoutException](common-errors/read-timeout.md)** - Read operations timing out
- **[WriteTimeoutException](common-errors/write-timeout.md)** - Write operations timing out
- **[UnavailableException](common-errors/unavailable.md)** - Insufficient replicas
- **[TombstoneOverwhelmingException](common-errors/tombstone-overwhelming.md)** - Too many tombstones
- **[NoHostAvailableException](common-errors/no-host-available.md)** - Driver connection issues
- **[SSTableCorruptedException](common-errors/sstable-corrupted.md)** - Data corruption
- **[OutOfMemoryError](common-errors/out-of-memory.md)** - Heap exhaustion
- **[BootstrapException](common-errors/bootstrap-exception.md)** - Node joining failures
- **[MutationFailedException](common-errors/mutation-failed.md)** - Write failures
- **[InvalidQueryException](common-errors/invalid-query.md)** - CQL errors

### Diagnosis Procedures

Root cause analysis guides:

- **[Performance Diagnosis](diagnosis/performance.md)** - Slow queries and latency
- **[Memory Diagnosis](diagnosis/memory.md)** - Heap and off-heap issues
- **[Disk Diagnosis](diagnosis/disk.md)** - I/O and storage problems
- **[Network Diagnosis](diagnosis/network.md)** - Connectivity issues
- **[Data Diagnosis](diagnosis/data.md)** - Corruption and consistency
- **[Startup Diagnosis](diagnosis/startup.md)** - Node will not start

### Operational Playbooks

Step-by-step procedures for common scenarios:

- **[Replace Dead Node](playbooks/replace-dead-node.md)**
- **[Recover from OOM](playbooks/recover-from-oom.md)**
- **[Handle Full Disk](playbooks/handle-full-disk.md)**
- **[Fix Schema Disagreement](playbooks/fix-schema-disagreement.md)**
- **[Repair Corrupted Data](playbooks/repair-corrupted-data.md)**
- **[Resolve Network Partition](playbooks/network-partition.md)**

### Log Analysis

Understanding Cassandra logs:

- **[Log Levels and Locations](log-analysis/log-locations.md)**
- **[Common Log Patterns](log-analysis/log-patterns.md)**
- **[GC Log Analysis](log-analysis/gc-logs.md)**
- **[Error Message Reference](log-analysis/error-messages.md)**

---

## First Response Checklist

When an issue occurs, gather this information first:

### 1. Check Node Status

```bash
# Cluster overview
nodetool status

# Node info
nodetool info

# Thread pool stats
nodetool tpstats

# Compaction status
nodetool compactionstats
```

### 2. Check Logs

```bash
# Recent errors
tail -100 /var/log/cassandra/system.log | grep -i error

# Warnings
tail -100 /var/log/cassandra/system.log | grep -i warn

# GC issues
grep "GC pause" /var/log/cassandra/gc.log | tail -20
```

### 3. Check Resources

```bash
# Disk space
df -h /var/lib/cassandra

# Memory
free -h

# CPU
top -b -n 1 | head -20

# I/O
iostat -x 1 5
```

### 4. Check Metrics

```bash
# Table stats for specific keyspace
nodetool tablestats my_keyspace

# Pending compactions
nodetool compactionstats | grep pending

# Dropped messages
nodetool tpstats | grep -i dropped
```

---

## Diagnostic Commands Reference

### nodetool Commands

| Command | Purpose |
|---------|---------|
| `nodetool status` | Cluster and node health |
| `nodetool info` | Node information |
| `nodetool tpstats` | Thread pool statistics |
| `nodetool tablestats <ks>` | Table statistics |
| `nodetool compactionstats` | Compaction status |
| `nodetool netstats` | Network status |
| `nodetool gossipinfo` | Gossip state |
| `nodetool describecluster` | Cluster description |
| `nodetool proxyhistograms` | Request latencies |
| `nodetool tablehistograms <ks> <table>` | Table latencies |

### Log Locations

| Log | Location | Purpose |
|-----|----------|---------|
| System log | `/var/log/cassandra/system.log` | Main application log |
| Debug log | `/var/log/cassandra/debug.log` | Detailed debug info |
| GC log | `/var/log/cassandra/gc.log` | Garbage collection |
| Audit log | `/var/log/cassandra/audit/audit.log` | Security audit |

### Key Metrics to Check

```bash
# JMX metrics via nodetool
nodetool gcstats                    # GC statistics
nodetool getlogginglevels           # Current log levels
nodetool statusbinary               # CQL port status
nodetool statusgossip               # Gossip status
```

---

## Issue Categories

### Timeout Issues

Requests failing due to time limits:

| Error | Default Timeout | Configuration |
|-------|-----------------|---------------|
| Read timeout | 5000ms | `read_request_timeout_in_ms` |
| Write timeout | 2000ms | `write_request_timeout_in_ms` |
| Range timeout | 10000ms | `range_request_timeout_in_ms` |
| Counter timeout | 5000ms | `counter_write_request_timeout_in_ms` |
| Truncate timeout | 60000ms | `truncate_request_timeout_in_ms` |

**Common causes**: Overload, slow disks, network issues, data model problems.

### Consistency Issues

Data inconsistency between replicas:

| Symptom | Cause | Action |
|---------|-------|--------|
| Different data per query | Repair needed | Run repair |
| Unavailable errors | Insufficient replicas | Check node status |
| Timeout with QUORUM | Multiple nodes slow | Check all replicas |

### Compaction Issues

Compaction falling behind:

| Symptom | Cause | Action |
|---------|-------|--------|
| High pending compactions | Write-heavy, slow disk | Increase throughput |
| Large SSTable files | No compaction | Check strategy |
| High read latency | Many SSTables | Force compaction |

### Memory Issues

Heap exhaustion or GC pressure:

| Symptom | Cause | Action |
|---------|-------|--------|
| OOM errors | Heap too small, large partitions | Increase heap, fix data model |
| Long GC pauses | Heap too large | Reduce heap size |
| Off-heap OOM | Bloom filters, compression | Adjust off-heap settings |

---

## Emergency Procedures

### Node Unresponsive

```bash
# 1. Check if process is running
ps aux | grep cassandra

# 2. Check for OOM kills
dmesg | grep -i "killed process"

# 3. Check system log
tail -100 /var/log/cassandra/system.log

# 4. If hung, get thread dump
jstack $(pgrep -f CassandraDaemon) > /tmp/threaddump.txt

# 5. If necessary, restart
sudo systemctl restart cassandra
```

### Disk Full

```bash
# 1. Check disk usage
df -h /var/lib/cassandra

# 2. Find large files
du -sh /var/lib/cassandra/*

# 3. Clear snapshots
nodetool clearsnapshot --all

# 4. If still full, consider temporary cleanup
ls -la /var/lib/cassandra/data/<keyspace>/<table>*/
```

### Cluster Partition

```bash
# 1. Check gossip state on both sides
nodetool gossipinfo

# 2. Verify network connectivity
nc -zv <other-node-ip> 7000
nc -zv <other-node-ip> 9042

# 3. Check firewall rules
sudo iptables -L -n

# 4. If network is fine, check for zombie nodes
nodetool status | grep -E "DN|UJ|UL"
```

---

## Getting Help

### Information to Collect

When seeking help, gather:

1. **Cassandra version**: `nodetool version`
2. **Cluster configuration**: `nodetool describecluster`
3. **Node status**: `nodetool status`
4. **Recent logs**: Last 100 lines of system.log
5. **Error messages**: Exact exception text
6. **Recent changes**: What changed before the issue

### Resources

- **[Apache Cassandra Slack](https://cassandra.apache.org/community/)** - Community chat
- **[AxonOps Community](https://axonops.com/community/)** - Professional support
- **[Stack Overflow](https://stackoverflow.com/questions/tagged/cassandra)** - Q&A

---

## Next Steps

- **[Common Errors](common-errors/index.md)** - Error reference
- **[Diagnosis Procedures](diagnosis/index.md)** - Root cause analysis
- **[Playbooks](playbooks/index.md)** - Step-by-step procedures
- **[Log Analysis](log-analysis/index.md)** - Understanding logs
