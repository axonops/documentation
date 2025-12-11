# nodetool tablehistograms

Displays latency histograms for a specific table.

## Synopsis

```bash
nodetool [connection_options] tablehistograms <keyspace> <table>
```

## Description

The `tablehistograms` command shows percentile distributions for read/write latencies, SSTable counts, partition sizes, and cell counts for a specific table.

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| keyspace | Yes | Keyspace name |
| table | Yes | Table name |

## Examples

```bash
nodetool tablehistograms my_keyspace users
```

**Output:**
```
my_keyspace/users histograms
Percentile      SSTables     Write Latency      Read Latency    Partition Size        Cell Count
                                  (micros)          (micros)           (bytes)
50%                 1.00             35.43            182.79             1747             14
75%                 1.00             50.55            310.55             3495             20
95%                 2.00            103.16            746.59            10485             35
98%                 2.00            152.32           1266.68            20971             51
99%                 3.00            258.47           2146.30            41943             62
Min                 0.00             14.24             42.51              125              5
Max                 5.00           1489.45          10066.33          5242880            219
```

## Interpreting Results

| Metric | Target |
|--------|--------|
| SSTables p99 | < 5 |
| Write Latency p99 | < 1000μs |
| Read Latency p99 | < 5000μs |
| Partition Size p99 | < 10MB |

## Related Commands

- [tablestats](tablestats.md) - Table statistics
- [proxyhistograms](proxyhistograms.md) - Coordinator latencies

## Related Documentation

- [Performance - Query Optimization](../../../operations/performance/query-optimization/index.md)
