---
title: "nodetool disableauditlog"
description: "Disable audit logging in Cassandra using nodetool disableauditlog command."
meta:
  - name: keywords
    content: "nodetool disableauditlog, disable audit, Cassandra audit log, security"
---

# nodetool disableauditlog

Disables audit logging on the node.

---

## Synopsis

```bash
nodetool [connection_options] disableauditlog
```

## Description

`nodetool disableauditlog` deactivates the audit logging feature on a Cassandra node. When disabled, the node stops recording audit events for authentication, authorization, and CQL operations.

!!! warning "Non-Persistent Setting"
    This setting is applied at runtime only and does not persist across node restarts. After a restart, audit logging reverts to the configuration in `cassandra.yaml`:

    ```yaml
    audit_logging_options:
        enabled: true    # or false
        logger:
          - class_name: BinAuditLogger
        included_keyspaces:
        excluded_keyspaces: system,system_schema,system_virtual_schema
        included_categories:
        excluded_categories:
    ```

    To permanently disable audit logging, set `enabled: false` in the `audit_logging_options` section of `cassandra.yaml`.

!!! warning "Compliance Impact"
    Disabling audit logging may violate regulatory compliance requirements. Ensure appropriate approvals before disabling in production environments subject to SOX, HIPAA, PCI-DSS, or similar regulations.

---

## Examples

### Basic Usage

```bash
nodetool disableauditlog
```

### Disable and Verify

```bash
nodetool disableauditlog
nodetool getauditlog
# Expected: enabled: false
```

---

## Behavior

When audit logging is disabled:

1. No new audit events are recorded
2. Existing audit logs remain on disk
3. Audit log archival continues for existing files
4. Performance overhead from auditing is eliminated

### What Continues

| Feature | Status |
|---------|--------|
| Existing audit logs | Preserved |
| Log archival | Continues for existing logs |
| All database operations | Continue normally |

### What Stops

| Feature | Status |
|---------|--------|
| New audit event recording | Stops |
| Audit log growth | Stops |
| Audit-related disk I/O | Stops |

---

## When to Use

### Emergency Performance Recovery

If audit logging is causing performance issues:

```bash
# Check current impact
nodetool tpstats

# Disable audit logging
nodetool disableauditlog

# Verify performance improvement
nodetool tpstats
```

### After Troubleshooting Session

When temporary auditing is no longer needed:

```bash
# Investigation complete
nodetool disableauditlog

# Verify disabled
nodetool getauditlog
```

### Disk Space Emergency

If audit logs are consuming too much disk:

```bash
# 1. Disable new audit logging
nodetool disableauditlog

# 2. Archive or remove old audit logs
mv /var/log/cassandra/audit/* /archive/

# 3. Verify disk space freed
df -h /var/log/cassandra/
```

### Before Maintenance

Temporarily disable during maintenance to reduce overhead:

```bash
# Before maintenance
nodetool disableauditlog

# Perform maintenance...

# After maintenance (if compliance requires)
nodetool enableauditlog --included-categories AUTH,DML,DDL,DCL
```

---

## Impact Assessment

### Immediate Effects

| Aspect | Impact |
|--------|--------|
| Audit event recording | Stops immediately |
| Disk I/O from auditing | Eliminated |
| Operation latency | May decrease slightly |
| Compliance coverage | Gaps in audit trail |

### Compliance Implications

| Scenario | Impact |
|----------|--------|
| Operations during disabled period | Not recorded |
| Security incidents | No audit trail |
| Access reviews | Incomplete data |
| Regulatory audits | Potential gap findings |

!!! danger "Audit Trail Gap"
    While audit logging is disabled, there is no record of database access. This creates a gap in the audit trail that may need to be documented and explained during compliance reviews.

---

## Workflow: Controlled Disable/Enable

```bash
#!/bin/bash
# controlled_audit_toggle.sh

echo "=== Audit Logging Control ==="
echo "WARNING: Disabling audit logging creates compliance gaps!"
echo ""

# 1. Document current state
echo "1. Current audit configuration:"
nodetool getauditlog

# 2. Log the disable action
echo ""
echo "2. Logging disable action..."
echo "$(date): Audit logging disabled by $(whoami) - Reason: [DOCUMENT REASON]" >> /var/log/cassandra/audit_changes.log

# 3. Disable audit logging
echo ""
echo "3. Disabling audit logging..."
nodetool disableauditlog

# 4. Verify disabled
echo ""
echo "4. Verification:"
nodetool getauditlog

echo ""
echo "IMPORTANT: Document the duration audit logging is disabled."
echo "Remember to re-enable: nodetool enableauditlog"
```

---

## Cluster-Wide Operations

### Disable on All Nodes

```bash
#!/bin/bash
# disable_audit_cluster.sh

echo "WARNING: Disabling audit logging cluster-wide!"
echo "This will create gaps in the audit trail."
echo ""

# Log the action
echo "$(date): Cluster-wide audit disable initiated by $(whoami)" >> /var/log/audit_changes.log

# Get list of node IPs from local nodetool status
nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo -n "$node: "
    ssh "$node" "nodetool disableauditlog" 2>/dev/null && echo "disabled" || echo "FAILED"
done

echo ""
echo "Verification:"
for node in $nodes; do
    echo -n "$node: "
    ssh "$node" "nodetool getauditlog" 2>/dev/null | grep "enabled"
done
```

---

## Managing Existing Audit Logs

### Preserve Existing Logs

```bash
# After disabling, audit logs remain
ls -la /var/log/cassandra/audit/

# Archive existing logs
tar -czf audit_logs_$(date +%Y%m%d).tar.gz /var/log/cassandra/audit/
```

### Clean Up Audit Logs

```bash
# After disabling, if cleanup is needed
# CAUTION: Ensure logs are archived first if required for compliance

# Remove old audit logs
rm -rf /var/log/cassandra/audit/*.cq4

# Or remove all audit logs
rm -rf /var/log/cassandra/audit/*
```

### Archive Before Cleanup

```bash
#!/bin/bash
# archive_and_cleanup_audit.sh

AUDIT_DIR="/var/log/cassandra/audit"
ARCHIVE_DIR="/archive/cassandra/audit"

# 1. Create archive
timestamp=$(date +%Y%m%d_%H%M%S)
archive_file="${ARCHIVE_DIR}/audit_${timestamp}.tar.gz"

echo "Archiving audit logs to $archive_file..."
tar -czf $archive_file $AUDIT_DIR/

# 2. Verify archive
if [ -f "$archive_file" ]; then
    echo "Archive created successfully: $(ls -lh $archive_file)"

    # 3. Clean up source
    echo "Cleaning up source directory..."
    rm -rf ${AUDIT_DIR}/*

    echo "Cleanup complete."
else
    echo "ERROR: Archive creation failed!"
    exit 1
fi
```

---

## Troubleshooting

### Cannot Disable

```bash
# Check JMX connectivity
nodetool info

# Check for errors
grep -i "audit" /var/log/cassandra/system.log | tail -20
```

### Audit Logs Still Growing After Disable

```bash
# Verify disabled
nodetool getauditlog

# If still showing enabled, retry
nodetool disableauditlog

# Check for configuration override
grep -i "audit" /etc/cassandra/cassandra.yaml
```

### Performance Not Improved After Disable

```bash
# Verify audit logging is truly disabled
nodetool getauditlog | grep enabled

# Check for other I/O sources
iostat -x 1

# Audit logging may not have been the cause
nodetool compactionstats
nodetool tpstats
```

---

## Re-enabling Audit Logging

After investigation or maintenance, re-enable with appropriate settings:

```bash
# Re-enable with previous settings
nodetool enableauditlog \
    --included-categories AUTH,DML,DDL,DCL \
    --excluded-keyspaces system,system_schema

# Verify enabled
nodetool getauditlog

# Log the re-enable action
echo "$(date): Audit logging re-enabled by $(whoami)" >> /var/log/cassandra/audit_changes.log
```

---

## Compliance Documentation

When disabling audit logging, maintain documentation:

```bash
#!/bin/bash
# Document audit logging changes

COMPLIANCE_LOG="/var/log/cassandra/compliance_audit.log"

# Log format: timestamp | action | user | reason | duration
log_entry() {
    echo "$(date -Iseconds) | $1 | $(whoami) | $2 | $3" >> $COMPLIANCE_LOG
}

# Example: Disable with documentation
log_entry "DISABLE" "Performance emergency - ticket INC12345" "Expected 2 hours"
nodetool disableauditlog

# Example: Re-enable with documentation
nodetool enableauditlog --included-categories AUTH,DML,DDL,DCL
log_entry "ENABLE" "Performance issue resolved - ticket INC12345" "N/A"
```

---

## Best Practices

!!! tip "Disable Guidelines"

    1. **Document the reason** - Record why auditing was disabled
    2. **Get approval** - Ensure appropriate authorization
    3. **Minimize duration** - Re-enable as soon as possible
    4. **Archive first** - Preserve existing logs before any cleanup
    5. **Monitor impact** - Verify expected performance improvement
    6. **Plan re-enablement** - Schedule when to re-enable

!!! danger "Compliance Warning"

    - Disabling audit logging creates gaps in the audit trail
    - May violate regulatory requirements
    - Document all periods when auditing was disabled
    - Consider this a temporary measure only
    - Review with compliance/security team before disabling

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [enableauditlog](enableauditlog.md) | Enable audit logging |
| [getauditlog](getauditlog.md) | View audit log configuration |
| [enablefullquerylog](enablefullquerylog.md) | Enable full query logging |
| [disablefullquerylog](disablefullquerylog.md) | Disable full query logging |