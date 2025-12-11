# Cassandra SSTable Tools

Command-line tools for SSTable inspection, maintenance, and recovery.

## sstableutil

List SSTable files for a table.

```bash
# List all SSTables for a table
sstableutil keyspace table

# Include temporary files
sstableutil -t keyspace table

# Show only data files
sstableutil -d keyspace table

# Cleanup temporary files
sstableutil -c keyspace table
```

## sstablemetadata

Display SSTable metadata and statistics.

```bash
# View metadata
sstablemetadata /var/lib/cassandra/data/keyspace/table-uuid/nb-1-big-Data.db

# Key information shown:
# - SSTable min/max timestamps
# - Partition count estimate
# - Compression ratio
# - Tombstone count
# - Clustering columns
```

### Sample Output

```
SSTable: /var/lib/cassandra/data/ks/users-abc123/nb-1-big-Data.db
Partitioner: org.apache.cassandra.dht.Murmur3Partitioner
Bloom Filter FP chance: 0.010000
Minimum timestamp: 1704067200000000
Maximum timestamp: 1704153600000000
Compression ratio: 0.456
Estimated droppable tombstones: 0.15
SSTable Level: 0
Repaired at: 0
Minimum TTL: 0
Maximum TTL: 86400
First token: -9223372036854775808
Last token: 9223372036854775807
Estimated partition count: 50000
```

## sstabledump

Export SSTable content as JSON.

```bash
# Dump entire SSTable
sstabledump /var/lib/cassandra/data/keyspace/table-uuid/nb-1-big-Data.db

# Dump specific partition
sstabledump -k partition_key /path/to/Data.db

# Exclude deleted data
sstabledump -d /path/to/Data.db

# Pretty print
sstabledump /path/to/Data.db | python -m json.tool
```

### Sample Output

```json
[
  {
    "partition": {
      "key": ["user123"],
      "position": 0
    },
    "rows": [
      {
        "type": "row",
        "clustering": ["2024-01-01"],
        "cells": [
          {"name": "email", "value": "user@example.com"},
          {"name": "name", "value": "John Doe"}
        ]
      }
    ]
  }
]
```

## sstablekeys

Extract partition keys from SSTable.

```bash
# List all partition keys
sstablekeys /var/lib/cassandra/data/keyspace/table-uuid/nb-1-big-Data.db

# Pipe to file
sstablekeys /path/to/Data.db > keys.txt

# Count keys
sstablekeys /path/to/Data.db | wc -l
```

## sstableexpiredblockers

Find SSTables blocking tombstone removal.

```bash
# Check for tombstone blockers
sstableexpiredblockers keyspace table

# Shows SSTables preventing gc_grace_seconds cleanup
```

## sstablelevelreset

Reset SSTable levels for LeveledCompactionStrategy.

```bash
# Reset all SSTables to level 0
sstablelevelreset --really-reset keyspace table

# Use when:
# - Migrating compaction strategies
# - Fixing level distribution issues
```

## sstableofflinerelevel

Relevel SSTables offline.

```bash
# Relevel SSTables
sstableofflinerelevel keyspace table

# Use when LCS levels are unbalanced
# Node must be stopped
```

## sstablescrub

Repair corrupted SSTables.

```bash
# Scrub SSTables (node must be stopped)
sstablescrub keyspace table

# Skip corrupted rows
sstablescrub -s keyspace table

# Reinsert overflowed counters
sstablescrub -r keyspace table

# Manifest check only
sstablescrub -m keyspace table
```

**When to use:**
- After hardware failure
- Corrupted SSTables detected
- Recovery scenarios

## sstableverify

Verify SSTable integrity.

```bash
# Verify SSTables
sstableverify keyspace table

# Extended verification
sstableverify -e keyspace table

# Check specific SSTable
sstableverify -f /path/to/Data.db keyspace table
```

## sstableloader (Bulk Loader)

Bulk load SSTables into a cluster.

```bash
# Basic usage
sstableloader -d node1,node2,node3 /path/to/sstables/keyspace/table/

# With authentication
sstableloader -d node1 -u cassandra -pw password /path/to/sstables/

# With SSL
sstableloader -d node1 \
    -ts /path/to/truststore.jks \
    -tspw truststorepass \
    /path/to/sstables/

# Specify connections per host
sstableloader -d node1 -c 8 /path/to/sstables/

# Throttle transfer rate (MB/s)
sstableloader -d node1 -t 100 /path/to/sstables/
```

### Use Cases

- **Migration**: Move data between clusters
- **Restore**: Restore from SSTable backup
- **Bulk import**: Load large datasets

## sstableupgrade

Upgrade SSTables to current version.

```bash
# Upgrade SSTables
sstableupgrade keyspace table

# Required after major version upgrades
# Converts SSTable format to current version
```

## Common Workflows

### Inspect Corrupted Data

```bash
# 1. Stop node
nodetool drain && systemctl stop cassandra

# 2. Verify SSTables
sstableverify -e keyspace table

# 3. Scrub to repair
sstablescrub -s keyspace table

# 4. Start node
systemctl start cassandra
```

### Export Data for Analysis

```bash
# Dump to JSON
for f in /var/lib/cassandra/data/ks/table-*/nb-*-big-Data.db; do
    sstabledump "$f" >> table_export.json
done
```

### Find Large Partitions

```bash
# Get partition keys with sizes
for f in /var/lib/cassandra/data/ks/table-*/nb-*-big-Data.db; do
    sstablemetadata "$f" | grep -E "partition|count"
done
```

### Bulk Migration

```bash
# 1. Snapshot source
nodetool snapshot keyspace

# 2. Copy SSTables
rsync -avz /var/lib/cassandra/data/keyspace/table-*/snapshots/snap1/ \
    dest:/staging/keyspace/table/

# 3. Load into destination cluster
sstableloader -d dest1,dest2 /staging/keyspace/table/
```

---

## Next Steps

- **[nodetool](../../operations/nodetool/index.md)** - Node management commands
- **[Backup/Restore](../../operations/backup-restore/index.md)** - Backup procedures
- **[Troubleshooting](../../troubleshooting/index.md)** - Problem diagnosis
