## Step 3 - axon-server configuration update

Make sure **elastic_host** and **elastic_port** are corresponding to your Elasticsearch instance.

* `/etc/axonops/axon-server.yml`

``` yaml hl_lines="3 4"
host: 0.0.0.0  # axon-server listening address (used by axon-dash and axon-agent)
port: 8080 # axon-server HTTP API listening port (used by axon-dash)
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

## Step 4 - Start the server

``` -
sudo systemctl daemon-reload
sudo systemctl start axon-server
sudo systemctl status axon-server
```

This will start the `axon-server` process as the `axonops` user, which was created during the package installation.  The default listening address is `0.0.0.0:8080`.

#### Package details

* Configuration: `/etc/axonops/axon-server.yml`
* Binary: `/usr/share/axonops/axon-server`
* Logs: `/var/log/axonops/axon-server.log` 
* Systemd service: `/usr/lib/systemd/system/axon-server.service`
* Copyright : `/usr/share/doc/axonops/axon-server/copyright`
* Licenses : `/usr/share/axonops/licenses/axon-server/`


## Step 5 - Installing axon-dash

Now **axon-server** is installed, you can start installing the GUI for it: [axon-dash](../axon-dash/install.md)





