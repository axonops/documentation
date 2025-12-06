# Hardware Recommendations for Cassandra

Select and configure hardware for optimal Cassandra performance.

## CPU

### Requirements

| Environment | Cores | Notes |
|-------------|-------|-------|
| Development | 2-4 | Minimum viable |
| Production | 8-16 | Standard workloads |
| Heavy workloads | 16-32 | High throughput |

### Guidelines

- More cores = better concurrent request handling
- Higher clock speed benefits single-threaded compaction
- Prefer modern architectures (Intel Xeon, AMD EPYC)
- Enable hyperthreading for mixed workloads

## Memory (RAM)

### Sizing

| Data per Node | Minimum RAM | Recommended |
|---------------|-------------|-------------|
| < 100GB | 16GB | 32GB |
| 100-500GB | 32GB | 64GB |
| 500GB-1TB | 64GB | 128GB |
| > 1TB | 128GB | 256GB |

### Memory Distribution

```
Total RAM: 64GB
├── JVM Heap: 16GB (25%)
├── Off-heap: 8GB (12.5%)
└── OS Page Cache: 40GB (62.5%)
```

**Key Principle:** More RAM for page cache = faster reads

## Storage

### SSD (Recommended)

| Type | IOPS | Use Case |
|------|------|----------|
| NVMe | 100K+ | High performance |
| SATA SSD | 50K+ | Standard production |
| SAS SSD | 30K+ | Cost-effective |

### Configuration

```yaml
# Separate disks recommended:
# /var/lib/cassandra/data      - Data files (largest)
# /var/lib/cassandra/commitlog - Commit log (fast)
# /var/lib/cassandra/hints     - Hints
```

### Capacity Planning

```
Raw capacity needed = Data size × Replication Factor × 1.2 (overhead)

Example:
- 500GB data
- RF=3
- Capacity = 500GB × 3 × 1.2 = 1.8TB total cluster storage
```

### RAID

| RAID | Use Case | Notes |
|------|----------|-------|
| RAID 0 | Commitlog | Performance, no redundancy |
| RAID 10 | Data | Balance of performance and redundancy |
| JBOD | Data | Let Cassandra handle distribution |

## Network

### Requirements

| Environment | Bandwidth | Notes |
|-------------|-----------|-------|
| Single DC | 1 Gbps | Minimum |
| Production | 10 Gbps | Recommended |
| Heavy replication | 25+ Gbps | Multi-DC, high throughput |

### Latency

- Same rack: < 0.5ms
- Same DC: < 1ms
- Cross-DC: Plan for 20-100ms+

## Reference Configurations

### Development

```
CPU: 4 cores
RAM: 16GB
Storage: 256GB SSD
Network: 1 Gbps
```

### Small Production

```
CPU: 8 cores
RAM: 32GB
Storage: 1TB NVMe
Network: 10 Gbps
```

### Standard Production

```
CPU: 16 cores
RAM: 64GB
Storage: 2TB NVMe × 2 (JBOD)
Network: 10 Gbps
```

### High Performance

```
CPU: 32 cores
RAM: 128GB
Storage: 2TB NVMe × 4 (JBOD)
Network: 25 Gbps
```

## Cloud Instance Types

### AWS

| Workload | Instance | vCPU | RAM | Storage |
|----------|----------|------|-----|---------|
| Dev | m5.xlarge | 4 | 16GB | gp3 |
| Small | i3.2xlarge | 8 | 61GB | NVMe |
| Standard | i3.4xlarge | 16 | 122GB | NVMe |
| Heavy | i3.8xlarge | 32 | 244GB | NVMe |

### GCP

| Workload | Instance | vCPU | RAM |
|----------|----------|------|-----|
| Dev | n2-standard-4 | 4 | 16GB |
| Small | n2-highmem-8 | 8 | 64GB |
| Standard | n2-highmem-16 | 16 | 128GB |

### Azure

| Workload | Instance | vCPU | RAM |
|----------|----------|------|-----|
| Dev | Standard_D4s_v3 | 4 | 16GB |
| Small | Standard_L8s_v2 | 8 | 64GB |
| Standard | Standard_L16s_v2 | 16 | 128GB |

## Sizing Calculator

```
Nodes needed = (Data size × RF) / (Storage per node × 0.5)

Example:
- 2TB raw data
- RF = 3
- 1TB storage per node
- Nodes = (2TB × 3) / (1TB × 0.5) = 12 nodes
```

## Anti-Patterns

| Issue | Problem | Solution |
|-------|---------|----------|
| Spinning disks | Slow compaction, high latency | Use SSDs |
| Small heap | Frequent GC, instability | Proper sizing |
| Overprovisioned heap | Wasted RAM, long GC | Max 31GB |
| Network congestion | Timeouts, inconsistency | 10Gbps+ |
| Heterogeneous cluster | Uneven load | Uniform hardware |

---

## Next Steps

- **[OS Tuning](../os-tuning/index.md)** - Operating system optimization
- **[JVM Tuning](../jvm-tuning/index.md)** - JVM configuration
- **[Cloud Deployment](../../cloud/index.md)** - Cloud-specific guidance
