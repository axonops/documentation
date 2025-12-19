---
title: "Kafka KRaft Mode"
description: "Apache Kafka KRaft architecture. Raft consensus, controller quorum, metadata log, and migration from ZooKeeper."
meta:
  - name: keywords
    content: "KRaft, Kafka Raft, Kafka without ZooKeeper, KRaft controller, Kafka metadata quorum"
---

# Kafka KRaft Mode

This page has moved to [KRaft: Kafka Raft Consensus](../kraft/index.md).

The KRaft documentation covers:

- [Why KRaft Replaced ZooKeeper](../kraft/index.md#why-kraft-replaced-zookeeper) — Architectural benefits
- [Raft Consensus Protocol](../kraft/index.md#raft-consensus-protocol) — Leader election, log replication
- [Metadata Log](../kraft/index.md#metadata-log) — `__cluster_metadata` topic structure
- [Controller Communication](../kraft/index.md#controller-communication) — Controller-to-broker protocols
- [Quorum Configuration](../kraft/index.md#quorum-configuration) — Combined vs isolated mode
- [Failover Behavior](../kraft/index.md#failover-behavior) — Controller and broker failure handling
- [Migration from ZooKeeper](../kraft/index.md#migration-from-zookeeper) — Step-by-step migration guide

For broker-specific configuration and operations, see [Brokers Overview](index.md).
