---
title: "nodetool statusautocompaction"
description: "Check if auto compaction is enabled for tables using nodetool statusautocompaction."
meta:
  - name: keywords
    content: "nodetool statusautocompaction, compaction status, auto compaction, Cassandra"
---

# nodetool statusautocompaction

Displays the auto-compaction status for specified keyspaces and tables.

---

## Synopsis

```bash
nodetool [connection_options] statusautocompaction [options] [--] [<keyspace> <tables>...]
```
See [connection options](index.md#connection-options) for connection options.

## Description

`nodetool statusautocompaction` reports whether automatic compaction is enabled or disabled for specified tables. This command is essential for verifying the state of auto-compaction after enable/disable operations and for auditing cluster configuration.

Auto-compaction status is a per-table setting that determines whether Cassandra's compaction strategy will automatically schedule compaction tasks.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | Target keyspace name. If omitted, shows status for all keyspaces |
| `tables` | Space-separated list of table names. If omitted, shows all tables in the keyspace |

---

## Options

| Option | Description |
|--------|-------------|
| `-a, --all` | Show per-keyspace/table status instead of summary |

---

## Output

### Summary (Default)

Without `-a/--all`, the command prints a summary:

```
running
```

Possible summary values:

| Output | Meaning |
|--------|---------|
| `running` | All tables have auto-compaction enabled |
| `not running` | All tables have auto-compaction disabled |
| `partially running` | Some tables enabled, some disabled |

### Detailed Output (with -a/--all)

With `-a` option, the command shows per-table status:

```bash
nodetool statusautocompaction -a
```

```
my_keyspace.users running=true
my_keyspace.orders running=true
my_keyspace.products running=false
```

---

## Examples

### Check All Tables

```bash
nodetool statusautocompaction
```

### Check Specific Keyspace

```bash
nodetool statusautocompaction my_keyspace
```

### Check Specific Table

```bash
nodetool statusautocompaction my_keyspace my_table
```

### Check Multiple Tables

```bash
nodetool statusautocompaction my_keyspace users orders products
```

### Check Remote Node

```bash
ssh 192.168.1.100 "nodetool statusautocompaction my_keyspace"
```

---

## Output Interpretation

### Summary Output (without -a)

| Output | Meaning | Action Needed |
|--------|---------|---------------|
| `running` | All tables have auto-compaction enabled | None (normal state) |
| `not running` | All tables have auto-compaction disabled | Investigate and re-enable |
| `partially running` | Mixed status across tables | Use `-a` to identify disabled tables |

### Detailed Output (with -a)

| Output | Meaning | Action Needed |
|--------|---------|---------------|
| `running=true` | Auto-compaction is enabled | None (normal state) |
| `running=false` | Auto-compaction is disabled | Consider re-enabling |

!!! info "Default State"
    All tables have auto-compaction **enabled** (`running=true`) by default. A `running=false` status indicates someone explicitly disabled it.

---

## Use Cases

### Verify After Enable/Disable

Confirm enable/disable commands took effect:

```bash
# After disabling
nodetool disableautocompaction my_keyspace my_table
nodetool statusautocompaction my_keyspace my_table
# Expected: my_keyspace.my_table running=false

# After enabling
nodetool enableautocompaction my_keyspace my_table
nodetool statusautocompaction my_keyspace my_table
# Expected: my_keyspace.my_table running=true
```

### Cluster Audit

Check auto-compaction status across all tables:

```bash
# Quick check - summary
nodetool statusautocompaction

# Find any tables with disabled auto-compaction (use -a for details)
nodetool statusautocompaction -a | grep "running=false"
```

### Health Check Integration

Include in operational health checks:

```bash
#!/bin/bash
# Check for unexpectedly disabled auto-compaction

status=$(nodetool statusautocompaction 2>/dev/null)

if [ "$status" = "running" ]; then
    echo "OK: All tables have auto-compaction enabled"
    exit 0
elif [ "$status" = "not running" ] || [ "$status" = "partially running" ]; then
    echo "WARNING: Auto-compaction is disabled or partially disabled"
    nodetool statusautocompaction -a | grep "running=false"
    exit 1
else
    echo "ERROR: Could not determine status"
    exit 2
fi
```

### Pre-Maintenance Check

Verify state before maintenance operations:

```bash
echo "=== Auto-Compaction Status Before Maintenance ==="
nodetool statusautocompaction my_keyspace

# Perform maintenance...

echo "=== Auto-Compaction Status After Maintenance ==="
nodetool statusautocompaction my_keyspace
```

---

## Monitoring Integration

### Prometheus Exporter

Export status as a metric:

```bash
#!/bin/bash
# Export auto-compaction status for monitoring

nodetool statusautocompaction -a 2>/dev/null | while read line; do
    table=$(echo $line | awk '{print $1}')
    status=$(echo $line | grep -c "running=true")
    echo "cassandra_autocompaction_enabled{table=\"$table\"} $status"
done
```

### Nagios/Icinga Check

```bash
#!/bin/bash
# check_autocompaction.sh

status=$(nodetool statusautocompaction 2>/dev/null)

if [ $? -ne 0 ]; then
    echo "UNKNOWN - Cannot connect to Cassandra"
    exit 3
fi

if [ "$status" = "running" ]; then
    echo "OK - All tables have auto-compaction enabled"
    exit 0
elif [ "$status" = "partially running" ]; then
    disabled_count=$(nodetool statusautocompaction -a 2>/dev/null | grep -c "running=false")
    echo "WARNING - $disabled_count table(s) have auto-compaction disabled"
    exit 1
else
    echo "CRITICAL - All tables have auto-compaction disabled"
    exit 2
fi
```

### JSON Output for Monitoring

```bash
#!/bin/bash
# Output JSON for monitoring systems

echo "{"
echo "  \"timestamp\": \"$(date -Iseconds)\","
echo "  \"tables\": ["

first=true
nodetool statusautocompaction -a 2>/dev/null | while read line; do
    table=$(echo $line | awk '{print $1}')
    enabled=$(echo $line | grep -q "running=true" && echo "true" || echo "false")

    if [ "$first" = true ]; then
        first=false
    else
        echo ","
    fi
    echo -n "    {\"table\": \"$table\", \"enabled\": $enabled}"
done

echo ""
echo "  ]"
echo "}"
```

---

## Cluster-Wide Audit

### Check All Nodes

```bash
#!/bin/bash
# audit_autocompaction_cluster.sh

echo "=== Cluster Auto-Compaction Audit ==="
echo ""

# Get list of node IPs from local nodetool status
nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo "=== Node: $node ==="
    status=$(ssh "$node" 'nodetool statusautocompaction 2>/dev/null')
    if [ "$status" = "running" ]; then
        echo "All tables have auto-compaction enabled"
    else
        echo "Status: $status"
        echo "Tables with disabled auto-compaction:"
        ssh "$node" 'nodetool statusautocompaction -a 2>/dev/null | grep "running=false"'
    fi
    echo ""
done
```

### Compare Across Nodes

```bash
#!/bin/bash
# compare_autocompaction_nodes.sh

# Check if auto-compaction status is consistent across nodes
KEYSPACE="my_keyspace"
TABLE="my_table"

echo "Checking $KEYSPACE.$TABLE across cluster..."

# Get list of node IPs from local nodetool status
nodes=$(nodetool status | grep "^UN" | awk '{print $2}')
statuses=""

for node in $nodes; do
    status=$(ssh "$node" 'nodetool statusautocompaction -a '"$KEYSPACE"' '"$TABLE"' 2>/dev/null | awk '"'"'{print $2}'"'"'')
    echo "$node: $status"
    statuses="$statuses$status\n"
done

unique=$(echo -e "$statuses" | sort -u | grep -v "^$" | wc -l)

if [ "$unique" -eq 1 ]; then
    echo ""
    echo "Status is CONSISTENT across all nodes"
else
    echo ""
    echo "WARNING: Status is INCONSISTENT across nodes!"
fi
```

---

## Common Scenarios

### Finding Forgotten Disabled Tables

```bash
# List all tables with disabled auto-compaction
nodetool statusautocompaction -a | grep "running=false"
```

### Verifying Bulk Load Set up

```bash
# Before bulk load - verify target table is disabled
nodetool statusautocompaction my_keyspace load_target
# Expected: running=false

# After bulk load - verify re-enabled
nodetool statusautocompaction my_keyspace load_target
# Expected: running=true
```

### Checking System Tables

```bash
# System tables should always have auto-compaction enabled
nodetool statusautocompaction system
nodetool statusautocompaction system_schema
```

---

## Troubleshooting

### Command Returns No Output

If no output is returned:

```bash
# Verify keyspace exists
nodetool tablestats | grep "Keyspace:"

# Check specific keyspace
nodetool statusautocompaction existing_keyspace
```

### Connection Errors

```bash
# Check JMX connectivity
nodetool info

# Verify Cassandra is running
pgrep -f CassandraDaemon
```

### Inconsistent Status Across Nodes

If nodes show different statuses:

```bash
# Each node maintains its own auto-compaction state
# After cluster-wide disable, re-enable on all nodes:

for node in $(nodetool status | grep "^UN" | awk '{print $2}'); do
    ssh "$node" "nodetool enableautocompaction my_keyspace my_table"
done
```

---

## Automation Script

```bash
#!/bin/bash
# check_and_report_autocompaction.sh

OUTPUT_FILE="/var/log/cassandra/autocompaction_status_$(date +%Y%m%d).log"

echo "=== Auto-Compaction Status Report ===" | tee $OUTPUT_FILE
echo "Generated: $(date)" | tee -a $OUTPUT_FILE
echo "" | tee -a $OUTPUT_FILE

# Count totals
total=$(nodetool statusautocompaction 2>/dev/null | wc -l)
enabled=$(nodetool statusautocompaction -a 2>/dev/null | grep -c "running=true")
disabled=$(nodetool statusautocompaction -a 2>/dev/null | grep -c "running=false")

echo "Summary:" | tee -a $OUTPUT_FILE
echo "  Total tables: $total" | tee -a $OUTPUT_FILE
echo "  Enabled: $enabled" | tee -a $OUTPUT_FILE
echo "  Disabled: $disabled" | tee -a $OUTPUT_FILE
echo "" | tee -a $OUTPUT_FILE

if [ "$disabled" -gt 0 ]; then
    echo "Tables with disabled auto-compaction:" | tee -a $OUTPUT_FILE
    nodetool statusautocompaction -a | grep "running=false" | tee -a $OUTPUT_FILE
    echo "" | tee -a $OUTPUT_FILE
    echo "ACTION REQUIRED: Review and re-enable if appropriate" | tee -a $OUTPUT_FILE
else
    echo "All tables have auto-compaction enabled." | tee -a $OUTPUT_FILE
fi
```

---

## Best Practices

!!! tip "Status Monitoring Guidelines"

    1. **Regular audits** - Periodically check for disabled auto-compaction
    2. **Include in health checks** - Add to monitoring and alerting
    3. **Verify after changes** - Always check status after enable/disable
    4. **Document disabled tables** - Know why any table has it disabled
    5. **Cluster consistency** - Verify status is consistent across nodes
    6. **Alert on disabled** - Set up alerts for `running=false` status

!!! warning "Disabled Auto-Compaction"
    If `statusautocompaction` shows `running=false` for any table, investigate immediately:

    - Was it intentionally disabled?
    - How long has it been disabled?
    - Is there a plan to re-enable?
    - What is the current SSTable count?

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [enableautocompaction](enableautocompaction.md) | Enable auto-compaction |
| [disableautocompaction](disableautocompaction.md) | Disable auto-compaction |
| [compactionstats](compactionstats.md) | View active compactions |
| [tablestats](tablestats.md) | View SSTable counts |
| [compact](compact.md) | Force manual compaction |