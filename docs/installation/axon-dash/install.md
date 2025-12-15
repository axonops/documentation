---
title: "AxonOps Dashboard Installation"
description: "Install AxonOps Dashboard. Web interface installation for monitoring and management."
meta:
  - name: keywords
    content: "AxonOps Dashboard install, web interface, installation"
---

# AxonOps Dashboard Installation

The AxonOps Dashboard (`axon-dash`) is a GUI service that is installed as a separate service to AxonOps Server (`axon-server`).
The GUI service can be co-hosted on the same server as the AxonOps Server process,
or can be run on a separate server.

This section describes the installation process for the GUI service.

## Installation

{!dynamic_pages/axon_dash/os.md!}

### Configuration File Locations

The following files are installed into the local file system:

* Configuration File: `/etc/axonops/axon-dash.yml`
* Binary: `/usr/share/axonops/axon-dash`
* Logs: `/var/log/axonops/axon-dash.log`
* Systemd service: `/usr/lib/systemd/system/axon-dash.service`
* Copyright : `/usr/share/doc/axonops/axon-dash/copyright`
* Licenses : `/usr/share/axonops/licenses/axon-dash/`

## Configure AxonOps Dashboard

If AxonOps Server has been installed on a different machine,
update the `axon-dash` configuration file found at `/etc/axonops/axon-dash.yml`
to specify the `axon-server` listening address:

```yaml
axon-server:
  # HTTP endpoint to access axon-server API from axon-dash
  private_endpoints: "http://127.0.0.1:8080"
  # example: "/gui"
  context_path: ""
```
Note: The AxonOps Server `api_port` defaults to `8080`.

## Configure AxonOps Server


If AxonOps Dashboard requires being bound and exposed to a different `host` and `port`,
update the `host` and/or `port` values for `axon-dash` from their defaults
within `/etc/axonops/axon-dash.yml`:


```yaml
axon-dash:
  host: 127.0.0.1
  port: 3000
  https: false
```

Subesquently, update the `axon_dash_url` value within `/etc/axonops/axon-server.yml`:

```yaml
axon_dash_url: http://127.0.0.1:3000
```

Note: The `axon-dash` address must be accessible from `axon-server`.

### Restart `axon-server` to Apply Changes

```bash
sudo systemctl restart axon-server
```

## Start AxonOps Dashboard

The following will start the `axon-dash` process as the `axonops` user, which was created during the package installation.


```bash
{!installation/axon-dash/scripts/start-axon-dash.sh!}
```

The default listening address is [0.0.0.0:3000](http://0.0.0.0:3000).

## Setup SSL/TLS for AxonOps Dashboard

The AxonOps Dashboard does not support SSL/TLS and needs Nginx to be setup in front of
the dashboard.

### Installing Nginx

Install Nginx using the [official guide](https://docs.nginx.com/nginx/admin-guide/installing-nginx/installing-nginx-open-source/){target="_blank"}.

#### Configuration File Locations

Most installations of Nginx use the default config location of `/etc/nginx/`.

The default location depends on whether or not the installation is from an
archive distribution (tar.gz or zip) or a package distribution (Debian or RPM packages).

Based on the installation the default location can be either:

- `/etc/nginx`
- `/usr/local/nginx/conf`
- `/usr/local/etc/nginx`

For more info on Nginx configuration, read [Creating Nginx Configuration Files](https://docs.nginx.com/nginx/admin-guide/basic-functionality/managing-configuration-files/#:~:text=By%20default%20the%20file%20is,local%2Fetc%2Fnginx.){target="_blank"}.

### Configure Nginx

Edit `/etc/nginx/nginx.conf` and add/update the following lines:


```nginx
server {
  listen <ip>:443 ssl;

  server_name <hostname>;

  client_max_body_size 100M;

  root /usr/share/nginx;
  index index.html;

  ssl_certificate     /full/path/to/ssl_cert;
  ssl_certificate_key /full/path/to/ssl_key/;
  ssl_protocols       TLSv1.2 TLSv1.3;

  location / {
    proxy_pass http://localhost:3000; #Default AxonOps-Dash port
  }
}
```

## Next - Installing AxonOps Agents

Now that the AxonOps Dashboard is installed,
we will  [install the AxonOps Agents](../agent/install.md) to populate the dashboard.
