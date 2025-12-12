---
description: "Cassandra data dashboard metrics mapping. Storage and SSTable metrics."
meta:
  - name: keywords
    content: "data metrics, storage metrics, SSTable metrics, Cassandra"
---

# AxonOps Data Dashboard Metrics Mapping

This document maps the metrics used in the AxonOps Data dashboard.

## Dashboard Overview

The Data dashboard provides insights into data storage characteristics including compression ratios, disk space usage, SSTable counts, and partition sizes. It helps monitor data distribution and identify tables with potential issues like large partitions or poor compression.

## Metrics Mapping

### Compression Metrics

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `cas_Table_CompressionRatio` | Compression effectiveness ratio | `keyspace`, `scope` (table), `dc`, `rack`, `host_id` |
| `cas_Table_CompressionMetadataOffHeapMemoryUsed` | Off-heap memory used by compression metadata | `keyspace`, `scope` (table), `dc`, `rack`, `host_id` |

### Disk Space Metrics

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `cas_Table_LiveDiskSpaceUsed` | Live data disk space (excludes deleted data) | `keyspace`, `scope` (table), `function=Count`, `dc`, `rack`, `host_id` |
| `cas_Table_TotalDiskSpaceUsed` | Total disk space including tombstones | `keyspace`, `scope` (table), `function=Count`, `dc`, `rack`, `host_id` |
| `cas_Table_LiveSSTableCount` | Number of live SSTables | `keyspace`, `scope` (table), `dc`, `rack`, `host_id` |

### Partition Size Metrics

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `cas_Table_MinPartitionSize` | Minimum partition size in bytes | `keyspace`, `scope` (table), `dc`, `rack`, `host_id` |
| `cas_Table_MeanPartitionSize` | Average partition size in bytes | `keyspace`, `scope` (table), `dc`, `rack`, `host_id` |
| `cas_Table_MaxPartitionSize` | Maximum partition size in bytes | `keyspace`, `scope` (table), `dc`, `rack`, `host_id` |

## Query Examples

### Compression Ratio
```promql
cas_Table_CompressionRatio{scope=~'$scope', scope!='', dc=~'$dc',rack=~'$rack',host_id=~'$host_id',keyspace=~'$keyspace'}
```

### Compression Metadata Memory
```promql
cas_Table_CompressionMetadataOffHeapMemoryUsed{scope=~'$scope', scope!='', dc=~'$dc',rack=~'$rack',host_id=~'$host_id',keyspace=~'$keyspace'}
```

### Live Disk Space Per Table
```promql
cas_Table_LiveDiskSpaceUsed{function='Count',dc=~'$dc',rack=~'$rack',host_id=~'$host_id',keyspace=~'$keyspace',scope=~'$scope', scope!=''}
```

### Total Disk Space Per Table
```promql
cas_Table_TotalDiskSpaceUsed{function='Count',dc=~'$dc',rack=~'$rack',host_id=~'$host_id',keyspace=~'$keyspace',scope=~'$scope'}
```

### SSTable Count
```promql
cas_Table_LiveSSTableCount{dc=~'$dc',rack=~'$rack',host_id=~'$host_id',scope=~'$scope', scope!=''}
```

### Partition Size Metrics
```promql
// Minimum
cas_Table_MinPartitionSize{dc=~'$dc',rack=~'$rack',host_id=~'$host_id',scope=~'$scope', scope!=''}

// Mean
cas_Table_MeanPartitionSize{dc=~'$dc',rack=~'$rack',host_id=~'$host_id',scope=~'$scope', scope!=''}

// Maximum
cas_Table_MaxPartitionSize{dc=~'$dc',rack=~'$rack',host_id=~'$host_id',scope=~'$scope', scope!=''}
```

## Panel Organization

### Compression Section
- **Compression Ratio** - Line chart showing compression effectiveness (lower is better)

- **Compression Metadata Off-Heap Memory per Table** - Memory overhead of compression

### Disk Space Per Node Section
- **Live Disk Space Per Table** - Active data size per table

- **Total Disk Space Per Table** - Total size including tombstones

- **Live SSTable Count Per Table** - Number of SSTables per table

### Row Size Per Node Section
- **Min Partition Size Per Table** - Smallest partition in each table

- **Mean Partition Size Per Table** - Average partition size

- **Max Row Size Per Table** - Largest partition (identifies potential hotspots)

## Filters

- **data center** (`dc`) - Filter by data center

- **rack** - Filter by rack

- **node** (`host_id`) - Filter by specific node

- **keyspace** - Filter by keyspace

- **table** (`scope`) - Filter by table

## Important Metrics Explained

### Compression Ratio
- Shows how well data compresses
- Lower values mean better compression
- Typical values: 0.3-0.5 for text data
- Depends on compression algorithm and data type

### Disk Space Metrics
- **Live Space**: Only counts active data

- **Total Space**: Includes tombstones and deleted data

- Difference indicates space that can be reclaimed by compaction

### SSTable Count
- High counts may indicate:

    - Need for compaction tuning
    - High write load
    - Compaction falling behind

- Affects read performance (more SSTables = more files to check)

### Partition Size Distribution
- **Min Size**: Usually very small (empty or near-empty partitions)

- **Mean Size**: Average across all partitions

- **Max Size**: Critical for identifying large partitions

  - Partitions > 100MB can cause performance issues
  - Partitions > 1GB should be investigated

## Legend Format

All panels use: `$dc - $host_id-$keyspace-$scope`

- Shows data center, node, keyspace, and table
- Allows easy identification of specific table metrics

## Best Practices

**Monitor Compression Ratio**:

   - Sudden changes may indicate data pattern changes
   - Poor compression might suggest wrong algorithm choice

**Watch Disk Space Growth**:

   - Compare live vs total space
   - Large differences suggest need for compaction

**Track SSTable Counts**:

   - Consistently high counts impact read performance
   - May need to adjust compaction strategy

**Monitor Partition Sizes**:

   - Large partitions (>100MB) need investigation
   - Very large partitions (>1GB) can cause operational issues
   - Consider data model changes for tables with large partitions

## Notes

- The `scope!=''` filter excludes empty table names
- `function='Count'` is used for disk space metrics
- All size metrics use binary units (bytes, not SI units)
- Partition size metrics are estimates based on sampling