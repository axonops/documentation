# Playbook: Replace a Dead Node

This playbook provides step-by-step instructions for replacing a failed Cassandra node that cannot be recovered.

## Overview

| Attribute | Value |
|-----------|-------|
| **Estimated Duration** | 30 minutes - 4 hours (depends on data size) |
| **Risk Level** | Medium |
| **Requires Downtime** | No (cluster remains available) |
| **Prerequisites** | Replacement hardware ready, network accessible |

## When to Use This Playbook

- Node hardware has failed and cannot be recovered
- Node has been down longer than `max_hint_window_in_ms` (default: 3 hours)
- Corrupted data that cannot be repaired
- Decommissioning and replacing simultaneously

## Prerequisites

- [ ] Replacement server provisioned with same specifications
- [ ] Cassandra installed (same version as cluster)
- [ ] Network connectivity verified to all cluster nodes
- [ ] Firewall rules configured (ports 7000, 7001, 9042, 7199)
- [ ] NTP synchronized
- [ ] Sufficient disk space (at least equal to failed node)

---

## Step 1: Confirm Node Status

### 1.1 Verify Node is Down

```bash
# On any live node
nodetool status
```

**Expected output**: Dead node shows as `DN` (Down/Normal):

```
Datacenter: dc1
===============
Status=Up/Down
|/ State=Normal/Leaving/Joining/Moving
--  Address       Load       Tokens  Owns   Host ID                               Rack
UN  10.0.0.1     256.12 KiB  256     ?      550e8400-e29b-41d4-a716-446655440000  rack1
DN  10.0.0.2     267.89 KiB  256     ?      660e8400-e29b-41d4-a716-446655440001  rack1  <-- Dead node
UN  10.0.0.3     245.34 KiB  256     ?      770e8400-e29b-41d4-a716-446655440002  rack1
```

### 1.2 Record Dead Node Information

**Critical**: Note these values from the dead node:

```bash
# Get Host ID of dead node
nodetool status | grep DN
# Record: Host ID = 660e8400-e29b-41d4-a716-446655440001

# Get IP address
# Record: IP = 10.0.0.2
```

### 1.3 Check Hints

```bash
# Check if hints exist for the dead node
nodetool getendpoints my_keyspace my_table some_partition_key
```

---

## Step 2: Prepare Replacement Node

### 2.1 Install Cassandra

```bash
# On replacement node (10.0.0.4)
sudo apt-get update
sudo apt-get install cassandra
# OR
sudo yum install cassandra
```

### 2.2 Verify Version Match

```bash
# On replacement node
cassandra -v

# On existing node
nodetool version
```

**Both must match.**

### 2.3 Clear Data Directories

```bash
# On replacement node - ensure clean state
sudo rm -rf /var/lib/cassandra/data/*
sudo rm -rf /var/lib/cassandra/commitlog/*
sudo rm -rf /var/lib/cassandra/saved_caches/*
sudo rm -rf /var/lib/cassandra/hints/*
```

---

## Step 3: Configure Replacement Node

### 3.1 Edit cassandra.yaml

```bash
sudo vi /etc/cassandra/cassandra.yaml
```

**Critical settings** (must match cluster, except IPs):

```yaml
cluster_name: 'ProductionCluster'  # Must match exactly!

# Set to replacement node's IP
listen_address: 10.0.0.4
rpc_address: 10.0.0.4

# Same seeds as cluster (do not include dead node)
seed_provider:
  - class_name: org.apache.cassandra.locator.SimpleSeedProvider
    parameters:
      - seeds: "10.0.0.1,10.0.0.3"

# Same snitch as cluster
endpoint_snitch: GossipingPropertyFileSnitch
```

### 3.2 Configure Rack/DC

```bash
sudo vi /etc/cassandra/cassandra-rackdc.properties
```

```properties
dc=dc1        # Same as dead node
rack=rack1    # Same as dead node
```

### 3.3 Set JVM Options

Ensure JVM settings match other nodes in `jvm.options` or `jvm11-server.options`.

---

## Step 4: Start Replacement with Replace Flag

### 4.1 Set Replace Address

**Option A**: Set in JVM options file

```bash
sudo vi /etc/cassandra/jvm-server.options
# Add this line:
-Dcassandra.replace_address_first_boot=10.0.0.2
```

**Option B**: Set via environment variable

```bash
export JVM_OPTS="$JVM_OPTS -Dcassandra.replace_address_first_boot=10.0.0.2"
```

### 4.2 Start Cassandra

```bash
sudo systemctl start cassandra
```

### 4.3 Monitor Bootstrap Progress

```bash
# Watch the logs
tail -f /var/log/cassandra/system.log

# Check progress
nodetool netstats

# On another node, check status
nodetool status
```

**Expected log messages**:

```
INFO  [main] StorageService.java - Replacing a node with token(s): [-9223372036854775808, ...]
INFO  [main] StorageService.java - Nodes [/10.0.0.2] are marked dead
INFO  [main] Gossiper.java - Replacing /10.0.0.2 with /10.0.0.4
```

---

## Step 5: Verify Replacement

### 5.1 Check Node Status

```bash
nodetool status
```

**Expected**: New node shows as `UN`:

```
Datacenter: dc1
===============
UN  10.0.0.1     256.12 KiB  256     33.3%  550e8400-e29b-41d4-a716-446655440000  rack1
UN  10.0.0.4     267.89 KiB  256     33.3%  880e8400-e29b-41d4-a716-446655440003  rack1  <-- New node
UN  10.0.0.3     245.34 KiB  256     33.4%  770e8400-e29b-41d4-a716-446655440002  rack1
```

**Note**: Dead node (10.0.0.2) is no longer listed.

### 5.2 Verify Data Streaming Complete

```bash
# On new node
nodetool netstats
```

**Expected**: No active streams:

```
Mode: NORMAL
Not sending any streams.
Not receiving any streams.
```

### 5.3 Check Gossip Info

```bash
nodetool gossipinfo
```

Verify new node appears with correct STATUS=NORMAL.

---

## Step 6: Post-Replacement Cleanup

### 6.1 Remove Replace Flag

**Important**: Remove the replace flag to prevent issues on restart.

```bash
sudo vi /etc/cassandra/jvm-server.options
# Remove or comment out:
# -Dcassandra.replace_address_first_boot=10.0.0.2
```

### 6.2 Run Repair on New Node

```bash
# Run repair to ensure data consistency
nodetool repair -pr
```

### 6.3 Update Seed List (if applicable)

If the dead node was a seed, update all nodes:

```bash
# On all nodes
sudo vi /etc/cassandra/cassandra.yaml
# Update seeds list to exclude dead node, include new node if desired
```

### 6.4 Update Monitoring/Alerting

- Update monitoring to track new node IP
- Remove dead node from monitoring
- Update documentation

---

## Troubleshooting

### Bootstrap Hangs

**Symptom**: Node stuck in `UJ` (Up/Joining) state.

```bash
# Check progress
nodetool netstats

# Check for errors
tail -100 /var/log/cassandra/system.log | grep -i error
```

**Solutions**:
- Wait (large datasets take time)
- Check network connectivity to other nodes
- Check disk space on new node

### Node Shows Wrong Tokens

**Symptom**: Token distribution uneven after replace.

```bash
# Check token distribution
nodetool ring
```

**Solution**: Run repair, then consider running `nodetool cleanup` on other nodes.

### Streaming Failures

**Symptom**: "Streaming error" in logs.

```bash
grep -i "stream" /var/log/cassandra/system.log | tail -50
```

**Solutions**:
- Check network connectivity
- Increase streaming timeout
- Restart bootstrap (clear data, try again)

### Old Node Reappears

**Symptom**: Dead node shows up again after replacement.

```bash
# Remove via assassinate (use with caution)
nodetool assassinate 10.0.0.2
```

---

## Rollback Procedure

If replacement fails and recovery is needed:

1. **Stop the replacement node**:
   ```bash
   sudo systemctl stop cassandra
   ```

2. **If original node can be recovered**, bring it back:
   ```bash
   # On original node
   sudo systemctl start cassandra
   ```

3. **Clear replacement node data**:
   ```bash
   sudo rm -rf /var/lib/cassandra/data/*
   ```

4. **Run repair on recovered node**:
   ```bash
   nodetool repair
   ```

---

## Checklist Summary

- [ ] Confirmed node is dead (DN status)
- [ ] Recorded dead node Host ID and IP
- [ ] Prepared replacement node hardware
- [ ] Installed matching Cassandra version
- [ ] Configured cassandra.yaml with replace flag
- [ ] Configured rack/DC properties
- [ ] Started node and monitored bootstrap
- [ ] Verified UN status and data streaming complete
- [ ] Removed replace flag from configuration
- [ ] Ran repair on new node
- [ ] Updated seed list if needed
- [ ] Updated monitoring and documentation

---

## Related Playbooks

- **[Decommission Node](decommission-node.md)**
- **[Add Node](add-node.md)**
- **[Recover from OOM](recover-from-oom.md)**
- **[Handle Full Disk](handle-full-disk.md)**
