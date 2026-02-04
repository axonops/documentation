---
title: "nodetool setsnapshotthrottle"
description: "Set snapshot throttle in Cassandra using nodetool setsnapshotthrottle command."
meta:
  - name: keywords
    content: "nodetool setsnapshotthrottle, snapshot throttle, backup speed, Cassandra"
---

# nodetool setsnapshotthrottle

Sets the snapshot link creation throttle.

---

## Synopsis

```bash
nodetool [connection_options] setsnapshotthrottle <links_per_second>
```
See [connection options](index.md#connection-options) for connection options.

## Description

`nodetool setsnapshotthrottle` sets the rate limit for snapshot hard link creation. The value specifies the maximum number of hard links that can be created per second during snapshot operations.

!!! info "Unit Clarification"
    The throttle is measured in **hard links per second**, not MB/s. Each SSTable component file requires a hard link, so the effective speed depends on file count rather than data size.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `links_per_second` | Maximum hard links per second. Set to 0 to disable throttling (unlimited). |

---

## Examples

### Set Throttle

```bash
# Allow 100 hard links per second
nodetool setsnapshotthrottle 100
```

### Disable Throttling

```bash
# Set to 0 for unlimited (no throttle)
nodetool setsnapshotthrottle 0
```

### Reduce for Lower Impact

```bash
# Slower snapshot creation with less I/O impact
nodetool setsnapshotthrottle 50
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [getsnapshotthrottle](getsnapshotthrottle.md) | View current throttle |
| [snapshot](snapshot.md) | Create snapshots |