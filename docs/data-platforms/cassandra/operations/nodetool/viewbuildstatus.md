---
title: "nodetool viewbuildstatus"
description: "Display materialized view build progress using nodetool viewbuildstatus command."
meta:
  - name: keywords
    content: "nodetool viewbuildstatus, view build status, materialized view, Cassandra"
---

# nodetool viewbuildstatus

Displays the build status of materialized views.

---

## Synopsis

```bash
nodetool [connection_options] viewbuildstatus [keyspace.view]
```

## Description

`nodetool viewbuildstatus` shows the progress of materialized view builds. When a materialized view is created, Cassandra must populate it with existing data, which can take time for large tables.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace.view` | Optional: specific view to check |

---

## Examples

### Check All Views

```bash
nodetool viewbuildstatus
```

### Check Specific View

```bash
nodetool viewbuildstatus my_keyspace.my_view
```

### Sample Output

```
Keyspace     View          Host          Status
my_keyspace  my_view       192.168.1.101 SUCCESS
my_keyspace  my_view       192.168.1.102 BUILDING
my_keyspace  my_view       192.168.1.103 SUCCESS
```

---

## Status Values

| Status | Meaning |
|--------|---------|
| SUCCESS | Build complete |
| BUILDING | Build in progress |
| STARTED | Build initiated |
| FAILED | Build failed |

---

## When to Use

### After Creating View

```bash
# Create view
cqlsh -e "CREATE MATERIALIZED VIEW..."

# Monitor build progress
watch nodetool viewbuildstatus my_keyspace.my_view
```

### Troubleshoot View Issues

```bash
# Check if view build failed
nodetool viewbuildstatus | grep FAILED
```

---

## Best Practices

!!! tip "Guidelines"

    1. **Monitor large builds** - View builds can take significant time
    2. **Check all nodes** - Build status varies per node
    3. **Investigate failures** - Check logs if build fails

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [compactionstats](compactionstats.md) | View build shows in compaction |
| [tablestats](tablestats.md) | View table statistics |
