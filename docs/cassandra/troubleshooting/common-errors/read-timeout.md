# ReadTimeoutException

`ReadTimeoutException` occurs when a read operation cannot complete within the configured timeout period.

## Error Message

```
com.datastax.driver.core.exceptions.ReadTimeoutException: Cassandra timeout during read query
at consistency LOCAL_QUORUM (2 responses were required but only 1 replica responded)
```

Or in logs:

```
ERROR [ReadStage-2] ReadCallback.java:123 - Read timeout: 5000 ms
```

---

## Symptoms

- Client receives `ReadTimeoutException`
- High read latencies in `nodetool proxyhistograms`
- Increased `ReadTimeout` count in JMX metrics
- Slow or unresponsive queries

---

## Diagnosis

### Step 1: Check Read Latency

```bash
# Overall read latencies
nodetool proxyhistograms

# Per-table latencies
nodetool tablehistograms my_keyspace my_table
```

**What to look for**: p99 latencies > timeout value (default 5000ms)

### Step 2: Check Table Statistics

```bash
nodetool tablestats my_keyspace.my_table
```

**Key metrics**:

| Metric | Warning Level | Indicates |
|--------|---------------|-----------|
| SSTable count | > 20 | Compaction lag |
| Partition size (max) | > 100MB | Large partitions |
| Tombstone scans | > 1000 | Too many tombstones |
| Bloom filter false positive ratio | > 0.01 | Inefficient bloom filters |

### Step 3: Check for Tombstones

```bash
# Enable query tracing
cqlsh> TRACING ON;
cqlsh> SELECT * FROM my_table WHERE pk = 'value';
```

**Look for**: "Scanned X tombstones" messages.

### Step 4: Check Thread Pool Status

```bash
nodetool tpstats
```

**Warning signs**:
- `ReadStage` pending > 0 for extended periods
- `ReadStage` blocked > 0
- High `All time blocked` count

### Step 5: Check Disk I/O

```bash
iostat -x 1 5
```

**Warning signs**:
- `%util` > 80%
- `await` > 10ms
- High `r_await` (read wait time)

### Step 6: Check Garbage Collection

```bash
grep "GC pause" /var/log/cassandra/gc.log | tail -20
```

**Warning signs**:
- GC pauses > 500ms
- Frequent full GC

---

## Root Causes

### 1. Large Partitions

**Symptoms**: Single partition queries slow, multi-partition queries fast.

**Verify**:
```bash
nodetool tablestats my_keyspace.my_table | grep -i partition
```

**Solution**:
- Redesign data model to use smaller partitions
- Use bucketing (e.g., by time period)
- Set partition size alerts

### 2. Too Many Tombstones

**Symptoms**: Queries become slower after deletes, slow range queries.

**Verify**:
```bash
# Run with tracing
TRACING ON;
SELECT * FROM my_table WHERE partition_key = 'x';
# Look for "Scanned X tombstones"
```

**Solution**:
- Reduce `gc_grace_seconds` (after ensuring repair runs regularly)
- Avoid deletes if possible (use TTL instead)
- Run compaction to purge tombstones
```bash
nodetool compact my_keyspace my_table
```

### 3. High SSTable Count

**Symptoms**: Read latency increases over time, compaction pending.

**Verify**:
```bash
nodetool compactionstats
nodetool tablestats my_keyspace.my_table | grep "SSTable count"
```

**Solution**:
- Increase compaction throughput
```bash
nodetool setcompactionthroughput 128
```
- Force compaction
```bash
nodetool compact my_keyspace my_table
```

### 4. Slow Disk I/O

**Symptoms**: All operations slow, high disk utilization.

**Verify**:
```bash
iostat -x 1 10
```

**Solution**:
- Use SSDs (required for production)
- Check for disk issues
- Reduce concurrent operations

### 5. Network Issues

**Symptoms**: Only some nodes show timeouts, inter-node latency high.

**Verify**:
```bash
# Check cross-node latency
nodetool netstats

# Ping test
ping -c 10 <other-node-ip>
```

**Solution**:
- Check network infrastructure
- Verify firewall rules
- Check for packet loss

### 6. GC Pressure

**Symptoms**: Intermittent timeouts, correlated with GC pauses.

**Verify**:
```bash
grep -E "GC|pause" /var/log/cassandra/gc.log | tail -50
```

**Solution**:
- Tune heap size (typically 8-31GB)
- Adjust GC settings
- Check for memory leaks

### 7. Overloaded Cluster

**Symptoms**: All operations slow, high thread pool utilization.

**Verify**:
```bash
nodetool tpstats
```

**Solution**:
- Add nodes
- Reduce traffic
- Optimize queries

---

## Resolution

### Immediate Actions

1. **Increase timeout** (temporary fix):
   ```yaml
   # cassandra.yaml
   read_request_timeout_in_ms: 10000
   ```

2. **Reduce consistency level** (if acceptable):
   ```sql
   CONSISTENCY LOCAL_ONE;
   SELECT * FROM my_table WHERE pk = 'x';
   ```

3. **Force compaction** (if SSTable count high):
   ```bash
   nodetool compact my_keyspace my_table
   ```

### Long-term Fixes

1. **Fix data model**:
   - Smaller partitions (< 100MB)
   - Avoid unbounded partition growth
   - Use appropriate clustering columns

2. **Tune compaction**:
   ```yaml
   # For time-series data
   compaction = {'class': 'TimeWindowCompactionStrategy',
                 'compaction_window_unit': 'HOURS',
                 'compaction_window_size': '1'}
   ```

3. **Add capacity**:
   - Add nodes if cluster is overloaded
   - Scale horizontally

4. **Optimize queries**:
   - Add appropriate indexes
   - Use LIMIT clause
   - Avoid full table scans

---

## Prevention

### Monitoring

Set up alerts for:

| Metric | Warning | Critical |
|--------|---------|----------|
| Read latency p99 | > 50ms | > 500ms |
| SSTable count | > 20 | > 50 |
| ReadStage pending | > 0 (sustained) | > 10 |
| GC pause time | > 200ms | > 500ms |

### Best Practices

1. **Design for your queries**: Model data based on access patterns
2. **Keep partitions small**: Target < 100MB per partition
3. **Avoid tombstones**: Use TTL instead of DELETE when possible
4. **Monitor proactively**: Track read latencies over time
5. **Run repairs**: Keep data consistent across replicas

---

## Related

- **[WriteTimeoutException](write-timeout.md)**
- **[Diagnosis Guide](../diagnosis/index.md)**
