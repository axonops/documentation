# nodetool setmaxhintwindow

Sets the maximum hint window in milliseconds.

---

## Synopsis

```bash
nodetool [connection_options] setmaxhintwindow <hint_window_in_ms>
```

## Description

`nodetool setmaxhintwindow` configures the maximum duration for which hints will be stored for an unavailable node. Hints for nodes down longer than this window are not stored.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `hint_window_in_ms` | Maximum hint window in milliseconds |

---

## Examples

### Set to 6 Hours

```bash
nodetool setmaxhintwindow 21600000
```

### Set to 1 Hour

```bash
nodetool setmaxhintwindow 3600000
```

### Verify Change

```bash
nodetool setmaxhintwindow 21600000
nodetool getmaxhintwindow
```

---

## Common Values

| Duration | Milliseconds |
|----------|--------------|
| 1 hour | 3600000 |
| 3 hours (default) | 10800000 |
| 6 hours | 21600000 |
| 12 hours | 43200000 |
| 24 hours | 86400000 |

---

## When to Use

### Longer Expected Outages

```bash
# Increase for maintenance windows
nodetool setmaxhintwindow 43200000  # 12 hours
```

### Reduce Disk Usage

```bash
# Shorter window = less hint storage
nodetool setmaxhintwindow 3600000  # 1 hour
```

---

## Best Practices

!!! tip "Hint Window Guidelines"

    1. **Balance** - Longer window = more disk, better coverage
    2. **Consider SLAs** - Set based on recovery expectations
    3. **Cluster-wide** - Apply same setting on all nodes
    4. **Persist in config** - Update cassandra.yaml for permanence

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [getmaxhintwindow](getmaxhintwindow.md) | View current setting |
| [listpendinghints](listpendinghints.md) | View pending hints |
