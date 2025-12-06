# nodetool netstats

Displays network statistics including streaming operations and read repair metrics.

## Synopsis

```bash
nodetool [connection_options] netstats
```

## Description

The `netstats` command provides visibility into network-level operations, particularly streaming activities during repair, bootstrap, and decommission operations. It also displays read repair statistics showing how often data inconsistencies are detected and corrected.

## Output Sections

### Mode

Current operational mode of the node:
- `NORMAL` - Standard operation
- `JOINING` - Bootstrap in progress
- `LEAVING` - Decommission in progress
- `DECOMMISSIONING` - Decommission in progress
- `MOVING` - Token migration in progress
- `DRAINING` - Drain in progress
- `DRAINED` - Drain complete

### Streaming Operations

Shows active data streaming sessions for repair, rebuild, or topology changes.

### Read Repair Statistics

Shows read repair activity and consistency checks.

### Message Pools

Shows message queue statistics for inter-node communication.

## Examples

### Basic Network Statistics

```bash
nodetool netstats
```

**Output (idle):**
```
Mode: NORMAL
Not sending any streams.
Not receiving any streams.

Read Repair Statistics:
Attempted: 987654
Mismatch (Blocking): 12345
Mismatch (Background): 23456

Pool Name                    Active   Pending
Large messages                  n/a         0
Small messages                  n/a         0
Gossip messages                 n/a         0
```

**Output (during streaming):**
```
Mode: NORMAL
Receiving streams:
    /10.0.0.2
        /10.0.0.2 sessions: 2
        Receiving 45 files, 5.2 GiB total. Already received 23 files, 2.1 GiB total
            /var/lib/cassandra/data/my_keyspace/users-abc123: Receiving 12/25 files
            /var/lib/cassandra/data/my_keyspace/orders-def456: Receiving 11/20 files

Sending streams:
    /10.0.0.3
        /10.0.0.3 sessions: 1
        Sending 67 files, 8.3 GiB total. Already sent 45 files, 5.6 GiB total
            /var/lib/cassandra/data/my_keyspace/users-abc123: Sending 45/67 files

Read Repair Statistics:
Attempted: 987654
Mismatch (Blocking): 12345
Mismatch (Background): 23456

Pool Name                    Active   Pending
Large messages                  n/a         0
Small messages                  n/a         0
Gossip messages                 n/a         0
```

## Output Fields

### Streaming Statistics

| Field | Description |
|-------|-------------|
| sessions | Number of active streaming sessions |
| files total | Total files to transfer |
| GiB total | Total data size to transfer |
| Already received/sent | Progress in files and bytes |

### Read Repair Statistics

| Field | Description |
|-------|-------------|
| Attempted | Total read repair attempts |
| Mismatch (Blocking) | Inconsistencies fixed synchronously |
| Mismatch (Background) | Inconsistencies fixed asynchronously |

### Message Pools

| Pool | Description |
|------|-------------|
| Large messages | Inter-node messages > 65KB |
| Small messages | Inter-node messages ≤ 65KB |
| Gossip messages | Cluster membership messages |

## Interpreting Results

### Read Repair Ratio

Calculate the read repair ratio:
```
ratio = (Mismatch Blocking + Mismatch Background) / Attempted
```

| Ratio | Interpretation |
|-------|----------------|
| < 0.01 | Normal - minimal inconsistencies |
| 0.01 - 0.10 | Elevated - consider repair schedule |
| > 0.10 | High - immediate repair recommended |

### Streaming Health

| Condition | Status |
|-----------|--------|
| Progress increasing | Healthy streaming |
| No progress for extended period | Possible stall |
| Many parallel sessions | Resource intensive |

## Common Use Cases

### Monitor Repair Progress

```bash
# Watch streaming during repair
watch -n 5 'nodetool netstats | head -30'
```

### Monitor Decommission

```bash
# Track decommission progress
while nodetool netstats | grep -q "LEAVING\|DECOMMISSIONING"; do
    nodetool netstats | head -20
    sleep 30
done
echo "Decommission complete"
```

### Check for Streaming Issues

```bash
#!/bin/bash
# Alert if streaming appears stalled

LAST_PROGRESS=""
CHECK_COUNT=0

while true; do
    CURRENT=$(nodetool netstats | grep "Already" | head -1)

    if [ "$CURRENT" = "$LAST_PROGRESS" ] && [ -n "$CURRENT" ]; then
        ((CHECK_COUNT++))
        if [ $CHECK_COUNT -gt 6 ]; then  # No progress for 3 minutes
            echo "WARNING: Streaming appears stalled"
            nodetool netstats
        fi
    else
        CHECK_COUNT=0
    fi

    LAST_PROGRESS="$CURRENT"
    sleep 30
done
```

### Read Repair Analysis

```bash
#!/bin/bash
# Calculate read repair ratio

STATS=$(nodetool netstats | grep -A 3 "Read Repair")
ATTEMPTED=$(echo "$STATS" | grep Attempted | awk '{print $2}')
BLOCKING=$(echo "$STATS" | grep Blocking | awk '{print $3}')
BACKGROUND=$(echo "$STATS" | grep Background | awk '{print $3}')

if [ "$ATTEMPTED" -gt 0 ]; then
    RATIO=$(echo "scale=4; ($BLOCKING + $BACKGROUND) / $ATTEMPTED" | bc)
    echo "Read repair ratio: $RATIO"

    if (( $(echo "$RATIO > 0.10" | bc -l) )); then
        echo "WARNING: High read repair ratio - consider running repair"
    fi
fi
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Command executed successfully |
| 1 | Error occurred |

## Related Commands

- [nodetool repair](repair.md) - Run repair operations
- [nodetool status](status.md) - Check cluster state
- [nodetool decommission](decommission.md) - Remove node
- [nodetool setstreamthroughput](setstreamthroughput.md) - Adjust streaming speed

## Related Documentation

- [Operations - Repair](../../../operations/repair/index.md) - Repair operations
- [Architecture - Consistency](../../../architecture/consistency/index.md) - Read repair concepts
- [Troubleshooting - Streaming Failures](../../../troubleshooting/playbooks/streaming-failures.md) - Resolving issues

## Version Information

Available in all Apache Cassandra versions.
