# Application Development

This section covers developing applications against Apache Cassandra, including CQL syntax, data modeling principles, and driver configuration.

---

## Understanding Consistency in Cassandra

A common misconception is that Cassandra is "eventually consistent" and therefore unsuitable for applications requiring strong consistency guarantees. In reality, Cassandra provides **tunable consistency**—developers control the consistency level on a per-query basis, ranging from eventual consistency to full linearizable consistency.

### Consistency Is a Developer Choice

| Consistency Level | Guarantee | Use Case |
|-------------------|-----------|----------|
| `ONE` | Acknowledged by one replica | Maximum availability, eventual consistency |
| `QUORUM` | Acknowledged by majority of replicas | Strong consistency with good availability |
| `LOCAL_QUORUM` | Majority within local datacenter | Strong consistency with low latency in multi-DC |
| `ALL` | Acknowledged by all replicas | Maximum consistency, reduced availability |
| `SERIAL` / `LOCAL_SERIAL` | Linearizable (via Paxos) | Compare-and-set operations |

!!! tip "Strong Consistency Formula"
    When `R + W > RF` (reads + writes > replication factor), strong consistency is achieved. With `RF=3`, using `QUORUM` for both reads and writes satisfies this: `2 + 2 > 3`.

### Common Patterns

**Strong consistency (most applications):**
```cql
-- Write with QUORUM
INSERT INTO users (id, name) VALUES (?, ?) USING CONSISTENCY QUORUM;

-- Read with QUORUM
SELECT * FROM users WHERE id = ? CONSISTENCY QUORUM;
```

**Eventual consistency (high-throughput, loss-tolerant):**
```cql
-- Metrics, logs, time-series where some loss is acceptable
INSERT INTO metrics (sensor_id, ts, value) VALUES (?, ?, ?) USING CONSISTENCY ONE;
```

**Linearizable consistency (compare-and-set):**
```cql
-- Lightweight transaction for conditional updates
UPDATE accounts SET balance = ? WHERE id = ? IF balance = ?;
```

### Why the Misconception Exists

Early Cassandra documentation emphasized availability and partition tolerance (the "AP" in CAP theorem), leading many to assume consistency was sacrificed. In practice:

- Cassandra defaults to `ONE` for reads and writes, which is eventually consistent
- Developers who do not explicitly set consistency levels experience eventual consistency
- The CAP theorem describes behavior during network partitions, not normal operation

!!! warning "Configure Consistency Explicitly"
    Driver defaults are optimized for availability, not consistency. Production applications should explicitly set consistency levels based on data requirements rather than relying on defaults.

---

## Developer Responsibility

Cassandra drivers differ fundamentally from traditional database drivers. A connection to a relational database typically abstracts away server topology—the application connects to a single endpoint, and failover (if any) is handled transparently by the database or a proxy layer.

Cassandra drivers expose the distributed nature of the cluster directly to the application. This design provides significant advantages—applications can achieve lower latency, better load distribution, and precise control over consistency—but it places responsibility on the developer to configure failure handling correctly.

### What the Driver Exposes

| Aspect | Traditional Database | Cassandra Driver |
|--------|---------------------|------------------|
| Topology awareness | Hidden behind single endpoint | Driver maintains live map of all nodes |
| Node failures | Handled by database/proxy | Application must configure retry and reconnection behavior |
| Request routing | Database decides | Application configures load balancing policy |
| Consistency trade-offs | Fixed by database | Application chooses per-query consistency level |

### Policies Control Failure Behavior

The driver provides configurable policies that determine application behavior during normal operation and failure scenarios:

| Policy | Controls |
|--------|----------|
| **Load Balancing** | Which nodes receive requests; datacenter affinity; rack awareness |
| **Retry** | Whether to retry failed requests; which errors are retryable; how many attempts |
| **Reconnection** | How quickly to attempt reconnection after node failure; backoff strategy |
| **Speculative Execution** | Whether to send redundant requests to reduce tail latency |

**Default policies may not match production requirements.** A retry policy that works for idempotent reads may cause duplicate writes. A load balancing policy optimized for single-datacenter deployments will perform poorly across regions. Speculative execution improves latency but increases cluster load.

### Consequences of Misconfiguration

Incorrectly configured driver policies can cause:

- **Cascading failures** — Aggressive retry policies can overwhelm an already struggling node
- **Uneven load** — Poor load balancing concentrates requests on subset of nodes
- **Data inconsistency** — Retrying non-idempotent operations may duplicate writes
- **Unnecessary latency** — Failing over to remote datacenter when local nodes are available
- **Connection storms** — Aggressive reconnection after network partition recovery

### Development Approach

When developing applications against Cassandra:

1. **Understand the policies** — Read the driver documentation for each policy type before writing production code
2. **Configure explicitly** — Do not rely on defaults; configure each policy based on application requirements
3. **Test failure scenarios** — Simulate node failures, network partitions, and high latency during development
4. **Monitor in production** — Track driver metrics (connection pool usage, retry rates, speculative execution triggers)
5. **Consider idempotency** — Design operations to be safely retryable where possible

---

## Section Contents

### Development Tools

- **[AxonOps Workbench](workbench.md)** — Open-source GUI for schema management, query execution, and data exploration
- **[CQLAI](cqlai.md)** — Modern AI-powered CQL shell with rich terminal interface

### References

- **[CQL Reference](../cql/index.md)** — Cassandra Query Language syntax and semantics
- **[Data Modeling](../data-modeling/index.md)** — Principles for designing effective Cassandra data models
- **[Drivers](drivers/index.md)** — Driver architecture, connection management, and policy configuration

