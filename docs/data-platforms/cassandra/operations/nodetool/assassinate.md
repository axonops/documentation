---
title: "nodetool assassinate"
description: "Remove a dead node from the Cassandra cluster forcibly using nodetool assassinate. Use as last resort when removenode fails."
meta:
  - name: keywords
    content: "nodetool assassinate, remove dead node, Cassandra cluster, force remove node"
---

# nodetool assassinate

Forcibly removes a dead node from gossip when normal removal methods fail.

---

## Synopsis

```bash
nodetool [connection_options] assassinate <ip_address>
```

## Description

`nodetool assassinate` forcibly removes a node's gossip state from the cluster. This is a last-resort operation when a dead node cannot be removed through normal means (`decommission` or `removenode`).

!!! danger "Last Resort Only"
    Assassinate should only be used when:

    - Node is permanently dead
    - `removenode` has failed or hung
    - Gossip state is corrupted
    - Normal cluster operations are blocked

---

## Arguments

| Argument | Description |
|----------|-------------|
| `ip_address` | IP address of the node to assassinate |

---

## When to Use

### Removenode Failed

When `nodetool removenode` fails or hangs:

```bash
# Removenode stuck for hours
nodetool removenode status
# Shows: InProgress but no movement

# Assassinate as last resort
nodetool assassinate 192.168.1.102
```

### Ghost Node in Cluster

Node was removed but still appears in `nodetool status`:

```bash
# Node shows DN or LEFT but won't disappear
nodetool status
# Shows: DN  192.168.1.102  ...

nodetool assassinate 192.168.1.102
```

### Stuck Decommission

When a node started decommissioning but failed midway:

```bash
# Node shows UL but hasn't progressed
# Node is now unreachable
nodetool assassinate 192.168.1.102
```

### Schema Blocked by Dead Node

Schema changes fail due to unreachable node:

```bash
# Schema change times out waiting for dead node
# After confirming node is permanently dead
nodetool assassinate 192.168.1.102
```

---

## When NOT to Use

### Node is Still Running

!!! danger "Never Assassinate Live Nodes"
    If the node is actually running:

    - Data inconsistency will occur
    - Node will try to rejoin
    - Creates split-brain scenario

    Verify node is truly dead first.

### Before Trying Normal Methods

Always attempt in this order:

1. **Node alive?** → Use `decommission` on the node
2. **Node dead?** → Use `removenode` from any live node
3. **Removenode failed?** → Use `assassinate` as last resort

### Network Issues

If the node is temporarily unreachable (not dead):

- Fix network issues instead
- Don't assassinate - node will recover

---

## Before Assassinating

### Verify Node is Dead

```bash
# Try to reach node
ping 192.168.1.102
ssh 192.168.1.102 'nodetool info'

# Check cluster status
nodetool status
nodetool gossipinfo | grep -A10 "/192.168.1.102"
```

### Document the Situation

!!! tip "Document Before Acting"
    Record:

    - Why node is being assassinated
    - Node details (Host ID, tokens)
    - Current cluster state
    - Any error messages from removenode

### Ensure Quorum

Verify remaining nodes can satisfy read/write quorum for all keyspaces.

---

## Examples

### Basic Assassination

```bash
nodetool assassinate 192.168.1.102
```

### Verify Removal

```bash
# Check node is gone
nodetool status

# Check gossip state
nodetool gossipinfo | grep 192.168.1.102
# Should return nothing
```

---

## Process Flow

### Node Removal Decision Tree

| Step | Question | Action |
|------|----------|--------|
| 1 | Is node responding? | **Yes**: Use `nodetool decommission` (on the node itself) |
| 2 | Did `nodetool removenode <host-id>` succeed? | **Yes**: Done. **No**: Continue |
| 3 | Have you waited a reasonable time? | **No**: Wait longer, monitor `removenode status` |
| 4 | Is node confirmed dead? | **Yes**: Use `nodetool assassinate <ip>` (last resort). **No**: Investigate further, try to recover node |

---

## After Assassination

### Verify Cluster State

```bash
# Check cluster status
nodetool status

# Verify schema agreement
nodetool describecluster

# Check gossip is clean
nodetool gossipinfo | grep -c "192.168.1.102"  # Should be 0
```

### Run Repair

Data may be inconsistent after forced removal:

```bash
# On each remaining node
nodetool repair -pr
```

### Clean Up Hardware

If the assassinated node still exists physically:

- Remove it from the network
- Clear its data directories if reusing hardware

---

## Common Issues

### Node Reappears After Assassination

If the "dead" node was actually alive:

!!! danger "Split Brain"
    The node will attempt to rejoin, causing data conflicts:

    1. Immediately stop Cassandra on that node
    2. Clear its data directories
    3. Run repair on remaining nodes

### "Unknown endpoint"

```
ERROR: Unknown endpoint /192.168.1.102
```

The node is not in the cluster's gossip state. No action needed.

### Assassination Doesn't Complete

If assassinate hangs:

1. Check logs for errors
2. Try from a different node
3. May need to restart affected nodes

### Schema Still Blocked

If schema changes still fail after assassination:

```bash
# Check schema versions
nodetool describecluster

# Force schema reset if needed (last resort)
nodetool resetlocalschema
```

---

## Risks and Consequences

### Data Loss Risk

!!! danger "Potential Data Loss"
    Assassinating a node that had unique data (RF=1 ranges) results in permanent data loss. Ensure:

    - RF > 1 for all keyspaces
    - Other replicas exist and are healthy

### Cluster Instability

Assassination can cause temporary instability:

- Gossip reconvergence
- Token range recalculation
- Schema propagation issues

### Recovery Difficulty

Once assassinated, the node cannot easily rejoin:

- Must be bootstrapped as new node
- Or completely replaced

---

## Best Practices

!!! warning "Assassination Guidelines"
    1. **Last resort only** - Try all other methods first
    2. **Verify node is dead** - Ping, SSH, check physically
    3. **Document everything** - Record why and when
    4. **Ensure quorum** - Verify remaining capacity
    5. **Repair after** - Run repair on remaining nodes
    6. **Remove hardware** - Prevent zombie node from returning
    7. **Review root cause** - Understand why node died

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [decommission](decommission.md) | Graceful removal of live node |
| [removenode](removenode.md) | Remove dead node (preferred) |
| [status](status.md) | Check cluster state |
| [gossipinfo](gossipinfo.md) | View gossip details |
| [repair](repair.md) | Run after assassination |
| [describecluster](describecluster.md) | Check schema agreement |
