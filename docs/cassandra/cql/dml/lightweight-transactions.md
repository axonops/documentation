---
description: "Lightweight transactions (LWT) in CQL using IF conditions. Compare-and-set operations with Paxos."
meta:
  - name: keywords
    content: "lightweight transactions, LWT, IF EXISTS, IF NOT EXISTS, Paxos, Cassandra"
---

# Lightweight Transactions

Lightweight Transactions (LWT) provide linearizable consistency through compare-and-set operations. They use the Paxos consensus protocol to ensure that only one concurrent operation succeeds when multiple clients attempt to modify the same data.

---

## Overview

### The Problem LWT Solves

Standard Cassandra writes use last-write-wins semantics—concurrent writes to the same row can overwrite each other unpredictably:

```graphviz dot lwt-race-condition.svg
digraph race_condition {
    rankdir=TB;
    node [fontname="Helvetica", fontsize=11];
    edge [fontname="Helvetica", fontsize=10];

    subgraph cluster_problem {
        label="Problem: Last-Write-Wins Race Condition";
        style=filled;
        fillcolor="#f8d7da";

        initial [label="inventory.quantity = 1", shape=box, style=filled, fillcolor="#e8f4f8"];

        clientA [label="Client A\nReads quantity = 1\nWants to decrement", shape=box, style=filled, fillcolor="#fff3cd"];
        clientB [label="Client B\nReads quantity = 1\nWants to decrement", shape=box, style=filled, fillcolor="#fff3cd"];

        writeA [label="UPDATE SET quantity = 0", shape=box, style=filled, fillcolor="#d4edda"];
        writeB [label="UPDATE SET quantity = 0", shape=box, style=filled, fillcolor="#d4edda"];

        result [label="Final: quantity = 0\nBut TWO items were 'sold'!\n(inventory went negative)", shape=box, style=filled, fillcolor="#f8d7da"];

        initial -> clientA;
        initial -> clientB;
        clientA -> writeA;
        clientB -> writeB;
        writeA -> result;
        writeB -> result;
    }
}
```

### How LWT Solves It

LWT ensures read-modify-write is atomic:

```graphviz dot lwt-solution.svg
digraph lwt_solution {
    rankdir=TB;
    node [fontname="Helvetica", fontsize=11];
    edge [fontname="Helvetica", fontsize=10];

    subgraph cluster_solution {
        label="Solution: Lightweight Transaction";
        style=filled;
        fillcolor="#d4edda";

        initial [label="inventory.quantity = 1", shape=box, style=filled, fillcolor="#e8f4f8"];

        clientA [label="Client A\nUPDATE ... IF quantity = 1", shape=box, style=filled, fillcolor="#fff3cd"];
        clientB [label="Client B\nUPDATE ... IF quantity = 1", shape=box, style=filled, fillcolor="#fff3cd"];

        paxos [label="Paxos Consensus\n(serializes operations)", shape=box, style=filled, fillcolor="#fff3cd"];

        resultA [label="Client A: [applied] = true\nquantity = 0", shape=box, style=filled, fillcolor="#d4edda"];
        resultB [label="Client B: [applied] = false\nquantity = 0 returned", shape=box, style=filled, fillcolor="#f8d7da"];

        initial -> clientA;
        initial -> clientB;
        clientA -> paxos;
        clientB -> paxos;
        paxos -> resultA [label="First"];
        paxos -> resultB [label="Second"];
    }
}
```

### Historical Context

| Version | LWT Feature |
|---------|-------------|
| 2.0 | Initial LWT implementation (Paxos) |
| 2.1 | Performance improvements |
| 3.0 | Batch LWT support improvements |
| 4.0 | Paxos state cleanup, better timeouts |
| 5.0 | Accord transaction protocol (future) |

---

## Paxos Consensus

### What Is Paxos?

Paxos is a distributed consensus algorithm that ensures agreement among nodes even when some nodes fail. Cassandra implements a variant called "single-decree Paxos" for LWT.

### Paxos Phases

```graphviz dot lwt-paxos-phases.svg
digraph paxos {
    rankdir=TB;
    node [fontname="Helvetica", fontsize=11];
    edge [fontname="Helvetica", fontsize=10];

    client [label="Client\nUPDATE ... IF ...", shape=box, style=filled, fillcolor="#e8f4f8"];

    subgraph cluster_phases {
        label="Paxos Consensus (4 Round Trips)";
        style=filled;
        fillcolor="#f8f9fa";

        prepare [label="1. PREPARE\nCoordinator → Replicas\n'I want to propose ballot N'", shape=box, style=filled, fillcolor="#fff3cd"];
        promise [label="2. PROMISE\nReplicas → Coordinator\n'I promise to accept ballot ≥ N'", shape=box, style=filled, fillcolor="#fff3cd"];
        read [label="3. READ\nGet current value to\nevaluate IF condition", shape=box, style=filled, fillcolor="#fff3cd"];
        propose [label="4. PROPOSE\nCoordinator → Replicas\n'Commit this value'", shape=box, style=filled, fillcolor="#fff3cd"];
        accept [label="5. ACCEPT\nReplicas → Coordinator\n'Value committed'", shape=box, style=filled, fillcolor="#d4edda"];
    }

    result [label="Return [applied] = true/false", shape=box, style=filled, fillcolor="#e8f4f8"];

    client -> prepare;
    prepare -> promise;
    promise -> read;
    read -> propose;
    propose -> accept;
    accept -> result;
    result -> client;
}
```

### Why LWT Is Slow

| Operation | Round Trips | Typical Latency |
|-----------|-------------|-----------------|
| Regular write | 1 | 1-5ms |
| Regular read | 1 | 1-5ms |
| LWT | 4 | 10-50ms |

**Contributing factors:**

- Multiple network round trips
- Contention handling (ballot conflicts)
- Serial execution per partition

---

## Synopsis

### INSERT IF NOT EXISTS

```cqlsyntax
INSERT INTO *table*
    ( *columns* )
    VALUES ( *values* )
    IF NOT EXISTS
```

### UPDATE IF / IF EXISTS

```cqlsyntax
UPDATE *table*
    SET *assignments*
    WHERE *primary_key*
    IF EXISTS
    | IF *condition* [ AND *condition* ... ]
```

### DELETE IF / IF EXISTS

```cqlsyntax
DELETE FROM *table*
    WHERE *primary_key*
    IF EXISTS
    | IF *condition* [ AND *condition* ... ]
```

**condition:**

```cqlsyntax
*column_name* *operator* *value*
| *column_name* [ *index* ] *operator* *value*
| *column_name* [ *key* ] *operator* *value*
| *column_name* IN ( *values* )
```

**operator:**

```cqlsyntax
= | != | < | > | <= | >= | IN
```

---

## INSERT IF NOT EXISTS

Ensures row creation only if it doesn't exist:

```sql
INSERT INTO users (user_id, username, email)
VALUES (uuid(), 'alice', 'alice@example.com')
IF NOT EXISTS;
```

### Results

**When applied (row didn't exist):**

```
 [applied]
-----------
      True
```

**When not applied (row exists):**

```
 [applied] | user_id                              | username | email
-----------+--------------------------------------+----------+---------------------
     False | 550e8400-e29b-41d4-a716-446655440000 | alice    | alice@example.com
```

The existing row values are returned for client decision-making.

### Use Cases

| Use Case | Example |
|----------|---------|
| Unique usernames | `INSERT INTO usernames (username, user_id) VALUES (?, ?) IF NOT EXISTS` |
| Idempotent writes | Prevent duplicate event processing |
| Resource allocation | First-come-first-served |

---

## UPDATE IF EXISTS

Updates only if row exists:

```sql
UPDATE users
SET last_login = toTimestamp(now())
WHERE user_id = ?
IF EXISTS;
```

**Use cases:**

- Don't create accidental rows
- Verify row presence before modification
- Avoid orphan data

## UPDATE IF Condition

Conditional update based on column values:

```sql
UPDATE inventory
SET quantity = quantity - 1
WHERE product_id = 'SKU-001'
IF quantity > 0;
```

### Multiple Conditions

```sql
UPDATE accounts
SET balance = balance - 100
WHERE account_id = ?
IF balance >= 100
  AND status = 'active'
  AND frozen = false;
```

### Collection Conditions

```sql
-- Check list element
UPDATE users
SET phone_numbers = ?
WHERE user_id = ?
IF phone_numbers[0] = '+1-555-0100';

-- Check map entry
UPDATE users
SET preferences = preferences + {'theme': 'dark'}
WHERE user_id = ?
IF preferences['theme'] = 'light';
```

---

## DELETE IF EXISTS / IF Condition

```sql
-- Delete only if exists
DELETE FROM sessions
WHERE session_id = ?
IF EXISTS;

-- Conditional delete
DELETE FROM users
WHERE user_id = ?
IF status = 'inactive'
  AND last_login < '2023-01-01';
```

---

## Serial Consistency Levels

LWT operations use special consistency levels:

### SERIAL

Global linearizability across all datacenters:

```sql
-- All replicas participate in Paxos
CONSISTENCY SERIAL;
UPDATE accounts SET balance = 100 WHERE id = ? IF balance = 50;
```

**Behavior:**

- Paxos runs across all replicas cluster-wide
- Highest consistency guarantee
- Highest latency (cross-DC round trips)

### LOCAL_SERIAL

Linearizability within local datacenter only:

```sql
-- Only local DC participates
CONSISTENCY LOCAL_SERIAL;
UPDATE accounts SET balance = 100 WHERE id = ? IF balance = 50;
```

**Behavior:**

- Paxos limited to local datacenter
- Lower latency than SERIAL
- Not linearizable across datacenters

### Choosing Serial Consistency

| Scenario | Recommended |
|----------|-------------|
| Single datacenter | Either (same behavior) |
| Multi-DC, local consistency acceptable | LOCAL_SERIAL |
| Multi-DC, global consistency required | SERIAL |
| Low latency priority | LOCAL_SERIAL |

---

## Contention and Retries

### Contention Handling

When multiple clients try LWT on the same partition:

```graphviz dot lwt-contention.svg
digraph contention {
    rankdir=TB;
    node [fontname="Helvetica", fontsize=11];
    edge [fontname="Helvetica", fontsize=10];

    clientA [label="Client A\nBallot 100", shape=box, style=filled, fillcolor="#d4edda"];
    clientB [label="Client B\nBallot 101", shape=box, style=filled, fillcolor="#f8d7da"];

    paxos [label="Paxos\nPrefers higher ballot", shape=box, style=filled, fillcolor="#fff3cd"];

    winA [label="Client A\nMust retry with\nhigher ballot", shape=box, style=filled, fillcolor="#f8d7da"];
    winB [label="Client B\nProceeds", shape=box, style=filled, fillcolor="#d4edda"];

    clientA -> paxos;
    clientB -> paxos;
    paxos -> winA [label="loses"];
    paxos -> winB [label="wins"];
}
```

### Client-Side Retry Logic

```java
// Java driver example with retry
int maxRetries = 5;
for (int i = 0; i < maxRetries; i++) {
    ResultSet rs = session.execute(lwtStatement);
    Row row = rs.one();

    if (row.getBool("[applied]")) {
        return true;  // Success
    }

    // Read current value and decide whether to retry
    int currentValue = row.getInt("quantity");
    if (currentValue <= 0) {
        return false;  // Can't complete operation
    }

    // Exponential backoff
    Thread.sleep((long) Math.pow(2, i) * 100);
}
throw new RuntimeException("Max retries exceeded");
```

### CAS (Compare-And-Set) Pattern

```sql
-- Read current state
SELECT version, content FROM documents WHERE doc_id = ?;

-- Attempt update with version check
UPDATE documents
SET content = 'new content', version = 6
WHERE doc_id = ?
IF version = 5;

-- If [applied] = false, re-read and retry
```

---

## Performance Considerations

### When to Use LWT

!!! tip "Good LWT Use Cases"
    1. **Unique constraints**: Username uniqueness, email uniqueness
    2. **Inventory management**: Prevent overselling
    3. **Idempotent operations**: Exactly-once processing
    4. **Optimistic locking**: Version-based updates
    5. **Resource allocation**: First-come-first-served

### When to Avoid LWT

!!! warning "Avoid LWT For"
    1. **High-throughput operations**: Consider different data model
    2. **Non-critical uniqueness**: Eventually consistent may suffice
    3. **Counters**: Use native counter columns instead
    4. **Cross-partition atomicity**: LWT is per-partition only

### Performance Metrics

```yaml
# Typical LWT latencies
single_partition_lwt: 15-30ms
contended_lwt: 50-200ms
cross_dc_lwt: 50-100ms

# Throughput impact
regular_write_throughput: 10000/s per partition
lwt_throughput: 500-1000/s per partition
```

### Monitoring LWT

```bash
# Cassandra metrics
nodetool proxyhistograms  # Look at CAS latencies

# CQL tracing
TRACING ON;
UPDATE users SET name = 'Alice' WHERE id = 1 IF name = 'Bob';
```

---

## Batches with LWT

LWT can be used in batches with special semantics:

```sql
BEGIN BATCH
    INSERT INTO users (user_id, username) VALUES (?, 'alice') IF NOT EXISTS;
    INSERT INTO usernames (username, user_id) VALUES ('alice', ?) IF NOT EXISTS;
APPLY BATCH;
```

### Batch LWT Behavior

- All conditions must be on same partition OR...
- Batch becomes a multi-partition Paxos (very expensive)
- All conditions evaluated atomically
- If ANY condition fails, entire batch fails

!!! danger "Multi-Partition LWT Batches"
    Multi-partition LWT batches require Paxos across all involved partitions, dramatically increasing latency and contention. Avoid if possible.

---

## Restrictions

!!! danger "Restrictions"
    **Timestamps:**

    - Cannot use `USING TIMESTAMP` with IF conditions
    - Paxos manages timestamps internally

    **Counters:**

    - Counter columns do not support IF conditions
    - Use regular counter increment/decrement

    **Scope:**

    - LWT is per-partition only
    - Cannot coordinate across partitions without batch
    - No cross-table LWT

    **Conditions:**

    - Conditions can only reference non-primary-key columns
    - Cannot reference columns in SET clause (no self-reference)
    - Collection element conditions require proper syntax

---

## Examples

### Unique Username Registration

```sql
-- Reserve username
INSERT INTO usernames (username, user_id, created_at)
VALUES ('desired_name', ?, toTimestamp(now()))
IF NOT EXISTS;

-- If applied, create user
-- If not applied, username taken
```

### Inventory Decrement

```sql
UPDATE inventory
SET quantity = quantity - 1,
    last_sale = toTimestamp(now())
WHERE product_id = 'SKU-001'
IF quantity > 0;

-- Handle result
-- [applied] = true: sale completed
-- [applied] = false: out of stock
```

### Optimistic Locking

```sql
-- Attempt update
UPDATE documents
SET content = 'updated content',
    version = 5,
    updated_at = toTimestamp(now()),
    updated_by = 'user123'
WHERE doc_id = ?
IF version = 4;

-- If [applied] = false, someone else modified
-- Re-read, merge changes, retry
```

### Account Balance Transfer

```sql
-- Debit source (with balance check)
UPDATE accounts
SET balance = balance - 100
WHERE account_id = 'source'
IF balance >= 100;

-- Only if debit succeeded, credit destination
-- (Application handles coordination)
```

### Session Management

```sql
-- Create session if user has no active session
INSERT INTO user_sessions (user_id, session_id, created_at)
VALUES (?, uuid(), toTimestamp(now()))
IF NOT EXISTS;

-- Invalidate specific session
DELETE FROM user_sessions
WHERE user_id = ? AND session_id = ?
IF EXISTS;
```

### Distributed Lock

```sql
-- Acquire lock
INSERT INTO locks (lock_name, owner, acquired_at)
VALUES ('resource_x', 'node_1', toTimestamp(now()))
IF NOT EXISTS;

-- Release lock (verify ownership)
DELETE FROM locks
WHERE lock_name = 'resource_x'
IF owner = 'node_1';
```

---

## Future: Accord Transactions

Cassandra 5.0+ introduces Accord, a new transaction protocol:

| Aspect | Paxos (LWT) | Accord |
|--------|-------------|--------|
| Scope | Single partition | Multi-partition |
| Consistency | Linearizable | Serializable |
| Latency | 4 round trips | 2 round trips (optimistic) |
| Throughput | Limited | Higher |

Accord enables true multi-partition transactions without the limitations of batch LWT.

---

## Related Documentation

- **[INSERT](insert.md)** - IF NOT EXISTS
- **[UPDATE](update.md)** - IF condition
- **[DELETE](delete.md)** - IF EXISTS
- **[BATCH](batch.md)** - LWT batches
