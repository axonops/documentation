---
title: "nodetool disablegossip"
description: "Disable gossip protocol on a Cassandra node using nodetool disablegossip. Use before maintenance."
meta:
  - name: keywords
    content: "nodetool disablegossip, disable gossip, Cassandra gossip, node maintenance"
---

# nodetool disablegossip

Disables the gossip protocol, isolating the node from cluster communication.

---

## Synopsis

```bash
nodetool [connection_options] disablegossip
```

## Description

`nodetool disablegossip` stops the node from participating in the gossip protocol. This effectively isolates the node from the rest of the cluster while keeping the Cassandra process running.

### Gossip Port Configuration

The gossip protocol uses the storage port for inter-node communication, configured in `cassandra.yaml`:

```yaml
storage_port: 7000        # Default inter-node communication port (unencrypted)
ssl_storage_port: 7001    # Default inter-node communication port (encrypted)
```

To verify the gossip port is listening:

```bash
# Check if Cassandra is listening on the gossip port
netstat -tlnp | grep 7000

# Alternative using ss
ss -tlnp | grep 7000

# Check the configured ports in cassandra.yaml
grep -E "storage_port|ssl_storage_port" /etc/cassandra/cassandra.yaml
```

!!! note "Port Remains Open"
    Unlike `disablebinary`, the `disablegossip` command does not close the storage port. The port remains open, but the node stops actively participating in the gossip protocol (no heartbeats sent, no state updates processed).

Gossip is responsible for:

- **Cluster membership** - Tracking which nodes are in the cluster
- **Failure detection** - Heartbeats to determine node liveness
- **Schema propagation** - Distributing DDL changes
- **State sharing** - Exchanging node metadata

!!! danger "Critical Operation"
    Disabling gossip is a significant action that isolates the node from the cluster. Other nodes will eventually mark this node as DOWN and stop routing requests to it.

---

## Behavior

When gossip is disabled:

1. The node stops sending heartbeats to other nodes
2. The node stops receiving cluster state updates
3. Other nodes will mark this node as DOWN (typically within 10-30 seconds)
4. Schema changes made elsewhere will not be received
5. The node continues running but is cluster-isolated

---

## Examples

### Basic Usage

```bash
nodetool disablegossip
```

### Verify Disabled

```bash
nodetool disablegossip
nodetool statusgossip
# Expected output: not running
```

### With Verification on Other Node

```bash
# On target node
nodetool disablegossip

# After ~30 seconds, on another node
nodetool status
# Target node should show as DN (Down/Normal)
```

---

## When to Use

### Controlled Node Isolation

Temporarily isolate a node for maintenance:

```bash
# Isolate from cluster
nodetool disablegossip

# Perform maintenance that requires isolation...

# Rejoin cluster
nodetool enablegossip
```

### Network Diagnostics

Isolate a node to debug network issues:

```bash
# Stop gossip traffic
nodetool disablegossip

# Capture network traffic without gossip noise
tcpdump -i eth0 port 7000

# Re-enable when done
nodetool enablegossip
```

### Testing Failure Scenarios

Simulate node failure for testing:

```bash
# Simulate down node
nodetool disablegossip

# Test application behavior with node down

# Restore
nodetool enablegossip
```

### Pre-Shutdown Preparation

Some maintenance procedures disable gossip before stopping:

```bash
# Stop accepting clients
nodetool disablebinary

# Stop gossip (isolated)
nodetool disablegossip

# Node is now isolated before actual shutdown
```

---

## When NOT to Use

!!! warning "Avoid in These Scenarios"

    - **Extended periods in production** - Node will be excluded from cluster operations
    - **Without a recovery plan** - Always know how to re-enable
    - **Instead of drain** - For graceful shutdown, use `drain` instead
    - **For load reduction** - Use `disablebinary` to stop client connections instead

### Prefer drain for Shutdown

For graceful shutdown, use drain rather than disablegossip:

```bash
# Correct: Graceful shutdown
nodetool drain

# Incorrect: Using disablegossip for shutdown
nodetool disablegossip  # Leaves node in ambiguous state
```

---

## Workflow: Controlled Isolation

```bash
# 1. Document current state
nodetool status
nodetool statusgossip

# 2. First disable client connections
nodetool disablebinary

# 3. Wait for in-flight requests to complete
sleep 10

# 4. Disable gossip (full isolation)
nodetool disablegossip

# 5. Verify isolation
nodetool statusgossip  # not running
nodetool statusbinary  # not running

# 6. Perform maintenance...

# 7. Re-enable in correct order
nodetool enablegossip
sleep 5  # Allow cluster synchronization
nodetool enablebinary

# 8. Verify restored
nodetool status  # Node should be UN
```

---

## Order of Operations

### Isolating a Node

| Step | Command | Effect |
|------|---------|--------|
| 1 | `disablebinary` | Stop new client connections |
| 2 | Wait for requests | Allow in-flight operations to complete |
| 3 | `disablegossip` | Isolate from cluster |

### Restoring a Node

| Step | Command | Effect |
|------|---------|--------|
| 1 | `enablegossip` | Rejoin cluster first |
| 2 | Wait 5-10 seconds | Allow state synchronization |
| 3 | `enablebinary` | Accept client connections |

---

## Impact on Cluster

### Immediate Effects

| Aspect | Impact |
|--------|--------|
| Heartbeats | Stop immediately |
| Cluster view | Node has stale information |
| Schema sync | No updates received |
| New nodes | Won't learn about them |

### Delayed Effects (10-30 seconds)

| Aspect | Impact |
|--------|--------|
| Node status | Marked as DOWN by others |
| Request routing | Traffic redirected to other nodes |
| Replication | This node excluded from writes |
| Hint storage | Hints stored for this node on coordinators |

### Long-term Effects

| Aspect | Impact |
|--------|--------|
| Data consistency | May need repair after rejoining |
| Hints | May accumulate on other nodes |
| Schema drift | May miss schema changes |

---

## Gossip vs Binary vs Drain

| Command | Gossip | Binary | Use Case |
|---------|--------|--------|----------|
| `disablegossip` | Disabled | Unchanged | Network debugging, testing |
| `disablebinary` | Running | Disabled | Stop clients, stay in cluster |
| `drain` | Disabled | Disabled | Graceful shutdown |

### State Combinations

| Gossip | Binary | Node State | Description |
|--------|--------|------------|-------------|
| Running | Running | Fully operational | Normal state |
| Running | Disabled | In cluster, no clients | Maintenance mode |
| Disabled | Running | Dangerous | Accepts requests but isolated |
| Disabled | Disabled | Fully isolated | Prepared for shutdown |

!!! danger "Avoid Gossip Disabled + Binary Enabled"
    Never disable gossip while leaving binary enabled. The node would accept client requests but cannot properly coordinate with the cluster, leading to consistency issues.

---

## Verification

### On the Node

```bash
nodetool statusgossip
# Expected: not running
```

### From Other Nodes

```bash
# After 30 seconds
nodetool status | grep <node_ip>
# Should show DN (Down/Normal)
```

### Check Gossip Info

```bash
# On another node, check gossip state
nodetool gossipinfo | grep -A10 <node_ip>
```

---

## Troubleshooting

### Node Won't Isolate

If status still shows "running":

```bash
# Retry
nodetool disablegossip

# Check logs
tail /var/log/cassandra/system.log | grep -i gossip
```

### Other Nodes Don't See Change

If other nodes still show this node as UP:

```bash
# Wait longer (gossip failure detection takes time)
sleep 60

# Check from multiple nodes
for node in node2 node3; do
    echo "=== $node ==="
    ssh "$node" "nodetool status | grep <this_node>"
done
```

### Recovery Issues

If gossip won't re-enable after maintenance:

```bash
# Check JMX is responding
nodetool info

# Try enabling
nodetool enablegossip

# If still failing, may need restart
# (as last resort)
```

---

## Monitoring During Isolation

### Track Node Status

```bash
# From another node, monitor status change
watch -n 5 'nodetool status'
```

### Check Hints Accumulation

```bash
# On other nodes, hints will accumulate for isolated node
nodetool tpstats | grep -i hint
```

### Monitor Logs

```bash
# On isolated node
tail -f /var/log/cassandra/system.log | grep -i gossip
```

---

## Automation Script

```bash
#!/bin/bash
# isolate_node.sh - Safely isolate a node from the cluster

echo "=== Current State ==="
echo "Gossip: $(nodetool statusgossip)"
echo "Binary: $(nodetool statusbinary)"

echo ""
echo "=== Isolating Node ==="

# Step 1: Disable binary first
echo "Disabling client connections..."
nodetool disablebinary
sleep 5

# Step 2: Disable gossip
echo "Disabling gossip (isolating from cluster)..."
nodetool disablegossip

# Verify
echo ""
echo "=== Verification ==="
echo "Gossip: $(nodetool statusgossip)"  # Should be: not running
echo "Binary: $(nodetool statusbinary)"  # Should be: not running

echo ""
echo "Node is now isolated from the cluster."
echo "Other nodes will mark this node as DOWN within 30 seconds."
echo ""
echo "To rejoin cluster:"
echo "  nodetool enablegossip"
echo "  sleep 5"
echo "  nodetool enablebinary"
```

---

## Best Practices

!!! tip "Gossip Disable Guidelines"

    1. **Document the reason** - Note why gossip was disabled
    2. **Set time limits** - Don't leave disabled indefinitely
    3. **Disable binary first** - Stop clients before isolating
    4. **Monitor other nodes** - Watch for impact on cluster
    5. **Plan recovery** - Know the steps to re-enable
    6. **Use drain for shutdown** - Prefer `drain` over manual gossip disable
    7. **Test in non-production** - Understand behavior before using in production

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [enablegossip](enablegossip.md) | Re-enable gossip protocol |
| [statusgossip](statusgossip.md) | Check gossip status |
| [gossipinfo](gossipinfo.md) | View detailed gossip state |
| [disablebinary](disablebinary.md) | Disable CQL connections |
| [drain](drain.md) | Graceful shutdown preparation |
| [status](status.md) | View cluster status |
