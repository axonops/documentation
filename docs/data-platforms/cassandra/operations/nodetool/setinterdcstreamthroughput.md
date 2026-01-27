---
title: "nodetool setinterdcstreamthroughput"
description: "Set inter-datacenter streaming throughput limit using nodetool setinterdcstreamthroughput."
meta:
  - name: keywords
    content: "nodetool setinterdcstreamthroughput, inter-DC streaming, throughput, multi-datacenter"
---

# nodetool setinterdcstreamthroughput

Sets the inter-datacenter stream throughput limit.

---

## Synopsis

```bash
nodetool [connection_options] setinterdcstreamthroughput [options] <throughput>
```

## Description

`nodetool setinterdcstreamthroughput` modifies the maximum throughput for streaming between datacenters. This is useful for controlling WAN bandwidth usage during cross-datacenter operations.

---

## Options

| Option | Description |
|--------|-------------|
| `-m, --mib` | Interpret the throughput value as MiB/s instead of Mb/s |
| `-e, --entire-sstable-throughput` | Set the entire-SSTable inter-DC streaming throughput |

---

## Arguments

| Argument | Description |
|----------|-------------|
| `throughput` | Maximum throughput. Default unit is **megabits per second (Mb/s)**. Use `-m` for MiB/s. Set to 0 to disable throttling. |

!!! note "Unit Clarification"
    By default, the argument is in **megabits per second (Mb/s)**, not megabytes. For example:

    - `nodetool setinterdcstreamthroughput 200` = 200 Mb/s = ~25 MiB/s
    - `nodetool setinterdcstreamthroughput -m 25` = 25 MiB/s = ~200 Mb/s

!!! note "cassandra.yaml Parameter"
    The corresponding cassandra.yaml parameter changed in 4.1:

    | Cassandra Version | Parameter Name | Example |
    |-------------------|----------------|---------|
    | Pre-4.1 | `inter_dc_stream_throughput_outbound_megabits_per_sec` | `200` |
    | 4.1+ | `inter_dc_stream_throughput` | `200Mb/s` or `24MiB/s` |

---

## Examples

### Set Throughput (Megabits per Second)

```bash
# Set to 50 Mb/s (~6 MiB/s)
nodetool setinterdcstreamthroughput 50
```

### Set Throughput (MiB per Second)

```bash
# Set to 25 MiB/s using the -m flag
nodetool setinterdcstreamthroughput -m 25
```

### Increase for Faster Cross-DC Operations

```bash
# Set to 200 Mb/s (~25 MiB/s)
nodetool setinterdcstreamthroughput 200
```

### Disable Throttling

```bash
# Set to 0 for unlimited throughput
nodetool setinterdcstreamthroughput 0
```

### Set Entire-SSTable Streaming Throughput

```bash
# Set entire-SSTable inter-DC streaming throughput
nodetool setinterdcstreamthroughput -e 200
```

---

## When to Use

### WAN Bandwidth Management

```bash
# Limit during business hours (25 Mb/s)
nodetool setinterdcstreamthroughput 25

# Increase during off-peak (100 Mb/s)
nodetool setinterdcstreamthroughput 100
```

### Cross-DC Rebuild

```bash
# Increase for faster rebuild (150 Mb/s)
nodetool setinterdcstreamthroughput 150
nodetool rebuild -- dc2
```

### Using MiB/s Units

```bash
# Set to 10 MiB/s (clearer unit)
nodetool setinterdcstreamthroughput -m 10

# Set to 50 MiB/s during maintenance
nodetool setinterdcstreamthroughput -m 50
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [getinterdcstreamthroughput](getinterdcstreamthroughput.md) | View current setting |
| [setstreamthroughput](setstreamthroughput.md) | Intra-DC throughput |