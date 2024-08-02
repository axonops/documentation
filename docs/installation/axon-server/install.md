## Step 3 - axon-server configurations


Make sure **elastic_host** and **elastic_port** are corresponding to your Elasticsearch instance.

* `/etc/axonops/axon-server.yml`

``` yaml hl_lines="3 4"
host: 0.0.0.0  # axon-server listening address (used by axon-dash and axon-agent) (env variable: AXONSERVER_HOST)
api_port: 8080 # axon-server HTTP API listening port (used by axon-dash) (AXONSERVER_PORT)
agents_port: 1888 # axon-server listening port for agent connections 
elastic_hosts: # Elasticsearch endpoint (env variable:ELASTIC_HOSTS, comma separated list)
  - http://localhost:9200
#integrations_proxy: # proxy endpoint for integrations. (INTEGRATIONS_PROXY)


# AxonOps licensing
license_key: license-key
org_name: my-company

# SSL/TLS Settings
tls:
  mode: "disabled" # disabled, TLS
  # Only set if mode is TLS
  skipVerify: false
  caFile: "path_to_certs_on_cassandra_node.crt" 
  certFile: "path_to_certs_on_cassandra_node.crt"
  keyFile: "path_to_key_file_on_cassandra_node.key"

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
#cql_proto_version: 4  # (CQL_PROTO_VERSION)
#cql_max_concurrent_reads: 1000  # (CQL_MAX_CONCURRENT_READS)
#cql_batch_size: 1  # (CQL_BATCH_SIZE)
#cql_page_size: 10  # (CQL_PAGE_SIZE)
#cql_autocreate_tables: true # (CQL_AUTO_CREATE_TABLES) this will tell axon-server to automatically create the metrics tables (true is recommended)
#cql_keyspace_replication: "{ 'class' : 'SimpleStrategy', 'replication_factor' : 1 }" # (CQL_KS_REPLICATION) keyspace replication for the metrics tables
#cql_retrypolicy_numretries: 3  # (CQL_RETRY_POLICY_NUM_RETRIES)
#cql_retrypolicy_min: 1s  # (CQL_RETRY_POLICY_MIN)
#cql_retrypolicy_max: 10s  # (CQL_RETRY_POLICY_MAX)
#cql_reconnectionpolicy_maxretries: 10 # (CQL_RECONNECTION_POLICY_MAX_RETRIES)
#cql_reconnectionpolicy_initialinterval: 1s # (CQL_RECONNECTION_POLICY_INITIAL_INTERVAL)
#cql_reconnectionpolicy_maxinterval: 10s # (CQL_RECONNECTION_POLICY_MAX_INTERVAL)
#cql_metrics_cache_max_size_mb: 100  #MB # (CQL_METRICS_CACHE_MAX_SIZE_MB)
#cql_read_consistency: "LOCAL_ONE" # (CQL_READ_CONSISTENCY) #One of the following:	ANY, ONE, TWO, THREE, QUORUM, ALL, LOCAL_QUORUM, EACH_QUORUM, LOCAL_ONE
#cql_write_consistency: "LOCAL_ONE" # (CQL_WRITE_CONSISTENCY) #One of the following:	ANY, ONE, TWO, THREE, QUORUM, ALL, LOCAL_QUORUM, EACH_QUORUM, LOCAL_ONE
#cql_lvl1_compaction_window_size: 12 # (CQL_LVL1_COMPACTION_WINDOW_SIZE)
#cql_lvl2_compaction_window_size: 1 # (CQL_LVL2_COMPACTION_WINDOW_SIZE)
#cql_lvl3_compaction_window_size: 1 # (CQL_LVL3_COMPACTION_WINDOW_SIZE)
#cql_lvl4_compaction_window_size: 10 # (CQL_LVL4_COMPACTION_WINDOW_SIZE)
#cql_lvl5_compaction_window_size: 120 # (CQL_LVL5_COMPACTION_WINDOW_SIZE)

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


# Storage options for PDF reports
# Override the default local path of /var/lib/axonops/reports
#report_storage_path: /my/reports/storage/directory

# Alternatively store PDF reports in an object store by providing report_storage_config
#report_storage_path: my-reports-s3-bucket/reports-folder
#report_storage_config:
#  type: s3
#  provider: AWS
#  access_key_id: MY_ACCESS_KEY_ID
#  secret_access_key: MY_SECRET_ACCESS_KEY
#  region: us-east-1
#  acl: private
#  server_side_encryption: AES256
#  storage_class: STANDARD
```
> For better performances on large clusters (100+ nodes), you can use a CQL store for the metrics such as **Cassandra**. To opt-in for CQL metrics storage, specify at least one CQL host with axon-server configuration.

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





