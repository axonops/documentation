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
nodetool [connection_options] viewbuildstatus <keyspace> <view>
nodetool [connection_options] viewbuildstatus <keyspace.view>
```

## Description

`nodetool viewbuildstatus` shows the progress of a materialized view build across all nodes. When a materialized view is created, Cassandra must populate it with existing data, which can take time for large tables.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | **Required.** The keyspace containing the view |
| `view` | **Required.** The materialized view name to check |

The view can be specified as two separate arguments (`keyspace view`) or as a single dotted notation (`keyspace.view`).

---

## Examples

### Check Specific View (two arguments)

```bash
nodetool viewbuildstatus my_keyspace my_view
```

### Check Specific View (dotted notation)

```bash
nodetool viewbuildstatus my_keyspace.my_view
```

### Sample Output (Build Complete)

When the view build has finished successfully on all nodes:

```
my_keyspace.my_view has finished building
```

### Sample Output (Build In Progress or Failed)

When any node has not completed the build, the command outputs a status message and a table with per-host status, then exits with an error:

```
my_keyspace.my_view has not finished building; node status is below.
Host            Info
192.168.1.101   SUCCESS
192.168.1.102   BUILDING
192.168.1.103   SUCCESS
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
# Check if view build failed (output goes to stderr on failure)
nodetool viewbuildstatus my_keyspace my_view 2>&1 | grep FAILED
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