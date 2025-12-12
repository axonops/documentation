---
description: "Cassandra snitch configuration. Data center and rack awareness settings."
meta:
  - name: keywords
    content: "Cassandra snitch, rack awareness, data center topology"
---

# Cassandra Snitch Configuration

The snitch determines how Cassandra maps nodes to datacenters and racks.

## Available Snitches

| Snitch | Use Case |
|--------|----------|
| SimpleSnitch | Single DC, no rack awareness |
| GossipingPropertyFileSnitch | Production (recommended) |
| PropertyFileSnitch | Legacy |
| Ec2Snitch | AWS single region |
| Ec2MultiRegionSnitch | AWS multi-region |
| GoogleCloudSnitch | GCP |
| RackInferringSnitch | IP-based inference |

## GossipingPropertyFileSnitch (Recommended)

### Configuration

```yaml
# cassandra.yaml
endpoint_snitch: GossipingPropertyFileSnitch
```

```properties
# cassandra-rackdc.properties
dc=datacenter1
rack=rack1

# Optional
prefer_local=true
dc_suffix=_analytics
```

### Multi-DC Setup

```properties
# Node in DC1
dc=us-east
rack=rack1

# Node in DC2
dc=eu-west
rack=rack1
```

## Cloud Snitches

### AWS (Ec2Snitch)

```yaml
# cassandra.yaml
endpoint_snitch: Ec2Snitch

# Automatic:
# DC = region (us-east-1)
# Rack = availability zone (us-east-1a)
```

### AWS Multi-Region

```yaml
# cassandra.yaml
endpoint_snitch: Ec2MultiRegionSnitch
listen_address: <private_ip>
broadcast_address: <public_ip>
```

### GCP

```yaml
# cassandra.yaml
endpoint_snitch: GoogleCloudSnitch

# Automatic:
# DC = project:region
# Rack = zone
```

## Changing Snitch

```bash
# 1. Update cassandra.yaml on all nodes
# 2. Update cassandra-rackdc.properties
# 3. Rolling restart cluster
# 4. Run repair

nodetool repair -full
```

## Verifying Topology

```bash
# Check datacenter/rack assignment
nodetool status

# Detailed gossip info
nodetool gossipinfo | grep -E "DC|RACK"
```

---

## Next Steps

- **[cassandra.yaml](../cassandra-yaml/index.md)** - Main config
- **[Replication](../../../architecture/distributed-data/replication.md)** - Replication config
