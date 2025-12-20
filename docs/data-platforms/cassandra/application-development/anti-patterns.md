---
title: "Cassandra Application Development Anti-Patterns"
description: "Common application development mistakes with Cassandra. Driver misuse, error handling pitfalls, and production failures."
meta:
  - name: keywords
    content: "Cassandra anti-patterns, driver mistakes, application errors, production failures"
---

# Application Development Anti-Patterns

These patterns compile without errors and pass basic testing. They fail in production when load increases, nodes fail, or edge cases occur. Each anti-pattern includes the failure scenario, symptoms, and correct implementation.

For data modeling anti-patterns (unbounded partitions, tombstones, ALLOW FILTERING), see [Data Modeling Anti-Patterns](../data-modeling/anti-patterns/index.md).

---

## Anti-Pattern Severity Reference

| Anti-Pattern | Severity | Failure Mode |
|--------------|----------|--------------|
| Session per request | Critical | Resource exhaustion, connection storms |
| Retrying non-idempotent writes | Critical | Data corruption, duplicates |
| Ignoring write timeouts | Critical | Silent data loss or duplication |
| Read-modify-write without LWT | Critical | Race conditions, lost updates |
| Synchronous calls in async context | High | Thread pool exhaustion, deadlocks |
| Unbounded IN clauses | High | Coordinator OOM, cascading timeouts |
| Missing local datacenter config | High | Cross-DC latency, failover failures |
| Catching generic exceptions | High | Hidden failures, incorrect recovery |
| Unprepared statements in loops | Medium | Performance degradation, cache churn |
| Batch misuse | Medium | Coordinator overload, timeouts |
| Missing timeouts | Medium | Request hangs, resource leaks |
| LWT overuse | Medium | Performance bottleneck |

---

## Session per Request (Critical)

### The Anti-Pattern

```java
// WRONG: New session for every request
public User getUser(UUID userId) {
    try (CqlSession session = CqlSession.builder()
            .addContactPoint(new InetSocketAddress("localhost", 9042))
            .withLocalDatacenter("dc1")
            .build()) {

        return session.execute(
            "SELECT * FROM users WHERE user_id = ?", userId
        ).one();
    }
}
```

### What Goes Wrong

| Phase | Action | Cost |
|-------|--------|------|
| **Connect** | TCP handshake to contact point | 1-10 ms |
| **Negotiate** | CQL protocol handshake | 5-20 ms |
| **Discover** | Fetch cluster topology | 50-200 ms |
| **Pool** | Open connections to all nodes | 100-500 ms |
| **Execute** | Run the actual query | 2-10 ms |
| **Close** | Tear down all connections | 10-50 ms |

**Total overhead per request: 170-790 ms** for a 2-10 ms query.

At 100 requests/second:
- 100 full connection cycles per second
- 100 × (nodes in cluster) TCP connections opened and closed
- Cluster sees connection storms during traffic spikes
- `nodetool netstats` shows thousands of pending connections

### The Fix

```java
// CORRECT: Single session for application lifetime
public class CassandraService {
    private final CqlSession session;
    private final PreparedStatement selectUser;

    public CassandraService() {
        this.session = CqlSession.builder()
            .addContactPoint(new InetSocketAddress("localhost", 9042))
            .withLocalDatacenter("dc1")
            .build();

        this.selectUser = session.prepare(
            "SELECT * FROM users WHERE user_id = ?"
        );
    }

    public User getUser(UUID userId) {
        Row row = session.execute(selectUser.bind(userId)).one();
        return mapToUser(row);
    }

    public void shutdown() {
        session.close();
    }
}
```

### Detection

```bash
# Connection churn in Cassandra logs
grep "connections" /var/log/cassandra/debug.log | grep -E "(opened|closed)"

# High connection counts
nodetool netstats | grep -A 20 "Mode:"

# In application metrics: session creation rate should be ~0
```

---

## Retrying Non-Idempotent Writes (Critical)

### The Anti-Pattern

```java
// WRONG: Automatic retry on all writes
public void incrementCounter(UUID pageId) {
    int attempts = 0;
    while (attempts < 3) {
        try {
            session.execute(
                "UPDATE page_stats SET views = views + 1 WHERE page_id = ?",
                pageId
            );
            return;
        } catch (Exception e) {
            attempts++;
            if (attempts >= 3) throw e;
        }
    }
}
```

### What Goes Wrong

```
Timeline:
  T+0ms:    Client sends INCREMENT to Coordinator
  T+5ms:    Coordinator sends to Replica A
  T+6ms:    Replica A applies: views = 100 → 101
  T+7ms:    Network hiccup, ACK lost
  T+2000ms: Client timeout, assumes failure
  T+2001ms: Client retry #1 sends INCREMENT
  T+2006ms: Replica A applies: views = 101 → 102  ← DUPLICATE!
  T+2010ms: ACK succeeds

  Result: views = 102 (should be 101)
```

| Operation | Idempotent? | Safe to Retry? |
|-----------|-------------|----------------|
| `SELECT *` | Yes | Yes |
| `INSERT ... IF NOT EXISTS` | Yes | Yes |
| `UPDATE ... SET x = 5` | Yes | Yes |
| `UPDATE ... SET x = x + 1` | **No** | **No** |
| `DELETE` | Yes | Yes |
| `INSERT` (without IF NOT EXISTS) | Depends | Maybe |

### The Fix

```java
// CORRECT: Mark idempotency explicitly
public void setPageViews(UUID pageId, long views) {
    // Idempotent: setting to specific value
    Statement stmt = setViewsStmt.bind(pageId, views)
        .setIdempotent(true);
    session.execute(stmt);
}

public void incrementCounter(UUID pageId) {
    // Non-idempotent: no automatic retry
    Statement stmt = incrementStmt.bind(pageId)
        .setIdempotent(false)
        .setRetryPolicy(FallthroughRetryPolicy.INSTANCE);

    try {
        session.execute(stmt);
    } catch (WriteTimeoutException e) {
        // Log for manual investigation - do NOT retry
        log.error("Counter increment may have failed for page {}: {}",
            pageId, e.getMessage());
        // Optionally: queue for reconciliation
    }
}
```

### Alternative: Use LWT for Idempotency

```java
// Make increment idempotent with request ID
public void incrementWithDedup(UUID pageId, UUID requestId) {
    // Check if already processed
    Row existing = session.execute(
        "SELECT request_id FROM page_updates WHERE page_id = ? AND request_id = ?",
        pageId, requestId
    ).one();

    if (existing != null) {
        return; // Already processed
    }

    // Atomic check-and-update
    ResultSet rs = session.execute(
        "INSERT INTO page_updates (page_id, request_id, processed_at) " +
        "VALUES (?, ?, toTimestamp(now())) IF NOT EXISTS",
        pageId, requestId
    );

    if (rs.wasApplied()) {
        session.execute(
            "UPDATE page_stats SET views = views + 1 WHERE page_id = ?",
            pageId
        );
    }
}
```

---

## Ignoring Write Timeout Results (Critical)

### The Anti-Pattern

```java
// WRONG: Treating timeout as definite failure
public void createOrder(Order order) {
    try {
        session.execute(insertOrder.bind(order.getId(), order.getData()));
        log.info("Order created: {}", order.getId());
    } catch (WriteTimeoutException e) {
        // WRONG: Assuming the write failed
        log.error("Order creation failed: {}", order.getId());
        throw new OrderCreationFailedException(order.getId());
    }
}
```

### What Goes Wrong

A `WriteTimeoutException` means: **"The coordinator didn't receive enough acknowledgments within the timeout period."**

It does NOT mean the write failed:

| WriteType | What Happened | Data State |
|-----------|---------------|------------|
| `SIMPLE` | Coordinator timed out waiting for replicas | Write may exist on 0, 1, 2, or all replicas |
| `BATCH` | Batch log written, mutations may be partial | Batch will eventually complete |
| `BATCH_LOG` | Batch log write timed out | Batch may or may not execute |
| `UNLOGGED_BATCH` | Some mutations may have applied | Partial writes possible |

### The Fix

```java
// CORRECT: Handle timeout as unknown state
public OrderResult createOrder(Order order) {
    try {
        session.execute(insertOrder.bind(order.getId(), order.getData()));
        return OrderResult.success(order.getId());

    } catch (WriteTimeoutException e) {
        log.warn("Order {} write timeout - state unknown. " +
                 "WriteType: {}, received: {}/{} acks",
                 order.getId(),
                 e.getWriteType(),
                 e.getReceived(),
                 e.getBlockFor());

        // Option 1: Return unknown status, let caller decide
        return OrderResult.unknown(order.getId());

        // Option 2: Check if write succeeded (if idempotent insert)
        // return verifyOrderExists(order.getId());

        // Option 3: Queue for reconciliation
        // reconciliationQueue.add(order.getId());
    }
}

// For critical operations: verify state
private OrderResult verifyOrderExists(UUID orderId) {
    Row row = session.execute(
        selectOrder.bind(orderId)
            .setConsistencyLevel(ConsistencyLevel.ALL)
    ).one();

    if (row != null) {
        return OrderResult.success(orderId);
    }
    return OrderResult.failed(orderId);
}
```

---

## Read-Modify-Write Without LWT (Critical)

### The Anti-Pattern

```java
// WRONG: Non-atomic read-modify-write
public void transferFunds(UUID from, UUID to, BigDecimal amount) {
    // Read current balances
    Row fromRow = session.execute(
        "SELECT balance FROM accounts WHERE account_id = ?", from
    ).one();
    Row toRow = session.execute(
        "SELECT balance FROM accounts WHERE account_id = ?", to
    ).one();

    BigDecimal fromBalance = fromRow.getBigDecimal("balance");
    BigDecimal toBalance = toRow.getBigDecimal("balance");

    // Calculate new balances
    BigDecimal newFromBalance = fromBalance.subtract(amount);
    BigDecimal newToBalance = toBalance.add(amount);

    // Write new balances - RACE CONDITION HERE
    session.execute(
        "UPDATE accounts SET balance = ? WHERE account_id = ?",
        newFromBalance, from
    );
    session.execute(
        "UPDATE accounts SET balance = ? WHERE account_id = ?",
        newToBalance, to
    );
}
```

### What Goes Wrong

```
Thread A                          Thread B
────────                          ────────
Read from_balance = 100
                                  Read from_balance = 100
Calculate: 100 - 50 = 50
                                  Calculate: 100 - 30 = 70
Write from_balance = 50
                                  Write from_balance = 70  ← Overwrites!

Result: Account shows 70, but 80 was withdrawn
        Lost update: $50 transfer was overwritten
```

### The Fix: Lightweight Transactions

```java
// CORRECT: Atomic compare-and-set
public TransferResult transferFunds(UUID from, UUID to, BigDecimal amount) {
    // Read with serial consistency
    Row fromRow = session.execute(
        SimpleStatement.newInstance(
            "SELECT balance FROM accounts WHERE account_id = ?", from
        ).setSerialConsistencyLevel(ConsistencyLevel.LOCAL_SERIAL)
    ).one();

    BigDecimal currentBalance = fromRow.getBigDecimal("balance");

    if (currentBalance.compareTo(amount) < 0) {
        return TransferResult.insufficientFunds();
    }

    // Atomic conditional update
    BigDecimal newBalance = currentBalance.subtract(amount);

    ResultSet rs = session.execute(
        "UPDATE accounts SET balance = ? " +
        "WHERE account_id = ? " +
        "IF balance = ?",  // Only if balance hasn't changed
        newBalance, from, currentBalance
    );

    if (!rs.wasApplied()) {
        // Balance changed - retry or fail
        return TransferResult.concurrentModification();
    }

    // Credit destination (separate LWT if needed)
    session.execute(
        "UPDATE accounts SET balance = balance + ? WHERE account_id = ?",
        amount, to
    );

    return TransferResult.success();
}
```

### When LWT Is Not Needed

| Pattern | LWT Required? |
|---------|---------------|
| Last-write-wins updates | No |
| Append-only data (logs, events) | No |
| Counter increments (approximate) | No |
| Unique constraint enforcement | **Yes** |
| Balance/inventory checks | **Yes** |
| State machine transitions | **Yes** |

---

## Synchronous in Async Context (High)

### The Anti-Pattern

```java
// WRONG: Blocking call inside async handler
public CompletableFuture<Response> handleRequest(Request request) {
    return CompletableFuture.supplyAsync(() -> {
        // This blocks the async thread pool!
        Row row = session.execute(selectStmt.bind(request.getId())).one();
        return new Response(row.getString("data"));
    });
}

// WRONG: Blocking to get async result
public Response handleRequestBad(Request request) {
    CompletionStage<AsyncResultSet> future = session.executeAsync(
        selectStmt.bind(request.getId())
    );

    // Blocks thread waiting for async result - defeats the purpose
    AsyncResultSet rs = future.toCompletableFuture().join();
    return new Response(rs.one().getString("data"));
}
```

### What Goes Wrong

| Problem | Impact |
|---------|--------|
| Thread pool exhaustion | All async workers blocked on I/O |
| Deadlock potential | If pool is bounded and all threads wait |
| Latency spikes | New requests queue behind blocked threads |
| Throughput collapse | Async system behaves like sync with fewer threads |

### The Fix

```java
// CORRECT: Fully async chain
public CompletionStage<Response> handleRequest(Request request) {
    return session.executeAsync(selectStmt.bind(request.getId()))
        .thenApply(rs -> rs.one())
        .thenApply(row -> new Response(row.getString("data")));
}

// CORRECT: Async with error handling
public CompletionStage<Response> handleRequestWithErrors(Request request) {
    return session.executeAsync(selectStmt.bind(request.getId()))
        .thenApply(rs -> {
            Row row = rs.one();
            if (row == null) {
                throw new NotFoundException(request.getId());
            }
            return new Response(row.getString("data"));
        })
        .exceptionally(e -> {
            if (e.getCause() instanceof NotFoundException) {
                return Response.notFound();
            }
            log.error("Query failed for {}", request.getId(), e);
            return Response.error();
        });
}
```

### Reactive Streams (Java Driver 4.x)

```java
// CORRECT: Reactive pagination
public Flux<User> getAllUsers() {
    return Flux.from(session.executeReactive(selectAllUsers))
        .map(this::mapToUser);
}

// CORRECT: Backpressure-aware processing
public Mono<Long> countActiveUsers() {
    return Flux.from(session.executeReactive(selectAllUsers))
        .filter(row -> "active".equals(row.getString("status")))
        .count();
}
```

---

## Unbounded IN Clauses (High)

### The Anti-Pattern

```java
// WRONG: Building IN clause from user input
public List<Product> getProducts(List<UUID> productIds) {
    // productIds could have 1000+ items
    String cql = "SELECT * FROM products WHERE product_id IN (" +
        productIds.stream()
            .map(UUID::toString)
            .collect(Collectors.joining(",")) +
        ")";

    return session.execute(cql).all().stream()
        .map(this::mapToProduct)
        .collect(Collectors.toList());
}
```

### What Goes Wrong

| IN Clause Size | Coordinator Memory | Concurrent Sub-queries |
|----------------|-------------------|------------------------|
| 10 | ~10 KB | 10 |
| 100 | ~100 KB | 100 |
| 1,000 | ~1 MB | 1,000 |
| 10,000 | ~10 MB | 10,000 → OOM |

Additional problems:
- Prepared statement cache pollution (each unique IN size = new entry)
- Single slow sub-query delays entire response
- No partial results on failure

### The Fix

```java
// CORRECT: Batch in application with controlled parallelism
public List<Product> getProducts(List<UUID> productIds) {
    int batchSize = 20;
    List<Product> results = new ArrayList<>();

    for (int i = 0; i < productIds.size(); i += batchSize) {
        List<UUID> batch = productIds.subList(
            i, Math.min(i + batchSize, productIds.size())
        );

        ResultSet rs = session.execute(
            selectProductsIn.bind(batch)
        );

        rs.forEach(row -> results.add(mapToProduct(row)));
    }

    return results;
}

// CORRECT: Parallel async with bounded concurrency
public CompletableFuture<List<Product>> getProductsAsync(List<UUID> productIds) {
    Semaphore semaphore = new Semaphore(50); // Max 50 concurrent

    List<CompletableFuture<Product>> futures = productIds.stream()
        .map(id -> CompletableFuture.supplyAsync(() -> {
            try {
                semaphore.acquire();
                try {
                    Row row = session.execute(selectProduct.bind(id)).one();
                    return row != null ? mapToProduct(row) : null;
                } finally {
                    semaphore.release();
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return null;
            }
        }))
        .collect(Collectors.toList());

    return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
        .thenApply(v -> futures.stream()
            .map(CompletableFuture::join)
            .filter(Objects::nonNull)
            .collect(Collectors.toList()));
}
```

---

## Missing Local Datacenter (High)

### The Anti-Pattern

```java
// WRONG: No datacenter configuration
CqlSession session = CqlSession.builder()
    .addContactPoint(new InetSocketAddress("10.0.1.1", 9042))
    .build();  // Will fail or route to wrong DC
```

### What Goes Wrong

| Scenario | Result |
|----------|--------|
| Single DC cluster | Works (sometimes) |
| Multi-DC cluster | Queries route to random DC |
| DC failure | Failover may route to wrong DC |
| Driver 4.x | Throws exception: "No local datacenter set" |

### The Fix

```java
// CORRECT: Always specify local datacenter
CqlSession session = CqlSession.builder()
    .addContactPoint(new InetSocketAddress("10.0.1.1", 9042))
    .withLocalDatacenter("us-east-1")  // Always required
    .build();

// CORRECT: From configuration
CqlSession session = CqlSession.builder()
    .withConfigLoader(
        DriverConfigLoader.fromClasspath("application.conf")
    )
    .build();

// application.conf
datastax-java-driver {
    basic {
        contact-points = ["10.0.1.1:9042", "10.0.1.2:9042"]
        local-datacenter = "us-east-1"
    }
}
```

---

## Catching Generic Exceptions (High)

### The Anti-Pattern

```java
// WRONG: Generic exception handling
public User getUser(UUID userId) {
    try {
        return session.execute(selectUser.bind(userId)).one();
    } catch (Exception e) {
        log.error("Query failed", e);
        return null;  // Hides the real problem
    }
}
```

### What Goes Wrong

| Exception Type | Correct Action | Generic Handler Does |
|----------------|----------------|----------------------|
| `NoNodeAvailableException` | Circuit breaker, alert ops | Returns null |
| `ReadTimeoutException` | Maybe retry | Returns null |
| `InvalidQueryException` | Fix the query (bug) | Returns null |
| `AuthenticationException` | Fix credentials | Returns null |
| `SyntaxError` | Fix CQL syntax (bug) | Returns null |

All failures look the same in logs. Bugs are hidden. Operations doesn't know cluster is down.

### The Fix

```java
// CORRECT: Specific exception handling
public User getUser(UUID userId) {
    try {
        Row row = session.execute(selectUser.bind(userId)).one();
        return row != null ? mapToUser(row) : null;

    } catch (NoNodeAvailableException e) {
        // Cluster is down - this is an emergency
        log.error("CRITICAL: No Cassandra nodes available", e);
        metrics.increment("cassandra.cluster_unavailable");
        throw new ServiceUnavailableException("Database unavailable");

    } catch (ReadTimeoutException e) {
        // Query took too long - might retry
        log.warn("Read timeout for user {}: received {}/{} responses",
            userId, e.getReceived(), e.getBlockFor());
        metrics.increment("cassandra.read_timeout");

        if (e.getReceived() > 0) {
            // Got some data, might be consistent enough
            throw new PartialDataException("Partial read for user " + userId);
        }
        throw new QueryTimeoutException("User query timed out");

    } catch (QueryValidationException e) {
        // Bug in our code - query is malformed
        log.error("BUG: Invalid query for user {}", userId, e);
        throw new IllegalStateException("Invalid query", e);

    } catch (DriverException e) {
        // Other driver errors
        log.error("Driver error for user {}", userId, e);
        throw new DataAccessException("Database error", e);
    }
}
```

---

## Unprepared Statements in Loops (Medium)

### The Anti-Pattern

```java
// WRONG: String concatenation in loop
public void importUsers(List<User> users) {
    for (User user : users) {
        String cql = String.format(
            "INSERT INTO users (user_id, name, email) VALUES (%s, '%s', '%s')",
            user.getId(), user.getName(), user.getEmail()
        );
        session.execute(cql);  // Parsed every time
    }
}
```

### What Goes Wrong

| Problem | Impact |
|---------|--------|
| No prepared statement cache | CQL parsed on every execution |
| No token-aware routing | Coordinator may not route optimally |
| CQL injection vulnerability | `user.getName()` could contain `'); DROP TABLE users; --` |
| String formatting overhead | CPU wasted on string operations |

### The Fix

```java
// CORRECT: Prepare once, bind in loop
public void importUsers(List<User> users) {
    PreparedStatement insertUser = session.prepare(
        "INSERT INTO users (user_id, name, email) VALUES (?, ?, ?)"
    );

    for (User user : users) {
        session.execute(insertUser.bind(
            user.getId(),
            user.getName(),
            user.getEmail()
        ));
    }
}

// BETTER: Async with batching
public CompletableFuture<Void> importUsersAsync(List<User> users) {
    PreparedStatement insertUser = session.prepare(
        "INSERT INTO users (user_id, name, email) VALUES (?, ?, ?)"
    );

    List<CompletableFuture<AsyncResultSet>> futures = users.stream()
        .map(user -> session.executeAsync(insertUser.bind(
            user.getId(),
            user.getName(),
            user.getEmail()
        )).toCompletableFuture())
        .collect(Collectors.toList());

    return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]));
}
```

---

## Batch Misuse (Medium)

### The Anti-Pattern

```java
// WRONG: Batch for bulk operations
public void importProducts(List<Product> products) {
    BatchStatement batch = BatchStatement.builder(BatchType.LOGGED).build();

    for (Product product : products) {
        batch = batch.add(insertProduct.bind(
            product.getId(),
            product.getName(),
            product.getPrice()
        ));
    }

    session.execute(batch);  // 10,000 statements in one batch!
}
```

### What Goes Wrong

Batches in Cassandra are **NOT** for bulk operations:

| What You Think | What Actually Happens |
|----------------|----------------------|
| "Batch = faster bulk insert" | Coordinator must hold entire batch in memory |
| "Batch = transaction" | LOGGED batch only ensures atomicity, not isolation |
| "More in batch = better" | Large batches timeout, overload coordinator |

| Batch Size | Result |
|------------|--------|
| 1-10 statements | OK (if same partition) |
| 10-100 statements | Warning signs |
| 100+ statements | Timeouts, coordinator OOM |

### The Fix

```java
// CORRECT: Batches only for same-partition atomicity
public void updateUserWithAddress(User user, Address address) {
    // Both statements target same partition key
    BatchStatement batch = BatchStatement.builder(BatchType.LOGGED)
        .addStatement(updateUser.bind(user.getId(), user.getName()))
        .addStatement(updateAddress.bind(user.getId(), address.getStreet()))
        .build();

    session.execute(batch);
}

// CORRECT: Async for bulk operations
public CompletableFuture<Void> importProducts(List<Product> products) {
    List<CompletableFuture<AsyncResultSet>> futures = products.stream()
        .map(product -> session.executeAsync(insertProduct.bind(
            product.getId(),
            product.getName(),
            product.getPrice()
        )).toCompletableFuture())
        .collect(Collectors.toList());

    return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]));
}

// CORRECT: UNLOGGED batch for same-partition bulk
public void addOrderItems(UUID orderId, List<OrderItem> items) {
    // All items have same partition key (orderId)
    BatchStatementBuilder batch = BatchStatement.builder(BatchType.UNLOGGED);

    for (OrderItem item : items) {
        batch.addStatement(insertOrderItem.bind(
            orderId,  // Same partition key
            item.getProductId(),
            item.getQuantity()
        ));
    }

    session.execute(batch.build());
}
```

### Batch Guidelines

| Use Case | Batch Type | Max Size |
|----------|------------|----------|
| Atomic multi-table update (same partition) | LOGGED | 5-10 |
| Bulk insert to same partition | UNLOGGED | 10-50 |
| Bulk insert to different partitions | No batch (use async) | N/A |

---

## Missing Timeouts (Medium)

### The Anti-Pattern

```java
// WRONG: No timeout configuration
CqlSession session = CqlSession.builder()
    .addContactPoint(new InetSocketAddress("localhost", 9042))
    .withLocalDatacenter("dc1")
    .build();

// Request can hang indefinitely
Row row = session.execute("SELECT * FROM large_table").one();
```

### What Goes Wrong

- Requests hang during network partitions
- Thread pool exhaustion from blocked requests
- No circuit breaker trigger (never fails, just hangs)
- Application appears frozen

### The Fix

```java
// CORRECT: Configure timeouts
CqlSession session = CqlSession.builder()
    .addContactPoint(new InetSocketAddress("localhost", 9042))
    .withLocalDatacenter("dc1")
    .withConfigLoader(DriverConfigLoader.programmaticBuilder()
        .withDuration(DefaultDriverOption.REQUEST_TIMEOUT, Duration.ofSeconds(5))
        .withDuration(DefaultDriverOption.CONNECTION_INIT_QUERY_TIMEOUT, Duration.ofSeconds(5))
        .withDuration(DefaultDriverOption.CONNECTION_CONNECT_TIMEOUT, Duration.ofSeconds(5))
        .build())
    .build();

// Per-query timeout override
Statement stmt = selectStmt.bind(userId)
    .setTimeout(Duration.ofSeconds(2));
```

| Timeout | Recommended | Description |
|---------|-------------|-------------|
| `REQUEST_TIMEOUT` | 5-10s | Total request time |
| `CONNECTION_CONNECT_TIMEOUT` | 5s | TCP connect time |
| `CONNECTION_INIT_QUERY_TIMEOUT` | 5s | Initial handshake |

---

## LWT Overuse (Medium)

### The Anti-Pattern

```java
// WRONG: LWT for every write
public void saveUser(User user) {
    session.execute(
        "INSERT INTO users (user_id, name, email) VALUES (?, ?, ?) IF NOT EXISTS",
        user.getId(), user.getName(), user.getEmail()
    );
}

public void updateUser(User user) {
    session.execute(
        "UPDATE users SET name = ?, email = ? WHERE user_id = ? IF EXISTS",
        user.getName(), user.getEmail(), user.getId()
    );
}
```

### What Goes Wrong

LWT uses Paxos consensus:

| Operation | Regular Write | LWT |
|-----------|---------------|-----|
| Round trips | 1 | 4 (Prepare, Promise, Accept, Ack) |
| Latency | 2-5 ms | 20-50 ms |
| Throughput | 10,000+/s per partition | ~100/s per partition |

### The Fix

```java
// CORRECT: LWT only when needed
public void saveUser(User user) {
    // Regular insert - last write wins
    session.execute(insertUser.bind(
        user.getId(), user.getName(), user.getEmail()
    ));
}

// LWT only for uniqueness constraint
public boolean registerEmail(String email, UUID userId) {
    ResultSet rs = session.execute(
        "INSERT INTO users_by_email (email, user_id) VALUES (?, ?) IF NOT EXISTS",
        email, userId
    );
    return rs.wasApplied();
}

// LWT for state transitions
public boolean markOrderShipped(UUID orderId) {
    ResultSet rs = session.execute(
        "UPDATE orders SET status = 'shipped' WHERE order_id = ? IF status = 'pending'",
        orderId
    );
    return rs.wasApplied();
}
```

### When to Use LWT

| Use Case | LWT Needed? |
|----------|-------------|
| Unique email registration | Yes |
| Balance check before debit | Yes |
| State machine transitions | Yes |
| Last-write-wins updates | No |
| Append-only logs | No |
| Idempotent upserts | No |

---

## Quick Reference: Anti-Pattern Detection

| Symptom | Likely Anti-Pattern |
|---------|---------------------|
| Connection storm in logs | Session per request |
| Duplicate records appearing | Retrying non-idempotent writes |
| Data inconsistency after timeout | Ignoring write timeout |
| Lost updates | Read-modify-write without LWT |
| Thread pool exhaustion | Sync in async context |
| Coordinator OOM | Unbounded IN clauses |
| Cross-DC latency | Missing local datacenter |
| All errors look the same | Generic exception handling |
| Slow bulk imports | Unprepared statements |
| Batch timeouts | Batch misuse |
| Hanging requests | Missing timeouts |
| Slow partition writes | LWT overuse |

---

## Related Documentation

- **[Data Modeling Anti-Patterns](../data-modeling/anti-patterns/index.md)** - Schema design mistakes
- **[Driver Best Practices](drivers/best-practices.md)** - Correct patterns
- **[Error Handling](drivers/policies/retry.md)** - Retry policies
- **[Prepared Statements](drivers/prepared-statements.md)** - Statement caching
