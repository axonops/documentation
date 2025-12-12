# nodetool getstreamthroughput

Displays the stream throughput limit in MB/s.

---

## Synopsis

```bash
nodetool [connection_options] getstreamthroughput
```

## Description

`nodetool getstreamthroughput` shows the current maximum throughput for streaming operations such as bootstrap, rebuild, and repair. This limit controls how fast data is transferred between nodes.

---

## Examples

### Basic Usage

```bash
nodetool getstreamthroughput
```

### Sample Output

```
Current stream throughput: 200 MB/s
```

---

## Configuration

```yaml
# cassandra.yaml
stream_throughput_outbound_megabits_per_sec: 200
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
