# Apache Cassandra Documentation

Apache Cassandra is a distributed NoSQL database designed for extreme scale, exceptional performance, and continuous availability. There is no master node—every node can handle reads and writes, so the failure of any single node (or even an entire datacenter) does not take down the database.

Cassandra excels at write-heavy workloads, time-series data, and applications requiring geographic distribution. Cassandra is less suited for complex queries, ad-hoc analytics, or workloads requiring strong consistency with frequent cross-partition transactions.

## What is Apache Cassandra?

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

## Documentation Sections

### Getting Started

New to Cassandra? Start here:

- [What is Cassandra?](getting-started/what-is-cassandra.md) - Introduction and core concepts
- [Installation Guide](getting-started/installation/index.md) - Install on Linux, Docker, or Kubernetes
- [First Cluster](getting-started/first-cluster.md) - Create and configure a first cluster
- [CQL Quickstart](getting-started/quickstart-cql.md) - Learn Cassandra Query Language basics
- [Driver Setup](getting-started/drivers/index.md) - Connect your application

### Architecture

Understand how Cassandra works:

- [Architecture Overview](architecture/index.md) - Distributed architecture fundamentals
- [Data Distribution](architecture/distributed-data/index.md) - Partitioning and token rings
- [Replication](architecture/distributed-data/replication.md) - How data is replicated for fault tolerance
- [Consistency Levels](architecture/distributed-data/consistency.md) - Tunable consistency explained
- [Compaction Strategies](architecture/storage-engine/compaction/index.md) - STCS, LCS, TWCS, and UCS
- [Storage Engine](architecture/storage-engine/index.md) - Memtables, SSTables, and commit log

### CQL Reference

Complete Cassandra Query Language documentation:

- [CQL Overview](cql/index.md) - CQL language reference
- [Data Types](cql/data-types/index.md) - Native, collection, and user-defined types
- [DDL Commands](cql/ddl/index.md) - CREATE, ALTER, DROP statements
- [DML Commands](cql/dml/index.md) - SELECT, INSERT, UPDATE, DELETE
- [Indexing](cql/indexing/index.md) - Secondary indexes and SAI
- [Functions](cql/functions/index.md) - Built-in and user-defined functions

### Data Modeling

Design effective Cassandra data models:

- [Data Modeling Guide](data-modeling/index.md) - Query-first design methodology
- [Key Concepts](data-modeling/concepts/index.md) - Partition keys, clustering columns
- [Anti-Patterns](data-modeling/anti-patterns/index.md) - Common mistakes to avoid

### Operations

Run Cassandra in production:

- [Operations Guide](operations/index.md) - Day-to-day operations
- [Cluster Management](operations/cluster-management/index.md) - Add, remove, replace nodes
- [Backup & Restore](operations/backup-restore/index.md) - Snapshots and recovery
- [Repair](operations/repair/index.md) - Maintain data consistency
- [Maintenance](operations/maintenance/index.md) - Routine maintenance tasks

### Configuration

Configure Cassandra for your workload:

- [Configuration Reference](operations/configuration/index.md) - All configuration files
- [cassandra.yaml](operations/configuration/cassandra-yaml/index.md) - Main configuration file
- [JVM Options](operations/configuration/jvm-options/index.md) - Heap and GC settings
- [Snitch Configuration](operations/configuration/snitch-config/index.md) - Topology awareness

### JMX Reference

Monitor and manage via JMX:

- [JMX Overview](operations/jmx-reference/index.md) - Connecting and using JMX
- [MBeans Reference](operations/jmx-reference/mbeans/index.md) - All 30 MBeans documented
- [Metrics Reference](operations/jmx-reference/metrics/index.md) - 500+ metrics with thresholds

### Monitoring

Monitor your Cassandra cluster:

- [Monitoring Guide](operations/monitoring/index.md) - What and how to monitor
- [Key Metrics](operations/monitoring/key-metrics/index.md) - Essential metrics to track
- [Alerting](operations/monitoring/alerting/index.md) - Alert thresholds and setup
- [Logging](operations/monitoring/logging/index.md) - Log analysis and configuration

### Performance

Optimize Cassandra performance:

- [Performance Tuning](operations/performance/index.md) - Optimization strategies
- [Hardware Sizing](operations/performance/hardware/index.md) - CPU, memory, disk recommendations
- [JVM Tuning](operations/performance/jvm-tuning/index.md) - GC and heap optimization
- [OS Tuning](operations/performance/os-tuning/index.md) - Linux kernel parameters
- [Query Optimization](operations/performance/query-optimization/index.md) - Efficient queries

### Security

Secure your cluster:

- [Security Guide](security/index.md) - Security overview
- [Authentication](security/authentication/index.md) - User authentication
- [Authorization](security/authorization/index.md) - Role-based access control
- [Encryption](security/encryption/index.md) - TLS and encryption at rest

### Tools

Essential Cassandra tools:

- [nodetool](operations/nodetool/index.md) - Cluster management commands
- [cqlsh](tools/cqlsh/index.md) - CQL shell reference
- [CQLAI](tools/cqlai/index.md) - Modern AI-powered CQL shell
- [SSTable Tools](operations/sstable-management/index.md) - SSTable utilities
- [cassandra-stress](tools/cassandra-stress/index.md) - Load testing

### Troubleshooting

Diagnose and fix issues:

- [Troubleshooting Guide](troubleshooting/index.md) - Problem-solving methodology
- [Diagnosis Procedures](troubleshooting/diagnosis/index.md) - Root cause analysis
- [Log Analysis](troubleshooting/log-analysis/index.md) - Interpreting logs

### Reference

Quick reference materials:

- [Reference](reference/index.md) - Quick reference

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

## About This Documentation

This documentation is maintained by [AxonOps](https://axonops.com), the monitoring, maintenance, and backup platform for Apache Cassandra.

### Cassandra Versions

This documentation covers:

- **Apache Cassandra 4.x** (4.0, 4.1)
- **Apache Cassandra 5.x** (5.0)

Version-specific differences are noted where applicable.

### Contributing

Found an error or want to contribute? Visit our [GitHub repository](https://github.com/axonops/documentation).

### Related Resources

- [Apache Cassandra Official Site](https://cassandra.apache.org/)
- [AxonOps Platform](https://axonops.com)
- [CQLAI - Modern CQL Shell](https://github.com/axonops/cqlai)
