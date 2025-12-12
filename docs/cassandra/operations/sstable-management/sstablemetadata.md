# sstablemetadata

Displays detailed metadata and statistics for SSTable files.

---

## Synopsis

```bash
sstablemetadata [options] <sstable_files>
```

---

## Description

`sstablemetadata` reads SSTable Statistics.db files and displays comprehensive metadata about SSTables. This information is essential for:

- **Capacity planning** - Understanding data distribution and growth
- **Performance tuning** - Identifying compression ratios and partition sizes
- **Troubleshooting** - Checking repair status, tombstone counts, and timestamps
- **Compaction analysis** - Viewing SSTable levels and sizes
- **Repair diagnostics** - Verifying repaired/unrepaired status

The tool can run while Cassandra is active as it only reads metadata files.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `sstable_files` | One or more paths to SSTable Data.db files |

---

## Options

| Option | Description |
|--------|-------------|
| `-g, --gc_grace_seconds <n>` | Override gc_grace_seconds for TTL calculations |
| `-c, --colors` | Colorize output for better readability |
| `-s, --scan` | Scan data file in addition to metadata |
| `-t, --timestamp <format>` | Timestamp format for dates |
| `-u, --unix-timestamp` | Show timestamps as Unix epoch |

---

## Output Fields

### SSTable Properties

| Field | Description |
|-------|-------------|
| `SSTable` | File path and name |
| `SSTable Version` | Format version (ma, mb, nb, etc.) |
| `Partitioner` | Murmur3Partitioner or other |
| `Bloom Filter FP chance` | False positive probability |
| `Minimum Timestamp` | Earliest data timestamp |
| `Maximum Timestamp` | Latest data timestamp |

### Size Metrics

| Field | Description |
|-------|-------------|
| `Size` | Uncompressed data size |
| `Compressed Size` | On-disk compressed size |
| `Compression Ratio` | Compression effectiveness |
| `Estimated Partition Count` | Number of partitions |

### Partition Statistics

| Field | Description |
|-------|-------------|
| `Estimated Partition Size` | Min/Max/Avg partition sizes |
| `Estimated Cell Count` | Number of cells |
| `Estimated Tombstone Count` | Tombstone drop time histogram |

### Repair Information

| Field | Description |
|-------|-------------|
| `Repaired At` | Timestamp when marked repaired (0 = unrepaired) |
| `Pending Repair` | UUID if pending repair |
| `isTransient` | Whether SSTable is from transient replica |

### Compaction Information

| Field | Description |
|-------|-------------|
| `Level` | LCS compaction level (0-9) |
| `First Token` | First token in SSTable |
| `Last Token` | Last token in SSTable |

---

## Examples

### Basic Metadata Display

```bash
# View metadata for single SSTable
sstablemetadata /var/lib/cassandra/data/my_keyspace/my_table-abc123/nb-1-big-Data.db
```

### Multiple SSTables

```bash
# View metadata for all SSTables in a table directory
sstablemetadata /var/lib/cassandra/data/my_keyspace/my_table-*/nb-*-big-Data.db
```

### With Color Output

```bash
# Colorized output for easier reading
sstablemetadata -c /path/to/sstable-Data.db
```

### Check Repair Status

```bash
# Check if SSTables are repaired
sstablemetadata /var/lib/cassandra/data/my_keyspace/my_table-*/*-Data.db | grep -E "SSTable|Repaired"
```

### Find SSTable Versions

```bash
# Check SSTable format versions (useful before upgrade)
sstablemetadata /var/lib/cassandra/data/my_keyspace/my_table-*/*-Data.db | grep "SSTable Version"
```

---

## Sample Output

```
SSTable: /var/lib/cassandra/data/my_keyspace/users-a1b2c3d4/nb-1-big-Data.db
SSTable Version: nb
Partitioner: org.apache.cassandra.dht.Murmur3Partitioner
Bloom Filter FP chance: 0.010000

Minimum Timestamp: 2024-01-01T00:00:00.000Z
Maximum Timestamp: 2024-01-15T23:59:59.000Z
First Token: -9223372036854775808
Last Token: 9223372036854775807

Size: 1073741824 (1.0 GB)
Compressed Size: 268435456 (256 MB)
Compression Ratio: 0.25
Compression Class: org.apache.cassandra.io.compress.LZ4Compressor

Estimated Partition Count: 100000
Estimated Cell Count: 5000000
Estimated Tombstone Drop Time:
  1705363200: 150
  1705449600: 230

SSTable Level: 2
Repaired At: 1705401600000 (2024-01-16T12:00:00.000Z)
Pending Repair: null
isTransient: false

Estimated Partition Size (bytes):
  Min: 128
  Max: 1048576
  Mean: 10737

Estimated Column Count:
  Min: 5
  Max: 500
  Mean: 50
```

---

## Common Use Cases

### Checking Compression Effectiveness

```bash
#!/bin/bash
# compression_report.sh - Report compression ratios

DATA_DIR="/var/lib/cassandra/data"
KEYSPACE="$1"
TABLE="$2"

echo "Compression Report for ${KEYSPACE}.${TABLE}"
echo "============================================"

total_raw=0
total_compressed=0

for sstable in ${DATA_DIR}/${KEYSPACE}/${TABLE}-*/*-Data.db; do
    output=$(sstablemetadata "$sstable" 2>/dev/null)

    raw=$(echo "$output" | grep "^Size:" | awk '{print $2}')
    compressed=$(echo "$output" | grep "Compressed Size:" | awk '{print $3}')
    ratio=$(echo "$output" | grep "Compression Ratio:" | awk '{print $3}')

    echo "$(basename $sstable): Raw=$raw Compressed=$compressed Ratio=$ratio"

    total_raw=$((total_raw + raw))
    total_compressed=$((total_compressed + compressed))
done

echo ""
echo "Total: Raw=$total_raw Compressed=$total_compressed"
echo "Overall Ratio: $(echo "scale=2; $total_compressed / $total_raw" | bc)"
```

### Finding Large Partitions

```bash
#!/bin/bash
# large_partitions.sh - Find SSTables with large partitions

DATA_DIR="/var/lib/cassandra/data"
KEYSPACE="$1"
TABLE="$2"
THRESHOLD="${3:-104857600}"  # Default 100MB

echo "Finding partitions larger than $THRESHOLD bytes"
echo "================================================"

for sstable in ${DATA_DIR}/${KEYSPACE}/${TABLE}-*/*-Data.db; do
    max_size=$(sstablemetadata "$sstable" 2>/dev/null | grep "Max:" | head -1 | awk '{print $2}')

    if [ "$max_size" -gt "$THRESHOLD" ]; then
        echo "WARNING: $sstable has partitions up to $max_size bytes"
    fi
done
```

### Repair Status Audit

```bash
#!/bin/bash
# repair_audit.sh - Check repair status of all SSTables

DATA_DIR="/var/lib/cassandra/data"
KEYSPACE="$1"

repaired=0
unrepaired=0
pending=0

for sstable in ${DATA_DIR}/${KEYSPACE}/*/*-Data.db; do
    output=$(sstablemetadata "$sstable" 2>/dev/null)

    repaired_at=$(echo "$output" | grep "Repaired At:" | awk '{print $3}')
    pending_repair=$(echo "$output" | grep "Pending Repair:" | awk '{print $3}')

    if [ "$pending_repair" != "null" ]; then
        pending=$((pending + 1))
        echo "PENDING: $sstable"
    elif [ "$repaired_at" -eq 0 ] 2>/dev/null; then
        unrepaired=$((unrepaired + 1))
        echo "UNREPAIRED: $sstable"
    else
        repaired=$((repaired + 1))
    fi
done

echo ""
echo "Summary:"
echo "  Repaired: $repaired"
echo "  Unrepaired: $unrepaired"
echo "  Pending: $pending"
```

### LCS Level Distribution

```bash
#!/bin/bash
# lcs_levels.sh - Show SSTable distribution across LCS levels

DATA_DIR="/var/lib/cassandra/data"
KEYSPACE="$1"
TABLE="$2"

declare -A levels

for sstable in ${DATA_DIR}/${KEYSPACE}/${TABLE}-*/*-Data.db; do
    level=$(sstablemetadata "$sstable" 2>/dev/null | grep "SSTable Level:" | awk '{print $3}')
    levels[$level]=$((${levels[$level]:-0} + 1))
done

echo "LCS Level Distribution for ${KEYSPACE}.${TABLE}"
echo "=============================================="
for level in $(echo "${!levels[@]}" | tr ' ' '\n' | sort -n); do
    count=${levels[$level]}
    bar=$(printf '%*s' $count '' | tr ' ' '#')
    echo "L$level: $count $bar"
done
```

### Tombstone Analysis

```bash
#!/bin/bash
# tombstone_analysis.sh - Analyze tombstone distribution

DATA_DIR="/var/lib/cassandra/data"
KEYSPACE="$1"
TABLE="$2"

echo "Tombstone Analysis for ${KEYSPACE}.${TABLE}"
echo "==========================================="

for sstable in ${DATA_DIR}/${KEYSPACE}/${TABLE}-*/*-Data.db; do
    echo ""
    echo "SSTable: $(basename $sstable)"

    sstablemetadata "$sstable" 2>/dev/null | grep -A 20 "Estimated Tombstone Drop Time:" | head -10
done
```

---

## Metadata Interpretation

### SSTable Version Guide

| Version | Cassandra Version | Notes |
|---------|-------------------|-------|
| jb | 2.0.x | Legacy format |
| ka | 2.1.x | Legacy format |
| la | 2.2.x | Legacy format |
| ma | 3.0.x | Big format introduced |
| mb | 3.11.x | Big format |
| nb | 4.0.x | Big format |
| nc | 4.1.x | Big format |
| oa | 5.0.x | BTI format |

### Repair Status Values

| Repaired At | Meaning |
|-------------|---------|
| 0 | Never repaired (unrepaired) |
| Non-zero timestamp | Marked repaired at that time |

| Pending Repair | Meaning |
|----------------|---------|
| null | Not in pending repair |
| UUID | Part of ongoing repair session |

### Compression Ratio Interpretation

| Ratio | Interpretation |
|-------|----------------|
| < 0.3 | Excellent compression |
| 0.3 - 0.5 | Good compression |
| 0.5 - 0.7 | Average compression |
| > 0.7 | Poor compression (consider different compressor) |
| > 1.0 | Data is not compressible |

---

## Troubleshooting

### Missing Metadata

```bash
# Error: Unable to read Statistics.db

# Check file exists
ls -la /path/to/sstable-Statistics.db

# May be corrupted - verify SSTable
sstableverify keyspace table
```

### Permission Issues

```bash
# Run as cassandra user
sudo -u cassandra sstablemetadata /var/lib/cassandra/data/.../nb-1-big-Data.db
```

### Incorrect Timestamps

```bash
# Specify timestamp format
sstablemetadata -t "yyyy-MM-dd'T'HH:mm:ss" /path/to/sstable-Data.db

# Or use Unix timestamps
sstablemetadata -u /path/to/sstable-Data.db
```

---

## Best Practices

!!! tip "sstablemetadata Guidelines"

    1. **Regular monitoring** - Track compression ratios over time
    2. **Pre-upgrade checks** - Verify SSTable versions before upgrades
    3. **Repair audits** - Regularly check repair status
    4. **Capacity planning** - Monitor partition sizes and counts
    5. **Performance analysis** - Check tombstone distributions
    6. **Script automation** - Build monitoring scripts around output

!!! info "Safe Operation"

    Unlike most SSTable tools, `sstablemetadata` is read-only and can safely run while Cassandra is active. It only reads metadata files, not data files.

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [sstabledump](sstabledump.md) | View actual data content |
| [sstablepartitions](sstablepartitions.md) | Detailed partition analysis |
| [sstablerepairedset](sstablerepairedset.md) | Modify repair status |
| [sstableutil](sstableutil.md) | List SSTable files |
| [nodetool tablestats](../nodetool/tablestats.md) | Live table statistics |
