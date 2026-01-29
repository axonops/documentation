---
title: "nodetool setlogginglevel"
description: "Set logging level for Cassandra classes using nodetool setlogginglevel command."
meta:
  - name: keywords
    content: "nodetool setlogginglevel, logging level, debug logging, Cassandra logs"
---

# nodetool setlogginglevel

Changes the logging level for a class or package at runtime.

---

## Synopsis

```bash
nodetool [connection_options] setlogginglevel [<class|component>] [<level>]
```

## Description

`nodetool setlogginglevel` dynamically changes the logging level for a specific Java class, package, or built-in component without restarting Cassandra. This is useful for debugging issues in production.

!!! warning "Non-Persistent Setting"
    This setting is applied at runtime only and does not persist across node restarts. After a restart, the logging levels revert to the configuration in `logback.xml`.

!!! info "Reset All Loggers"
    Calling `nodetool setlogginglevel` with **no arguments** resets all logging levels to the initial configuration from `logback.xml`.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `class` | Fully qualified class name, package, or built-in component name. If omitted with level, resets all loggers |
| `level` | Log level: TRACE, DEBUG, INFO, WARN, ERROR, OFF. If omitted, resets the specified logger |

### Built-in Component Shortcuts

The command supports component shortcuts that map to predefined logger sets:

| Component | Description | Mapped Loggers |
|-----------|-------------|----------------|
| `bootstrap` | Bootstrap operations | Bootstrap-related loggers |
| `compaction` | Compaction operations | `org.apache.cassandra.db.compaction` |
| `repair` | Repair operations | `org.apache.cassandra.repair` |
| `streaming` | Streaming operations | `org.apache.cassandra.streaming` |
| `cql` | CQL query handling | CQL transport loggers |
| `ring` | Ring/token management | Ring-related loggers |

---

## Log Levels

| Level | Description |
|-------|-------------|
| `TRACE` | Most verbose; detailed tracing information |
| `DEBUG` | Debugging information |
| `INFO` | Informational messages (default) |
| `WARN` | Warning messages |
| `ERROR` | Error messages only |
| `OFF` | Disable logging |

---

## Examples

### Enable Debug for Compaction

```bash
nodetool setlogginglevel org.apache.cassandra.db.compaction DEBUG
```

### Enable Debug for Gossip

```bash
nodetool setlogginglevel org.apache.cassandra.gms DEBUG
```

### Enable Debug for Repair

```bash
nodetool setlogginglevel org.apache.cassandra.repair DEBUG
```

### Enable Debug for All Cassandra Classes

```bash
nodetool setlogginglevel org.apache.cassandra DEBUG
```

### Enable Trace for Specific Class

```bash
nodetool setlogginglevel org.apache.cassandra.db.compaction.CompactionManager TRACE
```

### Disable Logging for Noisy Class

```bash
nodetool setlogginglevel org.apache.cassandra.transport.messages OFF
```

### Reset to Default (INFO)

```bash
nodetool setlogginglevel org.apache.cassandra.db.compaction INFO
```

### Reset All Loggers to Initial Configuration

```bash
# No arguments resets all loggers
nodetool setlogginglevel
```

### Reset Specific Logger

```bash
# Omit level to reset a specific logger
nodetool setlogginglevel org.apache.cassandra.db.compaction
```

### Using Component Shortcuts

```bash
# Enable DEBUG for compaction using component shortcut
nodetool setlogginglevel compaction DEBUG

# Enable DEBUG for repair
nodetool setlogginglevel repair DEBUG

# Enable DEBUG for streaming
nodetool setlogginglevel streaming DEBUG
```

---

## Common Debug Targets

### Compaction Issues

```bash
nodetool setlogginglevel org.apache.cassandra.db.compaction DEBUG
```

### Repair Problems

```bash
nodetool setlogginglevel org.apache.cassandra.repair DEBUG
nodetool setlogginglevel org.apache.cassandra.streaming DEBUG
```

### Gossip/Cluster Issues

```bash
nodetool setlogginglevel org.apache.cassandra.gms DEBUG
nodetool setlogginglevel org.apache.cassandra.net DEBUG
```

### Read/Write Path

```bash
nodetool setlogginglevel org.apache.cassandra.db DEBUG
nodetool setlogginglevel org.apache.cassandra.service DEBUG
```

### Authentication Issues

```bash
nodetool setlogginglevel org.apache.cassandra.auth DEBUG
```

### CQL Protocol

```bash
nodetool setlogginglevel org.apache.cassandra.transport DEBUG
```

### Hinted Handoff

```bash
nodetool setlogginglevel org.apache.cassandra.hints DEBUG
```

---

## Viewing Changed Levels

```bash
nodetool getlogginglevels
```

Shows all loggers with non-default levels.

---

## Workflow: Debug an Issue

```bash
# 1. Enable debug logging for relevant component
nodetool setlogginglevel org.apache.cassandra.db.compaction DEBUG

# 2. Reproduce the issue
nodetool compact my_keyspace my_table

# 3. Check logs
tail -f /var/log/cassandra/debug.log

# 4. Reset logging level
nodetool setlogginglevel org.apache.cassandra.db.compaction INFO
```

---

## Log Output Location

Debug/trace logs typically go to:

```
/var/log/cassandra/debug.log
```

Check `logback.xml` for exact configuration.

---

## Important Considerations

!!! warning "Performance Impact"
    - DEBUG and TRACE levels generate significant log volume
    - May impact performance on busy clusters
    - May fill disk quickly
    - Always reset after debugging

### Best Practices

1. **Be specific** - Target specific classes, not broad packages
2. **Time-limited** - Enable only for debugging duration
3. **Monitor disk** - Debug logs grow fast
4. **Reset promptly** - Return to INFO when done

---

## Scripting Example

```bash
#!/bin/bash
# debug_compaction.sh - Enable debug, wait, then reset

DURATION=${1:-60}  # Default 60 seconds

echo "Enabling compaction debug logging for $DURATION seconds..."
nodetool setlogginglevel org.apache.cassandra.db.compaction DEBUG

sleep $DURATION

echo "Resetting to INFO..."
nodetool setlogginglevel org.apache.cassandra.db.compaction INFO

echo "Done. Check /var/log/cassandra/debug.log"
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [getlogginglevels](getlogginglevels.md) | View current logging levels |
| [info](info.md) | Node information |
| [compactionstats](compactionstats.md) | Alternative to debug logs |