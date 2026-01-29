---
title: "AxonOps Agent Installation"
hide:
  - toc
---

# AxonOps Agent Installation

The AxonOps Agent enables collection of:

* Metrics
* Logs
* Events

The AxonOps Agent also enables the following maintenance operations to be performed on the cluster:

* Adaptive repairs
* Backups

See [Installing AxonOps agent for Cassandra in Docker](./docker.md) if you are running Cassandra under Docker, and the [Kubernetes guide](../kubernetes/index.md) if you are setting up Strimzi or K8ssandra clusters.

## Version Compatibility

AxonOps Agent is available for the following versions of Apache Cassandra and Apache Kafka:

### Cassandra

* Apache Cassandra 3.0.x
* Apache Cassandra 3.11.x
* Apache Cassandra 4.0.x
* Apache Cassandra 4.1.x
* Apache Cassandra 5.0.x

### Kafka

* Apache Kafka 2.x
* Apache Kafka 3.x


## Set up the package repository

{!dynamic_pages/axon_agent/os.md!}

### Select Service to Configure

<label>
  <input type="radio" id="Cassandra" name="Service" onChange="updateService()" checked=true />
  <img src="/get_started/cassandra.png" class="skip-lightbox" width="180px" height="180px" alt="cassandra">
</label>
<label>
  <input type="radio" id="Kafka" name="Service" onChange="updateService()" />
  <img src="/get_started/kafka.png" class="skip-lightbox" width="180px" height="180px" alt="kafka">
</label>

<div id="CassandraDiv" name="service_div" markdown="1">

{!installation/agent/agent_setup_cassandra.md!}

</div>

<div id="KafkaDiv" name="service_div" style="display:none" markdown="1">

{!installation/agent/agent_setup_kafka.md!}

</div>

## Start the AxonOps Agent

```bash
{!installation/axon-agent/scripts/restart-axon-agent.sh!}
```
