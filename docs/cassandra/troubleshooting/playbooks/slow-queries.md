# Slow Queries

Slow queries manifest as high latency, timeouts, or degraded application performance. This playbook helps identify and resolve query performance issues.

---

## Symptoms

- High read/write latencies in `nodetool proxyhistograms`
- Query timeouts from client applications
- Specific queries consistently slow
- "Slow query" warnings in logs
- User-reported application slowness

---

## Diagnosis

### Step 1: Check Overall Latencies

```bash
# Coordinator latencies
nodetool proxyhistograms

# Per-table latencies
nodetool tablehistograms my_keyspace my_table
```

**What to look for:**
- p99 latency > 100ms for reads
- p99 latency > 50ms for writes
- Large gap between p50 and p99 (inconsistent performance)

### Step 2: Enable Slow Query Logging

```yaml
# cassandra.yaml
slow_query_log_timeout_in_ms: 500
```

Then check logs:
```bash
grep "slow query" /var/log/cassandra/debug.log | tail -50
```

### Step 3: Trace Specific Queries

```sql
TRACING ON;
SELECT * FROM my_table WHERE ...;
TRACING OFF;
```

**What to look for in trace:**
- Time spent in each phase
- Number of SSTables read
- Tombstones scanned
- Partitions touched

### Step 4: Check Table Health

```bash
nodetool tablestats my_keyspace.my_table
```

**Problem indicators:**
- High SSTable count (> 20)
- High tombstones per slice
- Large partition sizes
- Low key cache hit rate

### Step 5: Check for Hotspots

```bash
# Top partitions by read/write activity
nodetool toppartitions my_keyspace my_table 10000
```

---

## Resolution

### Query Anti-Pattern: Full Table Scan

**Problem:**
```sql
SELECT * FROM users;  -- Scans entire cluster
```

**Solution:**
```sql
-- Add WHERE clause on partition key
SELECT * FROM users WHERE user_id = ?;

-- Or use pagination
SELECT * FROM users LIMIT 100;
```

### Query Anti-Pattern: ALLOW FILTERING

**Problem:**
```sql
SELECT * FROM users WHERE email = 'test@example.com' ALLOW FILTERING;
```

**Solution:**
```sql
-- Create secondary index
CREATE INDEX ON users (email);

-- Or create materialized view
CREATE MATERIALIZED VIEW users_by_email AS
  SELECT * FROM users
  WHERE email IS NOT NULL AND user_id IS NOT NULL
  PRIMARY KEY (email, user_id);
```

### Query Anti-Pattern: IN with Many Values

**Problem:**
```sql
SELECT * FROM orders WHERE order_id IN (uuid1, uuid2, ..., uuid100);
```

**Solution:**
```sql
-- Use async parallel queries from application
-- Or batch into smaller groups
SELECT * FROM orders WHERE order_id IN (uuid1, uuid2, uuid3);
```

### Query Anti-Pattern: Range Queries on Clustering Columns

**Problem:**
```sql
SELECT * FROM events WHERE user_id = ? AND event_time > '2024-01-01';
-- Scans potentially millions of rows
```

**Solution:**
```sql
-- Add LIMIT
SELECT * FROM events WHERE user_id = ? AND event_time > '2024-01-01' LIMIT 1000;

-- Or redesign for bounded queries
SELECT * FROM events WHERE user_id = ? AND day = '2024-01-15';
```

### Data Model Issue: Large Partitions

See [Large Partition Issues](large-partition.md).

```bash
# Check partition sizes
nodetool tablestats my_keyspace.my_table | grep partition
```

### Data Model Issue: Tombstone Accumulation

See [Tombstone Accumulation](tombstone-accumulation.md).

```bash
# Check tombstone counts
nodetool tablestats my_keyspace.my_table | grep tombstone
```

### Infrastructure Issue: Compaction Backlog

```bash
# Check pending compactions
nodetool compactionstats

# If backlog exists
nodetool compact my_keyspace my_table
```

### Infrastructure Issue: Insufficient Resources

```bash
# Check CPU
top -p $(pgrep -f CassandraDaemon)

# Check disk I/O
iostat -x 1 5

# Check thread pools
nodetool tpstats
```

---

## Query Optimization Checklist

| Check | Good | Bad | Fix |
|-------|------|-----|-----|
| Partition key in WHERE | Yes | No | Add partition key filter |
| ALLOW FILTERING | Not used | Used | Create index or view |
| IN clause size | < 10 values | > 100 values | Parallel queries |
| Result set size | LIMIT used | No LIMIT | Add LIMIT |
| Table SSTable count | < 20 | > 50 | Run compaction |
| Tombstones per read | < 100 | > 1000 | Fix data model |
| Key cache hit rate | > 90% | < 50% | Increase cache |

---

## Recovery

### Verify Improvement

```bash
# Check latencies after fix
nodetool tablehistograms my_keyspace my_table

# Trace query again
TRACING ON;
<your query>;
TRACING OFF;
```

### Monitor Going Forward

Set up alerts on:
- p99 read latency > 100ms
- p99 write latency > 50ms
- Slow query log entries

---

## Prevention

1. **Review queries before production** - Check execution plans
2. **Monitor query latencies** - Alert on degradation
3. **Design data model for queries** - Don't retrofit
4. **Use prepared statements** - Reduce parsing overhead
5. **Implement client-side caching** - Reduce load for hot data
6. **Run regular compaction** - Keep SSTable counts low

---

## Related Commands

| Command | Purpose |
|---------|---------|
| `nodetool proxyhistograms` | Overall latencies |
| `nodetool tablehistograms` | Per-table latencies |
| `nodetool tablestats` | Table health metrics |
| `nodetool toppartitions` | Identify hot partitions |
| `TRACING ON/OFF` | Query tracing |

## Related Documentation

- [CQL Reference](../../cql/index.md) - Query syntax and options
- [Data Modeling](../../data-modeling/index.md) - Design patterns
- [Large Partition Issues](large-partition.md) - Partition sizing
- [Tombstone Accumulation](tombstone-accumulation.md) - Tombstone issues
