# nodetool statusbinary

Displays the status of the CQL native transport.

---

## Synopsis

```bash
nodetool [connection_options] statusbinary
```

## Description

`nodetool statusbinary` shows whether the CQL native transport (client protocol) is running. This is the protocol used by CQL drivers to connect to Cassandra on port 9042 (by default).

---

## Output

### Running

```
running
```

The native transport is active and accepting client connections.

### Not Running

```
not running
```

The native transport is disabled. Clients cannot connect via CQL.

---

## Examples

### Check Status

```bash
nodetool statusbinary
```

### Use in Scripts

```bash
if [ "$(nodetool statusbinary)" = "running" ]; then
    echo "CQL is accepting connections"
else
    echo "CQL is disabled"
fi
```

---

## Use Cases

### Verify Node Accessibility

```bash
# Check if node can accept client traffic
nodetool statusbinary
```

### Pre-Maintenance Check

```bash
# Before maintenance, verify current state
nodetool statusbinary
# Should be: running

# Disable for maintenance
nodetool disablebinary

# After maintenance, re-enable
nodetool enablebinary

# Verify
nodetool statusbinary
# Should be: running
```

### Health Check Script

```bash
#!/bin/bash
# node_health.sh

BINARY=$(nodetool statusbinary)
GOSSIP=$(nodetool statusgossip)

echo "Binary (CQL): $BINARY"
echo "Gossip: $GOSSIP"

if [ "$BINARY" = "running" ] && [ "$GOSSIP" = "running" ]; then
    echo "Node is healthy"
    exit 0
else
    echo "Node has issues"
    exit 1
fi
```

---

## When Binary is Disabled

If `statusbinary` shows "not running":

### Intentional Disable

During maintenance, the binary transport may be intentionally disabled:

```bash
# Re-enable if maintenance is complete
nodetool enablebinary
```

### After Node Restart

Binary should automatically start on node startup. If not:

1. Check logs for startup errors
2. Verify `native_transport_port` configuration
3. Check for port conflicts

### Troubleshooting

```bash
# Check if port is in use
netstat -tlnp | grep 9042

# Check Cassandra logs
tail -100 /var/log/cassandra/system.log | grep -i "native\|binary"
```

---

## Related Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `start_native_transport` | true | Auto-start on node boot |
| `native_transport_port` | 9042 | CQL port |
| `native_transport_max_threads` | 128 | Max client threads |

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [enablebinary](enablebinary.md) | Enable CQL transport |
| [disablebinary](disablebinary.md) | Disable CQL transport |
| [statusgossip](statusgossip.md) | Check gossip status |
| [status](status.md) | Overall node status |
