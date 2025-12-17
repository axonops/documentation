---
title: "Apache Cassandra Documentation"
description: "Complete Apache Cassandra documentation and reference guide. Production-grade coverage of architecture, CQL, operations, and troubleshooting."
meta:
  - name: keywords
    content: "Apache Cassandra documentation, Cassandra reference, Cassandra guide, CQL reference, Cassandra operations"
---

# Apache Cassandra® Documentation

Production-grade reference for architecture, CQL, and operations.

## Documentation Scope

This reference documentation covers Apache Cassandra versions 4.0 through 5.x, with emphasis on production deployments. **Cassandra 5.0 (September 2024) introduced major features** including Storage-Attached Indexes (SAI), Vector Search, and Unified Compaction Strategy (UCS).

| Version Range | Java Requirement | Documentation Status |
|--------------|:----------------:|---------------------|
| 3.11.x       | Java 8           | Legacy reference |
| 4.0.x        | Java 8/11        | Supported |
| 4.1.x        | Java 8/11        | Fully Documented |
| 5.0.x        | Java 11/17       | **Current (5.0.6)** |

Legend: ✅ Production Ready | ⚠️ Limited/Deprecated | ❌ Not Supported

---

## What's New

### Cassandra 5.0.6 (October 2025) - Current Release

- Bug fixes and stability improvements

### Cassandra 5.0.0 (September 2024) - Major Release

- **Storage-Attached Indexes (SAI)** (CEP-7) - Efficient secondary indexing within storage layer
- **Vector data type and search** (CEP-30) - Approximate nearest neighbor searching via SAI
- **Unified Compaction Strategy (UCS)** (CEP-26) - Adaptive compaction replacing multiple strategies
- **Trie memtables** (CEP-19) - Trie-based in-memory data structures
- **Trie SSTables** (CEP-25) - Trie-indexed SSTable format
- **Dynamic Data Masking** (CEP-20) - Selective redaction of sensitive data at query time
- **Java 17 support** - recommended for Cassandra 5.0
- **TTL and writetime on collections/UDTs** - Extended metadata for complex types
- **CIDR-based authorizer** (CEP-33) - Network-based access control
- **New math functions**: `abs`, `exp`, `log`, `log10`, `round`

### Cassandra 4.1.10 (September 2025)

- Bug fixes and stability improvements

### Cassandra 4.1.0 (December 2022)

- **Paxos v2** - Enhanced lightweight transaction protocol
- **Guardrails** - Operational safety boundaries and limits
- **Partition denylist** - Block access to problematic partitions
- **Top partition tracking** - Per-table monitoring of hot partitions
- **Native transport rate limiting** - Request throughput controls
- **Client-side password hashing** - Enhanced authentication security
- **Pluggable memtables** - Custom memtable implementations

### Cassandra 4.0.19 (October 2025)

- Bug fixes and stability improvements

### Cassandra 4.0.0 (July 2021)

- **Virtual tables** - System information via CQL queries
- **Audit logging** - Comprehensive query audit trail
- **Full query logging** - Capture all queries for replay
- **Incremental repair improvements** - More efficient anti-entropy
- **Zero-copy streaming** - Faster data transfer between nodes
- **Java 11 support** - Modern JVM compatibility

---

Apache Cassandra is a widely adopted distributed database, but much of its operational and architectural knowledge has historically lived in mailing lists, conference talks, and tribal knowledge rather than formal documentation.

This documentation provides a comprehensive, production-focused reference for Apache Cassandra, covering storage engine internals, compaction strategies, indexing, CQL semantics, data modeling, and operational tooling. Content is designed for developers, operators, and architects building and maintaining Cassandra deployments at scale.

This documentation complements the [Official Apache Cassandra Documentation](https://cassandra.apache.org/doc/latest/), providing deeper explanations of behavioral contracts, failure semantics, and practical guidance for real-world deployments.

---

Apache Cassandra is a distributed NoSQL database designed for extreme scale, exceptional performance, and continuous availability. There is no master node—every node can handle reads and writes, so the failure of any single node (or even an entire datacenter) does not take down the database.

Cassandra excels at write-heavy workloads, time-series data, and applications requiring geographic distribution. Cassandra is less suited for complex queries, ad-hoc analytics, or workloads requiring strong consistency with frequent cross-partition transactions.

---

## About This Documentation

This documentation serves as a comprehensive reference for Apache Cassandra, covering architecture, configuration, operations, data modeling, CQL, and troubleshooting. The goal is to provide complete, accurate, and practical guidance for developers, operators, and architects working with Cassandra in production environments.

| Principle | Description |
|-----------|-------------|
| **Source Code Verified** | Configuration options, default values, and behavior are cross-referenced against the Cassandra source code to ensure accuracy |
| **CEP Aligned** | New features reference their corresponding [Cassandra Enhancement Proposals](https://cwiki.apache.org/confluence/display/CASSANDRA/CEP) (CEPs) for design rationale and implementation details |
| **Version Aware** | Documentation notes version-specific differences between Cassandra 4.x and 5.x releases |
| **Operationally Focused** | Content prioritizes practical operational guidance derived from production experience |

Topics are organized for both learning and reference. New users can follow the Getting Started guides sequentially, while experienced operators can use the detailed reference sections for specific configuration options, JMX metrics, and operational procedures.

---

## What is Apache Cassandra?

### History and Origins

Cassandra was created at Facebook in 2007 by Avinash Lakshman and Prashant Malik to power Facebook's Inbox Search feature—a system requiring high write throughput across hundreds of millions of users with strict latency requirements. Lakshman, a co-author of Amazon's Dynamo paper, brought distributed systems expertise that shaped Cassandra's architecture.

| Year | Milestone |
|------|-----------|
| 2007 | Development begins at Facebook |
| 2008 | Open sourced under Apache License 2.0 (July) |
| 2009 | Enters Apache Incubator (March) |
| 2010 | Graduates to Apache Top-Level Project (February) |
| 2011 | Cassandra 1.0 released |
| 2014 | Cassandra 2.0 introduces lightweight transactions |
| 2016 | Cassandra 3.0 brings materialized views and SASI |
| 2021 | Cassandra 4.0 after extensive testing focus |
| 2024 | Cassandra 5.0 introduces vectors, SAI, and UCS |

The project is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0), permitting commercial use, modification, and distribution.

### Design Influences

Cassandra's design draws from two foundational distributed systems papers: Google's BigTable (2006) provided the storage model—SSTables, memtables, and the LSM-tree architecture. Amazon's Dynamo (2007) provided the distribution model—consistent hashing, gossip-based cluster membership, and tunable consistency levels.

### Performance Characteristics

Cassandra delivers exceptional performance at scale:

| Metric | Typical Performance | Notes |
|--------|---------------------|-------|
| **Write Throughput** | 100,000+ writes/sec per node | Sequential I/O to commit log; parallel memtable inserts |
| **Read Latency (P99)** | 1-5 ms | With proper data modeling and warm caches |
| **Write Latency (P99)** | 1-2 ms | Commit log append + memtable insert |
| **Scalability** | Linear to 1000+ nodes | Proven in production at petabyte scale |

Performance derives from Cassandra's architecture:

- **Log-structured writes**: All writes append sequentially to the commit log, avoiding random disk seeks
- **Memtable buffering**: Recent writes held in memtables before flushing to disk
- **Parallel execution**: Requests distributed across nodes; no single bottleneck
- **Token-aware routing**: Drivers send requests directly to replica nodes, avoiding extra network hops

### Fault Tolerance

Cassandra is designed to survive failures at every level:

| Failure Scenario | Cassandra Behavior |
|------------------|-------------------|
| **Single node failure** | Remaining replicas serve requests; hinted handoff queues writes for recovery |
| **Rack failure** | Rack-aware replication ensures replicas exist in other racks |
| **Datacenter failure** | Multi-DC replication provides geographic redundancy; traffic fails over automatically |
| **Network partition** | Nodes continue serving requests independently; reconciliation occurs on recovery |

Unlike primary-replica databases that fail over to a standby, Cassandra has no failover—all nodes are active and capable of serving any request. This eliminates failover latency and split-brain scenarios.

### Key Features

| Feature | Description |
|---------|-------------|
| **Distributed Architecture** | Data is automatically distributed across multiple nodes |
| **Linear Scalability** | Add capacity by adding nodes with no downtime |
| **High Availability** | No single point of failure; survives node and datacenter failures |
| **Tunable Consistency** | Choose consistency level per operation |
| **Multi-Datacenter Replication** | Built-in support for geographically distributed clusters |
| **Flexible Schema** | Wide-column store with support for complex data types |

## Common Misconceptions

Understanding what Cassandra is *not* helps set appropriate expectations.

| Misconception | Reality |
|---------------|---------|
| **"Cassandra is eventually consistent"** | Cassandra offers **tunable** consistency. With `QUORUM` reads and writes, strong consistency is achieved. "Eventually consistent" only applies when using weaker consistency levels like `ONE`. |
| **"Cassandra doesn't support transactions"** | Cassandra supports lightweight transactions (LWT) using Paxos for compare-and-set operations. Accord, a general-purpose distributed transaction protocol, is under active development for a future release. LWT provides linearizable consistency for specific use cases, though not ACID transactions across arbitrary rows. |
| **"Cassandra can't do joins"** | Correct—by design. Cassandra optimizes for fast reads at scale by denormalizing data. Model data according to query patterns rather than normalizing and joining at read time. |
| **"Cassandra is only for write-heavy workloads"** | Cassandra handles read-heavy workloads effectively when data is modeled correctly. The key is designing tables around query patterns, not write patterns. |
| **"Cassandra requires expensive hardware"** | Cassandra runs effectively on both commodity hardware and high-end servers. Modern Cassandra scales well both horizontally (adding nodes) and vertically (larger instances with more CPU cores and memory). |
| **"Cassandra is hard to operate"** | Modern tooling such as [AxonOps](https://axonops.com) automates most operational tasks. The learning curve exists, but operational complexity is manageable with proper tooling and training. |
| **"Data modeling is too difficult"** | Query-first modeling is different from relational modeling, not harder. Once the principles are understood (partition keys, clustering columns, denormalization), modeling becomes straightforward. Tools like [AxonOps Workbench](https://github.com/axonops/axonops-workbench) provide visual data modeling assistance. |
| **"Cassandra loses data"** | Data loss occurs from misconfiguration (improper `gc_grace_seconds`, skipped repairs) or hardware failures beyond the replication factor—not from Cassandra itself. With proper operations, Cassandra provides strong durability guarantees. |
| **"Cassandra is an in-memory database"** | Cassandra is a persistent, disk-based database. While memtables buffer recent writes in memory, all data is durably written to the commit log immediately and flushed to SSTables on disk. Memory caches improve read performance but are not the primary storage. |

## Getting Started

New to Cassandra? Begin with installation and initial configuration.

<div class="grid cards" markdown>

-   :material-download:{ .lg .middle } **Installation**

    ---

    Install Cassandra on Linux, Docker, or Kubernetes environments.

    [:octicons-arrow-right-24: Installation Guide](getting-started/installation/index.md)

-   :material-rocket-launch:{ .lg .middle } **First Cluster**

    ---

    Create and configure a first Cassandra cluster step by step.

    [:octicons-arrow-right-24: First Cluster](getting-started/first-cluster.md)

-   :material-language-java:{ .lg .middle } **Client Drivers**

    ---

    Connect applications using Java, Python, Go, and other drivers.

    [:octicons-arrow-right-24: Driver Setup](getting-started/drivers/index.md)

-   :material-console:{ .lg .middle } **CQL Quickstart**

    ---

    Learn Cassandra Query Language basics with hands-on examples.

    [:octicons-arrow-right-24: CQL Quickstart](getting-started/quickstart-cql.md)

</div>

---

## Architecture

Understand Cassandra's distributed architecture and storage engine.

<div class="grid cards" markdown>

-   :material-sitemap:{ .lg .middle } **Architecture Overview**

    ---

    Distributed architecture fundamentals, gossip protocol, and cluster topology.

    [:octicons-arrow-right-24: Architecture Overview](architecture/index.md)

-   :material-share-variant:{ .lg .middle } **Data Distribution**

    ---

    Partitioning, token rings, and virtual nodes (vnodes) explained.

    [:octicons-arrow-right-24: Data Distribution](architecture/distributed-data/index.md)

-   :material-content-copy:{ .lg .middle } **Replication**

    ---

    Replication strategies, consistency levels, and fault tolerance.

    [:octicons-arrow-right-24: Replication](architecture/distributed-data/replication.md)

-   :material-harddisk:{ .lg .middle } **Storage Engine**

    ---

    Memtables, SSTables, commit log, and write path internals.

    [:octicons-arrow-right-24: Storage Engine](architecture/storage-engine/index.md)

-   :material-folder-zip:{ .lg .middle } **Compaction**

    ---

    STCS, LCS, TWCS, and UCS compaction strategies explained.

    [:octicons-arrow-right-24: Compaction Strategies](architecture/storage-engine/compaction/index.md)

</div>

---

## CQL Reference

Complete Cassandra Query Language documentation.

<div class="grid cards" markdown>

-   :material-database:{ .lg .middle } **CQL Overview**

    ---

    CQL language reference and query syntax fundamentals.

    [:octicons-arrow-right-24: CQL Overview](cql/index.md)

-   :material-format-list-bulleted-type:{ .lg .middle } **Data Types**

    ---

    Native, collection, and user-defined types reference.

    [:octicons-arrow-right-24: Data Types](cql/data-types/index.md)

-   :material-table-plus:{ .lg .middle } **DDL Commands**

    ---

    CREATE, ALTER, DROP statements for schema management.

    [:octicons-arrow-right-24: DDL Commands](cql/ddl/index.md)

-   :material-table-edit:{ .lg .middle } **DML Commands**

    ---

    SELECT, INSERT, UPDATE, DELETE for data manipulation.

    [:octicons-arrow-right-24: DML Commands](cql/dml/index.md)

-   :material-magnify:{ .lg .middle } **Indexing**

    ---

    Secondary indexes, SASI, and Storage-Attached Indexing (SAI).

    [:octicons-arrow-right-24: Indexing](cql/indexing/index.md)

-   :material-function:{ .lg .middle } **Functions**

    ---

    Built-in and user-defined functions reference.

    [:octicons-arrow-right-24: Functions](cql/functions/index.md)

</div>

---

## Data Modeling

Design effective Cassandra data models.

<div class="grid cards" markdown>

-   :material-drawing:{ .lg .middle } **Data Modeling Guide**

    ---

    Query-first design methodology and denormalization patterns.

    [:octicons-arrow-right-24: Data Modeling Guide](data-modeling/index.md)

-   :material-key:{ .lg .middle } **Key Concepts**

    ---

    Partition keys, clustering columns, and primary key design.

    [:octicons-arrow-right-24: Key Concepts](data-modeling/concepts/index.md)

-   :material-alert-octagon:{ .lg .middle } **Anti-Patterns**

    ---

    Common data modeling mistakes and how to avoid them.

    [:octicons-arrow-right-24: Anti-Patterns](data-modeling/anti-patterns/index.md)

</div>

---

## Operations

Production deployment, monitoring, and maintenance procedures.

<div class="grid cards" markdown>

-   :material-server-network:{ .lg .middle } **Cluster Management**

    ---

    Add, remove, replace, and decommission nodes safely.

    [:octicons-arrow-right-24: Cluster Management](operations/cluster-management/index.md)

-   :material-backup-restore:{ .lg .middle } **Backup & Restore**

    ---

    Snapshots, incremental backups, and disaster recovery.

    [:octicons-arrow-right-24: Backup & Restore](operations/backup-restore/index.md)

-   :material-wrench:{ .lg .middle } **Repair**

    ---

    Anti-entropy repair to maintain data consistency.

    [:octicons-arrow-right-24: Repair](operations/repair/index.md)

-   :material-cog:{ .lg .middle } **Configuration**

    ---

    cassandra.yaml, JVM options, and snitch configuration.

    [:octicons-arrow-right-24: Configuration](operations/configuration/index.md)

-   :material-tools:{ .lg .middle } **Maintenance**

    ---

    Routine maintenance tasks and operational procedures.

    [:octicons-arrow-right-24: Maintenance](operations/maintenance/index.md)

</div>

---

## Monitoring & Performance

Monitor clusters and optimize performance.

<div class="grid cards" markdown>

-   :material-chart-line:{ .lg .middle } **Monitoring**

    ---

    JMX metrics, key metrics to track, and alerting strategies.

    [:octicons-arrow-right-24: Monitoring Guide](operations/monitoring/index.md)

-   :material-gauge:{ .lg .middle } **JMX Reference**

    ---

    500+ metrics with thresholds and 30 MBeans documented.

    [:octicons-arrow-right-24: JMX Reference](operations/jmx-reference/index.md)

-   :material-speedometer:{ .lg .middle } **Performance Tuning**

    ---

    Hardware sizing, JVM tuning, and OS optimization.

    [:octicons-arrow-right-24: Performance Guide](operations/performance/index.md)

-   :material-flash:{ .lg .middle } **Query Optimization**

    ---

    Write efficient queries and avoid performance pitfalls.

    [:octicons-arrow-right-24: Query Optimization](operations/performance/query-optimization/index.md)

</div>

---

## Security

Authentication, authorization, and encryption for Cassandra deployments.

<div class="grid cards" markdown>

-   :material-account-key:{ .lg .middle } **Authentication**

    ---

    Internal authentication, LDAP integration, and Kerberos.

    [:octicons-arrow-right-24: Authentication](security/authentication/index.md)

-   :material-shield-lock:{ .lg .middle } **Authorization**

    ---

    Role-based access control and permission management.

    [:octicons-arrow-right-24: Authorization](security/authorization/index.md)

-   :material-lock:{ .lg .middle } **Encryption**

    ---

    TLS for client and internode encryption, encryption at rest.

    [:octicons-arrow-right-24: Encryption](security/encryption/index.md)

</div>

---

## Tools

Essential Cassandra command-line and administration tools.

<div class="grid cards" markdown>

-   :material-console-line:{ .lg .middle } **nodetool**

    ---

    Cluster management commands for operations and diagnostics.

    [:octicons-arrow-right-24: nodetool Reference](operations/nodetool/index.md)

-   :material-code-greater-than:{ .lg .middle } **cqlsh**

    ---

    Interactive CQL shell for queries and schema management.

    [:octicons-arrow-right-24: cqlsh Reference](tools/cqlsh/index.md)

-   :material-robot:{ .lg .middle } **CQLAI**

    ---

    Modern AI-powered CQL shell with intelligent assistance.

    [:octicons-arrow-right-24: CQLAI](tools/cqlai/index.md)

-   :material-test-tube:{ .lg .middle } **cassandra-stress**

    ---

    Load testing and benchmarking tool for Cassandra.

    [:octicons-arrow-right-24: cassandra-stress](tools/cassandra-stress/index.md)

</div>

---

## Troubleshooting

Diagnostic procedures and solutions for common issues.

<div class="grid cards" markdown>

-   :material-stethoscope:{ .lg .middle } **Diagnosis**

    ---

    Root cause analysis procedures and diagnostic workflows.

    [:octicons-arrow-right-24: Diagnosis Guide](troubleshooting/diagnosis/index.md)

-   :material-file-search:{ .lg .middle } **Log Analysis**

    ---

    Interpreting logs, log patterns, and log configuration.

    [:octicons-arrow-right-24: Log Analysis](troubleshooting/log-analysis/index.md)

-   :material-alert-circle:{ .lg .middle } **Common Errors**

    ---

    ReadTimeout, WriteTimeout, and other common errors explained.

    [:octicons-arrow-right-24: Troubleshooting Guide](troubleshooting/index.md)

</div>

---

## Quick Reference

<div class="grid cards" markdown>

-   :material-book-open-variant:{ .lg .middle } **Reference**

    ---

    Quick reference for configuration, metrics, and commands.

    [:octicons-arrow-right-24: Reference](reference/index.md)

</div>

---

## Quick Links

### By Experience Level

**Beginners**:
[Installation](getting-started/installation/index.md) →
[First Cluster](getting-started/first-cluster.md) →
[CQL Quickstart](getting-started/quickstart-cql.md)

**Developers**:
[Data Modeling](data-modeling/index.md) →
[CQL Reference](cql/index.md) →
[Drivers](getting-started/drivers/index.md)

**Operators**:
[Operations](operations/index.md) →
[Monitoring](operations/monitoring/index.md) →
[Troubleshooting](troubleshooting/index.md)

**Performance Engineers**:
[JMX Metrics](operations/jmx-reference/metrics/index.md) →
[Performance Tuning](operations/performance/index.md) →
[Benchmarking](operations/performance/benchmarking/index.md)

### Common Tasks

| Task | Documentation |
|------|---------------|
| Install Cassandra | [Installation Guide](getting-started/installation/index.md) |
| Design a data model | [Data Modeling Guide](data-modeling/index.md) |
| Fix timeout errors | [ReadTimeoutException](troubleshooting/common-errors/read-timeout.md) |
| Manage cluster nodes | [Cluster Management](operations/cluster-management/index.md) |
| Configure backups | [Backup Guide](operations/backup-restore/index.md) |
| Monitor the cluster | [Monitoring Guide](operations/monitoring/index.md) |
| Tune performance | [Performance Guide](operations/performance/index.md) |

---

## Version Compatibility

### Supported Versions

| Version | Release Date | End of Support | Status |
|---------|--------------|----------------|--------|
| 5.0.x | September 2024 | Until 5.3.0 release | **Current** |
| 4.1.x | December 2022 | Until 5.2.0 release | Supported |
| 4.0.x | July 2021 | Until 5.1.0 release | Supported |
| 3.11.x | June 2017 | Unmaintained | Legacy |

!!! warning "Upgrade Path"
    Direct upgrades skipping major versions are not supported. To upgrade from 3.11.x to 5.0.x:

    1. Upgrade 3.11.x → 4.0.x
    2. Upgrade 4.0.x → 4.1.x
    3. Upgrade 4.1.x → 5.0.x

!!! note "Documentation Conventions"
    This documentation uses RFC 2119 terminology (must, should, may) to indicate requirement levels. Version-specific behaviors are explicitly noted with the applicable Cassandra version range.

---

## Contributing

This documentation is maintained by [AxonOps](https://axonops.com). Found an error or want to contribute? Visit the [GitHub repository](https://github.com/axonops/documentation).

---

## Related Resources

- [Apache Cassandra Official Site](https://cassandra.apache.org/)
- [AxonOps Platform](https://axonops.com)
- [CQLAI - Modern CQL Shell](https://github.com/axonops/cqlai)
