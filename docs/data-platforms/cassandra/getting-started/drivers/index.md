---
title: "Cassandra Driver Guide"
description: "Getting started with Cassandra drivers. Quick setup guides for popular languages."
meta:
  - name: keywords
    content: "Cassandra drivers setup, quick start, language drivers"
---

# Cassandra Driver Guide

This guide covers connecting applications to Apache Cassandra using official drivers, with setup and basic usage for popular programming languages.

## Available Drivers

| Language | Driver | Status | Repository |
|----------|--------|--------|------------|
| **Java** | Apache Cassandra Java Driver | Production | [GitHub](https://github.com/apache/cassandra-java-driver) |
| **Python** | Apache Cassandra Python Driver | Production | [GitHub](https://github.com/apache/cassandra-python-driver) |
| **Python** | Async Python Cassandra Client | Early Release | [GitHub](https://github.com/axonops/async-python-cassandra-client) |
| **Node.js** | DataStax Node.js Driver | Production | [GitHub](https://github.com/datastax/nodejs-driver) |
| **Go** | GoCQL | Production | [GitHub](https://github.com/gocql/gocql) |
| **C#/.NET** | Apache Cassandra C# Driver | Production | [GitHub](https://github.com/apache/cassandra-csharp-driver) |
| **C/C++** | Apache Cassandra C++ Driver | Production | [GitHub](https://github.com/apache/cassandra-cpp-driver) |
| **Ruby** | Apache Cassandra Ruby Driver | Production | [GitHub](https://github.com/apache/cassandra-ruby-driver) |
| **PHP** | Apache Cassandra PHP Driver | Production | [GitHub](https://github.com/apache/cassandra-php-driver) |

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

For async frameworks like FastAPI and aiohttp:

```bash
pip install async-cassandra
```

```python
import asyncio
from async_cassandra import AsyncCluster

async def main():
    cluster = AsyncCluster(['127.0.0.1'])
    session = await cluster.connect()

    result = await session.execute("SELECT release_version FROM system.local")
    print(f"Cassandra version: {result.one().release_version}")

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

```python
# Python example with authentication
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

```python
# Python example with SSL
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

---

## Load Balancing Policies

### Token-Aware (Recommended)

Routes queries to the node that owns the data:

```java
// Java - Token-aware is default in v4+
CqlSession session = CqlSession.builder()
    .addContactPoint(new InetSocketAddress("127.0.0.1", 9042))
    .withLocalDatacenter("dc1")
    .build();
```

```python
# Python
from cassandra.policies import TokenAwarePolicy, DCAwareRoundRobinPolicy

cluster = Cluster(
    ['127.0.0.1'],
    load_balancing_policy=TokenAwarePolicy(
        DCAwareRoundRobinPolicy(local_dc='dc1')
    )
)
```

### DC-Aware Round Robin

Prefers nodes in the local datacenter:

```javascript
// Node.js
const client = new cassandra.Client({
  contactPoints: ['127.0.0.1'],
  localDataCenter: 'dc1',
  policies: {
    loadBalancing: new cassandra.policies.loadBalancing.DCAwareRoundRobinPolicy('dc1')
  }
});
```

---

## Prepared Statements

Always use prepared statements for:
- Better performance (parsed once)
- Protection against CQL injection
- Type safety

### Example

```python
# Python
from cassandra.cluster import Cluster

cluster = Cluster(['127.0.0.1'])
session = cluster.connect('my_keyspace')

# Prepare once
insert_stmt = session.prepare("""
    INSERT INTO users (user_id, username, email)
    VALUES (?, ?, ?)
""")

# Execute many times
import uuid
session.execute(insert_stmt, [uuid.uuid4(), 'john_doe', 'john@example.com'])
session.execute(insert_stmt, [uuid.uuid4(), 'jane_doe', 'jane@example.com'])
```

```java
// Java
PreparedStatement prepared = session.prepare(
    "INSERT INTO users (user_id, username, email) VALUES (?, ?, ?)"
);

BoundStatement bound = prepared.bind(
    UUID.randomUUID(), "john_doe", "john@example.com"
);
session.execute(bound);
```

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

For high-throughput applications:

### Python (asyncio)

!!! tip "Async Frameworks (FastAPI, aiohttp)"
    For true async/await support with frameworks like FastAPI, consider the [Async Python Cassandra Client](https://github.com/axonops/async-python-cassandra-client). It wraps the standard driver to prevent blocking the event loop and supports async paging with `async for` loops.

```python
from cassandra.cluster import Cluster
import asyncio

cluster = Cluster(['127.0.0.1'])
session = cluster.connect('my_keyspace')

async def insert_user(user_id, username, email):
    future = session.execute_async(
        "INSERT INTO users (user_id, username, email) VALUES (%s, %s, %s)",
        [user_id, username, email]
    )
    return future.result()

# Run multiple inserts concurrently
async def main():
    tasks = [
        insert_user(uuid.uuid4(), f'user{i}', f'user{i}@example.com')
        for i in range(100)
    ]
    await asyncio.gather(*tasks)

asyncio.run(main())
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

### Python

```python
from cassandra.cluster import Cluster
from cassandra.policies import HostDistance

cluster = Cluster(['127.0.0.1'])

# Set pool size per host
cluster.set_core_connections_per_host(HostDistance.LOCAL, 4)
cluster.set_max_connections_per_host(HostDistance.LOCAL, 10)
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

Handle transient failures:

```python
# Python
from cassandra.policies import RetryPolicy
from cassandra.cluster import Cluster

class CustomRetryPolicy(RetryPolicy):
    def on_read_timeout(self, query, consistency, required, received, data_retrieved, retry_num):
        if retry_num < 3:
            return self.RETRY, consistency
        return self.RETHROW, None

cluster = Cluster(
    ['127.0.0.1'],
    default_retry_policy=CustomRetryPolicy()
)
```

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

### Example

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
- **[Python Driver](https://github.com/apache/cassandra-python-driver)** - Apache Cassandra Python Driver
- **[Node.js Driver](https://github.com/datastax/nodejs-driver)** - DataStax Node.js Driver
- **[Go Driver](https://github.com/gocql/gocql)** - GoCQL

---

## Next Steps

After connecting the application:

1. **[Data Modeling](../../data-modeling/index.md)** - Design effective schemas
2. **[CQL Reference](../../cql/index.md)** - Full query language reference
3. **[Performance Tuning](../../operations/performance/index.md)** - Optimize application performance
