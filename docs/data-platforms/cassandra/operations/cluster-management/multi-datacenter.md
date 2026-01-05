---
title: "Cassandra Multi-Datacenter Operations"
description: "Add and remove Cassandra datacenters. Multi-DC expansion and consolidation procedures."
meta:
  - name: keywords
    content: "Cassandra multi-datacenter, add datacenter, remove datacenter, geographic replication"
---

# Multi-Datacenter Operations

This guide covers procedures for adding and removing datacenters in a Cassandra cluster.

---

## Adding a Datacenter

Expanding to a new datacenter provides geographic redundancy and reduced latency for regional users.

### Prerequisites

| Requirement | Verification |
|-------------|--------------|
| Existing cluster healthy | All nodes `UN` |
| Network connectivity | New DC can reach existing DCs |
| Cross-DC latency acceptable | < 100ms recommended |
| Same Cassandra version | Match existing cluster |
| Hardware provisioned | Nodes ready in new DC |

### Planning Considerations

**Replication strategy:**

The cluster must use `NetworkTopologyStrategy` for multi-DC deployments:

```sql
-- Check current replication
DESCRIBE KEYSPACE my_keyspace;

-- Must be NetworkTopologyStrategy, not SimpleStrategy
```

**Node count:**

- New datacenter should have at least RF nodes
- Typically match node count of existing DC

**Network requirements:**

| Port | Purpose |
|------|---------|
| 7000 | Internode (gossip, streaming) |
| 7001 | Internode SSL |
| 9042 | Client connections |

### Procedure

**Step 1: Update keyspace replication**

Before adding any nodes, update all keyspaces to include the new datacenter:

```sql
-- User keyspaces
ALTER KEYSPACE my_keyspace WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3,
    'dc2': 3  -- New datacenter
};

-- System keyspaces (critical!)
ALTER KEYSPACE system_auth WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3,
    'dc2': 3
};

ALTER KEYSPACE system_distributed WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3,
    'dc2': 3
};

ALTER KEYSPACE system_traces WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3,
    'dc2': 3
};
```

!!! warning "Update system_auth First"
    The `system_auth` keyspace must be updated before adding nodes. Otherwise, authentication may fail for new nodes.

**Step 2: Configure nodes in new datacenter**

On each new node:

```yaml
# cassandra.yaml

cluster_name: 'ProductionCluster'  # Must match
num_tokens: 256                    # Match existing

# Seeds from BOTH datacenters
seed_provider:
  - class_name: org.apache.cassandra.locator.SimpleSeedProvider
    parameters:
      - seeds: "dc1-node1,dc1-node2,dc2-node1"

# This node's address
listen_address: <node_ip>
rpc_address: <node_ip>

# Snitch for multi-DC
endpoint_snitch: GossipingPropertyFileSnitch
```

```properties
# cassandra-rackdc.properties
dc=dc2
rack=rack1
```

**Step 3: Start nodes in new datacenter**

Add nodes one at a time, but do NOT wait for bootstrap:

```bash
# New DC nodes start with auto_bootstrap: false
# They join the ring but receive no data yet

# Start first node
sudo systemctl start cassandra

# Verify it joins (shows UN but with 0 load)
nodetool status

# Start remaining nodes
```

!!! note "Bootstrap Disabled"
    For new datacenter nodes, set `auto_bootstrap: false`. Data will be populated via rebuild, not bootstrap.

**Step 4: Rebuild data in new datacenter**

On each node in the new datacenter, run rebuild:

```bash
# Rebuild from existing datacenter
nodetool rebuild dc1

# This streams all data for this node's token ranges from dc1
```

**Rebuild one node at a time** to avoid overwhelming the source datacenter.

```bash
# Monitor rebuild progress
nodetool netstats

# Watch for completion
tail -f /var/log/cassandra/system.log | grep -i rebuild
```

**Step 5: Verify completion**

```bash
# All nodes UN with data
nodetool status

# Example output:
# Datacenter: dc1
# UN  10.0.1.1  245.5 GB  256  ...
# UN  10.0.1.2  238.2 GB  256  ...
# UN  10.0.1.3  251.8 GB  256  ...
#
# Datacenter: dc2
# UN  10.0.2.1  243.1 GB  256  ...  <-- Data present
# UN  10.0.2.2  240.7 GB  256  ...
# UN  10.0.2.3  248.3 GB  256  ...
```

### Duration Estimates

| Data to Rebuild | Per Node |
|-----------------|----------|
| 100 GB | 1-2 hours |
| 500 GB | 4-8 hours |
| 1 TB | 8-16 hours |

Total time = Per node time × Number of nodes in new DC (sequential).

---

## Removing a Datacenter

Consolidating datacenters by removing one entirely.

### Prerequisites

| Requirement | Verification |
|-------------|--------------|
| All nodes in DC healthy | `nodetool status` shows UN |
| Data replicated elsewhere | Other DCs have copies |
| No clients using removed DC | Traffic shifted away |
| No LOCAL_* consistency from removed DC | Clients updated |

!!! danger "Data Loss Risk"
    Ensure all data is replicated to remaining datacenters before removal. If RF in the removed DC exceeds remaining capacity, data loss occurs.

### Procedure

**Step 1: Redirect client traffic**

Update clients to no longer contact the datacenter being removed:

```java
// Java driver - update contact points
CqlSession session = CqlSession.builder()
    .addContactPoint(new InetSocketAddress("dc1-node1", 9042))
    .addContactPoint(new InetSocketAddress("dc1-node2", 9042))
    // Remove dc2 contact points
    .withLocalDatacenter("dc1")
    .build();
```

**Step 2: Update keyspace replication**

Remove the datacenter from all keyspaces:

```sql
-- User keyspaces
ALTER KEYSPACE my_keyspace WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3
    -- dc2 removed
};

-- System keyspaces
ALTER KEYSPACE system_auth WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3
};

ALTER KEYSPACE system_distributed WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3
};

ALTER KEYSPACE system_traces WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3
};
```

**Step 3: Decommission all nodes in the datacenter**

Remove nodes one at a time:

```bash
# On each node in dc2
nodetool decommission

# Wait for completion before starting next
```

**Step 4: Verify removal**

```bash
# dc2 should not appear
nodetool status

# Only dc1 remains
# Datacenter: dc1
# UN  10.0.1.1  245.5 GB  256  ...
# UN  10.0.1.2  238.2 GB  256  ...
# UN  10.0.1.3  251.8 GB  256  ...
```

**Step 5: Update seed lists**

Remove dc2 seeds from all remaining nodes:

```yaml
# cassandra.yaml on dc1 nodes
seed_provider:
  - class_name: org.apache.cassandra.locator.SimpleSeedProvider
    parameters:
      - seeds: "dc1-node1,dc1-node2"  # dc2 seeds removed
```

---

## Changing Datacenter Names

Renaming a datacenter requires migrating to a new DC configuration.

### Procedure

1. Add nodes with new DC name (as if adding new datacenter)
2. Rebuild data to new DC
3. Update replication to include new DC name
4. Redirect clients to new DC name
5. Remove old DC

!!! warning "Complex Operation"
    DC renaming is effectively adding a new DC and removing the old one. Plan for significant downtime or accept temporary doubled hardware.

---

## Cross-DC Consistency Considerations

### Consistency Level Behavior

| Consistency Level | Multi-DC Behavior |
|-------------------|-------------------|
| `ONE` | Satisfied by any DC |
| `LOCAL_ONE` | Must be satisfied in coordinator's DC |
| `QUORUM` | Majority across ALL DCs |
| `LOCAL_QUORUM` | Majority in coordinator's DC only |
| `EACH_QUORUM` | Majority in EACH DC |
| `ALL` | All replicas in ALL DCs |

### Recommended Settings

| Use Case | Write CL | Read CL |
|----------|----------|---------|
| Strong local consistency | `LOCAL_QUORUM` | `LOCAL_QUORUM` |
| Global strong consistency | `QUORUM` | `QUORUM` |
| Availability priority | `LOCAL_ONE` | `LOCAL_ONE` |
| Cross-DC reads during DC failure | `QUORUM` | `QUORUM` |

!!! tip "LOCAL_QUORUM Recommendation"
    For most multi-DC deployments, `LOCAL_QUORUM` provides the best balance of consistency and availability. It ensures strong consistency within each DC while tolerating complete DC failure.

---

## Troubleshooting

### Rebuild Stalled

**Symptoms:** `nodetool netstats` shows no progress

```bash
# Check source DC health
nodetool status

# Check network connectivity
nc -zv dc1-node1 7000

# Check logs
grep -i "stream\|rebuild" /var/log/cassandra/system.log | tail -50
```

**Solutions:**

1. Verify cross-DC network connectivity
2. Check source DC capacity (may be overwhelmed)
3. Increase streaming timeouts

### Authentication Failures in New DC

**Symptoms:** Nodes can't authenticate after joining

**Cause:** `system_auth` not replicated to new DC before nodes joined

**Solution:**

```sql
-- Update system_auth replication
ALTER KEYSPACE system_auth WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3,
    'dc2': 3
};

-- Run repair on system_auth
nodetool repair system_auth
```

### Cross-DC Latency Issues

**Symptoms:** Client requests slow when coordinator in different DC

**Solutions:**

1. Use `LOCAL_QUORUM` instead of `QUORUM`
2. Configure client with correct local DC:

```java
.withLocalDatacenter("dc1")
```

3. Review cross-DC network performance

---

## Related Documentation

- **[Cluster Management Overview](index.md)** - Operation selection
- **[Adding Nodes](adding-nodes.md)** - Bootstrap procedures
- **[Removing Nodes](removing-nodes.md)** - Decommission procedures
- **[Consistency Levels](../../architecture/distributed-data/consistency-levels.md)** - Multi-DC consistency
