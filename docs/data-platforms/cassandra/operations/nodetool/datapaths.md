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
nodetool [connection_options] datapaths
```

## Description

`nodetool datapaths` shows the configured data directories for the Cassandra node. These are the filesystem paths where Cassandra stores SSTables and other data files.

---

## Examples

### Basic Usage

```bash
nodetool datapaths
```

### Sample Output

```
/var/lib/cassandra/data
```

Or for multiple data directories:

```
/mnt/disk1/cassandra/data
/mnt/disk2/cassandra/data
/mnt/disk3/cassandra/data
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
# Check space on data directories
for path in $(nodetool datapaths); do
    echo "$path: $(df -h $path | tail -1 | awk '{print $4}') free"
done
```

### Troubleshooting

```bash
# Verify data directories exist and are accessible
nodetool datapaths | xargs -I {} ls -la {}
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
