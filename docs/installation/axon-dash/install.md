# AxonOps GUI installation

AxonOps GUI service is installed as a separate service to AxonOps Server. The GUI service (axon-dash) can be co-hosted on the same server as the AxonOps Server process, or they can be runnin on 2 separate servers.

This section describes the installation process for the GUI service.

#### CentOS / RedHat installer
``` -
sudo yum-config-manager --add-repo https://repo.digitalis.io/repository/axonops-yum/stable/x64
sudo yum install axon-dash
```
#### Debian / Ubuntu installer
``` -
sudo cp /etc/apt/sources.list /etc/apt/sources.list_backup
echo "deb https://repo.digitalis.io/repository/axonops-apt xenial main" | sudo tee /etc/apt/sources.list.d/axonops.list
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 727BDA4A
sudo apt-get update
sudo apt-get install axon-dash
```

#### Package details

* Configuration: `/etc/axonops/axon-dash.yml`
* Binary: `/usr/share/axonops/axon-dash`
* Logs: `/var/log/axonops/axon-dash.log` 
* Systemd service: `usr/lib/systemd/system/axon-dash.service`
* Copyright : `/usr/share/doc/axonops/axon-dash/copyright`
* Licenses : `/usr/share/axonops/licenses/axon-dash/`

#### Configuration
Make sure **axon-dash** configuration points to the correct **axon-server** listening address:

**axon-dash** configuration file `/etc/axonops/axon-dash.yml`:
``` yaml  hl_lines="5 6 7"
axon-dash: #  The listening address of axon-dash
  host: 0.0.0.0
  port: 3000

axon-server:
  public_endpoints: "http://axon-server.public:8080, https://axon-server.public" # Public HTTP endpoint to axon-server API. This can be a list with comma separator. http://127.0.0.1 or http://locahost are always wrong.
  context_path: "" # exemple: "/gui"
```

## axon-server configuration update
Make sure **axon-server** configuration is up to date and point to **axon-dash** and **elasticsearch** listening address:

**axon-server** configuration file `/etc/axonops/axon-server.yml`:

``` yaml hl_lines="3 6 7"
host: 0.0.0.0  # axon-server listening address 
port: 8080 # axon-server listening port 
elastic_host: localhost # Elasticsearch endpoint
elastic_port: 9200 # Elasticsearch port

axon-dash: # This must point to axon-dash address
  host: 127.0.0.1
  port: 3000
  https: false

alerting:
# How long to wait before sending a notification again if it has already
# been sent successfully for an alert. (Usually ~3h or more).
  notification_interval: 3h

retention:
  events: 24w # logs and events retention. Must be expressed in weeks (w)
  metrics:
      high_resolution: 30d # High frequency metrics. Must be expressed in days (d)
      med_resolution: 24w # Must be expressed in weeks (w)
      low_resolution: 24M # Must be expressed in months (M)
      super_low_resolution: 3y # Must be expressed in years (y)
  backups: # Those are use as defaults but can be overridden from the UI
    local: 10d
    remote: 30d 
```

Restart **axon-server** after updating it's configuration
``` -
sudo systemctl restart axon-server
```

#### Start axon-dash

``` -
sudo systemctl daemon-reload
sudo systemctl start axon-dash
sudo systemctl status axon-dash
```

This will start the **axon-dash** process as the **axonops** user, which was created during the package installation. The default listening address is `0.0.0.0:3000`.


## Installing axon-agent

Now **axon-dash** is installed, you can start installing [axon-agent](../axon-agent/install.md)