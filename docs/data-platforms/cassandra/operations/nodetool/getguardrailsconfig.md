---
title: "nodetool getguardrailsconfig"
description: "Display guardrails configuration in Cassandra using nodetool getguardrailsconfig."
meta:
  - name: keywords
    content: "nodetool getguardrailsconfig, guardrails, Cassandra limits, configuration"
---

# nodetool getguardrailsconfig

!!! info "Cassandra 5.0+"
    This command is available in Cassandra 5.0 and later.

Displays the current guardrails configuration.

---

## Synopsis

```bash
nodetool [connection_options] getguardrailsconfig
```

---

## Description

`nodetool getguardrailsconfig` displays the current guardrails configuration for the node. Guardrails are protective limits that prevent potentially harmful operations in Cassandra, such as creating too many tables, using dangerous query patterns, or exceeding safe data sizes.

Guardrails help maintain cluster stability by enforcing best practices and preventing operations that could lead to performance degradation or outages.

---

## Output Categories

### Table Guardrails

| Setting | Description |
|---------|-------------|
| `tables_warn_threshold` | Warning when table count exceeds this |
| `tables_fail_threshold` | Reject operations when table count exceeds this |
| `columns_per_table_warn_threshold` | Warning for columns per table |
| `columns_per_table_fail_threshold` | Rejection for columns per table |

### Query Guardrails

| Setting | Description |
|---------|-------------|
| `page_size_warn_threshold` | Warning for large page sizes |
| `page_size_fail_threshold` | Rejection for excessive page sizes |
| `in_select_cartesian_product_warn_threshold` | Warning for IN clause combinations |
| `in_select_cartesian_product_fail_threshold` | Rejection for IN clause combinations |

### Collection Guardrails

| Setting | Description |
|---------|-------------|
| `collection_size_warn_threshold` | Warning for large collections |
| `collection_size_fail_threshold` | Rejection for excessive collections |
| `items_per_collection_warn_threshold` | Warning for collection item count |
| `items_per_collection_fail_threshold` | Rejection for collection item count |

### Partition Guardrails

| Setting | Description |
|---------|-------------|
| `partition_keys_in_select_warn_threshold` | Warning for partition keys in SELECT |
| `partition_keys_in_select_fail_threshold` | Rejection for partition keys in SELECT |

---

## Examples

### Basic Usage

```bash
nodetool getguardrailsconfig
```

**Sample output:**

```
Guardrails Configuration:
  Tables:
    Warn Threshold: 100
    Fail Threshold: 150
  Columns Per Table:
    Warn Threshold: 50
    Fail Threshold: 100
  Page Size:
    Warn Threshold: 5000
    Fail Threshold: 10000
  Collection Size:
    Warn Threshold: 65536
    Fail Threshold: -1 (disabled)
  ...
```

---

## When to Use

### Review Cluster Protection Settings

```bash
# Check current guardrail configuration
nodetool getguardrailsconfig
```

Review guardrails when:

- Planning schema changes
- Debugging query rejections
- Auditing cluster configuration
- Onboarding new development teams

### Before Schema Operations

```bash
# Check limits before creating tables
nodetool getguardrailsconfig | grep -i table
```

Verify guardrail limits before operations that might be affected.

### Troubleshooting Query Failures

```bash
# Check if queries are hitting guardrails
nodetool getguardrailsconfig
```

When queries fail with guardrail errors, check current thresholds to understand the limits.

---

## Guardrail Types

### Warn vs Fail Thresholds

- **Warn threshold**: Logs a warning but allows the operation
- **Fail threshold**: Rejects the operation with an error

A value of `-1` typically indicates the guardrail is disabled.

### Categories

**Schema Guardrails:**

- Number of tables per keyspace
- Columns per table
- Secondary indexes per table
- Materialized views per table

**Query Guardrails:**

- Page size limits
- IN clause restrictions
- ALLOW FILTERING controls
- Partition scan limits

**Data Guardrails:**

- Collection sizes
- Partition sizes
- Column value sizes
- TTL settings

---

## Best Practices

!!! tip "Guardrail Strategy"

    1. **Use warn thresholds** - Enable warnings before hard failures to catch issues early
    2. **Document limits** - Ensure developers understand guardrail boundaries
    3. **Monitor warnings** - Set up alerts for guardrail warnings
    4. **Review periodically** - Adjust thresholds based on operational experience

!!! info "When to Adjust Guardrails"

    Consider modifying guardrails when:

    - Legitimate use cases exceed defaults
    - Stricter controls are needed for multi-tenant environments
    - Specific applications have validated requirements

!!! warning "Guardrail Considerations"

    - Guardrails exist to protect cluster stability
    - Relaxing limits should be done cautiously
    - Test thoroughly before changing production guardrails
    - Some guardrails affect existing data operations, not just new writes

---

## Related Configuration

Guardrails can also be configured in `cassandra.yaml`:

```yaml
guardrails:
    tables_warn_threshold: 100
    tables_fail_threshold: 150
    columns_per_table_warn_threshold: 50
    columns_per_table_fail_threshold: 100
    # ... additional settings
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [setguardrailsconfig](setguardrailsconfig.md) | Modify guardrail settings |
| [describecluster](describecluster.md) | Cluster configuration overview |
| [info](info.md) | Node information |
