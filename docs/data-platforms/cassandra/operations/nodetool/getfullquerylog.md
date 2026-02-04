---
title: "nodetool getfullquerylog"
description: "Display full query log configuration in Cassandra using nodetool getfullquerylog."
meta:
  - name: keywords
    content: "nodetool getfullquerylog, FQL config, query logging, Cassandra"
---

# nodetool getfullquerylog

Displays the current full query logging configuration.

---

## Synopsis

```bash
nodetool [connection_options] getfullquerylog
```
See [connection options](index.md#connection-options) for connection options.

## Description

`nodetool getfullquerylog` retrieves and displays the current full query logging (FQL) configuration on a Cassandra node. This command shows whether FQL is enabled, the log path, roll cycle, and other configuration parameters.

---

## Output

### When Enabled

```
enabled             true
log_dir             /var/log/cassandra/fql
archive_command
roll_cycle          HOURLY
block               true
max_log_size        17179869184
max_queue_weight    268435456
max_archive_retries 10
```

### When Disabled

The command shows the configuration from `cassandra.yaml` even when FQL is disabled. Fields will reflect configured values, not necessarily empty:

```
enabled             false
log_dir             /var/log/cassandra/fql
archive_command
roll_cycle          HOURLY
...
```

---

## Examples

### Basic Usage

```bash
nodetool getfullquerylog
```

### Check Specific Field

```bash
# Check if enabled
nodetool getfullquerylog | grep "enabled"

# Check log path
nodetool getfullquerylog | grep "log_dir"
```

### Check Remote Node

```bash
ssh 192.168.1.100 "nodetool getfullquerylog"
```

---

## Output Fields

| Field | Description |
|-------|-------------|
| `enabled` | Whether FQL is active |
| `log_dir` | Path where FQL logs are written |
| `archive_command` | Command executed for log archival |
| `roll_cycle` | Log file rotation frequency (MINUTELY, HOURLY, DAILY) |
| `block` | Whether to block queries if logging falls behind |
| `max_log_size` | Maximum total log size in bytes |
| `max_queue_weight` | Maximum in-memory queue size in bytes |
| `max_archive_retries` | Maximum retries for archive command |

---

## Use Cases

### Verify Configuration After Enable

```bash
# Enable FQL
nodetool enablefullquerylog --path /var/log/cassandra/fql --roll-cycle HOURLY

# Verify configuration
nodetool getfullquerylog
```

### Health Check Integration

```bash
#!/bin/bash
# check_fql_status.sh

config=$(nodetool getfullquerylog 2>/dev/null)

if echo "$config" | grep -q "enabled.*true"; then
    echo "FQL Status: ENABLED"

    log_dir=$(echo "$config" | grep "log_dir" | awk '{print $2}')
    block=$(echo "$config" | grep "block" | awk '{print $2}')

    echo "  Log Directory: $log_dir"
    echo "  Blocking Mode: $block"

    if [ -d "$log_dir" ]; then
        echo "  Log Size: $(du -sh $log_dir | awk '{print $1}')"
    fi

    exit 0
else
    echo "FQL Status: DISABLED"
    exit 0
fi
```

### Monitor FQL Configuration

```bash
#!/bin/bash
# fql_status_report.sh

echo "=== Full Query Logging Status ==="
echo "Timestamp: $(date)"
echo ""

# Get configuration
config=$(nodetool getfullquerylog 2>/dev/null)
echo "Configuration:"
echo "$config"

# If enabled, show additional info
if echo "$config" | grep -q "enabled.*true"; then
    log_dir=$(echo "$config" | grep "log_dir" | awk '{print $2}')
    max_size=$(echo "$config" | grep "max_log_size" | awk '{print $2}')

    echo ""
    echo "Log Directory Status:"
    if [ -d "$log_dir" ]; then
        current_size=$(du -sb $log_dir 2>/dev/null | awk '{print $1}')
        echo "  Current Size: $current_size bytes"
        echo "  Max Size: $max_size bytes"
        echo "  Usage: $(awk "BEGIN {printf \"%.1f\", ($current_size/$max_size)*100}")%"
        echo "  Files: $(ls -1 $log_dir 2>/dev/null | wc -l)"
    else
        echo "  Log directory does not exist"
    fi
fi
```

### Cluster Configuration Check

```bash
#!/bin/bash
# check_fql_cluster.sh

echo "=== Cluster FQL Configuration ==="

# Get list of node IPs from local nodetool status
nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo ""
    echo "=== $node ==="
    ssh "$node" "nodetool getfullquerylog 2>/dev/null"
done
```

### Verify Cluster Consistency

```bash
#!/bin/bash
# verify_fql_consistency.sh

# Get list of node IPs from local nodetool status
nodes=$(nodetool status | grep "^UN" | awk '{print $2}')
enabled_count=0
disabled_count=0

echo "FQL Status by Node:"
for node in $nodes; do
    config=$(ssh "$node" "nodetool getfullquerylog 2>/dev/null)"
    if echo "$config" | grep -q "enabled.*true"; then
        echo "$node: ENABLED"
        ((enabled_count++))
    else
        echo "$node: DISABLED"
        ((disabled_count++))
    fi
done

echo ""
echo "Summary:"
echo "  Enabled: $enabled_count"
echo "  Disabled: $disabled_count"

if [ "$enabled_count" -gt 0 ] && [ "$disabled_count" -gt 0 ]; then
    echo ""
    echo "WARNING: Inconsistent FQL state across cluster!"
fi
```

---

## Monitoring Integration

### Prometheus Exporter

```bash
#!/bin/bash
# Export FQL config as metrics

config=$(nodetool getfullquerylog 2>/dev/null)

# Enabled status
enabled=$(echo "$config" | grep "enabled" | grep -q "true" && echo "1" || echo "0")
echo "cassandra_fql_enabled $enabled"

if [ "$enabled" = "1" ]; then
    # Blocking mode
    blocking=$(echo "$config" | grep "block" | grep -q "true" && echo "1" || echo "0")
    echo "cassandra_fql_blocking $blocking"

    # Max log size
    max_size=$(echo "$config" | grep "max_log_size" | awk '{print $2}')
    [ -n "$max_size" ] && echo "cassandra_fql_max_log_size_bytes $max_size"

    # Current log size
    log_dir=$(echo "$config" | grep "log_dir" | awk '{print $2}')
    if [ -d "$log_dir" ]; then
        current_size=$(du -sb $log_dir 2>/dev/null | awk '{print $1}')
        echo "cassandra_fql_current_size_bytes $current_size"
    fi
fi
```

### JSON Output

```bash
#!/bin/bash
# Output FQL config as JSON

config=$(nodetool getfullquerylog 2>/dev/null)

enabled=$(echo "$config" | grep "enabled" | awk '{print $2}')
log_dir=$(echo "$config" | grep "log_dir" | awk '{print $2}')
roll_cycle=$(echo "$config" | grep "roll_cycle" | awk '{print $2}')
block=$(echo "$config" | grep "block" | awk '{print $2}')
max_log_size=$(echo "$config" | grep "max_log_size" | awk '{print $2}')

cat <<EOF
{
  "timestamp": "$(date -Iseconds)",
  "full_query_logging": {
    "enabled": $enabled,
    "log_dir": "$log_dir",
    "roll_cycle": "$roll_cycle",
    "block": $block,
    "max_log_size": $max_log_size
  }
}
EOF
```

---

## Troubleshooting

### Command Returns Error

```bash
# Check JMX connectivity
nodetool info

# Check Cassandra version (FQL requires 4.0+)
nodetool version
```

### Empty or Unexpected Configuration

```bash
# Compare with cassandra.yaml
grep -A 10 "full_query_logging_options" /etc/cassandra/cassandra.yaml

# Runtime settings may differ from config file
```

### Log Directory Issues

```bash
# Get log directory from config
log_dir=$(nodetool getfullquerylog | grep "log_dir" | awk '{print $2}')

# Check if directory exists
ls -la $log_dir

# Check permissions
stat $log_dir

# Check disk space
df -h $log_dir
```

---

## Configuration Comparison

### Runtime vs Persistent

| Setting Source | Persistence | Scope |
|----------------|-------------|-------|
| `enablefullquerylog` | Until restart | This node only |
| `cassandra.yaml` | Permanent | All restarts |

```bash
# Show both configurations
echo "=== Runtime Configuration ==="
nodetool getfullquerylog

echo ""
echo "=== cassandra.yaml Configuration ==="
grep -A 10 "full_query_logging_options" /etc/cassandra/cassandra.yaml
```

---

## FQL Configuration Report

```bash
#!/bin/bash
# fql_report.sh

OUTPUT_FILE="/var/log/cassandra/fql_config_$(date +%Y%m%d).log"

echo "=== Full Query Logging Configuration Report ===" | tee $OUTPUT_FILE
echo "Generated: $(date)" | tee -a $OUTPUT_FILE
echo "Node: $(hostname)" | tee -a $OUTPUT_FILE
echo "" | tee -a $OUTPUT_FILE

echo "Current Configuration:" | tee -a $OUTPUT_FILE
nodetool getfullquerylog 2>/dev/null | tee -a $OUTPUT_FILE

echo "" | tee -a $OUTPUT_FILE

# If enabled, show log info
config=$(nodetool getfullquerylog 2>/dev/null)
if echo "$config" | grep -q "enabled.*true"; then
    log_dir=$(echo "$config" | grep "log_dir" | awk '{print $2}')

    echo "Log Directory Contents:" | tee -a $OUTPUT_FILE
    ls -la $log_dir 2>/dev/null | tee -a $OUTPUT_FILE

    echo "" | tee -a $OUTPUT_FILE
    echo "Log Directory Size:" | tee -a $OUTPUT_FILE
    du -sh $log_dir 2>/dev/null | tee -a $OUTPUT_FILE

    echo "" | tee -a $OUTPUT_FILE
    echo "Disk Usage:" | tee -a $OUTPUT_FILE
    df -h $log_dir 2>/dev/null | tee -a $OUTPUT_FILE
fi
```

---

## Best Practices

!!! tip "Configuration Monitoring"

    1. **Verify after enable** - Always check config after enabling FQL
    2. **Monitor log growth** - Watch `log_dir` size regularly
    3. **Check blocking mode** - Understand performance implications
    4. **Cluster consistency** - Verify same config across nodes
    5. **Compare to limits** - Track current size vs `max_log_size`
    6. **Document settings** - Record intended configuration

!!! info "Configuration Tips"

    - Runtime settings from `enablefullquerylog` don't persist across restarts
    - For permanent configuration, update `cassandra.yaml`
    - Consider blocking mode impact on production latency
    - Set appropriate `max_log_size` to prevent disk exhaustion

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [enablefullquerylog](enablefullquerylog.md) | Enable FQL |
| [disablefullquerylog](disablefullquerylog.md) | Disable FQL |
| [resetfullquerylog](resetfullquerylog.md) | Reset FQL path |
| [getauditlog](getauditlog.md) | View audit log config |