---
title: "Cassandra Performance Benchmarking"
description: "Cassandra benchmarking guide. Test performance with cassandra-stress."
meta:
  - name: keywords
    content: "Cassandra benchmarking, cassandra-stress, performance testing"
---

# Cassandra Benchmarking

Measure and validate Cassandra cluster performance.

## cassandra-stress

The official benchmarking tool included with Cassandra.

### Basic Usage

```bash
# Write test (1M operations)
cassandra-stress write n=1000000 -rate threads=50

# Read test
cassandra-stress read n=1000000 -rate threads=50

# Mixed workload (50% read, 50% write)
cassandra-stress mixed ratio\(write=1,read=1\) n=1000000 -rate threads=50
```

### Connection Options

```bash
cassandra-stress write n=1000000 \
    -node 192.168.1.10,192.168.1.11,192.168.1.12 \
    -rate threads=100 \
    -mode native cql3 \
    -transport "truststore=/path/to/truststore.jks truststore-password=pass" \
    -log file=results.log
```

### Custom Schema

```bash
# Create YAML profile
cat > user_profile.yaml << 'EOF'
keyspace: test_ks
keyspace_definition: |
  CREATE KEYSPACE test_ks WITH replication = {'class': 'NetworkTopologyStrategy', 'dc1': 3};

table: users
table_definition: |
  CREATE TABLE users (
    user_id uuid PRIMARY KEY,
    name text,
    email text,
    created_at timestamp
  )

columnspec:
  - name: user_id
    size: fixed(36)
  - name: name
    size: gaussian(10..50)
  - name: email
    size: gaussian(20..50)
  - name: created_at

insert:
  partitions: fixed(1)
  batchtype: UNLOGGED

queries:
  read_by_id:
    cql: SELECT * FROM users WHERE user_id = ?
    fields: samerow
EOF

# Run with profile
cassandra-stress user profile=user_profile.yaml ops\(insert=3,read_by_id=7\) n=1000000
```

## Key Metrics to Measure

### Throughput

```
Op rate       : Operations per second
Partition rate: Partitions written/read per second
Row rate      : Rows affected per second
```

### Latency

```
Latency mean  : Average latency
Latency median: 50th percentile
Latency 95th  : 95th percentile (target < 50ms)
Latency 99th  : 99th percentile
Latency max   : Maximum observed latency
```

## Benchmark Scenarios

### Write Performance

```bash
# Sequential writes
cassandra-stress write n=5000000 cl=LOCAL_QUORUM \
    -rate threads=200 \
    -node node1,node2,node3

# Expected: 20,000-100,000 ops/sec per node (varies by hardware)
```

### Read Performance

```bash
# Random reads
cassandra-stress read n=5000000 cl=LOCAL_QUORUM \
    -rate threads=200 \
    -node node1,node2,node3

# Expected: 10,000-50,000 ops/sec per node
```

### Mixed Workload

```bash
# 70% read, 30% write (typical application)
cassandra-stress mixed ratio\(read=7,write=3\) n=5000000 cl=LOCAL_QUORUM \
    -rate threads=200
```

### Counter Workload

```bash
cassandra-stress counter_write n=1000000 \
    -rate threads=50
```

## YCSB (Yahoo Cloud Serving Benchmark)

Alternative benchmark suite for database comparison.

### Setup

```bash
# Clone YCSB
git clone https://github.com/brianfrankcooper/YCSB.git
cd YCSB

# Build Cassandra binding
mvn -pl site.ycsb:cassandra-binding -am clean package
```

### Run Workloads

```bash
# Load data
./bin/ycsb load cassandra-cql -s -P workloads/workloada \
    -p hosts="node1,node2,node3" \
    -p recordcount=1000000

# Run workload A (50% read, 50% update)
./bin/ycsb run cassandra-cql -s -P workloads/workloada \
    -p hosts="node1,node2,node3" \
    -p operationcount=1000000
```

### YCSB Workloads

| Workload | Read | Update | Insert | Scan | RMW |
|----------|------|--------|--------|------|-----|
| A | 50% | 50% | - | - | - |
| B | 95% | 5% | - | - | - |
| C | 100% | - | - | - | - |
| D | 95% | - | 5% | - | - |
| E | - | - | 5% | 95% | - |
| F | 50% | - | - | - | 50% |

## Interpreting Results

### Good Performance Indicators

```
✓ Op rate consistent across nodes
✓ p99 latency < 100ms
✓ No timeouts or errors
✓ Stable throughput over time
✓ GC pauses < 200ms
```

### Problem Indicators

```
✗ High latency variance
✗ Increasing latency over time
✗ Error rate > 0.1%
✗ Uneven distribution across nodes
✗ GC pauses > 500ms
```

## Benchmark Best Practices

1. **Warm up cluster** - Run shorter test first
2. **Use realistic data** - Match production data patterns
3. **Test at scale** - Use production-like data volumes
4. **Run multiple times** - Average results across runs
5. **Monitor during tests** - Watch GC, I/O, CPU
6. **Test failure scenarios** - One node down, network partition

## Sample Results Interpretation

```
Results:
Op rate                   :   45,231 op/s
Partition rate            :   45,231 pk/s
Row rate                  :   45,231 row/s
Latency mean              :    4.4 ms
Latency median            :    2.1 ms
Latency 95th percentile   :   12.3 ms
Latency 99th percentile   :   35.2 ms
Latency 99.9th percentile :   89.4 ms
Latency max               :  245.1 ms
Total partitions          : 5,000,000
Total errors              :        0
```

**Analysis:**
- 45K ops/sec is good for 3-node cluster
- Median 2.1ms is excellent
- p99 at 35ms is acceptable
- No errors indicates stability

---

## Next Steps

- **[cassandra-stress](../../../tools/cassandra-stress/index.md)** - Full tool reference
- **[Query Optimization](../query-optimization/index.md)** - Optimize slow queries
- **[Key Metrics](../../monitoring/key-metrics/index.md)** - Production monitoring
