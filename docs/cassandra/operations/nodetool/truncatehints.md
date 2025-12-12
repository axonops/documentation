# nodetool truncatehints

Removes all pending hints from this node.

---

## Synopsis

```bash
nodetool [connection_options] truncatehints [endpoint]
```

## Description

`nodetool truncatehints` deletes stored hints on this node. Hints are writes stored temporarily when a replica is unavailable, to be replayed when the replica recovers. Truncating hints discards these pending writes.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `endpoint` | Optional. Only truncate hints for this specific endpoint IP |

---

## Examples

### Truncate All Hints

```bash
nodetool truncatehints
```

### Truncate Hints for Specific Node

```bash
nodetool truncatehints 192.168.1.105
```

---

## When to Use

### Node Permanently Removed

When a node is removed and won't return:

```bash
# After removing node 192.168.1.105
nodetool truncatehints 192.168.1.105
```

Hints for removed nodes will never be delivered.

### Hint Backlog Too Large

When hints have accumulated excessively:

```bash
# Check hint status
nodetool tpstats | grep -i hint

# If backlog is causing issues
nodetool truncatehints
```

### Replace Node Scenario

When replacing a node (new node, same IP):

```bash
# Truncate hints for the old node
nodetool truncatehints 192.168.1.105

# Then add replacement node
```

---

## When NOT to Use

!!! danger "Data Loss Warning"
    Truncating hints means:

    - Pending writes will NOT be delivered
    - Data may become inconsistent
    - Only use when recovery isn't possible or desired

### Don't Use When

- Node is temporarily down and will recover
- You want to preserve data consistency
- During normal operations

---

## Understanding Hints

### What Hints Contain

When a write fails to reach a replica:

1. Coordinator stores the write as a "hint"
2. Hint includes: mutation data + target endpoint
3. When target recovers, hints are replayed

### Hint Location

Hints are stored in:

```
/var/lib/cassandra/hints/
```

### Check Pending Hints

```bash
# See hint delivery status
nodetool tpstats | grep -i hint

# List hint files
ls -la /var/lib/cassandra/hints/
```

---

## Impact of Truncation

| Scenario | Impact |
|----------|--------|
| Target node returns | Missed writes not recovered (run repair) |
| Target node replaced | Old hints not needed anyway |
| Target node removed | Hints would never deliver |

### Recovery After Truncation

If hints are truncated but data consistency is needed:

```bash
# Run repair to restore consistency
nodetool repair -pr keyspace
```

---

## Hint Configuration

Related settings in `cassandra.yaml`:

| Setting | Default | Description |
|---------|---------|-------------|
| `max_hint_window_in_ms` | 10800000 (3 hours) | Stop hinting after this duration |
| `hinted_handoff_enabled` | true | Whether hints are created |
| `hints_directory` | `$DATA/hints` | Hint storage location |

---

## Workflow: Decommission with Hints

```bash
# 1. Check if node has pending hints
nodetool tpstats | grep -i hint

# 2. If removing node permanently, truncate its hints
nodetool truncatehints <removed_node_ip>

# 3. Run repair to ensure consistency
nodetool repair -pr
```

---

## Monitoring Hints

### Before Truncation

```bash
# Check hint backlog
nodetool tpstats | grep HintedHandoff

# Check hint files size
du -sh /var/lib/cassandra/hints/
```

### After Truncation

```bash
# Verify hints removed
ls -la /var/lib/cassandra/hints/

# Confirm empty
nodetool tpstats | grep HintedHandoff
```

---

## Common Scenarios

### Scenario 1: Long-Down Node

Node has been down for days:

```bash
# Check hints accumulated
du -sh /var/lib/cassandra/hints/

# If node won't return, truncate
nodetool truncatehints 192.168.1.105

# Run repair on recovered node instead
```

### Scenario 2: Hint Disk Full

Hints filling disk:

```bash
# Emergency truncation
nodetool truncatehints

# Then run repairs
nodetool repair -pr
```

### Scenario 3: Node Replacement

Replacing dead node with new hardware:

```bash
# Truncate hints for old node
nodetool truncatehints 192.168.1.105

# Bootstrap new node with same tokens
# Run repair after bootstrap
```

---

## Best Practices

!!! tip "Hint Management"
    1. **Prefer repair over truncation** - Repair recovers data properly
    2. **Truncate only for removed nodes** - Hints to removed nodes are useless
    3. **Monitor hint growth** - Large hint backlogs indicate problems
    4. **Repair after truncation** - Restore consistency
    5. **Consider max_hint_window** - Tune to match your SLA

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [tpstats](tpstats.md) | Check hint delivery status |
| [repair](repair.md) | Restore consistency after truncation |
| [removenode](removenode.md) | Remove dead nodes (truncate hints after) |
| [decommission](decommission.md) | Graceful node removal |
