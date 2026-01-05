---
title: "Cassandra Replacing Nodes"
description: "Replace failed Cassandra nodes. Node replacement procedures using replace_address_first_boot with behavioral contracts."
meta:
  - name: keywords
    content: "Cassandra replace node, replace_address_first_boot, node replacement, hardware failure"
---

# Replacing Nodes

Node replacement substitutes a failed node with new hardware while preserving the cluster's token distribution. The replacement node inherits the dead node's token ranges and receives data from surviving replicas.

---

## When to Use Replacement

| Scenario | Use Replacement | Use Removenode + Add |
|----------|-----------------|----------------------|
| Hardware failure, same token config | Yes | No |
| Hardware failure, changing token count | No | Yes |
| Planned hardware upgrade | Either | Either |
| IP address must change | Yes | Yes |
| Datacenter restructuring | No | Yes |

### Replacement vs Remove + Add

| Aspect | Replacement | Remove + Add |
|--------|-------------|--------------|
| Streaming operations | 1 | 2 |
| Total duration | Shorter | Longer |
| Token distribution | Preserved | May change (vnodes) |
| Cleanup required | No | Yes |

---

## Prerequisites

The following conditions must be met:

| Requirement | Verification |
|-------------|--------------|
| Dead node must be recognized as down | `nodetool status` shows `DN` |
| Replacement hardware must be available | Same or better specs |
| Network connectivity to all nodes | Ports 7000, 7001, 9042 open |
| Same Cassandra version | Match cluster version exactly |
| Same token configuration | `num_tokens` must match dead node |

!!! warning "Version Compatibility"
    The replacement node must run the same Cassandra version as the cluster. Version mismatches cause schema conflicts and potential data corruption.

---

## Behavioral Contract

### Guarantees

- Replacement node receives all data for the dead node's token ranges
- Data is streamed from surviving replicas (not the dead node)
- Replacement node assumes the dead node's position in the ring
- Client topology awareness updates automatically after replacement

### Failure Semantics

| Scenario | Outcome | Recovery |
|----------|---------|----------|
| Replacement completes | Node joins ring with full data | None required |
| Streaming interrupted | Partial data on replacement | Clear data, restart replacement |
| Source replicas unavailable | Streaming stalls or fails | Wait for replica recovery |
| Insufficient replicas (RF=1) | Data loss | Cannot recover without backup |

---

## Replace with Same IP Address

Use this procedure when the replacement hardware can use the dead node's IP address.

### Step 1: Verify Dead Node Status

```bash
# From any live node
nodetool status

# Dead node should show DN (Down, Normal)
# Datacenter: dc1
# Status=Up/Down  State=Normal/Leaving/Joining/Moving
# UN  10.0.1.1  100 GB  256  ?  rack1
# DN  10.0.1.2  100 GB  256  ?  rack1  <-- Dead node
# UN  10.0.1.3  100 GB  256  ?  rack1
```

### Step 2: Record Dead Node Configuration

```bash
# Note from nodetool status:
# - IP address: 10.0.1.2
# - Token count: 256
# - Datacenter: dc1
# - Rack: rack1
```

### Step 3: Prepare Replacement Node

Install Cassandra with identical version and configure:

```yaml
# cassandra.yaml

cluster_name: 'ProductionCluster'  # Must match exactly
num_tokens: 256                    # Must match dead node

# Network - use dead node's IP
listen_address: 10.0.1.2
rpc_address: 10.0.1.2

# Seeds - use 2-3 live nodes (NOT the dead node)
seed_provider:
  - class_name: org.apache.cassandra.locator.SimpleSeedProvider
    parameters:
      - seeds: "10.0.1.1,10.0.1.3"

# Snitch must match cluster
endpoint_snitch: GossipingPropertyFileSnitch

# Do NOT set auto_bootstrap (replacement handles this)
```

Configure datacenter and rack:

```properties
# cassandra-rackdc.properties
dc=dc1
rack=rack1
```

### Step 4: Configure Replacement JVM Option

Add the replacement directive to JVM options:

```bash
# For Cassandra 4.0+: jvm-server.options or jvm11-server.options
# For Cassandra 3.x: jvm.options or cassandra-env.sh

-Dcassandra.replace_address_first_boot=10.0.1.2
```

Or via environment variable:

```bash
export JVM_OPTS="$JVM_OPTS -Dcassandra.replace_address_first_boot=10.0.1.2"
```

### Step 5: Start Replacement Node

```bash
# Ensure data directories are empty
sudo rm -rf /var/lib/cassandra/data/*
sudo rm -rf /var/lib/cassandra/commitlog/*
sudo rm -rf /var/lib/cassandra/saved_caches/*

# Start Cassandra
sudo systemctl start cassandra
```

### Step 6: Monitor Streaming Progress

```bash
# Watch node join
watch -n 10 'nodetool status'

# Monitor streaming
nodetool netstats

# Check logs for progress
tail -f /var/log/cassandra/system.log | grep -i "stream\|bootstrap\|replace"
```

### Step 7: Verify Completion

```bash
# Node should show UN
nodetool status

# Verify token ownership
nodetool ring | grep 10.0.1.2

# Check no active streaming
nodetool netstats
```

### Step 8: Remove JVM Option

After successful replacement, remove the `replace_address_first_boot` option:

```bash
# Edit jvm-server.options
# Remove: -Dcassandra.replace_address_first_boot=10.0.1.2

# Restart is optional but recommended
sudo systemctl restart cassandra
```

!!! warning "Remove the JVM Option"
    The `replace_address_first_boot` option must be removed after successful replacement. Leaving it in place causes issues if the node is restarted.

---

## Replace with Different IP Address

When the replacement node must use a different IP address:

### Configuration

```yaml
# cassandra.yaml on NEW node

# Use the NEW IP address
listen_address: 10.0.1.10  # New IP
rpc_address: 10.0.1.10     # New IP

# Seeds - live nodes only
seed_provider:
  - class_name: org.apache.cassandra.locator.SimpleSeedProvider
    parameters:
      - seeds: "10.0.1.1,10.0.1.3"
```

### JVM Option

Reference the OLD (dead) node's IP:

```bash
# Points to the dead node being replaced
-Dcassandra.replace_address_first_boot=10.0.1.2  # Dead node's IP
```

The replacement node uses its own IP but replaces the dead node's token ranges.

---

## Cassandra Version-Specific Behavior

| Version | Option | Notes |
|---------|--------|-------|
| 2.x - 3.x | `replace_address` | Deprecated; use `replace_address_first_boot` |
| 3.x+ | `replace_address_first_boot` | Only applies on first start; requires IP address |

!!! note "First Boot Only"
    The `_first_boot` suffix indicates the option only takes effect on the node's first startup. Subsequent restarts ignore it, preventing accidental re-replacement.

---

## Performance Tuning

### Accelerate Streaming

```yaml
# cassandra.yaml on replacement node

# Increase inbound streaming (default 200 Mbps)
stream_throughput_outbound_megabits_per_sec: 400

# Cassandra 4.0+: stream entire SSTables (faster)
stream_entire_sstables: true
```

On source nodes:

```bash
# Temporarily increase outbound streaming
nodetool setstreamthroughput 400
```

### Duration Estimates

| Data to Stream | 200 Mbps | 400 Mbps |
|----------------|----------|----------|
| 100 GB | 1 hour | 30 min |
| 500 GB | 5 hours | 2.5 hours |
| 1 TB | 10 hours | 5 hours |
| 2 TB | 20 hours | 10 hours |

---

## Restore from Backup

For large datasets, restoring from an AxonOps backup may be faster than streaming from replicas.

### When to Use Backup Restore

| Scenario | Recommended Approach |
|----------|---------------------|
| Small dataset (< 500 GB) | Standard replacement (streaming) |
| Large dataset (> 1 TB) | Consider backup restore |
| Recent backup available (< 3 hours) | Backup restore with hints |
| No recent backup | Standard replacement |

### Procedure

**Step 1: Prepare replacement node**

Configure the node as described in [Replace with Same IP Address](#replace-with-same-ip-address) or [Replace with Different IP Address](#replace-with-different-ip-address), but do not start Cassandra yet.

**Step 2: Restore data from backup**

Restore the full SSTable backup to the new node's data directory:

```bash
# Restore from AxonOps backup
# See AxonOps documentation for specific restore commands
axonops-restore --target /var/lib/cassandra/data
```

**Step 3: Start replacement node**

```bash
sudo systemctl start cassandra
```

The node joins the ring with restored data. If the backup is recent, minimal streaming occurs.

### Hint-Based Recovery

If the replacement occurs within the hint window (default 3 hours), hints stored on other nodes are delivered to the replacement node:

- Other nodes retain hints for the dead node during the outage
- When the replacement joins, hints are replayed automatically
- Data written during the outage is recovered via hints

### Required: Run Full Repair

After backup restore, a full repair must run to recover data not captured in the backup:

```bash
nodetool repair -full
```

**Data requiring repair:**

| Data Type | Why Repair is Needed |
|-----------|---------------------|
| Commitlog batch window | Up to 10 seconds of acknowledged writes not yet synced (`commitlog_sync_period_in_ms`) |
| Memtable data | Unflushed data at backup time |
| Writes after backup | Data written between backup and failure |
| Sudden node loss | No clean shutdown to flush memtables |

!!! note "Commitlog Sync Window"
    By default, Cassandra syncs commitlogs every 10 seconds (`commitlog_sync_period_in_ms: 10000`). Even with a clean shutdown, writes acknowledged within this window may not be persisted. This data must be recovered from replicas via repair.

!!! warning "Repair is Mandatory"
    Skipping repair after backup restore leaves the node with stale data. The node serves reads but may return outdated values for data written after the backup.

### Backup Restore vs Streaming

| Aspect | Backup Restore | Streaming |
|--------|----------------|-----------|
| Speed (large data) | Faster (local I/O) | Slower (network) |
| Cluster impact | Minimal | Source nodes load |
| Data freshness | Requires repair | Current data |
| Hint recovery | Within hint window | Automatic |
| Complexity | Requires backup infrastructure | Built-in |

---

## Troubleshooting

### Replacement Fails to Start

**Symptoms:** Node won't start or immediately exits

**Common causes:**

| Cause | Solution |
|-------|----------|
| Dead node not recognized | Verify `nodetool status` shows DN |
| Wrong IP in replace option | Correct the `replace_address_first_boot` value |
| Version mismatch | Install matching Cassandra version |
| Data directory not empty | Clear `/var/lib/cassandra/*` |

```bash
# Check logs for specific errors
grep -i "error\|replace\|bootstrap" /var/log/cassandra/system.log | head -50
```

### Replacement Streaming Stalled

**Symptoms:** Node stuck in `UJ` state, no streaming progress

```bash
# Check streaming status
nodetool netstats

# Check source node health
nodetool status
```

**Solutions:**

1. Verify network connectivity to all nodes
2. Check disk space on source and target
3. Increase `streaming_socket_timeout_in_ms` for large partitions:

```yaml
# cassandra.yaml
streaming_socket_timeout_in_ms: 86400000  # 24 hours
```

### Replacement Interrupted

If replacement is interrupted mid-stream:

```bash
# Stop Cassandra
sudo systemctl stop cassandra

# Clear all data
sudo rm -rf /var/lib/cassandra/data/*
sudo rm -rf /var/lib/cassandra/commitlog/*
sudo rm -rf /var/lib/cassandra/saved_caches/*

# Ensure JVM option still present
# Restart
sudo systemctl start cassandra
```

### Token Mismatch After Replacement

**Symptoms:** Replacement node has different token count

**Cause:** `num_tokens` in cassandra.yaml doesn't match the dead node

**Solution:** The replacement must be restarted with correct `num_tokens`:

```bash
# Stop node
sudo systemctl stop cassandra

# Clear data
sudo rm -rf /var/lib/cassandra/data/*

# Fix cassandra.yaml
num_tokens: 256  # Match original

# Restart
sudo systemctl start cassandra
```

---

## Post-Replacement Tasks

### Verify Cluster Health

```bash
# All nodes UN
nodetool status

# Schema agreement
nodetool describecluster

# Token distribution correct
nodetool ring | head -30
```

### Update Infrastructure

| Task | Action |
|------|--------|
| Monitoring | Update node IP if changed |
| Load balancers | Update IP if changed |
| Seed lists | Update if replacement is a seed |
| DNS | Update records if applicable |

### Optional: Run Repair

While not strictly required after replacement, repair ensures full consistency:

```bash
# Repair the replacement node's ranges
nodetool repair -pr
```

---

## Related Documentation

- **[Cluster Management Overview](index.md)** - Operation selection guide
- **[Removing Nodes](removing-nodes.md)** - Alternative removal methods
- **[Adding Nodes](adding-nodes.md)** - Bootstrap procedures
- **[Node Lifecycle](../../architecture/cluster-management/node-lifecycle.md)** - State transitions
