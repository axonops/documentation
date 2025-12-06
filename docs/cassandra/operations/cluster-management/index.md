# Cassandra Cluster Management

Need more capacity? Add a node—Cassandra automatically rebalances data while serving traffic. Node died? Replace it without taking the cluster offline. Decommissioning old hardware? Stream data off gracefully, then remove it from the ring.

These operations work because Cassandra has no master. Every node knows the cluster topology through gossip, and token ranges determine which nodes own which data. When topology changes, nodes stream data to their new owners in the background.

The one gotcha: after adding nodes, existing nodes still have copies of data they no longer own. Run `nodetool cleanup` to reclaim that space.

This guide covers the procedures for scaling and maintaining cluster topology.

## Cluster Operations

| Operation | Command | Impact |
|-----------|---------|--------|
| Add node | Start with proper config | Streaming |
| Remove node | `nodetool decommission` | Streaming |
| Replace node | `replace_address_first_boot` | Streaming |
| Move node | `nodetool move` | Streaming |

## Adding a Node

```bash
# 1. Install Cassandra on new node

# 2. Configure cassandra.yaml
cluster_name: 'ExistingCluster'
seeds: "existing_seed1,existing_seed2"
listen_address: <new_node_ip>

# 3. Start Cassandra
sudo systemctl start cassandra

# 4. Monitor bootstrap
nodetool netstats

# 5. Verify node joined
nodetool status

# 6. Run cleanup on existing nodes
nodetool cleanup
```

## Removing a Node

### Graceful Decommission (Node is up)

```bash
# On node to remove
nodetool decommission

# Monitor progress
nodetool netstats

# Verify removal
nodetool status  # Node should not appear
```

### Force Remove (Node is down)

```bash
# Get host ID
nodetool status

# Remove by host ID
nodetool removenode <host_id>

# If stuck, force
nodetool removenode force <host_id>
```

## Replacing a Node

```bash
# 1. Configure new node
# cassandra.yaml or JVM options
JVM_OPTS="$JVM_OPTS -Dcassandra.replace_address_first_boot=<dead_node_ip>"

# 2. Start new node
sudo systemctl start cassandra

# 3. Monitor replacement
nodetool netstats

# 4. Verify
nodetool status

# 5. Remove JVM option and restart
```

## Checking Cluster Health

```bash
# Node status
nodetool status

# Cluster description
nodetool describecluster

# Schema agreement
nodetool describecluster | grep "Schema versions"

# Ring topology
nodetool ring
```

## Token Management

```bash
# View token ranges
nodetool ring

# Get endpoints for key
nodetool getendpoints keyspace table key

# Describe ring for keyspace
nodetool describering keyspace
```

---

## Next Steps

- **[Adding Nodes](adding-nodes.md)** - Detailed guide
- **[Removing Nodes](removing-nodes.md)** - Safe removal
- **[Replacing Nodes](replacing-nodes.md)** - Node replacement
