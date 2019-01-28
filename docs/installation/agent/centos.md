# axon-java-agent installation (cassandra CentOS / RedHat)

``` -
sudo yum install <TODO>
```

#### Package details

* Configuration: `/etc/axonops/axon-agent.yml`
* Binary: `usr/share/axonops/axon-agent`
* Systemd service: `usr/lib/systemd/system/axon-agent.service`
* crt used for it's OpenTSDB endpoint when SSL is active: `/etc/axonops/agent.crt`
* key used for it's OpenTSDB endpoint when SSL is active: `/etc/axonops/agent.key `

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

You can extend axon-agent capabilities for the following applications:

* [cassandra](../cassandra-agent/centos.md)
* [DSE](../dse-agent/centos.md)