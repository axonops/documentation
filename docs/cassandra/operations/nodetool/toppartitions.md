# nodetool toppartitions

Samples and displays the most active partitions.

---

## Synopsis

```bash
nodetool [connection_options] toppartitions [options] <keyspace> <table> <duration>
```

## Description

`nodetool toppartitions` samples partition access over a specified duration and reports the most frequently accessed partitions. This helps identify hot partitions that may be causing performance issues.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | The keyspace to sample |
| `table` | The table to sample |
| `duration` | Sampling duration in milliseconds |

---

## Options

| Option | Description |
|--------|-------------|
| `-s, --size <count>` | Number of top partitions to return (default: 10) |
| `-k, --ks-filters <filters>` | Keyspace filters |
| `-c, --cf-filters <filters>` | Table (column family) filters |
| `-a, --samplers <samplers>` | Sampler types: READS, WRITES, CAS_CONTENTIONS |

---

## Output Format

```
WRITES Sampler:
  Cardinality: ~1000
  Top 10 partitions:
    Partition                   Count       +/-
    user_12345                  150         10
    user_67890                  120         8
    user_11111                  95          7
    ...

READS Sampler:
  Cardinality: ~800
  Top 10 partitions:
    Partition                   Count       +/-
    product_abc                 200         15
    product_xyz                 180         12
    ...
```

---

## Examples

### Sample for 10 Seconds (10000 ms)

```bash
nodetool toppartitions my_keyspace my_table 10000
```

### Sample with More Results

```bash
nodetool toppartitions -s 20 my_keyspace my_table 30000
```

### Sample Reads Only

```bash
nodetool toppartitions -a READS my_keyspace my_table 10000
```

### Sample Writes Only

```bash
nodetool toppartitions -a WRITES my_keyspace my_table 10000
```

### Sample CAS Contentions

```bash
nodetool toppartitions -a CAS_CONTENTIONS my_keyspace my_table 10000
```

---

## Understanding Results

### Cardinality

```
Cardinality: ~1000
```

Estimated number of unique partitions accessed during sampling.

### Count

```
user_12345     150     10
```

- `150`: Number of times this partition was accessed
- `10`: Statistical margin of error

### Hot Partition Indicators

| Metric | Warning Sign |
|--------|--------------|
| Single partition >> others | Potential hot partition |
| High count + high error | Variable access pattern |
| Low cardinality + high count | Few partitions handling all traffic |

---

## Use Cases

### Identify Hot Partitions

```bash
# Sample during peak traffic
nodetool toppartitions my_keyspace my_table 60000
```

Hot partitions may indicate:
- Data model issues (poor partition key choice)
- Application bugs (always accessing same key)
- Natural access patterns (celebrity problem)

### Performance Troubleshooting

```bash
# When seeing high latency
nodetool toppartitions -s 20 my_keyspace slow_table 30000
```

If one partition dominates, investigate that partition.

### Capacity Planning

```bash
# Understand access distribution
nodetool toppartitions -s 50 my_keyspace my_table 300000
```

Even distribution = good
Skewed distribution = potential scaling issue

---

## Sampling Strategies

### Short Sample (Quick Check)

```bash
# 10 second sample
nodetool toppartitions my_keyspace my_table 10000
```

Good for: Quick identification of obvious hot spots

### Medium Sample (Typical Analysis)

```bash
# 1 minute sample
nodetool toppartitions my_keyspace my_table 60000
```

Good for: Normal troubleshooting

### Long Sample (Thorough Analysis)

```bash
# 5 minute sample
nodetool toppartitions my_keyspace my_table 300000
```

Good for: Capturing intermittent patterns

---

## Interpreting Access Patterns

### Healthy Distribution

```
Partition      Count
part_1         100
part_2         95
part_3         92
part_4         88
...
```

Traffic distributed relatively evenly.

### Hot Partition

```
Partition      Count
hot_key        5000
part_2         50
part_3         45
...
```

One partition receiving 100x more traffic than others.

### Write-Heavy Partition

```
WRITES:
  hot_key      1000
  other        10

READS:
  hot_key      50
  other        45
```

Partition is write-heavy—may need data model review.

---

## Addressing Hot Partitions

### Data Model Solutions

1. **Add randomization to partition key**
   ```sql
   -- Instead of
   CREATE TABLE events (date DATE, event_id UUID, ...);

   -- Use bucketing
   CREATE TABLE events (date DATE, bucket INT, event_id UUID, ...);
   ```

2. **Composite partition key**
   ```sql
   PRIMARY KEY ((user_id, bucket), timestamp)
   ```

### Application Solutions

1. **Client-side caching** - Reduce read frequency
2. **Write batching** - Reduce write frequency
3. **Load spreading** - Distribute across multiple keys

---

## Automation Example

```bash
#!/bin/bash
# monitor_hot_partitions.sh

KEYSPACE=$1
TABLE=$2
DURATION=60000  # 1 minute
THRESHOLD=100   # Alert if count > 100

result=$(nodetool toppartitions -s 5 $KEYSPACE $TABLE $DURATION 2>/dev/null)

# Parse top partition count
top_count=$(echo "$result" | grep -A2 "Top" | tail -1 | awk '{print $2}')

if [ -n "$top_count" ] && [ "$top_count" -gt "$THRESHOLD" ]; then
    echo "ALERT: Hot partition detected in $KEYSPACE.$TABLE"
    echo "$result"
fi
```

---

## Limitations

!!! info "Sampling Limitations"
    - Results are statistical samples, not exact counts
    - Short samples may miss intermittent patterns
    - High-traffic tables need longer sampling
    - Sampling adds minimal overhead

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [tablestats](tablestats.md) | Overall table statistics |
| [tablehistograms](tablehistograms.md) | Latency distributions |
| [proxyhistograms](proxyhistograms.md) | Coordinator latencies |
| [tpstats](tpstats.md) | Thread pool statistics |
