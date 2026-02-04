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
See [connection options](index.md#connection-options) for connection options.

## Description

`nodetool setbatchlogreplaythrottle` modifies the throttle rate for batchlog replay operations at runtime.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `batchlog_replay_throttle` | Replay throttle in KiB/s. Set to 0 to disable throttling. |

!!! info "Throttle Behavior"
    - Setting the value to **0 disables throttling** entirely
    - The effective throttle is **proportionally reduced based on cluster size** to prevent overwhelming recovered nodes during replay

!!! note "cassandra.yaml Parameter"
    The corresponding cassandra.yaml parameter changed in 4.1:

    | Cassandra Version | Parameter Name | Example |
    |-------------------|----------------|---------|
    | Pre-4.1 | `batchlog_replay_throttle_in_kb` | `1024` |
    | 4.1+ | `batchlog_replay_throttle` | `1024KiB` |

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

### Disable Throttling

```bash
# Remove throttle limit (use with caution)
nodetool setbatchlogreplaythrottle 0
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [getbatchlogreplaythrottle](getbatchlogreplaythrottle.md) | View current throttle |
| [replaybatchlog](replaybatchlog.md) | Force replay |