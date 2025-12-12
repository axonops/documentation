---
description: "Linux OS tuning for Cassandra. Swappiness, zone_reclaim, transparent huge pages, and limits."
meta:
  - name: keywords
    content: "Linux tuning, Cassandra OS config, swappiness, THP, vm.max_map_count"
---

# Linux Memory Configuration

Linux kernel settings can impact Cassandra memory behavior. Most settings have sensible defaults, but a few adjustments are recommended for optimal performance.

---

## Swap

Swap allows the kernel to move inactive memory pages to disk, freeing RAM for other uses. For Cassandra, swapping is problematic because:

- Swapped JVM pages cause unpredictable latency spikes
- GC performance degrades severely when heap is partially swapped
- Cassandra's memory access patterns don't benefit from swap

**Recommended settings:**

```bash
# Minimize swapping (0-1 recommended for Cassandra)
# 0 = swap only to avoid OOM, 1 = minimal swap
sudo sysctl vm.swappiness=1

# Make permanent
echo "vm.swappiness = 1" | sudo tee -a /etc/sysctl.conf
```

| vm.swappiness | Behavior |
|---------------|----------|
| 0 | Swap only to avoid OOM killer |
| 1 | Minimal swapping (recommended) |
| 10 | Light swapping |
| 60 | Default, moderate swapping |

!!! note "Swap vs No Swap"
    Some guides recommend disabling swap entirely. However, keeping swap enabled with `vm.swappiness=1` provides a safety net—the OOM killer is more disruptive than brief swap usage during memory pressure.

---

## Transparent Huge Pages (THP)

Transparent Huge Pages is a Linux feature that automatically manages large memory pages (2MB instead of 4KB). While THP can improve performance for some workloads, it causes problems for Cassandra:

- Memory allocation latency spikes during defragmentation
- Unpredictable pause times unrelated to GC
- Memory fragmentation over time

**Disable THP:**

```bash
# Check current status
cat /sys/kernel/mm/transparent_hugepage/enabled
cat /sys/kernel/mm/transparent_hugepage/defrag

# Disable at runtime
echo never | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
echo never | sudo tee /sys/kernel/mm/transparent_hugepage/defrag

# Make permanent (add to /etc/rc.local or systemd unit)
```

For systemd-based systems, create `/etc/systemd/system/disable-thp.service`:

```ini
[Unit]
Description=Disable Transparent Huge Pages

[Service]
Type=oneshot
ExecStart=/bin/sh -c "echo never > /sys/kernel/mm/transparent_hugepage/enabled"
ExecStart=/bin/sh -c "echo never > /sys/kernel/mm/transparent_hugepage/defrag"

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable disable-thp
sudo systemctl start disable-thp
```

!!! warning "THP Must Be Disabled"
    Cassandra will log a warning at startup if THP is enabled. Performance issues caused by THP can be difficult to diagnose—disable it proactively.

---

## Memory Map Limits

Cassandra uses memory-mapped files for SSTable access. The kernel limits the number of memory mappings per process.

```bash
# Check current limit
cat /proc/sys/vm/max_map_count

# Increase if needed (default 65530 is usually sufficient)
sudo sysctl vm.max_map_count=1048575

# Make permanent
echo "vm.max_map_count = 1048575" | sudo tee -a /etc/sysctl.conf
```

Increase `vm.max_map_count` if Cassandra logs errors about memory mapping failures, particularly with many SSTables.

---

## Zone Reclaim Mode

On NUMA systems, zone reclaim mode controls whether the kernel reclaims memory from local zones before allocating from remote zones.

```bash
# Disable zone reclaim (recommended for databases)
sudo sysctl vm.zone_reclaim_mode=0

# Make permanent
echo "vm.zone_reclaim_mode = 0" | sudo tee -a /etc/sysctl.conf
```

---

## NUMA Considerations

On multi-socket servers with Non-Uniform Memory Access (NUMA), memory access latency varies depending on which CPU socket allocated the memory.

**Options:**

1. **Interleave memory** (simple, recommended for most cases):
   ```bash
   numactl --interleave=all cassandra
   ```

2. **Bind to single node** (if Cassandra fits in one node's memory):
   ```bash
   numactl --cpunodebind=0 --membind=0 cassandra
   ```

3. **Let JVM handle it** (modern JVMs are NUMA-aware):
   ```bash
   # jvm-server.options
   -XX:+UseNUMA
   ```

---

## Recommended Kernel Settings

```bash
# /etc/sysctl.conf additions for Cassandra

# Minimize swapping
vm.swappiness = 1

# Increase memory map limit
vm.max_map_count = 1048575

# Disable zone reclaim
vm.zone_reclaim_mode = 0

# Network settings (optional, for high throughput)
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
```

Apply changes:
```bash
sudo sysctl -p
```

---

## Related Documentation

- **[JVM](jvm.md)** - JVM configuration and garbage collection
- **[Cassandra Memory](memory.md)** - Heap, off-heap, and page cache
