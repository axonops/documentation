---
title: "nodetool gettimeout"
description: "Display timeout settings for various Cassandra operations using nodetool gettimeout."
meta:
  - name: keywords
    content: "nodetool gettimeout, timeout settings, Cassandra timeouts, operation timeout"
---

# nodetool gettimeout

Displays the timeout value for the specified type.

---

## Synopsis

```bash
nodetool [connection_options] gettimeout <timeout_type>
```

## Description

`nodetool gettimeout` retrieves the current timeout value for a specific operation type. Timeouts control how long Cassandra waits for various operations before failing with a timeout exception.

Understanding current timeout settings is essential for:

- **Troubleshooting timeout errors** - Verify current settings
- **Performance tuning** - Assess if timeouts match workload requirements
- **Configuration validation** - Confirm runtime matches expected values

---

## Arguments

| Argument | Description |
|----------|-------------|
| `timeout_type` | The type of timeout to query |

### Timeout Types

| Type | Description |
|------|-------------|
| `read` | Timeout for read operations |
| `write` | Timeout for write operations |
| `range` | Timeout for range read operations |
| `counterwrite` | Timeout for counter write operations |
| `cascontention` | Timeout for CAS (Compare-and-Set) contention retries |
| `truncate` | Timeout for truncate operations |
| `misc` | Timeout for miscellaneous operations |
| `internodeconnect` | Timeout for internode connections |
| `internodeuser` | Timeout for internode user operations |
| `internodestreaminguser` | Timeout for internode streaming operations |

---

## Examples

### Get Read Timeout

```bash
nodetool gettimeout read
```

Output:
```
Current timeout for type read: 5000 ms
```

### Get Write Timeout

```bash
nodetool gettimeout write
```

### Get All Timeouts

```bash
# Check all timeout types
for type in read write range counterwrite cascontention truncate misc; do
    echo -n "$type: "
    nodetool gettimeout $type
done
```

---

## Default Timeout Values

| Timeout Type | Default | Description |
|--------------|---------|-------------|
| `read` | 5000 ms | Single partition reads |
| `write` | 2000 ms | Writes and mutations |
| `range` | 10000 ms | Range scans and token range reads |
| `counterwrite` | 5000 ms | Counter mutations |
| `cascontention` | 1000 ms | LWT contention retries |
| `truncate` | 60000 ms | Table truncation |

---

## Use Cases

### Troubleshoot Timeout Errors

When seeing `ReadTimeoutException` or `WriteTimeoutException`:

```bash
# Check current read timeout
nodetool gettimeout read

# If timeouts are appropriate, issue is likely performance-related
# If timeouts are too low, consider increasing

# Check write timeout
nodetool gettimeout write
```

### Verify Configuration

Confirm runtime matches cassandra.yaml:

```bash
#!/bin/bash
# verify_timeouts.sh

echo "=== Timeout Configuration Verification ==="
echo ""

echo "Runtime values:"
for type in read write range counterwrite; do
    nodetool gettimeout $type
done

echo ""
echo "cassandra.yaml values:"
grep -E "read_request_timeout|write_request_timeout|range_request_timeout|counter_write_request_timeout" /etc/cassandra/cassandra.yaml
```

### Performance Analysis

Understand timeout settings for capacity planning:

```bash
#!/bin/bash
# timeout_analysis.sh

echo "=== Timeout Analysis ==="
echo ""

read_timeout=$(nodetool gettimeout read 2>/dev/null | grep -oE "[0-9]+" | head -1)
write_timeout=$(nodetool gettimeout write 2>/dev/null | grep -oE "[0-9]+" | head -1)
range_timeout=$(nodetool gettimeout range 2>/dev/null | grep -oE "[0-9]+" | head -1)

echo "Current Timeouts:"
echo "  Read:  ${read_timeout}ms"
echo "  Write: ${write_timeout}ms"
echo "  Range: ${range_timeout}ms"

echo ""
echo "Recommendations:"
if [ "$read_timeout" -lt 5000 ]; then
    echo "  - Read timeout below default (5000ms)"
fi
if [ "$write_timeout" -lt 2000 ]; then
    echo "  - Write timeout below default (2000ms)"
fi
```

---

## Cluster-Wide Check

### Compare Across Nodes

```bash
#!/bin/bash
# check_timeouts_cluster.sh

TIMEOUT_TYPE="${1:-read}"

echo "=== Cluster Timeout Check: $TIMEOUT_TYPE ==="
echo ""

# Get list of node IPs from local nodetool status
nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo -n "$node: "
    ssh "$node" "nodetool gettimeout $TIMEOUT_TYPE" 2>/dev/null || echo "FAILED"
done
```

### Verify Consistency

```bash
#!/bin/bash
# verify_timeout_consistency.sh

echo "=== Timeout Consistency Check ==="
echo ""

# Get list of node IPs from local nodetool status
nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for type in read write range counterwrite; do
    echo "Checking $type timeout:"
    values=""
    for node in $nodes; do
        value=$(ssh "$node" "nodetool gettimeout $type" 2>/dev/null | grep -oE "[0-9]+" | head -1)
        echo "  $node: ${value}ms"
        values="$values $value"
    done

    unique=$(echo $values | tr ' ' '\n' | sort -u | grep -v "^$" | wc -l)
    if [ "$unique" -gt 1 ]; then
        echo "  WARNING: Inconsistent values across cluster!"
    else
        echo "  OK: Consistent across cluster"
    fi
    echo ""
done
```

---

## Monitoring Integration

### Prometheus Export

```bash
#!/bin/bash
# Export timeouts as metrics

for type in read write range counterwrite cascontention; do
    value=$(nodetool gettimeout $type 2>/dev/null | grep -oE "[0-9]+" | head -1)
    if [ -n "$value" ]; then
        echo "cassandra_timeout_${type}_ms $value"
    fi
done
```

### JSON Output

```bash
#!/bin/bash
# Output timeouts as JSON

echo "{"
echo "  \"timestamp\": \"$(date -Iseconds)\","
echo "  \"timeouts\": {"

first=true
for type in read write range counterwrite cascontention truncate; do
    value=$(nodetool gettimeout $type 2>/dev/null | grep -oE "[0-9]+" | head -1)
    if [ -n "$value" ]; then
        if [ "$first" = true ]; then
            first=false
        else
            echo ","
        fi
        echo -n "    \"$type\": $value"
    fi
done

echo ""
echo "  }"
echo "}"
```

---

## Troubleshooting

### Command Fails

```bash
# Check JMX connectivity
nodetool info

# Verify timeout type is valid
nodetool gettimeout read  # Known valid type
```

### Invalid Timeout Type

```bash
# If you see "unknown timeout type" error
# Use one of: read, write, range, counterwrite, cascontention, truncate, misc
```

### Unexpected Value

```bash
# If value differs from cassandra.yaml
# Runtime may have been changed with settimeout
# Or JVM parameters may override

# Check for JVM overrides
ps aux | grep cassandra | grep timeout
```

---

## Best Practices

!!! tip "Timeout Management"

    1. **Document current values** - Record timeouts as part of configuration management
    2. **Cluster consistency** - Ensure all nodes have the same timeouts
    3. **Monitor timeout errors** - Correlate errors with timeout settings
    4. **Adjust carefully** - Increasing timeouts masks performance issues
    5. **Consider workload** - Range queries often need longer timeouts

!!! info "Timeout Tuning Guidance"

    - **Read timeout**: Increase for slow storage or complex queries
    - **Write timeout**: Rarely needs increasing; investigate if writes timeout
    - **Range timeout**: May need increasing for large scans
    - **Counter timeout**: Important for counter-heavy workloads
    - **CAS contention**: Affects LWT operations under contention

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [settimeout](settimeout.md) | Modify timeout values |
| [info](info.md) | General node information |
| [proxyhistograms](proxyhistograms.md) | View latency distributions |
