---
title: "Cassandra SSTable Tools"
description: "Complete SSTable tools reference for Apache Cassandra including sstableloader, sstabledump, sstablescrub, and other offline utilities."
meta:
  - name: keywords
    content: "SSTable tools, Cassandra utilities, sstableloader, sstabledump, sstablescrub, offline tools"
---

# SSTable Tools

Apache Cassandra provides a suite of command-line utilities for managing SSTables (Sorted String Tables) directly on disk. These tools operate at the storage layer, enabling administrators to inspect, repair, migrate, and manipulate SSTable files outside of normal Cassandra operations.

---

## Overview

### What Are SSTables?

SSTables are immutable data files that store Cassandra's on-disk data. Each SSTable consists of multiple component files:

```
Data.db          # Actual row data
Index.db         # Partition index
Filter.db        # Bloom filter for partition lookup
Statistics.db    # SSTable metadata and statistics
Summary.db       # Index summary for faster lookups
TOC.txt          # Table of contents listing components
CompressionInfo.db  # Compression metadata (if compressed)
Digest.crc32     # Checksum for data integrity
```

### When to Use SSTable Tools

| Scenario | Tool |
|----------|------|
| Bulk loading data into cluster | [sstableloader](sstableloader.md) |
| Recovering from SSTable corruption | [sstablescrub](sstablescrub.md) |
| Verifying SSTable integrity | [sstableverify](sstableverify.md) |
| Upgrading after Cassandra version change | [sstableupgrade](sstableupgrade.md) |
| Inspecting SSTable contents | [sstabledump](sstabledump.md) |
| Viewing SSTable metadata | [sstablemetadata](sstablemetadata.md) |
| Finding large partitions | [sstablepartitions](sstablepartitions.md) |
| Splitting oversized SSTables | [sstablesplit](sstablesplit.md) |
| Managing repair status | [sstablerepairedset](sstablerepairedset.md) |
| Fixing LCS level issues | [sstablelevelreset](sstablelevelreset.md), [sstableofflinerelevel](sstableofflinerelevel.md) |
| Diagnosing tombstone issues | [sstableexpiredblockers](sstableexpiredblockers.md) |
| Listing SSTable files | [sstableutil](sstableutil.md) |

---

## Critical Requirements

!!! danger "Stop Cassandra Before Running Most Tools"
    **Most SSTable tools require Cassandra to be stopped** before execution. Running these tools while Cassandra is active can cause:

    - Data corruption
    - Inconsistent reads
    - SSTable file conflicts
    - Unexpected behavior

    **Exceptions:** `sstablepartitions` and `sstableutil` can run while Cassandra is active.

### Pre-Execution Checklist

```bash
# 1. Verify Cassandra is stopped
nodetool drain                    # Flush and stop accepting writes
sudo systemctl stop cassandra     # Stop the service
pgrep -f CassandraDaemon         # Verify no process running

# 2. Backup before destructive operations
nodetool snapshot -t before_sstable_ops keyspace_name

# 3. Verify SSTable locations
ls -la /var/lib/cassandra/data/<keyspace>/<table>-*/
```

---

## Tool Categories

### Data Loading and Migration

Tools for moving data into Cassandra clusters.

| Tool | Description | Cassandra Running? |
|------|-------------|--------------------|
| [sstableloader](sstableloader.md) | Bulk load SSTables into a live cluster | **Yes** (target cluster) |

### Repair and Recovery

Tools for fixing corrupted or problematic SSTables.

| Tool | Description | Cassandra Running? |
|------|-------------|--------------------|
| [sstablescrub](sstablescrub.md) | Remove corruption, preserve valid data | No |
| [sstableverify](sstableverify.md) | Check SSTable integrity without modification | No |

### Inspection and Diagnostics

Tools for examining SSTable contents and metadata.

| Tool | Description | Cassandra Running? |
|------|-------------|--------------------|
| [sstabledump](sstabledump.md) | Export SSTable data as JSON | No |
| [sstablemetadata](sstablemetadata.md) | Display SSTable statistics and properties | No |
| [sstablepartitions](sstablepartitions.md) | Identify large partitions | Yes (safe) |
| [sstableexpiredblockers](sstableexpiredblockers.md) | Find SSTables blocking tombstone removal | No |
| [sstableutil](sstableutil.md) | List SSTable files for a table | Yes (safe) |

### Maintenance and Optimization

Tools for SSTable maintenance operations.

| Tool | Description | Cassandra Running? |
|------|-------------|--------------------|
| [sstableupgrade](sstableupgrade.md) | Upgrade SSTables to current Cassandra version | No |
| [sstablesplit](sstablesplit.md) | Split large SSTables into smaller files | No |
| [sstablelevelreset](sstablelevelreset.md) | Reset LCS levels to zero | No |
| [sstableofflinerelevel](sstableofflinerelevel.md) | Recalculate LCS levels offline | No |
| [sstablerepairedset](sstablerepairedset.md) | Mark SSTables as repaired/unrepaired | No |

---

## SSTable File Locations

### Default Paths

```bash
# Data directory (default)
/var/lib/cassandra/data/<keyspace>/<table>-<uuid>/

# Example
/var/lib/cassandra/data/my_keyspace/users-a1b2c3d4e5f6/

# SSTable naming convention (Cassandra 3.0+)
<version>-<generation>-<format>-<component>.db
# Example: nb-1-big-Data.db
```

### Finding SSTables

```bash
# List all SSTables for a table
sstableutil my_keyspace my_table

# Find Data.db files directly
find /var/lib/cassandra/data/my_keyspace/my_table-*/ -name "*Data.db"

# Find with human-readable sizes
find /var/lib/cassandra/data/my_keyspace/my_table-*/ -name "*Data.db" -exec ls -lh {} \;
```

---

## Common Workflows

### Workflow 1: Recovering from Corruption

When Cassandra reports SSTable corruption or fails to start:

```bash
# 1. Stop Cassandra
sudo systemctl stop cassandra

# 2. Identify corrupted SSTables
sstableverify my_keyspace my_table

# 3. Attempt to scrub corrupted files
sstablescrub my_keyspace my_table

# 4. If scrub fails, try with skip-corrupted
sstablescrub --skip-corrupted my_keyspace my_table

# 5. Start Cassandra
sudo systemctl start cassandra

# 6. Run repair to restore consistency
nodetool repair my_keyspace my_table
```

### Workflow 2: Post-Upgrade SSTable Migration

After upgrading Cassandra to a new major version:

```bash
# 1. Stop Cassandra after upgrade
sudo systemctl stop cassandra

# 2. Upgrade all SSTables
sstableupgrade my_keyspace my_table

# Or upgrade all tables in keyspace
for table in $(ls /var/lib/cassandra/data/my_keyspace/); do
    table_name=$(echo $table | cut -d'-' -f1)
    sstableupgrade my_keyspace $table_name
done

# 3. Start Cassandra
sudo systemctl start cassandra
```

### Workflow 3: Bulk Loading Data

Loading SSTables from another cluster or backup:

```bash
# 1. Prepare directory structure
mkdir -p /tmp/load/my_keyspace/my_table/

# 2. Copy SSTable files
cp /backup/my_keyspace/my_table/*.db /tmp/load/my_keyspace/my_table/

# 3. Load into cluster (Cassandra must be running on target)
sstableloader -d node1,node2,node3 /tmp/load/my_keyspace/my_table/

# 4. Verify data loaded
cqlsh -e "SELECT COUNT(*) FROM my_keyspace.my_table;"
```

### Workflow 4: Diagnosing Large Partitions

Finding partitions that may cause performance issues:

```bash
# 1. Scan for large partitions (can run while Cassandra is up)
sstablepartitions --min-size 100MiB /var/lib/cassandra/data/my_keyspace/my_table-*/

# 2. Get detailed metadata
sstablemetadata /var/lib/cassandra/data/my_keyspace/my_table-*/nb-1-big-Data.db

# 3. Dump specific partition for analysis
sstabledump -k "problem_partition_key" /path/to/sstable-Data.db
```

### Workflow 5: Preparing for Incremental Repair Migration

Migrating to incremental repair:

```bash
# 1. Stop Cassandra
sudo systemctl stop cassandra

# 2. Mark all existing SSTables as unrepaired
find /var/lib/cassandra/data/my_keyspace/my_table-*/ -name "*Data.db" -print0 | \
    xargs -0 -I {} sstablerepairedset --really-set --is-unrepaired {}

# 3. Start Cassandra
sudo systemctl start cassandra

# 4. Run incremental repair
nodetool repair -pr my_keyspace my_table
```

---

## Tool Reference Quick Guide

### Inspection Commands (Read-Only)

```bash
# View SSTable metadata
sstablemetadata /path/to/sstable-Data.db

# Dump entire SSTable as JSON
sstabledump /path/to/sstable-Data.db

# Dump specific partition
sstabledump -k "partition_key" /path/to/sstable-Data.db

# Find large partitions
sstablepartitions --min-size 50MiB /path/to/data/

# List SSTable files
sstableutil my_keyspace my_table

# Find expired tombstone blockers
sstableexpiredblockers my_keyspace my_table
```

### Repair Commands (Modifies Data)

```bash
# Verify SSTable integrity
sstableverify my_keyspace my_table

# Scrub corrupted SSTables
sstablescrub my_keyspace my_table

# Scrub with options
sstablescrub --skip-corrupted --no-validate my_keyspace my_table
```

### Maintenance Commands (Modifies Data)

```bash
# Upgrade SSTables after version upgrade
sstableupgrade my_keyspace my_table

# Split large SSTables (50MB default)
sstablesplit --size 100 /path/to/sstable-Data.db

# Reset LCS levels
sstablelevelreset --really-reset my_keyspace my_table

# Relevel offline
sstableofflinerelevel my_keyspace my_table

# Mark as repaired
sstablerepairedset --really-set --is-repaired /path/to/sstable-Data.db
```

### Data Loading

```bash
# Load SSTables into cluster
sstableloader -d host1,host2 /path/to/keyspace/table/

# With throttling
sstableloader -d host1,host2 --throttle-mib 50 /path/to/keyspace/table/

# With authentication
sstableloader -d host1,host2 -u user -pw pass /path/to/keyspace/table/
```

---

## Troubleshooting

### Tool Won't Run

```bash
# Check JAVA_HOME
echo $JAVA_HOME

# Check Cassandra environment
source /etc/cassandra/cassandra-env.sh

# Run with full path
/usr/share/cassandra/tools/bin/sstablemetadata /path/to/sstable
```

### Permission Denied

```bash
# Tools must run as cassandra user or with appropriate permissions
sudo -u cassandra sstablemetadata /var/lib/cassandra/data/...

# Or fix permissions
sudo chown -R cassandra:cassandra /var/lib/cassandra/data/
```

### SSTable Not Found

```bash
# Use sstableutil to find correct paths
sstableutil my_keyspace my_table

# Check for transaction logs indicating in-progress operations
ls /var/lib/cassandra/data/my_keyspace/my_table-*/*.log
```

### Out of Memory

```bash
# Increase heap for SSTable tools
export JVM_OPTS="-Xmx4G"
sstablescrub my_keyspace my_table

# Or edit cassandra-env.sh
```

---

## Best Practices

!!! tip "SSTable Tool Guidelines"

    1. **Always backup first** - Snapshot before running destructive tools
    2. **Stop Cassandra** - Most tools require Cassandra to be stopped
    3. **Run as cassandra user** - Ensure proper file permissions
    4. **Test in staging** - Validate procedures before production
    5. **Monitor disk space** - Some tools create temporary files
    6. **Check exit codes** - Verify tools completed successfully
    7. **Run repair after** - Restore consistency after SSTable modifications

!!! warning "Data Safety"

    - `sstablescrub` may drop corrupted rows permanently
    - `sstablesplit` creates new files before removing originals
    - `sstablerepairedset` affects incremental repair behavior
    - Always have a repair strategy after SSTable modifications

---

## Tools Reference

| Tool | Purpose | Documentation |
|------|---------|---------------|
| sstabledump | Export SSTable data as JSON | [sstabledump](sstabledump.md) |
| sstableexpiredblockers | Find tombstone blocking SSTables | [sstableexpiredblockers](sstableexpiredblockers.md) |
| sstablelevelreset | Reset LCS levels to zero | [sstablelevelreset](sstablelevelreset.md) |
| sstableloader | Bulk load SSTables into cluster | [sstableloader](sstableloader.md) |
| sstablemetadata | Display SSTable metadata | [sstablemetadata](sstablemetadata.md) |
| sstableofflinerelevel | Recalculate LCS levels | [sstableofflinerelevel](sstableofflinerelevel.md) |
| sstablepartitions | Find large partitions | [sstablepartitions](sstablepartitions.md) |
| sstablerepairedset | Manage repair status | [sstablerepairedset](sstablerepairedset.md) |
| sstablescrub | Repair corrupted SSTables | [sstablescrub](sstablescrub.md) |
| sstablesplit | Split large SSTables | [sstablesplit](sstablesplit.md) |
| sstableupgrade | Upgrade SSTable format | [sstableupgrade](sstableupgrade.md) |
| sstableutil | List SSTable files | [sstableutil](sstableutil.md) |
| sstableverify | Verify SSTable integrity | [sstableverify](sstableverify.md) |