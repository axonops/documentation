---
title: "nodetool getsnapshotthrottle"
description: "Display snapshot throttle setting in Cassandra using nodetool getsnapshotthrottle."
meta:
  - name: keywords
    content: "nodetool getsnapshotthrottle, snapshot throttle, backup speed, Cassandra"
---

# nodetool getsnapshotthrottle

Displays the snapshot link creation throttle.

---

## Synopsis

```bash
nodetool [connection_options] getsnapshotthrottle
```

## Description

`nodetool getsnapshotthrottle` shows the current throttle rate for snapshot hard link creation in **links per second**. This limits how fast hard links are created during snapshot operations.

---

## Output

When throttling is enabled:

```
Snapshot throttle: 1000 links/second
```

When throttling is disabled (value is 0):

```
Snapshot throttle is disabled
```

---

## Examples

### Basic Usage

```bash
nodetool getsnapshotthrottle
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [setsnapshotthrottle](setsnapshotthrottle.md) | Modify throttle |
| [snapshot](snapshot.md) | Create snapshots |