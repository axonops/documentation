# AxonOps Server Installation

## Installation

{!dynamic_pages/axon_server/os.md!}

### Configuration File Locations

The following files are installed into the local file system:

- Configuration File: `/etc/axonops/axon-server.yml`
- Binary: `/usr/share/axonops/axon-server`
- Logs: `/var/log/axonops/axon-server.log`
- Systemd service: `/usr/lib/systemd/system/axon-server.service`
- Copyright : `/usr/share/doc/axonops/axon-server/copyright`
- Licenses : `/usr/share/axonops/licenses/axon-server/`

## Configure AxonOps Server

### Configure Elasticsearch

Confirm the `network.host` and `http.port` values within
`/etc/elasticsearch/elasticsearch.yml` for the dedicated Elasticsearch instance
correspond to the values for `search_db` within `/etc/axonops/axon-server.yml`.

The following example works for the default Single-Server configuration:

```yaml
search_db:
  hosts:
    - http://localhost:9200
```

#### Basic Auth in Elasticsearch

If using Basic Auth with the default Single-Server configuration,
ensure `search_db` values are setup using the following format:

```yaml
search_db:
  hosts:
    - http://localhost:9200

  username: opensearch-user
  password: my-strong-password
```

Update the above `username` and `password` with the dedicated service account/user
[created in Elasticsearch](../elasticsearch/install.md#set-passwords-for-default-user).

#### Load Balancing for Elasticsearch

By default, AxonOps Server will only connect to the Elasticsearch nodes listed in its
configuration and will not automatically discover other nodes in the cluster.
To enable AxonOps' node discovery, set `search_db.discover_nodes:true` which will
utilize the full list of discovered nodes to round-robin requests sent to Elasticsearch.

When setting up load balancing nodes or infrastructure in front of Elasticsearch,
the load balancer has smart load balancing capabilites and AxonOps' node discovery
is not required.

### Setup AxonOps License

> This section is for Enterprise plan clients and is not needed on the Free Forever plan.

Ensure the following values are set to unlock the Enterprise features of AxonOps:

```yaml
license_key: license-key
org_name: my-company
```

Note: Both values need to match the information provided during the Enterprise
onboarding process and are case-sensitive.
These values *cannot* be found on [console.axonops.com](https://console.axonops.com).

### Configure Cassandra as Metrics Store

To use [Cassandra as AxonOps' metrics store](metricsdatabase.md),
specify at least one CQL host within the `cql_hosts` key within `/etc/axonops/axon-server.yml`.

For better performance on larger clusters (10+ nodes),
it is recommended to use Cassandra as a Metrics Storage engine.

### Sample Configuration File

The following is a sample configuration file that can be used as a quick reference:

```yaml hl_lines="7 8 33 34"
# axon-server listening address (used by axon-agents for connections)
# (env variable: AXONSERVER_HOST)
host: 0.0.0.0
# axon-server listening port for agent connections
agents_port: 1888

# axon-server listening address
# (env variable: used by axon-dash for connections)
api_host: 127.0.0.1

# axon-server HTTP API listening port (used by axon-dash)
# (AXONSERVER_PORT)
api_port: 8080

search_db:
  # Elasticsearch endpoint
  # (env variable:ELASTIC_HOSTS, comma separated list)
  hosts:
    - http://localhost:9200

  username: opensearch-user
  password: my-strong-password

  # SSL/TLS config for Elasticsearch
  skip_verify: false # Disables CA and Hostname verification

  # Configure the number of replicas per shard. Defaults to 0 if not specified.
  replicas: 0

  # Configure the number of shards per index.
  # The default value of 1 is recommended for most use cases
  shards: 1

  # Enable/disable Elasticsearch cluster discovery (sniffing).
  # Defaults to false, set to true to enable
  # Allows more nodes to be added to Elasticsearch for Metrics storage
  # without having to restart Axon-Server
  # and update search_db.hosts with all the ELK node values.
  discover_nodes: false

  # How often to perform cluster discovery.
  # Default is every 5 minutes if this is omitted
  discover_nodes_interval: 1m

  max_results: 1000

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

## Start the AxonOps Server

This following will start the `axon-server` process as the `axonops` user,
which was created during the package installation.
The default listening address is [0.0.0.0:8080](http://0.0.0.0:8080){target="_blank"}.

```bash
{!installation/axon-server/scripts/start-axon-server.sh!}
```

## Next - Install AxonOps Dashboard

Now that AxonOps Server (`axon-server`) is installed, you can start installing the GUI for it: [AxonOps Dashboard (axon-dash)](../axon-dash/install.md).
