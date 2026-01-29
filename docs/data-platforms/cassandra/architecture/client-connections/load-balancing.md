---
title: "Cassandra Load Balancing Policies"
description: "Client-side load balancing in Cassandra drivers. Token-aware routing and datacenter awareness."
meta:
  - name: keywords
    content: "load balancing, token-aware routing, datacenter aware, Cassandra driver"
---

# Load Balancing Policies

Load balancing policies determine how drivers select coordinator nodes for each request. The choice of policy significantly impacts latency, throughput, and resource utilization across the cluster.

---

## Client-Side Load Balancing

### No External Load Balancer Required

Unlike traditional RDBMS architectures where applications connect through a load balancer (HAProxy, F5, PgBouncer, etc.), Cassandra drivers perform load balancing internally:

```plantuml
@startuml
skinparam backgroundColor transparent
title Traditional RDBMS vs Cassandra Connection Model

skinparam rectangle {
    BackgroundColor #7B4B96
    FontColor white
    BorderColor #5A3670
    roundCorner 10
}

package "Traditional RDBMS" as RDBMS #FFCDD2 {
    rectangle "Application" as App1
    rectangle "Load Balancer\n(HAProxy/F5)" as LB
    rectangle "DB Primary" as Primary
    rectangle "DB Replica" as Replica1
    rectangle "DB Replica" as Replica2

    App1 -down-> LB
    LB -down-> Primary
    LB -down-> Replica1
    LB -down-> Replica2

    note bottom of LB
      Single point of failure
      Additional latency hop
      Complex failover config
    end note
}

package "Cassandra" as Cass #E8F5E9 {
    rectangle "Application\n+ Driver" as App2
    rectangle "Node 1" as N1
    rectangle "Node 2" as N2
    rectangle "Node 3" as N3
    rectangle "Node 4" as N4

    App2 -down-> N1
    App2 -down-> N2
    App2 -down-> N3
    App2 -down-> N4

    note bottom of App2
      Driver connects directly
      to all nodes
      No intermediary required
    end note
}
@enduml
```

**Problems with External Load Balancers for Distributed Databases:**

| Issue | Impact |
|-------|--------|
| Single point of failure | Load balancer outage = total outage |
| Additional network hop | 0.5-2ms added latency per request |
| No data locality awareness | Cannot route to replica nodes |
| Connection pooling conflicts | LB pools vs driver pools |
| Health check limitations | Cannot assess Cassandra-specific health |
| Cost and complexity | Additional infrastructure to manage |

### Driver Bootstrap Process

When a Cassandra driver initializes, it performs cluster discovery automatically:

```plantuml
@startuml
skinparam backgroundColor transparent
title Driver Bootstrap and Cluster Discovery

skinparam sequence {
    ParticipantBackgroundColor #7B4B96
    ParticipantFontColor white
    ArrowColor #5A3670
}

participant "Application" as App
participant "Driver" as D
participant "Contact Point\n(Node 1)" as CP
participant "Node 2" as N2
participant "Node 3" as N3

== Initialization ==
App -> D: create Session(contact_points=[node1])

== Discovery ==
D -> CP: Connect
D -> CP: QUERY system.local
CP --> D: Node 1 info, cluster_name, partitioner
D -> CP: QUERY system.peers
CP --> D: [Node 2, Node 3, ...] with tokens, DC, rack

== Connection Pool Setup ==
D -> N2: Connect
D -> N3: Connect
D -> CP: Maintain connection
note right: Driver now has\nconnections to ALL nodes

== Metadata Sync ==
D -> D: Build token ring map
D -> D: Initialize load balancing policy

== Ready ==
D --> App: Session ready
@enduml
```

**Bootstrap Steps:**

1. **Contact point connection**: Driver connects to one or more seed addresses provided in configuration
2. **Cluster discovery**: Queries `system.local` and `system.peers` tables to discover all nodes
3. **Metadata retrieval**: Obtains token assignments, datacenter/rack topology, schema information
4. **Connection establishment**: Opens connection pools to all discovered nodes (based on distance policy)
5. **Token ring construction**: Builds internal map of token ranges to nodes for data-aware routing

!!! info "Contact Points Are Not Special"
    Contact points are only used for initial discovery. After bootstrap, the driver treats all nodes equally. If a contact point goes down, the driver continues operating with other nodes. Provide multiple contact points for bootstrap resilience.

### Direct Node Connections

After bootstrap, the driver maintains persistent connections to cluster nodes:

```plantuml
@startuml
skinparam backgroundColor transparent
title Driver Connection State (9 nodes across 3 datacenters)

package "DC1 (LOCAL)" #E8F5E9 {
    database "Node1\n8 conn" as N1
    database "Node2\n8 conn" as N2
    database "Node3\n8 conn" as N3
}

package "DC2 (REMOTE)" #FFF3E0 {
    database "Node4\n2 conn" as N4
    database "Node5\n2 conn" as N5
    database "Node6\n2 conn" as N6
}

package "DC3 (IGNORED)" #FFEBEE {
    database "Node7\n0 conn" as N7
    database "Node8\n0 conn" as N8
    database "Node9\n0 conn" as N9
}

note bottom of N1
  LOCAL: 8 connections/node (24 total)
end note

note bottom of N4
  REMOTE: 2 connections/node (12 total)
end note

note bottom of N7
  IGNORED: 0 connections
end note
@enduml
```

**Benefits of Direct Connections:**

| Benefit | Description |
|---------|-------------|
| No single point of failure | Any node can serve any request |
| Optimal latency | Direct path, no intermediary hop |
| Data-aware routing | Driver routes to replica nodes |
| Automatic failover | Instant reroute on node failure |
| Topology awareness | Respects datacenter boundaries |
| Dynamic scaling | New nodes discovered automatically |

### Load Balancing Policy Role

The load balancing policy determines request routing after connections are established:

```plantuml
@startuml
skinparam backgroundColor transparent
title Request Routing with Load Balancing Policy

skinparam ActivityBackgroundColor #F9E5FF
skinparam ActivityBorderColor #7B4B96
skinparam ActivityDiamondBackgroundColor #E8F5E9
skinparam ActivityDiamondBorderColor #4CAF50

start

:Application executes query;

:Load Balancing Policy\nevaluates request;

if (Token-aware enabled\nand partition key known?) then (yes)
    :Calculate partition token;
    :Identify replica nodes;
    :Return replicas first,\nthen other nodes;
else (no)
    if (DC-aware enabled?) then (yes)
        :Return local DC nodes first,\nthen remote DC nodes;
    else (no)
        :Return all nodes\nin round-robin order;
    endif
endif

:Driver sends to first\navailable node in plan;

if (Request succeeds?) then (yes)
    :Return result;
else (no)
    :Try next node in plan;
endif

stop
@enduml
```

!!! tip "Recommended Production Configuration"
    For most production deployments, use Token-Aware policy wrapping DC-Aware Round Robin:
    ```
    TokenAwarePolicy(DCAwareRoundRobinPolicy(local_dc="dc1"))
    ```
    This routes directly to replica nodes when possible, falls back to local DC round-robin, and only uses remote DCs as a last resort.

---

## Load Balancing Overview

### Role of the Coordinator

Every CQL request is sent to a coordinator node that:

1. Receives the request from the client
2. Determines which replicas hold the data
3. Forwards requests to replicas
4. Collects and aggregates responses
5. Returns results to the client

The load balancing policy selects this coordinator.

### Selection Criteria

| Criterion | Benefit |
|-----------|---------|
| Data locality | Reduces network hops |
| Node health | Avoids failing nodes |
| Load distribution | Prevents hot spots |
| Datacenter proximity | Minimizes latency |
| Connection availability | Uses ready connections |

---

## Policy Architecture

### Policy Interface

Load balancing policies implement a common interface:

```python
# Conceptual interface
class LoadBalancingPolicy:
    def initialize(self, cluster):
        """Called when driver initializes with cluster metadata"""
        pass

    def distance(self, host):
        """Return distance classification for host"""
        # Returns: LOCAL, REMOTE, or IGNORED
        pass

    def new_query_plan(self, keyspace, statement):
        """Return iterator of hosts to try for this query"""
        pass

    def on_add(self, host):
        """Called when node joins cluster"""
        pass

    def on_remove(self, host):
        """Called when node leaves cluster"""
        pass

    def on_up(self, host):
        """Called when node becomes available"""
        pass

    def on_down(self, host):
        """Called when node becomes unavailable"""
        pass
```

### Query Plan

The query plan is an ordered sequence of nodes to try:

```plantuml
@startuml
skinparam backgroundColor transparent

participant "Driver" as D
participant "Policy" as P
participant "Node A" as A
participant "Node B" as B
participant "Node C" as C

D -> P: new_query_plan(query)
P --> D: [A, B, C]
D -> A: execute
A --> D: Timeout
D -> B: retry
B --> D: Success

@enduml
```

---

## Built-in Policies

### Round Robin

Distributes requests evenly across all nodes:

```plantuml
@startuml
skinparam backgroundColor transparent

rectangle "Round Robin Query Plans" {
    card "Query 1: [**A**, B, C, D]" as Q1
    card "Query 2: [**B**, C, D, A]" as Q2
    card "Query 3: [**C**, D, A, B]" as Q3
    card "Query 4: [**D**, A, B, C]" as Q4
}

Q1 -[hidden]down-> Q2
Q2 -[hidden]down-> Q3
Q3 -[hidden]down-> Q4

note right of Q1 : Position advances\neach query
@enduml
```

**Characteristics:**

- Simple, predictable distribution
- No awareness of data location
- Good for uniform workloads

!!! info "Not Recommended for Production"
    Round Robin policy ignores data locality and datacenter topology. For production deployments, use DC-aware or Token-aware policies instead.

**Implementation:**
```python
class RoundRobinPolicy:
    def __init__(self):
        self.hosts = []
        self.index = 0

    def new_query_plan(self, keyspace, statement):
        hosts = list(self.hosts)
        start = self.index
        self.index = (self.index + 1) % len(hosts)

        # Rotate to start position
        return hosts[start:] + hosts[:start]
```

### DC-Aware Round Robin

Prioritizes nodes in the local datacenter:

```plantuml
@startuml
skinparam backgroundColor transparent

package "dc1 (local)" #E8F5E9 {
    card "A" as A
    card "B" as B
    card "C" as C
}

package "dc2 (remote)" #FFF3E0 {
    card "D" as D
    card "E" as E
    card "F" as F
}

card "Query Plan: [A, B, C, D, E, F]" as plan #E3F2FD

A -down-> plan
B -down-> plan
C -down-> plan
D -down-> plan
E -down-> plan
F -down-> plan

note bottom of plan : Local DC nodes first,\nthen remote DC nodes
@enduml
```

**Configuration:**
| Parameter | Description |
|-----------|-------------|
| local_dc | Preferred datacenter name |
| used_hosts_per_remote_dc | Remote hosts to include (0 = none) |

**Implementation Logic:**
```python
class DCAwareRoundRobinPolicy:
    def distance(self, host):
        if host.datacenter == self.local_dc:
            return DISTANCE_LOCAL
        elif self.used_hosts_per_remote_dc > 0:
            return DISTANCE_REMOTE
        else:
            return DISTANCE_IGNORED

    def new_query_plan(self, keyspace, statement):
        local = self.get_local_hosts()
        remote = self.get_remote_hosts()

        # Round-robin within local, then remote
        plan = rotate(local, self.local_index)
        if self.used_hosts_per_remote_dc > 0:
            plan.extend(rotate(remote, self.remote_index))

        return plan
```

### Token-Aware Policy

Routes requests directly to replica nodes:

```plantuml
@startuml
skinparam backgroundColor transparent

participant "Driver" as D
participant "Token Policy" as P
participant "Metadata" as M
participant "Replica A" as A
participant "Non-Replica X" as X

D -> P: new_query_plan(query with partition key)
P -> M: get_replicas(partition_key)
M --> P: [A, B, C]
P --> D: [A, B, C, X, Y, Z]
note right: Replicas first,\nthen other nodes
D -> A: execute
note right: Direct to data owner

@enduml
```

**How Token Awareness Works:**

1. Driver calculates partition token from query
2. Looks up token → replica mapping
3. Places replicas first in query plan
4. Falls back to non-replicas if all fail

**Requirements:**
- Partition key must be known (bound values available)
- Metadata must be synchronized
- Typically wraps another policy for non-token-aware queries

**Partition Key Detection:**

| Query Type | Token Calculable |
|------------|------------------|
| Prepared with PK bound | Yes |
| Simple with PK literal | Sometimes (parsing required) |
| Range queries | No |
| Queries without WHERE | No |

!!! tip "Use Prepared Statements for Token Awareness"
    Token-aware routing works best with prepared statements, which provide partition key metadata. Simple string queries may not benefit from token awareness.

### Latency-Aware Policy

Prefers nodes with lower observed latency:

```plantuml
@startuml
skinparam backgroundColor transparent

rectangle "Latency Tracking" {
    card "Node A\navg 2ms" as A #C8E6C9
    card "Node C\navg 3ms" as C #FFF9C4
    card "Node B\navg 5ms" as B #FFCDD2
}

card "Query Plan: [A, C, B]" as plan #E3F2FD

A -down-> plan : 1st
C -down-> plan : 2nd
B -down-> plan : 3rd

note bottom of plan : Ordered by observed latency\n(fastest first)
@enduml
```

**Characteristics:**
- Adapts to network conditions
- Helps with heterogeneous hardware
- May create hot spots on fast nodes

**Configuration:**
| Parameter | Description |
|-----------|-------------|
| exclusion_threshold | Latency multiplier to exclude (e.g., 2.0) |
| scale | Time scale for averaging (e.g., 100ms) |
| retry_period | How often to retry excluded nodes |
| update_rate | Latency sample rate |

---

## Policy Composition

### Wrapping Policies

Policies can wrap other policies to add behavior:

```plantuml
@startuml
skinparam backgroundColor transparent

rectangle "TokenAwarePolicy" #E8F5E9 {
    rectangle "DCAwareRoundRobinPolicy\n(local_dc=\"dc1\")" #FFF3E0
}

note right of "TokenAwarePolicy"
  1. TokenAwarePolicy adds replicas first
  2. DCAwareRoundRobinPolicy orders remaining by DC
end note
@enduml
```

### Common Compositions

| Composition | Use Case |
|-------------|----------|
| Token(DCRoundRobin) | Standard production setup |
| Token(LatencyAware(DCRoundRobin)) | Latency-sensitive apps |
| DCRoundRobin only | When token calculation expensive |
| RoundRobin only | Single-DC, uniform access |

---

## Distance Classification

### Distance Types

Policies classify nodes by distance:

| Distance | Meaning | Connection Behavior |
|----------|---------|---------------------|
| LOCAL | Primary preference | Full connection pool |
| REMOTE | Secondary preference | Reduced pool size |
| IGNORED | Never use | No connections |

### Distance Impact

```yaml
# Typical pool configuration
connection_pool:
  local:
    core_connections: 2
    max_connections: 8
  remote:
    core_connections: 1
    max_connections: 2
```

---

## Multi-Datacenter Considerations

### Local-Only Access

For applications that should never cross datacenters:

```python
DCAwareRoundRobinPolicy(
    local_dc="dc1",
    used_hosts_per_remote_dc=0  # Never use remote
)
```

**Implications:**
- Lower latency (no cross-DC)
- Reduced availability (local failures = unavailable)
- Required for some compliance scenarios

### Remote Fallback

Allow falling back to remote datacenters:

```python
DCAwareRoundRobinPolicy(
    local_dc="dc1",
    used_hosts_per_remote_dc=2  # Include 2 per remote DC
)
```

**Implications:**
- Higher availability
- Possible high-latency responses
- Cross-DC traffic costs

### Multi-Region Writes

For write operations spanning regions:

```
Consistency Level: LOCAL_QUORUM
- Only requires quorum in local DC
- Async replication to remote DCs
- Lowest write latency

Consistency Level: EACH_QUORUM
- Requires quorum in every DC
- Higher latency
- Stronger consistency
```

---

## Node State Handling

### State Transitions

```plantuml
@startuml
skinparam backgroundColor transparent

state "UP" as U
state "DOWN" as D
state "UNKNOWN" as X

[*] --> X : Initial
X --> U : Connection succeeds
X --> D : Connection fails
U --> D : on_down event
D --> U : on_up event
U --> D : Connection errors

@enduml
```

### Reconnection Behavior

When a node goes down:

```plantuml
@startuml
skinparam backgroundColor transparent

start
:Node failure detected;
:Mark node DOWN;
:Remove from query plans;

repeat
  :Wait (exponential backoff:\n1s, 2s, 4s, ... 60s max);
  :Attempt reconnection;
repeat while (Connection failed?) is (yes)
->no;

:Mark node UP;
:Include in query plans;
stop
@enduml
```

### Speculative Awareness

Load balancing interacts with speculative execution:

```plantuml
@startuml
skinparam backgroundColor transparent

concise "Node A" as A
concise "Node B" as B
concise "Client" as C

@0
C is "Send to A"
A is "Processing"

@50
C is "Spec. send to B"
B is "Processing"

@70
A is "Response"
C is "Use A's response"

@80
B is "Response (ignored)"

@enduml
```

---

## Query Routing Optimization

### Token Calculation

For token-aware routing, drivers calculate partition tokens:

```python
def calculate_token(partition_key, partitioner):
    # Murmur3Partitioner (default)
    if partitioner == "Murmur3Partitioner":
        return murmur3_hash(partition_key)

    # RandomPartitioner (legacy)
    elif partitioner == "RandomPartitioner":
        return md5_hash(partition_key)
```

### Metadata Synchronization

Token awareness requires current metadata:

```plantuml
@startuml
skinparam backgroundColor transparent

rectangle "Driver Metadata" #E3F2FD {
    card "Token → Host mapping" as t
    card "Keyspace → Replication strategy" as k
    card "Table → Partition key definition" as p
}

rectangle "Refresh Triggers" #FFF3E0 {
    card "Topology change event" as e1
    card "Schema change event" as e2
    card "Periodic refresh (optional)" as e3
    card "Manual refresh" as e4
}

e1 --> t
e2 --> k
e2 --> p
e3 --> t
e4 --> t
@enduml
```

### Prepared Statement Optimization

Prepared statements enable better routing:

```python
# Without preparation - must parse query
session.execute("SELECT * FROM users WHERE id = 12345")
# Parsing may not extract partition key

# With preparation - routing info cached
stmt = session.prepare("SELECT * FROM users WHERE id = ?")
session.execute(stmt, [12345])
# Driver knows exactly which partition
```

---

## Custom Policies

### When to Customize

Custom policies for:
- Special routing requirements
- Custom health checks
- Workload-specific distribution
- Integration with external systems

### Implementation Guidelines

```python
class CustomLoadBalancingPolicy:
    def __init__(self, config):
        self.config = config

    def initialize(self, cluster):
        # Store reference for metadata access
        self.cluster = cluster
        self.hosts = set()

    def distance(self, host):
        # Classify based on custom criteria
        if self.is_preferred(host):
            return DISTANCE_LOCAL
        elif self.is_acceptable(host):
            return DISTANCE_REMOTE
        else:
            return DISTANCE_IGNORED

    def new_query_plan(self, keyspace, statement):
        # Build ordered list based on:
        # - Data locality
        # - Node health
        # - Custom metrics
        # - Business rules
        return self.order_hosts(statement)

    def on_up(self, host):
        self.hosts.add(host)

    def on_down(self, host):
        # Don't remove immediately - allow recovery
        pass

    def on_remove(self, host):
        self.hosts.discard(host)
```

---

## Performance Considerations

### Policy Overhead

| Policy | Overhead per Query |
|--------|-------------------|
| Round Robin | O(1) |
| DC-Aware | O(1) |
| Token-Aware | O(log n) token lookup |
| Latency-Aware | O(n) sorting |

### Caching

Effective policies cache:
- Host lists per datacenter
- Token → host mappings
- Distance calculations
- Query plans for repeated queries

### Monitoring

Key metrics for load balancing:

| Metric | Indicates |
|--------|-----------|
| Requests per node | Distribution evenness |
| Cross-DC requests | Fallback frequency |
| Retry rate | Initial selection quality |
| Speculative executions | Latency issues |

---

## Related Documentation

- **[Failure Handling](failure-handling.md)** - Retry and speculative execution
- **[Async Connections](async-connections.md)** - Connection pools per distance
- **[CQL Protocol](cql-protocol.md)** - Coordinator role in protocol