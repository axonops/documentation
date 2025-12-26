---
title: "Installing Apache Cassandra"
description: "Cassandra installation guide. Install on Linux, macOS, and Windows."
meta:
  - name: keywords
    content: "Cassandra installation, install Cassandra, setup guide"
---

# Installing Apache Cassandra

This guide provides comprehensive installation instructions for Apache Cassandra, covering development setups through production deployments. It explains not just *how* to install, but *why* certain configurations matter and what problems occur when steps are skipped.

## Before Installing: Critical Decisions

Before running any installation commands, certain decisions must be made that are difficult to change later:

### 1. Cassandra Version Selection

| Version | Java Required | Status | When to Use |
|---------|---------------|--------|-------------|
| **5.0.x** | JDK 11 or 17 (Recommended) | Latest stable | New deployments, want latest features (SAI, Vector Search, Trie indexes) |
| **4.1.x** | JDK 11 | LTS | Production systems needing stability, most tested version |
| **4.0.x** | JDK 11 | Maintenance | Existing clusters, conservative environments |
| **3.11.x** | JDK 8 | Legacy | Only for existing clusters that cannot upgrade |

**Important version differences:**

- **5.0**: Storage Attached Indexes (SAI) are production-ready, vector search support, new Trie-based indexes, improved guardrails
- **4.1**: Virtual tables for configuration, pluggable memtable implementations, faster streaming
- **4.0**: Audit logging, full query logging, Java 11 support, improved compaction
- **3.11**: Still runs Java 8, no audit logging, missing modern features

!!! tip "Recommendation"
   Apache Cassandra 5.0 is GA and suitable for production when running a recent 5.0.x release. Use it for new clusters, and upgrade existing ones after normal staging validation.

---

### 2. Hardware Requirements by Use Case

#### Development/Testing

```
CPU:     2-4 cores
RAM:     8 GB minimum (4GB heap + OS)
Storage: 20 GB SSD
Network: 100 Mbps

REALITY CHECK: Cassandra can run on less, but:
- < 4GB RAM: Constant GC pressure, random crashes
- HDD instead of SSD: 10x slower compaction, unusable for realistic testing
- Single core: JVM threads starve each other
```

#### Small Production (< 100GB data per node)

```
CPU:     8 cores (16 threads with hyperthreading)
RAM:     32 GB
Storage: 500 GB NVMe SSD
Network: 1 Gbps dedicated

WHY THESE NUMBERS:
- 8 cores: 4 for compaction, 4 for request handling under load
- 32 GB: 8GB heap + 24GB for OS page cache (critical for read performance)
- NVMe: Compaction is I/O bound; SATA SSD adds 2-5x latency
- 1 Gbps: Streaming during repairs/bootstrapping saturates lesser links
```

#### Standard Production (100GB-500GB data per node)

```
CPU:     16 cores
RAM:     64 GB
Storage: 2 TB NVMe SSD
Network: 10 Gbps

WHY THESE NUMBERS:
- 16 cores: Handles 10K+ ops/sec comfortably
- 64 GB: 16-24GB heap + 40GB page cache
- 2 TB: 500GB data + 500GB for compaction headroom + growth
- 10 Gbps: Multi-DC replication and repairs without throttling
```

#### High-Performance Production (> 500GB per node)

```
CPU:     32+ cores
RAM:     128 GB
Storage: 4+ TB NVMe (multiple drives in JBOD)
Network: 25 Gbps

CRITICAL CONSIDERATIONS:
- Never exceed 31GB heap (compressed OOPs limit)
- Multiple smaller drives outperform single large drive
- CPU becomes bottleneck before other resources at this scale
```

### 3. JDK Selection

Cassandra is extremely sensitive to JDK choice. Wrong JDK = production incidents.

```bash
# Check Java version
java -version

# MUST see output like:
# openjdk version "11.0.x" or "17.0.x"
# OpenJDK Runtime Environment
```

**Supported JDK Matrix:**

| Cassandra | JDK 8 | JDK 11 | JDK 17 | JDK 21 |
|-----------|-------|--------|--------|--------|
| 5.0 | ❌ | ✅ | ✅ | ❌ |
| 4.1 | ❌ | ✅ | ✅ (4.1.3+) | ❌ |
| 4.0 | ❌ | ✅ | ❌ | ❌ |
| 3.11 | ✅ | ❌ | ❌ | ❌ |

**JDK Vendor Recommendations:**

1. **Eclipse Temurin (Adoptium)** - Recommended for most deployments
2. **Amazon Corretto** - Best for AWS deployments
3. **Azul Zulu** - Free with optional commercial support
4. **Oracle JDK** - Requires license for production

!!! danger "Never use these JDKs with Cassandra"
    - **GraalVM** - Incompatible bytecode optimizations
    - **OpenJ9/IBM J9** - Different memory model causes data corruption
    - **Any JDK < 11.0.11** - Critical GC bugs

---

## Installation Methods Comparison

| Method | Complexity | Update Path | Best For |
|--------|------------|-------------|----------|
| **Package Manager** | Low | `apt upgrade` | Single-node or learning |
| **Tarball** | Medium | Manual | Custom configurations, multiple versions |
| **Docker** | Low | Pull new image | Development, CI/CD |
| **Kubernetes** | High | Operator-managed | Cloud-native, auto-scaling |
| **Ansible** | Low | Re-run playbook | Production clusters, repeatable deployments |

!!! success "Recommendation for Production Deployments"
    For production clusters, we recommend **[Method 5: Ansible Automation](#method-5-ansible-automation-recommended-for-production)** using the [AxonOps Ansible Collection](https://github.com/axonops/axonops-ansible-collection). It automates all OS tuning, security hardening, and Cassandra best practices, and works as a standalone Cassandra installer even without AxonOps monitoring.

---

## Method 1: Package Manager Installation

### Ubuntu/Debian Installation

#### Step 1: System Preparation

```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# Install required dependencies
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    gnupg2 \
    curl \
    wget \
    net-tools \
    sysstat \
    iotop \
    htop

# Verify no existing Cassandra installation
dpkg -l | grep cassandra
# If found, remove completely:
# sudo apt-get remove --purge cassandra
# sudo rm -rf /var/lib/cassandra /var/log/cassandra /etc/cassandra
```

#### Step 2: Install Java 11

```bash
# Install OpenJDK 11
sudo apt-get install -y openjdk-11-jdk

# Verify installation
java -version
# Should output: openjdk version "11.0.x"

# Set JAVA_HOME (add to /etc/environment for persistence)
echo 'JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64' | sudo tee -a /etc/environment
source /etc/environment

# Verify JAVA_HOME
echo $JAVA_HOME
# Should output: /usr/lib/jvm/java-11-openjdk-amd64

# TROUBLESHOOTING: If multiple Java versions exist:
sudo update-alternatives --config java
# Select the java-11-openjdk option
```

#### Step 3: Add Cassandra Repository

```bash
# Download and add Apache Cassandra signing keys
curl -fsSL https://downloads.apache.org/cassandra/KEYS | sudo gpg --dearmor -o /usr/share/keyrings/cassandra-archive-keyring.gpg

# Verify the key was added
gpg --no-default-keyring --keyring /usr/share/keyrings/cassandra-archive-keyring.gpg --list-keys
# Should show Apache Cassandra keys

# Add the repository for Cassandra 5.0
echo "deb [signed-by=/usr/share/keyrings/cassandra-archive-keyring.gpg] https://debian.cassandra.apache.org 50x main" | \
    sudo tee /etc/apt/sources.list.d/cassandra.sources.list

# For Cassandra 4.1 instead, use:
# echo "deb [signed-by=/usr/share/keyrings/cassandra-archive-keyring.gpg] https://debian.cassandra.apache.org 41x main" | \
#     sudo tee /etc/apt/sources.list.d/cassandra.sources.list

# Update package list
sudo apt-get update

# Verify repository is available
apt-cache policy cassandra
# Should show available versions from debian.cassandra.apache.org
```

#### Step 4: Configure System Limits (BEFORE Installing)

!!! warning "Critical Step"
    Cassandra will fail or perform terribly without proper limits. Configure these before installing.

```bash
# Create limits configuration
sudo tee /etc/security/limits.d/cassandra.conf << 'EOF'
# Cassandra process limits
cassandra - memlock unlimited
cassandra - nofile 100000
cassandra - nproc 32768
cassandra - as unlimited

# Also set for root (for manual testing)
root - memlock unlimited
root - nofile 100000
root - nproc 32768
EOF

# Verify PAM is configured to read limits.d
grep -q "pam_limits.so" /etc/pam.d/common-session || \
    echo "session required pam_limits.so" | sudo tee -a /etc/pam.d/common-session

grep -q "pam_limits.so" /etc/pam.d/common-session-noninteractive || \
    echo "session required pam_limits.so" | sudo tee -a /etc/pam.d/common-session-noninteractive
```

#### Step 5: Disable Transparent Huge Pages

!!! danger "Mandatory Configuration"
    THP causes severe latency spikes with Cassandra. Disabling THP is mandatory for production.

```bash
# Check current THP status
cat /sys/kernel/mm/transparent_hugepage/enabled
# [always] madvise never  <- BAD: THP is enabled
# always madvise [never]  <- GOOD: THP is disabled

# Disable THP immediately
echo never | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
echo never | sudo tee /sys/kernel/mm/transparent_hugepage/defrag

# Make persistent across reboots - create systemd service
sudo tee /etc/systemd/system/disable-thp.service << 'EOF'
[Unit]
Description=Disable Transparent Huge Pages (THP)
DefaultDependencies=no
After=sysinit.target local-fs.target
Before=cassandra.service

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'echo never | tee /sys/kernel/mm/transparent_hugepage/enabled > /dev/null'
ExecStart=/bin/sh -c 'echo never | tee /sys/kernel/mm/transparent_hugepage/defrag > /dev/null'

[Install]
WantedBy=basic.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable disable-thp
sudo systemctl start disable-thp

# Verify it is disabled
cat /sys/kernel/mm/transparent_hugepage/enabled
# Should show: always madvise [never]
```

#### Step 6: Configure Swap (Important for Stability)

```bash
# Check current swap
free -h
cat /proc/swaps

# Option A: Disable swap entirely (recommended for dedicated Cassandra servers)
sudo swapoff -a
# Remove swap entries from /etc/fstab to make permanent
sudo sed -i '/swap/d' /etc/fstab

# Option B: Keep minimal swap but prevent Cassandra from using it
# Set vm.swappiness to 1 (not 0, which can cause OOM killer issues)
echo 'vm.swappiness = 1' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# IMPORTANT:
# - Cassandra manages its own memory via JVM heap
# - If Cassandra swaps, latency goes from milliseconds to seconds
# - OOM killer is preferable to swap-induced latency spirals
```

#### Step 7: Install Cassandra

```bash
# Install Cassandra
sudo apt-get install -y cassandra

# Don't start it yet - configuration is required first
sudo systemctl stop cassandra

# Verify installation
ls -la /etc/cassandra/
# Should see: cassandra.yaml, cassandra-env.sh, jvm11-server.options, etc.

ls -la /var/lib/cassandra/
# Should see: data, commitlog, saved_caches, hints directories
```

#### Step 8: Initial Configuration

```bash
# Backup original configuration
sudo cp /etc/cassandra/cassandra.yaml /etc/cassandra/cassandra.yaml.original

# Edit configuration
sudo nano /etc/cassandra/cassandra.yaml
```

**Minimum required changes for cassandra.yaml:**

```yaml
# CLUSTER IDENTIFICATION
# Must be identical across all nodes in the cluster
# Cannot be changed after data is written without wiping the cluster
cluster_name: 'Production Cluster'

# DIRECTORIES
# Change these if using dedicated disks (recommended)
data_file_directories:
  - /var/lib/cassandra/data   # Best on fast SSD
commitlog_directory: /var/lib/cassandra/commitlog  # Best on separate SSD
saved_caches_directory: /var/lib/cassandra/saved_caches
hints_directory: /var/lib/cassandra/hints

# NETWORK CONFIGURATION
# listen_address: IP other Cassandra nodes will use to connect
# rpc_address: IP clients will use to connect

# For single node development:
listen_address: localhost
rpc_address: localhost

# For production (replace with actual IP):
# listen_address: 192.168.1.10
# rpc_address: 192.168.1.10

# SEED NODES
# Seeds are used for bootstrapping gossip - NOT special nodes
# Use 2-3 seeds per datacenter, never more than 3
seed_provider:
  - class_name: org.apache.cassandra.locator.SimpleSeedProvider
    parameters:
      - seeds: "127.0.0.1"
      # For production cluster:
      # - seeds: "192.168.1.10,192.168.1.11"

# ENDPOINT SNITCH
# Determines how Cassandra locates nodes in the topology
# SimpleSnitch: Single DC, no rack awareness - development only
# GossipingPropertyFileSnitch: Production - reads from cassandra-rackdc.properties
endpoint_snitch: SimpleSnitch
# For production, change to:
# endpoint_snitch: GossipingPropertyFileSnitch
```

#### Step 9: Configure JVM Settings

For production systems, JVM settings must be tuned:

```bash
# Edit JVM options
sudo nano /etc/cassandra/jvm11-server.options
```

**Key settings to modify:**

```bash
# HEAP SIZE
# For 32GB RAM system, use 8GB heap (leaves 24GB for page cache)
# Find these lines and modify:
-Xms8G
-Xmx8G

# HEAP SIZING FORMULA:
# - Development (8GB RAM): -Xms2G -Xmx2G
# - Small prod (16GB RAM): -Xms4G -Xmx4G
# - Medium prod (32GB RAM): -Xms8G -Xmx8G
# - Large prod (64GB RAM): -Xms16G -Xmx16G
# - Max prod (128GB+ RAM): -Xms31G -Xmx31G (NEVER exceed 31G)

# GC LOGGING - essential for troubleshooting
# Uncomment or add:
-Xlog:gc*:file=/var/log/cassandra/gc.log:time,uptime:filecount=10,filesize=10M
```

#### Step 10: Start Cassandra

```bash
# Start the service
sudo systemctl start cassandra

# Watch the logs for startup (takes 30-120 seconds)
sudo tail -f /var/log/cassandra/system.log

# WHAT TO LOOK FOR IN LOGS:

# GOOD - startup is progressing:
# "Listening for thrift clients..."  (if enabled)
# "Starting listening for CQL clients on /127.0.0.1:9042"
# "Node /127.0.0.1 state jump to NORMAL"

# BAD - startup failed:
# "Exception encountered during startup"
# "OutOfMemoryError"
# "Unable to bind to address"

# Check service status
sudo systemctl status cassandra

# Verify node is up
nodetool status

# EXPECTED OUTPUT:
# Datacenter: datacenter1
# =======================
# Status=Up/Down
# |/ State=Normal/Leaving/Joining/Moving
# --  Address    Load       Tokens  Owns   Host ID                               Rack
# UN  127.0.0.1  674.83 KiB  16     100.0%  550e8400-e29b-41d4-a716-446655440000  rack1
#
# UN = Up and Normal (good)
# DN = Down and Normal (bad)
# UJ = Up and Joining (bootstrapping)
# UL = Up and Leaving (decommissioning)
```

#### Step 11: Enable Automatic Start

```bash
# Enable Cassandra to start on boot
sudo systemctl enable cassandra

# Verify it is enabled
systemctl is-enabled cassandra
# Should output: enabled
```

#### Step 12: Verify Installation

```bash
# Connect with cqlsh
cqlsh

# If connection is refused, wait 30 more seconds and retry

# Run basic verification queries
cqlsh> DESCRIBE CLUSTER;
# Shows cluster name and partitioner

cqlsh> SELECT cluster_name, listen_address, release_version FROM system.local;
# Shows current node info

cqlsh> CREATE KEYSPACE test_install WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
cqlsh> USE test_install;
cqlsh> CREATE TABLE test (id int PRIMARY KEY, value text);
cqlsh> INSERT INTO test (id, value) VALUES (1, 'installation successful');
cqlsh> SELECT * FROM test;
# Should return the inserted row

# Cleanup test data
cqlsh> DROP KEYSPACE test_install;
cqlsh> exit
```

---

### RHEL/CentOS/Rocky Linux Installation

#### Step 1: System Preparation

```bash
# Update system
sudo yum update -y

# Install dependencies
sudo yum install -y \
    curl \
    wget \
    net-tools \
    sysstat \
    iotop \
    htop \
    yum-utils

# Disable SELinux (or configure it properly)
# SELinux in enforcing mode blocks Cassandra file access
sudo setenforce 0
sudo sed -i 's/SELINUX=enforcing/SELINUX=permissive/' /etc/selinux/config
```

!!! warning "SELinux in High-Security Environments"
    For high-security environments, configure SELinux policies properly instead of disabling. See [Red Hat SELinux documentation](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/using_selinux/).

#### Step 2: Install Java 11

```bash
# Install OpenJDK 11
sudo yum install -y java-11-openjdk java-11-openjdk-devel

# Set as default (if multiple Java versions exist)
sudo alternatives --set java /usr/lib/jvm/java-11-openjdk-*/bin/java

# Verify
java -version

# Set JAVA_HOME
echo 'export JAVA_HOME=/usr/lib/jvm/java-11-openjdk' | sudo tee /etc/profile.d/java.sh
source /etc/profile.d/java.sh
```

#### Step 3: Configure System Limits

```bash
# Create limits file
sudo tee /etc/security/limits.d/cassandra.conf << 'EOF'
cassandra - memlock unlimited
cassandra - nofile 100000
cassandra - nproc 32768
cassandra - as unlimited
EOF

# For RHEL 7+, also configure systemd limits
sudo mkdir -p /etc/systemd/system/cassandra.service.d/
sudo tee /etc/systemd/system/cassandra.service.d/limits.conf << 'EOF'
[Service]
LimitNOFILE=100000
LimitNPROC=32768
LimitMEMLOCK=infinity
EOF
```

#### Step 4: Disable THP and Configure Swap

```bash
# Disable THP (same as Ubuntu)
echo never | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
echo never | sudo tee /sys/kernel/mm/transparent_hugepage/defrag

# Create persistent service (same as Ubuntu section above)

# Disable swap
sudo swapoff -a
sudo sed -i '/swap/d' /etc/fstab
```

#### Step 5: Add Cassandra Repository

```bash
# Create repo file for Cassandra 5.0
sudo tee /etc/yum.repos.d/cassandra.repo << 'EOF'
[cassandra]
name=Apache Cassandra
baseurl=https://redhat.cassandra.apache.org/50x/
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://downloads.apache.org/cassandra/KEYS
enabled=1
EOF

# Clean yum cache and verify
sudo yum clean all
sudo yum makecache
yum list available | grep cassandra
```

#### Step 6: Install and Configure

```bash
# Install Cassandra
sudo yum install -y cassandra

# Stop service for configuration
sudo systemctl stop cassandra

# Configure cassandra.yaml (same settings as Ubuntu section)
sudo nano /etc/cassandra/conf/cassandra.yaml

# Configure JVM options
sudo nano /etc/cassandra/conf/jvm11-server.options

# Note: RHEL/CentOS config path is /etc/cassandra/conf/
# Ubuntu/Debian config path is /etc/cassandra/
```

#### Step 7: Start and Verify

```bash
# Reload systemd for limit changes
sudo systemctl daemon-reload

# Start Cassandra
sudo systemctl start cassandra
sudo systemctl enable cassandra

# Verify
nodetool status
cqlsh
```

---

## Method 2: Tarball Installation

Use tarball installation when needing:
- Multiple Cassandra versions on one machine
- Installation in non-standard locations
- No root/sudo access
- Complete control over the installation

### Complete Tarball Installation

```bash
# Define version
CASSANDRA_VERSION="5.0.2"

# Create cassandra user (as root)
sudo useradd -r -m -d /opt/cassandra -s /bin/bash cassandra

# Download Cassandra
cd /tmp
wget https://downloads.apache.org/cassandra/${CASSANDRA_VERSION}/apache-cassandra-${CASSANDRA_VERSION}-bin.tar.gz

# Verify download integrity
wget https://downloads.apache.org/cassandra/${CASSANDRA_VERSION}/apache-cassandra-${CASSANDRA_VERSION}-bin.tar.gz.sha256
sha256sum -c apache-cassandra-${CASSANDRA_VERSION}-bin.tar.gz.sha256
# MUST output: apache-cassandra-X.X.X-bin.tar.gz: OK
# If verification fails, re-download - file may be corrupted or tampered

# Also verify GPG signature for production
wget https://downloads.apache.org/cassandra/${CASSANDRA_VERSION}/apache-cassandra-${CASSANDRA_VERSION}-bin.tar.gz.asc
wget https://downloads.apache.org/cassandra/KEYS
gpg --import KEYS
gpg --verify apache-cassandra-${CASSANDRA_VERSION}-bin.tar.gz.asc apache-cassandra-${CASSANDRA_VERSION}-bin.tar.gz
# Should show "Good signature from"

# Extract to installation directory
sudo tar -xzf apache-cassandra-${CASSANDRA_VERSION}-bin.tar.gz -C /opt/
sudo mv /opt/apache-cassandra-${CASSANDRA_VERSION} /opt/cassandra-${CASSANDRA_VERSION}
sudo ln -s /opt/cassandra-${CASSANDRA_VERSION} /opt/cassandra/current

# Create data directories on appropriate filesystems
# Ideally: data on one SSD, commitlog on another SSD
sudo mkdir -p /var/lib/cassandra/{data,commitlog,saved_caches,hints}
sudo mkdir -p /var/log/cassandra

# Set ownership
sudo chown -R cassandra:cassandra /opt/cassandra-${CASSANDRA_VERSION}
sudo chown -R cassandra:cassandra /opt/cassandra
sudo chown -R cassandra:cassandra /var/lib/cassandra
sudo chown -R cassandra:cassandra /var/log/cassandra

# Set permissions
sudo chmod 750 /var/lib/cassandra
sudo chmod 750 /var/log/cassandra
```

### Configure Environment

```bash
# Create environment file
sudo tee /etc/profile.d/cassandra.sh << 'EOF'
export CASSANDRA_HOME=/opt/cassandra/current
export PATH=$PATH:$CASSANDRA_HOME/bin
EOF

# Apply to current session
source /etc/profile.d/cassandra.sh

# Also set in cassandra user's profile
sudo -u cassandra bash -c 'echo "export CASSANDRA_HOME=/opt/cassandra/current" >> ~/.bashrc'
sudo -u cassandra bash -c 'echo "export PATH=\$PATH:\$CASSANDRA_HOME/bin" >> ~/.bashrc'
```

### Configure Cassandra

```bash
# Edit main configuration
sudo -u cassandra nano /opt/cassandra/current/conf/cassandra.yaml

# Key changes - update directory paths:
# data_file_directories:
#   - /var/lib/cassandra/data
# commitlog_directory: /var/lib/cassandra/commitlog
# saved_caches_directory: /var/lib/cassandra/saved_caches
# hints_directory: /var/lib/cassandra/hints

# Update cassandra-env.sh for logging
sudo -u cassandra nano /opt/cassandra/current/conf/cassandra-env.sh
# Find and update:
# export CASSANDRA_LOG_DIR=/var/log/cassandra
```

### Create systemd Service

```bash
sudo tee /etc/systemd/system/cassandra.service << 'EOF'
[Unit]
Description=Apache Cassandra Database
Documentation=https://cassandra.apache.org/doc/latest/
After=network-online.target
Wants=network-online.target

[Service]
Type=forking
User=cassandra
Group=cassandra
Environment="CASSANDRA_HOME=/opt/cassandra/current"
Environment="CASSANDRA_CONF=/opt/cassandra/current/conf"
Environment="CASSANDRA_LOG_DIR=/var/log/cassandra"
PIDFile=/var/run/cassandra/cassandra.pid
ExecStartPre=/bin/mkdir -p /var/run/cassandra
ExecStartPre=/bin/chown cassandra:cassandra /var/run/cassandra
ExecStart=/opt/cassandra/current/bin/cassandra -p /var/run/cassandra/cassandra.pid -R
ExecStop=/opt/cassandra/current/bin/nodetool drain
StandardOutput=journal
StandardError=journal

# Resource limits
LimitNOFILE=100000
LimitMEMLOCK=infinity
LimitNPROC=32768
LimitAS=infinity

# Restart behavior
Restart=on-failure
RestartSec=30s
TimeoutStartSec=180
TimeoutStopSec=180

[Install]
WantedBy=multi-user.target
EOF

# Reload and start
sudo systemctl daemon-reload
sudo systemctl start cassandra
sudo systemctl enable cassandra

# Verify
sudo systemctl status cassandra
nodetool status
```

---

## Method 3: Docker Installation

!!! info "Docker Use Cases"
    Docker is excellent for development, CI/CD pipelines, and learning. For production, consider Kubernetes operators instead.

### Development: Single Node

```bash
# Basic single node
docker run --name cassandra-dev \
  -d \
  -p 9042:9042 \
  -e CASSANDRA_CLUSTER_NAME=DevCluster \
  -e HEAP_NEWSIZE=256M \
  -e MAX_HEAP_SIZE=1G \
  cassandra:5.0

# With persistent data (survives container restarts)
docker volume create cassandra-data

docker run --name cassandra-dev \
  -d \
  -p 9042:9042 \
  -v cassandra-data:/var/lib/cassandra \
  -e CASSANDRA_CLUSTER_NAME=DevCluster \
  -e HEAP_NEWSIZE=256M \
  -e MAX_HEAP_SIZE=1G \
  cassandra:5.0

# Check logs for startup completion
docker logs -f cassandra-dev
# Wait for: "Starting listening for CQL clients on /0.0.0.0:9042"

# Connect
docker exec -it cassandra-dev cqlsh

# Or use CQLAI from host (if installed)
cqlai -h localhost -p 9042
```

### Development: Multi-Node Cluster

**docker-compose.yml for 3-node cluster:**

```yaml
version: '3.8'

# IMPORTANT: This is for development/testing only
# Production deployments should use Kubernetes operators

services:
  cassandra-seed:
    image: cassandra:5.0
    container_name: cassandra-seed
    hostname: cassandra-seed
    ports:
      - "9042:9042"      # CQL
      - "7199:7199"      # JMX
    environment:
      - CASSANDRA_CLUSTER_NAME=DockerCluster
      - CASSANDRA_DC=dc1
      - CASSANDRA_RACK=rack1
      - CASSANDRA_ENDPOINT_SNITCH=GossipingPropertyFileSnitch
      - CASSANDRA_NUM_TOKENS=16
      - HEAP_NEWSIZE=256M
      - MAX_HEAP_SIZE=1G
    volumes:
      - cassandra-seed-data:/var/lib/cassandra
    networks:
      - cassandra-net
    healthcheck:
      test: ["CMD", "cqlsh", "-e", "describe cluster"]
      interval: 30s
      timeout: 10s
      retries: 10
      start_period: 60s

  cassandra-node1:
    image: cassandra:5.0
    container_name: cassandra-node1
    hostname: cassandra-node1
    depends_on:
      cassandra-seed:
        condition: service_healthy
    environment:
      - CASSANDRA_CLUSTER_NAME=DockerCluster
      - CASSANDRA_DC=dc1
      - CASSANDRA_RACK=rack1
      - CASSANDRA_ENDPOINT_SNITCH=GossipingPropertyFileSnitch
      - CASSANDRA_SEEDS=cassandra-seed
      - CASSANDRA_NUM_TOKENS=16
      - HEAP_NEWSIZE=256M
      - MAX_HEAP_SIZE=1G
    volumes:
      - cassandra-node1-data:/var/lib/cassandra
    networks:
      - cassandra-net
    healthcheck:
      test: ["CMD", "cqlsh", "-e", "describe cluster"]
      interval: 30s
      timeout: 10s
      retries: 10
      start_period: 60s

  cassandra-node2:
    image: cassandra:5.0
    container_name: cassandra-node2
    hostname: cassandra-node2
    depends_on:
      cassandra-node1:
        condition: service_healthy
    environment:
      - CASSANDRA_CLUSTER_NAME=DockerCluster
      - CASSANDRA_DC=dc1
      - CASSANDRA_RACK=rack1
      - CASSANDRA_ENDPOINT_SNITCH=GossipingPropertyFileSnitch
      - CASSANDRA_SEEDS=cassandra-seed
      - CASSANDRA_NUM_TOKENS=16
      - HEAP_NEWSIZE=256M
      - MAX_HEAP_SIZE=1G
    volumes:
      - cassandra-node2-data:/var/lib/cassandra
    networks:
      - cassandra-net

volumes:
  cassandra-seed-data:
  cassandra-node1-data:
  cassandra-node2-data:

networks:
  cassandra-net:
    driver: bridge
```

**Start the cluster:**

```bash
# Start seed node first (health check ensures it is ready)
docker-compose up -d cassandra-seed

# Wait for seed to be healthy (watch for healthy status)
docker-compose ps
# Wait until cassandra-seed shows "healthy"

# Start remaining nodes (depends_on + health check handles ordering)
docker-compose up -d

# Monitor startup
docker-compose logs -f

# Check cluster status
docker exec -it cassandra-seed nodetool status
# All nodes should show UN (Up Normal)
```

**Cleanup:**

```bash
# Stop cluster
docker-compose down

# Stop and remove data (DESTROYS DATA)
docker-compose down -v
```

---

## Method 4: Kubernetes Installation

!!! tip "Use an Operator"
    For Kubernetes, use an operator rather than raw StatefulSets. Operators handle complex operations like scaling, repairs, and upgrades.

### Option A: K8ssandra (Recommended)

K8ssandra is a production-ready distribution that includes Cassandra, Stargate (APIs), Reaper (repairs), Medusa (backups), and monitoring.

```bash
# Prerequisites
# - Kubernetes 1.21+
# - kubectl configured
# - Helm 3.x
# - cert-manager installed

# Install cert-manager (required)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Wait for cert-manager
kubectl wait --for=condition=Available deployment --all -n cert-manager --timeout=300s

# Add K8ssandra Helm repo
helm repo add k8ssandra https://helm.k8ssandra.io/stable
helm repo update

# Install K8ssandra operator
helm install k8ssandra-operator k8ssandra/k8ssandra-operator \
  -n k8ssandra-operator \
  --create-namespace \
  --wait

# Verify operator is running
kubectl get pods -n k8ssandra-operator
```

**Create a Cassandra cluster:**

```yaml
# k8ssandra-cluster.yaml
apiVersion: k8ssandra.io/v1alpha1
kind: K8ssandraCluster
metadata:
  name: production
  namespace: k8ssandra-operator
spec:
  cassandra:
    serverVersion: "4.1.3"
    serverImage: "k8ssandra/cass-management-api:4.1.3"

    # Cluster topology
    datacenters:
      - metadata:
          name: dc1
        size: 3  # Number of nodes

        # Storage configuration
        storageConfig:
          cassandraDataVolumeClaimSpec:
            storageClassName: fast-ssd  # Use appropriate storage class
            accessModes:
              - ReadWriteOnce
            resources:
              requests:
                storage: 100Gi

        # Resource allocation
        resources:
          requests:
            cpu: 2000m
            memory: 8Gi
          limits:
            cpu: 4000m
            memory: 16Gi

        # JVM settings
        config:
          jvmOptions:
            heapSize: 4Gi
            heapNewGenSize: 1Gi

        # Cassandra configuration overrides
        config:
          cassandraYaml:
            num_tokens: 16
            allocate_tokens_for_local_replication_factor: 3
            concurrent_reads: 32
            concurrent_writes: 32
            concurrent_counter_writes: 32

    # Authentication
    superuserSecretRef:
      name: cassandra-superuser

    # Reaper for repairs (optional but recommended)
    reaper:
      autoScheduling:
        enabled: true

    # Medusa for backups (optional)
    medusa:
      storageProperties:
        storageProvider: s3
        region: us-east-1
        bucketName: my-cassandra-backups
        storageSecretRef:
          name: medusa-bucket-secret
```

**Deploy:**

```bash
# Create superuser secret
kubectl create secret generic cassandra-superuser \
  -n k8ssandra-operator \
  --from-literal=username=admin \
  --from-literal=password='YourSecurePassword123!'

# Apply cluster configuration
kubectl apply -f k8ssandra-cluster.yaml

# Watch pods come up (takes 5-10 minutes)
kubectl get pods -n k8ssandra-operator -w

# Check cluster status
kubectl exec -it production-dc1-default-sts-0 -n k8ssandra-operator -- nodetool status
```

### Option B: Cass-Operator (DataStax)

```bash
# Install Cass-Operator
kubectl apply -f https://raw.githubusercontent.com/k8ssandra/cass-operator/v1.18.2/docs/user/cass-operator-manifests.yaml

# Create namespace for cluster
kubectl create namespace cassandra

# Create cluster
kubectl apply -f - <<EOF
apiVersion: cassandra.datastax.com/v1beta1
kind: CassandraDatacenter
metadata:
  name: dc1
  namespace: cassandra
spec:
  clusterName: production
  serverType: cassandra
  serverVersion: "4.1.3"
  managementApiAuth:
    insecure: {}
  size: 3
  storageConfig:
    cassandraDataVolumeClaimSpec:
      storageClassName: fast-ssd
      accessModes:
        - ReadWriteOnce
      resources:
        requests:
          storage: 100Gi
  resources:
    requests:
      memory: 8Gi
      cpu: 2000m
    limits:
      memory: 16Gi
      cpu: 4000m
  config:
    cassandra-yaml:
      num_tokens: 16
    jvm-server-options:
      initial_heap_size: 4G
      max_heap_size: 4G
EOF
```

---

## Method 5: Ansible Automation (Recommended for Production)

For automated, repeatable deployments across multiple environments, the [AxonOps Ansible Collection](https://github.com/axonops/axonops-ansible-collection) provides production-grade installation of Apache Cassandra with optional AxonOps monitoring integration.

!!! tip "Standalone Cassandra Installation"
    The Cassandra role in this collection is **fully standalone**. You can deploy a production-ready Apache Cassandra cluster without using AxonOps. The collection handles all the complex configuration, OS tuning, and best practices automatically.

!!! example "Ready-to-Use Reference Implementation"
    For a complete, production-grade example you can clone and adapt, see the **[AxonOps Cassandra Lab](https://github.com/axonops/ansible-cassandra-lab)**. This project demonstrates a multi-datacenter Cassandra 5.0 deployment with Terraform infrastructure provisioning and complete Ansible configuration, including SSL/TLS, authentication, audit logging, and AxonOps monitoring.

### Why Use Ansible for Cassandra?

| Benefit | Description |
|---------|-------------|
| **Production-Ready** | Implements all OS tuning, limits, THP disabling, and Cassandra best practices automatically |
| **Repeatable** | Same playbook deploys identical clusters across dev, staging, and production |
| **Multi-Version** | Supports Cassandra 3.11, 4.x, and 5.x with version-specific configurations |
| **Tarball-Based** | Default tar installation simplifies upgrades and downgrades vs package managers |
| **Optional Monitoring** | Add AxonOps agent for monitoring (SaaS or self-hosted) only if needed |
| **Idempotent** | Run playbooks repeatedly without breaking existing installations |
| **Multi-Environment** | Hierarchical configuration supports dev, staging, and production from one codebase |

### Prerequisites

- Ansible 2.9+ installed on control machine
- SSH access to target nodes (key-based authentication recommended)
- Target nodes running supported Linux (RHEL/CentOS 7+, Ubuntu 18.04+, Debian 10+)
- Python 3.x on target nodes
- (Optional) Pipenv for isolated Python environments

### Quick Start: Install the Collection

```bash
# Download the latest release
curl -L -o axonops-ansible.tar.gz \
  https://github.com/axonops/axonops-ansible-collection/releases/latest/download/axonops-axonops-latest.tar.gz

# Install the collection
ansible-galaxy collection install axonops-ansible.tar.gz

# Verify installation
ansible-galaxy collection list | grep axonops
```

### Available Roles

The collection provides roles for complete infrastructure deployment:

| Role | Purpose |
|------|---------|
| `axonops.axonops.preflight` | Pre-installation system checks and validation |
| `axonops.axonops.java` | Install Java (OpenJDK or Azul Zulu) |
| `axonops.axonops.cassandra` | Install and configure Apache Cassandra |
| `axonops.axonops.agent` | Install AxonOps monitoring agent |
| `axonops.axonops.server` | Install AxonOps Server (self-hosted) |
| `axonops.axonops.dash` | Install AxonOps Dashboard (self-hosted) |
| `axonops.axonops.elastic` | Install Elasticsearch for AxonOps |
| `axonops.axonops.configurations` | Configure alerts, integrations, backups |

### Option A: Simple Deployment (Single Environment)

For a straightforward deployment without multi-environment complexity:

**inventory.yml:**

```yaml
all:
  children:
    cassandra:
      hosts:
        cass-node1:
          ansible_host: 192.168.1.10
          cassandra_rack: rack1
        cass-node2:
          ansible_host: 192.168.1.11
          cassandra_rack: rack2
        cass-node3:
          ansible_host: 192.168.1.12
          cassandra_rack: rack3
      vars:
        # Cassandra configuration
        cassandra_cluster_name: "ProductionCluster"
        cassandra_version: "5.0.5"
        cassandra_dc: "dc1"

        # Installation method (tar recommended)
        cassandra_install_format: tar

        # Java configuration
        java_pkg: "java-17-openjdk-headless"

        # Seed nodes (first 2-3 nodes)
        cassandra_seeds:
          - 192.168.1.10
          - 192.168.1.11

        # Security settings
        cassandra_authenticator: PasswordAuthenticator
        cassandra_authorizer: CassandraAuthorizer
```

**cassandra.yml playbook:**

```yaml
---
- name: Deploy Apache Cassandra Cluster
  hosts: cassandra
  become: true

  roles:
    - role: axonops.axonops.preflight
    - role: axonops.axonops.java
    - role: axonops.axonops.cassandra
```

**Deploy:**

```bash
ansible-playbook -i inventory.yml cassandra.yml
```

### Option B: Production Multi-Environment Structure

For production deployments, use hierarchical configuration with `group_vars` for environment-specific overrides. This structure is demonstrated in the [full example](https://github.com/axonops/axonops-ansible-collection/tree/main/examples/full-example).

**Recommended project structure:**

```
my-cassandra-deployment/
├── ansible.cfg
├── Makefile
├── requirements.yml
│
├── inventories/
│   ├── dev/hosts.ini
│   ├── stg/hosts.ini
│   └── prd/hosts.ini
│
├── group_vars/
│   ├── all/                    # Global defaults
│   │   ├── cassandra.yml       # Cassandra defaults
│   │   ├── java.yml            # Java configuration
│   │   └── common.yml          # OS settings
│   ├── dev/                    # Development overrides
│   │   ├── cassandra.yml
│   │   └── vault.yml           # Encrypted secrets
│   ├── stg/                    # Staging overrides
│   │   ├── cassandra.yml
│   │   └── vault.yml
│   └── prd/                    # Production overrides
│       ├── cassandra.yml
│       └── vault.yml
│
├── files/
│   ├── dev/ssl/                # Dev certificates
│   ├── stg/ssl/                # Staging certificates
│   └── prd/ssl/                # Production certificates
│
├── alerts-config/              # AxonOps monitoring (optional)
│   └── my-org/
│       ├── alert_endpoints.yml
│       ├── metric_alert_rules.yml
│       └── prd/                # Cluster-specific overrides
│           └── alert_routes.yml
│
├── cassandra.yml               # Main playbook
├── common.yml                  # OS hardening playbook
└── rolling-restart.yml         # Safe restart playbook
```

**Example inventories/prd/hosts.ini:**

```ini
[cassandra]
cass-prd-1 ansible_host=10.0.1.10 cassandra_rack=rack1
cass-prd-2 ansible_host=10.0.1.11 cassandra_rack=rack2
cass-prd-3 ansible_host=10.0.1.12 cassandra_rack=rack3
cass-prd-4 ansible_host=10.0.2.10 cassandra_rack=rack1 cassandra_dc=dc2
cass-prd-5 ansible_host=10.0.2.11 cassandra_rack=rack2 cassandra_dc=dc2
cass-prd-6 ansible_host=10.0.2.12 cassandra_rack=rack3 cassandra_dc=dc2

[cassandra:vars]
cassandra_dc=dc1
```

**Example group_vars/all/cassandra.yml (global defaults):**

```yaml
# Cassandra version and installation
cassandra_version: "5.0.5"
cassandra_install_format: tar

# Cluster defaults
cassandra_num_tokens: 16
cassandra_endpoint_snitch: GossipingPropertyFileSnitch

# Performance tuning
cassandra_concurrent_reads: 32
cassandra_concurrent_writes: 32
cassandra_concurrent_counter_writes: 32
cassandra_memtable_flush_writers: 2

# Security defaults
cassandra_authenticator: PasswordAuthenticator
cassandra_authorizer: CassandraAuthorizer
cassandra_role_manager: CassandraRoleManager

# Audit logging
cassandra_audit_logging_enabled: true
cassandra_audit_logging_included_categories: DDL,DCL,AUTH,ERROR
```

**Example group_vars/prd/cassandra.yml (production overrides):**

```yaml
# Production cluster name
cassandra_cluster_name: "Production-Cassandra"

# Production seeds
cassandra_seeds:
  - 10.0.1.10
  - 10.0.1.11
  - 10.0.2.10

# Production performance tuning
cassandra_concurrent_reads: 64
cassandra_concurrent_writes: 64

# Enable SSL in production
cassandra_ssl_enable: true
cassandra_ssl_internode: true
cassandra_ssl_client: true
```

### Secrets Management with Ansible Vault

Encrypt sensitive configuration using Ansible Vault:

```bash
# Create vault password file (do not commit to Git)
echo "your-secure-password" > ~/.ansible_vault_pass
chmod 600 ~/.ansible_vault_pass

# Create encrypted secrets file
ansible-vault create group_vars/prd/vault.yml
```

**Example vault.yml content:**

```yaml
# Cassandra credentials
vault_cassandra_admin_password: "SecurePassword123!"
vault_cassandra_jmx_password: "JmxSecurePass456!"

# SSL keystore passwords
vault_cassandra_ssl_keystore_pass: "keystorepass"
vault_cassandra_ssl_truststore_pass: "truststorepass"

# AxonOps credentials (if using)
vault_axon_agent_key: "your-agent-key-from-axonops"
vault_axon_agent_customer_name: "your-org-name"
```

**Reference vault variables in playbooks:**

```yaml
# In group_vars/prd/cassandra.yml
cassandra_admin_password: "{{ vault_cassandra_admin_password }}"
cassandra_ssl_keystore_password: "{{ vault_cassandra_ssl_keystore_pass }}"
```

### Makefile Workflow

Use a Makefile for consistent deployment commands:

```makefile
ENVIRONMENT ?= dev
ANSIBLE_USER ?= root
ANSIBLE_VAULT_PASSWORD_FILE ?= ~/.ansible_vault_pass
EXTRA ?=

.PHONY: prep common cassandra alerts rolling-restart

prep:
	ansible-galaxy collection install -r requirements.yml

common:
	ansible-playbook -i inventories/$(ENVIRONMENT)/hosts.ini \
		-u $(ANSIBLE_USER) \
		--vault-password-file $(ANSIBLE_VAULT_PASSWORD_FILE) \
		common.yml $(EXTRA)

cassandra:
	ansible-playbook -i inventories/$(ENVIRONMENT)/hosts.ini \
		-u $(ANSIBLE_USER) \
		--vault-password-file $(ANSIBLE_VAULT_PASSWORD_FILE) \
		cassandra.yml $(EXTRA)

alerts:
	ansible-playbook -i inventories/$(ENVIRONMENT)/hosts.ini \
		-u $(ANSIBLE_USER) \
		--vault-password-file $(ANSIBLE_VAULT_PASSWORD_FILE) \
		alerts.yml $(EXTRA)

rolling-restart:
	ansible-playbook -i inventories/$(ENVIRONMENT)/hosts.ini \
		-u $(ANSIBLE_USER) \
		--vault-password-file $(ANSIBLE_VAULT_PASSWORD_FILE) \
		rolling-restart.yml $(EXTRA)
```

**Deploy to different environments:**

```bash
# Deploy to development
make cassandra ENVIRONMENT=dev

# Deploy to production
make cassandra ENVIRONMENT=prd

# Dry-run to production (no changes)
make cassandra ENVIRONMENT=prd EXTRA="--check --diff"

# Update configuration only (no reinstall)
make cassandra ENVIRONMENT=prd EXTRA="--tags config"
```

### SSL/TLS Configuration

**Development (auto-generated self-signed certificates):**

```yaml
# group_vars/dev/cassandra.yml
cassandra_ssl_enable: true
cassandra_ssl_create: true  # Auto-generate certificates
```

Certificates are stored in `files/dev/ssl/` and SHOULD be committed to Git for development consistency.

**Production (organization-managed certificates):**

```yaml
# group_vars/prd/cassandra.yml
cassandra_ssl_enable: true
cassandra_ssl_create: false  # Use provided certificates
cassandra_ssl_keystore_password: "{{ vault_cassandra_ssl_keystore_pass }}"
cassandra_ssl_truststore_password: "{{ vault_cassandra_ssl_truststore_pass }}"
```

Place CA-signed certificates in `files/prd/ssl/` (encrypted or via external secrets management).

### Adding AxonOps Monitoring

Add the AxonOps agent role to enable monitoring:

**cassandra.yml playbook with monitoring:**

```yaml
---
- name: Deploy Apache Cassandra with AxonOps Monitoring
  hosts: cassandra
  become: true

  roles:
    - role: axonops.axonops.preflight
    - role: axonops.axonops.java
    - role: axonops.axonops.cassandra
    - role: axonops.axonops.agent
```

**group_vars/prd/axonops.yml:**

```yaml
# AxonOps Cloud
axon_agent_server_host: "agents.axonops.cloud"
axon_agent_customer_name: "{{ vault_axon_agent_customer_name }}"
axon_agent_key: "{{ vault_axon_agent_key }}"
axon_java_agent: "axon-cassandra5.0-agent"

# Or for self-hosted AxonOps:
# axon_agent_server_host: "axonops.internal.example.com"
```

### AxonOps Configuration as Code

Configure monitoring, alerts, and backups via YAML files in `alerts-config/`:

```
alerts-config/
└── my-org/                           # Organization name
    ├── alert_endpoints.yml           # Slack, PagerDuty, email
    ├── metric_alert_rules.yml        # Default metric alerts
    ├── log_alert_rules.yml           # Log-based alerts
    ├── service_checks.yml            # Health checks
    └── prd/                           # Cluster-specific overrides
        ├── alert_routes.yml          # Route alerts to endpoints
        ├── backups.yml               # Backup schedules
        └── dashboards.yml            # Custom dashboards
```

**Example alert_endpoints.yml:**

```yaml
endpoints:
  - name: slack-ops
    type: slack
    webhook_url: "{{ vault_slack_webhook_url }}"
    channel: "#cassandra-alerts"

  - name: pagerduty-critical
    type: pagerduty
    routing_key: "{{ vault_pagerduty_routing_key }}"
```

Apply monitoring configuration:

```bash
make alerts ENVIRONMENT=prd
```

### Key Configuration Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `cassandra_version` | Latest | Cassandra version (e.g., `5.0.5`, `4.1.6`) |
| `cassandra_install_format` | `tar` | Installation method: `tar` (recommended) or `pkg` |
| `cassandra_cluster_name` | `Test Cluster` | Cluster name (MUST match all nodes) |
| `cassandra_dc` | `dc1` | Datacenter name |
| `cassandra_rack` | `rack1` | Rack name |
| `cassandra_seeds` | `[]` | Seed node IPs |
| `cassandra_num_tokens` | `16` | Number of virtual nodes |
| `cassandra_authenticator` | `AllowAllAuthenticator` | Authentication class |
| `cassandra_authorizer` | `AllowAllAuthorizer` | Authorization class |
| `cassandra_ssl_enable` | `false` | Enable SSL/TLS |
| `cassandra_ssl_create` | `false` | Auto-generate certificates |
| `cassandra_audit_logging_enabled` | `false` | Enable audit logging |
| `java_pkg` | `java-11-openjdk-headless` | Java package |
| `axon_java_agent` | - | AxonOps agent version |
| `axon_agent_server_host` | - | AxonOps server address |

### What the Cassandra Role Configures

The role automatically handles all production requirements:

- **OS Configuration**: File descriptor limits (100,000+), nproc limits, memory locking
- **Transparent Huge Pages**: Disabled automatically
- **Swap Configuration**: Configured for Cassandra workloads
- **Directory Structure**: Creates data, commitlog, hints, saved_caches with correct permissions
- **cassandra.yaml**: Complete configuration including cluster settings, networking, snitch, tokens
- **JVM Options**: Heap sizing (auto-calculated or manual), GC settings, JMX configuration
- **Security**: Authentication, authorization, SSL/TLS, audit logging
- **Systemd Service**: Creates and enables the Cassandra service
- **Firewall Rules**: Opens required ports if firewalld is active

### Common Operations

**Rolling restart (zero-downtime):**

```bash
make rolling-restart ENVIRONMENT=prd
```

The rolling restart playbook:

1. Checks cluster health before starting
2. Drains each node before restart
3. Waits for node to rejoin cluster
4. Verifies cluster health before proceeding to next node

**Configuration update (no reinstall):**

```bash
# Edit configuration
vim group_vars/prd/cassandra.yml

# Apply config changes only
make cassandra ENVIRONMENT=prd EXTRA="--tags config"

# Restart to apply
make rolling-restart ENVIRONMENT=prd
```

**Upgrade Cassandra version:**

```yaml
# Update version in group_vars
cassandra_version: "5.0.6"
```

```bash
# Apply upgrade
make cassandra ENVIRONMENT=prd -e "cassandra_upgrade=true"

# Rolling restart to complete upgrade
make rolling-restart ENVIRONMENT=prd
```

### Troubleshooting

```bash
# Test connectivity to all nodes
ansible -i inventories/prd/hosts.ini cassandra -m ping

# Run with verbose output
make cassandra ENVIRONMENT=prd EXTRA="-vvv"

# Run only preflight checks
make cassandra ENVIRONMENT=prd EXTRA="--tags preflight"

# Check cluster status across all nodes
ansible -i inventories/prd/hosts.ini cassandra -a "nodetool status"

# View Cassandra logs
ansible -i inventories/prd/hosts.ini cassandra -a "tail -50 /var/log/cassandra/system.log"

# Check AxonOps agent status
ansible -i inventories/prd/hosts.ini cassandra -a "systemctl status axon-agent"
```

### Reference Implementation: AxonOps Cassandra Lab

For a complete, working example that you can clone and adapt, see the **[AxonOps Cassandra Lab](https://github.com/axonops/ansible-cassandra-lab)**:

- **Multi-datacenter**: 12 nodes across 2 DCs with 3 racks each
- **Infrastructure as Code**: Terraform for Hetzner Cloud (adaptable to other providers)
- **Complete security**: SSL/TLS, authentication, authorization, audit logging
- **AxonOps integration**: Full monitoring, alerting, and backup configuration
- **Web terminal**: Wetty-based browser access to cluster
- **Workbench integration**: AxonOps Workbench configuration included

```bash
# Clone the lab project
git clone https://github.com/axonops/ansible-cassandra-lab.git
cd ansible-cassandra-lab

# Review and adapt configuration
cat ansible/group_vars/all/cassandra.yml

# Deploy (after configuring infrastructure)
cd ansible
make cassandra ENVIRONMENT=lab
```

### Additional Resources

- **Ansible Collection**: [axonops/axonops-ansible-collection](https://github.com/axonops/axonops-ansible-collection)
- **Full Example**: [examples/full-example](https://github.com/axonops/axonops-ansible-collection/tree/main/examples/full-example)
- **Cassandra Lab**: [axonops/ansible-cassandra-lab](https://github.com/axonops/ansible-cassandra-lab)
- **AxonOps Cloud Setup**: [Getting Started with AxonOps Cloud](../../../../get_started/cloud.md)
- **AxonOps Self-Hosted**: [Installing AxonOps Server](../../../../installation/axon-server/axonserver_install.md)

!!! note "Prefer Chef?"
    If your organization uses Chef instead of Ansible, see the [AxonOps Chef Cookbook](https://github.com/axonops/axonops-chef) for similar functionality.

---

## Post-Installation Validation Checklist

After any installation method, verify these items:

### 1. Cluster Health

```bash
# Check all nodes are up
nodetool status
# All nodes should show 'UN' (Up Normal)

# Check for schema agreement
nodetool describecluster
# Schema versions should show single version (all nodes agree)

# Check gossip information
nodetool gossipinfo
# Should show status=NORMAL for all nodes
```

### 2. Basic Functionality

```sql
-- Connect and verify
cqlsh

-- Check cluster info
DESCRIBE CLUSTER;

-- Test write
CREATE KEYSPACE IF NOT EXISTS system_check WITH replication = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};

USE system_check;

CREATE TABLE IF NOT EXISTS health_check (
  check_id uuid PRIMARY KEY,
  check_time timestamp,
  status text
);

INSERT INTO health_check (check_id, check_time, status)
VALUES (uuid(), toTimestamp(now()), 'OK');

-- Test read
SELECT * FROM health_check;

-- Cleanup
DROP KEYSPACE system_check;
```

### 3. Resource Verification

```bash
# Check file descriptor limits
cat /proc/$(pgrep -f CassandraDaemon)/limits | grep "open files"
# Should show at least 100000

# Check THP is disabled
cat /sys/kernel/mm/transparent_hugepage/enabled
# Should show: always madvise [never]

# Check heap size
nodetool info | grep "Heap Memory"
# Should match the configured heap size

# Check GC type
nodetool gcstats
# Shows GC statistics and type
```

### 4. Performance Baseline

```bash
# Run a quick benchmark
cassandra-stress write n=10000 -rate threads=4

# Expected output for healthy system:
# Op rate: > 1000 ops/sec
# Latency mean: < 10ms
# Latency 99th: < 100ms
```

---

## Troubleshooting Installation Issues

### Issue: Cassandra Won't Start

```bash
# Check the logs first - ALWAYS
sudo tail -100 /var/log/cassandra/system.log
sudo journalctl -u cassandra -n 100

# Common causes and solutions:

# 1. Java not found
# Error: "Unable to find java executable"
# Solution: Install JDK 11 and set JAVA_HOME
which java
echo $JAVA_HOME

# 2. Port already in use
# Error: "java.net.BindException: Address already in use"
# Solution: Find and stop conflicting process
sudo lsof -i :9042
sudo lsof -i :7000
sudo lsof -i :7199

# 3. Out of memory
# Error: "java.lang.OutOfMemoryError"
# Solution: Reduce heap size or add more RAM
free -h  # Check available memory

# 4. Permission denied
# Error: "AccessDeniedException" or "Permission denied"
# Solution: Fix ownership
sudo chown -R cassandra:cassandra /var/lib/cassandra
sudo chown -R cassandra:cassandra /var/log/cassandra

# 5. Corrupt system tables (after crash)
# Error: "CorruptSSTableException" on startup
# Solution: Try removing corrupt files (DANGEROUS - last resort)
# First try: nodetool scrub system
# If that fails, examine which file is corrupt from logs
```

### Issue: cqlsh Connection Refused

```bash
# Is Cassandra actually running?
sudo systemctl status cassandra
ps aux | grep cassandra

# Is native transport enabled and listening?
grep "native_transport_port" /etc/cassandra/cassandra.yaml
sudo netstat -tlnp | grep 9042

# Check if startup completed
sudo tail /var/log/cassandra/system.log | grep "Starting listening for CQL"

# Try connecting with explicit host
cqlsh 127.0.0.1 9042 --debug

# Check rpc_address setting
grep "rpc_address" /etc/cassandra/cassandra.yaml
# If rpc_address: 0.0.0.0, also set broadcast_rpc_address to the node IP
```

### Issue: Node Won't Join Cluster

```bash
# Check seeds are reachable
ping <seed_ip>
telnet <seed_ip> 7000  # Gossip port

# Check cluster_name matches exactly
grep cluster_name /etc/cassandra/cassandra.yaml
# Must be IDENTICAL on all nodes, including spaces and case

# Check tokens are not conflicting
nodetool ring | head

# Look for gossip issues
grep -i gossip /var/log/cassandra/system.log | tail -20

# Verify snitch is consistent across cluster
grep endpoint_snitch /etc/cassandra/cassandra.yaml
# All nodes should use same snitch
```

### Issue: Slow Performance After Installation

```bash
# Check THP is actually disabled
cat /sys/kernel/mm/transparent_hugepage/enabled
# Must show [never]

# Check swap usage
free -h
# Swap used should be 0 or nearly 0

# Check GC behavior
nodetool gcstats
# G1 or ZGC should be in use, not CMS

# Check compaction is not backed up
nodetool compactionstats
# Pending tasks should be low (< 10)

# Check disk I/O
iostat -xm 2
# await should be < 5ms for SSD
# %util should be < 80%
```

---

## Next Steps After Installation

1. **[Configure the Cluster](../first-cluster.md)** - Multi-node setup and networking
2. **[Security Setup](../../security/index.md)** - Enable authentication and encryption
3. **[Production Checklist](../production-checklist.md)** - Complete production readiness
4. **[Install CQLAI](../../tools/cqlai/installation/index.md)** - Modern CQL shell with AI assistance
5. **[Set Up Monitoring](../../operations/monitoring/index.md)** - Monitor the cluster with AxonOps
