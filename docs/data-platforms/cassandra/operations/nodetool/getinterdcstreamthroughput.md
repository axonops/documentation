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
nodetool [connection_options] getinterdcstreamthroughput
```

## Description

`nodetool getinterdcstreamthroughput` shows the maximum throughput for streaming operations between datacenters. This separate limit allows controlling bandwidth usage across potentially slower or more expensive WAN links.

---

## Examples

### Basic Usage

```bash
nodetool getinterdcstreamthroughput
```

### Sample Output

```
Current inter-datacenter stream throughput: 100 MB/s
```

---

## Configuration

```yaml
# cassandra.yaml
inter_dc_stream_throughput_outbound_megabits_per_sec: 100
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
