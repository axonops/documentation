# nodetool info

Displays detailed information about the local node, including memory usage, cache statistics, uptime, and operational state.

## Synopsis

```bash
nodetool [connection_options] info
```

## Description

The `info` command provides comprehensive diagnostic information about a single Cassandra node. Unlike `status` which shows cluster-wide information, `info` focuses on the local node's internal state including JVM memory usage, cache performance, and data statistics.

This command is essential for understanding node-level resource utilization and identifying potential memory or cache issues.

## Connection Options

| Option | Description |
|--------|-------------|
| -h, --host | Hostname or IP address to connect to (default: localhost) |
| -p, --port | JMX port number (default: 7199) |
| -u, --username | JMX username for authentication |
| -pw, --password | JMX password for authentication |
| -T, --tokens | Display all token values assigned to this node |

## Output Fields

| Field | Description | Healthy Range |
|-------|-------------|---------------|
| ID | Node's unique Host ID (UUID) | N/A |
| Gossip active | Whether the gossip protocol is running | true |
| Native Transport active | Whether the CQL native protocol is accepting connections | true |
| Load | Total data size stored on disk | Varies by deployment |
| Generation No | Gossip generation number (epoch timestamp when node last started) | Increases on each restart |
| Uptime (seconds) | Time since Cassandra process started | N/A |
| Heap Memory (MB) | Used / Total JVM heap memory | Used < 75% of Total |
| Off Heap Memory (MB) | Memory allocated outside JVM heap (bloom filters, compression metadata) | Varies by data size |
| Data Center | Datacenter assignment from snitch configuration | As configured |
| Rack | Rack assignment from snitch configuration | As configured |
| Exceptions | Count of unhandled exceptions since startup | 0 |
| Key Cache | Key cache entries, size, capacity, hit rate | Hit rate > 0.85 |
| Row Cache | Row cache statistics (if enabled) | Hit rate > 0.90 if used |
| Counter Cache | Counter cache statistics | Hit rate > 0.85 |
| Chunk Cache | Off-heap chunk cache for compressed data | Varies |
| Percent Repaired | Percentage of data covered by incremental repair | > 90% |

## Examples

### Basic Node Information

```bash
nodetool info
```

**Output:**
```
ID                     : a1b2c3d4-e5f6-7890-abcd-ef1234567890
Gossip active          : true
Native Transport active: true
Load                   : 156.23 GiB
Generation No          : 1704067200
Uptime (seconds)       : 2592000
Heap Memory (MB)       : 12288.00 / 16384.00
Off Heap Memory (MB)   : 2048.56
Data Center            : dc1
Rack                   : rack1
Exceptions             : 0
Key Cache              : entries 2500000, size 512 MiB, capacity 512 MiB, 98765432 hits, 100000000 requests, 0.988 recent hit rate, 14400 save period in seconds
Row Cache              : entries 0, size 0 bytes, capacity 0 bytes, 0 hits, 0 requests, NaN recent hit rate, 0 save period in seconds
Counter Cache          : entries 0, size 0 bytes, capacity 0 bytes, 0 hits, 0 requests, NaN recent hit rate, 7200 save period in seconds
Chunk Cache            : entries 1024, size 1 GiB, capacity 1 GiB, 87654321 misses, 987654321 requests, 0.911 recent hit rate, 922.337 microseconds miss latency
Percent Repaired       : 94.7%
Token                  : (invoke with -T/--tokens to see all 256 tokens)
```

### Display Token Information

```bash
nodetool info -T
```

Appends all tokens assigned to the node, useful for debugging token distribution issues.

### Remote Node Information

```bash
nodetool -h 10.0.0.2 info
```

## Interpreting Results

### Memory Analysis

**Heap Memory:**
```
Heap Memory (MB)       : 12288.00 / 16384.00
```

- First value: Currently used heap memory
- Second value: Maximum allocated heap memory
- **Warning**: If used consistently exceeds 75% of total, consider increasing heap or investigating memory pressure

**Off Heap Memory:**
```
Off Heap Memory (MB)   : 2048.56
```

Off-heap memory includes:
- Bloom filter data
- Index summary data
- Compression metadata
- Memtable data (if `memtable_allocation_type: offheap_objects`)

### Cache Performance

**Key Cache:**
```
Key Cache: entries 2500000, size 512 MiB, capacity 512 MiB, 98765432 hits, 100000000 requests, 0.988 recent hit rate
```

| Metric | Description | Target |
|--------|-------------|--------|
| entries | Number of cached partition key positions | N/A |
| size | Current memory usage | < capacity |
| capacity | Maximum allowed size | As configured |
| hit rate | Percentage of requests served from cache | > 0.85 |

**Low hit rate causes:**
- Cache too small for working set
- Access patterns not cache-friendly
- Recent node restart (cache warming)

**Row Cache:**
Row cache stores entire partition data. A `NaN` hit rate indicates the cache is disabled (default).

### Repair Status

```
Percent Repaired: 94.7%
```

Indicates the percentage of data marked as repaired through incremental repair. Values below 90% suggest repair operations are falling behind.

## Warning Indicators

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Heap usage | > 75% of max | Review heap sizing, check for memory leaks |
| Exceptions | > 0 | Review system.log for exception details |
| Key Cache hit rate | < 0.85 | Consider increasing key_cache_size |
| Percent Repaired | < 90% | Schedule repair operations |
| Native Transport active | false | CQL connections will fail - investigate |
| Gossip active | false | Node isolated from cluster - critical |

## Common Use Cases

### Health Check Extraction

```bash
#!/bin/bash
# Extract key health metrics
nodetool info | awk '
    /Heap Memory/ {
        split($4, used, "/")
        split($5, max, "/")
        heap_pct = (used[1] / max[1]) * 100
        printf "heap_usage_percent=%.1f\n", heap_pct
    }
    /Exceptions/ { print "exceptions=" $3 }
    /Key Cache.*hit rate/ {
        match($0, /([0-9.]+) recent hit rate/)
        print "key_cache_hit_rate=" substr($0, RSTART, RLENGTH)
    }
    /Percent Repaired/ { print "percent_repaired=" $4 }
'
```

### Memory Monitoring

```bash
# Alert if heap usage exceeds 80%
HEAP_INFO=$(nodetool info | grep "Heap Memory")
USED=$(echo $HEAP_INFO | awk '{print $4}' | tr -d '/')
MAX=$(echo $HEAP_INFO | awk '{print $5}')
PERCENT=$(echo "scale=2; $USED / $MAX * 100" | bc)

if (( $(echo "$PERCENT > 80" | bc -l) )); then
    echo "WARNING: Heap usage at ${PERCENT}%"
fi
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Command executed successfully |
| 1 | Error connecting to JMX or executing command |

## Related Commands

- [nodetool status](status.md) - Cluster-wide node status
- [nodetool gcstats](gcstats.md) - Garbage collection statistics
- [nodetool tpstats](tpstats.md) - Thread pool statistics
- [nodetool tablestats](tablestats.md) - Per-table statistics

## Related Documentation

- [Monitoring - Key Metrics](../../../monitoring/key-metrics/index.md) - Understanding node metrics
- [Performance - JVM Tuning](../../../performance/jvm-tuning/index.md) - Heap and GC optimization
- [Configuration - cassandra.yaml](../../../configuration/cassandra-yaml/index.md) - Cache configuration settings
- [Operations - Repair](../../../operations/repair/index.md) - Maintaining repair percentage

## Version Information

Available in all Apache Cassandra versions. The `Chunk Cache` field was added in Cassandra 4.0. Output format is consistent across 4.x and 5.x releases.
