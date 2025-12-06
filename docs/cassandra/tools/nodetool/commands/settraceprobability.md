# nodetool settraceprobability

Sets the probability of tracing queries.

## Synopsis

```bash
nodetool [connection_options] settraceprobability <value>
```

## Description

The `settraceprobability` command sets the probability (0.0 to 1.0) that a query will be traced. Tracing captures detailed timing for each operation step.

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| value | Yes | Probability from 0.0 (no tracing) to 1.0 (all queries) |

## Examples

```bash
# Trace 1% of queries
nodetool settraceprobability 0.01

# Disable tracing
nodetool settraceprobability 0
```

## Note

High trace probability impacts performance. Use 0.01 or lower in production.

## Related Commands

- [gettraceprobability](gettraceprobability.md) - Get current value

## Related Documentation

- [Performance - Query Optimization](../../../performance/query-optimization/index.md)
