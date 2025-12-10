# nodetool drain

Flushes all memtables and stops accepting connections, preparing the node for a clean shutdown.

## Synopsis

```bash
nodetool [connection_options] drain
```

## Description

The `drain` command performs a graceful preparation for node shutdown. It flushes all memtables to disk, stops listening for CQL connections, and disables gossip participation. After draining, the node remains running but is no longer functional—it must be restarted to resume operations.

This is the recommended command before stopping Cassandra for maintenance, upgrades, or planned downtime.

## Process

### Drain Steps

1. **Stop listening for connections** - No new CQL connections accepted
2. **Stop gossip** - Node stops participating in cluster gossip
3. **Flush all memtables** - All in-memory data written to SSTables
4. **Finish pending operations** - Complete in-flight requests
5. **Enter drained state** - Node is idle but process remains running

### Post-Drain State

After drain completes:
- Node is marked as down in gossip (other nodes see it as `DN`)
- No client connections are possible
- No new writes are accepted
- Process remains running
- **Node cannot resume** - restart required

## Examples

### Standard Graceful Shutdown

```bash
# Drain the node
nodetool drain

# Stop the Cassandra service
sudo systemctl stop cassandra
```

### Scripted Shutdown

```bash
#!/bin/bash
# Graceful shutdown script

echo "Draining node..."
nodetool drain

if [ $? -eq 0 ]; then
    echo "Drain complete, stopping service..."
    sudo systemctl stop cassandra
    echo "Cassandra stopped"
else
    echo "ERROR: Drain failed"
    exit 1
fi
```

### With Timeout Handling

```bash
#!/bin/bash
# Drain with timeout

TIMEOUT=300  # 5 minutes

echo "Starting drain with ${TIMEOUT}s timeout..."
timeout $TIMEOUT nodetool drain

if [ $? -eq 0 ]; then
    echo "Drain successful"
    sudo systemctl stop cassandra
elif [ $? -eq 124 ]; then
    echo "WARNING: Drain timed out after ${TIMEOUT}s"
    echo "Forcing shutdown..."
    sudo systemctl stop cassandra
else
    echo "ERROR: Drain failed with exit code $?"
    exit 1
fi
```

## Duration

Drain duration depends primarily on memtable size:

| Memtable Size | Approximate Duration |
|---------------|---------------------|
| < 100 MB | Seconds |
| 100 MB - 1 GB | 10-30 seconds |
| 1 - 5 GB | 30 seconds - 2 minutes |
| > 5 GB | Several minutes |

**Factors affecting duration:**
- Total memtable data size across all tables
- Disk I/O speed
- Compression settings
- Number of tables with data

## Monitoring

### Before Drain

Check current memtable sizes:
```bash
nodetool tablestats | grep "Memtable data size"
```

### During Drain

The drain command blocks until complete. Monitor from another session:
```bash
# Check if node is still accepting connections
nodetool status

# Check flush progress
nodetool tpstats | grep MemtableFlushWriter
```

## Drain vs Flush

| Aspect | `nodetool flush` | `nodetool drain` |
|--------|-----------------|------------------|
| Flushes memtables | Yes | Yes |
| Stops connections | No | Yes |
| Stops gossip | No | Yes |
| Node remains operational | Yes | No |
| Reversible | Yes | No (restart required) |

**Use flush when:** Taking a snapshot, freeing memory, preparing for compaction
**Use drain when:** Shutting down, maintenance, upgrades

## Common Use Cases

### Rolling Restart

```bash
#!/bin/bash
# Rolling restart of single node

# Check node is healthy before restart
nodetool status | grep "^UN.*$(hostname -i)" || exit 1

# Drain
nodetool drain

# Restart
sudo systemctl restart cassandra

# Wait for node to rejoin
sleep 30
until nodetool status | grep "^UN.*$(hostname -i)"; do
    echo "Waiting for node to come up..."
    sleep 10
done

echo "Node restarted successfully"
```

### Pre-Upgrade Shutdown

```bash
#!/bin/bash
# Shutdown before Cassandra upgrade

echo "Preparing for upgrade..."

# Flush all data
nodetool drain

# Stop service
sudo systemctl stop cassandra

# Verify process is stopped
if pgrep -x "java" | xargs -I {} cat /proc/{}/cmdline 2>/dev/null | grep -q cassandra; then
    echo "ERROR: Cassandra process still running"
    exit 1
fi

echo "Node ready for upgrade"
```

## Troubleshooting

### Drain Hangs

**Symptoms:** Command does not complete.

**Investigation:**
```bash
# Check flush activity
nodetool tpstats | grep -E "Flush|Pending"

# Check for blocked operations
nodetool tpstats | grep -v "0         0"
```

**Possible causes:**
- Large memtables taking time to flush
- Disk I/O bottleneck
- Blocked thread pool

**Resolution:**
```bash
# If drain is stuck too long, force shutdown (less graceful)
sudo systemctl stop cassandra
```

### Node Marked Down But Not Drained

If node is marked down but drain wasn't run:
- Other nodes may send hints
- Commitlog will be replayed on restart (longer startup)
- No data loss, but less efficient

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Drain completed successfully |
| 1 | Error occurred during drain |

## Related Commands

- [nodetool flush](flush.md) - Flush without stopping connections
- [nodetool status](status.md) - Check cluster state
- [nodetool info](info.md) - Check node state
- [nodetool stopdaemon](stopdaemon.md) - Stop Cassandra daemon

## Version Information

Available in all Apache Cassandra versions with consistent behavior.
