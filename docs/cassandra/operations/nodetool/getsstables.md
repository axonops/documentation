# nodetool getsstables

Lists SSTables containing a partition key.

---

## Synopsis

```bash
nodetool [connection_options] getsstables [--hex-format] <keyspace> <table> <key>
```

## Description

`nodetool getsstables` identifies which SSTable files contain data for a specific partition key. This is useful for debugging, investigating data distribution, or understanding where specific data resides on disk.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | Target keyspace name |
| `table` | Target table name |
| `key` | Partition key value |

## Options

| Option | Description |
|--------|-------------|
| `--hex-format` | Interpret key as hex-encoded bytes |

---

## Examples

### Basic Usage

```bash
nodetool getsstables my_keyspace my_table user123
```

### Hex-Encoded Key

```bash
nodetool getsstables --hex-format my_keyspace my_table 0x1234567890abcdef
```

### Sample Output

```
/var/lib/cassandra/data/my_keyspace/my_table-12345678901234567890/mc-1-big-Data.db
/var/lib/cassandra/data/my_keyspace/my_table-12345678901234567890/mc-5-big-Data.db
```

---

## Use Cases

### Debug Data Location

```bash
# Find which SSTables contain specific partition
nodetool getsstables my_keyspace users user_12345
```

### Investigate Hot Partitions

```bash
# Check if hot key spans multiple SSTables
nodetool getsstables my_keyspace events hot_partition_key | wc -l
```

### Verify Compaction

```bash
# Before and after compaction, check key distribution
nodetool getsstables my_keyspace my_table test_key
```

---

## Best Practices

!!! tip "Usage Guidelines"

    1. **Know key format** - Ensure correct key encoding
    2. **Multiple SSTables normal** - Data may span multiple files
    3. **Post-compaction** - Fewer SSTables after compaction

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [tablestats](tablestats.md) | Table SSTable counts |
| [compact](compact.md) | Force compaction |
| [getendpoints](getendpoints.md) | Find replicas for key |
