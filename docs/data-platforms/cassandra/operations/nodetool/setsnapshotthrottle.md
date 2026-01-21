---
title: "nodetool setsnapshotthrottle"
description: "Set snapshot throttle in Cassandra using nodetool setsnapshotthrottle command."
meta:
  - name: keywords
    content: "nodetool setsnapshotthrottle, snapshot throttle, backup speed, Cassandra"
search:
  boost: 3
---

# nodetool setsnapshotthrottle

Sets the snapshot link creation throttle.

---

## Synopsis

```bash
nodetool [connection_options] setsnapshotthrottle <throttle_in_mb>
```

## Description

`nodetool setsnapshotthrottle` sets the rate limit for snapshot hard link creation in MB/s.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `throttle_in_mb` | Throttle rate in MB/s |

---

## Examples

### Set Throttle

```bash
nodetool setsnapshotthrottle 100
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [getsnapshotthrottle](getsnapshotthrottle.md) | View current throttle |
| [snapshot](snapshot.md) | Create snapshots |
