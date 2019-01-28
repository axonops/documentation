# axon-java-agent for DSE installation

This agent will enable metrics collection from DSE and enable adaptive repairs and backups.

## Prerequisites

DSE agent needs axon-agent to be installed and configured properly. If not installed already, please go to [axon-agent](../agent/centos) installation 
page.

#### Setup axon-agent for DSE

You'll need the specify/update the following lines from axon-agent.yml:

``` yaml
axon-agent:
    standalone_mode: false
    type: "dse"
```

## Install DSE agent


``` -
sudo yum install <TODO>
```

#### Package details

* Configuration: `/etc/axonops/axon-java-agent.yml`
* Binary: `usr/share/axonops/axon-dse<version>-agent-1.0.jar`
* Version number: `usr/share/axonops/axon-dse<version>-agent-1.0.version`

#### Configure DSE to use axon-java-agent

Edit `cassandra-env.sh` usually located in your dse install path such as `/<path_to_DSE>/resources/cassandra/conf/cassandra-env.sh` and add at the end of the file the following line:

``` bash 
JVM_OPTS="$JVM_OPTS -javaagent:/usr/share/axonops/axon-dse<version>-agent-1.0.jar=/etc/axonops/axon-java-agent.yml"
```

exemple:
``` -
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
