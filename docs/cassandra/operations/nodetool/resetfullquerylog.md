---
description: "Reset full query log in Cassandra using nodetool resetfullquerylog command."
meta:
  - name: keywords
    content: "nodetool resetfullquerylog, reset FQL, query logging, Cassandra"
---

# nodetool resetfullquerylog

Resets the full query logging path to the configured value.

---

## Synopsis

```bash
nodetool [connection_options] resetfullquerylog
```

## Description

`nodetool resetfullquerylog` resets the full query logging (FQL) path to the default value configured in `cassandra.yaml`. This is useful when FQL was enabled with a custom path via `enablefullquerylog --path` and needs to be restored to the configuration file setting.

!!! info "Path Reset Only"
    This command resets the log path configuration but does not delete existing log files or change the enabled/disabled state of FQL.

---

## Examples

### Basic Usage

```bash
nodetool resetfullquerylog
```

### Reset and Verify

```bash
nodetool resetfullquerylog
nodetool getfullquerylog
```

### On Remote Node

```bash
nodetool -h 192.168.1.100 resetfullquerylog
```

---

## Behavior

When `resetfullquerylog` is executed:

1. FQL path is reset to the `cassandra.yaml` configured value
2. If FQL is enabled, logging continues to the reset path
3. Existing log files at the previous path remain unchanged
4. FQL enabled/disabled state is not affected

### What Changes

| Aspect | Before | After |
|--------|--------|-------|
| Log path | Custom path from `--path` | Path from `cassandra.yaml` |

### What Stays the Same

| Aspect | Status |
|--------|--------|
| FQL enabled/disabled | Unchanged |
| Existing log files | Preserved at old location |
| Other FQL settings | Unchanged |

---

## When to Use

### Restore Default Path

After using a temporary custom path:

```bash
# Previously enabled with custom path
nodetool enablefullquerylog --path /tmp/fql_debug

# Reset to configured path
nodetool resetfullquerylog

# Verify
nodetool getfullquerylog
```

### Configuration Consistency

Align runtime settings with configuration file:

```bash
# Check current runtime path
nodetool getfullquerylog | grep log_dir

# Check configured path
grep "log_dir" /etc/cassandra/cassandra.yaml

# Reset to match config
nodetool resetfullquerylog
```

### After Debugging Session

Return to normal operation after debug session:

```bash
# Debug session used custom path
# Now restore normal path
nodetool resetfullquerylog

# Continue with normal FQL path
nodetool getfullquerylog
```

---

## Workflow: Debug Session with Custom Path

```bash
#!/bin/bash
# fql_debug_session.sh

DEBUG_PATH="/tmp/fql_debug_$(date +%Y%m%d_%H%M%S)"
mkdir -p $DEBUG_PATH

echo "=== FQL Debug Session ==="

# 1. Save current configuration
echo "1. Current FQL configuration:"
nodetool getfullquerylog

# 2. Enable with debug path
echo ""
echo "2. Enabling FQL with debug path: $DEBUG_PATH"
nodetool enablefullquerylog --path $DEBUG_PATH --roll-cycle MINUTELY

# 3. Wait for data collection
echo ""
echo "3. Collecting data... Press Enter when done."
read

# 4. Disable FQL
echo ""
echo "4. Disabling FQL..."
nodetool disablefullquerylog

# 5. Process debug logs
echo ""
echo "5. Debug logs captured at: $DEBUG_PATH"
echo "   Size: $(du -sh $DEBUG_PATH)"
echo "   Entries: $(fqltool dump $DEBUG_PATH 2>/dev/null | wc -l)"

# 6. Reset to default path
echo ""
echo "6. Resetting to default path..."
nodetool resetfullquerylog

# 7. Verify reset
echo ""
echo "7. Configuration after reset:"
nodetool getfullquerylog

echo ""
echo "=== Debug Session Complete ==="
echo "Debug logs remain at: $DEBUG_PATH"
```

---

## Configuration Reference

### cassandra.yaml Setting

```yaml
# cassandra.yaml
full_query_logging_options:
    log_dir: /var/log/cassandra/fql
    # ... other settings
```

### Runtime Override

```bash
# Override configured path at runtime
nodetool enablefullquerylog --path /custom/path

# Reset to cassandra.yaml path
nodetool resetfullquerylog
```

---

## Cluster-Wide Operations

### Reset on All Nodes

```bash
#!/bin/bash
# reset_fql_cluster.sh

echo "Resetting FQL path cluster-wide..."

nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo -n "$node: "
    nodetool -h $node resetfullquerylog 2>/dev/null && echo "reset" || echo "FAILED"
done

echo ""
echo "Verification:"
for node in $nodes; do
    echo "=== $node ==="
    nodetool -h $node getfullquerylog 2>/dev/null | grep "log_dir"
done
```

---

## Troubleshooting

### Reset Has No Effect

```bash
# Check if cassandra.yaml has FQL configuration
grep -A 10 "full_query_logging_options" /etc/cassandra/cassandra.yaml

# If no config, reset has nothing to reset to
# The path may remain unchanged or empty
```

### Path Not Changed After Reset

```bash
# Verify the reset command succeeded
nodetool resetfullquerylog

# Check current configuration
nodetool getfullquerylog

# Check cassandra.yaml for configured path
grep "log_dir" /etc/cassandra/cassandra.yaml

# If cassandra.yaml doesn't have a path configured,
# the runtime path may remain
```

### Logs at Old Path

```bash
# After reset, existing logs remain at old path
# They are not moved or deleted

# Check old path
ls -la /old/custom/path/

# Move or archive if needed
mv /old/custom/path/* /archive/
```

---

## Managing Multiple Paths

### After Reset

```bash
#!/bin/bash
# cleanup_fql_paths.sh

# Get current configured path
current_path=$(nodetool getfullquerylog | grep "log_dir" | awk '{print $2}')

echo "Current FQL path: $current_path"
echo ""

# Find other potential FQL directories
echo "Potential FQL directories on this system:"
find /var/log/cassandra /tmp -type d -name "*fql*" 2>/dev/null

echo ""
echo "Review and clean up old FQL directories as needed."
```

---

## Best Practices

!!! tip "Reset Guidelines"

    1. **Document custom paths** - Track when and why custom paths are used
    2. **Clean up after reset** - Archive or remove logs at old paths
    3. **Verify configuration** - Check `cassandra.yaml` has valid FQL config
    4. **Cluster consistency** - Reset on all nodes if custom path was cluster-wide
    5. **Check disk space** - Ensure default path has sufficient space

!!! info "When to Reset"

    - After temporary debugging sessions
    - To align runtime with configuration
    - After maintenance operations that used custom paths
    - To restore normal operational logging

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [enablefullquerylog](enablefullquerylog.md) | Enable FQL (with optional custom path) |
| [disablefullquerylog](disablefullquerylog.md) | Disable FQL |
| [getfullquerylog](getfullquerylog.md) | View FQL configuration |
