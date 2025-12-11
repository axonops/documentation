# nodetool setinterdcstreamthroughput

Sets the inter-datacenter stream throughput limit.

---

## Synopsis

```bash
nodetool [connection_options] setinterdcstreamthroughput <throughput_mb_per_sec>
```

## Description

`nodetool setinterdcstreamthroughput` modifies the maximum throughput for streaming between datacenters. This is useful for controlling WAN bandwidth usage during cross-datacenter operations.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `throughput_mb_per_sec` | Maximum throughput in MB/s |

---

## Examples

### Set Throughput

```bash
nodetool setinterdcstreamthroughput 50
```

### Increase for Faster Cross-DC Operations

```bash
nodetool setinterdcstreamthroughput 200
```

---

## When to Use

### WAN Bandwidth Management

```bash
# Limit during business hours
nodetool setinterdcstreamthroughput 25

# Increase during off-peak
nodetool setinterdcstreamthroughput 100
```

### Cross-DC Rebuild

```bash
# Increase for faster rebuild
nodetool setinterdcstreamthroughput 150
nodetool rebuild -- dc2
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [getinterdcstreamthroughput](getinterdcstreamthroughput.md) | View current setting |
| [setstreamthroughput](setstreamthroughput.md) | Intra-DC throughput |
