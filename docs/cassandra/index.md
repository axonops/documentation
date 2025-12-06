# Apache Cassandra Documentation

Apache Cassandra is a distributed NoSQL database that scales horizontally across commodity hardware while providing continuous availability. There is no master node—every node can handle reads and writes, so the failure of any single node (or even an entire datacenter) does not take down the database.

Cassandra excels at write-heavy workloads, time-series data, and applications requiring geographic distribution. Cassandra is less suited for complex queries, ad-hoc analytics, or workloads requiring strong consistency with frequent cross-partition transactions.

## What is Apache Cassandra?

Cassandra's design draws from two foundational distributed systems papers: Google's BigTable (2006) provided the storage model—SSTables, memtables, and the LSM-tree architecture. Amazon's Dynamo (2007) provided the distribution model—consistent hashing, gossip-based cluster membership, and tunable consistency levels.

### Key Features

| Feature | Description |
|---------|-------------|
| **Distributed Architecture** | Data is automatically distributed across multiple nodes |
| **Linear Scalability** | Add capacity by adding nodes with no downtime |
| **High Availability** | No single point of failure; survives node and datacenter failures |
| **Tunable Consistency** | Choose consistency level per operation |
| **Multi-Datacenter Replication** | Built-in support for geographically distributed clusters |
| **Flexible Schema** | Wide-column store with support for complex data types |

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
- [Data Distribution](architecture/data-distribution.md) - Partitioning and token rings
- [Replication](architecture/replication/index.md) - How data is replicated for fault tolerance
- [Consistency Levels](architecture/consistency/index.md) - Tunable consistency explained
- [Compaction Strategies](architecture/compaction/index.md) - STCS, LCS, TWCS, and UCS
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
- [Patterns](data-modeling/patterns/index.md) - Time-series, bucketing, denormalization
- [Anti-Patterns](data-modeling/anti-patterns/index.md) - Common mistakes to avoid
- [Real-World Examples](data-modeling/examples/index.md) - Production-ready schemas

### Operations

Run Cassandra in production:

- [Operations Guide](operations/index.md) - Day-to-day operations
- [Cluster Management](operations/cluster-management/index.md) - Add, remove, replace nodes
- [Backup & Restore](operations/backup-restore/index.md) - Snapshots and recovery
- [Repair](operations/repair/index.md) - Maintain data consistency
- [Rolling Restart](operations/rolling-restart.md) - Zero-downtime restarts

### Configuration

Configure Cassandra for your workload:

- [Configuration Reference](configuration/index.md) - All configuration files
- [cassandra.yaml](configuration/cassandra-yaml/index.md) - Main configuration file
- [JVM Options](configuration/jvm-options/index.md) - Heap and GC settings
- [Snitch Configuration](configuration/snitch-config/index.md) - Topology awareness

### JMX Reference

Monitor and manage via JMX:

- [JMX Overview](jmx-reference/index.md) - Connecting and using JMX
- [MBeans Reference](jmx-reference/mbeans/index.md) - All 30 MBeans documented
- [Metrics Reference](jmx-reference/metrics/index.md) - 500+ metrics with thresholds

### Monitoring

Monitor your Cassandra cluster:

- [Monitoring Guide](monitoring/index.md) - What and how to monitor
- [Key Metrics](monitoring/key-metrics/index.md) - Essential metrics to track
- [Alerting](monitoring/alerting/index.md) - Alert thresholds and setup
- [Dashboards](monitoring/dashboards/index.md) - Grafana and AxonOps dashboards

### Performance

Optimize Cassandra performance:

- [Performance Tuning](performance/index.md) - Optimization strategies
- [Hardware Sizing](performance/hardware/index.md) - CPU, memory, disk recommendations
- [JVM Tuning](performance/jvm-tuning/index.md) - GC and heap optimization
- [OS Tuning](performance/os-tuning/index.md) - Linux kernel parameters
- [Query Optimization](performance/query-optimization/index.md) - Efficient queries

### Security

Secure your cluster:

- [Security Guide](security/index.md) - Security overview
- [Authentication](security/authentication/index.md) - User authentication
- [Authorization](security/authorization/index.md) - Role-based access control
- [Encryption](security/encryption/index.md) - TLS and encryption at rest

### Tools

Essential Cassandra tools:

- [Tools Overview](tools/index.md) - All available tools
- [nodetool](tools/nodetool/index.md) - Cluster management commands
- [cqlsh](tools/cqlsh/index.md) - CQL shell reference
- [CQLAI](tools/cqlai/index.md) - Modern AI-powered CQL shell
- [SSTable Tools](tools/sstable-tools/index.md) - SSTable utilities
- [cassandra-stress](tools/cassandra-stress/index.md) - Load testing

### Troubleshooting

Diagnose and fix issues:

- [Troubleshooting Guide](troubleshooting/index.md) - Problem-solving methodology
- [Common Errors](troubleshooting/common-errors/index.md) - Exception reference
- [Diagnosis Procedures](troubleshooting/diagnosis/index.md) - Root cause analysis
- [Playbooks](troubleshooting/playbooks/index.md) - Step-by-step runbooks
- [Log Analysis](troubleshooting/log-analysis/index.md) - Interpreting logs

### Multi-Datacenter

Deploy across datacenters:

- [Multi-DC Guide](multi-datacenter/index.md) - Multi-datacenter architecture
- [Replication Strategies](multi-datacenter/replication.md) - Cross-DC replication
- [Failover](multi-datacenter/failover.md) - DC failover procedures

### Reference

Quick reference materials:

- [Reference](reference/index.md) - Quick reference
- [System Tables](reference/system-tables.md) - System keyspace tables
- [Virtual Tables](reference/virtual-tables.md) - Virtual table reference
- [Limits](reference/limits.md) - Cassandra limits
- [Glossary](reference/glossary.md) - Terminology

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
[Monitoring](monitoring/index.md) →
[Troubleshooting](troubleshooting/index.md)

**Performance Engineers**:
[JMX Metrics](jmx-reference/metrics/index.md) →
[Performance Tuning](performance/index.md) →
[Benchmarking](performance/benchmarking/index.md)

### Common Tasks

| Task | Documentation |
|------|---------------|
| Install Cassandra | [Installation Guide](getting-started/installation/index.md) |
| Design a data model | [Data Modeling Guide](data-modeling/index.md) |
| Fix timeout errors | [ReadTimeoutException](troubleshooting/common-errors/read-timeout.md) |
| Add a node | [Adding Nodes](operations/cluster-management/adding-nodes.md) |
| Configure backups | [Backup Guide](operations/backup-restore/index.md) |
| Monitor the cluster | [Monitoring Guide](monitoring/index.md) |
| Tune performance | [Performance Guide](performance/index.md) |

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
