# AxonOps GUI installation

AxonOps GUI service is installed as a separate service to AxonOps Server. The GUI service (axon-dash) can be co-hosted on the same server as the AxonOps Server process, or they can be running on 2 separate servers.

This section describes the installation process for the GUI service.

## Step 1 - Installation

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

sudo yum install axon-dash
```
#### Debian / Ubuntu
``` bash
curl https://packages.axonops.com/apt/repo-signing-key.gpg | sudo apt-key add -
echo "deb https://packages.axonops.com/apt axonops-apt main" | sudo tee /etc/apt/sources.list.d/axonops-apt.list
sudo apt-get update
sudo apt-get install axon-dash
```

## Step 2 - Configuration
Change **axon-dash** configuration to specify **axon-server** listening address.

* `/etc/axonops/axon-dash.yml`
``` yaml  hl_lines="7"
axon-dash: # The listening address of axon-dash
  host: 0.0.0.0
  port: 3000
  line_charts_max_results: 256

axon-server:
  public_endpoints: "http://axon-server.public:8080, https://axon-server.public" # Public HTTP endpoint to axon-server API. This can be a list with comma separator. http://127.0.0.1 or http://locahost are always wrong.
  context_path: "" # example: "/gui"
```
> axon-server default listening port is **8080**


## Step 3 - axon-server configuration update
Update **axon-server** configuration by setting the correct **axon-dash** **host** and **port**:

* `/etc/axonops/axon-server.yml`

``` yaml hl_lines="7 8"
host: 0.0.0.0  # axon-server listening address 
port: 8080 # axon-server listening port 
elastic_host: http://localhost # Elasticsearch endpoint
elastic_port: 9200 # Elasticsearch port

axon-dash: # This must point to axon-dash address
  host: 127.0.0.1
  port: 3000
  https: false

alerting:
# How long to wait before sending a notification again if it has already
# been sent successfully for an alert. (Usually ~3h or more).
  notification_interval: 3h

retention:
  events: 8w # logs and events retention. Must be expressed in weeks (w)
  metrics:
      high_resolution: 14d # High frequency metrics. Must be expressed in days (d)
      med_resolution: 12w # Must be expressed in weeks (w)
      low_resolution: 12M # Must be expressed in months (M)
      super_low_resolution: 2y # Must be expressed in years (y)
  backups: # Those are use as defaults but can be overridden from the UI
    local: 10d
    remote: 30d
```

## Step 4 - Restart **axon-server** after updating it's configuration
``` bash
sudo systemctl restart axon-server
```

## Step 5 - Start axon-dash

``` bash
sudo systemctl daemon-reload
sudo systemctl start axon-dash
sudo systemctl status axon-dash
```

This will start the **axon-dash** process as the **axonops** user, which was created during the package installation. The default listening address is `0.0.0.0:3000`.


#### Package details

* Configuration: `/etc/axonops/axon-dash.yml`
* Binary: `/usr/share/axonops/axon-dash`
* Logs: `/var/log/axonops/axon-dash.log` 
* Systemd service: `/usr/lib/systemd/system/axon-dash.service`
* Copyright : `/usr/share/doc/axonops/axon-dash/copyright`
* Licenses : `/usr/share/axonops/licenses/axon-dash/`


## Step 6 - Installing agents

Now **axon-dash** is installed, you can start installing [cassandra-agent](../cassandra-agent/install.md)
