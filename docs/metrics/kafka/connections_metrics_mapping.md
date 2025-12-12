---
description: "Kafka connections dashboard metrics mapping. Client connection statistics."
meta:
  - name: keywords
    content: "Kafka connections, client connections, connection metrics"
---

# AxonOps Kafka Connections Dashboard Metrics Mapping

## Overview

The Kafka Connections Dashboard provides comprehensive monitoring of client connections to Kafka brokers. It tracks connection counts, creation/close rates, client versions, and acceptor performance to help identify connection issues and optimize network resource usage.

## Metrics Mapping

| Dashboard Metric | Description | Attributes |
|-----------------|-----------|-------------|
| **Connection Metrics** | | | |
| `kaf_socket_server_metrics_` (function='connection_count') | Current number of active connections | listener={listener}, networkProcessor={id} |
| `kaf_socket_server_metrics_` (function='connection_creation_rate') | Rate of new connections created per second | listener={listener} |
| `kaf_socket_server_metrics_` (function='connection_close_rate') | Rate of connections closed per second | listener={listener} |
| `kaf_socket_server_metrics_` (function='connections') | Connections by client software version | listener={listener}, clientSoftwareName={name}, clientSoftwareVersion={version} |
| **Acceptor Metrics** | | | |
| `kaf_Acceptor_AcceptorBlockedPercent` | Percentage of time acceptor thread is blocked | listener={listener} |

## Query Examples

### Connection Count
```promql
// Total connections per broker
sum(kaf_socket_server_metrics_{function='connection_count',rack=~'$rack',host_id=~'$host_id'}) by (host_id)

// Total connections per listener
sum(kaf_socket_server_metrics_{function='connection_count',rack=~'$rack',host_id=~'$host_id'}) by (listener)
```

### Connection Creation Rate
```promql
// Connection creation rate per broker
sum(kaf_socket_server_metrics_{function='connection_creation_rate',rack=~'$rack',host_id=~'$host_id'}) by (host_id)

// Connection creation rate per listener
sum(kaf_socket_server_metrics_{function='connection_creation_rate',rack=~'$rack',host_id=~'$host_id'}) by (listener)
```

### Connection Close Rate
```promql
// Connection close rate per broker
sum(kaf_socket_server_metrics_{function='connection_close_rate',rack=~'$rack',host_id=~'$host_id'}) by (host_id)

// Connection close rate per listener
sum(kaf_socket_server_metrics_{function='connection_close_rate',rack=~'$rack',host_id=~'$host_id'}) by (listener)
```

### Client Version Distribution
```promql
// Connections grouped by client software and version
sum(kaf_socket_server_metrics_{function='connections',rack=~'$rack',host_id=~'$host_id'}) by (clientSoftwareVersion, clientSoftwareName)
```

### Acceptor Performance
```promql
// Acceptor blocked percentage
kaf_Acceptor_AcceptorBlockedPercent{function='MeanRate',rack=~'$rack',host_id=~'$host_id'}
```

## Panel Organization

**Overview Section**

   - Empty row for spacing/organization

**Connections**

   - Connections count per broker
   - Connections count per listener
   - Connections creation rate per broker
   - Connections creation rate per listener
   - Connections close rate per broker
   - Connections close rate per listener
   - Connections per client version
   - Acceptor Blocked Percentage

## Filters

- **rack**: Filter by rack location

- **host_id**: Filter by specific host/broker

## Best Practices

**Connection Monitoring**

   - Monitor total connection count against broker limits
   - Track connection creation/close rates for unusual patterns
   - High connection churn may indicate client issues

**Listener Analysis**

   - Monitor connections per listener (PLAINTEXT, SSL, SASL)
   - Different listeners may have different performance characteristics
   - Ensure balanced connection distribution across listeners

**Client Version Tracking**

   - Track client software versions for compatibility
   - Identify outdated clients that need upgrading
   - Monitor for unauthorized or unexpected client versions

**Acceptor Performance**

   - High acceptor blocked percentage indicates connection bottlenecks
   - May need to tune acceptor thread configuration
   - Consider increasing network threads if consistently blocked

**Connection Limits**

   - Set appropriate connection limits per broker
   - Monitor approaching connection limit thresholds
   - Plan capacity based on connection growth trends

**Security Considerations**

   - Monitor for connection spikes (potential DoS)
   - Track connections from unexpected sources
   - Ensure proper authentication/authorization on all listeners

**Performance Tuning**

   - Adjust `max.connections.per.ip` for client fairness
   - Tune `num.network.threads` based on connection load
   - Monitor connection creation rate during peak times