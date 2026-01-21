---
title: "Operating System Tuning for Cassandra"
description: "Operating system tuning for Cassandra. Linux kernel and file system settings."
meta:
  - name: keywords
    content: "Cassandra OS tuning, Linux tuning, kernel settings"
search:
  boost: 3
---

# Operating System Tuning for Cassandra

Optimize your Linux operating system for Cassandra performance.

## Disk I/O Settings

### Scheduler

```bash
# Check current scheduler
cat /sys/block/sda/queue/scheduler

# Set to deadline or noop for SSDs
echo deadline > /sys/block/sda/queue/scheduler
# Or for NVMe
echo none > /sys/block/nvme0n1/queue/scheduler
```

### Read-Ahead

```bash
# Set read-ahead (8KB for SSDs, 64KB for HDDs)
blockdev --setra 8 /dev/sda

# Verify
blockdev --getra /dev/sda
```

### Persistent Configuration

```bash
# /etc/udev/rules.d/60-cassandra.rules
ACTION=="add|change", KERNEL=="sd[a-z]", ATTR{queue/scheduler}="deadline"
ACTION=="add|change", KERNEL=="sd[a-z]", ATTR{queue/read_ahead_kb}="8"
ACTION=="add|change", KERNEL=="nvme[0-9]*", ATTR{queue/scheduler}="none"
```

## Memory Settings

### Swap

```bash
# Disable swap (recommended)
swapoff -a

# Or set swappiness to minimum
echo 0 > /proc/sys/vm/swappiness

# Persistent
echo "vm.swappiness = 0" >> /etc/sysctl.conf
```

### Zone Reclaim

```bash
# Disable zone reclaim for NUMA
echo 0 > /proc/sys/vm/zone_reclaim_mode
```

### Dirty Pages

```bash
# /etc/sysctl.conf
vm.dirty_background_ratio = 5
vm.dirty_ratio = 80
```

## Network Tuning

### TCP Settings

```bash
# /etc/sysctl.conf

# Increase socket buffer sizes
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.core.rmem_default = 16777216
net.core.wmem_default = 16777216
net.core.optmem_max = 40960

# TCP buffers
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216

# Connection handling
net.core.netdev_max_backlog = 50000
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 30000

# Timeouts
net.ipv4.tcp_fin_timeout = 10
net.ipv4.tcp_keepalive_time = 60
net.ipv4.tcp_keepalive_probes = 3
net.ipv4.tcp_keepalive_intvl = 10
```

### Apply Changes

```bash
sysctl -p
```

## File Descriptors

### Limits

```bash
# /etc/security/limits.conf
cassandra soft nofile 100000
cassandra hard nofile 100000
cassandra soft nproc 32768
cassandra hard nproc 32768
cassandra soft memlock unlimited
cassandra hard memlock unlimited
cassandra soft as unlimited
cassandra hard as unlimited
```

### Verify

```bash
# As cassandra user
ulimit -n   # File descriptors
ulimit -u   # Processes
ulimit -l   # Memory lock
```

## Transparent Huge Pages

**Disable THP** - causes latency spikes with Cassandra.

```bash
# Check current status
cat /sys/kernel/mm/transparent_hugepage/enabled
cat /sys/kernel/mm/transparent_hugepage/defrag

# Disable
echo never > /sys/kernel/mm/transparent_hugepage/enabled
echo never > /sys/kernel/mm/transparent_hugepage/defrag
```

### Persistent Disable

```bash
# /etc/rc.local or systemd service
if test -f /sys/kernel/mm/transparent_hugepage/enabled; then
    echo never > /sys/kernel/mm/transparent_hugepage/enabled
fi
if test -f /sys/kernel/mm/transparent_hugepage/defrag; then
    echo never > /sys/kernel/mm/transparent_hugepage/defrag
fi
```

## CPU Settings

### CPU Governor

```bash
# Set to performance
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    echo performance > $cpu
done

# Verify
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
```

### NUMA

```bash
# Verify NUMA topology
numactl --hardware

# Run Cassandra with NUMA awareness
numactl --interleave=all cassandra
```

## Filesystem

Filesystem selection significantly impacts Cassandra performance, particularly for commit log operations. The choice between XFS and ext4 depends on workload characteristics and Linux distribution.

**Quick recommendations:**

| Use Case | Filesystem | Notes |
|----------|------------|-------|
| **Data directories** | XFS | Optimized for large files and parallel I/O |
| **Commit logs** | ext4 or XFS + compression | ext4 has better memory-mapped I/O performance |

→ [Filesystem Selection Guide](filesystem.md) - Complete architecture comparison, benchmarks, and configuration

**Basic mount options:**

```bash
# XFS for data
/dev/sdb1 /var/lib/cassandra/data xfs defaults,noatime,nodiratime 0 2

# ext4 for commit logs
/dev/sdc1 /var/lib/cassandra/commitlog ext4 defaults,noatime,nodiratime 0 2
```

## Complete Configuration Script

```bash
#!/bin/bash
# cassandra-os-tuning.sh

# Disable swap
swapoff -a

# Disable THP
echo never > /sys/kernel/mm/transparent_hugepage/enabled
echo never > /sys/kernel/mm/transparent_hugepage/defrag

# Set swappiness
sysctl -w vm.swappiness=0

# Disk scheduler (adjust device names)
echo deadline > /sys/block/sda/queue/scheduler

# Apply sysctl settings
sysctl -p

echo "OS tuning applied"
```

---

## Next Steps

- **[Filesystem Selection](filesystem.md)** - XFS vs ext4 architecture and recommendations
- **[JVM Tuning](../jvm-tuning/index.md)** - JVM optimization
- **[Hardware](../hardware/index.md)** - Hardware sizing
- **[Performance Overview](../index.md)** - Performance guide
