---
title: "Cassandra Configuration Reference"
description: "Cassandra configuration overview. YAML files, JVM options, and runtime settings."
meta:
  - name: keywords
    content: "Cassandra configuration, config files, settings overview"
---

# Cassandra Configuration Reference

Cassandra configuration is spread across three places: `cassandra.yaml` for database settings, JVM options files for heap and garbage collection, and OS-level settings for limits and kernel parameters. Changes to some settings take effect immediately; others require a rolling restart.

The defaults prioritize safe startup over performance—Cassandra will run on minimal hardware without crashing, but it will not perform well. Production deployments typically change a dozen or more settings from defaults: larger heap, faster compaction, higher file descriptor limits, and workload-appropriate thread pools.

This reference covers each configuration file and the settings that matter most.

## Configuration Files

| File | Purpose | Location |
|------|---------|----------|
| `cassandra.yaml` | Main configuration | `/etc/cassandra/` |
| `cassandra-env.sh` | Environment variables | `/etc/cassandra/` |
| `jvm.options` / `jvm11-server.options` | JVM settings | `/etc/cassandra/` |
| `cassandra-rackdc.properties` | DC/rack configuration | `/etc/cassandra/` |
| `logback.xml` | Logging configuration | `/etc/cassandra/` |

---

## Documentation Structure

### cassandra.yaml

- **[cassandra.yaml Overview](cassandra-yaml/index.md)** - Main configuration

### JVM Options

- **[JVM Tuning Overview](jvm-options/index.md)** - Heap and GC settings

### Snitch Configuration

- **[Snitch Overview](snitch-config/index.md)** - Topology awareness

### Guardrails

- **[Guardrails Reference](guardrails.md)** - Configurable limits to protect cluster stability (Cassandra 4.0+)

### Logging

- **[Logging Configuration (logback.xml)](logback.md)** - Log levels, rotation, and output configuration

---

## cassandra.yaml Quick Reference

### Essential Settings

```yaml
# Cluster identification
cluster_name: 'ProductionCluster'
num_tokens: 16

# Network
listen_address: 10.0.0.1
rpc_address: 10.0.0.1
native_transport_port: 9042
storage_port: 7000

# Seeds
seed_provider:
  - class_name: org.apache.cassandra.locator.SimpleSeedProvider
    parameters:
      - seeds: "10.0.0.1,10.0.0.2"

# Snitch
endpoint_snitch: GossipingPropertyFileSnitch

# Directories
data_file_directories:
  - /var/lib/cassandra/data
commitlog_directory: /var/lib/cassandra/commitlog
saved_caches_directory: /var/lib/cassandra/saved_caches
hints_directory: /var/lib/cassandra/hints
```

### Performance Settings

```yaml
# Concurrent operations
concurrent_reads: 32
concurrent_writes: 32
concurrent_counter_writes: 32
concurrent_materialized_view_writes: 32

# Compaction
# 4.0: compaction_throughput_mb_per_sec, 4.1+: compaction_throughput (e.g., 64MiB/s)
compaction_throughput_mb_per_sec: 64
concurrent_compactors: 2

# Memtable
memtable_heap_space_in_mb: 2048
memtable_offheap_space_in_mb: 2048
memtable_flush_writers: 2

# Commit log
commitlog_sync: periodic
# 4.0: _in_ms suffix, 4.1+: duration syntax (e.g., 10s)
commitlog_sync_period_in_ms: 10000
commitlog_segment_size_in_mb: 32
```

!!! note "Configuration Syntax Changes in 4.1+"
    Cassandra 4.1+ introduced duration literals (e.g., `10s`, `200ms`, `1h`) and data rate units (e.g., `64MiB/s`). The `_in_ms` and `_mb_per_sec` suffixes are deprecated but still accepted. See [cassandra.yaml](cassandra-yaml/index.md) for version-specific parameter names.

### Timeout Settings

```yaml
# 4.0 syntax shown; 4.1+ uses duration literals (e.g., 5s instead of 5000)
read_request_timeout_in_ms: 5000
write_request_timeout_in_ms: 2000
counter_write_request_timeout_in_ms: 5000
range_request_timeout_in_ms: 10000
truncate_request_timeout_in_ms: 60000
request_timeout_in_ms: 10000
```

### Security Settings

```yaml
# Authentication
authenticator: PasswordAuthenticator
authorizer: CassandraAuthorizer
role_manager: CassandraRoleManager

# Client encryption
client_encryption_options:
  enabled: true
  optional: false
  keystore: /etc/cassandra/conf/.keystore
  keystore_password: cassandra

# Server encryption
server_encryption_options:
  internode_encryption: all
  keystore: /etc/cassandra/conf/.keystore
  keystore_password: cassandra
  truststore: /etc/cassandra/conf/.truststore
  truststore_password: cassandra
```

---

## JVM Options Quick Reference

### Heap Settings

```bash
# jvm11-server.options

# Heap size (set both to same value)
-Xms16G
-Xmx16G

# Or for auto-sizing (not recommended for production)
# -XX:MaxRAMPercentage=50.0
```

### G1GC Settings (Recommended)

```bash
# Use G1GC
-XX:+UseG1GC

# Pause time target
-XX:MaxGCPauseMillis=500

# Other G1 options
-XX:G1RSetUpdatingPauseTimePercent=5
-XX:InitiatingHeapOccupancyPercent=70

# GC Logging
-Xlog:gc*:file=/var/log/cassandra/gc.log:time,uptime:filecount=10,filesize=10M
```

### ZGC Settings (JDK 17+)

```bash
# Use ZGC
-XX:+UseZGC
-XX:+ZGenerational

# ZGC options
-XX:SoftMaxHeapSize=28G  # Soft target (under -Xmx)
```

---

## OS-Level Configuration

### sysctl Settings

```bash
# /etc/sysctl.d/99-cassandra.conf

# Virtual memory
vm.max_map_count = 1048575
vm.swappiness = 1

# Network
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
```

### Limits

```bash
# /etc/security/limits.d/cassandra.conf

cassandra soft memlock unlimited
cassandra hard memlock unlimited
cassandra soft nofile 1048576
cassandra hard nofile 1048576
cassandra soft nproc 32768
cassandra hard nproc 32768
```

### Disable Swap

```bash
# Temporary
sudo swapoff -a

# Permanent
# Remove/comment swap entries in /etc/fstab
```

### Disable THP

```bash
echo never > /sys/kernel/mm/transparent_hugepage/enabled
echo never > /sys/kernel/mm/transparent_hugepage/defrag
```

---

## Configuration by Workload

### Read-Heavy Workload

```yaml
# More read threads
concurrent_reads: 64

# Higher key cache
key_cache_size_in_mb: 200

# Leveled compaction (better read performance)
# Set per-table via CQL

# Lower bloom filter FP rate
# Set per-table: bloom_filter_fp_chance = 0.01
```

### Write-Heavy Workload

```yaml
# More write threads
concurrent_writes: 64

# Larger memtables
memtable_heap_space_in_mb: 4096

# Higher compaction throughput
compaction_throughput_mb_per_sec: 128

# More compaction threads
concurrent_compactors: 4

# Periodic commit log sync
commitlog_sync: periodic
commitlog_sync_period_in_ms: 10000
```

### Time-Series Workload

```yaml
# Use TWCS per table (via CQL)
# TimeWindowCompactionStrategy with appropriate window

# Set TTL per table
# default_time_to_live

# Lower gc_grace for TTL data
# gc_grace_seconds: 86400  (per table)

# Disable key cache (usually not useful for time-series)
# key_cache_size_in_mb: 0
```

---

## Configuration Validation

### Check Current Config

```bash
# Via nodetool
nodetool getlogginglevels
nodetool getstreamthroughput
nodetool getcompactionthroughput

# Via CQL
SELECT * FROM system.local;
SELECT * FROM system_schema.keyspaces;
```

### Common Mistakes

| Mistake | Correct Approach |
|---------|------------------|
| Heap > 31GB | Keep heap ≤ 31GB (compressed oops) |
| swap enabled | Disable swap completely |
| listen_address = localhost | Use actual IP or 0.0.0.0 |
| Only 1-2 seeds | Use 2-3 seeds per DC |
| THP enabled | Disable THP |
| Low file limits | Set to 1M+ |

---

## Next Steps

- **[cassandra.yaml Deep Dive](cassandra-yaml/index.md)** - Every parameter
- **[JVM Tuning](jvm-options/index.md)** - Heap and GC
- **[Performance Tuning](../performance/index.md)** - Optimization guide
- **[Production Checklist](../../getting-started/production-checklist.md)** - Go-live prep