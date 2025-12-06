# nodetool getlogginglevels

Displays current logging levels.

## Synopsis

```bash
nodetool [connection_options] getlogginglevels
```

## Description

The `getlogginglevels` command shows all loggers that have been explicitly configured with a non-default level.

## Examples

```bash
nodetool getlogginglevels
```

**Output:**
```
Logger Name                                       Log Level
ROOT                                                   INFO
org.apache.cassandra.db.compaction                    DEBUG
org.apache.cassandra.repair                           DEBUG
```

## Related Commands

- [setlogginglevel](setlogginglevel.md) - Change log levels

## Related Documentation

- [Troubleshooting - Log Analysis](../../../troubleshooting/log-analysis/index.md)
