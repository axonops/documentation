---
title: "nodetool netstats"
description: "Display network statistics and streaming operations in Cassandra using nodetool netstats."
meta:
  - name: keywords
    content: "nodetool netstats, network statistics, streaming status, Cassandra"
---

# nodetool netstats

Displays network statistics including streaming operations, messaging activity, and connection states.

---

## Synopsis

```bash
nodetool [connection_options] netstats [-H]
```

## Description

`nodetool netstats` shows current network activity including:

- Active streaming sessions (repair, bootstrap, rebuild)
- Pending and completed streams
- Message queues to other nodes
- Read repair statistics

This is essential for monitoring data movement during topology changes, repairs, and other streaming operations.

---

## Options

| Option | Description |
|--------|-------------|
| `-H, --human-readable` | Display bytes in human-readable format |

---

## Output Example

```
Mode: NORMAL
Not sending any streams.
Read Repair Statistics:
Attempted: 1234
Mismatch (Blocking): 56
Mismatch (Background): 78

Pool Name                    Active   Pending      Completed   Dropped
Large messages                  n/a         0           1234         0
Small messages                  n/a        12         567890         0
Gossip messages                 n/a         0          12345         0
```

### With Active Streaming

```
Mode: NORMAL
Receiving from: /192.168.1.102
        /var/lib/cassandra/data/my_keyspace/users-a1b2c3d4
            Receiving 12 files, 1.2GB total. Already received 8 files, 800MB total
            Progress: 66%

Sending to: /192.168.1.103
        /var/lib/cassandra/data/my_keyspace/orders-b2c3d4e5
            Sending 5 files, 500MB total. Already sent 3 files, 300MB total
            Progress: 60%

Read Repair Statistics:
Attempted: 1234
Mismatch (Blocking): 56
Mismatch (Background): 78
```

---

## Output Fields

### Mode

Current node operation mode:

| Mode | Description |
|------|-------------|
| NORMAL | Standard operation |
| STARTING | Node is starting up |
| JOINING | Node is bootstrapping |
| LEAVING | Node is decommissioning |
| MOVING | Node is moving to new token |
| DRAINING | Node is draining |
| DRAINED | Node has drained |

### Streaming Information

| Field | Description |
|-------|-------------|
| Receiving from | Nodes sending data to this node |
| Sending to | Nodes receiving data from this node |
| Files | Number of SSTable files being transferred |
| Progress | Percentage complete |

### Message Pools

| Pool | Description |
|------|-------------|
| Large messages | Large inter-node messages (streaming, repair) |
| Small messages | Regular inter-node messages (reads, writes) |
| Gossip messages | Gossip protocol messages |

### Pool Statistics

| Field | Description |
|-------|-------------|
| Active | Currently processing |
| Pending | Waiting to be processed |
| Completed | Successfully processed |
| Dropped | Timed out and dropped |

### Read Repair Statistics

| Field | Description |
|-------|-------------|
| Attempted | Total read repairs started |
| Mismatch (Blocking) | Inconsistencies found during blocking reads |
| Mismatch (Background) | Inconsistencies found during background repair |

---

## When to Use

### Monitor Streaming Operations

During bootstrap, decommission, repair, or rebuild:

```bash
# Continuous monitoring
watch -n 2 'nodetool netstats'
```

### Check for Stuck Streaming

If an operation seems stuck:

```bash
nodetool netstats
```

Progress percentage that doesn't change indicates a problem.

### Troubleshoot Slow Operations

```bash
nodetool netstats -H
```

Shows how much data remains to transfer.

### Investigate Dropped Messages

```bash
nodetool netstats | grep Dropped
```

Non-zero dropped messages indicate network or processing issues.

---

## Examples

### Basic Usage

```bash
nodetool netstats
```

### Human-Readable Sizes

```bash
nodetool netstats -H
```

### Monitor Streaming Continuously

```bash
watch -n 5 'nodetool netstats -H'
```

### Check on All Nodes

```bash
for node in node1 node2 node3; do
    echo "=== $node ==="
    nodetool -h $node netstats
done
```

### Extract Stream Progress

```bash
nodetool netstats | grep -E "Progress|Receiving|Sending"
```

---

## Interpreting Results

### No Active Streams (Normal)

```
Mode: NORMAL
Not sending any streams.
```

Normal state when no data movement operations are running.

### Bootstrap in Progress

```
Mode: JOINING
Receiving from: /192.168.1.101
    Progress: 45%
Receiving from: /192.168.1.102
    Progress: 52%
Receiving from: /192.168.1.103
    Progress: 38%
```

New node receiving data from existing nodes.

### Repair Streaming

```
Mode: NORMAL
Sending to: /192.168.1.102
    streaming_repair_task
    Progress: 80%
```

Repair operation sending data to out-of-sync node.

### Decommission Progress

```
Mode: LEAVING
Sending to: /192.168.1.101
    Progress: 25%
Sending to: /192.168.1.103
    Progress: 30%
```

Node sending its data to remaining nodes.

---

## Troubleshooting with netstats

### Streaming Appears Stuck

If progress doesn't increase:

1. Check network connectivity between nodes
2. Check disk space on receiving node
3. Check for errors in system.log
4. Verify streaming isn't throttled

```bash
# Check streaming throughput settings
nodetool getstreamthroughput
nodetool getinterdcstreamthroughput
```

### High Dropped Messages

```
Pool Name                    Active   Pending      Completed   Dropped
Small messages                  n/a        50         567890       125
```

!!! danger "Dropped Messages"
    Dropped messages indicate:

    - Network timeouts
    - Overloaded nodes
    - Processing delays

    Investigate immediately - affects data consistency.

### High Pending Messages

```
Pool Name                    Active   Pending      Completed   Dropped
Small messages                  n/a       500         567890         0
```

!!! warning "Message Backlog"
    High pending indicates:

    - Node is overloaded
    - Network backpressure
    - May lead to dropped messages

### Large Read Repair Mismatch

```
Read Repair Statistics:
Attempted: 10000
Mismatch (Blocking): 5000
```

50% mismatch rate indicates:

- Recent node outage
- Repair hasn't run recently
- Write issues during failures

---

## Streaming Throughput

Control streaming speed to reduce impact:

```bash
# Get current setting
nodetool getstreamthroughput

# Set throughput (MB/s)
nodetool setstreamthroughput 200

# Inter-DC streaming
nodetool getinterdcstreamthroughput
nodetool setinterdcstreamthroughput 50
```

!!! tip "Throttling Trade-offs"
    - Higher throughput = faster operations, more impact on production
    - Lower throughput = slower operations, less impact
    - Default is often conservative; increase for faster streaming

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [status](status.md) | Check node states |
| [tpstats](tpstats.md) | Thread pool statistics |
| [compactionstats](compactionstats.md) | Compaction progress |
| [repair](repair.md) | Triggers streaming |
| [decommission](decommission.md) | Triggers streaming |
| [rebuild](rebuild.md) | Triggers streaming |
| [setstreamthroughput](setstreamthroughput.md) | Control streaming rate |
