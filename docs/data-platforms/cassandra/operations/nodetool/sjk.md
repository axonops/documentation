---
title: "nodetool sjk"
description: "Run Swiss Java Knife diagnostics on Cassandra JVM using nodetool sjk command."
meta:
  - name: keywords
    content: "nodetool sjk, Swiss Java Knife, JVM diagnostics, Cassandra, thread dump, heap histogram, CPU profiling"
---

# nodetool sjk

Invokes the Swiss Java Knife (SJK) diagnostic tool for JVM troubleshooting and performance analysis.

---

## Synopsis

```bash
nodetool [connection_options] sjk [--] <args>
```

See [connection options](index.md#connection-options) for connection options.

**Arguments:**

| Argument | Description |
|----------|-------------|
| `--` | Optional separator to distinguish nodetool options from SJK arguments |
| `<args>` | Arguments passed verbatim to Swiss Java Knife |

The `--` separator is useful when SJK arguments might be mistaken for nodetool options.

## Description

`nodetool sjk` provides access to [Swiss Java Knife (SJK)](https://github.com/aragozin/jvm-tools), a collection of command-line tools for JVM diagnostics, monitoring, and profiling.

### Background

SJK was integrated into Cassandra nodetool via [CASSANDRA-12197](https://issues.apache.org/jira/browse/CASSANDRA-12197). This integration allows operators to perform JVM diagnostics directly through nodetool without needing to install separate tools or manage additional JAR files on Cassandra nodes.

### How It Works

When `nodetool sjk` is invoked:

1. Nodetool establishes a JMX connection to the target Cassandra node using standard nodetool connection options (`-h`, `-p`, `-u`, `-pw`)
2. The SJK arguments are passed to the embedded SJK library
3. SJK commands that require JVM access use the JMX connection and process ID provided by nodetool
4. Results are returned to the console

!!! note "Connection Handling"
    Cassandra's nodetool integration manages the JMX connection. SJK's own connection options (`--pid`, `--socket`, etc.) are not available through `nodetool sjk`. The connection is always established through nodetool's standard mechanism.

---

## Getting Help

To see available SJK commands for the installed Cassandra version:

```bash
# List all available commands
nodetool sjk --commands

# Get general help
nodetool sjk --help

# Get help for a specific command
nodetool sjk <command> --help
```

!!! tip "Version-Specific Commands"
    The available commands and their options depend on the SJK version bundled with the Cassandra distribution. Always use `nodetool sjk --commands` to see what is available in the current environment.

---

## Common Commands

The following commands are typically available. Run `nodetool sjk --commands` to confirm availability and `nodetool sjk <command> --help` for exact option names.

### ttop - Thread CPU Usage

Displays JVM threads sorted by CPU usage, similar to the Linux `top` command but for threads within a single JVM process.

```bash
# Show thread CPU usage
nodetool sjk ttop

# Show top N threads (check --help for exact option name)
nodetool sjk ttop --help
```

**Use cases:**

- Identify threads consuming excessive CPU
- Detect runaway compaction or streaming threads
- Find threads blocked in contention
- Monitor allocation rates to diagnose GC pressure

---

### hh - Heap Histogram

Prints a histogram of objects on the heap, similar to `jmap -histo`. This is useful for identifying memory leaks or unexpected object retention.

!!! warning "Stop-the-World Pause"
    The heap histogram operation may cause a stop-the-world pause. Some options require a full garbage collection. Use with caution on production systems.

```bash
# Show heap histogram
nodetool sjk hh

# Show top N classes with live objects only
nodetool sjk -- hh --top-number 20 --live

# Get help for available options
nodetool sjk hh --help
```

**Use cases:**

- Identify classes with unexpectedly high instance counts
- Detect memory leaks (growing instance counts over time)
- Analyze object retention patterns
- Compare live vs dead objects to understand allocation patterns

---

### gc - Garbage Collection Tracker

Reports garbage collection statistics in real time.

```bash
# Monitor GC activity
nodetool sjk gc

# Get available options
nodetool sjk gc --help
```

**Use cases:**

- Monitor GC behavior under load
- Detect long GC pauses affecting latency
- Verify GC tuning changes
- Correlate GC activity with application performance

---

### stcap - Stack Trace Capture

Captures thread stack traces at regular intervals for profiling and analysis.

```bash
# Capture stack traces (check --help for options)
nodetool sjk stcap --help

# Example: capture to file for specified duration
nodetool sjk -- stcap --output /tmp/stacks.std --timeout 30000
```

**Use cases:**

- Profile CPU-intensive operations
- Identify hot code paths
- Analyze thread behavior over time
- Create data for flame graph generation

---

### ssa - Stack Trace Analyzer

Analyzes stack trace files created by `stcap`.

```bash
# Analyze captured file
nodetool sjk -- ssa --file /tmp/stacks.std --help

# Generate histogram
nodetool sjk -- ssa --file /tmp/stacks.std --histo
```

---

### mx - MBean Operations

Queries and invokes JMX MBean operations.

```bash
# Get help for MBean operations
nodetool sjk mx --help

# Example: list MBean info
nodetool sjk -- mx --bean "java.lang:type=Memory" --info
```

---

## Practical Examples

### Diagnosing High CPU Usage

```bash
# Step 1: Identify which threads are using CPU
nodetool sjk ttop

# Step 2: If specific threads are high, capture stack traces
nodetool sjk -- stcap --output /tmp/high-cpu.std --timeout 60000

# Step 3: Analyze the captured data
nodetool sjk -- ssa --file /tmp/high-cpu.std --histo
```

### Investigating Memory Issues

```bash
# Step 1: Get heap histogram
nodetool sjk -- hh --top-number 30

# Step 2: Check for live objects only (triggers GC)
nodetool sjk -- hh --top-number 30 --live

# Step 3: Monitor GC behavior
nodetool sjk gc
```

### Collecting Diagnostic Data

```bash
# Create diagnostic directory
mkdir -p /tmp/cassandra-diag

# Capture thread CPU usage
nodetool sjk ttop > /tmp/cassandra-diag/ttop.txt

# Capture heap histogram
nodetool sjk -- hh --top-number 50 > /tmp/cassandra-diag/heap.txt

# Capture stack traces for 60 seconds
nodetool sjk -- stcap --output /tmp/cassandra-diag/stacks.std --timeout 60000
```

---

## Common Cassandra Thread Patterns

When analyzing thread output, these patterns indicate Cassandra-specific activity:

| Thread Name Pattern | Purpose |
|--------------------|---------|
| `ReadStage-*` | Processing read requests |
| `MutationStage-*` | Processing write requests |
| `CompactionExecutor-*` | Running compactions |
| `MemtableFlushWriter-*` | Flushing memtables |
| `GossipStage-*` | Cluster gossip protocol |
| `Native-Transport-*` | CQL client connections |
| `HintsDispatcher-*` | Delivering stored hints |

---

## Best Practices

### Production Usage

- Use `ttop` and `gc` freely—they have minimal overhead
- Use `hh` sparingly as it may cause stop-the-world pauses
- Capture stack traces (`stcap`) during off-peak hours when possible
- Always check `--help` for exact option names before scripting

### Using the Separator

When SJK options conflict with nodetool parsing, use `--` to separate them:

```bash
# Without separator (may cause parsing issues)
nodetool sjk hh --top-number 10

# With separator (explicit argument passing)
nodetool sjk -- hh --top-number 10
```

---

## Troubleshooting

### Command Not Recognized

If a command is not recognized, verify it is available:

```bash
nodetool sjk --commands
```

### Connection Issues

SJK commands use the nodetool JMX connection. If commands fail:

```bash
# Verify nodetool connectivity first
nodetool status

# Check JMX settings
grep JMX /etc/cassandra/cassandra-env.sh
```

### Option Errors

Option names may vary between SJK versions. Always check:

```bash
nodetool sjk <command> --help
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [tpstats](tpstats.md) | Thread pool statistics (Cassandra-specific) |
| [gcstats](gcstats.md) | GC statistics (Cassandra-specific format) |
| [info](info.md) | General node information including memory |
| [tablestats](tablestats.md) | Table-level metrics |

## External Resources

- [SJK GitHub Repository](https://github.com/aragozin/jvm-tools) - Source code and documentation
- [CASSANDRA-12197](https://issues.apache.org/jira/browse/CASSANDRA-12197) - Integration ticket
