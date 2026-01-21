---
title: "nodetool statusbackup"
description: "Check if incremental backup is enabled using nodetool statusbackup command."
meta:
  - name: keywords
    content: "nodetool statusbackup, backup status, incremental backup, Cassandra"
search:
  boost: 3
---

# nodetool statusbackup

Displays the current status of incremental backup on the node.

---

## Synopsis

```bash
nodetool [connection_options] statusbackup
```

## Description

`nodetool statusbackup` reports whether incremental backup is currently enabled on the node. Incremental backup, when enabled, automatically creates hard links to newly flushed SSTables in a `backups` subdirectory.

This command is essential for:

- Verifying backup configuration
- Troubleshooting backup issues
- Auditing backup status across nodes
- Health check scripts

---

## Output

### When Enabled

```
running
```

Incremental backup is active. New SSTables will be linked to the backups directory upon flush.

### When Disabled

```
not running
```

Incremental backup is disabled. No automatic backup links are being created.

---

## Examples

### Basic Usage

```bash
nodetool statusbackup
```

### Cluster-Wide Check

```bash
#!/bin/bash
# Check backup status across all nodes using SSH

for node in node1 node2 node3; do
    echo -n "$node: "
    ssh "$node" "nodetool statusbackup"
done
```

Output:
```
node1: running
node2: running
node3: not running
```

---

## Use Cases

### Verify Backup Configuration

Confirm incremental backup is properly enabled:

```bash
nodetool statusbackup
# Expected: running
```

### Pre-Maintenance Check

Verify backup status before maintenance:

```bash
echo "=== Backup Status Check ==="
echo "Backup status: $(nodetool statusbackup)"

if [ "$(nodetool statusbackup)" = "running" ]; then
    echo "Incremental backup is ENABLED"
else
    echo "WARNING: Incremental backup is DISABLED"
fi
```

### Health Check Script

Include backup status in node health checks:

```bash
#!/bin/bash
# node_health_check.sh

echo "=== Node Health Check ==="
echo "Binary: $(nodetool statusbinary)"
echo "Gossip: $(nodetool statusgossip)"
echo "Backup: $(nodetool statusbackup)"
echo ""

# Alert if backup is unexpectedly disabled
if [ "$(nodetool statusbackup)" != "running" ]; then
    echo "ALERT: Incremental backup is not running!"
fi
```

### Cluster Audit Script

Audit backup status across all nodes:

```bash
#!/bin/bash
# backup_audit.sh

echo "=== Cluster Backup Status Audit ==="
echo ""

# Get list of node IPs from local nodetool
nodes=$(nodetool status | grep -E "^UN|^DN" | awk '{print $2}')
enabled=0
disabled=0

for node in $nodes; do
    status=$(ssh "$node" "nodetool statusbackup" 2>/dev/null)
    if [ "$status" = "running" ]; then
        echo "$node: ENABLED"
        ((enabled++))
    else
        echo "$node: DISABLED"
        ((disabled++))
    fi
done

echo ""
echo "Summary: $enabled enabled, $disabled disabled"
```

---

## Understanding Incremental Backup

### How It Works

When incremental backup is enabled (`running`):

1. Cassandra monitors memtable flushes
2. Each new SSTable gets a hard link created in the `backups` directory
3. Hard links share disk blocks with the original SSTable
4. After compaction removes the original, the backup file becomes the sole reference

### Backup Directory Structure

```
/var/lib/cassandra/data/<keyspace>/<table>-<uuid>/
├── backups/                      # Incremental backups
│   ├── nb-1-big-Data.db
│   ├── nb-1-big-Index.db
│   └── ...
└── snapshots/                    # Point-in-time snapshots
    └── <snapshot_tag>/
```

### Status Implications

| Status | Meaning | New SSTables |
|--------|---------|--------------|
| `running` | Backup enabled | Auto-linked to backups/ |
| `not running` | Backup disabled | No backup links created |

---

## Configuration Methods

### Runtime Toggle

```bash
# Enable
nodetool enablebackup
nodetool statusbackup  # running

# Disable
nodetool disablebackup
nodetool statusbackup  # not running
```

### Persistent Configuration

In `cassandra.yaml`:

```yaml
incremental_backups: true
```

### Runtime vs Persistent

| Method | Persistence | Takes Effect |
|--------|-------------|--------------|
| `enablebackup` / `disablebackup` | Until restart | Immediately |
| `cassandra.yaml` | Permanent | After restart |

---

## Monitoring Integration

### Prometheus Exporter

Export status as metric:

```bash
#!/bin/bash
# Export backup status for Prometheus

status=$(nodetool statusbackup)
if [ "$status" = "running" ]; then
    echo "cassandra_incremental_backup_enabled 1"
else
    echo "cassandra_incremental_backup_enabled 0"
fi
```

### Nagios/Check Script

```bash
#!/bin/bash
# check_cassandra_backup.sh

status=$(nodetool statusbackup 2>/dev/null)

if [ $? -ne 0 ]; then
    echo "UNKNOWN - Cannot connect to Cassandra"
    exit 3
fi

if [ "$status" = "running" ]; then
    echo "OK - Incremental backup is enabled"
    exit 0
else
    echo "WARNING - Incremental backup is disabled"
    exit 1
fi
```

### JSON Health Output

```bash
#!/bin/bash
# Output JSON for monitoring systems

backup_status=$(nodetool statusbackup)
backup_enabled="false"
[ "$backup_status" = "running" ] && backup_enabled="true"

echo "{\"backup_enabled\": $backup_enabled, \"status\": \"$backup_status\"}"
```

---

## Troubleshooting

### Status Shows "not running" Unexpectedly

If backup should be enabled but shows disabled:

```bash
# Check cassandra.yaml setting
grep incremental_backups /etc/cassandra/cassandra.yaml

# Check if runtime disabled
nodetool statusbackup

# Re-enable if needed
nodetool enablebackup

# Verify
nodetool statusbackup
```

### Cannot Determine Status

If command fails:

```bash
# Check JMX connectivity
nodetool info

# Check Cassandra is running
pgrep -f CassandraDaemon

# Check logs
tail /var/log/cassandra/system.log
```

### Backup Files Not Appearing

If status is "running" but no backup files:

```bash
# Verify status
nodetool statusbackup

# Force a flush to generate SSTables
nodetool flush my_keyspace

# Check backup directory
ls -la /var/lib/cassandra/data/my_keyspace/*/backups/
```

---

## Comparing with Snapshots

| Aspect | Incremental Backup | Snapshot |
|--------|-------------------|----------|
| Status check | `statusbackup` | `listsnapshots` |
| Enable/create | `enablebackup` | `snapshot` |
| Disable/clear | `disablebackup` | `clearsnapshot` |
| Automatic | Yes (on flush) | No (manual) |
| Point-in-time | No (continuous) | Yes |
| Restoration | Need baseline + incrementals | Self-contained |

---

## Workflow: Verify Backup Strategy

```bash
#!/bin/bash
# verify_backup_strategy.sh

echo "=== Backup Strategy Verification ==="
echo ""

# Check incremental backup status
echo "1. Incremental Backup Status:"
echo "   $(nodetool statusbackup)"
echo ""

# Check for existing snapshots
echo "2. Existing Snapshots:"
nodetool listsnapshots | tail -5
echo ""

# Check backup directory sizes
echo "3. Backup Directory Sizes:"
du -sh /var/lib/cassandra/data/*/*/backups/ 2>/dev/null | head -5
echo ""

# Check cassandra.yaml configuration
echo "4. Configuration:"
echo "   cassandra.yaml setting:"
grep incremental_backups /etc/cassandra/cassandra.yaml
```

---

## Best Practices

!!! tip "Backup Status Monitoring Guidelines"

    1. **Regular verification** - Check status as part of routine monitoring
    2. **Cluster consistency** - Ensure all nodes have same backup configuration
    3. **Include in health checks** - Add to monitoring dashboards
    4. **Alert on changes** - Notify if backup becomes disabled unexpectedly
    5. **Document expectations** - Know which nodes should have backup enabled
    6. **Combine with snapshots** - Use both incremental and snapshot backups

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [enablebackup](enablebackup.md) | Enable incremental backup |
| [disablebackup](disablebackup.md) | Disable incremental backup |
| [snapshot](snapshot.md) | Create point-in-time backup |
| [listsnapshots](listsnapshots.md) | List existing snapshots |
| [clearsnapshot](clearsnapshot.md) | Remove snapshots |
