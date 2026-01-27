---
title: "nodetool enablehintsfordc"
description: "Enable hinted handoff for a specific datacenter using nodetool enablehintsfordc."
meta:
  - name: keywords
    content: "nodetool enablehintsfordc, enable hints DC, hinted handoff, multi-datacenter"
---

# nodetool enablehintsfordc

Enables hints for a specific datacenter.

---

## Synopsis

```bash
nodetool [connection_options] enablehintsfordc <datacenter>
```

## Description

`nodetool enablehintsfordc` re-enables hint storage for nodes in a specific datacenter after it was disabled with `disablehintsfordc`. When enabled, the local node will store hints for writes destined for unavailable nodes in the specified datacenter.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `datacenter` | Name of the datacenter to enable hints for |

---

## Examples

### Enable Hints for a Datacenter

```bash
nodetool enablehintsfordc dc2
```

---

## When to Use

### After Datacenter Recovery

Re-enable hints after a datacenter comes back online:

```bash
# DC2 is back online
nodetool enablehintsfordc dc2

# Verify hints are being stored again
```

### After Datacenter Maintenance

Resume normal hint behavior after planned maintenance:

```bash
# Maintenance complete
nodetool enablehintsfordc dc2

# Monitor hint activity
nodetool listpendinghints
```

### Restore Normal Operations

Return to default behavior after temporary disable:

```bash
# Re-enable hints for datacenter
nodetool enablehintsfordc dc2

# Verify enabled (no specific status command, but hints will accumulate)
```

---

## Cluster-Wide Operation

### Enable on All Nodes

Hints are stored on coordinator nodes, so enable on all nodes:

```bash
#!/bin/bash
# enable_hints_dc_cluster.sh

DATACENTER="$1"

if [ -z "$DATACENTER" ]; then
    echo "Usage: $0 <datacenter>"
    exit 1
fi

# Get list of node IPs from local nodetool status
nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo -n "$node: "
    ssh "$node" "nodetool enablehintsfordc $DATACENTER" && echo "enabled" || echo "FAILED"
done
```

---

## Use Cases

### Multi-DC Recovery Workflow

```bash
#!/bin/bash
# dc_recovery_workflow.sh

DC_NAME="$1"

echo "=== Datacenter Recovery: $DC_NAME ==="

# 1. Verify DC is back online
echo "1. Checking datacenter status..."
nodetool status | grep "$DC_NAME" -A 10

# 2. Re-enable hints for this DC on all nodes via SSH
echo ""
echo "2. Enabling hints for $DC_NAME..."
for node in $(nodetool status | grep "^UN" | awk '{print $2}'); do
    ssh "$node" "nodetool enablehintsfordc $DC_NAME" 2>/dev/null
done

# 3. Run repair to restore consistency
echo ""
echo "3. Consider running repair for full consistency"
echo "   nodetool repair -dc $DC_NAME"
```

---

## Impact

### When Hints Are Enabled

| Aspect | Behavior |
|--------|----------|
| Hint storage | Resumes for DC |
| Coordinator disk | May grow with hints |
| Automatic recovery | Restored |
| Write guarantees | Full coverage |

---

## Troubleshooting

### Hints Not Being Stored After Enable

```bash
# Verify datacenter name is correct
nodetool status

# Check if hints are accumulating
nodetool listpendinghints

# Check for errors
grep -i "hint" /var/log/cassandra/system.log | tail -10
```

### Wrong Datacenter Name

```bash
# List available datacenters
nodetool status | grep "Datacenter:" | awk '{print $2}'

# Use exact datacenter name
nodetool enablehintsfordc <exact_name>
```

---

## Best Practices

!!! tip "Enable Hints Guidelines"

    1. **Verify DC is healthy** - Ensure nodes are UP before enabling
    2. **Enable cluster-wide** - Run on all coordinator nodes
    3. **Monitor after enable** - Watch hint accumulation
    4. **Consider repair** - Run repair for extended outages

!!! info "Default Behavior"

    By default, hints are enabled for all datacenters. This command is only needed after explicitly disabling hints for a DC.

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [disablehintsfordc](disablehintsfordc.md) | Disable hints for a datacenter |
| [enablehandoff](enablehandoff.md) | Enable all hinted handoff |
| [listpendinghints](listpendinghints.md) | List pending hints |
| [statushandoff](statushandoff.md) | Check handoff status |