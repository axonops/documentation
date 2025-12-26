---
title: "Cassandra Driver Guide"
description: "Getting started with Cassandra drivers. Quick setup guides for popular languages."
meta:
  - name: keywords
    content: "Cassandra drivers setup, quick start, language drivers"
---

# Cassandra Driver Guide

This guide covers connecting applications to Apache Cassandra using official drivers, with setup and basic usage for popular programming languages.

## How Cassandra Drivers Differ from Traditional Database Drivers

Cassandra's native protocol works fundamentally differently from traditional database drivers (JDBC, ODBC, etc.). Understanding these differences is essential for building efficient applications.

### Multiplexed Connections, Not Connection Pools

Traditional database drivers use a **connection-per-query** model:

- Each query requires an exclusive connection
- Connection pools manage a fixed set of connections (e.g., 10-100)
- Under load, queries queue waiting for an available connection
- Each connection = one in-flight request

Cassandra drivers use a **multiplexed connection** model:

- A single TCP connection handles **thousands of concurrent requests** (up to 32,768 with protocol v3+)
- Requests are tagged with unique stream IDs and multiplexed over the connection
- Responses are matched to requests by stream ID, arriving in any order
- No query queuing at the connection level - all requests are immediately in-flight

```
Traditional (MySQL, PostgreSQL):
  Connection 1: [Query A waiting...] → [Response A]
  Connection 2: [Query B waiting...] → [Response B]
  Connection 3: [Query C waiting...] → [Response C]
  (3 connections for 3 concurrent queries)

Cassandra (multiplexed):
  Connection 1: [Query A id=1] [Query B id=2] [Query C id=3] → [Response B] [Response A] [Response C]
  (1 connection for thousands of concurrent queries)
```

This means you **don't need large connection pools**. A single connection per host is often sufficient, and the driver manages this automatically.

### Persistent Connections with Cluster Awareness

Unlike traditional drivers that simply execute queries, Cassandra drivers maintain an **ongoing relationship** with the cluster. This is why `Cluster` and `Session` instances are designed to be **long-lived** - you create them once at application startup and reuse them for the entire application lifecycle. Creating multiple instances is unnecessary and wasteful; a single `Session` can handle all your application's queries concurrently.

**At connection time:**

1. Driver connects to one of the provided contact points
2. Queries system tables to discover all nodes, their tokens, and datacenter/rack topology
3. Establishes connections to nodes based on the load balancing policy
4. Subscribes to cluster event notifications

**During operation:**

The driver continuously receives **push notifications** from the cluster about:

- **Topology changes** - nodes added, removed, or moving tokens
- **Status changes** - nodes going up or down (immediate notification, not polling)
- **Schema changes** - tables created, altered, or dropped

This makes the driver **highly available and self-healing**:

- If a node goes down, the driver is notified immediately and routes around it
- New nodes are automatically discovered and added to the connection pool
- Schema changes are detected and prepared statements are automatically re-prepared

### Dynamic Connection Management

The driver automatically adjusts connections based on load and cluster changes:

- Connections are established lazily to nodes as needed
- Failed connections are automatically retried with configurable backoff
- Connections are distributed based on load balancing policy (not all nodes need connections)
- The driver maintains heartbeats to detect stale connections

### Request Routing Intelligence

Unlike traditional drivers that send all queries to a single endpoint (or load balancer), Cassandra drivers include **token-aware routing**:

- The driver knows which nodes own which data (via token ranges)
- Queries are sent directly to a node that has the data locally
- This eliminates an extra network hop that a coordinator would add
- The routing table is continuously updated as topology changes

### Implications for Application Design

| Traditional Driver Pattern | Cassandra Driver Pattern |
|---------------------------|-------------------------|
| Configure connection pool size carefully | Minimal configuration needed - driver auto-manages |
| Monitor pool exhaustion | Monitor per-host request queues |
| Scale connections with load | Scale with more application instances |
| Health checks via test queries | Health managed via protocol events |
| Retry logic in application | Retry policies built into driver |
| Manual failover configuration | Automatic failover via cluster awareness |

---

## Available Drivers

| Language | Driver | Status | Repository |
|----------|--------|--------|------------|
| **Java** | Apache Cassandra Java Driver | Production | [GitHub](https://github.com/apache/cassandra-java-driver) |
| **Scala/Java** | Apache Spark Cassandra Connector | Production | [GitHub](https://github.com/datastax/spark-cassandra-connector) |
| **Python** | Apache Cassandra Python Driver | Production | [GitHub](https://github.com/apache/cassandra-python-driver) |
| **Python** | Async Python Cassandra Client | Early Release | [GitHub](https://github.com/axonops/async-python-cassandra-client) |
| **Node.js** | DataStax Node.js Driver | Production | [GitHub](https://github.com/datastax/nodejs-driver) |
| **Go** | GoCQL | Production | [GitHub](https://github.com/gocql/gocql) |
| **C#/.NET** | DataStax C# Driver | Production | [GitHub](https://github.com/datastax/csharp-driver) |
| **C/C++** | DataStax C++ Driver | Production | [GitHub](https://github.com/datastax/cpp-driver) |
| **Ruby** | DataStax Ruby Driver | Maintenance | [GitHub](https://github.com/datastax/ruby-driver) |
| **PHP** | DataStax PHP Driver | Maintenance | [GitHub](https://github.com/datastax/php-driver) |

---

## Quick Start Examples

### Java

```xml
<!-- pom.xml -->
<dependency>
    <groupId>com.datastax.oss</groupId>
    <artifactId>java-driver-core</artifactId>
    <version>4.17.0</version>
</dependency>
```

```java
import com.datastax.oss.driver.api.core.CqlSession;
import com.datastax.oss.driver.api.core.cql.*;

public class QuickStart {
    public static void main(String[] args) {
        try (CqlSession session = CqlSession.builder()
                .addContactPoint(new InetSocketAddress("127.0.0.1", 9042))
                .withLocalDatacenter("datacenter1")
                .build()) {

            ResultSet rs = session.execute("SELECT release_version FROM system.local");
            Row row = rs.one();
            System.out.println("Cassandra version: " + row.getString("release_version"));
        }
    }
}
```

### Python

```bash
pip install cassandra-driver
```

```python
from cassandra.cluster import Cluster

cluster = Cluster(['127.0.0.1'])
session = cluster.connect()

row = session.execute("SELECT release_version FROM system.local").one()
print(f"Cassandra version: {row.release_version}")

cluster.shutdown()
```

### Python (Async)

For async frameworks like FastAPI and aiohttp. Requires Python 3.12+ and Cassandra 4.0+:

```bash
pip install async-cassandra
```

```python
import asyncio
from async_cassandra import AsyncCluster

async def main():
    # Create long-lived cluster and session
    cluster = AsyncCluster(['127.0.0.1'])
    session = await cluster.connect()

    result = await session.execute("SELECT release_version FROM system.local")
    print(f"Cassandra version: {result.one().release_version}")

    # Only close when application shuts down
    await session.close()
    await cluster.shutdown()

asyncio.run(main())
```

### Node.js

```bash
npm install cassandra-driver
```

```javascript
const cassandra = require('cassandra-driver');

const client = new cassandra.Client({
  contactPoints: ['127.0.0.1'],
  localDataCenter: 'datacenter1'
});

async function run() {
  await client.connect();
  const result = await client.execute('SELECT release_version FROM system.local');
  console.log('Cassandra version:', result.rows[0].release_version);
  await client.shutdown();
}

run();
```

### Go

```bash
go get github.com/gocql/gocql
```

```go
package main

import (
    "fmt"
    "log"
    "github.com/gocql/gocql"
)

func main() {
    cluster := gocql.NewCluster("127.0.0.1")
    cluster.Keyspace = "system"
    session, err := cluster.CreateSession()
    if err != nil {
        log.Fatal(err)
    }
    defer session.Close()

    var version string
    if err := session.Query("SELECT release_version FROM local").Scan(&version); err != nil {
        log.Fatal(err)
    }
    fmt.Println("Cassandra version:", version)
}
```

---

## Connection Configuration

### Essential Settings

All drivers require these settings:

| Setting | Description | Example |
|---------|-------------|---------|
| Contact Points | Initial nodes to connect to | `["10.0.0.1", "10.0.0.2"]` |
| Local Datacenter | Preferred DC for routing | `"dc1"` |
| Port | CQL native port | `9042` |
| Keyspace | Default keyspace (optional) | `"my_app"` |

### Authentication

**Java**:

```java
CqlSession session = CqlSession.builder()
    .addContactPoint(new InetSocketAddress("127.0.0.1", 9042))
    .withLocalDatacenter("dc1")
    .withAuthCredentials("app_user", "app_password")
    .build();
```

**Python**:

```python
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

auth_provider = PlainTextAuthProvider(
    username='app_user',
    password='app_password'
)

cluster = Cluster(
    ['127.0.0.1'],
    auth_provider=auth_provider
)
```

### SSL/TLS

**Java** (application.conf):

```hocon
datastax-java-driver {
  advanced.ssl-engine-factory {
    class = DefaultSslEngineFactory
    truststore-path = /path/to/truststore.jks
    truststore-password = truststorepass
    keystore-path = /path/to/keystore.jks
    keystore-password = keystorepass
  }
}
```

```java
// SSL is automatically enabled when ssl-engine-factory is configured
CqlSession session = CqlSession.builder()
    .addContactPoint(new InetSocketAddress("127.0.0.1", 9042))
    .withLocalDatacenter("dc1")
    .build();
```

**Python**:

```python
from cassandra.cluster import Cluster
import ssl

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.load_verify_locations('/path/to/ca.crt')
ssl_context.load_cert_chain(
    certfile='/path/to/client.crt',
    keyfile='/path/to/client.key'
)

cluster = Cluster(
    ['127.0.0.1'],
    ssl_context=ssl_context
)
```

### Java Driver Configuration System

The Java driver uses a unique configuration approach based on the [Typesafe Config](https://github.com/lightbend/config) library. This is different from other drivers which typically use only programmatic configuration.

#### How It Works

The driver ships with a `reference.conf` file containing sensible defaults for all options. You create an `application.conf` file to override specific settings - you only need to specify what you want to change, not the entire configuration.

Configuration files use **HOCON** (Human-Optimized Config Object Notation), an improved JSON superset that supports comments, substitutions, and includes.

**application.conf** (place in your classpath):

```hocon
datastax-java-driver {
  basic {
    contact-points = ["10.0.0.1:9042", "10.0.0.2:9042"]

    # Explicit local DC - if omitted, driver uses the DC of the first contact point that responds
    load-balancing-policy.local-datacenter = "dc1"

    request.timeout = 5 seconds
  }

  advanced {
    connection {
      pool.local.size = 4
      pool.remote.size = 2
    }
    retry-policy.class = DefaultRetryPolicy
  }
}
```

```java
// Driver automatically loads application.conf from classpath
CqlSession session = CqlSession.builder().build();
```

#### Configuration Loading Order

The driver checks these locations in order (later sources override earlier ones):

1. `reference.conf` (built-in driver defaults)
2. `application.properties` (classpath)
3. `application.json` (classpath)
4. `application.conf` (classpath)
5. System properties

#### Execution Profiles

Profiles allow different configuration sets for different query types without changing code:

```hocon
datastax-java-driver {
  basic.request.timeout = 2 seconds

  profiles {
    oltp {
      basic.request.timeout = 100 milliseconds
      basic.request.consistency = LOCAL_QUORUM
    }
    olap {
      basic.request.timeout = 30 seconds
      basic.request.consistency = LOCAL_ONE
    }
  }
}
```

```java
// Use profiles per-query
PreparedStatement stmt = session.prepare("SELECT * FROM large_table");
session.execute(stmt.bind().setExecutionProfileName("olap"));
```

#### Programmatic Configuration

For frameworks with their own configuration mechanisms (Spring Boot, Quarkus), you can build configuration programmatically:

```java
DriverConfigLoader loader = DriverConfigLoader.programmaticBuilder()
    .withDuration(DefaultDriverOption.REQUEST_TIMEOUT, Duration.ofSeconds(5))
    .withString(DefaultDriverOption.LOAD_BALANCING_LOCAL_DATACENTER, "dc1")
    .startProfile("slow")
        .withDuration(DefaultDriverOption.REQUEST_TIMEOUT, Duration.ofSeconds(30))
    .endProfile()
    .build();

CqlSession session = CqlSession.builder()
    .withConfigLoader(loader)
    .build();
```

#### Loading from External Files

Load configuration from files outside the classpath:

```java
// From filesystem
DriverConfigLoader loader = DriverConfigLoader.fromFile(
    new File("/etc/myapp/cassandra.conf"));

// From URL
DriverConfigLoader loader = DriverConfigLoader.fromUrl(
    new URL("http://config-server/cassandra.conf"));

CqlSession session = CqlSession.builder()
    .withConfigLoader(loader)
    .build();
```

#### Configuration Reloading

By default, configuration files are reloaded periodically and the driver adjusts settings dynamically:

```hocon
datastax-java-driver {
  basic.config-reload-interval = 5 minutes
}
```

!!! note "Java Driver Only"
    This file-based configuration system is unique to the Java driver. Python, Node.js, Go, and other drivers use programmatic configuration only. For comprehensive details, see the [Java Driver Configuration Reference](https://github.com/apache/cassandra-java-driver/tree/4.x/manual/core/configuration).

---

## Load Balancing Policies

Load balancing policies determine which Cassandra node receives each query. The right policy reduces latency, distributes load evenly, and ensures queries stay within the correct datacenter for multi-DC deployments.

### Understanding Contact Points

The contact points you provide when creating a cluster connection are **not** a list of nodes for failover - they are **bootstrap points** used only for initial cluster discovery.

When the driver connects:

1. It connects to one of the contact points
2. It queries the system tables to discover **all** nodes in the cluster
3. It establishes connections to other nodes based on the load balancing policy
4. It subscribes to **cluster events** via the native protocol

After bootstrap, the driver **continuously receives updates** about:

- **Topology changes** - nodes joining, leaving, or moving tokens
- **Node status** - nodes going up or down
- **Schema changes** - new tables, altered columns, dropped keyspaces

This means even if all your contact points go down after initial connection, the driver remains connected and aware of the cluster state through its existing connections. The contact points are only needed again if the driver completely disconnects and needs to re-bootstrap.

**Java**:

```java
// Contact points are ONLY used for initial bootstrap - not ongoing connections
// When using multi-DC contact points, set local DC explicitly to ensure deterministic routing
CqlSession session = CqlSession.builder()
    .addContactPoint(new InetSocketAddress("node1.dc1.example.com", 9042))
    .addContactPoint(new InetSocketAddress("node1.dc2.example.com", 9042))  // DC2 - bootstrap fallback
    .withLocalDatacenter("dc1")  // Explicit DC; if omitted, uses DC of first responding contact point
    .build();
```

**Python**:

```python
from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy

# Contact points are ONLY used for initial bootstrap - not ongoing connections
# If all contact points are in the same DC, the driver auto-detects local DC
cluster = Cluster(['node1.dc1.example.com', 'node2.dc1.example.com'])

# When using multi-DC contact points, set local DC explicitly to ensure deterministic routing
cluster = Cluster(
    contact_points=[
        'node1.dc1.example.com',  # DC1
        'node1.dc2.example.com',  # DC2 - in case DC1 is unreachable at startup
    ],
    load_balancing_policy=DCAwareRoundRobinPolicy(local_dc='dc1')
)
```

### Why Load Balancing Matters

In a Cassandra cluster, data is distributed across nodes using consistent hashing. Each partition key hashes to a specific token, and that token determines which nodes store the data (based on replication factor). A good load balancing policy:

- **Reduces latency** by sending queries directly to nodes that own the data
- **Avoids cross-DC traffic** by preferring local nodes in multi-DC deployments
- **Distributes load** evenly to prevent hotspots
- **Handles failures** gracefully by trying other nodes when one is unavailable

### Policy Types

| Policy | Description | Use Case |
|--------|-------------|----------|
| **Token-Aware** | Routes to the node owning the partition | Default choice - lowest latency |
| **DC-Aware Round Robin** | Prefers nodes in the local DC, round-robins among them | Multi-DC deployments |
| **Round Robin** | Distributes evenly across all nodes | Rarely used - ignores data locality |
| **Whitelist/Allowlist** | Restricts to specific nodes | Testing, maintenance |

### Token-Aware Policy (Recommended)

Token-aware routing sends queries directly to a node that owns the requested partition, eliminating an extra network hop. Without token-awareness, a coordinator node must forward the query to the replica nodes, adding latency.

```
Without Token-Aware:
  Client → Coordinator → Replica (owns data) → Coordinator → Client

With Token-Aware:
  Client → Replica (owns data) → Client
```

**Java** (token-aware is default in driver v4+):

```java
// Token-aware + DC-aware is the default behavior
CqlSession session = CqlSession.builder()
    .addContactPoint(new InetSocketAddress("127.0.0.1", 9042))
    .withLocalDatacenter("dc1")  // Explicit DC; if omitted, uses DC of first responding contact point
    .build();
```

**Python (sync driver)**:

```python
from cassandra.cluster import Cluster
from cassandra.policies import TokenAwarePolicy, DCAwareRoundRobinPolicy

# Wrap DC-aware policy with token-aware for best performance
cluster = Cluster(
    ['127.0.0.1'],
    load_balancing_policy=TokenAwarePolicy(
        DCAwareRoundRobinPolicy(local_dc='dc1')
    )
)
```

**Python (async driver)**:

```python
from async_cassandra import AsyncCluster
from cassandra.policies import TokenAwarePolicy, DCAwareRoundRobinPolicy

cluster = AsyncCluster(
    ['127.0.0.1'],
    load_balancing_policy=TokenAwarePolicy(
        DCAwareRoundRobinPolicy(local_dc='dc1')
    )
)
session = await cluster.connect('my_keyspace')
```

**Node.js**:

```javascript
const cassandra = require('cassandra-driver');

const client = new cassandra.Client({
  contactPoints: ['127.0.0.1'],
  localDataCenter: 'dc1',
  // Token-aware is enabled by default in Node.js driver
});
```

### DC-Aware Round Robin

In multi-datacenter deployments, DC-aware routing ensures queries go to nodes in the local datacenter, avoiding cross-DC latency (which can be 10-100x higher than local).

**Java**:

```java
// Local DC is required in Java driver v4+
CqlSession session = CqlSession.builder()
    .addContactPoint(new InetSocketAddress("127.0.0.1", 9042))
    .withLocalDatacenter("dc1")  // Queries only go to dc1 nodes
    .build();
```

**Python**:

```python
from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy

cluster = Cluster(
    ['127.0.0.1'],
    load_balancing_policy=DCAwareRoundRobinPolicy(
        local_dc='dc1',
        used_hosts_per_remote_dc=0  # Never use remote DC nodes (default)
    )
)
```

**Node.js**:

```javascript
const client = new cassandra.Client({
  contactPoints: ['127.0.0.1'],
  localDataCenter: 'dc1',  // Explicit DC; if omitted, uses DC of first responding contact point
});
```

!!! info "Automatic Local Datacenter Detection"
    If you don't explicitly set the local datacenter, the driver uses the datacenter of the **first contact point that responds**. This means you can control the local DC implicitly by only providing contact points from a single DC. However, if your contact points span multiple DCs, the driver's local DC becomes non-deterministic - whichever node responds first determines routing for the lifetime of the session.

### Configuring Failover to Remote DCs

By default, drivers only use local DC nodes. To allow failover to remote DCs when all local nodes are down:

**Python**:

```python
from cassandra.policies import DCAwareRoundRobinPolicy, TokenAwarePolicy

cluster = Cluster(
    ['127.0.0.1'],
    load_balancing_policy=TokenAwarePolicy(
        DCAwareRoundRobinPolicy(
            local_dc='dc1',
            used_hosts_per_remote_dc=2  # Use up to 2 nodes per remote DC as fallback
        )
    )
)
```

**Java** (application.conf):

```hocon
datastax-java-driver {
  basic.load-balancing-policy {
    local-datacenter = "dc1"
  }
  advanced.load-balancing-policy {
    dc-failover {
      max-nodes-per-remote-dc = 2
      allow-for-local-consistency-levels = false
    }
  }
}
```

### Avoiding Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Multi-DC contact points without explicit local DC | Non-deterministic DC selection based on first responder | Set explicit `local_dc` or use contact points from single DC only |
| Using Round Robin | Ignores data locality, higher latency | Use Token-Aware + DC-Aware |
| Hardcoding contact points from one DC | If that DC is down, can't bootstrap | Include contact points from multiple DCs (with explicit local DC) |
| Allowing remote DC for LOCAL_* consistency | Violates consistency guarantees | Set `allow-for-local-consistency-levels = false` |

---

## Prepared Statements

Prepared statements are the correct way to execute parameterized queries in Cassandra. They provide significant benefits over simple string-based queries.

### Why Use Prepared Statements?

**Performance**: When you prepare a statement, Cassandra parses the CQL, validates it against the schema, and creates an execution plan. This happens **once**. Subsequent executions skip all parsing and planning - only the bound values are sent to the server. For queries executed thousands of times, this dramatically reduces CPU usage on both client and server.

**Security**: Prepared statements prevent CQL injection attacks. Values are bound as typed parameters, not concatenated into the query string, so malicious input cannot alter the query structure.

**Type Safety**: The driver validates that bound values match the expected types before sending to the server, catching type errors early rather than at execution time.

**Token-Aware Routing**: Prepared statements include partition key metadata, enabling the driver to route queries directly to the node that owns the data - impossible with unparsed query strings.

### Correct Usage Pattern

Prepare statements **once** at application startup or first use, then reuse the prepared statement for all executions:

```python
# Python - Prepare once, execute many times
from cassandra.cluster import Cluster

cluster = Cluster(['127.0.0.1'])
session = cluster.connect('my_keyspace')

# Prepare once (typically at startup or in an initialization block)
insert_stmt = session.prepare("""
    INSERT INTO users (user_id, username, email)
    VALUES (?, ?, ?)
""")

# Execute many times with different values
import uuid
session.execute(insert_stmt, [uuid.uuid4(), 'john_doe', 'john@example.com'])
session.execute(insert_stmt, [uuid.uuid4(), 'jane_doe', 'jane@example.com'])
```

```java
// Java - Prepare once, execute many times
PreparedStatement insertStmt = session.prepare(
    "INSERT INTO users (user_id, username, email) VALUES (?, ?, ?)"
);

// Execute many times
BoundStatement bound = insertStmt.bind(UUID.randomUUID(), "john_doe", "john@example.com");
session.execute(bound);
```

```python
# Python (async) - Prepare once, execute many times
from async_cassandra import AsyncCluster

cluster = AsyncCluster(['127.0.0.1'])
session = await cluster.connect('my_keyspace')

# Prepare once
insert_stmt = await session.prepare(
    "INSERT INTO users (user_id, username, email) VALUES (?, ?, ?)"
)

# Execute many times
await session.execute(insert_stmt, [user_id, 'john_doe', 'john@example.com'])
```

### Anti-Patterns to Avoid

#### ❌ Preparing the Same Statement Repeatedly

**Java**:

```java
// WRONG - Prepares on every call, wasting resources
public void insertUser(CqlSession session, UUID userId, String username, String email) {
    PreparedStatement stmt = session.prepare(
        "INSERT INTO users (user_id, username, email) VALUES (?, ?, ?)");
    session.execute(stmt.bind(userId, username, email));
}

// RIGHT - Prepare once at startup, reuse
private final PreparedStatement insertStmt;

public UserRepository(CqlSession session) {
    this.insertStmt = session.prepare(
        "INSERT INTO users (user_id, username, email) VALUES (?, ?, ?)");
}

public void insertUser(UUID userId, String username, String email) {
    session.execute(insertStmt.bind(userId, username, email));
}
```

**Python**:

```python
# WRONG - Prepares on every call, wasting resources
def insert_user(session, user_id, username, email):
    stmt = session.prepare("INSERT INTO users (user_id, username, email) VALUES (?, ?, ?)")
    session.execute(stmt, [user_id, username, email])

# RIGHT - Prepare once, reuse
insert_stmt = session.prepare("INSERT INTO users (user_id, username, email) VALUES (?, ?, ?)")

def insert_user(session, user_id, username, email):
    session.execute(insert_stmt, [user_id, username, email])
```

Each `prepare()` call sends a request to the server. Preparing the same statement repeatedly wastes network round-trips and server CPU.

#### ❌ Embedding Values in the Query String

**Java**:

```java
// WRONG - Values in query string (CQL injection risk, no caching benefit)
String username = "john_doe";
session.execute("SELECT * FROM users WHERE username = '" + username + "'");

// WRONG - Still wrong, even with prepare
session.prepare("SELECT * FROM users WHERE username = '" + username + "'");

// RIGHT - Use bind parameters
PreparedStatement stmt = session.prepare("SELECT * FROM users WHERE username = ?");
session.execute(stmt.bind(username));
```

**Python**:

```python
# WRONG - Values in query string (CQL injection risk, no caching benefit)
username = "john_doe"
session.execute(f"SELECT * FROM users WHERE username = '{username}'")

# WRONG - Still wrong, even with prepare
session.prepare(f"SELECT * FROM users WHERE username = '{username}'")

# RIGHT - Use bind parameters
stmt = session.prepare("SELECT * FROM users WHERE username = ?")
session.execute(stmt, [username])
```

Embedding values in the query string:
- Creates a unique query for each value, defeating caching
- Opens CQL injection vulnerabilities
- Prevents token-aware routing

#### ❌ Dynamic Table or Column Names

**Java**:

```java
// WRONG - Cannot use bind parameters for table/column names
String table = "users";
PreparedStatement stmt = session.prepare(
    "SELECT * FROM " + table + " WHERE id = ?");  // Creates new prepared stmt per table

// Acceptable only if limited set of tables - prepare each once at startup
private final PreparedStatement userStmt;
private final PreparedStatement orderStmt;

public Repository(CqlSession session) {
    this.userStmt = session.prepare("SELECT * FROM users WHERE id = ?");
    this.orderStmt = session.prepare("SELECT * FROM orders WHERE id = ?");
}
```

**Python**:

```python
# WRONG - Cannot use bind parameters for table/column names
table = "users"
stmt = session.prepare(f"SELECT * FROM {table} WHERE id = ?")  # Creates new prepared stmt per table

# Acceptable only if limited set of tables - prepare each once at startup
user_stmt = session.prepare("SELECT * FROM users WHERE id = ?")
order_stmt = session.prepare("SELECT * FROM orders WHERE id = ?")
```

Bind parameters (`?`) can only be used for **values**, not for table names, column names, or other CQL syntax. If you need dynamic table access, prepare all variants at startup.

### Server-Side Prepared Statement Cache

Cassandra caches prepared statements on each node. You can monitor this cache to detect issues:

**Key metrics to monitor:**

| Metric | Description | Warning Sign |
|--------|-------------|--------------|
| `PreparedStatementsCount` | Number of cached prepared statements | Continuously growing = prepare leak |
| `PreparedStatementsEvicted` | Statements evicted from cache | High rate = cache too small or over-preparing |
| `PreparedStatementsExecuted` | Execution count | Should be >> PreparedStatementsCount |

**Using nodetool:**

```bash
# View prepared statement cache stats
nodetool info | grep -i prepared
```

**Cassandra configuration (cassandra.yaml):**

```yaml
# Maximum number of prepared statements to cache (default: 10000)
prepared_statements_cache_size_mb: 100
```

!!! warning "Prepared Statement Leak"
    If `PreparedStatementsCount` grows continuously without bound, you likely have a prepare leak - code that prepares statements with dynamic values embedded in the query string. Each unique query string creates a new cache entry until the cache fills and evictions begin, degrading performance.

---

## Consistency Levels

Set consistency per query:

```python
# Python
from cassandra import ConsistencyLevel
from cassandra.query import SimpleStatement

stmt = SimpleStatement(
    "SELECT * FROM users WHERE user_id = %s",
    consistency_level=ConsistencyLevel.QUORUM
)
session.execute(stmt, [user_id])
```

```java
// Java
session.execute(
    SimpleStatement.newInstance("SELECT * FROM users WHERE user_id = ?", userId)
        .setConsistencyLevel(DefaultConsistencyLevel.QUORUM)
);
```

### Consistency Level Reference

| Level | Reads | Writes | Use Case |
|-------|-------|--------|----------|
| `ONE` | Fast | Fast | Non-critical data |
| `QUORUM` | Majority | Majority | Default for most apps |
| `LOCAL_QUORUM` | Local majority | Local majority | Multi-DC deployments |
| `ALL` | All replicas | All replicas | Highest consistency |

---

## Async Operations

Asynchronous database operations are essential for building high-throughput, responsive applications. Rather than blocking a thread while waiting for Cassandra to respond, async operations allow your application to handle other work concurrently.

### Why Async Matters

**Python and the GIL**: Python's Global Interpreter Lock (GIL) means only one thread can execute Python bytecode at a time. In synchronous code, when your application waits for a Cassandra query to return, that thread is blocked and cannot process other requests. With async/await, the event loop can handle thousands of concurrent requests on a single thread by switching between tasks during I/O waits. This is particularly critical for web frameworks like FastAPI and aiohttp where blocking the event loop freezes your entire application.

**Java and Thread Efficiency**: While Java doesn't have a GIL, creating threads is expensive (typically 1MB of stack memory each). Synchronous drivers require one thread per concurrent query, limiting scalability. Async operations with `CompletionStage` allow a small thread pool to handle many concurrent requests, reducing memory overhead and context-switching costs. This is especially valuable in reactive frameworks like Spring WebFlux and Vert.x.

**Node.js**: Being single-threaded and event-driven by design, Node.js naturally benefits from async operations. The driver's Promise-based API integrates seamlessly with the event loop.

### Python (asyncio)

Use the [Async Python Cassandra Client](https://github.com/axonops/async-python-cassandra-client) for true async/await support with frameworks like FastAPI and aiohttp:

```python
import asyncio
import uuid
from async_cassandra import AsyncCluster

# Long-lived cluster and session (create once, reuse for all requests)
cluster = None
session = None

async def startup():
    global cluster, session
    cluster = AsyncCluster(['127.0.0.1'])
    session = await cluster.connect('my_keyspace')

async def shutdown():
    if session:
        await session.close()
    if cluster:
        await cluster.shutdown()

async def insert_users():
    # Prepare statement once, execute many times
    insert_stmt = await session.prepare(
        "INSERT INTO users (user_id, username, email) VALUES (?, ?, ?)"
    )

    # Run multiple inserts concurrently
    tasks = [
        session.execute(insert_stmt, [uuid.uuid4(), f'user{i}', f'user{i}@example.com'])
        for i in range(100)
    ]
    await asyncio.gather(*tasks)

async def main():
    await startup()
    try:
        await insert_users()
    finally:
        await shutdown()

asyncio.run(main())
```

For streaming large result sets without memory exhaustion, use `execute_stream()` with a context manager:

```python
from async_cassandra.streaming import StreamConfig

config = StreamConfig(fetch_size=1000)

# Context manager ensures streaming resources are cleaned up
async with await session.execute_stream(
    "SELECT * FROM large_table",
    stream_config=config
) as result:
    async for row in result:
        await process_row(row)  # Non-blocking, other requests keep flowing
```

### Java (CompletionStage)

```java
CompletionStage<AsyncResultSet> future = session.executeAsync(
    "SELECT * FROM users WHERE user_id = ?", userId
);

future.thenAccept(resultSet -> {
    Row row = resultSet.one();
    System.out.println("Username: " + row.getString("username"));
});
```

### Node.js (Promise-based)

```javascript
// Execute multiple queries concurrently
const queries = [
  client.execute('SELECT * FROM users WHERE user_id = ?', [userId1]),
  client.execute('SELECT * FROM users WHERE user_id = ?', [userId2]),
  client.execute('SELECT * FROM users WHERE user_id = ?', [userId3])
];

const results = await Promise.all(queries);
```

---

## Connection Pooling

Drivers maintain connection pools automatically. Key settings:

### Python (sync driver)

```python
from cassandra.cluster import Cluster
from cassandra.policies import HostDistance

cluster = Cluster(['127.0.0.1'])

# Set pool size per host (only works with protocol v1/v2)
cluster.set_core_connections_per_host(HostDistance.LOCAL, 4)
cluster.set_max_connections_per_host(HostDistance.LOCAL, 10)
```

### Python (async driver)

With protocol v3+ (required by async-cassandra), the Python driver uses a **single connection per host** that supports up to 32,768 concurrent requests. This is more efficient than multiple connections due to reduced lock contention and overhead.

```python
from async_cassandra import AsyncCluster

cluster = AsyncCluster(
    ['127.0.0.1'],
    executor_threads=4,          # Thread pool for callbacks (default: 2)
    idle_heartbeat_interval=30,  # Keep-alive interval in seconds
    connect_timeout=10,          # Connection timeout (default: 5)
    request_timeout=10,          # Per-request timeout (default: 10)
)
```

### Java

```java
// application.conf
datastax-java-driver {
  advanced.connection {
    pool {
      local.size = 4
      remote.size = 2
    }
  }
}
```

---

## Retry Policies

Retry policies determine how drivers handle transient failures such as timeouts, temporary node unavailability, or network issues. When a query fails, the retry policy decides whether to:

- **Retry** the query on the same or a different node
- **Rethrow** the exception to the application
- **Ignore** the failure (for writes where partial success is acceptable)

### Idempotency: Critical for Safe Retries

**Drivers only retry queries that are marked as idempotent.** A query is idempotent if executing it multiple times produces the same result as executing it once. This is essential because when a timeout occurs, the driver cannot know whether the query actually succeeded on the server.

| Query Type | Idempotent? | Reason |
|------------|-------------|--------|
| `SELECT * FROM users WHERE id = ?` | ✅ Yes | Same data returned each time |
| `UPDATE users SET name = 'John' WHERE id = ?` | ✅ Yes | Setting to absolute value is repeatable |
| `DELETE FROM users WHERE id = ?` | ✅ Yes | Deleting twice has same effect |
| `INSERT INTO users (id, name) VALUES (?, ?) IF NOT EXISTS` | ✅ Yes | LWT ensures exactly-once semantics |
| `SELECT now() FROM system.local` | ❌ No | Returns different timestamp each call |
| `UPDATE users SET counter = counter + 1 WHERE id = ?` | ❌ No | Increment applied multiple times |
| `INSERT INTO logs (id, ts) VALUES (uuid(), ?)` | ❌ No | Generates different UUID each time |

!!! warning "Default: Queries are NOT idempotent"
    By default, drivers assume queries are **not** idempotent and will not retry them on timeout. You MUST explicitly mark queries as idempotent to enable retries.

### Python (sync driver)

```python
from cassandra.cluster import Cluster

cluster = Cluster(['127.0.0.1'])
session = cluster.connect('my_keyspace')

# Prepared statement for idempotent read
select_stmt = session.prepare("SELECT * FROM users WHERE id = ?")
select_stmt.is_idempotent = True  # SELECTs are safe to retry
result = session.execute(select_stmt, [user_id])

# Prepared statement for idempotent write (absolute value update)
update_stmt = session.prepare("UPDATE users SET name = ? WHERE id = ?")
bound = update_stmt.bind(['John', user_id])
bound.is_idempotent = True  # Setting absolute value is safe to retry
session.execute(bound)

# Prepared statement for non-idempotent write - do NOT mark
counter_stmt = session.prepare("UPDATE counters SET views = views + 1 WHERE page_id = ?")
session.execute(counter_stmt, [page_id])  # Counter increment must not retry
```

### Python (async driver)

The async driver includes `AsyncRetryPolicy` with configurable retry attempts. Read operations (SELECTs) are automatically retried without needing to mark them as idempotent.

```python
from async_cassandra import AsyncCluster
from async_cassandra.retry_policy import AsyncRetryPolicy

# Configure retry policy with max retries
cluster = AsyncCluster(
    ['127.0.0.1'],
    retry_policy=AsyncRetryPolicy(max_retries=5)
)
session = await cluster.connect('my_keyspace')

# Prepared statement for read - automatically retried
select_stmt = await session.prepare("SELECT * FROM users WHERE id = ?")
result = await session.execute(select_stmt, [user_id])

# Prepared statement for idempotent write
insert_stmt = await session.prepare("INSERT INTO users (id, email) VALUES (?, ?) IF NOT EXISTS")
insert_stmt.is_idempotent = True  # LWT is safe to retry
await session.execute(insert_stmt, [user_id, 'john@example.com'])

# Prepared statement for non-idempotent write - do NOT mark
counter_stmt = await session.prepare("UPDATE counters SET views = views + 1 WHERE page_id = ?")
await session.execute(counter_stmt, [page_id])  # Counter increment must not retry
```

### Java

```java
import com.datastax.oss.driver.api.core.CqlSession;
import com.datastax.oss.driver.api.core.cql.*;

CqlSession session = CqlSession.builder()
    .addContactPoint(new InetSocketAddress("127.0.0.1", 9042))
    .withLocalDatacenter("dc1")
    .build();

// Mark simple statement as idempotent
SimpleStatement stmt = SimpleStatement.newInstance(
    "SELECT * FROM users WHERE id = ?", userId)
    .setIdempotent(true);
session.execute(stmt);

// Prepared statements - set on bound statement
PreparedStatement prepared = session.prepare(
    "UPDATE users SET name = ? WHERE id = ?");
BoundStatement bound = prepared.bind("John", userId)
    .setIdempotent(true);
session.execute(bound);
```

**Configure retry policy in application.conf:**

```hocon
datastax-java-driver {
  advanced.retry-policy {
    class = DefaultRetryPolicy
  }

  # Or use a custom policy
  # class = com.example.MyRetryPolicy
}
```

### Built-in Retry Policies

| Policy | Behavior |
|--------|----------|
| **DefaultRetryPolicy** | Retries reads once if enough replicas responded; never retries writes |
| **FallthroughRetryPolicy** | Never retries - always rethrows to application |
| **DowngradingConsistencyRetryPolicy** | Retries at lower consistency level (use with caution) |

Consult your driver's documentation for the complete list of available retry policies and guidance on implementing custom policies for your specific requirements.

---

## Error Handling

Common exceptions to handle:

| Exception | Cause | Action |
|-----------|-------|--------|
| `NoHostAvailable` | No nodes reachable | Check connectivity |
| `ReadTimeout` | Read took too long | Retry or check data model |
| `WriteTimeout` | Write took too long | Retry or check cluster health |
| `Unavailable` | Not enough replicas | Check cluster health |
| `InvalidQuery` | CQL syntax error | Fix query |

### Examples

**Java**:

```java
import com.datastax.oss.driver.api.core.servererrors.*;
import com.datastax.oss.driver.api.core.AllNodesFailedException;

try {
    session.execute("SELECT * FROM users");
} catch (ReadTimeoutException e) {
    System.out.println("Query timed out - consider adjusting timeout or data model");
} catch (UnavailableException e) {
    System.out.printf("Not enough replicas: required=%d, alive=%d%n",
        e.getRequired(), e.getAlive());
} catch (WriteTimeoutException e) {
    System.out.println("Write timed out - check cluster health");
} catch (AllNodesFailedException e) {
    System.out.println("Cannot connect to any host: " + e.getAllErrors());
}
```

**Python**:

```python
from cassandra import ReadTimeout, Unavailable, NoHostAvailable

try:
    session.execute("SELECT * FROM users")
except ReadTimeout:
    print("Query timed out - consider adjusting timeout or data model")
except Unavailable as e:
    print(f"Not enough replicas: required={e.required_replicas}, alive={e.alive_replicas}")
except NoHostAvailable as e:
    print(f"Cannot connect to any host: {e.errors}")
```

---

## Best Practices

### Do

- ✅ Use prepared statements for repeated queries
- ✅ Set appropriate consistency levels
- ✅ Use token-aware load balancing
- ✅ Handle exceptions gracefully
- ✅ Close sessions and clusters on shutdown
- ✅ Use async for high-throughput workloads

### Don't

- ❌ Create new sessions for each query
- ❌ Use `ALLOW FILTERING` in production
- ❌ Ignore connection pool settings
- ❌ Use `ALL` consistency unnecessarily
- ❌ Ignore timeouts and retries

---

## Driver Documentation

For detailed driver documentation, refer to the official repositories:

- **[Java Driver](https://github.com/apache/cassandra-java-driver)** - Apache Cassandra Java Driver
- **[Spark Cassandra Connector](https://github.com/datastax/spark-cassandra-connector)** - Apache Spark integration for Cassandra
- **[Python Driver](https://github.com/apache/cassandra-python-driver)** - Apache Cassandra Python Driver
- **[Async Python Client](https://github.com/axonops/async-python-cassandra-client)** - Async Python Cassandra Client
- **[Node.js Driver](https://github.com/datastax/nodejs-driver)** - DataStax Node.js Driver
- **[Go Driver](https://github.com/gocql/gocql)** - GoCQL
- **[C# Driver](https://github.com/datastax/csharp-driver)** - DataStax C# Driver
- **[C++ Driver](https://github.com/datastax/cpp-driver)** - DataStax C++ Driver
- **[Ruby Driver](https://github.com/datastax/ruby-driver)** - DataStax Ruby Driver (maintenance mode)
- **[PHP Driver](https://github.com/datastax/php-driver)** - DataStax PHP Driver (maintenance mode)

---

## Next Steps

After connecting the application:

1. **[Data Modeling](../../data-modeling/index.md)** - Design effective schemas
2. **[CQL Reference](../../cql/index.md)** - Full query language reference
3. **[Performance Tuning](../../operations/performance/index.md)** - Optimize application performance
