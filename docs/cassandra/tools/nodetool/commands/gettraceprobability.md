# nodetool gettraceprobability

Gets the current query tracing probability.

## Synopsis

```bash
nodetool [connection_options] gettraceprobability
```

## Description

The `gettraceprobability` command displays the current probability setting for query tracing.

## Examples

```bash
nodetool gettraceprobability
```

**Output:**
```
Current trace probability: 0.01
```

## Related Commands

- [settraceprobability](settraceprobability.md) - Set trace probability

## Related Documentation

- [Performance - Query Optimization](../../../performance/query-optimization/index.md)
