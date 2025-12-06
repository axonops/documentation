# WriteTimeoutException Troubleshooting

## Symptoms

- `WriteTimeoutException` in application logs
- Error message: `Cassandra timeout during SIMPLE write query`
- Client receives timeout error before operation completes
- Consistency level not achieved within timeout period

## Error Message Examples

```
com.datastax.driver.core.exceptions.WriteTimeoutException:
Cassandra timeout during SIMPLE write query at consistency QUORUM
(2 replicas were required but only 1 acknowledged the write)
```

```
WriteTimeout: Error from server: code=1100 [Coordinator node timed out waiting
for replica nodes' responses] message="Operation timed out - received only
1 responses." info={'received_responses': 1, 'required_responses': 2,
'consistency': 'QUORUM', 'write_type': 'SIMPLE'}
```

---

## Common Causes

### 1. Overloaded Nodes

Replicas are too busy to process writes in time.

**Diagnosis**:
```bash
# Check MutationStage pending/blocked
nodetool tpstats | grep -E "Pool|Mutation"

# Check for dropped messages
nodetool tpstats | grep -E "MUTATION|Dropped"

# High MutationStage pending indicates overload
```

**Resolution**:
- Scale cluster (add nodes)
- Reduce write throughput
- Increase concurrent_writes in cassandra.yaml
- Check for hot partitions

### 2. Network Issues

Network latency or partition between coordinator and replicas.

**Diagnosis**:
```bash
# Check network latency
ping <replica_ip>

# Check gossip state
nodetool gossipinfo | grep -A5 <replica_ip>

# Look for UnreachableMembers
nodetool status
```

**Resolution**:
- Fix network connectivity issues
- Check firewall rules (port 7000)
- Verify inter-node networking

### 3. Replica Node Down or Unresponsive

Not enough live replicas to satisfy consistency level.

**Diagnosis**:
```bash
# Check cluster status
nodetool status

# Look for Down (D) or unavailable nodes
# Check if nodes are joining/leaving (J/L)
```

**Resolution**:
- Bring down nodes back up
- Lower consistency level (if acceptable)
- Replace dead nodes

### 4. Disk I/O Bottleneck

Commit log writes are slow.

**Diagnosis**:
```bash
# Check disk I/O
iostat -xz 1 5

# Check commit log directory latency
# Look for high await times

# Check for disk full
df -h /var/lib/cassandra
```

**Resolution**:
- Use SSD/NVMe for commit log
- Separate commit log from data directory
- Increase disk capacity

### 5. Large Writes or Batches

Individual writes or batches too large.

**Diagnosis**:
```bash
# Check for batch size warnings
grep -i "batch" /var/log/cassandra/system.log

# Check write sizes in table stats
nodetool tablestats my_keyspace.table | grep -i write
```

**Resolution**:
- Reduce batch sizes
- Split large writes into smaller operations
- Review data model for write amplification

### 6. GC Pauses

Long garbage collection pauses blocking writes.

**Diagnosis**:
```bash
# Check GC logs
tail -100 /var/log/cassandra/gc.log

# Look for long pauses (> 500ms)
grep -E "pause.*[0-9]{4,}ms" /var/log/cassandra/gc.log
```

**Resolution**:
- Tune GC settings
- Reduce heap size if too large
- Consider ZGC (JDK 17+)

---

## Write Types

The `write_type` in the error indicates what kind of write failed:

| Write Type | Description | Common Issues |
|------------|-------------|---------------|
| `SIMPLE` | Regular INSERT/UPDATE | Node overload, network |
| `BATCH` | Batch operation | Batch too large, spanning partitions |
| `UNLOGGED_BATCH` | Unlogged batch | Same as BATCH |
| `COUNTER` | Counter update | Counter replica issues |
| `BATCH_LOG` | Batch log write | Batch log nodes unavailable |
| `CAS` | Lightweight transaction | Paxos timeout, contention |
| `VIEW` | Materialized view | View replicas unavailable |

---

## Step-by-Step Diagnosis

### Step 1: Check Write Type and Consistency Level

```sql
-- What was the query?
-- Check consistency level requirement
CONSISTENCY;

-- For QUORUM with RF=3, need 2 replicas
-- For LOCAL_QUORUM with RF=3 in DC, need 2 in that DC
```

### Step 2: Check Cluster Status

```bash
# Are all replicas up?
nodetool status

# Check which nodes own the partition
nodetool getendpoints my_keyspace my_table <partition_key>
```

### Step 3: Check Node Health

```bash
# On coordinator and replicas:

# Thread pools
nodetool tpstats

# Dropped messages (critical)
nodetool tpstats | grep -E "Dropped|MUTATION"

# GC activity
nodetool gcstats

# Recent errors
tail -100 /var/log/cassandra/system.log | grep -i error
```

### Step 4: Check Resource Utilization

```bash
# CPU
top -b -n 1 | head -20

# Memory
free -h

# Disk I/O
iostat -xz 1 5

# Network
sar -n DEV 1 5
```

### Step 5: Review Metrics

```bash
# Write latency
nodetool proxyhistograms

# Table-level write stats
nodetool tablestats my_keyspace.table | grep -i write
```

---

## Resolution Strategies

### Immediate Actions

1. **Lower consistency level** (temporary):
```sql
-- If eventual consistency is acceptable
CONSISTENCY LOCAL_ONE;
INSERT INTO table ...;
```

2. **Increase timeout** (application):
```java
// Java driver
SimpleStatement stmt = SimpleStatement.builder("INSERT ...")
    .setTimeout(Duration.ofSeconds(30))
    .build();
```

3. **Add retry logic** (application):
```java
RetryPolicy retry = new RetryPolicy() {
    @Override
    public RetryDecision onWriteTimeout(...) {
        if (writeType == WriteType.SIMPLE && retryCount < 3) {
            return RetryDecision.retry(cl);
        }
        return RetryDecision.rethrow();
    }
};
```

### Long-term Fixes

1. **Scale cluster**:
```bash
# Add nodes to distribute load
# Monitor: nodetool status during expansion
```

2. **Tune cassandra.yaml**:
```yaml
# Increase write timeout
write_request_timeout_in_ms: 10000  # default: 2000

# Increase concurrent writes (if CPU available)
concurrent_writes: 64  # default: 32

# Optimize commit log
commitlog_sync: periodic
commitlog_sync_period_in_ms: 10000
```

3. **Review data model**:
- Check for hot partitions
- Split large partitions
- Reduce write amplification

4. **Optimize hardware**:
- Use NVMe for commit log
- Increase network bandwidth
- Add RAM for more memtable space

---

## Prevention

### Best Practices

```yaml
# Appropriate timeouts
write_request_timeout_in_ms: 5000  # 5 seconds

# Adequate thread pool
concurrent_writes: 32  # Based on disk count

# Proper sizing
# memtable_heap_space_in_mb: adequate for workload
```

### Monitoring

```yaml
# Alert on:
- Write latency p99 > 1 second
- Dropped MUTATION messages > 0
- MutationStage pending > 100
- Disk I/O await > 10ms
```

### Application Design

```java
// Set appropriate timeouts
DriverConfigLoader loader = DriverConfigLoader.programmaticBuilder()
    .withDuration(DefaultDriverOption.REQUEST_TIMEOUT, Duration.ofSeconds(10))
    .build();

// Use async writes for high throughput
session.executeAsync(statement);

// Implement proper error handling
try {
    session.execute(statement);
} catch (WriteTimeoutException e) {
    // Log and handle appropriately
    // Consider: retry, queue for later, alert
}
```

---

## Related Issues

- **[ReadTimeoutException](read-timeout.md)** - Read timeout troubleshooting
- **[UnavailableException](unavailable.md)** - Replica unavailability
- **[OverloadedException](overloaded.md)** - Node overload

---

## Next Steps

- **[Thread Pool Tuning](../../performance/index.md)** - Optimize thread pools
- **[Network Troubleshooting](../../troubleshooting/index.md)** - Network issues
- **[Monitoring Guide](../../monitoring/index.md)** - Set up alerts
