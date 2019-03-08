# axon-java-agent for DSE installation

This agent will enable metrics collection from DSE and enable adaptive repairs and backups.

## Prerequisites

DSE agent needs **axon-agent** to be installed and configured properly. If not installed already, please go to [axon-agent](../../axon-agent/install) installation 
page.

#### Setup axon-agent for DSE

You'll need the specify/update the following lines from **axon-agent.yml** located in `/etc/axonops/axon-agent.yml`:



``` yaml hl_lines="2 8 9 10 11"
axon-server:
    hosts: "axon-server_endpoint" # Specify axon-server endpoint

axon-agent:
    host: 0.0.0.0 # axon-agent listening address for it's OpenTSDB endpoint
    port: 9916 # axon-agent listening port for it's OpenTSDB endpoint
    org: "your_organisation_name" # Specify your organisation name
    standalone_mode: false
    type: "dse"
    #cluster_name: "standalone" # comment that line
    ssl: false # SSL flag for it's OpenTSDB endpoint
```
* Set `standalone_mode` to **false**
* Set `type` to **dse**
* Don't forget to comment or remove the `cluster_name` as it will be deduced from DSE configuration.
* Don't forget to specify **axon-server** host and port if that's not already specified.

## DSE agent installation

Make sure the `{version}` of your DSE and DSE agent are compatible from the [compatibility matrix](../../compat_matrix/compat_matrix). 


#### CentOS / RedHat installer
``` -
sudo yum install <TODO>
```
#### Debian / Ubuntu installer
``` -
sudo apt-get install <TODO>
```

#### Package details

* Configuration: `/etc/axonops/axon-java-agent.yml`
* Binary: `usr/share/axonops/axon-dse{version}-agent-1.0.jar`
* Version number: `usr/share/axonops/axon-dse{version}-agent-1.0.version`

#### Configure DSE 

Edit `cassandra-env.sh` usually located in your dse install path such as `/<path_to_DSE>/resources/cassandra/conf/cassandra-env.sh` and add at the end of the file the following line:

``` bash 
JVM_OPTS="$JVM_OPTS -javaagent:/usr/share/axonops/axon-dse{version}-agent-1.0.jar=/etc/axonops/axon-java-agent.yml"
```


example:
``` bash
JVM_OPTS="$JVM_OPTS -javaagent:/usr/share/axonops/axon-dse6.0.4-agent-1.0.jar=/etc/axonops/axon-java-agent.yml"
```


#### Start DSE

All you need to do now is start DSE.


#### Configuration defaults

``` yaml
tier0: # metrics collected every 5 seconds
    metrics:
        jvm_:
          - "java.lang:*"
        cas_:
          - "org.apache.cassandra.metrics:*"
          - "org.apache.cassandra.net:type=FailureDetector"
          - "com.datastax.bdp:type=dsefs,*"

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
