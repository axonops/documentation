---
title: "nodetool drain"
description: "Prepare Cassandra node for shutdown using nodetool drain. Flushes memtables and stops accepting writes."
meta:
  - name: keywords
    content: "nodetool drain, Cassandra shutdown, flush memtables, graceful shutdown"
---

# nodetool drain

Drains the node by flushing all memtables, stopping acceptance of writes, and preparing for shutdown.

---

## Synopsis

```bash
nodetool [connection_options] drain
```
See [connection options](index.md#connection-options) for connection options.

## Description

`nodetool drain` gracefully prepares a node for shutdown by:

1. Flushing all memtables to SSTables
2. Stopping native transport (CQL connections)
3. Stopping gossip
4. Stopping accepting writes
5. Completing in-flight requests

This ensures no data loss when stopping Cassandra.

---

## When to Use

### Before Stopping Cassandra

!!! tip "Always Drain Before Shutdown"
    ```bash
    nodetool drain
    sudo systemctl stop cassandra
    ```

    Without drain, Cassandra must replay commit logs on restart, which takes longer.

### Before Upgrades

```bash
nodetool drain
sudo systemctl stop cassandra
# Perform upgrade
sudo systemctl start cassandra
```

### Before Maintenance

```bash
nodetool drain
# Node is now safe to work on
```

---

## When NOT to Use

### For Quick Restart

If Cassandra needs to restart quickly and data persistence is not critical:

```bash
# Faster but commit log replay on startup
sudo systemctl stop cassandra
```

However, this is rarely recommended.

### When Node Will Be Removed

If decommissioning the node:

```bash
# Use decommission instead
nodetool decommission
```

---

## Drain Process

| Step | Action | Description |
|------|--------|-------------|
| 1 | Stop accepting new connections | No new client connections accepted |
| 2 | Complete in-flight requests | Allow current requests to finish |
| 3 | Flush all memtables to disk | Ensures all data in memory is written to SSTables |
| 4 | Stop gossip | Node stops communicating with cluster |
| 5 | Stop native transport | CQL connections closed |
| 6 | Enter DRAINED state | Node is safe to stop |

!!! info "After Drain"
    Node is now safe to stop. The Cassandra process is still running but not accepting work.

---

## After Drain

### Node State

```bash
nodetool info
# Shows: Mode: DRAINED
```

### Behavior

| Feature | State |
|---------|-------|
| CQL connections | Refused |
| Gossip | Stopped |
| Writes | Rejected |
| Reads | May still work briefly |
| JMX | Still available |

### Stopping Cassandra

```bash
# After drain completes
sudo systemctl stop cassandra

# Or
pkill -f CassandraDaemon
```

---

## Examples

### Standard Shutdown

```bash
nodetool drain
sudo systemctl stop cassandra
```

### Shutdown Script

```bash
#!/bin/bash
echo "Draining node..."
nodetool drain

echo "Waiting for drain to complete..."
while nodetool info 2>/dev/null | grep -q "Mode: NORMAL"; do
    sleep 1
done

echo "Stopping Cassandra..."
sudo systemctl stop cassandra
echo "Done"
```

### Remote Drain

```bash
ssh 192.168.1.101 "nodetool drain"
ssh 192.168.1.101 'sudo systemctl stop cassandra'
```

---

## Monitoring Drain

### Check Progress

```bash
# Watch memtable flush
nodetool tpstats | grep -i flush

# Check mode
nodetool info | grep Mode
```

### Drain Complete

When drain completes:
```
Mode: DRAINED
```

### Logs

```bash
tail -f /var/log/cassandra/system.log | grep -i drain
```

---

## Common Issues

### Drain Times Out

If drain takes too long:

1. Check for large memtables
2. Check disk I/O performance
3. Check for pending tasks

```bash
nodetool tpstats
nodetool compactionstats
```

### "Cannot drain - already drained"

Node was already drained:

```bash
# Just stop the process
sudo systemctl stop cassandra
```

### Connections Still Active After Drain

Some connections may linger briefly. Drain stops new connections but allows in-flight requests to complete.

### Stuck in Draining State

If drain doesn't complete:

```bash
# Check what's blocking
nodetool tpstats
nodetool info

# Last resort: force stop
sudo systemctl stop cassandra
```

!!! warning "Force Stop Risk"
    Force stopping without drain completing requires commit log replay on restart.

---

## Drain vs. Other Commands

| Command | Purpose | Continues Running |
|---------|---------|-------------------|
| `drain` | Prepare for shutdown | Yes (drained state) |
| `stopdaemon` | Stop Cassandra immediately | No |
| `disablebinary` | Stop CQL only | Yes (operational) |
| `disablegossip` | Stop gossip only | Yes (isolated) |

### When to Use Each

| Scenario | Command |
|----------|---------|
| Graceful shutdown | `drain` then stop |
| Emergency stop | `stopdaemon` (last resort) |
| Maintenance (keep running) | `disablebinary` |
| Network troubleshooting | `disablegossip` |

---

## Recovery from Drained State

To return a drained node to service:

```bash
# Must restart Cassandra
sudo systemctl restart cassandra
```

There is no "undrain" command. The node must be restarted.

---

## Best Practices

!!! tip "Drain Guidelines"
    1. **Always drain before shutdown** - Prevents data loss
    2. **Wait for completion** - Check mode is DRAINED
    3. **Include in scripts** - Automate shutdown procedures
    4. **Monitor during drain** - Catch any issues
    5. **Plan for duration** - Large memtables take time to flush

### Shutdown Checklist

- [ ] Check node status: `nodetool status`
- [ ] Drain the node: `nodetool drain`
- [ ] Verify drained: `nodetool info | grep Mode`
- [ ] Stop service: `sudo systemctl stop cassandra`
- [ ] Verify stopped: `pgrep -f CassandraDaemon`

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [flush](flush.md) | Flushes memtables only |
| [disablebinary](disablebinary.md) | Disables CQL only |
| [disablegossip](disablegossip.md) | Disables gossip only |
| [info](info.md) | Check drain state |