---
description: "Schema disagreement troubleshooting playbook. Resolve schema conflicts."
meta:
  - name: keywords
    content: "schema disagreement, schema conflict, metadata issues"
---

# Schema Disagreement

Schema disagreement occurs when nodes in a cluster have different versions of the schema. This can cause query failures, inconsistent behavior, and operational issues.

---

## Symptoms

- `nodetool describecluster` shows multiple schema versions
- DDL operations fail or hang
- Queries return inconsistent results
- Errors mentioning "schema disagreement" in logs
- New nodes fail to join cluster

---

## Diagnosis

### Step 1: Check Schema Versions

```bash
nodetool describecluster
```

**Expected output (healthy):**
```
Schema versions:
    <schema-uuid>: [node1, node2, node3]
```

**Problem output:**
```
Schema versions:
    <schema-uuid-1>: [node1, node2]
    <schema-uuid-2>: [node3]
    UNREACHABLE: [node4]
```

### Step 2: Identify Affected Nodes

```bash
# Check gossip info for schema version per node
nodetool gossipinfo | grep -E "SCHEMA|STATUS"
```

### Step 3: Check for Pending Schema Changes

```bash
# Look for schema-related messages
grep -i "schema" /var/log/cassandra/system.log | tail -50
```

### Step 4: Check Node Connectivity

```bash
# Verify all nodes can communicate
for node in node1 node2 node3; do
    nc -zv $node 7000 && echo "$node: OK" || echo "$node: FAILED"
done
```

---

## Resolution

### Option 1: Wait for Convergence (Minor Disagreement)

Schema changes propagate via gossip. For recent changes, wait 30-60 seconds:

```bash
# Monitor schema convergence
watch -n 5 'nodetool describecluster | grep -A 20 "Schema versions"'
```

### Option 2: Force Schema Refresh

On each node with outdated schema:

```bash
# Reload schema from peers
nodetool reloadlocalschema
```

### Option 3: Reset Local Schema (Single Node)

If one node has corrupted schema:

```bash
# Warning: This drops local schema and reloads from peers
nodetool resetlocalschema
```

!!! warning "Use with Caution"
    `resetlocalschema` should only be used on a single node that has diverged from the cluster. Never run on multiple nodes simultaneously.

### Option 4: Rolling Restart

If schema disagreement persists:

```bash
# On each node, one at a time:
nodetool drain
sudo systemctl restart cassandra

# Wait for node to rejoin before proceeding to next
nodetool status
```

### Option 5: Force Schema Rebuild (Last Resort)

If all else fails, on the problematic node:

```bash
# 1. Stop Cassandra
sudo systemctl stop cassandra

# 2. Clear local schema tables
cqlsh -e "TRUNCATE system_schema.tables;"
cqlsh -e "TRUNCATE system_schema.columns;"
# ... (other system_schema tables)

# 3. Restart and let it rebuild from peers
sudo systemctl start cassandra
```

---

## Recovery

### Verify Resolution

```bash
# All nodes should show same schema version
nodetool describecluster

# Test DDL operations
cqlsh -e "CREATE KEYSPACE IF NOT EXISTS test_schema WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};"
cqlsh -e "DROP KEYSPACE test_schema;"
```

### Prevention

1. **Avoid concurrent DDL** - Only run schema changes from one client
2. **Wait between DDL operations** - Allow 10+ seconds between changes
3. **Monitor schema versions** - Alert on disagreement
4. **Keep cluster healthy** - Address node issues promptly

---

## Common Causes

| Cause | Prevention |
|-------|------------|
| Concurrent DDL from multiple clients | Use single schema management tool |
| Network partition during DDL | Ensure network stability |
| Node crash during schema change | Monitor node health |
| Gossip issues | Check firewall rules for port 7000 |
| Clock skew | Synchronize clocks with NTP |

---

## Related Commands

| Command | Purpose |
|---------|---------|
| `nodetool describecluster` | View schema versions |
| `nodetool gossipinfo` | Check gossip state |
| `nodetool reloadlocalschema` | Refresh schema from peers |
| `nodetool resetlocalschema` | Reset and reload schema |

## Related Documentation

- [Gossip Failures](gossip-failures.md) - Gossip troubleshooting
- [Cluster Management](../../operations/cluster-management/index.md) - Cluster operations
