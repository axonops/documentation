---
title: "Cassandra Replication"
description: "Data replication in Cassandra. Replication factor, strategies, and multi-datacenter configuration."
meta:
  - name: keywords
    content: "Cassandra replication, replication factor, NetworkTopologyStrategy, replica"
---

# Replication

Replication is fundamental to Cassandra's architecture. Every write is automatically copied to multiple nodes based on the keyspace's replication factor configuration, with no external tools or application logic required. This built-in redundancy means nodes can fail, disks can die, and with appropriate per-datacenter replication factors and consistency levels, entire datacenters can go offline while the data remains available and intact.

Unlike traditional databases that treat replication as an add-on feature, Cassandra was designed from the ground up with replication as a core primitive. The system assumes failures will happen and handles them transparently. A node crashes during a write? The replicas have the data. Network partitions a datacenter? The other datacenters continue serving requests. This design enables true 24/7 availability without the operational complexity of failover procedures.

The **replication factor (RF)** determines how many copies of each partition exist, and the **replication strategy** determines where those copies are placed across the cluster topology.

---

## Replication Factor

The replication factor specifies how many nodes store a copy of each partition.

### Choosing Replication Factor

| RF | Fault Tolerance | Trade-off |
|----|-----------------|-----------|
| 1 | None—any node failure loses data | No redundancy |
| 2 | Single node failure | No quorum possible with one node down |
| 3 | Single node failure with quorum | Production minimum (recommended) |
| 5 | Two node failures with quorum | Critical data requiring extreme durability |
| >5 | Diminishing returns | Rarely justified |

**RF = 3 is the production standard:**

```
RF = 3 with QUORUM:
- One node down: Still have quorum (2 of 3)
- Can serve reads/writes with one node down
- Note: Full repair requires all replicas available for complete synchronization
- Balances durability, availability, and storage cost
```

### RF and Cluster Size

```
Rule: RF ≤ nodes_in_smallest_dc

If DC has 2 nodes, max RF = 2 (each partition on both nodes)
If DC has 3 nodes, RF = 3 means every node has every partition
If DC has 10 nodes, RF = 3 means each partition on 3 of 10 nodes

ANTI-PATTERN:
DC with 3 nodes, RF = 5  ← Cannot place 5 replicas on 3 nodes
Cassandra will place 3 replicas, but report RF=5
This causes Unavailable exceptions for QUORUM (needs 3)
```

---

## Replication Strategies

### SimpleStrategy (Development Only)

SimpleStrategy places replicas on consecutive nodes around the ring with no awareness of racks or datacenters:

**Algorithm:**

1. Hash partition key → token
2. Find node that owns this token (primary replica)
3. Walk clockwise, place replicas on next (RF-1) nodes

```graphviz circo simplestrategy.svg
digraph SimpleStrategy {
    bgcolor="transparent"
    graph [fontname="Helvetica", fontsize=11]
    node [fontname="Helvetica", fontsize=10]
    edge [fontname="Helvetica", fontsize=9]

    // Nodes on the ring
    node [shape=circle, style=filled, width=0.9, fixedsize=true]
    A [label="Node A", fillcolor="#e0e0e0"]
    B [label="Node B\n(primary)", fillcolor="#c8e6c9"]
    C [label="Node C\n(replica 2)", fillcolor="#c8e6c9"]
    D [label="Node D\n(replica 3)", fillcolor="#c8e6c9"]

    // Ring structure
    edge [color="#666666", penwidth=2, arrowsize=0.8]
    A -> B
    B -> C [label=" clockwise"]
    C -> D
    D -> A
}
```

!!! warning "Rack Unawareness"
    SimpleStrategy has no rack awareness. Nodes B, C, D might all be on the same rack—if that rack loses power, all replicas are lost.

```sql
-- SimpleStrategy configuration
CREATE KEYSPACE dev_keyspace WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 3
};
```

**Never use SimpleStrategy in production**—it has no rack awareness.

### NetworkTopologyStrategy (Production Standard)

NetworkTopologyStrategy (NTS) places replicas while respecting datacenter and rack boundaries.

**Algorithm (for each datacenter):**

1. Hash partition key → token
2. Find node in this DC that owns token (primary replica)
3. Walk clockwise, selecting nodes on **different racks**
4. Continue until RF replicas placed in this DC
5. Repeat for each DC

```dot
digraph NTS {
    rankdir=LR
    node [shape=box, style=filled, fontname="Helvetica"]
    edge [style=invis]

    subgraph cluster_dc1 {
        label="DC1 (RF=3)"
        style=rounded
        bgcolor="#e8f4f8"
        fontname="Helvetica-Bold"

        subgraph cluster_rack_a {
            label="Rack A"
            style=dashed
            bgcolor="#ffffff"
            N1 [label="N1 ✓\nReplica 1", fillcolor="#90EE90"]
        }

        subgraph cluster_rack_b {
            label="Rack B"
            style=dashed
            bgcolor="#ffffff"
            N2 [label="N2 ✓\nReplica 2", fillcolor="#90EE90"]
        }

        subgraph cluster_rack_c {
            label="Rack C"
            style=dashed
            bgcolor="#ffffff"
            N3 [label="N3 ✓\nReplica 3", fillcolor="#90EE90"]
        }

        N1 -> N2 -> N3
    }

    subgraph cluster_dc2 {
        label="DC2 (RF=3)"
        style=rounded
        bgcolor="#fff8e8"
        fontname="Helvetica-Bold"

        subgraph cluster_rack_x {
            label="Rack X"
            style=dashed
            bgcolor="#ffffff"
            N4 [label="N4 ✓\nReplica 4", fillcolor="#87CEEB"]
        }

        subgraph cluster_rack_y {
            label="Rack Y"
            style=dashed
            bgcolor="#ffffff"
            N5 [label="N5 ✓\nReplica 5", fillcolor="#87CEEB"]
        }

        subgraph cluster_rack_z {
            label="Rack Z"
            style=dashed
            bgcolor="#ffffff"
            N6 [label="N6 ✓\nReplica 6", fillcolor="#87CEEB"]
        }

        N4 -> N5 -> N6
    }

    // Force left-to-right layout
    N3 -> N4 [constraint=true]
}
```

```sql
-- NetworkTopologyStrategy configuration
CREATE KEYSPACE production WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3,
    'dc2': 3
};

-- Single DC with rack awareness
CREATE KEYSPACE single_dc WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'datacenter1': 3
};
```

### NTS Replica Placement Algorithm

For a partition with token T in a DC with RF=3:

| Step | Action | Result |
|------|--------|--------|
| 1 | Find first node clockwise from T | Replica 1 (e.g., Rack A) |
| 2 | Walk clockwise, find node on **different** rack | Replica 2 (Rack B or C) |
| 3 | Continue clockwise, find node on **third** rack | Replica 3 |

**Rack availability impact:**

| Racks Available | Replica Distribution |
|-----------------|---------------------|
| 3+ racks | Full diversity—each replica on different rack |
| 2 racks | Two replicas share a rack |
| 1 rack | All replicas on same rack (no diversity) |

!!! tip "Rack Diversity"
    With RF=3, at least 3 racks are needed for full rack diversity.

---

## Snitches: Topology Awareness

### Why Snitches Exist

NetworkTopologyStrategy places replicas on different racks to survive hardware failures—but Cassandra has no inherent knowledge of physical infrastructure. IP addresses alone reveal nothing about which nodes share a rack, power supply, or network switch.

The **snitch** solves this problem by mapping physical infrastructure to logical Cassandra topology. Given any node's IP address, the snitch returns that node's datacenter and rack. This mapping enables:

| Function | How Snitch Enables It |
|----------|----------------------|
| Replica placement | NTS uses rack information to spread replicas across failure domains |
| Request routing | Coordinators prefer nodes in the local datacenter for lower latency |
| Consistency enforcement | LOCAL_QUORUM identifies which nodes are "local" via datacenter membership |

Without accurate snitch configuration, Cassandra cannot distinguish between nodes in the same rack versus different racks, potentially placing all replicas in a single failure domain.

### Configuration Considerations

The snitch must be configured during initial cluster deployment, before starting the node for the first time. Once a node joins the cluster with a particular datacenter and rack assignment, changing this topology is operationally complex and requires careful coordination (see [Snitch Configuration Issues](#snitch-configuration-issues)).

Two categories of snitches exist:

- **Manual configuration** — The administrator explicitly defines each node's datacenter and rack (e.g., GossipingPropertyFileSnitch)
- **Automatic detection** — The snitch queries cloud provider metadata APIs to determine topology (e.g., Ec2Snitch, GoogleCloudSnitch)

**GossipingPropertyFileSnitch is recommended** for most deployments because it provides full flexibility: topology names can match organizational conventions, nodes can be moved between logical racks without infrastructure changes, and the configuration works identically across on-premises, cloud, and hybrid environments.

### Available Snitches

| Snitch | Use Case | Topology Source |
|--------|----------|-----------------|
| **GossipingPropertyFileSnitch** | Production (recommended) | Local properties file |
| **Ec2Snitch** | AWS single region | EC2 metadata API |
| **Ec2MultiRegionSnitch** | AWS multi-region | EC2 metadata API + public IPs |
| **GoogleCloudSnitch** | Google Cloud Platform | GCE metadata API |
| **AzureSnitch** | Microsoft Azure | Azure metadata API |
| **SimpleSnitch** | Single-node development | None (all nodes in same DC/rack) |
| **PropertyFileSnitch** | Legacy | Central topology file (deprecated) |

### How Snitches Work

Each node runs a snitch implementation that:

1. **Determines local topology** — On startup, the snitch identifies the local node's datacenter and rack (from configuration file or cloud metadata API)
2. **Propagates via gossip** — The local topology is included in gossip messages, so all nodes learn each other's DC/rack membership
3. **Resolves queries** — When Cassandra needs to know any node's location, it queries the snitch (which returns cached gossip data for remote nodes)

```
Snitch query flow:

Application:  getDatacenter(10.0.1.5) → "us-east"
              getRack(10.0.1.5)       → "rack-a"

Internal lookup:
  Local node?  → Read from configuration
  Remote node? → Return cached gossip state
```

---

### GossipingPropertyFileSnitch (Recommended)

Each node reads its own DC/rack from a local file, then gossips it to others:

```yaml
# cassandra.yaml
endpoint_snitch: GossipingPropertyFileSnitch
```

```properties
# conf/cassandra-rackdc.properties
dc=us-east-1
rack=rack-a
# Optional: prefer_local=true (prefer connecting to local DC)
```

**Why GossipingPropertyFileSnitch is recommended:**

| Advantage | Description |
|-----------|-------------|
| Simple configuration | One file per node |
| Universal | Works anywhere (cloud, on-prem, containers) |
| No dependencies | No external services required |
| Automatic propagation | Topology shared via gossip |

### Cloud Snitches

#### Ec2Snitch (AWS Single Region)

```yaml
# cassandra.yaml
endpoint_snitch: Ec2Snitch
```

Automatically detects:

- **Datacenter**: AWS region (e.g., `us-east-1`)
- **Rack**: Availability zone (e.g., `us-east-1a`)

**Keyspace must use region name:**

```sql
CREATE KEYSPACE my_ks WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'us-east-1': 3  -- Must match EC2 region name
};
```

#### Ec2MultiRegionSnitch (AWS Multi-Region)

```yaml
# cassandra.yaml
endpoint_snitch: Ec2MultiRegionSnitch

# REQUIRED: Node's public IP for cross-region communication
broadcast_address: <public_ip>
broadcast_rpc_address: <public_ip>

# Listen on all interfaces
listen_address: <private_ip>
```

**Critical requirement**: Security groups must allow cross-region traffic on:

- Port 7000 (inter-node)
- Port 7001 (inter-node SSL)
- Port 9042 (native transport, if clients cross regions)

#### GoogleCloudSnitch (GCP)

```yaml
# cassandra.yaml
endpoint_snitch: GoogleCloudSnitch
```

Automatically detects:

- **Datacenter**: `<project>:<region>` (e.g., `myproject:us-central1`)
- **Rack**: Zone (e.g., `us-central1-a`)

### Snitch Configuration Issues

**Problem 1: Changing snitches on existing cluster**

```
WRONG: Simply changing the snitch class

What happens:
- Node restarts with new snitch
- Reports different DC/rack name
- Cassandra thinks it is a NEW node
- Data starts streaming (wrong!)

CORRECT: Change snitch, then change topology step by step
1. Stop node
2. Change snitch in cassandra.yaml
3. Update cassandra-rackdc.properties to SAME DC/rack as before
4. Restart
5. Repeat for all nodes
6. Only then update DC/rack names one at a time
```

**Problem 2: Inconsistent DC/rack names**

```
Node 1: dc=US-EAST, rack=rack1
Node 2: dc=us-east, rack=rack1   ← Different case!
Node 3: dc=us_east, rack=rack1   ← Different format!

Result: Cassandra sees 3 different DCs
        Replication is completely wrong
```

**Always verify topology:**

```bash
nodetool status
# Should show expected DC names and node distribution

nodetool describecluster
# Shows DC info and schema agreement
```

---

## Multi-DC Replication Patterns

### Active-Active

Both datacenters serve traffic with full replication:

```sql
CREATE KEYSPACE active_active WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'us-east': 3,
    'us-west': 3
};
```

| Characteristic | Value |
|----------------|-------|
| Consistency | LOCAL_QUORUM for low latency |
| Total storage | 6× raw data |
| Failure tolerance | Either DC can serve all traffic |

### Three-Region Global

Global distribution with local consistency:

```sql
CREATE KEYSPACE global WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'us-east': 3,
    'us-west': 3,
    'eu-west': 3
};
```

| Characteristic | Value |
|----------------|-------|
| Consistency | LOCAL_QUORUM for regional, QUORUM for global |
| Total storage | 9× raw data |
| Use case | Global applications with regional users |

### Analytics Replica

Separate datacenter for analytics workloads:

```sql
CREATE KEYSPACE with_analytics WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'production': 3,
    'analytics': 2
};
```

| Characteristic | Value |
|----------------|-------|
| Analytics DC | Runs Spark jobs, never serves production traffic |
| Lower RF | Acceptable for read-only analytics |

---

## Changing Replication

### Increasing Replication Factor

Increasing RF is operationally simple but has significant consequences that require careful planning.

```sql
-- Current: RF=2, Target: RF=3

-- Step 1: Alter keyspace (changes metadata only)
ALTER KEYSPACE my_keyspace WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'datacenter1': 3
};
```

```bash
# Step 2: Run repair to stream data to new replicas on all nodes
nodetool repair -full my_keyspace

# This streams data to the third replica for each partition
# Can take hours/days depending on data size
```

**Critical warning**: The `ALTER KEYSPACE` command changes metadata immediately, but new replicas contain no data. To populate the new replica endpoints, the repair process must be executed to stream data from existing replicas. This process takes a significant amount of time—hours to days depending on data volume.

During this repair window, **queries will fail or return incomplete data**:

| Issue | Consequence |
|-------|-------------|
| New replicas are empty | Reads from new replicas return no data |
| QUORUM uses new RF | QUORUM now requires ⌊3/2⌋+1 = 2 nodes, but only 2 have data |
| Read repair is insufficient | Only helps for rows that are read; most data remains missing |

This operation requires careful planning and should be scheduled during low-traffic periods with appropriate consistency level adjustments.

### Decreasing Replication Factor

```sql
-- Current: RF=3, Target: RF=2

-- Step 1: Alter keyspace
ALTER KEYSPACE my_keyspace WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'datacenter1': 2
};
```

```bash
# Step 2: Run cleanup to remove extra replicas
nodetool cleanup my_keyspace

# This deletes data that nodes no longer own
# Required on every node
```

### Adding a Datacenter

```bash
# Step 1: Configure new DC nodes
# cassandra.yaml: Same cluster_name, correct seeds
# cassandra-rackdc.properties: Correct DC/rack names

# Step 2: Start new nodes (they join empty)
```

```sql
-- Step 3: Update keyspace to include new DC
ALTER KEYSPACE my_keyspace WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3,
    'dc2': 3  -- New DC
};
```

```bash
# Step 4: Rebuild new DC from existing DC
# Run on EACH node in the new DC:
nodetool rebuild -- dc1

# Streams all data from dc1 to the new node
# Faster than repair (streams only, no comparisons)
```

### Removing a Datacenter

```sql
-- Step 1: Update keyspace to remove DC
ALTER KEYSPACE my_keyspace WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3
    -- dc2 removed
};
```

```bash
# Step 2: Run repair on remaining DC
nodetool repair -full my_keyspace

# Step 3: Decommission nodes in removed DC
nodetool decommission  # On each node in dc2

# Step 4: Update seed list to remove dc2 nodes
```

---

## Monitoring Replication

### Cluster Topology

```bash
# Node status and ownership
nodetool status my_keyspace

# Output:
# Datacenter: dc1
# ==============
# Status=Up/Down
# |/ State=Normal/Leaving/Joining/Moving
# --  Address    Load       Tokens  Owns (effective)  Rack
# UN  10.0.1.1   256 GB     16      33.3%            rack1
# UN  10.0.1.2   248 GB     16      33.3%            rack2
# UN  10.0.1.3   252 GB     16      33.3%            rack3
```

### Streaming Status

```bash
# Current streaming operations
nodetool netstats

# Shows:
# - Receiving streams (from other nodes)
# - Sending streams (to other nodes)
# - Progress percentage
```

---

## Troubleshooting

### Unavailable Exceptions

```
Error: Not enough replicas available for query at consistency QUORUM
       (2 required but only 1 alive)
```

| Cause | Diagnosis | Resolution |
|-------|-----------|------------|
| Nodes down | `nodetool status` shows DN | Restart nodes or lower CL |
| RF > nodes | Keyspace RF higher than DC size | Lower RF or add nodes |
| Network partition | Some nodes unreachable | Fix network |

### Uneven Data Distribution

```
nodetool status shows:
Node 1: 100 GB
Node 2: 500 GB  ← Much larger
Node 3: 120 GB
```

| Cause | Diagnosis | Resolution |
|-------|-----------|------------|
| Hot partitions | Check `nodetool tablestats` | Redesign partition keys |
| Uneven tokens | Check `nodetool ring` | Rebalance or use vnodes |
| Late joiner | Node joined after data loaded | Run repair |

### Missing Data After Node Replacement

```bash
# Check if replacement completed
nodetool netstats  # Look for ongoing streams

# Run repair to ensure data is complete
nodetool repair -full my_keyspace
```

---

## Best Practices

| Area | Recommendation |
|------|----------------|
| Strategy | Always use NetworkTopologyStrategy (even for single DC) |
| Replication factor | RF=3 minimum for production |
| Rack distribution | Distribute nodes across at least RF racks |
| Multi-DC | Same RF across DCs for active-active |
| Snitch | Use GossipingPropertyFileSnitch for portability |
| Naming | Use consistent DC/rack naming (case-sensitive) |
| New DCs | Use `nodetool rebuild` (faster than repair) |

---

## Related Documentation

- **[Distributed Data Overview](index.md)** - How partitioning, replication, and consistency work together
- **[Partitioning](partitioning.md)** - How data is distributed to nodes
- **[Consistency](consistency.md)** - How consistency levels interact with replication
- **[Replica Synchronization](replica-synchronization.md)** - How replicas converge