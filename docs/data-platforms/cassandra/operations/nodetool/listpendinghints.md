---
title: "nodetool listpendinghints"
description: "Display pending hints for nodes in Cassandra using nodetool listpendinghints."
meta:
  - name: keywords
    content: "nodetool listpendinghints, pending hints, hinted handoff, Cassandra"
---

# nodetool listpendinghints

Lists the pending hints for each node in the cluster.

---

## Synopsis

```bash
nodetool [connection_options] listpendinghints
```

## Description

`nodetool listpendinghints` displays information about hints that are waiting to be delivered to their target nodes. Hints are stored when a write cannot reach all replica nodes, and are delivered when those nodes become available again.

This command helps monitor hint backlog and identify nodes that may have been unavailable.

---

## Examples

### Basic Usage

```bash
nodetool listpendinghints
```

---

## Output

### Sample Output

```
Host ID                               Hints
12345678-1234-1234-1234-123456789abc  1523
87654321-4321-4321-4321-cba987654321  42
abcdef12-3456-7890-abcd-ef1234567890  0
```

### Output Fields

| Field | Description |
|-------|-------------|
| Host ID | UUID of the target node |
| Hints | Number of pending hints for that node |

---

## Use Cases

### Monitor Hint Backlog

```bash
# Check pending hints
nodetool listpendinghints

# High numbers indicate recent node unavailability
```

### After Node Recovery

Verify hints are being delivered:

```bash
# Check hints before and after
nodetool listpendinghints

# Wait and check again
sleep 60
nodetool listpendinghints

# Counts should decrease as hints are delivered
```

### Troubleshoot Consistency

When investigating data inconsistencies:

```bash
# Large hint counts for a node suggest recent outage
nodetool listpendinghints

# Consider running repair if hints are old
```

---

## Monitoring Script

```bash
#!/bin/bash
# monitor_pending_hints.sh

THRESHOLD=10000

echo "=== Pending Hints Check ==="

total_hints=0
nodetool listpendinghints | tail -n +2 | while read host_id hints; do
    total_hints=$((total_hints + hints))

    if [ "$hints" -gt "$THRESHOLD" ]; then
        echo "WARNING: $host_id has $hints pending hints"
    elif [ "$hints" -gt 0 ]; then
        echo "INFO: $host_id has $hints pending hints"
    fi
done

echo ""
echo "Total pending hints: $total_hints"
```

---

## Cluster-Wide Check

```bash
#!/bin/bash
# cluster_pending_hints.sh

echo "=== Cluster Pending Hints ==="# Get list of node IPs from local nodetool status


nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo ""
    echo "=== Hints on $node ==="
    ssh "$node" "nodetool listpendinghints 2>/dev/null | tail -n +2 | \"
        awk '{sum+=$2} END {print "Total:", sum}'
done
```

---

## Understanding Hints

### Hint Lifecycle

```
1. Write received by coordinator
2. Replica unreachable → hint stored locally
3. Replica recovers → hint delivered
4. Successful delivery → hint deleted
```

### Hint Window

Hints are only stored for nodes that have been down less than the hint window:

```yaml
# cassandra.yaml
max_hint_window_in_ms: 10800000  # 3 hours default
```

---

## Troubleshooting

### Large Hint Backlog

```bash
# Check which nodes have pending hints
nodetool listpendinghints

# Check if target nodes are UP
nodetool status

# If target is UP but hints not delivering, check:
nodetool tpstats | grep -i hint
```

### Hints Not Decreasing

```bash
# Check hint delivery status
nodetool statushandoff

# Ensure delivery is not paused
nodetool resumehandoff

# Check for delivery errors
grep -i "hint" /var/log/cassandra/system.log | tail -20
```

### Hints Growing Despite Healthy Cluster

```bash
# May indicate network issues
# Check connectivity to target nodes
nodetool status

# Check for intermittent failures
nodetool failuredetector
```

---

## Hints and Consistency

| Scenario | Hints | Consistency |
|----------|-------|-------------|
| Hints delivered | Decreasing | Being restored |
| Hints stale (expired) | May show 0 | Requires repair |
| Hints accumulating | Increasing | Target node down |

!!! warning "Hint Expiration"
    Hints older than `max_hint_window_in_ms` are dropped. If a node was down longer than this window, use `nodetool repair` to restore consistency.

---

## Best Practices

!!! tip "Hint Monitoring Guidelines"

    1. **Regular checks** - Include in monitoring
    2. **Alert on high counts** - May indicate failing nodes
    3. **Watch trends** - Increasing hints = problem
    4. **Repair after long outages** - Don't rely on hints alone
    5. **Size hint storage** - Ensure adequate disk for hints

!!! info "Normal Behavior"

    - Small hint counts are normal during temporary outages
    - Hints should decrease as target nodes recover
    - Zero hints is ideal but brief non-zero is okay

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [truncatehints](truncatehints.md) | Remove all pending hints |
| [statushandoff](statushandoff.md) | Check handoff status |
| [pausehandoff](pausehandoff.md) | Pause hint delivery |
| [resumehandoff](resumehandoff.md) | Resume hint delivery |
| [repair](repair.md) | Restore consistency |
