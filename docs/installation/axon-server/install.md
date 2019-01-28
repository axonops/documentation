
#### Package details

* Configuration: `/etc/axonops/axon-server.yml`
* Logs: `/var/log/axonops/axon-server.log` 
* Binary: `usr/share/axonops/axon-server`
* Systemd service: `usr/lib/systemd/system/axon-server.service`

#### Start the server

``` -
systemctl daemon-reload
systemctl start axon-server
systemctl status axon-server
```

This will start the `axon-server` process as the `axonops` user, which was created during the package installation.  The default listening address is `0.0.0.0:8080`.

#### Configuration defaults

``` yaml

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

## Installing axon-dash

Now **axon-server** is installed, you can start installing [axon-dash](../axon-dash/install.md)




