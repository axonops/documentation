# Multi-Datacenter Cassandra Guide

Cassandra was built for multi-datacenter deployments. Clusters can run across AWS regions, between cloud providers, or spanning continents—and if an entire datacenter goes offline, traffic automatically routes to the survivors.

The key is LOCAL_QUORUM consistency: reads and writes only wait for acknowledgment from replicas in the local datacenter, while remote datacenters receive updates asynchronously. This provides local latency with geographic redundancy.

The trade-offs are real: cross-DC replication adds complexity, repair takes longer, and misconfiguring consistency levels can cause either availability loss (if too many replicas are required) or silent inconsistency (if too few are required). This guide covers how to set it up correctly.

## Multi-DC Overview

### Benefits

| Benefit | Description |
|---------|-------------|
| **High Availability** | Survive entire DC failure |
| **Disaster Recovery** | Geographic redundancy |
| **Low Latency** | Local reads for global users |
| **Compliance** | Data residency requirements |
| **Load Distribution** | Spread traffic across regions |

### Architecture Patterns

```
Pattern 1: Active-Active (Recommended)
┌─────────────────┐     ┌─────────────────┐
│    US-EAST      │◄───►│    EU-WEST      │
│   RF = 3        │     │   RF = 3        │
│   Reads/Writes  │     │   Reads/Writes  │
└─────────────────┘     └─────────────────┘
Both DCs handle traffic, data replicated between them

Pattern 2: Active-Passive
┌─────────────────┐     ┌─────────────────┐
│    PRIMARY      │────►│    BACKUP       │
│   RF = 3        │     │   RF = 3        │
│   All traffic   │     │   DR only       │
└─────────────────┘     └─────────────────┘
Backup DC receives replication, no client traffic

Pattern 3: Active-Active-Active
┌─────────────────┐
│    US-EAST      │
│   RF = 3        │
└────────┬────────┘
         │
┌────────┴────────┐
│                 │
▼                 ▼
┌─────────┐ ┌─────────┐
│ US-WEST │ │ EU-WEST │
│  RF = 3 │ │  RF = 3 │
└─────────┘ └─────────┘
Three DCs, each handling local traffic
```

---

## Planning Multi-DC Deployment

### Network Requirements

| Requirement | Specification |
|-------------|---------------|
| Bandwidth | 1+ Gbps between DCs |
| Latency | < 100ms round trip |
| Reliability | Redundant links recommended |
| Ports | 7000 (inter-node), 7001 (SSL), 9042 (CQL) |

### Sizing Considerations

```
Per-DC sizing:
- Minimum 3 nodes per DC (for RF=3)
- Recommended 3 racks per DC
- Same hardware specs across DCs
- Account for cross-DC replication overhead

Data growth:
- Cross-DC replication doubles write volume
- Plan storage for full dataset in each DC
- Commit log space for cross-DC hints
```

### Replication Strategy

```sql
-- Always use NetworkTopologyStrategy for multi-DC
CREATE KEYSPACE global_app WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'us-east': 3,
    'eu-west': 3
};

-- Never SimpleStrategy in multi-DC!
```

---

## Configuration

### Snitch Configuration

```yaml
# cassandra.yaml (all nodes)
endpoint_snitch: GossipingPropertyFileSnitch
```

```properties
# cassandra-rackdc.properties

# US-EAST nodes:
dc=us-east
rack=rack1

# EU-WEST nodes:
dc=eu-west
rack=rack1
```

### Seed Configuration

```yaml
# cassandra.yaml
# Include seeds from ALL datacenters
seed_provider:
  - class_name: org.apache.cassandra.locator.SimpleSeedProvider
    parameters:
      - seeds: "10.0.0.1,10.0.0.2,10.1.0.1,10.1.0.2"
                # US-EAST seeds    EU-WEST seeds

# Guidelines:
# - 2-3 seeds per datacenter
# - Seeds should be stable nodes
# - Don't make all nodes seeds
```

### Network Configuration

```yaml
# cassandra.yaml

# For nodes with public and private IPs:
listen_address: 10.0.0.1          # Private IP (internal)
broadcast_address: 52.1.2.3       # Public IP (cross-DC)
rpc_address: 10.0.0.1             # Client connections
broadcast_rpc_address: 10.0.0.1   # Advertised to clients

# For AWS multi-region:
# Use Ec2MultiRegionSnitch
endpoint_snitch: Ec2MultiRegionSnitch
```

### Internode Communication

```yaml
# cassandra.yaml

# Compress cross-DC traffic
internode_compression: dc  # Only cross-DC traffic

# SSL for cross-DC (recommended)
server_encryption_options:
    internode_encryption: dc  # Encrypt cross-DC only
    # Or 'all' for all traffic
    keystore: /etc/cassandra/certs/keystore.jks
    keystore_password: password
    truststore: /etc/cassandra/certs/truststore.jks
    truststore_password: password
```

---

## Consistency Levels for Multi-DC

### Consistency Level Reference

| Level | Scope | Use Case |
|-------|-------|----------|
| LOCAL_ONE | Local DC | Fastest, eventual |
| LOCAL_QUORUM | Local DC | Strong local consistency |
| EACH_QUORUM | All DCs | Strong global consistency |
| QUORUM | Global | Majority overall |
| ONE | Any DC | Eventual, any replica |
| ALL | All DCs | Strongest, lowest availability |

### Recommended Patterns

```sql
-- Standard multi-DC (most common)
-- Writes: LOCAL_QUORUM (fast, local consistency)
-- Reads: LOCAL_QUORUM (fast, strong local)
CONSISTENCY LOCAL_QUORUM;
INSERT INTO users ...;
SELECT * FROM users ...;

-- Cross-DC consistency required
-- Writes: EACH_QUORUM (ensure all DCs)
-- Reads: QUORUM (majority overall)
CONSISTENCY EACH_QUORUM;
INSERT INTO critical_data ...;

-- High performance, eventual consistency
-- Writes: LOCAL_ONE
-- Reads: LOCAL_ONE
CONSISTENCY LOCAL_ONE;
INSERT INTO metrics ...;
```

### Write Path with LOCAL_QUORUM

```
Write with LOCAL_QUORUM (RF=3 per DC):

Client (US) ──► Coordinator (US-EAST)
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
    US Node 1   US Node 2   US Node 3    ← Local replicas
        │           │           │
        └─────┬─────┘           │
              ▼                 │
         Return to client       │
         (2 local ACKs)         │
                                │
                    Async to EU-WEST ──►
                                        │
                            ┌───────────┼───────────┐
                            ▼           ▼           ▼
                        EU Node 1   EU Node 2   EU Node 3
```

---

## Deploying Multi-DC Cluster

### Step 1: Deploy First Datacenter

```bash
# Configure all nodes in DC1
# cassandra.yaml
cluster_name: 'GlobalCluster'
listen_address: <node_ip>
seeds: "10.0.0.1,10.0.0.2"
endpoint_snitch: GossipingPropertyFileSnitch

# cassandra-rackdc.properties
dc=us-east
rack=rack1

# Start DC1 nodes one at a time
sudo systemctl start cassandra
nodetool status
```

### Step 2: Create Keyspaces

```sql
-- Create with both DCs (DC2 will be empty initially)
CREATE KEYSPACE my_app WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'us-east': 3,
    'eu-west': 3
};
```

### Step 3: Deploy Second Datacenter

```bash
# Configure DC2 nodes
# cassandra.yaml
cluster_name: 'GlobalCluster'  # SAME cluster name
listen_address: <node_ip>
broadcast_address: <public_ip>  # If needed for cross-DC
seeds: "10.0.0.1,10.1.0.1"     # Include seeds from both DCs
endpoint_snitch: GossipingPropertyFileSnitch

# cassandra-rackdc.properties
dc=eu-west
rack=rack1

# Start DC2 nodes
sudo systemctl start cassandra
```

### Step 4: Stream Data to New DC

```bash
# On each node in the new DC
nodetool rebuild -- us-east

# Monitor progress
nodetool netstats

# Verify data
nodetool status my_app
```

---

## Operational Procedures

### Cross-DC Repair

```bash
# Repair within each DC separately
# On US-EAST nodes:
nodetool repair -pr -dc us-east my_app

# On EU-WEST nodes:
nodetool repair -pr -dc eu-west my_app

# Cross-DC repair (when needed)
nodetool repair -pr my_app
```

### Rolling Restart

```bash
# Restart one DC at a time
# Start with non-primary DC

# DC2 (EU-WEST):
for node in eu-west-1 eu-west-2 eu-west-3; do
    ssh $node "nodetool drain && sudo systemctl restart cassandra"
    # Wait for node to be UN
    sleep 60
done

# Then DC1 (US-EAST):
for node in us-east-1 us-east-2 us-east-3; do
    ssh $node "nodetool drain && sudo systemctl restart cassandra"
    sleep 60
done
```

### Adding a Datacenter

```bash
# 1. Configure new DC nodes (do not start yet)
# 2. Update seeds in all nodes (rolling restart existing)
# 3. Start new DC nodes
# 4. Update keyspace replication
ALTER KEYSPACE my_app WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'us-east': 3,
    'eu-west': 3,
    'ap-south': 3  # New DC
};

# 5. Rebuild data on new DC
# On each new node:
nodetool rebuild -- us-east
```

### Removing a Datacenter

```bash
# 1. Redirect all traffic away from DC
# 2. Update keyspace to remove DC
ALTER KEYSPACE my_app WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'us-east': 3
    # eu-west removed
};

# 3. Run repair on remaining DCs
nodetool repair -pr my_app

# 4. Decommission nodes in removed DC
# On each node:
nodetool decommission

# 5. Remove from seeds configuration
```

---

## Failover and Recovery

### DC Failure Scenarios

```
Scenario 1: Complete DC Loss
┌─────────────────┐     ┌─────────────────┐
│    US-EAST      │     │    EU-WEST      │
│   ████████      │     │   (OFFLINE)     │
│   All traffic   │     │                 │
└─────────────────┘     └─────────────────┘

Actions:
1. Traffic automatically routes to live DC
2. LOCAL_QUORUM operations continue
3. EACH_QUORUM operations fail
4. Monitor hints accumulation
```

### Handling DC Failure

```bash
# 1. Monitor hint storage
nodetool tpstats | grep Hint

# 2. If hints exceed threshold, consider reducing
# hinted_handoff_throttle_in_kb or max_hint_window_in_ms

# 3. When DC recovers:
# Start nodes
# Hints replay automatically
# Run repair to ensure consistency
nodetool repair -pr -dc eu-west my_app
```

### Disaster Recovery

```bash
# If DC is permanently lost:

# 1. Remove dead DC from topology
ALTER KEYSPACE my_app WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'us-east': 3
};

# 2. Remove dead nodes
nodetool removenode <host_id>  # For each dead node

# 3. Build replacement DC (new infrastructure)
# Follow "Adding a Datacenter" procedure

# 4. Restore replication
ALTER KEYSPACE my_app WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'us-east': 3,
    'eu-west-new': 3
};

# 5. Rebuild new DC
nodetool rebuild -- us-east
```

---

## Client Configuration

### Driver Configuration

```java
// Java driver - multi-DC aware
CqlSession session = CqlSession.builder()
    .addContactPoints(
        InetSocketAddress.createUnresolved("us-east-1.example.com", 9042),
        InetSocketAddress.createUnresolved("eu-west-1.example.com", 9042)
    )
    .withLocalDatacenter("us-east")  // REQUIRED
    .withLoadBalancingPolicy(
        new DefaultLoadBalancingPolicy.Builder()
            .withLocalDatacenter("us-east")
            .withDatacenterFailoverAllowedFor(
                FailoverPolicy.ON_TIMEOUT_OR_UNAVAILABLE)  // Failover to remote DC
            .build()
    )
    .build();
```

```python
# Python driver
from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy

cluster = Cluster(
    contact_points=['us-east-1.example.com', 'eu-west-1.example.com'],
    load_balancing_policy=DCAwareRoundRobinPolicy(
        local_dc='us-east',
        used_hosts_per_remote_dc=1  # Allow remote DC failover
    )
)
```

### Application Patterns

```java
// Use LOCAL_QUORUM for most operations
SimpleStatement stmt = SimpleStatement.builder("SELECT * FROM users WHERE id = ?")
    .setConsistencyLevel(DefaultConsistencyLevel.LOCAL_QUORUM)
    .build();

// Use EACH_QUORUM for critical writes
SimpleStatement critical = SimpleStatement.builder("INSERT INTO orders ...")
    .setConsistencyLevel(DefaultConsistencyLevel.EACH_QUORUM)
    .build();

// Handle unavailable errors
try {
    session.execute(stmt);
} catch (UnavailableException e) {
    // Remote DC down, consider retry with LOCAL_QUORUM
}
```

---

## Monitoring Multi-DC

### Key Metrics

```yaml
# Cross-DC latency
- cassandra_clientrequest_latency{scope="Write",dc="remote"}

# Hints metrics (indicates cross-DC issues)
- cassandra_storage_totalhints
- cassandra_hintedhandoff_hints_total

# Per-DC metrics
- cassandra_table_operations{dc="us-east"}
- cassandra_table_operations{dc="eu-west"}
```

### Alerting

```yaml
alerts:
  # DC-specific node down
  - alert: CassandraNodeDown
    expr: up{job="cassandra"} == 0
    labels:
      severity: critical

  # Cross-DC connectivity issues
  - alert: HighCrossDCLatency
    expr: cassandra_clientrequest_latency{scope="Write",quantile="0.99"} > 200000
    labels:
      severity: warning

  # Hints accumulating (DC connectivity issue)
  - alert: HintsAccumulating
    expr: rate(cassandra_storage_totalhints[5m]) > 10
    labels:
      severity: warning
```

---

## Best Practices

### Design

- Use NetworkTopologyStrategy for all keyspaces
- Same RF in each DC for active-active
- Design for DC independence (LOCAL_QUORUM)
- Plan capacity for DC failure (other DCs handle all traffic)

### Operations

- Stagger operations across DCs
- Repair each DC separately
- Monitor cross-DC latency
- Test failover procedures regularly

### Network

- Use dedicated links between DCs
- Enable compression for cross-DC traffic
- Enable SSL for cross-DC communication
- Monitor bandwidth utilization

---

## Next Steps

- **[Replication Guide](../architecture/distributed-data/replication.md)** - Replication strategies
- **[Consistency Guide](../architecture/distributed-data/consistency.md)** - Consistency levels
- **[Operations Guide](../operations/index.md)** - Operational procedures
- **[Cloud Deployment](../cloud/index.md)** - Cloud-specific guidance
