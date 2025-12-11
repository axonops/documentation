# nodetool setstreamthroughput

Sets the streaming throughput limit for inter-node data transfers.

---

## Synopsis

```bash
nodetool [connection_options] setstreamthroughput <throughput_mb_per_sec>
```

## Description

`nodetool setstreamthroughput` controls the maximum rate at which data can be streamed between Cassandra nodes. Streaming occurs during:

- **Repair operations** - Transferring data to synchronize replicas
- **Bootstrap** - New nodes receiving data from existing nodes
- **Rebuild** - Nodes rebuilding data from other data centers
- **Decommission** - Nodes transferring data before leaving cluster
- **Node replacement** - Replacement nodes receiving data

This setting affects outgoing streams from the node where the command is executed.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `throughput_mb_per_sec` | Maximum streaming rate in MB/s. Use `0` for unlimited |

---

## Examples

### Set Throughput

```bash
nodetool setstreamthroughput 200
```

### Unlimited Streaming

```bash
nodetool setstreamthroughput 0
```

!!! warning "Unlimited Streaming"
    Setting to 0 removes all throttling. Use with caution as it may saturate network bandwidth and impact other operations.

### Verify Setting

```bash
nodetool setstreamthroughput 200
nodetool getstreamthroughput
# Output: Current stream throughput: 200 MB/s
```

---

## When to Use

### Speed Up Maintenance Operations

During scheduled maintenance windows:

```bash
# Increase throughput for faster repair
nodetool setstreamthroughput 400

# Run repair
nodetool repair -pr my_keyspace

# Restore normal throughput
nodetool setstreamthroughput 200
```

### Reduce Network Impact

During high traffic periods:

```bash
# Reduce streaming to prioritize client traffic
nodetool setstreamthroughput 100
```

### Bootstrap Optimization

When adding new nodes:

```bash
# On seed nodes (streaming sources)
nodetool setstreamthroughput 300

# Monitor bootstrap progress
nodetool netstats
```

### Decommission Acceleration

Speed up node removal:

```bash
# Before decommissioning
nodetool setstreamthroughput 400

# Start decommission
nodetool decommission

# Monitor progress
watch nodetool netstats
```

### Multi-DC Considerations

Adjust for cross-datacenter rebuilds:

```bash
# Lower throughput for WAN links
nodetool setstreamthroughput 50

# Start rebuild
nodetool rebuild dc1

# Monitor
nodetool netstats
```

---

## Recommended Values

### By Scenario

| Scenario | Throughput | Rationale |
|----------|------------|-----------|
| Default | 200 MB/s | Balanced default |
| High-performance network | 400-800 MB/s | Fast 10GbE+ networks |
| Shared network | 100-200 MB/s | Avoid impacting other traffic |
| Maintenance window | 400+ MB/s | Prioritize streaming |
| Cross-DC (WAN) | 50-100 MB/s | Limited bandwidth |
| During high load | 100 MB/s | Prioritize client traffic |

### By Network Type

| Network | Recommended Range |
|---------|-------------------|
| 1 GbE | 50-100 MB/s |
| 10 GbE | 200-500 MB/s |
| 25 GbE | 400-800 MB/s |
| AWS (same AZ) | 200-400 MB/s |
| AWS (cross AZ) | 100-200 MB/s |
| Cross region/WAN | 50-100 MB/s |

---

## Workflow: Rolling Repair with Optimized Streaming

```bash
#!/bin/bash
# repair_with_tuned_streaming.sh

# Store original value
original=$(nodetool getstreamthroughput | awk '{print $4}')
echo "Original streaming throughput: $original MB/s"

# Increase for repair
echo "Increasing streaming throughput to 400 MB/s"
nodetool setstreamthroughput 400

# Run repair
echo "Starting repair..."
nodetool repair -pr my_keyspace

# Restore original
echo "Restoring original throughput: $original MB/s"
nodetool setstreamthroughput $original

echo "Repair complete"
```

---

## Workflow: Bootstrap New Node

On existing nodes (streaming sources):

```bash
# 1. Check current settings
nodetool getstreamthroughput

# 2. Increase for bootstrap
nodetool setstreamthroughput 400

# 3. (Bootstrap starts on new node)

# 4. Monitor streaming
watch 'nodetool netstats | head -20'

# 5. After bootstrap completes, restore
nodetool setstreamthroughput 200
```

---

## Relationship with Other Settings

### Streaming vs Compaction

Both affect disk I/O and should be considered together:

| Setting | Affects | Command |
|---------|---------|---------|
| Stream throughput | Node-to-node transfers | `setstreamthroughput` |
| Compaction throughput | Local SSTable processing | `setcompactionthroughput` |

```bash
# Check both settings
echo "Stream: $(nodetool getstreamthroughput)"
echo "Compaction: $(nodetool getcompactionthroughput)"
```

### Total I/O Budget

Consider combined impact:

```bash
# During heavy streaming
nodetool setstreamthroughput 300
nodetool setcompactionthroughput 32  # Reduce to free I/O for streaming

# After streaming completes
nodetool setstreamthroughput 200
nodetool setcompactionthroughput 64  # Restore normal compaction
```

---

## Monitoring Streaming

### Check Current Activity

```bash
nodetool netstats
```

Output:
```
Mode: NORMAL
Not sending any streams.
Read Repair Statistics:
Attempted: 1234
Mismatch (Blocking): 56
Mismatch (Background): 78
Pool Name                    Active   Pending      Completed   Dropped
Large messages                    0         0          12345         0
Small messages                    0         0         678901         0
```

### During Active Streaming

```bash
nodetool netstats
```

Output during bootstrap/repair:
```
Mode: NORMAL
Receiving from: /192.168.1.101
  /192.168.1.101
    Receiving 15 files, 2.3 GB total. Already received 1.1 GB, at 45.2 MB/s
      my_keyspace/my_table
Sending to: /192.168.1.102
  /192.168.1.102
    Sending 10 files, 1.8 GB total. Already sent 900 MB, at 38.5 MB/s
```

### Monitor Progress

```bash
# Continuous monitoring
watch -n 5 'nodetool netstats | grep -E "Receiving|Sending|MB/s"'
```

---

## Persistence

### Runtime Changes

Changes made with `setstreamthroughput` are **not persistent** and reset on node restart.

### Permanent Configuration

To persist the setting, edit `cassandra.yaml`:

```yaml
# Throttle inter-datacenter streaming in MB/s
stream_throughput_outbound_megabits_per_sec: 200

# Note: This setting is in Mb/s (megabits), not MB/s (megabytes)
# 200 Mb/s ≈ 25 MB/s
```

!!! warning "Units Difference"
    `cassandra.yaml` uses megabits per second (Mb/s), while `nodetool` uses megabytes per second (MB/s).

    Conversion: `MB/s × 8 = Mb/s`

### Applying Persistent Changes

```bash
# Edit cassandra.yaml
vim /etc/cassandra/cassandra.yaml

# Change takes effect after restart
systemctl restart cassandra

# Or apply at runtime (temporary)
nodetool setstreamthroughput 200
```

---

## Troubleshooting

### Streaming Too Slow

If bootstrap/repair taking too long:

```bash
# Check current limit
nodetool getstreamthroughput

# Check actual rate
nodetool netstats | grep "MB/s"

# If rate << limit, bottleneck is elsewhere
# Check: disk I/O, network, source node load

# Increase limit
nodetool setstreamthroughput 400
```

### Network Saturation

If streaming impacts client traffic:

```bash
# Reduce streaming throughput
nodetool setstreamthroughput 100

# Verify client latencies improve
nodetool proxyhistograms
```

### Streaming Fails

If streams fail or timeout:

```bash
# Check streaming status
nodetool netstats

# Check for errors in logs
grep -i stream /var/log/cassandra/system.log | tail -20

# Try reducing throughput (too fast can cause issues)
nodetool setstreamthroughput 100
```

---

## Cluster-Wide Management

### Apply to All Nodes

```bash
for node in node1 node2 node3; do
    echo "Setting streaming throughput on $node"
    nodetool -h $node setstreamthroughput 200
done
```

### Verify Cluster Settings

```bash
for node in node1 node2 node3; do
    echo -n "$node: "
    nodetool -h $node getstreamthroughput
done
```

---

## Automation Script

```bash
#!/bin/bash
# adjust_streaming.sh - Adjust streaming throughput cluster-wide

THROUGHPUT="${1:-200}"
NODES=$(nodetool status | grep "^UN" | awk '{print $2}')

echo "Setting streaming throughput to $THROUGHPUT MB/s on all nodes"
echo "=============================================="

for node in $NODES; do
    echo -n "$node: "
    nodetool -h $node setstreamthroughput $THROUGHPUT 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "OK"
    else
        echo "FAILED"
    fi
done

echo ""
echo "Verification:"
for node in $NODES; do
    echo -n "$node: "
    nodetool -h $node getstreamthroughput 2>/dev/null | awk '{print $4 " " $5}'
done
```

---

## Best Practices

!!! tip "Streaming Throughput Guidelines"

    1. **Know your network** - Set appropriate limits for your bandwidth
    2. **Adjust for operations** - Increase during maintenance windows
    3. **Monitor actively** - Watch `netstats` during streaming operations
    4. **Balance with compaction** - Consider total I/O budget
    5. **Test before production** - Validate settings in non-production first
    6. **Document changes** - Log when and why throughput was adjusted
    7. **Cluster consistency** - Use similar settings across nodes
    8. **WAN awareness** - Use lower settings for cross-DC operations

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [netstats](netstats.md) | Monitor streaming activity |
| [repair](repair.md) | Triggers streaming |
| [rebuild](rebuild.md) | Triggers cross-DC streaming |
| [decommission](decommission.md) | Triggers outgoing streams |
| [setcompactionthroughput](setcompactionthroughput.md) | Related I/O throttle |
| [getcompactionthroughput](getcompactionthroughput.md) | View compaction throttle |
