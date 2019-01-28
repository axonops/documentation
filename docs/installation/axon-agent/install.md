# axon-agent installation

#### CentOS / RedHat installer
``` -
sudo yum install <TODO>
```
#### Debian / Ubuntu installer
``` -
sudo apt-get install <TODO>
```

#### Package details

* Configuration: `/etc/axonops/axon-agent.yml`
* Binary: `usr/share/axonops/axon-agent`
* Systemd service: `usr/lib/systemd/system/axon-agent.service`
* certificate file used for it's OpenTSDB endpoint when SSL is active: `/etc/axonops/agent.crt`
* key file used for it's OpenTSDB endpoint when SSL is active: `/etc/axonops/agent.key `


#### Configuration
Make sure **axon-agent** configuration points to the correct **axon-server** address and your **organisation name** is specified:

``` yaml hl_lines="2 8"
axon-server:
    hosts: "axon-server_endpoint" # Specify axon-server IP (ex: "192.168.0.5")

axon-agent:
    host: 0.0.0.0 # axon-agent listening address for it's OpenTSDB endpoint
    port: 9916 # axon-agent listening port for it's OpenTSDB endpoint
    org: "your_organisation_name" # Specify your organisation name
    standalone_mode: true
    type: "standalone"
    cluster_name: "standalone"
    ssl: false # SSL flag for it's OpenTSDB endpoint
```

#### Start axon-agent

``` -
systemctl daemon-reload
systemctl start axon-agent
systemctl status axon-agent
```

This will start the **axon-agent** process as the **axonops** user, which was created during the package installation. The default OpenTSDB listening address is **0.0.0.0:9916**.

* Note that you will have to refresh **axon-dash** page to show the newly connected node.

## Going further

You can extend axon-agent capabilities for the following applications:

* [cassandra](../cassandra-agent/install.md)
* [DSE](../dse-agent/install.md)