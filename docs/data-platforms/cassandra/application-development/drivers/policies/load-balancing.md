---
title: "Cassandra Driver Load Balancing Policy"
description: "Cassandra load balancing policies. Configure token-aware, data center-aware, and round-robin routing."
meta:
  - name: keywords
    content: "Cassandra load balancing, token-aware, DC-aware, round-robin"
---

# Load Balancing Policy

The load balancing policy determines which nodes receive requests. This policy directly affects latency, throughput, and cluster load distribution.

---

## How Load Balancing Works

For each request, the load balancing policy returns an ordered list of nodes to try:

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Load Balancing Query Plan

rectangle "Request:\nSELECT * FROM users\nWHERE user_id = 'abc123'" as request #E8E8E8

rectangle "Load Balancing Policy Evaluates:\n1. Which nodes are replicas?\n2. Which nodes are in local DC?\n3. Which nodes are healthy?\n4. How to order nodes?" as policy #FFE8CC

package "Query Plan (ordered)" #E8F4E8 {
    package "Replicas (preferred)" #D4EDDA {
        rectangle "1. Node2" as n2 #7B4B96
        rectangle "2. Node5" as n5 #7B4B96
    }
    package "Non-replicas (fallback)" #FFF3CD {
        rectangle "3. Node1" as n1 #6C757D
        rectangle "4. Node3" as n3 #6C757D
        rectangle "5. Node6" as n6 #6C757D
    }
}

request --> policy
policy --> n2

@enduml
```

The driver sends the request to the first node. If that fails and the retry policy allows retry, the next node in the list is tried.

---

## Token-Aware Routing

Token-aware load balancing sends requests directly to replica nodes, avoiding an extra network hop:

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Token-Aware Routing Comparison

rectangle "Without Token-Aware (2 network hops)" #FFE8E8 {
    rectangle "Application" as app1 #E8E8E8
    rectangle "Node1\n(coordinator)" as coord #FFE8CC
    rectangle "Node3\n(replica)" as replica1 #7B4B96

    app1 -> coord : 1. request
    coord -> replica1 : 2. forward
    replica1 --> coord : 3. response
    coord --> app1 : 4. response
}

rectangle "With Token-Aware (1 network hop)" #E8F4E8 {
    rectangle "Application" as app2 #E8E8E8
    rectangle "Node3\n(replica)" as replica2 #7B4B96

    app2 -> replica2 : 1. request
    replica2 --> app2 : 2. response
}

@enduml
```

### Requirements for Token-Aware Routing

Token-aware routing requires:

1. **Routing key available** — The driver must be able to determine the partition key value
2. **Metadata available** — Driver must have current token map

The routing key can be provided via:

- **Prepared statements with bound values** (most common)
- **Simple statements with explicit routing key set**
- **Simple statements with bound values** (driver may infer routing key)

```java
// Token-aware: prepared statement with bound partition key
PreparedStatement prepared = session.prepare(
    "SELECT * FROM users WHERE user_id = ?");
BoundStatement bound = prepared.bind(userId);  // Driver knows partition key
session.execute(bound);  // Routes to replica

// Token-aware: simple statement with explicit routing key
SimpleStatement simple = SimpleStatement.builder(
    "SELECT * FROM users WHERE user_id = 'abc123'")
    .setRoutingKey(TypeCodecs.UUID.encode(userId, ProtocolVersion.V4))
    .build();
session.execute(simple);  // Routes to replica

// NOT token-aware: literal values without routing key metadata
SimpleStatement unrouted = SimpleStatement.newInstance(
    "SELECT * FROM users WHERE user_id = 'abc123'");
session.execute(unrouted);  // Driver cannot extract partition key, uses round-robin
```

---

## Datacenter Awareness

In multi-datacenter deployments, the load balancing policy must be configured with the local datacenter:

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Datacenter-Aware Routing

rectangle "Application\n(configured: local_dc = \"dc1\")" as app #E8E8E8

package "DC1 (local) - Latency: ~1ms" #E8F4E8 {
    rectangle "Node1" as n1 #7B4B96
    rectangle "Node2" as n2 #7B4B96
    rectangle "Node3" as n3 #7B4B96
}

package "DC2 (remote) - Latency: ~50ms" #FFF3CD {
    rectangle "Node4" as n4 #6C757D
    rectangle "Node5" as n5 #6C757D
    rectangle "Node6" as n6 #6C757D
}

app --> n1 : requests
app --> n2
app --> n3
app ..> n4 : fallback only
app ..> n5
app ..> n6

note bottom of n6
  Local DC nodes preferred.
  Remote DC usage depends on policy configuration.
end note

@enduml
```

### Configuration

```java
// Java driver
CqlSession session = CqlSession.builder()
    .withLocalDatacenter("dc1")
    .build();
```

```python
# Python driver
from cassandra.policies import DCAwareRoundRobinPolicy
cluster = Cluster(
    contact_points=['10.0.1.1'],
    load_balancing_policy=DCAwareRoundRobinPolicy(local_dc='dc1')
)
```

**Failure to configure local datacenter correctly results in requests potentially routing to remote datacenters with significantly higher latency.**

---

## Common Load Balancing Policies

### Round-Robin (Basic)

Distributes requests evenly across all nodes without considering replicas:

| Advantage | Disadvantage |
|-----------|--------------|
| Simple, predictable | Extra network hop for every request |
| Even distribution | No datacenter awareness |

Use case: Development environments, specific analytics workloads.

### Datacenter-Aware Round-Robin

Round-robin within local datacenter only:

| Advantage | Disadvantage |
|-----------|--------------|
| Respects datacenter locality | Still not token-aware |
| Predictable distribution within DC | Extra hop for most requests |

Use case: When token-aware routing is not possible (e.g., many simple statements).

### Token-Aware with DC Awareness (Recommended)

Combines token-aware routing with datacenter preference:

```
Algorithm:
1. Calculate replica set for partition key
2. Filter to local datacenter replicas
3. Order by health/load (implementation varies)
4. Append non-replica local nodes as fallback
5. Optionally append remote DC nodes as last resort
```

| Advantage | Disadvantage |
|-----------|--------------|
| Minimum latency (direct to replica) | Requires prepared statements for full benefit |
| Respects datacenter locality | Slightly more complex configuration |
| Built-in fallback ordering | |

This combination is commonly used for production deployments. Verify the default behavior for the specific driver version in use.

---

## Rack Awareness

Some load balancing policies consider rack placement to improve fault tolerance:

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Rack-Aware Replica Selection

rectangle "Application\n(in rack-a)" as app #E8E8E8

package "Replicas for partition" #F8F9FA {
    package "rack-a" #E8F4E8 {
        rectangle "Node1\n(1st choice)" as n1 #7B4B96
    }

    package "rack-b" #FFF3CD {
        rectangle "Node2\n(2nd choice)" as n2 #6C757D
    }

    package "rack-c" #FFF3CD {
        rectangle "Node3\n(3rd choice)" as n3 #6C757D
    }
}

app --> n1 : same rack\n(lowest latency)
app .[#gray,dashed].> n2
app .[#gray,dashed].> n3

@enduml
```

Rack awareness provides marginal latency improvement when:

- Application servers are rack-aligned with Cassandra nodes
- Network topology has rack-level latency differences

---

## Filtering Unhealthy Nodes

Load balancing policies typically exclude nodes that are:

| Condition | Behavior |
|-----------|----------|
| Marked DOWN | Excluded from query plan |
| Recently failed | May be deprioritized (implementation varies) |
| High latency | Some policies track latency and avoid slow nodes |
| Overloaded | Some policies consider in-flight request count |

### Latency-Aware Routing

Some drivers offer latency-aware policies that track response times and prefer faster nodes:

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Latency-Aware Node Selection

left to right direction

rectangle "Driver\n(tracks latency)" as driver #E8E8E8

rectangle "Node1\navg: 2ms\n(preferred)" as n1 #28A745
rectangle "Node2\navg: 5ms" as n2 #FFC107
rectangle "Node3\navg: 15ms\n(deprioritized)" as n3 #DC3545

driver --> n1 : 1st
driver --> n2 : 2nd
driver .[#gray,dashed].> n3 : 3rd

@enduml
```

Considerations:

- Latency tracking adds overhead
- May cause herding (all clients avoid same node simultaneously)
- Typically combined with, not replacing, token-aware routing

---

## Configuration Recommendations

| Deployment | Recommended Policy |
|------------|-------------------|
| Single datacenter | Token-aware with round-robin fallback |
| Multi-datacenter | Token-aware with DC awareness |
| Analytics/batch | Round-robin or DC-aware round-robin |
| Latency-sensitive | Token-aware with latency tracking |

### Anti-Patterns

| Anti-Pattern | Problem |
|--------------|---------|
| No local DC configured in multi-DC | Requests may route cross-DC |
| Round-robin for OLTP workloads | Unnecessary latency for every request |
| Token-aware without prepared statements | Falls back to round-robin anyway |

---

## Related Documentation

- **[Retry Policy](retry.md)** — What happens when the selected node fails
- **[Speculative Execution](speculative-execution.md)** — Sending to multiple nodes concurrently
