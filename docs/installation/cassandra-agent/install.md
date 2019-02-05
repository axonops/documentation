# AxonOps Cassandra agent installation

This agent will enable metrics collection, adaptive repairs and backups for Cassandra.

## Available versions
* Cassandra 3.11.x


## Cassandra agent installation

> Make sure that the `<version>` of your Cassandra and Cassandra agent are compatible from the [compatibility matrix](../../compat_matrix/compat_matrix). 


#### CentOS / RedHat installer
``` bash
printf '%s\n%s\n%s\n%s\n%s\n%s\n' '[axonops]' 'name=axonops Repository' 'baseurl=https://repo.digitalis.io/repository/axonops-yum/stable/x64/' 'enabled=1' 'gpgcheck=0' | sudo tee /etc/yum.repos.d/axonops.repo
sudo yum install axon-cassandra<version>-agent
```
#### Debian / Ubuntu installer
``` bash
sudo cp /etc/apt/sources.list /etc/apt/sources.list_backup
echo "deb https://repo.digitalis.io/repository/axonops-apt xenial main" | sudo tee /etc/apt/sources.list.d/axonops.list
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 727BDA4A
sudo apt-get update
sudo apt-get install axon-cassandra<version>-agent
```
> Note: This will install our Cassandra agent and it's dependency axon-agent


#### Configuration
Update the following highlighted lines from `/etc/axonops/axon-agent.yml`:

``` yaml hl_lines="2 5 9"
axon-server:
    hosts: "axon-server_endpoint" # Specify axon-server IP axon-server.mycompany.com

axon-agent:
    org: "my-company-test" # Specify your organisation name

NTP:
    host: "ntp.mycompany.com" # Specify you NTP server IP address or hostname

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

  blacklist: # You can blacklist metrics based on MBean query pattern
    - "org.apache.cassandra.metrics:type=ColumnFamily,*" # duplication of table metrics
    - "org.apache.cassandra.metrics:name=SnapshotsSize,*" # Collecting SnapshotsSize metrics slows down collection

  free_text_blacklist: # You can blacklist metrics based on Regex pattern
    - "org.apache.cassandra.metrics:type=ThreadPools,path=internal,scope=Repair#.*"

  warningThresholdMillis: 100 # This will warn in logs when a MBean takes longer than the specified value.
```


#### Configure Cassandra 

Edit `cassandra-env.sh` usually located in your Cassandra install path such as `/<path_to_Cassandra>/conf/cassandra-env.sh` and append the following line at the end of the file:

``` bash 
JVM_OPTS="$JVM_OPTS -javaagent:/usr/share/axonops/axon-cassandra<version>-agent.jar=/etc/axonops/axon-agent.yml"
```

>Exemple with Cassandra agent version *3.11*:
``` bash
JVM_OPTS="$JVM_OPTS -javaagent:/usr/share/axonops/axon-cassandra3.11-agent.jar=/etc/axonops/axon-agent.yml"
```
#### Add axonops user to Cassandra user group and Cassandra user to axonops group

``` bash
sudo usermod -aG <your_cassandra_group> axonops
sudo usermod -aG axonops <your_cassandra_user>
```

#### Start Cassandra

All you need to do now is start Cassandra.



#### Cassandra agent Package details

* Configuration: `/etc/axonops/axon-agent.yml`
* Binary: `/usr/share/axonops/axon-cassandra<version>-agent.jar`
* Version number: `/usr/share/axonops/axon-cassandra<version>-agent.version`
* Copyright : `/usr/share/doc/axonops/axon-cassandra<version>-agent/copyright`
* Licenses : `/usr/share/axonops/licenses/axon-cassandra<version>-agent/`

#### axon-agent Package details

* Configuration: `/etc/axonops/axon-agent.yml`
* Binary: `usr/share/axonops/axon-agent`
* Logs : `/var/log/axonops/axon-agent.log`
* Systemd service: `/usr/lib/systemd/system/axon-agent.service`
* certificate file used for it's OpenTSDB endpoint when SSL is active: `/etc/axonops/agent.crt`
* key file used for it's OpenTSDB endpoint when SSL is active: `/etc/axonops/agent.key `