# Fault Tolerance and Failure Scenarios

This section examines Cassandra's fault tolerance architecture from both server-side and client-side perspectives. Understanding how failures propagate through the system—and how both the cluster and client drivers respond—is essential for designing resilient applications.

---

## Fault Tolerance Model

Cassandra's fault tolerance derives from three architectural properties:

| Property | Mechanism | Benefit |
|----------|-----------|---------|
| **Replication** | Data copied to RF nodes | No single point of failure for data |
| **Decentralization** | No master node, peer-to-peer | No single point of failure for coordination |
| **Tunable consistency** | Configurable read/write guarantees | Trade-off availability vs consistency |

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Fault Tolerance Architecture

rectangle "Client Layer" as client_layer #E8F4E8 {
    card "Driver\n• Connection pooling\n• Request routing\n• Retry policies" as driver #5B9BD5
    card "Load Balancing Policy\n• Token-aware routing\n• DC-aware routing\n• Latency-aware" as lb #5B9BD5
    card "Retry Policy\n• Idempotent retries\n• Speculative execution\n• Fallback strategies" as retry #5B9BD5
}

rectangle "Server Layer" as server_layer #FFE8E8 {
    card "Coordinator\n• Request routing\n• Replica selection\n• Timeout handling" as coordinator #C55A11
    card "Gossip\n• Failure detection\n• Topology awareness\n• State propagation" as gossip #C55A11
    card "Hinted Handoff\n• Write buffering\n• Eventual delivery\n• Consistency repair" as hints #C55A11
}

rectangle "Data Layer" as data_layer #E8E8F4 {
    card "Replication\n• RF copies per partition\n• Multi-DC replication\n• Rack distribution" as replication #70AD47
    card "Repair\n• Anti-entropy\n• Merkle trees\n• Consistency restoration" as repair #70AD47
}

driver --> lb
lb --> retry
retry ..> coordinator
coordinator --> gossip
coordinator --> hints
gossip --> replication
hints --> replication
replication --> repair

@enduml
```

---

## Failure Taxonomy

### Failure Scope Hierarchy

Failures occur at different scopes, each with distinct characteristics and recovery strategies:

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Failure Scope Hierarchy

card "Process Failure\n• JVM crash\n• OOM kill\n• Application bug" as process #70AD47
card "Node Failure\n• Hardware failure\n• OS crash\n• Power loss" as node_f #5B9BD5
card "Rack Failure\n• Top-of-rack switch\n• Power distribution\n• Cooling failure" as rack #FFC000
card "Datacenter Failure\n• Network isolation\n• Power grid\n• Natural disaster" as dc #C55A11
card "Region Failure\n• Multiple DC outage\n• Wide-area network\n• Geographic event" as region #C00000

process --> node_f : escalates
node_f --> rack : correlates
rack --> dc : correlates
dc --> region : correlates

@enduml
```

### Failure Characteristics

| Scope | Typical Duration | Detection Time | Recovery Approach |
|-------|------------------|----------------|-------------------|
| **Process** | Seconds-minutes | ~10 seconds (Phi) | Automatic restart |
| **Node** | Minutes-hours | ~10 seconds (Phi) | Replacement or repair |
| **Rack** | Minutes-hours | ~10 seconds (Phi) | Wait or redistribute |
| **Datacenter** | Hours-days | Seconds (network) | Failover to other DC |
| **Region** | Hours-days | Seconds (network) | DR procedures |

---

## Node Failure Scenarios

### Single Node Failure

The most common failure scenario. Cassandra continues operating if sufficient replicas remain:

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Single Node Failure (RF=3, CL=QUORUM)

rectangle "Before Failure" as before #E8F4E8 {
    card "Client" as client1 #5B9BD5
    card "Node 1\n(replica)" as n1 #70AD47
    card "Node 2\n(replica)" as n2 #70AD47
    card "Node 3\n(replica)" as n3 #70AD47
}

rectangle "After Node 2 Fails" as after #FFE8E8 {
    card "Client" as client2 #5B9BD5
    card "Node 1\n(replica)" as n1b #70AD47
    card "Node 2\n(DOWN)" as n2b #C00000
    card "Node 3\n(replica)" as n3b #70AD47
}

client1 --> n1
client1 --> n2
client1 --> n3

client2 --> n1b
client2 ..> n2b #red
client2 --> n3b

@enduml
```

**Impact Analysis:**

| Consistency Level | RF=3, 1 Node Down | Outcome |
|-------------------|-------------------|---------|
| ONE | 2 replicas available | Reads/writes succeed |
| QUORUM | 2 of 3 available | Reads/writes succeed (2 ≥ ⌈3/2⌉ + 1) |
| ALL | Only 2 available | Reads/writes **fail** |
| LOCAL_QUORUM | Depends on DC | Succeeds if local DC unaffected |

### Server-Side Response

When a node fails, the server-side components respond:

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Server-Side Failure Response

card "Node Failure\nDetected" as failure #C00000
card "1. Phi Accrual Detection\nφ exceeds threshold (~8-10s)" as phi #5B9BD5
card "2. Gossip Propagation\nDOWN status spreads (~seconds)" as gossip #5B9BD5
card "3. Hinted Handoff\nWrites stored for failed node" as hints #FFC000
card "4. Request Rerouting\nExclude from replica selection" as reroute #70AD47

failure --> phi
phi --> gossip
gossip --> hints
gossip --> reroute

@enduml
```

**Timeline:**

| Time | Event |
|------|-------|
| T+0 | Node stops responding |
| T+1-8s | Phi value rises as heartbeats missed |
| T+8-10s | Phi exceeds threshold, node marked DOWN locally |
| T+10-15s | DOWN status propagates via gossip |
| T+10s+ | Hints accumulate on coordinators |
| T+recovery | Node restarts, hints replay |

### Client-Side Response

The driver detects and responds to node failures:

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Driver Failure Response

rectangle "Detection" as detection #E8E8E8 {
    card "Connection Timeout\nor Read Timeout" as timeout #FFC000
    card "Connection Heartbeat\nFailure" as heartbeat #FFC000
    card "Topology Event\n(STATUS_CHANGE)" as event #FFC000
}

rectangle "Response" as response #E8F4E8 {
    card "Mark Node DOWN\nin connection pool" as mark #5B9BD5
    card "Schedule Reconnection\n(exponential backoff)" as reconnect #5B9BD5
    card "Route Requests\nto other nodes" as reroute #70AD47
}

rectangle "Request Handling" as request_handling #FFE8E8 {
    card "Retry Policy\nEvaluates error" as retry_policy #C55A11
    card "Retry on\nNext Host" as retry_next #C55A11
    card "Propagate Error\nto Application" as fail #C00000
}

timeout --> mark
heartbeat --> mark
event --> mark
mark --> reconnect
mark --> reroute
reroute --> retry_policy
retry_policy --> retry_next : retryable
retry_policy --> fail : non-retryable

@enduml
```

---

## Rack Failure Scenarios

### Rack-Aware Replication

With `NetworkTopologyStrategy` and rack-aware placement, Cassandra distributes replicas across racks:

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Rack-Aware Replica Placement (RF=3)

card "Partition A" as partition #FFC000

rectangle "Datacenter 1" as dc1 #E8E8E8 {
    rectangle "Rack 1" as rack1 #E8F4E8 {
        card "Node 1\nReplica A" as r1n1 #5B9BD5
        card "Node 2" as r1n2 #70AD47
    }

    rectangle "Rack 2" as rack2 #FFE8E8 {
        card "Node 3\nReplica A" as r2n1 #5B9BD5
        card "Node 4" as r2n2 #70AD47
    }

    rectangle "Rack 3" as rack3 #E8E8F4 {
        card "Node 5\nReplica A" as r3n1 #5B9BD5
        card "Node 6" as r3n2 #70AD47
    }
}

partition --> r1n1
partition --> r2n1
partition --> r3n1

@enduml
```

### Rack Failure Impact

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Rack Failure Scenario (RF=3, 3 Racks)

rectangle "Healthy State" as healthy #E8F4E8 {
    card "Rack 1\n2 nodes\n1 replica" as rack1_h #70AD47
    card "Rack 2\n2 nodes\n1 replica" as rack2_h #70AD47
    card "Rack 3\n2 nodes\n1 replica" as rack3_h #70AD47
}

rectangle "Rack 2 Failed" as failed #FFE8E8 {
    card "Rack 1\n2 nodes\n1 replica" as rack1_f #70AD47
    card "Rack 2\nDOWN" as rack2_f #C00000
    card "Rack 3\n2 nodes\n1 replica" as rack3_f #70AD47
}

note right of failed
  Result:
  • 2 of 3 replicas available
  • QUORUM satisfied
  • ONE satisfied
  • ALL fails
end note

@enduml
```

**Rack Failure Tolerance:**

| Configuration | Racks | RF | Rack Failure Tolerance | Notes |
|---------------|-------|----|-----------------------|-------|
| Minimum | 1 | 3 | None | All replicas in same failure domain |
| Standard | 3 | 3 | 1 rack | One replica per rack |
| Enhanced | 3 | 5 | 1 rack | At least 2 replicas survive |
| High | 5 | 5 | 2 racks | Replicas spread across 5 racks |

---

## Datacenter Failure Scenarios

### Multi-Datacenter Topology

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Multi-Datacenter Topology (RF=3 per DC)

rectangle "DC1 (US-East)" as dc1 #E8F4E8 {
    card "Node 1" as dc1_n1 #5B9BD5
    card "Node 2" as dc1_n2 #5B9BD5
    card "Node 3" as dc1_n3 #5B9BD5
}

rectangle "DC2 (US-West)" as dc2 #FFE8E8 {
    card "Node 4" as dc2_n1 #C55A11
    card "Node 5" as dc2_n2 #C55A11
    card "Node 6" as dc2_n3 #C55A11
}

rectangle "DC3 (EU-West)" as dc3 #E8E8F4 {
    card "Node 7" as dc3_n1 #70AD47
    card "Node 8" as dc3_n2 #70AD47
    card "Node 9" as dc3_n3 #70AD47
}

dc1_n1 ..> dc2_n1 : async\nreplication
dc1_n1 ..> dc3_n1 : async\nreplication
dc2_n1 ..> dc3_n1

@enduml
```

### DC Failure Response

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Datacenter Failure Response

card "DC1 Fails\n(network partition or outage)" as failure #C00000

rectangle "Server Response" as server_response #E8E8E8 {
    card "All DC1 nodes\nmarked DOWN" as detect #5B9BD5
    card "Hints stored\nfor DC1 nodes" as hints_dc #5B9BD5
    card "DC2/DC3 continue\nserving requests" as continue #70AD47
}

rectangle "Client Response (DC-Aware Policy)" as client_response #FFE8E8 {
    card "Local DC\nunavailable" as local_fail #FFC000
    card "Failover to\nremote DC" as failover #C55A11
    card "Higher latency\n(cross-DC)" as latency #C55A11
}

failure --> detect
detect --> hints_dc
hints_dc --> continue
failure --> local_fail
local_fail --> failover
failover --> latency

@enduml
```

### Consistency Level Behavior During DC Failure

| Consistency Level | DC1 Down | Behavior |
|-------------------|----------|----------|
| LOCAL_ONE | ✗ | Fails for DC1 clients, succeeds for DC2/DC3 |
| LOCAL_QUORUM | ✗ | Fails for DC1 clients, succeeds for DC2/DC3 |
| QUORUM | Depends | May succeed if enough total replicas (e.g., RF=3×3=9, need 5) |
| EACH_QUORUM | ✗ | **Fails** - requires quorum in each DC |
| ONE | ✓ | Succeeds if any replica reachable |
| ALL | ✗ | **Fails** - requires all replicas |

---

## Driver Policies and Failure Handling

### Load Balancing Policy

The load balancing policy determines how requests are routed, including during failures:

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Load Balancing Policy Decision Flow

card "Client Request" as request #5B9BD5
card "Token-Aware\nIdentify replica nodes\nfor partition key" as token #FFC000
card "DC-Aware\nPrefer local DC\nFallback to remote" as dc_aware #FFC000
card "Rack-Aware\n(Optional)\nDistribute across racks" as rack_aware #FFC000
card "Latency-Aware\n(Optional)\nPrefer fastest nodes" as latency #FFC000
card "Select Node\nfrom filtered set" as select #70AD47

request --> token
token --> dc_aware
dc_aware --> rack_aware
rack_aware --> latency
latency --> select

@enduml
```

**Policy Configuration for Fault Tolerance:**

```java
// Recommended production configuration
LoadBalancingPolicy policy = new TokenAwarePolicy(
    DCAwareRoundRobinPolicy.builder()
        .withLocalDc("dc1")
        .withUsedHostsPerRemoteDc(2)  // Failover capacity
        .allowRemoteDCsForLocalConsistencyLevel()  // Optional: allow remote DC for LOCAL_*
        .build()
);
```

### Retry Policy

The retry policy determines whether and how to retry failed requests:

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Retry Policy Decision Flow

start
#C00000:Request Error;

if (Error Type?) then (ReadTimeout)
    #5B9BD5:Read Timeout\nData received?;
    if (data received?) then (yes)
        #70AD47:Retry\nSame Host;
    else (no)
        #70AD47:Retry\nNext Host;
    endif
elseif (WriteTimeout)
    #5B9BD5:Write Timeout\nWrite type?;
    if (idempotent?) then (yes)
        #70AD47:Retry\nSame Host;
    else (no)
        #C00000:Rethrow\nto Application;
    endif
else (Unavailable)
    #5B9BD5:Unavailable\nReplicas available?;
    if (enough alive?) then (yes)
        #70AD47:Retry\nNext Host;
    else (no)
        #C00000:Rethrow\nto Application;
    endif
endif

stop

@enduml
```

**Error Types and Retry Behavior:**

| Error | Cause | Default Retry Behavior |
|-------|-------|----------------------|
| **ReadTimeoutException** | Coordinator timeout waiting for replicas | Retry same host if data received |
| **WriteTimeoutException** | Coordinator timeout waiting for acks | Retry only if idempotent (BATCH_LOG, UNLOGGED_BATCH) |
| **UnavailableException** | Insufficient replicas known alive | Retry on next host (once) |
| **NoHostAvailableException** | All hosts exhausted | No retry, propagate to application |
| **OperationTimedOutException** | Client-side timeout | No retry, propagate to application |

### Speculative Execution

Speculative execution sends redundant requests to reduce tail latency:

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Speculative Execution (delay=100ms)

card "Client" as client #5B9BD5

rectangle "Timeline" as timeline #E8E8E8 {
    card "T+0ms\nSend to Node 1" as t0 #70AD47
    card "T+100ms\nNo response\nSend to Node 2" as t100 #FFC000
    card "T+150ms\nNode 2 responds\nCancel Node 1" as t150 #70AD47
}

card "Node 1\n(slow/failed)" as node1 #C00000
card "Node 2\n(fast)" as node2 #70AD47

client --> t0
t0 ..> node1
t0 --> t100 : timeout
t100 --> node2
node2 --> t150

@enduml
```

**Speculative Execution Configuration:**

```java
// Speculative execution for read-heavy workloads
SpeculativeExecutionPolicy specPolicy =
    new ConstantSpeculativeExecutionPolicy(
        100,  // Delay before speculation (ms)
        2     // Maximum speculative executions
    );

// Or percentile-based
SpeculativeExecutionPolicy percentilePolicy =
    new PercentileSpeculativeExecutionPolicy(
        tracker,  // PercentileTracker
        99.0,     // Percentile threshold
        2         // Maximum speculative executions
    );
```

---

## Recovery Scenarios

### Node Recovery After Failure

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Node Recovery Process

card "Node Restarts" as restart #5B9BD5
card "1. Gossip Rejoin\nContact seeds/peers\nSync cluster state" as gossip_rejoin #5B9BD5
card "2. Hints Replay\nReceive buffered writes\nfrom coordinators" as hints_replay #FFC000
card "3. Read Repair\nFix inconsistencies\non read path" as read_repair #FFC000
card "4. Full Repair\n(if needed)\nAnti-entropy sync" as full_repair #C55A11
card "Fully Synchronized" as normal #70AD47

restart --> gossip_rejoin
gossip_rejoin --> hints_replay
hints_replay --> read_repair
read_repair --> full_repair
full_repair --> normal

@enduml
```

**Recovery Timeline:**

| Phase | Duration | Data Synchronized |
|-------|----------|-------------------|
| Gossip rejoin | Seconds | Cluster topology, schema |
| Hints replay | Minutes-hours | Writes during downtime (if hints available) |
| Read repair | Ongoing | Data accessed by reads |
| Full repair | Hours-days | All data (comprehensive) |

### When Full Repair is Required

Full repair should be run after recovery if:

| Condition | Reason |
|-----------|--------|
| Downtime > `max_hint_window_in_ms` (default 3 hours) | Hints expired, writes lost |
| Hints delivery failed | Check `nodetool tpstats` for dropped hints |
| Multiple node failures | Hints may be incomplete |
| Consistency-critical data | Ensure complete synchronization |

### Datacenter Recovery

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Datacenter Recovery Process

card "DC Comes Online" as dc_online #5B9BD5

rectangle "Immediate (Automatic)" as immediate #E8F4E8 {
    card "Gossip Sync\nAll nodes rejoin cluster" as gossip_sync #70AD47
    card "Hints Replay\nBuffered writes delivered" as hints #70AD47
    card "Resume Traffic\nClients reconnect" as traffic #70AD47
}

rectangle "Manual (If Needed)" as manual #FFE8E8 {
    card "Assess Data Loss\nCheck hint delivery\nReview logs" as assess #C55A11
    card "Repair DC\nnodetool repair -dc <dc>" as repair_dc #C55A11
    card "Verify Consistency\nCompare cross-DC" as verify #C55A11
}

dc_online --> gossip_sync
gossip_sync --> hints
hints --> traffic
traffic ..> assess : if prolonged outage
assess --> repair_dc
repair_dc --> verify

@enduml
```

---

## Client Failover Patterns

### Active-Passive DC Failover

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Active-Passive DC Failover

rectangle "Normal Operation" as normal #E8F4E8 {
    card "Application" as app1 #5B9BD5
    card "DC1 (Active)\nlocal_dc=dc1" as dc1_active #70AD47
    card "DC2 (Standby)\nreceives async replication" as dc2_standby #FFC000
}

rectangle "During DC1 Failure" as failover #FFE8E8 {
    card "Application" as app2 #5B9BD5
    card "DC1 (DOWN)" as dc1_down #C00000
    card "DC2 (Active)\nfailover triggered" as dc2_active #70AD47
}

app1 --> dc1_active : all traffic
dc1_active ..> dc2_standby : replication

app2 ..> dc1_down #red
app2 --> dc2_active : failover traffic

@enduml
```

### Active-Active DC Pattern

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

title Active-Active Multi-DC Pattern

rectangle "Application Layer" as apps #E8E8E8 {
    card "App (US-East)\nlocal_dc=dc1" as app_east #5B9BD5
    card "App (US-West)\nlocal_dc=dc2" as app_west #5B9BD5
}

rectangle "Cassandra Cluster" as cluster #E8F4E8 {
    card "DC1 (US-East)\nRF=3" as dc1 #70AD47
    card "DC2 (US-West)\nRF=3" as dc2 #70AD47
}

app_east --> dc1 : local
app_west --> dc2 : local
app_east ..> dc2 : failover
app_west ..> dc1 : failover
dc1 <--> dc2 : async replication

@enduml
```

**Active-Active Considerations:**

| Aspect | Recommendation |
|--------|----------------|
| Consistency | Use LOCAL_QUORUM for low latency |
| Conflicts | Last-write-wins (LWW) by default; design for idempotency |
| Failover | Automatic via driver DC-aware policy |
| Capacity | Each DC sized to handle full load |

---

## Monitoring Failure Scenarios

### Key Metrics

| Metric | Source | Failure Indication |
|--------|--------|-------------------|
| `org.apache.cassandra.metrics.ClientRequest.Timeouts` | JMX | Request timeouts increasing |
| `org.apache.cassandra.metrics.ClientRequest.Unavailables` | JMX | Insufficient replicas |
| `org.apache.cassandra.metrics.Storage.Hints` | JMX | Hints accumulating (node down) |
| `org.apache.cassandra.metrics.DroppedMessage.*` | JMX | Messages dropped under load |

### Alert Thresholds

| Condition | Warning | Critical |
|-----------|---------|----------|
| Node DOWN | Any node | Multiple nodes |
| Rack DOWN | N/A | Any rack |
| Hints pending | > 1000 | > 10000 |
| Timeout rate | > 0.1% | > 1% |
| Unavailable rate | > 0 | > 0.1% |

---

## Related Documentation

- **[Gossip Protocol](../cluster-management/gossip.md)** - Failure detection mechanics (Phi Accrual)
- **[Node Replacement](../cluster-management/node-replacement.md)** - Dead node recovery procedures
- **[Consistency](../distributed-data/consistency.md)** - Consistency levels and availability trade-offs
- **[Replication](../distributed-data/replication.md)** - Multi-DC replication configuration
- **[Driver Policies](../../application-development/drivers/policies/index.md)** - Detailed policy configuration
- **[Retry Policy](../../application-development/drivers/policies/retry.md)** - Retry behavior configuration
- **[Load Balancing](../../application-development/drivers/policies/load-balancing.md)** - Routing policy configuration

