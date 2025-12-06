# nodetool proxyhistograms

Displays coordinator-level latency histograms.

## Synopsis

```bash
nodetool [connection_options] proxyhistograms
```

## Description

The `proxyhistograms` command shows end-to-end request latency at the coordinator level, including network time and consistency level coordination.

## Examples

```bash
nodetool proxyhistograms
```

**Output:**
```
Percentile       Read Latency     Write Latency     Range Latency
                     (micros)          (micros)          (micros)
50%                    892.15            234.87           1845.67
75%                   1489.45            456.23           3127.89
95%                   3561.23           1023.45           8234.56
98%                   5897.34           1756.89          14567.23
99%                   8956.78           2456.78          23456.78
Min                    182.79             35.43            746.59
Max                  45678.90          12345.67          98765.43
```

## Interpreting Results

These latencies include:
- Network round-trip time to replicas
- Consistency level coordination
- Local processing time

Compare with `tablehistograms` to isolate network vs local processing time.

## Related Commands

- [tablehistograms](tablehistograms.md) - Per-table latencies
- [tablestats](tablestats.md) - Table statistics

## Related Documentation

- [Architecture - Consistency](../../../architecture/consistency/index.md)
