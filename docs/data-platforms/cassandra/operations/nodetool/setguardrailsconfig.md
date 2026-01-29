---
title: "nodetool setguardrailsconfig"
description: "Configure guardrails limits in Cassandra using nodetool setguardrailsconfig."
meta:
  - name: keywords
    content: "nodetool setguardrailsconfig, guardrails, Cassandra limits, configuration"
---

# nodetool setguardrailsconfig

!!! info "Cassandra 5.0+"
    This command is available in Cassandra 5.0 and later.

Modifies guardrail configuration settings at runtime.

---

## Synopsis

```bash
nodetool [connection_options] setguardrailsconfig <guardrail_setter> <value(s)>
```

---

## Description

`nodetool setguardrailsconfig` modifies guardrail settings at runtime without requiring a node restart. Guardrails protect the cluster from potentially harmful operations by enforcing limits on schema, queries, and data sizes.

The command takes a guardrail setter name followed by one or more values, depending on the guardrail type.

!!! warning "Non-Persistent Setting"

    Settings modified with this command are **not persisted** to configuration files. Changes will be lost on node restart. Update `cassandra.yaml` to make changes permanent.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `guardrail_setter` | Name of the guardrail setter (e.g., `tables`, `page_size`) |
| `value(s)` | One or more values depending on the guardrail type |

### Value Semantics

Different guardrail types require different argument patterns:

| Guardrail Type | Arguments | Reset Value |
|----------------|-----------|-------------|
| **Threshold guardrails** (e.g., `tables`, `page_size`) | `<fail_threshold> <warn_threshold>` | `-1` to disable |
| **Flag guardrails** (e.g., `allow_filtering`) | `true` or `false` | N/A |
| **String/list thresholds** | Value as string | `null` or `[]` to reset |

!!! info "Argument Order"
    For threshold guardrails, specify **fail threshold first, then warn threshold**.

---

## Common Guardrail Setters

### Table Guardrails

| Setter | Arguments | Description |
|--------|-----------|-------------|
| `tables` | `<fail> <warn>` | Table count thresholds |
| `columns_per_table` | `<fail> <warn>` | Columns per table thresholds |

### Query Guardrails

| Setter | Arguments | Description |
|--------|-----------|-------------|
| `page_size` | `<fail> <warn>` | Page size thresholds |
| `partition_keys_in_select` | `<fail> <warn>` | Partition keys in SELECT thresholds |

### Collection Guardrails

| Setter | Arguments | Description |
|--------|-----------|-------------|
| `collection_size` | `<fail> <warn>` | Collection size thresholds (in bytes) |
| `items_per_collection` | `<fail> <warn>` | Collection item count thresholds |

---

## Examples

### Increase Table Limit

```bash
# Set fail=300, warn=200
nodetool setguardrailsconfig tables 300 200
```

### Set Page Size Limits

```bash
# Set fail=10000, warn=5000
nodetool setguardrailsconfig page_size 10000 5000
```

### Disable a Guardrail

```bash
# Set to -1 to disable (both fail and warn)
nodetool setguardrailsconfig tables -1 -1
```

### Stricter Collection Limits

```bash
# Collection size: fail=65536, warn=32768
nodetool setguardrailsconfig collection_size 65536 32768

# Items per collection: fail=100, warn=50
nodetool setguardrailsconfig items_per_collection 100 50
```

### Enterprise Multi-Tenant Settings

```bash
# Stricter limits for shared clusters
nodetool setguardrailsconfig tables 75 50
nodetool setguardrailsconfig columns_per_table 50 30
```

---

## When to Use

### Temporary Relaxation for Migration

```bash
# Temporarily allow more tables for migration (fail=500, warn=400)
nodetool setguardrailsconfig tables 500 400

# Perform migration...

# Restore normal limits (fail=150, warn=100)
nodetool setguardrailsconfig tables 150 100
```

### Emergency Unblock

```bash
# Unblock critical operation (fail=20000, warn=15000)
nodetool setguardrailsconfig page_size 20000 15000

# Perform operation...

# Restore limits (fail=10000, warn=5000)
nodetool setguardrailsconfig page_size 10000 5000
```

### Hardening New Clusters

```bash
# Apply stricter guardrails for new deployments
nodetool setguardrailsconfig tables 100 50
nodetool setguardrailsconfig columns_per_table 50 25
```

---

## Best Practices

!!! tip "Guardrail Management"

    1. **Prefer warnings first** - Set warn thresholds to catch issues before hitting fail limits
    2. **Test changes** - Verify guardrail changes in non-production first
    3. **Document exceptions** - Record why guardrails were modified
    4. **Cluster-wide consistency** - Apply same settings across all nodes

!!! warning "Important Considerations"

    - Relaxing guardrails can impact cluster stability
    - Changes affect only the target node
    - Lost on restart unless updated in `cassandra.yaml`
    - Some limits protect against resource exhaustion

!!! danger "Risks of Disabling Guardrails"

    Disabling guardrails (setting to -1) removes protection against:

    - Schema bloat (too many tables/columns)
    - Memory exhaustion (large collections/partitions)
    - Query performance issues (unbounded queries)

    Only disable with careful consideration of risks.

---

## Configuration Reference

For persistent configuration in `cassandra.yaml`:

```yaml
guardrails:
    # Table limits
    tables_warn_threshold: 100
    tables_fail_threshold: 150
    columns_per_table_warn_threshold: 50
    columns_per_table_fail_threshold: 100

    # Query limits
    page_size_warn_threshold: 5000
    page_size_fail_threshold: 10000
    partition_keys_in_select_warn_threshold: 20
    partition_keys_in_select_fail_threshold: 100

    # Collection limits
    collection_size_warn_threshold_in_kb: 64
    collection_size_fail_threshold_in_kb: -1
    items_per_collection_warn_threshold: 100
    items_per_collection_fail_threshold: -1
```

---

## Verification

After making changes:

```bash
# Verify new settings
nodetool getguardrailsconfig

# Test with a query that was previously blocked
# Monitor logs for warnings
```

---

## Cluster-Wide Application

To apply guardrails across the cluster:

```bash
# Apply to all nodes
for host in node1 node2 node3; do
    ssh "$host" 'nodetool setguardrailsconfig tables 150 100'
done
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [getguardrailsconfig](getguardrailsconfig.md) | View current settings |
| [describecluster](describecluster.md) | Cluster configuration |
| [info](info.md) | Node information |