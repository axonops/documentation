# AxonOps Kafka ZooKeeper Dashboard Metrics Mapping

## Overview

The Kafka ZooKeeper Dashboard monitors the health and performance of ZooKeeper ensemble used by Kafka for cluster coordination (in non-KRaft mode). It tracks connections, request latency, node statistics, and session management to ensure ZooKeeper is functioning properly.

## Metrics Mapping

| Dashboard Metric | Description | Attributes |
|-----------------|-----------|-------------|
| **ZooKeeper Health Metrics** |
| `zk_NumAliveConnections` | Number of active client connections | port={port} |
| `zk_NodeCount` | Total number of znodes | port={port} |
| `zk_WatchCount` | Total number of watches | port={port} |
| `zk_OutstandingRequests` | Number of queued requests | port={port} |
| **Request Latency Metrics** |
| `zk_MinRequestLatency` | Minimum request latency | port={port} |
| `zk_AvgRequestLatency` | Average request latency | port={port} |
| `zk_MaxRequestLatency` | Maximum request latency | port={port} |
| **Packet Metrics** |
| `zk_PacketsSent` | Number of packets sent | port={port} |
| `zk_PacketsReceived` | Number of packets received | port={port} |
| **Kafka-Reported ZooKeeper Metrics** |
| `kaf_ZooKeeperClientMetrics_ZooKeeperRequestLatencyMs` | ZooKeeper request latency from Kafka perspective | - |
| `kaf_SessionExpireListener_ZooKeeperExpiresPerSec` | Rate of ZooKeeper session expirations | - |
| `kaf_SessionExpireListener_ZooKeeperAuthFailuresPerSec` | Rate of ZooKeeper authentication failures | - |
| `kaf_SessionExpireListener_ZooKeeperSyncConnectsPerSec` | Rate of ZooKeeper connections | - |
| `kaf_SessionExpireListener_ZooKeeperDisconnectsPerSec` | Rate of ZooKeeper disconnections | - |

## Query Examples

### Health Check Metrics
```promql
// Alive connections
zk_NumAliveConnections{rack='$rack',host_id=~'$host_id'}

// Total znode count
sum(zk_NodeCount{host_id=~'$host_id',type='kafka',node_type='zookeeper'})

// Total watch count
sum(zk_WatchCount{host_id=~'$host_id',type='kafka',node_type='zookeeper'})

// Outstanding requests
sum(zk_OutstandingRequests{host_id=~'$host_id',type='kafka',node_type='zookeeper'})
```

### Request Latency
```promql
// Minimum request latency
zk_MinRequestLatency{host_id=~'$host_id',type='kafka',node_type='zookeeper'}

// Average request latency
zk_AvgRequestLatency{host_id=~'$host_id',node_type='zookeeper',type='kafka'}

// Maximum request latency
zk_MaxRequestLatency{host_id=~'$host_id',node_type='zookeeper',type='kafka'}

// Kafka-reported ZooKeeper latency
kaf_ZooKeeperClientMetrics_ZooKeeperRequestLatencyMs{rack=~'$rack',host_id=~'$host_id'}
```

### Traffic Metrics
```promql
// Packets sent rate
sum(zk_PacketsSent{host_id=~'$host_id', axonfunction='rate', type='kafka',node_type='zookeeper'})

// Packets received rate
sum(zk_PacketsReceived{host_id=~'$host_id', axonfunction='rate', type='kafka',node_type='zookeeper'})

// Znode creation rate
avg(zk_NodeCount{host_id=~'$host_id', axonfunction='rate',type='kafka',node_type='zookeeper'})
```

### Connection Management
```promql
// Session expiration rate
kaf_SessionExpireListener_ZooKeeperExpiresPerSec{axonfunction='rate',rack=~'$rack',host_id=~'$host_id'}

// Authentication failure rate
kaf_SessionExpireListener_ZooKeeperAuthFailuresPerSec{axonfunction='rate',rack=~'$rack',host_id=~'$host_id'}

// Connection rate
kaf_SessionExpireListener_ZooKeeperSyncConnectsPerSec{axonfunction='rate',rack=~'$rack',host_id=~'$host_id'}

// Disconnection rate
kaf_SessionExpireListener_ZooKeeperDisconnectsPerSec{axonfunction='rate',rack=~'$rack',host_id=~'$host_id'}
```

## Panel Organization

**Overview Section**

   - Empty row for spacing/organization

**Health Check**

   - Alive Connections
   - Outstanding Requests
   - Number of Watchers
   - Number of ZNodes

**Request Latency**

   - Packets (sent/received rates)
   - Znode Creation Rate
   - Request Latency - Minimum
   - Request Latency - Average
   - Request Latency - Maximum
   - Kafka Reported Request Latency

**Connections**

   - Zookeeper expired connections per sec
   - Zookeeper auth failures per sec
   - Zookeeper disconnect per sec
   - Zookeeper connections per sec

## Filters

- **host_id**: Filter by specific ZooKeeper node

- **rack**: Filter by rack location

## Best Practices

**Health Monitoring**

   - Monitor alive connections for capacity planning
   - Outstanding requests should remain low
   - High watch count may impact performance
   - Monitor znode count growth

**Latency Analysis**

   - Average latency should be below tickTime
   - High max latency indicates potential issues
   - Compare ZK-reported vs Kafka-reported latency

**Connection Management**

   - Monitor session expirations for client issues
   - Auth failures indicate security problems
   - High disconnect rate suggests network issues

**Performance Tuning**

   - Adjust tickTime based on latency requirements
   - Monitor packet rates for network saturation
   - Balance connections across ensemble members

**Troubleshooting**

   - High outstanding requests: Check ZK performance
   - Session expirations: Review session timeout settings
   - Auth failures: Check SASL/ACL configurations

**Capacity Planning**

   - Monitor znode growth rate
   - Track connection count trends
   - Plan for watch count scaling

**ZooKeeper Ensemble Health**

   - Ensure all ensemble members are responsive
   - Monitor for leader elections
   - Check fsync latency on ZK data directory