# AxonOps Cassandra agent installation

This agent will enable metrics, logs and events collection with adaptive repairs and backups for Cassandra.

See [Installing axon-agent for Cassandra in Docker](docker.md) if you are running Cassandra under Docker.

## AxonOps Agent is a available for the followig versions of Apache Casssandra

* Apache Cassandra 3.0.x
* Apache Cassandra 3.11.x
* Apache Cassandra 4.0.x
* Apache Cassandra 4.1.x
* Apache Cassandra 5.0.x


## Step 1 - Setup the AxonOps repository and install AxonOps Agent

{!dynamic_pages/axon_agent/os.md!}

## Step 2 - Install Cassandra Agent

{!dynamic_pages/axon_agent/cassandra.md!}

> Note: This will install the AxonOps Cassandra agent and its dependency: **axon-agent**

## Step 3 - Agent Configuration

Update the following highlighted lines from `/etc/axonops/axon-agent.yml`:

If you have enabled SSL/TLS on the AxonOps Server the agents need to have the same SSL/TLS config to be able to connect.

``` yaml hl_lines="2 6"
axon-server:
    hosts: "axon-server_endpoint" # Your axon-server IP or hostname, e.g. axonops.mycompany.com
    port: 1888 # The default axon-server port is 1888

axon-agent:
    org: "my-company" # Your organisation name
    # SSL/TLS Settings from AxonOps Agent to AxonOps Server
    tls:
        mode: "disabled" # disabled, TLS
        # Only set below if mode is TLS
        skipVerify: false # Disables CA and Hostname verification
        caFile: "path_to_certs_on_axon_agent_node.crt" # required if skipVerify is not set and you are using a self-signed cert
        certFile: "path_to_certs_on_axon_agent_node.crt"
        keyFile: "path_to_key_file_on_axon_agent_node.key"
    disable_auto_update: true

NTP:
    host: "ntp.mycompany.com" # Your NTP server IP address or hostname 
```

## Step 4 - Configure Cassandra

{!dynamic_pages/axon_agent/java.md!}

> **NB.** Make sure that this configuration will not get overridden by an automation tool.

## Step 5 - Add axonops user to Cassandra user group and Cassandra user to axonops group

``` bash
sudo usermod -aG <your_cassandra_group> axonops
sudo usermod -aG axonops <your_cassandra_user>
```

## Step 6 - Start/Restart Cassandra

To load the Axon java agent and Cassandra config changes please,

- Start the Cassandra service if stopped.
- Restart the Cassandra service if already running.

## Step 7 - Start axon-agent
``` bash
sudo systemctl start axon-agent
```

## (Optional) Step 8 - Cassandra Remote Backups or Restore Prerequisites

* If you plan to use AxonOps remote backup functionality, **axonops** user will require **read** access on Cassandra **data** folder.

* As well if you plan to Restore data with AxonOps,  **axonops** user will require **write** access to Cassandra **data** folder. We recommend to only provide temporary write access to **axonops** when required.


#### Cassandra agent Package details

* Configuration: `/etc/axonops/axon-agent.yml`
* Binary: `/usr/share/axonops/axon-cassandra{version}-agent.jar`
* Version number: `/usr/share/axonops/axon-cassandra{version}-agent.version`
* Copyright : `/usr/share/doc/axonops/axon-cassandra{version}-agent/copyright`
* Licenses : `/usr/share/axonops/licenses/axon-cassandra{version}-agent/`

#### axon-agent Package details (dependency of Cassandra agent)

* Configuration: `/etc/axonops/axon-agent.yml`
* Binary: `usr/share/axonops/axon-agent`
* Logs : `/var/log/axonops/axon-agent.log`
* Systemd service: `/usr/lib/systemd/system/axon-agent.service`
