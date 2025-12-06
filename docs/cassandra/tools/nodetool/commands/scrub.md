# nodetool scrub

Rebuilds SSTables, attempting to fix corruption.

## Synopsis

```bash
nodetool [connection_options] scrub [options] [keyspace [table ...]]
```

## Description

The `scrub` command rebuilds SSTables by reading and rewriting data, removing any corrupted rows in the process.

## Options

| Option | Description |
|--------|-------------|
| -n, --no-validate | Skip column validation |
| -s, --skip-corrupted | Skip corrupted rows instead of failing |
| -r, --reinsert-overflowed-ttl | Reinsert rows with overflowed TTL |
| -j, --jobs | Number of parallel jobs |

## Examples

```bash
# Scrub with corrupted row skip
nodetool scrub --skip-corrupted my_keyspace users

# Basic scrub
nodetool scrub my_keyspace users
```

**Caution:** Using `--skip-corrupted` may result in data loss.

## Related Commands

- [verify](verify.md) - Verify SSTable integrity
- [compact](compact.md) - Force compaction

## Related Documentation

- [Troubleshooting - Diagnosis](../../../troubleshooting/diagnosis/index.md)
- [Tools - SSTable Tools](../../sstable-tools/index.md)
