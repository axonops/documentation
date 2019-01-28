# axon-dash installation (CentOS / RedHat)


``` -
sudo yum install <TODO>
```

#### Package details

* Configuration: `/etc/axonops/axon-dash.yml`
* Binary: `usr/share/axonops/axon-dash`
* Systemd service: `usr/lib/systemd/system/axon-dash.service`

#### Start axon-dash

``` -
systemctl daemon-reload
systemctl start axon-dash
systemctl status axon-dash
```

This will start the `axon-dash` process as the `axonops` user, which was created during the package installation. The default listening address is `0.0.0.0:3000`.

#### Configuration defaults

``` yaml
axon-dash: #  The listening listening address of axon-dash
  host: 0.0.0.0
  port: 3000

axon-server: # This must point to axon-server listening address
  host: 127.0.0.1 
  port: 8080
```

## Installing axon-agent

Now axon-dash is installed, you can start installing [axon-agent](../agent/centos.md)