---
title: "nodetool getmaxhintwindow"
description: "Display maximum hint window duration in Cassandra using nodetool getmaxhintwindow."
meta:
  - name: keywords
    content: "nodetool getmaxhintwindow, hint window, hinted handoff, Cassandra"
---

# nodetool getmaxhintwindow

Displays the maximum hint window in milliseconds.

---

## Synopsis

```bash
nodetool [connection_options] getmaxhintwindow
```

## Description

`nodetool getmaxhintwindow` displays the current maximum hint window configuration. The hint window defines how long Cassandra will store hints for an unavailable node. If a node is down longer than this window, hints are not stored and repair is needed to restore consistency.

---

## Examples

### Basic Usage

```bash
nodetool getmaxhintwindow
```

### Sample Output

```
Current max hint window: 10800000 ms
```

---

## Understanding the Hint Window

### Default Value

```yaml
# cassandra.yaml
max_hint_window_in_ms: 10800000  # 3 hours (default)
```

### How It Works

| Node Down Duration | Hint Behavior |
|--------------------|---------------|
| < hint window | Hints stored and delivered |
| > hint window | No hints stored, needs repair |

---

## Use Cases

### Verify Configuration

```bash
# Check current hint window
nodetool getmaxhintwindow

# Convert to hours: 10800000ms = 3 hours
```

### Capacity Planning

Understanding hint window helps plan for:
- Maximum outage duration covered by hints
- When repair becomes necessary
- Hint storage disk requirements

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [setmaxhintwindow](setmaxhintwindow.md) | Set hint window |
| [listpendinghints](listpendinghints.md) | View pending hints |
| [statushandoff](statushandoff.md) | Check handoff status |
