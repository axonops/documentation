---
title: "nodetool stopdaemon"
description: "Stop Cassandra daemon process using nodetool stopdaemon command."
meta:
  - name: keywords
    content: "nodetool stopdaemon, stop Cassandra, shutdown daemon, Cassandra"
---

# nodetool stopdaemon

Stops the Cassandra daemon process.

---

## Synopsis

```bash
nodetool [connection_options] stopdaemon
```
See [connection options](index.md#connection-options) for connection options.

## Description

`nodetool stopdaemon` sends a shutdown signal to the Cassandra process, terminating the daemon. This is a **hard stop** that does not perform graceful draining—use `drain` first for a clean shutdown.

!!! warning "Not Graceful"
    `stopdaemon` does not flush memtables or complete pending operations. For graceful shutdown, always run `drain` before `stopdaemon`.

---

## Behavior

When `stopdaemon` is executed:

1. JMX shutdown signal is sent to Cassandra
2. Cassandra process begins termination
3. In-flight requests may be interrupted
4. Unflushed memtable data remains in commit log
5. Process exits

What does NOT happen:
- Memtables are not flushed to SSTables
- Pending operations are not completed
- Gossip shutdown notification is not sent
- Other nodes are not informed gracefully

---

## Examples

### Basic Usage

```bash
nodetool stopdaemon
```

### Graceful Shutdown (Recommended)

```bash
# First drain (graceful)
nodetool drain

# Then stop
nodetool stopdaemon
```

### Emergency Stop

When immediate shutdown is required:

```bash
nodetool stopdaemon
```

---

## When to Use

### After Drain

The recommended shutdown sequence:

```bash
# 1. Drain first (flushes data, stops accepting requests)
nodetool drain

# 2. Stop the daemon
nodetool stopdaemon
```

### Emergency Situations

When immediate shutdown is critical:

```bash
# Stop immediately (not graceful)
nodetool stopdaemon
```

Use emergency stop when:
- Node is causing cluster-wide issues
- Runaway process consuming resources
- Security incident requiring immediate isolation
- `drain` is hanging or not responding

### After drain Completes

Once drain finishes, `stopdaemon` simply terminates the process:

```bash
# Drain completes
nodetool drain
# INFO: DRAINED

# Safe to stop now
nodetool stopdaemon
```

---

## Comparison: drain vs stopdaemon

| Action | drain | stopdaemon |
|--------|-------|------------|
| Flush memtables | Yes | No |
| Complete pending requests | Yes | No |
| Stop gossip | Yes | Immediate |
| Stop native transport | Yes | Immediate |
| Notify other nodes | Yes | No |
| Process exits | No | Yes |
| Data safety | Safe | Requires commit log replay |

### Graceful Shutdown Sequence

| Step | Command | What Happens |
|------|---------|--------------|
| 1 | `drain` | Flush memtables, stop accepting requests, stop gossip |
| 2 | `stopdaemon` | Exit process (data is safe) |

### Emergency Shutdown Sequence

| Step | Command | What Happens |
|------|---------|--------------|
| 1 | `stopdaemon` | Immediate exit (commit log replay needed on restart) |

---

## Post-Stop Verification

### Verify Process Stopped

```bash
# Check for Cassandra process
pgrep -f CassandraDaemon
# Should return nothing (no output)

# Alternative
ps aux | grep CassandraDaemon | grep -v grep
# Should return nothing
```

### Verify Ports Released

```bash
# CQL port
netstat -tlnp | grep 9042
# Should return nothing

# JMX port
netstat -tlnp | grep 7199
# Should return nothing

# Inter-node port
netstat -tlnp | grep 7000
# Should return nothing
```

### All-in-One Verification

```bash
#!/bin/bash
# verify_stopped.sh

echo "=== Cassandra Stop Verification ==="
echo ""

# Process check
pid=$(pgrep -f CassandraDaemon)
if [ -z "$pid" ]; then
    echo "Process: STOPPED"
else
    echo "Process: STILL RUNNING (PID: $pid)"
fi

# Port checks
for port in 9042 7199 7000 7001; do
    if netstat -tlnp 2>/dev/null | grep -q ":$port "; then
        echo "Port $port: IN USE"
    else
        echo "Port $port: FREE"
    fi
done
```

---

## Alternatives to stopdaemon

### systemd (Recommended for Production)

```bash
# Stop via systemd (usually runs drain internally)
systemctl stop cassandra
```

Most distribution packages configure systemd to call `drain` before stopping.

### init.d

```bash
service cassandra stop
```

### kill Command (Last Resort)

```bash
# Find PID
pid=$(pgrep -f CassandraDaemon)

# Normal kill (SIGTERM)
kill $pid

# Force kill if unresponsive (SIGKILL)
kill -9 $pid
```

!!! danger "Force Kill"
    `kill -9` should only be used when the process is completely unresponsive. It prevents any cleanup and may require longer commit log replay.

### Comparison of Stop Methods

| Method | Graceful | Runs Drain | Recommended |
|--------|----------|------------|-------------|
| `nodetool drain && stopdaemon` | Yes | Yes | Yes |
| `systemctl stop cassandra` | Usually | Depends on unit file | Yes |
| `nodetool stopdaemon` alone | No | No | Emergency only |
| `kill <pid>` | Partial | No | Last resort |
| `kill -9 <pid>` | No | No | Extreme emergency |

---

## Workflow: Planned Maintenance Stop

```bash
#!/bin/bash
# graceful_stop.sh

echo "=== Graceful Cassandra Shutdown ==="
echo ""

# 1. Check current state
echo "1. Pre-stop status:"
echo "   Binary: $(nodetool statusbinary)"
echo "   Gossip: $(nodetool statusgossip)"

# 2. Drain
echo ""
echo "2. Draining node..."
nodetool drain
echo "   Drain complete"

# 3. Stop daemon
echo ""
echo "3. Stopping daemon..."
nodetool stopdaemon

# 4. Wait for process exit
echo ""
echo "4. Waiting for process to exit..."
for i in {1..30}; do
    if ! pgrep -f CassandraDaemon > /dev/null; then
        echo "   Process stopped"
        break
    fi
    sleep 1
done

# 5. Verify
echo ""
echo "5. Verification:"
if pgrep -f CassandraDaemon > /dev/null; then
    echo "   WARNING: Process still running!"
else
    echo "   Cassandra stopped successfully"
fi
```

---

## Workflow: Emergency Stop

```bash
#!/bin/bash
# emergency_stop.sh

echo "=== EMERGENCY STOP ==="
echo "WARNING: This is not a graceful shutdown!"
echo ""

# Immediate stop
nodetool stopdaemon

# Wait briefly
sleep 5

# Check if stopped
if pgrep -f CassandraDaemon > /dev/null; then
    echo "Process still running, forcing kill..."
    pkill -9 -f CassandraDaemon
    sleep 2
fi

# Final check
if pgrep -f CassandraDaemon > /dev/null; then
    echo "ERROR: Cannot stop Cassandra!"
    exit 1
else
    echo "Cassandra stopped"
    echo "NOTE: Commit log replay will occur on restart"
fi
```

---

## After Stop: Restart Considerations

### If Stopped Without Drain

When Cassandra restarts after `stopdaemon` without `drain`:

1. Commit log is replayed
2. Unflushed memtable data is recovered
3. Startup may take longer
4. Data integrity is maintained (commit log is durable)

```bash
# Start after emergency stop
systemctl start cassandra

# Monitor startup (may be slower due to replay)
tail -f /var/log/cassandra/system.log | grep -i "replay\|starting\|listening"
```

### If Stopped After Drain

Clean restart:

```bash
# Normal start
systemctl start cassandra

# Quick startup expected
tail -f /var/log/cassandra/system.log | grep -i "starting\|listening"
```

---

## Troubleshooting

### stopdaemon Doesn't Work

If JMX command fails:

```bash
# Check JMX connectivity
nodetool info
# If this fails, JMX is unreachable

# Use kill instead
pid=$(pgrep -f CassandraDaemon)
kill $pid
```

### Process Hangs After stopdaemon

If process doesn't exit:

```bash
# Check process state
ps aux | grep CassandraDaemon

# Check what it's doing
strace -p $(pgrep -f CassandraDaemon) 2>&1 | head -20

# Force kill if necessary
kill -9 $(pgrep -f CassandraDaemon)
```

### Cannot Connect to JMX

```bash
# If nodetool can't connect
nodetool stopdaemon
# Error: Failed to connect to '127.0.0.1:7199'

# Use systemctl or kill instead
systemctl stop cassandra
# or
kill $(pgrep -f CassandraDaemon)
```

---

## Best Practices

!!! tip "Shutdown Guidelines"

    1. **Always drain first** - Run `nodetool drain` before `stopdaemon`
    2. **Use systemd in production** - Prefer `systemctl stop` for managed shutdown
    3. **Verify stopped** - Confirm process exited and ports released
    4. **Document emergency stops** - Log when and why emergency stop was used
    5. **Allow startup time** - Expect longer restart after non-graceful stop
    6. **Reserve for emergencies** - Only use `stopdaemon` alone when drain is not viable

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [drain](drain.md) | Graceful prepare for shutdown |
| [status](status.md) | Check cluster status before stop |
| [info](info.md) | Node information |
| [disablebinary](disablebinary.md) | Stop client connections |
| [disablegossip](disablegossip.md) | Stop cluster communication |