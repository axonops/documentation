---
title: "Cassandra Add Node"
description: "Add node troubleshooting playbook. Debug node bootstrap issues."
meta:
  - name: keywords
    content: "add node troubleshooting, bootstrap issues, node problems"
search:
  boost: 3
---

# Add Node

Adding a node (bootstrapping) expands cluster capacity by introducing a new node that receives a portion of the existing data.

---

## Prerequisites

- New node with Cassandra installed (same version as cluster)
- Network connectivity to existing nodes (ports 7000, 9042, 7199)
- Sufficient disk space for data share
- `cassandra.yaml` configured with correct cluster name and seeds

---

## Pre-Bootstrap Checklist

### Step 1: Verify Cluster Health

```bash
# On existing node
nodetool status
```

All nodes should show `UN` (Up/Normal).

### Step 2: Check for Running Operations

```bash
nodetool compactionstats
nodetool netstats
```

Avoid bootstrapping during heavy compaction or repairs.

### Step 3: Prepare New Node

On new node:

```bash
# Verify Cassandra is installed
cassandra -v

# Verify configuration
grep -E "cluster_name|seeds|listen_address" /etc/cassandra/cassandra.yaml
```

**Required cassandra.yaml settings:**

```yaml
cluster_name: 'MyCluster'  # Must match existing cluster
seeds: "existing-node1,existing-node2"  # 2-3 existing nodes
listen_address: <new-node-ip>
rpc_address: <new-node-ip>  # Or 0.0.0.0
auto_bootstrap: true  # Default, ensures data streaming
```

### Step 4: Clear Data Directories (If Reusing Hardware)

```bash
sudo rm -rf /var/lib/cassandra/data/*
sudo rm -rf /var/lib/cassandra/commitlog/*
sudo rm -rf /var/lib/cassandra/saved_caches/*
sudo rm -rf /var/lib/cassandra/hints/*
```

---

## Bootstrap Procedure

### Step 1: Start Cassandra on New Node

```bash
sudo systemctl start cassandra

# Monitor startup
tail -f /var/log/cassandra/system.log
```

### Step 2: Monitor Bootstrap Progress

On any node:

```bash
nodetool status
```

New node will show as `UJ` (Up/Joining) during bootstrap.

```bash
# On new node - watch streaming
nodetool netstats
```

### Step 3: Wait for Completion

Bootstrap can take hours. The node is not fully operational until complete.

```bash
# Monitor from existing node
watch -n 60 'nodetool status'
```

### Step 4: Verify Completion

```bash
nodetool status
```

New node should show `UN` (Up/Normal).

### Step 5: Run Cleanup on Existing Nodes

After successful bootstrap, run cleanup to remove data that moved to new node:

```bash
# On each existing node
nodetool cleanup

# Or cleanup specific keyspace
nodetool cleanup my_keyspace
```

!!! info "Cleanup Timing"
    Cleanup should be run after bootstrap completes but before the next repair. It removes data that no longer belongs to the node.

---

## Troubleshooting

### Bootstrap Never Starts

**Check logs:**
```bash
grep -i "bootstrap\|gossip\|schema" /var/log/cassandra/system.log | tail -50
```

**Common causes:**
- Wrong cluster name → Fix in cassandra.yaml
- Cannot reach seeds → Check network connectivity
- Schema disagreement → Fix on existing cluster first

### Bootstrap Fails Mid-Way

```bash
# Check reason
grep -i "error\|failed" /var/log/cassandra/system.log | tail -50

# Common fixes:
# 1. Clear data and retry
sudo systemctl stop cassandra
sudo rm -rf /var/lib/cassandra/data/*
sudo systemctl start cassandra

# 2. If disk full on source nodes
nodetool clearsnapshot --all  # On source nodes
```

### Bootstrap Very Slow

```bash
# Check streaming throughput
nodetool getstreamthroughput

# Increase if network allows
nodetool setstreamthroughput 400  # MB/s
```

### Node Joins but Shows Wrong Token Range

This may indicate `initial_token` is set incorrectly or `auto_bootstrap` was false.

```bash
# Check token assignment
nodetool ring | grep <new-node-ip>

# May need to decommission and re-add with correct settings
```

---

## Streaming Performance

### Speed Up Bootstrap

On source and target nodes:

```bash
# Increase stream throughput (default usually 200 Mbps)
nodetool setstreamthroughput 400
```

### Monitor Streaming

```bash
# On new node
nodetool netstats

# Watch for:
# - Receiving from multiple nodes
# - Progress increasing
```

---

## Post-Bootstrap Tasks

### 1. Run Cleanup on Old Nodes

```bash
# On each existing node (one at a time to limit impact)
nodetool cleanup
```

### 2. Update Seed List (If Appropriate)

If adding to seed nodes, update `cassandra.yaml` on all nodes:

```yaml
seeds: "node1,node2,new-node"  # Add new node if it should be a seed
```

### 3. Verify Data Distribution

```bash
nodetool status
```

Check that data is roughly balanced across nodes.

### 4. Run Repair (Recommended)

```bash
# After cleanup, ensure data consistency
nodetool repair -pr
```

---

## Adding Multiple Nodes

When adding multiple nodes:

1. **Add one at a time** - Wait for each bootstrap to complete
2. **Run cleanup after all additions** - More efficient
3. **Alternatively**: Add all at once with calculated tokens (advanced)

### Sequential Addition

```bash
# Node A: Start and wait for UN status
# Node B: Start and wait for UN status
# Node C: Start and wait for UN status
# Then: Run cleanup on all existing nodes
```

---

## Time Estimation

| Cluster Data Size | Bootstrap Duration |
|-------------------|-------------------|
| < 100 GB total | 30 min - 1 hour |
| 100 GB - 1 TB | 1-4 hours |
| 1 TB - 10 TB | 4-24 hours |
| > 10 TB | 24+ hours |

Duration depends on:
- Total data in cluster
- Number of existing nodes
- Network bandwidth
- Disk I/O speed

---

## Best Practices

| Practice | Reason |
|----------|--------|
| Add during low-traffic periods | Reduces impact |
| Add one node at a time | Prevents overload |
| Monitor throughout | Catch issues early |
| Run cleanup after | Reclaim space on old nodes |
| Verify token distribution | Ensure balanced cluster |
| Update monitoring | Include new node |

---

## Related Procedures

| Scenario | Procedure |
|----------|-----------|
| Removing node | [Decommission Node](decommission-node.md) |
| Replacing failed node | [Replace Dead Node](replace-dead-node.md) |
| Cluster not healthy | Fix issues first |

## Related Commands

| Command | Purpose |
|---------|---------|
| `nodetool status` | Cluster overview |
| `nodetool netstats` | Streaming progress |
| `nodetool cleanup` | Remove relocated data |
| `nodetool ring` | Token distribution |
| `nodetool setstreamthroughput` | Adjust streaming speed |
