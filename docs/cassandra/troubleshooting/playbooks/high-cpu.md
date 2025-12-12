---
description: "High CPU troubleshooting playbook. Diagnose CPU-bound issues."
meta:
  - name: keywords
    content: "high CPU troubleshooting, CPU issues, performance problems"
---

# High CPU Usage Playbook

## Symptoms

- CPU utilization consistently above 70%
- Slow query response times
- Node performance degradation
- Increased latency across the cluster

## Impact

- **Severity**: Medium to High
- **Services Affected**: All queries to the affected node
- **User Impact**: Increased latency, potential timeouts

---

## Immediate Assessment

### Step 1: Confirm High CPU

```bash
# Check overall CPU usage
top -b -n 1 | head -20

# Check Cassandra process
ps aux | grep -i cassandra

# Check CPU usage over time
sar -u 1 10

# Expected output showing high CPU:
# %user   %nice %system %iowait  %idle
# 75.50    0.00    8.20    2.30   14.00
```

### Step 2: Identify CPU Consumer

```bash
# Cassandra JVM CPU breakdown
top -H -p $(pgrep -f CassandraDaemon)

# Look for:
# - GC threads (high = memory pressure)
# - CompactionExecutor threads
# - ReadStage/MutationStage threads

# Check thread distribution
nodetool tpstats
```

### Step 3: Check for Common Causes

```bash
# 1. Check compaction activity
nodetool compactionstats

# 2. Check for GC pressure
tail -100 /var/log/cassandra/gc.log | grep "pause"

# 3. Check thread pools
nodetool tpstats | grep -E "Pending|Blocked"

# 4. Check for expensive queries
grep -i "slow" /var/log/cassandra/system.log | tail -20
```

---

## Common Causes and Solutions

### Cause 1: Heavy Compaction

**Diagnosis**:
```bash
nodetool compactionstats

# High CPU during compaction:
# Active compactions: 4
# pending tasks: 45
```

**Resolution**:
```bash
# Reduce compaction throughput
nodetool setcompactionthroughput 32  # MB/s

# Reduce concurrent compactors
# Edit cassandra.yaml:
# concurrent_compactors: 1

# For immediate relief (temporary)
nodetool stop COMPACTION
# WARNING: Only temporary, compaction backlog will grow
```

### Cause 2: Garbage Collection

**Diagnosis**:
```bash
# Check GC activity
grep -E "GC pause|Total time" /var/log/cassandra/gc.log | tail -50

# Check heap usage
nodetool info | grep "Heap Memory"

# High GC means heap pressure
```

**Resolution**:
```bash
# Tune GC settings in jvm11-server.options
# -XX:MaxGCPauseMillis=500
# -XX:InitiatingHeapOccupancyPercent=70

# If heap is too small, increase (max 31GB)
# -Xmx16G -Xms16G

# After changes, rolling restart required
```

### Cause 3: High Query Volume

**Diagnosis**:
```bash
# Check request rates
nodetool proxyhistograms

# Check thread pool saturation
nodetool tpstats | grep -E "ReadStage|MutationStage"

# Active or Pending > 0 indicates load
```

**Resolution**:
```bash
# Scale cluster (add nodes)
# Or redirect traffic (load balancer)

# Temporary: Increase thread pool size
# Edit cassandra.yaml:
# concurrent_reads: 64
# concurrent_writes: 64
# Requires restart
```

### Cause 4: Expensive Queries

**Diagnosis**:
```bash
# Check for ALLOW FILTERING or large scans
grep -i "allow filtering\|full scan" /var/log/cassandra/system.log

# Enable slow query logging
# cassandra.yaml: slow_query_log_timeout_in_ms: 500

# Check table statistics for problem tables
nodetool tablestats | grep -A20 "Table: "
```

**Resolution**:
```sql
-- Fix query patterns
-- Instead of ALLOW FILTERING, create proper table

-- Check for missing indexes or bad data model
DESCRIBE TABLE problem_table;

-- Review and optimize queries
TRACING ON;
SELECT * FROM problem_table WHERE ...;
```

### Cause 5: Large Partitions

**Diagnosis**:
```bash
# Check partition sizes
nodetool tablehistograms keyspace table | grep "Partition Size"

# Large partitions cause CPU during reads
# 99th percentile > 100MB indicates problem
```

**Resolution**:
```sql
-- Implement time bucketing
-- Split large partitions
-- See data modeling best practices
```

### Cause 6: Tombstone Scanning

**Diagnosis**:
```bash
# Check tombstone counts
nodetool tablestats keyspace | grep -i tombstone

# Large tombstone counts cause CPU on reads
```

**Resolution**:
```bash
# Run compaction to remove tombstones
nodetool compact keyspace table

# Review delete patterns
# Use TTL instead of explicit deletes
```

---

## Detailed Investigation

### Thread Dump Analysis

```bash
# Take thread dump
jstack $(pgrep -f CassandraDaemon) > /tmp/threaddump_$(date +%s).txt

# Look for:
# - Many threads in RUNNABLE state
# - Threads blocked on locks
# - GC threads consuming CPU

# Analyze hot methods
grep -A 10 "RUNNABLE" /tmp/threaddump_*.txt | head -100
```

### Profile with async-profiler

```bash
# Download async-profiler
wget https://github.com/jvm-profiling-tools/async-profiler/releases/download/v2.9/async-profiler-2.9-linux-x64.tar.gz
tar xzf async-profiler-2.9-linux-x64.tar.gz

# Profile CPU for 60 seconds
./profiler.sh -d 60 -f /tmp/profile.html $(pgrep -f CassandraDaemon)

# Open profile.html in browser to see flame graph
```

### Check for Hot Partitions

```bash
# Enable tracing
cqlsh -e "TRACING ON; SELECT * FROM keyspace.table WHERE partition_key = ?;"

# Look for:
# - High number of rows read
# - Long read time
# - Many SSTables accessed
```

---

## Resolution Steps

### Immediate Actions

```bash
# 1. Reduce compaction impact
nodetool setcompactionthroughput 16

# 2. Check if single node is hot (route traffic away)
nodetool status  # Check load distribution

# 3. If GC-related, restart node (clears heap)
nodetool drain
sudo systemctl restart cassandra
```

### Short-term Fixes

```bash
# 1. Add capacity (if needed)
# Scale horizontally

# 2. Tune thread pools
# cassandra.yaml adjustments

# 3. Optimize queries
# Fix ALLOW FILTERING
# Add appropriate indexes
```

### Long-term Solutions

```bash
# 1. Review and fix data model
# Implement proper partitioning
# Time bucketing for time-series

# 2. Upgrade hardware
# More CPU cores
# Faster storage (NVMe)

# 3. Scale cluster appropriately
# Add nodes before hitting limits
```

---

## Prevention

### Monitoring

```yaml
# Alert on:
- CPU > 60% for 10 minutes (warning)
- CPU > 80% for 5 minutes (critical)
- Pending compactions > 20
- GC pause > 500ms
```

### Capacity Planning

```
Monitor trends:
- CPU utilization over time
- Request rate growth
- Data growth rate

Plan scaling:
- Scale before hitting 70% sustained CPU
- Add nodes in pairs for balance
- Test new capacity in staging
```

### Query Review

```sql
-- Regularly review slow queries
-- Enable slow query logging

-- Audit ALLOW FILTERING usage
grep -r "ALLOW FILTERING" /app/queries/

-- Review data model quarterly
```

---

## Verification

After resolution, verify:

```bash
# CPU returned to normal
top -b -n 1 | grep Cpu

# Latency improved
nodetool proxyhistograms

# Thread pools healthy
nodetool tpstats | grep -E "Pending|Blocked"

# Compaction backlog managed
nodetool compactionstats
```

---

## Related Issues

- **[High Memory Usage](high-memory.md)** - Memory troubleshooting
- **[Slow Queries](slow-queries.md)** - Query optimization
- **[Compaction Issues](compaction-issues.md)** - Compaction troubleshooting

## Next Steps

- **[Performance Tuning](../../operations/performance/index.md)** - Optimization guide
- **[Monitoring Guide](../../operations/monitoring/index.md)** - Set up alerts
- **[Data Modeling](../../data-modeling/index.md)** - Schema design
