# AxonOps Cassandra agent installation

This agent will enable metrics, logs and events collection with adaptive repairs and backups for Cassandra.

See [Installing axon-agent for Cassandra in Docker](./docker.md) if you are running Cassandra under Docker.

## Available versions

* Apache Cassandra 4.1.x
* Apache Cassandra 4.0.x
* Apache Cassandra 3.11.x
* Apache Cassandra 3.0.x


## Step 1 - Installation

> Make sure that the `{version}` of your Cassandra and Cassandra agent are compatible from the [compatibility matrix](../../compat_matrix/compat_matrix). 

### Select the OS Family. 
<label>
  <input type="radio" name="osFamily" value="/installation-starter/cassandra-agent/install/#__tabbed_1_1" onChange="updateOS()">
  <img src="/get_started/debian.png" class="skip-lightbox" width="180px">
</label>
<label>
  <input type="radio" name="osFamily" value="/installation-starter/cassandra-agent/install/#__tabbed_1_2" onChange="updateOS()">
  <img src="/get_started/red_hat.png" class="skip-lightbox" width="180px">
</label>

===+ "Debian / Ubuntu"
    ``` bash
    sudo apt-get update
    sudo apt-get install -y curl gnupg ca-certificates
    curl -L https://packages.axonops.com/apt/repo-signing-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/axonops.gpg
    echo "deb [arch=arm64,amd64 signed-by=/usr/share/keyrings/axonops.gpg] https://packages.axonops.com/apt axonops-apt main" | sudo tee /etc/apt/sources.list.d/axonops-apt.list
    sudo apt-get update
    sudo apt-get install axon-cassandra{version}-agent
    ```
=== "RedHat / CentOS"
    ``` bash
    sudo tee /etc/yum.repos.d/axonops-yum.repo << EOL
    [axonops-yum]
    name=axonops-yum
    baseurl=https://packages.axonops.com/yum/
    enabled=1
    repo_gpgcheck=0
    gpgcheck=0
    EOL

    sudo yum install axon-cassandra{version}-agent
    ```

> Note: This will install the AxonOps Cassandra agent and its dependency: **axon-agent**


## Step 2 - Agent Configuration

Update the following highlighted lines from `/etc/axonops/axon-agent.yml`:
When setting up SSL/TLS on the AxonOps Server the agents need to be able to connect 

``` yaml hl_lines="2 6"
axon-server:
    hosts: "axon-server_endpoint" # Your axon-server IP or hostname, e.g. axonops.mycompany.com
    port: 1888 # The default axon-server port is 1888

axon-agent:
    org: "my-company" # Your organisation name
    # SSL/TLS Settings from AxonOps Agent to AxonOps Server
    tls:
        mode: "disabled" # disabled, TLS

NTP:
    host: "ntp.mycompany.com" # Your NTP server IP address or hostname 
```

## Step 3 - Configure Cassandra 
Edit `cassandra-env.sh`, which is usually located in `/<Cassandra Installation Directory>/conf/cassandra-env.sh` for
tarball installs or `/etc/cassandra/cassandra-env.sh` for package installs,
and append the following line at the end of the file:

``` bash 
JVM_OPTS="$JVM_OPTS -javaagent:/usr/share/axonops/axon-cassandra{version}-agent.jar=/etc/axonops/axon-agent.yml"
```

> for example with Cassandra agent version *3.11*:
``` bash
JVM_OPTS="$JVM_OPTS -javaagent:/usr/share/axonops/axon-cassandra3.11-agent.jar=/etc/axonops/axon-agent.yml"
```
> Make sure that this configuration will not get overridden by an automation tool.

## Step 4 - Add axonops user to Cassandra user group and Cassandra user to axonops group

``` bash
sudo usermod -aG <your_cassandra_group> axonops
sudo usermod -aG axonops <your_cassandra_user>
```

## Step 5 - Start Cassandra


## Step 6 - Start axon-agent
``` bash
sudo systemctl start axon-agent
```


## (Optional) Step 7 - Cassandra Remote Backups or Restore Prerequisites

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
