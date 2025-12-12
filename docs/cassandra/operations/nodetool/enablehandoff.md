---
description: "Enable hinted handoff in Cassandra using nodetool enablehandoff command."
meta:
  - name: keywords
    content: "nodetool enablehandoff, enable hints, hinted handoff, Cassandra"
---

# nodetool enablehandoff

Re-enables hinted handoff on the node.

---

## Synopsis

```bash
nodetool [connection_options] enablehandoff
```

## Description

`nodetool enablehandoff` re-enables the hinted handoff mechanism after it was disabled with `disablehandoff`. Hinted handoff is a critical consistency feature that stores write hints for temporarily unavailable nodes, ensuring data is delivered when those nodes recover.

When a coordinator receives a write request and a replica is temporarily unavailable, the coordinator stores a "hint" locally. Once the unavailable replica comes back online, the coordinator replays the hint to bring the replica up to date.

!!! info "Consistency Mechanism"
    Hinted handoff is one of Cassandra's key mechanisms for maintaining eventual consistency. It ensures that writes intended for temporarily down nodes are not lost and are delivered when the node recovers.

---

## Behavior

When hinted handoff is enabled:

1. Coordinator nodes store hints for unavailable replicas
2. Hints are stored in the `system.hints` table
3. When target nodes recover, hints are replayed automatically
4. Old hints expire based on `max_hint_window_in_ms` (default: 3 hours)

### Hint Storage

Hints are stored on the **coordinator** node that received the original write request, not on the unavailable node.

---

## Examples

### Basic Usage

```bash
nodetool enablehandoff
```

### Verify Status

```bash
nodetool enablehandoff
nodetool statushandoff
# Expected: Hinted handoff is running
```

### On Remote Node

```bash
nodetool -h 192.168.1.100 enablehandoff
```

---

## When to Use

### After Maintenance

Re-enable hinted handoff after maintenance operations:

```bash
# Maintenance complete, restore normal operation
nodetool enablehandoff

# Verify enabled
nodetool statushandoff
```

### After Troubleshooting

When handoff was disabled to investigate hint-related issues:

```bash
# Issue resolved
nodetool enablehandoff
```

### After Node Recovery

When restoring full functionality to a node:

```bash
# Enable handoff
nodetool enablehandoff

# Check for pending hints
nodetool tpstats | grep -i hint
```

---

## Impact of Hinted Handoff

### When Enabled (Normal)

| Scenario | Behavior |
|----------|----------|
| Replica down during write | Hint stored on coordinator |
| Replica recovers | Hints replayed automatically |
| Write consistency | Maintained via hint delivery |
| Coordinator disk | Uses space for hint storage |

### When Disabled

| Scenario | Behavior |
|----------|----------|
| Replica down during write | No hint stored |
| Replica recovers | Missing writes not delivered |
| Write consistency | Requires repair to restore |
| Coordinator disk | No hint storage overhead |

!!! danger "Consistency Risk"
    With hinted handoff disabled, writes to temporarily unavailable replicas are lost. The only way to restore consistency is through repair operations.

---

## Understanding Hinted Handoff

### How It Works

```
Write Request Flow (with hint):

1. Client → Coordinator: WRITE (CL=QUORUM, RF=3)

2. Coordinator sends to replicas:
   - Replica A: ✓ Success
   - Replica B: ✓ Success
   - Replica C: ✗ Timeout (node down)

3. Quorum satisfied (2/3), client gets success

4. Coordinator stores hint for Replica C

5. Later, when Replica C recovers:
   - Coordinator detects recovery via gossip
   - Hint is replayed to Replica C
   - Replica C receives the write
```

### Hint Window

Hints are only stored for nodes that are expected to recover within the hint window:

```yaml
# cassandra.yaml
max_hint_window_in_ms: 10800000  # 3 hours (default)
```

If a node is down longer than the hint window, hints are not stored, and repair is required.

---

## Configuration

### cassandra.yaml Settings

```yaml
# Enable/disable hinted handoff globally
hinted_handoff_enabled: true

# Maximum time to store hints for a dead node
max_hint_window_in_ms: 10800000  # 3 hours

# Throttle hint delivery
hinted_handoff_throttle_in_kb: 1024

# Maximum hint delivery threads
max_hints_delivery_threads: 2
```

### Runtime vs Configuration

| Method | Persistence | Scope |
|--------|-------------|-------|
| `nodetool enablehandoff` | Until restart | This node only |
| `cassandra.yaml` setting | Permanent | All restarts |

---

## Monitoring Hints

### Check Hint Status

```bash
# View hinted handoff status
nodetool statushandoff

# Check hint-related thread pools
nodetool tpstats | grep -i hint
```

### Check Pending Hints

```bash
# List pending hints by target node
nodetool listpendinghints
```

Example output:
```
Host ID                               Hints
12345678-1234-1234-1234-123456789abc  1523
87654321-4321-4321-4321-cba987654321  42
```

### View Hints Table Size

```bash
# Check hints table size
nodetool tablestats system.hints
```

---

## Workflow: Recovery After Handoff Disable

```bash
#!/bin/bash
# recover_from_disabled_handoff.sh

echo "=== Hinted Handoff Recovery ==="

# 1. Check current status
echo "1. Current status:"
nodetool statushandoff

# 2. Enable hinted handoff
echo ""
echo "2. Enabling hinted handoff..."
nodetool enablehandoff

# 3. Verify enabled
echo ""
echo "3. Verifying enabled:"
nodetool statushandoff

# 4. Check for pending hints
echo ""
echo "4. Pending hints:"
nodetool listpendinghints

# 5. Check hint thread pool
echo ""
echo "5. Hint thread pool status:"
nodetool tpstats | grep -i hint

echo ""
echo "=== Complete ==="
echo "NOTE: If handoff was disabled during node outages, run repair to restore consistency."
```

---

## Cluster-Wide Operations

### Enable on All Nodes

```bash
#!/bin/bash
# enable_handoff_cluster.sh

nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

echo "Enabling hinted handoff cluster-wide..."
for node in $nodes; do
    echo -n "$node: "
    nodetool -h $node enablehandoff 2>/dev/null && echo "enabled" || echo "FAILED"
done

echo ""
echo "Verification:"
for node in $nodes; do
    echo -n "$node: "
    nodetool -h $node statushandoff 2>/dev/null
done
```

---

## Troubleshooting

### Handoff Won't Enable

```bash
# Check JMX connectivity
nodetool info

# Check logs
tail -100 /var/log/cassandra/system.log | grep -i hint
```

### Hints Not Being Delivered

If hints are not being replayed to recovered nodes:

```bash
# Check if target node is seen as UP
nodetool status

# Check hint delivery threads
nodetool tpstats | grep -i hint

# Check for hint delivery errors in logs
grep -i "hint" /var/log/cassandra/system.log | tail -20
```

### High Hint Accumulation

If hints are accumulating but not being delivered:

```bash
# Check pending hints
nodetool listpendinghints

# Check target nodes are UP
nodetool status

# May need to truncate old hints and repair instead
nodetool truncatehints
nodetool repair -pr
```

---

## Best Practices

!!! tip "Hinted Handoff Guidelines"

    1. **Keep enabled in production** - Hinted handoff is essential for consistency
    2. **Monitor hint accumulation** - Watch for growing hint backlogs
    3. **Verify after enable** - Confirm with `statushandoff`
    4. **Consider hint window** - Adjust based on expected outage durations
    5. **Plan for repair** - If disabled during outages, run repair afterward
    6. **Monitor disk space** - Hints consume disk on coordinators

!!! warning "Repair Required"
    If hinted handoff was disabled while nodes were down, run `nodetool repair` to restore consistency. Hints that would have been stored during that period are lost.

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [disablehandoff](disablehandoff.md) | Disable hinted handoff |
| [statushandoff](statushandoff.md) | Check handoff status |
| [pausehandoff](pausehandoff.md) | Pause hint delivery |
| [resumehandoff](resumehandoff.md) | Resume hint delivery |
| [listpendinghints](listpendinghints.md) | List pending hints |
| [truncatehints](truncatehints.md) | Remove all hints |
| [repair](repair.md) | Anti-entropy repair |
