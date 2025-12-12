# Large Partition Issues

Large partitions are a common cause of performance problems in Cassandra. They cause slow reads, OOM during compaction, and uneven data distribution.

---

## Symptoms

- Slow reads on specific partition keys
- OOM errors during compaction
- "Compacting large partition" warnings in logs
- Uneven disk usage across nodes
- Read timeouts on specific queries
- High GC pressure when accessing certain data

---

## Diagnosis

### Step 1: Check for Large Partition Warnings

```bash
grep -i "large partition\|compacting large\|Writing large partition" /var/log/cassandra/system.log | tail -20
```

Example warning:
```
WARN  Writing large partition my_keyspace/my_table:key123 (150.2 MiB) to sstable
```

### Step 2: Check Table Statistics

```bash
nodetool tablestats my_keyspace.my_table
```

**Key metrics:**
- `Compacted partition maximum bytes`: Largest partition
- `Compacted partition mean bytes`: Average partition size

**Target:** Keep partitions under 100 MB.

### Step 3: Identify Specific Large Partitions

```bash
# Use sstablepartitions tool (Cassandra 4.0+)
sstablepartitions /var/lib/cassandra/data/my_keyspace/my_table-*/nb-*-big-Data.db --min-size 50MB
```

Or query with tracing:

```sql
TRACING ON;
SELECT * FROM my_table WHERE partition_key = 'suspect_key' LIMIT 1;
TRACING OFF;
```

### Step 4: Check Partition Size Configuration

```bash
grep -i "partition_size\|compaction_large" /etc/cassandra/cassandra.yaml
```

### Step 5: Monitor During Access

```bash
# Watch for GC during large partition access
nodetool gcstats

# Watch heap usage
nodetool info | grep Heap
```

---

## Resolution

### Immediate: Handle OOM During Compaction

**Temporarily skip large partition:**

```bash
# Not recommended for production, but for emergency
# Reduce compaction throughput
nodetool setcompactionthroughput 16
```

**Increase heap (temporary):**

This is a workaround, not a fix:
```bash
# In jvm.options
-Xmx16G  # Increase temporarily
```

### Short-term: Adjust Compaction Settings

```yaml
# cassandra.yaml - increase limits for large partitions
compaction_large_partition_warning_threshold_mb: 100
```

### Long-term: Fix Data Model

**Problem Pattern 1: Unbounded partition growth**

```sql
-- Bad: All events for a user in one partition
CREATE TABLE user_events (
    user_id uuid,
    event_time timestamp,
    data text,
    PRIMARY KEY (user_id, event_time)
);
-- Partition grows forever
```

**Solution: Add time bucketing**

```sql
-- Good: Events bucketed by day
CREATE TABLE user_events (
    user_id uuid,
    day date,
    event_time timestamp,
    data text,
    PRIMARY KEY ((user_id, day), event_time)
);
-- Partition limited to one day of events
```

**Problem Pattern 2: Wide rows with many columns**

```sql
-- Bad: Thousands of columns per row
CREATE TABLE sensor_data (
    sensor_id uuid,
    metric_name text,
    value double,
    PRIMARY KEY (sensor_id, metric_name)
);
-- Can have millions of metrics per sensor
```

**Solution: Add bucketing or limit scope**

```sql
-- Good: Bucket by time period
CREATE TABLE sensor_data (
    sensor_id uuid,
    hour timestamp,
    metric_name text,
    value double,
    PRIMARY KEY ((sensor_id, hour), metric_name)
);
```

**Problem Pattern 3: Collection columns**

```sql
-- Bad: Large collections
CREATE TABLE users (
    user_id uuid PRIMARY KEY,
    followers set<uuid>  -- Can grow to millions
);
```

**Solution: Use separate table**

```sql
-- Good: Separate relationship table
CREATE TABLE user_followers (
    user_id uuid,
    follower_id uuid,
    followed_at timestamp,
    PRIMARY KEY (user_id, follower_id)
);
```

### Data Migration Strategy

To fix existing large partitions:

```sql
-- 1. Create new table with better model
CREATE TABLE user_events_v2 (...);

-- 2. Migrate data with bucketing
-- Use Spark, application code, or COPY command

-- 3. Update application to use new table

-- 4. Drop old table after verification
DROP TABLE user_events;
```

---

## Recovery

### Verify Partition Sizes

```bash
# After data model fix, check new partition sizes
nodetool tablestats my_keyspace.my_table_v2 | grep "partition"
```

### Monitor for Recurrence

Set up alerting:
- Alert on "Writing large partition" log entries
- Alert on max partition size > 50MB
- Monitor specific problematic partition keys

---

## Partition Size Guidelines

| Size | Status | Action |
|------|--------|--------|
| < 10 MB | Good | No action needed |
| 10-50 MB | Warning | Monitor, plan for growth |
| 50-100 MB | Problem | Redesign data model |
| > 100 MB | Critical | Immediate remediation required |

### Estimating Partition Size

```
Partition size ≈ (number of rows) × (average row size)
Row size ≈ sum of column sizes + clustering key size + 23 bytes overhead
```

### Design Targets

| Metric | Target |
|--------|--------|
| Partition size | < 100 MB |
| Rows per partition | < 100,000 |
| Cells per partition | < 100,000 |

---

## Prevention

1. **Design for bounded partitions** - Always include time or other limiting factor
2. **Avoid unbounded collections** - Use separate tables instead
3. **Monitor partition sizes** - Alert before they become critical
4. **Test with realistic data** - Load test with expected data volumes
5. **Review data model changes** - Check for partition size impact

---

## Related Commands

| Command | Purpose |
|---------|---------|
| `nodetool tablestats` | Check partition size metrics |
| `sstablepartitions` | Find large partitions in SSTables |
| `nodetool gcstats` | Monitor GC during access |

## Related Documentation

- [Data Modeling](../../data-modeling/index.md) - Partition design best practices
- [GC Pause Issues](gc-pause.md) - GC problems from large partitions
- [Compaction Management](../../operations/compaction-management/index.md) - Compaction and large partitions
