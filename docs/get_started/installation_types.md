# On-premises installation options

The different options for setting up the AxonOps platform on-premises, depending on your environment and preferences:
 
## Docker or Podman: 
  
For quick evaluations or smaller clusters, our Docker and Podman Compose setup is the fastest way to get everything running.

Instructions and files at [AxonOps Docker/Podman Compose:](https://github.com/axonops/axonops-server-compose)

## Ansible: 

A more automated and repeatable approach,the Ansible collection can install both the AxonOps server and agents across your Cassandra or Kafka nodes.

Instructions and files at [AxonOps Ansible Collection:](https://github.com/axonops/axonops-ansible-collection)

## Kubernetes: 

For deployments into Kubernetes environments, a Helm chart is available.

Instructions and files at [AxonOps Helm Chart:](https://github.com/axonops/helm-axonops)

## Offline Installations: 

If you need to download packages for offline installation due to security requirements, you can use our package downloader script.

Instructions and files at [AxonOps Offline Script:](https://github.com/axonops/axonops-installer-packages-downloader)

## Configuration Automation: 

A repository of ansible playbooks that automate AxonOps configuration.

Easily setup alerts, dashboards, backups, integrations and other configurations.

Instructions and files at [AxonOps Config Automation:](https://github.com/axonops/axonops-config-automation)