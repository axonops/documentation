---
title: "Cassandra Adding Nodes"
description: "Add nodes to Cassandra cluster. Scale out procedure and bootstrap process."
meta:
  - name: keywords
    content: "add Cassandra node, cluster scaling, bootstrap node"
---

# Adding Nodes

Adding nodes (bootstrapping) expands cluster capacity by introducing new nodes that automatically receive a portion of existing data.

---

## Overview

When a new node joins a Cassandra cluster:

1. Node contacts seed nodes to learn cluster topology
2. Gossip propagates the new node information
3. Existing nodes stream data to the new node
4. New node becomes operational after bootstrap completes

---

## Prerequisites

### Hardware Requirements

- Same or compatible hardware as existing nodes
- Sufficient disk space for expected data share
- Network connectivity to all existing nodes

### Software Requirements

- Same Cassandra version as existing cluster
- Matching JVM version
- Consistent configuration (snitch, partitioner)

### Network Requirements

| Port | Purpose |
|------|---------|
| 7000 | Internode communication (gossip) |
| 7001 | Internode communication (SSL) |
| 9042 | CQL native transport |
| 7199 | JMX monitoring |

---

## Configuration

### cassandra.yaml Settings

```yaml
# Must match existing cluster
cluster_name: 'ProductionCluster'

# Seed nodes (2-3 existing nodes)
seed_provider:
  - class_name: org.apache.cassandra.locator.SimpleSeedProvider
    parameters:
      - seeds: "10.0.1.1,10.0.1.2"

# New node's address
listen_address: 10.0.1.10
rpc_address: 10.0.1.10

# Enable bootstrap (default)
auto_bootstrap: true

# Match existing cluster settings
endpoint_snitch: GossipingPropertyFileSnitch
partitioner: org.apache.cassandra.dht.Murmur3Partitioner
```

### For Multi-Datacenter

Configure datacenter and rack in `cassandra-rackdc.properties`:

```properties
dc=dc1
rack=rack1
```

---

## Bootstrap Procedure

### Step 1: Verify Cluster Health

On any existing node:

```bash
nodetool status
```

All nodes should show `UN` (Up/Normal).

### Step 2: Verify No Ongoing Operations

```bash
nodetool compactionstats
nodetool netstats
```

Avoid bootstrapping during heavy compaction or repairs.

### Step 3: Start New Node

```bash
# Clear any existing data (if reusing hardware)
sudo rm -rf /var/lib/cassandra/data/*
sudo rm -rf /var/lib/cassandra/commitlog/*
sudo rm -rf /var/lib/cassandra/saved_caches/*

# Start Cassandra
sudo systemctl start cassandra
```

### Step 4: Monitor Bootstrap

From any node:

```bash
# Watch node status
nodetool status
```

New node shows as `UJ` (Up/Joining) during bootstrap.

On new node:

```bash
# Monitor streaming progress
nodetool netstats

# Watch logs
tail -f /var/log/cassandra/system.log
```

### Step 5: Verify Completion

```bash
nodetool status
```

New node should show `UN` (Up/Normal).

### Step 6: Run Cleanup

After bootstrap, run cleanup on **existing nodes** to remove data that moved to the new node:

```bash
# On each existing node (one at a time)
nodetool cleanup
```

---

## Monitoring Bootstrap

### Progress Indicators

```bash
# Streaming sessions
nodetool netstats

# Bootstrap status in logs
grep -i bootstrap /var/log/cassandra/system.log | tail -20
```

### Streaming Throughput

```bash
# Check current throughput
nodetool getstreamthroughput

# Increase if needed (MB/s)
nodetool setstreamthroughput 400
```

---

## Time Estimation

| Total Cluster Data | Expected Duration |
|-------------------|-------------------|
| < 100 GB | 30 min - 1 hour |
| 100 GB - 500 GB | 1-4 hours |
| 500 GB - 2 TB | 4-12 hours |
| > 2 TB | 12+ hours |

Factors affecting duration:
- Network bandwidth
- Disk I/O speed
- Number of existing nodes
- Stream throughput settings

---

## Adding Multiple Nodes

### Sequential Addition (Recommended)

```bash
# Add nodes one at a time
# 1. Bootstrap node A, wait for UN status
# 2. Bootstrap node B, wait for UN status
# 3. Run cleanup on all original nodes
```

### Concurrent Addition (Advanced)

Multiple nodes can bootstrap simultaneously if:
- Sufficient network bandwidth
- Adequate disk I/O on source nodes
- Tokens are manually assigned to prevent overlap

---

## Troubleshooting

### Bootstrap Fails to Start

**Check connectivity:**
```bash
nc -zv seed-node1 7000
nc -zv seed-node1 9042
```

**Check configuration:**
```bash
grep -E "cluster_name|seeds" /etc/cassandra/cassandra.yaml
```

**Check logs:**
```bash
grep -i "error\|failed" /var/log/cassandra/system.log | tail -50
```

### Bootstrap Slow or Stalled

**Check streaming:**
```bash
nodetool netstats
```

**Increase throughput:**
```bash
nodetool setstreamthroughput 400
```

**Check source node disk:**
```bash
# On source nodes
iostat -x 1 5
```

### Bootstrap Fails Mid-Way

**Clear and retry:**
```bash
sudo systemctl stop cassandra
sudo rm -rf /var/lib/cassandra/data/*
sudo rm -rf /var/lib/cassandra/commitlog/*
sudo systemctl start cassandra
```

### Wrong Token Assignment

With vnodes (default), tokens are automatically assigned. If tokens appear wrong:

```bash
# Check token distribution
nodetool ring

# May need to decommission and re-add
nodetool decommission
# Then clear data and restart
```

---

## Post-Bootstrap Tasks

### 1. Run Cleanup

On all existing nodes:

```bash
nodetool cleanup my_keyspace
```

### 2. Update Monitoring

- Add new node to monitoring systems
- Update alerting configuration
- Add to backup schedules

### 3. Update Seed List (Optional)

If adding the node as a seed:

```yaml
# On all nodes, update cassandra.yaml
seeds: "existing-seed1,existing-seed2,new-node"
```

### 4. Run Repair

After cluster stabilizes:

```bash
nodetool repair -pr
```

---

## Best Practices

| Practice | Reason |
|----------|--------|
| Add one node at a time | Prevents overload |
| Run during low traffic | Reduces impact |
| Monitor throughout | Catch issues early |
| Run cleanup after | Reclaim space |
| Update documentation | Track cluster changes |

---

## Related Commands

| Command | Purpose |
|---------|---------|
| `nodetool status` | Cluster status |
| `nodetool netstats` | Streaming status |
| `nodetool cleanup` | Remove old data |
| `nodetool ring` | Token distribution |
| `nodetool decommission` | Remove node |

## Related Documentation

- [Cluster Management Overview](index.md) - Cluster operations
- [Decommission Node](../../troubleshooting/playbooks/decommission-node.md) - Removing nodes
- [Replace Dead Node](../../troubleshooting/playbooks/replace-dead-node.md) - Replacing failed nodes
