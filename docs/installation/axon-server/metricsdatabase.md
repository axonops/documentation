---
description: "Configure metrics database for AxonOps Server. Cassandra as metrics storage backend."
meta:
  - name: keywords
    content: "metrics database, Cassandra metrics store, AxonOps storage"
---

# Using Cassandra as a Metrics Store

## Prerequisites

A dedicated Cassandra cluster is required to use Cassandra as AxonOps' metrics store.
Using a Cassandra cluster with at least 3 nodes is recommended.

For better performance on larger clusters (10+ nodes),
it is recommended to use Cassandra as a Metrics Storage engine.

Currently supported versions of Cassandra include:

- Latest GA Version
- Previous Stable Version
- Older Stable Version

For more information on Cassandra versioning, see the [Cassandra Downloads Page](https://cassandra.apache.org/_/download.html){target="_blank"}.

## Update axon-server.yml

To use a Cassandra cluster as the AxonOps metrics store, specify CQL hosts in `axon-server.yml`:

``` bash
cql_hosts :
    - 192.168.0.1:9042
    - 192.168.0.2:9042
    ...
```

By default, the AxonOps server automatically creates the necessary keyspace and tables.
You can override this behavior by specifying the following fields in `axon-server.yml`:

``` bash
cql_autocreate_tables : false
cql_keyspace : "axonops"
cql_keyspace_replication : "{ 'class' : 'NetworkTopologyStrategy', 'dc1' : 3 }"
```

Setting up at least a 3 nodes cluster with `NetworkTopologyStrategy` and a replication factor of `3` is recommended.

## Connecting to an Encrypted Cassandra Metrics Store

Setting up a Secured Socket Layer (SSL) connection to Cassandra is recommended.

When connecting to Cassandra using SSL, update the following fields in `axon-server.yml`:

``` bash
cql_ssl: true
cql_skip_verify: false
cql_ca_file: '/path/to/ca_cert'
cql_cert_file: '/path/to/cert_file'
cql_key_file: '/path/to/key_file'
```

## Additional CQL fields


Additional CQL fields are available within `axon-server.yml`, as required:

```golang
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
cql_read_consistency string (controls the consistency of read operations, defaults to LOCAL_ONE)              
cql_write_consistency string (controls the consistency of write operations, defaults to LOCAL_ONE)               
cql_lvl1_compaction_window_size int (used for the table named 'metrics5' when you let axonserver managing the tables automatically)                  
cql_lvl2_compaction_window_size int (used for the table named 'metrics60' when you let axonserver managing the tables automatically)                  
cql_lvl3_compaction_window_size int (used for the table named 'metrics720' when you let axonserver managing the tables automatically)                  
cql_lvl4_compaction_window_size int (used for the table named 'metrics7200' when you let axonserver managing the tables automatically)                  
cql_lvl5_compaction_window_size int (used for the table named 'metrics86400' when you let axonserver managing the tables automatically)                  
```

## Create AxonOps Schema

The default metrics keyspace/table definition can be found below.

``` sql
CREATE KEYSPACE axonops WITH
    replication = {'class': 'NetworkTopologyStrategy', 'dc1': '3'};

CREATE TABLE v2metrics5 (
    orgid text,
    clusterhash bigint,
    metricid bigint,
    time int,
    value float,
    PRIMARY KEY ((orgid, clusterhash, metricid), time)
) WITH CLUSTERING ORDER BY (time DESC)
    AND caching = {'keys': 'ALL', 'rows_per_partition': '256'}
    AND compaction = {'class': 'TimeWindowCompactionStrategy',
        'compaction_window_size': '1', 'compaction_window_unit': 'DAYS',
        'max_threshold': '32', 'min_threshold': '4'}
    AND default_time_to_live = 604800
    AND comment = '7 days retention for 5 seconds resolution metrics';

CREATE TABLE v2metrics60 (
    orgid text,
    clusterhash bigint,
    metricid bigint,
    time int,
    value float,
    PRIMARY KEY ((orgid, clusterhash, metricid), time)
) WITH CLUSTERING ORDER BY (time DESC)
    AND caching = {'keys': 'ALL', 'rows_per_partition': '256'}
    AND compaction = {'class': 'TimeWindowCompactionStrategy',
        'compaction_window_size': '1', 'compaction_window_unit': 'DAYS',
        'max_threshold': '32', 'min_threshold': '4'}
    AND default_time_to_live = 2592000
    AND comment = '30 days retention for 60 seconds resolution metrics';

CREATE TABLE v2metrics720 (
    orgid text,
    clusterhash bigint,
    metricid bigint,
    time int,
    value float,
    PRIMARY KEY ((orgid, clusterhash, metricid), time)
) WITH CLUSTERING ORDER BY (time DESC)
    AND caching = {'keys': 'ALL', 'rows_per_partition': '256'}
    AND compaction = {'class': 'TimeWindowCompactionStrategy',
        'compaction_window_size': '4', 'compaction_window_unit': 'DAYS',
        'max_threshold': '32', 'min_threshold': '4'}
    AND default_time_to_live = 5184000
    AND comment = '60 days retention for 720 seconds resolution metrics';

CREATE TABLE v2metrics7200 (
    orgid text,
    clusterhash bigint,
    metricid bigint,
    time int,
    value float,
    PRIMARY KEY ((orgid, clusterhash, metricid), time)
) WITH CLUSTERING ORDER BY (time DESC)
    AND caching = {'keys': 'ALL', 'rows_per_partition': '256'}
    AND compaction = {'class': 'TimeWindowCompactionStrategy',
        'compaction_window_size': '30', 'compaction_window_unit': 'DAYS',
        'max_threshold': '32', 'min_threshold': '4'}
    AND default_time_to_live = 15552000
    AND comment = '180 days retention for 7200 seconds resolution metrics';

CREATE TABLE v2metrics86400 (
    orgid text,
    clusterhash bigint,
    metricid bigint,
    time int,
    value float,
    PRIMARY KEY ((orgid, clusterhash, metricid), time)
) WITH CLUSTERING ORDER BY (time DESC)
    AND caching = {'keys': 'ALL', 'rows_per_partition': '365'}
    AND compaction = {'class': 'TimeWindowCompactionStrategy',
        'compaction_window_size': '60', 'compaction_window_unit': 'DAYS',
        'max_threshold': '32', 'min_threshold': '4'}
    AND default_time_to_live = 31536000
    AND comment = '365 days retention for 86400 seconds resolution metrics';
```
