---
description: "Resume hinted handoff delivery in Cassandra using nodetool resumehandoff command."
meta:
  - name: keywords
    content: "nodetool resumehandoff, resume hints, hinted handoff, Cassandra"
---

# nodetool resumehandoff

Resumes the delivery of hints that was previously paused.

---

## Synopsis

```bash
nodetool [connection_options] resumehandoff
```

## Description

`nodetool resumehandoff` resumes the delivery of stored hints to their target nodes after it was paused with `pausehandoff`. When resumed, the node begins replaying accumulated hints to recovered replicas, restoring data consistency.

This command only affects hint delivery—it does not change whether new hints are being stored (controlled by `enablehandoff`/`disablehandoff`).

!!! info "Resume After Pause"
    Use this command after `pausehandoff` to restore normal hint delivery behavior. If hints were disabled with `disablehandoff`, use `enablehandoff` instead.

---

## Behavior

When hint delivery is resumed:

1. Hint delivery threads become active
2. Accumulated hints begin replaying to target nodes
3. Recovered replicas receive their missing writes
4. Consistency is progressively restored

### Delivery Process

```
Resume Hint Delivery:

1. resumehandoff command received
2. Hint delivery threads activated
3. For each target node:
   - Check if node is UP via gossip
   - Begin streaming hints to node
   - Mark delivered hints for deletion
4. Consistency restored without repair
```

---

## Examples

### Basic Usage

```bash
nodetool resumehandoff
```

### Resume and Monitor

```bash
nodetool resumehandoff

# Watch hint delivery progress
watch -n 2 'nodetool tpstats | grep -i hint'
```

### On Remote Node

```bash
nodetool -h 192.168.1.100 resumehandoff
```

---

## When to Use

### After Temporary Pause

Resume normal operation after a maintenance pause:

```bash
# Maintenance complete, resume delivery
nodetool resumehandoff

# Verify delivery is active
nodetool tpstats | grep -i hint
```

### After Node Stabilization

When a recovering node is ready to receive hints:

```bash
# Node has stabilized after recovery
nodetool resumehandoff

# Monitor hint delivery
nodetool listpendinghints
```

### After Troubleshooting

When hint-related investigation is complete:

```bash
# Issue resolved, resume delivery
nodetool resumehandoff

# Check for pending hints
nodetool listpendinghints
```

### During Maintenance Window

Resume hint delivery during off-peak hours:

```bash
# Off-peak hours, safe to resume
nodetool resumehandoff

# Monitor progress until hints are delivered
watch 'nodetool listpendinghints'
```

---

## Impact Assessment

### Immediate Effects

| Aspect | Impact |
|--------|--------|
| Hint delivery threads | Activate immediately |
| Network traffic | Increases (hint streaming) |
| Target node load | Increases (processing hints) |
| Coordinator disk | Begins freeing (delivered hints removed) |

### Short-term Effects

| Aspect | Impact |
|--------|--------|
| Pending hint count | Decreases progressively |
| Data consistency | Improves as hints delivered |
| Hints table size | Shrinks as hints are delivered |
| Read performance | May improve on target nodes |

!!! info "Gradual Delivery"
    Hints are delivered gradually based on `hinted_handoff_throttle_in_kb` to prevent overwhelming target nodes.

---

## Monitoring After Resume

### Track Hint Delivery

```bash
# Watch hint delivery progress
watch -n 5 'nodetool listpendinghints'
```

### Monitor Thread Activity

```bash
# Check hint delivery threads
nodetool tpstats | grep -i hint
```

Example output when delivering:
```
Pool Name                         Active   Pending      Completed   Blocked  All time blocked
HintedHandoff                          2         0           1523         0                 0
```

### Track Hints Table Size

```bash
# Monitor hints table shrinking
watch -n 30 'nodetool tablestats system.hints | grep "Space used"'
```

---

## Workflow: Complete Pause/Resume Cycle

```bash
#!/bin/bash
# hint_pause_resume_cycle.sh

echo "=== Hint Delivery Pause/Resume Cycle ==="

# 1. Initial status
echo "1. Initial Status:"
echo "Pending hints:"
nodetool listpendinghints
echo ""
echo "Hint threads:"
nodetool tpstats | grep -i hint

# 2. Pause delivery
echo ""
echo "2. Pausing hint delivery..."
nodetool pausehandoff

# 3. Perform maintenance or wait
echo ""
echo "3. Hint delivery paused. Perform maintenance or press Enter to resume."
read -p "Press Enter to continue..."

# 4. Resume delivery
echo ""
echo "4. Resuming hint delivery..."
nodetool resumehandoff

# 5. Monitor delivery progress
echo ""
echo "5. Monitoring delivery (Ctrl+C to exit):"
while true; do
    pending=$(nodetool listpendinghints 2>/dev/null | tail -n +2 | awk '{sum+=$2} END {print sum+0}')
    echo "$(date '+%H:%M:%S') - Pending hints: $pending"

    if [ "$pending" -eq 0 ]; then
        echo "All hints delivered!"
        break
    fi
    sleep 5
done

echo ""
echo "=== Cycle Complete ==="
```

---

## Throttling Hint Delivery

### Default Throttling

Hint delivery is throttled by default to prevent overwhelming target nodes:

```yaml
# cassandra.yaml
hinted_handoff_throttle_in_kb: 1024  # KB per second
max_hints_delivery_threads: 2
```

### Adjust During Delivery

```bash
# If delivery is too slow and nodes can handle more
nodetool sethintedhandoffthrottlekb 2048

# If target nodes are struggling
nodetool sethintedhandoffthrottlekb 512
```

### Monitor Delivery Rate

```bash
#!/bin/bash
# Monitor hint delivery rate

prev_completed=0
while true; do
    completed=$(nodetool tpstats 2>/dev/null | grep "HintedHandoff" | awk '{print $4}')
    if [ -n "$prev_completed" ] && [ "$prev_completed" -gt 0 ]; then
        rate=$((completed - prev_completed))
        echo "$(date '+%H:%M:%S') - Hints delivered in last interval: $rate"
    fi
    prev_completed=$completed
    sleep 10
done
```

---

## Cluster-Wide Operations

### Resume on All Nodes

```bash
#!/bin/bash
# resume_handoff_cluster.sh

echo "Resuming hint delivery cluster-wide..."

nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo -n "$node: "
    nodetool -h $node resumehandoff 2>/dev/null && echo "resumed" || echo "FAILED"
done

echo ""
echo "Verification (hint thread activity):"
for node in $nodes; do
    echo "=== $node ==="
    nodetool -h $node tpstats 2>/dev/null | grep -i hint
done
```

### Monitor Cluster-Wide Delivery

```bash
#!/bin/bash
# monitor_cluster_hint_delivery.sh

echo "=== Cluster Hint Delivery Status ==="

nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

total_pending=0
for node in $nodes; do
    pending=$(nodetool -h $node listpendinghints 2>/dev/null | tail -n +2 | awk '{sum+=$2} END {print sum+0}')
    echo "$node: $pending pending hints"
    total_pending=$((total_pending + pending))
done

echo ""
echo "Total cluster pending hints: $total_pending"
```

---

## Troubleshooting

### Hints Not Being Delivered After Resume

```bash
# Check if target nodes are UP
nodetool status

# Check hint thread activity
nodetool tpstats | grep -i hint

# Check for errors in logs
grep -i "hint" /var/log/cassandra/system.log | tail -20
```

### Slow Hint Delivery

```bash
# Check current throttle setting
nodetool gethintedhandoffthrottlekb

# Increase if nodes can handle more
nodetool sethintedhandoffthrottlekb 2048

# Check hint delivery threads
nodetool tpstats | grep -i hint
```

### Hint Delivery Errors

```bash
# Check logs for hint delivery failures
grep -i "hint" /var/log/cassandra/system.log | grep -i "error\|fail" | tail -20

# Check target node connectivity
nodetool ring | head -20

# Verify target node is responsive
nodetool -h <target_node> info
```

### Hints Expired During Pause

If hints expired while delivery was paused:

```bash
# Check pending hints (may show 0 if expired)
nodetool listpendinghints

# Run repair to restore consistency
nodetool repair -pr
```

---

## Recovery After Extended Pause

If hints were paused for an extended period:

```bash
#!/bin/bash
# recovery_after_extended_pause.sh

echo "=== Recovery After Extended Hint Pause ==="

# 1. Resume hint delivery
echo "1. Resuming hint delivery..."
nodetool resumehandoff

# 2. Check for pending hints
echo ""
echo "2. Pending hints:"
nodetool listpendinghints

pending=$(nodetool listpendinghints 2>/dev/null | tail -n +2 | awk '{sum+=$2} END {print sum+0}')

if [ "$pending" -eq 0 ]; then
    echo ""
    echo "WARNING: No pending hints found."
    echo "If hints were paused longer than the hint window, they may have expired."
    echo ""
    echo "3. Running repair to restore consistency..."
    nodetool repair -pr
else
    echo ""
    echo "3. $pending hints pending, monitoring delivery..."
    # Monitor until complete
    while [ "$pending" -gt 0 ]; do
        sleep 10
        pending=$(nodetool listpendinghints 2>/dev/null | tail -n +2 | awk '{sum+=$2} END {print sum+0}')
        echo "Pending: $pending"
    done
    echo "All hints delivered!"
fi

echo ""
echo "=== Recovery Complete ==="
```

---

## Best Practices

!!! tip "Resume Guidelines"

    1. **Resume promptly** - Don't leave hints paused beyond the hint window
    2. **Monitor after resume** - Watch hint delivery progress
    3. **Check throttling** - Adjust if delivery is too slow or fast
    4. **Verify target nodes** - Ensure target nodes are UP before resuming
    5. **Plan for expired hints** - Run repair if hints may have expired
    6. **Resume cluster-wide** - If paused cluster-wide, resume on all nodes

!!! warning "After Extended Pause"
    If hints were paused longer than `max_hint_window_in_ms` (default 3 hours), some hints may have expired. Run `nodetool repair -pr` after resuming to ensure full consistency.

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [pausehandoff](pausehandoff.md) | Pause hint delivery |
| [enablehandoff](enablehandoff.md) | Enable hint storage |
| [disablehandoff](disablehandoff.md) | Disable hint storage and delivery |
| [statushandoff](statushandoff.md) | Check handoff status |
| [listpendinghints](listpendinghints.md) | List pending hints |
| [truncatehints](truncatehints.md) | Remove all hints |
| [sethintedhandoffthrottlekb](sethintedhandoffthrottlekb.md) | Control delivery throttle |
