# AxonOps Dash/GUI installation

AxonOps GUI service is installed as a separate service to AxonOps Server. The GUI service (axon-dash) can be co-hosted on the same server as the AxonOps Server process, or they can be running on 2 separate servers.

This section describes the installation process for the GUI service.

## Step 1 - Installation

{!dynamic_pages/axon_dash/os.md!}

## Step 2 - Configuration

Change **axon-dash** configuration to specify **axon-server** listening address.

* `/etc/axonops/axon-dash.yml`
``` yaml  hl_lines="7"
axon-dash: # The listening address of axon-dash
  host: 0.0.0.0
  port: 3000
  line_charts_max_results: 256

axon-server:
  private_endpoints: "http://127.0.0.1:8080" # HTTP endpoint to access axon-server API from axon-dash.
  context_path: "" # example: "/gui"
```
> axon-server default API port is **8080**


## Step 3 - axon-server configuration update
if required, update **axon-server** configuration by setting the correct **axon-dash** **host** and **port**:

* `/etc/axonops/axon-server.yml`

``` yaml hl_lines="7 8"
...
axon-dash: # This must point to the axon-dash address accessible from axon-server
  host: 127.0.0.1
  port: 3000
  https: false
...
```

## Step 4 - Restart **axon-server** after updating its configuration
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

## Step 6 - Setting up SSL/TLS for AxonDash

AxonDash does not support SSL/TLS and needs to be fronted by Nginx. You can install and configure Nginx by following the [Configure Nginx](../axon-dash/configure_nginx.md) guide.

## Step 7 - Installing agents

Now **axon-dash** is installed, you can start installing [cassandra-agent](../agent/install.md)
