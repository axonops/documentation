---
title: "nodetool gossipinfo"
description: "Display gossip information for all nodes in Cassandra cluster using nodetool gossipinfo."
meta:
  - name: keywords
    content: "nodetool gossipinfo, gossip protocol, node information, Cassandra cluster"
---

# nodetool gossipinfo

Displays the gossip information for all nodes in the cluster as seen by the local node.

---

## Synopsis

```bash
nodetool [connection_options] gossipinfo
```
See [connection options](index.md#connection-options) for connection options.

## Description

`nodetool gossipinfo` shows detailed gossip state for every node known to the cluster, including:

- Node status and state
- Generation and heartbeat information
- Schema version
- Datacenter and rack assignment
- Token ownership
- Release version

This is essential for troubleshooting cluster communication and state issues.

---

## Output Example

```
/192.168.1.101
  generation:1699574400
  heartbeat:12345
  STATUS:16:NORMAL,-9223372036854775808
  LOAD:12340:2.56789E11
  SCHEMA:10:a1b2c3d4-e5f6-7890-abcd-ef1234567890
  DC:8:dc1
  RACK:9:rack1
  RELEASE_VERSION:7:4.1.3
  RPC_ADDRESS:3:192.168.1.101
  NATIVE_ADDRESS_AND_PORT:12:192.168.1.101:9042
  NET_VERSION:1:12
  HOST_ID:2:a1b2c3d4-e5f6-7890-abcd-ef1234567890
  TOKENS:11:<hidden>

/192.168.1.102
  generation:1699574500
  heartbeat:12346
  STATUS:16:NORMAL,-3074457345618258602
  LOAD:12341:2.48789E11
  SCHEMA:10:a1b2c3d4-e5f6-7890-abcd-ef1234567890
  DC:8:dc1
  RACK:9:rack2
  RELEASE_VERSION:7:4.1.3
  ...
```

---

## Output Fields

### Node Identification

| Field | Description |
|-------|-------------|
| IP Address | Node's broadcast address |
| HOST_ID | Unique node identifier |
| RPC_ADDRESS | Address for client connections |
| NATIVE_ADDRESS_AND_PORT | CQL native protocol endpoint |

### Generation and Heartbeat

| Field | Description |
|-------|-------------|
| generation | Epoch timestamp when node started (resets on restart) |
| heartbeat | Counter incremented each gossip round |

### Status Information

| Field | Format | Description |
|-------|--------|-------------|
| STATUS | version:state,token | Node state (NORMAL, LEAVING, etc.) |
| LOAD | version:bytes | Data size on node |
| SCHEMA | version:uuid | Schema version |

### Location

| Field | Description |
|-------|-------------|
| DC | Datacenter name |
| RACK | Rack name |

### Version Information

| Field | Description |
|-------|-------------|
| RELEASE_VERSION | Cassandra version |
| NET_VERSION | Protocol version |

---

## Interpreting Status Values

### Node States

| State | Meaning |
|-------|---------|
| NORMAL | Operating normally |
| LEAVING | Decommission in progress |
| LEFT | Has been decommissioned |
| MOVING | Moving to new token |
| BOOT | Bootstrap in progress |
| hibernate | Node is hibernating |

### Generation Number

```
generation:1699574400
```

The generation is the Unix timestamp when the node started. Uses include:

- Identifying node restarts (new generation = restart)
- Gossip conflict resolution (higher generation wins)

### Heartbeat

```
heartbeat:12345
```

Increments every gossip round (~1 second). Used to detect:

- Node liveness
- Gossip communication problems

---

## When to Use

### Troubleshoot Node Communication

```bash
nodetool gossipinfo | grep -E "^/|STATUS|heartbeat"
```

Identify nodes with stale heartbeats.

### Verify Cluster Membership

```bash
nodetool gossipinfo | grep "^/"
```

List all nodes known to gossip.

### Check Schema Agreement

```bash
nodetool gossipinfo | grep SCHEMA
```

All nodes should have the same SCHEMA UUID.

### Investigate Topology Issues

```bash
nodetool gossipinfo | grep -E "DC|RACK"
```

Verify datacenter and rack assignments.

### Debug Node Not Joining

```bash
# Check if new node appears in gossip
nodetool gossipinfo | grep <new-node-ip>
```

---

## Examples

### Basic Usage

```bash
nodetool gossipinfo
```

### Filter for Specific Node

```bash
nodetool gossipinfo | grep -A20 "/192.168.1.102"
```

### Check All Status Values

```bash
nodetool gossipinfo | grep STATUS
```

### Find Nodes Not in NORMAL State

```bash
nodetool gossipinfo | grep STATUS | grep -v NORMAL
```

### Compare Schema Across Nodes

```bash
nodetool gossipinfo | grep SCHEMA | sort | uniq -c
```

### Check for Stale Nodes

```bash
# Nodes with old generations or low heartbeats may be stale
nodetool gossipinfo | grep -E "generation|heartbeat"
```

---

## Common Issues

### Node Shows OLD Generation

If a node's generation is much older than others:

```
/192.168.1.102
  generation:1609459200  (old)
```

This node may have stale gossip information. Try:

```bash
# On the problematic node
nodetool gossipinfo  # Compare with other nodes
```

### Inconsistent Schema

```bash
nodetool gossipinfo | grep SCHEMA
```

Different SCHEMA UUIDs indicate schema disagreement. See `describecluster` for resolution.

### Node Stuck in LEAVING

```
STATUS:16:LEAVING,-9223372036854775808
```

Decommission may have failed. Check logs and consider:

```bash
# If node is dead and stuck
nodetool assassinate <ip-address>
```

### Ghost Node (LEFT but Still Appearing)

```
STATUS:16:LEFT,-9223372036854775808
```

Node was decommissioned but still in gossip. Usually clears automatically, but if persistent:

```bash
nodetool assassinate <ip-address>
```

### Missing Node in Gossip

If a node doesn't appear:

1. Check if node is running
2. Check network connectivity
3. Verify seed configuration
4. Check firewall rules for gossip port (7000/7001)

---

## Gossip Troubleshooting Flow

| Check | If No | If Yes |
|-------|-------|--------|
| Node appears in gossipinfo? | Check network/firewall, verify seeds | Continue to next check |
| Heartbeat increasing? | Node may be frozen - check GC and resources | Continue to next check |
| Status is NORMAL? | Check for stuck operations, may need intervention | Continue to next check |
| Schema matches other nodes? | Wait for propagation or reload schema | Node is healthy |

---

## Gossip vs. Status

| Command | Shows | Use For |
|---------|-------|---------|
| `gossipinfo` | Full gossip state, all fields | Debugging, detailed analysis |
| `status` | Summary view, key metrics | Quick health check |

Use `gossipinfo` when `status` doesn't provide enough detail.

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [status](status.md) | Summary cluster status |
| [describecluster](describecluster.md) | Cluster metadata and schema |
| [ring](ring.md) | Token distribution |
| [enablegossip](enablegossip.md) | Enable gossip |
| [disablegossip](disablegossip.md) | Disable gossip |
| [statusgossip](statusgossip.md) | Check if gossip enabled |
| [assassinate](assassinate.md) | Force remove stuck node |