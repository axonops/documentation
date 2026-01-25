---
title: "Cassandra Driver Policies"
description: "Cassandra driver policies for load balancing, retry logic, reconnection, and speculative execution. Configure failure handling and optimize client performance."
meta:
  - name: keywords
    content: "Cassandra driver policies, load balancing policy, retry policy"
---

# Driver Policies

Driver policies control how the application interacts with the Cassandra cluster during normal operation and failure scenarios. These policies are the primary mechanism through which developers configure failure handling behavior.

---

## Developer Responsibility for Failure Handling

Unlike traditional databases where failure handling is largely abstracted away, Cassandra drivers expose failure scenarios directly to the application. **The developer is responsible for configuring appropriate responses to failures.**

This design is intentional: Cassandra's distributed architecture means that "failure" is nuanced. A node being slow is different from a node being down. A write timeout does not mean the write failed—it may have succeeded on some replicas. The driver cannot make assumptions about what the application considers acceptable behavior.

| Failure Type | What Happened | Driver's Question | Developer Must Decide |
|--------------|---------------|-------------------|----------------------|
| Read timeout | Some replicas didn't respond in time | Retry or fail? | Is stale data acceptable? Retry elsewhere? |
| Write timeout | Coordinator didn't get enough acknowledgments | Retry or fail? | Is duplicate write acceptable? Is operation idempotent? |
| Unavailable | Not enough replicas alive to satisfy CL | Retry or fail? | Lower consistency acceptable? Wait and retry? |
| Node down | Node unreachable | Where to route? When to retry connection? | Failover strategy? Recovery timing? |

**Default policies exist but are generic.** Production applications must evaluate each policy against their specific requirements for consistency, latency, and availability.

---

## Policy Overview

| Policy | Question It Answers | Default Behavior |
|--------|--------------------|--------------------|
| **Load Balancing** | Which node should handle this request? | Round-robin across local datacenter, token-aware |
| **Retry** | Should a failed request be retried? | Retry read timeouts once, don't retry write timeouts |
| **Reconnection** | How quickly to reconnect after node failure? | Exponential backoff (driver-specific defaults) |
| **Speculative Execution** | Should redundant requests be sent? | Disabled |

---

## Default Policy Behavior

Understanding default behavior is essential before customizing policies.

### Java Driver Defaults (v4.x)

| Policy | Configuration | Behavior |
|--------|---------------|----------|
| Load Balancing | `basic.load-balancing-policy` | Token-aware, prefers local DC, round-robin within replicas |
| Retry | `DefaultRetryPolicy` | Retry read timeout if enough replicas responded; never retry write timeout |
| Reconnection | `ExponentialReconnectionPolicy` | Base: 1 second, Max: 60 seconds (verify for specific version) |
| Speculative Execution | None | Disabled—must explicitly enable |

### Python Driver Defaults

| Policy | Default Implementation | Behavior |
|--------|----------------------|----------|
| Load Balancing | `TokenAwarePolicy(DCAwareRoundRobinPolicy())` | Token-aware wrapping DC-aware round-robin |
| Retry | `RetryPolicy` | Retry read timeout once on same host; retry unavailable once on next host |
| Reconnection | `ExponentialReconnectionPolicy` | Base: 1 second, Max: 600 seconds |
| Speculative Execution | None | Disabled |

---

## Failure Scenarios

Understanding common failure scenarios helps in selecting appropriate policies.

### Scenario 1: Single Node Failure

```plantuml
@startuml
skinparam backgroundColor transparent

participant "Application" as App
participant "Driver" as Drv
participant "Node1" as N1
participant "Node2" as N2
participant "Node3" as N3

note over N1: Node1 fails
App -> Drv: Execute query
Drv -> N1: Request [token owner]
N1 -x Drv: Connection failed
note over Drv: Load balancer selects next node
Drv -> N2: Request [replica]
N2 --> Drv: Success
Drv --> App: Result

@enduml
```

**Policy involvement:**

- **Load Balancing**: Provides fallback nodes when primary fails
- **Retry**: Determines if connection failure triggers retry
- **Reconnection**: Schedules background reconnection to Node1

### Scenario 2: Read Timeout (Partial Response)

```plantuml
@startuml
skinparam backgroundColor transparent

participant "Application" as App
participant "Driver" as Drv
participant "Coordinator" as Coord
participant "Replica1" as R1
participant "Replica2" as R2
participant "Replica3" as R3

App -> Drv: SELECT [QUORUM]
Drv -> Coord: Query
Coord -> R1: Read request
Coord -> R2: Read request
Coord -> R3: Read request
R1 --> Coord: Data
note over R2,R3: Slow or unresponsive
note over Coord: Timeout waiting for quorum
Coord --> Drv: ReadTimeoutException\n[received=1, required=2]
note over Drv: Retry policy consulted
Drv --> App: Retry or throw?

@enduml
```

**Policy involvement:**

- **Retry**: Decides whether to retry based on how many replicas responded
- **Speculative Execution**: Could have sent parallel request to avoid timeout

### Scenario 3: Write Timeout (Dangerous)

```plantuml
@startuml
skinparam backgroundColor transparent

participant "Application" as App
participant "Driver" as Drv
participant "Coordinator" as Coord
participant "Replica1" as R1
participant "Replica2" as R2

App -> Drv: INSERT [QUORUM]
Drv -> Coord: Write
Coord -> R1: Write request
Coord -> R2: Write request
R1 --> Coord: ACK
note over R2: Slow - no response
note over Coord: Timeout [received=1, required=2]
Coord --> Drv: WriteTimeoutException
note over Drv: Did R2 receive the write?
note over Drv: Retry could cause duplicate!

@enduml
```

**Critical consideration**: Write may have succeeded on R2 but acknowledgment was lost. Retrying non-idempotent writes risks data corruption.

### Scenario 4: Network Partition

```plantuml
@startuml
skinparam backgroundColor transparent

package "Reachable" {
    rectangle "Application" as App
    rectangle "Node1" as N1
    rectangle "Node2" as N2
}

package "Partitioned" #ffeeee {
    rectangle "Node3" as N3 #ffcccc
    rectangle "Node4" as N4 #ffcccc
    rectangle "Node5" as N5 #ffcccc
}

App --> N1
App --> N2
App ..> N3 : blocked

@enduml
```

**Policy involvement:**

- **Load Balancing**: Must route only to reachable nodes
- **Reconnection**: Attempts to reconnect to partitioned nodes
- **Retry**: Unavailable exceptions if CL cannot be met with reachable nodes

---

## Multi-Datacenter Configuration

Multi-DC deployments require careful policy configuration to ensure correct behavior during normal operation and DC failures.

### Local Datacenter Configuration

**Always configure the local datacenter explicitly.** This is the most critical setting for multi-DC deployments.

```java
// Java - REQUIRED for multi-DC
CqlSession session = CqlSession.builder()
    .withLocalDatacenter("dc1")
    .build();
```

```python
# Python - REQUIRED for multi-DC
from cassandra.policies import DCAwareRoundRobinPolicy
cluster = Cluster(
    load_balancing_policy=DCAwareRoundRobinPolicy(local_dc='dc1')
)
```

### Multi-DC Request Routing

```plantuml
@startuml
skinparam backgroundColor transparent

package "Application in DC1" {
    rectangle "Application" as App
}

package "DC1 (Local)" #e6ffe6 {
    rectangle "Node1" as N1
    rectangle "Node2" as N2
    rectangle "Node3" as N3
}

package "DC2 (Remote)" #fff0e6 {
    rectangle "Node4" as N4
    rectangle "Node5" as N5
    rectangle "Node6" as N6
}

App --> N1 : PRIMARY\n(low latency)
App --> N2 : PRIMARY
App --> N3 : PRIMARY
App ..> N4 : FAILOVER ONLY
App ..> N5 : FAILOVER ONLY

@enduml
```

### DC Failover Behavior

| Configuration | Normal Operation | Local DC Down |
|---------------|-----------------|---------------|
| `LOCAL_QUORUM` + local DC only | Routes to local DC | **All requests fail** |
| `LOCAL_QUORUM` + remote DC allowed | Routes to local DC | **Still fails** (`LOCAL_*` CLs only count local replicas) |
| `QUORUM` + remote DC allowed | May route anywhere | Continues if global quorum available |

### Multi-DC Policy Configuration

Configure multi-DC failover via `application.conf`:

```hocon
datastax-java-driver {
  basic.load-balancing-policy {
    local-datacenter = "dc1"
  }
  advanced.load-balancing-policy {
    # Allow failover to remote DC (requires non-LOCAL consistency levels)
    dc-failover.max-nodes-per-remote-dc = 2
  }
}
```

!!! warning "LOCAL consistency levels"
    Allowing remote DC nodes in the load balancing policy does not enable failover for `LOCAL_*` consistency levels. These levels only count replicas in the coordinator's datacenter regardless of where the request originates.

### Consistency Level Implications

| Consistency Level | Multi-DC Behavior | DC Failure Impact |
|-------------------|-------------------|-------------------|
| `LOCAL_ONE` | Local DC only | Fails if local DC down |
| `LOCAL_QUORUM` | Local DC only | Fails if local DC down |
| `QUORUM` | Global quorum | May succeed with one DC down |
| `EACH_QUORUM` | Quorum in every DC | Fails if any DC down |
| `ALL` | Every replica | Fails if any node down |

**Recommendation**: Use `LOCAL_QUORUM` for most operations. Configure load balancer to allow remote DC failover only when acceptable for the use case.

---

## Why Policies Matter

Default policies are designed for general use cases but may not match specific application requirements:

### Load Balancing Examples

| Scenario | Default Behavior | Problem |
|----------|------------------|---------|
| Multi-DC deployment | May route to remote DC | High latency if local DC not configured |
| Heterogeneous hardware | Equal distribution | Overloads weaker nodes |
| Batch analytics | Token-aware routing | Optimal for OLTP, but analytics may prefer round-robin |

### Retry Examples

| Scenario | Default Behavior | Problem |
|----------|------------------|---------|
| Non-idempotent writes | May retry on timeout | Potential duplicate writes |
| Overloaded cluster | Retry immediately | Amplifies load, worsens situation |
| Read timeout | Retry same node | Node may still be slow |

### Reconnection Examples

| Scenario | Default Behavior | Problem |
|----------|------------------|---------|
| Brief network blip | Exponential backoff | Slow recovery for transient issues |
| Node replacement | Standard reconnection | May attempt reconnection to decommissioned node |
| Rolling restart | Backoff after each node | Cascading delays |

---

## Policy Interactions

Policies do not operate in isolation—they interact during request execution:

```plantuml
@startuml
skinparam backgroundColor transparent

rectangle "Application executes query" as A
rectangle "Load Balancing Policy" as B
rectangle "Send to Node1" as C
card "Response?" as D
rectangle "Return result" as E
rectangle "Retry Policy" as F
rectangle "Send to Node3" as G
rectangle "Return error" as H
card "Response?" as I
rectangle "Continue or fail" as J

A --> B
B --> C : Returns node order:\n[N1, N3, N2]
C --> D
D --> E : Success
D --> F : Failure
F --> G : Retry allowed
F --> H : No retry
G --> I
I --> E : Success
I --> J : Failure

@enduml
```

If speculative execution is enabled, requests are sent concurrently:

```plantuml
@startuml
skinparam backgroundColor transparent

participant "Application" as App
participant "Driver" as Drv
participant "Node1" as N1
participant "Node3" as N3

App -> Drv: Execute query
Drv -> N1: Request
note over Drv: Start 50ms timer
Drv -> N3: Speculative request
N3 --> Drv: Response [fast]
Drv --> App: Return result
note over N1: Original still pending
N1 --> Drv: Response [ignored]

@enduml
```

---

## Configuration Approach

### Explicit Configuration

Do not rely on defaults for production deployments. Configure each policy explicitly via `application.conf` (preferred) or programmatically:

```hocon
# application.conf - Recommended approach for Java Driver 4.x
datastax-java-driver {
  basic {
    load-balancing-policy.local-datacenter = "dc1"
  }
  advanced {
    reconnection-policy {
      class = ExponentialReconnectionPolicy
      base-delay = 1 second
      max-delay = 5 minutes
    }
    speculative-execution-policy {
      class = ConstantSpeculativeExecutionPolicy
      max-executions = 2
      delay = 100 milliseconds
    }
  }
}
```

```java
// Load configuration from application.conf
CqlSession session = CqlSession.builder()
    .withConfigLoader(DriverConfigLoader.fromClasspath("application.conf"))
    .build();
```

### Per-Statement Override

Some policies can be overridden per statement:

```java
// Override retry policy for specific query
Statement statement = SimpleStatement.builder("SELECT * FROM users WHERE id = ?")
    .addPositionalValue(userId)
    .setRetryPolicy(FallthroughRetryPolicy.INSTANCE)  // No retries
    .build();
```

This allows different behavior for different query types (e.g., strict no-retry for non-idempotent writes).

---

## Policy Recommendations by Use Case

| Use Case | Load Balancing | Retry | Reconnection | Speculative Execution |
|----------|---------------|-------|--------------|----------------------|
| **OLTP (low latency)** | Token-aware, local DC | Conservative (reads only) | Fast base (500ms) | Enable for reads |
| **Batch/Analytics** | Round-robin or token-aware | Aggressive retry | Standard | Disable |
| **Multi-DC Active-Active** | Token-aware, local DC, failover enabled | Per-DC retry | Standard | Local DC only |
| **Write-heavy** | Token-aware | No retry for writes | Standard | Disable |
| **Read-heavy** | Token-aware | Retry reads | Standard | Enable |

### OLTP Application Configuration

```hocon
# application-oltp.conf
datastax-java-driver {
  basic.load-balancing-policy.local-datacenter = "dc1"
  advanced {
    load-balancing-policy.slow-replica-avoidance = true
    reconnection-policy {
      class = ExponentialReconnectionPolicy
      base-delay = 500 milliseconds
      max-delay = 2 minutes
    }
    speculative-execution-policy {
      class = ConstantSpeculativeExecutionPolicy
      max-executions = 2
      delay = 50 milliseconds
    }
  }
}
```

### Multi-DC Active-Active Configuration

```hocon
# application-multi-dc.conf
datastax-java-driver {
  basic.load-balancing-policy.local-datacenter = "dc1"
  advanced {
    load-balancing-policy {
      # Allow failover to remote DC (requires non-LOCAL consistency levels)
      dc-failover.max-nodes-per-remote-dc = 2
    }
    reconnection-policy {
      class = ExponentialReconnectionPolicy
      base-delay = 1 second
      max-delay = 5 minutes
    }
    # No speculative execution across DCs (latency difference too high)
  }
}
```

---

## Section Contents

- **[Load Balancing Policy](load-balancing.md)** — Node selection and request distribution
- **[Retry Policy](retry.md)** — Handling failed requests and error classification
- **[Reconnection Policy](reconnection.md)** — Recovery after node failures
- **[Speculative Execution Policy](speculative-execution.md)** — Reducing tail latency through redundant requests

