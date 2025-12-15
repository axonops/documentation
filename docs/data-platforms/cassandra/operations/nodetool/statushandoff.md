---
title: "nodetool statushandoff"
description: "Check if hinted handoff is enabled using nodetool statushandoff command."
meta:
  - name: keywords
    content: "nodetool statushandoff, handoff status, hinted handoff, Cassandra"
---

# nodetool statushandoff

Displays the current status of hinted handoff on the node.

---

## Synopsis

```bash
nodetool [connection_options] statushandoff
```

## Description

`nodetool statushandoff` reports whether the hinted handoff mechanism is currently enabled or disabled on the node. This command is essential for verifying the state of hinted handoff after enable/disable operations and for routine health checks.

Hinted handoff is a critical consistency mechanism that stores write hints for temporarily unavailable replicas, ensuring data is delivered when those replicas recover.

---

## Output

### Enabled (Normal State)

```
Hinted handoff is running
```

### Disabled

```
Hinted handoff is not running
```

---

## Examples

### Basic Usage

```bash
nodetool statushandoff
```

### Check After Enable/Disable

```bash
# After disabling
nodetool disablehandoff
nodetool statushandoff
# Expected: Hinted handoff is not running

# After enabling
nodetool enablehandoff
nodetool statushandoff
# Expected: Hinted handoff is running
```

---

## Output Interpretation

| Output | Meaning | Action Needed |
|--------|---------|---------------|
| `Hinted handoff is running` | Handoff is enabled | None (normal state) |
| `Hinted handoff is not running` | Handoff is disabled | Consider re-enabling |

!!! info "Default State"
    Hinted handoff is **enabled** by default. A "not running" status indicates someone explicitly disabled it or it was disabled in `cassandra.yaml`.

---

## Use Cases

### Verify After Operations

Confirm enable/disable commands took effect:

```bash
# Verify after disable
nodetool disablehandoff
nodetool statushandoff
# Confirm: Hinted handoff is not running

# Verify after enable
nodetool enablehandoff
nodetool statushandoff
# Confirm: Hinted handoff is running
```

### Health Check Integration

Include in operational health checks:

```bash
#!/bin/bash
# check_handoff_status.sh

status=$(nodetool statushandoff 2>/dev/null)

if echo "$status" | grep -q "is running"; then
    echo "OK: Hinted handoff is enabled"
    exit 0
else
    echo "WARNING: Hinted handoff is disabled!"
    exit 1
fi
```

### Pre-Maintenance Check

Verify state before maintenance operations:

```bash
echo "=== Hinted Handoff Status Before Maintenance ==="
nodetool statushandoff

# Perform maintenance...

echo "=== Hinted Handoff Status After Maintenance ==="
nodetool statushandoff
```

### Troubleshooting Consistency Issues

When investigating data consistency problems:

```bash
# Check if handoff is enabled
nodetool statushandoff

# If disabled, consistency issues may be due to lost hints
# Re-enable and run repair
nodetool enablehandoff
nodetool repair -pr
```

---

## Monitoring Integration

### Prometheus Exporter

Export status as a metric:

```bash
#!/bin/bash
# Export handoff status for monitoring

status=$(nodetool statushandoff 2>/dev/null)

if echo "$status" | grep -q "is running"; then
    echo "cassandra_hinted_handoff_enabled 1"
else
    echo "cassandra_hinted_handoff_enabled 0"
fi
```

### Nagios/Icinga Check

```bash
#!/bin/bash
# check_hinted_handoff.sh

status=$(nodetool statushandoff 2>/dev/null)

if [ $? -ne 0 ]; then
    echo "UNKNOWN - Cannot connect to Cassandra"
    exit 3
fi

if echo "$status" | grep -q "is running"; then
    echo "OK - Hinted handoff is enabled"
    exit 0
else
    echo "CRITICAL - Hinted handoff is disabled"
    exit 2
fi
```

### JSON Output for Monitoring

```bash
#!/bin/bash
# Output JSON for monitoring systems

status=$(nodetool statushandoff 2>/dev/null)
enabled=$(echo "$status" | grep -q "is running" && echo "true" || echo "false")

cat <<EOF
{
  "timestamp": "$(date -Iseconds)",
  "metric": "hinted_handoff_status",
  "enabled": $enabled,
  "status_message": "$status"
}
EOF
```

---

## Cluster-Wide Audit

### Check All Nodes

```bash
#!/bin/bash
# audit_handoff_cluster.sh

echo "=== Cluster Hinted Handoff Audit ==="
echo ""

# Get list of node IPs from local nodetool status
nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

all_enabled=true
for node in $nodes; do
    status=$(ssh "$node" "nodetool statushandoff" 2>/dev/null)
    echo -n "$node: "

    if echo "$status" | grep -q "is running"; then
        echo "ENABLED"
    else
        echo "DISABLED"
        all_enabled=false
    fi
done

echo ""
if [ "$all_enabled" = true ]; then
    echo "Status: All nodes have hinted handoff enabled"
else
    echo "WARNING: Some nodes have hinted handoff disabled!"
fi
```

### Verify Cluster Consistency

```bash
#!/bin/bash
# verify_handoff_consistency.sh

# Get list of node IPs from local nodetool status
nodes=$(nodetool status | grep "^UN" | awk '{print $2}')
enabled_count=0
disabled_count=0

for node in $nodes; do
    status=$(ssh "$node" "nodetool statushandoff" 2>/dev/null)
    if echo "$status" | grep -q "is running"; then
        ((enabled_count++))
    else
        ((disabled_count++))
    fi
done

total=$((enabled_count + disabled_count))

echo "Hinted Handoff Status Summary:"
echo "  Total nodes: $total"
echo "  Enabled: $enabled_count"
echo "  Disabled: $disabled_count"

if [ "$disabled_count" -gt 0 ] && [ "$enabled_count" -gt 0 ]; then
    echo ""
    echo "WARNING: Inconsistent state across cluster!"
    echo "Consider enabling on all nodes for consistency."
fi
```

---

## Understanding Status Context

### Status vs Pause State

The `statushandoff` command shows whether hint storage is enabled, not whether delivery is paused:

| Command | What It Checks |
|---------|----------------|
| `statushandoff` | Is hint storage enabled? |
| N/A (check tpstats) | Is hint delivery active? |

```bash
# Check both hint storage and delivery status
echo "Hint Storage Status:"
nodetool statushandoff

echo ""
echo "Hint Delivery Activity:"
nodetool tpstats | grep -i hint
```

### Related Status Commands

```bash
# Complete hint system status check
echo "=== Hinted Handoff System Status ==="

echo "1. Handoff Status:"
nodetool statushandoff

echo ""
echo "2. Pending Hints:"
nodetool listpendinghints

echo ""
echo "3. Hint Thread Pool:"
nodetool tpstats | grep -i hint

echo ""
echo "4. Hints Table Size:"
nodetool tablestats system.hints 2>/dev/null | grep "Space used" || echo "No hints table data"
```

---

## Configuration Check

### Compare Runtime vs Config

```bash
#!/bin/bash
# Check if runtime matches configuration

echo "=== Hinted Handoff Configuration Check ==="

# Runtime status
echo "Runtime Status:"
nodetool statushandoff

# Configuration file
echo ""
echo "cassandra.yaml Setting:"
grep "hinted_handoff_enabled" /etc/cassandra/cassandra.yaml 2>/dev/null || echo "Not found in config"

# Compare
runtime_enabled=$(nodetool statushandoff 2>/dev/null | grep -q "is running" && echo "true" || echo "false")
config_enabled=$(grep "hinted_handoff_enabled" /etc/cassandra/cassandra.yaml 2>/dev/null | grep -q "true" && echo "true" || echo "false")

echo ""
if [ "$runtime_enabled" != "$config_enabled" ]; then
    echo "WARNING: Runtime status differs from configuration!"
    echo "  Runtime: $runtime_enabled"
    echo "  Config: $config_enabled"
    echo "  This may indicate a runtime change that won't persist after restart."
else
    echo "Runtime status matches configuration."
fi
```

---

## Troubleshooting

### Command Returns Error

```bash
# Check JMX connectivity
nodetool info

# Verify Cassandra is running
pgrep -f CassandraDaemon
```

### Unexpected Status

If status doesn't match expectations:

```bash
# Check cassandra.yaml setting
grep hinted_handoff_enabled /etc/cassandra/cassandra.yaml

# Check for recent enable/disable commands in logs
grep -i "hint" /var/log/cassandra/system.log | tail -20
```

### Status Differs Across Nodes

If nodes show different statuses:

```bash
#!/bin/bash
# Each node maintains its own handoff state
# Synchronize by running on all nodes via SSH:

for node in $(nodetool status | grep "^UN" | awk '{print $2}'); do
    ssh "$node" "nodetool enablehandoff"
done

# Verify consistency
for node in $(nodetool status | grep "^UN" | awk '{print $2}'); do
    echo -n "$node: "
    ssh "$node" "nodetool statushandoff"
done
```

---

## Automation Script

```bash
#!/bin/bash
# handoff_status_report.sh

OUTPUT_FILE="/var/log/cassandra/handoff_status_$(date +%Y%m%d).log"

echo "=== Hinted Handoff Status Report ===" | tee $OUTPUT_FILE
echo "Generated: $(date)" | tee -a $OUTPUT_FILE
echo "" | tee -a $OUTPUT_FILE

# Local node status
echo "Local Node Status:" | tee -a $OUTPUT_FILE
nodetool statushandoff | tee -a $OUTPUT_FILE

echo "" | tee -a $OUTPUT_FILE

# Pending hints
echo "Pending Hints:" | tee -a $OUTPUT_FILE
nodetool listpendinghints 2>/dev/null | tee -a $OUTPUT_FILE

echo "" | tee -a $OUTPUT_FILE

# Hint configuration
echo "Configuration:" | tee -a $OUTPUT_FILE
grep -E "hinted_handoff|max_hint" /etc/cassandra/cassandra.yaml 2>/dev/null | tee -a $OUTPUT_FILE

echo "" | tee -a $OUTPUT_FILE

# Assessment
status=$(nodetool statushandoff 2>/dev/null)
if echo "$status" | grep -q "is running"; then
    echo "Assessment: Hinted handoff is ENABLED (normal state)" | tee -a $OUTPUT_FILE
else
    echo "Assessment: Hinted handoff is DISABLED - ACTION REQUIRED" | tee -a $OUTPUT_FILE
    echo "Recommendation: Re-enable with 'nodetool enablehandoff'" | tee -a $OUTPUT_FILE
fi
```

---

## Best Practices

!!! tip "Status Monitoring Guidelines"

    1. **Regular checks** - Include in routine health monitoring
    2. **Cluster consistency** - Verify all nodes have the same status
    3. **Verify after changes** - Always check status after enable/disable
    4. **Alert on disabled** - Set up alerts for "not running" status
    5. **Document changes** - Log when and why status was changed
    6. **Compare to config** - Ensure runtime matches intended configuration

!!! warning "Disabled Hinted Handoff"
    If `statushandoff` shows "not running", investigate immediately:

    - Was it intentionally disabled?
    - How long has it been disabled?
    - Are there any down nodes that would have needed hints?
    - Is repair scheduled to restore consistency?

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [enablehandoff](enablehandoff.md) | Enable hinted handoff |
| [disablehandoff](disablehandoff.md) | Disable hinted handoff |
| [pausehandoff](pausehandoff.md) | Pause hint delivery |
| [resumehandoff](resumehandoff.md) | Resume hint delivery |
| [listpendinghints](listpendinghints.md) | List pending hints |
| [truncatehints](truncatehints.md) | Remove all hints |
