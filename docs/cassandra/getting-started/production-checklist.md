# Production Readiness Checklist

This checklist covers everything needed to prepare a Cassandra cluster for production workloads. Use it as a guide before going live and as an ongoing reference.

## Quick Checklist

### Critical (Must Have)

- [ ] Minimum 3 nodes per datacenter
- [ ] Replication factor ≥ 3
- [ ] Authentication enabled
- [ ] NetworkTopologyStrategy for all keyspaces
- [ ] SSDs for data storage
- [ ] Monitoring configured
- [ ] Backup strategy implemented
- [ ] Repair schedule configured

### Important (Should Have)

- [ ] TLS encryption enabled
- [ ] Role-based access control
- [ ] JVM tuned for workload
- [ ] OS-level tuning applied
- [ ] Alerting configured
- [ ] Runbooks documented
- [ ] Disaster recovery tested

---

## Hardware Requirements

### Minimum Production Specifications

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| **CPU** | 8 cores | 16+ cores | More cores = more concurrent operations |
| **RAM** | 16 GB | 32-64 GB | Half for JVM heap, half for OS cache |
| **Storage** | 500 GB SSD | 1-4 TB NVMe | SSDs mandatory for production |
| **Network** | 1 Gbps | 10 Gbps | Low latency critical |

### Storage Guidelines

```bash
# Verify SSD performance
fio --name=randwrite --ioengine=libaio --iodepth=32 --rw=randwrite \
    --bs=4k --direct=1 --size=1G --numjobs=4 --runtime=60 \
    --group_reporting --filename=/var/lib/cassandra/test
```

**Expected minimums**:
- Random write IOPS: > 10,000
- Sequential write: > 200 MB/s
- Latency (p99): < 1ms

### Disk Layout Recommendation

```
/                       # OS (50-100 GB)
/var/lib/cassandra/     # Cassandra data
├── data/              # SSTables (largest)
├── commitlog/         # Commit log (fast SSD, separate if possible)
├── saved_caches/      # Caches (small)
└── hints/             # Hints (small)
```

---

## Configuration Checklist

### cassandra.yaml Critical Settings

```yaml
# Cluster settings
cluster_name: 'ProductionCluster'  # Cannot change after data written
num_tokens: 16                      # 16 for new clusters

# Network
listen_address: <private-ip>        # Internal communication
rpc_address: <private-ip>           # Client connections
broadcast_rpc_address: <public-ip>  # Only if behind NAT

# Snitch (always use GossipingPropertyFileSnitch for production)
endpoint_snitch: GossipingPropertyFileSnitch

# Authentication (MUST enable for production)
authenticator: PasswordAuthenticator
authorizer: CassandraAuthorizer
role_manager: CassandraRoleManager

# Performance
concurrent_reads: 32                # 16 × number of drives
concurrent_writes: 32               # 8 × number of cores
concurrent_counter_writes: 32

# Compaction
compaction_throughput_mb_per_sec: 64   # Increase for faster compaction
concurrent_compactors: 2               # Default: min(cores, disk count)

# Commit log
commitlog_sync: periodic
commitlog_sync_period_in_ms: 10000

# Timeouts
read_request_timeout_in_ms: 5000
write_request_timeout_in_ms: 2000
counter_write_request_timeout_in_ms: 5000
request_timeout_in_ms: 10000

# Hinted handoff
hinted_handoff_enabled: true
max_hint_window_in_ms: 10800000  # 3 hours

# Memory
memtable_heap_space_in_mb: 2048
memtable_offheap_space_in_mb: 2048
```

### JVM Settings

Edit `jvm11-server.options` (or `jvm-server.options`):

```bash
# Heap size: 50% of RAM, max 31GB (to use compressed pointers)
-Xms16G
-Xmx16G

# G1GC settings (recommended for Cassandra 4+)
-XX:+UseG1GC
-XX:MaxGCPauseMillis=500
-XX:G1RSetUpdatingPauseTimePercent=5
-XX:InitiatingHeapOccupancyPercent=70

# GC logging
-Xlog:gc*:file=/var/log/cassandra/gc.log:time,uptime:filecount=10,filesize=10M
```

### cassandra-rackdc.properties

```properties
dc=dc1
rack=rack1
# prefer_local=true  # Enable for multi-DC
```

---

## Security Configuration

### 1. Enable Authentication

```yaml
# cassandra.yaml
authenticator: PasswordAuthenticator
authorizer: CassandraAuthorizer
role_manager: CassandraRoleManager
```

After enabling, change default credentials:

```sql
-- Connect with default credentials (cassandra/cassandra)
cqlsh -u cassandra -p cassandra

-- Create admin user
CREATE ROLE admin WITH PASSWORD = 'strong_password_here'
    AND SUPERUSER = true
    AND LOGIN = true;

-- Create application user
CREATE ROLE app_user WITH PASSWORD = 'app_password_here'
    AND LOGIN = true;

-- Grant permissions
GRANT ALL PERMISSIONS ON KEYSPACE myapp TO app_user;

-- Disable default cassandra user (after verifying admin works!)
ALTER ROLE cassandra WITH PASSWORD = 'new_random_password' AND LOGIN = false;
```

### 2. Enable TLS Encryption

Generate certificates:

```bash
# Generate keystore for each node
keytool -genkeypair -alias node1 \
    -keyalg RSA -keysize 2048 \
    -dname "CN=node1.cassandra.local" \
    -validity 365 \
    -keystore /etc/cassandra/conf/.keystore \
    -storepass cassandra \
    -keypass cassandra

# Export certificate
keytool -export -alias node1 \
    -keystore /etc/cassandra/conf/.keystore \
    -file node1.cer \
    -storepass cassandra

# Import to truststore (repeat for each node's cert)
keytool -import -alias node1 \
    -file node1.cer \
    -keystore /etc/cassandra/conf/.truststore \
    -storepass cassandra -noprompt
```

Configure TLS in `cassandra.yaml`:

```yaml
# Client-to-node encryption
client_encryption_options:
    enabled: true
    optional: false
    keystore: /etc/cassandra/conf/.keystore
    keystore_password: cassandra
    truststore: /etc/cassandra/conf/.truststore
    truststore_password: cassandra
    require_client_auth: false
    protocol: TLS
    cipher_suites: [TLS_RSA_WITH_AES_128_CBC_SHA, TLS_RSA_WITH_AES_256_CBC_SHA]

# Node-to-node encryption
server_encryption_options:
    internode_encryption: all
    keystore: /etc/cassandra/conf/.keystore
    keystore_password: cassandra
    truststore: /etc/cassandra/conf/.truststore
    truststore_password: cassandra
    require_client_auth: true
```

### 3. Network Security

Required firewall ports:

| Port | Purpose | Access |
|------|---------|--------|
| 7000 | Inter-node | Cluster only |
| 7001 | Inter-node (TLS) | Cluster only |
| 9042 | CQL clients | Application servers |
| 9142 | CQL clients (TLS) | Application servers |
| 7199 | JMX | Monitoring only |

```bash
# UFW example (Ubuntu)
sudo ufw allow from 10.0.0.0/8 to any port 7000
sudo ufw allow from 10.0.0.0/8 to any port 7001
sudo ufw allow from 10.0.0.0/8 to any port 9042
sudo ufw allow from 10.0.1.0/24 to any port 7199  # Monitoring subnet only
```

---

## OS-Level Tuning

### sysctl Settings

Create `/etc/sysctl.d/99-cassandra.conf`:

```bash
# Virtual memory
vm.max_map_count = 1048575
vm.swappiness = 1
vm.dirty_ratio = 80
vm.dirty_background_ratio = 5

# Network
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.core.rmem_default = 16777216
net.core.wmem_default = 16777216
net.core.optmem_max = 40960
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.core.netdev_max_backlog = 50000
net.ipv4.tcp_max_syn_backlog = 30000
net.ipv4.tcp_max_tw_buckets = 2000000
net.ipv4.tcp_slow_start_after_idle = 0
```

Apply:

```bash
sudo sysctl -p /etc/sysctl.d/99-cassandra.conf
```

### Limits Configuration

Create `/etc/security/limits.d/cassandra.conf`:

```bash
cassandra soft memlock unlimited
cassandra hard memlock unlimited
cassandra soft nofile 1048576
cassandra hard nofile 1048576
cassandra soft nproc 32768
cassandra hard nproc 32768
cassandra soft as unlimited
cassandra hard as unlimited
```

### Disable Swap

```bash
# Disable swap permanently
sudo swapoff -a
sudo sed -i '/swap/d' /etc/fstab
```

### Disable Transparent Huge Pages

Create `/etc/rc.local` or systemd service:

```bash
echo never > /sys/kernel/mm/transparent_hugepage/enabled
echo never > /sys/kernel/mm/transparent_hugepage/defrag
```

---

## Monitoring Setup

### Key Metrics to Monitor

| Metric | Warning | Critical | Notes |
|--------|---------|----------|-------|
| Heap usage | > 70% | > 85% | GC pressure |
| Write latency (p99) | > 10ms | > 100ms | Disk/compaction issues |
| Read latency (p99) | > 50ms | > 500ms | Disk/data model issues |
| Pending compactions | > 20 | > 50 | Compaction falling behind |
| Dropped messages | > 0 | > 100 | Timeout/overload |
| Disk usage | > 60% | > 80% | Plan for capacity |

### Enable JMX

```yaml
# cassandra-env.sh
JVM_OPTS="$JVM_OPTS -Djava.rmi.server.hostname=<node-ip>"
JVM_OPTS="$JVM_OPTS -Dcom.sun.management.jmxremote.port=7199"
JVM_OPTS="$JVM_OPTS -Dcom.sun.management.jmxremote.ssl=false"
JVM_OPTS="$JVM_OPTS -Dcom.sun.management.jmxremote.authenticate=true"
```

### Recommended Monitoring Tools

1. **[AxonOps](https://axonops.com)** - Purpose-built for Cassandra
2. **Prometheus + Grafana** - With JMX exporter
3. **DataStax MCAC** - Metrics Collector for Apache Cassandra

---

## Backup Strategy

### Snapshot Backups

```bash
# Take snapshot of all keyspaces
nodetool snapshot -t backup_$(date +%Y%m%d)

# Take snapshot of specific keyspace
nodetool snapshot -t daily_backup my_keyspace

# List snapshots
nodetool listsnapshots

# Clear old snapshots
nodetool clearsnapshot -t old_backup_name
```

### Backup Schedule

| Type | Frequency | Retention | Notes |
|------|-----------|-----------|-------|
| Snapshot | Daily | 7 days | Full backup |
| Incremental | Hourly | 24 hours | Between snapshots |
| Commitlog | Continuous | 24 hours | Point-in-time recovery |

### Offsite Backup

```bash
# Example: Sync snapshots to S3
aws s3 sync /var/lib/cassandra/data/my_keyspace/my_table-*/snapshots/daily_backup \
    s3://my-cassandra-backups/$(date +%Y%m%d)/
```

---

## Repair Schedule

### Configure Regular Repairs

Repairs should complete within `gc_grace_seconds` (default 10 days):

```bash
# Run repair on a keyspace (one node at a time)
nodetool repair -pr my_keyspace

# Full repair (all ranges, rarely needed)
nodetool repair -full my_keyspace
```

### Recommended Repair Schedule

| Cluster Size | Repair Frequency | Parallelism |
|--------------|------------------|-------------|
| 3 nodes | Weekly | Sequential |
| 6-12 nodes | Twice weekly | 2 parallel |
| 12+ nodes | Daily (incremental) | 3+ parallel |

### Automated Repair Tools

- **[AxonOps Repair](https://axonops.com)** - Automated scheduling
- **Cassandra Reaper** - Open-source repair scheduler

---

## Keyspace Configuration

### Always Use NetworkTopologyStrategy

```sql
-- WRONG: SimpleStrategy (do not use in production)
CREATE KEYSPACE bad_example WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 3
};

-- CORRECT: NetworkTopologyStrategy
CREATE KEYSPACE good_example WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3
};

-- Multi-datacenter
CREATE KEYSPACE multi_dc_example WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3,
    'dc2': 3
};
```

### Migrate Existing Keyspaces

```sql
ALTER KEYSPACE my_keyspace WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3
};

-- Then run repair to ensure data is replicated correctly
-- nodetool repair my_keyspace
```

---

## Pre-Launch Verification

### 1. Cluster Health

```bash
# All nodes UN (Up/Normal)
nodetool status

# Schema agreement
nodetool describecluster

# No pending compactions backlog
nodetool compactionstats
```

### 2. Performance Baseline

```bash
# Run stress test
cassandra-stress write n=1000000 -rate threads=50 -node 10.0.0.1

# Review latencies
cassandra-stress read n=1000000 -rate threads=50 -node 10.0.0.1
```

### 3. Failover Test

```bash
# Stop one node
sudo systemctl stop cassandra

# Verify cluster still operates (RF=3, CL=QUORUM)
cqlsh 10.0.0.2
SELECT * FROM system.local;

# Start node back
sudo systemctl start cassandra

# Verify it rejoins
nodetool status
```

### 4. Backup/Restore Test

```bash
# Take snapshot
nodetool snapshot -t test_backup my_keyspace

# Simulate data loss (on test cluster only!)
# cqlsh: TRUNCATE my_table;

# Restore from snapshot
# (copy snapshot files back to data directory)

# Verify data
cqlsh: SELECT COUNT(*) FROM my_table;
```

---

## Documentation Requirements

Ensure documentation exists for:

- [ ] Network topology diagram
- [ ] Node inventory (IPs, DCs, racks)
- [ ] Keyspace replication settings
- [ ] Backup procedures and schedules
- [ ] Restore procedures (tested!)
- [ ] Scaling procedures
- [ ] On-call runbooks
- [ ] Contact information for support

---

## Next Steps

After completing this checklist:

1. **[Operations Guide](../operations/index.md)** - Day-to-day procedures
2. **[Monitoring Setup](../monitoring/index.md)** - Detailed monitoring configuration
3. **[Troubleshooting](../troubleshooting/index.md)** - Common issues and solutions
4. **[Performance Tuning](../performance/index.md)** - Optimize for the workload
