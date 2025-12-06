# Memory Management

Cassandra uses multiple memory regions: JVM heap, off-heap native memory, and OS page cache. Understanding memory allocation is essential for performance tuning.

## Memory Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ SYSTEM MEMORY                                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ JVM HEAP (managed by garbage collector)                      │ │
│ │                                                              │ │
│ │ ├── Memtables (configurable: heap or off-heap)              │ │
│ │ ├── Key Cache                                                │ │
│ │ ├── Row Cache (if enabled)                                   │ │
│ │ ├── Partition Summary (pre-4.0)                             │ │
│ │ └── Internal data structures                                 │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ OFF-HEAP (native memory, not garbage collected)              │ │
│ │                                                              │ │
│ │ ├── Bloom filters                                            │ │
│ │ ├── Compression metadata                                     │ │
│ │ ├── Partition index (trie, 4.0+)                            │ │
│ │ ├── Memtables (if offheap_objects or offheap_buffers)       │ │
│ │ └── Chunk cache                                              │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ OS PAGE CACHE (managed by operating system)                  │ │
│ │                                                              │ │
│ │ ├── Recently read SSTable data                              │ │
│ │ └── Memory-mapped files                                      │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## JVM Heap

The JVM heap is managed by the garbage collector. Large heaps increase GC pause times.

### Heap Sizing Guidelines

| Server RAM | Recommended Heap | Rationale |
|------------|------------------|-----------|
| 16GB | 4-8GB | Small deployments |
| 32GB | 8GB | Standard production |
| 64GB | 8-16GB | Large deployments |
| 128GB+ | 16-31GB | Maximum practical heap |

**Do not exceed 31GB heap.** Beyond this threshold, JVM uses 64-bit object pointers, reducing effective memory.

### Configuration

```bash
# jvm.options or jvm-server.options

# Set heap size (min = max for predictable behavior)
-Xms8G
-Xmx8G

# G1 garbage collector (recommended)
-XX:+UseG1GC
-XX:MaxGCPauseMillis=500
```

### Heap Components

| Component | Description | Configuration |
|-----------|-------------|---------------|
| Memtables | In-memory write buffer | `memtable_heap_space_in_mb` |
| Key Cache | Partition key → offset | `key_cache_size_in_mb` |
| Row Cache | Cached row data | `row_cache_size_in_mb` |
| Summary | Sampled index (pre-4.0) | `min_index_interval` |

---

## Off-Heap Memory

Off-heap memory is native memory outside the JVM heap, not subject to garbage collection.

### Off-Heap Components

| Component | Description | Memory Scaling |
|-----------|-------------|----------------|
| Bloom filters | Existence checks | ~10 bits per partition key |
| Compression info | Chunk offsets | Proportional to data size |
| Partition index | Trie index (4.0+) | Proportional to partition count |
| Memtables | Write buffer (if configured) | `memtable_offheap_space_in_mb` |
| Chunk cache | Compressed SSTable chunks | `file_cache_size_in_mb` |

### Configuration

```yaml
# cassandra.yaml

# Off-heap memtables
memtable_offheap_space_in_mb: 2048
memtable_allocation_type: offheap_buffers

# Chunk cache (auto-sized by default)
# file_cache_size_in_mb: auto
```

### Memtable Allocation Types

| Type | Heap Usage | Off-Heap Usage | GC Impact |
|------|------------|----------------|-----------|
| `heap_buffers` | High | None | High |
| `offheap_objects` | Medium | High | Medium |
| `offheap_buffers` | Low | High | Low |

For large heaps or high write throughput, use `offheap_buffers` to reduce GC pressure.

---

## OS Page Cache

The operating system automatically caches recently accessed file data in unused RAM.

### Page Cache Benefits

- SSTable data cached after first read
- No configuration required
- Automatically sized to available RAM
- Shared across all processes

### Sizing

```
Page Cache = Total RAM - Heap - Off-Heap - OS Overhead

Example (64GB server):
- Heap: 8GB
- Off-heap: 8GB
- OS: 4GB
- Page cache: ~44GB available
```

### Maximizing Page Cache

- Keep heap size reasonable (8-16GB)
- Leave sufficient RAM for page cache
- Avoid memory-hungry co-located processes

---

## Memory Sizing Example

### 64GB Server Configuration

```
Total RAM: 64GB

Allocation:
├── JVM Heap: 8GB
│   ├── Memtables (heap portion): 2GB
│   ├── Key Cache: 100MB
│   └── Internal: ~6GB
│
├── Off-Heap: 8-12GB
│   ├── Memtables (off-heap): 2GB
│   ├── Bloom filters: ~1GB (varies)
│   ├── Partition indexes: ~2GB (varies)
│   └── Chunk cache: 2-4GB
│
├── OS Overhead: 4GB
│
└── Page Cache: 40-44GB
```

### Configuration

```yaml
# cassandra.yaml

# Memtables
memtable_heap_space_in_mb: 2048
memtable_offheap_space_in_mb: 2048
memtable_allocation_type: offheap_buffers

# Key cache
key_cache_size_in_mb: 100

# Row cache (disabled)
row_cache_size_in_mb: 0
```

```bash
# jvm-server.options
-Xms8G
-Xmx8G
```

---

## Monitoring Memory

### Heap Usage

```bash
# Current heap usage
nodetool info | grep "Heap Memory"

# GC statistics
nodetool gcstats

# Detailed memory breakdown
nodetool info
```

### Off-Heap Usage

```bash
# Off-heap memory used
nodetool info | grep "Off Heap Memory"

# Bloom filter memory
nodetool tablestats | grep -i bloom
```

### JMX Metrics

```
# Heap
java.lang:type=Memory/HeapMemoryUsage

# Memtables
org.apache.cassandra.metrics:type=Table,name=MemtableOnHeapSize
org.apache.cassandra.metrics:type=Table,name=MemtableOffHeapSize

# Caches
org.apache.cassandra.metrics:type=Cache,scope=KeyCache,name=Size
org.apache.cassandra.metrics:type=Cache,scope=RowCache,name=Size

# Bloom filters
org.apache.cassandra.metrics:type=Table,name=BloomFilterOffHeapMemoryUsed
```

---

## Memory Troubleshooting

### High Heap Usage

**Symptoms:**

- Long GC pauses
- Heap usage consistently >70%
- OOM errors

**Investigation:**

```bash
nodetool info | grep "Heap Memory"
nodetool gcstats
grep "GC pause" /var/log/cassandra/gc.log
```

**Solutions:**

1. Move memtables off-heap
2. Reduce key cache size
3. Disable row cache
4. Reduce number of tables

### Memory Pressure from Many Tables

Each table requires:

- One memtable
- Bloom filters per SSTable
- Index structures per SSTable

**Guideline:** Avoid more than 200 tables per node.

### Bloom Filter Memory

Bloom filter memory scales with partition count:

```
Memory ≈ partitions × SSTables × 10 bits × (1 / ln(2)²)

Example:
- 100 million partitions
- 20 SSTables average
- ~300MB bloom filter memory
```

**Reduce by:**

- Increasing `bloom_filter_fp_chance`
- Reducing SSTable count (better compaction)

---

## Best Practices

### General

- Set heap to 8-16GB (never >31GB)
- Use G1 garbage collector
- Leave ~50% of RAM for page cache
- Monitor GC pause times

### Write-Heavy Workloads

```yaml
memtable_heap_space_in_mb: 4096
memtable_offheap_space_in_mb: 4096
memtable_allocation_type: offheap_buffers
memtable_flush_writers: 4
```

### Read-Heavy Workloads

```yaml
key_cache_size_in_mb: 200
# Ensure sufficient page cache for working set
```

### Mixed Workloads

```yaml
memtable_heap_space_in_mb: 2048
memtable_offheap_space_in_mb: 2048
memtable_allocation_type: offheap_buffers
key_cache_size_in_mb: 100
```

---

## Related Documentation

- **[Storage Engine Overview](index.md)** - Architecture overview
- **[Write Path](write-path.md)** - Memtable configuration
- **[Read Path](read-path.md)** - Cache configuration
- **[JVM Tuning](../../performance/jvm-tuning/index.md)** - GC configuration
