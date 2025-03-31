# Installing axon-agent for Cassandra in Docker

!!! info "Caveats"
      - Cassandra logs cannot normally be collected by AxonOps as they are sent to stdout and handled by the
        Docker logging driver
      - If axon-agent is running under Docker it assumes that the Cassandra user's GID is 999 as it is in the
        official Cassandra images. If this is not the case then AxonOps may not be able to backup the Cassandra data.

To enable the full functionality of the AxonOps agent some directories must be accessible to both the Cassandra and
AxonOps Agent processes.

| Directory            | Required | Description                                                                                                                                                                           |
|----------------------|----------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `/var/lib/axonops`   | Required | Contains UNIX domain sockets, Cassandra agent jars and local data stored by the agent. This directory must be readable and writable by Cassandra and AxonOps                          |
| `/etc/axonops`       | Required | Contains the configuration for AxonOps. This directory must be readable by Cassandra and AxonOps                                                                                      |                                                                             |
| `/var/log/axonops`   | Required | The Cassandra agent will write logs to this directory where they will be buffered and sent to the AxonOps server This directory must be writable by Cassandra and readable by AxonOps |
| `/var/lib/cassandra` | Optional | For the backups feature to function correctly the Cassandra data directory must be readable by the AxonOps agent                                                                      |

When running Cassandra under Docker it is possible to run the AxonOps agent either on the host or in another 
Docker container. When installing on the host follow the instructions under
[AxonOps Cassandra agent installation](install.md) to install the agent and ensure that the appropriate directories are
mapped into the Cassandra container.

## Example with Docker Compose

This example shows running a single Cassandra node and the AxonOps agent under Docker Compose using host volumes
to share data between the containers.

```yaml
version: "3"

services:
  cassandra:
    image: cassandra:4.0
    container_name: cassandra
    restart: always
    volumes:
      - ./cassandra:/var/lib/cassandra
      - ./axonops/var:/var/lib/axonops
      - ./axonops/etc:/etc/axonops
      - ./axonops/log:/var/log/axonops
    ports:
      - "9042:9042"
    environment:
      - JVM_EXTRA_OPTS=-javaagent:/var/lib/axonops/axon-cassandra4.0-agent.jar=/etc/axonops/axon-agent.yml
      - CASSANDRA_CLUSTER_NAME=my-cluster

  axon-agent:
    image: registry.axonops.com/axonops-public/axonops-docker/axon-agent:latest
    restart: always
    environment:
      # Enter the hostname or IP address of your AxonOps server here
      - AXON_AGENT_SERVER_HOST=axonops-server.example.com
    volumes:
      - ./cassandra:/var/lib/cassandra
      - ./axonops/var:/var/lib/axonops
      - ./axonops/etc:/etc/axonops
      - ./axonops/log:/var/log/axonops
```
