---
title: "nodetool getcompactionthreshold"
description: "Display min/max compaction thresholds for a table using nodetool getcompactionthreshold."
meta:
  - name: keywords
    content: "nodetool getcompactionthreshold, compaction threshold, Cassandra compaction, table settings"
---

# nodetool getcompactionthreshold

Displays the compaction thresholds for a table.

---

## Synopsis

```bash
nodetool [connection_options] getcompactionthreshold <keyspace> <table>
```
See [connection options](index.md#connection-options) for connection options.

## Description

`nodetool getcompactionthreshold` displays the minimum and maximum SSTable count thresholds that trigger compaction for a specific table. These thresholds control when automatic compaction occurs.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | Target keyspace name |
| `table` | Target table name |

---

## Examples

### Basic Usage

```bash
nodetool getcompactionthreshold my_keyspace my_table
```

### Sample Output

```
Current compaction thresholds for my_keyspace/my_table:
 min = 4, max = 32
```

---

## Understanding Thresholds

### Minimum Threshold

- Minimum SSTables needed to trigger compaction
- Default: 4

### Maximum Threshold

- Maximum SSTables to include in single compaction
- Default: 32

---

## Use Cases

### Verify Table Configuration

```bash
# Check thresholds for a table
nodetool getcompactionthreshold my_keyspace my_table
```

### Compare with Table Stats

```bash
# Get current SSTable count
nodetool tablestats my_keyspace.my_table | grep "SSTable count"

# Compare with thresholds
nodetool getcompactionthreshold my_keyspace my_table
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [setcompactionthreshold](setcompactionthreshold.md) | Modify thresholds |
| [compactionstats](compactionstats.md) | View compaction status |
| [tablestats](tablestats.md) | Table statistics |