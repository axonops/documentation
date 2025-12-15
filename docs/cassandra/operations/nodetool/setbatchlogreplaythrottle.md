---
title: "nodetool setbatchlogreplaythrottle"
description: "Set batch log replay throttle in Cassandra using nodetool setbatchlogreplaythrottle."
meta:
  - name: keywords
    content: "nodetool setbatchlogreplaythrottle, batch log, replay throttle, Cassandra"
---

# nodetool setbatchlogreplaythrottle

Sets the batchlog replay throttle in KB/s.

---

## Synopsis

```bash
nodetool [connection_options] setbatchlogreplaythrottle <throttle_in_kb>
```

## Description

`nodetool setbatchlogreplaythrottle` modifies the throttle rate for batchlog replay operations at runtime.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `throttle_in_kb` | Replay throttle in KB/s |

---

## Examples

### Set Throttle

```bash
nodetool setbatchlogreplaythrottle 2048
```

### Increase for Faster Replay

```bash
nodetool setbatchlogreplaythrottle 4096
```

---

## When to Use

### Speed Up Batch Replay

```bash
# Increase for faster catchup
nodetool setbatchlogreplaythrottle 4096
nodetool replaybatchlog
```

### Reduce Impact

```bash
# During high load
nodetool setbatchlogreplaythrottle 512
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [getbatchlogreplaythrottle](getbatchlogreplaythrottle.md) | View current throttle |
| [replaybatchlog](replaybatchlog.md) | Force replay |
