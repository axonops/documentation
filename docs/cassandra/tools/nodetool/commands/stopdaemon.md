# nodetool stopdaemon

Stops the Cassandra daemon process.

## Synopsis

```bash
nodetool [connection_options] stopdaemon
```

## Description

The `stopdaemon` command sends a shutdown signal to the Cassandra daemon, causing it to terminate. Unlike `drain`, this command does not flush memtables before stopping—it initiates an immediate shutdown.

!!! warning "Not Recommended for Normal Use"
    For graceful shutdowns, use `nodetool drain` followed by `systemctl stop cassandra`. The `stopdaemon` command should only be used when other shutdown methods fail or in specific automation scenarios.

## Behavior

### What stopdaemon Does

1. Sends shutdown signal to Cassandra JVM
2. Cassandra begins shutdown sequence
3. Process terminates

### What stopdaemon Does NOT Do

- Does not flush memtables (data in memtables will be recovered from commitlog on restart)
- Does not wait for in-flight operations to complete
- Does not gracefully remove node from gossip

## Examples

### Stop the Daemon

```bash
nodetool stopdaemon
```

### Verify Process Stopped

```bash
# Check if process is still running
ps aux | grep cassandra

# Or check service status
systemctl status cassandra
```

## Comparison with Other Shutdown Methods

| Method | Flushes Memtables | Graceful | Recommended |
|--------|-------------------|----------|-------------|
| `nodetool drain` + `systemctl stop` | Yes | Yes | Yes |
| `nodetool stopdaemon` | No | Partial | No |
| `systemctl stop cassandra` | No | Partial | For scripts |
| `kill -9` | No | No | Emergency only |

## When to Use

### Appropriate Use Cases

- Automation scripts where drain has already been run
- When JMX is available but systemd is not
- Testing and development environments
- When other shutdown methods fail

### When NOT to Use

- Normal production shutdowns (use drain + systemctl stop)
- When data integrity is critical (drain first)
- Rolling restarts (drain first)

## Graceful Shutdown Process

The recommended shutdown sequence:

```bash
#!/bin/bash
# Recommended graceful shutdown

# 1. Drain the node (flush memtables, stop connections)
nodetool drain

# 2. Stop the service
sudo systemctl stop cassandra

# Alternative if systemd not available:
# nodetool stopdaemon
```

## Recovery After Non-Graceful Shutdown

If `stopdaemon` was used without `drain`:

1. **On restart**: Cassandra replays commitlog to recover unflushed data
2. **Startup time**: May be longer due to commitlog replay
3. **Data integrity**: No data loss (commitlog contains all writes)

```bash
# Monitor commitlog replay on startup
tail -f /var/log/cassandra/system.log | grep -i commitlog
```

## Troubleshooting

### Command Fails

```bash
# Check JMX connectivity
nodetool info

# If JMX fails, use systemctl
sudo systemctl stop cassandra

# If systemctl fails, use kill
sudo pkill -f CassandraDaemon
```

### Process Doesn't Stop

```bash
# Check if still running
pgrep -f CassandraDaemon

# Force kill if necessary (last resort)
sudo pkill -9 -f CassandraDaemon
```

### Node Stuck in Shutdown

```bash
# Check what threads are active
jstack $(pgrep -f CassandraDaemon) > /tmp/thread_dump.txt

# Review for stuck threads
grep -A 20 "BLOCKED\|WAITING" /tmp/thread_dump.txt
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Shutdown signal sent successfully |
| 1 | Error sending shutdown signal |

## Related Commands

| Command | Purpose |
|---------|---------|
| [drain](../../../operations/nodetool/drain.md) | Flush and prepare for shutdown (recommended) |
| [info](../../../operations/nodetool/info.md) | Check node status |
| [status](../../../operations/nodetool/status.md) | Check cluster status |

## Version Information

Available in all Apache Cassandra versions.

## Best Practices

!!! tip "Shutdown Guidelines"

    1. **Always drain first** in production environments
    2. **Use systemctl** for service management when available
    3. **Reserve stopdaemon** for automation or when other methods fail
    4. **Monitor startup** after non-graceful shutdown for commitlog replay
    5. **Document** if stopdaemon is used in scripts and why
