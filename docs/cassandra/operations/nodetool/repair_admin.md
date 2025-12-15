---
title: "nodetool repair_admin"
description: "Manage and monitor repair operations in Cassandra using nodetool repair_admin."
meta:
  - name: keywords
    content: "nodetool repair_admin, repair management, repair status, Cassandra"
---

# nodetool repair_admin

Manages and monitors repair sessions on the cluster.

---

## Synopsis

```bash
nodetool [connection_options] repair_admin <list | cancel | cleanup> [options]
```

## Description

`nodetool repair_admin` provides administrative control over repair sessions:

- **list**: View active and recent repair sessions
- **cancel**: Stop a running repair
- **cleanup**: Clean up orphaned repair sessions (Cassandra 4.0+)

Essential for managing repairs in production environments.

---

## Subcommands

### list

List repair sessions.

```bash
nodetool repair_admin list [--all]
```

| Option | Description |
|--------|-------------|
| `--all` | Include completed repairs, not just active |

### cancel

Cancel a running repair.

```bash
nodetool repair_admin cancel <session_id>
```

### cleanup (4.0+)

Clean up orphaned repair metadata.

```bash
nodetool repair_admin cleanup
```

---

## Examples

### List Active Repairs

```bash
nodetool repair_admin list
```

Output:
```
id                                   state        command          coordinator                  participants                 last_update
a1b2c3d4-e5f6-7890-abcd-ef1234567890 RUNNING      RANGE            192.168.1.101                192.168.1.101,192.168.1.102  2024-01-15T10:30:00Z
b2c3d4e5-f6a7-8901-bcde-f12345678901 RUNNING      VALIDATION       192.168.1.102                192.168.1.102,192.168.1.103  2024-01-15T10:31:00Z
```

### List All Repairs (Including Completed)

```bash
nodetool repair_admin list --all
```

Shows history of repairs including completed and failed.

### Cancel a Repair

```bash
nodetool repair_admin cancel a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### Clean Up Orphaned Sessions (4.0+)

```bash
nodetool repair_admin cleanup
```

---

## Output Fields

### Repair Session Information

| Field | Description |
|-------|-------------|
| id | Unique session identifier (UUID) |
| state | Current state (RUNNING, FAILED, COMPLETED) |
| command | Repair type (RANGE, VALIDATION, SYNC) |
| coordinator | Node coordinating the repair |
| participants | Nodes involved in the repair |
| last_update | Timestamp of last status update |

### Session States

| State | Description |
|-------|-------------|
| RUNNING | Repair is in progress |
| COMPLETED | Repair finished successfully |
| FAILED | Repair encountered an error |

---

## When to Use

### Monitor Active Repairs

Before starting maintenance:

```bash
nodetool repair_admin list
```

Check if repairs are already running.

### Diagnose Slow Repairs

```bash
nodetool repair_admin list --all
```

View repair history to identify patterns.

### Cancel Stuck Repairs

When a repair is hung or needs to be stopped:

```bash
# Find the session ID
nodetool repair_admin list

# Cancel it
nodetool repair_admin cancel <session_id>
```

### Before Topology Changes

Ensure no repairs are running before:

- Decommission
- Adding nodes
- Major maintenance

```bash
nodetool repair_admin list
# Should show no RUNNING repairs
```

---

## Canceling Repairs

### When to Cancel

!!! warning "Cancel Considerations"
    Cancel repairs when:

    - Repair is stuck (no progress)
    - Emergency maintenance needed
    - Repair started by mistake
    - Repair is impacting production too heavily

### How to Cancel

```bash
# Get session ID
nodetool repair_admin list

# Cancel the session
nodetool repair_admin cancel a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### After Canceling

Canceled repairs leave data partially synchronized:

1. Data already streamed remains in place
2. Unprocessed ranges were not repaired
3. Run repair again later to complete synchronization

---

## Repair States Deep Dive

### Running Repair

```
id                                   state        command
a1b2c3d4-...                        RUNNING      RANGE
```

Active repair - do not interfere unless necessary.

### Failed Repair

```
id                                   state        command
b2c3d4e5-...                        FAILED       VALIDATION
```

!!! danger "Investigate Failures"
    Failed repairs indicate:

    - Node unreachable
    - Timeout occurred
    - Resource exhaustion
    - SSTable corruption

    Check logs for details:
    ```bash
    grep -i "repair.*failed\|repair.*error" /var/log/cassandra/system.log
    ```

### Orphaned Sessions

Sessions that didn't clean up properly:

```bash
# Clean up orphaned metadata
nodetool repair_admin cleanup
```

---

## Monitoring Best Practices

### Before Starting Repair

```bash
# Check for existing repairs
nodetool repair_admin list

# Verify cluster health
nodetool status
```

### During Repair

```bash
# Watch progress
watch -n 30 'nodetool repair_admin list'

# Monitor streaming
nodetool netstats
```

### After Repair

```bash
# Verify completion
nodetool repair_admin list --all | grep COMPLETED

# Check for failures
nodetool repair_admin list --all | grep FAILED
```

---

## Common Issues

### Cannot Find Session ID

If `repair_admin list` shows no sessions but repair seems running:

- Check other nodes (repair coordinator may be different)
- Check `nodetool netstats` for streaming activity

### Cancel Doesn't Work

If cancel doesn't stop the repair:

1. Verify correct session ID
2. Try from the coordinator node
3. Check logs for errors
4. May need to wait for current streaming to complete

### Repairs Start Automatically

Unexpected repairs may be from:

- Scheduled repair tools (AxonOps, Reaper)
- Cron jobs
- Application-triggered repairs

Check all potential sources.

---

## Integration with Repair Tools

### AxonOps

AxonOps manages repairs automatically:

```bash
# View repairs including those managed by AxonOps
nodetool repair_admin list --all
```

Repairs started by AxonOps appear with distinctive session IDs.

### Cassandra Reaper

If using Reaper for repair management:

- Repairs appear in `repair_admin list`
- Cancel through Reaper UI when possible
- Use `repair_admin cancel` only if needed

---

## Scripting Examples

### Check for Active Repairs

```bash
#!/bin/bash
if nodetool repair_admin list | grep -q RUNNING; then
    echo "Repairs are running"
    exit 1
else
    echo "No active repairs"
    exit 0
fi
```

### Cancel All Repairs

```bash
#!/bin/bash
# Emergency: cancel all running repairs
for session in $(nodetool repair_admin list | grep RUNNING | awk '{print $1}'); do
    echo "Canceling $session"
    nodetool repair_admin cancel "$session"
done
```

### Monitor Repair Progress

```bash
#!/bin/bash
while true; do
    clear
    echo "=== Repair Status $(date) ==="
    nodetool repair_admin list
    echo ""
    echo "=== Network Activity ==="
    nodetool netstats | head -20
    sleep 30
done
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [repair](repair.md) | Start repair operations |
| [netstats](netstats.md) | Monitor streaming during repair |
| [status](status.md) | Check cluster state |
| [tpstats](tpstats.md) | Monitor repair thread pools |
| [compactionstats](compactionstats.md) | Validation compactions during repair |
