---
title: "Cassandra Repair Failures"
description: "Repair failures troubleshooting playbook. Debug failed repair operations."
meta:
  - name: keywords
    content: "repair failures troubleshooting, failed repair, repair issues"
---

# Repair Failures

Repairs synchronize data across replicas to ensure consistency. Repair failures leave data inconsistent and can lead to read inconsistencies.

---

## Symptoms

- `nodetool repair` exits with errors
- Repairs hang indefinitely
- "Repair session failed" in logs
- Incremental repair streams failing
- Long-running repairs that never complete
- OOM during repair

---

## Diagnosis

### Step 1: Check Active Repairs

```bash
nodetool repair_admin list
```

### Step 2: Check Repair History

```bash
# View recent repairs
cqlsh -e "SELECT * FROM system_distributed.repair_history LIMIT 20;"

# Check parent repair sessions
cqlsh -e "SELECT * FROM system_distributed.parent_repair_history LIMIT 10;"
```

### Step 3: Check Logs for Errors

```bash
grep -i "repair\|streaming\|merkle" /var/log/cassandra/system.log | tail -100
```

**Common error patterns:**
- `Repair session failed`
- `Sync failed between`
- `Streaming error`
- `OutOfMemoryError during repair`

### Step 4: Check Resource Usage

```bash
# During repair
top -p $(pgrep -f CassandraDaemon)
iostat -x 1 5
df -h /var/lib/cassandra
```

### Step 5: Check Stream Throughput

```bash
nodetool netstats
```

---

## Resolution

### Case 1: Repair Session Stuck

**Cancel and restart:**

```bash
# List active repairs
nodetool repair_admin list

# Cancel stuck repair
nodetool repair_admin cancel <repair-id>

# Or cancel all repairs on node
nodetool repair_admin cancel --force

# Restart with smaller scope
nodetool repair -pr my_keyspace my_table
```

### Case 2: OOM During Repair

**Reduce repair scope:**

```bash
# Repair one table at a time
nodetool repair -pr my_keyspace table1
nodetool repair -pr my_keyspace table2

# Use subrange repair for large tables
nodetool repair -pr -st <start_token> -et <end_token> my_keyspace
```

**Adjust memory settings:**

```bash
# Reduce merkle tree memory
# In cassandra.yaml
repair_session_max_tree_depth: 18  # Default 20, reduce for large partitions
```

### Case 3: Streaming Failures

**Check network:**

```bash
# Verify streaming ports
nc -zv <peer-node> 7000

# Check streaming throughput limit
nodetool getstreamthroughput
```

**Increase timeouts:**

```yaml
# cassandra.yaml
streaming_socket_timeout_in_ms: 86400000  # 24 hours
streaming_keep_alive_period_in_secs: 300
```

### Case 4: Repair Taking Too Long

**Use parallel repair:**

```bash
# Parallel repair (Cassandra 4.0+)
nodetool repair -pr --parallel my_keyspace
```

**Increase stream throughput:**

```bash
# Check current setting
nodetool getstreamthroughput

# Increase if network allows (MB/s)
nodetool setstreamthroughput 200
```

**Schedule repairs by token range:**

```bash
#!/bin/bash
# Repair in smaller chunks
ranges=$(nodetool describering my_keyspace | grep TokenRange | head -10)
for range in $ranges; do
    start=$(echo $range | cut -d'(' -f2 | cut -d',' -f1)
    end=$(echo $range | cut -d',' -f2 | cut -d')' -f1)
    nodetool repair -st $start -et $end my_keyspace
done
```

### Case 5: Incremental Repair Issues

**Switch to full repair:**

```bash
# Full repair instead of incremental
nodetool repair -full -pr my_keyspace
```

**Reset repair state:**

```bash
# Mark SSTables as unrepaired (use with caution)
nodetool repair_admin cancel --force
sstablerepairedset --really-set --is-unrepaired /var/lib/cassandra/data/my_keyspace/my_table-*/*.db
```

### Case 6: Schema Disagreement Blocking Repair

```bash
# Check schema
nodetool describecluster

# Fix schema disagreement first (see schema-disagreement.md)
nodetool reloadlocalschema

# Then retry repair
nodetool repair -pr my_keyspace
```

---

## Recovery

### Verify Repair Completion

```bash
# Check repair history
cqlsh -e "SELECT * FROM system_distributed.repair_history WHERE keyspace_name = 'my_keyspace' LIMIT 5;"

# Verify no pending repairs
nodetool repair_admin list
```

### Verify Data Consistency

```bash
# Run read repair on critical data
cqlsh -e "SELECT * FROM my_keyspace.my_table WHERE ... ;"
# With consistency ALL to force read repair
```

---

## Repair Best Practices

### Scheduling

| Cluster Size | Repair Frequency | Strategy |
|--------------|------------------|----------|
| < 10 nodes | Weekly | Full cluster repair |
| 10-50 nodes | Weekly per node | Rolling repair |
| > 50 nodes | Sub-range daily | Token range repair |

### Command Options

```bash
# Primary range only (most common)
nodetool repair -pr my_keyspace

# Full repair (vs incremental)
nodetool repair -full -pr my_keyspace

# Specific tables
nodetool repair -pr my_keyspace table1 table2

# Parallel (Cassandra 4.0+)
nodetool repair -pr --parallel my_keyspace

# Local datacenter only
nodetool repair -pr -local my_keyspace
```

### Resource Management

```yaml
# cassandra.yaml - repair settings
repair_session_max_tree_depth: 18
repair_session_space_in_mb: 256

# Limit repair impact
compaction_throughput_mb_per_sec: 64
stream_throughput_outbound_megabits_per_sec: 200
```

---

## Prevention

1. **Schedule regular repairs** - Run before gc_grace_seconds expires
2. **Monitor repair duration** - Alert if repairs take > 24 hours
3. **Size partitions appropriately** - Large partitions cause OOM during repair
4. **Maintain cluster health** - Repair requires all replicas available
5. **Use repair tools** - Consider Reaper for automated repair scheduling

---

## Related Commands

| Command | Purpose |
|---------|---------|
| `nodetool repair` | Run repair |
| `nodetool repair_admin list` | List active repairs |
| `nodetool repair_admin cancel` | Cancel repair |
| `nodetool netstats` | Check streaming status |
| `nodetool setstreamthroughput` | Adjust stream speed |

## Related Documentation

- [Repair Operations](../../operations/repair/index.md) - Repair concepts and procedures
- [Schema Disagreement](schema-disagreement.md) - Schema issues affecting repair
