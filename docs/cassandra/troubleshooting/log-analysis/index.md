# Cassandra Log Analysis

Guide to analyzing Cassandra logs for troubleshooting.

## Log Locations

```
/var/log/cassandra/
├── system.log      # Main application log
├── debug.log       # Debug-level logging
├── gc.log          # Garbage collection
└── audit/          # Audit logs (if enabled)
```

## Key Patterns to Search

### Errors and Exceptions

```bash
# All errors
grep -i "error\|exception" /var/log/cassandra/system.log | tail -50

# Stack traces
grep -A 20 "Exception" /var/log/cassandra/system.log

# Specific errors
grep -i "ReadTimeoutException" /var/log/cassandra/system.log
grep -i "WriteTimeoutException" /var/log/cassandra/system.log
grep -i "UnavailableException" /var/log/cassandra/system.log
```

### Performance Issues

```bash
# Slow queries
grep -i "slow" /var/log/cassandra/system.log

# Tombstone warnings
grep -i "tombstone" /var/log/cassandra/system.log

# Large partitions
grep -i "large partition\|large row" /var/log/cassandra/system.log

# Compaction
grep -i "compaction\|compacted" /var/log/cassandra/system.log
```

### Cluster Events

```bash
# Node status changes
grep -i "is now\|state jump\|marking" /var/log/cassandra/system.log

# Gossip events
grep -i "gossip" /var/log/cassandra/system.log

# Streaming
grep -i "streaming\|stream" /var/log/cassandra/system.log
```

## GC Log Analysis

```bash
# Long pauses
grep -E "pause.*[0-9]{3,}ms" /var/log/cassandra/gc.log

# Full GC events
grep -i "full gc\|to-space" /var/log/cassandra/gc.log

# Heap after GC
grep -E "Heap:.* -> " /var/log/cassandra/gc.log
```

## Common Log Messages

### Normal Operations

```
INFO  - Starting listening for CQL clients
INFO  - Completed loading
INFO  - Starting compaction
INFO  - Compacted to [sstable]
```

### Warning Signs

```
WARN  - Dropping MUTATION message
WARN  - Detected GC pause of Xms
WARN  - Large partition in sstable
WARN  - Tombstones scanned X for query
```

### Critical Issues

```
ERROR - Exception in thread
ERROR - Error writing to channel
FATAL - Cannot start Cassandra
```

## Log Aggregation Tools

| Tool | Features |
|------|----------|
| ELK Stack | Full-text search, visualization |
| Splunk | Enterprise log management |
| Loki | Lightweight, Grafana integration |
| CloudWatch | AWS native |

---

## Next Steps

- **[Diagnosis Guide](../diagnosis/index.md)** - Systematic diagnosis
- **[Common Errors](../common-errors/index.md)** - Error reference
- **[Monitoring](../../operations/monitoring/index.md)** - Proactive monitoring
