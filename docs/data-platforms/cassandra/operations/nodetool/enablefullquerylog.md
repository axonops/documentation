---
title: "nodetool enablefullquerylog"
description: "Enable full query logging in Cassandra using nodetool enablefullquerylog for debugging."
meta:
  - name: keywords
    content: "nodetool enablefullquerylog, enable FQL, query logging, Cassandra debugging"
search:
  boost: 3
---

# nodetool enablefullquerylog

Enables full query logging (FQL) on the node.

---

## Synopsis

```bash
nodetool [connection_options] enablefullquerylog [options]
```

## Description

`nodetool enablefullquerylog` activates full query logging on a Cassandra node. Unlike audit logging which focuses on security events, full query logging (FQL) captures complete query execution details including latency metrics, making it ideal for performance analysis and query optimization.

Full query logging is essential for:

- **Performance analysis** - Understanding query patterns and latencies
- **Query optimization** - Identifying slow queries for tuning
- **Capacity planning** - Analyzing workload characteristics
- **Debugging** - Reproducing query sequences for issue investigation
- **Workload migration** - Capturing queries to replay on test environments

!!! info "Cassandra 4.0+"
    Full query logging is available in Apache Cassandra 4.0 and later versions.

---

## Options

| Option | Description |
|--------|-------------|
| `--path` | Path to the FQL log directory |
| `--roll-cycle` | Log file roll cycle (MINUTELY, HOURLY, DAILY) |
| `--block` | Block queries if log falls behind (default: true) |
| `--max-queue-weight` | Maximum weight of in-memory queue (bytes) |
| `--max-log-size` | Maximum total log size before oldest logs deleted |
| `--archive-command` | Command to archive rolled log segments |
| `--max-archive-retries` | Maximum retries for archive command |

---

## Examples

### Enable with Defaults

```bash
nodetool enablefullquerylog
```

### Specify Log Path

```bash
nodetool enablefullquerylog --path /var/log/cassandra/fql
```

### Configure Roll Cycle and Size

```bash
nodetool enablefullquerylog \
    --path /var/log/cassandra/fql \
    --roll-cycle HOURLY \
    --max-log-size 10737418240
```

### Non-blocking Mode

```bash
# Don't block queries if logging falls behind
nodetool enablefullquerylog \
    --path /var/log/cassandra/fql \
    --block false
```

### Full Configuration

```bash
nodetool enablefullquerylog \
    --path /var/log/cassandra/fql \
    --roll-cycle HOURLY \
    --block true \
    --max-queue-weight 268435456 \
    --max-log-size 17179869184 \
    --archive-command "/usr/local/bin/archive_fql.sh %path"
```

---

## Log Contents

Full query logs capture:

| Field | Description |
|-------|-------------|
| Query timestamp | When the query was executed |
| Protocol version | CQL protocol version |
| Query type | Type of operation |
| Query string | Complete CQL statement |
| Query parameters | Bound parameter values |
| Consistency level | Requested consistency |
| Serial consistency | Serial consistency for LWTs |
| Timestamp | Client-provided timestamp |
| Keyspace | Target keyspace |
| Query latency | Server-side execution time |

---

## Log Format

FQL uses Chronicle Queue format (binary). To read logs:

```bash
# Use the fqltool to read logs
fqltool dump /var/log/cassandra/fql/

# Or use fqltool replay to replay queries
fqltool replay --keyspace my_keyspace /var/log/cassandra/fql/
```

---

## Use Cases

### Performance Baseline

Capture query patterns before optimization:

```bash
# Enable FQL
nodetool enablefullquerylog --path /var/log/cassandra/fql --roll-cycle HOURLY

# Let it run during representative workload...

# Disable and analyze
nodetool disablefullquerylog
fqltool dump /var/log/cassandra/fql/ > queries.txt
```

### Slow Query Analysis

Identify slow queries:

```bash
# Enable FQL
nodetool enablefullquerylog --path /var/log/cassandra/fql

# After collection period
fqltool dump /var/log/cassandra/fql/ | grep -E "latency.*[0-9]{4,}ms"
```

### Migration Testing

Capture production queries for test replay:

```bash
# On production
nodetool enablefullquerylog --path /var/log/cassandra/fql --roll-cycle MINUTELY

# Collect for desired period...
nodetool disablefullquerylog

# Copy logs to test environment
scp -r /var/log/cassandra/fql/ test-server:/data/fql/

# On test server - replay queries
fqltool replay \
    --target test-cluster-host \
    --keyspace my_keyspace \
    /data/fql/
```

### Debug Query Sequences

Capture exact query sequence leading to an issue:

```bash
# Enable when issue suspected
nodetool enablefullquerylog --path /var/log/cassandra/fql

# Reproduce the issue...

# Disable and analyze
nodetool disablefullquerylog
fqltool dump /var/log/cassandra/fql/ | tail -100
```

### Workload Characterization

Understand query distribution:

```bash
# Enable during typical workload
nodetool enablefullquerylog --path /var/log/cassandra/fql

# Analyze query types
fqltool dump /var/log/cassandra/fql/ | grep -oE "SELECT|INSERT|UPDATE|DELETE" | sort | uniq -c | sort -rn
```

---

## Configuration in cassandra.yaml

For persistent configuration:

```yaml
# cassandra.yaml
full_query_logging_options:
    log_dir: /var/log/cassandra/fql
    roll_cycle: HOURLY
    block: true
    max_queue_weight: 268435456
    max_log_size: 17179869184
    archive_command:
    max_archive_retries: 10
```

---

## Impact Assessment

### Performance Impact

| Factor | Impact |
|--------|--------|
| Disk I/O | Moderate to high |
| CPU | Low |
| Query latency | Minimal with `--block false`, noticeable with `--block true` |
| Disk space | Can grow rapidly |

!!! warning "Disk Space Consumption"
    Full query logging records ALL queries with full details. Disk usage can grow very quickly in high-throughput environments. Monitor disk space and set appropriate `--max-log-size`.

### Disk Space Estimation

```bash
# Rough estimation
# queries/sec * avg_query_size_bytes * seconds

# Example: 10,000 queries/sec * 500 bytes * 3600 sec/hour = ~18 GB/hour
```

---

## Monitoring FQL

### Check Status

```bash
nodetool getfullquerylog
```

### Monitor Log Size

```bash
# Watch log directory growth
watch -n 10 'du -sh /var/log/cassandra/fql/'

# Check file count
ls -la /var/log/cassandra/fql/ | wc -l
```

### Verify Logging

```bash
# Execute a query
cqlsh -e "SELECT * FROM system.local"

# Check log growth
ls -la /var/log/cassandra/fql/

# Dump recent entries
fqltool dump /var/log/cassandra/fql/ | tail -5
```

---

## FQL Tool Commands

### Dump Logs

```bash
# Dump all logs
fqltool dump /var/log/cassandra/fql/

# Dump with filtering
fqltool dump /var/log/cassandra/fql/ | grep "SELECT"
```

### Replay Queries

```bash
# Replay to same cluster
fqltool replay \
    --target 192.168.1.100 \
    --keyspace my_keyspace \
    /var/log/cassandra/fql/

# Replay with rate limiting
fqltool replay \
    --target 192.168.1.100 \
    --keyspace my_keyspace \
    --rate-limit 1000 \
    /var/log/cassandra/fql/
```

### Compare Results

```bash
# Replay and compare results between clusters
fqltool compare \
    --target 192.168.1.100 \
    --target 192.168.1.200 \
    --keyspace my_keyspace \
    /var/log/cassandra/fql/
```

---

## Workflow: Performance Analysis

```bash
#!/bin/bash
# fql_performance_analysis.sh

FQL_PATH="/var/log/cassandra/fql"
DURATION_MINUTES=30

echo "=== Full Query Log Performance Analysis ==="

# 1. Clear old logs
echo "1. Clearing old FQL data..."
rm -rf ${FQL_PATH}/*

# 2. Enable FQL
echo "2. Enabling FQL..."
nodetool enablefullquerylog --path $FQL_PATH --roll-cycle MINUTELY

# 3. Wait for collection
echo "3. Collecting queries for $DURATION_MINUTES minutes..."
sleep $((DURATION_MINUTES * 60))

# 4. Disable FQL
echo "4. Disabling FQL..."
nodetool disablefullquerylog

# 5. Analyze
echo "5. Analyzing captured queries..."

echo ""
echo "=== Query Type Distribution ==="
fqltool dump $FQL_PATH 2>/dev/null | grep -oE "^(SELECT|INSERT|UPDATE|DELETE|BATCH)" | sort | uniq -c | sort -rn

echo ""
echo "=== Total Queries Captured ==="
fqltool dump $FQL_PATH 2>/dev/null | wc -l

echo ""
echo "=== Log Size ==="
du -sh $FQL_PATH

echo ""
echo "Analysis complete. Full logs at: $FQL_PATH"
```

---

## Cluster-Wide Enablement

### Enable on All Nodes

```bash
#!/bin/bash
# enable_fql_cluster.sh

FQL_PATH="/var/log/cassandra/fql"# Get list of node IPs from local nodetool status


nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

echo "Enabling FQL cluster-wide..."
for node in $nodes; do
    echo -n "$node: "
    ssh "$node" "nodetool enablefullquerylog --path $FQL_PATH 2>/dev/null && echo "enabled" || echo "FAILED""
done

echo ""
echo "Verification:"
for node in $nodes; do
    echo "=== $node ==="
    ssh "$node" "nodetool getfullquerylog 2>/dev/null | head -5"
done
```

---

## Troubleshooting

### FQL Not Recording

```bash
# Verify enabled
nodetool getfullquerylog

# Check log directory permissions
ls -la /var/log/cassandra/fql/

# Check disk space
df -h /var/log/cassandra/

# Check for errors in logs
grep -i "fql\|fullquery" /var/log/cassandra/system.log | tail -20
```

### High Latency After Enable

```bash
# Check if blocking mode is causing delays
nodetool getfullquerylog | grep block

# Switch to non-blocking mode
nodetool disablefullquerylog
nodetool enablefullquerylog --path /var/log/cassandra/fql --block false
```

### Logs Growing Too Fast

```bash
# Set maximum log size
nodetool disablefullquerylog
nodetool enablefullquerylog \
    --path /var/log/cassandra/fql \
    --max-log-size 5368709120 \
    --roll-cycle MINUTELY
```

### Cannot Read Log Files

```bash
# Verify fqltool is available
which fqltool

# If not in path, use full path
/path/to/cassandra/tools/bin/fqltool dump /var/log/cassandra/fql/

# Check file permissions
ls -la /var/log/cassandra/fql/
```

---

## Best Practices

!!! tip "FQL Usage Guidelines"

    1. **Use sparingly** - Enable only when needed (performance analysis, debugging)
    2. **Set size limits** - Always configure `--max-log-size` to prevent disk exhaustion
    3. **Use non-blocking** - Set `--block false` in production to prevent latency impact
    4. **Monitor disk** - Watch log directory growth carefully
    5. **Short duration** - Enable for limited periods, not continuously
    6. **Archive promptly** - Process and remove logs after analysis
    7. **Test environment** - Prefer enabling on test/staging when possible

!!! warning "Production Considerations"

    - FQL can significantly impact disk I/O
    - Blocking mode can increase query latency
    - In high-throughput environments, logs grow very quickly
    - Consider sampling at application level instead of full logging

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [disablefullquerylog](disablefullquerylog.md) | Disable FQL |
| [getfullquerylog](getfullquerylog.md) | View FQL configuration |
| [resetfullquerylog](resetfullquerylog.md) | Reset FQL path |
| [enableauditlog](enableauditlog.md) | Enable audit logging |
