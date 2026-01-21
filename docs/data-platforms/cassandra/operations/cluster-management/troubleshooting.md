---
title: "Cassandra Cluster Management Troubleshooting"
description: "Diagnose and resolve Cassandra topology operation issues. Bootstrap, decommission, and streaming problems."
meta:
  - name: keywords
    content: "Cassandra troubleshooting, bootstrap failed, decommission stuck, streaming issues"
search:
  boost: 3
---

# Cluster Management Troubleshooting

This guide covers diagnosis and resolution of common issues during topology operations.

---

## Diagnostic Commands

### Essential Commands

```bash
# Cluster state
nodetool status

# Streaming status
nodetool netstats

# Schema agreement
nodetool describecluster

# Gossip state
nodetool gossipinfo

# Active operations
nodetool compactionstats
```

### Log Analysis

```bash
# Recent errors
grep -i "error\|exception\|failed" /var/log/cassandra/system.log | tail -50

# Streaming issues
grep -i stream /var/log/cassandra/system.log | tail -50

# Bootstrap/decommission
grep -i "bootstrap\|decommission\|leaving\|joining" /var/log/cassandra/system.log | tail -50
```

---

## Bootstrap Issues

### Node Won't Join Cluster

**Symptoms:** New node starts but doesn't appear in `nodetool status`

**Diagnostic steps:**

```bash
# Check if Cassandra is running
sudo systemctl status cassandra

# Check for startup errors
tail -100 /var/log/cassandra/system.log | grep -i error

# Verify network connectivity to seeds
nc -zv <seed_ip> 7000
nc -zv <seed_ip> 9042
```

**Common causes and solutions:**

| Cause | Diagnosis | Solution |
|-------|-----------|----------|
| Cluster name mismatch | `grep cluster_name cassandra.yaml` | Fix name, clear data, restart |
| Seeds unreachable | `nc -zv seed 7000` fails | Check firewall, network |
| Wrong listen_address | Check logs for binding errors | Fix `listen_address` in yaml |
| Data directory not empty | Check `/var/lib/cassandra/data` | Clear data directories |
| Schema disagreement | `nodetool describecluster` shows multiple versions | Wait or restart seeds |

```bash
# Clear data for fresh start
sudo systemctl stop cassandra
sudo rm -rf /var/lib/cassandra/data/*
sudo rm -rf /var/lib/cassandra/commitlog/*
sudo rm -rf /var/lib/cassandra/saved_caches/*
sudo systemctl start cassandra
```

### Bootstrap Stalled

**Symptoms:** Node shows `UJ` (Joining) for extended period, streaming shows no progress

**Diagnostic steps:**

```bash
# Check streaming progress
nodetool netstats

# Look for streaming errors
grep -i "stream.*error\|stream.*failed" /var/log/cassandra/system.log

# Check source nodes
nodetool status
```

**Common causes and solutions:**

| Cause | Diagnosis | Solution |
|-------|-----------|----------|
| Source node overloaded | High CPU/IO on source | Wait or reduce stream throughput |
| Network issues | Packet loss, timeouts in logs | Fix network |
| Large partitions | Timeout errors in logs | Increase `streaming_socket_timeout_in_ms` |
| Disk full | Check `df -h` | Free space |

```yaml
# cassandra.yaml - increase timeouts for large partitions
streaming_socket_timeout_in_ms: 86400000  # 24 hours
```

### Bootstrap Failed Mid-Way

**Symptoms:** Node crashed or was stopped during bootstrap

**Recovery:**

```bash
# Clear partial data and retry
sudo systemctl stop cassandra
sudo rm -rf /var/lib/cassandra/data/*
sudo rm -rf /var/lib/cassandra/commitlog/*
sudo rm -rf /var/lib/cassandra/saved_caches/*
sudo systemctl start cassandra
```

---

## Decommission Issues

### Decommission Stuck

**Symptoms:** Node remains in `UL` (Leaving) state for extended period

**Diagnostic steps:**

```bash
# Check streaming progress
nodetool netstats

# Look for target node issues
nodetool status

# Check logs
grep -i "decommission\|stream" /var/log/cassandra/system.log | tail -50
```

**Common causes and solutions:**

| Cause | Diagnosis | Solution |
|-------|-----------|----------|
| Target nodes unavailable | `nodetool status` shows DN | Fix target nodes |
| Network issues | Streaming errors in logs | Fix network |
| Target disk full | Check target `df -h` | Free space on targets |
| Streaming throttled | Low throughput in `netstats` | Increase stream throughput |

!!! warning "Cannot Cancel Decommission"
    Once decommission starts, it must complete. If truly stuck:

    1. Try waiting longer (decommission can take many hours)
    2. Fix underlying issues (network, disk, node health)
    3. As last resort: stop the node and use `nodetool removenode` from another node

### Decommission Interrupted

**Symptoms:** Decommissioning node was stopped or crashed

**Recovery options:**

| Scenario | Solution |
|----------|----------|
| Node can be restarted | Restart; decommission should resume |
| Node cannot be restarted | Use `nodetool removenode` from other node |
| Data partially streamed | Run repair after recovery |

---

## Removenode Issues

### Removenode Not Progressing

**Symptoms:** `nodetool removenode status` shows no progress

**Diagnostic steps:**

```bash
# Check removenode status
nodetool removenode status

# Check streaming
nodetool netstats

# Check logs on executing node
grep -i "remove\|stream" /var/log/cassandra/system.log | tail -50
```

**Solutions:**

```bash
# If stuck for > 1 hour with no progress
nodetool removenode force <host_id>

# After force removal, run repair
nodetool repair -full
```

### Wrong Node Removed

**Symptoms:** Accidentally removed wrong node

**Recovery:**

1. If node still has data: restart it (will try to rejoin)
2. If data cleared: add as new node (bootstrap)
3. Run repair to ensure consistency

---

## Replacement Issues

### Replacement Won't Start

**Symptoms:** Node with `replace_address_first_boot` won't start

**Diagnostic steps:**

```bash
# Check for startup errors
tail -100 /var/log/cassandra/system.log | grep -i error

# Verify dead node is recognized
nodetool status  # Should show DN for dead node
```

**Common causes and solutions:**

| Cause | Diagnosis | Solution |
|-------|-----------|----------|
| Dead node not recognized | Not in `nodetool status` as DN | Wait for gossip timeout |
| Wrong IP in replace option | IP mismatch | Correct the JVM option |
| Data directory not empty | Has old data | Clear data directories |
| Version mismatch | Check versions | Install matching version |

### Replacement Streaming Stalled

**Symptoms:** Replacement node stuck in `UJ` state

**Same solutions as bootstrap stalled** (see above)

### Replacement Node Has Wrong Tokens

**Symptoms:** After replacement, node has different token count

**Cause:** `num_tokens` doesn't match dead node

**Solution:**

```bash
# Must restart with correct configuration
sudo systemctl stop cassandra
sudo rm -rf /var/lib/cassandra/data/*

# Fix cassandra.yaml
num_tokens: <match_dead_node>

# Restart
sudo systemctl start cassandra
```

---

## Streaming Issues

### Streaming Timeouts

**Symptoms:** Repeated timeout errors during any topology operation

```bash
# Typical error in logs
ERROR [Stream...] stream/StreamResultFuture.java:...
  Stream failed: java.net.SocketTimeoutException: Read timed out
```

**Solutions:**

```yaml
# cassandra.yaml - increase timeouts
streaming_socket_timeout_in_ms: 86400000  # 24 hours (default: 1 hour)

# For Cassandra 4.0+
stream_entire_sstables: true  # Faster for large files
```

### Streaming Too Slow

**Symptoms:** Topology operations taking excessive time

**Diagnosis:**

```bash
# Check current throughput
nodetool getstreamthroughput

# Check network utilization
iftop -i eth0  # or appropriate interface
```

**Solutions:**

```bash
# Increase streaming throughput (MB/s)
nodetool setstreamthroughput 400  # Default is 200

# Cassandra 4.0+ in cassandra.yaml
stream_entire_sstables: true
```

### Streaming Failures

**Symptoms:** Repeated streaming failures

**Diagnostic steps:**

```bash
# Check for failures
nodetool netstats | grep -i failed

# Check specific errors
grep -i "stream.*failed\|stream.*error" /var/log/cassandra/system.log
```

**Common causes:**

| Cause | Solution |
|-------|----------|
| Network instability | Fix network issues |
| Disk I/O bottleneck | Reduce concurrent streaming |
| Memory pressure | Increase heap or reduce streaming |
| Firewall issues | Open port 7000 between all nodes |

---

## Gossip Issues

### Node Stuck in Gossip

**Symptoms:** Node appears in `nodetool status` but shouldn't (already removed)

**Cause:** Gossip state not properly propagated

**Solutions:**

```bash
# Option 1: Assassinate the stuck node
nodetool assassinate <stuck_node_ip>

# Option 2: If that fails, rolling restart of cluster
# Start with seeds, then other nodes
```

### Schema Disagreement

**Symptoms:** `nodetool describecluster` shows multiple schema versions

**Diagnostic:**

```bash
nodetool describecluster

# Example problematic output:
# Schema versions:
#     abc-123: [10.0.1.1, 10.0.1.2]
#     def-456: [10.0.1.3]  <-- Different!
```

**Solutions:**

1. Wait (schema should converge within minutes)
2. If persists, restart the disagreeing node
3. If still persists, restart seeds

---

## Network Issues

### Port Connectivity Problems

**Verification:**

```bash
# From each node, verify connectivity to all others
for ip in 10.0.1.1 10.0.1.2 10.0.1.3; do
    nc -zv $ip 7000 && echo "$ip:7000 OK" || echo "$ip:7000 FAILED"
    nc -zv $ip 9042 && echo "$ip:9042 OK" || echo "$ip:9042 FAILED"
done
```

**Required ports:**

| Port | Purpose | Required Between |
|------|---------|------------------|
| 7000 | Internode | All nodes |
| 7001 | Internode SSL | All nodes (if SSL) |
| 9042 | Native transport | Clients and nodes |
| 7199 | JMX | Admin hosts |

### Cross-DC Connectivity

For multi-DC setups:

```bash
# Verify cross-DC latency
ping <other_dc_node>

# Should be < 100ms for reasonable performance
# Higher latency impacts streaming and consistency
```

---

## Recovery Procedures

### Node Completely Unrecoverable

If a node cannot be recovered and removenode fails:

```bash
# 1. Try removenode
nodetool removenode <host_id>

# 2. If stuck, force
nodetool removenode force <host_id>

# 3. If still stuck, assassinate
nodetool assassinate <node_ip>

# 4. Run full repair
nodetool repair -full
```

### Cluster Partition (Split Brain)

**Symptoms:** Nodes in different groups can't see each other

**Immediate actions:**

1. Stop writes if possible
2. Identify the partition cause (network, firewall)
3. Restore connectivity
4. Run full repair

```bash
# After connectivity restored
nodetool repair -full
```

---

## Related Documentation

- **[Cluster Management Overview](index.md)** - Operation selection
- **[Adding Nodes](adding-nodes.md)** - Bootstrap procedures
- **[Removing Nodes](removing-nodes.md)** - Removal procedures
- **[Replacing Nodes](replacing-nodes.md)** - Replacement procedures
- **[Repair Operations](../repair/index.md)** - Post-issue repair
