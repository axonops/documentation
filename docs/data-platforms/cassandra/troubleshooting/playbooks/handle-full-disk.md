---
title: "Cassandra Handle Full Disk"
description: "Full disk troubleshooting playbook. Handle disk space emergencies."
meta:
  - name: keywords
    content: "full disk troubleshooting, disk space, storage emergency"
---

# Handle Full Disk

A full disk is a critical emergency that can cause data loss, node failures, and cluster instability. Immediate action is required.

---

## Symptoms

- Write failures with "No space left on device"
- Cassandra process crashes or refuses to start
- Compaction failures
- Commit log segment allocation failures
- Node becomes unavailable

---

## Immediate Response

### Step 1: Assess Situation

```bash
# Check disk usage
df -h /var/lib/cassandra

# Check what's consuming space
du -sh /var/lib/cassandra/*
```

### Step 2: Stop Writes (If Possible)

```bash
# Disable binary protocol to stop client writes
nodetool disablebinary

# Disable gossip to prevent coordinator traffic
nodetool disablegossip
```

### Step 3: Quick Space Recovery

**Option A: Clear snapshots (fastest, usually safe)**

```bash
# List snapshots
nodetool listsnapshots

# Clear all snapshots
nodetool clearsnapshot --all

# Check recovered space
df -h /var/lib/cassandra
```

**Option B: Clear old hints (if hints are large)**

```bash
# Check hints size
du -sh /var/lib/cassandra/hints

# Truncate hints (some data loss risk during node down scenarios)
nodetool truncatehints
```

**Option C: Clear saved caches**

```bash
rm -rf /var/lib/cassandra/saved_caches/*
```

### Step 4: Verify Recovery

```bash
df -h /var/lib/cassandra
# Should show < 90% usage for safe operation
```

### Step 5: Re-enable Operations

```bash
nodetool enablegossip
nodetool enablebinary
```

---

## Diagnosis

### What's Using Space?

```bash
# Detailed breakdown
du -h /var/lib/cassandra/data/* | sort -h | tail -20

# Snapshots
du -sh /var/lib/cassandra/data/*/*/snapshots/* 2>/dev/null | sort -h | tail -10

# Commitlog
du -sh /var/lib/cassandra/commitlog

# Hints
du -sh /var/lib/cassandra/hints
```

### Identify Large Tables

```bash
# Size per table
nodetool tablestats 2>/dev/null | grep -E "Table:|Space used" | paste - - | sort -t: -k3 -h | tail -20
```

### Check for Snapshot Accumulation

```bash
nodetool listsnapshots
```

Old snapshots from backups, repairs, or schema changes accumulate over time.

---

## Resolution by Cause

### Cause 1: Snapshot Accumulation

**Clear specific snapshots:**
```bash
# Clear snapshot by name
nodetool clearsnapshot -t snapshot_name

# Clear all snapshots
nodetool clearsnapshot --all
```

**Clear snapshots for specific keyspace:**
```bash
nodetool clearsnapshot -t snapshot_name -- my_keyspace
```

### Cause 2: Failed Compaction

Compaction needs temporary space. If disk filled mid-compaction:

```bash
# Clear snapshots first
nodetool clearsnapshot --all

# Reduce compaction parallelism
nodetool setconcurrentcompactors 1

# Reduce compaction throughput
nodetool setcompactionthroughput 32
```

### Cause 3: Large Table Growth

```bash
# Identify growing tables
nodetool tablestats my_keyspace | grep -E "Table:|Space used"

# Consider:
# 1. Add nodes to distribute data
# 2. Implement TTLs
# 3. Archive old data
```

### Cause 4: Commitlog Growth

```bash
# Check commitlog
du -sh /var/lib/cassandra/commitlog/*

# Force flush to reduce commitlog
nodetool flush

# If commitlog is blocking startup, may need to clear
# WARNING: DATA LOSS - unflushed data will be lost
# sudo rm /var/lib/cassandra/commitlog/*
```

### Cause 5: Hints Accumulation

Hints accumulate when nodes are down:

```bash
# Check hints
du -sh /var/lib/cassandra/hints

# Truncate hints (loses hints data)
nodetool truncatehints

# Fix underlying node issues
nodetool status  # All should be UN
```

---

## Emergency Procedures

### Cannot Start Cassandra Due to Full Disk

```bash
# 1. Clear snapshots manually
rm -rf /var/lib/cassandra/data/*/*/snapshots/*

# 2. Clear saved caches
rm -rf /var/lib/cassandra/saved_caches/*

# 3. If still full, reduce commitlog
# WARNING: Potential data loss
rm /var/lib/cassandra/commitlog/*

# 4. Try starting
sudo systemctl start cassandra
```

### Multiple Nodes Full

Indicates cluster capacity issue:

1. Add temporary disk capacity if possible
2. Clear snapshots on all nodes
3. Plan capacity expansion urgently
4. Consider emergency node additions

---

## Prevention

### Monitoring

Set up alerts:

| Metric | Warning | Critical |
|--------|---------|----------|
| Disk usage | > 70% | > 85% |
| Disk growth rate | Unusual spike | - |

### Automated Cleanup

```bash
#!/bin/bash
# cleanup_snapshots.sh - Run periodically

# Clear snapshots older than 7 days
find /var/lib/cassandra/data -path '*/snapshots/*' -mtime +7 -delete

# Report disk usage
df -h /var/lib/cassandra | mail -s "Cassandra disk report" admin@example.com
```

### Configuration

```yaml
# cassandra.yaml

# Auto-snapshot before DROP/TRUNCATE
auto_snapshot: true

# Limit hints storage
max_hints_file_size_in_mb: 128
hints_flush_period_in_ms: 10000
max_hints_delivery_threads: 2
```

### Capacity Planning

| Data Growth | Action |
|-------------|--------|
| < 5% per month | Monitor |
| 5-10% per month | Plan expansion |
| > 10% per month | Expand immediately |

**Rule of thumb:** Keep disk usage below 50% to allow for:
- Compaction temporary space
- Growth headroom
- Emergency buffer

---

## Recovery Verification

```bash
# Verify disk space
df -h /var/lib/cassandra

# Verify node health
nodetool status
nodetool info

# Verify compaction can run
nodetool compactionstats

# Verify writes work
cqlsh -e "INSERT INTO system_auth.roles (role) VALUES ('test_write');"
cqlsh -e "DELETE FROM system_auth.roles WHERE role = 'test_write';"
```

---

## Space Requirements

### Minimum Free Space

| Component | Requirement |
|-----------|-------------|
| Compaction | 50% of largest SSTable |
| Repair | Variable, can be significant |
| Normal operations | 20% free recommended |
| Safe operating range | < 70% used |

### Estimation

```bash
# Current usage
df -h /var/lib/cassandra

# Data size
nodetool tablestats 2>/dev/null | grep "Space used (total)" | awk '{sum+=$5} END {print sum/1024/1024/1024 " GB"}'

# Snapshot size
du -sh /var/lib/cassandra/data/*/*/snapshots/* 2>/dev/null | awk '{sum+=$1} END {print sum " total in snapshots"}'
```

---

## Related Issues

| Problem | Playbook |
|---------|----------|
| Compaction failing | [Compaction Issues](compaction-issues.md) |
| Node down | [Replace Dead Node](replace-dead-node.md) |
| OOM related to disk | [Recover from OOM](recover-from-oom.md) |

## Related Commands

| Command | Purpose |
|---------|---------|
| `nodetool clearsnapshot` | Remove snapshots |
| `nodetool listsnapshots` | List snapshots |
| `nodetool truncatehints` | Clear hints |
| `nodetool flush` | Flush memtables |
| `nodetool disablebinary` | Stop client connections |