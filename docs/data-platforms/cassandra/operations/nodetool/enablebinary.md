---
title: "nodetool enablebinary"
description: "Enable CQL native transport (binary protocol) in Cassandra using nodetool enablebinary."
meta:
  - name: keywords
    content: "nodetool enablebinary, enable CQL, native transport, Cassandra protocol"
search:
  boost: 3
---

# nodetool enablebinary

Enables the CQL native transport, allowing client connections.

---

## Synopsis

```bash
nodetool [connection_options] enablebinary
```

## Description

`nodetool enablebinary` enables the CQL native transport protocol, which handles all CQL client connections. When enabled, the node accepts connections on the native transport port (default: 9042) from CQL drivers and tools like `cqlsh`.

The native transport is Cassandra's primary client interface, supporting:

- **CQL queries** - SELECT, INSERT, UPDATE, DELETE operations
- **Prepared statements** - Pre-compiled queries for performance
- **Batch operations** - Atomic multi-statement execution
- **Streaming results** - Pagination for large result sets
- **Event notifications** - Schema change and topology events

---

## Behavior

When the native transport is enabled:

1. Cassandra begins listening on the configured native transport port
2. New client connections are accepted
3. The node can serve as a coordinator for CQL requests
4. Event listeners receive topology and schema notifications

!!! info "Connection Handling"
    Existing connections established before a disable/enable cycle may need to reconnect. Most CQL drivers handle this automatically through their connection pooling logic.

---

## Examples

### Basic Usage

```bash
nodetool enablebinary
```

### Verify Enabled

```bash
nodetool enablebinary
nodetool statusbinary
# Expected output: running
```

### Test Client Connectivity

```bash
# Enable binary
nodetool enablebinary

# Verify with cqlsh
cqlsh localhost 9042 -e "SELECT now() FROM system.local"
```

---

## When to Use

### After Maintenance

Re-enable client connections after maintenance:

```bash
# Maintenance complete
nodetool enablebinary

# Verify
nodetool statusbinary
```

### Recovery from Accidental Disable

If binary was accidentally disabled:

```bash
# Check status
nodetool statusbinary
# Output: not running

# Enable immediately
nodetool enablebinary

# Verify clients can connect
cqlsh localhost
```

### After Node Restart Issues

If binary transport failed to start automatically:

```bash
# Check current state
nodetool statusbinary

# Enable if not running
nodetool enablebinary

# Check logs if it fails
tail -100 /var/log/cassandra/system.log | grep -i native
```

### Controlled Traffic Restoration

Restore client traffic after a controlled outage:

```bash
# Verify cluster state first
nodetool status

# Enable binary to accept traffic
nodetool enablebinary

# Monitor for issues
watch nodetool tpstats
```

---

## Workflow: Complete Node Recovery

After full node isolation, restore in the correct order:

```bash
# 1. Check current state
nodetool statusgossip  # Verify gossip is running
nodetool statusbinary  # Verify binary is not running

# 2. Ensure gossip is running first
if [ "$(nodetool statusgossip)" != "running" ]; then
    nodetool enablegossip
    sleep 5  # Wait for cluster sync
fi

# 3. Verify node is seen as UP by cluster
nodetool status | grep $(hostname -i)
# Should show "UN" (Up/Normal)

# 4. Enable binary transport
nodetool enablebinary

# 5. Verify operational
nodetool statusbinary  # running

# 6. Test client connectivity
cqlsh localhost -e "SELECT * FROM system.local"
```

---

## Order of Operations

### Restoring a Node

Always follow this order when restoring from isolation:

| Step | Command | Reason |
|------|---------|--------|
| 1 | `enablegossip` | Node must be in cluster first |
| 2 | Wait 5-10 seconds | Allow cluster state sync |
| 3 | `enablebinary` | Now safe to accept clients |

!!! warning "Enable Gossip First"
    Never enable binary while gossip is disabled. The node would accept requests but cannot coordinate properly with other nodes, leading to potential consistency issues.

### Isolating a Node

The reverse order for isolation:

| Step | Command | Reason |
|------|---------|--------|
| 1 | `disablebinary` | Stop new client connections |
| 2 | Wait for operations | Allow in-flight requests to complete |
| 3 | `disablegossip` | Then isolate from cluster |

---

## Port and Configuration

### Default Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `native_transport_port` | 9042 | Standard CQL port |
| `native_transport_port_ssl` | 9142 | SSL-enabled CQL port |
| `start_native_transport` | true | Auto-start on boot |
| `native_transport_max_threads` | 128 | Max client handler threads |
| `native_transport_max_frame_size_in_mb` | 256 | Max request size |

### Verifying Port Binding

```bash
# Check if port is listening
netstat -tlnp | grep 9042

# Or with ss
ss -tlnp | grep 9042
```

---

## Verification

### Command Verification

```bash
nodetool statusbinary
# Expected: running
```

### Port Verification

```bash
# Verify port is listening
netstat -tlnp | grep 9042
# tcp  0  0 0.0.0.0:9042  0.0.0.0:*  LISTEN  <pid>/java
```

### Client Connection Test

```bash
# Test with cqlsh
cqlsh localhost 9042 -e "DESCRIBE KEYSPACES"

# Test with simple query
cqlsh localhost -e "SELECT cluster_name FROM system.local"
```

### Driver Connection Test

```bash
# Python driver test
python3 -c "
from cassandra.cluster import Cluster
cluster = Cluster(['localhost'])
session = cluster.connect()
print('Connected:', session.execute('SELECT now() FROM system.local').one())
cluster.shutdown()
"
```

---

## Troubleshooting

### Binary Won't Enable

If `enablebinary` doesn't work:

```bash
# Check JMX connectivity
nodetool info

# Check logs for errors
tail -100 /var/log/cassandra/system.log | grep -i "native\|binary"

# Check for port conflicts
netstat -tlnp | grep 9042
```

### Port Already in Use

```bash
# Find process using port
lsof -i :9042

# Check if another Cassandra process is running
pgrep -f CassandraDaemon
```

### Connection Refused After Enable

If clients get connection refused:

```bash
# Verify status
nodetool statusbinary

# Check listening address
grep native_transport /etc/cassandra/cassandra.yaml

# Verify firewall allows connections
iptables -L -n | grep 9042
```

### SSL Configuration Issues

If using SSL and connections fail:

```bash
# Check SSL configuration in cassandra.yaml
grep -A20 client_encryption /etc/cassandra/cassandra.yaml

# Verify certificate files exist and are readable
ls -la /path/to/keystore.jks

# Check SSL port
netstat -tlnp | grep 9142
```

---

## Monitoring After Enable

### Watch Thread Pools

```bash
# Monitor for request handling
watch -n 2 'nodetool tpstats | head -20'
```

### Check Client Connections

```bash
# Count active connections
netstat -an | grep 9042 | grep ESTABLISHED | wc -l
```

### Monitor Latency

```bash
# Watch coordinator latencies
nodetool proxyhistograms
```

---

## Client Behavior

### Connection Pooling

Most CQL drivers maintain connection pools. After enabling binary:

- Existing pooled connections may be stale
- Drivers typically detect this and reconnect
- Some drivers may need explicit reconnection

### Retry Policies

Client retry policies determine behavior when binary is toggled:

| Policy | Behavior |
|--------|----------|
| Default | Retry on same/next coordinator |
| Fallthrough | Fail immediately |
| DowngradingConsistency | Retry with lower CL |

### Driver Reconnection

Most drivers handle reconnection automatically:

```python
# Python driver example - automatic reconnection
from cassandra.cluster import Cluster
from cassandra.policies import ConstantReconnectionPolicy

cluster = Cluster(
    ['node1', 'node2'],
    reconnection_policy=ConstantReconnectionPolicy(delay=5.0)
)
```

---

## Automation Script

```bash
#!/bin/bash
# enable_client_access.sh - Safely enable client access

echo "=== Pre-checks ==="

# Verify gossip is running
if [ "$(nodetool statusgossip)" != "running" ]; then
    echo "ERROR: Gossip not running. Enable gossip first."
    echo "Run: nodetool enablegossip"
    exit 1
fi

# Check node status in cluster
status=$(nodetool status | grep "$(hostname -i)" | awk '{print $1}')
if [ "$status" != "UN" ]; then
    echo "WARNING: Node status is '$status', expected 'UN'"
    echo "Wait for node to be fully recognized before enabling binary"
fi

echo ""
echo "=== Enabling Binary Transport ==="

# Enable binary
nodetool enablebinary

# Verify
sleep 2
if [ "$(nodetool statusbinary)" = "running" ]; then
    echo "Binary transport enabled successfully"
else
    echo "ERROR: Failed to enable binary transport"
    exit 1
fi

# Test connectivity
echo ""
echo "=== Testing Connectivity ==="
if cqlsh localhost -e "SELECT now() FROM system.local" 2>/dev/null; then
    echo "CQL connection test: PASSED"
else
    echo "CQL connection test: FAILED"
    echo "Check logs: tail /var/log/cassandra/system.log"
fi

echo ""
echo "=== Current State ==="
echo "Gossip: $(nodetool statusgossip)"
echo "Binary: $(nodetool statusbinary)"
echo "Port 9042: $(netstat -tlnp 2>/dev/null | grep 9042 | awk '{print $4}')"
```

---

## Best Practices

!!! tip "Binary Transport Guidelines"

    1. **Enable gossip first** - Always ensure cluster communication before client access
    2. **Verify before enabling** - Check node is healthy and in cluster
    3. **Test after enabling** - Verify clients can actually connect
    4. **Monitor thread pools** - Watch for request handling issues
    5. **Gradual traffic restoration** - Use load balancer to slowly add node back
    6. **Document in runbooks** - Include enable/disable in maintenance procedures

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [disablebinary](disablebinary.md) | Disable CQL transport |
| [statusbinary](statusbinary.md) | Check transport status |
| [enablegossip](enablegossip.md) | Enable gossip (do first) |
| [statusgossip](statusgossip.md) | Check gossip status |
| [tpstats](tpstats.md) | Monitor thread pools |
| [status](status.md) | Check cluster status |
