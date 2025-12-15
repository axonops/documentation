---
title: "nodetool enableauditlog"
description: "Enable audit logging in Cassandra using nodetool enableauditlog for security compliance."
meta:
  - name: keywords
    content: "nodetool enableauditlog, enable audit, Cassandra audit log, security compliance"
---

# nodetool enableauditlog

Enables audit logging on the node.

---

## Synopsis

```bash
nodetool [connection_options] enableauditlog [options]
```

## Description

`nodetool enableauditlog` activates the audit logging feature on a Cassandra node. When enabled, Cassandra records audit events such as authentication attempts, authorization checks, and CQL operations to a configurable audit log.

Audit logging is essential for:

- **Security compliance** - Meeting regulatory requirements (SOX, HIPAA, PCI-DSS)
- **Security monitoring** - Detecting unauthorized access attempts
- **Forensic analysis** - Investigating security incidents
- **Access tracking** - Recording who accessed what data and when

!!! info "Cassandra 4.0+"
    Audit logging is available in Apache Cassandra 4.0 and later versions.

---

## Options

| Option | Description |
|--------|-------------|
| `--excluded-categories` | Comma-separated list of audit categories to exclude |
| `--excluded-keyspaces` | Comma-separated list of keyspaces to exclude from auditing |
| `--excluded-users` | Comma-separated list of users to exclude from auditing |
| `--included-categories` | Comma-separated list of audit categories to include |
| `--included-keyspaces` | Comma-separated list of keyspaces to include for auditing |
| `--included-users` | Comma-separated list of users to include for auditing |
| `--logger` | Audit logger class name |
| `--roll-cycle` | Log file roll cycle (HOURLY, DAILY, etc.) |
| `--block` | Block operations if audit log is full |
| `--max-archive-retries` | Maximum archive retries |
| `--archive-command` | Archive command for rolled logs |

---

## Audit Categories

| Category | Description |
|----------|-------------|
| `QUERY` | SELECT statements |
| `DML` | INSERT, UPDATE, DELETE statements |
| `DDL` | CREATE, ALTER, DROP statements |
| `DCL` | GRANT, REVOKE statements |
| `AUTH` | Authentication events (login, failed attempts) |
| `PREPARE` | Prepared statement creation |
| `ERROR` | Query errors |
| `OTHER` | Other audit events |

---

## Examples

### Enable with Default Settings

```bash
nodetool enableauditlog
```

### Enable for Specific Categories

```bash
# Only audit authentication and DCL (permissions) events
nodetool enableauditlog --included-categories AUTH,DCL
```

### Exclude System Keyspaces

```bash
# Audit all except system keyspaces
nodetool enableauditlog --excluded-keyspaces system,system_schema,system_auth,system_distributed,system_traces
```

### Audit Specific Users

```bash
# Only audit specific user activity
nodetool enableauditlog --included-users admin,operator

# Or audit everyone except certain users
nodetool enableauditlog --excluded-users monitoring_user,backup_user
```

### Audit Specific Keyspaces

```bash
# Only audit activity on sensitive keyspaces
nodetool enableauditlog --included-keyspaces customer_data,financial_records
```

### Full Configuration Example

```bash
nodetool enableauditlog \
    --included-categories AUTH,DML,DDL,DCL \
    --excluded-keyspaces system,system_schema \
    --excluded-users monitoring \
    --roll-cycle HOURLY \
    --block true
```

### On Remote Node

```bash
nodetool -h 192.168.1.100 enableauditlog --included-categories AUTH,DML
```

---

## Audit Log Output

### Default Location

```
/var/log/cassandra/audit/
```

### Log Format

Audit logs are written in a binary format by default (Chronicle Queue). Each entry contains:

- Timestamp
- User
- Source IP
- Operation type
- Keyspace/Table
- CQL statement
- Status (success/failure)

### Viewing Audit Logs

```bash
# Use auditlogviewer tool
auditlogviewer /var/log/cassandra/audit/

# Or configure a custom logger for text output
```

---

## Configuration in cassandra.yaml

Runtime settings from `enableauditlog` can also be configured persistently:

```yaml
# cassandra.yaml
audit_logging_options:
    enabled: true
    logger:
      - class_name: BinAuditLogger
    included_keyspaces: customer_data,financial
    excluded_keyspaces: system,system_schema
    included_categories: AUTH,DML,DDL,DCL
    excluded_categories:
    included_users:
    excluded_users: monitoring
    roll_cycle: HOURLY
    block: true
    max_queue_weight: 268435456
    max_log_size: 17179869184
    archive_command:
    max_archive_retries: 10
```

---

## Use Cases

### Compliance Auditing

Enable comprehensive auditing for regulatory compliance:

```bash
# PCI-DSS / SOX compliance - audit all data access
nodetool enableauditlog \
    --included-categories AUTH,QUERY,DML,DDL,DCL \
    --excluded-keyspaces system,system_schema,system_auth \
    --roll-cycle DAILY \
    --block true
```

### Security Monitoring

Focus on security-relevant events:

```bash
# Authentication and authorization events
nodetool enableauditlog \
    --included-categories AUTH,DCL,ERROR \
    --roll-cycle HOURLY
```

### Sensitive Data Access

Audit access to specific sensitive data:

```bash
# Only audit customer data keyspace
nodetool enableauditlog \
    --included-keyspaces pii_data,financial_data \
    --included-categories QUERY,DML \
    --roll-cycle HOURLY
```

### Troubleshooting Access Issues

Temporarily enable to investigate access problems:

```bash
# Enable detailed auditing
nodetool enableauditlog \
    --included-categories AUTH,ERROR

# Investigate...

# Disable when done
nodetool disableauditlog
```

---

## Impact Assessment

### Performance Impact

| Factor | Impact |
|--------|--------|
| Disk I/O | Moderate (writes to audit log) |
| CPU | Low to moderate |
| Latency | Slight increase (especially with `--block true`) |
| Disk space | Depends on volume and retention |

!!! warning "Performance Considerations"
    Audit logging adds overhead to every audited operation. In high-throughput environments, carefully select which categories and keyspaces to audit to minimize impact.

### Disk Space Planning

```bash
# Estimate audit log size
# Consider: operations/second * average log entry size * retention period

# Example: 10,000 ops/sec * 200 bytes * 86400 seconds/day = ~172 GB/day
```

---

## Monitoring Audit Logging

### Check Status

```bash
nodetool getauditlog
```

### Monitor Log Growth

```bash
# Check audit log directory size
du -sh /var/log/cassandra/audit/

# Watch log growth
watch -n 60 'du -sh /var/log/cassandra/audit/'
```

### Verify Logging

```bash
# Perform an operation
cqlsh -e "SELECT * FROM system.local LIMIT 1"

# Check audit log (if using text logger)
tail -f /var/log/cassandra/audit/audit.log

# Or use auditlogviewer for binary logs
auditlogviewer /var/log/cassandra/audit/ | tail -10
```

---

## Cluster-Wide Enablement

### Enable on All Nodes

```bash
#!/bin/bash
# enable_audit_cluster.sh

CATEGORIES="AUTH,DML,DDL,DCL"
EXCLUDED_KS="system,system_schema,system_auth"

nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

echo "Enabling audit logging cluster-wide..."
for node in $nodes; do
    echo -n "$node: "
    nodetool -h $node enableauditlog \
        --included-categories $CATEGORIES \
        --excluded-keyspaces $EXCLUDED_KS \
        2>/dev/null && echo "enabled" || echo "FAILED"
done

echo ""
echo "Verification:"
for node in $nodes; do
    echo "=== $node ==="
    nodetool -h $node getauditlog 2>/dev/null
done
```

---

## Troubleshooting

### Audit Log Not Writing

```bash
# Check directory permissions
ls -la /var/log/cassandra/audit/

# Check disk space
df -h /var/log/cassandra/

# Check logs for errors
grep -i "audit" /var/log/cassandra/system.log | tail -20
```

### Performance Degradation After Enable

```bash
# Check if blocking is causing issues
nodetool getauditlog | grep block

# Reduce scope of auditing
nodetool disableauditlog
nodetool enableauditlog --included-categories AUTH,ERROR

# Or disable blocking
nodetool enableauditlog --block false
```

### Log Files Growing Too Fast

```bash
# Narrow down what's being audited
nodetool disableauditlog

# Re-enable with stricter filters
nodetool enableauditlog \
    --included-categories AUTH,DCL \
    --excluded-keyspaces system,system_schema,system_auth,system_distributed,system_traces \
    --excluded-users monitoring,backup
```

---

## Log Management

### Archive Configuration

```bash
# Enable with archive command
nodetool enableauditlog \
    --archive-command "/usr/local/bin/archive_audit.sh %path" \
    --max-archive-retries 3
```

### Manual Log Rotation

```bash
#!/bin/bash
# Audit logs auto-rotate based on roll-cycle
# Manual archive example:

AUDIT_DIR="/var/log/cassandra/audit"
ARCHIVE_DIR="/archive/cassandra/audit"

# Move old logs to archive
find $AUDIT_DIR -name "*.cq4" -mtime +7 -exec mv {} $ARCHIVE_DIR/ \;

# Compress archived logs
find $ARCHIVE_DIR -name "*.cq4" -exec gzip {} \;
```

---

## Best Practices

!!! tip "Audit Logging Guidelines"

    1. **Start narrow** - Begin with critical categories (AUTH, DCL) and expand
    2. **Exclude system keyspaces** - Reduce noise from internal operations
    3. **Monitor disk space** - Audit logs can grow rapidly
    4. **Plan retention** - Establish log rotation and archival policies
    5. **Test performance** - Measure impact before production deployment
    6. **Consistent configuration** - Enable with same settings across all nodes
    7. **Secure audit logs** - Protect logs from tampering

!!! warning "Security Considerations"

    - Audit logs may contain sensitive query parameters
    - Secure the audit log directory with appropriate permissions
    - Consider encryption for audit log archives
    - Implement tamper-evident logging for compliance

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [disableauditlog](disableauditlog.md) | Disable audit logging |
| [getauditlog](getauditlog.md) | View audit log configuration |
| [enablefullquerylog](enablefullquerylog.md) | Enable full query logging |
