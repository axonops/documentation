---
title: "Cassandra Adding Nodes"
description: "Add nodes to Cassandra cluster. Bootstrap procedure with behavioral contracts and pre-flight requirements."
meta:
  - name: keywords
    content: "Cassandra bootstrap, add node, cluster scaling, expand cluster"
search:
  boost: 3
---

# Adding Nodes

Adding nodes (bootstrapping) expands cluster capacity by introducing new nodes that automatically receive a portion of existing data through streaming.

---

## Prerequisites

The following requirements must be met before adding a node:

### Cluster State Requirements

| Requirement | Verification | Rationale |
|-------------|--------------|-----------|
| All nodes must show `UN` status | `nodetool status` | Bootstrap from degraded cluster risks data loss |
| No topology changes in progress | `nodetool netstats` | Only one topology change may occur at a time |
| No active repairs | `nodetool netstats` | Concurrent operations cause unpredictable behavior |
| Schema agreement | `nodetool describecluster` | Schema disagreement causes bootstrap failures |

```bash
# Pre-flight verification
nodetool status              # All nodes UN
nodetool describecluster     # Single schema version
nodetool netstats            # No active streaming
nodetool compactionstats     # No heavy compaction
```

### Hardware Requirements

| Requirement | Rationale |
|-------------|-----------|
| Same or better specs as existing nodes | Uniform performance |
| Sufficient disk for expected data share | Node receives 1/N of cluster data |
| Network connectivity to all existing nodes | Gossip and streaming |

### Software Requirements

| Requirement | Consequence if Violated |
|-------------|------------------------|
| Same Cassandra version | Schema conflicts, potential data corruption |
| Same JVM version | Undefined behavior |
| Same partitioner | Node cannot join cluster |
| Compatible snitch | Topology awareness failures |

### Network Requirements

| Port | Protocol | Purpose |
|------|----------|---------|
| 7000 | TCP | Internode communication (gossip, streaming) |
| 7001 | TCP | Internode communication (SSL, if enabled) |
| 9042 | TCP | CQL native transport |
| 7199 | TCP | JMX monitoring (optional) |

---

## Behavioral Contract

### Guarantees

- New node receives data for its assigned token ranges from existing nodes
- Existing nodes continue serving client requests during bootstrap
- Data consistency is maintained (new node receives consistent replicas)
- Bootstrap is resumable if interrupted (with data directory cleared)

### Token Assignment

| Configuration | Behavior |
|---------------|----------|
| `num_tokens` set (vnodes) | Tokens automatically assigned from random distribution |
| `initial_token` set | Explicit token assignment (advanced) |

!!! note "Token Count"
    The `num_tokens` value should match existing nodes. Cassandra 4.0+ defaults to 16 tokens; earlier versions defaulted to 256.

### Failure Semantics

| Scenario | Outcome | Recovery |
|----------|---------|----------|
| Bootstrap completes | Node joins ring with full data | None required |
| Bootstrap interrupted | Partial data on new node | Clear data, restart |
| Source node fails during bootstrap | Streaming stalls | Wait for recovery or restart bootstrap |
| Network partition | Streaming fails | Resolve network, restart bootstrap |
| Disk full on new node | Bootstrap fails | Free space, clear data, restart |

---

## Configuration

### cassandra.yaml

The following settings must be configured on the new node:

```yaml
# Must match existing cluster exactly
cluster_name: 'ProductionCluster'

# Token configuration - must match existing nodes
num_tokens: 16                       # Or 256 for older clusters

# Seed nodes - 2-3 existing stable nodes
# The new node must NOT be listed as a seed
seed_provider:
  - class_name: org.apache.cassandra.locator.SimpleSeedProvider
    parameters:
      - seeds: "10.0.1.1,10.0.1.2"

# This node's address - must be reachable by all other nodes
listen_address: 10.0.1.10
rpc_address: 10.0.1.10

# Must match cluster configuration
endpoint_snitch: GossipingPropertyFileSnitch
partitioner: org.apache.cassandra.dht.Murmur3Partitioner

# Enable bootstrap (default is true)
auto_bootstrap: true
```

!!! warning "Seed Configuration"
    The new node must not be listed in its own seed list. Seeds should be 2-3 existing, stable nodes.

### cassandra-rackdc.properties

For multi-datacenter deployments:

```properties
dc=dc1
rack=rack1
```

The datacenter and rack must match the intended topology placement.

---

## Procedure

### Step 1: Verify Cluster Health

On any existing node:

```bash
# All nodes must show UN
nodetool status

# Schema must be in agreement
nodetool describecluster

# No active streaming or repairs
nodetool netstats
```

!!! danger "Do Not Proceed If"
    - Any node shows status other than `UN`
    - Schema versions disagree
    - Streaming or repair is in progress

### Step 2: Prepare New Node

```bash
# Install Cassandra (same version as cluster)
# Configure cassandra.yaml and cassandra-rackdc.properties

# Ensure data directories are empty
sudo rm -rf /var/lib/cassandra/data/*
sudo rm -rf /var/lib/cassandra/commitlog/*
sudo rm -rf /var/lib/cassandra/saved_caches/*
```

### Step 3: Start Bootstrap

```bash
sudo systemctl start cassandra
```

The node begins bootstrap automatically:

1. Contacts seed nodes to learn cluster topology
2. Gossip propagates new node information to all nodes
3. Existing nodes stream data to new node
4. New node transitions from `UJ` (Joining) to `UN` (Normal)

### Step 4: Monitor Progress

```bash
# Watch node status (from any node)
watch -n 10 'nodetool status'

# Monitor streaming progress (on new node)
nodetool netstats

# Watch logs for progress and errors
tail -f /var/log/cassandra/system.log | grep -i "stream\|bootstrap"
```

**Expected state transitions:**

| State | Code | Duration |
|-------|------|----------|
| Joining | `UJ` | Until streaming completes |
| Normal | `UN` | Bootstrap complete |

### Step 5: Verify Completion

```bash
# Node should show UN with data
nodetool status

# Verify token ownership
nodetool ring | grep <new_node_ip>

# No active streaming
nodetool netstats
```

### Step 6: Run Cleanup

After bootstrap completes, existing nodes retain data that moved to the new node. Cleanup must run on all existing nodes:

```bash
# On EACH existing node (not the new node)
# Run one node at a time
nodetool cleanup
```

See [Cleanup Operations](cleanup.md) for detailed guidance.

---

## Duration Estimates

Bootstrap duration depends on data volume and network throughput:

| Data to Stream | 200 Mbps (default) | 400 Mbps |
|----------------|-------------------|----------|
| 100 GB | 1-2 hours | 30-60 min |
| 500 GB | 4-8 hours | 2-4 hours |
| 1 TB | 8-16 hours | 4-8 hours |
| 2 TB | 16-32 hours | 8-16 hours |

**Factors affecting duration:**

- Network bandwidth between nodes
- Disk I/O throughput on source and target
- Number of source nodes (more nodes = more parallel streams)
- Stream throughput configuration
- Cluster load during bootstrap

---

## Performance Tuning

### Increase Streaming Throughput

Default streaming throughput is 200 Mbps. To accelerate bootstrap:

```bash
# On existing nodes - increase outbound streaming
nodetool setstreamthroughput 400  # MB/s
```

```yaml
# On new node - cassandra.yaml
stream_throughput_outbound_megabits_per_sec: 400
```

!!! warning "Client Impact"
    Higher streaming throughput increases network and I/O load, potentially impacting client request latency. Use aggressive settings only during maintenance windows.

### Cassandra 4.0+ Optimizations

```yaml
# cassandra.yaml - stream entire SSTables (faster)
stream_entire_sstables: true
```

---

## Rack-Aware Scaling

When using `NetworkTopologyStrategy` with multiple racks, nodes must be added evenly across racks to maintain balanced data distribution.

### The Imbalance Problem

Cassandra places one replica per rack (when RF ≤ rack count). Uneven node distribution causes uneven load:

```
RF=3, 3 racks, uneven distribution:

Rack1: 3 nodes → each handles 1/3 of rack's replica load
Rack2: 2 nodes → each handles 1/2 of rack's replica load
Rack3: 1 node  → handles 100% of rack's replica load ← OVERLOADED
```

### Balanced Addition Rules

| Current State | Correct Addition | Incorrect Addition |
|---------------|------------------|-------------------|
| 3 nodes (1 per rack) | Add 3 (1 to each rack) | Add 1 or 2 |
| 6 nodes (2 per rack) | Add 3 (1 to each rack) | Add 1 or 2 |
| 9 nodes (3 per rack) | Add 3 (1 to each rack) | Add 1 or 2 |

**Formula:** When adding nodes to a cluster with R racks, add in multiples of R to maintain balance.

### Verification

Check current rack distribution:

```bash
nodetool status

# Example balanced output (2 per rack):
# Datacenter: dc1
# UN  10.0.1.1  100 GB  rack1
# UN  10.0.1.2  100 GB  rack1
# UN  10.0.1.3  100 GB  rack2
# UN  10.0.1.4  100 GB  rack2
# UN  10.0.1.5  100 GB  rack3
# UN  10.0.1.6  100 GB  rack3
```

Check load distribution after adding:

```bash
# Load should be roughly equal across all nodes
nodetool status | awk '/UN/ {print $3, $8}'
```

!!! warning "Imbalanced Clusters"
    If an imbalanced state already exists, adding nodes to underrepresented racks is acceptable to restore balance. The goal is equal nodes per rack.

---

## Adding Multiple Nodes

### Sequential Addition (Required)

Nodes must be added one at a time when using vnodes (default):

```bash
# 1. Add first node, wait for UN status
# 2. Add second node, wait for UN status
# 3. Continue for all nodes
# 4. Run cleanup on all original nodes
```

**Wait times between additions:**

| Cluster Size | Minimum Wait |
|--------------|--------------|
| < 10 nodes | Until previous node shows UN |
| 10-50 nodes | UN + 1 hour stabilization |
| 50+ nodes | UN + 2-4 hours stabilization |

!!! danger "Never Bootstrap Multiple Nodes Simultaneously"
    Concurrent bootstraps with vnodes cause token collisions and unpredictable data distribution. Add nodes strictly sequentially.

### Manual Token Assignment (Advanced)

Multiple nodes may bootstrap concurrently only with manually assigned, non-overlapping tokens:

```yaml
# cassandra.yaml - explicit token (disables vnodes)
num_tokens: 1
initial_token: <calculated_token>
```

This approach is complex and rarely necessary.

---

## Troubleshooting

### Bootstrap Won't Start

**Symptoms:** Node starts but doesn't appear in `nodetool status`

| Cause | Diagnosis | Solution |
|-------|-----------|----------|
| Cluster name mismatch | Check `cluster_name` in yaml | Fix name, clear data, restart |
| Seeds unreachable | `nc -zv seed 7000` | Check firewall, network |
| Wrong listen_address | Log shows binding errors | Fix address in yaml |
| Data directory not empty | Check `/var/lib/cassandra/data` | Clear data directories |

```bash
# Check for errors
grep -i "error\|failed" /var/log/cassandra/system.log | tail -50
```

### Bootstrap Stalled

**Symptoms:** Node stuck in `UJ` state, streaming shows no progress

| Cause | Diagnosis | Solution |
|-------|-----------|----------|
| Source nodes overloaded | High CPU/IO on sources | Reduce stream throughput |
| Network issues | Packet loss, timeouts | Fix network |
| Large partitions | Timeout errors in logs | Increase `streaming_socket_timeout_in_ms` |
| Disk full | `df -h` on new node | Free space |

```yaml
# cassandra.yaml - for large partition timeouts
streaming_socket_timeout_in_ms: 86400000  # 24 hours
```

### Bootstrap Failed

**Symptoms:** Node crashed or stopped during bootstrap

**Recovery:**

```bash
# Clear partial data
sudo systemctl stop cassandra
sudo rm -rf /var/lib/cassandra/data/*
sudo rm -rf /var/lib/cassandra/commitlog/*
sudo rm -rf /var/lib/cassandra/saved_caches/*

# Restart bootstrap
sudo systemctl start cassandra
```

See [Troubleshooting](troubleshooting.md) for additional diagnostics.

---

## Post-Bootstrap Tasks

### Required: Run Cleanup

Cleanup must run on all existing nodes after bootstrap:

```bash
# On each existing node (one at a time)
nodetool cleanup
```

### Recommended: Update Monitoring

| Task | Action |
|------|--------|
| Monitoring | Add new node to monitoring systems |
| Alerting | Update alert configurations |
| Backups | Add to backup schedules |
| Documentation | Update cluster inventory |

### Optional: Update Seed List

If the new node should be a seed (only if replacing an unreliable seed):

```yaml
# On ALL nodes, update cassandra.yaml
seeds: "existing-seed1,existing-seed2,new-node"
```

Rolling restart required for seed list changes to take effect.

### Optional: Run Repair

After cluster stabilizes:

```bash
# Repair the new node's token ranges
nodetool repair -pr
```

---

## Related Documentation

- **[Cluster Management Overview](index.md)** - Operation selection guide
- **[Cleanup Operations](cleanup.md)** - Post-bootstrap cleanup
- **[Scaling Operations](scaling.md)** - Adding multiple nodes
- **[Removing Nodes](removing-nodes.md)** - Decommission procedures
- **[Troubleshooting](troubleshooting.md)** - Diagnostic procedures
