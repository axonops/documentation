# nodetool reloadtriggers

Reloads trigger classes from the triggers directory.

## Synopsis

```bash
nodetool [connection_options] reloadtriggers
```

## Description

The `reloadtriggers` command reloads custom trigger classes from the `triggers/` directory without restarting Cassandra.

## Examples

```bash
nodetool reloadtriggers
```

## Use Case

After adding or modifying trigger JAR files in the triggers directory, use this command to load them without node restart.

## Related Documentation

- [Configuration - cassandra.yaml](../../../configuration/cassandra-yaml/index.md)
