---
title: "Cassandra Query Consistency Levels"
description: "Consistency levels in Cassandra. ONE, QUORUM, ALL, LOCAL_QUORUM explained with trade-offs."
meta:
  - name: keywords
    content: "consistency level, Cassandra consistency, QUORUM, eventual consistency"
---

# Consistency

Consistency in Cassandra is tunable—the number of replicas that must acknowledge reads and writes is configurable per operation. This flexibility allows trading consistency for availability and latency.

---

## Consistency Is Per-Request

Unlike traditional databases where consistency is a system property, Cassandra allows specifying consistency per statement:

```sql
-- Strong consistency for this critical write
CONSISTENCY QUORUM;
INSERT INTO orders (id, amount) VALUES (uuid(), 100.00);

-- Weaker consistency for this non-critical read
CONSISTENCY ONE;
SELECT * FROM page_views WHERE page_id = 'homepage';
```

Different operations can be optimized differently within the same application.

---

## The Coordinator's Role

Every client request goes to a coordinator node, which manages the consistency guarantee:


```plantuml
@startuml

skinparam backgroundColor #FEFEFE

title Coordinator Processing a Write Request

boundary "Client" as C
rectangle "Coordinator Node" as COORD {
    card "1. Parse request" as P1
    card "2. Calculate token" as P2
    card "3. Look up replicas" as P3
    card "4. Send to ALL replicas" as P4
    card "5. Wait for QUORUM" as P5
    card "6. Return success" as P6

    P1 --> P2
    P2 --> P3
    P3 --> P4
    P4 --> P5
    P5 --> P6
}

database "Replica 1\nACK" as R1 #90EE90
database "Replica 2\nACK" as R2 #90EE90
database "Replica 3\n... writing" as R3 #f0f0f0

C --> COORD : INSERT with CL=QUORUM
COORD --> R1 : write
COORD --> R2 : write
COORD --> R3 : write

@enduml
```

### What Acknowledgment Means

**For writes**, a replica acknowledges after:

1. Writing to commit log (durability)
2. Writing to memtable (memory)

The data is not necessarily flushed to SSTable yet, but it is durable because of the commit log.

**For reads**, a replica acknowledges by returning its data.

---

## Write Consistency Levels

### ANY: Maximum Availability

```plantuml
@startuml

skinparam backgroundColor #FEFEFE

title ANY Consistency - Hinted Handoff

rectangle "Coordinator" as C

rectangle "All Replicas Down" as Replicas {
    database "N1" as R1 #ffcccc
    database "N2" as R2 #ffcccc
    database "N3" as R3 #ffcccc
}

database "Hint Storage" as H #ffffcc

C --> R1 : write (fails)
C --> R2 : write (fails)
C --> R3 : write (fails)
C --> H : store hint
H ..> Replicas : later delivery

@enduml
```

!!! danger "Data Loss Risk"
    If the coordinator crashes before delivering the hint, the data is **permanently lost**. Use ANY only for truly non-critical data.

**When to use**: Almost never. Only for truly non-critical data where losing some writes is acceptable.

### ONE: Single Replica

```plantuml
@startuml

skinparam backgroundColor #FEFEFE

title ONE Consistency - Single Replica ACK

rectangle "Coordinator" as C
boundary "Client" as Client

database "N1" as N1 #90EE90
database "N2" as N2 #f0f0f0
database "N3" as N3 #f0f0f0

C --> N1 : write
C ..> N2 : write (async)
C ..> N3 : write (async)
N1 --> C : ACK
C --> Client : SUCCESS

@enduml
```

RF = 3, ONE requires 1 ACK. Other replicas receive the write asynchronously.

**When to use**:

- High-throughput writes where some inconsistency is acceptable
- Time-series data with many writes per second
- When combined with ALL reads (R + W > N)

### QUORUM: Majority of All Replicas

| RF | QUORUM | Formula |
|----|--------|---------|
| 3 | 2 | floor(3/2) + 1 |
| 5 | 3 | floor(5/2) + 1 |
| 7 | 4 | floor(7/2) + 1 |

**Why majority matters**:

```plantuml
@startuml

skinparam backgroundColor #FEFEFE

title QUORUM Overlap Guarantees Consistency

rectangle "Write QUORUM" as Write {
    card "A" as WA #90EE90
    card "B" as WB #90EE90
    card "C" as WC #f0f0f0
}

rectangle "Read QUORUM" as Read {
    card "A" as RA #f0f0f0
    card "B" as RB #87CEEB
    card "C" as RC #87CEEB
}

WB -[#ff0000,bold]-> RB : OVERLAP

note bottom of WB
  Written to A, B
end note

note bottom of RB
  Read from B, C
  B has the write
end note

@enduml
```

With RF=3, QUORUM=2: Write to {A, B}, Read from {B, C}. The overlap (B) guarantees the read sees the write.

**Multi-datacenter QUORUM**:

```plantuml
@startuml

skinparam backgroundColor #FEFEFE

title Multi-DC QUORUM (Total RF=6, QUORUM=4)

rectangle "Coordinator" as Coord

rectangle "DC1 (RF=3)" as DC1 {
    database "A" as A #90EE90
    database "B" as B #90EE90
    database "C" as C #f0f0f0
}

rectangle "DC2 (RF=3)" as DC2 {
    database "D" as D #90EE90
    database "E" as E #90EE90
    database "F" as F #f0f0f0
}

Coord --> A : write
Coord --> B : write
Coord --> D : cross-DC
Coord --> E : cross-DC

@enduml
```

Total RF = 6, QUORUM = 4. Must wait for cross-DC network round trip (50-200ms).

**When to use**:

- Single datacenter deployments
- When global consistency across all DCs is required

### LOCAL_QUORUM: Majority in Local Datacenter

```plantuml
@startuml

skinparam backgroundColor #FEFEFE

title LOCAL_QUORUM - Only Wait for Local DC

rectangle "Coordinator" as Coord
boundary "Client" as Client

rectangle "DC1 - Coordinator Here" as DC1 #e6ffe6 {
    database "A" as A #90EE90
    database "B" as B #90EE90
    database "C" as C #f0f0f0
}

rectangle "DC2 - Remote" as DC2 #f0f0f0 {
    database "D" as D #f0f0f0
    database "E" as E #f0f0f0
    database "F" as F #f0f0f0
}

Coord --> A : write + wait
Coord --> B : write + wait
Coord ..> D : async (no wait)
Coord ..> E : async (no wait)

A --> Coord : ACK
B --> Coord : ACK
Coord --> Client : SUCCESS

@enduml
```

2 ACKs from DC1 = SUCCESS. Data is still sent to DC2, but coordinator does not wait.

!!! tip "Latency Advantage"
    | Consistency | Path | Typical Latency |
    |-------------|------|-----------------|
    | QUORUM (multi-DC) | Client → DC1 → DC2 → DC1 → Client | 50-200ms |
    | LOCAL_QUORUM | Client → DC1 → Client | 1-5ms |

    LOCAL_QUORUM is **10-100x faster** for multi-DC deployments.

**When to use**: Multi-DC deployments (almost always the right choice).

### EACH_QUORUM: Quorum in Every Datacenter

```plantuml
@startuml

skinparam backgroundColor #FEFEFE

title EACH_QUORUM - Quorum Required in Every DC

rectangle "Coordinator" as Coord
boundary "Client" as Client

rectangle "DC1" as DC1 {
    database "A" as A #90EE90
    database "B" as B #90EE90
    database "C" as C #f0f0f0
}

rectangle "DC2" as DC2 {
    database "D" as D #90EE90
    database "E" as E #90EE90
    database "F" as F #f0f0f0
}

Coord --> DC1 : must get quorum
Coord --> DC2 : must get quorum
DC1 --> Coord : 2/3 ACK
DC2 --> Coord : 2/3 ACK
Coord --> Client : SUCCESS

note bottom of DC2
  Must wait for slowest DC
end note

@enduml
```

Must wait for the **slowest DC** to achieve quorum.

**When to use**:

- Regulatory requirements for cross-DC consistency
- Financial transactions that must be in all regions before acknowledgment
- Rare—most applications do not need this

### ALL: Every Replica

```plantuml
@startuml

skinparam backgroundColor #FEFEFE

title ALL Consistency - Every Replica Must ACK

rectangle "Coordinator" as C

database "N1" as N1 #90EE90
database "N2" as N2 #90EE90
database "N3" as N3 #90EE90

C --> N1 : write
C --> N2 : write
C --> N3 : write
N1 --> C : ACK
N2 --> C : ACK
N3 --> C : ACK

@enduml
```

!!! warning "Availability Risk"
    If **any** replica is down, the write **fails**. Single node failure causes complete write unavailability.

**When to use**: Almost never for writes. Single node failure causes all writes to fail.

---

## Read Consistency Levels

### ONE: Fastest Reads

```plantuml
@startuml

skinparam backgroundColor #FEFEFE

title ONE Read - Fastest but Possibly Stale

participant "Client" as Client
participant "Coordinator" as Coord
database "N1" as N1
database "N2" as N2

Client -> Coord : Read request
Coord -> N1 : Read
N1 -> Coord : Data (possibly stale)
Coord -> Client : Return data

note over N2 : N2, N3 not contacted

@enduml
```

If N1 has stale data, stale data is returned. Background read repair may fix inconsistency later.

### QUORUM: Strong Consistency Reads

```plantuml
@startuml

skinparam backgroundColor #FEFEFE

title QUORUM Read - Compare Timestamps

participant "Client" as Client
participant "Coordinator" as Coord
database "N1" as N1
database "N2" as N2

Client -> Coord : Read request (QUORUM)
Coord -> N1 : Read
Coord -> N2 : Read
N1 -> Coord : Data (ts=1000)
N2 -> Coord : Data (ts=2000)

note over Coord
  Compare timestamps
  Return newest (ts=2000)
end note

Coord -> Client : Data (ts=2000)

note over Coord, N1 : Trigger read repair for N1

@enduml
```

Coordinator returns the **newest** data based on timestamp. If replicas disagree, coordinator triggers read repair.

### LOCAL_QUORUM: Fast Strong Reads

Same logic as QUORUM, but only contacts local DC replicas. Provides strong consistency within the datacenter with lower latency.

### EACH_QUORUM: Not Supported for Reads

!!! note
    EACH_QUORUM is **write-only**. For reads, use QUORUM (for cross-DC consistency) or LOCAL_QUORUM (for local consistency).

### ALL: Read From Every Replica

```plantuml
@startuml

skinparam backgroundColor #FEFEFE

title ALL Read - Any Failure Causes Timeout

participant "Client" as Client
participant "Coordinator" as Coord
database "N1" as N1
database "N2" as N2
database "N3" as N3

Client -> Coord : Read request (ALL)
Coord -> N1 : Read
Coord -> N2 : Read
Coord -> N3 : Read
N1 -> Coord : Data
N2 -> Coord : Data
N3 ->x Coord : Timeout/Down

Coord -> Client : TIMEOUT ERROR

@enduml
```

!!! warning
    If **any** replica is down or slow, the read **times out**.

**When ALL reads make sense**:

- Combined with ONE writes (R + W > N)
- Read-heavy workload where fast writes are desired
- Single node failure causes all reads to fail

---

## The Strong Consistency Formula

### R + W > N

The fundamental rule for strong consistency:

```
R = Number of replicas read
W = Number of replicas written
N = Replication factor

If R + W > N, reads will see the latest writes.
```

**Why it works**:

```
N = 3 (three replicas total)
W = 2 (write to two replicas)
R = 2 (read from two replicas)

R + W = 4 > 3 = N

The sets of written replicas and read replicas MUST overlap.

Write went to: {A, B}
Read contacts: {B, C}
Overlap: B ← Has the write
```

### Common Combinations

| Combination | R + W | Strong? | Use Case |
|-------------|-------|---------|----------|
| W=QUORUM, R=QUORUM | 4 > 3 | Yes | Standard strong consistency |
| W=ONE, R=ALL | 4 > 3 | Yes | Write-heavy, few reads |
| W=ALL, R=ONE | 4 > 3 | Yes | Read-heavy, few writes |
| W=LOCAL_QUORUM, R=LOCAL_QUORUM | 4 > 3 per DC | Yes (per DC) | Multi-DC standard |
| W=ONE, R=ONE | 2 < 3 | No | High throughput, eventual |
| W=ONE, R=QUORUM | 3 = 3 | No* | Sometimes inconsistent |

*R + W = N is not sufficient; must be strictly greater than.

### Multi-DC Complexity

| Configuration | QUORUM | LOCAL_QUORUM |
|---------------|--------|--------------|
| DC1: RF=3, DC2: RF=3 | 4 (global) | 2 (per DC) |
| **Write behavior** | 4 replicas (any DC) | 2 replicas (local DC only) |
| **Read behavior** | 4 replicas (any DC) | 2 replicas (local DC only) |
| **Consistency** | Global | Per-DC (cross-DC eventual) |

For most applications, LOCAL_QUORUM is sufficient because cross-DC replication happens in milliseconds.

---

## Failure Scenarios

### Single Node Failure (RF=3)

```plantuml
@startuml

skinparam backgroundColor #FEFEFE

title RF=3, One Node Down

rectangle "Cluster" as Cluster {
    database "A" as A #90EE90
    database "B" as B #90EE90
    database "C" as C #ffcccc
}

note right of C : Node down

@enduml
```

| CL | Works? | Reason |
|----|--------|--------|
| ONE | ✓ | 2 replicas available |
| QUORUM (2) | ✓ | 2 of 3 available |
| ALL | ✗ | C is down |

### Two Node Failure (RF=3)

```plantuml
@startuml

skinparam backgroundColor #FEFEFE

title RF=3, Two Nodes Down

rectangle "Cluster" as Cluster {
    database "A" as A #90EE90
    database "B" as B #ffcccc
    database "C" as C #ffcccc
}

note right of B : Nodes down

@enduml
```

| CL | Works? | Reason |
|----|--------|--------|
| ONE | ✓ | 1 replica available |
| QUORUM (2) | ✗ | Only 1 of 3 available |
| ALL | ✗ | B and C down |

### Entire Datacenter Failure

```plantuml
@startuml

skinparam backgroundColor #FEFEFE

title Entire Datacenter Failure

rectangle "DC1 (UP)" as DC1 #e6ffe6 {
    database "A" as A #90EE90
    database "B" as B #90EE90
    database "C" as C #90EE90
}

rectangle "DC2 (DOWN)" as DC2 #ffe6e6 {
    database "D" as D #ffcccc
    database "E" as E #ffcccc
    database "F" as F #ffcccc
}

note right of DC2 : Entire DC down

@enduml
```

| CL | Works? | Reason |
|----|--------|--------|
| LOCAL_ONE | ✓ | Only needs local DC |
| LOCAL_QUORUM | ✓ | Only needs local DC |
| QUORUM (4/6) | ✗ | Only 3 of 6 available |
| EACH_QUORUM | ✗ | DC2 has no quorum |

!!! tip "Key Insight"
    LOCAL_QUORUM survives **entire DC failure** while maintaining strong local consistency. This is why it is recommended for multi-DC deployments.

---

## Lightweight Transactions (LWT)

### When Regular Consistency Is Not Enough

Regular QUORUM consistency does not provide linearizability for compare-and-set operations:

```
Problem scenario (race condition):

Time 0: Both Client A and Client B read balance = 100
Time 1: Client A: UPDATE SET balance = 100 - 50
Time 2: Client B: UPDATE SET balance = 100 - 30

Result: balance = 70 (should be 20!)
Both clients read 100, both subtracted from 100.
```

### LWT Solves This With Paxos

Lightweight transactions use the Paxos consensus algorithm ([Lamport, L., 1998, "The Part-Time Parliament"](https://lamport.azurewebsites.net/pubs/lamport-paxos.pdf)) to achieve linearizable consistency for compare-and-set operations.

```sql
-- Compare-and-set with IF clause triggers LWT
UPDATE account SET balance = 50 WHERE id = 1 IF balance = 100;

-- Returns [applied] = true if balance was 100
-- Returns [applied] = false if balance was different
```

### How LWT Works

LWT uses four Paxos phases, requiring 4 round trips compared to 1 for regular writes:

```plantuml
@startuml

skinparam backgroundColor #FEFEFE

title Lightweight Transaction (Paxos) - 4 Phases

participant "Client" as Client
participant "Coordinator" as Coord
database "Replica 1" as R1
database "Replica 2" as R2
database "Replica 3" as R3

Client -> Coord : UPDATE ... IF balance = 100

== Phase 1: PREPARE ==

Coord -> R1 : PREPARE(ballot=1)
Coord -> R2 : PREPARE(ballot=1)
Coord -> R3 : PREPARE(ballot=1)
R1 -> Coord : PROMISE
R2 -> Coord : PROMISE
R3 -> Coord : PROMISE

== Phase 2: READ (check IF condition) ==

Coord -> R1 : READ
Coord -> R2 : READ
R1 -> Coord : balance=100
R2 -> Coord : balance=100

note over Coord : IF condition passes

== Phase 3: PROPOSE ==

Coord -> R1 : PROPOSE(ballot=1, balance=50)
Coord -> R2 : PROPOSE(ballot=1, balance=50)
Coord -> R3 : PROPOSE(ballot=1, balance=50)
R1 -> Coord : ACCEPT
R2 -> Coord : ACCEPT
R3 -> Coord : ACCEPT

== Phase 4: COMMIT ==

Coord -> R1 : COMMIT
Coord -> R2 : COMMIT
Coord -> R3 : COMMIT

Coord -> Client : [applied]=true

@enduml
```

| Aspect | Regular Write | LWT Write |
|--------|---------------|-----------|
| Round trips | 1 | 4 |
| Latency | ~1-5ms | ~4-20ms |
| Throughput | High | Low |

### Serial Consistency Levels

```sql
-- SERIAL: Paxos across ALL datacenters
SERIAL CONSISTENCY SERIAL;
INSERT INTO unique_emails (email, user_id)
VALUES ('a@b.com', 123) IF NOT EXISTS;

-- LOCAL_SERIAL: Paxos within local datacenter only
SERIAL CONSISTENCY LOCAL_SERIAL;
INSERT INTO user_sessions (session_id, user_id)
VALUES (uuid(), 123) IF NOT EXISTS;
```

| Serial CL | Scope | Latency | Use Case |
|-----------|-------|---------|----------|
| SERIAL | All DCs | High (cross-DC) | Global uniqueness |
| LOCAL_SERIAL | Local DC | Lower | DC-local uniqueness |

### LWT Best Practices

1. **Use sparingly**: LWT is 4x slower than regular writes
2. **Batch related LWTs**: Multiple LWT in same partition can share Paxos
3. **Consider alternatives**: Often application-level locking or redesign is better
4. **Monitor contention**: High LWT contention causes performance collapse

```sql
-- Good: Single LWT for compare-and-set
UPDATE inventory SET qty = qty - 1 WHERE product_id = ? IF qty > 0;

-- Bad: Using LWT unnecessarily
INSERT INTO events (id, data) VALUES (uuid(), ?) IF NOT EXISTS;
-- UUID is always unique, LWT is not needed
```

---

## Speculative Execution

Speculative execution sends duplicate requests to reduce tail latency when one replica is slow.

### Without Speculative Execution

When one replica is slow (e.g., due to GC pause), the client must wait for it:

```plantuml
@startuml

skinparam backgroundColor #FEFEFE

title Without Speculative Execution

participant "Client" as Client
participant "Coordinator" as Coord
database "N1 (fast)" as N1
database "N2 (slow)" as N2

note over Client : QUORUM read (need 2 of 3)
Client -> Coord : Read request
note over Coord : T+0ms

Coord -> N1 : Read
Coord -> N2 : Read

note over Coord : T+5ms
N1 -> Coord : Response
note over Coord : Have 1, need 2...waiting

note over N2 : GC pause

note over Coord : T+500ms
N2 -> Coord : Response (delayed)
Coord -> Client : Return result
note over Client : Total latency: 500ms

@enduml
```

### With Speculative Execution

When a replica exceeds the expected latency threshold, the coordinator sends a speculative request to another replica:

```plantuml
@startuml

skinparam backgroundColor #FEFEFE

title With Speculative Execution

participant "Client" as Client
participant "Coordinator" as Coord
database "N1 (fast)" as N1
database "N2 (slow)" as N2
database "N3 (fast)" as N3

note over Client : QUORUM read (need 2 of 3)
Client -> Coord : Read request
note over Coord : T+0ms

Coord -> N1 : Read
Coord -> N2 : Read

note over Coord : T+5ms
N1 -> Coord : Response

note over Coord : T+10ms: N2 exceeds 99th percentile
Coord -> N3 : Speculative read

note over Coord : T+15ms
N3 -> Coord : Response

note over Coord : Have 2 responses (N1, N3)
Coord -> Client : Return result
note over Client : Total latency: 15ms

note over N2 : Still processing...ignored

@enduml
```

| Scenario | Latency |
|----------|---------|
| Without speculative execution | 500ms (waiting for slow N2) |
| With speculative execution | 15ms (N3 responds instead) |

### Configuration

```sql
-- Per-table speculative retry setting
ALTER TABLE users WITH speculative_retry = '99percentile';

-- Options:
-- 'Xpercentile': Retry after X percentile latency
-- 'Yms': Retry after Y milliseconds
-- 'ALWAYS': Always send to extra replica immediately
-- 'NONE': Disable speculative retry
```

**Trade-off**: Speculative execution increases replica load but reduces tail latency.

---

## Debugging Consistency Issues

### "I wrote data but cannot read it"

**Diagnosis steps:**

1. Check consistency levels: Write CL + Read CL > RF?
2. Check for clock skew: `ntpq -p` on each node
3. Check for failed writes: Application logs for timeouts
4. Enable tracing: `TRACING ON;`

### Tracing

```sql
TRACING ON;

SELECT * FROM users WHERE user_id = 123;

-- Output shows:
-- - Which replicas were contacted
-- - Response times from each
-- - Whether read repair occurred
```

### JMX Metrics

```
# Unavailable errors (CL could not be satisfied)
org.apache.cassandra.metrics:type=ClientRequest,scope=Read,name=Unavailables
org.apache.cassandra.metrics:type=ClientRequest,scope=Write,name=Unavailables

# Timeouts
org.apache.cassandra.metrics:type=ClientRequest,scope=Read,name=Timeouts
org.apache.cassandra.metrics:type=ClientRequest,scope=Write,name=Timeouts

# LWT metrics
org.apache.cassandra.metrics:type=ClientRequest,scope=CASWrite,name=Latency
org.apache.cassandra.metrics:type=ClientRequest,scope=CASWrite,name=ContentionHistogram
```

---

## Best Practices

### Choosing Consistency Levels

| Scenario | Write CL | Read CL | Rationale |
|----------|----------|---------|-----------|
| Single DC, strong consistency | QUORUM | QUORUM | R+W > N |
| Multi-DC, low latency | LOCAL_QUORUM | LOCAL_QUORUM | No cross-DC wait |
| Multi-DC, global consistency | QUORUM | QUORUM | Cross-DC consensus |
| High throughput, eventual OK | ONE | ONE | Fastest |
| Write-heavy | ONE | ALL | Fast writes |
| Read-heavy | ALL | ONE | Fast reads |
| Time-series metrics | LOCAL_ONE | LOCAL_ONE | Volume over consistency |

### Common Mistakes

| Mistake | Consequence |
|---------|-------------|
| Using ALL in production | Single node failure breaks everything |
| QUORUM in multi-DC when LOCAL_QUORUM suffices | Unnecessary latency |
| ONE/ONE without understanding | No consistency guarantee |
| Overusing LWT | Performance degradation |
| Ignoring clock skew | Silent data loss via timestamp conflicts |

### Monitoring

| Metric | Alert Threshold | Meaning |
|--------|-----------------|---------|
| Unavailables | >0 | CL cannot be met |
| Timeouts | >1% | Replicas too slow |
| Read repair rate | >10% | High inconsistency |
| LWT contention | >10% | Redesign needed |

---

## Related Documentation

- **[Distributed Data Overview](index.md)** - How partitioning, replication, and consistency work together
- **[Replication](replication.md)** - How replicas are placed
- **[Replica Synchronization](replica-synchronization.md)** - How replicas converge
- **[Operations](../../operations/repair/index.md)** - Running repair
