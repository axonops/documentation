# nodetool reloadlocalschema

Reloads the local schema from disk.

## Synopsis

```bash
nodetool [connection_options] reloadlocalschema
```

## Description

The `reloadlocalschema` command reloads the schema from the local system tables. Use when schema files have been manually modified.

## Examples

```bash
nodetool reloadlocalschema
```

## Related Commands

- [resetlocalschema](resetlocalschema.md) - Reset schema to cluster state
- [describecluster](describecluster.md) - Check schema versions

## Related Documentation

- [Troubleshooting - Schema Disagreement](../../../troubleshooting/playbooks/schema-disagreement.md)
