# Decommission Node

Decommissioning removes a node from the cluster by streaming its data to remaining nodes. This is the proper way to permanently remove a healthy node.

---

## Prerequisites

- Node is UP and operational
- Cluster has sufficient capacity after removal
- No other operations (repair, bootstrap) running
- Recent backup available

!!! warning "When NOT to Use Decommission"
    - If node is DOWN: Use `nodetool removenode` instead
    - If node is unresponsive: Use `nodetool assassinate` (last resort)
    - If removing multiple nodes: Decommission one at a time

---

## Pre-Decommission Checklist

### Step 1: Verify Cluster Health

```bash
nodetool status
```

All other nodes should show `UN` (Up/Normal).

### Step 2: Check Capacity After Removal

```bash
# Current data per node
nodetool status | awk '/^UN/ {print $1, $3}'

# Verify remaining nodes can absorb data
# Rule: Each remaining node should have < 70% disk after decommission
```

### Step 3: Run Repair First (Optional but Recommended)

```bash
# Ensures data is consistent before streaming
nodetool repair -pr
```

### Step 4: Disable Auto-Bootstrap (Precaution)

Ensure `auto_bootstrap: false` won't be an issue if node accidentally restarts.

### Step 5: Notify Stakeholders

Decommission can take hours and impacts cluster performance during streaming.

---

## Decommission Procedure

### Step 1: Start Decommission

On the node to be removed:

```bash
nodetool decommission
```

This command:
1. Stops accepting new writes
2. Streams data to other replicas
3. Leaves the token ring
4. Shuts down (in some versions)

### Step 2: Monitor Progress

In another terminal:

```bash
# Watch streaming progress
nodetool netstats

# Watch decommission status
nodetool status | grep -E "UL|UJ|UN"
# UL = Leaving, UJ = Joining, UN = Normal
```

### Step 3: Wait for Completion

Decommission can take hours depending on data size. Do not interrupt.

```bash
# Monitor from another node
watch -n 60 'nodetool status'
```

### Step 4: Verify Completion

From another node:

```bash
nodetool status
```

The decommissioned node should no longer appear.

### Step 5: Clean Up (After Decommission)

On the decommissioned node (if still running):

```bash
# Stop Cassandra if still running
sudo systemctl stop cassandra

# Optionally remove data
sudo rm -rf /var/lib/cassandra/data/*
sudo rm -rf /var/lib/cassandra/commitlog/*
sudo rm -rf /var/lib/cassandra/saved_caches/*
```

---

## Troubleshooting

### Decommission Seems Stuck

```bash
# Check netstats for streaming activity
nodetool netstats

# Check logs
tail -100 /var/log/cassandra/system.log | grep -i "stream\|decommission"
```

If truly stuck (no progress for hours):
1. Check disk space on receiving nodes
2. Check network connectivity
3. Check for errors in logs

### Decommission Failed Mid-Way

```bash
# Check node status
nodetool status

# If node shows UL (Leaving) but decommission failed:
# Option 1: Restart and retry
sudo systemctl restart cassandra
nodetool decommission

# Option 2: Cancel and diagnose
nodetool netstats  # Check for issues
```

### Node Reappears After Decommission

The node's data directories may not have been cleared:

```bash
# On the decommissioned node, clear all data
sudo systemctl stop cassandra
sudo rm -rf /var/lib/cassandra/data/*
sudo rm -rf /var/lib/cassandra/commitlog/*
```

### Not Enough Space on Remaining Nodes

```bash
# Cancel decommission if possible (Ctrl+C usually works)
# Then:
# 1. Add more nodes first, OR
# 2. Clean up snapshots on remaining nodes
nodetool clearsnapshot --all
# 3. Add disk capacity
```

---

## Streaming Performance

### Monitor Streaming

```bash
# Detailed streaming info
nodetool netstats

# Streaming throughput
nodetool getstreamthroughput
```

### Speed Up Streaming (If Needed)

```bash
# Increase throughput (Mbps)
nodetool setstreamthroughput 400

# On receiving nodes, ensure capacity
nodetool setconcurrentcompactors 2
```

---

## Recovery If Interrupted

If decommission is interrupted:

### Node Still in Cluster (UL Status)

```bash
# Restart Cassandra
sudo systemctl restart cassandra

# Retry decommission
nodetool decommission
```

### Node Removed but Data Remains

```bash
# Clear data and repurpose hardware
sudo systemctl stop cassandra
sudo rm -rf /var/lib/cassandra/*

# Or re-add as new node (requires different IP or cleared system tables)
```

---

## Best Practices

| Practice | Reason |
|----------|--------|
| Decommission one node at a time | Prevents overload |
| Run repair before decommission | Ensures data consistency |
| Monitor during process | Catch issues early |
| Have backup ready | Recovery option |
| Plan maintenance window | Performance impact |
| Verify capacity first | Prevent disk full |

---

## Time Estimation

| Data per Node | Expected Duration |
|---------------|-------------------|
| < 100 GB | 1-2 hours |
| 100-500 GB | 2-8 hours |
| 500 GB - 1 TB | 8-24 hours |
| > 1 TB | 24+ hours |

Duration depends on:
- Network bandwidth
- Disk I/O speed
- Stream throughput settings
- Concurrent operations

---

## Related Procedures

| Scenario | Procedure |
|----------|-----------|
| Node is DOWN | [Replace Dead Node](replace-dead-node.md) |
| Adding capacity | [Add Node](add-node.md) |
| Node unresponsive | Use `nodetool removenode` or `assassinate` |

## Related Commands

| Command | Purpose |
|---------|---------|
| `nodetool decommission` | Remove healthy node |
| `nodetool removenode` | Remove dead node |
| `nodetool netstats` | Monitor streaming |
| `nodetool setstreamthroughput` | Adjust streaming speed |
| `nodetool status` | Verify cluster state |
