# nodetool info

Displays detailed information about a single Cassandra node including memory usage, disk capacity, uptime, and operational statistics.

---

## Synopsis

```bash
nodetool [connection_options] info
```

## Description

`nodetool info` provides comprehensive information about the connected node:

- Node identification (ID, tokens, datacenter, rack)
- Memory usage (heap, off-heap)
- Disk capacity and usage
- Uptime and exception count
- Cache statistics

This command is essential for understanding a single node's resource utilization.

---

## Output Example

```
ID                     : a1b2c3d4-e5f6-7890-abcd-ef1234567890
Gossip active          : true
Native Transport active: true
Load                   : 256.12 GiB
Generation No          : 1699574400
Uptime (seconds)       : 864000
Heap Memory (MB)       : 4096.00 / 8192.00
Off Heap Memory (MB)   : 512.45
Data Center            : dc1
Rack                   : rack1
Exceptions             : 0
Key Cache              : entries 125000, size 256 MiB, capacity 512 MiB, 98534221 hits, 99123456 requests, 0.994 recent hit rate, 14400 save period in seconds
Row Cache              : entries 0, size 0 bytes, capacity 0 bytes, 0 hits, 0 requests, NaN recent hit rate, 0 save period in seconds
Counter Cache          : entries 0, size 0 bytes, capacity 0 bytes, 0 hits, 0 requests, NaN recent hit rate, 7200 save period in seconds
Network Cache          : size 64 MiB, overflow size: 0 bytes, capacity 128 MiB
Percent Repaired       : 98.45%
Token                  : (invoke with -T/--tokens to see all 256 tokens)
```

---

## Output Fields

### Node Identification

| Field | Description |
|-------|-------------|
| ID | Unique UUID for this node (Host ID) |
| Data Center | Datacenter name from snitch configuration |
| Rack | Rack name from snitch configuration |
| Generation No | Gossip generation number (timestamp-based, increases on restart) |
| Token | Token(s) owned by this node |

### Status Indicators

| Field | Description |
|-------|-------------|
| Gossip active | Whether gossip protocol is enabled |
| Native Transport active | Whether CQL native protocol is accepting connections |
| Uptime | Time since Cassandra started (in seconds) |

### Resource Usage

| Field | Description |
|-------|-------------|
| Load | Total data size on disk |
| Heap Memory | Used / Maximum JVM heap memory |
| Off Heap Memory | Memory used outside JVM heap (bloom filters, compression metadata, etc.) |

### Health Indicators

| Field | Description |
|-------|-------------|
| Exceptions | Count of exceptions since startup |
| Percent Repaired | Percentage of data that has been repaired (incremental repair) |

### Cache Statistics

| Field | Description |
|-------|-------------|
| Key Cache | Partition key location cache |
| Row Cache | Cached row data |
| Counter Cache | Counter value cache |
| Network Cache | Buffer cache for network operations |

---

## Options

| Option | Description |
|--------|-------------|
| `-T, --tokens` | Display all tokens owned by this node |

### Show All Tokens

```bash
nodetool info -T
```

Outputs all 256 (or configured `num_tokens`) tokens.

---

## Interpreting Results

### Memory Usage

```
Heap Memory (MB)       : 6144.00 / 8192.00
```

!!! warning "Heap Usage"
    - **75-85% used**: Normal operating range
    - **>90% used**: Risk of GC pressure, consider increasing heap or reducing load
    - **<50% used**: Heap may be over-provisioned

```
Off Heap Memory (MB)   : 512.45
```

Off-heap memory includes:

- Bloom filters
- Compression metadata
- Index summaries
- Native memory for Netty buffers

### Cache Hit Rates

```
Key Cache: ... 0.994 recent hit rate
```

| Hit Rate | Assessment |
|----------|------------|
| > 0.95 | Excellent |
| 0.85 - 0.95 | Good |
| 0.70 - 0.85 | Acceptable |
| < 0.70 | Consider increasing cache size |

!!! info "Key Cache Importance"
    The key cache stores partition key locations, avoiding disk seeks. A high hit rate significantly improves read performance.

### Uptime Analysis

```
Uptime (seconds)       : 864000
```

- 864000 seconds = 10 days
- Short uptime after expected restart: Normal
- Unexpected short uptime: Investigate restarts in logs

### Exception Count

```
Exceptions             : 0
```

!!! danger "Non-Zero Exceptions"
    Exceptions indicate errors that may affect operations:

    - Check `system.log` for exception details
    - Common causes: disk errors, network issues, OOM
    - Counter resets on restart

### Percent Repaired

```
Percent Repaired       : 98.45%
```

| Percentage | Assessment |
|------------|------------|
| > 95% | Good repair compliance |
| 80-95% | Repairs may be falling behind |
| < 80% | Urgent: Review repair schedule |

!!! note "Incremental Repair Only"
    This metric only applies when using incremental repair. With full repair, this may show 0% or inaccurate values.

---

## Examples

### Basic Health Check

```bash
nodetool info
```

Quick check of node health indicators.

### Script: Extract Heap Usage

```bash
nodetool info | grep "Heap Memory" | awk -F'[:/]' '{print "Used: "$2" Max: "$3}'
```

### Script: Check for Exceptions

```bash
exceptions=$(nodetool info | grep "Exceptions" | awk '{print $3}')
if [ "$exceptions" -gt 0 ]; then
    echo "WARNING: $exceptions exceptions logged"
fi
```

### Compare Multiple Nodes

```bash
for host in 192.168.1.101 192.168.1.102 192.168.1.103; do
    echo "=== $host ==="
    nodetool -h $host info | grep -E "(Load|Heap|Exceptions|Percent Repaired)"
done
```

---

## When to Use

| Scenario | Purpose |
|----------|---------|
| Daily health check | Verify memory, cache, and exception status |
| After restarts | Confirm node came up correctly |
| Before maintenance | Check node state before operations |
| Performance investigation | Review cache hit rates and memory |
| Capacity planning | Assess resource utilization |

---

## When NOT to Use

!!! note "Limitations"
    - **For cluster-wide view**: Use `nodetool status`
    - **For continuous monitoring**: Use metrics collection
    - **For historical trends**: Use AxonOps
    - **For detailed table stats**: Use `nodetool tablestats`

---

## Troubleshooting

### Native Transport Inactive

```
Native Transport active: false
```

CQL connections will fail. Enable with:

```bash
nodetool enablebinary
```

Or investigate why it was disabled (resource exhaustion, manual action).

### Gossip Inactive

```
Gossip active          : false
```

!!! danger "Gossip Disabled"
    Node is isolated from cluster. Enable immediately:

    ```bash
    nodetool enablegossip
    ```

    Check logs for why gossip was disabled.

### High Off-Heap Memory

Large off-heap memory usage may indicate:

- Many tables/keyspaces (bloom filters per SSTable)
- Large partition keys (more index memory)
- Need to tune bloom filter settings

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [status](status.md) | Cluster-wide status overview |
| [tpstats](tpstats.md) | Thread pool statistics |
| [tablestats](tablestats.md) | Per-table statistics |
| [gcstats](gcstats.md) | Garbage collection details |
| [gossipinfo](gossipinfo.md) | Gossip protocol state |
