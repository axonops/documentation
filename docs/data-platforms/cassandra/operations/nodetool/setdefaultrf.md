---
title: "nodetool setdefaultrf"
description: "Set default replication factor for auto-created keyspaces using nodetool setdefaultrf."
meta:
  - name: keywords
    content: "nodetool setdefaultrf, replication factor, default RF, Cassandra"
---

# nodetool setdefaultrf

!!! info "Cassandra 4.1+"
    This command is available in Cassandra 4.1 and later.

Sets the default replication factor used by NetworkTopologyStrategy auto-expansion.

---

## Synopsis

```bash
nodetool [connection_options] setdefaultrf <replication_factor>
```

## Description

`nodetool setdefaultrf` configures the cluster-wide default replication factor that is applied when creating or altering keyspaces using NetworkTopologyStrategy with the `replication_factor` shorthand instead of explicit datacenter mappings.

### How Auto-Expansion Works

When a keyspace is created using `NetworkTopologyStrategy` with the generic `replication_factor` parameter, Cassandra automatically expands this to all known datacenters:

```sql
-- Using replication_factor shorthand
CREATE KEYSPACE my_keyspace WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'replication_factor': 3
};

-- Cassandra expands this to explicit datacenter mappings:
-- 'dc1': 3, 'dc2': 3, 'dc3': 3 (for all datacenters in the cluster)
```

The value set by `setdefaultrf` becomes the default when `replication_factor` is not explicitly specified in the CQL statement.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `replication_factor` | The default replication factor to apply. Must be a positive integer. |

---

## When to Use

### Standardizing Replication Across Teams

In multi-tenant or multi-team environments, setting a cluster-wide default ensures new keyspaces follow organizational standards without requiring explicit specification:

```bash
# Set production standard of RF=3
nodetool setdefaultrf 3
```

This prevents accidental creation of under-replicated keyspaces when developers omit explicit replication settings.

### Preparing for Cluster Expansion

Before adding new datacenters, set the default RF to ensure auto-expansion applies the correct replication factor:

```bash
# Before adding dc3 to the cluster
nodetool setdefaultrf 3

# When dc3 joins, keyspaces using auto-expansion will include dc3 with RF=3
```

### Automation and Infrastructure-as-Code

When using automation tools that create keyspaces, `setdefaultrf` provides a safety net:

```bash
# Ensure minimum replication regardless of script defaults
nodetool setdefaultrf 3
```

---

## Behavior Details

### Node-Level Setting

This setting is **per-node** and is not persisted across restarts. Each node in the cluster maintains its own default RF value. For consistent behavior:

1. Run the command on all nodes
2. Or configure `default_keyspace_rf` in `cassandra.yaml` for persistence

### Does Not Affect Existing Keyspaces

Changing the default RF does not alter existing keyspaces. It only affects:

- New keyspaces created with `replication_factor` shorthand
- `ALTER KEYSPACE` commands using `replication_factor` shorthand

### Interaction with Explicit Settings

Explicit datacenter settings always override the default:

```sql
-- DC1 gets RF=5, DC2 uses the default from setdefaultrf (e.g., 3)
CREATE KEYSPACE mixed_rf WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'replication_factor': 3,
    'dc1': 5
};
```

---

## Examples

### Set Default RF to Production Standard

```bash
nodetool setdefaultrf 3
```

### Verify the Setting

```bash
nodetool getdefaultrf
```

**Output:**

```
3
```

### Applying Across All Nodes

```bash
# Run on each node or use parallel execution
for host in node1 node2 node3; do
    ssh "$host" "nodetool setdefaultrf 3"
done
```

---

## Best Practices

!!! tip "Recommendations"

    1. **Set on all nodes** - The setting is per-node; ensure consistency across the cluster
    2. **Use with cassandra.yaml** - For persistence, also configure `default_keyspace_rf` in cassandra.yaml
    3. **Match node count** - The default RF should not exceed the number of nodes in the smallest datacenter
    4. **Production standard: RF=3** - Provides fault tolerance for one node failure while maintaining QUORUM availability

!!! warning "Limitations"

    - Does not affect keyspaces created with explicit datacenter mappings
    - Does not retroactively change existing keyspaces
    - Resets to default (1) on node restart unless configured in cassandra.yaml

---

## Related Configuration

The persistent equivalent in `cassandra.yaml`:

```yaml
# Default replication factor for auto-expanding keyspaces
default_keyspace_rf: 3
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [getdefaultrf](getdefaultrf.md) | View current default RF |
| [describecluster](describecluster.md) | View cluster topology and datacenter information |
| [status](status.md) | Check node count per datacenter |

## Related Documentation

- [Keyspace DDL](../../cql/ddl/keyspace.md) - Creating and altering keyspaces
- [Replication](../../architecture/distributed-data/replication.md) - Replication concepts and strategies
