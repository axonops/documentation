---
description: "Disable CQL native transport (binary protocol) in Cassandra using nodetool disablebinary."
meta:
  - name: keywords
    content: "nodetool disablebinary, disable CQL, native transport, Cassandra protocol"
---

# nodetool disablebinary

Disables the CQL native transport, stopping the node from accepting new client connections.

---

## Synopsis

```bash
nodetool [connection_options] disablebinary
```

## Description

`nodetool disablebinary` disables the CQL native transport protocol, which handles all CQL client connections. Once disabled, the node stops listening on the native transport port, and existing connections are terminated.

### Native Transport Port Configuration

The native transport port is configured in `cassandra.yaml`:

```yaml
native_transport_port: 9042  # Default CQL port
```

To verify the current port and whether it is listening:

```bash
# Check if Cassandra is listening on the CQL port
netstat -tlnp | grep 9042

# Alternative using ss
ss -tlnp | grep 9042

# Check the configured port in cassandra.yaml
grep native_transport_port /etc/cassandra/cassandra.yaml
```

This command is commonly used for:

- **Controlled maintenance** - Stop new traffic before maintenance
- **Load shedding** - Remove node from client traffic during issues
- **Graceful node removal** - First step before gossip disable or drain
- **Rolling restarts** - Prevent traffic during restart procedure

!!! warning "Client Impact"
    Disabling binary causes clients to lose their connection to this node. Ensure CQL drivers are configured with multiple contact points so they can failover to other nodes.

---

## Behavior

When binary transport is disabled:

1. The node stops listening on the native transport port
2. New connection attempts are refused
3. Existing connections are terminated (may take a few seconds)
4. The node remains in the cluster and participates in gossip
5. The node can still receive replicated writes (as a replica, not coordinator)

---

## Examples

### Basic Usage

```bash
nodetool disablebinary
```

### Verify Disabled

```bash
nodetool disablebinary
nodetool statusbinary
# Expected output: not running
```

### Verify Port Closed

```bash
nodetool disablebinary
sleep 2
netstat -tlnp | grep 9042
# Should return nothing (port not listening)
```

---

## When to Use

### Pre-Maintenance

Stop client traffic before maintenance:

```bash
# Stop accepting new clients
nodetool disablebinary

# Wait for in-flight requests
sleep 10

# Perform maintenance...

# Restore client access
nodetool enablebinary
```

### Before Node Restart

Graceful traffic removal before restart:

```bash
# Remove from client traffic
nodetool disablebinary

# Wait for connections to drain
sleep 30

# Perform drain for graceful shutdown
nodetool drain

# Restart
systemctl restart cassandra
```

### Load Shedding

Temporarily remove an overloaded node from client traffic:

```bash
# Check current load
nodetool tpstats  # Look for backed up requests

# Remove from client traffic
nodetool disablebinary

# Address the issue...

# Restore
nodetool enablebinary
```

### Rolling Upgrade Procedure

```bash
# Step 1: Remove from client traffic
nodetool disablebinary
sleep 10

# Step 2: Wait for in-flight operations
nodetool tpstats  # Verify queues drain

# Step 3: Drain and stop
nodetool drain
systemctl stop cassandra

# Step 4: Perform upgrade...

# Step 5: Start Cassandra (binary auto-enables)
systemctl start cassandra

# Step 6: Verify
nodetool statusbinary  # Should be: running
```

### Controlled Node Isolation

For full isolation, disable binary first, then gossip:

```bash
# Step 1: Stop client traffic
nodetool disablebinary

# Step 2: Wait for requests to complete
sleep 15

# Step 3: Isolate from cluster
nodetool disablegossip
```

---

## What Happens to Existing Connections

When binary is disabled:

| Phase | Duration | Client Experience |
|-------|----------|-------------------|
| Immediate | 0-1 second | New connections refused |
| Short-term | 1-10 seconds | Existing queries may complete |
| Cleanup | 10-30 seconds | All connections terminated |

### Client Driver Behavior

Most CQL drivers handle this gracefully:

| Driver Feature | Behavior |
|----------------|----------|
| Connection pooling | Detects closed connections, removes from pool |
| Failover | Routes to other nodes automatically |
| Reconnection | Attempts reconnect per policy |
| Request retry | Retries on different coordinator |

---

## Order of Operations

### Graceful Maintenance Sequence

| Step | Command | Wait | Reason |
|------|---------|------|--------|
| 1 | `disablebinary` | 10-30s | Stop new client traffic |
| 2 | Wait | varies | Allow in-flight requests to complete |
| 3 | Maintenance | - | Perform the actual maintenance |
| 4 | `enablebinary` | 2s | Restore client access |
| 5 | Verify | - | Confirm clients can connect |

### Graceful Shutdown Sequence

| Step | Command | Wait | Reason |
|------|---------|------|--------|
| 1 | `disablebinary` | 10s | Stop clients |
| 2 | `drain` | varies | Flush data, stop gossip |
| 3 | Stop service | - | Shutdown process |

---

## Binary vs Gossip vs Drain

| Command | Binary | Gossip | Memtables | Use Case |
|---------|--------|--------|-----------|----------|
| `disablebinary` | Disabled | Running | In memory | Maintenance (stay in cluster) |
| `disablegossip` | Unchanged | Disabled | In memory | Network isolation |
| `drain` | Disabled | Disabled | Flushed | Graceful shutdown |

### Choosing the Right Command

| Scenario | Use |
|----------|-----|
| Quick maintenance, stay in cluster | `disablebinary` |
| Network debugging, isolation | `disablegossip` |
| Node restart or shutdown | `drain` |
| Full isolation before shutdown | `disablebinary` → `disablegossip` |

---

## Verification

### Command Verification

```bash
nodetool statusbinary
# Expected: not running
```

### Port Verification

```bash
# Port should not be listening
netstat -tlnp | grep 9042
# (no output expected)

ss -tlnp | grep 9042
# (no output expected)
```

### Connection Count

```bash
# Before disable - count connections
netstat -an | grep 9042 | grep ESTABLISHED | wc -l
# Output: 42

# After disable
nodetool disablebinary
sleep 5
netstat -an | grep 9042 | grep ESTABLISHED | wc -l
# Output: 0
```

---

## Impact Assessment

### On This Node

| Aspect | Impact |
|--------|--------|
| Client connections | Refused |
| Coordinator role | Cannot serve as coordinator |
| Replica role | Still receives writes from coordinators |
| Gossip | Still participating |
| Cluster membership | Still visible as UP |

### On Cluster

| Aspect | Impact |
|--------|--------|
| Client capacity | Reduced by one node |
| Coordinator load | Distributed to other nodes |
| Replication | Unchanged (node still receives replicas) |
| Consistency | Unchanged (if RF > 1) |

### On Clients

| Aspect | Impact |
|--------|--------|
| Active connections | Terminated |
| New connections | Refused, failover to other nodes |
| In-flight requests | May fail or retry |
| Request latency | May increase (fewer coordinators) |

---

## Monitoring

### Before Disabling

```bash
# Count current connections
netstat -an | grep 9042 | grep ESTABLISHED | wc -l

# Check for active requests
nodetool tpstats | grep -E "Native|Request"
```

### During Disable

```bash
# Watch connections drain
watch 'netstat -an | grep 9042 | wc -l'
```

### After Disabling

```bash
# Verify status
nodetool statusbinary

# Check other nodes absorbed traffic
nodetool -h other_node tpstats
```

---

## Troubleshooting

### Binary Won't Disable

If status still shows "running":

```bash
# Retry
nodetool disablebinary

# Check JMX connectivity
nodetool info

# Check logs
tail /var/log/cassandra/system.log | grep -i binary
```

### Connections Still Showing

If connections persist after disable:

```bash
# Check TIME_WAIT connections (normal)
netstat -an | grep 9042 | grep TIME_WAIT | wc -l

# These will clear automatically in ~60 seconds
```

### Clients Not Failing Over

If clients report errors instead of failing over:

```bash
# Check client driver configuration:
# - Multiple contact points configured?
# - Reconnection policy enabled?
# - Appropriate retry policy?

# Check other nodes are healthy
nodetool status
```

---

## Automation Script

```bash
#!/bin/bash
# disable_client_access.sh - Safely remove node from client traffic

echo "=== Current State ==="
echo "Binary: $(nodetool statusbinary)"
echo "Connections: $(netstat -an 2>/dev/null | grep 9042 | grep ESTABLISHED | wc -l)"

echo ""
echo "=== Disabling Binary Transport ==="

# Disable binary
nodetool disablebinary

# Wait for connections to drain
echo "Waiting for connections to drain..."
for i in {1..30}; do
    conns=$(netstat -an 2>/dev/null | grep 9042 | grep ESTABLISHED | wc -l)
    if [ "$conns" -eq 0 ]; then
        echo "All connections drained"
        break
    fi
    echo "  Remaining connections: $conns"
    sleep 1
done

# Verify
echo ""
echo "=== Verification ==="
echo "Binary: $(nodetool statusbinary)"
echo "Connections: $(netstat -an 2>/dev/null | grep 9042 | grep ESTABLISHED | wc -l)"

# Check node still in cluster
echo ""
echo "=== Cluster Status ==="
nodetool status | head -10

echo ""
echo "Node removed from client traffic but still in cluster."
echo "To restore: nodetool enablebinary"
```

---

## Wait Time Recommendations

| Scenario | Recommended Wait After Disable |
|----------|-------------------------------|
| Quick config change | 5-10 seconds |
| Rolling restart | 30-60 seconds |
| Before drain | 10-30 seconds |
| Heavy load node | 60-120 seconds |

### Calculating Wait Time

```bash
# Check current request rate
nodetool proxyhistograms | head -5

# General rule: wait until tpstats shows minimal pending
nodetool tpstats | grep -E "Native|Read|Write"
# Wait until "Pending" columns are near zero
```

---

## Best Practices

!!! tip "Binary Disable Guidelines"

    1. **Monitor before disabling** - Know current connection count and load
    2. **Allow drain time** - Wait for in-flight requests to complete
    3. **Verify client failover** - Ensure clients connect to other nodes
    4. **Keep gossip running** - Node stays in cluster for replication
    5. **Document the action** - Note when and why binary was disabled
    6. **Set time limits** - Don't leave disabled indefinitely
    7. **Re-enable promptly** - Restore client access after maintenance

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [enablebinary](enablebinary.md) | Re-enable CQL transport |
| [statusbinary](statusbinary.md) | Check transport status |
| [disablegossip](disablegossip.md) | Disable gossip (further isolation) |
| [drain](drain.md) | Full graceful shutdown prep |
| [tpstats](tpstats.md) | Monitor request handling |
| [netstats](netstats.md) | Network/streaming statistics |
