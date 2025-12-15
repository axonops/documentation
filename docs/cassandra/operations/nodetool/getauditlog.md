---
title: "nodetool getauditlog"
description: "Display current audit log configuration in Cassandra using nodetool getauditlog."
meta:
  - name: keywords
    content: "nodetool getauditlog, audit log config, Cassandra audit, security settings"
---

# nodetool getauditlog

Displays the current audit logging configuration.

---

## Synopsis

```bash
nodetool [connection_options] getauditlog
```

## Description

`nodetool getauditlog` retrieves and displays the current audit logging configuration on a Cassandra node. This command shows whether auditing is enabled and all associated settings including included/excluded categories, keyspaces, and users.

---

## Output

### When Enabled

```
enabled: true
logger: BinAuditLogger
included_keyspaces: customer_data,financial
excluded_keyspaces: system,system_schema,system_auth
included_categories: AUTH,DML,DDL,DCL
excluded_categories:
included_users:
excluded_users: monitoring
roll_cycle: HOURLY
block: true
max_queue_weight: 268435456
max_log_size: 17179869184
```

### When Disabled

```
enabled: false
logger:
included_keyspaces:
excluded_keyspaces:
included_categories:
excluded_categories:
included_users:
excluded_users:
roll_cycle:
block:
max_queue_weight:
max_log_size:
```

---

## Examples

### Basic Usage

```bash
nodetool getauditlog
```

### Check Specific Field

```bash
# Check if enabled
nodetool getauditlog | grep "enabled:"

# Check what categories are being audited
nodetool getauditlog | grep "included_categories"
```

### Check Remote Node

```bash
nodetool -h 192.168.1.100 getauditlog
```

---

## Output Fields

| Field | Description |
|-------|-------------|
| `enabled` | Whether audit logging is active |
| `logger` | Audit logger class name |
| `included_keyspaces` | Keyspaces being audited (if set) |
| `excluded_keyspaces` | Keyspaces excluded from auditing |
| `included_categories` | Audit event categories being captured |
| `excluded_categories` | Categories excluded from auditing |
| `included_users` | Users being audited (if set) |
| `excluded_users` | Users excluded from auditing |
| `roll_cycle` | Log file rotation frequency |
| `block` | Whether to block operations if log is full |
| `max_queue_weight` | Maximum queue size in bytes |
| `max_log_size` | Maximum total log size |

---

## Use Cases

### Verify After Configuration Change

Confirm settings after enabling audit logging:

```bash
# Enable with specific settings
nodetool enableauditlog --included-categories AUTH,DML --excluded-keyspaces system

# Verify configuration
nodetool getauditlog
```

### Health Check

Include in operational health checks:

```bash
#!/bin/bash
# check_audit_status.sh

config=$(nodetool getauditlog 2>/dev/null)

if echo "$config" | grep -q "enabled: true"; then
    echo "OK: Audit logging is enabled"

    # Check for recommended settings
    if echo "$config" | grep -q "AUTH"; then
        echo "  - AUTH events are being audited"
    else
        echo "  WARNING: AUTH events not being audited"
    fi

    if echo "$config" | grep -q "block: true"; then
        echo "  - Blocking mode is enabled (recommended)"
    else
        echo "  - Non-blocking mode (events may be lost)"
    fi

    exit 0
else
    echo "CRITICAL: Audit logging is disabled!"
    exit 2
fi
```

### Compliance Verification

Verify audit configuration meets compliance requirements:

```bash
#!/bin/bash
# compliance_check.sh

echo "=== Audit Logging Compliance Check ==="

config=$(nodetool getauditlog 2>/dev/null)
issues=0

# Check enabled
if ! echo "$config" | grep -q "enabled: true"; then
    echo "FAIL: Audit logging is not enabled"
    ((issues++))
else
    echo "PASS: Audit logging is enabled"
fi

# Check required categories
required_categories=("AUTH" "DML" "DDL" "DCL")
categories=$(echo "$config" | grep "included_categories" | cut -d: -f2)

for cat in "${required_categories[@]}"; do
    if echo "$categories" | grep -q "$cat"; then
        echo "PASS: $cat category is being audited"
    else
        echo "FAIL: $cat category is NOT being audited"
        ((issues++))
    fi
done

# Check blocking mode
if echo "$config" | grep -q "block: true"; then
    echo "PASS: Blocking mode enabled"
else
    echo "WARN: Non-blocking mode - audit events may be lost"
fi

echo ""
if [ $issues -eq 0 ]; then
    echo "Compliance check PASSED"
else
    echo "Compliance check FAILED - $issues issue(s) found"
fi
```

### Cluster Audit Consistency

Verify audit configuration is consistent across nodes:

```bash
#!/bin/bash
# check_audit_consistency.sh

echo "=== Cluster Audit Configuration Check ==="

nodes=$(nodetool status | grep "^UN" | awk '{print $2}')
first_config=""

for node in $nodes; do
    config=$(nodetool -h $node getauditlog 2>/dev/null)

    if [ -z "$first_config" ]; then
        first_config="$config"
        echo "Reference node: $node"
        echo "$config"
        echo ""
    else
        if [ "$config" = "$first_config" ]; then
            echo "$node: CONSISTENT"
        else
            echo "$node: DIFFERS"
            echo "Differences:"
            diff <(echo "$first_config") <(echo "$config")
        fi
    fi
done
```

---

## Monitoring Integration

### Prometheus Exporter

```bash
#!/bin/bash
# Export audit config as metrics

config=$(nodetool getauditlog 2>/dev/null)

# Enabled status
enabled=$(echo "$config" | grep "enabled:" | grep -q "true" && echo "1" || echo "0")
echo "cassandra_audit_logging_enabled $enabled"

# Blocking mode
blocking=$(echo "$config" | grep "block:" | grep -q "true" && echo "1" || echo "0")
echo "cassandra_audit_logging_blocking $blocking"

# Max log size
max_size=$(echo "$config" | grep "max_log_size:" | awk '{print $2}')
[ -n "$max_size" ] && echo "cassandra_audit_max_log_size_bytes $max_size"
```

### JSON Output

```bash
#!/bin/bash
# Output audit config as JSON

config=$(nodetool getauditlog 2>/dev/null)

enabled=$(echo "$config" | grep "enabled:" | awk '{print $2}')
logger=$(echo "$config" | grep "logger:" | cut -d: -f2 | xargs)
categories=$(echo "$config" | grep "included_categories:" | cut -d: -f2 | xargs)
block=$(echo "$config" | grep "block:" | awk '{print $2}')

cat <<EOF
{
  "timestamp": "$(date -Iseconds)",
  "audit_logging": {
    "enabled": $enabled,
    "logger": "$logger",
    "included_categories": "$categories",
    "blocking": $block
  }
}
EOF
```

---

## Troubleshooting

### Command Returns Empty

```bash
# Check JMX connectivity
nodetool info

# Check Cassandra version (audit logging requires 4.0+)
nodetool version
```

### Unexpected Configuration

```bash
# Compare with cassandra.yaml settings
grep -A 20 "audit_logging_options" /etc/cassandra/cassandra.yaml

# Runtime changes may differ from config file
# Settings from enableauditlog override cassandra.yaml until restart
```

### Configuration Not Taking Effect

```bash
# Verify the enable command worked
nodetool getauditlog | grep enabled

# If still showing unexpected config, re-enable
nodetool enableauditlog --included-categories AUTH,DML,DDL,DCL
```

---

## Configuration Comparison

### Runtime vs Persistent

| Setting Source | Persistence | Scope |
|----------------|-------------|-------|
| `enableauditlog` | Until restart | This node only |
| `cassandra.yaml` | Permanent | All restarts |

```bash
# Show runtime config
echo "=== Runtime Configuration ==="
nodetool getauditlog

# Show file config
echo ""
echo "=== cassandra.yaml Configuration ==="
grep -A 15 "audit_logging_options" /etc/cassandra/cassandra.yaml
```

---

## Audit Configuration Report

```bash
#!/bin/bash
# generate_audit_report.sh

OUTPUT_FILE="/var/log/cassandra/audit_config_$(date +%Y%m%d).log"

echo "=== Audit Logging Configuration Report ===" | tee $OUTPUT_FILE
echo "Generated: $(date)" | tee -a $OUTPUT_FILE
echo "Node: $(hostname)" | tee -a $OUTPUT_FILE
echo "" | tee -a $OUTPUT_FILE

echo "Current Configuration:" | tee -a $OUTPUT_FILE
nodetool getauditlog 2>/dev/null | tee -a $OUTPUT_FILE

echo "" | tee -a $OUTPUT_FILE
echo "Audit Log Directory:" | tee -a $OUTPUT_FILE
ls -la /var/log/cassandra/audit/ 2>/dev/null | tee -a $OUTPUT_FILE

echo "" | tee -a $OUTPUT_FILE
echo "Audit Log Size:" | tee -a $OUTPUT_FILE
du -sh /var/log/cassandra/audit/ 2>/dev/null | tee -a $OUTPUT_FILE

echo "" | tee -a $OUTPUT_FILE
echo "Disk Usage:" | tee -a $OUTPUT_FILE
df -h /var/log/cassandra/ | tee -a $OUTPUT_FILE
```

---

## Best Practices

!!! tip "Configuration Verification"

    1. **Regular checks** - Periodically verify audit configuration
    2. **After changes** - Always check config after enable/disable
    3. **Cluster consistency** - Ensure all nodes have same config
    4. **Compare to requirements** - Verify against compliance needs
    5. **Document settings** - Keep record of intended configuration
    6. **Monitor disk space** - Check log growth alongside config

!!! info "Configuration Tips"

    - Runtime settings from `enableauditlog` don't persist across restarts
    - For permanent configuration, update `cassandra.yaml`
    - Consider both runtime and file settings when troubleshooting

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [enableauditlog](enableauditlog.md) | Enable audit logging |
| [disableauditlog](disableauditlog.md) | Disable audit logging |
| [enablefullquerylog](enablefullquerylog.md) | Enable full query logging |
| [getfullquerylog](getfullquerylog.md) | View full query log config |
