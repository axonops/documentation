# nodetool gossipinfo

Displays gossip state information for all known nodes.

## Synopsis

```bash
nodetool [connection_options] gossipinfo
```

## Description

The `gossipinfo` command shows the gossip protocol state for all nodes in the cluster, including heartbeat information, status, and application state.

## Examples

```bash
nodetool gossipinfo
```

**Output:**
```
/10.0.0.1
  generation:1704067200
  heartbeat:987654
  STATUS:16:NORMAL,-1234567890123456789
  LOAD:876543:1.56789E11
  SCHEMA:12:a1b2c3d4-e5f6-7890-abcd-ef1234567890
  DC:8:dc1
  RACK:10:rack1
  RELEASE_VERSION:4:4.1.3
  HOST_ID:2:a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

## Key Fields

| Field | Description |
|-------|-------------|
| generation | Epoch timestamp when node started |
| heartbeat | Monotonically increasing liveness counter |
| STATUS | Current node state |
| SCHEMA | Schema version UUID |
| DC/RACK | Datacenter and rack assignment |

## Related Commands

- [status](status.md) - Cluster status
- [describecluster](describecluster.md) - Schema versions

## Related Documentation

- [Architecture - Gossip Protocol](../../../architecture/gossip.md)
- [Troubleshooting - Gossip Failures](../../../troubleshooting/playbooks/gossip-failures.md)
