# AxonOps Table Dashboard Metrics Mapping

This document maps the metrics used in the AxonOps Table dashboard.

## Dashboard Overview

The Table dashboard provides comprehensive table-level metrics including coordinator and replica statistics, latency metrics, throughput, data distribution, and performance indicators. It helps identify table-specific issues and optimization opportunities.

## Metrics Mapping

### Data Distribution Metrics

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `cas_Table_LiveDiskSpaceUsed` | Live data size per table | `keyspace`, `scope` (table), `function=Count`, `dc`, `rack`, `host_id` |

### Coordinator Metrics (Table-level)

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `cas_Table_CoordinatorReadLatency` | Read latency at coordinator level | `keyspace`, `scope` (table), `function` (percentiles/Count), `axonfunction` (rate), `dc`, `rack`, `host_id` |
| `cas_Table_CoordinatorWriteLatency` | Write latency at coordinator level | `keyspace`, `scope` (table), `function` (percentiles/Count), `axonfunction` (rate), `dc`, `rack`, `host_id` |
| `cas_Table_CoordinatorScanLatency` | Range scan latency at coordinator | `keyspace`, `scope` (table), `function` (percentiles/Count), `axonfunction` (rate), `dc`, `rack`, `host_id` |

### Replica Metrics (Local)

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `cas_Table_ReadLatency` | Local read latency | `keyspace`, `scope` (table), `function` (percentiles/Count), `axonfunction` (rate), `dc`, `rack`, `host_id` |
| `cas_Table_WriteLatency` | Local write latency | `keyspace`, `scope` (table), `function` (percentiles/Count), `axonfunction` (rate), `dc`, `rack`, `host_id` |
| `cas_Table_RangeLatency` | Local range query latency | `keyspace`, `scope` (table), `function` (percentiles/Count), `axonfunction` (rate), `dc`, `rack`, `host_id` |

### Partition and SSTable Metrics

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `cas_Table_MeanPartitionSize` | Average partition size | `keyspace`, `scope` (table), `dc`, `rack`, `host_id` |
| `cas_Table_MaxPartitionSize` | Maximum partition size | `keyspace`, `scope` (table), `dc`, `rack`, `host_id` |
| `cas_Table_EstimatedPartitionCount` | Estimated number of partitions | `keyspace`, `scope` (table), `dc`, `rack`, `host_id` |
| `cas_Table_LiveSSTableCount` | Number of live SSTables | `keyspace`, `scope` (table), `dc`, `rack`, `host_id` |
| `cas_Table_SSTablesPerReadHistogram` | SSTables accessed per read | `keyspace`, `scope` (table), `function` (percentiles), `dc`, `rack`, `host_id` |

### Performance Indicators

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `cas_Table_TombstoneScannedHistogram` | Tombstones scanned per query | `keyspace`, `scope` (table), `function` (percentiles), `dc`, `rack`, `host_id` |
| `cas_Table_SpeculativeRetries` | Speculative retry attempts | `keyspace`, `scope` (table), `function=Count`, `axonfunction` (rate), `dc`, `rack`, `host_id` |
| `cas_Table_BloomFilterFalseRatio` | Bloom filter false positive ratio | `keyspace`, `scope` (table), `dc`, `rack`, `host_id` |
| `cas_Table_BloomFilterDiskSpaceUsed` | Disk space used by bloom filters | `keyspace`, `scope` (table), `dc`, `rack`, `host_id` |

### Memory Metrics

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `cas_Table_AllMemtablesHeapSize` | Heap memory used by memtables | `keyspace`, `scope` (table), `dc`, `rack`, `host_id` |
| `cas_Table_AllMemtablesOffHeapSize` | Off-heap memory used by memtables | `keyspace`, `scope` (table), `dc`, `rack`, `host_id` |

### JVM Garbage Collection Metrics

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `jvm_GarbageCollector_G1_Young_Generation` | G1 young generation GC | `function` (CollectionTime/CollectionCount), `axonfunction` (rate), `dc`, `rack`, `host_id` |
| `jvm_GarbageCollector_Shenandoah_Cycles` | Shenandoah GC cycles | `function` (CollectionCount), `axonfunction` (rate), `dc`, `rack`, `host_id` |
| `jvm_GarbageCollector_Shenandoah_Pauses` | Shenandoah GC pauses | `function` (CollectionTime), `axonfunction` (rate), `dc`, `rack`, `host_id` |
| `jvm_GarbageCollector_ZGC` | ZGC garbage collector | `function` (CollectionTime/CollectionCount), `axonfunction` (rate), `dc`, `rack`, `host_id` |

## Query Examples

### Tables Overview Section
```promql
# Table Data Size Distribution (Pie Chart)
sum by (keyspace,scope) (cas_Table_LiveDiskSpaceUsed{function='Count',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'})

# Coordinator Table Reads Distribution (Pie Chart)
sum by (keyspace,scope) (cas_Table_CoordinatorReadLatency{axonfunction='rate',dc=~'$dc',rack=~'$rack',host_id=~'$host_id',function='Count'})

# Coordinator Table Writes Distribution (Pie Chart)
sum by (keyspace, scope) (cas_Table_CoordinatorWriteLatency{dc=~'$dc',rack=~'$rack',host_id=~'$host_id',axonfunction='rate',function=~'Count'})
```

### Coordinator Table Statistics
```promql
# Max Coordinator Read Latency
max(cas_Table_CoordinatorReadLatency{dc=~'$dc',rack=~'$rack',host_id=~'$host_id',function='$percentile',keyspace=~'$keyspace',scope=~'$scope'}) by ($groupBy,keyspace,scope)

# Max Coordinator Write Latency
max(cas_Table_CoordinatorWriteLatency{dc=~'$dc',rack=~'$rack',host_id=~'$host_id',function='$percentile',keyspace=~'$keyspace',scope=~'$scope'}) by ($groupBy,keyspace,scope)

# Max Coordinator Range Read Latency
max(cas_Table_CoordinatorScanLatency{dc=~'$dc',rack=~'$rack',host_id=~'$host_id',function=~'$percentile',keyspace=~'$keyspace',scope=~'$scope'}) by ($groupBy,keyspace,scope)

# Total Coordinator Reads/sec
sum (cas_Table_CoordinatorReadLatency{dc=~'$dc',rack=~'$rack',host_id=~'$host_id',axonfunction='rate',function=~'Count',keyspace=~'$keyspace',scope=~'$scope'}) by ($groupBy,keyspace,scope)

# Average Coordinator Range Reads/sec
avg(cas_Table_CoordinatorScanLatency{dc=~'$dc',rack=~'$rack',host_id=~'$host_id',axonfunction='rate',function=~'Count',keyspace=~'$keyspace',scope=~'$scope'}) by ($groupBy,keyspace,scope)

# Total Coordinator Writes/sec
sum (cas_Table_CoordinatorWriteLatency{dc=~'$dc',rack=~'$rack',host_id=~'$host_id',axonfunction='rate',function='Count',keyspace=~'$keyspace',scope=~'$scope'}) by ($groupBy,keyspace,scope)
```

### Table Replica Statistics
```promql
# Average Replica Read Latency
avg(cas_Table_ReadLatency{scope=~'$scope',scope!='',keyspace=~'$keyspace',function='$percentile',function!='Min|Max',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by ($groupBy,keyspace,scope)

# Average Replica Range Read Latency
avg(cas_Table_RangeLatency{scope=~'$scope',scope!='',keyspace=~'$keyspace',function='$percentile',function!='Min|Max',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by ($groupBy,keyspace,scope)

# Average Replica Write Latency
avg(cas_Table_WriteLatency{scope=~'$scope',scope!='',keyspace=~'$keyspace',function='$percentile',function!='Min|Max',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by ($groupBy,keyspace,scope)

# Total Replica Reads/sec
sum(cas_Table_ReadLatency{axonfunction='rate',scope=~'$scope',scope!='',keyspace=~'$keyspace',function='Count',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by ($groupBy,keyspace,scope)

# Total Replica Range Reads/sec
sum(cas_Table_RangeLatency{axonfunction='rate',scope=~'$scope',scope!='',keyspace=~'$keyspace',function='Count',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by ($groupBy,keyspace,scope)

# Total Replica Writes/sec
sum(cas_Table_WriteLatency{axonfunction='rate',scope=~'$scope',scope!='',keyspace=~'$keyspace',function='Count',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by ($groupBy,keyspace,scope)
```

### Latency Causes
```promql
# Average Mean Partition Size
avg(cas_Table_MeanPartitionSize{dc=~'$dc',rack=~'$rack',host_id=~'$host_id',scope=~'$scope',scope!=''}) by ($groupBy,keyspace,scope)

# Total Estimated Partitions
sum(cas_Table_EstimatedPartitionCount{dc=~'$dc',rack=~'$rack',host_id=~'$host_id',keyspace='$keyspace',scope='$scope'}) by ($groupBy,keyspace,scope)

# Max Partition Size
max(cas_Table_MaxPartitionSize{dc=~'$dc',rack=~'$rack',host_id=~'$host_id',scope=~'$scope',scope!=''}) by ($groupBy,keyspace,scope)

# SSTables Per Read
cas_Table_SSTablesPerReadHistogram{scope=~'$scope',scope!='',keyspace=~'$keyspace',function='$percentile',function!='Min|Max',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}

# Max Live SSTables
max(cas_Table_LiveSSTableCount{dc=~'$dc',rack=~'$rack',host_id=~'$host_id',scope=~'$scope',scope!=''}) by ($groupBy,keyspace,scope)

# Tombstones Scanned
cas_Table_TombstoneScannedHistogram{scope=~'$scope',scope!='',keyspace=~'$keyspace',function='$percentile',function!='Count|Min|Max',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}

# Speculative Retries
cas_Table_SpeculativeRetries{axonfunction='rate',scope=~'$scope',scope!='',keyspace=~'$keyspace',function='Count',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}

# Bloom Filter False Ratio
cas_Table_BloomFilterFalseRatio{scope=~'$scope',scope!='',keyspace=~'$keyspace',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}

# Max Bloom Filter Disk
max(cas_Table_BloomFilterDiskSpaceUsed{dc=~'$dc',rack=~'$rack',host_id=~'$host_id',keyspace='$keyspace',scope='$scope'}) by ($groupBy,keyspace,scope)
```

### Memory Statistics
```promql
# Total Table Heap Memory
sum(cas_Table_AllMemtablesHeapSize{dc=~'$dc',rack='$rack',host_id=~'$host_id',keyspace='$keyspace',scope='$scope'}) by ($groupBy,keyspace,scope)

# Total Table Off-Heap Memory
sum(cas_Table_AllMemtablesOffHeapSize{dc=~'$dc',rack='$rack',host_id=~'$host_id',keyspace='$keyspace',scope='$scope'}) by ($groupBy,keyspace,scope)

# GC Duration - G1 YoungGen
jvm_GarbageCollector_G1_Young_Generation{axonfunction='rate',function='CollectionTime',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}

# GC Count per sec - G1 YoungGen
jvm_GarbageCollector_G1_Young_Generation{axonfunction='rate',function='CollectionCount',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}
```

## Panel Organization

### Tables Overview
- **Table Data Size % Distribution** - Pie chart showing relative data size per table

- **Coordinator Table Reads % Distribution** - Read request distribution by table

- **Coordinator Table Writes % Distribution** - Write request distribution by table

### Coordinator Table Statistics
- **Max Coordinator Table Read Latency** - Maximum read latency at coordinator

- **Max Coordinator Table Write Latency** - Maximum write latency at coordinator

- **Max Coordinator Table Range Read Latency** - Maximum range query latency

- **Total Coordinator Table Reads/Sec** - Read throughput at coordinator

- **Average Coordinator Table Range Reads/Sec** - Range query throughput

- **Total Coordinator Table Writes/Sec** - Write throughput at coordinator

### Table Replica Statistics
- **Average Replica Read Latency** - Local read latency

- **Average Replica Range Read Latency** - Local range query latency

- **Average Replica Write Latency** - Local write latency

- **Total Replica Reads/sec** - Local read throughput

- **Total Replica Table Range Reads/sec** - Local range query throughput

- **Total Replica Writes/sec** - Local write throughput

### Latency Causes
- **Average Mean Table Partition Size** - Average partition size indicator

- **Total Estimated Table Partitions Count** - Partition count per table

- **Max Table Partition Size** - Largest partition (hotspot indicator)

- **SSTables Per Read** - SSTable access efficiency

- **Max Live SSTables per Table** - SSTable count (compaction indicator)

- **Tombstones Scanned per Table** - Tombstone impact on reads

- **SpeculativeRetries By Node For Table Reads** - Retry attempts

- **Bloom Filter False Positive Ratio** - Filter efficiency

- **Max Table Bloom Filter Disk** - Bloom filter storage

### Memory Statistics
- **Total Table Heap Memory** - Memtable heap usage

- **Total Table Off-Heap Memory** - Memtable off-heap usage

- **GC duration - G1 YoungGen** - Young generation GC time

- **GC count per sec - G1 YoungGen** - Young generation GC frequency

- **GC duration - Shenandoah** - Shenandoah GC time

- **GC Count per sec - Shenandoah** - Shenandoah GC frequency

- **GC duration - ZGC** - ZGC time

- **GC Count per sec - ZGC** - ZGC frequency

## Filters

- **data center** (`dc`) - Filter by data center

- **rack** - Filter by rack

- **node** (`host_id`) - Filter by specific node

- **groupBy** - Dynamic grouping (dc, rack, host_id)

- **percentile** - Select latency percentile (50th, 75th, 95th, 98th, 99th, 999th)

- **keyspace** - Filter by keyspace

- **table** (`scope`) - Filter by table

## Understanding Table Metrics

### Coordinator vs Replica Metrics
- **Coordinator**: Metrics from the node coordinating the request

- **Replica**: Metrics from nodes storing the data

- Coordinator latency includes network and replica time
- Replica latency is local operation time only

### Performance Indicators

**Partition Size**:

   - Large partitions (>100MB) cause performance issues
   - Monitor max size for hotspot detection
   - Mean size indicates data distribution

**SSTable Metrics**:

   - High SSTable count impacts read performance
   - More SSTables = more files to check
   - Indicates compaction strategy effectiveness

**Tombstones**:

   - Deleted data markers
   - High tombstone counts slow reads
   - Indicates need for compaction or TTL review

**Bloom Filters**:

   - Probabilistic data structure for SSTable lookups
   - False positive ratio should be <0.1
   - Higher ratios mean unnecessary SSTable reads

**Speculative Retries**:

   - Proactive retry mechanism for slow reads
   - High rates indicate inconsistent performance
   - May need tuning or investigation

## Best Practices

### Table Design
- **Partition Size**: Keep <100MB, ideally <10MB

- **Even Distribution**: Avoid hotspots

- **Appropriate TTL**: Manage tombstone creation

- **Compression**: Choose based on workload

### Performance Monitoring
**Latency Percentiles**:

   - p50: Median performance
   - p99: Tail latency
   - Large p50-p99 gap indicates issues

**Throughput Balance**:

   - Even distribution across tables
   - Identify heavy tables
   - Plan capacity accordingly

**Resource Usage**:

   - Monitor memory per table
   - Track GC impact
   - Balance heap/off-heap usage

### Troubleshooting

**High Latency**:

   - Check partition sizes
   - Review SSTable counts
   - Monitor tombstones
   - Verify bloom filter efficiency

**Memory Issues**:

   - Check memtable sizes
   - Monitor GC frequency
   - Review flush thresholds

**Throughput Problems**:

   - Analyze coordinator distribution
   - Check speculative retries
   - Review consistency levels

## Units and Display

- **Latency**: microseconds

- **Throughput**: ops/sec (rps/wps)

- **Size**: bytes (binary units)

- **Ratio**: decimal/percentage

- **Count**: short (absolute numbers)

- **GC**: milliseconds/count per sec

**Legend Format**:

  - Overview: `$keyspace $scope`
  - Details: `$groupBy - $keyspace $scope`
  - Node-specific: `$dc - $host_id`

## Notes

- The `scope!=''` filter excludes empty table names
- `function!='Min|Max'` excludes extreme values for percentiles
- Coordinator metrics show client-facing performance
- Replica metrics show storage-layer performance
- GC metrics help correlate latency with JVM behavior
- Some queries use special operations like `diff` or specific rack filtering