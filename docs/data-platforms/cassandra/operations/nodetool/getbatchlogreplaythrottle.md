---
title: "nodetool getbatchlogreplaythrottle"
description: "Display batch log replay throttle setting in Cassandra using nodetool getbatchlogreplaythrottle."
meta:
  - name: keywords
    content: "nodetool getbatchlogreplaythrottle, batch log, replay throttle, Cassandra"
---

# nodetool getbatchlogreplaythrottle

Displays the batchlog replay throttle in KB/s.

---

## Synopsis

```bash
nodetool [connection_options] getbatchlogreplaythrottle
```

## Description

`nodetool getbatchlogreplaythrottle` shows the current throttle rate for batchlog replay operations. This controls how fast pending batches are replayed.

!!! info "Per-Node Throttle"
    The displayed throttle is the per-node rate. The actual throttle per endpoint is calculated as the total throttle divided by the number of nodes in the cluster.

---

## Examples

### Basic Usage

```bash
nodetool getbatchlogreplaythrottle
```

### Sample Output

```
Batchlog replay throttle: 1024 KB/s
```

---

## Configuration

The cassandra.yaml parameter name varies by version:

| Cassandra Version | Parameter Name | Example |
|-------------------|----------------|---------|
| Pre-4.1 | `batchlog_replay_throttle_in_kb` | `1024` |
| 4.1+ | `batchlog_replay_throttle` | `1024KiB` |

```yaml
# cassandra.yaml (4.1+)
batchlog_replay_throttle: 1024KiB

# cassandra.yaml (Pre-4.1)
# batchlog_replay_throttle_in_kb: 1024
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [setbatchlogreplaythrottle](setbatchlogreplaythrottle.md) | Modify throttle |
| [replaybatchlog](replaybatchlog.md) | Force replay |
