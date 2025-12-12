---
description: "Run Swiss Java Knife diagnostics on Cassandra JVM using nodetool sjk command."
meta:
  - name: keywords
    content: "nodetool sjk, Swiss Java Knife, JVM diagnostics, Cassandra"
---

# nodetool sjk

Invokes the Swiss Java Knife diagnostic tool.

---

## Synopsis

```bash
nodetool [connection_options] sjk <sjk_arguments>
```

## Description

`nodetool sjk` provides access to Swiss Java Knife (SJK) diagnostic commands for JVM troubleshooting. SJK offers various tools for analyzing thread dumps, heap usage, and other JVM internals.

---

## Examples

### Thread Dump

```bash
nodetool sjk ttop
```

### Stack Trace Analysis

```bash
nodetool sjk stcap
```

### Help

```bash
nodetool sjk --help
```

---

## Common SJK Commands

| Command | Description |
|---------|-------------|
| `ttop` | Thread CPU usage |
| `stcap` | Stack trace capture |
| `stcpy` | Stack trace copy |
| `hh` | Heap histogram |
| `gc` | GC statistics |

---

## When to Use

### CPU Analysis

```bash
# Find threads using most CPU
nodetool sjk ttop -n 10
```

### Thread Analysis

```bash
# Capture stack traces
nodetool sjk stcap -o stacks.txt
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [tpstats](tpstats.md) | Thread pool statistics |
| [gcstats](gcstats.md) | GC statistics |
