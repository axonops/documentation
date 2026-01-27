---
title: "nodetool getinterdcstreamthroughput"
description: "Display inter-datacenter streaming throughput limit using nodetool getinterdcstreamthroughput."
meta:
  - name: keywords
    content: "nodetool getinterdcstreamthroughput, inter-DC streaming, throughput, multi-datacenter"
---

# nodetool getinterdcstreamthroughput

Displays the inter-datacenter stream throughput limit.

---

## Synopsis

```bash
nodetool [connection_options] getinterdcstreamthroughput [options]
```

## Options

| Option | Description |
|--------|-------------|
| `-m, --mib` | Display throughput in MiB/s instead of Mb/s |
| `-d, --precise-mbit` | Display precise Mb/s value as a decimal |
| `-e, --entire-sstable-throughput` | Show entire SSTable streaming throughput instead of inter-DC throughput |

## Description

`nodetool getinterdcstreamthroughput` shows the maximum throughput for streaming operations between datacenters. By default, the output is in **megabits per second (Mb/s)**, not megabytes. This separate limit allows controlling bandwidth usage across potentially slower or more expensive WAN links.

---

## Examples

### Basic Usage

```bash
nodetool getinterdcstreamthroughput
```

### Sample Output

```
Current inter-datacenter stream throughput: 100 Mb/s
```

A value of `unlimited` indicates that the configured value is `0` or negative (no throttling).

### Display in MiB/s

```bash
nodetool getinterdcstreamthroughput --mib
```

---

## Configuration

The cassandra.yaml parameter name varies by version:

| Cassandra Version | Parameter Name | Example | Unit |
|-------------------|----------------|---------|------|
| Pre-4.1 | `inter_dc_stream_throughput_outbound_megabits_per_sec` | `100` | Megabits/s |
| 4.1+ | `inter_dc_stream_throughput` | `100Mb/s` or `12MiB/s` | Various |

```yaml
# cassandra.yaml (4.1+)
inter_dc_stream_throughput: 100Mb/s

# cassandra.yaml (Pre-4.1)
# inter_dc_stream_throughput_outbound_megabits_per_sec: 100
```

---

## Use Cases

### Verify WAN Bandwidth Settings

```bash
nodetool getinterdcstreamthroughput
```

### Multi-DC Operations

```bash
# Check before cross-DC rebuild
nodetool getinterdcstreamthroughput
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [setinterdcstreamthroughput](setinterdcstreamthroughput.md) | Modify throughput |
| [getstreamthroughput](getstreamthroughput.md) | Intra-DC throughput |
| [netstats](netstats.md) | Monitor streaming |