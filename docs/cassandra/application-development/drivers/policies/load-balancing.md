# Load Balancing Policy

The load balancing policy determines which nodes receive requests. This policy directly affects latency, throughput, and cluster load distribution.

---

## How Load Balancing Works

For each request, the load balancing policy returns an ordered list of nodes to try:

```graphviz dot load-balancing-query-plan.svg
digraph QueryPlan {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Load Balancing Query Plan";
    labelloc="t";
    fontsize=12;

    request [shape=box, style="rounded,filled", fillcolor="#E8E8E8",
        label="Request:\nSELECT * FROM users\nWHERE user_id = 'abc123'"];

    policy [shape=box, style="rounded,filled", fillcolor="#FFE8CC",
        label="Load Balancing Policy Evaluates:\n1. Which nodes are replicas?\n2. Which nodes are in local DC?\n3. Which nodes are healthy?\n4. How to order nodes?"];

    subgraph cluster_plan {
        label="Query Plan (ordered)";
        style="rounded,filled";
        fillcolor="#E8F4E8";
        color="#99CC99";

        subgraph cluster_replicas {
            label="Replicas (preferred)";
            style="rounded,filled";
            fillcolor="#D4EDDA";
            color="#28A745";

            n2 [shape=box, style="rounded,filled", fillcolor="#7B4B96", fontcolor="white", label="1. Node2"];
            n5 [shape=box, style="rounded,filled", fillcolor="#7B4B96", fontcolor="white", label="2. Node5"];
        }

        subgraph cluster_fallback {
            label="Non-replicas (fallback)";
            style="rounded,filled";
            fillcolor="#FFF3CD";
            color="#FFC107";

            n1 [shape=box, style="rounded,filled", fillcolor="#6C757D", fontcolor="white", label="3. Node1"];
            n3 [shape=box, style="rounded,filled", fillcolor="#6C757D", fontcolor="white", label="4. Node3"];
            n6 [shape=box, style="rounded,filled", fillcolor="#6C757D", fontcolor="white", label="5. Node6"];
        }
    }

    request -> policy;
    policy -> n2 [style=invis];
}
```

The driver sends the request to the first node. If that fails and the retry policy allows retry, the next node in the list is tried.

---

## Token-Aware Routing

Token-aware load balancing sends requests directly to replica nodes, avoiding an extra network hop:

```graphviz dot token-aware-comparison.svg
digraph TokenAware {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=LR;
    newrank=true;

    label="Token-Aware Routing Comparison";
    labelloc="t";
    fontsize=12;

    subgraph cluster_without {
        label="Without Token-Aware\n(2 network hops)";
        style="rounded,filled";
        fillcolor="#FFE8E8";
        color="#CC9999";

        app1 [shape=box, style="rounded,filled", fillcolor="#E8E8E8", label="Application"];
        coord [shape=box, style="rounded,filled", fillcolor="#FFE8CC", label="Node1\n(coordinator)"];
        replica1 [shape=box, style="rounded,filled", fillcolor="#7B4B96", fontcolor="white", label="Node3\n(coordinator/replica)"];

        app1 -> coord [label="1. request"];
        coord -> replica1 [label="2. forward"];
        replica1 -> coord [label="3. response", style=dashed];
        coord -> app1 [label="4. response", style=dashed];
    }

    subgraph cluster_with {
        label="With Token-Aware\n(1 network hop)";
        style="rounded,filled";
        fillcolor="#E8F4E8";
        color="#99CC99";

        app2 [shape=box, style="rounded,filled", fillcolor="#E8E8E8", label="Application"];
        replica2 [shape=box, style="rounded,filled", fillcolor="#7B4B96", fontcolor="white", label="Node3\n(replica)"];

        app2 -> replica2 [label="1. request"];
        replica2 -> app2 [label="2. response", style=dashed];
    }
}
```

### Requirements for Token-Aware Routing

Token-aware routing requires:

1. **Partition key known** — The driver must be able to extract the partition key from the query
2. **Prepared statements** — Simple statements without bound parameters cannot be routed token-aware
3. **Metadata available** — Driver must have current token map

```java
// Token-aware: partition key is bound
PreparedStatement prepared = session.prepare(
    "SELECT * FROM users WHERE user_id = ?");
BoundStatement bound = prepared.bind(userId);  // Driver knows partition key
session.execute(bound);  // Routes to replica

// NOT token-aware: partition key embedded in query string
SimpleStatement simple = SimpleStatement.newInstance(
    "SELECT * FROM users WHERE user_id = 'abc123'");
session.execute(simple);  // Cannot extract partition key, uses round-robin
```

---

## Datacenter Awareness

In multi-datacenter deployments, the load balancing policy must be configured with the local datacenter:

```graphviz dot datacenter-aware-routing.svg
digraph DatacenterAware {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;
    compound=true;

    label="Datacenter-Aware Routing";
    labelloc="t";
    fontsize=12;

    app [shape=box, style="rounded,filled", fillcolor="#E8E8E8",
        label="Application\n(configured: local_dc = \"dc1\")"];

    subgraph cluster_dc1 {
        label="DC1 (local)\nLatency: ~1ms";
        style="rounded,filled";
        fillcolor="#E8F4E8";
        color="#28A745";

        n1 [shape=box, style="rounded,filled", fillcolor="#7B4B96", fontcolor="white", label="Node1"];
        n2 [shape=box, style="rounded,filled", fillcolor="#7B4B96", fontcolor="white", label="Node2"];
        n3 [shape=box, style="rounded,filled", fillcolor="#7B4B96", fontcolor="white", label="Node3"];
    }

    subgraph cluster_dc2 {
        label="DC2 (remote)\nLatency: ~50ms";
        style="rounded,filled";
        fillcolor="#FFF3CD";
        color="#FFC107";

        n4 [shape=box, style="rounded,filled", fillcolor="#6C757D", fontcolor="white", label="Node4"];
        n5 [shape=box, style="rounded,filled", fillcolor="#6C757D", fontcolor="white", label="Node5"];
        n6 [shape=box, style="rounded,filled", fillcolor="#6C757D", fontcolor="white", label="Node6"];
    }

    app -> n1 [label="requests", lhead=cluster_dc1, penwidth=2];
    app -> n4 [label="fallback only", style=dashed, lhead=cluster_dc2];

    note [shape=box, style="rounded,filled", fillcolor="#F8F9FA",
        label="Local DC nodes always preferred.\nRemote DC used only if all local nodes unavailable."];

    n3 -> note [style=invis];
    n6 -> note [style=invis];
}
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

This is the default and recommended policy for most production deployments.

---

## Rack Awareness

Some load balancing policies consider rack placement to improve fault tolerance:

```graphviz dot rack-awareness.svg
digraph RackAware {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Rack-Aware Replica Selection";
    labelloc="t";
    fontsize=12;

    app [shape=box, style="rounded,filled", fillcolor="#E8E8E8",
        label="Application\n(in rack-a)"];

    subgraph cluster_racks {
        label="Replicas for partition";
        style="rounded,filled";
        fillcolor="#F8F9FA";

        subgraph cluster_racka {
            label="rack-a";
            style="rounded,filled";
            fillcolor="#E8F4E8";
            color="#28A745";

            n1 [shape=box, style="rounded,filled", fillcolor="#7B4B96", fontcolor="white",
                label="Node1\n(1st choice)"];
        }

        subgraph cluster_rackb {
            label="rack-b";
            style="rounded,filled";
            fillcolor="#FFF3CD";

            n2 [shape=box, style="rounded,filled", fillcolor="#6C757D", fontcolor="white",
                label="Node2\n(2nd choice)"];
        }

        subgraph cluster_rackc {
            label="rack-c";
            style="rounded,filled";
            fillcolor="#FFF3CD";

            n3 [shape=box, style="rounded,filled", fillcolor="#6C757D", fontcolor="white",
                label="Node3\n(3rd choice)"];
        }
    }

    app -> n1 [label="same rack\n(lowest latency)", penwidth=2];
    app -> n2 [style=dashed];
    app -> n3 [style=dashed];
}
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

```graphviz dot latency-aware.svg
digraph LatencyAware {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=LR;

    label="Latency-Aware Node Selection";
    labelloc="t";
    fontsize=12;

    driver [shape=box, style="rounded,filled", fillcolor="#E8E8E8", label="Driver\n(tracks latency)"];

    n1 [shape=box, style="rounded,filled", fillcolor="#28A745", fontcolor="white",
        label="Node1\navg: 2ms\n(preferred)"];
    n2 [shape=box, style="rounded,filled", fillcolor="#FFC107", fontcolor="black",
        label="Node2\navg: 5ms"];
    n3 [shape=box, style="rounded,filled", fillcolor="#DC3545", fontcolor="white",
        label="Node3\navg: 15ms\n(deprioritized)"];

    driver -> n1 [label="1st", penwidth=2];
    driver -> n2 [label="2nd"];
    driver -> n3 [label="3rd", style=dashed];
}
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

