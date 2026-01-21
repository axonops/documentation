---
title: "nodetool getendpoints"
description: "Find which nodes own a specific partition key using nodetool getendpoints command."
meta:
  - name: keywords
    content: "nodetool getendpoints, partition owner, replica nodes, Cassandra routing"
search:
  boost: 3
---

# nodetool getendpoints

Displays the replica nodes for a specific partition key.

---

## Synopsis

```bash
nodetool [connection_options] getendpoints <keyspace> <table> <key>
```

## Description

`nodetool getendpoints` shows which nodes store replicas for a given partition key. This is useful for debugging data placement, understanding query routing, and troubleshooting replication issues.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | The keyspace containing the table |
| `table` | The table to query |
| `key` | The partition key value |

---

## Output

```
192.168.1.101
192.168.1.102
192.168.1.103
```

Lists all replica endpoints that store data for the specified partition key.

---

## Examples

### Find Replicas for UUID Key

```bash
nodetool getendpoints my_keyspace users 550e8400-e29b-41d4-a716-446655440000
```

### Find Replicas for String Key

```bash
nodetool getendpoints my_keyspace customers "customer_123"
```

### Find Replicas for Integer Key

```bash
nodetool getendpoints my_keyspace orders 12345
```

### Find Replicas for Composite Key

For composite partition keys, use colon-separated values:

```bash
nodetool getendpoints my_keyspace events "2024-01-15:sensor_001"
```

---

## Use Cases

### Debug Data Location

```bash
# Where is this user's data stored?
nodetool getendpoints my_app users "user@example.com"
```

### Verify Replication

```bash
# Check if RF=3 is working
endpoints=$(nodetool getendpoints my_keyspace my_table "key123")
echo "$endpoints" | wc -l
# Should output: 3
```

### Troubleshoot Missing Data

```bash
# Find replicas, then query each directly
REPLICAS=$(nodetool getendpoints my_keyspace my_table "problem_key")
for host in $REPLICAS; do
    echo "=== $host ==="
    cqlsh $host -e "SELECT * FROM my_keyspace.my_table WHERE pk = 'problem_key';"
done
```

### Understand Query Routing

```bash
# See which nodes a driver will contact for this key
nodetool getendpoints my_keyspace my_table "hot_partition"
```

---

## Understanding the Output

### With RF=3 in Single DC

```bash
$ nodetool getendpoints my_keyspace my_table "key1"
192.168.1.101
192.168.1.102
192.168.1.103
```

The partition is stored on these 3 nodes.

### With NetworkTopologyStrategy (Multi-DC)

```bash
$ nodetool getendpoints my_keyspace my_table "key1"
192.168.1.101  # DC1
192.168.1.102  # DC1
192.168.1.103  # DC1
192.168.2.101  # DC2
192.168.2.102  # DC2
192.168.2.103  # DC2
```

Shows replicas in both datacenters.

---

## How It Works

1. Cassandra computes `token = hash(partition_key)`
2. Finds the node owning that token on the ring
3. Returns that node plus RF-1 subsequent nodes (or per-DC replicas)

```
partition_key → hash → token → primary replica → replica list
```

---

## Key Format by Data Type

| Key Type | Example Command |
|----------|-----------------|
| UUID | `nodetool getendpoints ks tbl 550e8400-e29b-...` |
| Text | `nodetool getendpoints ks tbl "my_string"` |
| Int | `nodetool getendpoints ks tbl 12345` |
| Composite | `nodetool getendpoints ks tbl "part1:part2"` |

---

## Scripting Examples

### Check All Keys in a List

```bash
#!/bin/bash
# check_key_distribution.sh

KS=$1
TBL=$2

while read key; do
    echo "Key: $key"
    nodetool getendpoints $KS $TBL "$key"
    echo "---"
done < keys.txt
```

### Find Hot Partition Owners

```bash
#!/bin/bash
# Find which nodes own suspected hot partitions

for key in "hot_key_1" "hot_key_2" "hot_key_3"; do
    echo "=== $key ==="
    nodetool getendpoints my_keyspace my_table "$key"
done | sort | uniq -c | sort -rn
```

### Verify Cross-DC Replication

```bash
#!/bin/bash
# Ensure key has replicas in both DCs

KEY=$1
ENDPOINTS=$(nodetool getendpoints my_keyspace my_table "$KEY")

DC1_COUNT=$(echo "$ENDPOINTS" | grep "192.168.1" | wc -l)
DC2_COUNT=$(echo "$ENDPOINTS" | grep "192.168.2" | wc -l)

echo "DC1 replicas: $DC1_COUNT"
echo "DC2 replicas: $DC2_COUNT"
```

---

## Common Issues

### Key Not Found Error

If the table doesn't exist or keyspace is wrong:

```
Table 'my_keyspace.nonexistent' does not exist
```

### Wrong Key Format

For composite partition keys, ensure correct format:

```bash
# Wrong (for composite key)
nodetool getendpoints ks tbl "value1" "value2"

# Correct (colon-separated)
nodetool getendpoints ks tbl "value1:value2"
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [ring](ring.md) | Token distribution overview |
| [describering](describering.md) | Token ranges with replicas |
| [status](status.md) | Node status and load |
| [gossipinfo](gossipinfo.md) | Detailed node information |
