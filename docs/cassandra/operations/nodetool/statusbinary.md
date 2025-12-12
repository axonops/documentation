# nodetool statusbinary

Displays the status of the CQL native transport (client protocol).

---

## Synopsis

```bash
nodetool [connection_options] statusbinary
```

---

## Description

`nodetool statusbinary` shows whether the CQL native transport is currently running or stopped. The native transport is the protocol that handles all CQL client connections—it's how applications communicate with Cassandra using CQL drivers on port 9042 (by default).

!!! info "What Is the Native Transport?"
    The native transport (also called "binary protocol" or "CQL protocol") is Cassandra's client communication layer. When enabled, the node listens for CQL connections and can serve as a coordinator for client requests. When disabled, clients cannot connect to this node, though it remains part of the cluster.

---

## What This Command Shows

### Output Values

| Output | Meaning |
|--------|---------|
| `running` | Native transport is active, accepting client connections |
| `not running` | Native transport is disabled, clients cannot connect |

### What "Running" Means

When the native transport is running:

```
┌─────────────────────────────────────────────────────────────┐
│                     Cassandra Node                          │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │           Native Transport (Port 9042)              │   │
│   │                    STATUS: RUNNING                  │   │
│   └─────────────────────────────────────────────────────┘   │
│              ▲           ▲           ▲                      │
│              │           │           │                      │
│         ┌────┴───┐  ┌────┴───┐  ┌────┴───┐                  │
│         │ Client │  │ Client │  │ cqlsh  │                  │
│         │ Driver │  │ Driver │  │        │                  │
│         └────────┘  └────────┘  └────────┘                  │
└─────────────────────────────────────────────────────────────┘

Node can:
✓ Accept new CQL connections
✓ Serve as coordinator for queries
✓ Return query results to clients
✓ Send schema/topology change events
```

### What "Not Running" Means

When the native transport is not running:

```
┌─────────────────────────────────────────────────────────────┐
│                     Cassandra Node                          │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │           Native Transport (Port 9042)              │   │
│   │                  STATUS: NOT RUNNING                │   │
│   │                     ╳ CLOSED ╳                      │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
│         ╳ Clients cannot connect ╳                          │
│                                                             │
│   But node still:                                           │
│   ✓ Participates in gossip                                  │
│   ✓ Receives replicated writes                              │
│   ✓ Serves as replica for reads from other coordinators     │
│   ✓ Shows as UP in nodetool status                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Examples

### Basic Usage

```bash
nodetool statusbinary
```

**Sample output when running:**
```
running
```

**Sample output when not running:**
```
not running
```

### Check Remote Node

```bash
nodetool -h 192.168.1.100 statusbinary
```

### Use in Conditional Scripts

```bash
#!/bin/bash
if [ "$(nodetool statusbinary)" = "running" ]; then
    echo "CQL is accepting connections"
else
    echo "CQL is disabled - clients cannot connect"
fi
```

### Check All Nodes in Cluster

```bash
#!/bin/bash
# check_binary_cluster.sh

echo "=== Native Transport Status Across Cluster ==="

nodes=$(nodetool status | grep "^UN\|^DN" | awk '{print $2}')

for node in $nodes; do
    status=$(nodetool -h $node statusbinary 2>/dev/null || echo "UNREACHABLE")
    echo "$node: $status"
done
```

**Sample output:**
```
=== Native Transport Status Across Cluster ===
192.168.1.101: running
192.168.1.102: running
192.168.1.103: not running    <-- This node won't accept clients
```

---

## Is the Status Persistent?

!!! warning "Non-Persistent Setting"
    The binary transport status is **NOT persistent across restarts** in the way you might expect:

| Scenario | Behavior |
|----------|----------|
| Node restart | Binary transport starts based on `start_native_transport` in cassandra.yaml |
| `disablebinary` then restart | Binary transport will be **running** again (default: auto-start) |
| `enablebinary` then restart | Binary transport will still be running (was already the default) |

### Default Startup Behavior

```yaml
# cassandra.yaml
start_native_transport: true   # Default - binary starts automatically
```

The runtime state (enabled/disabled via nodetool) is lost on restart. The node always starts based on cassandra.yaml configuration.

### Making a Disabled State Persistent

To permanently prevent binary transport from starting:

```yaml
# cassandra.yaml
start_native_transport: false
```

This is rarely used—typically only for special coordinator-less nodes.

---

## When to Check This Status

### Health Checks

Include in monitoring and health check scripts:

```bash
#!/bin/bash
# cassandra_health.sh

binary=$(nodetool statusbinary)
gossip=$(nodetool statusgossip)
status=$(nodetool status | grep "$(hostname -i)" | awk '{print $1}')

echo "Node Status: $status"
echo "Gossip: $gossip"
echo "Binary (CQL): $binary"

if [ "$binary" = "running" ] && [ "$gossip" = "running" ] && [ "$status" = "UN" ]; then
    echo "HEALTHY: Node fully operational"
    exit 0
else
    echo "WARNING: Node has issues"
    exit 1
fi
```

### Pre-Maintenance Verification

Before starting maintenance:

```bash
# Document current state
echo "Pre-maintenance state:"
echo "  Binary: $(nodetool statusbinary)"
echo "  Gossip: $(nodetool statusgossip)"
echo "  Connections: $(netstat -an | grep 9042 | grep ESTABLISHED | wc -l)"
```

### Post-Maintenance Verification

After completing maintenance:

```bash
#!/bin/bash
# verify_node_ready.sh

echo "Verifying node is ready for traffic..."

# Check binary is running
if [ "$(nodetool statusbinary)" != "running" ]; then
    echo "ERROR: Binary transport not running"
    echo "Run: nodetool enablebinary"
    exit 1
fi

# Test CQL connectivity
if ! cqlsh localhost -e "SELECT now() FROM system.local" >/dev/null 2>&1; then
    echo "ERROR: CQL connection test failed"
    exit 1
fi

echo "OK: Node is ready for client traffic"
```

### Troubleshooting Client Connectivity

When clients report connection failures:

```bash
#!/bin/bash
# diagnose_connectivity.sh

echo "=== Cassandra Connectivity Diagnosis ==="

# 1. Check binary status
echo ""
echo "1. Binary Transport Status:"
nodetool statusbinary

# 2. Check port listening
echo ""
echo "2. Port 9042 Listening:"
netstat -tlnp | grep 9042 || echo "   NOT LISTENING"

# 3. Check gossip (needed for proper operation)
echo ""
echo "3. Gossip Status:"
nodetool statusgossip

# 4. Check cluster membership
echo ""
echo "4. Node Status in Cluster:"
nodetool status | grep "$(hostname -i)"

# 5. Check for errors
echo ""
echo "5. Recent Native Transport Errors:"
grep -i "native\|binary" /var/log/cassandra/system.log | tail -5
```

---

## Common Reasons for "Not Running"

### 1. Intentionally Disabled for Maintenance

```bash
# Check if someone disabled it
nodetool statusbinary
# Output: not running

# Re-enable when maintenance is complete
nodetool enablebinary
```

### 2. Node Just Started

During startup, there's a brief window before binary is ready:

```bash
# Wait for node to fully start
sleep 30
nodetool statusbinary
```

### 3. Startup Configuration

Check if binary is configured to auto-start:

```bash
grep start_native_transport /etc/cassandra/cassandra.yaml
```

If `start_native_transport: false`, binary won't start automatically.

### 4. Port Conflict

Another process might be using port 9042:

```bash
# Check what's using the port
lsof -i :9042
netstat -tlnp | grep 9042
```

### 5. SSL/TLS Configuration Issues

If client encryption is misconfigured:

```bash
# Check SSL configuration
grep -A 10 "client_encryption_options" /etc/cassandra/cassandra.yaml

# Check for SSL-related errors
grep -i "ssl\|tls\|encrypt" /var/log/cassandra/system.log | tail -10
```

### 6. Address Binding Issues

If the node can't bind to the configured address:

```bash
# Check configured listen address
grep -E "listen_address|rpc_address" /etc/cassandra/cassandra.yaml

# Check for binding errors
grep -i "bind\|address" /var/log/cassandra/system.log | tail -5
```

---

## Relationship to Other Commands

### Binary vs Gossip

| Command | What It Controls | Impact When Disabled |
|---------|------------------|---------------------|
| `statusbinary` | Client connections | Clients can't connect |
| `statusgossip` | Cluster communication | Node isolated from cluster |

A healthy node typically has both running:

```bash
echo "Binary: $(nodetool statusbinary)"
echo "Gossip: $(nodetool statusgossip)"
# Both should show "running"
```

### Complete Node Status Check

```bash
#!/bin/bash
# full_node_status.sh

echo "=== Complete Node Status ==="
echo ""
echo "Cluster membership:"
nodetool status | grep -E "^UN|^DN|Address"
echo ""
echo "Binary (CQL clients): $(nodetool statusbinary)"
echo "Gossip (cluster comm): $(nodetool statusgossip)"
echo "Thrift (legacy):       $(nodetool statusthrift 2>/dev/null || echo 'N/A')"
echo ""
echo "Active connections:"
echo "  CQL (9042): $(netstat -an | grep ':9042.*ESTABLISHED' | wc -l)"
echo "  Internode:  $(netstat -an | grep ':7000.*ESTABLISHED' | wc -l)"
```

---

## Configuration Reference

### cassandra.yaml Settings

```yaml
# Whether to start native transport on node boot
start_native_transport: true

# Port for CQL connections
native_transport_port: 9042

# Port for SSL CQL connections (if enabled)
native_transport_port_ssl: 9142

# Maximum threads for handling CQL requests
native_transport_max_threads: 128

# Maximum frame size for CQL messages
native_transport_max_frame_size_in_mb: 256

# Allow older protocol versions
native_transport_allow_older_protocols: true
```

### Verifying Port Configuration

```bash
# Check configured port
grep native_transport_port /etc/cassandra/cassandra.yaml

# Check if port is listening
netstat -tlnp | grep $(grep native_transport_port /etc/cassandra/cassandra.yaml | awk '{print $2}')
```

---

## Monitoring and Alerting

### Prometheus/Metrics Integration

If using JMX metrics:

```bash
# JMX MBean for native transport status
# org.apache.cassandra.transport:type=NativeTransport
# Attribute: Running
```

### Health Check Endpoint Script

```bash
#!/bin/bash
# health_endpoint.sh - Returns HTTP-style status codes

binary=$(nodetool statusbinary 2>/dev/null)
gossip=$(nodetool statusgossip 2>/dev/null)

if [ "$binary" = "running" ] && [ "$gossip" = "running" ]; then
    echo "200 OK"
    exit 0
elif [ "$binary" = "not running" ]; then
    echo "503 Service Unavailable - Binary disabled"
    exit 1
else
    echo "500 Internal Server Error - Cannot determine status"
    exit 2
fi
```

### Alerting Rules

Example alert conditions:

| Condition | Severity | Action |
|-----------|----------|--------|
| Binary not running (unplanned) | Critical | Investigate immediately |
| Binary not running > 5 min | Warning | Check maintenance status |
| Binary running but no connections | Info | May be normal during low traffic |

---

## Troubleshooting

### Binary Shows "Running" But Clients Can't Connect

```bash
# 1. Verify port is actually listening
netstat -tlnp | grep 9042

# 2. Check firewall rules
iptables -L -n | grep 9042

# 3. Check listen address
grep rpc_address /etc/cassandra/cassandra.yaml
# If set to localhost, only local connections work

# 4. Test local connection
cqlsh localhost 9042 -e "SELECT now() FROM system.local"
```

### Binary Shows "Not Running" After Restart

```bash
# Check if configured to auto-start
grep start_native_transport /etc/cassandra/cassandra.yaml

# Check for startup errors
grep -i "native\|binary\|9042" /var/log/cassandra/system.log | tail -20

# Enable manually if needed
nodetool enablebinary
```

### Binary Keeps Stopping

```bash
# Check for OOM or crashes
grep -i "error\|exception\|killed" /var/log/cassandra/system.log | tail -20

# Check system resources
free -m
df -h /var/lib/cassandra

# Monitor for issues
tail -f /var/log/cassandra/system.log | grep -i "native\|binary"
```

### Status Command Itself Fails

```bash
# If nodetool can't connect
nodetool info 2>&1 | head -5

# Check JMX connectivity
netstat -tlnp | grep 7199

# Check Cassandra process is running
pgrep -f CassandraDaemon
```

---

## Best Practices

!!! tip "Status Binary Guidelines"

    1. **Include in health checks** - Monitor binary status as part of node health
    2. **Check before maintenance** - Document state before making changes
    3. **Verify after maintenance** - Confirm binary is running when expected
    4. **Alert on unexpected stops** - Binary stopping unexpectedly is a critical issue
    5. **Check cluster-wide** - Verify all nodes have consistent status
    6. **Combine with gossip check** - Both should typically be running together

!!! warning "Important Considerations"

    - Status is **not persistent** - Returns to default on restart
    - "Running" doesn't guarantee connectivity - Port binding and firewall also matter
    - Check both binary AND gossip for full health picture
    - A node with binary disabled is still part of the cluster (receives replicated writes)

!!! info "When Binary Should Be "Not Running""

    It's normal and expected for binary to be "not running" when:

    - During planned maintenance window
    - Node is being drained before shutdown
    - Temporarily removed from client traffic for troubleshooting
    - Rolling restart in progress

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [enablebinary](enablebinary.md) | Enable CQL transport |
| [disablebinary](disablebinary.md) | Disable CQL transport |
| [statusgossip](statusgossip.md) | Check inter-node communication status |
| [enablegossip](enablegossip.md) | Enable cluster communication |
| [disablegossip](disablegossip.md) | Disable cluster communication |
| [status](status.md) | Overall cluster status |
| [info](info.md) | Node information |
| [drain](drain.md) | Graceful shutdown preparation |
