---
title: "Cassandra cassandra.yaml Configuration"
description: "Apache Cassandra cassandra.yaml configuration documentation including parameter reference and configuration guide."
meta:
  - name: keywords
    content: "cassandra.yaml, Cassandra configuration, config reference"
---

# cassandra.yaml Configuration

The `cassandra.yaml` file is the primary configuration file for Apache Cassandra. It controls cluster identity, network settings, storage paths, performance tuning, security, and operational behavior.

---

## Documentation

| Document | Description |
|----------|-------------|
| **[Parameter Reference](reference.md)** | Canonical reference of all cassandra.yaml parameters with types, defaults, version compatibility, and brief descriptions |
| **[Configuration Guide](guide.md)** | In-depth explanations, best practices, common mistakes, and production recommendations |

---

## File Location

| Installation Method | Default Path |
|---------------------|--------------|
| Package (apt/yum) | `/etc/cassandra/cassandra.yaml` |
| Tarball | `$CASSANDRA_HOME/conf/cassandra.yaml` |
| Docker | `/etc/cassandra/cassandra.yaml` |
| Kubernetes | Typically mounted as ConfigMap |

---

## Version Compatibility

### Parameter Format Changes (Cassandra 4.1+)

Cassandra 4.1 introduced human-readable formats for duration, data size, and data rate parameters.

| Format Type | Pre-4.1 Example | 4.1+ Example |
|-------------|-----------------|--------------|
| Duration | `read_request_timeout_in_ms: 5000` | `read_request_timeout: 5s` |
| Data size | `commitlog_segment_size_in_mb: 32` | `commitlog_segment_size: 32MiB` |
| Data rate | `compaction_throughput_mb_per_sec: 64` | `compaction_throughput: 64MiB/s` |

!!! note "Backward Compatibility"
    Cassandra 4.1+ accepts both old and new formats. Existing configurations continue to work without modification when upgrading.

See the **[Parameter Reference](reference.md)** for version-specific information on each parameter.

---

## Quick Start

### Minimum Required Settings

Before starting a production cluster, these settings must be configured:

```yaml
# Cluster identity (cannot change after data written)
cluster_name: 'MyCluster'

# Network binding
listen_address: <node_ip>
rpc_address: <node_ip>  # Or 0.0.0.0 with broadcast_rpc_address set

# Seed nodes for cluster discovery
seed_provider:
  - class_name: org.apache.cassandra.locator.SimpleSeedProvider
    parameters:
      - seeds: "seed1_ip,seed2_ip"

# Topology awareness
endpoint_snitch: GossipingPropertyFileSnitch
```

!!! danger "Do Not Use Defaults in Production"
    The default `cluster_name: 'Test Cluster'` and `listen_address: localhost` are intended for local development only. Using defaults in production will cause operational issues.

---

## Configuration Categories

| Category | Key Parameters | Reference |
|----------|----------------|-----------|
| **Cluster Identity** | `cluster_name`, `num_tokens`, `allocate_tokens_for_local_replication_factor` | [Reference](reference.md#cluster-configuration) |
| **Network** | `listen_address`, `rpc_address`, `broadcast_address`, ports | [Reference](reference.md#network-listen-addresses) |
| **Storage** | `data_file_directories`, `commitlog_directory`, `hints_directory` | [Reference](reference.md#data-directories) |
| **Performance** | `concurrent_reads`, `concurrent_writes`, memtable settings | [Reference](reference.md#concurrent-operations) |
| **Commit Log** | `commitlog_sync`, `commitlog_segment_size`, `commitlog_total_space` | [Reference](reference.md#commit-log) |
| **Compaction** | `compaction_throughput`, `concurrent_compactors` | [Reference](reference.md#compaction) |
| **Caching** | `key_cache_size`, `row_cache_size`, `counter_cache_size` | [Reference](reference.md#caching) |
| **Timeouts** | `read_request_timeout`, `write_request_timeout`, `range_request_timeout` | [Reference](reference.md#request-timeouts) |
| **Hinted Handoff** | `hinted_handoff_enabled`, `max_hint_window`, `hinted_handoff_throttle` | [Reference](reference.md#hinted-handoff) |
| **Security** | `authenticator`, `authorizer`, encryption options | [Reference](reference.md#security-authentication) |
| **Gossip** | `seed_provider`, `endpoint_snitch`, `phi_convict_threshold` | [Reference](reference.md#snitch-configuration) |

---

## Related Documentation

- **[JVM Options](../jvm-options/index.md)** - Heap and garbage collection configuration
- **[Snitch Configuration](../snitch-config/index.md)** - Datacenter and rack topology
- **[Security Configuration](../../../security/index.md)** - Authentication, authorization, encryption