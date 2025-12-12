# Gossip Failures

Gossip is Cassandra's peer-to-peer protocol for sharing cluster state. Gossip failures cause nodes to lose visibility of each other, leading to cluster partitions and availability issues.

---

## Symptoms

- Nodes showing as DOWN (DN) in `nodetool status` despite being running
- `nodetool gossipinfo` shows stale or missing entries
- "Unable to gossip with" errors in logs
- New nodes failing to join cluster
- Inconsistent cluster views across nodes
- Schema disagreement

---

## Diagnosis

### Step 1: Check Node Status

```bash
# On multiple nodes - compare output
nodetool status
```

Different views from different nodes indicate gossip issues.

### Step 2: Check Gossip State

```bash
nodetool gossipinfo
```

**Key fields to check:**
- `STATUS`: Should be NORMAL for healthy nodes
- `HEARTBEAT`: Should be recent (incrementing)
- `GENERATION`: Timestamp of last restart

### Step 3: Check Gossip Service

```bash
nodetool statusgossip
```

Should return `running`. If `not running`, gossip is disabled.

### Step 4: Check Network Connectivity

```bash
# Gossip uses port 7000 (or 7001 for SSL)
for node in node1 node2 node3; do
    nc -zv $node 7000 && echo "$node gossip: OK" || echo "$node gossip: FAILED"
done

# Check internode communication
for node in node1 node2 node3; do
    nc -zv $node 7000
    nc -zv $node 9042
done
```

### Step 5: Check Logs

```bash
grep -i "gossip\|cannot reach\|connection refused" /var/log/cassandra/system.log | tail -50
```

### Step 6: Check Seeds Configuration

```bash
grep seeds /etc/cassandra/cassandra.yaml
```

Ensure seeds are reachable and consistent across cluster.

---

## Resolution

### Case 1: Network Issues

**Problem:** Firewall blocking gossip port

```bash
# Check firewall
sudo iptables -L -n | grep 7000

# Open gossip port
sudo iptables -A INPUT -p tcp --dport 7000 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 7001 -j ACCEPT  # SSL
```

**Problem:** DNS resolution failing

```bash
# Test DNS
nslookup node1.example.com

# Use IP addresses in cassandra.yaml if DNS unreliable
listen_address: 192.168.1.10
```

### Case 2: Gossip Disabled

```bash
# Check status
nodetool statusgossip

# Enable if disabled
nodetool enablegossip
```

### Case 3: Stale Gossip State

**Problem:** Node has outdated view of cluster

```bash
# Restart gossip (non-disruptive)
nodetool disablegossip
sleep 5
nodetool enablegossip
```

### Case 4: Corrupted Gossip State

**Problem:** Node persistently has wrong cluster view

```bash
# Rolling restart of affected node
nodetool drain
sudo systemctl restart cassandra
```

### Case 5: Zombie Node

**Problem:** Removed node still appearing in gossip

```bash
# Check for zombie entries
nodetool gossipinfo | grep -B5 "STATUS:LEFT\|STATUS:removed"

# Force remove if necessary (use carefully)
nodetool assassinate <zombie-node-ip>
```

!!! warning "Assassinate Warning"
    `nodetool assassinate` should only be used for nodes that have been properly decommissioned or are permanently dead. Using it on a live node can cause data loss.

### Case 6: Seed Node Issues

**Problem:** All seed nodes unreachable

1. Verify at least one seed is running and reachable
2. Ensure seeds are listed consistently across all nodes
3. Seeds should never include all nodes - typically 2-3 per datacenter

```yaml
# cassandra.yaml - good seed configuration
seed_provider:
  - class_name: org.apache.cassandra.locator.SimpleSeedProvider
    parameters:
      - seeds: "node1,node2"  # 2-3 seeds per DC
```

---

## Recovery

### Verify Gossip Health

```bash
# All nodes should see the same status
for node in node1 node2 node3; do
    echo "=== $node ==="
    nodetool -h $node status | head -10
done

# Gossip should show recent heartbeats
nodetool gossipinfo | grep HEARTBEAT
```

### Verify Schema Agreement

```bash
nodetool describecluster | grep -A 20 "Schema versions"
```

All nodes should show the same schema version.

---

## Common Causes

| Cause | Symptom | Fix |
|-------|---------|-----|
| Firewall | Connection refused | Open ports 7000/7001 |
| DNS issues | Cannot resolve hostname | Use IPs or fix DNS |
| Network partition | Partial cluster visibility | Fix network routing |
| Clock skew | Gossip timestamp errors | Sync with NTP |
| Bad seed config | Nodes can't find cluster | Fix seeds list |
| Resource exhaustion | Gossip timeouts | Add resources |

---

## Gossip Port Reference

| Port | Purpose | Protocol |
|------|---------|----------|
| 7000 | Internode gossip | TCP |
| 7001 | Internode gossip (SSL) | TCP |
| 7199 | JMX monitoring | TCP |
| 9042 | CQL native transport | TCP |

---

## Prevention

1. **Monitor gossip health** - Alert on nodes marked DOWN
2. **Use stable networking** - Avoid network configurations that cause partitions
3. **Sync clocks** - Use NTP across all nodes
4. **Consistent configuration** - Same seeds on all nodes
5. **Firewall rules** - Ensure gossip ports are always open
6. **Multiple seeds** - 2-3 per datacenter for redundancy

---

## Related Commands

| Command | Purpose |
|---------|---------|
| `nodetool status` | Cluster overview |
| `nodetool gossipinfo` | Detailed gossip state |
| `nodetool statusgossip` | Check if gossip is running |
| `nodetool enablegossip` | Enable gossip |
| `nodetool disablegossip` | Disable gossip |
| `nodetool assassinate` | Remove dead node from gossip |

## Related Documentation

- [Schema Disagreement](schema-disagreement.md) - Schema issues often caused by gossip problems
- [Configuration](../../operations/configuration/index.md) - Configuration including network setup
