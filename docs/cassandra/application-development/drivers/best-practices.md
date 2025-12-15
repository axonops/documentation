---
title: "Cassandra Driver Best Practices"
description: "Best practices for Cassandra driver usage. Connection pooling, retry logic, and performance optimization."
meta:
  - name: keywords
    content: "Cassandra driver best practices, connection pooling, retry logic, performance"
---

# Driver Best Practices

This page consolidates production configuration recommendations for Cassandra drivers.

---

## Session Management

### Single Session per Application

Create one session and reuse it throughout the application lifecycle:

```java
// CORRECT: Single session, created once
public class CassandraConfig {
    private static CqlSession session;

    public static synchronized CqlSession getSession() {
        if (session == null) {
            session = CqlSession.builder()
                .withLocalDatacenter("dc1")
                .build();
        }
        return session;
    }

    public static void shutdown() {
        if (session != null) {
            session.close();
        }
    }
}
```

```java
// WRONG: Session per request
public User getUser(UUID id) {
    try (CqlSession session = CqlSession.builder().build()) {  // Expensive!
        return session.execute(...);
    }
}
```

| Aspect | Single Session | Session per Request |
|--------|---------------|---------------------|
| Connection overhead | Once at startup | Every request |
| Metadata discovery | Once | Every request |
| Prepared statement cache | Shared | Rebuilt each time |
| Resource usage | Predictable | Unbounded |

### Graceful Shutdown

Close the session cleanly on application shutdown:

```java
Runtime.getRuntime().addShutdownHook(new Thread(() -> {
    session.close();  // Waits for in-flight requests
}));
```

---

## Connection Configuration

### Contact Points

Provide multiple contact points for initial connection:

```java
CqlSession session = CqlSession.builder()
    .addContactPoint(new InetSocketAddress("10.0.1.1", 9042))
    .addContactPoint(new InetSocketAddress("10.0.1.2", 9042))
    .addContactPoint(new InetSocketAddress("10.0.1.3", 9042))
    .withLocalDatacenter("dc1")
    .build();
```

The driver only needs one successful connection to discover the full cluster topology, but multiple contact points provide redundancy during startup.

### Local Datacenter

Always configure local datacenter explicitly in multi-DC deployments:

```java
// REQUIRED for multi-DC
.withLocalDatacenter("dc1")
```

Failure to configure results in potential cross-DC routing with high latency.

### Connection Pool Sizing

Default pool settings work for most workloads. Adjust only when:

- Measured stream exhaustion occurs
- Throughput exceeds tens of thousands requests/second per node
- Monitoring shows pool-related bottlenecks

```java
// Only if needed based on measurements
.withPoolingOptions(
    PoolingOptions.builder()
        .setConnectionsPerHost(DriverConnectionGroup.REMOTE, 1, 1)
        .setConnectionsPerHost(DriverConnectionGroup.LOCAL, 2, 4)
        .build())
```

---

## Query Execution

### Use Prepared Statements

Prepare all production queries:

```java
// Prepare once at startup
private final PreparedStatement selectUser = session.prepare(
    "SELECT * FROM users WHERE user_id = ?");

// Execute with bound values
public User getUser(UUID userId) {
    Row row = session.execute(selectUser.bind(userId)).one();
    return mapToUser(row);
}
```

Benefits:

- Reduced parsing overhead
- Token-aware routing
- Protection against CQL injection

### Set Appropriate Consistency Levels

Choose consistency level based on requirements:

```java
Statement statement = selectUser.bind(userId)
    .setConsistencyLevel(ConsistencyLevel.LOCAL_QUORUM);  // Explicit
```

| Use Case | Recommended CL |
|----------|---------------|
| Strong consistency reads | LOCAL_QUORUM |
| Strong consistency writes | LOCAL_QUORUM |
| Eventually consistent reads | LOCAL_ONE |
| Analytics/reporting | ONE |
| Cross-DC consistency | QUORUM or EACH_QUORUM |

### Set Query Timeouts

Configure appropriate timeouts:

```java
Statement statement = selectUser.bind(userId)
    .setTimeout(Duration.ofSeconds(5));  // Query-specific timeout
```

| Timeout Type | Recommendation |
|--------------|----------------|
| Read timeout | 5-10 seconds (longer than expected P99) |
| Write timeout | 10-30 seconds (allow for hints, batches) |
| Connection timeout | 5 seconds |

---

## Error Handling

### Handle Specific Exceptions

```java
try {
    session.execute(statement);
} catch (NoNodeAvailableException e) {
    // All nodes down - circuit breaker or fail
    log.error("Cluster unavailable", e);
    throw new ServiceUnavailableException();

} catch (QueryExecutionException e) {
    if (e instanceof ReadTimeoutException) {
        // Replica(s) didn't respond - may retry
        ReadTimeoutException rte = (ReadTimeoutException) e;
        log.warn("Read timeout: received {}/{} required",
            rte.getReceived(), rte.getRequired());

    } else if (e instanceof WriteTimeoutException) {
        // Write may or may not have succeeded
        WriteTimeoutException wte = (WriteTimeoutException) e;
        log.error("Write timeout for {}: received {}/{}",
            wte.getWriteType(), wte.getReceived(), wte.getRequired());
        // DO NOT retry non-idempotent writes automatically

    } else if (e instanceof UnavailableException) {
        // Not enough replicas alive
        UnavailableException ue = (UnavailableException) e;
        log.warn("Unavailable: alive {}/{} required",
            ue.getAlive(), ue.getRequired());
    }
}
```

### Idempotency Marking

Mark idempotent operations explicitly:

```java
// Safe to retry
Statement readStatement = selectUser.bind(userId)
    .setIdempotent(true);

// NOT safe to retry
Statement counterStatement = updateCounter.bind(pageId)
    .setIdempotent(false);
```

---

## Policy Configuration

### Production Policy Template

```java
CqlSession session = CqlSession.builder()
    .addContactPoints(contactPoints)
    .withLocalDatacenter("dc1")

    // Load balancing: token-aware with DC awareness
    .withLoadBalancingPolicy(
        DefaultLoadBalancingPolicy.builder()
            .withLocalDatacenter("dc1")
            .build())

    // Retry: conservative, respects idempotency
    .withRetryPolicy(DefaultRetryPolicy.INSTANCE)

    // Reconnection: exponential backoff
    .withReconnectionPolicy(
        ExponentialReconnectionPolicy.builder()
            .withBaseDelay(Duration.ofSeconds(1))
            .withMaxDelay(Duration.ofMinutes(5))
            .build())

    // Speculative execution: disabled by default
    // Enable only for idempotent, latency-sensitive queries
    // .withSpeculativeExecutionPolicy(...)

    .build();
```

### Per-Query Policy Override

Override policies for specific query types:

```java
// Latency-sensitive read with speculative execution
Statement fastRead = selectUser.bind(userId)
    .setIdempotent(true)
    .setSpeculativeExecutionPolicy(speculativePolicy);

// Non-idempotent write with no retry
Statement counterUpdate = incrementCounter.bind(pageId)
    .setIdempotent(false)
    .setRetryPolicy(FallthroughRetryPolicy.INSTANCE);
```

---

## Monitoring

### Essential Metrics

Monitor these driver metrics:

| Metric Category | Key Metrics |
|-----------------|-------------|
| Latency | Request latency percentiles (P50, P95, P99) |
| Throughput | Requests per second |
| Errors | Error rate by type (timeout, unavailable, etc.) |
| Connections | Open connections per node |
| Pool | In-flight requests, available streams |
| Retries | Retry rate, retry success rate |
| Speculative | Trigger rate, win rate |

### Health Checks

Implement application health checks:

```java
public boolean isHealthy() {
    try {
        // Simple query to verify connectivity
        session.execute("SELECT now() FROM system.local");
        return true;
    } catch (Exception e) {
        return false;
    }
}
```

### Logging

Configure appropriate driver logging:

```xml
<!-- Log connection events -->
<logger name="com.datastax.oss.driver.internal.core.pool" level="INFO"/>

<!-- Log retries and speculative execution -->
<logger name="com.datastax.oss.driver.internal.core.retry" level="DEBUG"/>

<!-- Reduce noise from metadata refresh -->
<logger name="com.datastax.oss.driver.internal.core.metadata" level="WARN"/>
```

---

## Common Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Session per request | Massive overhead | Single shared session |
| Unprepared statements in loops | Parsing overhead, no token-aware | Prepare and reuse |
| Ignoring local datacenter | Cross-DC latency | Configure explicitly |
| Retrying non-idempotent writes | Data corruption | Mark idempotency, custom retry |
| Unbounded IN clauses | Prepared statement cache churn | Fixed sizes or pagination |
| Synchronous calls in async context | Thread pool exhaustion | Use async API consistently |
| No timeout configuration | Requests hang indefinitely | Set explicit timeouts |
| Catching generic Exception | Hides specific error handling | Catch specific exceptions |

---

## Checklist

Before deploying to production:

- [ ] Single session instance shared across application
- [ ] Local datacenter configured explicitly
- [ ] All queries use prepared statements
- [ ] Consistency levels set explicitly
- [ ] Timeouts configured appropriately
- [ ] Idempotent operations marked
- [ ] Error handling for specific exception types
- [ ] Driver metrics exported to monitoring
- [ ] Health check endpoint implemented
- [ ] Graceful shutdown configured
- [ ] Connection pool sized appropriately (if non-default)
- [ ] Retry policy reviewed for workload
- [ ] Speculative execution evaluated (if latency-sensitive)

---

## Related Documentation

- **[Connection Management](connection-management.md)** — Connection pooling details
- **[Policies](policies/index.md)** — Policy configuration reference
- **[Prepared Statements](prepared-statements.md)** — Statement preparation and caching

