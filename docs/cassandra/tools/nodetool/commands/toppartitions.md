# nodetool toppartitions

Samples and reports the most active partitions.

## Synopsis

```bash
nodetool [connection_options] toppartitions <keyspace> <table> <duration> [options]
```

## Description

The `toppartitions` command samples read and write activity to identify hot partitions by frequency or size.

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| keyspace | Yes | Keyspace name |
| table | Yes | Table name |
| duration | Yes | Sampling duration in milliseconds |

## Options

| Option | Description |
|--------|-------------|
| -s, --size | Number of partitions to report (default: 10) |
| -k &lt;samplers&gt; | Samplers: READS, WRITES, CAS_CONTENTIONS |

## Examples

```bash
# Sample for 60 seconds
nodetool toppartitions my_keyspace users 60000

# Top 20 by reads
nodetool toppartitions my_keyspace users 60000 -s 20 -k READS
```

**Output:**
```
WRITES Sampler:
  Cardinality: ~5234567 (256 capacity)
  Top 10 partitions:
	Partition                              Count       +/-
	user:12345678                           2345       234
	user:23456789                           1987       198
```

## Use Cases

- Identifying hot partitions
- Detecting access pattern anomalies
- Validating data model partition key choices

## Related Commands

- [tablestats](tablestats.md) - Table statistics
- [tablehistograms](tablehistograms.md) - Latency histograms

## Related Documentation

- [Data Modeling - Anti-Patterns](../../../data-modeling/anti-patterns/index.md)
- [Troubleshooting - Large Partition](../../../troubleshooting/playbooks/large-partition.md)
