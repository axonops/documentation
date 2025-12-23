---
title: "Kafka Performance"
description: "Apache Kafka performance tuning. Throughput optimization, latency reduction, and benchmarking."
meta:
  - name: keywords
    content: "Kafka performance, throughput tuning, latency optimization, Kafka benchmarking"
---

# Kafka Performance

Performance tuning guide for Apache Kafka clusters.

---

## Performance Dimensions

| Dimension | Description | Trade-offs |
|-----------|-------------|------------|
| **Throughput** | Messages/bytes per second | May increase latency |
| **Latency** | End-to-end message delay | May reduce throughput |
| **Durability** | Data persistence guarantee | Impacts throughput |
| **Availability** | System uptime | Requires more resources |

---

## Throughput Optimization

### Producer Throughput

```properties
# High throughput producer configuration
batch.size=131072                    # 128KB batches
linger.ms=20                         # Wait for batching
buffer.memory=67108864               # 64MB buffer
compression.type=lz4                 # Fast compression
acks=1                               # Leader ack only (trade durability)
max.in.flight.requests.per.connection=5
```

**Throughput Checklist:**
- [ ] Enable compression (lz4 or zstd)
- [ ] Increase batch.size
- [ ] Set linger.ms > 0
- [ ] Use async sends
- [ ] Partition across multiple brokers

### Consumer Throughput

```properties
# High throughput consumer configuration
fetch.min.bytes=65536                # Fetch at least 64KB
fetch.max.wait.ms=500                # Wait up to 500ms
fetch.max.bytes=52428800             # 50MB per fetch
max.partition.fetch.bytes=10485760   # 10MB per partition
max.poll.records=1000                # Records per poll
```

### Broker Throughput

```properties
# Broker configuration
num.network.threads=8                # Network I/O threads
num.io.threads=16                    # Disk I/O threads
socket.send.buffer.bytes=1048576     # 1MB send buffer
socket.receive.buffer.bytes=1048576  # 1MB receive buffer
num.replica.fetchers=4               # Replication threads
```

---

## Latency Optimization

### Low Latency Producer

```properties
# Low latency producer configuration
batch.size=16384                     # Small batches
linger.ms=0                          # No batching delay
compression.type=none                # No compression overhead
acks=1                               # Leader ack only
max.block.ms=1000                    # Fast failure
```

### Low Latency Consumer

```properties
# Low latency consumer configuration
fetch.min.bytes=1                    # Return immediately
fetch.max.wait.ms=0                  # No wait
max.poll.records=100                 # Small batches
```

### Broker Latency

```properties
# Broker configuration
socket.request.max.bytes=10485760    # Smaller max request
num.network.threads=16               # More network threads
```

---

## Durability Configuration

### Maximum Durability

```properties
# Producer
acks=all
enable.idempotence=true
retries=2147483647
max.in.flight.requests.per.connection=5

# Broker/Topic
min.insync.replicas=2
unclean.leader.election.enable=false
default.replication.factor=3
```

### Balanced Durability

```properties
# Producer
acks=all
enable.idempotence=true

# Topic
min.insync.replicas=2
replication.factor=3
```

---

## Compression Tuning

### Compression Comparison

| Algorithm | CPU Usage | Compression Ratio | Speed |
|-----------|-----------|-------------------|-------|
| none | 0% | 1.0x | Fastest |
| snappy | Low | 1.5-2x | Fast |
| lz4 | Low | 2-3x | Fast |
| gzip | High | 3-5x | Slow |
| zstd | Medium | 3-4x | Fast |

### Compression Selection

```properties
# Best for most use cases
compression.type=lz4

# Maximum compression
compression.type=zstd

# CPU constrained
compression.type=snappy
```

---

## Partition Tuning

### Partition Count

**Formula:**
```
Partitions = max(
  throughput / per_partition_throughput,
  consumer_instances
)
```

**Guidelines:**
- ~10 MB/s per partition typical
- More partitions = more parallelism
- Too many partitions = overhead

### Partition Distribution

```bash
# Check leader distribution
kafka-topics.sh --bootstrap-server kafka:9092 --describe | \
  grep "Leader:" | awk '{print $4}' | sort | uniq -c

# Rebalance leaders
kafka-leader-election.sh --bootstrap-server kafka:9092 \
  --election-type preferred \
  --all-topic-partitions
```

---

## OS Tuning

### Linux Kernel Parameters

```bash
# /etc/sysctl.conf

# Network buffers
net.core.rmem_max=16777216
net.core.wmem_max=16777216
net.core.rmem_default=16777216
net.core.wmem_default=16777216
net.ipv4.tcp_rmem=4096 87380 16777216
net.ipv4.tcp_wmem=4096 87380 16777216

# File descriptors
fs.file-max=1000000

# Virtual memory
vm.swappiness=1
vm.dirty_ratio=80
vm.dirty_background_ratio=5

# Page cache
vm.vfs_cache_pressure=50
```

### File Descriptor Limits

```bash
# /etc/security/limits.conf
kafka soft nofile 128000
kafka hard nofile 128000
kafka soft nproc 128000
kafka hard nproc 128000
```

### Disk Configuration

Filesystem selection significantly impacts Kafka throughput. XFS is recommended for all log directories.

| Filesystem | Recommendation | Notes |
|------------|----------------|-------|
| **XFS** | Recommended | Best sequential write performance, allocation group parallelism |
| **ext4** | Acceptable | Suitable for smaller deployments |
| **ZFS** | Not recommended | CoW overhead, ARC competes with page cache |

```bash
# Mount options for Kafka data (XFS)
/dev/nvme0n1 /kafka/data xfs noatime,nodiratime 0 2

# I/O scheduler (for NVMe/SSDs)
echo none > /sys/block/nvme0n1/queue/scheduler
```

→ [Filesystem Selection Guide](filesystem.md) - Complete filesystem architecture comparison, page cache tuning, and configuration

---

## JVM Tuning

### Heap Configuration

```bash
# Recommended heap size: 6-8GB
export KAFKA_HEAP_OPTS="-Xms6g -Xmx6g"
```

### GC Configuration

```bash
export KAFKA_JVM_PERFORMANCE_OPTS="-server \
  -XX:+UseG1GC \
  -XX:MaxGCPauseMillis=20 \
  -XX:InitiatingHeapOccupancyPercent=35 \
  -XX:G1HeapRegionSize=16M \
  -XX:MinMetaspaceFreeRatio=50 \
  -XX:MaxMetaspaceFreeRatio=80"
```

---

## Benchmarking

### Producer Benchmark

```bash
# Throughput test
kafka-producer-perf-test.sh \
  --topic test-topic \
  --num-records 10000000 \
  --record-size 1024 \
  --throughput -1 \
  --producer-props \
    bootstrap.servers=kafka:9092 \
    batch.size=65536 \
    linger.ms=10 \
    compression.type=lz4
```

### Consumer Benchmark

```bash
# Throughput test
kafka-consumer-perf-test.sh \
  --bootstrap-server kafka:9092 \
  --topic test-topic \
  --messages 10000000 \
  --threads 4
```

### End-to-End Latency

```bash
kafka-run-class.sh kafka.tools.EndToEndLatency \
  kafka:9092 \
  test-topic \
  10000 \
  all \
  1024
```

---

## Performance Metrics

### Key Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| `MessagesInPerSec` | Produce rate | Workload dependent |
| `BytesInPerSec` | Bytes produced | Workload dependent |
| `BytesOutPerSec` | Bytes consumed | Workload dependent |
| `TotalTimeMs (P99)` | Request latency | < 100ms |
| `RequestQueueTimeMs` | Queue time | < 10ms |
| `UnderReplicatedPartitions` | Replication health | 0 |

### Identifying Bottlenecks

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| High RequestQueueTimeMs | Network threads saturated | Increase num.network.threads |
| High LocalTimeMs | Disk I/O slow | Faster disks, more I/O threads |
| High RemoteTimeMs | Replication lag | More replica fetchers |
| High ResponseQueueTimeMs | Network threads saturated | Increase num.network.threads |

---

## Related Documentation

- [Filesystem Selection](filesystem.md) - Filesystem recommendations and page cache tuning
- [Operations Overview](../index.md) - Operations guide
- [Capacity Planning](capacity-planning/index.md) - Sizing guide
- [Configuration](../configuration/index.md) - Configuration reference
- [Monitoring](../monitoring/index.md) - Metrics and alerting
