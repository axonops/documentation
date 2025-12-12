---
description: "Pause hinted handoff delivery in Cassandra using nodetool pausehandoff command."
meta:
  - name: keywords
    content: "nodetool pausehandoff, pause hints, hinted handoff, Cassandra"
---

# nodetool pausehandoff

Pauses the delivery of hints to recovering nodes.

---

## Synopsis

```bash
nodetool [connection_options] pausehandoff
```

## Description

`nodetool pausehandoff` temporarily stops the delivery of stored hints to their target nodes. Unlike `disablehandoff`, this command does **not** prevent new hints from being stored—it only pauses the replay of existing hints.

This is useful when hint delivery is causing performance issues on recovering nodes or when controlled hint replay timing is needed.

!!! info "Pause vs Disable"
    - **pausehandoff**: Stops hint delivery only. New hints continue to be stored.
    - **disablehandoff**: Stops both hint storage AND delivery.

---

## Behavior

When hint delivery is paused:

1. New hints continue to be stored for unavailable replicas
2. Existing hints are NOT delivered to recovered nodes
3. Hints accumulate until delivery is resumed
4. Hint expiration continues (hints may expire before delivery)

### What Continues

| Feature | Status |
|---------|--------|
| New hint storage | Continues normally |
| Gossip | Continues normally |
| Writes | Continue normally |
| Read repairs | Continue normally |

### What Stops

| Feature | Status |
|---------|--------|
| Hint delivery | Paused |
| Automatic consistency restoration | Suspended |
| Hint replay to recovered nodes | Stopped |

---

## Examples

### Basic Usage

```bash
nodetool pausehandoff
```

### Pause and Verify

```bash
nodetool pausehandoff

# Check hint delivery threads
nodetool tpstats | grep -i hint
```

### On Remote Node

```bash
nodetool -h 192.168.1.100 pausehandoff
```

---

## When to Use

### Recovering Node Under Stress

When a recovering node is overwhelmed by hint replay:

```bash
# 1. Pause hint delivery
nodetool pausehandoff

# 2. Let the node stabilize
# Monitor: nodetool tpstats

# 3. Resume when ready
nodetool resumehandoff
```

### Controlled Recovery Timing

When needing to control when hints are delivered:

```bash
# Pause during peak hours
nodetool pausehandoff

# Resume during maintenance window
# (later)
nodetool resumehandoff
```

### Troubleshooting Hint Storms

When investigating hint-related performance issues:

```bash
# 1. Check hint delivery activity
nodetool tpstats | grep -i hint

# 2. Pause if hint delivery is causing issues
nodetool pausehandoff

# 3. Investigate
nodetool listpendinghints
nodetool tablestats system.hints

# 4. Resume when resolved
nodetool resumehandoff
```

### During Node Maintenance

Prevent hint delivery to a node under maintenance:

```bash
# On coordinator nodes, pause hint delivery
nodetool pausehandoff

# Perform maintenance on target node
# ...

# Resume after maintenance
nodetool resumehandoff
```

---

## Impact Assessment

### Immediate Effects

| Aspect | Impact |
|--------|--------|
| Hint delivery | Stops immediately |
| Coordinator load | May increase (hints accumulate) |
| Target node load | Decreases (no hint replay) |
| Disk usage | Hints continue accumulating |

### Consistency Implications

| Scenario | With Delivery | With Paused Delivery |
|----------|---------------|---------------------|
| Node recovers | Hints replayed immediately | Hints queued, not delivered |
| Multiple writes | Consistency restored quickly | Consistency delayed |
| Hint expiration | Normal | Hints may expire before delivery |

!!! warning "Hint Expiration Risk"
    While delivery is paused, hints continue to age. If paused too long, hints may expire (default: 3 hours) and be lost. Run repair to restore consistency if hints expire.

---

## Workflow: Controlled Hint Delivery

```bash
#!/bin/bash
# controlled_hint_delivery.sh

echo "=== Controlled Hint Delivery ==="

# 1. Check current hint status
echo "1. Current pending hints:"
nodetool listpendinghints

# 2. Pause delivery
echo ""
echo "2. Pausing hint delivery..."
nodetool pausehandoff

# 3. Verify paused
echo ""
echo "3. Hint thread activity (should show no active delivery):"
nodetool tpstats | grep -i hint

# 4. Wait for user confirmation
echo ""
read -p "Press Enter to resume hint delivery..."

# 5. Resume delivery
echo ""
echo "5. Resuming hint delivery..."
nodetool resumehandoff

# 6. Monitor delivery
echo ""
echo "6. Monitoring hint delivery:"
watch -n 2 'nodetool tpstats | grep -i hint'
```

---

## Monitoring While Paused

### Track Hint Accumulation

```bash
# Check pending hints periodically
watch -n 60 'nodetool listpendinghints'
```

### Monitor Hints Table Size

```bash
# Track disk usage by hints
watch -n 60 'nodetool tablestats system.hints | grep "Space used"'
```

### Check Hint Age

```bash
#!/bin/bash
# Monitor hint accumulation while paused

echo "=== Hint Status (Delivery Paused) ==="

# Pending hints
echo "Pending hints by target:"
nodetool listpendinghints

# Hints table size
echo ""
echo "Hints table size:"
nodetool tablestats system.hints 2>/dev/null | grep -E "Space used|SSTable count"

# Warn about expiration
echo ""
hint_window=$(grep "max_hint_window_in_ms" /etc/cassandra/cassandra.yaml 2>/dev/null | awk '{print $2}')
if [ -n "$hint_window" ]; then
    hours=$((hint_window / 3600000))
    echo "Hint window: ${hours} hours"
    echo "WARNING: Hints older than ${hours} hours will expire!"
fi
```

---

## Risks and Mitigations

### Risk: Hint Expiration

**Cause:** Hints expire while delivery is paused

**Mitigation:**
```bash
# Track pause duration
echo "Paused at: $(date)" >> /var/log/cassandra/hint_pause.log

# Set a reminder to resume
echo "nodetool resumehandoff" | at now + 2 hours

# After resuming, check if hints expired and run repair if needed
nodetool resumehandoff
nodetool repair -pr
```

### Risk: Disk Space Exhaustion

**Cause:** Hints accumulate while paused

**Mitigation:**
```bash
# Monitor disk usage
df -h /var/lib/cassandra

# If critical, may need to truncate hints
nodetool truncatehints

# Then run repair to restore consistency
nodetool repair -pr
```

### Risk: Forgot to Resume

**Symptom:** Recovered nodes remain inconsistent

**Mitigation:**
```bash
# Include in monitoring
#!/bin/bash
# check_hint_delivery.sh

active=$(nodetool tpstats 2>/dev/null | grep "HintedHandoff" | awk '{print $2}')
pending=$(nodetool listpendinghints 2>/dev/null | tail -n +2 | awk '{sum+=$2} END {print sum}')

if [ "$pending" -gt 0 ] && [ "$active" -eq 0 ]; then
    echo "WARNING: Hints pending but delivery may be paused!"
    echo "Pending hints: $pending"
fi
```

---

## Cluster-Wide Operations

### Pause on All Nodes

```bash
#!/bin/bash
# pause_handoff_cluster.sh

echo "Pausing hint delivery cluster-wide..."

nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo -n "$node: "
    nodetool -h $node pausehandoff 2>/dev/null && echo "paused" || echo "FAILED"
done

echo ""
echo "Verification (hint thread activity):"
for node in $nodes; do
    echo "=== $node ==="
    nodetool -h $node tpstats 2>/dev/null | grep -i hint
done

echo ""
echo "REMEMBER: Resume with 'nodetool resumehandoff' on all nodes"
```

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
echo "Hint delivery resumed on all nodes."
```

---

## Troubleshooting

### Hints Still Being Delivered After Pause

```bash
# Verify pause was successful
nodetool tpstats | grep -i hint

# If still active, retry
nodetool pausehandoff

# Check for multiple coordinators
# Each coordinator node needs to pause separately
```

### Cannot Pause

```bash
# Check JMX connectivity
nodetool info

# Check logs for errors
tail -100 /var/log/cassandra/system.log | grep -i hint
```

### High Hint Accumulation While Paused

```bash
# Check pending hints
nodetool listpendinghints

# Check hints table size
nodetool tablestats system.hints

# If too many hints, consider:
# 1. Resume delivery to reduce backlog
# 2. Or truncate and repair if hints will expire anyway
```

---

## Comparison: Pause vs Disable

| Aspect | pausehandoff | disablehandoff |
|--------|--------------|----------------|
| New hint storage | Continues | Stops |
| Hint delivery | Stops | Stops |
| Coordinator disk impact | Continues growing | Stops growing |
| Recovery without repair | Yes (resume) | No (repair required) |
| Use case | Temporary relief | Emergency only |

### Choose pausehandoff When:

- Recovering node is overwhelmed
- Need temporary performance relief
- Plan to resume delivery soon
- Want to preserve hints for later delivery

### Choose disablehandoff When:

- Disk space emergency on coordinator
- Node will be down longer than hint window
- Need to completely stop hint-related activity

---

## Best Practices

!!! tip "Pause Guidelines"

    1. **Prefer pause over disable** - Pause preserves hints for later delivery
    2. **Set time limits** - Don't leave paused indefinitely (hints expire)
    3. **Monitor accumulation** - Watch hint count and disk usage while paused
    4. **Document the reason** - Log why and when you paused
    5. **Plan for resume** - Know when you'll resume delivery
    6. **Consider hint window** - Resume before hints start expiring

!!! warning "Pause Duration Limits"
    The default hint window is 3 hours. If delivery is paused longer than this, hints for down nodes will expire and be lost. Either:

    - Resume delivery before hints expire
    - Plan for repair after resuming
    - Adjust `max_hint_window_in_ms` if longer pause needed

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [resumehandoff](resumehandoff.md) | Resume hint delivery |
| [enablehandoff](enablehandoff.md) | Enable hint storage |
| [disablehandoff](disablehandoff.md) | Disable hint storage and delivery |
| [statushandoff](statushandoff.md) | Check handoff status |
| [listpendinghints](listpendinghints.md) | List pending hints |
| [truncatehints](truncatehints.md) | Remove all hints |
