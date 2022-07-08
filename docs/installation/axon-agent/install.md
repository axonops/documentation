# axon-agent installation

There 2 elements to the AxonOps agent. The first is the axon-agent, which is a native application for Linux running as a standalone daemon process. The second is the Java agent which is added to the Java process. Two components communicate with each other using the Unix domain socket. The reason for this approach are the following requirements we have on the agent process.

* No JMX
* Metrics must push metrics from Cassandra all the way to the AxonOps server - never pull.

AxonOps Java agent will push the metrics to the AxonOps native agent, which in turn pushes them to the AxonOps server. Scraping a large volume of metrics against the JMX is slow. We also wanted to avoid exposing an HTTP endpoint within Cassandra like the [Prometheus JMX exporter](https://github.com/prometheus/jmx_exporter) does.

The messaging between native agent and Java agent are bi-directional - i.e. AxonOps server sends control messages to Cassandra for operations such as repair and backups without the use of JMX.

This section describes how to install and configure both the native agent and Java agent.



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

sudo yum install axon-agent
```
#### Debian / Ubuntu
``` bash
curl https://packages.axonops.com/apt/repo-signing-key.gpg | sudo apt-key add -
echo "deb https://packages.axonops.com/apt axonops-apt main" | sudo tee /etc/apt/sources.list.d/axonops-apt.list
sudo apt-get update
sudo apt-get install axon-agent
```

#### Package details

* Configuration: `/etc/axonops/axon-agent.yml`
* Binary: `usr/share/axonops/axon-agent`
* Logs : `/var/log/axonops/axon-agent.log`
* Systemd service: `/usr/lib/systemd/system/axon-agent.service`
* certificate file used for it's OpenTSDB endpoint when SSL is active: `/etc/axonops/agent.crt`
* key file used for it's OpenTSDB endpoint when SSL is active: `/etc/axonops/agent.key `


#### Configuration
Make sure **axon-agent** configuration points to the correct **axon-server** address and your **organisation name** is specified:

``` yaml hl_lines="2 7 14"
axon-server:
    hosts: "axon-server_endpoint" # Specify axon-server IP axon-server.mycompany.com

axon-agent:
    org: "my-company-test" # Specify your organisation name
    type: "cassandra"

NTP:
    host: "ntp.mycompany.com" # Specify you NTP server IP address or hostname
```

#### Start axon-agent

``` bash
systemctl daemon-reload
systemctl start axon-agent
systemctl status axon-agent
```


This will start the **axon-agent** process as the **axonops** user, which was created during the package installation.

* Note that you will have to refresh **axon-dash** page to show the newly connected node.

## Next Steps

To complete your agent installation you will need to follow the steps in the link below:

* [cassandra](../cassandra-agent/install.md)
