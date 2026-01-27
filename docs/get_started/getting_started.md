---
title: "Getting Started"
description: "Getting started with AxonOps self-hosted deployment. Installation overview and requirements."
meta:
  - name: keywords
    content: "AxonOps getting started, self-hosted, installation overview"
---

# Getting Started

Installing AxonOps Unified Monitoring on your own premises as a self-managed cluster gives you full control over every aspect of your AxonOps deployment.

AxonOps components run on a wide array of operating systems including (but not limited to):

- Ubuntu
- Debian
- Red Hat Enterprise Linux (RHEL)
- Amazon Linux


AxonOps Unified Monitoring consists of 4 main components:

- axon-server
    - Backend that collects cluster information and interacts with your clusters.
- axon-dash
    - Web UI to display and interact with your clusters.
- AxonOps agent
    - called from within the JVM to send metrics to axon-server.
- storage engine
    - stores metrics, logs, configurations, and metadata about your cluster.


Below are the steps to install and configure an on-premises AxonOps Unified Monitoring installation.

### Set up Storage Engine

Elasticsearch is always required and the default data storage for all Cassandra and Kafka metrics as well as application logs, AxonOps configuration and metrics metadata. 

You can choose to use Cassandra as a metrics store instead of Elasticsearch for better performance when monitoring larger numbers of nodes.

Elasticsearch is still required in conjunction with the dedicated AxonOps Cassandra cluster. 

#### Elasticsearch (Required)

AxonOps is currently compatible with Elasticsearch 7.x and 8.x.

We recommend [installing the latest available Elasticsearch release](../installation/elasticsearch/install.md).

#### Cassandra (Optional)

For more information please read more on setting up [Cassandra as a Metrics Database](../installation/axon-server/metricsdatabase.md).

### Set up AxonOps Server

[Install and configure AxonOps Server (`axon-server`)](../installation/axon-server/axonserver_install.md).

### Set up AxonOps Dashboard

[Install and configure AxonOps Dashboard (`axon-dash`)](../installation/axon-dash/install.md).

### Set up AxonOps Agent

[Install and configure AxonOps Agent (`AxonOps agent`) for Cassandra or Kafka](../installation/agent/install.md).

## Alternative Installation Options

Below are different options for on-premise installations of the AxonOps platform,
depending on your environment and preferences.
 
### Docker or Podman
  
For quick evaluations or smaller clusters, our Docker and Podman Compose setup is the fastest way to get everything running.

Instructions and files can be found [here](https://github.com/axonops/axonops-server-compose).

### Ansible

For an automated and repeatable approach, the Ansible collection can install both the
AxonOps Server and Agents across Cassandra or Kafka clusters.

Instructions and files can be found [here](https://github.com/axonops/axonops-ansible-collection).

### Kubernetes

For deployments into Kubernetes environments, a Helm chart is available.

Instructions and files can be found [here](https://github.com/axonops/axonops-containers/tree/development/axonops/charts).

### Offline Installations

If you need to download packages for offline installation due to security requirements, you can use our package downloader script.

Instructions and files can be found [here](https://github.com/axonops/axonops-installer-packages-downloader).

## Configuration Automation

To easily set up alerts, dashboards, backups, integrations, and other configurations,
use this repository of Ansible playbooks to automate AxonOps configuration.

Instructions and files can be found [here](https://github.com/axonops/axonops-config-automation).
