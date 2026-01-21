---
title: "cassandra-stress"
description: "Cassandra-stress benchmarking tool for load testing, capacity planning, and performance regression testing. Configure workloads, measure throughput and latency."
meta:
  - name: keywords
    content: "cassandra-stress, load testing, benchmarking tool"
search:
  boost: 3
---

# cassandra-stress

The official Cassandra benchmarking and load testing tool.

## Overview

cassandra-stress is a Java-based tool for:
- Benchmarking cluster performance
- Load testing before production
- Capacity planning
- Regression testing

## Basic Commands

### Write Test

```bash
# Insert 1 million rows
cassandra-stress write n=1000000

# With specific thread count
cassandra-stress write n=1000000 -rate threads=50

# With consistency level
cassandra-stress write n=1000000 cl=LOCAL_QUORUM

# Against specific nodes
cassandra-stress write n=1000000 -node 192.168.1.10,192.168.1.11
```

### Read Test

```bash
# Read 1 million rows (requires prior write)
cassandra-stress read n=1000000 -rate threads=50

# No warmup
cassandra-stress read n=1000000 no-warmup
```

### Mixed Workload

```bash
# 50% read, 50% write
cassandra-stress mixed ratio\(write=1,read=1\) n=1000000

# 70% read, 30% write
cassandra-stress mixed ratio\(read=7,write=3\) n=1000000

# Duration-based
cassandra-stress mixed ratio\(read=7,write=3\) duration=10m
```

## Connection Options

### Target Nodes

```bash
-node 192.168.1.10
-node 192.168.1.10,192.168.1.11,192.168.1.12
```

### Authentication

```bash
-mode native cql3 user=cassandra password=cassandra
```

### SSL/TLS

```bash
-transport "truststore=/path/truststore.jks truststore-password=pass"

# Full SSL config
-transport "truststore=/path/truststore.jks truststore-password=pass keystore=/path/keystore.jks keystore-password=pass"
```

### CQL Protocol

```bash
-mode native cql3
-port native=9042
```

## Rate Limiting

### Thread-Based

```bash
# Fixed thread count
-rate threads=100

# Thread range (auto-tune)
-rate threads>=50 threads<=200
```

### Throughput-Based

```bash
# Target ops/sec
-rate threads=50 throttle=10000/s

# Fixed rate
-rate "fixed=5000/s"
```

## Custom Schema

### YAML Profile

```yaml
# user_profile.yaml
keyspace: stress_test
keyspace_definition: |
  CREATE KEYSPACE stress_test WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3
  };

table: users
table_definition: |
  CREATE TABLE users (
    user_id uuid,
    username text,
    email text,
    created_at timestamp,
    profile_data blob,
    PRIMARY KEY (user_id)
  )

columnspec:
  - name: user_id
    size: fixed(36)
    population: uniform(1..10000000)
  - name: username
    size: gaussian(5..20)
    population: uniform(1..10000000)
  - name: email
    size: gaussian(15..50)
  - name: created_at
    cluster: fixed(1)
  - name: profile_data
    size: gaussian(100..1000)

insert:
  partitions: fixed(1)
  batchtype: UNLOGGED

queries:
  read_user:
    cql: SELECT * FROM users WHERE user_id = ?
    fields: samerow
  read_username:
    cql: SELECT username, email FROM users WHERE user_id = ?
    fields: samerow
```

### Run with Profile

```bash
# Insert data
cassandra-stress user profile=user_profile.yaml \
    ops\(insert=1\) n=1000000

# Mixed operations
cassandra-stress user profile=user_profile.yaml \
    ops\(insert=1,read_user=3\) duration=30m

# Specific query
cassandra-stress user profile=user_profile.yaml \
    ops\(read_user=1\) n=500000
```

## Column Specifications

### Size Distributions

```yaml
columnspec:
  # Fixed size
  - name: id
    size: fixed(36)

  # Gaussian distribution
  - name: data
    size: gaussian(100..500)  # mean ~300

  # Uniform distribution
  - name: content
    size: uniform(50..200)

  # Exponential distribution
  - name: blob
    size: exp(100..10000)
```

### Population Distributions

```yaml
columnspec:
  - name: user_id
    population: uniform(1..1000000)

  - name: partition_key
    population: gaussian(1..100000)

  # Sequence (incremental)
  - name: seq_id
    population: seq(1..10000000)
```

## Output and Logging

### Log to File

```bash
cassandra-stress write n=1000000 -log file=stress.log
```

### Graph Output

```bash
cassandra-stress write n=1000000 -graph file=results.html title="Write Test"
```

### Interval Reporting

```bash
# Report every 5 seconds
cassandra-stress write n=1000000 -log interval=5
```

## Understanding Results

### Key Metrics

```
Results:
Op rate       : 45,231 op/s       # Operations per second
Partition rate: 45,231 pk/s       # Partitions per second
Row rate      : 45,231 row/s      # Rows per second
Latency mean  :  4.4 ms           # Average latency
Latency median:  2.1 ms           # 50th percentile
Latency 95th  : 12.3 ms           # 95th percentile
Latency 99th  : 35.2 ms           # 99th percentile
Latency max   : 245.1 ms          # Maximum observed
Total errors  :     0             # Error count
```

### Performance Guidelines

| Metric | Good | Warning | Bad |
|--------|------|---------|-----|
| p95 latency | < 20ms | 20-50ms | > 50ms |
| p99 latency | < 50ms | 50-100ms | > 100ms |
| Error rate | 0% | < 0.1% | > 0.1% |

## Counter Operations

```bash
# Counter writes
cassandra-stress counter_write n=1000000 -rate threads=50

# Counter reads
cassandra-stress counter_read n=1000000
```

## Advanced Examples

### Warm-Up Then Test

```bash
# Warm-up phase
cassandra-stress write n=100000 -rate threads=10

# Actual test
cassandra-stress write n=5000000 -rate threads=100
```

### Multiple DCs

```bash
cassandra-stress write n=1000000 \
    -node dc1-node1,dc1-node2 \
    cl=LOCAL_QUORUM \
    -rate threads=100
```

### Compaction Stress Test

```bash
# Heavy writes to trigger compaction
cassandra-stress write n=10000000 \
    -rate threads=200 \
    -schema "replication(strategy=NetworkTopologyStrategy,dc1=3)" \
    -log interval=10
```

### Time-Series Workload

```yaml
# timeseries_profile.yaml
keyspace: metrics
table: sensor_data
table_definition: |
  CREATE TABLE sensor_data (
    sensor_id text,
    bucket text,
    ts timestamp,
    value double,
    PRIMARY KEY ((sensor_id, bucket), ts)
  ) WITH CLUSTERING ORDER BY (ts DESC)

columnspec:
  - name: sensor_id
    size: fixed(10)
    population: uniform(1..1000)
  - name: bucket
    size: fixed(10)
  - name: ts
    cluster: uniform(1..1000)
  - name: value
    population: gaussian(0..100)
```

## Troubleshooting

### Connection Errors

```bash
# Verify connectivity
cassandra-stress write n=1 -node 192.168.1.10

# Check native transport
nodetool status
```

### Out of Memory

```bash
# Increase stress tool heap
export JVM_OPTS="-Xms4G -Xmx4G"
cassandra-stress write n=10000000
```

### Throttling Issues

```bash
# Reduce thread count
-rate threads=25

# Add throttle limit
-rate threads=50 throttle=5000/s
```

---

## Next Steps

- **[Benchmarking](../../operations/performance/benchmarking/index.md)** - Benchmarking guide
- **[Performance](../../operations/performance/index.md)** - Performance tuning
- **[Monitoring](../../operations/monitoring/index.md)** - Monitor during tests
