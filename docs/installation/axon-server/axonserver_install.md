# AxonOps Server installation

## Step 1 - Installation

Execute the following command to setup the AxonOps repository for your OS

{!dynamic_pages/axon_server/os.md!}

## Step 2 - Configure axon-server

*AxonOps Server configuration file location :* `/etc/axonops/axon-server.yml`

### Update elastic_hosts

Confirm the **elastic_url** and **elastic_port** correspond to the dedicated Elasticsearch instance.

#### Basic Auth in Elasticsearch (If enabled)

Update the username and password with the dedicated service account/user created in Elasticsearch

#### Load Balancer or Dedicated Coordinator nodes fronting Elasticsearch

By default AxonOps Server will discover all the nodes in the Elasticsearch cluster. It will utilise the list of dicovered nodes to round-robin requests to Elasticsearch.

When setting up a load balancing nodes or infrastrcutre that fronts Elasticsearch it has smart load balancing capabilites and the node discovery is not required.  

To turn off node discovery set `elastic_discover_nodes:false`

### AxonOps Licensing

This section is for Enterprise plan clients and is not needed on the Free Forever plan.

`license_key` : This key will be used to unlock the Enterprise features of AxonOps.
`org_name` : Needs to match the Name provided during the Enterprise onboarding process.

### Update Configuration File

``` yaml hl_lines="7 33 34"
host: 0.0.0.0  # axon-server listening address (used by axon-agents for connections) (env variable: AXONSERVER_HOST)
agents_port: 1888 # axon-server listening port for agent connections 

api_host: 127.0.0.1 # axon-server listening address (used by axon-dash for connections)
api_port: 8080 # axon-server HTTP API listening port (used by axon-dash) (AXONSERVER_PORT)

elastic_hosts: # Elasticsearch endpoint (env variable:ELASTIC_HOSTS, comma separated list)
  - http://localhost:9200

# Configure multiple Elasticsearch hosts with username and password authentication
# elastic_hosts:
# - https://username:password@ip.or.hostname:port
# - https://username:password@ip.or.hostname:port
# - https://username:password@ip.or.hostname:port

# SSL/TLS config for Elasticsearch
# elastic_skipVerify: true # Disables CA and Hostname verification

# Configure the number of shards per index. The default value of 1 is recommended for most use cases
elastic_shards: 1
# Configure the number of replicas per shard. Defaults to 0 if not specified.
elastic_replicas: 0

# Enable/disable Elasticsearch cluster discovery (sniffing). Defaults to true, set to false to disable
# Allows more nodes to be added to Elasticsearch for Metrics storage without having to restart Axon-Server and update elastic_hosts with all the ELK node values.
elastic_discover_nodes: true
# How often to perform cluster discovery. Default is every 5 minutes if this is omitted
elastic_discover_node_interval: 5m

#integrations_proxy: # proxy endpoint for integrations. (INTEGRATIONS_PROXY)

# AxonOps licensing
license_key: license-key
org_name: my-company

# SSL/TLS Settings for AxonOps Agent connections
tls:
  mode: "disabled" # disabled, TLS
  # Only set below if mode is TLS
  skipVerify: false # Disables CA and Hostname verification
  caFile: "path_to_certs_on_axonops_server.crt" # required if skipVerify is not set and you are using a self-signed cert
  certFile: "path_to_certs_on_axonops_server.crt"
  keyFile: "path_to_key_file_on_axonops_server.key"

# For better performance on large clusters, you can use a CQL store for the metrics.
# To opt-in for CQL metrics storage, just specify at least one CQL host.
# We do recommend to specify a NetworkTopologyStrategy for cql_keyspace_replication
#cql_hosts: #  (CQL_HOSTS, comma separated list)
#  - 192.168.0.10:9042
#  - 192.168.0.11:9042
#cql_username: "cassandra" # (CQL_USERNAME)
#cql_password: "cassandra" # (CQL_PASSWORD)
#cql_local_dc: datacenter1 # (CQL_LOCAL_DC)
#cql_ssl: false # (CQL_SSL)
#cql_skip_verify: false  # (CQL_SSL_SKIP_VERIFY)
#cql_ca_file: /path/to/ca_file  # (CQL_CA_FILE)
#cql_cert_file: /path/to/cert_file  # (CQL_CERT_FILE)
#cql_key_file: /path/to/key_file  # (CQL_KEY_FILE)
#cql_autocreate_tables: true # (CQL_AUTO_CREATE_TABLES) this will tell axon-server to automatically create the metrics tables (true is recommended)
#cql_keyspace_replication: "{ 'class' : 'SimpleStrategy', 'replication_factor' : 1 }" # (CQL_KS_REPLICATION) keyspace replication for the metrics tables
#cql_read_consistency: "LOCAL_ONE" # (CQL_READ_CONSISTENCY) #One of the following:	ANY, ONE, TWO, THREE, QUORUM, ALL, LOCAL_QUORUM, EACH_QUORUM, LOCAL_ONE
#cql_write_consistency: "LOCAL_ONE" # (CQL_WRITE_CONSISTENCY) #One of the following:	ANY, ONE, TWO, THREE, QUORUM, ALL, LOCAL_QUORUM, EACH_QUORUM, LOCAL_ONE

axon-dash: # This must point to the axon-dash address accessible from axon-server
  host: 127.0.0.1
  port: 3000
  https: false

alerting:
# How long to wait before sending a notification again if it has already
# been sent successfully for an alert. (Usually ~3h or more).
  notification_interval: 3h

# Default retention settings, most can be overridden from the frontend
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

> For better performances on large clusters (100+ nodes), you can use a CQL store for the metrics such as **Cassandra**. To opt-in for CQL metrics storage, specify at least one CQL host with axon-server configuration.

## Step 3 - Start the server

``` -
sudo systemctl daemon-reload
sudo systemctl start axon-server
sudo systemctl status axon-server
```

This will start the `axon-server` process as the `axonops` user, which was created during the package installation.  The default listening address is `0.0.0.0:8080`.

## Package details

* Configuration File: `/etc/axonops/axon-server.yml`
* Binary: `/usr/share/axonops/axon-server`
* Logs: `/var/log/axonops/axon-server.log` 
* Systemd service: `/usr/lib/systemd/system/axon-server.service`
* Copyright : `/usr/share/doc/axonops/axon-server/copyright`
* Licenses : `/usr/share/axonops/licenses/axon-server/`


## Next - Install axon-dash

Now **axon-server** is installed, you can start installing the GUI for it: [axon-dash](../axon-dash/install.md)
