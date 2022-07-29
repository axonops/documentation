# AxonOps Cassandra agent installation

This agent will enable metrics, logs and events collection with adaptive repairs and backups for Cassandra.

## Available versions
* Apache Cassandra 3.0.x
* Apache Cassandra 3.11.x


## Step 1 - Installation

> Make sure that the `{version}` of your Cassandra and Cassandra agent are compatible from the [compatibility matrix](../../compat_matrix/compat_matrix). 


#### CentOS / RedHat
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
#### Debian / Ubuntu
``` bash
apt-get install curl gnupg
curl https://packages.axonops.com/apt/repo-signing-key.gpg | sudo apt-key add -
echo "deb https://packages.axonops.com/apt axonops-apt main" | sudo tee /etc/apt/sources.list.d/axonops-apt.list
sudo apt-get update

sudo apt-get install axon-cassandra{version}-agent
```
> Note: This will install AxonOps Cassandra agent and its dependency: axon-agent


## Step 2 - Agent Configuration

Update the following highlighted lines from `/etc/axonops/axon-agent.yml`:

``` yaml hl_lines="2 5 8"
axon-server:
    hosts: "axon-server_endpoint" # Specify axon-server IP axon-server.mycompany.com

axon-agent:
    org: "my-company-test" # Specify your organisation name

NTP:
    host: "ntp.mycompany.com" # Specify your NTP server IP address or hostname

cassandra:
  tier0: # metrics collected every 5 seconds
      metrics:
          jvm_:
            - "java.lang:*"
          cas_:
            - "org.apache.cassandra.metrics:*"
            - "org.apache.cassandra.net:type=FailureDetector"

  tier1:
      frequency: 300 # metrics collected every 300 seconds (5m)
      metrics:
          cas_:
            - "org.apache.cassandra.metrics:name=EstimatedPartitionCount,*"

  #tier2:
  #    frequency: 3600 # 1h

  #tier3:
  #    frequency: 86400 # 1d

  blacklist: # You can blacklist metrics based on MBean query pattern (regular expression)
    - "org.apache.cassandra.metrics:type=ColumnFamily.*" # duplication of table metrics
    - "org.apache.cassandra.metrics:name=SnapshotsSize.*" # Collecting SnapshotsSize metrics slows down collection

  free_text_blacklist: # You can blacklist metrics based on Regex pattern
    - "org.apache.cassandra.metrics:type=ThreadPools,path=internal,scope=Repair#.*"

  warningThresholdMillis: 100 # This will warn in logs when a MBean takes longer than the specified value.

  logFormat: "%4$s %1$tY-%1$tm-%1$td %1$tH:%1$tM:%1$tS,%1$tL %5$s%6$s%n"
```

> Note: the log format will only be used by AxonOps Cassandra agent

## Step 3 - Configure Cassandra 
Edit `cassandra-env.sh` usually located in your Cassandra install path such as `/<Cassandra Installation Directory>/conf/cassandra-env.sh` and append the following line at the end of the file:

``` bash 
JVM_OPTS="$JVM_OPTS -javaagent:/usr/share/axonops/axon-cassandra{version}-agent.jar=/etc/axonops/axon-agent.yml"
```

>example with Cassandra agent version *3.11*:
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
sudo service axon-agent start
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
