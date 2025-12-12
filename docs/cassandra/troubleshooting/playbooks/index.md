# Troubleshooting Playbooks

Step-by-step guides for diagnosing and resolving specific Cassandra issues.

Each playbook follows the **SDRR Framework**:

1. **Symptoms** - Observable indicators of the problem
2. **Diagnosis** - Commands and checks to identify root cause
3. **Resolution** - Step-by-step fix procedures
4. **Recovery** - Verification and prevention

---

## Performance Issues

| Playbook | Symptoms | Severity |
|----------|----------|----------|
| [High CPU Usage](high-cpu.md) | CPU consistently > 80%, slow responses | Medium |
| [High Memory Usage](high-memory.md) | OOM errors, frequent GC, heap exhaustion | High |
| [Slow Queries](slow-queries.md) | High latency, timeouts on specific queries | Medium |
| [GC Pause Issues](gc-pause.md) | Long GC pauses, application stalls | High |
| [Large Partition Issues](large-partition.md) | Slow reads, OOM during compaction | High |
| [Tombstone Accumulation](tombstone-accumulation.md) | TombstoneOverwhelmingException, slow reads | High |
| [Compaction Issues](compaction-issues.md) | Growing SSTable count, degrading reads | Medium |

---

## Cluster Issues

| Playbook | Symptoms | Severity |
|----------|----------|----------|
| [Schema Disagreement](schema-disagreement.md) | Schema versions differ across nodes | High |
| [Gossip Failures](gossip-failures.md) | Nodes not seeing each other | Critical |
| [Repair Failures](repair-failures.md) | Repairs failing or not completing | Medium |

---

## Node Operations

| Playbook | Symptoms | Severity |
|----------|----------|----------|
| [Replace Dead Node](replace-dead-node.md) | Node permanently failed | High |
| [Decommission Node](decommission-node.md) | Removing node from cluster | Medium |
| [Add Node](add-node.md) | Expanding cluster capacity | Low |
| [Recover from OOM](recover-from-oom.md) | Node killed by OOM | High |
| [Handle Full Disk](handle-full-disk.md) | Disk space exhausted | Critical |

---

## Quick Reference

### Emergency Response Priority

| Severity | Response Time | Examples |
|----------|---------------|----------|
| **Critical** | Immediate | Disk full, gossip failure, cluster partition |
| **High** | Within 1 hour | OOM, schema disagreement, node down |
| **Medium** | Within 4 hours | High CPU, compaction backlog, repair failures |
| **Low** | Scheduled | Capacity planning, node additions |

### First Response Commands

```bash
# Quick cluster health check
nodetool status
nodetool tpstats | head -20
nodetool compactionstats

# Check for immediate issues
df -h /var/lib/cassandra          # Disk space
free -h                            # Memory
tail -50 /var/log/cassandra/system.log | grep -i error
```

---

## Using These Playbooks

### Before Starting

1. **Read the entire playbook** before executing commands
2. **Understand the impact** of each step
3. **Have rollback plan** ready
4. **Notify stakeholders** for production changes

### During Execution

1. **Follow steps in order** - sequence matters
2. **Verify each step** before proceeding
3. **Document what was done** for post-incident review
4. **Monitor impact** on cluster and applications

### After Resolution

1. **Verify the fix** using the recovery section
2. **Document root cause** and timeline
3. **Implement prevention** measures
4. **Update runbooks** if needed

---

## Related Documentation

- [Common Errors](../common-errors/index.md) - Error reference guide
- [Diagnosis Guide](../diagnosis/index.md) - Systematic diagnosis
- [Log Analysis](../log-analysis/index.md) - Understanding logs
- [Monitoring](../../operations/monitoring/index.md) - Proactive monitoring
