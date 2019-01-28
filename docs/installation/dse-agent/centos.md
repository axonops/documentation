# axon-java-agent for DSE installation (CentOS / RedHat)

## Prerequisites

DSE agent needs axon-agent to run properly. If not installed already, please go to [axon-agent](../agent/centos) installation page.

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

This will enhance the capabilities provided by axonops such as the adaptive repairs and the backups.

#### Start axon-agent

``` -
systemctl daemon-reload
systemctl start axon-agent
systemctl status axon-agent
```

This will start the `axon-agent` process as the `axonops` user, which was created during the package installation. The default OpenTSDB listening address is `0.0.0.0:9916`.

#### Configuration defaults

``` yaml
axon-server:
    hosts: "set_axon-server_endpoint" # Specify axon-server endpoint
    port: 1888

axon-agent:
    host: 0.0.0.0 # axon-agent listening address for it's OpenTSDB endpoint
    port: 9916 # axon-agent listening port for it's OpenTSDB endpoint
    org: "set_your_organisation_name" # Specify your organisation name
    standalone_mode: true
    type: "standalone"
    cluster_name: "standalone"
    ssl: false # SSL flag for it's OpenTSDB endpoint
```

## Going further

If you want to extend axon-agent capabilities and use it on a cassandra/DSE node, you can start installing [axon-java-agent](../../cassandra-agent.md)