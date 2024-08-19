## Step 3 - axon-server configurations


Make sure **elastic_host** and **elastic_port** are corresponding to your Elasticsearch instance.

**Basic Auth in Elasticsearch** 

- Create a user that has a dedicated role and username password.
- Please dont use any of the built in users for Elasticsearch.

To create users please refer to the Elasticsearch docs [here](https://www.elastic.co/guide/en/elasticsearch/reference/current/setting-up-authentication.html){target="_blank"}


*AxonOps Server configuration file location :* `/etc/axonops/axon-server.yml`

``` yaml hl_lines="11 12"
host: 0.0.0.0  # axon-server listening address (used by axon-agents for connections) (env variable: AXONSERVER_HOST)
agents_port: 1888 # axon-server listening port for agent connections 

api_host: 127.0.0.1 # axon-server listening address (used by axon-dash for connections)
api_port: 8080 # axon-server HTTP API listening port (used by axon-dash) (AXONSERVER_PORT)

elastic_hosts: # Elasticsearch endpoint (env variable:ELASTIC_HOSTS, comma separated list)
  - http://localhost:9200

# AxonOps licensing
license_key: license-key
org_name: my-company

# SSL/TLS Settings for AxonOps Agent connections
tls:
  mode: "disabled" # disabled, TLS

axon-dash: # This must point to the axon-dash address accessible from axon-server
  host: 127.0.0.1
  port: 3000
  https: false
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





