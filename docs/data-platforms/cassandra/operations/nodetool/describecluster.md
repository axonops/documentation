---
title: "nodetool describecluster"
description: "Display cluster information including schema versions and snitch using nodetool describecluster."
meta:
  - name: keywords
    content: "nodetool describecluster, cluster info, schema version, Cassandra snitch"
search:
  boost: 3
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
        DatabaseVersion: 4.1.3
Schema versions:
        a1b2c3d4-e5f6-7890-abcd-ef1234567890: [192.168.1.101, 192.168.1.102, 192.168.1.103]

Effective Dynamic Snitch Scores:
        /192.168.1.101: 0.001
        /192.168.1.102: 0.002
        /192.168.1.103: 0.001
```

---

## Output Fields

### Cluster Information

| Field | Description |
|-------|-------------|
| Name | Cluster name from cassandra.yaml |
| Snitch | Endpoint snitch class in use |
| DynamicEndPointSnitch | Whether dynamic snitch is enabled |
| DatabaseVersion | Cassandra version |

### Schema Versions

Shows which schema version each node has:

```
Schema versions:
        <schema-version-uuid>: [list of nodes]
```

### Dynamic Snitch Scores

Performance scores for each node (lower is better):

```
Effective Dynamic Snitch Scores:
        /192.168.1.101: 0.001
        /192.168.1.102: 0.050
        /192.168.1.103: 0.002
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

### Dynamic Snitch Scores

Scores reflect recent performance:

| Score | Meaning |
|-------|---------|
| ~0.001 | Excellent performance |
| 0.01-0.05 | Good performance |
| > 0.1 | Slow compared to others |
| Very high | Node may have issues |

!!! tip "Score Interpretation"
    High dynamic snitch scores cause coordinators to prefer other replicas:

    - Can indicate slow disk I/O
    - Network latency issues
    - GC problems
    - Overloaded node

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
