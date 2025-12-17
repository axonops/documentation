---
title: "Apache Kafka Reference Documentation"
description: "Comprehensive Apache Kafka documentation covering architecture, operations, security, and best practices for production deployments."
meta:
  - name: keywords
    content: "Apache Kafka, Kafka documentation, event streaming, distributed messaging, Kafka architecture, Kafka operations"
---

# Apache Kafka® Reference Documentation

Apache Kafka® is a distributed event streaming platform designed for high-throughput, fault-tolerant data pipelines. This documentation provides comprehensive coverage of Kafka architecture, operations, and best practices for production deployments.

## Documentation Scope

This reference documentation covers Apache Kafka versions 2.8 through 4.1.x, with particular emphasis on KRaft-mode deployments. **Kafka 4.0 (March 2025) removed ZooKeeper entirely**—KRaft is now the only supported metadata management mode.

| Version Range | ZooKeeper Mode | KRaft Mode | Documentation Status |
|--------------|:--------------:|:----------:|---------------------|
| 2.8.x        | ✅            | ⚠️ Early Access | Legacy reference |
| 3.0.x - 3.2.x | ✅           | ⚠️ Preview | Legacy reference |
| 3.3.x - 3.5.x | ✅           | ✅         | Supported |
| 3.6.x - 3.9.x | ⚠️ Deprecated | ✅         | Fully Documented |
| 4.0.x        | ❌ Removed    | ✅         | Fully Documented |
| 4.1.x        | ❌ Removed    | ✅         | **Current (4.1.1)** |

Legend: ✅ Production Ready | ⚠️ Limited/Deprecated | ❌ Not Supported

---

## What's New

### Kafka 4.1 (September 2025) - Current Release

Latest: **4.1.1** (November 2025)

- **Streams Rebalance Protocol** (KIP-1071) - Early access for improved Kafka Streams rebalancing
- **Enhanced metrics registration** (KIP-877) - Better metrics for plugins and connectors across brokers, producers, and consumers
- Various bug fixes and stability improvements in 4.1.1

### Kafka 4.0 (March 2025) - Major Release

- **ZooKeeper removed** - KRaft is now the only metadata management mode
- **New Consumer Group Protocol GA** (KIP-848) - Dramatically faster rebalances
- **Queues for Kafka** (KIP-932) - Early access for traditional queue semantics
- **Java 17 required** for brokers, Connect, and tools (Java 11 for clients)
- **Log4j2** replaces Log4j 1.x
- **MirrorMaker 1 removed** - Use MirrorMaker 2

### Kafka 3.9 (November 2024)

- **Dynamic KRaft quorum** (KIP-853) - Add/remove controllers without downtime
- Final 3.x release before ZooKeeper removal

### Kafka 3.8 (July 2024)

- **Compression level configuration** (KIP-390)
- Tiered storage JBOD compatibility (early access)

### Kafka 3.7 (February 2024)

- **JBOD in KRaft** (KIP-858) - Early access
- **Client metrics** (KIP-714)
- **Next-gen consumer rebalance** (KIP-848) - Early access

---

## Getting Started

New to Apache Kafka? Begin with installation and initial configuration.

<div class="grid cards" markdown>

-   :material-download:{ .lg .middle } **Installation**

    ---

    Deploy Kafka on Linux, containerized environments, or managed cloud services.

    [:octicons-arrow-right-24: Installation Guide](getting-started/installation/index.md)

-   :material-language-java:{ .lg .middle } **Client Drivers**

    ---

    Configure client libraries for Java, Python, Go, and other languages.

    [:octicons-arrow-right-24: Driver Documentation](getting-started/drivers/index.md)

</div>

---

## Core Concepts

Understand the fundamental concepts underpinning Kafka's distributed architecture.

<div class="grid cards" markdown>

-   :material-sitemap:{ .lg .middle } **Architecture Patterns**

    ---

    Event sourcing, CQRS, and streaming architectures built on Kafka.

    [:octicons-arrow-right-24: Architecture Patterns](concepts/architecture-patterns/index.md)

-   :material-sync:{ .lg .middle } **Delivery Semantics**

    ---

    At-least-once, at-most-once, and exactly-once delivery guarantees.

    [:octicons-arrow-right-24: Delivery Semantics](concepts/delivery-semantics/index.md)

-   :material-database-export:{ .lg .middle } **Data Integration**

    ---

    Integrating Kafka with external systems using Connect and Streams.

    [:octicons-arrow-right-24: Data Integration](concepts/data-integration/index.md)

-   :material-earth:{ .lg .middle } **Multi-Datacenter**

    ---

    Cross-datacenter replication strategies and disaster recovery.

    [:octicons-arrow-right-24: Multi-Datacenter](concepts/multi-datacenter/index.md)

</div>

---

## Architecture

Deep dive into Kafka's internal architecture and distributed systems design.

<div class="grid cards" markdown>

-   :material-file-tree:{ .lg .middle } **Topics & Partitions**

    ---

    Topics, partitions, partition leaders, ISR, and leader election.

    [:octicons-arrow-right-24: Topics & Partitions](architecture/topics/index.md)

-   :material-server:{ .lg .middle } **Brokers**

    ---

    Broker architecture, request handling, and controller responsibilities.

    [:octicons-arrow-right-24: Broker Architecture](architecture/brokers/index.md)

-   :material-vector-triangle:{ .lg .middle } **Topology**

    ---

    Cluster topology, rack awareness, and network configuration.

    [:octicons-arrow-right-24: Cluster Topology](architecture/topology/index.md)

-   :material-harddisk:{ .lg .middle } **Storage Engine**

    ---

    Log segments, compaction, and retention policies.

    [:octicons-arrow-right-24: Storage Engine](architecture/storage-engine/index.md)

-   :material-content-copy:{ .lg .middle } **Replication**

    ---

    Partition replication, ISR management, and leader election.

    [:octicons-arrow-right-24: Replication](architecture/replication/index.md)

-   :material-shield-check:{ .lg .middle } **Fault Tolerance**

    ---

    Failure detection, recovery mechanisms, and high availability.

    [:octicons-arrow-right-24: Fault Tolerance](architecture/fault-tolerance/index.md)

-   :material-atom:{ .lg .middle } **Transaction Coordinator**

    ---

    Exactly-once semantics, producer IDs, and two-phase commit.

    [:octicons-arrow-right-24: Transactions](architecture/transactions/index.md)

</div>

---

## Producers and Consumers

Configuration and best practices for Kafka clients.

<div class="grid cards" markdown>

-   :material-upload:{ .lg .middle } **Producers**

    ---

    Producer configuration, batching, compression, and delivery guarantees.

    [:octicons-arrow-right-24: Producer Guide](application-development/producers/index.md)

-   :material-download:{ .lg .middle } **Consumers**

    ---

    Consumer groups, offset management, and rebalancing strategies.

    [:octicons-arrow-right-24: Consumer Guide](application-development/consumers/index.md)

</div>

---

## Stream Processing

Build real-time stream processing applications.

<div class="grid cards" markdown>

-   :material-connection:{ .lg .middle } **Kafka Connect**

    ---

    Source and sink connectors for data integration pipelines.

    [:octicons-arrow-right-24: Kafka Connect](kafka-connect/connectors/index.md)

-   :material-chart-timeline-variant:{ .lg .middle } **Kafka Streams**

    ---

    Stream processing DSL for stateful transformations.

    [:octicons-arrow-right-24: Kafka Streams](application-development/kafka-streams/dsl/index.md)

-   :material-file-document-check:{ .lg .middle } **Schema Registry**

    ---

    Schema management for Avro, Protobuf, and JSON Schema.

    [:octicons-arrow-right-24: Schema Registry](schema-registry/schema-formats/index.md)

</div>

---

## Operations

Production deployment, monitoring, and maintenance procedures.

<div class="grid cards" markdown>

-   :material-console:{ .lg .middle } **CLI Tools**

    ---

    Command-line tools for cluster administration and troubleshooting.

    [:octicons-arrow-right-24: CLI Reference](operations/cli-tools/index.md)

-   :material-cog:{ .lg .middle } **Configuration**

    ---

    Broker, producer, and consumer configuration reference.

    [:octicons-arrow-right-24: Configuration Guide](operations/configuration/index.md)

-   :material-chart-line:{ .lg .middle } **Monitoring**

    ---

    JMX metrics, health checks, and alerting strategies.

    [:octicons-arrow-right-24: Monitoring Guide](operations/monitoring/index.md)

-   :material-backup-restore:{ .lg .middle } **Backup & Restore**

    ---

    Data backup strategies and disaster recovery procedures.

    [:octicons-arrow-right-24: Backup & Restore](operations/backup-restore/index.md)

-   :material-wrench:{ .lg .middle } **Maintenance**

    ---

    Rolling upgrades, partition reassignment, and cluster expansion.

    [:octicons-arrow-right-24: Maintenance](operations/maintenance/index.md)

-   :material-speedometer:{ .lg .middle } **Performance Tuning**

    ---

    Throughput optimization, latency tuning, and capacity planning.

    [:octicons-arrow-right-24: Performance](operations/performance/capacity-planning/index.md)

</div>

---

## Security

Authentication, authorization, and encryption for Kafka deployments.

<div class="grid cards" markdown>

-   :material-account-key:{ .lg .middle } **Authentication**

    ---

    SASL/SCRAM, SASL/GSSAPI (Kerberos), and mTLS authentication.

    [:octicons-arrow-right-24: Authentication](security/authentication/index.md)

-   :material-shield-lock:{ .lg .middle } **Authorization**

    ---

    ACL-based authorization and role-based access control.

    [:octicons-arrow-right-24: Authorization](security/authorization/index.md)

-   :material-lock:{ .lg .middle } **Encryption**

    ---

    TLS/SSL encryption for data in transit.

    [:octicons-arrow-right-24: Encryption](security/encryption/index.md)

</div>

---

## Cloud Deployments

Deploy Kafka on cloud platforms and container orchestration systems.

<div class="grid cards" markdown>

-   :fontawesome-brands-aws:{ .lg .middle } **AWS**

    ---

    Amazon MSK and self-managed Kafka on EC2.

    [:octicons-arrow-right-24: AWS Deployment](cloud/aws/index.md)

-   :fontawesome-brands-microsoft:{ .lg .middle } **Azure**

    ---

    Azure Event Hubs for Kafka and AKS deployments.

    [:octicons-arrow-right-24: Azure Deployment](cloud/azure/index.md)

-   :fontawesome-brands-google:{ .lg .middle } **Google Cloud**

    ---

    Self-managed Kafka on GKE and Compute Engine.

    [:octicons-arrow-right-24: GCP Deployment](cloud/gcp/index.md)

-   :material-kubernetes:{ .lg .middle } **Kubernetes**

    ---

    Strimzi operator and StatefulSet deployments.

    [:octicons-arrow-right-24: Kubernetes](cloud/kubernetes/index.md)

</div>

---

## Troubleshooting

Diagnostic procedures and solutions for common issues.

<div class="grid cards" markdown>

-   :material-alert-circle:{ .lg .middle } **Common Errors**

    ---

    Error codes, root causes, and resolution procedures.

    [:octicons-arrow-right-24: Error Reference](troubleshooting/common-errors/index.md)

-   :material-stethoscope:{ .lg .middle } **Diagnosis**

    ---

    Diagnostic procedures for cluster issues.

    [:octicons-arrow-right-24: Diagnosis Guide](troubleshooting/diagnosis/index.md)

-   :material-file-search:{ .lg .middle } **Log Analysis**

    ---

    Log patterns, analysis techniques, and monitoring.

    [:octicons-arrow-right-24: Log Analysis](troubleshooting/log-analysis/index.md)

</div>

---

## Quick Reference

<div class="grid cards" markdown>

-   :material-book-open-variant:{ .lg .middle } **Reference**

    ---

    Configuration reference, CLI commands, and metrics catalog.

    [:octicons-arrow-right-24: Quick Reference](reference/index.md)

-   :material-swap-horizontal:{ .lg .middle } **Migration**

    ---

    ZooKeeper to KRaft migration and version upgrade guides.

    [:octicons-arrow-right-24: Migration Guide](migration/index.md)

</div>

---

## Version Compatibility

This documentation follows Apache Kafka's semantic versioning. Behavioral differences between versions are explicitly noted throughout.

### KRaft Migration Timeline

| Milestone | Version | Date | Status |
|-----------|---------|------|--------|
| KRaft Early Access | 2.8.0 | April 2021 | Development only |
| KRaft Preview | 3.0.0 - 3.2.x | Sept 2021 - May 2022 | Testing environments |
| KRaft Production Ready | 3.3.0 | October 2022 | General availability |
| ZooKeeper Deprecated | 3.6.0 | October 2023 | Migration recommended |
| Dynamic KRaft Quorum | 3.9.0 | November 2024 | Add/remove controllers |
| **ZooKeeper Removed** | **4.0.0** | **March 2025** | **KRaft required** |
| Current Release | 4.1.1 | November 2025 | Latest stable |

!!! warning "Kafka 4.0+ Migration Path"
    Kafka 4.0 does not support ZooKeeper mode. To upgrade:

    1. If on Kafka < 3.3: Upgrade to 3.9.x first
    2. Migrate from ZooKeeper to KRaft mode
    3. Then upgrade to Kafka 4.0+

    Direct upgrade from ZooKeeper mode to 4.0 is not possible.

!!! note "Documentation Conventions"
    This documentation uses RFC 2119 terminology (must, should, may) to indicate requirement levels. Version-specific behaviors are explicitly noted with the applicable Kafka version range.

---

## Related Resources

- [Apache Kafka Official Documentation](https://kafka.apache.org/documentation/)
- [Kafka Improvement Proposals (KIPs)](https://cwiki.apache.org/confluence/display/KAFKA/Kafka+Improvement+Proposals)
- [AxonOps Kafka Monitoring](../index.md) - Monitor Kafka clusters with AxonOps
