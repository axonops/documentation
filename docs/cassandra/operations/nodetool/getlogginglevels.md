# nodetool getlogginglevels

Displays the current logging levels for all loggers.

---

## Synopsis

```bash
nodetool [connection_options] getlogginglevels
```

## Description

`nodetool getlogginglevels` shows all loggers that have been explicitly configured with non-default logging levels. This includes both levels set at runtime via `setlogginglevel` and levels configured in `logback.xml`.

---

## Output Format

```
Logger Name                                  Log Level
ROOT                                         INFO
org.apache.cassandra.db.compaction           DEBUG
org.apache.cassandra.gms                     DEBUG
```

---

## Examples

### View Current Levels

```bash
nodetool getlogginglevels
```

### Filter for Specific Package

```bash
nodetool getlogginglevels | grep compaction
```

### Check if Debug is Enabled

```bash
nodetool getlogginglevels | grep DEBUG
```

---

## Use Cases

### Verify Debug Settings

After enabling debug logging:

```bash
# Enable debug
nodetool setlogginglevel org.apache.cassandra.repair DEBUG

# Verify it's set
nodetool getlogginglevels | grep repair
```

### Audit Logging Configuration

```bash
# See all non-default loggers
nodetool getlogginglevels
```

### Before Node Restart

```bash
# Document current debug settings (they don't persist)
nodetool getlogginglevels > /tmp/logging_levels_backup.txt
```

---

## Understanding Output

### ROOT Logger

```
ROOT                                         INFO
```

The root logger affects all classes not explicitly configured.

### Package Loggers

```
org.apache.cassandra.db                      DEBUG
```

All classes under this package inherit this level.

### Class Loggers

```
org.apache.cassandra.db.compaction.CompactionManager    TRACE
```

Specific class with its own level.

---

## Common Logger Packages

| Package | Purpose |
|---------|---------|
| `org.apache.cassandra.db` | Database operations |
| `org.apache.cassandra.db.compaction` | Compaction |
| `org.apache.cassandra.gms` | Gossip |
| `org.apache.cassandra.net` | Networking |
| `org.apache.cassandra.repair` | Repair |
| `org.apache.cassandra.streaming` | Streaming |
| `org.apache.cassandra.hints` | Hinted handoff |
| `org.apache.cassandra.auth` | Authentication |
| `org.apache.cassandra.transport` | CQL protocol |

---

## Workflow: Troubleshooting Session

```bash
# 1. Check current state
nodetool getlogginglevels

# 2. Enable needed debug levels
nodetool setlogginglevel org.apache.cassandra.repair DEBUG
nodetool setlogginglevel org.apache.cassandra.streaming DEBUG

# 3. Verify enabled
nodetool getlogginglevels

# 4. Debug the issue...

# 5. Reset all debug levels
nodetool setlogginglevel org.apache.cassandra.repair INFO
nodetool setlogginglevel org.apache.cassandra.streaming INFO

# 6. Confirm reset
nodetool getlogginglevels
```

---

## Scripting Example

```bash
#!/bin/bash
# check_debug_logging.sh - Alert if debug logging is enabled

DEBUG_COUNT=$(nodetool getlogginglevels | grep -c "DEBUG\|TRACE")

if [ "$DEBUG_COUNT" -gt 0 ]; then
    echo "WARNING: $DEBUG_COUNT logger(s) at DEBUG/TRACE level"
    nodetool getlogginglevels | grep "DEBUG\|TRACE"
else
    echo "OK: No debug logging enabled"
fi
```

### Reset All to Defaults

```bash
#!/bin/bash
# reset_logging.sh - Reset all loggers to INFO

for logger in $(nodetool getlogginglevels | grep -v "^Logger\|^ROOT" | awk '{print $1}'); do
    echo "Resetting $logger to INFO"
    nodetool setlogginglevel "$logger" INFO
done
```

---

## Persistence Note

!!! info "Runtime Configuration"
    Levels shown by `getlogginglevels` include:

    - Runtime changes via `setlogginglevel` (not persisted)
    - Static configuration from `logback.xml` (persisted)

    After restart, only `logback.xml` settings remain.

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [setlogginglevel](setlogginglevel.md) | Change logging levels |
| [info](info.md) | General node information |
