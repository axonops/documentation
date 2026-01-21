---
title: "nodetool statusgossip"
description: "Check if gossip protocol is enabled using nodetool statusgossip command."
meta:
  - name: keywords
    content: "nodetool statusgossip, gossip status, gossip protocol, Cassandra"
search:
  boost: 3
---

# nodetool statusgossip

Displays the status of the gossip protocol.

---

## Synopsis

```bash
nodetool [connection_options] statusgossip
```

## Description

`nodetool statusgossip` shows whether the gossip protocol is running on this node. Gossip is the peer-to-peer protocol Cassandra uses for cluster membership and failure detection.

---

## Output

### Running

```
running
```

Gossip is active. The node is communicating with other cluster members.

### Not Running

```
not running
```

Gossip is disabled. The node is isolated from the cluster.

---

## Examples

### Check Status

```bash
nodetool statusgossip
```

### Use in Scripts

```bash
if [ "$(nodetool statusgossip)" = "running" ]; then
    echo "Node is participating in cluster"
else
    echo "Node is isolated"
fi
```

---

## Understanding Gossip

Gossip handles:

- **Cluster membership**: Who is in the cluster
- **Failure detection**: Which nodes are alive/dead
- **Schema changes**: Propagating DDL changes
- **State sharing**: Sharing node metadata

---

## Use Cases

### Verify Cluster Participation

```bash
nodetool statusgossip
```

### Pre-Maintenance Check

```bash
# Check current state
nodetool statusgossip

# Disable gossip (isolates node)
nodetool disablegossip

# Perform maintenance...

# Re-enable gossip
nodetool enablegossip

# Verify
nodetool statusgossip
```

### Node Health Check

```bash
#!/bin/bash
GOSSIP=$(nodetool statusgossip)
BINARY=$(nodetool statusbinary)

if [ "$GOSSIP" = "running" ]; then
    echo "Gossip: OK"
else
    echo "WARNING: Gossip disabled - node is isolated!"
fi

if [ "$BINARY" = "running" ]; then
    echo "Binary: OK"
else
    echo "WARNING: CQL disabled - no client connections!"
fi
```

---

## When Gossip is Disabled

!!! danger "Isolated Node"
    When gossip is disabled:

    - Node cannot detect other nodes
    - Other nodes may mark this node as DOWN
    - Schema changes won't propagate
    - The node is effectively isolated

### Intentional Disable

For certain maintenance operations:

```bash
# Isolate node temporarily
nodetool disablegossip

# Do maintenance...

# Rejoin cluster
nodetool enablegossip
```

### After Node Restart

Gossip should automatically start. If not:

1. Check logs for errors
2. Verify seed nodes configuration
3. Check network connectivity

```bash
# Check logs
grep -i gossip /var/log/cassandra/system.log | tail -20
```

---

## Gossip vs Binary Status

| Status | Gossip | Binary | Node State |
|--------|--------|--------|------------|
| Normal | running | running | Fully operational |
| Maintenance | running | not running | In cluster but not serving clients |
| Isolated | not running | - | Not participating in cluster |
| Starting | running | not running | Still initializing |

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [enablegossip](enablegossip.md) | Enable gossip |
| [disablegossip](disablegossip.md) | Disable gossip |
| [gossipinfo](gossipinfo.md) | Detailed gossip state |
| [statusbinary](statusbinary.md) | CQL transport status |
| [status](status.md) | Cluster overview |
