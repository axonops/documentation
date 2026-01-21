---
title: "Cassandra MBeans Reference"
description: "Cassandra MBeans reference. All available management beans and operations."
meta:
  - name: keywords
    content: "Cassandra MBeans, JMX management, MBean operations"
search:
  boost: 3
---

# Cassandra MBeans Reference

This section provides detailed documentation for all major MBeans exposed by Apache Cassandra. Each MBean includes attributes, operations, and practical examples.

## MBean Overview

| MBean | Domain | Purpose |
|-------|--------|---------|
| [StorageServiceMBean](#storageservicembean) | `o.a.c.db` | Core cluster operations |
| [StorageProxyMBean](#storageproxymbean) | `o.a.c.db` | Request coordination |
| [CompactionManagerMBean](#compactionmanagermbean) | `o.a.c.db` | Compaction control |
| [ColumnFamilyStoreMBean](#columnfamilystorembean) | `o.a.c.db` | Table operations |
| [GossiperMBean](#gossipermbean) | `o.a.c.gms` | Gossip protocol |
| [StreamManagerMBean](#streammanagermbean) | `o.a.c.streaming` | Data streaming |
| [CacheServiceMBean](#cacheservicembean) | `o.a.c.db` | Cache management |
| [CommitLogMBean](#commitlogmbean) | `o.a.c.db` | Commit log |
| [HintedHandoffManagerMBean](#hintedhandoffmanagermbean) | `o.a.c.db` | Hint delivery |
| [MessagingServiceMBean](#messagingservicembean) | `o.a.c.net` | Inter-node messaging |
| [EndpointSnitchMBean](#endpointsnitchmbean) | `o.a.c.locator` | Topology |
| [FailureDetectorMBean](#failuredetectormbean) | `o.a.c.gms` | Node detection |

---

## StorageServiceMBean

**ObjectName**: `org.apache.cassandra.db:type=StorageService`

The primary MBean for cluster-level operations. Controls node lifecycle, topology changes, and cluster-wide operations.

### Key Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `LiveNodes` | List<String> | IP addresses of live nodes |
| `UnreachableNodes` | List<String> | IP addresses of unreachable nodes |
| `JoiningNodes` | List<String> | Nodes currently joining |
| `LeavingNodes` | List<String> | Nodes currently leaving |
| `MovingNodes` | List<String> | Nodes currently moving |
| `OperationMode` | String | STARTING, NORMAL, JOINING, LEAVING, etc. |
| `ClusterName` | String | Cluster name |
| `LocalHostId` | String | UUID of this node |
| `Tokens` | List<String> | Tokens owned by this node |
| `ReleaseVersion` | String | Cassandra version |
| `SchemaVersion` | UUID | Current schema version |
| `Keyspaces` | List<String> | All keyspace names |
| `NativeTransportRunning` | boolean | CQL port status |
| `GossipRunning` | boolean | Gossip status |
| `Initialized` | boolean | Node initialized |

### Operations

| Operation | Parameters | Description |
|-----------|------------|-------------|
| `forceKeyspaceFlush` | keyspace | Flush memtables to disk |
| `forceKeyspaceCompaction` | keyspace | Trigger major compaction |
| `takeSnapshot` | tag, keyspaces | Create snapshot |
| `clearSnapshot` | tag, keyspaces | Remove snapshot |
| `repair` | keyspace, options | Start repair |
| `decommission` | - | Remove node from cluster |
| `move` | newToken | Move node to new token |
| `removeNode` | hostId | Force remove dead node |
| `assassinate` | address | Remove via gossip |
| `drain` | - | Flush and stop accepting writes |
| `truncate` | keyspace, table | Truncate table |
| `refreshSizeEstimates` | - | Update size estimates |

### nodetool Mappings

| nodetool Command | JMX Operation |
|------------------|---------------|
| `nodetool status` | `getLiveNodes()`, `getUnreachableNodes()` |
| `nodetool flush` | `forceKeyspaceFlush()` |
| `nodetool compact` | `forceKeyspaceCompaction()` |
| `nodetool snapshot` | `takeSnapshot()` |
| `nodetool repair` | `repair()` |
| `nodetool decommission` | `decommission()` |
| `nodetool drain` | `drain()` |
| `nodetool info` | Various attributes |

### Example: Get Node Status

```java
ObjectName ssBean = new ObjectName("org.apache.cassandra.db:type=StorageService");

// Get live nodes
List<String> liveNodes = (List<String>) mbsc.getAttribute(ssBean, "LiveNodes");
System.out.println("Live nodes: " + liveNodes);

// Get operation mode
String mode = (String) mbsc.getAttribute(ssBean, "OperationMode");
System.out.println("Mode: " + mode);

// Get cluster name
String cluster = (String) mbsc.getAttribute(ssBean, "ClusterName");
System.out.println("Cluster: " + cluster);
```

---

## StorageProxyMBean

**ObjectName**: `org.apache.cassandra.db:type=StorageProxy`

Controls request coordination settings including timeouts and consistency behavior.

### Key Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `TotalHints` | long | Total hints stored |
| `HintsInProgress` | int | Hints currently being delivered |
| `ReadRepairAttempted` | long | Read repair attempts |
| `ReadRepairRepairedBlocking` | long | Blocking read repairs |
| `ReadRepairRepairedBackground` | long | Background read repairs |
| `SchemaVersions` | Map | Schema versions per node |

### Configuration Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `RpcTimeout` | long | 10000ms | General RPC timeout |
| `ReadRpcTimeout` | long | 5000ms | Read timeout |
| `WriteRpcTimeout` | long | 2000ms | Write timeout |
| `RangeRpcTimeout` | long | 10000ms | Range query timeout |
| `CounterWriteRpcTimeout` | long | 5000ms | Counter write timeout |
| `TruncateRpcTimeout` | long | 60000ms | Truncate timeout |

### Operations

| Operation | Description |
|-----------|-------------|
| `setRpcTimeout` | Set general timeout |
| `setReadRpcTimeout` | Set read timeout |
| `setWriteRpcTimeout` | Set write timeout |
| `reloadTriggerClasses` | Reload trigger classes |

---

## CompactionManagerMBean

**ObjectName**: `org.apache.cassandra.db:type=CompactionManager`

Controls compaction operations and provides compaction statistics.

### Key Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `PendingTasks` | int | Pending compaction tasks |
| `CompletedTasks` | long | Completed compactions |
| `Compactions` | List<Map> | Currently running compactions |
| `PendingTasksByTableName` | Map | Pending tasks per table |

### Operations

| Operation | Parameters | Description |
|-----------|------------|-------------|
| `forceUserDefinedCompaction` | ks, table, files | Compact specific SSTables |
| `stopCompaction` | type | Stop compaction by type |
| `stopCompactionById` | compactionId | Stop specific compaction |
| `setConcurrentCompactors` | value | Set parallel compactors |
| `getConcurrentCompactors` | - | Get parallel compactor count |
| `setCompactionThroughput` | mbPerSec | Set throughput limit |
| `getCompactionThroughput` | - | Get throughput limit |

### nodetool Mappings

| nodetool Command | JMX Operation |
|------------------|---------------|
| `nodetool compactionstats` | `getCompactions()`, `getPendingTasks()` |
| `nodetool setcompactionthroughput` | `setCompactionThroughput()` |
| `nodetool stop COMPACTION` | `stopCompaction()` |

### Example: Monitor Compactions

```java
ObjectName cmBean = new ObjectName("org.apache.cassandra.db:type=CompactionManager");

// Get pending compactions
int pending = (int) mbsc.getAttribute(cmBean, "PendingTasks");
System.out.println("Pending compactions: " + pending);

// Get active compactions
List<Map<String, String>> compactions =
    (List<Map<String, String>>) mbsc.getAttribute(cmBean, "Compactions");
for (Map<String, String> c : compactions) {
    System.out.println("Compacting: " + c.get("keyspace") + "." + c.get("columnfamily"));
    System.out.println("  Progress: " + c.get("progress") + "%");
}
```

---

## ColumnFamilyStoreMBean

**ObjectName**: `org.apache.cassandra.db:type=ColumnFamilies,keyspace={ks},columnfamily={table}`

Per-table operations and statistics.

### Key Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `LiveSSTableCount` | int | Number of live SSTables |
| `LiveDiskSpaceUsed` | long | Disk space used (bytes) |
| `TotalDiskSpaceUsed` | long | Total disk space |
| `MemtableColumnsCount` | long | Columns in memtable |
| `MemtableSwitchCount` | int | Memtable flush count |
| `MemtableLiveDataSize` | long | Memtable data size |
| `BloomFilterFalsePositives` | long | Bloom filter false positives |
| `BloomFilterFalseRatio` | double | False positive ratio |
| `MeanPartitionSize` | long | Average partition size |
| `MaxPartitionSize` | long | Maximum partition size |
| `CompressionRatio` | double | Compression ratio |
| `SSTablesPerReadHistogram` | long[] | SSTables accessed per read |

### Operations

| Operation | Description |
|-----------|-------------|
| `forceFlush` | Flush memtable |
| `forceCompactionForTokenRange` | Compact token range |
| `estimateKeys` | Estimate key count |
| `loadNewSSTables` | Load new SSTables from disk |
| `setCompactionStrategyClass` | Change compaction strategy |
| `setCompactionThresholds` | Set min/max thresholds |

---

## GossiperMBean

**ObjectName**: `org.apache.cassandra.gms:type=Gossiper`

Gossip protocol management.

### Key Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `EndpointStates` | Map | State of all known endpoints |
| `DownEndpoints` | Set<String> | Down endpoints |

### Operations

| Operation | Description |
|-----------|-------------|
| `assassinateEndpoint` | Remove endpoint via gossip |
| `unsafeAssassinateEndpoint` | Force assassinate |
| `getCurrentGenerationNumber` | Get gossip generation |
| `getEndpointDowntime` | Get endpoint downtime |

---

## MessagingServiceMBean

**ObjectName**: `org.apache.cassandra.net:type=MessagingService`

Inter-node messaging statistics.

### Key Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `DroppedMessages` | Map | Dropped messages by type |
| `RecentlyDroppedMessages` | Map | Recently dropped messages |
| `TimeoutsPerHost` | Map | Timeouts per remote host |

### Message Types

| Type | Description |
|------|-------------|
| `MUTATION` | Write requests |
| `READ` | Read requests |
| `READ_REPAIR` | Read repair requests |
| `REQUEST_RESPONSE` | Responses |
| `RANGE_SLICE` | Range query requests |
| `PAGED_RANGE` | Paged range requests |
| `COUNTER_MUTATION` | Counter writes |
| `HINT` | Hint delivery |

### Example: Check Dropped Messages

```java
ObjectName msBean = new ObjectName("org.apache.cassandra.net:type=MessagingService");

Map<String, Integer> dropped =
    (Map<String, Integer>) mbsc.getAttribute(msBean, "DroppedMessages");

for (Map.Entry<String, Integer> entry : dropped.entrySet()) {
    if (entry.getValue() > 0) {
        System.out.println("WARNING: " + entry.getValue() +
            " dropped " + entry.getKey() + " messages");
    }
}
```

---

## CacheServiceMBean

**ObjectName**: `org.apache.cassandra.db:type=Caches`

Cache management and statistics.

### Key Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `KeyCacheCapacityInBytes` | long | Key cache size |
| `KeyCacheSize` | long | Keys in cache |
| `KeyCacheHits` | long | Cache hits |
| `KeyCacheMisses` | long | Cache misses |
| `KeyCacheRecentHitRate` | double | Recent hit rate |
| `RowCacheCapacityInBytes` | long | Row cache size |
| `RowCacheSize` | long | Rows in cache |
| `RowCacheHits` | long | Cache hits |
| `RowCacheMisses` | long | Cache misses |
| `RowCacheRecentHitRate` | double | Recent hit rate |

### Operations

| Operation | Description |
|-----------|-------------|
| `invalidateKeyCache` | Clear key cache |
| `invalidateRowCache` | Clear row cache |
| `setKeyCacheCapacity` | Set key cache size |
| `setRowCacheCapacity` | Set row cache size |
| `saveCaches` | Persist caches to disk |

---

## Additional MBeans

### CommitLogMBean

**ObjectName**: `org.apache.cassandra.db:type=Commitlog`

| Attribute | Description |
|-----------|-------------|
| `CompletedTasks` | Completed commit log tasks |
| `PendingTasks` | Pending tasks |
| `TotalCommitLogSize` | Total commit log size |
| `ActiveSegmentCount` | Active segments |

### HintedHandoffManagerMBean

**ObjectName**: `org.apache.cassandra.db:type=HintedHandoffManager`

| Attribute | Description |
|-----------|-------------|
| `StoredHints` | Total stored hints |
| `EndpointsWithPendingHints` | Endpoints waiting for hints |

### StreamManagerMBean

**ObjectName**: `org.apache.cassandra.streaming:type=StreamManager`

| Attribute | Description |
|-----------|-------------|
| `CurrentStreams` | Active streams |

### EndpointSnitchMBean

**ObjectName**: `org.apache.cassandra.locator:type=EndpointSnitchInfo`

| Attribute | Description |
|-----------|-------------|
| `SnitchName` | Active snitch class |
| `Datacenter` | Local datacenter |
| `Rack` | Local rack |

### FailureDetectorMBean

**ObjectName**: `org.apache.cassandra.gms:type=FailureDetector`

Monitors node availability using the Phi Accrual failure detector algorithm.

| Attribute | Description |
|-----------|-------------|
| `AllEndpointStates` | State information for all known endpoints |
| `SimpleStates` | Simplified UP/DOWN status for endpoints |
| `PhiValues` | Current phi values for each endpoint |

| Operation | Description |
|-----------|-------------|
| `getEndpointState(String)` | Get gossip state for specific endpoint |
| `forceConviction(String)` | Force mark endpoint as down |

---

## Quick Navigation

- [StorageServiceMBean](#storageservicembean)
- [StorageProxyMBean](#storageproxymbean)
- [CompactionManagerMBean](#compactionmanagermbean)
- [ColumnFamilyStoreMBean](#columnfamilystorembean)
- [GossiperMBean](#gossipermbean)
- [MessagingServiceMBean](#messagingservicembean)
- [CacheServiceMBean](#cacheservicembean)
- [StreamManagerMBean](#streammanagermbean)
- [CommitLogMBean](#commitlogmbean)
- [HintedHandoffManagerMBean](#hintedhandoffmanagermbean)
- [EndpointSnitchMBean](#endpointsnitchmbean)
- [FailureDetectorMBean](#failuredetectormbean)

---

## Next Steps

- **[Metrics Reference](../metrics/index.md)** - Detailed metrics documentation
- **[Connecting to JMX](../connecting/index.md)** - Setup and security
- **[Monitoring Guide](../../monitoring/index.md)** - Using JMX for monitoring
