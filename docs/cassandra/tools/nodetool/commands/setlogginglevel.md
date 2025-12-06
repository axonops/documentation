# nodetool setlogginglevel

Dynamically changes the logging level.

## Synopsis

```bash
nodetool [connection_options] setlogginglevel <class_qualifier> <level>
```

## Description

The `setlogginglevel` command changes the logging level for a specific logger at runtime without restarting Cassandra.

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| class_qualifier | Yes | Logger class or package name |
| level | Yes | Log level: TRACE, DEBUG, INFO, WARN, ERROR |

## Examples

```bash
# Debug compaction
nodetool setlogginglevel org.apache.cassandra.db.compaction DEBUG

# Debug repair
nodetool setlogginglevel org.apache.cassandra.repair DEBUG

# Reset to INFO
nodetool setlogginglevel org.apache.cassandra.db.compaction INFO
```

## Common Loggers

| Logger | Purpose |
|--------|---------|
| org.apache.cassandra.db.compaction | Compaction |
| org.apache.cassandra.repair | Repair |
| org.apache.cassandra.streaming | Streaming |
| org.apache.cassandra.net | Network |
| org.apache.cassandra.cql3 | CQL |
| org.apache.cassandra.hints | Hints |
| org.apache.cassandra.gms | Gossip |

## Related Commands

- [getlogginglevels](getlogginglevels.md) - View current levels

## Related Documentation

- [Troubleshooting - Log Analysis](../../../troubleshooting/log-analysis/index.md)
