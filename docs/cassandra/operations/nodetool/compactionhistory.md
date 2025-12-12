---
description: "View compaction history in Cassandra using nodetool compactionhistory. Analyze past compaction operations."
meta:
  - name: keywords
    content: "nodetool compactionhistory, compaction history, Cassandra compaction, SSTable history"
---

# nodetool compactionhistory

Displays the history of completed compaction operations.

---

## Synopsis

```bash
nodetool [connection_options] compactionhistory
```

## Description

`nodetool compactionhistory` shows information about previously completed compactions. This helps analyze compaction patterns, identify problematic tables, and understand historical compaction behavior.

---

## Output Format

```
Compaction History:
id                                   keyspace_name columnfamily_name compacted_at            bytes_in    bytes_out   rows_merged
abc12345-def6-7890-abcd-ef1234567890 my_keyspace   my_table          2024-01-15T10:30:00     1073741824  536870912   {1:150, 2:50}
def67890-abcd-1234-ef56-7890abcdef12 my_keyspace   my_table          2024-01-15T09:15:00     2147483648  1073741824  {1:300, 2:100}
```

---

## Output Fields

| Field | Description |
|-------|-------------|
| `id` | Unique compaction ID |
| `keyspace_name` | Keyspace containing the table |
| `columnfamily_name` | Table name |
| `compacted_at` | Timestamp of compaction completion |
| `bytes_in` | Total bytes read from input SSTables |
| `bytes_out` | Total bytes written to output SSTable |
| `rows_merged` | Distribution of rows merged per SSTable |

---

## Examples

### View All Compaction History

```bash
nodetool compactionhistory
```

### Filter by Keyspace

```bash
nodetool compactionhistory | grep my_keyspace
```

### Filter by Table

```bash
nodetool compactionhistory | grep my_table
```

### Recent Compactions Only

```bash
nodetool compactionhistory | head -20
```

---

## Understanding the Output

### Bytes In vs Bytes Out

```
bytes_in: 1073741824  bytes_out: 536870912
```

- **bytes_in > bytes_out**: Data was compacted (tombstones removed, duplicates merged)
- **bytes_in ≈ bytes_out**: Little compaction benefit (fresh data)
- High ratio indicates effective compaction

### Rows Merged

```
rows_merged: {1:150, 2:50}
```

- `1:150` - 150 rows appeared in only 1 SSTable (no merging needed)
- `2:50` - 50 rows appeared in 2 SSTables (were merged)

Higher numbers in the merge count indicate more overwrites or deletions being resolved.

---

## Analysis Use Cases

### Check Compaction Efficiency

```bash
# Calculate compression ratio for recent compactions
nodetool compactionhistory | awk 'NR>2 {
    if ($5 > 0) {
        ratio = $6 / $5
        printf "%s.%s: %.2f\n", $2, $3, ratio
    }
}' | head -10
```

Ratio close to 1.0 = little benefit; lower ratio = good compaction.

### Find Tables with Most Compactions

```bash
nodetool compactionhistory | awk 'NR>2 {print $2"."$3}' | sort | uniq -c | sort -rn | head -10
```

### Check Compaction Timestamps

```bash
# See when compactions occurred
nodetool compactionhistory | awk 'NR>2 {print $4}' | cut -dT -f1 | sort | uniq -c
```

---

## Troubleshooting with Compaction History

### Frequent Small Compactions

If seeing many small compactions:

```bash
nodetool compactionhistory | awk 'NR>2 && $5 < 100000000 {print}' | wc -l
```

Many small compactions may indicate:
- High write rate
- STCS with small sstable_size_in_mb
- Need to tune compaction settings

### Large Compactions Taking Too Long

```bash
# Find largest compactions
nodetool compactionhistory | awk 'NR>2 {print $5, $2"."$3}' | sort -rn | head -5
```

Consider:
- LCS for more predictable compaction sizes
- Increasing compaction throughput
- Adding more compaction threads

### No Recent Compactions

If compactionhistory shows old entries only:

```bash
# Check if compactions are running
nodetool compactionstats

# Check if auto-compaction is enabled
nodetool statusautocompaction my_keyspace my_table
```

---

## Monitoring Compaction Patterns

### Daily Compaction Volume

```bash
#!/bin/bash
# compaction_daily_stats.sh

echo "Date,Compactions,BytesIn,BytesOut"
nodetool compactionhistory | awk 'NR>2 {
    date = substr($4, 1, 10)
    counts[date]++
    bytes_in[date] += $5
    bytes_out[date] += $6
}
END {
    for (d in counts) {
        printf "%s,%d,%.2fGB,%.2fGB\n", d, counts[d], bytes_in[d]/1073741824, bytes_out[d]/1073741824
    }
}' | sort
```

### Table-Level Analysis

```bash
#!/bin/bash
# Analyze compaction efficiency by table

echo "Table,Compactions,AvgRatio"
nodetool compactionhistory | awk 'NR>2 && $5 > 0 {
    table = $2"."$3
    counts[table]++
    ratios[table] += $6/$5
}
END {
    for (t in counts) {
        printf "%s,%d,%.3f\n", t, counts[t], ratios[t]/counts[t]
    }
}' | sort -t, -k2 -rn
```

---

## History Retention

Compaction history is stored in `system.compaction_history` table:

```sql
SELECT * FROM system.compaction_history LIMIT 10;
```

!!! info "History Limits"
    - History is kept for a limited time
    - Older entries are automatically removed
    - For long-term analysis, export to external monitoring

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [compactionstats](compactionstats.md) | Current compaction status |
| [tablestats](tablestats.md) | Table statistics including SSTable count |
| [compact](compact.md) | Force compaction |
| [setcompactionthroughput](setcompactionthroughput.md) | Control compaction speed |
