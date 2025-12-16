---
title: "nodetool disableoldprotocolversions"
description: "Disable old CQL protocol versions in Cassandra using nodetool disableoldprotocolversions."
meta:
  - name: keywords
    content: "nodetool disableoldprotocolversions, CQL protocol, protocol versions, Cassandra"
---

# nodetool disableoldprotocolversions

Disables support for older CQL native protocol versions, requiring clients to use modern protocol versions.

---

## Synopsis

```bash
nodetool [connection_options] disableoldprotocolversions
```

## Description

`nodetool disableoldprotocolversions` disables support for older CQL native protocol versions on the node. When executed, clients using protocol versions older than the current default will be rejected, requiring them to upgrade to a supported version.

### CQL Native Protocol Versions

The CQL native protocol has evolved through several versions, each adding features and improvements:

| Protocol Version | Cassandra Version | Key Features |
|------------------|-------------------|--------------|
| V3 | 2.1+ | User-defined types, tuples, pagination |
| V4 | 2.2+ | Custom payloads, warnings, timestamps |
| V5 | 4.0+ | Improved metadata, duration type, per-query keyspace |
| V6 | 5.0+ | Tablets, vector type support |

When old protocol versions are disabled, typically V3 and V4 are blocked, requiring clients to use V5 or later.

!!! warning "Non-Persistent Setting"
    This setting is applied at runtime only and does not persist across node restarts. After a restart, support for older protocol versions is re-enabled by default.

    To permanently disable old protocol versions, configure the `native_transport_allow_older_protocols` setting in `cassandra.yaml`:

    ```yaml
    native_transport_allow_older_protocols: false
    ```

---

## Behavior

When old protocol versions are disabled:

1. New client connections using old protocol versions are rejected
2. Existing connections using old protocols may continue until disconnected
3. Clients receive a protocol error indicating the version is not supported
4. Clients configured with protocol negotiation will attempt to use a newer version

### What Gets Blocked

| Client Action | Result |
|---------------|--------|
| New connection with V3 | Rejected |
| New connection with V4 | Rejected (typically) |
| New connection with V5+ | Accepted |
| Existing V3/V4 connection | May continue until disconnect |

### Client Error Messages

Clients attempting to connect with old protocol versions will see errors similar to:

```
Protocol version V3 is not supported by this server
```

Or driver-specific errors like:

```
com.datastax.driver.core.exceptions.UnsupportedProtocolVersionException:
Host /192.168.1.100:9042 does not support protocol version V3
```

---

## Arguments

This command takes no arguments.

---

## Examples

### Basic Usage

```bash
nodetool disableoldprotocolversions
```

### Verify Current Protocol Support

```bash
# Check which clients are connected with which protocol versions
nodetool clientstats
```

### With Client Verification First

```bash
# 1. Check current client protocol versions
nodetool clientstats | grep -i protocol

# 2. If all clients support V5+, disable old versions
nodetool disableoldprotocolversions

# 3. Monitor for connection errors
tail -f /var/log/cassandra/system.log | grep -i protocol
```

---

## When to Use

### Security Hardening

Older protocol versions may have security limitations. Disabling them enforces use of protocols with better security features:

```bash
# Part of security hardening procedure
nodetool disableoldprotocolversions
```

### After Client Driver Upgrades

Once all application clients have been upgraded to use modern drivers:

```bash
# Verify all clients use V5+
nodetool clientstats

# Disable old versions
nodetool disableoldprotocolversions
```

### Compliance Requirements

Some security standards require disabling legacy protocols:

```bash
# For PCI-DSS, SOC2, or internal security policies
nodetool disableoldprotocolversions
```

### Feature Enforcement

To ensure clients use features only available in newer protocols:

```bash
# Require V5+ for duration type support, per-query keyspace, etc.
nodetool disableoldprotocolversions
```

---

## When NOT to Use

### Legacy Clients Still in Use

!!! danger "Client Compatibility"
    Do not disable old protocol versions if any clients require them:

    - Legacy application drivers that cannot be upgraded
    - Third-party tools using older protocol versions
    - ETL processes with outdated Cassandra drivers

    Disabling will cause these clients to fail immediately.

### During Rolling Upgrades

Avoid changing protocol settings during cluster or client upgrades:

```bash
# Wait until all clients are confirmed upgraded
# Then disable old versions
```

### Without Testing

Always test in non-production first to identify affected clients.

---

## Pre-Requisites

### Verify Client Protocol Versions

Before disabling, audit all connected clients:

```bash
# List all client connections and their protocol versions
nodetool clientstats
```

Example output:

```
Address          SSL   Protocol   User     Keyspace   Requests
192.168.1.50     true  V5         app_user my_ks      15234
192.168.1.51     true  V5         app_user my_ks      12456
192.168.1.52     false V4         etl_user analytics  3421   # <-- Old version!
```

### Identify V3/V4 Clients

```bash
# Find clients using old protocols
nodetool clientstats | grep -E "V3|V4"
```

### Check Driver Versions

Common drivers and their protocol support:

| Driver | Minimum Version for V5 |
|--------|----------------------|
| DataStax Java Driver | 4.0+ |
| DataStax Python Driver | 3.25+ |
| GoCQL | 1.0+ |
| DataStax C++ Driver | 2.15+ |
| DataStax Node.js Driver | 4.0+ |

---

## Impact Assessment

### Immediate Effects

| Aspect | Impact |
|--------|--------|
| New V3/V4 connections | Rejected |
| Existing V3/V4 connections | May continue temporarily |
| V5+ connections | Unaffected |
| Client errors | Immediate for blocked versions |

### Application Impact

| Scenario | Result |
|----------|--------|
| Modern driver (V5+) | No impact |
| Legacy driver (V3/V4) | Connection failures |
| Driver with negotiation | Falls back to newer version if supported |
| Mixed client environment | Some clients fail |

---

## Cluster-Wide Operations

### Disable on All Nodes

For complete enforcement, disable on all nodes:

```bash
#!/bin/bash
# disable_old_protocols_cluster.sh

echo "Disabling old protocol versions cluster-wide..."# Get list of node IPs from local nodetool status


nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo -n "$node: "
    ssh "$node" "nodetool disableoldprotocolversions 2>/dev/null && echo "disabled" || echo "FAILED""
done

echo ""
echo "Old protocol versions disabled on all nodes."
echo "Remember: This setting does not persist across restarts."
echo "Update cassandra.yaml to make permanent."
```

### Verify Cluster-Wide Status

```bash
#!/bin/bash
# check_protocol_status.sh

echo "Checking protocol version status across cluster..."# Get list of node IPs from local nodetool status


nodes=$(nodetool status | grep "^UN" | awk '{print $2}')

for node in $nodes; do
    echo "=== $node ==="
    ssh "$node" "nodetool clientstats 2>/dev/null | head -10"
    echo ""
done
```

---

## Rollback Procedure

If clients experience issues after disabling:

```bash
# Re-enable old protocol versions
nodetool enableoldprotocolversions

# Verify clients can connect
nodetool clientstats
```

---

## Monitoring

### Watch for Connection Errors

```bash
# Monitor logs for protocol errors
tail -f /var/log/cassandra/system.log | grep -i "protocol version"
```

### Track Client Connections

```bash
# Continuous monitoring of client protocols
watch -n 30 'nodetool clientstats | grep -E "Protocol|V[0-9]"'
```

### Alert on Legacy Protocols

```bash
#!/bin/bash
# alert_old_protocols.sh

old_clients=$(nodetool clientstats 2>/dev/null | grep -cE "V3|V4")

if [ "$old_clients" -gt 0 ]; then
    echo "WARNING: $old_clients clients using old protocol versions"
    nodetool clientstats | grep -E "V3|V4"
fi
```

---

## Troubleshooting

### Clients Cannot Connect After Disable

```bash
# 1. Check if old protocols are the issue
nodetool enableoldprotocolversions

# 2. Verify client can connect
nodetool clientstats | grep <client_ip>

# 3. Identify protocol version
nodetool clientstats | grep <client_ip> | awk '{print $3}'

# 4. Upgrade client driver if using old protocol
```

### Cannot Identify Which Clients Use Old Protocols

```bash
# Get detailed client information
nodetool clientstats

# Cross-reference with application deployment records
# Check load balancer logs for source IPs
```

### Command Has No Effect

```bash
# Verify command executed
nodetool clientstats

# Check if already disabled
# Try on specific node
ssh <node_ip> "nodetool disableoldprotocolversions"

# Check JMX connectivity
nodetool info
```

---

## Migration Strategy

### Phased Approach

1. **Audit Phase**
   ```bash
   # Document all clients and their protocol versions
   nodetool clientstats > client_audit_$(date +%Y%m%d).txt
   ```

2. **Notification Phase**
   - Identify owners of legacy clients
   - Set upgrade deadline
   - Provide driver upgrade guidance

3. **Testing Phase**
   ```bash
   # Test in non-production
   nodetool disableoldprotocolversions
   # Run integration tests
   ```

4. **Production Phase**
   ```bash
   # Disable during maintenance window
   nodetool disableoldprotocolversions
   # Monitor for issues
   ```

5. **Persistence Phase**
   ```yaml
   # Update cassandra.yaml
   native_transport_allow_older_protocols: false
   ```

---

## Best Practices

!!! tip "Guidelines"

    1. **Audit first** - Identify all clients before disabling
    2. **Communicate** - Notify application teams of the change
    3. **Test thoroughly** - Validate in non-production environments
    4. **Phase the rollout** - Consider node-by-node or DC-by-DC
    5. **Monitor actively** - Watch for connection failures
    6. **Have rollback ready** - Know how to re-enable quickly
    7. **Make persistent** - Update `cassandra.yaml` after validation
    8. **Document** - Record which clients were upgraded and when

!!! danger "Avoid"

    - Disabling without client audit
    - Disabling during peak traffic
    - Forgetting to make the change persistent
    - Ignoring client upgrade requirements

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [enableoldprotocolversions](enableoldprotocolversions.md) | Re-enable old protocol versions |
| [clientstats](clientstats.md) | View client connections and protocol versions |
| [status](status.md) | Check cluster health |
