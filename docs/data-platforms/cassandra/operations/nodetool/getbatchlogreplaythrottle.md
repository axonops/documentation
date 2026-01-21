---
title: "nodetool getbatchlogreplaythrottle"
description: "Display batch log replay throttle setting in Cassandra using nodetool getbatchlogreplaythrottle."
meta:
  - name: keywords
    content: "nodetool getbatchlogreplaythrottle, batch log, replay throttle, Cassandra"
search:
  boost: 3
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

```yaml
# cassandra.yaml
batchlog_replay_throttle_in_kb: 1024
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [setbatchlogreplaythrottle](setbatchlogreplaythrottle.md) | Modify throttle |
| [replaybatchlog](replaybatchlog.md) | Force replay |
