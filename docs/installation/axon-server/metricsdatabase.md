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

By default, axonserver will automatically creates the necessary keyspace and tables.
You can override this behavior by specifying the following field in **axon-server.yml**:
``` bash
cql_autocreate_tables : false
cql_keyspace : "axonops"
cql_keyspace_replication : "{ 'class' : 'SimpleStrategy', 'replication_factor' : 1 }"
```

We recommend to setup at least a 3 nodes cluster with **NetworkTopologyStrategy** and a **replication_factor** of **3**.

## Connecting to encrypted Cassandra metrics store
We recommend to setup a Secured Socket Layer to Cassandra with the following field in **axon-server.yml**:
``` bash
cql_ssl: true
cql_skip_verify: false
cql_ca_file: '/path/to/ca_cert'
cql_cert_file: '/path/to/cert_file'
cql_key_file: '/path/to/key_file'
```

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
cql_read_consistency string                
cql_write_consistency string                
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
    PRIMARY KEY ((orgid, metricid), time)) WITH CLUSTERING ORDER BY (time DESC)
    AND default_time_to_live = 2592000
    AND compaction = { 'class' : 'TimeWindowCompactionStrategy', 'compaction_window_unit' : 'DAYS', 'compaction_window_size' : '12'}
    ;


CREATE TABLE IF NOT EXISTS axonops.metrics60 (
		orgid text,
		metricid int, 
		time int,
		value float,
		PRIMARY KEY ((orgid, metricid), time)) WITH CLUSTERING ORDER BY (time DESC)
	 AND default_time_to_live = 14515200
	 AND compaction = { 'class' : 'TimeWindowCompactionStrategy', 'compaction_window_unit' : 'DAYS', 'compaction_window_size' : '1'}
	 ;

CREATE TABLE IF NOT EXISTS axonops.metrics720 (
		orgid text,
		metricid int, 
		time int,
		value float,
		PRIMARY KEY ((orgid, metricid), time)) WITH CLUSTERING ORDER BY (time DESC)
	 AND default_time_to_live = 14515200
	 AND compaction = { 'class' : 'TimeWindowCompactionStrategy', 'compaction_window_unit' : 'DAYS', 'compaction_window_size' : '1'}
	 ;

CREATE TABLE IF NOT EXISTS axonops.metrics7200 (
		orgid text,
		metricid int, 
		time int,
		value float,
		PRIMARY KEY ((orgid, metricid), time)) WITH CLUSTERING ORDER BY (time DESC)
	 AND default_time_to_live = 63037440
	 AND compaction = { 'class' : 'TimeWindowCompactionStrategy', 'compaction_window_unit' : 'DAYS', 'compaction_window_size' : '10'}
	 ;

CREATE TABLE IF NOT EXISTS axonops.metrics86400 (
		orgid text,
		metricid int, 
		time int,
		value float,
		PRIMARY KEY ((orgid, metricid), time)) WITH CLUSTERING ORDER BY (time DESC)
	 AND default_time_to_live = 94608000
	 AND compaction = { 'class' : 'TimeWindowCompactionStrategy', 'compaction_window_unit' : 'DAYS', 'compaction_window_size' : '120'}
	 ;

```