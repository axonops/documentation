---
title: "AxonOps Agent Installation"
hide:
  - toc
search:
  boost: 5
---

# AxonOps Agent Installation

The AxonOps Agent enables collection of:

* Metrics
* Logs
* Events

The AxonOps Agent also enables the following maintence operations to be performed on the cluster:

* Adaptive repairs
* Backups

See [Installing axon-agent for Cassandra in Docker](./docker.md) if you are running Cassandra under Docker and the [Kubernetes](../kubernetes/index.md) if you are setting up either Strimzi or K8ssandra clusters.

## Version Compatibility

AxonOps Agent is available for the following versions of Apache Casssandra and Apache Kafka:

### Cassandra

* Apache Cassandra 3.0.x
* Apache Cassandra 3.11.x
* Apache Cassandra 4.0.x
* Apache Cassandra 4.1.x
* Apache Cassandra 5.0.x

### Kafka

* Apache Kafa 2.x
* Apache Kafa 3.x


## Setup the Package Repository

{!dynamic_pages/axon_agent/os.md!}

### Select Service to Configure

<label>
  <input type="radio" id="Cassandra" name="Service" onChange="updateService()" checked=true />
  <img src="/get_started/cassandra.png" class="skip-lightbox" width="180px" height="180px">
</label>
<label>
  <input type="radio" id="Kafka" name="Service" onChange="updateService()" />
  <img src="/get_started/kafka.png" class="skip-lightbox" width="180px" height="180px">
</label>

<div id="CassandraDiv" name="service_div" markdown="1">

{!installation/agent/agent_setup_cassandra.md!}

</div>

<div id="KafkaDiv" name="service_div" style="display:none" markdown="1">

{!installation/agent/agent_setup_kafka.md!}

</div>

## Start the AxonOps Agent

``` bash
{!installation/axon-agent/scripts/restart-axon-agent.sh!}
```
