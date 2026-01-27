---
title: "nodetool disablehandoff"
description: "Disable hinted handoff in Cassandra using nodetool disablehandoff command."
meta:
  - name: keywords
    content: "nodetool disablehandoff, disable hints, hinted handoff, Cassandra"
---

# nodetool disablehandoff

Disables hinted handoff on the node.

---

## Synopsis

```bash
nodetool [connection_options] disablehandoff
```

## Description

`nodetool disablehandoff` disables the hinted handoff mechanism on the node. When disabled, the node will not store hints for writes intended for temporarily unavailable replicas. This is a significant change that affects data consistency guarantees.

!!! warning "Non-Persistent Setting"
    This setting is applied at runtime only and does not persist across node restarts. After a restart, hinted handoff reverts to the `hinted_handoff_enabled` setting in `cassandra.yaml` (default: `true`).

    To make the change permanent, update `cassandra.yaml`:

    ```yaml
    hinted_handoff_enabled: false
    ```

!!! danger "Critical Consistency Impact"
    Disabling hinted handoff means writes to unavailable replicas will be lost and only recoverable through repair operations. Use this command with extreme caution in production environments.

---

## Behavior

When hinted handoff is disabled:

1. No new hints are stored for unavailable replicas
2. Existing hints continue to be delivered (unless paused)
3. Writes to down nodes are acknowledged but data is lost for those replicas
4. Repair becomes the only mechanism to restore consistency

### What Continues

| Feature | Status |
|---------|--------|
| Existing hint delivery | Continues (unless paused) |
| Writes | Succeed if consistency level met |
| Gossip | Continues normally |
| Compaction | Continues normally |

### What Stops

| Feature | Status |
|---------|--------|
| New hint storage | Disabled |
| Automatic recovery | Requires repair |
| Write durability to down nodes | Lost |

---

## Examples

### Basic Usage

```bash
nodetool disablehandoff
```

### Verify Disabled

```bash
nodetool disablehandoff
nodetool statushandoff
# Expected: Hinted handoff is not running
```

---

## When to Use

### Disk Space Emergency

When coordinator nodes are running out of disk space due to hint accumulation:

```bash
# 1. Disable new hint storage
nodetool disablehandoff

# 2. Truncate existing hints
nodetool truncatehints

# 3. Free more space if needed
nodetool clearsnapshot --all

# 4. Re-enable when space is available
nodetool enablehandoff
```

### Troubleshooting Hint Storms

When hint replay is causing performance issues:

```bash
# 1. Pause hint delivery first
nodetool pausehandoff

# 2. If issues persist, disable completely
nodetool disablehandoff

# 3. Investigate and resolve
# ...

# 4. Re-enable
nodetool enablehandoff
```

### During Controlled Decommission

Sometimes disabled before decommissioning nodes:

```bash
# On all nodes, disable hints for the departing node
nodetool disablehintsfordc dc_being_removed

# Or disable globally during the operation
nodetool disablehandoff
```

### Long-Term Node Outage

When a node will be down longer than the hint window:

```bash
# Hints won't be stored anyway after window expires
# May choose to disable to reduce coordinator overhead
nodetool disablehandoff

# Plan for repair when node returns
```

---

## Impact Assessment

### Immediate Effects

| Aspect | Impact |
|--------|--------|
| New hint storage | Stops immediately |
| Coordinator disk usage | Stops growing from hints |
| Write acknowledgments | Continue normally |
| Consistency level satisfaction | Unchanged |

### Consistency Implications

| Scenario | With Handoff | Without Handoff |
|----------|--------------|-----------------|
| Node down 5 minutes | Hints stored, auto-recovery | Data lost, needs repair |
| Node down 1 hour | Hints stored, auto-recovery | Data lost, needs repair |
| Node down 4 hours | Beyond window, needs repair | Data lost, needs repair |

!!! warning "Silent Data Loss"
    With handoff disabled, writes to unavailable replicas appear to succeed (if consistency level is met) but the data is silently lost for those replicas. There's no error or indication of the missing data until inconsistencies are discovered.

---

## Workflow: Emergency Disk Space Recovery

```bash
#!/bin/bash
# emergency_hint_cleanup.sh

echo "=== Emergency Hint Cleanup ==="
echo "WARNING: This will prevent automatic recovery for down nodes!"
echo ""

# 1. Check current hint status
echo "1. Current hint status:"
nodetool statushandoff
echo ""

echo "Pending hints:"
nodetool listpendinghints
echo ""

echo "Hints table size:"
nodetool tablestats system.hints | grep "Space used"
echo ""

# 2. Disable new hints
echo "2. Disabling hinted handoff..."
nodetool disablehandoff

# 3. Truncate existing hints
echo "3. Truncating existing hints..."
nodetool truncatehints

# 4. Verify cleanup
echo "4. Verification:"
echo "Hints table after truncate:"
nodetool tablestats system.hints | grep "Space used"
echo ""

echo "=== Complete ==="
echo ""
echo "IMPORTANT: Run 'nodetool repair' to restore consistency!"
echo "Remember to re-enable: nodetool enablehandoff"
```

---

## Risks and Mitigations

### Risk: Silent Data Inconsistency

**Cause:** Writes to down nodes are lost without indication

**Mitigation:**
- Schedule immediate repair after re-enabling
- Monitor for node down events during disabled period
- Keep disabled period as short as possible

```bash
# After re-enabling
nodetool enablehandoff

# Run repair to restore consistency
nodetool repair -pr
```

### Risk: Forgot to Re-enable

**Symptom:** Ongoing data inconsistency

**Mitigation:**
```bash
# Set a reminder
echo "nodetool enablehandoff" | at now + 1 hour

# Include in monitoring
nodetool statushandoff | grep -q "not running" && \
    echo "WARNING: Hinted handoff is disabled!"
```

### Risk: Multiple Nodes with Different States

**Cause:** Inconsistent cluster configuration

**Mitigation:**
```bash
# Audit all nodes
for node in $(nodetool status | grep "^UN" | awk '{print $2}'); do
    echo -n "$node: "
    ssh "$node" "nodetool statushandoff"
done
```

---

## Monitoring While Disabled

### Track Duration

```bash
# Log when disabled
echo "$(date): Hinted handoff disabled" >> /var/log/cassandra/handoff_changes.log

# Log when re-enabled
echo "$(date): Hinted handoff enabled" >> /var/log/cassandra/handoff_changes.log
```

### Monitor Node Status

While handoff is disabled, closely monitor for node failures:

```bash
# Watch cluster status
watch -n 30 'nodetool status | grep -v "^UN"'

# Any node not UN means potential data loss
```

### Check for Impact

```bash
# After re-enabling, check for inconsistencies
nodetool describecluster

# Run repair on potentially affected keyspaces
nodetool repair -pr my_keyspace
```

---

## Cluster-Wide Operations

### Disable on All Nodes

```bash
#!/bin/bash
# disable_handoff_cluster.sh

echo "WARNING: Disabling hinted handoff cluster-wide!"
echo "This will prevent automatic recovery for node outages."
echo ""# Get list of node IPs from local nodetool status


nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo -n "$node: "
    ssh "$node" "nodetool disablehandoff 2>/dev/null && echo "disabled" || echo "FAILED""
done

echo ""
echo "Verification:"
for node in $nodes; do
    echo -n "$node: "
    ssh "$node" "nodetool statushandoff 2>/dev/null"
done

echo ""
echo "REMEMBER: Re-enable with: nodetool enablehandoff"
echo "REMEMBER: Run repair afterward: nodetool repair -pr"
```

---

## Troubleshooting

### Handoff Already Disabled

If you expected it to be enabled:

```bash
# Check cassandra.yaml setting
grep hinted_handoff_enabled /etc/cassandra/cassandra.yaml

# Check if runtime disabled
nodetool statushandoff

# Enable if needed
nodetool enablehandoff
```

### Cannot Disable

```bash
# Check JMX connectivity
nodetool info

# Check logs for errors
tail -100 /var/log/cassandra/system.log | grep -i hint
```

---

## Recovery Procedure

After re-enabling hinted handoff:

```bash
#!/bin/bash
# recover_after_handoff_disable.sh

echo "=== Recovery After Hinted Handoff Disable ==="

# 1. Re-enable hinted handoff
echo "1. Enabling hinted handoff..."
nodetool enablehandoff

# 2. Verify enabled
echo ""
echo "2. Verification:"
nodetool statushandoff

# 3. Check cluster status
echo ""
echo "3. Cluster status (check for any DN nodes):"
nodetool status | head -15

# 4. Run repair for affected keyspaces
echo ""
echo "4. Running repair..."
# For each keyspace that may have been affected:
for ks in $(nodetool tablestats | grep "Keyspace:" | awk '{print $2}' | grep -v "^system"); do
    echo "Repairing $ks..."
    nodetool repair -pr $ks
done

echo ""
echo "=== Recovery Complete ==="
```

---

## Best Practices

!!! tip "Disable Guidelines"

    1. **Avoid in production** - Only disable as last resort
    2. **Document the reason** - Log why and when disabled
    3. **Set time limits** - Don't leave disabled indefinitely
    4. **Monitor closely** - Watch for node failures during disabled period
    5. **Plan for repair** - Schedule repair immediately after re-enabling
    6. **Communicate** - Inform team when handoff is disabled

!!! danger "Never Do"

    - Leave handoff disabled for extended periods
    - Disable without a recovery plan
    - Assume data is consistent after disabling
    - Forget to repair after re-enabling

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [enablehandoff](enablehandoff.md) | Re-enable hinted handoff |
| [statushandoff](statushandoff.md) | Check handoff status |
| [pausehandoff](pausehandoff.md) | Pause hint delivery |
| [resumehandoff](resumehandoff.md) | Resume hint delivery |
| [truncatehints](truncatehints.md) | Remove all hints |
| [listpendinghints](listpendinghints.md) | List pending hints |
| [repair](repair.md) | Anti-entropy repair |