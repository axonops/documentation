# nodetool repair_admin

Manages and monitors repair sessions (Cassandra 4.0+).

## Synopsis

```bash
nodetool [connection_options] repair_admin <subcommand> [options]
```

## Description

The `repair_admin` command provides management capabilities for repair sessions, including listing active repairs and canceling operations.

## Subcommands

| Subcommand | Description |
|------------|-------------|
| list | List all active repair sessions |
| summarize_pending | Show pending repair summary |
| summarize_repaired | Show repaired data summary |
| cancel | Cancel a repair session |

## Examples

### List Active Repairs

```bash
nodetool repair_admin list
```

**Output:**
```
id                                   state      coordinator  participants
a1b2c3d4-e5f6-7890-abcd-ef1234567890 RUNNING    10.0.0.1    [10.0.0.1, 10.0.0.2, 10.0.0.3]
```

### Cancel Repair

```bash
nodetool repair_admin cancel a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### Summarize Pending Repairs

```bash
nodetool repair_admin summarize_pending
```

## Related Commands

- [repair](repair.md) - Run repair
- [netstats](netstats.md) - Monitor streaming

## Related Documentation

- [Operations - Repair](../../../operations/repair/index.md)
- [Troubleshooting - Repair Failures](../../../troubleshooting/playbooks/repair-failures.md)

## Version Information

Available in Apache Cassandra 4.0 and later.
