# nodetool gcstats

Displays garbage collection statistics.

## Synopsis

```bash
nodetool [connection_options] gcstats
```

## Description

The `gcstats` command shows JVM garbage collection statistics including pause times and memory reclamation.

## Examples

```bash
nodetool gcstats
```

**Output:**
```
       Interval (ms) Max GC Elapsed (ms)Total GC Elapsed (ms)Stdev GC Elapsed (ms)   GC Reclaimed (MB)         Collections      Direct Memory Bytes
              311890                 234                12345                   45               123456                 234                12345678
```

## Key Metrics

| Metric | Description | Warning Threshold |
|--------|-------------|-------------------|
| Max GC Elapsed | Longest GC pause | > 500ms |
| Stdev GC Elapsed | Pause time variability | High value = inconsistent |
| GC Reclaimed | Memory freed | Low = memory pressure |

## Related Commands

- [info](info.md) - Heap memory usage
- [tpstats](tpstats.md) - Thread pool statistics

## Related Documentation

- [Performance - JVM Tuning](../../../operations/performance/jvm-tuning/index.md)
- [Troubleshooting - GC Pause](../../../troubleshooting/playbooks/gc-pause.md)
