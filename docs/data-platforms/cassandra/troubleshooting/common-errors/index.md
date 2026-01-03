---
title: "Common Cassandra Errors"
description: "Common Cassandra errors reference. Error messages and resolutions."
meta:
  - name: keywords
    content: "Cassandra errors, common errors, error messages"
---

# Common Cassandra Errors

Reference guide for frequently encountered Cassandra errors, their causes, and solutions.

---

## Error Categories

### Timeout Errors

Errors occurring when operations exceed configured time limits.

| Error | Default Timeout | Common Cause |
|-------|-----------------|--------------|
| [ReadTimeoutException](read-timeout.md) | 5000ms | Slow disk, large partitions, tombstones |
| [WriteTimeoutException](write-timeout.md) | 2000ms | Overloaded nodes, disk issues |
| RangeSliceTimeoutException | 10000ms | Large range scans |
| TruncateException | 60000ms | Large table truncation |

### Availability Errors

Errors related to replica availability.

| Error | Cause | Solution |
|-------|-------|----------|
| `UnavailableException` | Insufficient replicas alive | Check node status, reduce consistency level |
| `NoHostAvailableException` | Cannot reach any coordinator | Check network, verify cluster is running |
| `WriteFailureException` | Replica write failed | Check failing node logs |
| `ReadFailureException` | Replica read failed | Check failing node logs |

### Data Errors

Errors related to data or schema.

| Error | Cause | Solution |
|-------|-------|----------|
| `InvalidQueryException` | CQL syntax or semantic error | Fix query syntax |
| `InvalidRequestException` | Invalid request parameters | Check request parameters |
| `TombstoneOverwhelmingException` | Too many tombstones | Fix data model, run compaction |
| `SyntaxException` | CQL syntax error | Check CQL syntax |

### Authentication/Authorization Errors

Security-related errors.

| Error | Cause | Solution |
|-------|-------|----------|
| `AuthenticationException` | Invalid credentials | Verify username/password |
| `UnauthorizedException` | Insufficient permissions | Grant required permissions |

### Lightweight Transaction Errors

Errors related to LWT (Paxos-based compare-and-set operations).

| Error | Cause | Solution |
|-------|-------|----------|
| `CasWriteTimeoutException` | Paxos consensus timeout | Check for contention, increase timeout |
| LWT/non-LWT mixing issues | Mixed clock domains | Use LWT consistently for all operations on same data |
| Silent operation failures | Paxos clock vs regular timestamp conflict | See [LWT Troubleshooting](lightweight-transactions.md) |

---

## Quick Diagnosis

### Check Cluster Health

```bash
# Node status
nodetool status

# Thread pools (look for blocked/dropped)
nodetool tpstats

# Compaction status
nodetool compactionstats
```

### Check Logs

```bash
# Recent errors
grep -i "error\|exception" /var/log/cassandra/system.log | tail -50

# Specific error
grep "TimeoutException" /var/log/cassandra/system.log | tail -20
```

### Check Table Health

```bash
# Table statistics
nodetool tablestats my_keyspace.my_table

# Key metrics to check:
# - SSTable count (high = needs compaction)
# - Average tombstones per read (high = data model issue)
# - Partition size (large = data model issue)
```

---

## Error Resolution Workflow

```
Error Occurs
    │
    ▼
┌─────────────────────────────────────┐
│  1. Identify error type             │
│     - Check client exception        │
│     - Check Cassandra logs          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  2. Check cluster health            │
│     - nodetool status               │
│     - nodetool tpstats              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  3. Check specific component        │
│     - Table stats for data issues   │
│     - Compaction for performance    │
│     - Logs for stack traces         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  4. Apply fix                       │
│     - See specific error page       │
│     - Follow playbook if available  │
└─────────────────────────────────────┘
```

---

## Detailed Error Guides

### Timeout Errors

- **[ReadTimeoutException](read-timeout.md)** - Read operations timing out
- **[WriteTimeoutException](write-timeout.md)** - Write operations timing out

### Lightweight Transaction Errors

- **[LWT Troubleshooting](lightweight-transactions.md)** - Paxos contention, LWT/non-LWT mixing, timeout handling

### Playbooks for Complex Issues

For issues requiring multi-step resolution, see the [Troubleshooting Playbooks](../playbooks/index.md).

---

## Prevention

### Monitoring

Set up alerts for early warning:

| Metric | Warning Threshold | Critical Threshold |
|--------|-------------------|-------------------|
| Read latency p99 | > 100ms | > 500ms |
| Write latency p99 | > 50ms | > 200ms |
| Pending compactions | > 20 | > 100 |
| Dropped messages | > 0 | > 10/min |
| SSTable count | > 20 per table | > 50 per table |

### Best Practices

1. **Monitor proactively** - Don't wait for errors
2. **Run repairs regularly** - Weekly for most workloads
3. **Keep compaction healthy** - Monitor pending tasks
4. **Size partitions correctly** - Aim for < 100MB per partition
5. **Avoid tombstone accumulation** - Use TTLs and proper deletion patterns

---

## Related Documentation

- [Troubleshooting Overview](../index.md) - General troubleshooting framework
- [Diagnosis Guide](../diagnosis/index.md) - Systematic diagnosis procedures
- [Log Analysis](../log-analysis/index.md) - Understanding Cassandra logs
- [Playbooks](../playbooks/index.md) - Step-by-step resolution guides
