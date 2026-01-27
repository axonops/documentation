---
title: "Kafka Topics"
description: "Kafka topic management in AxonOps. Monitor and manage topics across clusters."
meta:
  - name: keywords
    content: "Kafka topics, topic management, AxonOps Kafka"
---

# Kafka Topics

## What is a topic?

A Kafka topic is a core concept in Apache Kafka, serving as a logical channel or category where data streams are organized and managed. Producers write (publish) messages to topics, and consumers read (subscribe) to messages from topics. Topics decouple producers from consumers, enabling scalable and real-time data pipelines.

- Naming: Topics are named to reflect the data they contain, such as temperature_readings or user_activity.

- Decoupling: Producers and consumers operate independently, using the topic as an intermediary.

- Retention: Kafka retains messages in a topic for a configurable period (default is 7 days), regardless of whether they have been consumed.

- Partitions: Each topic is split into one or more partitions. Partitions allow Kafka to scale horizontally and enable parallel processing. Each partition is an ordered, immutable sequence of records, and each record within a partition has a unique offset.

- Replication: Partitions are replicated across multiple brokers for fault tolerance. Each partition has a leader (handles reads/writes) and followers (replicate data for redundancy).

## Topic Overview

In the topic overview page you can get a holistic view of all the topics in your Kafka cluster.

**Click Topics in the left navigation to open the overview page.**

<img src="../topic_click.png" width="700" alt="Topic navigation item">

On the overview page, interact with topic information including Topics, Partitions, ISR (In-Sync Replicas), Alerts, Counters, Sizes, and topic actions such as:

- Edit Topic: :material-pencil:{ .edit_config }
- Clone Topic: :material-content-copy:{ .copy_config }
- Delete Topic: :material-trash-can:{ .delete_config }

<img src="../topic_overview.png" width="700" alt="Topic overview page">

### Selected Topic Information

<img src="../topic_configuration.png" width="700" alt="Selected topic details panel">

Once a topic has been selected, the following information is displayed:

| Detail | Description |
| --- | --- |
| Configuration | Kafka topic configuration options. See [topic configuration](configure_topic.md#topic-configuration). |
| Partitions | Partition ID, brokers where each partition resides, and offsets. |
| Consumers | Current list of consumers that are consuming from the topic. |
| ACLs | Current ACLs applied to the topic. See [Kafka ACL overview](../acl/overview.md). |
