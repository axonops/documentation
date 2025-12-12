# Setting Up a Cassandra Cluster

This guide walks through building a Cassandra cluster from scratch. It covers not just the "how" but the "why" behind each configuration choice, common mistakes that cause problems later, and how to verify the cluster is working correctly.

## Understanding Cluster Architecture First

Before configuring anything, understand the target architecture.

### What Makes a Cassandra Cluster

A Cassandra cluster is a collection of nodes that:
- **Share the same `cluster_name`** - Nodes with different cluster names will not talk to each other
- **Use the same partitioner** - How data is distributed (always Murmur3 for new clusters)
- **Communicate via gossip** - Nodes constantly share state with each other
- **Own portions of the token ring** - Each node is responsible for specific data

```
                    Token Ring Visualization

                         0 (max token)
                            │
                    ┌───────┴───────┐
                    │               │
              ┌─────┴─────┐   ┌─────┴─────┐
              │   Node A   │   │   Node B   │
              │  owns:     │   │  owns:     │
              │  0 to 33%  │   │ 33% to 66% │
              └─────┬─────┘   └─────┬─────┘
                    │               │
                    └───────┬───────┘
                            │
                     ┌──────┴──────┐
                     │   Node C    │
                     │  owns:      │
                     │ 66% to 100% │
                     └─────────────┘

When data is INSERTed:
1. Partition key is hashed → produces token (e.g., 45%)
2. Token falls in Node B's range → Node B is "primary" replica
3. Data copied to other nodes based on replication factor
```

### The Seed Node Misconception

**Seeds are NOT special nodes. They are NOT masters. They do NOT coordinate anything.**

Seeds serve exactly one purpose: **bootstrapping gossip**. When a node starts, it needs to find at least one other node to learn about the cluster. Seeds are the nodes it tries first.

```
Node Starting Up:
1. Read seed list from config: "10.0.0.1, 10.0.0.2"
2. Contact 10.0.0.1: "Hey, who's in this cluster?"
3. 10.0.0.1 responds: "Here is info about nodes A, B, C, D..."
4. New node now knows about entire cluster
5. Seeds are no longer special - node gossips with everyone
```

**Seed best practices:**
- 2-3 seeds per datacenter (never just 1)
- Seeds should be stable, long-running nodes
- Don't make all nodes seeds (defeats the purpose)
- New nodes should NOT be seeds until fully joined

### Token Allocation: `num_tokens`

Each node owns multiple token ranges. The `num_tokens` setting determines how many:

| Setting | Meaning | When to Use |
|---------|---------|-------------|
| `num_tokens: 16` | Node owns 16 random ranges | Cassandra 4.0+, recommended |
| `num_tokens: 256` | Node owns 256 random ranges | Legacy clusters |
| `num_tokens: 1` | Node owns 1 range (manual) | Special cases only |

**Why 16 tokens in Cassandra 4.0+?**

```
Before (256 tokens):
- Better distribution but HUGE overhead
- Token metadata in gossip = large messages
- Repair/streaming touches many small ranges

After (16 tokens):
- Uses allocate_tokens_for_local_replication_factor algorithm
- Near-perfect distribution with far less overhead
- Faster repairs, less memory usage
```

---

## Single-Node Development Setup

For development and testing, one node is sufficient.

### Docker (Fastest)

```bash
# Create and start container
docker run --name cassandra-dev \
  -d \
  -p 9042:9042 \
  -p 7199:7199 \
  -e CASSANDRA_CLUSTER_NAME=DevCluster \
  -e HEAP_NEWSIZE=256M \
  -e MAX_HEAP_SIZE=1G \
  cassandra:5.0

# WHAT THESE SETTINGS MEAN:
# -p 9042:9042  : CQL port (how applications connect)
# -p 7199:7199  : JMX port (how nodetool connects)
# MAX_HEAP_SIZE : JVM heap size (1G is fine for dev)

# Watch startup (takes 60-90 seconds)
docker logs -f cassandra-dev

# WHAT TO LOOK FOR:
# "Starting listening for CQL clients on /0.0.0.0:9042"
# This means Cassandra is ready

# Verify it is working
docker exec cassandra-dev nodetool status

# EXPECTED OUTPUT:
# Datacenter: datacenter1
# =======================
# Status=Up/Down
# |/ State=Normal/Leaving/Joining/Moving
# --  Address    Load       Tokens  Owns (effective)  Host ID   Rack
# UN  172.17.0.2 75.2 KiB   16      100.0%           abc123... rack1

# Connect with cqlsh
docker exec -it cassandra-dev cqlsh
```

### Local Tarball Installation

If not using Docker:

```bash
# Assuming the installation guide was followed
# and Cassandra is at /opt/cassandra

# Edit configuration
sudo nano /opt/cassandra/conf/cassandra.yaml
```

**Minimum changes for single-node development:**

```yaml
# Identify the cluster (any name)
cluster_name: 'DevCluster'

# How many token ranges this node owns
num_tokens: 16

# Network binding - localhost for single-node dev
listen_address: localhost
rpc_address: localhost

# Since we're the only node, we're our own seed
seed_provider:
  - class_name: org.apache.cassandra.locator.SimpleSeedProvider
    parameters:
      - seeds: "localhost"

# Simple snitch is fine for single-node
endpoint_snitch: SimpleSnitch
```

```bash
# Start Cassandra
sudo systemctl start cassandra

# Or manually:
/opt/cassandra/bin/cassandra -f  # -f keeps it in foreground

# Verify
nodetool status
cqlsh
```

---

## Three-Node Production Cluster

A 3-node cluster is the minimum for production because:
- Allows RF=3 (three copies of data)
- Survives loss of one node without data loss
- Enables LOCAL_QUORUM consistency

### Prerequisites Checklist

Before beginning, verify:

```bash
# ☐ Same Cassandra version on all nodes
cassandra -v  # Run on each node

# ☐ Network connectivity (all nodes can reach all other nodes)
# From node 1:
nc -zv 10.0.0.2 7000 && echo "OK" || echo "FAIL"
nc -zv 10.0.0.3 7000 && echo "OK" || echo "FAIL"
# Repeat from each node to all other nodes

# ☐ Required ports open in firewall
# 7000 - Inter-node communication (gossip)
# 7001 - Inter-node TLS (if encrypted)
# 9042 - CQL client connections
# 7199 - JMX monitoring

# ☐ NTP synchronized (critical for Cassandra!)
timedatectl status
# System clock synchronized: yes

# ☐ Same system configuration on all nodes
# - Same limits.conf
# - Same THP disabled
# - Same swap settings
```

### Network Layout

For this example:

```
Datacenter: dc1
├── Node 1: 10.0.0.1 (seed)
├── Node 2: 10.0.0.2 (seed)
└── Node 3: 10.0.0.3

All nodes in same rack: rack1
```

### Step 1: Configure Node 1 (First Seed)

```bash
# Stop Cassandra if running
sudo systemctl stop cassandra

# Clear any existing data (ONLY for fresh cluster)
sudo rm -rf /var/lib/cassandra/data/*
sudo rm -rf /var/lib/cassandra/commitlog/*
sudo rm -rf /var/lib/cassandra/saved_caches/*
sudo rm -rf /var/lib/cassandra/hints/*

# Edit configuration
sudo nano /etc/cassandra/cassandra.yaml
```

**cassandra.yaml for Node 1:**

```yaml
# ============================================================
# CLUSTER IDENTIFICATION
# ============================================================

# Must be IDENTICAL on all nodes - cannot be changed later
# Pick something meaningful to the organization
cluster_name: 'Production'

# ============================================================
# TOKEN ALLOCATION
# ============================================================

# Number of token ranges this node owns
# 16 is optimal for Cassandra 4.0+
num_tokens: 16

# Let Cassandra optimally allocate tokens
# This requires knowing the intended RF for this DC
allocate_tokens_for_local_replication_factor: 3

# ============================================================
# NETWORK CONFIGURATION
# ============================================================

# IP address to bind for inter-node communication
# Must be reachable by all other nodes
# DO NOT use 0.0.0.0 - Cassandra needs a specific IP for gossip
listen_address: 10.0.0.1

# IP address for CQL client connections
# Can be same as listen_address or 0.0.0.0 for all interfaces
rpc_address: 10.0.0.1

# If rpc_address is 0.0.0.0, this tells other nodes what IP to use
# broadcast_rpc_address: 10.0.0.1

# Port for inter-node communication
storage_port: 7000

# Port for CQL native protocol
native_transport_port: 9042

# ============================================================
# SEED NODES
# ============================================================

# Seeds are contact points for bootstrapping gossip
# Include 2-3 per datacenter for redundancy
seed_provider:
  - class_name: org.apache.cassandra.locator.SimpleSeedProvider
    parameters:
      # Comma-separated list, NO spaces after commas
      - seeds: "10.0.0.1,10.0.0.2"

# ============================================================
# SNITCH CONFIGURATION
# ============================================================

# Determines how nodes are grouped into datacenters and racks
# GossipingPropertyFileSnitch: reads DC/rack from cassandra-rackdc.properties
# ALWAYS use this for production, even single-DC
endpoint_snitch: GossipingPropertyFileSnitch

# ============================================================
# DATA DIRECTORIES
# ============================================================

# Where SSTables are stored
# For production: use dedicated SSD, ideally multiple drives
data_file_directories:
  - /var/lib/cassandra/data

# Commit log - sequential writes
# For best performance: separate SSD from data
commitlog_directory: /var/lib/cassandra/commitlog

# Saved caches (key cache, row cache if enabled)
saved_caches_directory: /var/lib/cassandra/saved_caches

# Hints for downed nodes
hints_directory: /var/lib/cassandra/hints

# ============================================================
# PERFORMANCE SETTINGS (adjust based on workload)
# ============================================================

# Concurrent reads/writes - depends on CPU cores
# General rule: 16 * number_of_cores
concurrent_reads: 32
concurrent_writes: 32
concurrent_counter_writes: 32

# Memtable settings
# memtable_heap_space_in_mb: 2048
# memtable_offheap_space_in_mb: 2048

# Compaction throughput - limit to prevent I/O storms
# 64 MB/s is conservative, increase if I/O allows
compaction_throughput_mb_per_sec: 64
```

**cassandra-rackdc.properties for Node 1:**

```bash
sudo nano /etc/cassandra/cassandra-rackdc.properties
```

```properties
# Datacenter name - used in NetworkTopologyStrategy
dc=dc1

# Rack name - used for replica placement
rack=rack1

# For multi-DC: prefer local DC for reads
# prefer_local=true
```

### Step 2: Configure Node 2 (Second Seed)

Copy configuration from Node 1, then change only these settings:

**cassandra.yaml differences:**

```yaml
# ONLY these lines are different from Node 1:
listen_address: 10.0.0.2
rpc_address: 10.0.0.2
```

**cassandra-rackdc.properties:** Same as Node 1 (same DC, same rack)

### Step 3: Configure Node 3

Copy configuration from Node 1, then change:

**cassandra.yaml differences:**

```yaml
listen_address: 10.0.0.3
rpc_address: 10.0.0.3
```

### Step 4: Start the Cluster (Order Matters!)

**Critical: Start nodes one at a time and wait for each to fully join.**

Why? When multiple nodes start simultaneously, they may:
- Pick conflicting token ranges
- Create gossip storms
- Fail to bootstrap properly

```bash
# ============================================================
# ON NODE 1 (First Seed)
# ============================================================

sudo systemctl start cassandra

# Watch the logs
sudo tail -f /var/log/cassandra/system.log

# WAIT for these messages:
# "Starting listening for CQL clients on /10.0.0.1:9042"
# "Node /10.0.0.1 state jump to NORMAL"

# Verify node is up
nodetool status

# EXPECTED OUTPUT:
# Datacenter: dc1
# ===============
# Status=Up/Down
# |/ State=Normal/Leaving/Joining/Moving
# --  Address   Load      Tokens  Owns  Host ID                               Rack
# UN  10.0.0.1  74 KiB    16      100%  550e8400-e29b-41d4-a716-446655440000  rack1

# UN = Up and Normal - this is what we want
# Wait 1-2 minutes before starting next node

# ============================================================
# ON NODE 2 (After Node 1 shows UN)
# ============================================================

sudo systemctl start cassandra

# Watch logs
sudo tail -f /var/log/cassandra/system.log

# LOOK FOR:
# "Handshaking version with /10.0.0.1"
# "Node /10.0.0.2 state jump to NORMAL"

# Verify both nodes are up
nodetool status

# EXPECTED:
# UN  10.0.0.1  74 KiB    16     ?     ...  rack1
# UN  10.0.0.2  75 KiB    16     ?     ...  rack1

# Wait 1-2 minutes before starting Node 3

# ============================================================
# ON NODE 3 (After Node 2 shows UN)
# ============================================================

sudo systemctl start cassandra
sudo tail -f /var/log/cassandra/system.log

# Verify all three nodes
nodetool status

# EXPECTED FINAL STATE:
# Datacenter: dc1
# ===============
# --  Address   Load      Tokens  Owns (effective)  Host ID     Rack
# UN  10.0.0.1  95 KiB    16      68.5%            ...         rack1
# UN  10.0.0.2  87 KiB    16      65.2%            ...         rack1
# UN  10.0.0.3  91 KiB    16      66.3%            ...         rack1
```

### Step 5: Verify Cluster Health

Run these checks from any node:

```bash
# 1. All nodes up?
nodetool status
# All should show UN

# 2. Schema agreement?
nodetool describecluster

# LOOK FOR:
# Schema versions:
#     abc-123-xyz: [10.0.0.1, 10.0.0.2, 10.0.0.3]
#
# All nodes should show SAME schema version
# If different versions, wait a few minutes and check again

# 3. Gossip healthy?
nodetool gossipinfo | head -50

# Each node should show:
#   STATUS:NORMAL
#   LOAD: (some number)
#   SCHEMA: (same for all)

# 4. Can we connect?
cqlsh 10.0.0.1
cqlsh 10.0.0.2
cqlsh 10.0.0.3
# All should connect

# 5. Test write/read
cqlsh << 'EOF'
CREATE KEYSPACE test_cluster WITH replication = {
  'class': 'NetworkTopologyStrategy',
  'dc1': 3
};

USE test_cluster;

CREATE TABLE health_check (
  id uuid PRIMARY KEY,
  created timestamp,
  node text
);

INSERT INTO health_check (id, created, node)
VALUES (uuid(), toTimestamp(now()), 'test');

SELECT * FROM health_check;

DROP KEYSPACE test_cluster;
EOF
```

---

## Multi-Datacenter Cluster

For geographic distribution, disaster recovery, or workload isolation.

### Why Multi-DC?

| Use Case | Benefit |
|----------|---------|
| **Disaster Recovery** | If DC1 dies, DC2 continues serving |
| **Low Latency** | Users connect to nearest DC |
| **Workload Isolation** | Analytics in DC2, OLTP in DC1 |
| **Compliance** | Data stays in specific regions |

### Architecture

```
                      US-EAST (dc1)                    EU-WEST (dc2)
                 ┌───────────────────┐             ┌───────────────────┐
                 │                   │             │                   │
                 │  ┌─────┐ ┌─────┐  │             │  ┌─────┐ ┌─────┐  │
       User ────►│  │ N1  │ │ N2  │  │◄──────────►│  │ N4  │ │ N5  │  │◄──── User
       (US)      │  │seed │ │     │  │   Async    │  │seed │ │     │  │      (EU)
                 │  └─────┘ └─────┘  │   Repl     │  └─────┘ └─────┘  │
                 │       ┌─────┐     │             │       ┌─────┐     │
                 │       │ N3  │     │             │       │ N6  │     │
                 │       └─────┘     │             │       └─────┘     │
                 │                   │             │                   │
                 └───────────────────┘             └───────────────────┘

Replication: LOCAL_QUORUM reads/writes stay in local DC
Cross-DC replication is asynchronous
```

### Network Requirements

For multi-DC, the following is needed:

```
WITHIN each DC:
- Low latency (< 1ms)
- High bandwidth (10Gbps+)
- Ports: 7000, 9042, 7199

BETWEEN DCs:
- Higher latency acceptable (50-200ms)
- Moderate bandwidth (depends on write rate)
- Ports: 7000 (gossip/streaming)
- Consider dedicated WAN links or VPN
```

### Configuration for Multi-DC

**DC1 Node (10.1.0.1):**

```yaml
# cassandra.yaml
cluster_name: 'GlobalCluster'
num_tokens: 16

listen_address: 10.1.0.1
rpc_address: 10.1.0.1

# CRITICAL: Seeds from BOTH datacenters
seed_provider:
  - class_name: org.apache.cassandra.locator.SimpleSeedProvider
    parameters:
      - seeds: "10.1.0.1,10.2.0.1"  # One from dc1, one from dc2

endpoint_snitch: GossipingPropertyFileSnitch
```

```properties
# cassandra-rackdc.properties
dc=dc1
rack=rack1
# Enable local DC preference for requests
prefer_local=true
```

**DC2 Node (10.2.0.1):**

```yaml
# cassandra.yaml - same as DC1 except:
listen_address: 10.2.0.1
rpc_address: 10.2.0.1

# Seeds MUST include nodes from both DCs
seed_provider:
  - class_name: org.apache.cassandra.locator.SimpleSeedProvider
    parameters:
      - seeds: "10.1.0.1,10.2.0.1"
```

```properties
# cassandra-rackdc.properties
dc=dc2
rack=rack1
prefer_local=true
```

### Multi-DC Keyspace

```sql
-- Create keyspace with replication in both DCs
CREATE KEYSPACE production WITH replication = {
  'class': 'NetworkTopologyStrategy',
  'dc1': 3,  -- 3 replicas in dc1
  'dc2': 3   -- 3 replicas in dc2
};

-- For read-heavy workloads in one DC:
CREATE KEYSPACE analytics WITH replication = {
  'class': 'NetworkTopologyStrategy',
  'dc1': 1,  -- Minimal copies in dc1
  'dc2': 3   -- Full copies in dc2 (where analytics runs)
};
```

### Consistency Levels for Multi-DC

| Consistency Level | Meaning | Use When |
|-------------------|---------|----------|
| `LOCAL_ONE` | 1 replica in local DC | Low latency, okay with eventual |
| `LOCAL_QUORUM` | Majority in local DC | **Most common for multi-DC** |
| `EACH_QUORUM` | Majority in EACH DC | Strong consistency, higher latency |
| `QUORUM` | Majority overall | Avoid - might cross DCs |

```sql
-- Typical multi-DC usage:
CONSISTENCY LOCAL_QUORUM;

-- Writes go to local DC, async replicate to remote
INSERT INTO users (id, name) VALUES (uuid(), 'test');

-- Reads from local DC only
SELECT * FROM users WHERE id = ?;
```

---

## Expanding an Existing Cluster

### Adding a Node to Existing Cluster

```bash
# On new node:

# 1. Install Cassandra (same version as cluster!)
# 2. Configure cassandra.yaml:
#    - Same cluster_name
#    - Same seeds (include existing nodes)
#    - Different listen_address (this node's IP)
#    - Same snitch

# 3. Start Cassandra
sudo systemctl start cassandra

# 4. Watch it bootstrap (download data from existing nodes)
nodetool netstats  # Shows streaming progress

# 5. Once status shows UN, run repair
nodetool repair -full

# The new node will:
# - Contact seeds
# - Learn about cluster
# - Pick token ranges
# - Stream data from existing nodes
# - Join the ring
# This can take hours for large clusters
```

### Scaling from 3 to 6 Nodes

```bash
# Add nodes ONE AT A TIME
# Wait for each to reach UN status before adding next

# After all nodes added:
nodetool status

# Run cleanup on OLD nodes to remove data
# they're no longer responsible for:
nodetool cleanup

# This should be run on all existing nodes
# after any node is added to the cluster
```

---

## Troubleshooting Cluster Setup

### Problem: Node Won't Start

```bash
# Check logs first - ALWAYS
sudo tail -100 /var/log/cassandra/system.log

# Common causes:

# 1. Cluster name mismatch
grep cluster_name /etc/cassandra/cassandra.yaml
# Compare with running cluster:
cqlsh -e "SELECT cluster_name FROM system.local"

# 2. Listen address wrong
grep listen_address /etc/cassandra/cassandra.yaml
ip addr show  # Verify IP exists on this machine

# 3. Data directories have old data
ls /var/lib/cassandra/data/system/
# If from different cluster, must clear:
sudo rm -rf /var/lib/cassandra/data/*
sudo rm -rf /var/lib/cassandra/commitlog/*

# 4. Java issues
java -version  # Must be 11 or 17
echo $JAVA_HOME
```

### Problem: Node Joins But Shows Wrong DC/Rack

```bash
# Once a node joins with DC/rack, it CANNOT be changed without:
# 1. Decommissioning the node
# 2. Clearing data
# 3. Rejoining with correct settings

nodetool decommission  # Wait for completion
sudo systemctl stop cassandra
sudo rm -rf /var/lib/cassandra/data/*
# Fix cassandra-rackdc.properties
sudo systemctl start cassandra
```

### Problem: Nodes Not Seeing Each Other

```bash
# Check gossip from each node
nodetool gossipinfo | grep -A 5 "10.0.0"

# Test network connectivity
nc -zv 10.0.0.2 7000  # Gossip port
nc -zv 10.0.0.2 9042  # CQL port

# Check firewall
sudo iptables -L -n | grep 7000
sudo ufw status

# Check seed configuration
grep seeds /etc/cassandra/cassandra.yaml
# Seeds must be identical on all nodes
```

### Problem: Schema Disagreement

```bash
nodetool describecluster

# Shows:
# Schema versions:
#     abc123: [10.0.0.1, 10.0.0.2]
#     xyz789: [10.0.0.3]       # BAD - different schema

# Usually resolves within minutes
# If persists:
nodetool resetlocalschema  # Run on disagreeing node
# Or restart the disagreeing node
```

### Problem: Bootstrap Stuck

```bash
# Check progress
nodetool netstats

# Shows:
# Mode: JOINING
# Receiving: 45% (streaming data)

# If stuck at same percentage for > 30 mins:
# Check logs for errors
grep -i error /var/log/cassandra/system.log | tail -20

# May need to restart and retry
sudo systemctl restart cassandra
```

---

## Docker Compose Development Cluster

For local development with a multi-node cluster:

```yaml
# docker-compose.yml
version: '3.8'

services:
  cass1:
    image: cassandra:5.0
    container_name: cass1
    ports:
      - "9042:9042"
    environment:
      - CASSANDRA_CLUSTER_NAME=DevCluster
      - CASSANDRA_DC=dc1
      - CASSANDRA_RACK=rack1
      - CASSANDRA_ENDPOINT_SNITCH=GossipingPropertyFileSnitch
      - CASSANDRA_SEEDS=cass1
      - MAX_HEAP_SIZE=1G
      - HEAP_NEWSIZE=256M
    volumes:
      - cass1-data:/var/lib/cassandra
    networks:
      - cass-net
    healthcheck:
      test: ["CMD", "cqlsh", "-e", "DESCRIBE CLUSTER"]
      interval: 30s
      timeout: 10s
      retries: 10
      start_period: 60s

  cass2:
    image: cassandra:5.0
    container_name: cass2
    depends_on:
      cass1:
        condition: service_healthy
    environment:
      - CASSANDRA_CLUSTER_NAME=DevCluster
      - CASSANDRA_DC=dc1
      - CASSANDRA_RACK=rack1
      - CASSANDRA_ENDPOINT_SNITCH=GossipingPropertyFileSnitch
      - CASSANDRA_SEEDS=cass1
      - MAX_HEAP_SIZE=1G
      - HEAP_NEWSIZE=256M
    volumes:
      - cass2-data:/var/lib/cassandra
    networks:
      - cass-net
    healthcheck:
      test: ["CMD", "cqlsh", "-e", "DESCRIBE CLUSTER"]
      interval: 30s
      timeout: 10s
      retries: 10
      start_period: 60s

  cass3:
    image: cassandra:5.0
    container_name: cass3
    depends_on:
      cass2:
        condition: service_healthy
    environment:
      - CASSANDRA_CLUSTER_NAME=DevCluster
      - CASSANDRA_DC=dc1
      - CASSANDRA_RACK=rack1
      - CASSANDRA_ENDPOINT_SNITCH=GossipingPropertyFileSnitch
      - CASSANDRA_SEEDS=cass1
      - MAX_HEAP_SIZE=1G
      - HEAP_NEWSIZE=256M
    volumes:
      - cass3-data:/var/lib/cassandra
    networks:
      - cass-net

volumes:
  cass1-data:
  cass2-data:
  cass3-data:

networks:
  cass-net:
    driver: bridge
```

```bash
# Start cluster (health checks ensure proper ordering)
docker-compose up -d

# Watch progress
docker-compose logs -f

# Check status
docker exec cass1 nodetool status

# Connect
docker exec -it cass1 cqlsh

# Cleanup
docker-compose down -v  # -v removes volumes (data)
```

---

## Next Steps

The cluster is running. Next steps:

1. **[Production Checklist](production-checklist.md)** - Security hardening and optimization
2. **[CQL Quickstart](quickstart-cql.md)** - Start writing queries
3. **[Data Modeling](../data-modeling/index.md)** - Design the schema properly
4. **[Set Up Monitoring](../operations/monitoring/index.md)** - Monitor with AxonOps
5. **[Operations Guide](../operations/index.md)** - Day-to-day management
