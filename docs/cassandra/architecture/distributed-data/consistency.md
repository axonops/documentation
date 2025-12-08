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


```mermaid
flowchart TB
    C[Client] -->|"INSERT with CL=QUORUM"| COORD

    subgraph COORD["Coordinator Node"]
        P1["1. Parse request"]
        P2["2. Calculate token"]
        P3["3. Look up replicas"]
        P4["4. Send to ALL replicas"]
        P5["5. Wait for QUORUM"]
        P6["6. Return success"]
        P1 --> P2 --> P3 --> P4 --> P5 --> P6
    end

    COORD -->|write| R1["Replica 1<br/>✓ ACK"]
    COORD -->|write| R2["Replica 2<br/>✓ ACK"]
    COORD -->|write| R3["Replica 3<br/>... writing"]
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

```mermaid
flowchart LR
    subgraph Replicas["All Replicas Down"]
        R1[N1 ✗]
        R2[N2 ✗]
        R3[N3 ✗]
    end

    C[Coordinator] -->|write| R1
    C -->|write| R2
    C -->|write| R3
    C -->|store hint| H[(Hint Storage)]
    H -->|"later delivery"| Replicas

    style R1 fill:#ffcccc
    style R2 fill:#ffcccc
    style R3 fill:#ffcccc
    style H fill:#ffffcc
```

!!! danger "Data Loss Risk"
    If the coordinator crashes before delivering the hint, the data is **permanently lost**. Use ANY only for truly non-critical data.

**When to use**: Almost never. Only for truly non-critical data where losing some writes is acceptable.

### ONE: Single Replica

```mermaid
flowchart LR
    C[Coordinator] -->|write| N1[N1 ✓]
    C -.->|write| N2[N2 ...]
    C -.->|write| N3[N3 ...]
    N1 -->|ACK| C
    C -->|SUCCESS| Client

    style N1 fill:#90EE90
    style N2 fill:#f0f0f0
    style N3 fill:#f0f0f0
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

```mermaid
flowchart LR
    subgraph Write["Write QUORUM"]
        WA[A ✓]
        WB[B ✓]
        WC[C]
    end

    subgraph Read["Read QUORUM"]
        RA[A]
        RB[B ✓]
        RC[C ✓]
    end

    WB -.->|OVERLAP| RB

    style WA fill:#90EE90
    style WB fill:#90EE90,stroke:#ff0000,stroke-width:3px
    style RB fill:#87CEEB,stroke:#ff0000,stroke-width:3px
    style RC fill:#87CEEB
```

With RF=3, QUORUM=2: Write to {A, B}, Read from {B, C}. The overlap (B) guarantees the read sees the write.

**Multi-datacenter QUORUM**:

```mermaid
flowchart TB
    subgraph DC1["DC1 (RF=3)"]
        A[A ✓]
        B[B ✓]
        C[C]
    end

    subgraph DC2["DC2 (RF=3)"]
        D[D ✓]
        E[E ✓]
        F[F]
    end

    Coord[Coordinator] -->|write| A
    Coord -->|write| B
    Coord -->|"cross-DC"| D
    Coord -->|"cross-DC"| E

    style A fill:#90EE90
    style B fill:#90EE90
    style D fill:#90EE90
    style E fill:#90EE90
```

Total RF = 6, QUORUM = 4. Must wait for cross-DC network round trip (50-200ms).

**When to use**:

- Single datacenter deployments
- When global consistency across all DCs is required

### LOCAL_QUORUM: Majority in Local Datacenter

```mermaid
flowchart TB
    subgraph DC1["DC1 - Coordinator Here"]
        A[A ✓]
        B[B ✓]
        C[C]
    end

    subgraph DC2["DC2 - Remote"]
        D[D]
        E[E]
        F[F]
    end

    Coord[Coordinator] -->|write + wait| A
    Coord -->|write + wait| B
    Coord -.->|"async (no wait)"| D
    Coord -.->|"async (no wait)"| E

    A -->|ACK| Coord
    B -->|ACK| Coord
    Coord -->|SUCCESS| Client[Client]

    style A fill:#90EE90
    style B fill:#90EE90
    style DC1 fill:#e6ffe6
    style DC2 fill:#f0f0f0
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

```mermaid
flowchart TB
    subgraph DC1["DC1"]
        A[A ✓]
        B[B ✓]
        C[C]
    end

    subgraph DC2["DC2"]
        D[D ✓]
        E[E ✓]
        F[F]
    end

    Coord[Coordinator] -->|"must get quorum"| DC1
    Coord -->|"must get quorum"| DC2
    DC1 -->|"2/3 ACK"| Coord
    DC2 -->|"2/3 ACK"| Coord
    Coord -->|SUCCESS| Client[Client]

    style A fill:#90EE90
    style B fill:#90EE90
    style D fill:#90EE90
    style E fill:#90EE90
```

Must wait for the **slowest DC** to achieve quorum.

**When to use**:

- Regulatory requirements for cross-DC consistency
- Financial transactions that must be in all regions before acknowledgment
- Rare—most applications do not need this

### ALL: Every Replica

```mermaid
flowchart LR
    C[Coordinator] -->|write| N1[N1 ✓]
    C -->|write| N2[N2 ✓]
    C -->|write| N3[N3 ✓]
    N1 -->|ACK| C
    N2 -->|ACK| C
    N3 -->|ACK| C

    style N1 fill:#90EE90
    style N2 fill:#90EE90
    style N3 fill:#90EE90
```

!!! warning "Availability Risk"
    If **any** replica is down, the write **fails**. Single node failure causes complete write unavailability.

**When to use**: Almost never for writes. Single node failure causes all writes to fail.

---

## Read Consistency Levels

### ONE: Fastest Reads

```mermaid
sequenceDiagram
    participant Client
    participant Coord as Coordinator
    participant N1 as N1
    participant N2 as N2

    Client->>Coord: Read request
    Coord->>N1: Read
    N1->>Coord: Data (possibly stale)
    Coord->>Client: Return data
    Note over Coord,N2: N2, N3 not contacted
```

If N1 has stale data, stale data is returned. Background read repair may fix inconsistency later.

### QUORUM: Strong Consistency Reads

```mermaid
sequenceDiagram
    participant Client
    participant Coord as Coordinator
    participant N1 as N1
    participant N2 as N2

    Client->>Coord: Read request (QUORUM)
    par Contact replicas
        Coord->>N1: Read
        Coord->>N2: Read
    end
    N1->>Coord: Data (ts=1000)
    N2->>Coord: Data (ts=2000)
    Note over Coord: Compare timestamps<br/>Return newest (ts=2000)
    Coord->>Client: Data (ts=2000)
    Note over Coord,N1: Trigger read repair for N1
```

Coordinator returns the **newest** data based on timestamp. If replicas disagree, coordinator triggers read repair.

### LOCAL_QUORUM: Fast Strong Reads

Same logic as QUORUM, but only contacts local DC replicas. Provides strong consistency within the datacenter with lower latency.

### EACH_QUORUM: Not Supported for Reads

!!! note
    EACH_QUORUM is **write-only**. For reads, use QUORUM (for cross-DC consistency) or LOCAL_QUORUM (for local consistency).

### ALL: Read From Every Replica

```mermaid
sequenceDiagram
    participant Client
    participant Coord as Coordinator
    participant N1 as N1
    participant N2 as N2
    participant N3 as N3

    Client->>Coord: Read request (ALL)
    par Contact all replicas
        Coord->>N1: Read
        Coord->>N2: Read
        Coord->>N3: Read
    end
    N1->>Coord: Data
    N2->>Coord: Data
    N3--xCoord: Timeout/Down
    Coord->>Client: TIMEOUT ERROR
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

```mermaid
flowchart LR
    subgraph Cluster["RF=3, One Node Down"]
        A[A ✓]
        B[B ✓]
        C[C ✗]
    end

    style A fill:#90EE90
    style B fill:#90EE90
    style C fill:#ffcccc
```

| CL | Works? | Reason |
|----|--------|--------|
| ONE | ✓ | 2 replicas available |
| QUORUM (2) | ✓ | 2 of 3 available |
| ALL | ✗ | C is down |

### Two Node Failure (RF=3)

```mermaid
flowchart LR
    subgraph Cluster["RF=3, Two Nodes Down"]
        A[A ✓]
        B[B ✗]
        C[C ✗]
    end

    style A fill:#90EE90
    style B fill:#ffcccc
    style C fill:#ffcccc
```

| CL | Works? | Reason |
|----|--------|--------|
| ONE | ✓ | 1 replica available |
| QUORUM (2) | ✗ | Only 1 of 3 available |
| ALL | ✗ | B and C down |

### Entire Datacenter Failure

```mermaid
flowchart LR
    subgraph DC1["DC1 (UP)"]
        A[A ✓]
        B[B ✓]
        C[C ✓]
    end

    subgraph DC2["DC2 (DOWN)"]
        D[D ✗]
        E[E ✗]
        F[F ✗]
    end

    style A fill:#90EE90
    style B fill:#90EE90
    style C fill:#90EE90
    style D fill:#ffcccc
    style E fill:#ffcccc
    style F fill:#ffcccc
    style DC1 fill:#e6ffe6
    style DC2 fill:#ffe6e6
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

```mermaid
sequenceDiagram
    participant Client
    participant Coord as Coordinator
    participant R1 as Replica 1
    participant R2 as Replica 2
    participant R3 as Replica 3

    Client->>Coord: UPDATE ... IF balance = 100

    Note over Coord,R3: Phase 1: PREPARE
    par Send prepare
        Coord->>R1: PREPARE(ballot=1)
        Coord->>R2: PREPARE(ballot=1)
        Coord->>R3: PREPARE(ballot=1)
    end
    R1->>Coord: PROMISE
    R2->>Coord: PROMISE
    R3->>Coord: PROMISE

    Note over Coord,R3: Phase 2: READ (check IF condition)
    par Read current value
        Coord->>R1: READ
        Coord->>R2: READ
    end
    R1->>Coord: balance=100
    R2->>Coord: balance=100
    Note over Coord: IF condition passes

    Note over Coord,R3: Phase 3: PROPOSE
    par Send proposal
        Coord->>R1: PROPOSE(ballot=1, balance=50)
        Coord->>R2: PROPOSE(ballot=1, balance=50)
        Coord->>R3: PROPOSE(ballot=1, balance=50)
    end
    R1->>Coord: ACCEPT
    R2->>Coord: ACCEPT
    R3->>Coord: ACCEPT

    Note over Coord,R3: Phase 4: COMMIT
    par Commit value
        Coord->>R1: COMMIT
        Coord->>R2: COMMIT
        Coord->>R3: COMMIT
    end

    Coord->>Client: [applied]=true
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

```mermaid
sequenceDiagram
    participant Client
    participant Coord as Coordinator
    participant N1 as N1 (fast)
    participant N2 as N2 (slow)

    Note over Client: QUORUM read (need 2 of 3)
    Client->>Coord: Read request
    Note over Coord: T+0ms
    par Send to replicas
        Coord->>N1: Read
        Coord->>N2: Read
    end
    Note over Coord: T+5ms
    N1->>Coord: Response
    Note over Coord: Have 1, need 2...waiting
    Note over N2: GC pause
    Note over Coord: T+500ms
    N2->>Coord: Response (delayed)
    Coord->>Client: Return result
    Note over Client: Total latency: 500ms
```

### With Speculative Execution

When a replica exceeds the expected latency threshold, the coordinator sends a speculative request to another replica:

```mermaid
sequenceDiagram
    participant Client
    participant Coord as Coordinator
    participant N1 as N1 (fast)
    participant N2 as N2 (slow)
    participant N3 as N3 (fast)

    Note over Client: QUORUM read (need 2 of 3)
    Client->>Coord: Read request
    Note over Coord: T+0ms
    par Send to replicas
        Coord->>N1: Read
        Coord->>N2: Read
    end
    Note over Coord: T+5ms
    N1->>Coord: Response
    Note over Coord: T+10ms: N2 exceeds 99th percentile
    Coord->>N3: Speculative read
    Note over Coord: T+15ms
    N3->>Coord: Response
    Note over Coord: Have 2 responses (N1, N3)
    Coord->>Client: Return result
    Note over Client: Total latency: 15ms
    Note over N2: Still processing...ignored
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
