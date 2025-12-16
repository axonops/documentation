---
title: "nodetool sethintedhandoffthrottlekb"
description: "Set hinted handoff throttle in KB/s using nodetool sethintedhandoffthrottlekb."
meta:
  - name: keywords
    content: "nodetool sethintedhandoffthrottlekb, hint throttle, hinted handoff, Cassandra"
---

# nodetool sethintedhandoffthrottlekb

Sets the hinted handoff throttle rate in KB per second.

---

## Synopsis

```bash
nodetool [connection_options] sethintedhandoffthrottlekb <throttle_in_kb>
```

## Description

`nodetool sethintedhandoffthrottlekb` controls the rate at which hints are delivered to recovered nodes. This throttle prevents hint delivery from overwhelming target nodes or consuming excessive network bandwidth.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `throttle_in_kb` | Maximum hint delivery rate in kilobytes per second |

---

## Examples

### Set Throttle Rate

```bash
# Set to 1024 KB/s (1 MB/s)
nodetool sethintedhandoffthrottlekb 1024
```

### Increase for Faster Delivery

```bash
# Increase to 2048 KB/s for faster hint delivery
nodetool sethintedhandoffthrottlekb 2048
```

### Decrease for Reduced Impact

```bash
# Reduce to 512 KB/s to minimize impact on target nodes
nodetool sethintedhandoffthrottlekb 512
```

---

## When to Use

### Node Recovery Under Load

Reduce throttle when recovering node is busy:

```bash
# Slow down hint delivery
nodetool sethintedhandoffthrottlekb 256

# Monitor target node
ssh <target_node> "nodetool tpstats"
```

### Speed Up Hint Delivery

Increase throttle when hints need to be delivered quickly:

```bash
# Check pending hints
nodetool listpendinghints

# Increase throttle for faster delivery
nodetool sethintedhandoffthrottlekb 4096
```

### Network Bandwidth Management

Adjust based on available network capacity:

```bash
# High-bandwidth network
nodetool sethintedhandoffthrottlekb 4096

# Limited bandwidth
nodetool sethintedhandoffthrottlekb 512
```

---

## Configuration

### Default Value

```yaml
# cassandra.yaml
hinted_handoff_throttle_in_kb: 1024  # Default 1 MB/s
```

### Runtime vs Persistent

| Setting | Persistence |
|---------|-------------|
| `sethintedhandoffthrottlekb` | Until restart |
| `cassandra.yaml` | Permanent |

---

## Impact Assessment

### Higher Throttle

| Effect | Impact |
|--------|--------|
| Hint delivery | Faster |
| Network usage | Higher |
| Target node load | Higher |
| Recovery time | Shorter |

### Lower Throttle

| Effect | Impact |
|--------|--------|
| Hint delivery | Slower |
| Network usage | Lower |
| Target node load | Lower |
| Recovery time | Longer |

---

## Monitoring Hint Delivery

```bash
#!/bin/bash
# monitor_hint_delivery.sh

echo "=== Hint Delivery Monitor ==="

# Initial hint count
initial=$(nodetool listpendinghints | tail -n +2 | awk '{sum+=$2} END {print sum}')
echo "Initial pending hints: $initial"

# Wait and check again
sleep 60

final=$(nodetool listpendinghints | tail -n +2 | awk '{sum+=$2} END {print sum}')
echo "Pending hints after 60s: $final"

delivered=$((initial - final))
echo "Hints delivered: $delivered"
echo "Approximate rate: $((delivered / 60)) hints/second"
```

---

## Cluster-Wide Setting

```bash
#!/bin/bash
# set_hint_throttle_cluster.sh

THROTTLE="$1"

if [ -z "$THROTTLE" ]; then
    echo "Usage: $0 <throttle_kb>"
    exit 1
fi# Get list of node IPs from local nodetool status


nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

echo "Setting hint throttle to ${THROTTLE} KB/s cluster-wide..."
for node in $nodes; do
    echo -n "$node: "
    ssh "$node" "nodetool sethintedhandoffthrottlekb $THROTTLE && echo "OK" || echo "FAILED""
done
```

---

## Troubleshooting

### Hints Delivering Too Slowly

```bash
# Check current pending hints
nodetool listpendinghints

# Increase throttle
nodetool sethintedhandoffthrottlekb 4096

# Monitor delivery rate
watch -n 10 'nodetool listpendinghints'
```

### Target Node Overwhelmed

```bash
# Check target node health
ssh <target_node> "nodetool tpstats"

# Reduce throttle
nodetool sethintedhandoffthrottlekb 256

# Monitor target node recovery
```

---

## Best Practices

!!! tip "Throttle Guidelines"

    1. **Start conservative** - Lower throttle for busy clusters
    2. **Monitor target nodes** - Watch for overload signs
    3. **Adjust dynamically** - Increase during maintenance windows
    4. **Balance speed vs impact** - Faster isn't always better
    5. **Cluster-wide consistency** - Set same value on all nodes

!!! info "Throttle Selection"

    - **256-512 KB/s**: Low-impact, slow recovery
    - **1024 KB/s**: Balanced (default)
    - **2048-4096 KB/s**: Fast recovery, higher impact
    - **Unlimited (0)**: Maximum speed, use cautiously

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [listpendinghints](listpendinghints.md) | View pending hints |
| [statushandoff](statushandoff.md) | Check handoff status |
| [pausehandoff](pausehandoff.md) | Pause hint delivery |
| [resumehandoff](resumehandoff.md) | Resume hint delivery |
| [getmaxhintwindow](getmaxhintwindow.md) | View hint window |
