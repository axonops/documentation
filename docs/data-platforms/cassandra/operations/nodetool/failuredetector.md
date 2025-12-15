---
title: "nodetool failuredetector"
description: "Display failure detector information for Cassandra cluster nodes using nodetool failuredetector."
meta:
  - name: keywords
    content: "nodetool failuredetector, failure detection, Cassandra cluster, node status"
---

# nodetool failuredetector

Displays the failure detector information for the cluster.

---

## Synopsis

```bash
nodetool [connection_options] failuredetector
```

## Description

`nodetool failuredetector` displays information about Cassandra's failure detector, which monitors the health of nodes in the cluster using the Phi Accrual Failure Detector algorithm. This information helps understand how the cluster perceives node health and connectivity.

The failure detector uses gossip heartbeats to calculate a "phi" value representing the likelihood that a node has failed. When phi exceeds the configured threshold, the node is marked as down.

---

## Examples

### Basic Usage

```bash
nodetool failuredetector
```

---

## Output

### Sample Output

```
Endpoint            Phi
192.168.1.101       0.0034521
192.168.1.102       0.0028934
192.168.1.103       0.0041256
192.168.1.104       5.2341567
```

### Interpreting Phi Values

| Phi Value | Interpretation |
|-----------|----------------|
| 0 - 0.5 | Very healthy, recent heartbeat |
| 0.5 - 5 | Healthy, normal range |
| 5 - 8 | Elevated, possible issues |
| > 8 | Likely down (default threshold) |

---

## Failure Detection Algorithm

### Phi Accrual Failure Detector

```
How Phi is Calculated:

1. Each node sends periodic heartbeats via gossip
2. Receiving nodes track heartbeat arrival times
3. Statistical analysis calculates expected arrival time
4. Phi = -log10(P(heartbeat will still arrive))
5. Higher phi = higher probability of failure
```

### Default Threshold

```yaml
# cassandra.yaml
phi_convict_threshold: 8
```

A node is marked DOWN when phi exceeds this threshold.

---

## Use Cases

### Diagnose Cluster Health

```bash
# Check all nodes' phi values
nodetool failuredetector

# Identify nodes with elevated phi
nodetool failuredetector | awk '$2 > 1 {print}'
```

### Network Issue Investigation

When experiencing intermittent connectivity:

```bash
# Monitor phi values over time
watch -n 5 'nodetool failuredetector'
```

### Pre-Maintenance Check

Before cluster operations:

```bash
# Ensure all nodes are healthy
nodetool failuredetector

# All phi values should be low
```

---

## Monitoring Script

```bash
#!/bin/bash
# monitor_failure_detector.sh

THRESHOLD=5.0

echo "=== Failure Detector Check ==="
echo ""

# Get failure detector info
nodetool failuredetector | tail -n +2 | while read endpoint phi; do
    # Compare phi to threshold
    elevated=$(echo "$phi > $THRESHOLD" | bc -l)

    if [ "$elevated" -eq 1 ]; then
        echo "WARNING: $endpoint has elevated phi: $phi"
    else
        echo "OK: $endpoint phi=$phi"
    fi
done
```

---

## Cluster-Wide Check

```bash
#!/bin/bash
# cluster_failure_detector.sh

echo "=== Cluster Failure Detector Status ==="# Get list of node IPs from local nodetool status


nodes=$(nodetool status | grep "^UN\|^DN" | awk '{print $2}')

for node in $nodes; do
    echo ""
    echo "=== From perspective of $node ==="
    ssh "$node" "nodetool failuredetector 2>/dev/null || echo "Cannot connect to $node""
done
```

---

## Troubleshooting

### High Phi Values

If a node shows consistently high phi:

```bash
# Check network connectivity
ping <node_ip>

# Check if node is under load
ssh <node_ip> "nodetool tpstats"

# Check for GC issues
ssh <node_ip> "nodetool gcstats"
```

### Fluctuating Phi Values

Indicates network instability:

```bash
# Check for network issues
traceroute <node_ip>

# Monitor over time
for i in {1..60}; do
    echo "$(date): $(nodetool failuredetector | grep <node_ip>)"
    sleep 10
done
```

### Node Incorrectly Marked Down

If a healthy node is marked down:

```bash
# Check phi threshold
grep phi_convict_threshold /etc/cassandra/cassandra.yaml

# Consider adjusting if network is high-latency
# Higher threshold = more tolerant of delays
```

---

## Configuration

### Phi Threshold

```yaml
# cassandra.yaml
phi_convict_threshold: 8  # Default

# For high-latency networks, consider increasing:
# phi_convict_threshold: 12
```

### Affecting Factors

| Factor | Effect on Phi |
|--------|---------------|
| Network latency | Higher latency → higher phi |
| GC pauses | Long GC → spikes in phi |
| CPU load | High load → delayed heartbeats |
| Network packet loss | Missing heartbeats → elevated phi |

---

## Best Practices

!!! tip "Failure Detector Guidelines"

    1. **Regular monitoring** - Include in health checks
    2. **Baseline values** - Know normal phi ranges for your cluster
    3. **Alert on elevated phi** - Before nodes are marked down
    4. **Investigate spikes** - Don't ignore temporary elevations
    5. **Tune threshold** - Adjust for network characteristics

!!! info "Healthy Cluster Indicators"

    - All phi values < 1.0
    - Values stable over time
    - No sudden spikes
    - Symmetric across nodes (A sees B same as B sees A)

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [gossipinfo](gossipinfo.md) | Detailed gossip state |
| [status](status.md) | Cluster status overview |
| [info](info.md) | Node information |
| [netstats](netstats.md) | Network statistics |
