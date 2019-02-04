# axon-java-agent for Cassandra installation

This agent will enable metrics collection from Cassandra and enable adaptive repairs and backups.

## Available versions
* 3.11.3

## Prerequisites

Cassandra agent needs **axon-agent** to be installed and configured properly. If not installed already, please go to [axon-agent](../../axon-agent/install) installation 
page.

#### Setup axon-agent for Cassandra

You'll need the specify/update the following lines from **axon-agent.yml** located in `/etc/axonops/axon-agent.yml`:



``` yaml hl_lines="2 7 8 9 10 11"
axon-server:
    hosts: "axon-server_endpoint" # Specify axon-server endpoint

axon-agent:
    host: 0.0.0.0 # axon-agent listening address for it's OpenTSDB endpoint
    port: 9916 # axon-agent listening port for it's OpenTSDB endpoint
    org: "your_organisation_name" # Specify your organisation name
    standalone_mode: false
    type: "cassandra"
    #cluster_name: "standalone" # comment that line
    ssl: false # SSL flag for it's OpenTSDB endpoint
```
* Set `standalone_mode` to **false**
* Set `type` to **cassandra**
* Don't forget to comment or remove the `cluster_name` as it will be deduced from DSE configuration.
* Don't forget to specify **axon-server** host and port if that's not already specified.

## Cassandra agent installation

> Make sure the `<version>` of your Cassandra and Cassandra agent are compatible from the [compatibility matrix](../../compat_matrix/compat_matrix). 


#### CentOS / RedHat installer
``` -
printf '%s\n%s\n%s\n%s\n%s\n%s\n' '[axonops]' 'name=axonops Repository' 'baseurl=https://repo.digitalis.io/repository/axonops-yum/stable/x64/' 'enabled=1' 'gpgcheck=1' | sudo tee /etc/yum.repos.d/axonops.repo
sudo yum install axon-cassandra<version>-agent
```
#### Debian / Ubuntu installer
``` -
sudo cp /etc/apt/sources.list /etc/apt/sources.list_backup
echo "deb https://repo.digitalis.io/repository/axonops-apt xenial main" | sudo tee /etc/apt/sources.list.d/axonops.list
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 727BDA4A
sudo apt-get update
sudo apt-get install axon-cassandra<version>-agent
```

#### Package details

* Configuration: `/etc/axonops/axon-java-agent.yml`
* Binary: `/usr/share/axonops/axon-cassandra<version>-agent.jar`
* Version number: `/usr/share/axonops/axon-cassandra<version>-agent.version`
* Copyright : `/usr/share/doc/axonops/axon-cassandra<version>-agent/copyright`
* Licenses : `/usr/share/axonops/licenses/axon-cassandra<version>-agent/`

#### Configure Cassandra 

Edit `cassandra-env.sh` usually located in your Cassandra install path such as `/<path_to_Cassandra>/conf/cassandra-env.sh` and add at the end of the file the following line:

``` bash 
JVM_OPTS="$JVM_OPTS -javaagent:/usr/share/axonops/axon-cassandra<version>-agent.jar=/etc/axonops/axon-java-agent.yml"
```


exemple:
``` bash
JVM_OPTS="$JVM_OPTS -javaagent:/usr/share/axonops/axon-cassandra3.11.3-agent.jar=/etc/axonops/axon-java-agent.yml"
```
#### Add axonops user to Cassandra user group and Cassandra user to axonops group

``` bash
usermod -aG <your_cassandra_group> axonops
usermod -aG axonops <your_cassandra_user>
```

#### Start Cassandra

All you need to do now is start Cassandra.


#### Configuration defaults

``` yaml
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

blacklist: # You can blacklist metrics based on MBean query pattern
  - "org.apache.cassandra.metrics:type=ColumnFamily,*" # dup of tables
  - "org.apache.cassandra.metrics:name=SnapshotsSize,*" # generally takes time

free_text_blacklist: # You can blacklist metrics based on Regex pattern
  - "org.apache.cassandra.metrics:type=ThreadPools,path=internal,scope=Repair#.*"

warningThresholdMillis: 100 # This will warn in logs when a MBean takes longer than the specified value.

whitelisted_clients: # Whitelist for CQL connections
  - "127.0.0.1"
  - "^*.*.*.*"
```
