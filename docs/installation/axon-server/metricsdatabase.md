# axon-server metrics database

# Using Cassandra as a metrics store
You can use Cassandra as a metrics store instead of Elasticsearch for better performances.
To start using a CQL store you just have to specify CQL hosts in **axon-server.yml**:
``` bash
cql_hosts :
    - 192.168.0.1:9042
    - 192.168.0.2:9042
    ...
```

By default, the AxonOps server automatically creates the necessary keyspace and tables.
You can override this behavior by specifying the following field in **axon-server.yml**:
``` bash
cql_autocreate_tables : false
cql_keyspace : "axonops"
cql_keyspace_replication : "{ 'class' : 'SimpleStrategy', 'replication_factor' : 1 }"
```

We recommend setting up at least a 3 nodes cluster with **NetworkTopologyStrategy** and a **replication_factor** of **3**.

## Connecting to encrypted Cassandra metrics store
We recommend setting up a Secured Socket Layer connection to Cassandra with the following fields in **axon-server.yml**:
``` bash
cql_ssl: true
cql_skip_verify: false
cql_ca_file: '/path/to/ca_cert'
cql_cert_file: '/path/to/cert_file'
cql_key_file: '/path/to/key_file'
```

## Metrics cache recommendations
When using Cassandra as a metrics store the AxonOps server can cache metrics data in memory to further improve
performance. This is configured using the `cql_metrics_cache_max_items` and `cql_metrics_cache_max_size_mb` options 
in **axon-server.yml**. The default values are shown here:
```yaml
cql_metrics_cache_max_items: 5000000
cql_metrics_cache_max_size_mb: 400
```

The recommended settings for these options are as follows:

| Cassandra Nodes | cql_metrics_cache_max_items | cql_metrics_cache_max_size_mb |
|-----------------|-----------------------------|-------------------------------|
| <10             | 5000000                     | 1000                          |
| <50             | 5000000                     | 4000                          |
| 100             | 10000000                    | 10000                         |
| 200             | 10000000                    | 20000                         |

These sizes can be tuned to balance memory use in AxonOps against the read workload on Cassandra.
When tuning these parameters it is recommended to set `cql_metrics_cache_max_items` to a high value and limit the
cache size with `cql_metrics_cache_max_size_mb`.

## Other CQL fields
You can also specify the following fields:
``` bash
cql_proto_version int                   
cql_batch_size  int                   
cql_page_size int                   
cql_local_dc string                
cql_username string                
cql_password string                
cql_max_concurrent_reads int                   
cql_retrypolicy_numretries int                   
cql_retrypolicy_min string "1s"
cql_retrypolicy_max string "10s"
cql_reconnectionpolicy_maxretries int                   
cql_reconnectionpolicy_initialinterval string "1s"
cql_reconnectionpolicy_maxinterval string  "10s"
cql_metrics_cache_max_size_mb int64 in MB               
cql_metrics_cache_max_items  int64 in MB                        
cql_read_consistency string (controls the consistency of read operations, defaults to LOCAL_ONE)              
cql_write_consistency string (controls the consistency of write operations, defaults to LOCAL_ONE)               
cql_lvl1_compaction_window_size int (used for the table named 'metrics5' when you let axonserver managing the tables automatically)                  
cql_lvl2_compaction_window_size int (used for the table named 'metrics60' when you let axonserver managing the tables automatically)                  
cql_lvl3_compaction_window_size int (used for the table named 'metrics720' when you let axonserver managing the tables automatically)                  
cql_lvl4_compaction_window_size int (used for the table named 'metrics7200' when you let axonserver managing the tables automatically)                  
cql_lvl5_compaction_window_size int (used for the table named 'metrics86400' when you let axonserver managing the tables automatically)                  
```


The CQL for the default tables are the following:
``` bash
CREATE TABLE IF NOT EXISTS axonops.metrics5 (
    orgid text,
    metricid int,
    time int,
    value float,
    PRIMARY KEY ((orgid, metricid), time)
) WITH CLUSTERING ORDER BY (time DESC)
   AND caching = {'keys': 'ALL', 'rows_per_partition': '256'}
   AND compaction = {'class': 'TimeWindowCompactionStrategy', 'compaction_window_size': '1', 'compaction_window_unit': 'DAYS', 'max_threshold': '32', 'min_threshold': '4'}
   AND default_time_to_live = 604800
   AND comment = '7 days retention for 5 seconds resolution metrics';

CREATE TABLE IF NOT EXISTS axonops.metrics60 (
    orgid text,
    metricid int,
    time int,
    value float,
    PRIMARY KEY ((orgid, metricid), time)
) WITH CLUSTERING ORDER BY (time DESC)
   AND caching = {'keys': 'ALL', 'rows_per_partition': '256'}
   AND compaction = {'class': 'TimeWindowCompactionStrategy', 'compaction_window_size': '1', 'compaction_window_unit': 'DAYS', 'max_threshold': '32', 'min_threshold': '4'}
   AND default_time_to_live = 2592000
   AND comment = '30 days retention for 60 seconds resolution metrics';

CREATE TABLE IF NOT EXISTS axonops.metrics720 (
    orgid text,
    metricid int,
    time int,
    value float,
    PRIMARY KEY ((orgid, metricid), time)
) WITH CLUSTERING ORDER BY (time DESC)
   AND caching = {'keys': 'ALL', 'rows_per_partition': '256'}
   AND compaction = {'class': 'TimeWindowCompactionStrategy', 'compaction_window_size': '4', 'compaction_window_unit': 'DAYS', 'max_threshold': '32', 'min_threshold': '4'}
   AND default_time_to_live = 5184000
   AND comment = '60 days retention for 720 seconds resolution metrics';

CREATE TABLE IF NOT EXISTS axonops.metrics7200 (
    orgid text,
    metricid int,
    time int,
    value float,
    PRIMARY KEY ((orgid, metricid), time)
) WITH CLUSTERING ORDER BY (time DESC)
   AND caching = {'keys': 'ALL', 'rows_per_partition': '256'}
   AND compaction = {'class': 'TimeWindowCompactionStrategy', 'compaction_window_size': '30', 'compaction_window_unit': 'DAYS', 'max_threshold': '32', 'min_threshold': '4'}
   AND default_time_to_live = 15552000
   AND comment = '180 days retention for 7200 seconds resolution metrics';

CREATE TABLE IF NOT EXISTS axonops.metrics86400 (
    orgid text,
    metricid int,
    time int,
    value float,
    PRIMARY KEY ((orgid, metricid), time)
) WITH CLUSTERING ORDER BY (time DESC)
   AND caching = {'keys': 'ALL', 'rows_per_partition': '365'}
   AND compaction = {'class': 'TimeWindowCompactionStrategy', 'compaction_window_size': '60', 'compaction_window_unit': 'DAYS', 'max_threshold': '32', 'min_threshold': '4'}
   AND default_time_to_live = 31536000
   AND comment = '365 days retention for 86400 seconds resolution metrics';
```
