# cassandra.yaml Complete Reference

The `cassandra.yaml` file is the primary configuration for Apache Cassandra. This reference covers not just what each setting does, but *why* it might need changing, what can go wrong, and production-tested recommendations.

Getting configuration wrong can cause data loss, performance problems, or cluster instability. Read the explanations, not just the defaults.

---

## File Location and Basics

```
Default locations:
- Package install (apt/yum): /etc/cassandra/cassandra.yaml
- Tarball install: $CASSANDRA_HOME/conf/cassandra.yaml
- Docker: /etc/cassandra/cassandra.yaml
- Kubernetes: Usually mounted as ConfigMap

Configuration changes require node restart (except noted).
Test changes in non-production first.
```

---

## Critical Settings (Must Configure Before Production)

These settings either cannot be changed after cluster initialization or will cause major problems if left at defaults in production.

### cluster_name

```yaml
cluster_name: 'MyProductionCluster'
```

| Aspect | Details |
|--------|---------|
| Default | `'Test Cluster'` |
| Can change | **NO** - cannot change after writing data |
| Purpose | Identifies cluster; nodes refuse to join mismatched clusters |
| Recommendation | Set meaningful name before first node starts |

**What happens if wrong**:
- Drivers verify cluster_name on connect—mismatch = connection refused
- Cannot rename later without wiping all data
- Cluster with default name screams "test environment"

### listen_address / listen_interface

```yaml
# Option 1: Specific IP
listen_address: 10.0.0.1

# Option 2: Network interface (Cassandra resolves to IP)
listen_interface: eth0

# NEVER use both - pick one
```

| Aspect | Details |
|--------|---------|
| Default | `localhost` |
| Can change | Yes, but requires careful coordination |
| Purpose | IP address for inter-node communication |
| Must set | **YES** - localhost does not work for multi-node |

**What happens if wrong**:
- `localhost`: Other nodes cannot connect to this node
- `0.0.0.0`: **INVALID** - Cassandra needs specific IP for gossip
- Wrong IP: Node unreachable, appears down to cluster

**Container/Cloud note**:
```yaml
# In Docker/Kubernetes with dynamic IPs:
# Use listen_interface instead of listen_address
listen_interface: eth0
listen_interface_prefer_ipv6: false
```

### rpc_address / rpc_interface

```yaml
# Option 1: Specific IP (clients connect to this)
rpc_address: 10.0.0.1

# Option 2: Listen on all interfaces (common in production)
rpc_address: 0.0.0.0

# Option 3: Network interface
rpc_interface: eth0
```

| Aspect | Details |
|--------|---------|
| Default | `localhost` |
| Can change | Yes, with restart |
| Purpose | IP address for client (CQL) connections |
| Common production | `0.0.0.0` to accept connections on any interface |

**What happens if wrong**:
- `localhost`: Only local clients can connect
- Wrong IP: Clients cannot reach Cassandra

### broadcast_address / broadcast_rpc_address

```yaml
# What other nodes see as this node's address
broadcast_address: 54.123.45.67

# What clients see as this node's address
broadcast_rpc_address: 54.123.45.67
```

| Aspect | Details |
|--------|---------|
| Default | Same as listen_address/rpc_address |
| When needed | NAT, cloud environments, containers |
| Purpose | Address advertised to others (vs. address bound locally) |

**Cloud/NAT scenario**:
```yaml
# Node's private IP (inside VPC)
listen_address: 10.0.0.1

# Node's public IP (what other nodes/clients reach)
broadcast_address: 54.123.45.67
broadcast_rpc_address: 54.123.45.67

# This tells the cluster:
# "I'm listening on 10.0.0.1, but tell everyone to reach me at 54.123.45.67"
```

### seed_provider

```yaml
seed_provider:
  - class_name: org.apache.cassandra.locator.SimpleSeedProvider
    parameters:
      - seeds: "10.0.0.1,10.0.0.2,10.0.0.3"
```

| Aspect | Details |
|--------|---------|
| Purpose | Contact points for new nodes joining cluster |
| Recommendation | 2-3 seeds per datacenter |
| Can change | Yes, with restart |

**Seed misconceptions**:

```
WRONG: "Seeds are special leaders"
RIGHT: Seeds are just initial contact points for gossip

WRONG: "Make all nodes seeds for redundancy"
RIGHT: This breaks gossip protocol, causes performance issues

WRONG: "Seeds handle more traffic"
RIGHT: Seeds are only used during startup/rejoining

CORRECT SETUP:
- Pick 2-3 stable nodes per DC as seeds
- Seeds should be geographically distributed within DC
- All nodes must have SAME seed list
- Seeds do not need to be first nodes started (but makes it easier)
```

### endpoint_snitch

```yaml
endpoint_snitch: GossipingPropertyFileSnitch
```

| Aspect | Details |
|--------|---------|
| Default | `SimpleSnitch` |
| Production | `GossipingPropertyFileSnitch` or cloud-specific |
| Can change | **Carefully** - requires rolling update |
| Purpose | Determines datacenter and rack for each node |

**Snitch options**:

| Snitch | Use Case | Requires Additional Config |
|--------|----------|---------------------------|
| `SimpleSnitch` | Dev only, single DC | None |
| `GossipingPropertyFileSnitch` | Production (recommended) | `cassandra-rackdc.properties` |
| `Ec2Snitch` | AWS single region | None (auto-detect) |
| `Ec2MultiRegionSnitch` | AWS multi-region | `broadcast_address` required |
| `GoogleCloudSnitch` | GCP | None (auto-detect) |
| `AzureSnitch` | Azure | None (auto-detect) |

**GossipingPropertyFileSnitch setup**:
```properties
# cassandra-rackdc.properties (same directory as cassandra.yaml)
dc=us-east
rack=rack1
prefer_local=true
```

**What happens if wrong**:
- Wrong snitch: Replicas placed incorrectly, potential data loss on failure
- Inconsistent DC names: Cassandra sees multiple "DCs," breaks replication
- Changing snitch on running cluster: Data streaming chaos

---

## Network Configuration

### Ports

```yaml
# Inter-node communication (must be open between all nodes)
storage_port: 7000              # Unencrypted
ssl_storage_port: 7001          # Encrypted (when internode_encryption enabled)

# Client connections
native_transport_port: 9042     # CQL
native_transport_port_ssl: 9142 # CQL over SSL (optional, for separate SSL port)
```

**Firewall rules needed**:
```
Between all Cassandra nodes:
- TCP 7000 (or 7001 for SSL)
- TCP 7199 (JMX - for nodetool)

Between clients and Cassandra:
- TCP 9042 (or 9142 for SSL)
```

### Native Transport Settings

```yaml
# Enable CQL protocol
native_transport_enabled: true

# Maximum frame size (large batches may need increase)
native_transport_max_frame_size_in_mb: 256

# Maximum concurrent connections (per node)
native_transport_max_concurrent_connections: -1  # -1 = unlimited

# Maximum concurrent requests per connection
native_transport_max_concurrent_connections_per_ip: -1
```

### Inter-node Compression

```yaml
internode_compression: dc

# Options:
# - none: No compression (fastest, most bandwidth)
# - dc: Compress only cross-datacenter traffic (recommended for multi-DC)
# - all: Compress all inter-node traffic
```

**When to use what**:
- `none`: Single DC with fast network, CPU-constrained
- `dc`: Multi-DC with expensive/limited cross-DC bandwidth
- `all`: Bandwidth-constrained everywhere

---

## Directory Configuration

### Data Directories

```yaml
data_file_directories:
  - /var/lib/cassandra/data

# Multiple directories for JBOD (Just a Bunch of Disks):
# data_file_directories:
#   - /mnt/disk1/cassandra/data
#   - /mnt/disk2/cassandra/data
#   - /mnt/disk3/cassandra/data
```

**JBOD considerations**:
```
Cassandra places entire SSTables on one disk
Distribution is somewhat even, but not perfect
If one disk fills up, writes to tables on that disk fail
Disk failure loses data on that disk only (replicas on other nodes provide protection)

RAID alternatives:
- RAID0: Better throughput, but failure loses all data on node
- RAID10: Redundancy, but expensive
- JBOD with Cassandra replication: Common, cost-effective
```

### Commit Log Directory

```yaml
commitlog_directory: /var/lib/cassandra/commitlog
```

**Critical**: Put commit log on separate physical disk from data if possible.

```
Why separate disk?
- Commit log writes are sequential
- Data writes are also sequential (during flush)
- On same disk, they compete for I/O
- Separate disk: Both get sequential I/O = better throughput

Ideal setup:
- Commit log: Fast SSD/NVMe
- Data: Can be SSD or NVMe (or spinning disk for capacity)
```

### Other Directories

```yaml
# Hints for unavailable nodes
hints_directory: /var/lib/cassandra/hints

# Saved caches (key cache, row cache)
saved_caches_directory: /var/lib/cassandra/saved_caches

# CDC (Change Data Capture) logs
cdc_raw_directory: /var/lib/cassandra/cdc_raw
```

---

## Memory and Performance

### Token Allocation

```yaml
# Number of vnodes per node
num_tokens: 16

# Automatic token allocation (Cassandra 4.0+)
allocate_tokens_for_local_replication_factor: 3
```

| num_tokens | Pros | Cons | Recommendation |
|------------|------|------|----------------|
| 1 | Simple, predictable | Uneven distribution, slow streaming | Legacy only |
| 16 | Good balance | Slight gossip overhead | **Recommended (4.0+)** |
| 256 | Very even distribution | Memory overhead, slow startup | Legacy default |

**Cassandra 4.0+ optimization**:
```yaml
num_tokens: 16
allocate_tokens_for_local_replication_factor: 3  # Set to your RF

# This uses a smarter algorithm to distribute tokens evenly
# based on expected replication factor
```

### Concurrent Operations

```yaml
# Thread pools for different operations
concurrent_reads: 32
concurrent_writes: 32
concurrent_counter_writes: 32
concurrent_materialized_view_writes: 32
```

**Sizing guidelines**:
```
concurrent_reads: 16 × number_of_drives
  - Reads may block on disk I/O
  - More threads keep CPU busy while waiting for disk

concurrent_writes: 8 × number_of_CPU_cores
  - Writes are CPU-bound (serialization, hashing)
  - Less I/O blocking than reads

Examples:
- 4 cores, 1 SSD: reads=16, writes=32
- 8 cores, 4 SSDs: reads=64, writes=64
- 16 cores, 8 NVMe: reads=128, writes=128
```

### Memtable Configuration

```yaml
# Memory for memtables (on-heap)
memtable_heap_space_in_mb: 2048

# Memory for memtables (off-heap, reduces GC pressure)
memtable_offheap_space_in_mb: 2048

# How memtable memory is allocated
memtable_allocation_type: heap_buffers
# Options: heap_buffers, offheap_buffers, offheap_objects

# Number of concurrent memtable flushes
memtable_flush_writers: 2

# When to start flushing (fraction of total memtable space)
memtable_cleanup_threshold: 0.11
```

**Memory math**:
```
Total memtable space = memtable_heap_space + memtable_offheap_space

When total memtables reach (memtable_cleanup_threshold × heap_size):
  Cassandra flushes the largest memtable

Example with 8GB heap:
  memtable_cleanup_threshold: 0.11
  Flush trigger: 8GB × 0.11 = 880MB in memtables

For large heaps (>16GB), consider:
  memtable_allocation_type: offheap_buffers
  This moves memtable data off JVM heap → less GC pressure
```

---

## Commit Log Configuration

### Sync Mode

```yaml
# How commit log is synced to disk
commitlog_sync: periodic
commitlog_sync_period_in_ms: 10000

# Alternative: batch mode
# commitlog_sync: batch
# commitlog_sync_batch_window_in_ms: 2
```

**Trade-off explained**:

| Mode | Latency | Throughput | Data Loss Risk |
|------|---------|------------|----------------|
| `periodic` (10s) | Lowest | Highest | Up to 10 seconds |
| `periodic` (1s) | Low | High | Up to 1 second |
| `batch` (2ms) | Higher | Lower | Up to 2ms |
| `batch` (50ms) | Medium | Medium | Up to 50ms |

```
Why periodic is usually fine:
- Data is on multiple replicas (RF=3)
- For data loss: ALL replicas must fail within sync period
- Very unlikely scenario

When to use batch:
- Regulatory requirements for durability
- Single replica or RF=1
- Financial/banking applications
```

### Commit Log Sizing

```yaml
# Size of each segment file
commitlog_segment_size_in_mb: 32

# Total space for all commit logs
commitlog_total_space_in_mb: 8192
```

**What happens when commit log fills up**:
```
If commitlog_total_space reached:
1. Writes BLOCK (cannot accept new writes)
2. Cassandra forces memtable flush
3. Flushed memtables allow commit log segments to be recycled
4. Writes resume

Symptoms:
- Sudden write latency spike
- "Commit log segment limit reached" in logs

Prevention:
- Size appropriately for write rate
- Monitor commit log segment count
- Ensure memtables flush regularly
```

---

## Compaction Configuration

### Throughput Throttling

```yaml
# Maximum compaction throughput (MB/s)
compaction_throughput_mb_per_sec: 64

# Set to 0 for unlimited (careful!)
```

**Tuning compaction throughput**:
```
Low value (32-64):
- Protects read/write latency
- Compaction may fall behind on write-heavy workloads

High value (128-256):
- Compaction keeps up with writes
- May impact read/write latency during compaction

Unlimited (0):
- Compaction runs as fast as possible
- Risk of overwhelming disk I/O
- Only use if compaction consistently behind
```

```bash
# Change at runtime (does not persist)
nodetool setcompactionthroughput 128
```

### Concurrent Compactors

```yaml
concurrent_compactors: 2

# Default: min(8, number of disks, number of cores)
```

**Guidelines**:
```
Single SSD: 1-2 compactors
Multiple SSDs (JBOD): Number of disks, up to 4
NVMe: 2-4 depending on cores

Too many compactors:
- I/O contention between compactions
- Impact on read/write latency

Too few compactors:
- Compaction backlog
- SSTable count grows
- Read latency increases
```

### Large Partition Handling

```yaml
# Warn in log when partition exceeds this size during compaction
compaction_large_partition_warning_threshold_mb: 100
```

**Large partitions cause**:
- Compaction memory pressure
- Read timeouts (entire partition loaded for range queries)
- Heap pressure during repair

---

## Timeout Configuration

### Read/Write Timeouts

```yaml
# Coordinator waits this long for reads
read_request_timeout_in_ms: 5000

# Coordinator waits this long for writes
write_request_timeout_in_ms: 2000

# Range scans (often slower)
range_request_timeout_in_ms: 10000

# Counter operations (require read-before-write)
counter_write_request_timeout_in_ms: 5000

# Lightweight transactions (Paxos)
cas_contention_timeout_in_ms: 1000

# Default for unspecified operations
request_timeout_in_ms: 10000
```

**Timeout strategy**:
```
Writes should timeout before reads (prevent zombie writes):
  write_request_timeout < read_request_timeout

Counter writes need more time (read + write):
  counter_write_timeout ≥ read_timeout + write_timeout

Range scans need most time:
  range_request_timeout > read_request_timeout

LWT has inherent latency:
  cas_contention_timeout should accommodate 4 round trips
```

**When to increase timeouts**:
```
Cross-datacenter operations: Higher latency
  - Increase for QUORUM (cross-DC) operations
  - Keep lower for LOCAL_* operations

Large partitions: Slower reads
  - Temporary fix: increase timeout
  - Real fix: redesign data model

Under load: Higher contention
  - Temporary: increase timeout
  - Real fix: scale cluster or optimize queries
```

---

## Caching Configuration

### Key Cache

```yaml
# Size in MB (caches partition key → SSTable offset)
key_cache_size_in_mb: 100

# How often to save to disk (seconds)
key_cache_save_period: 14400

# Number of keys to save
key_cache_keys_to_save: 100000
```

**Key cache explained**:
```
What it caches:
  Partition key → byte offset in SSTable index

Benefits:
  Avoids reading SSTable index from disk
  Very memory-efficient (~8 bytes per key)

Sizing:
  Default: min(5% heap, 100MB)
  Monitor hit rate via JMX
  Increase if hit rate low and memory available
```

### Row Cache (Use With Caution)

```yaml
# Size in MB (caches entire rows)
row_cache_size_in_mb: 0  # Disabled by default

# How often to save
row_cache_save_period: 0
```

**Row cache: Usually a bad idea**:
```
Sounds good: "Cache entire rows in memory!"

Reality:
- Uses significant heap (entire rows, not just keys)
- GC pressure from large objects
- Invalidation on any write
- Often less effective than OS page cache

When it might help:
- Very small table (< 1GB)
- Extremely read-heavy (99.9% reads)
- Rows rarely change
- Consistent hot set (same rows read repeatedly)

Better alternative: Let OS page cache handle it
```

---

## Security Configuration

### Authentication

```yaml
# No authentication (default, NOT for production)
authenticator: AllowAllAuthenticator

# Username/password authentication
authenticator: PasswordAuthenticator
```

**Enabling authentication**:
```yaml
# Step 1: Set authenticator
authenticator: PasswordAuthenticator

# Step 2: Restart node

# Step 3: Connect with default credentials
# cqlsh -u cassandra -p cassandra

# Step 4: Change default password immediately!
ALTER USER cassandra WITH PASSWORD 'new_secure_password';

# Step 5: Create application users
CREATE ROLE app_user WITH PASSWORD = 'app_password' AND LOGIN = true;
```

### Authorization

```yaml
# No authorization (default)
authorizer: AllowAllAuthorizer

# Role-based access control
authorizer: CassandraAuthorizer

# Required for CassandraAuthorizer
role_manager: CassandraRoleManager
```

**Enabling authorization**:
```sql
-- After enabling CassandraAuthorizer and restarting

-- Grant permissions
GRANT SELECT ON KEYSPACE my_app TO app_read_user;
GRANT MODIFY ON KEYSPACE my_app TO app_write_user;
GRANT ALL ON KEYSPACE my_app TO app_admin;

-- Role hierarchy
CREATE ROLE developers;
GRANT SELECT ON KEYSPACE my_app TO developers;
GRANT developers TO dev_user1;
GRANT developers TO dev_user2;
```

### Encryption: Client-to-Node

```yaml
client_encryption_options:
    enabled: true
    optional: false  # true = allow unencrypted connections too
    keystore: /etc/cassandra/ssl/.keystore
    keystore_password: ${KEYSTORE_PASSWORD}  # Environment variable
    truststore: /etc/cassandra/ssl/.truststore
    truststore_password: ${TRUSTSTORE_PASSWORD}
    protocol: TLS
    accepted_protocols:
      - TLSv1.2
      - TLSv1.3
    cipher_suites:
      - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
      - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
    require_client_auth: false  # true = mutual TLS
```

### Encryption: Node-to-Node

```yaml
server_encryption_options:
    internode_encryption: all
    # Options: none, dc (only cross-DC), rack (only cross-rack), all
    keystore: /etc/cassandra/ssl/.keystore
    keystore_password: ${KEYSTORE_PASSWORD}
    truststore: /etc/cassandra/ssl/.truststore
    truststore_password: ${TRUSTSTORE_PASSWORD}
    require_client_auth: true  # Recommended: nodes must authenticate
    require_endpoint_verification: true  # Verify hostname
```

---

## Hinted Handoff

```yaml
# Enable/disable hints
hinted_handoff_enabled: true

# Maximum time to store hints for unavailable node
max_hint_window_in_ms: 10800000  # 3 hours

# Throttle hint delivery (KB/s per destination)
hinted_handoff_throttle_in_kb: 1024

# Maximum hints stored per destination host
max_hints_file_size_in_mb: 128
```

**Hint configuration strategy**:
```
max_hint_window_in_ms:
  - Longer = more hints stored = more recovery possible
  - Shorter = less disk used = faster recovery
  - Default 3 hours handles most temporary outages
  - For planned maintenance exceeding 3 hours: run repair after

hinted_handoff_throttle_in_kb:
  - Protects recovering node from being overwhelmed
  - Increase if node recovery is slow
  - Decrease if recovering node CPU/disk constrained

When hints matter:
  - Node temporarily down (network, restart, etc.)
  - Hints replay when node returns
  - If down longer than max_hint_window: hints dropped, need repair
```

---

## Gossip and Failure Detection

```yaml
# How often to gossip (milliseconds)
# Do not change unless the gossip protocol is well understood
# gossip_settle_min_wait_ms: 5000

# Failure detection thresholds
phi_convict_threshold: 8
# Higher = more tolerant of latency spikes
# Lower = faster failure detection
# Default 8 is good for most deployments
```

**Phi convict threshold tuning**:
```
Cloud environments with variable latency:
  phi_convict_threshold: 12

Very stable, low-latency network:
  phi_convict_threshold: 6

Symptoms of too low:
  - Nodes flapping (marking down/up frequently)
  - "Marking X as DOWN" followed by "Marking X as UP" in logs

Symptoms of too high:
  - Slow failure detection
  - Long time before traffic routes around failed node
```

---

## Tombstone Protection

```yaml
# Warn when query scans this many tombstones
tombstone_warn_threshold: 1000

# Fail query when this many tombstones scanned
tombstone_failure_threshold: 100000
```

**Tombstone thresholds explained**:
```
What triggers these:
  - Wide partition with many deletes
  - Range query over deleted data
  - Poor data model (delete pattern does not match read pattern)

Warning (1000):
  - Logged in system.log
  - Query still completes
  - Investigate data model

Failure (100000):
  - Query aborted
  - Client gets TombstoneOverwhelmingException
  - Immediate attention needed

Fixes:
  1. Fix data model (avoid wide partitions with deletes)
  2. Run major compaction (temporary fix)
  3. Increase thresholds (hides problem, not recommended)
```

---

## Production Configurations

### Minimal Single-DC Production

```yaml
cluster_name: 'Production'
num_tokens: 16
allocate_tokens_for_local_replication_factor: 3

seed_provider:
  - class_name: org.apache.cassandra.locator.SimpleSeedProvider
    parameters:
      - seeds: "10.0.0.1,10.0.0.2"

listen_address: ${NODE_IP}
rpc_address: 0.0.0.0
broadcast_rpc_address: ${NODE_IP}

endpoint_snitch: GossipingPropertyFileSnitch

data_file_directories:
  - /var/lib/cassandra/data
commitlog_directory: /var/lib/cassandra/commitlog
hints_directory: /var/lib/cassandra/hints

authenticator: PasswordAuthenticator
authorizer: CassandraAuthorizer
role_manager: CassandraRoleManager

concurrent_reads: 32
concurrent_writes: 32

commitlog_sync: periodic
commitlog_sync_period_in_ms: 10000
```

### Multi-DC Production

```yaml
cluster_name: 'GlobalProduction'
num_tokens: 16
allocate_tokens_for_local_replication_factor: 3

seed_provider:
  - class_name: org.apache.cassandra.locator.SimpleSeedProvider
    parameters:
      # 2 seeds from each DC
      - seeds: "10.0.0.1,10.0.0.2,10.1.0.1,10.1.0.2"

listen_address: ${PRIVATE_IP}
broadcast_address: ${PUBLIC_IP}
rpc_address: 0.0.0.0
broadcast_rpc_address: ${PUBLIC_IP}

endpoint_snitch: GossipingPropertyFileSnitch

internode_compression: dc

server_encryption_options:
    internode_encryption: all
    keystore: /etc/cassandra/ssl/.keystore
    keystore_password: ${KEYSTORE_PASSWORD}
    truststore: /etc/cassandra/ssl/.truststore
    truststore_password: ${TRUSTSTORE_PASSWORD}
    require_client_auth: true

client_encryption_options:
    enabled: true
    keystore: /etc/cassandra/ssl/.keystore
    keystore_password: ${KEYSTORE_PASSWORD}

authenticator: PasswordAuthenticator
authorizer: CassandraAuthorizer
```

### High-Throughput Write-Heavy

```yaml
# Larger memtables = fewer flushes
memtable_heap_space_in_mb: 4096
memtable_offheap_space_in_mb: 4096
memtable_flush_writers: 4

# More concurrent writes
concurrent_writes: 64

# Higher compaction throughput
compaction_throughput_mb_per_sec: 128
concurrent_compactors: 4

# Larger commit log
commitlog_total_space_in_mb: 16384
```

---

## Common Misconfigurations

| Mistake | Symptom | Fix |
|---------|---------|-----|
| `listen_address: localhost` | Nodes cannot gossip | Use actual IP |
| `seed_provider: all nodes` | Gossip protocol breaks | 2-3 seeds per DC |
| `row_cache_size_in_mb: 1000` | GC pauses, heap pressure | Set to 0 |
| `concurrent_compactors: 16` | I/O contention, slow reads | Match disk count |
| Different `cluster_name` | Node will not join | Must match all nodes |
| Wrong snitch | Replica placement wrong | Match topology |

---

## Next Steps

- **[JVM Options](../jvm-options/index.md)** - Heap and GC configuration
- **[Snitch Configuration](../snitch-config/index.md)** - Detailed topology setup
- **[Security](../../security/index.md)** - Authentication and encryption
- **[Performance Tuning](../../performance/index.md)** - Optimization strategies
- **[Operations](../../operations/index.md)** - Day-to-day management
