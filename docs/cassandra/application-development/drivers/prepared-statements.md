# Prepared Statements

Prepared statements are the recommended method for executing CQL queries in production applications. They provide performance benefits, security protection, and enable token-aware routing.

---

## How Prepared Statements Work

Prepared statements separate query parsing from execution:

### Simple Statement (every execution)

```mermaid
sequenceDiagram
    participant App as Application
    participant C as Cassandra

    App->>C: SELECT * FROM users WHERE id = 'abc123'
    Note right of C: Parse query
    Note right of C: Validate schema
    Note right of C: Create execution plan
    Note right of C: Execute query
    C-->>App: Results
```

### Prepared Statement

**PREPARE phase (once):**

```mermaid
sequenceDiagram
    participant App as Application
    participant C as Cassandra

    App->>C: PREPARE: SELECT * FROM users WHERE id = ?
    Note right of C: Parse query
    Note right of C: Validate schema
    Note right of C: Create execution plan
    Note right of C: Cache plan with ID
    C-->>App: Prepared ID + column metadata
```

**EXECUTE phase (every request):**

```mermaid
sequenceDiagram
    participant App as Application
    participant C as Cassandra

    App->>C: EXECUTE: Prepared ID + [bound values]
    Note right of C: Look up cached plan
    Note right of C: Execute (no parsing)
    C-->>App: Results
```

---

## Performance Benefits

### Reduced Server-Side Overhead

| Operation | Simple Statement | Prepared Statement |
|-----------|-----------------|-------------------|
| Parse query | Every request | Once |
| Validate schema | Every request | Once |
| Create plan | Every request | Once |
| Execute | Every request | Every request |

For high-throughput workloads, the parsing overhead is significant:

```
Throughput comparison (10,000 queries/sec):

Simple statements:
  10,000 × (parse + validate + plan + execute)
  CPU overhead: ~30% spent on parsing

Prepared statements:
  1 × (parse + validate + plan)
  10,000 × (execute only)
  CPU overhead: <5% for statement handling
```

### Token-Aware Routing

Prepared statements enable token-aware routing because the driver knows the partition key structure:

```mermaid
sequenceDiagram
    participant App as Application
    participant Driver as Driver
    participant N1 as Node 1 (Replica)
    participant N2 as Node 2
    participant N3 as Node 3

    Note over App,Driver: Preparation Phase
    App->>Driver: Prepare: SELECT * FROM users<br/>WHERE user_id = ? AND region = ?
    Driver->>N1: PREPARE request
    N1-->>Driver: Prepared ID + Metadata:<br/>- user_id: partition key[0]<br/>- region: partition key[1]

    Note over App,Driver: Execution Phase
    App->>Driver: Execute with user_id='abc', region='us-east'
    Note over Driver: Extract partition key values
    Note over Driver: Calculate token = murmur3('abc', 'us-east')
    Note over Driver: Token maps to Node 1
    Driver->>N1: EXECUTE (direct to replica)
    Note right of N2: Skipped - not a replica
    Note right of N3: Skipped - not a replica
    N1-->>Driver: Results
    Driver-->>App: Results
```

Without prepared statements, the driver cannot determine partition key values from embedded query strings.

---

## Prepared Statement Lifecycle

### Preparation

```java
// Prepare once (typically at application startup)
PreparedStatement prepared = session.prepare(
    "SELECT * FROM users WHERE user_id = ?");
```

The driver:

1. Sends PREPARE request to one node
2. Receives prepared statement ID and metadata
3. Caches the prepared statement locally
4. Automatically re-prepares on other nodes as needed

### Execution

```java
// Execute many times with different values
BoundStatement bound = prepared.bind(userId);
ResultSet results = session.execute(bound);
```

The driver:

1. Looks up cached prepared statement
2. Serializes bound values
3. Sends EXECUTE request (not the query string)
4. Routes token-aware if partition key bound

### Automatic Re-Preparation

If a node restarts or does not have the prepared statement, the driver automatically re-prepares:

```mermaid
sequenceDiagram
    participant App as Application
    participant Driver as Driver
    participant N2 as Node 2

    App->>Driver: Execute prepared statement
    Driver->>N2: EXECUTE (Prepared ID + values)
    Note right of N2: Statement not in cache
    N2-->>Driver: UNPREPARED error
    Driver->>N2: PREPARE (query string)
    Note right of N2: Parse and cache
    N2-->>Driver: Prepared ID
    Driver->>N2: EXECUTE (Prepared ID + values)
    Note right of N2: Execute query
    N2-->>Driver: Results
    Driver-->>App: Results
```

This is transparent to the application.

---

## Binding Values

### Positional Binding

```java
PreparedStatement prepared = session.prepare(
    "INSERT INTO users (id, name, email) VALUES (?, ?, ?)");

// Bind by position
BoundStatement bound = prepared.bind(
    userId,     // position 0
    "Alice",    // position 1
    "alice@example.com"  // position 2
);
```

### Named Binding

```java
PreparedStatement prepared = session.prepare(
    "INSERT INTO users (id, name, email) VALUES (:id, :name, :email)");

// Bind by name
BoundStatement bound = prepared.bind()
    .setUuid("id", userId)
    .setString("name", "Alice")
    .setString("email", "alice@example.com");
```

Named binding is more readable and less error-prone for queries with many parameters.

### Null Values

Explicitly bind null values:

```java
// Correct: explicit null
bound.setString("middle_name", null);

// Incorrect: unbound value
// Leaves value unset, may cause errors
```

---

## Caching Prepared Statements

### Driver-Side Cache

Drivers maintain a cache of prepared statements:

```graphviz dot prepared-statement-cache.svg
digraph PreparedStatementCache {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    rankdir=TB;

    label="Driver Prepared Statement Cache";
    labelloc="t";
    fontsize=12;

    cache [shape=none, label=<
        <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6" BGCOLOR="#f8f9fa">
            <TR>
                <TD COLSPAN="3" BGCOLOR="#7B4B96"><FONT COLOR="white"><B>Prepared Statement Cache</B></FONT></TD>
            </TR>
            <TR>
                <TD BGCOLOR="#e8e8e8"><B>Query String</B></TD>
                <TD BGCOLOR="#e8e8e8"><B>Prepared ID</B></TD>
                <TD BGCOLOR="#e8e8e8"><B>Metadata</B></TD>
            </TR>
            <TR>
                <TD ALIGN="LEFT">SELECT * FROM users WHERE id=?</TD>
                <TD><FONT FACE="monospace">0x8a3f...</FONT></TD>
                <TD>[id, name, email]</TD>
            </TR>
            <TR>
                <TD ALIGN="LEFT">INSERT INTO events (...) VALUES</TD>
                <TD><FONT FACE="monospace">0x2b7c...</FONT></TD>
                <TD>[partition_id, event_id]</TD>
            </TR>
            <TR>
                <TD ALIGN="LEFT">UPDATE users SET name=? WHERE</TD>
                <TD><FONT FACE="monospace">0x9d1e...</FONT></TD>
                <TD>[name, id]</TD>
            </TR>
        </TABLE>
    >];

    lookup [shape=box, style="rounded,filled", fillcolor="#E8F4E8", label="Cache lookup: O(1)\nby query string hash"];

    cache -> lookup [style=invis];
}
```

### Application-Level Caching

Prepare statements once and reuse:

```java
// GOOD: Prepare once, reuse
public class UserRepository {
    private final PreparedStatement selectUser;
    private final PreparedStatement insertUser;

    public UserRepository(CqlSession session) {
        this.selectUser = session.prepare(
            "SELECT * FROM users WHERE id = ?");
        this.insertUser = session.prepare(
            "INSERT INTO users (id, name) VALUES (?, ?)");
    }

    public User getUser(UUID id) {
        return session.execute(selectUser.bind(id))...;
    }
}
```

```java
// BAD: Prepare every request
public User getUser(UUID id) {
    // Prepares the same statement repeatedly!
    PreparedStatement ps = session.prepare(
        "SELECT * FROM users WHERE id = ?");
    return session.execute(ps.bind(id))...;
}
```

The driver caches prepared statements, so re-preparing is not catastrophic, but it adds unnecessary overhead.

---

## Schema Changes and Prepared Statements

When schema changes, prepared statements may become invalid:

```mermaid
sequenceDiagram
    participant App as Application
    participant Driver as Driver
    participant C as Cassandra

    Note over App,C: Initial State
    App->>Driver: Prepare SELECT * FROM users WHERE id = ?
    Driver->>C: PREPARE request
    C-->>Driver: Prepared ID + metadata (id, name, email)
    Driver-->>App: PreparedStatement

    Note over App,C: Schema Change Occurs
    rect rgb(255, 240, 240)
        Note over C: ALTER TABLE users DROP email
    end

    Note over App,C: Next Execution
    App->>Driver: Execute with bound values
    Driver->>C: EXECUTE request
    Note right of C: Detects schema mismatch
    C-->>Driver: Schema changed notification
    Driver->>C: Re-PREPARE request
    C-->>Driver: New Prepared ID + metadata (id, name)
    Driver->>C: EXECUTE with new ID
    C-->>Driver: Results
    Driver-->>App: Results (without email column)
```

### Handling Schema Changes

| Driver Behavior | Description |
|-----------------|-------------|
| Automatic re-prepare | Driver detects schema change, re-prepares |
| Metadata refresh | Driver updates column metadata |
| Application notification | Some drivers emit events for schema changes |

Best practice: Prepare statements at startup and handle re-preparation transparently. Avoid caching result metadata assumptions.

---

## Batch Statements

Prepared statements can be used in batches:

```java
PreparedStatement insertEvent = session.prepare(
    "INSERT INTO events (partition_id, event_id, data) VALUES (?, ?, ?)");

BatchStatement batch = BatchStatement.newInstance(BatchType.UNLOGGED)
    .add(insertEvent.bind(partitionId, event1Id, data1))
    .add(insertEvent.bind(partitionId, event2Id, data2))
    .add(insertEvent.bind(partitionId, event3Id, data3));

session.execute(batch);
```

**Important**: Batches should contain statements for the same partition. Cross-partition batches have significant performance overhead.

---

## Prepared Statement Limits

Cassandra limits prepared statements per node:

| Parameter | Default | Description |
|-----------|---------|-------------|
| prepared_statements_cache_size_mb | 10MB | Memory for prepared statement cache |

When cache is full, least-recently-used statements are evicted:

```mermaid
sequenceDiagram
    participant Driver as Driver
    participant C as Cassandra

    Note over C: Cache full (10MB)
    Driver->>C: PREPARE new statement
    Note right of C: Evict LRU statement
    Note right of C: Cache new statement
    C-->>Driver: Prepared ID

    Note over Driver,C: Later: Execute evicted statement
    Driver->>C: EXECUTE (evicted statement ID)
    C-->>Driver: UNPREPARED error
    Driver->>C: PREPARE (query string)
    C-->>Driver: New Prepared ID
    Driver->>C: EXECUTE (new ID)
    C-->>Driver: Results
```

### Avoiding Cache Churn

| Anti-Pattern | Problem |
|--------------|---------|
| Dynamic query generation | Thousands of unique queries fill cache |
| String concatenation in queries | Each variation is separate statement |
| Unbounded IN clauses | `IN (?, ?, ?, ...)` with varying count |

```java
// BAD: Dynamic IN clause (each size is different prepared statement)
String query = "SELECT * FROM users WHERE id IN (" +
    String.join(",", Collections.nCopies(ids.size(), "?")) + ")";

// BETTER: Fixed batch size or multiple queries
// Or use token-range queries for large sets
```

---

## Best Practices

| Practice | Rationale |
|----------|-----------|
| Prepare at startup | Amortize preparation cost, fail fast on errors |
| Reuse prepared statements | Avoid redundant cache lookups |
| Use named parameters | More readable, less error-prone |
| Bind all values explicitly | Avoid unbound value errors |
| Use for all production queries | Performance and token-aware routing |
| Avoid dynamic query generation | Prevents cache churn |

---

## Related Documentation

- **[Load Balancing Policy](policies/load-balancing.md)** — Token-aware routing with prepared statements
- **[CQL Reference](../../cql/index.md)** — Query syntax

