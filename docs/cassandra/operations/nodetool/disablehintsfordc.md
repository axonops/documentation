# nodetool disablehintsfordc

Disables hints for a specific datacenter.

---

## Synopsis

```bash
nodetool [connection_options] disablehintsfordc <datacenter>
```

## Description

`nodetool disablehintsfordc` prevents the local node from storing hints for writes destined for nodes in a specific datacenter. This is useful when a datacenter is expected to be unavailable for an extended period or is being decommissioned.

!!! warning "Non-Persistent Setting"
    This setting is applied at runtime only and does not persist across node restarts. After a restart, hints for all datacenters are enabled unless configured otherwise in `cassandra.yaml`.

    To permanently disable hints for a datacenter, add it to the `hinted_handoff_disabled_datacenters` list in `cassandra.yaml`:

    ```yaml
    hinted_handoff_disabled_datacenters:
        - dc2
    ```

!!! warning "Consistency Impact"
    Disabling hints for a datacenter means writes to unavailable nodes in that DC will not be recovered automatically. Use `nodetool repair` to restore consistency after re-enabling.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `datacenter` | Name of the datacenter to disable hints for |

---

## Examples

### Disable Hints for a Datacenter

```bash
nodetool disablehintsfordc dc2
```

### On Remote Node

```bash
nodetool -h 192.168.1.100 disablehintsfordc dc2
```

---

## When to Use

### Datacenter Decommissioning

Prevent hint accumulation for a DC being removed:

```bash
# Disable hints for DC being decommissioned
nodetool disablehintsfordc dc_old

# Proceed with decommission operations
```

### Extended Datacenter Outage

When a DC will be down longer than the hint window:

```bash
# DC2 will be down for extended maintenance
nodetool disablehintsfordc dc2

# Hints would expire anyway, this prevents accumulation
```

### Disk Space Management

Prevent hints from consuming disk when a DC is unavailable:

```bash
# Check current hint usage
nodetool tablestats system.hints

# Disable hints for unavailable DC
nodetool disablehintsfordc dc2
```

---

## Cluster-Wide Operation

### Disable on All Nodes

Hints are stored on coordinator nodes, so disable on all:

```bash
#!/bin/bash
# disable_hints_dc_cluster.sh

DATACENTER="$1"

if [ -z "$DATACENTER" ]; then
    echo "Usage: $0 <datacenter>"
    exit 1
fi

nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

echo "Disabling hints for $DATACENTER on all nodes..."
for node in $nodes; do
    echo -n "$node: "
    nodetool -h $node disablehintsfordc $DATACENTER && echo "disabled" || echo "FAILED"
done

echo ""
echo "Remember to re-enable with: nodetool enablehintsfordc $DATACENTER"
```

---

## Impact Assessment

### Immediate Effects

| Aspect | Impact |
|--------|--------|
| New hints for DC | Not stored |
| Existing hints | Continue delivery attempts |
| Coordinator disk | Stops growing for this DC |

### Consistency Implications

| Scenario | With Hints | Without Hints |
|----------|------------|---------------|
| DC temporarily down | Auto-recovery | Needs repair |
| Node restart | Hints delivered | Needs repair |
| Network partition | Hints queued | Data diverges |

---

## Workflow: Datacenter Maintenance

```bash
#!/bin/bash
# dc_maintenance_workflow.sh

DC_NAME="$1"

echo "=== Datacenter Maintenance: $DC_NAME ==="

# 1. Disable hints for the DC
echo "1. Disabling hints for $DC_NAME..."
for node in $(nodetool status | grep "^UN" | awk '{print $2}'); do
    nodetool -h $node disablehintsfordc $DC_NAME 2>/dev/null
done

# 2. Log the action
echo "$(date): Hints disabled for $DC_NAME" >> /var/log/cassandra/dc_maintenance.log

# 3. Remind about re-enabling
echo ""
echo "Hints disabled for $DC_NAME"
echo "After maintenance, run:"
echo "  - nodetool enablehintsfordc $DC_NAME (on all nodes)"
echo "  - nodetool repair -dc $DC_NAME"
```

---

## Troubleshooting

### Hints Still Growing After Disable

```bash
# Verify disabled on all coordinators
# Must run on every node in the cluster

# Check if hints are from before disable
nodetool listpendinghints
```

### Wrong Datacenter Name

```bash
# List available datacenters
nodetool status | grep "Datacenter:" | awk '{print $2}'

# Use exact name (case-sensitive)
```

---

## Recovery After Extended Disable

```bash
#!/bin/bash
# recover_after_dc_maintenance.sh

DC_NAME="$1"

echo "=== Recovery After DC Maintenance ==="

# 1. Re-enable hints
echo "1. Re-enabling hints for $DC_NAME..."
for node in $(nodetool status | grep "^UN" | awk '{print $2}'); do
    nodetool -h $node enablehintsfordc $DC_NAME 2>/dev/null
done

# 2. Run repair
echo ""
echo "2. Running repair for $DC_NAME..."
nodetool repair -dc $DC_NAME

echo ""
echo "Recovery complete."
```

---

## Best Practices

!!! tip "Disable Hints Guidelines"

    1. **Disable cluster-wide** - Run on all coordinator nodes
    2. **Document the reason** - Log why and when disabled
    3. **Plan for repair** - Schedule repair after re-enabling
    4. **Set reminders** - Don't forget to re-enable

!!! danger "Considerations"

    - Data consistency relies on repair after re-enabling
    - Don't disable indefinitely without reason
    - Affects all writes to nodes in that DC
    - Must disable on all nodes to be effective

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [enablehintsfordc](enablehintsfordc.md) | Re-enable hints for a datacenter |
| [disablehandoff](disablehandoff.md) | Disable all hinted handoff |
| [listpendinghints](listpendinghints.md) | List pending hints |
| [repair](repair.md) | Restore consistency |
