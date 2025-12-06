# nodetool move

Moves the node to a new token position.

## Synopsis

```bash
nodetool [connection_options] move <new_token>
```

## Description

The `move` command relocates the node to a new position in the token ring. This is rarely used with virtual nodes (vnodes) enabled.

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| new_token | Yes | New token value for the node |

## Examples

```bash
nodetool move 1234567890123456789
```

## Note

With vnodes (default configuration), each node has multiple tokens (typically 256). The `move` command is designed for single-token configurations and is rarely used in modern deployments.

## Related Commands

- [ring](ring.md) - View token ring
- [status](status.md) - Check token ownership

## Related Documentation

- [Architecture - Data Distribution](../../../architecture/data-distribution.md)
