---
title: "Cassandra Troubleshooting Guide"
description: "Cassandra troubleshooting guide. Diagnose and resolve common issues."
meta:
  - name: keywords
    content: "Cassandra troubleshooting, diagnosis, problem resolution"
---

# Troubleshooting Guide

This guide provides systematic approaches to diagnosing and resolving common Cassandra operational issues.

!!! tip "Systematic Troubleshooting"
    Follow the pattern: **Observe** (gather data) → **Hypothesize** (form theory) → **Test** (verify theory) → **Fix** (implement solution) → **Verify** (confirm resolution).

---

## Quick Diagnostics

### First Response Commands

Run these commands to quickly assess cluster health:

```bash
#!/bin/bash
# quick-diagnostic.sh

echo "=== Node Status ==="
nodetool status

echo -e "\n=== Ring Health ==="
nodetool describecluster | head -30

echo -e "\n=== Thread Pool Status ==="
nodetool tpstats | grep -E "Pool|Active|Pending|Blocked"

echo -e "\n=== Dropped Messages ==="
nodetool tpstats | grep -i dropped | grep -v "^0"

echo -e "\n=== Compaction Status ==="
nodetool compactionstats | head -20

echo -e "\n=== Recent Errors ==="
tail -100 /var/log/cassandra/system.log | grep -i "error\|exception\|warn" | tail -20
```

### Cluster State Quick Check

| Check | Command | Healthy State |
|-------|---------|---------------|
| All nodes up | `nodetool status` | All UN (Up Normal) |
| Schema agreement | `nodetool describecluster` | Single schema version |
| No dropped messages | `nodetool tpstats` | All zeros |
| Compaction healthy | `nodetool compactionstats` | <50 pending |

---

## Node Issues

### Node Won't Start

**Symptoms:** Cassandra process fails to start or crashes immediately

**Diagnostic steps:**

```bash
# Check system log for startup errors
tail -200 /var/log/cassandra/system.log | grep -i "error\|exception\|fatal"

# Check if port is already in use
netstat -tlnp | grep -E "7000|9042|7199"

# Check disk space
df -h /var/lib/cassandra

# Check file permissions
ls -la /var/lib/cassandra/
ls -la /var/log/cassandra/

# Check JVM can allocate heap
java -Xmx16G -version 2>&1
```

**Common causes and solutions:**

| Cause | Log Pattern | Solution |
|-------|-------------|----------|
| Port in use | "Address already in use" | Kill existing process or change ports |
| Insufficient disk | "No space left on device" | Free disk space or add storage |
| Permission denied | "Permission denied" | Fix ownership: `chown -R cassandra:cassandra /var/lib/cassandra` |
| Corrupt commit log | "CommitLog" + "corrupt" | Remove corrupt segment (data loss risk) |
| Heap allocation failure | "Could not reserve enough space" | Reduce heap or add memory |
| Schema corruption | "Schema" + "cannot" | Restore from backup or repair schema |

**Commit log corruption recovery:**

```bash
# WARNING: May cause data loss for unflushed writes
# Identify corrupt segment
ls -la /var/lib/cassandra/commitlog/

# Move corrupt segment
mv /var/lib/cassandra/commitlog/CommitLog-*.log /tmp/corrupt_commitlog/

# Restart Cassandra
sudo systemctl start cassandra
```

### Node Unresponsive (Hung)

**Symptoms:** Node running but not responding to queries or nodetool

**Diagnostic steps:**

```bash
# Check if process is running
ps aux | grep cassandra

# Check GC activity
tail -50 /var/log/cassandra/gc.log

# Generate thread dump
kill -3 $(pgrep -f CassandraDaemon)
# Or: jstack $(pgrep -f CassandraDaemon) > /tmp/thread_dump.txt

# Check system resources
top -p $(pgrep -f CassandraDaemon)
iostat -x 1 5
```

**Common causes:**

| Cause | Indicators | Solution |
|-------|------------|----------|
| GC storm | Long GC pauses in gc.log | Reduce heap, tune GC, reduce load |
| Thread starvation | Blocked threads in dump | Identify contention, increase pool |
| Disk I/O saturation | High iowait in top | Reduce load, faster storage |
| Network partition | Gossip timeouts in log | Check network connectivity |

### Node Marked Down (DN)

**Symptoms:** Node shows DN in `nodetool status` from other nodes' perspective

**Diagnostic steps:**

```bash
# On "down" node - check if it thinks it's up
nodetool status

# Check gossip state
nodetool gossipinfo

# Check network from other nodes
nc -zv <down_node_ip> 7000
nc -zv <down_node_ip> 9042

# Check firewall
iptables -L -n

# Check for gossip issues in log
grep -i gossip /var/log/cassandra/system.log | tail -50
```

**Common causes:**

| Cause | Solution |
|-------|----------|
| Network partition | Resolve network issue |
| Firewall blocking | Open ports 7000, 7001, 9042 |
| GC pauses causing timeouts | Tune GC |
| phi_convict_threshold too low | Increase threshold (rare) |

---

## Performance Issues

### High Read Latency

**Symptoms:** P99 read latency exceeds SLA, slow queries

**Diagnostic steps:**

```bash
# Check latency by table
nodetool tablestats <keyspace> | grep -A 15 "Table:"

# Check tombstone counts
nodetool tablestats <keyspace>.<table> | grep -i tombstone

# Check SSTable count
nodetool tablestats <keyspace>.<table> | grep "SSTable count"

# Check partition sizes
nodetool tablehistograms <keyspace> <table>

# Check bloom filter effectiveness
nodetool tablestats <keyspace>.<table> | grep -i bloom
```

**Common causes and solutions:**

| Cause | Indicator | Solution |
|-------|-----------|----------|
| Too many SSTables | SSTable count >20 (STCS) | Force compaction, adjust strategy |
| Excessive tombstones | Tombstones/read >1000 | Reduce deletes, force compaction |
| Large partitions | Partition size >100MB | Redesign data model |
| Poor bloom filter | False positive >10% | Increase bloom filter FP chance |
| Cold cache | Low key cache hits | Warm cache, increase size |
| GC pauses | P99 latency spikes | Tune GC |

### High Write Latency

**Symptoms:** P99 write latency exceeds SLA, timeouts

**Diagnostic steps:**

```bash
# Check commit log disk
df -h /var/lib/cassandra/commitlog
iostat -x 1 5

# Check memtable flush rate
nodetool tpstats | grep -i memtable

# Check mutation stage
nodetool tpstats | grep -i mutation

# Check hints accumulation
ls -la /var/lib/cassandra/hints/
```

**Common causes and solutions:**

| Cause | Indicator | Solution |
|-------|-----------|----------|
| Commit log disk slow | High iowait | Use faster disk, separate disk |
| Memtable flush backlog | Pending memtable flushes | Increase flush writers |
| Compaction backlog | Pending compactions >100 | Increase compaction throughput |
| Hints accumulation | Large hints directory | Investigate down nodes |
| Batch too large | Batch size warnings | Reduce batch size |

### Dropped Messages

**Symptoms:** Non-zero dropped messages in `nodetool tpstats`

```bash
# Check which message types are dropped
nodetool tpstats | grep -i dropped

# Message types:
# MUTATION - Write requests dropped
# READ - Read requests dropped
# RANGE_SLICE - Range query requests dropped
# REQUEST_RESPONSE - Response to coordinator dropped
```

**Interpretation:**

| Message Type | Meaning | Common Cause |
|--------------|---------|--------------|
| MUTATION | Writes not processed in time | Overload, disk slow |
| READ | Reads not processed in time | Overload, compaction |
| RANGE_SLICE | Range queries dropped | Large scans, overload |
| REQUEST_RESPONSE | Responses dropped | Network, overload |

**Solutions:**

```yaml
# Increase timeouts (cassandra.yaml)
read_request_timeout_in_ms: 10000
write_request_timeout_in_ms: 5000

# Or reduce load on cluster
# Or add capacity
```

---

## Cluster Issues

### Schema Disagreement

**Symptoms:** Multiple schema versions in `nodetool describecluster`

**Diagnostic steps:**

```bash
# Check schema versions
nodetool describecluster

# Identify which nodes have which version
nodetool describecluster | grep -A 100 "Schema versions"

# Check for pending schema changes
grep -i schema /var/log/cassandra/system.log | tail -50
```

**Solutions:**

```bash
# Usually resolves automatically - wait 30 seconds

# If persistent, restart problematic nodes
# (one at a time)

# Force schema refresh
nodetool resetlocalschema  # Cassandra 4.0+

# Last resort - rolling restart of cluster
```

### Gossip Issues

**Symptoms:** Nodes don't see each other, split cluster

**Diagnostic steps:**

```bash
# Check gossip state
nodetool gossipinfo

# Check for gossip errors
grep -i gossip /var/log/cassandra/system.log | grep -i "error\|fail" | tail -20

# Verify seed connectivity
nc -zv <seed_ip> 7000
```

**Common causes:**

| Cause | Solution |
|-------|----------|
| Network partition | Resolve network issue |
| Seed nodes down | Ensure seeds are up |
| Firewall | Open port 7000 between nodes |
| Different cluster names | Fix cassandra.yaml |

### Inconsistent Data (Read Repair Failures)

**Symptoms:** Different data returned for same query, repair errors

**Diagnostic steps:**

```bash
# Check repair history
nodetool netstats | grep -i repair

# Run consistency check
nodetool verify <keyspace> <table>

# Check for read repair errors
grep -i "read repair" /var/log/cassandra/system.log | tail -20
```

**Solutions:**

```bash
# Run full repair
nodetool repair -full <keyspace>

# For specific table
nodetool repair <keyspace> <table>
```

---

## Storage Issues

### Disk Space Exhaustion

**Symptoms:** Writes failing, "No space left on device" errors

**Immediate actions:**

```bash
# Check disk usage
df -h /var/lib/cassandra

# Find large files
du -sh /var/lib/cassandra/*
du -sh /var/lib/cassandra/data/*/*

# Clear snapshots
nodetool clearsnapshot

# Clear old commit logs (if already flushed)
ls -la /var/lib/cassandra/commitlog/
```

**Longer-term solutions:**

```bash
# Run cleanup to remove data no longer owned
nodetool cleanup

# Drop unused snapshots
nodetool listsnapshots
nodetool clearsnapshot -t <snapshot_name>

# Compact to reclaim tombstone space
nodetool compact <keyspace> <table>

# Add storage or nodes
```

### SSTable Corruption

**Symptoms:** Read errors, "CorruptSSTableException" in logs

**Diagnostic steps:**

```bash
# Identify corrupt SSTable from error
grep -i corrupt /var/log/cassandra/system.log

# Verify SSTable
sstableverify <keyspace> <table>

# Check specific SSTable
tools/bin/sstablemetadata <sstable_path>
```

**Solutions:**

```bash
# If other replicas exist (RF > 1)
# Remove corrupt SSTable and repair
rm <corrupt_sstable>*  # Remove all components
nodetool repair <keyspace> <table>

# If no other replicas
# Try scrubbing (may lose some data)
nodetool scrub <keyspace> <table>
```

### Commit Log Issues

**Symptoms:** Startup failures mentioning commit log

**Solutions:**

```bash
# If commit log corrupt and data can be rebuilt from replicas
# Move corrupt segments
mkdir /tmp/corrupt_commitlog
mv /var/lib/cassandra/commitlog/CommitLog-7-*.log /tmp/corrupt_commitlog/

# Restart and repair
sudo systemctl start cassandra
nodetool repair
```

!!! danger "Data Loss Risk"
    Removing commit log segments loses any writes not yet flushed to SSTables. Only do this if data can be recovered from other replicas.

---

## Repair Issues

### Repair Stuck or Slow

**Symptoms:** Repair running for excessive time, no progress

**Diagnostic steps:**

```bash
# Check repair status
nodetool netstats | grep -i repair

# Check for streaming
nodetool netstats | grep -i stream

# Check thread pools
nodetool tpstats | grep -i repair
```

**Solutions:**

```bash
# Stop stuck repair
nodetool stop REPAIR

# Check for network issues between nodes
nc -zv <other_node> 7000

# Reduce repair scope
# Instead of full keyspace repair:
nodetool repair <keyspace> <single_table>

# Use parallel repair for faster completion
nodetool repair -par <keyspace>
```

### Repair Failures

**Symptoms:** "Repair session failed" errors

**Common causes:**

| Error | Cause | Solution |
|-------|-------|----------|
| "Connection refused" | Node down | Ensure all nodes up |
| "Timeout" | Network or load | Increase timeout, reduce load |
| "Out of memory" | Too many ranges | Reduce scope, increase heap |
| "Anti-compaction" | Incremental repair issue | Use full repair |

---

## Memory Issues

### OutOfMemoryError

**Symptoms:** OOM errors in logs, node crashes

**Diagnostic steps:**

```bash
# Check heap usage before OOM
grep -i "heap\|memory" /var/log/cassandra/system.log | tail -50

# Check for large allocations
grep -i "allocat" /var/log/cassandra/debug.log | tail -50

# Analyze heap dump if generated
jmap -histo $(pgrep -f CassandraDaemon) | head -30
```

**Common causes and solutions:**

| Cause | Indicator | Solution |
|-------|-----------|----------|
| Heap too small | Frequent full GCs | Increase heap |
| Large partitions | Query timeouts before OOM | Redesign data model |
| Too many tombstones | Tombstone warnings | Reduce deletes, compact |
| Memory leak | Gradual heap growth | Upgrade Cassandra |
| Off-heap exhaustion | Native memory errors | Reduce off-heap usage |

### GC Pressure

**Symptoms:** Long GC pauses, high GC CPU usage

**Diagnostic steps:**

```bash
# Check GC statistics
nodetool gcstats

# Analyze GC log
grep "pause" /var/log/cassandra/gc.log | tail -20

# Check for long pauses
grep -E "pause.*[0-9]{4,}ms" /var/log/cassandra/gc.log
```

**Solutions:**

```bash
# Reduce heap if >32GB
# jvm-server.options
-Xms24G
-Xmx24G

# Tune G1GC
-XX:MaxGCPauseMillis=300
-XX:InitiatingHeapOccupancyPercent=70

# Reduce memory pressure
# - Smaller partitions
# - Fewer tombstones
# - Lower concurrent queries
```

---

## Network Issues

### Inter-Node Connectivity Problems

**Symptoms:** Nodes marking each other down, streaming failures

**Diagnostic steps:**

```bash
# Test connectivity
nc -zv <other_node> 7000  # Storage
nc -zv <other_node> 7001  # SSL storage
nc -zv <other_node> 7199  # JMX

# Check for TCP issues
netstat -s | grep -i "retransmit\|timeout"

# Check MTU issues
ping -M do -s 1472 <other_node>
```

**Solutions:**

| Issue | Solution |
|-------|----------|
| Firewall blocking | Open ports 7000, 7001, 9042 |
| MTU mismatch | Set consistent MTU across network |
| Network saturation | Increase bandwidth, throttle streaming |
| TCP timeouts | Tune kernel TCP settings |

### Client Connection Issues

**Symptoms:** Client can't connect, connection timeouts

**Diagnostic steps:**

```bash
# Check native transport
nodetool status | grep -i native

# Test from client machine
nc -zv <cassandra_node> 9042

# Check connection limits
nodetool clientstats

# Check for connection errors
grep -i "native\|connect" /var/log/cassandra/system.log | grep -i error
```

**Solutions:**

```yaml
# cassandra.yaml - ensure native transport enabled
start_native_transport: true

# Check rpc_address (should be reachable IP)
rpc_address: 0.0.0.0
broadcast_rpc_address: <public_ip>
```

---

## AxonOps Troubleshooting Support

Diagnosing Cassandra issues requires correlating metrics, logs, and cluster state across multiple nodes. [AxonOps](https://axonops.com) provides integrated troubleshooting capabilities.

### Centralized Diagnostics

AxonOps provides:

- **Unified log view**: Search and correlate logs across all nodes
- **Metric correlation**: Overlay metrics with events and errors
- **Historical analysis**: Compare current state to past baselines
- **Alert context**: See related metrics when alerts fire

### Automated Issue Detection

- **Anomaly detection**: ML-based identification of unusual patterns
- **Root cause suggestions**: Guidance based on symptom patterns
- **Impact analysis**: Understand which services are affected
- **Runbook integration**: Link alerts to resolution procedures

### Troubleshooting Workflows

- **Guided diagnostics**: Step-by-step investigation workflows
- **Comparison tools**: Compare nodes to identify outliers
- **Timeline reconstruction**: Build sequence of events leading to issues
- **Knowledge base**: Access to common issues and solutions

See the [AxonOps documentation](../../../monitoring/overview.md) for troubleshooting features.

---

## Emergency Procedures

### Node Recovery Priority

1. **Assess scope**: How many nodes affected?
2. **Maintain quorum**: Ensure RF/2+1 nodes per DC remain up
3. **Stop the bleeding**: Prevent additional failures
4. **Communicate**: Alert stakeholders
5. **Recover**: Bring nodes back or replace

### Emergency Contacts

Document these for your organization:

- On-call DBA/SRE contact
- Infrastructure team contact
- Application team contacts
- Management escalation path

### Data Loss Scenarios

| Scenario | Risk | Recovery |
|----------|------|----------|
| Single node loss | Low (RF>1) | Replace node, repair |
| Rack loss | Low-Medium | Replace nodes, repair |
| DC loss | Medium | Failover to other DC |
| All replicas lost | High | Restore from backup |

---

## Best Practices

### Proactive Troubleshooting

1. **Monitor continuously**: Detect issues before users report
2. **Establish baselines**: Know what "normal" looks like
3. **Document incidents**: Build knowledge base
4. **Practice recovery**: Regular DR drills

### During Incidents

1. **Don't panic**: Methodical troubleshooting is faster
2. **Gather data first**: Collect logs and metrics before changing things
3. **One change at a time**: Avoid confusing multiple changes
4. **Document actions**: Track what was tried and results

### Post-Incident

1. **Root cause analysis**: Understand why it happened
2. **Prevent recurrence**: Implement fixes
3. **Update runbooks**: Capture new knowledge
4. **Share learnings**: Team awareness

---

## Related Documentation

- **[Monitoring](../monitoring/index.md)** - Metrics for diagnostics
- **[Performance Tuning](../performance/index.md)** - Resolving performance issues
- **[Cluster Management](../cluster-management/index.md)** - Node operations
- **[Repair Operations](../repair/index.md)** - Repair troubleshooting
- **[Backup & Restore](../backup-restore/index.md)** - Recovery procedures
