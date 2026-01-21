---
title: "nodetool bootstrap"
description: "Check or resume bootstrap operations in Cassandra using nodetool bootstrap command."
meta:
  - name: keywords
    content: "nodetool bootstrap, Cassandra bootstrap, node joining, resume bootstrap"
search:
  boost: 3
---

# nodetool bootstrap

Manages the bootstrap process for a node joining the cluster.

---

## Synopsis

```bash
nodetool [connection_options] bootstrap resume
```

## Description

`nodetool bootstrap` manages the bootstrap process when a new node joins a Cassandra cluster. Bootstrap is the process by which a new node receives data from existing nodes to take ownership of its assigned token ranges.

The `resume` subcommand allows resuming a previously interrupted bootstrap operation.

!!! info "Bootstrap Context"
    Bootstrap typically happens automatically when a new node starts. This command is primarily used to resume interrupted bootstrap operations.

---

## Subcommands

| Subcommand | Description |
|------------|-------------|
| `resume` | Resume a previously interrupted bootstrap process |

---

## Examples

### Resume Interrupted Bootstrap

```bash
nodetool bootstrap resume
```

---

## When to Use

### After Bootstrap Failure

If bootstrap was interrupted due to network issues or node failure:

```bash
# Check current bootstrap status
nodetool netstats

# Resume bootstrap
nodetool bootstrap resume
```

### After Node Restart During Bootstrap

When a node restarts before completing bootstrap:

```bash
# Node has restarted, resume bootstrap
nodetool bootstrap resume

# Monitor progress
nodetool netstats
```

---

## Bootstrap Process

### Normal Bootstrap Flow

```
1. New node starts and contacts seed nodes
2. Node receives cluster topology via gossip
3. Token assignment determined
4. Streaming begins from existing nodes
5. Node receives data for its token ranges
6. Bootstrap completes, node becomes UN (Up/Normal)
```

### Interrupted Bootstrap

If bootstrap is interrupted:

- Node status shows as UJ (Up/Joining) or similar
- Data streaming incomplete
- `nodetool bootstrap resume` continues from where it stopped

---

## Monitoring Bootstrap

### Check Status

```bash
# View bootstrap/streaming status
nodetool netstats

# Check node state
nodetool status
```

### Monitor Progress

```bash
# Watch streaming progress
watch -n 5 'nodetool netstats | head -30'
```

---

## Troubleshooting

### Bootstrap Won't Resume

```bash
# Check node state
nodetool info | grep "Gossip"

# Check for errors
tail -100 /var/log/cassandra/system.log | grep -i bootstrap
```

### Bootstrap Taking Too Long

```bash
# Check streaming throughput
nodetool getstreamthroughput

# Increase if needed
nodetool setstreamthroughput 200
```

### Bootstrap Fails Repeatedly

```bash
# Check disk space
df -h /var/lib/cassandra

# Check network connectivity to seed nodes
nodetool status

# Review logs for specific errors
grep -i "bootstrap\|stream" /var/log/cassandra/system.log | tail -50
```

---

## Best Practices

!!! tip "Bootstrap Guidelines"

    1. **Monitor progress** - Watch `nodetool netstats` during bootstrap
    2. **Ensure resources** - Sufficient disk space and network bandwidth
    3. **One at a time** - Bootstrap one node at a time
    4. **Check completion** - Verify node reaches UN status

!!! warning "Bootstrap Considerations"

    - Bootstrap can take hours for large datasets
    - Network bandwidth is critical
    - Other cluster operations may be slower during bootstrap
    - Don't add multiple nodes simultaneously

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [netstats](netstats.md) | Monitor streaming progress |
| [status](status.md) | Check cluster state |
| [rebuild](rebuild.md) | Rebuild from another datacenter |
| [join](join.md) | Join the ring |
