---
title: "Cassandra Reference"
description: "Cassandra reference documentation. Project resources, links, and official guides."
meta:
  - name: keywords
    content: "Cassandra reference, documentation, project resources"
---

# Cassandra Reference

Quick reference for Apache Cassandra.

## Ports

| Port | Protocol | Purpose |
|------|----------|---------|
| 9042 | CQL | Native client connections (TLS configured via `client_encryption_options`) |
| 7000 | TCP | Inter-node communication (TLS configured via `server_encryption_options`) |
| 7199 | JMX | JMX monitoring |

!!! note "Deprecated Ports"
    - Port 9142 (`native_transport_port_ssl`) was deprecated in Cassandra 4.x and removed in 5.0. TLS is now configured on the standard 9042 port.
    - Port 7001 (`ssl_storage_port`) is deprecated. Internode TLS is configured on the standard 7000 port.

## Directories

| Directory | Purpose |
|-----------|---------|
| `/var/lib/cassandra/data` | SSTable data |
| `/var/lib/cassandra/commitlog` | Commit log |
| `/var/lib/cassandra/saved_caches` | Key/row cache |
| `/var/lib/cassandra/hints` | Hinted handoff |
| `/etc/cassandra/` | Configuration |
| `/var/log/cassandra/` | Logs |

## Configuration Files

| File | Purpose |
|------|---------|
| `cassandra.yaml` | Main configuration |
| `cassandra-env.sh` | Environment variables |
| `jvm11-server.options` | JVM settings |
| `cassandra-rackdc.properties` | DC/rack configuration |
| `logback.xml` | Logging configuration |

## Consistency Levels

| Level | Description |
|-------|-------------|
| ANY | One response (including hints) |
| ONE | One replica |
| TWO | Two replicas |
| THREE | Three replicas |
| QUORUM | Majority of replicas |
| LOCAL_QUORUM | Majority in local DC |
| EACH_QUORUM | Majority in each DC |
| ALL | All replicas |
| LOCAL_ONE | One in local DC |
| SERIAL | Serial consistency (LWT) |
| LOCAL_SERIAL | Local serial (LWT) |

## Common nodetool Commands

```bash
nodetool status              # Cluster status
nodetool info                # Node info
nodetool tpstats             # Thread pools
nodetool tablestats ks       # Table stats
nodetool compactionstats     # Compaction status
nodetool repair -pr ks       # Primary range repair
nodetool flush ks            # Flush memtables
nodetool drain               # Prepare for shutdown
nodetool snapshot            # Create backup
nodetool describecluster     # Cluster info
```

## CQL Quick Reference

```sql
-- Keyspace
CREATE KEYSPACE ks WITH replication = {
    'class': 'NetworkTopologyStrategy', 'dc1': 3
};

-- Table
CREATE TABLE ks.users (
    user_id UUID PRIMARY KEY,
    name TEXT
);

-- CRUD
INSERT INTO ks.users (user_id, name) VALUES (uuid(), 'John');
SELECT * FROM ks.users WHERE user_id = ?;
UPDATE ks.users SET name = 'Jane' WHERE user_id = ?;
DELETE FROM ks.users WHERE user_id = ?;
```

## Data Types

| Type | Description |
|------|-------------|
| `UUID` | 128-bit unique identifier |
| `TIMEUUID` | Time-based UUID |
| `TEXT` | UTF-8 string |
| `INT` | 32-bit integer |
| `BIGINT` | 64-bit integer |
| `FLOAT` | 32-bit floating point |
| `DOUBLE` | 64-bit floating point |
| `BOOLEAN` | true/false |
| `TIMESTAMP` | Date and time |
| `DATE` | Date only |
| `BLOB` | Binary data |
| `LIST<T>` | Ordered collection |
| `SET<T>` | Unique collection |
| `MAP<K,V>` | Key-value pairs |

---

## Apache Cassandra Project Resources

### Official Resources

| Resource | URL |
|----------|-----|
| Project Website | [cassandra.apache.org](https://cassandra.apache.org/) |
| Documentation | [cassandra.apache.org/doc/latest/](https://cassandra.apache.org/doc/latest/) |
| Downloads | [cassandra.apache.org/download/](https://cassandra.apache.org/download/) |

### Source Code and Development

| Resource | URL |
|----------|-----|
| GitHub Repository | [github.com/apache/cassandra](https://github.com/apache/cassandra) |
| GitHub Mirror (read-only) | [github.com/apache/cassandra](https://github.com/apache/cassandra) |
| ASF GitBox | [gitbox.apache.org/repos/asf/cassandra.git](https://gitbox.apache.org/repos/asf/cassandra.git) |

### Issue Tracking and Enhancement Proposals

| Resource | URL |
|----------|-----|
| JIRA Issue Tracker | [issues.apache.org/jira/browse/CASSANDRA](https://issues.apache.org/jira/browse/CASSANDRA) |
| CEP Wiki (Enhancement Proposals) | [cwiki.apache.org/confluence/display/CASSANDRA/CEP](https://cwiki.apache.org/confluence/pages/viewpage.action?pageId=95652201) |
| Cassandra Wiki | [cwiki.apache.org/confluence/display/CASSANDRA](https://cwiki.apache.org/confluence/display/CASSANDRA) |

### Community

| Resource | URL |
|----------|-----|
| ASF Slack (#cassandra) | [s.apache.org/slack-invite](https://s.apache.org/slack-invite) (then join #cassandra) |
| Stack Overflow | [stackoverflow.com/questions/tagged/cassandra](https://stackoverflow.com/questions/tagged/cassandra) |

### Mailing Lists

| List | Purpose | Subscribe |
|------|---------|-----------|
| user@cassandra.apache.org | User questions and discussions | [Subscribe](https://lists.apache.org/list.html?user@cassandra.apache.org) |
| dev@cassandra.apache.org | Development discussions | [Subscribe](https://lists.apache.org/list.html?dev@cassandra.apache.org) |
| commits@cassandra.apache.org | Commit notifications | [Subscribe](https://lists.apache.org/list.html?commits@cassandra.apache.org) |

### Blogs and News

| Resource | URL |
|----------|-----|
| Apache Cassandra Blog | [cassandra.apache.org/blog/](https://cassandra.apache.org/blog/) |
| Planet Cassandra | [planetcassandra.org](https://planetcassandra.org/) |

---

## Next Steps

- **[CQL Reference](../cql/index.md)** - Full CQL guide
- **[Configuration](../operations/configuration/index.md)** - Configuration details
- **[nodetool](../operations/nodetool/index.md)** - Command reference