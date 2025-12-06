# SSTable Reference

SSTables (Sorted String Tables) are Cassandra's persistent storage files. All data ultimately resides in SSTables on disk—they are the database files. When a memtable flushes, it creates an SSTable. When compaction runs, it reads SSTables and writes new ones. When a node restarts, it reads SSTables to rebuild its state.

Each SSTable is immutable once written. This immutability simplifies concurrency (no locks needed for reads), enables efficient sequential writes, and allows safe snapshots via hard links. However, it also means that updates and deletes create new data rather than modifying existing files, requiring background compaction to reclaim space and merge versions.

An SSTable is not a single file but a set of component files: data, indexes, bloom filter, compression metadata, and statistics. Understanding these components is essential for troubleshooting, capacity planning, and performance analysis.

---

## SSTable File Location

```
data_directory/keyspace_name/table_name-table_uuid/
├── na-1-big-Data.db
├── na-1-big-Index.db
├── na-1-big-Filter.db
├── na-1-big-Statistics.db
├── na-1-big-Summary.db
├── na-1-big-CompressionInfo.db
├── na-1-big-Digest.crc32
└── na-1-big-TOC.txt
```

---

## File Naming Convention

```
<version>-<generation>-<format>-<component>.<extension>

Example: na-1-big-Data.db

na      - SSTable format version
1       - Generation number (increments with compaction)
big     - Format type
Data    - Component type
db      - File extension
```

### Version Identifiers

| Version | Cassandra Version | Notes |
|---------|-------------------|-------|
| `la` | 2.1 | Legacy format |
| `lb` | 2.1 | Legacy format |
| `ma` | 3.0 | Introduced new storage format |
| `mb` | 3.0 | Storage format revision |
| `mc` | 3.0 | Storage format revision |
| `md` | 3.11 | Storage format revision |
| `na` | 4.0 | Current format, trie-based indexes |
| `nb` | 4.0+ | Format revision |
| `nc` | 5.0 | Latest format |

### SSTable Identifiers (Cassandra 4.1+)

Cassandra 4.1 introduced an alternative SSTable naming scheme using globally unique identifiers instead of sequential generation numbers. This feature is enabled by default in Cassandra 5.0.

**Traditional (sequential):**
```
na-1-big-Data.db
na-2-big-Data.db
na-3-big-Data.db
```

**UUID-based (Cassandra 4.1+):**
```
nb-1-big-Data.db                              (sequential)
nb-3fw2_0zer_0000wjnhm8y18d-big-Data.db       (UUID-based)
```

**Identifier Structure:**

The UUID-based identifier is 28 characters using Base36 encoding (`0-9a-z`):

```
3fw2_0zer_0000wjnhm8y18d000
├──┘ ├──┘ ├───┘├──────────┘
│    │    │    │
│    │    │    └── Random part (13 chars) - unique per Cassandra process
│    │    └─────── Nano part (5 chars) - nanosecond precision
│    └──────────── Second part (4 chars) - seconds within day
└───────────────── Day part (4 chars) - days since epoch
```

Format regex: `([0-9a-z]{4})_([0-9a-z]{4})_([0-9a-z]{5})([0-9a-z]{13})`

This structure ensures identifiers are:

- **Lexicographically sortable** - Natural ordering by creation time
- **Globally unique** - No collisions across the entire cluster
- **Self-describing** - Creation time encoded in the identifier

**Configuration:**

```yaml
# cassandra.yaml

# Enable UUID-based SSTable identifiers
# Default: false (4.1), true (5.0+)
# WARNING: Cannot be disabled once SSTables are created with UUIDs
uuid_sstable_identifiers_enabled: true
```

**Comparison:**

| Aspect | Sequential | UUID-based |
|--------|------------|------------|
| Uniqueness | Per-table only | Cluster-wide |
| Streaming conflicts | Possible | None |
| Sorting | Numeric order | Lexicographic (time-ordered) |
| Creation time | Requires metadata lookup | Encoded in identifier |
| Downgrade | Always supported | Not supported once enabled |

**Problem: Generation Counter Reset After Truncate**

Sequential generation numbers reset after truncating a table and restarting the node. This causes SSTable identifier collisions during backup restore operations.

*Scenario: Backup and restore after truncate*

```
Step 1: Table has data, take a snapshot backup
└── keyspace/table-abc123/
    ├── nb-1-big-Data.db
    ├── nb-2-big-Data.db
    └── nb-3-big-Data.db

    → nodetool snapshot keyspace table (backup saved)

Step 2: Truncate the table
    → TRUNCATE keyspace.table;
    → All SSTables removed, generation counter state cleared

Step 3: Restart the node
    → Generation counter resets to 1

Step 4: New data written to table
└── keyspace/table-abc123/
    ├── nb-1-big-Data.db    ← NEW data, same filename as backup!
    ├── nb-2-big-Data.db    ← NEW data, same filename as backup!
    └── nb-3-big-Data.db    ← NEW data, same filename as backup!

Step 5: Attempt to restore backup
    → CONFLICT: Backup files (nb-1, nb-2, nb-3) collide with current files
    → Cannot restore without overwriting current data or manually renaming
```

**Remote backup storage corruption:**

The problem is worse with remote backup destinations (S3, GCS, Azure Blob). Incremental backups upload SSTables by filename:

```
Remote storage (S3 bucket):
└── backups/cluster1/node1/keyspace/table/
    ├── nb-1-big-Data.db    ← From initial backup (important data)
    ├── nb-2-big-Data.db
    └── nb-3-big-Data.db

After truncate + restart + new writes:
└── New SSTable files: nb-1, nb-2, nb-3

Next incremental backup runs:
└── backups/cluster1/node1/keyspace/table/
    ├── nb-1-big-Data.db    ← OVERWRITTEN with new data!
    ├── nb-2-big-Data.db    ← OVERWRITTEN - original backup lost!
    └── nb-3-big-Data.db    ← OVERWRITTEN
```

The original backup data is permanently lost. Backup tools cannot distinguish between "same file updated" and "different file with same name."

*Same scenario with UUID identifiers:*

```
Step 1: Table has data, take a snapshot backup
└── keyspace/table-abc123/
    ├── nb-3fw2_0zer_0000wjnhm8y18d000-big-Data.db
    ├── nb-3fw2_0zer_0001xkpl9z28e111-big-Data.db
    └── nb-3fw2_0zer_0002ymqm0a39f222-big-Data.db

    → nodetool snapshot keyspace table (backup saved)

Step 2: Truncate and restart
    → TRUNCATE keyspace.table;
    → Restart node (UUID generator continues with new random component)

Step 3: New data written to table
└── keyspace/table-abc123/
    ├── nb-3fw3_1abc_0000wabc123def00-big-Data.db   ← Different identifier
    ├── nb-3fw3_1abc_0001xdef456ghi11-big-Data.db
    └── nb-3fw3_1abc_0002yghi789jkl22-big-Data.db

Step 4: Restore backup - no conflicts
└── keyspace/table-abc123/
    ├── nb-3fw2_0zer_0000wjnhm8y18d000-big-Data.db   ← Restored from backup
    ├── nb-3fw2_0zer_0001xkpl9z28e111-big-Data.db   ← Restored from backup
    ├── nb-3fw2_0zer_0002ymqm0a39f222-big-Data.db   ← Restored from backup
    ├── nb-3fw3_1abc_0000wabc123def00-big-Data.db   ← Current data preserved
    ├── nb-3fw3_1abc_0001xdef456ghi11-big-Data.db
    └── nb-3fw3_1abc_0002yghi789jkl22-big-Data.db
```

UUID identifiers incorporate a random component unique to each Cassandra process, so identifiers never repeat even after truncate and restart.

**Scenarios where UUID identifiers prevent collisions:**

| Operation | Sequential Problem | UUID Solution |
|-----------|-------------------|---------------|
| Restore after truncate | Generation resets, filenames collide | Unique identifiers always |
| Incremental backup to S3/GCS | New files overwrite old backups | Each backup file unique |
| Multiple backup restore | Cannot merge backups from different times | Safe to combine |
| Repair streaming | Incoming SSTable may match local name | No conflicts possible |
| Node rebuild | Streamed files may collide | Safe parallel streaming |

**Source:** [Apache Cassandra 4.1: New SSTable Identifiers](https://cassandra.apache.org/_/blog/Apache-Cassandra-4.1-New-SSTable-Identifiers.html)

---

## SSTable Component Files

### Data File (Data.db)

Contains the actual row data for all partitions in the SSTable.

| Attribute | Description |
|-----------|-------------|
| **Purpose** | Store partition and row data |
| **Contents** | Serialized partitions with rows and cells |
| **Compression** | Compressed in chunks (configurable) |
| **Size** | Largest component, varies with data volume |

**Structure:**

```
┌─────────────────────────────────────────────────────────┐
│ Partition 1                                              │
│ ├── Partition Key (serialized)                          │
│ ├── Partition Header (deletion info, flags)             │
│ ├── Row 1 (clustering key + cells)                      │
│ ├── Row 2 (clustering key + cells)                      │
│ └── ...                                                 │
├─────────────────────────────────────────────────────────┤
│ Partition 2                                              │
│ └── ...                                                 │
├─────────────────────────────────────────────────────────┤
│ ...                                                     │
└─────────────────────────────────────────────────────────┘
```

---

### Partition Index (Index.db / Partitions.db)

Maps partition keys to byte offsets in the Data file.

**Pre-4.0 (Index.db):**

| Attribute | Description |
|-----------|-------------|
| **Purpose** | Map partition keys to data file offsets |
| **Contents** | Partition key → offset pairs |
| **Access** | Requires Summary.db for efficient lookup |

**Cassandra 4.0+ (Partitions.db):**

| Attribute | Description |
|-----------|-------------|
| **Purpose** | Trie-based partition index |
| **Contents** | Compressed prefix trie of partition keys |
| **Access** | Direct lookup without summary file |
| **Benefits** | 50-80% smaller, off-heap, faster lookups |

---

### Row Index (Rows.db) - Cassandra 4.0+

Maps clustering keys to positions within partitions.

| Attribute | Description |
|-----------|-------------|
| **Purpose** | Locate rows within large partitions |
| **Contents** | Clustering key → intra-partition offset |
| **When Created** | Only for partitions exceeding threshold |

---

### Bloom Filter (Filter.db)

Probabilistic data structure for quick partition key lookups.

| Attribute | Description |
|-----------|-------------|
| **Purpose** | Quickly eliminate SSTables from read path |
| **Contents** | Bit array with hashed partition keys |
| **False Positives** | Possible (configurable rate) |
| **False Negatives** | Impossible |
| **Memory** | Loaded into off-heap memory |

**Configuration:**

```sql
ALTER TABLE my_table WITH bloom_filter_fp_chance = 0.01;
```

---

### Summary (Summary.db) - Pre-4.0

Sampled index for efficient partition lookup.

| Attribute | Description |
|-----------|-------------|
| **Purpose** | In-memory sample of partition index |
| **Contents** | Every Nth partition key from index |
| **Memory** | Loaded into JVM heap |
| **Note** | Replaced by trie index in Cassandra 4.0+ |

**Configuration (pre-4.0):**

```yaml
# cassandra.yaml
min_index_interval: 128    # Minimum sampling rate
max_index_interval: 2048   # Maximum sampling rate
```

---

### Compression Info (CompressionInfo.db)

Metadata for compressed data chunks.

| Attribute | Description |
|-----------|-------------|
| **Purpose** | Map uncompressed offsets to compressed chunks |
| **Contents** | Chunk boundaries and compressed sizes |
| **Required For** | Random access within compressed data |

**Structure:**

```
Data.db is compressed in fixed-size chunks:

Uncompressed: [Chunk 1: 64KB][Chunk 2: 64KB][Chunk 3: 64KB]
                   ↓              ↓              ↓
Compressed:   [28KB]         [30KB]         [25KB]

CompressionInfo.db stores:
- Chunk 1 starts at offset 0
- Chunk 2 starts at offset 28672
- Chunk 3 starts at offset 59392
```

---

### Statistics (Statistics.db)

Metadata about the SSTable contents.

| Attribute | Description |
|-----------|-------------|
| **Purpose** | Store SSTable metadata for query optimization |
| **Contents** | Min/max values, tombstone counts, timestamps |
| **Used By** | Query planner, compaction, repair |

**Contents include:**

| Statistic | Description |
|-----------|-------------|
| Partition count | Number of partitions in SSTable |
| Row count | Total rows across all partitions |
| Min/max timestamp | Timestamp range of data |
| Min/max clustering | Clustering key range |
| Min/max partition key | Partition key range (token) |
| Tombstone count | Number of tombstones |
| Droppable tombstone count | Tombstones eligible for removal |
| SSTable level | Compaction level (for LCS) |
| Compression ratio | Achieved compression ratio |

---

### Digest (Digest.crc32 / Digest.adler32 / Digest.sha1)

Checksum for data integrity verification.

| Attribute | Description |
|-----------|-------------|
| **Purpose** | Detect data corruption |
| **Contents** | Checksum of Data.db contents |
| **Verification** | Checked during reads and streaming |

---

### Table of Contents (TOC.txt)

Lists all component files for the SSTable.

| Attribute | Description |
|-----------|-------------|
| **Purpose** | Enumerate SSTable components |
| **Contents** | List of component file names |
| **Format** | Plain text, one file per line |

**Example contents:**

```
TOC.txt
Data.db
Index.db
Filter.db
Statistics.db
Summary.db
CompressionInfo.db
Digest.crc32
```

---

## Component File Reference Summary

| Component | File Extension | Purpose | Memory Location |
|-----------|---------------|---------|-----------------|
| Data | `-Data.db` | Row data | Disk (page cache) |
| Partition Index | `-Index.db` | Key → offset map | Heap (pre-4.0) |
| Partition Index | `-Partitions.db` | Trie index | Off-heap (4.0+) |
| Row Index | `-Rows.db` | Clustering → offset | Off-heap (4.0+) |
| Bloom Filter | `-Filter.db` | Existence check | Off-heap |
| Summary | `-Summary.db` | Sampled index | Heap (pre-4.0) |
| Compression Info | `-CompressionInfo.db` | Chunk offsets | Off-heap |
| Statistics | `-Statistics.db` | Metadata | Loaded on demand |
| Digest | `-Digest.*` | Checksum | Loaded on demand |
| TOC | `-TOC.txt` | File list | Loaded on demand |

---

## Compression

SSTable data is compressed in chunks for efficient random access.

### Compression Configuration

```sql
-- View current compression
SELECT compression FROM system_schema.tables
WHERE keyspace_name = 'ks' AND table_name = 'table';

-- Configure compression
ALTER TABLE my_table WITH compression = {
    'class': 'LZ4Compressor',
    'chunk_length_in_kb': 64
};

-- Disable compression
ALTER TABLE my_table WITH compression = {'enabled': 'false'};
```

### Compressor Comparison

| Compressor | Speed | Ratio | CPU | Use Case |
|------------|-------|-------|-----|----------|
| LZ4Compressor | Fastest | ~2.5x | Lowest | Default, most workloads |
| SnappyCompressor | Fast | ~2.5x | Low | Alternative to LZ4 |
| ZstdCompressor | Medium | ~3-4x | Medium | Better ratio (4.0+) |
| DeflateCompressor | Slow | ~3-4x | High | Maximum compression |
| NoCompressor | N/A | 1x | None | Pre-compressed data |

### Chunk Size

| Chunk Size | Read Pattern | Compression Ratio |
|------------|--------------|-------------------|
| 16KB | Random reads | Lower |
| 64KB (default) | Mixed | Balanced |
| 256KB | Sequential reads | Higher |

```sql
-- Smaller chunks for random reads
ALTER TABLE random_access WITH compression = {
    'class': 'LZ4Compressor',
    'chunk_length_in_kb': 16
};

-- Larger chunks for sequential reads
ALTER TABLE sequential_access WITH compression = {
    'class': 'LZ4Compressor',
    'chunk_length_in_kb': 256
};
```

---

## SSTable Tools

### sstablemetadata

Display SSTable metadata:

```bash
tools/bin/sstablemetadata /path/to/na-1-big-Data.db
```

Output includes:
- Partition count
- Row count
- Timestamp range
- Tombstone statistics
- Compression ratio

### sstableutil

List SSTable files:

```bash
tools/bin/sstableutil keyspace table
```

### sstabledump

Dump SSTable contents as JSON:

```bash
tools/bin/sstabledump /path/to/na-1-big-Data.db
```

### sstablescrub

Rebuild SSTable, removing corrupt data:

```bash
tools/bin/sstablescrub keyspace table
```

### sstableexpiredblockers

Find SSTables blocking tombstone removal:

```bash
tools/bin/sstableexpiredblockers keyspace table
```

---

## Monitoring SSTables

```bash
# SSTable count per table
nodetool tablestats keyspace.table | grep "SSTable count"

# Total disk usage
nodetool tablestats keyspace.table | grep "Space used"

# List SSTables
ls -la /var/lib/cassandra/data/keyspace/table-*/

# SSTable sizes
du -sh /var/lib/cassandra/data/keyspace/table-*/*.db
```

### JMX Metrics

```
org.apache.cassandra.metrics:type=Table,name=LiveSSTableCount
org.apache.cassandra.metrics:type=Table,name=SSTablesPerReadHistogram
org.apache.cassandra.metrics:type=Table,name=TotalDiskSpaceUsed
org.apache.cassandra.metrics:type=Table,name=CompressionRatio
```

---

## Related Documentation

- **[Storage Engine Overview](index.md)** - Architecture overview
- **[Write Path](write-path.md)** - How SSTables are created
- **[Read Path](read-path.md)** - How SSTables are read
- **[Compaction](../compaction/index.md)** - How SSTables are merged
