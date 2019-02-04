# axon-agent installation

#### CentOS / RedHat installer
``` -
sudo yum-config-manager --add-repo https://repo.digitalis.io/repository/axonops-yum/stable/x64
sudo yum install axon-agent
```
#### Debian / Ubuntu installer
``` -
sudo cp /etc/apt/sources.list /etc/apt/sources.list_backup
echo "deb https://repo.digitalis.io/repository/axonops-apt xenial main" | sudo tee /etc/apt/sources.list.d/axonops.list
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 727BDA4A
sudo apt-get update
sudo apt-get install axon-agent
```

#### Package details

* Configuration: `/etc/axonops/axon-agent.yml`
* Binary: `/usr/share/axonops/axon-agent`
* Logs : `/var/log/axonops/axon-agent.log`
* Systemd service: `/usr/lib/systemd/system/axon-agent.service`
* certificate file used for it's OpenTSDB endpoint when SSL is active: `/etc/axonops/agent.crt`
* key file used for it's OpenTSDB endpoint when SSL is active: `/etc/axonops/agent.key`
* Copyright : `/usr/share/doc/axonops/axon-agent/copyright`
* Licenses : `/usr/share/axonops/licenses/axon-agent/`


#### Configuration
Make sure **axon-agent** configuration points to the correct **axon-server** address and your **organisation name** is specified:

``` yaml hl_lines="2 7 14"
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

NTP:
    host: "set_NTP_server" # Specify a NTP to determine a NTP offset 
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