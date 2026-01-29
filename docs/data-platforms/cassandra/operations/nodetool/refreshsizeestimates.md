---
title: "nodetool refreshsizeestimates"
description: "Refresh size estimates for tables in Cassandra using nodetool refreshsizeestimates."
meta:
  - name: keywords
    content: "nodetool refreshsizeestimates, size estimates, table statistics, Cassandra"
---

# nodetool refreshsizeestimates

Refreshes the size estimates table.

---

## Synopsis

```bash
nodetool [connection_options] refreshsizeestimates
```

## Description

`nodetool refreshsizeestimates` updates the `system.size_estimates` table with current partition count and data size estimates for each table. These estimates are used by drivers for query planning and range scans.

---

## Examples

### Basic Usage

```bash
nodetool refreshsizeestimates
```

---

## When to Use

### After Major Data Changes

```bash
# After bulk load
nodetool refreshsizeestimates
```

### Before Capacity Planning

```bash
# Get fresh estimates for planning
nodetool refreshsizeestimates

# Query estimates
cqlsh -e "SELECT * FROM system.size_estimates LIMIT 10;"
```

### After Compaction

```bash
# Update estimates after major compaction
nodetool refreshsizeestimates
```

---

## Size Estimates Table

```sql
SELECT keyspace_name, table_name, range_start, range_end,
       mean_partition_size, partitions_count
FROM system.size_estimates;
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [tablestats](tablestats.md) | Detailed table statistics |
| [ring](ring.md) | Token range information |