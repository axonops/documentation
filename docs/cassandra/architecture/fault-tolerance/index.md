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

```graphviz dot fault-tolerance-layers.svg
digraph FaultToleranceLayers {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Fault Tolerance Architecture";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    subgraph cluster_client {
        label="Client Layer";
        style="rounded,filled";
        fillcolor="#E8F4E8";
        color="#99CC99";

        driver [label="Driver\n• Connection pooling\n• Request routing\n• Retry policies", fillcolor="#5B9BD5", fontcolor="white"];
        lb [label="Load Balancing Policy\n• Token-aware routing\n• DC-aware routing\n• Latency-aware", fillcolor="#5B9BD5", fontcolor="white"];
        retry [label="Retry Policy\n• Idempotent retries\n• Speculative execution\n• Fallback strategies", fillcolor="#5B9BD5", fontcolor="white"];
    }

    subgraph cluster_server {
        label="Server Layer";
        style="rounded,filled";
        fillcolor="#FFE8E8";
        color="#CC9999";

        coordinator [label="Coordinator\n• Request routing\n• Replica selection\n• Timeout handling", fillcolor="#C55A11", fontcolor="white"];
        gossip [label="Gossip\n• Failure detection\n• Topology awareness\n• State propagation", fillcolor="#C55A11", fontcolor="white"];
        hints [label="Hinted Handoff\n• Write buffering\n• Eventual delivery\n• Consistency repair", fillcolor="#C55A11", fontcolor="white"];
    }

    subgraph cluster_data {
        label="Data Layer";
        style="rounded,filled";
        fillcolor="#E8E8F4";
        color="#9999CC";

        replication [label="Replication\n• RF copies per partition\n• Multi-DC replication\n• Rack distribution", fillcolor="#70AD47", fontcolor="white"];
        repair [label="Repair\n• Anti-entropy\n• Merkle trees\n• Consistency restoration", fillcolor="#70AD47", fontcolor="white"];
    }

    driver -> lb -> retry;
    retry -> coordinator [style=dashed];
    coordinator -> gossip;
    coordinator -> hints;
    gossip -> replication;
    hints -> replication;
    replication -> repair;
}
```

---

## Failure Taxonomy

### Failure Scope Hierarchy

Failures occur at different scopes, each with distinct characteristics and recovery strategies:

```graphviz dot failure-hierarchy.svg
digraph FailureHierarchy {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Failure Scope Hierarchy";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    process [label="Process Failure\n• JVM crash\n• OOM kill\n• Application bug", fillcolor="#70AD47", fontcolor="white"];
    node_f [label="Node Failure\n• Hardware failure\n• OS crash\n• Power loss", fillcolor="#5B9BD5", fontcolor="white"];
    rack [label="Rack Failure\n• Top-of-rack switch\n• Power distribution\n• Cooling failure", fillcolor="#FFC000", fontcolor="black"];
    dc [label="Datacenter Failure\n• Network isolation\n• Power grid\n• Natural disaster", fillcolor="#C55A11", fontcolor="white"];
    region [label="Region Failure\n• Multiple DC outage\n• Wide-area network\n• Geographic event", fillcolor="#C00000", fontcolor="white"];

    process -> node_f [label="escalates"];
    node_f -> rack [label="correlates"];
    rack -> dc [label="correlates"];
    dc -> region [label="correlates"];
}
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

```graphviz dot single-node-failure.svg
digraph SingleNodeFailure {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=LR;

    label="Single Node Failure (RF=3, CL=QUORUM)";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    subgraph cluster_before {
        label="Before Failure";
        style="rounded,filled";
        fillcolor="#E8F4E8";
        color="#99CC99";

        client1 [label="Client", fillcolor="#5B9BD5", fontcolor="white"];

        n1 [label="Node 1\n(replica)", fillcolor="#70AD47", fontcolor="white"];
        n2 [label="Node 2\n(replica)", fillcolor="#70AD47", fontcolor="white"];
        n3 [label="Node 3\n(replica)", fillcolor="#70AD47", fontcolor="white"];

        client1 -> n1;
        client1 -> n2;
        client1 -> n3;
    }

    subgraph cluster_after {
        label="After Node 2 Fails";
        style="rounded,filled";
        fillcolor="#FFE8E8";
        color="#CC9999";

        client2 [label="Client", fillcolor="#5B9BD5", fontcolor="white"];

        n1b [label="Node 1\n(replica)", fillcolor="#70AD47", fontcolor="white"];
        n2b [label="Node 2\n(DOWN)", fillcolor="#C00000", fontcolor="white"];
        n3b [label="Node 3\n(replica)", fillcolor="#70AD47", fontcolor="white"];

        client2 -> n1b;
        client2 -> n2b [style=dashed, color="red"];
        client2 -> n3b;
    }

    n3 -> n1b [style=invis];
}
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

```graphviz dot server-side-response.svg
digraph ServerSideResponse {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Server-Side Failure Response";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    failure [label="Node Failure\nDetected", fillcolor="#C00000", fontcolor="white"];

    phi [label="1. Phi Accrual Detection\nφ exceeds threshold (~8-10s)", fillcolor="#5B9BD5", fontcolor="white"];
    gossip [label="2. Gossip Propagation\nDOWN status spreads (~seconds)", fillcolor="#5B9BD5", fontcolor="white"];
    hints [label="3. Hinted Handoff\nWrites stored for failed node", fillcolor="#FFC000", fontcolor="black"];
    reroute [label="4. Request Rerouting\nExclude from replica selection", fillcolor="#70AD47", fontcolor="white"];

    failure -> phi -> gossip;
    gossip -> hints;
    gossip -> reroute;
}
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

```graphviz dot client-side-response.svg
digraph ClientSideResponse {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Driver Failure Response";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    subgraph cluster_detection {
        label="Detection";
        style="rounded,filled";
        fillcolor="#E8E8E8";
        color="#999999";

        timeout [label="Connection Timeout\nor Read Timeout", fillcolor="#FFC000", fontcolor="black"];
        heartbeat [label="Connection Heartbeat\nFailure", fillcolor="#FFC000", fontcolor="black"];
        event [label="Topology Event\n(STATUS_CHANGE)", fillcolor="#FFC000", fontcolor="black"];
    }

    subgraph cluster_response {
        label="Response";
        style="rounded,filled";
        fillcolor="#E8F4E8";
        color="#99CC99";

        mark [label="Mark Node DOWN\nin connection pool", fillcolor="#5B9BD5", fontcolor="white"];
        reconnect [label="Schedule Reconnection\n(exponential backoff)", fillcolor="#5B9BD5", fontcolor="white"];
        reroute [label="Route Requests\nto other nodes", fillcolor="#70AD47", fontcolor="white"];
    }

    subgraph cluster_retry {
        label="Request Handling";
        style="rounded,filled";
        fillcolor="#FFE8E8";
        color="#CC9999";

        retry_policy [label="Retry Policy\nEvaluates error", fillcolor="#C55A11", fontcolor="white"];
        retry_next [label="Retry on\nNext Host", fillcolor="#C55A11", fontcolor="white"];
        fail [label="Propagate Error\nto Application", fillcolor="#C00000", fontcolor="white"];
    }

    timeout -> mark;
    heartbeat -> mark;
    event -> mark;
    mark -> reconnect;
    mark -> reroute;
    reroute -> retry_policy;
    retry_policy -> retry_next [label="retryable"];
    retry_policy -> fail [label="non-retryable"];
}
```

---

## Rack Failure Scenarios

### Rack-Aware Replication

With `NetworkTopologyStrategy` and rack-aware placement, Cassandra distributes replicas across racks:

```graphviz dot rack-aware-placement.svg
digraph RackAwarePlacement {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Rack-Aware Replica Placement (RF=3)";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    subgraph cluster_dc1 {
        label="Datacenter 1";
        style="rounded,filled";
        fillcolor="#E8E8E8";
        color="#999999";

        subgraph cluster_rack1 {
            label="Rack 1";
            style="rounded,filled";
            fillcolor="#E8F4E8";
            color="#99CC99";

            r1n1 [label="Node 1\nReplica A", fillcolor="#5B9BD5", fontcolor="white"];
            r1n2 [label="Node 2", fillcolor="#70AD47", fontcolor="white"];
        }

        subgraph cluster_rack2 {
            label="Rack 2";
            style="rounded,filled";
            fillcolor="#FFE8E8";
            color="#CC9999";

            r2n1 [label="Node 3\nReplica A", fillcolor="#5B9BD5", fontcolor="white"];
            r2n2 [label="Node 4", fillcolor="#70AD47", fontcolor="white"];
        }

        subgraph cluster_rack3 {
            label="Rack 3";
            style="rounded,filled";
            fillcolor="#E8E8F4";
            color="#9999CC";

            r3n1 [label="Node 5\nReplica A", fillcolor="#5B9BD5", fontcolor="white"];
            r3n2 [label="Node 6", fillcolor="#70AD47", fontcolor="white"];
        }
    }

    partition [label="Partition A", fillcolor="#FFC000", fontcolor="black"];
    partition -> r1n1;
    partition -> r2n1;
    partition -> r3n1;
}
```

### Rack Failure Impact

```graphviz dot rack-failure.svg
digraph RackFailure {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=LR;

    label="Rack Failure Scenario (RF=3, 3 Racks)";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    subgraph cluster_healthy {
        label="Healthy State";
        style="rounded,filled";
        fillcolor="#E8F4E8";
        color="#99CC99";

        rack1_h [label="Rack 1\n2 nodes\n1 replica", fillcolor="#70AD47", fontcolor="white"];
        rack2_h [label="Rack 2\n2 nodes\n1 replica", fillcolor="#70AD47", fontcolor="white"];
        rack3_h [label="Rack 3\n2 nodes\n1 replica", fillcolor="#70AD47", fontcolor="white"];
    }

    subgraph cluster_failed {
        label="Rack 2 Failed";
        style="rounded,filled";
        fillcolor="#FFE8E8";
        color="#CC9999";

        rack1_f [label="Rack 1\n2 nodes\n1 replica", fillcolor="#70AD47", fontcolor="white"];
        rack2_f [label="Rack 2\nDOWN", fillcolor="#C00000", fontcolor="white"];
        rack3_f [label="Rack 3\n2 nodes\n1 replica", fillcolor="#70AD47", fontcolor="white"];
    }

    rack3_h -> rack1_f [style=invis];

    result [label="Result:\n• 2 of 3 replicas available\n• QUORUM satisfied\n• ONE satisfied\n• ALL fails", shape=note, fillcolor="#FFC000", fontcolor="black"];

    rack3_f -> result [style=invis];
}
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

```graphviz dot multi-dc-topology.svg
digraph MultiDCTopology {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=LR;

    label="Multi-Datacenter Topology (RF=3 per DC)";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    subgraph cluster_dc1 {
        label="DC1 (US-East)";
        style="rounded,filled";
        fillcolor="#E8F4E8";
        color="#99CC99";

        dc1_n1 [label="Node 1", fillcolor="#5B9BD5", fontcolor="white"];
        dc1_n2 [label="Node 2", fillcolor="#5B9BD5", fontcolor="white"];
        dc1_n3 [label="Node 3", fillcolor="#5B9BD5", fontcolor="white"];
    }

    subgraph cluster_dc2 {
        label="DC2 (US-West)";
        style="rounded,filled";
        fillcolor="#FFE8E8";
        color="#CC9999";

        dc2_n1 [label="Node 4", fillcolor="#C55A11", fontcolor="white"];
        dc2_n2 [label="Node 5", fillcolor="#C55A11", fontcolor="white"];
        dc2_n3 [label="Node 6", fillcolor="#C55A11", fontcolor="white"];
    }

    subgraph cluster_dc3 {
        label="DC3 (EU-West)";
        style="rounded,filled";
        fillcolor="#E8E8F4";
        color="#9999CC";

        dc3_n1 [label="Node 7", fillcolor="#70AD47", fontcolor="white"];
        dc3_n2 [label="Node 8", fillcolor="#70AD47", fontcolor="white"];
        dc3_n3 [label="Node 9", fillcolor="#70AD47", fontcolor="white"];
    }

    dc1_n1 -> dc2_n1 [style=dashed, label="async\nreplication"];
    dc1_n1 -> dc3_n1 [style=dashed, label="async\nreplication"];
    dc2_n1 -> dc3_n1 [style=dashed];
}
```

### DC Failure Response

```graphviz dot dc-failure-response.svg
digraph DCFailureResponse {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Datacenter Failure Response";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    failure [label="DC1 Fails\n(network partition or outage)", fillcolor="#C00000", fontcolor="white"];

    subgraph cluster_server_response {
        label="Server Response";
        style="rounded,filled";
        fillcolor="#E8E8E8";
        color="#999999";

        detect [label="All DC1 nodes\nmarked DOWN", fillcolor="#5B9BD5", fontcolor="white"];
        hints_dc [label="Hints stored\nfor DC1 nodes", fillcolor="#5B9BD5", fontcolor="white"];
        continue [label="DC2/DC3 continue\nserving requests", fillcolor="#70AD47", fontcolor="white"];
    }

    subgraph cluster_client_response {
        label="Client Response (DC-Aware Policy)";
        style="rounded,filled";
        fillcolor="#FFE8E8";
        color="#CC9999";

        local_fail [label="Local DC\nunavailable", fillcolor="#FFC000", fontcolor="black"];
        failover [label="Failover to\nremote DC", fillcolor="#C55A11", fontcolor="white"];
        latency [label="Higher latency\n(cross-DC)", fillcolor="#C55A11", fontcolor="white"];
    }

    failure -> detect -> hints_dc -> continue;
    failure -> local_fail -> failover -> latency;
}
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

```graphviz dot load-balancing-policy.svg
digraph LoadBalancingPolicy {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Load Balancing Policy Decision Flow";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    request [label="Client Request", fillcolor="#5B9BD5", fontcolor="white"];

    token [label="Token-Aware\nIdentify replica nodes\nfor partition key", fillcolor="#FFC000", fontcolor="black"];

    dc_aware [label="DC-Aware\nPrefer local DC\nFallback to remote", fillcolor="#FFC000", fontcolor="black"];

    rack_aware [label="Rack-Aware\n(Optional)\nDistribute across racks", fillcolor="#FFC000", fontcolor="black"];

    latency [label="Latency-Aware\n(Optional)\nPrefer fastest nodes", fillcolor="#FFC000", fontcolor="black"];

    select [label="Select Node\nfrom filtered set", fillcolor="#70AD47", fontcolor="white"];

    request -> token -> dc_aware -> rack_aware -> latency -> select;
}
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

```graphviz dot retry-policy-flow.svg
digraph RetryPolicyFlow {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Retry Policy Decision Flow";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    error [label="Request Error", fillcolor="#C00000", fontcolor="white"];

    check_type [label="Error Type?", shape=diamond, fillcolor="#E8E8E8", fontcolor="black"];

    read_timeout [label="Read Timeout\nData received?", fillcolor="#5B9BD5", fontcolor="white"];
    write_timeout [label="Write Timeout\nWrite type?", fillcolor="#5B9BD5", fontcolor="white"];
    unavailable [label="Unavailable\nReplicas available?", fillcolor="#5B9BD5", fontcolor="white"];

    retry_same [label="Retry\nSame Host", fillcolor="#70AD47", fontcolor="white"];
    retry_next [label="Retry\nNext Host", fillcolor="#70AD47", fontcolor="white"];
    rethrow [label="Rethrow\nto Application", fillcolor="#C00000", fontcolor="white"];
    ignore [label="Ignore\n(return empty)", fillcolor="#FFC000", fontcolor="black"];

    error -> check_type;
    check_type -> read_timeout [label="ReadTimeout"];
    check_type -> write_timeout [label="WriteTimeout"];
    check_type -> unavailable [label="Unavailable"];

    read_timeout -> retry_same [label="data received"];
    read_timeout -> retry_next [label="no data"];
    write_timeout -> rethrow [label="non-idempotent"];
    write_timeout -> retry_same [label="idempotent"];
    unavailable -> retry_next [label="enough alive"];
    unavailable -> rethrow [label="not enough"];
}
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

```graphviz dot speculative-execution.svg
digraph SpeculativeExecution {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=LR;

    label="Speculative Execution (delay=100ms)";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    client [label="Client", fillcolor="#5B9BD5", fontcolor="white"];

    subgraph cluster_timeline {
        label="Timeline";
        style="rounded,filled";
        fillcolor="#E8E8E8";
        color="#999999";

        t0 [label="T+0ms\nSend to Node 1", fillcolor="#70AD47", fontcolor="white"];
        t100 [label="T+100ms\nNo response\nSend to Node 2", fillcolor="#FFC000", fontcolor="black"];
        t150 [label="T+150ms\nNode 2 responds\nCancel Node 1", fillcolor="#70AD47", fontcolor="white"];
    }

    node1 [label="Node 1\n(slow/failed)", fillcolor="#C00000", fontcolor="white"];
    node2 [label="Node 2\n(fast)", fillcolor="#70AD47", fontcolor="white"];

    client -> t0;
    t0 -> node1 [style=dashed];
    t0 -> t100 [label="timeout"];
    t100 -> node2;
    node2 -> t150;
}
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

```graphviz dot node-recovery.svg
digraph NodeRecovery {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Node Recovery Process";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    restart [label="Node Restarts", fillcolor="#5B9BD5", fontcolor="white"];

    gossip_rejoin [label="1. Gossip Rejoin\nContact seeds/peers\nSync cluster state", fillcolor="#5B9BD5", fontcolor="white"];

    hints_replay [label="2. Hints Replay\nReceive buffered writes\nfrom coordinators", fillcolor="#FFC000", fontcolor="black"];

    read_repair [label="3. Read Repair\nFix inconsistencies\non read path", fillcolor="#FFC000", fontcolor="black"];

    full_repair [label="4. Full Repair\n(if needed)\nAnti-entropy sync", fillcolor="#C55A11", fontcolor="white"];

    normal [label="Fully Synchronized", fillcolor="#70AD47", fontcolor="white"];

    restart -> gossip_rejoin -> hints_replay -> read_repair -> full_repair -> normal;
}
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

```graphviz dot dc-recovery.svg
digraph DCRecovery {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Datacenter Recovery Process";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    dc_online [label="DC Comes Online", fillcolor="#5B9BD5", fontcolor="white"];

    subgraph cluster_immediate {
        label="Immediate (Automatic)";
        style="rounded,filled";
        fillcolor="#E8F4E8";
        color="#99CC99";

        gossip_sync [label="Gossip Sync\nAll nodes rejoin cluster", fillcolor="#70AD47", fontcolor="white"];
        hints [label="Hints Replay\nBuffered writes delivered", fillcolor="#70AD47", fontcolor="white"];
        traffic [label="Resume Traffic\nClients reconnect", fillcolor="#70AD47", fontcolor="white"];
    }

    subgraph cluster_manual {
        label="Manual (If Needed)";
        style="rounded,filled";
        fillcolor="#FFE8E8";
        color="#CC9999";

        assess [label="Assess Data Loss\nCheck hint delivery\nReview logs", fillcolor="#C55A11", fontcolor="white"];
        repair_dc [label="Repair DC\nnodetool repair -dc <dc>", fillcolor="#C55A11", fontcolor="white"];
        verify [label="Verify Consistency\nCompare cross-DC", fillcolor="#C55A11", fontcolor="white"];
    }

    dc_online -> gossip_sync -> hints -> traffic;
    traffic -> assess [style=dashed, label="if prolonged outage"];
    assess -> repair_dc -> verify;
}
```

---

## Client Failover Patterns

### Active-Passive DC Failover

```graphviz dot active-passive-failover.svg
digraph ActivePassiveFailover {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Active-Passive DC Failover";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    subgraph cluster_normal {
        label="Normal Operation";
        style="rounded,filled";
        fillcolor="#E8F4E8";
        color="#99CC99";

        app1 [label="Application", fillcolor="#5B9BD5", fontcolor="white"];
        dc1_active [label="DC1 (Active)\nlocal_dc=dc1", fillcolor="#70AD47", fontcolor="white"];
        dc2_standby [label="DC2 (Standby)\nreceives async replication", fillcolor="#FFC000", fontcolor="black"];

        app1 -> dc1_active [label="all traffic"];
        dc1_active -> dc2_standby [style=dashed, label="replication"];
    }

    subgraph cluster_failover {
        label="During DC1 Failure";
        style="rounded,filled";
        fillcolor="#FFE8E8";
        color="#CC9999";

        app2 [label="Application", fillcolor="#5B9BD5", fontcolor="white"];
        dc1_down [label="DC1 (DOWN)", fillcolor="#C00000", fontcolor="white"];
        dc2_active [label="DC2 (Active)\nfailover triggered", fillcolor="#70AD47", fontcolor="white"];

        app2 -> dc1_down [style=dashed, color="red"];
        app2 -> dc2_active [label="failover traffic"];
    }
}
```

### Active-Active DC Pattern

```graphviz dot active-active.svg
digraph ActiveActive {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Active-Active Multi-DC Pattern";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    subgraph cluster_apps {
        label="Application Layer";
        style="rounded,filled";
        fillcolor="#E8E8E8";
        color="#999999";

        app_east [label="App (US-East)\nlocal_dc=dc1", fillcolor="#5B9BD5", fontcolor="white"];
        app_west [label="App (US-West)\nlocal_dc=dc2", fillcolor="#5B9BD5", fontcolor="white"];
    }

    subgraph cluster_dcs {
        label="Cassandra Cluster";
        style="rounded,filled";
        fillcolor="#E8F4E8";
        color="#99CC99";

        dc1 [label="DC1 (US-East)\nRF=3", fillcolor="#70AD47", fontcolor="white"];
        dc2 [label="DC2 (US-West)\nRF=3", fillcolor="#70AD47", fontcolor="white"];
    }

    app_east -> dc1 [label="local"];
    app_west -> dc2 [label="local"];
    app_east -> dc2 [style=dashed, label="failover"];
    app_west -> dc1 [style=dashed, label="failover"];
    dc1 -> dc2 [dir=both, label="async replication"];
}
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

