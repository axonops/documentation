---
title: "Lightweight Transaction Errors"
description: "Troubleshooting Cassandra lightweight transaction (LWT) issues including Paxos clock conflicts, mixing LWT with non-LWT operations, and consistency problems."
meta:
  - name: keywords
    content: "LWT errors, Paxos, IF NOT EXISTS, IF EXISTS, CAS, compare-and-set, Cassandra troubleshooting"
search:
  boost: 3
---

# Lightweight Transaction Errors

This page covers common issues encountered when using Cassandra lightweight transactions (LWT), including Paxos-related problems and the pitfalls of mixing LWT with non-LWT operations.

---

## LWT and Non-LWT Mixing Issues

### Symptoms

- A `DELETE` operation returns success, but the row still exists when queried
- An `UPDATE` appears to succeed, but the data remains unchanged
- Data inconsistencies when the same partition is accessed by both LWT and non-LWT operations
- Intermittent failures where operations "sometimes work" depending on timing

### Root Cause

Paxos (the consensus protocol underlying LWT) uses its own **hybrid-logical clock** that is separate from the regular Cassandra timestamp mechanism. When you mix LWT operations (e.g., `INSERT ... IF NOT EXISTS`) with non-LWT operations (e.g., standard `DELETE`) on the same data:

1. The LWT operation commits with a Paxos-managed timestamp
2. The non-LWT operation uses a client-side or coordinator timestamp
3. These timestamps are not coordinated, so the non-LWT operation may use a timestamp that appears "older" than the LWT commit
4. Cassandra's last-write-wins semantics cause the non-LWT operation to be effectively ignored

This is not a bug—it is inherent to how Paxos ensures linearizability within LWT operations while remaining decoupled from standard writes.

### Diagnostics

**Step 1: Identify the operation pattern**

Review your application code for patterns like:

```sql
-- LWT insert
INSERT INTO table (pk, data) VALUES (?, ?) IF NOT EXISTS;

-- Followed by non-LWT delete
DELETE FROM table WHERE pk = ?;
```

**Step 2: Verify with tracing**

Enable tracing to see the actual timestamps used:

```sql
TRACING ON;

-- Execute your LWT operation
INSERT INTO users (user_id, name) VALUES (123, 'test') IF NOT EXISTS;

-- Execute your non-LWT operation
DELETE FROM users WHERE user_id = 123;

-- Query to verify
SELECT * FROM users WHERE user_id = 123;

TRACING OFF;
```

Examine the trace output for timestamp discrepancies between operations.

**Step 3: Check for timing-dependent behavior**

If adding a delay between operations changes the outcome, you have confirmed an LWT/non-LWT mixing issue:

```python
# If this pattern shows different results with/without sleep,
# you have an LWT mixing issue
session.execute("INSERT INTO t (pk) VALUES (1) IF NOT EXISTS")
time.sleep(1)  # Remove this to reproduce the issue
session.execute("DELETE FROM t WHERE pk = 1")
```

### Resolution

**Option 1: Use LWT consistently (RECOMMENDED)**

If data is inserted with `IF NOT EXISTS`, delete it with `IF EXISTS`:

```sql
-- Insert with LWT
INSERT INTO users (user_id, name) VALUES (123, 'test') IF NOT EXISTS;

-- Delete with LWT (consistent)
DELETE FROM users WHERE user_id = 123 IF EXISTS;
```

This ensures both operations go through Paxos and use the same clock domain.

**Option 2: Avoid LWT if not required**

If you do not need the linearizability guarantees of LWT, use standard operations throughout:

```sql
-- Standard insert (no IF condition)
INSERT INTO users (user_id, name) VALUES (123, 'test');

-- Standard delete
DELETE FROM users WHERE user_id = 123;
```

**Option 3: Accept the trade-offs (NOT RECOMMENDED)**

If you understand the risks and cannot change your data model:

1. Add application-level delays between LWT and non-LWT operations (fragile, timing-dependent)
2. Implement verification loops that retry operations if the expected state is not achieved
3. Accept that some operations may silently fail

!!! warning "Delays Are Not a Solution"
    Adding `sleep()` or delays between operations is not a reliable solution. The required delay is timing-dependent and varies based on cluster load, network conditions, and replication factor. What works in testing may fail in production.

### Prevention

1. **Establish LWT boundaries**: Decide at the table or partition level whether data will be managed with LWT. Document this decision.
2. **Use LWT for all operations on LWT-managed data**: If `INSERT ... IF NOT EXISTS` is used, also use `UPDATE ... IF` and `DELETE ... IF EXISTS`.
3. **Code review for mixing**: Add linting or code review checks to catch LWT/non-LWT mixing on the same tables.
4. **Consider Accord**: Cassandra 5.0+ introduces Accord transactions which may provide better semantics for complex transactional patterns.

---

## Paxos Contention Errors

### Symptoms

- High latency on LWT operations
- `CasWriteTimeoutException` errors
- Increased Paxos round trips visible in tracing
- LWT throughput significantly lower than expected

### Root Cause

When multiple clients attempt LWT operations on the same partition simultaneously, Paxos contention occurs. Each conflicting operation must retry with a higher ballot number, causing:

- Multiple round trips per operation
- Increased latency
- Potential timeouts under heavy contention

### Diagnostics

```sql
-- Check CAS metrics
nodetool tpstats | grep -i paxos

-- Enable tracing to see contention
TRACING ON;
UPDATE accounts SET balance = 100 WHERE id = 1 IF balance > 0;
TRACING OFF;
```

Look for multiple PREPARE/PROMISE cycles in the trace output.

### Resolution

1. **Reduce contention**: Redesign data model to spread hot partitions
2. **Increase timeouts**: Adjust `cas_contention_timeout` in `cassandra.yaml` if timeouts are premature
3. **Implement backoff**: Add exponential backoff in application retry logic
4. **Batch related operations**: Use LWT batches to combine multiple operations on the same partition

---

## LWT Timeout Behavior

### Symptoms

- `WriteTimeoutException` during LWT operations
- Uncertainty about whether the operation was applied
- Duplicate data after retry attempts

### Root Cause

When an LWT times out, the operation may have partially completed (Paxos PREPARE succeeded but PROPOSE failed, or PROPOSE succeeded but acknowledgment was lost). The outcome is undefined.

### Resolution

**After a timeout, you MUST read to verify state before retrying:**

```java
try {
    session.execute(lwtStatement);
} catch (WriteTimeoutException e) {
    // Read to determine actual state
    Row current = session.execute(readStatement).one();
    if (current == null || !expectedState(current)) {
        // Safe to retry
        session.execute(lwtStatement);
    }
}
```

See [Failure Semantics](../../cql/dml/lightweight-transactions.md#failure-semantics) for detailed timeout handling guidance.

---

## Related Documentation

- [Lightweight Transactions Reference](../../cql/dml/lightweight-transactions.md) - Complete LWT documentation
- [Consistency Levels](../../architecture/distributed-data/consistency.md) - Understanding SERIAL and LOCAL_SERIAL
- [Troubleshooting Overview](../index.md) - General troubleshooting framework
