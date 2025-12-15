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
Seeds:
192.168.1.101
192.168.1.102
192.168.1.103
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

# Verify connectivity to seeds
for seed in $(nodetool getseeds | tail -n +2); do
    ping -c 1 $seed
done
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
