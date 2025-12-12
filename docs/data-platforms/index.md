---
description: "AxonOps supported data platforms. Cassandra and Kafka monitoring overview."
meta:
  - name: keywords
    content: "data platforms, AxonOps platforms, Cassandra, Kafka"
---

# Data Platforms Documentation

This documentation provides comprehensive guides and references for distributed data platforms. Whether operating existing clusters or evaluating new deployments, these resources cover architecture, configuration, operations, and best practices.

## Apache Cassandra

Apache Cassandra is a distributed NoSQL database designed for scalability and high availability. It handles large volumes of data across commodity hardware while providing continuous availability with no single point of failure.

**Key Characteristics:**

- Masterless architecture with peer-to-peer replication
- Linear horizontal scalability
- Tunable consistency levels per operation
- Multi-datacenter replication built in
- Optimized for write-heavy workloads

[View Apache Cassandra Documentation](../cassandra/index.md)

---

## Apache Kafka

Apache Kafka is a distributed event streaming platform capable of handling trillions of events per day. It provides high-throughput, fault-tolerant messaging with strong ordering guarantees.

**Key Characteristics:**

- Distributed commit log architecture
- High-throughput publish-subscribe messaging
- Durable message storage with configurable retention
- Stream processing capabilities
- Horizontal scalability through partitioning

[View Apache Kafka Documentation](../kafka/index.md)

---

## Choosing a Platform

| Use Case | Recommended Platform |
|----------|---------------------|
| High-volume data storage with flexible queries | Apache Cassandra |
| Real-time event streaming and messaging | Apache Kafka |
| Time-series data with high write throughput | Apache Cassandra |
| Event sourcing and log aggregation | Apache Kafka |
| Multi-datacenter data replication | Both |

---

## About This Documentation

This documentation is maintained by [AxonOps](https://axonops.com), providing monitoring, maintenance, and operational tools for distributed data platforms.

### Related Resources

- [AxonOps Platform](https://axonops.com) - Monitoring and management for Cassandra and Kafka
- [Apache Cassandra Official Site](https://cassandra.apache.org/)
- [Apache Kafka Official Site](https://kafka.apache.org/)
