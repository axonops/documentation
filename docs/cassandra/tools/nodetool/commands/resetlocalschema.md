# nodetool resetlocalschema

Resets the local schema to match the cluster schema.

## Synopsis

```bash
nodetool [connection_options] resetlocalschema
```

## Description

The `resetlocalschema` command drops the local schema and rebuilds it from other nodes in the cluster. Use when a node has persistent schema disagreement.

## Examples

```bash
nodetool resetlocalschema
```

## Caution

This command drops and rebuilds local schema. Only use when:
- Node has persistent schema disagreement
- Schema appears corrupted
- Other schema sync methods have failed

## Related Commands

- [describecluster](describecluster.md) - Check schema versions
- [reloadlocalschema](reloadlocalschema.md) - Reload from disk

## Related Documentation

- [Troubleshooting - Schema Disagreement](../../../troubleshooting/playbooks/schema-disagreement.md)
