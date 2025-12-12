# nodetool settimeout

Sets the timeout value for the specified type.

---

## Synopsis

```bash
nodetool [connection_options] settimeout <timeout_type> <timeout_value_in_ms>
```

## Description

`nodetool settimeout` modifies the timeout value for a specific operation type at runtime. This allows adjusting timeouts without restarting the node, useful for:

- **Emergency response** - Temporarily increase timeouts during performance issues
- **Workload accommodation** - Adjust for queries with known longer execution times
- **Testing** - Experiment with different timeout values

!!! warning "Runtime Change"
    Timeout changes take effect immediately but don't persist across restarts. For permanent changes, update `cassandra.yaml`.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `timeout_type` | The type of timeout to modify |
| `timeout_value_in_ms` | New timeout value in milliseconds |

### Timeout Types

| Type | Description | Default |
|------|-------------|---------|
| `read` | Read operations | 5000 ms |
| `write` | Write operations | 2000 ms |
| `range` | Range read operations | 10000 ms |
| `counterwrite` | Counter write operations | 5000 ms |
| `cascontention` | CAS contention retries | 1000 ms |
| `truncate` | Truncate operations | 60000 ms |
| `misc` | Miscellaneous operations | 10000 ms |
| `internodeconnect` | Internode connections | 10000 ms |

---

## Examples

### Increase Read Timeout

```bash
nodetool settimeout read 10000
```

### Increase Range Timeout

```bash
# For large range scans
nodetool settimeout range 30000
```

### Decrease Write Timeout

```bash
nodetool settimeout write 1000
```

### On Remote Node

```bash
nodetool -h 192.168.1.100 settimeout read 10000
```

### Verify Change

```bash
# Set timeout
nodetool settimeout read 10000

# Verify
nodetool gettimeout read
```

---

## When to Use

### During Performance Degradation

Temporarily increase timeouts while investigating issues:

```bash
# Increase read timeout during slow disk performance
nodetool settimeout read 15000

# Increase range timeout for large scans
nodetool settimeout range 60000

# After issue resolved, restore defaults
nodetool settimeout read 5000
nodetool settimeout range 10000
```

### For Known Slow Operations

Accommodate queries with predictably longer execution:

```bash
# Large token range scans
nodetool settimeout range 30000

# Complex read operations
nodetool settimeout read 10000
```

### Troubleshooting Timeout Errors

When timeout errors occur but operations should succeed:

```bash
# Check current timeout
nodetool gettimeout read

# Increase temporarily
nodetool settimeout read 20000

# Test operation
cqlsh -e "SELECT * FROM large_table LIMIT 1000;"

# Monitor and adjust
```

### Counter-Heavy Workloads

Adjust counter write timeout for busy counter tables:

```bash
nodetool settimeout counterwrite 10000
```

---

## Impact Assessment

### Increasing Timeouts

| Effect | Impact |
|--------|--------|
| Fewer timeout errors | Operations wait longer |
| Resource usage | Connections held longer |
| Error detection | Delayed failure detection |
| Client experience | Longer wait for failures |

### Decreasing Timeouts

| Effect | Impact |
|--------|--------|
| More timeout errors | Operations fail faster |
| Resource release | Connections freed sooner |
| Error detection | Faster failure detection |
| Client experience | Quicker error responses |

!!! danger "Timeout Considerations"
    Increasing timeouts masks underlying performance issues. Use temporary increases for emergency response, but investigate and fix root causes.

---

## Workflow: Emergency Timeout Adjustment

```bash
#!/bin/bash
# emergency_timeout_adjust.sh

echo "=== Emergency Timeout Adjustment ==="
echo ""

# 1. Record current values
echo "1. Current timeout values:"
for type in read write range; do
    nodetool gettimeout $type
done

# 2. Save to restore later
echo ""
echo "2. Saving current values..."
read_timeout=$(nodetool gettimeout read 2>/dev/null | grep -oE "[0-9]+" | head -1)
write_timeout=$(nodetool gettimeout write 2>/dev/null | grep -oE "[0-9]+" | head -1)
range_timeout=$(nodetool gettimeout range 2>/dev/null | grep -oE "[0-9]+" | head -1)

echo "   read=$read_timeout write=$write_timeout range=$range_timeout"

# 3. Apply emergency values (2x default)
echo ""
echo "3. Applying emergency timeout values..."
nodetool settimeout read 10000
nodetool settimeout write 4000
nodetool settimeout range 20000

echo ""
echo "4. New values:"
for type in read write range; do
    nodetool gettimeout $type
done

# 4. Create restore script
echo ""
echo "5. Created restore script: /tmp/restore_timeouts.sh"
cat > /tmp/restore_timeouts.sh << EOF
#!/bin/bash
nodetool settimeout read $read_timeout
nodetool settimeout write $write_timeout
nodetool settimeout range $range_timeout
echo "Timeouts restored to original values."
EOF
chmod +x /tmp/restore_timeouts.sh

echo ""
echo "=== Emergency adjustment complete ==="
echo "Run '/tmp/restore_timeouts.sh' to restore original values."
```

---

## Cluster-Wide Changes

### Set on All Nodes

```bash
#!/bin/bash
# set_timeout_cluster.sh

TIMEOUT_TYPE="$1"
TIMEOUT_VALUE="$2"

if [ -z "$TIMEOUT_TYPE" ] || [ -z "$TIMEOUT_VALUE" ]; then
    echo "Usage: $0 <timeout_type> <timeout_value_ms>"
    exit 1
fi

echo "Setting $TIMEOUT_TYPE timeout to ${TIMEOUT_VALUE}ms cluster-wide..."

nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo -n "$node: "
    nodetool -h $node settimeout $TIMEOUT_TYPE $TIMEOUT_VALUE && echo "OK" || echo "FAILED"
done

echo ""
echo "Verification:"
for node in $nodes; do
    echo -n "$node: "
    nodetool -h $node gettimeout $TIMEOUT_TYPE
done
```

### Batch Set Multiple Timeouts

```bash
#!/bin/bash
# set_all_timeouts.sh

READ_TIMEOUT="${1:-5000}"
WRITE_TIMEOUT="${2:-2000}"
RANGE_TIMEOUT="${3:-10000}"

echo "Setting timeouts: read=$READ_TIMEOUT write=$WRITE_TIMEOUT range=$RANGE_TIMEOUT"

nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo "Configuring $node..."
    nodetool -h $node settimeout read $READ_TIMEOUT
    nodetool -h $node settimeout write $WRITE_TIMEOUT
    nodetool -h $node settimeout range $RANGE_TIMEOUT
done

echo "Complete."
```

---

## Configuration Persistence

### Runtime vs Permanent

| Setting Source | Persistence | Scope |
|----------------|-------------|-------|
| `settimeout` | Until restart | This node only |
| `cassandra.yaml` | Permanent | All restarts |

### Making Changes Permanent

```yaml
# cassandra.yaml
read_request_timeout_in_ms: 10000
write_request_timeout_in_ms: 4000
range_request_timeout_in_ms: 20000
counter_write_request_timeout_in_ms: 10000
cas_contention_timeout_in_ms: 2000
truncate_request_timeout_in_ms: 60000
```

---

## Troubleshooting

### Timeout Still Occurring

```bash
# Verify the change took effect
nodetool gettimeout read

# May need to increase further
nodetool settimeout read 30000

# Or investigate underlying performance issue
nodetool proxyhistograms
```

### Command Fails

```bash
# Check JMX connectivity
nodetool info

# Verify valid timeout type
# Valid types: read, write, range, counterwrite, cascontention, truncate, misc
```

### Client Still Times Out

```bash
# Server-side timeouts affect Cassandra's internal timeouts
# Client driver timeouts are separate

# Ensure client timeout >= server timeout
# Check client driver configuration
```

---

## Best Practices

!!! tip "Timeout Setting Guidelines"

    1. **Temporary only** - Runtime changes should be temporary
    2. **Document changes** - Log when and why timeouts changed
    3. **Restore after fix** - Return to defaults once issues resolved
    4. **Investigate root cause** - Don't use increased timeouts as permanent fix
    5. **Cluster consistency** - Set same values on all nodes
    6. **Monitor effect** - Track if timeout errors decrease

!!! warning "Timeout Anti-Patterns"

    - **Don't set extremely high values** - Masks problems, wastes resources
    - **Don't leave temporary increases permanent** - Update cassandra.yaml if needed
    - **Don't ignore timeout errors** - They indicate performance issues
    - **Don't set lower than client timeouts** - Client times out first

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [gettimeout](gettimeout.md) | View current timeout values |
| [proxyhistograms](proxyhistograms.md) | View latency distributions |
| [info](info.md) | General node information |
