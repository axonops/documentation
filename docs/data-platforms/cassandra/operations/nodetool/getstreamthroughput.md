---
title: "nodetool getstreamthroughput"
description: "Display streaming throughput limit in Cassandra using nodetool getstreamthroughput."
meta:
  - name: keywords
    content: "nodetool getstreamthroughput, streaming throughput, data streaming, Cassandra"
---

# nodetool getstreamthroughput

Displays the stream throughput limit.

---

## Synopsis

```bash
nodetool [connection_options] getstreamthroughput [options]
```

## Options

| Option | Description |
|--------|-------------|
| `-m, --mib` | Display throughput in MiB/s instead of Mb/s |
| `-d, --precise-mbit` | Display precise Mb/s value as a decimal |
| `-e, --entire-sstable-throughput` | Show entire SSTable streaming throughput instead of standard streaming throughput |

## Description

`nodetool getstreamthroughput` shows the current maximum throughput for streaming operations such as bootstrap, rebuild, and repair. By default, the output is in **megabits per second (Mb/s)**, not megabytes. This limit controls how fast data is transferred between nodes.

---

## Examples

### Basic Usage

```bash
nodetool getstreamthroughput
```

### Sample Output

```
Current stream throughput: 200 Mb/s
```

A value of `unlimited` indicates that the configured value is `0` or negative (no throttling).

### Display in MiB/s

```bash
nodetool getstreamthroughput --mib
```

---

## Configuration

The cassandra.yaml parameter name varies by version:

| Cassandra Version | Parameter Name | Example | Unit |
|-------------------|----------------|---------|------|
| Pre-4.1 | `stream_throughput_outbound_megabits_per_sec` | `200` | Megabits/s |
| 4.1+ | `stream_throughput` | `200Mb/s` or `24MiB/s` | Various |

```yaml
# cassandra.yaml (4.1+)
stream_throughput: 200Mb/s

# cassandra.yaml (Pre-4.1)
# stream_throughput_outbound_megabits_per_sec: 200
```

---

## Use Cases

### Verify Configuration

```bash
nodetool getstreamthroughput
```

### Before Streaming Operations

```bash
# Check throughput before bootstrap
nodetool getstreamthroughput
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [setstreamthroughput](setstreamthroughput.md) | Modify throughput |
| [netstats](netstats.md) | Monitor streaming |
| [getinterdcstreamthroughput](getinterdcstreamthroughput.md) | Inter-DC throughput |