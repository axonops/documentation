# Getting Started

Installing AxonOps Unified Monitoring on your own premises as a self-managed cluster gives you full control over every aspect of you AxonOps deployment.

AxonOps components run on a wide array of operating systems including (but not limited to):

- Ubuntu
- Debian
- RedHat Enterprise Linux (RHEL)
- Amazon Linux


AxonOps Unified Monitoring consists of 4 main components:

- axon-server
- axon-dash
- axon-agent
- storage engine


## Please follow the following steps to get your on-premise AxonOps Unified Monitoring installed and configured: 

### Step 1 : Storage Engine

Elasticsearch is always required and the default data storage for all Cassandra and Kafka metrics as well as application logs, AxonOps configuration and metrics metadata. 

You can choose to use Cassandra as a metrics store instead of Elasticsearch for better performance when monitoring larger numbers of nodes.

Elasticsearch is still required in conjunction with the dedicated AxonOps Cassandra cluster. 

#### Elasticsearch (Required)

AxonOps is currently compatible with Elasticsearch 7.x and 8.x.

We recommend installing the latest available release.

[Install Elasticsearch](/installation/elasticsearch/install/)

#### Cassandra (Optional)

For more information please read more on setting up [Cassandra as a Metrics Database](/installation/axon-server/metricsdatabase/)

### Step 2 : Install and configure axon-server.

[Install and configure axon-server](/installation/axon-server/axonserver_install/) 

### Step 3 : Install and configure axon-dash 

[Install and configure axon-dash](/installation/axon-dash/install/) 

### Step 4 : Install and configure axon-agent for Cassandra or Kafka

[Install and configure axon-agent for Cassandra or Kafka](/installation/agent/install/) 

## Alternative installation options: 

The different options for setting up the AxonOps platform on-premises, depending on your environment and preferences:
 
### Docker or Podman: 
  
For quick evaluations or smaller clusters, our Docker and Podman Compose setup is the fastest way to get everything running.

Instructions and files at [AxonOps Docker/Podman Compose:](https://github.com/axonops/axonops-server-compose)

### Ansible: 

A more automated and repeatable approach,the Ansible collection can install both the AxonOps server and agents across your Cassandra or Kafka nodes.

Instructions and files at [AxonOps Ansible Collection:](https://github.com/axonops/axonops-ansible-collection)

### Kubernetes: 

For deployments into Kubernetes environments, a Helm chart is available.

Instructions and files at [AxonOps Helm Chart:](https://github.com/axonops/helm-axonops)

### Offline Installations: 

If you need to download packages for offline installation due to security requirements, you can use our package downloader script.

Instructions and files at [AxonOps Offline Script:](https://github.com/axonops/axonops-installer-packages-downloader)

## Configuration Automation: 

A repository of ansible playbooks that automate AxonOps configuration.

Easily setup alerts, dashboards, backups, integrations and other configurations.

Instructions and files at [AxonOps Config Automation:](https://github.com/axonops/axonops-config-automation)