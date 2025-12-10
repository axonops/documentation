# nodetool tablestats

Displays comprehensive statistics for tables, including read/write latencies, SSTable counts, and space usage.

## Synopsis

```bash
nodetool [connection_options] tablestats [options] [keyspace[.table] ...]
```

## Description

The `tablestats` command (formerly `cfstats`) provides detailed per-table metrics essential for understanding table performance and storage characteristics. Statistics include operation counts, latencies, SSTable information, partition sizes, and tombstone metrics.

This command is fundamental for identifying performance issues, validating data models, and capacity planning.

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| keyspace | No | Limit output to specified keyspace |
| keyspace.table | No | Limit output to specific table |

## Options

| Option | Description |
|--------|-------------|
| -H, --human-readable | Display sizes in human-readable format (KiB, MiB, GiB) |
| -F, --format &lt;format&gt; | Output format: json, yaml |
| -s, --sort &lt;sort_key&gt; | Sort tables by specified metric |
| -t, --top &lt;count&gt; | Show only top N tables by sort key |
| -i, --ignore &lt;tables&gt; | Comma-separated list of tables to ignore |

## Output Fields

### Space and SSTable Metrics

| Field | Description | Healthy Range |
|-------|-------------|---------------|
| SSTable count | Number of SSTable files on disk | Strategy-dependent |
| Old SSTable count | SSTables from previous version | 0 after upgrade |
| Space used (live) | Current data size | N/A |
| Space used (total) | Including obsolete data pending compaction | Close to live |
| Space used by snapshots | Disk used by snapshots | 0 if no active snapshots |
| Off heap memory used | Memory for bloom filters, indexes, metadata | Proportional to data |
| SSTable Compression Ratio | Compressed/uncompressed size | 0.2-0.5 typical |

### Partition Metrics

| Field | Description | Healthy Range |
|-------|-------------|---------------|
| Number of partitions (estimate) | Estimated partition count | N/A |
| Compacted partition minimum bytes | Smallest partition size | N/A |
| Compacted partition maximum bytes | Largest partition size | < 100 MB |
| Compacted partition mean bytes | Average partition size | Application-dependent |

### Memtable Metrics

| Field | Description | Healthy Range |
|-------|-------------|---------------|
| Memtable cell count | Cells in active memtable | N/A |
| Memtable data size | Size of active memtable | < memtable_heap_space |
| Memtable off heap memory used | Off-heap memtable memory | If configured |
| Memtable switch count | Number of flushes | N/A |
| Pending flushes | Memtables awaiting flush | 0-1 normal |

### Operation Metrics

| Field | Description | Healthy Range |
|-------|-------------|---------------|
| Local read count | Total local reads | N/A |
| Local read latency | Average read latency (ms) | < 5ms typical |
| Local write count | Total local writes | N/A |
| Local write latency | Average write latency (ms) | < 1ms typical |
| Dropped Mutations | Writes that timed out | 0 |

### Repair Metrics

| Field | Description | Healthy Range |
|-------|-------------|---------------|
| Percent repaired | Data covered by repair | > 90% |
| Bytes repaired | Size of repaired data | N/A |
| Bytes unrepaired | Size of unrepaired data | < 10% of total |
| Bytes pending repair | Data in active repair | 0 when idle |

### Read Path Metrics

| Field | Description | Healthy Range |
|-------|-------------|---------------|
| Bloom filter false positives | Count of false positives | Low relative to reads |
| Bloom filter false ratio | False positive rate | < 0.01 |
| Bloom filter space used | Memory for bloom filters | N/A |
| Average live cells per slice | Cells returned per read | Application-dependent |
| Maximum live cells per slice | Peak cells per read | Watch for outliers |
| Average tombstones per slice | Tombstones scanned per read | < 1.0 |
| Maximum tombstones per slice | Peak tombstones per read | < 100 |
| Droppable tombstone ratio | Ratio of expired tombstones | Low |

## Examples

### All Tables Statistics

```bash
nodetool tablestats
```

### Human-Readable Output

```bash
nodetool tablestats -H my_keyspace
```

**Output:**
```
Total number of tables: 5
----------------
Keyspace : my_keyspace
	Table: users
	SSTable count: 4
	Old SSTable count: 0
	Space used (live): 12.5 GiB
	Space used (total): 12.8 GiB
	Space used by snapshots (total): 0 bytes
	Off heap memory used (total): 45.2 MiB
	SSTable Compression Ratio: 0.3456
	Number of partitions (estimate): 5000000
	Memtable cell count: 125000
	Memtable data size: 48.5 MiB
	Memtable off heap memory used: 0 bytes
	Memtable switch count: 234
	Local read count: 98765432
	Local read latency: 0.892 ms
	Local write count: 45678901
	Local write latency: 0.234 ms
	Pending flushes: 0
	Percent repaired: 96.5
	Bytes repaired: 12.1 GiB
	Bytes unrepaired: 450.2 MiB
	Bytes pending repair: 0 bytes
	Bloom filter false positives: 12345
	Bloom filter false ratio: 0.00012
	Bloom filter space used: 4.5 MiB
	Bloom filter off heap memory used: 4.5 MiB
	Index summary off heap memory used: 2.3 MiB
	Compression metadata off heap memory used: 38.4 MiB
	Compacted partition minimum bytes: 125
	Compacted partition maximum bytes: 85234567
	Compacted partition mean bytes: 2456
	Average live cells per slice (last five minutes): 12.5
	Maximum live cells per slice (last five minutes): 156
	Average tombstones per slice (last five minutes): 0.3
	Maximum tombstones per slice (last five minutes): 25
	Dropped Mutations: 0
	Droppable tombstone ratio: 0.00012
```

### Specific Table

```bash
nodetool tablestats my_keyspace.users
```

### JSON Output

```bash
nodetool tablestats -F json my_keyspace
```

### Sort by Read Latency

```bash
nodetool tablestats -s read_latency
```

### Top 10 Tables by Size

```bash
nodetool tablestats -s space_used_live -t 10
```

## Interpreting Results

### Warning Indicators

| Condition | Threshold | Indication |
|-----------|-----------|------------|
| SSTable count (STCS) | > 32 | Compaction falling behind |
| SSTable count (LCS) | > L0 files | LCS overwhelmed |
| Max partition size | > 100 MB | Large partition anti-pattern |
| Avg tombstones per slice | > 1.0 | Tombstone accumulation |
| Max tombstones per slice | > 1000 | Severe tombstone issue |
| Bloom filter false ratio | > 0.01 | Bloom filter undersized |
| Dropped Mutations | > 0 | Write timeout occurred |
| Read latency | > 10 ms | Performance investigation needed |
| Write latency | > 5 ms | Performance investigation needed |
| Percent repaired | < 90% | Repair falling behind |

### Common Anti-Pattern Detection

**Large Partitions:**
```
Compacted partition maximum bytes: 524288000  # 500 MB
```
- Partition exceeds 100 MB recommendation
- Review partition key design

**Tombstone Accumulation:**
```
Average tombstones per slice (last five minutes): 45.6
Maximum tombstones per slice (last five minutes): 12500
```
- Excessive tombstones being scanned
- Review delete patterns, TTL usage

**Compaction Backlog (STCS):**
```
SSTable count: 87
```
- Too many SSTables for SizeTiered strategy
- Check compaction throughput

## Common Use Cases

### Performance Comparison Script

```bash
#!/bin/bash
# Compare read latencies across tables
nodetool tablestats | awk '
    /Keyspace :/ { ks=$3 }
    /Table:/ { tbl=$2 }
    /Local read latency/ {
        printf "%s.%s: %s ms\n", ks, tbl, $4
    }
' | sort -t: -k2 -n -r | head -10
```

### Tombstone Analysis

```bash
#!/bin/bash
# Find tables with tombstone issues
nodetool tablestats | awk '
    /Keyspace :/ { ks=$3 }
    /Table:/ { tbl=$2 }
    /Average tombstones per slice/ {
        if ($7 > 1.0) {
            printf "WARNING: %s.%s avg_tombstones=%.2f\n", ks, tbl, $7
        }
    }
    /Maximum tombstones per slice/ {
        if ($7 > 100) {
            printf "CRITICAL: %s.%s max_tombstones=%d\n", ks, tbl, $7
        }
    }
'
```

### Large Partition Detection

```bash
#!/bin/bash
# Find tables with large partitions
nodetool tablestats | awk '
    /Keyspace :/ { ks=$3 }
    /Table:/ { tbl=$2 }
    /Compacted partition maximum bytes/ {
        size_mb = $5 / 1048576
        if (size_mb > 100) {
            printf "LARGE PARTITION: %s.%s max_size=%.1f MB\n", ks, tbl, size_mb
        }
    }
'
```

### Monitoring Export

```bash
# Export key metrics for monitoring
nodetool tablestats -F json | jq -r '
    .[] |
    "cassandra_table_read_latency{keyspace=\"\(.keyspace)\",table=\"\(.table)\"} \(.read_latency)",
    "cassandra_table_write_latency{keyspace=\"\(.keyspace)\",table=\"\(.table)\"} \(.write_latency)",
    "cassandra_table_sstable_count{keyspace=\"\(.keyspace)\",table=\"\(.table)\"} \(.sstable_count)"
'
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Command executed successfully |
| 1 | Error connecting to JMX or executing command |
| 2 | Invalid arguments |

## Related Commands

- [nodetool tablehistograms](tablehistograms.md) - Latency percentile distributions
- [nodetool toppartitions](toppartitions.md) - Identify hot partitions
- [nodetool compactionstats](compactionstats.md) - Compaction status
- [nodetool tpstats](tpstats.md) - Thread pool statistics

## Version Information

Available in all Apache Cassandra versions. The command was renamed from `cfstats` to `tablestats` in Cassandra 3.0, with `cfstats` maintained as an alias. JSON/YAML output formats were added in Cassandra 4.0.
