---
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
nodetool [connection_options] setlogginglevel <class> <level>
```

## Description

`nodetool setlogginglevel` dynamically changes the logging level for a specific Java class or package without restarting Cassandra. This is useful for debugging issues in production.

!!! warning "Non-Persistent Setting"
    This setting is applied at runtime only and does not persist across node restarts. After a restart, the logging levels revert to the configuration in `logback.xml`.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `class` | Fully qualified class name or package (empty for root logger) |
| `level` | Log level: TRACE, DEBUG, INFO, WARN, ERROR, OFF |

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

### Reset Root Logger

```bash
nodetool setlogginglevel "" INFO
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
