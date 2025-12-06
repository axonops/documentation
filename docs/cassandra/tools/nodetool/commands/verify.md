# nodetool verify

Verifies SSTable integrity by checking checksums.

## Synopsis

```bash
nodetool [connection_options] verify [options] [keyspace [table ...]]
```

## Description

The `verify` command checks SSTable integrity by validating checksums and structure without modifying data.

## Options

| Option | Description |
|--------|-------------|
| -e, --extended | Extended verification (slower, more thorough) |
| -c, --check-version | Check SSTable version compatibility |
| -t, --token-range | Verify specific token range |

## Examples

```bash
# Basic verification
nodetool verify my_keyspace users

# Extended verification
nodetool verify -e my_keyspace users
```

## Related Commands

- [scrub](scrub.md) - Rebuild SSTables
- [tablestats](tablestats.md) - Table statistics

## Related Documentation

- [Troubleshooting - Diagnosis](../../../troubleshooting/diagnosis/index.md)
