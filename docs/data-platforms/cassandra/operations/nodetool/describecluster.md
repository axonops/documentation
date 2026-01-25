---
title: "nodetool describecluster"
description: "Display cluster information including schema versions and snitch using nodetool describecluster."
meta:
  - name: keywords
    content: "nodetool describecluster, cluster info, schema version, Cassandra snitch"
---

# nodetool describecluster

Displays basic cluster information including cluster name, snitch, and schema versions.

---

## Synopsis

```bash
nodetool [connection_options] describecluster
```

## Description

`nodetool describecluster` provides high-level cluster metadata:

- Cluster name
- Snitch in use
- Dynamic snitch settings
- Schema version information
- DynamicEndpointSnitch scores

This is useful for verifying cluster configuration and detecting schema disagreement.

---

## Output Example

```
Cluster Information:
        Name: Production Cluster
        Snitch: org.apache.cassandra.locator.GossipingPropertyFileSnitch
        DynamicEndPointSnitch: enabled
        Partitioner: org.apache.cassandra.dht.Murmur3Partitioner

Stats for all nodes:
        Live: 3
        Joining: 0
        Moving: 0
        Leaving: 0
        Unreachable: 0

Data Centers:
        dc1 #Nodes: 3 #Down: 0

Database versions:
        4.1.3: [192.168.1.101, 192.168.1.102, 192.168.1.103]

Keyspaces:
        my_keyspace -> Replication class: NetworkTopologyStrategy {dc1=3}
        system_auth -> Replication class: NetworkTopologyStrategy {dc1=3}

Schema versions:
        a1b2c3d4-e5f6-7890-abcd-ef1234567890: [192.168.1.101, 192.168.1.102, 192.168.1.103]
```

!!! note "Output Varies by Version"
    The exact output format varies between Cassandra versions. Some fields like "Effective Dynamic Snitch Scores" were present in older versions but may be absent in current releases.

---

## Output Fields

### Cluster Information

| Field | Description |
|-------|-------------|
| Name | Cluster name from cassandra.yaml |
| Snitch | Endpoint snitch class in use |
| DynamicEndPointSnitch | Whether dynamic snitch is enabled |
| Partitioner | Token partitioner class |

### Stats for all nodes

| Field | Description |
|-------|-------------|
| Live | Number of nodes in UN (Up/Normal) state |
| Joining | Number of nodes currently bootstrapping |
| Moving | Number of nodes moving tokens |
| Leaving | Number of nodes decommissioning |
| Unreachable | Number of nodes that cannot be reached |

### Data Centers

Shows each datacenter with node count and down node count.

### Database versions

Lists Cassandra versions with the nodes running each version.

### Keyspaces

Shows replication configuration for each keyspace.

### Schema Versions

Shows which schema version each node has:

```
Schema versions:
        <schema-version-uuid>: [list of nodes]
```

---

## Interpreting Results

### Healthy Cluster

```
Schema versions:
        a1b2c3d4-e5f6-7890-abcd-ef1234567890: [192.168.1.101, 192.168.1.102, 192.168.1.103]
```

All nodes show the same schema version = **healthy**.

### Schema Disagreement

```
Schema versions:
        a1b2c3d4-e5f6-7890-abcd-ef1234567890: [192.168.1.101, 192.168.1.102]
        b2c3d4e5-f6a7-8901-bcde-f12345678901: [192.168.1.103]
```

!!! danger "Schema Disagreement"
    Multiple schema versions indicates:

    - Recent schema change still propagating
    - Node was down during schema change
    - Network partition occurred

    **Action:** Wait for propagation or investigate the mismatched node.

### Resolving Schema Disagreement

If schema disagreement persists:

```bash
# On the disagreeing node, try reloading schema
nodetool reloadlocalschema

# If that doesn't work, restart the node
nodetool drain
sudo systemctl restart cassandra
```

---

## When to Use

### Before Schema Changes

```bash
# Verify all nodes agree on schema
nodetool describecluster
```

Don't make schema changes during disagreement.

### After Schema Changes

```bash
# Verify schema propagated
nodetool describecluster
```

All nodes should show the same schema version.

### Troubleshooting Performance

```bash
# Check dynamic snitch scores
nodetool describecluster
```

High scores indicate slow nodes.

### Initial Setup Verification

```bash
# Verify cluster configuration
nodetool describecluster
```

Confirm cluster name and snitch are correct.

---

## Examples

### Basic Usage

```bash
nodetool describecluster
```

### Check from Specific Node

```bash
ssh 192.168.1.101 "nodetool describecluster"
```

### Monitor Schema Agreement

```bash
# Wait for schema agreement
while nodetool describecluster | grep -q "Schema versions:" && \
      [ $(nodetool describecluster | grep -c "^\s*[a-f0-9]") -gt 1 ]; do
    echo "Waiting for schema agreement..."
    sleep 5
done
echo "Schema agreed"
```

### Check All Nodes

```bash
for node in node1 node2 node3; do
    echo "=== $node ==="
    ssh "$node" "nodetool describecluster | grep -A10 "Schema versions""
done
```

---

## Common Issues

### Multiple Schema Versions

**Cause:** Schema change didn't propagate to all nodes.

**Solutions:**
1. Wait - propagation can take time
2. Check if disagreeing node can reach others
3. Reload schema on disagreeing node
4. Restart disagreeing node as last resort

### "UNREACHABLE" Nodes in Schema List

```
Schema versions:
        a1b2c3d4-...: [192.168.1.101, 192.168.1.102]
        UNREACHABLE: [192.168.1.103]
```

Node 192.168.1.103 is down or unreachable. Check with `nodetool status`.

### Wrong Snitch Showing

If snitch doesn't match cassandra.yaml:

1. Verify configuration file
2. Restart node for changes to take effect
3. Ensure all nodes use the same snitch

!!! danger "Snitch Mismatch"
    All nodes MUST use the same snitch. Mismatched snitches cause incorrect replica selection and potential data loss.

---

## Snitch Types

| Snitch | Description |
|--------|-------------|
| SimpleSnitch | Single datacenter, no rack awareness |
| GossipingPropertyFileSnitch | Multi-DC, uses property file |
| PropertyFileSnitch | Multi-DC, uses static configuration |
| Ec2Snitch | AWS EC2, single region |
| Ec2MultiRegionSnitch | AWS EC2, multiple regions |
| GoogleCloudSnitch | Google Cloud Platform |
| RackInferringSnitch | Infers from IP address |

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [status](status.md) | Node status overview |
| [ring](ring.md) | Token distribution |
| [gossipinfo](gossipinfo.md) | Detailed gossip state |
| [info](info.md) | Node-specific information |
