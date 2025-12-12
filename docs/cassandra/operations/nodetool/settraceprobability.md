# nodetool settraceprobability

Sets the probability of tracing a request.

---

## Synopsis

```bash
nodetool [connection_options] settraceprobability <probability>
```

## Description

`nodetool settraceprobability` sets the probability (0.0 to 1.0) that any given request will be traced. Trace data is stored in the `system_traces` keyspace.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `probability` | Trace probability (0.0 to 1.0) |

---

## Examples

### Enable 1% Tracing

```bash
nodetool settraceprobability 0.01
```

### Enable Full Tracing

```bash
nodetool settraceprobability 1.0
```

### Disable Tracing

```bash
nodetool settraceprobability 0.0
```

---

## When to Use

### Performance Analysis

```bash
# Enable tracing
nodetool settraceprobability 0.1

# Query traces
cqlsh -e "SELECT * FROM system_traces.sessions LIMIT 10;"

# Disable after analysis
nodetool settraceprobability 0.0
```

---

## Best Practices

!!! warning "Performance Impact"

    Tracing adds overhead. Use low probabilities in production:
    - 0.001 (0.1%) for light sampling
    - 0.01 (1%) for moderate analysis
    - Higher values only for short periods

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [gettraceprobability](gettraceprobability.md) | View current probability |
