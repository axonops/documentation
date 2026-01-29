---
title: "Cassandra Node Replacement"
description: "Replace failed Cassandra nodes with replace_address_first_boot. Dead node replacement procedure."
meta:
  - name: keywords
    content: "node replacement, replace dead node, replace_address_first_boot, Cassandra"
---

# Node Replacement

This section examines the architectural considerations for handling failed nodes in a Cassandra cluster. Understanding failure classification, recovery strategies, and the mechanics of node replacement is essential for designing resilient cluster topologies.

For operational procedures and step-by-step instructions, see **[Operations: Cluster Management](../../operations/cluster-management/index.md)**.

---

## Failure Classification

### Types of Node Failures

Node failures fall into distinct categories, each requiring different recovery approaches:

```plantuml
@startuml
skinparam backgroundColor white

title Node Failure Classification

rectangle "Node Failure" as failure #C00000

rectangle "Transient Failure\n• Temporary outage\n• Restart recovers\n• Data intact" as transient #FFC000
rectangle "Permanent Failure\n• Hardware failure\n• Data loss\n• Node unrecoverable" as permanent #C00000

rectangle "Recovery: Restart\nHints replay automatically" as restart #70AD47
rectangle "Recovery: Replace\nNew node takes tokens\n(new Host ID)" as replace #5B9BD5
rectangle "Recovery: Remove\nReduce cluster size" as remove #7F7F7F

failure --> transient
failure --> permanent
transient --> restart
permanent --> replace
permanent --> remove

@enduml
```

| Failure Type | Characteristics | Recovery Approach |
|--------------|-----------------|-------------------|
| **Transient** | Node temporarily unavailable, data intact | Wait for restart, hints replay |
| **Recoverable** | Node can restart, possible data issues | Restart + repair |
| **Permanent** | Hardware failed, node cannot return | Replace or remove |

### Failure Detection

Cassandra detects node failures through the gossip protocol's Phi Accrual Failure Detector. When a node stops responding to gossip messages, other nodes independently calculate a suspicion level (φ). Once φ exceeds the configured threshold (default: 8), the node is marked DOWN locally.

Key characteristics:
- **Local determination**: Each node independently decides if a peer is DOWN
- **Not gossiped**: DOWN status is not propagated; each node must observe failure directly
- **Adaptive**: Phi Accrual adjusts to network latency variations

See **[Gossip Protocol](gossip.md)** for failure detection mechanics.

---

## Decision Framework

### Replace vs Remove

When a node permanently fails, the architectural decision between replacement and removal affects cluster capacity, data distribution, and recovery time:

```plantuml
@startuml
skinparam backgroundColor white

title Replace vs Remove Decision

start
#C00000:Node Permanently Failed;

if (Need to maintain\ncluster capacity?) then (Yes)
    if (Have replacement\nhardware available?) then (Yes)
        #70AD47:REPLACE
        New node assumes
        failed node's tokens;
    else (No\n(hardware pending))
        #FFC000:REMOVE now
        ADD new node later;
    endif
else (No\n(reducing capacity))
    #5B9BD5:REMOVE
    Redistribute data
    to remaining nodes;
endif

stop

@enduml
```

### Comparison of Approaches

| Factor | Replace | Remove |
|--------|---------|--------|
| **Cluster capacity** | Maintained | Reduced |
| **Data movement** | Stream to new node only | Redistribute across all remaining nodes |
| **Token ownership** | New node assumes dead node's tokens | Tokens redistributed to existing nodes |
| **Disk usage impact** | Isolated to new node | Increased on all remaining nodes |
| **Time to complete** | Longer (full data stream to one node) | Shorter (parallel redistribution) |
| **Network impact** | Concentrated streaming | Distributed streaming |

### Capacity Constraints

Before choosing an approach, verify capacity constraints:

| Constraint | Replace | Remove |
|------------|---------|--------|
| **Minimum nodes** | N ≥ RF after operation | N - 1 ≥ RF after operation |
| **Disk headroom** | New node needs capacity for its share | Remaining nodes need capacity for redistributed data |
| **Network bandwidth** | Streaming to single node | Parallel streaming between remaining nodes |

---

## Replacement Architecture

### Token Assumption Model

Node replacement operates on the principle of **token assumption**—the new node takes ownership of the failed node's token ranges without redistributing tokens across the cluster:

```plantuml
@startuml
skinparam backgroundColor white

title Token Assumption During Replacement

package "Before Failure" #E8E8E8 {
    rectangle "Token Ring\n\nNode A: tokens 0-33\nNode B: tokens 34-66\nNode C: tokens 67-100" as ring1 #5B9BD5
}

package "Node B Failed" #FFE8E8 {
    rectangle "Token Ring\n\nNode A: tokens 0-33\nNode B: DOWN\nNode C: tokens 67-100" as ring2 #C00000
}

package "After Replacement" #E8F4E8 {
    rectangle "Token Ring\n\nNode A: tokens 0-33\nNode D: tokens 34-66\nNode C: tokens 67-100" as ring3 #70AD47
}

ring1 --> ring2 : failure
ring2 --> ring3 : replace

@enduml
```

**Advantages of token assumption:**
- No token recalculation required
- Other nodes unaffected
- Predictable data movement
- Faster recovery than full rebalance

### Replacement Process Flow

```plantuml
@startuml
skinparam backgroundColor white

title Node Replacement Process

|Preparation|
#5B9BD5:Identify Dead Node
Obtain IP and Host ID;
#5B9BD5:Provision New Node
Same Cassandra version;
#5B9BD5:Configure Replacement
Set replace_address_first_boot;

|Execution|
#C55A11:New Node Starts
Contacts seeds;
#C55A11:Token Assumption
Claims dead node's ranges;
#C55A11:Data Streaming
Receives from replicas;

|Completion|
#70AD47:NORMAL State
Serves client traffic;
#70AD47:Repair
Ensures consistency;

@enduml
```

### Replace Address Mechanism

The `replace_address_first_boot` JVM option instructs a new node to assume a dead node's identity:

| Option | Behavior | Recommendation |
|--------|----------|----------------|
| `replace_address_first_boot` | Cleared after successful first boot | Preferred—prevents accidental re-replacement |
| `replace_address` | Persists across restarts | Legacy—can cause issues on restart |

**Architectural behavior:**
1. New node contacts seeds with replacement intent
2. Cluster validates dead node is actually DOWN
3. New node receives dead node's token assignments
4. Streaming begins from surviving replicas
5. Upon completion, new node announces NORMAL status
6. Dead node's gossip state is eventually purged

### Same-IP vs Different-IP Replacement

| Scenario | Token Handling | Host ID | Configuration |
|----------|---------------|---------|---------------|
| **Same IP** | Assumed from dead node | New ID generated | `replace_address_first_boot` with same IP |
| **Different IP** | Assumed from dead node | New ID generated | `replace_address_first_boot` with dead node's IP |

Both scenarios require the `replace_address_first_boot` option—the IP in the option always refers to the **dead node's address**, regardless of the new node's IP.

---

## Removal Architecture

### Token Redistribution Model

Node removal triggers token redistribution—the dead node's token ranges are reassigned to remaining nodes:

```plantuml
@startuml
skinparam backgroundColor white

title Node Removal - Token Redistribution

start
#5B9BD5:Dead Node Identified
Host ID known;
#5B9BD5:Removal Initiated
From any live node;
#FFC000:Ownership Update
Node removed from ring;
#C55A11:Data Streaming
Between remaining nodes;
#70AD47:Removal Complete
Node purged from ring;
stop

@enduml
```

### Removal vs Decommission

| Aspect | removenode | decommission |
|--------|------------|--------------|
| **Precondition** | Node is DOWN | Node is UP and operational |
| **Initiated from** | Any live node | The departing node itself |
| **Data source** | Remaining replicas stream to each other | Departing node streams its data out |
| **Coordination** | Distributed among remaining nodes | Centralized on departing node |
| **Use case** | Unplanned failure | Planned capacity reduction |

### Assassinate Operation

The `assassinate` operation forcibly removes a node from gossip state without data redistribution:

| Characteristic | Description |
|----------------|-------------|
| **Purpose** | Emergency removal of stuck nodes |
| **Data handling** | None—no streaming occurs |
| **Risk** | Potential data loss if replicas insufficient |
| **Post-action** | Full repair required on all nodes |

**Use only when:**
- Node is unresponsive but not fully DOWN
- `removenode` fails or hangs indefinitely
- Emergency cluster recovery is required

---

## Multiple Failure Scenarios

### Concurrent Failure Analysis

When multiple nodes fail, data availability depends on the relationship between failures and replication:

```plantuml
@startuml
skinparam backgroundColor white

title Multiple Failure Impact Analysis

start
#5B9BD5:Assess Failure Scope
Count failed nodes per token range;

if (Surviving Replicas ≥ 1\nfor all ranges?) then (Yes)
    #70AD47:Data Recoverable
    Sequential replacement possible;
    #70AD47:Replace One at a Time
    Repair between each;
else (No)
    #C00000:Data At Risk
    Backup restoration may be required;
    #C00000:Restore from Backup
    Then rebuild cluster;
endif

stop

@enduml
```

### Quorum Impact Matrix

| Failed Nodes | RF=3 Availability | Recovery Strategy |
|--------------|-------------------|-------------------|
| 1 | QUORUM available (2 of 3) | Standard replacement |
| 2 | ONE available only | Urgent replacement, sequential |
| 3 (same range) | Data unavailable | Backup restoration required |

### Recovery Ordering

When multiple nodes require replacement:

1. **Assess scope**: Identify which token ranges are affected
2. **Prioritize**: Replace nodes affecting most-critical ranges first
3. **Sequential execution**: Complete one replacement before starting next
4. **Repair between**: Run repair after each replacement to ensure consistency
5. **Verify coverage**: Confirm all ranges have sufficient replicas before proceeding

---

## Data Consistency Considerations

### Streaming During Replacement

During replacement, the new node receives data from surviving replicas:

| Source Selection | Criteria |
|------------------|----------|
| **Prefer local DC** | Minimize cross-datacenter traffic |
| **Replica availability** | Select from nodes holding required data |
| **Avoid concurrent streamers** | Prevent resource contention |

### Post-Replacement Consistency

After replacement completes, data consistency may require repair:

| Scenario | Repair Recommendation |
|----------|----------------------|
| Short downtime (< hint window) | Hints cover gap; repair optional |
| Extended downtime (> hint window) | Repair required for missed writes |
| Multiple failures | Full repair recommended |
| Consistency-critical data | Always run repair |

The hint window (default: 3 hours) determines whether hinted handoff can cover writes during downtime. Beyond this window, hints expire and repair becomes necessary.

---

## Related Documentation

- **[Node Lifecycle](node-lifecycle.md)** - Bootstrap, decommission, and state transitions
- **[Gossip Protocol](gossip.md)** - Failure detection mechanics
- **[Data Streaming](../distributed-data/streaming.md)** - Streaming architecture during replacement
- **[Scaling Operations](scaling.md)** - Capacity planning after node removal
- **[Fault Tolerance](../fault-tolerance/index.md)** - Failure scenarios and recovery patterns
- **[Operations: Cluster Management](../../operations/cluster-management/index.md)** - Step-by-step procedures
