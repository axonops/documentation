---
title: "nodetool datapaths"
description: "Display data file locations for Cassandra tables using nodetool datapaths command."
meta:
  - name: keywords
    content: "nodetool datapaths, data directories, Cassandra paths, SSTable locations"
---

# nodetool datapaths

!!! info "Cassandra 4.1+"
    This command is available in Cassandra 4.1 and later.

Displays the data file directories for the node.

---

## Synopsis

```bash
nodetool [connection_options] datapaths [options] [--] [<keyspace.table> | <keyspace>]
```

## Description

`nodetool datapaths` shows the data file paths for tables on the Cassandra node. The output is organized by keyspace and table, showing where each table's SSTables are stored.

## Options

| Option | Description |
|--------|-------------|
| `-F, --format <format>` | Output format (`json` or `yaml`) |

---

## Examples

### Basic Usage

```bash
nodetool datapaths
```

### Sample Output

```
Keyspace: my_keyspace
        Table: users
                /var/lib/cassandra/data/my_keyspace/users-abc123
        Table: orders
                /var/lib/cassandra/data/my_keyspace/orders-def456
Keyspace: system
        Table: local
                /var/lib/cassandra/data/system/local-xyz789
...
```

### Filter by Keyspace or Table

```bash
# Show paths for specific table
nodetool datapaths my_keyspace.users

# Show paths for all tables in a keyspace
nodetool datapaths my_keyspace
```

---

## Configuration

Data paths are configured in cassandra.yaml:

```yaml
# cassandra.yaml
data_file_directories:
    - /var/lib/cassandra/data

# Or multiple directories:
data_file_directories:
    - /mnt/disk1/cassandra/data
    - /mnt/disk2/cassandra/data
```

---

## Use Cases

### Verify Configuration

```bash
# Confirm data directory paths
nodetool datapaths
```

### Disk Space Monitoring

```bash
# Check disk space on data directories using tablestats
nodetool tablestats my_keyspace | grep "Space used"
```

### JSON Output

```bash
# Get paths in JSON format for scripting
nodetool datapaths -F json my_keyspace
```

---

## Best Practices

!!! tip "Data Path Guidelines"

    1. **Dedicated disks** - Use separate disks for data
    2. **Monitor space** - Track disk usage per path
    3. **Fast storage** - SSDs recommended for data paths
    4. **JBOD configuration** - Multiple paths for JBOD setups

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [info](info.md) | Node information including paths |
| [tablestats](tablestats.md) | Table disk usage |
| [status](status.md) | Cluster overview |