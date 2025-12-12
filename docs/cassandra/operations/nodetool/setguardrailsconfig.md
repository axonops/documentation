---
description: "Configure guardrails limits in Cassandra using nodetool setguardrailsconfig."
meta:
  - name: keywords
    content: "nodetool setguardrailsconfig, guardrails, Cassandra limits, configuration"
---

# nodetool setguardrailsconfig

Modifies guardrail configuration settings at runtime.

---

## Synopsis

```bash
nodetool [connection_options] setguardrailsconfig [options]
```

---

## Description

`nodetool setguardrailsconfig` modifies guardrail settings at runtime without requiring a node restart. Guardrails protect the cluster from potentially harmful operations by enforcing limits on schema, queries, and data sizes.

!!! warning "Non-Persistent Setting"

    Settings modified with this command are **not persisted** to configuration files. Changes will be lost on node restart. Update `cassandra.yaml` to make changes permanent.

---

## Common Options

### Table Guardrails

| Option | Description |
|--------|-------------|
| `--tables-warn-threshold <n>` | Warning threshold for table count |
| `--tables-fail-threshold <n>` | Failure threshold for table count |
| `--columns-per-table-warn-threshold <n>` | Warning for columns per table |
| `--columns-per-table-fail-threshold <n>` | Failure for columns per table |

### Query Guardrails

| Option | Description |
|--------|-------------|
| `--page-size-warn-threshold <n>` | Warning for large page sizes |
| `--page-size-fail-threshold <n>` | Rejection for excessive page sizes |
| `--partition-keys-in-select-warn-threshold <n>` | Warning for partition keys in SELECT |
| `--partition-keys-in-select-fail-threshold <n>` | Rejection for partition keys in SELECT |

### Collection Guardrails

| Option | Description |
|--------|-------------|
| `--collection-size-warn-threshold <bytes>` | Warning for collection sizes |
| `--collection-size-fail-threshold <bytes>` | Rejection for collection sizes |
| `--items-per-collection-warn-threshold <n>` | Warning for collection item count |
| `--items-per-collection-fail-threshold <n>` | Rejection for collection item count |

---

## Examples

### Increase Table Limit

```bash
nodetool setguardrailsconfig --tables-warn-threshold 200 --tables-fail-threshold 300
```

### Set Page Size Limits

```bash
nodetool setguardrailsconfig \
    --page-size-warn-threshold 5000 \
    --page-size-fail-threshold 10000
```

### Disable a Guardrail

```bash
# Set to -1 to disable
nodetool setguardrailsconfig --tables-fail-threshold -1
```

### Stricter Collection Limits

```bash
nodetool setguardrailsconfig \
    --collection-size-warn-threshold 32768 \
    --collection-size-fail-threshold 65536 \
    --items-per-collection-warn-threshold 50 \
    --items-per-collection-fail-threshold 100
```

### Enterprise Multi-Tenant Settings

```bash
# Stricter limits for shared clusters
nodetool setguardrailsconfig \
    --tables-warn-threshold 50 \
    --tables-fail-threshold 75 \
    --columns-per-table-warn-threshold 30 \
    --columns-per-table-fail-threshold 50
```

---

## When to Use

### Temporary Relaxation for Migration

```bash
# Temporarily allow more tables for migration
nodetool setguardrailsconfig --tables-fail-threshold 500

# Perform migration...

# Restore normal limits
nodetool setguardrailsconfig --tables-fail-threshold 150
```

### Emergency Unblock

```bash
# Unblock critical operation
nodetool setguardrailsconfig --page-size-fail-threshold 20000

# Perform operation...

# Restore limits
nodetool setguardrailsconfig --page-size-fail-threshold 10000
```

### Hardening New Clusters

```bash
# Apply stricter guardrails for new deployments
nodetool setguardrailsconfig \
    --tables-warn-threshold 50 \
    --tables-fail-threshold 100 \
    --columns-per-table-warn-threshold 25 \
    --columns-per-table-fail-threshold 50
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
    nodetool -h $host setguardrailsconfig \
        --tables-warn-threshold 100 \
        --tables-fail-threshold 150
done
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [getguardrailsconfig](getguardrailsconfig.md) | View current settings |
| [describecluster](describecluster.md) | Cluster configuration |
| [info](info.md) | Node information |
