### Start the Java Agent (init.d service)

To start the service using systemd:

``` -
systemctl daemon-reload
systemctl start axon-server
systemctl status axon-server
```

Enable the systemd service so that axon-server starts at boot.

``` extempore
sudo systemctl enable axon-server.service
```

### Environment file
The systemd service file and init.d script both use the file located at ` /etc/default/axon-server ` for environment variables used when starting the agent. Here you can override log directory, data directory and other variables.

### Logging
By default Java Agent will log to /var/log/axon-server