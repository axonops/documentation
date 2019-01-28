# axon-dash installation

#### CentOS / RedHat installer
``` -
sudo yum install <TODO>
```
#### Debian / Ubuntu installer
``` -
sudo apt-get install <TODO>
```

#### Package details

* Configuration: `/etc/axonops/axon-dash.yml`
* Binary: `usr/share/axonops/axon-dash`
* Logs: `TODO` 
* Systemd service: `usr/lib/systemd/system/axon-dash.service`


#### Configuration
Make sure **axon-dash** configuration points to the correct **axon-server** listening address:

**axon-dash** configuration file `/etc/axonops/axon-dash.yml`:
``` yaml  hl_lines="5 6 7"
axon-dash: #  The listening address of axon-dash
  host: 0.0.0.0
  port: 3000

axon-server: # This must point to axon-server interface listening address
  host: set_axon-server_IP  # 127.0.0.1 is always wrong
  port: 8080
```

## axon-server configuration update
Make sure **axon-server** configuration is up to date and point to **axon-dash** listening address:

**axon-server** configuration file `/etc/axonops/axon-server.yml`:

``` yaml hl_lines="6 7 8"

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
systemctl restart axon-server
```

#### Start axon-dash

``` -
systemctl daemon-reload
systemctl start axon-dash
systemctl status axon-dash
```

This will start the **axon-dash** process as the **axonops** user, which was created during the package installation. The default listening address is `0.0.0.0:3000`.


## Installing axon-agent

Now **axon-dash** is installed, you can start installing [axon-agent](../axon-agent/install.md)