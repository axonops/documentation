---
title: "nodetool getseeds"
description: "Display seed nodes for the Cassandra cluster using nodetool getseeds command."
meta:
  - name: keywords
    content: "nodetool getseeds, seed nodes, Cassandra cluster, cluster discovery"
---

# nodetool getseeds

Displays the seed node addresses.

---

## Synopsis

```bash
nodetool [connection_options] getseeds
```
See [connection options](index.md#connection-options) for connection options.

## Description

`nodetool getseeds` shows the currently configured seed nodes for this Cassandra node. Seed nodes are contact points used for cluster discovery and gossip bootstrapping.

---

## Examples

### Basic Usage

```bash
nodetool getseeds
```

### Sample Output

```
Current list of seed node IPs, excluding the current node's IP: 192.168.1.101, 192.168.1.102, 192.168.1.103
```

If this node is the only seed or no remote seeds are configured:

```
Current list of seed node IPs, excluding the current node's IP: (no remote seed IPs)
```

---

## Configuration

```yaml
# cassandra.yaml
seed_provider:
  - class_name: org.apache.cassandra.locator.SimpleSeedProvider
    parameters:
      - seeds: "192.168.1.101,192.168.1.102,192.168.1.103"
```

---

## Use Cases

### Verify Seed Configuration

```bash
nodetool getseeds
```

### Troubleshoot Cluster Discovery

```bash
# Check seeds when node can't join cluster
nodetool getseeds
```

---

## Best Practices

!!! tip "Seed Node Guidelines"

    1. **Multiple seeds** - Configure 2-3 seeds per datacenter
    2. **Stable nodes** - Choose reliable, long-running nodes
    3. **Not all nodes** - Don't make every node a seed

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [reloadseeds](reloadseeds.md) | Reload seed configuration |
| [gossipinfo](gossipinfo.md) | View gossip state |
| [status](status.md) | Cluster overview |