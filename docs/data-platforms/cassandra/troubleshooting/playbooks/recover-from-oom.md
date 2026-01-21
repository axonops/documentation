---
title: "Cassandra Recover from OOM"
description: "OOM recovery troubleshooting playbook. Recover from out-of-memory crashes."
meta:
  - name: keywords
    content: "OOM recovery, out of memory, crash recovery"
search:
  boost: 3
---

# Recover from OOM

OutOfMemoryError (OOM) crashes occur when the JVM exhausts available heap memory. This playbook covers immediate recovery and prevention.

---

## Symptoms

- Cassandra process terminated unexpectedly
- `OutOfMemoryError` in system.log
- Linux OOM killer messages in dmesg
- Node shows as DOWN in cluster

---

## Immediate Recovery

### Step 1: Confirm OOM Was the Cause

```bash
# Check dmesg for OOM killer
dmesg | grep -i "killed process\|oom"

# Check Cassandra logs
grep -i "outofmemory\|heap space\|gc overhead" /var/log/cassandra/system.log | tail -20
```

### Step 2: Check Node Status

```bash
# Is process running?
ps aux | grep cassandra

# Service status
systemctl status cassandra
```

### Step 3: Restart Cassandra

```bash
sudo systemctl start cassandra

# Monitor startup
tail -f /var/log/cassandra/system.log
```

### Step 4: Verify Node Rejoins

```bash
# From another node
nodetool status

# Wait for UN status
```

---

## Diagnosis

### Identify OOM Cause

Check logs for what was happening before OOM:

```bash
# Look at activity before crash
grep -B 50 "OutOfMemory" /var/log/cassandra/system.log | head -100

# Common patterns:
# - Large partition reads
# - Compaction
# - Repair
# - Batch operations
```

### Check Heap Configuration

```bash
# Current settings
grep -E "^-Xm|^-XX:.*Heap" /etc/cassandra/jvm.options
```

### Check What Consumed Memory

If heap dump exists:

```bash
# Location depends on configuration
ls -la /var/lib/cassandra/*.hprof

# Analyze with Eclipse MAT or similar tool
```

---

## Common OOM Causes and Fixes

### Cause 1: Large Partition Read

**Symptom:** OOM during read operation

```bash
grep -i "large partition" /var/log/cassandra/system.log
```

**Fix:** See [Large Partition Issues](large-partition.md)

```bash
# Immediate: Reduce concurrent reads
nodetool setconcurrency read 8
```

### Cause 2: Compaction

**Symptom:** OOM during compaction

```bash
grep -i "compacting" /var/log/cassandra/system.log | tail -20
```

**Fix:**

```bash
# Reduce compaction memory usage
# In cassandra.yaml
compaction_large_partition_warning_threshold_mb: 100

# Reduce concurrent compactors
nodetool setconcurrentcompactors 1
```

### Cause 3: Repair

**Symptom:** OOM during repair (Merkle tree building)

**Fix:**

```bash
# Reduce repair scope
nodetool repair -pr my_keyspace my_table  # One table at a time

# Or reduce Merkle tree depth
# In cassandra.yaml
repair_session_max_tree_depth: 16  # Default 20
```

### Cause 4: Batch Operations

**Symptom:** OOM during large batch writes

**Fix:**

- Reduce batch sizes in application
- Use unlogged batches for non-atomic operations

### Cause 5: Heap Too Small

**Symptom:** Frequent OOMs under normal load

**Fix:**

```bash
# In jvm.options
-Xms8G
-Xmx8G
```

### Cause 6: Heap Too Large

**Symptom:** OOM after long GC pauses

**Fix:** Counterintuitively, reducing heap can help:

```bash
# In jvm.options
-Xms8G
-Xmx8G
# Generally don't exceed 16GB
```

---

## Prevention Configuration

### jvm.options

```bash
# Heap sizing (8GB is often optimal)
-Xms8G
-Xmx8G

# Heap dump on OOM (for analysis)
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/lib/cassandra/

# Exit on OOM (allows systemd to restart)
-XX:+ExitOnOutOfMemoryError

# Or crash on OOM (creates core dump)
# -XX:+CrashOnOutOfMemoryError
```

### cassandra.yaml

```yaml
# Limit compaction memory
compaction_large_partition_warning_threshold_mb: 100

# Limit repair memory
repair_session_max_tree_depth: 18
repair_session_space_in_mb: 256

# Limit memtable size
memtable_heap_space_in_mb: 2048
memtable_offheap_space_in_mb: 2048
```

---

## Monitoring for OOM Prevention

### Key Metrics to Watch

| Metric | Warning | Critical |
|--------|---------|----------|
| Heap usage | > 70% | > 85% |
| GC pause time | > 500ms | > 2000ms |
| GC frequency | Every few seconds | Constant |

### Monitoring Commands

```bash
# Watch heap usage
watch -n 10 'nodetool info | grep -i heap'

# Watch GC
watch -n 30 'nodetool gcstats'
```

### Alert Configuration

Set alerts for:
- Heap usage > 80%
- GC time > 1 second
- OOM errors in logs

---

## Recovery Verification

### Verify Node Health

```bash
# Node status
nodetool status

# Heap usage after restart
nodetool info | grep Heap

# GC behavior
nodetool gcstats
```

### Verify Data Consistency

```bash
# After OOM, consider running repair
nodetool repair -pr my_keyspace
```

---

## Emergency Procedures

### If Node Won't Start After OOM

```bash
# Check for corrupted commitlog
ls -la /var/lib/cassandra/commitlog/

# If suspected corruption, can skip commitlog (DATA LOSS!)
# Only as last resort:
# sudo rm /var/lib/cassandra/commitlog/*
# Then start Cassandra
```

### If Multiple Nodes OOM

```bash
# Start nodes one at a time
# Allow each to fully join before starting next
# May indicate cluster-wide issue (bad query, data model)
```

---

## Best Practices

| Practice | Implementation |
|----------|----------------|
| Set heap appropriately | 8GB for most workloads |
| Enable OOM handling | `-XX:+ExitOnOutOfMemoryError` |
| Generate heap dumps | `-XX:+HeapDumpOnOutOfMemoryError` |
| Monitor heap usage | Alert at 75% |
| Limit partition sizes | Design for < 100MB |
| Regular compaction | Keep SSTable count low |

---

## Related Issues

| Problem | Playbook |
|---------|----------|
| Large partitions | [Large Partition Issues](large-partition.md) |
| GC problems | [GC Pause Issues](gc-pause.md) |
| General memory | [High Memory Usage](high-memory.md) |
| Disk full | [Handle Full Disk](handle-full-disk.md) |

## Related Commands

| Command | Purpose |
|---------|---------|
| `nodetool info` | Check heap usage |
| `nodetool gcstats` | GC statistics |
| `nodetool setconcurrency` | Reduce concurrent operations |
| `nodetool setconcurrentcompactors` | Reduce compaction parallelism |
