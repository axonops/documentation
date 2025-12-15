---
title: "nodetool disablefullquerylog"
description: "Disable full query logging in Cassandra using nodetool disablefullquerylog command."
meta:
  - name: keywords
    content: "nodetool disablefullquerylog, disable FQL, query logging, Cassandra"
---

# nodetool disablefullquerylog

Disables full query logging (FQL) on the node.

---

## Synopsis

```bash
nodetool [connection_options] disablefullquerylog
```

## Description

`nodetool disablefullquerylog` deactivates full query logging on a Cassandra node. When disabled, the node stops recording query execution details to the FQL log files.

This command is typically used after completing performance analysis or debugging sessions where query logging was temporarily enabled.

!!! warning "Non-Persistent Setting"
    This setting is applied at runtime only and does not persist across node restarts. After a restart, full query logging reverts to the `full_query_logging_options` configuration in `cassandra.yaml`.

    To permanently disable full query logging, ensure it is not configured in `cassandra.yaml`, or set:

    ```yaml
    full_query_logging_options:
        # log_dir: /var/log/cassandra/fql  # Comment out or remove to disable
    ```

---

## Examples

### Basic Usage

```bash
nodetool disablefullquerylog
```

### Disable and Verify

```bash
nodetool disablefullquerylog
nodetool getfullquerylog
# Expected: full_query_logging_path: (disabled)
```

### On Remote Node

```bash
nodetool -h 192.168.1.100 disablefullquerylog
```

---

## Behavior

When full query logging is disabled:

1. No new queries are logged
2. Existing log files remain on disk
3. Log archival continues for existing files
4. Disk I/O overhead from logging is eliminated

### What Continues

| Feature | Status |
|---------|--------|
| Existing FQL log files | Preserved |
| Archive command | Runs for existing logs |
| Query execution | Continues normally |

### What Stops

| Feature | Status |
|---------|--------|
| New query logging | Stops |
| FQL log growth | Stops |
| Logging overhead | Eliminated |

---

## When to Use

### After Performance Analysis

When analysis session is complete:

```bash
# Analysis complete
nodetool disablefullquerylog

# Process collected logs
fqltool dump /var/log/cassandra/fql/ > analysis_queries.txt
```

### Emergency Disk Space

If FQL is consuming too much disk:

```bash
# Disable logging immediately
nodetool disablefullquerylog

# Check disk space recovered
df -h /var/log/cassandra/

# Clean up logs if needed
rm -rf /var/log/cassandra/fql/*
```

### After Debugging Session

When issue investigation is complete:

```bash
# Debug session complete
nodetool disablefullquerylog

# Archive logs for reference
tar -czf debug_fql_$(date +%Y%m%d).tar.gz /var/log/cassandra/fql/
rm -rf /var/log/cassandra/fql/*
```

### Performance Issue Resolution

If FQL is causing latency problems:

```bash
# Check current impact
nodetool proxyhistograms

# Disable FQL
nodetool disablefullquerylog

# Verify latency improvement
nodetool proxyhistograms
```

---

## Impact Assessment

### Immediate Effects

| Aspect | Impact |
|--------|--------|
| Query logging | Stops immediately |
| Disk I/O | Decreases |
| Query latency | May improve (if blocking was enabled) |
| Log file growth | Stops |

### Performance Recovery

| Metric | Expected Change |
|--------|-----------------|
| Write latency | May decrease |
| Disk utilization | Decreases |
| CPU usage | Slight decrease |
| Query throughput | May increase |

---

## Workflow: Complete FQL Session

```bash
#!/bin/bash
# fql_session.sh

FQL_PATH="/var/log/cassandra/fql"
ARCHIVE_DIR="/archive/cassandra/fql"

echo "=== FQL Session Management ==="

# 1. Check if FQL is currently enabled
echo "1. Current FQL status:"
nodetool getfullquerylog

# 2. Disable FQL
echo ""
echo "2. Disabling FQL..."
nodetool disablefullquerylog

# 3. Verify disabled
echo ""
echo "3. Verification:"
nodetool getfullquerylog

# 4. Check captured data
echo ""
echo "4. Captured FQL data:"
if [ -d "$FQL_PATH" ] && [ "$(ls -A $FQL_PATH 2>/dev/null)" ]; then
    echo "Log directory size: $(du -sh $FQL_PATH)"
    echo "Query count: $(fqltool dump $FQL_PATH 2>/dev/null | wc -l)"
else
    echo "No FQL data found"
fi

# 5. Archive if requested
echo ""
read -p "Archive FQL logs? (y/n): " archive
if [ "$archive" = "y" ]; then
    mkdir -p $ARCHIVE_DIR
    archive_file="${ARCHIVE_DIR}/fql_$(date +%Y%m%d_%H%M%S).tar.gz"
    tar -czf $archive_file $FQL_PATH
    echo "Archived to: $archive_file"
fi

# 6. Clean up if requested
echo ""
read -p "Clean up FQL directory? (y/n): " cleanup
if [ "$cleanup" = "y" ]; then
    rm -rf ${FQL_PATH}/*
    echo "FQL directory cleaned"
fi

echo ""
echo "=== FQL Session Complete ==="
```

---

## Managing FQL Logs After Disable

### Preserve Logs

```bash
# After disabling, logs remain
ls -la /var/log/cassandra/fql/

# View log contents
fqltool dump /var/log/cassandra/fql/
```

### Archive Logs

```bash
# Create archive
tar -czf fql_$(date +%Y%m%d).tar.gz /var/log/cassandra/fql/

# Move to archive location
mv fql_*.tar.gz /archive/cassandra/
```

### Analyze Before Cleanup

```bash
# Quick analysis before cleanup
echo "Query Distribution:"
fqltool dump /var/log/cassandra/fql/ | grep -oE "^(SELECT|INSERT|UPDATE|DELETE)" | sort | uniq -c

echo ""
echo "Log Size:"
du -sh /var/log/cassandra/fql/
```

### Clean Up Logs

```bash
# Remove all FQL logs
rm -rf /var/log/cassandra/fql/*

# Verify cleanup
du -sh /var/log/cassandra/fql/
```

---

## Cluster-Wide Operations

### Disable on All Nodes

```bash
#!/bin/bash
# disable_fql_cluster.sh

echo "Disabling FQL cluster-wide..."

nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo -n "$node: "
    nodetool -h $node disablefullquerylog 2>/dev/null && echo "disabled" || echo "FAILED"
done

echo ""
echo "Verification:"
for node in $nodes; do
    echo -n "$node: "
    status=$(nodetool -h $node getfullquerylog 2>/dev/null | grep "enabled")
    echo "$status"
done
```

### Collect Logs from All Nodes

```bash
#!/bin/bash
# collect_fql_cluster.sh

DEST_DIR="/data/fql_collection_$(date +%Y%m%d)"
mkdir -p $DEST_DIR

nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo "Collecting FQL from $node..."
    scp -r $node:/var/log/cassandra/fql/ $DEST_DIR/$node/
done

echo "FQL logs collected to $DEST_DIR"
```

---

## Troubleshooting

### Cannot Disable

```bash
# Check JMX connectivity
nodetool info

# Check for errors
grep -i "fql\|fullquery" /var/log/cassandra/system.log | tail -20
```

### Logs Still Growing After Disable

```bash
# Verify disabled
nodetool getfullquerylog

# If still enabled, retry
nodetool disablefullquerylog

# Check for persistence in cassandra.yaml
grep -A 10 "full_query_logging" /etc/cassandra/cassandra.yaml
```

### Performance Not Improved

```bash
# FQL may not have been the bottleneck
# Check other metrics
nodetool tpstats
nodetool compactionstats
iostat -x 1
```

---

## Best Practices

!!! tip "Disable Guidelines"

    1. **Disable when done** - Don't leave FQL running indefinitely
    2. **Archive before cleanup** - Preserve logs if analysis is needed
    3. **Check disk space** - Verify space is freed after cleanup
    4. **Document findings** - Record analysis results before cleanup
    5. **Cluster consistency** - Disable on all nodes if enabled cluster-wide
    6. **Verify disabled** - Always check with `getfullquerylog`

!!! info "Post-Disable Workflow"

    After disabling FQL:

    1. Verify disabled with `getfullquerylog`
    2. Analyze captured logs with `fqltool dump`
    3. Archive logs if needed for future reference
    4. Clean up log directory to reclaim space
    5. Document any findings from the analysis

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [enablefullquerylog](enablefullquerylog.md) | Enable FQL |
| [getfullquerylog](getfullquerylog.md) | View FQL configuration |
| [resetfullquerylog](resetfullquerylog.md) | Reset FQL path |
| [disableauditlog](disableauditlog.md) | Disable audit logging |
