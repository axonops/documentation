# Data Streaming

Data streaming is the mechanism by which Cassandra nodes transfer SSTable data directly between each other. This inter-node data transfer occurs during cluster topology changes, repair operations, and failure recovery scenarios. Understanding the streaming subsystem is essential for capacity planning, operational troubleshooting, and performance optimization.

---

## Overview

### What is Streaming?

Streaming is Cassandra's bulk data transfer protocol for moving SSTable segments between nodes. Unlike the normal read/write path that operates on individual rows, streaming transfers entire SSTable files or portions thereof at the file level.

```graphviz dot streaming-overview.svg
digraph StreamingOverview {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];

    label="Streaming vs Normal Read/Write Path";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    subgraph cluster_normal {
        label="Normal Path\n(row-level)";
        style="rounded,filled";
        fillcolor="#E8F4E8";
        color="#99CC99";

        client [label="Client", fillcolor="#E8E8E8", fontcolor="black"];
        coord [label="Coordinator", fillcolor="#5B9BD5", fontcolor="white"];
        replica [label="Replica", fillcolor="#5B9BD5", fontcolor="white"];

        client -> coord [label="CQL query"];
        coord -> replica [label="row mutation"];
    }

    subgraph cluster_streaming {
        label="Streaming Path\n(SSTable-level)";
        style="rounded,filled";
        fillcolor="#FFE8E8";
        color="#CC9999";

        source [label="Source Node\nSSTable files", fillcolor="#C55A11", fontcolor="white"];
        target [label="Target Node\nSSTable files", fillcolor="#C55A11", fontcolor="white"];

        source -> target [label="SSTable segments\n(bulk transfer)", penwidth=2];
    }
}
```

### When Streaming Occurs

| Operation | Direction | Trigger |
|-----------|-----------|---------|
| Bootstrap | Existing → New node | New node joins cluster |
| Decommission | Leaving → Remaining nodes | Node removal initiated |
| Repair | Bidirectional between replicas | Manual or scheduled repair |
| Rebuild | Existing → Rebuilt node | `nodetool rebuild` command |
| Host replacement | Existing → Replacement node | Dead node replaced |
| Hinted handoff | Coordinator → Recovered node | Node recovers after failure |

---

## Streaming Architecture

### Protocol Stack

Cassandra's streaming protocol operates as a separate subsystem from the CQL protocol:

```graphviz dot protocol-stack.svg
digraph ProtocolStack {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Streaming Protocol Stack";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled", width=5];

    subgraph cluster_session {
        label="Streaming Session";
        style="rounded,filled";
        fillcolor="#E8E8E8";
        color="#999999";

        coord [label="Stream Coordinator\n• Identifies ranges\n• Selects SSTables\n• Manages transfers", fillcolor="#5B9BD5", fontcolor="white"];
        recv [label="Stream Receiver\n• Accepts connections\n• Receives file segments\n• Writes to local storage", fillcolor="#5B9BD5", fontcolor="white"];

        coord -> recv [style=invis];
        {rank=same; coord; recv}
    }

    messaging [label="Messaging Layer\nStreamInitMessage | FileMessage | StreamReceivedMessage | StreamCompleteMessage", fillcolor="#70AD47", fontcolor="white"];

    transport [label="Transport Layer\n• Dedicated streaming port (default: storage_port)\n• Optionally encrypted (TLS)\n• Compression (LZ4)", fillcolor="#C55A11", fontcolor="white"];

    coord -> messaging [style=invis];
    recv -> messaging [style=invis];
    messaging -> transport;
}
```

### Streaming Session Lifecycle

A streaming session progresses through distinct phases:

```graphviz dot streaming-lifecycle.svg
digraph StreamingLifecycle {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=LR;

    label="Streaming Session State Machine";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled", fillcolor="#5B9BD5", fontcolor="white"];

    init [label="INITIALIZED"];
    preparing [label="PREPARING"];
    streaming [label="STREAMING"];
    complete [label="COMPLETE", fillcolor="#70AD47"];
    failed [label="FAILED", fillcolor="#C00000"];

    init -> preparing [label="session start"];
    preparing -> streaming [label="plans exchanged"];
    streaming -> complete [label="all files transferred"];
    streaming -> failed [label="error/timeout"];
    preparing -> failed [label="error"];
}
```

**Phase descriptions:**

| Phase | Operations |
|-------|------------|
| **INITIALIZED** | Session created, peers identified |
| **PREPARING** | Token ranges calculated, SSTable selection, streaming plan exchanged |
| **STREAMING** | File transfers in progress, progress tracking |
| **COMPLETE** | All transfers successful, SSTables integrated |
| **FAILED** | Error occurred, partial cleanup, retry may follow |

### Zero-Copy Streaming (Cassandra 4.0+)

Cassandra 4.0 introduced zero-copy streaming, which transfers entire SSTable components without deserialization:

```graphviz dot zero-copy-comparison.svg
digraph ZeroCopyComparison {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=LR;

    label="Traditional vs Zero-Copy Streaming";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    subgraph cluster_traditional {
        label="Traditional Streaming (pre-4.0)";
        style="rounded,filled";
        fillcolor="#FFE8E8";
        color="#CC9999";

        src1 [label="SSTable\n(source)", fillcolor="#5B9BD5", fontcolor="white"];
        mem [label="Memory\n(heap)", fillcolor="#FFC000", fontcolor="black"];
        tgt1 [label="SSTable\n(target)", fillcolor="#5B9BD5", fontcolor="white"];

        src1 -> mem [label="deserialize"];
        mem -> tgt1 [label="serialize"];

        overhead [label="CPU + GC overhead", shape=plaintext, fontcolor="#C00000"];
    }

    subgraph cluster_zerocopy {
        label="Zero-Copy Streaming (4.0+)";
        style="rounded,filled";
        fillcolor="#E8F4E8";
        color="#99CC99";

        src2 [label="SSTable\n(source)", fillcolor="#70AD47", fontcolor="white"];
        tgt2 [label="SSTable\n(target)", fillcolor="#70AD47", fontcolor="white"];

        src2 -> tgt2 [label="direct file transfer\n(kernel buffer)", penwidth=2];

        minimal [label="Minimal CPU/heap usage", shape=plaintext, fontcolor="#507E32"];
    }
}
```

| Characteristic | Traditional | Zero-Copy |
|----------------|-------------|-----------|
| CPU usage | High (ser/deser) | Minimal |
| Heap pressure | Significant | Negligible |
| Throughput | Limited by CPU | Limited by network/disk |
| Compatibility | All SSTables | Same-version SSTables only |
| TLS support | Yes | No |

!!! warning "Zero-Copy Requirements and Limitations"
    Zero-copy streaming has specific requirements that, when not met, cause automatic fallback to traditional streaming:

    - **SSTable format compatibility**: Source and target nodes must use compatible SSTable formats. During rolling upgrades with format changes, traditional streaming is used.
    - **Inter-node encryption (TLS)**: Zero-copy streaming is **disabled** when inter-node encryption is enabled. TLS requires data to pass through the encryption layer, necessitating memory copies for encryption/decryption operations. Clusters with `server_encryption_options` enabled will always use traditional streaming.
    - **Configuration**: Zero-copy must be enabled via `stream_entire_sstables: true` (default in 4.0+).

    For security-conscious deployments requiring TLS, account for the additional CPU and memory overhead of traditional streaming during capacity planning for bootstrap, decommission, and repair operations.

---

## Bootstrap

Bootstrap is the process by which a new node joins the cluster and receives its share of data from existing nodes.

### Bootstrap Sequence

```graphviz dot bootstrap-sequence.svg
digraph BootstrapSequence {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Bootstrap Process";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    start [label="1. New Node Starts\nContacts seed nodes", fillcolor="#E8E8E8", fontcolor="black"];
    gossip [label="2. Gossip Integration\nLearns cluster topology", fillcolor="#5B9BD5", fontcolor="white"];
    token [label="3. Token Selection\nDetermines owned ranges", fillcolor="#5B9BD5", fontcolor="white"];
    plan [label="4. Stream Planning\nIdentifies source nodes", fillcolor="#5B9BD5", fontcolor="white"];
    stream [label="5. Data Streaming\nReceives SSTables", fillcolor="#FFC000", fontcolor="black"];
    finish [label="6. Bootstrap Complete\nAccepts client requests", fillcolor="#70AD47", fontcolor="white"];

    start -> gossip;
    gossip -> token;
    token -> plan;
    plan -> stream;
    stream -> finish;
}
```

### Token Range Calculation

During bootstrap, the new node must determine which token ranges it will own:

```graphviz dot token-range-bootstrap.svg
digraph TokenRangeBootstrap {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Token Range Calculation During Bootstrap";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    subgraph cluster_before {
        label="Before Bootstrap (4 nodes)";
        style="rounded,filled";
        fillcolor="#E8E8E8";
        color="#999999";

        before [label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
            <TR><TD BGCOLOR="#5B9BD5"><FONT COLOR="white">Token Range</FONT></TD><TD BGCOLOR="#5B9BD5"><FONT COLOR="white">Owner</FONT></TD></TR>
            <TR><TD>(0, 25]</TD><TD>Node A</TD></TR>
            <TR><TD>(25, 50]</TD><TD>Node B</TD></TR>
            <TR><TD>(50, 75]</TD><TD>Node C</TD></TR>
            <TR><TD>(75, 0]</TD><TD>Node D</TD></TR>
        </TABLE>>, shape=none];
    }

    subgraph cluster_after {
        label="After Bootstrap (5 nodes)";
        style="rounded,filled";
        fillcolor="#E8F4E8";
        color="#99CC99";

        after [label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
            <TR><TD BGCOLOR="#70AD47"><FONT COLOR="white">Token Range</FONT></TD><TD BGCOLOR="#70AD47"><FONT COLOR="white">Owner</FONT></TD></TR>
            <TR><TD>(0, 25]</TD><TD>Node A</TD></TR>
            <TR><TD>(25, 50]</TD><TD>Node B</TD></TR>
            <TR><TD>(50, 62]</TD><TD>Node C</TD></TR>
            <TR><TD BGCOLOR="#FFC000">(62, 75]</TD><TD BGCOLOR="#FFC000">Node E (new)</TD></TR>
            <TR><TD>(75, 0]</TD><TD>Node D</TD></TR>
        </TABLE>>, shape=none];
    }

    subgraph cluster_streaming {
        label="Node E Must Receive";
        style="rounded,filled";
        fillcolor="#FFE8E8";
        color="#CC9999";

        receive [label="• Primary range: (62, 75] from Node D\n• Replica ranges based on RF=3 topology", fillcolor="#C55A11", fontcolor="white"];
    }

    before -> after [label="Node E joins\n(token 62)"];
    after -> receive [style=dashed];
}
```

### Streaming Source Selection

The bootstrap coordinator selects source nodes based on:

1. **Token ownership**: Nodes currently owning required ranges
2. **Replica set**: For each range, any replica can serve as source
3. **Node state**: Only UP nodes considered
4. **Load balancing**: Distribute streaming load across sources

| Selection Criterion | Rationale |
|--------------------|-----------|
| Prefer local datacenter | Lower network latency |
| Prefer least-loaded nodes | Minimize impact on production |
| Avoid nodes already streaming | Prevent overload |
| Round-robin across replicas | Balance source load |

### Bootstrap Configuration

```yaml
# cassandra.yaml bootstrap parameters

# Number of concurrent streaming sessions per source
streaming_connections_per_host: 1

# Throughput limit (MB/s, 0 = unlimited)
stream_throughput_outbound_megabits_per_sec: 200

# Enable zero-copy streaming
stream_entire_sstables: true

# Bootstrap timeout
streaming_keep_alive_period_in_secs: 300
```

---

## Decommission

Decommission is the orderly removal of a node from the cluster, streaming all locally-owned data to remaining nodes before shutdown.

### Decommission Sequence

```graphviz dot decommission-sequence.svg
digraph DecommissionSequence {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Decommission Process";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    start [label="1. Decommission Initiated\nnodetool decommission", fillcolor="#E8E8E8", fontcolor="black"];
    announce [label="2. State Announcement\nGossip: LEAVING status", fillcolor="#5B9BD5", fontcolor="white"];
    plan [label="3. Stream Planning\nCalculate target nodes", fillcolor="#5B9BD5", fontcolor="white"];
    stream [label="4. Data Streaming\nTransfer all local data", fillcolor="#FFC000", fontcolor="black"];
    left [label="5. State: LEFT\nRemoved from ring", fillcolor="#C00000", fontcolor="white"];
    shutdown [label="6. Node Shutdown\nProcess terminates", fillcolor="#7F7F7F", fontcolor="white"];

    start -> announce;
    announce -> plan;
    plan -> stream;
    stream -> left;
    left -> shutdown;
}
```

### Range Redistribution

During decommission, the departing node's ranges must be redistributed:

```graphviz dot range-redistribution.svg
digraph RangeRedistribution {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Range Redistribution During Decommission";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    subgraph cluster_before {
        label="Before Decommission (RF=3, 5 nodes)";
        style="rounded,filled";
        fillcolor="#E8E8E8";
        color="#999999";

        range1 [label="Range (40, 60]", fillcolor="#FFC000", fontcolor="black"];
        c1 [label="Node C\n(primary)", fillcolor="#C00000", fontcolor="white"];
        d1 [label="Node D\n(replica)", fillcolor="#5B9BD5", fontcolor="white"];
        e1 [label="Node E\n(replica)", fillcolor="#5B9BD5", fontcolor="white"];

        range1 -> c1;
        range1 -> d1;
        range1 -> e1;
    }

    subgraph cluster_after {
        label="After Decommission (4 nodes)";
        style="rounded,filled";
        fillcolor="#E8F4E8";
        color="#99CC99";

        range2 [label="Range (40, 60]", fillcolor="#FFC000", fontcolor="black"];
        d2 [label="Node D\n(new primary)", fillcolor="#70AD47", fontcolor="white"];
        e2 [label="Node E\n(replica)", fillcolor="#5B9BD5", fontcolor="white"];
        a2 [label="Node A\n(new replica)", fillcolor="#70AD47", fontcolor="white"];

        range2 -> d2;
        range2 -> e2;
        range2 -> a2;
    }

    subgraph cluster_stream {
        label="Streaming Plan";
        style="rounded,filled";
        fillcolor="#FFE8E8";
        color="#CC9999";

        stream [label="Node C → Node A\nRange (40, 60] data\n\n(D and E already have replicas)", fillcolor="#C55A11", fontcolor="white"];
    }

    c1 -> stream [label="decommission", style=dashed];
    stream -> a2 [label="stream data", penwidth=2, color="#70AD47"];
}
```

### Decommission vs RemoveNode

| Operation | Use Case | Data Handling |
|-----------|----------|---------------|
| `decommission` | Node healthy, orderly removal | Streams data before leaving |
| `removenode` | Node dead/unrecoverable | No streaming; repair required after |
| `assassinate` | Force remove stuck node | Emergency only; data loss possible |

!!! warning "Decommission Requirements"
    Decommission can only proceed if the remaining cluster can satisfy the replication factor. Attempting to decommission when RF nodes would remain results in an error.

---

## Repair Streaming

Repair operations use streaming to synchronize data between replicas that have diverged.

### Repair Types and Streaming

| Repair Type | Streaming Behavior |
|-------------|-------------------|
| Full repair | Compare all data, stream differences |
| Incremental repair | Compare only unrepaired SSTables |
| Preview repair | Calculate differences only, no streaming |
| Subrange repair | Repair specific token ranges |

### Merkle Tree Exchange

Before streaming, repair uses Merkle trees to identify divergent ranges:

```graphviz dot merkle-tree-repair.svg
digraph MerkleTreeRepair {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Merkle Tree Comparison for Repair";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    subgraph cluster_node1 {
        label="Replica A";
        style="rounded,filled";
        fillcolor="#E8F4E8";
        color="#99CC99";

        build1 [label="1. Build Merkle Tree\nfrom local SSTables", fillcolor="#5B9BD5", fontcolor="white"];
        tree1 [label="Root: hash_A\n├─ L: hash_1\n└─ R: hash_2", fillcolor="#70AD47", fontcolor="white"];
    }

    subgraph cluster_node2 {
        label="Replica B";
        style="rounded,filled";
        fillcolor="#FFE8E8";
        color="#CC9999";

        build2 [label="1. Build Merkle Tree\nfrom local SSTables", fillcolor="#5B9BD5", fontcolor="white"];
        tree2 [label="Root: hash_B\n├─ L: hash_1\n└─ R: hash_3", fillcolor="#C55A11", fontcolor="white"];
    }

    compare [label="2. Compare Trees\nhash_A ≠ hash_B\nhash_2 ≠ hash_3", fillcolor="#FFC000", fontcolor="black"];

    stream [label="3. Stream Differing Range\nOnly R subtree data", fillcolor="#70AD47", fontcolor="white"];

    tree1 -> compare;
    tree2 -> compare;
    compare -> stream;
}
```

### Streaming During Repair

```graphviz dot repair-streaming-flow.svg
digraph RepairStreamingFlow {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Repair Streaming Flow";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    init [label="1. Coordinator initiates repair\nfor keyspace/table", fillcolor="#E8E8E8", fontcolor="black"];
    build [label="2. Each replica builds Merkle tree\nfor requested ranges", fillcolor="#5B9BD5", fontcolor="white"];
    exchange [label="3. Trees exchanged and\ncompared pairwise", fillcolor="#5B9BD5", fontcolor="white"];
    diff [label="4. Differing ranges identified\n(may be small subset)", fillcolor="#FFC000", fontcolor="black"];
    session [label="5. Streaming sessions created\nfor each difference", fillcolor="#5B9BD5", fontcolor="white"];
    stream [label="6. Data streamed from authoritative\nreplica to divergent replica", fillcolor="#C55A11", fontcolor="white"];
    complete [label="7. Received SSTables integrated\nrepair marked complete", fillcolor="#70AD47", fontcolor="white"];

    init -> build;
    build -> exchange;
    exchange -> diff;
    diff -> session;
    session -> stream;
    stream -> complete;
}
```

### Incremental Repair Optimization

Incremental repair tracks which SSTables have been repaired, reducing future repair scope:

| SSTable State | Description | Repair Behavior |
|---------------|-------------|-----------------|
| Unrepaired | Never included in repair | Included in next repair |
| Pending | Currently being repaired | Excluded from new repairs |
| Repaired | Successfully repaired | Excluded from incremental repair |

---

## Hinted Handoff

Hinted handoff is a lightweight streaming mechanism that delivers missed writes to nodes that were temporarily unavailable.

### Hint Storage and Delivery

```graphviz dot hinted-handoff.svg
digraph HintedHandoff {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Hinted Handoff Mechanism";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    subgraph cluster_write {
        label="1. Write Arrives (Node B down)";
        style="rounded,filled";
        fillcolor="#FFE8E8";
        color="#CC9999";

        write [label="Client Write\n(RF=3)", fillcolor="#E8E8E8", fontcolor="black"];
        a [label="Node A\n✓ Success", fillcolor="#70AD47", fontcolor="white"];
        b [label="Node B\n✗ Down", fillcolor="#C00000", fontcolor="white"];
        c [label="Node C\n✓ Success", fillcolor="#70AD47", fontcolor="white"];

        write -> a;
        write -> b [style=dashed];
        write -> c;
    }

    hint [label="2. Coordinator Stores Hint\nfor Node B", fillcolor="#FFC000", fontcolor="black"];

    subgraph cluster_replay {
        label="3. Node B Recovers";
        style="rounded,filled";
        fillcolor="#E8F4E8";
        color="#99CC99";

        recover [label="Node B\nBack Online", fillcolor="#5B9BD5", fontcolor="white"];
        deliver [label="Hints Delivered\nto Node B", fillcolor="#70AD47", fontcolor="white"];
    }

    b -> hint [style=dashed, label="failure detected"];
    hint -> deliver [label="gossip: B is UP"];
    deliver -> recover;
}
```

### Hint Structure

Hints are stored locally on the coordinator node:

```graphviz dot hint-record.svg
digraph HintRecord {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Hint Record Structure";
    labelloc="t";
    fontsize=12;

    hint [label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
        <TR><TD COLSPAN="2" BGCOLOR="#5B9BD5"><FONT COLOR="white"><B>Hint Record</B></FONT></TD></TR>
        <TR><TD ALIGN="LEFT">Target Host ID</TD><TD>uuid</TD></TR>
        <TR><TD ALIGN="LEFT">Hint ID</TD><TD>timeuuid</TD></TR>
        <TR><TD ALIGN="LEFT">Creation Time</TD><TD>timestamp</TD></TR>
        <TR><TD ALIGN="LEFT">Mutation</TD><TD>serialized write</TD></TR>
        <TR><TD ALIGN="LEFT">Message Version</TD><TD>protocol version</TD></TR>
    </TABLE>>, shape=none];

    storage [label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
        <TR><TD BGCOLOR="#70AD47"><FONT COLOR="white"><B>Storage</B></FONT></TD></TR>
        <TR><TD ALIGN="LEFT">Location: $CASSANDRA_HOME/data/hints/</TD></TR>
        <TR><TD ALIGN="LEFT">File Format: &lt;host_id&gt;-&lt;timestamp&gt;-&lt;version&gt;.hints</TD></TR>
    </TABLE>>, shape=none];

    hint -> storage [style=invis];
}
```

### Hint Configuration

```yaml
# cassandra.yaml hint parameters

# Enable/disable hinted handoff
hinted_handoff_enabled: true

# Maximum time to store hints (default: 3 hours)
max_hint_window_in_ms: 10800000

# Directory for hint files
hints_directory: /var/lib/cassandra/hints

# Hint delivery throttle (KB/s per destination)
hinted_handoff_throttle_in_kb: 1024

# Maximum hints delivery threads
max_hints_delivery_threads: 2

# Hint compression
hints_compression:
  - class_name: LZ4Compressor
```

### Hint Delivery Streaming

Unlike full SSTable streaming used in bootstrap and repair, hint delivery uses a lighter-weight mutation replay mechanism. Hints are streamed as individual mutations rather than file segments.

```graphviz dot hint-delivery-streaming.svg
digraph HintDeliveryStreaming {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=TB;

    label="Hint Delivery Streaming Flow";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    subgraph cluster_source {
        label="Hint Source (Coordinator)";
        style="rounded,filled";
        fillcolor="#E8E8E8";
        color="#999999";

        gossip [label="1. Gossip Detects\nTarget Node UP", fillcolor="#5B9BD5", fontcolor="white"];
        dispatch [label="2. HintsDispatcher\nSchedules Delivery", fillcolor="#5B9BD5", fontcolor="white"];
        read [label="3. Read Hints from\nLocal Hint Files", fillcolor="#5B9BD5", fontcolor="white"];
        throttle [label="4. Apply Throttle\n(hinted_handoff_throttle_in_kb)", fillcolor="#FFC000", fontcolor="black"];
    }

    subgraph cluster_transfer {
        label="Transfer";
        style="rounded,filled";
        fillcolor="#FFE8E8";
        color="#CC9999";

        send [label="5. Send Mutation\nvia Messaging Service", fillcolor="#C55A11", fontcolor="white"];
    }

    subgraph cluster_target {
        label="Hint Target (Recovered Node)";
        style="rounded,filled";
        fillcolor="#E8F4E8";
        color="#99CC99";

        receive [label="6. Receive Mutation", fillcolor="#70AD47", fontcolor="white"];
        apply [label="7. Apply to Memtable\n(normal write path)", fillcolor="#70AD47", fontcolor="white"];
        ack [label="8. Acknowledge\nReceipt", fillcolor="#70AD47", fontcolor="white"];
    }

    cleanup [label="9. Delete Hint\nfrom Source", fillcolor="#7F7F7F", fontcolor="white"];

    gossip -> dispatch -> read -> throttle;
    throttle -> send;
    send -> receive;
    receive -> apply -> ack;
    ack -> cleanup [style=dashed];
}
```

**Delivery mechanism details:**

| Aspect | Description |
|--------|-------------|
| **Transport** | Uses standard inter-node messaging (not dedicated streaming port) |
| **Serialization** | Hints deserialized and sent as mutation messages |
| **Ordering** | Delivered in timestamp order (oldest first) |
| **Batching** | Multiple hints may be batched per network round-trip |
| **Retries** | Failed deliveries retried with exponential backoff |

### Hint Streaming Parameters

The following parameters control hint delivery throughput and resource usage:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `hinted_handoff_throttle_in_kb` | 1024 | Maximum throughput per destination (KB/s) |
| `max_hints_delivery_threads` | 2 | Concurrent delivery threads |
| `hints_flush_period_in_ms` | 10000 | How often hint buffers flush to disk |
| `max_hints_file_size_in_mb` | 128 | Maximum size per hint file |

**Throttling calculation:**

```
Effective hint throughput = hinted_handoff_throttle_in_kb × max_hints_delivery_threads

Example with defaults:
  1024 KB/s × 2 threads = 2048 KB/s = ~2 MB/s total hint delivery capacity
```

```yaml
# cassandra.yaml - Hint delivery tuning

# Increase for faster hint delivery (impacts production traffic)
hinted_handoff_throttle_in_kb: 2048

# More threads for parallel delivery to multiple recovering nodes
max_hints_delivery_threads: 4

# Smaller files for more granular cleanup
max_hints_file_size_in_mb: 64
```

### Hint Delivery Process

| Phase | Operation |
|-------|-----------|
| **Detection** | Gossip announces target node UP |
| **Scheduling** | HintsDispatcher assigns delivery thread |
| **Reading** | Hints read from local hint files in timestamp order |
| **Throttling** | Delivery rate limited by `hinted_handoff_throttle_in_kb` |
| **Streaming** | Mutations sent via messaging service |
| **Application** | Target node applies mutations to memtable |
| **Acknowledgment** | Target confirms receipt |
| **Cleanup** | Delivered hints deleted from source |

### Hint Delivery vs SSTable Streaming

| Characteristic | Hint Delivery | SSTable Streaming |
|----------------|---------------|-------------------|
| **Data unit** | Individual mutations | SSTable file segments |
| **Transport** | Messaging service | Dedicated streaming protocol |
| **Throughput** | KB/s (throttled) | MB/s to GB/s |
| **CPU usage** | Moderate (deserialization) | Low (zero-copy) or high (traditional) |
| **Use case** | Small data volumes, short outages | Large data volumes, topology changes |
| **Port** | `native_transport_port` / `storage_port` | `storage_port` |

!!! warning "Hint Window Limitations"
    Hints are only stored for `max_hint_window_in_ms` duration (default: 3 hours). Nodes down longer than this window will not receive hints and require repair to restore consistency. For extended outages, full repair is necessary.

---

## Streaming Internals

### File Transfer Protocol

SSTable streaming operates on file segments:

```graphviz dot file-transfer-protocol.svg
digraph FileTransferProtocol {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=LR;

    label="SSTable File Transfer Protocol";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    subgraph cluster_source {
        label="Source Node";
        style="rounded,filled";
        fillcolor="#E8E8E8";
        color="#999999";

        sstable [label=<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="2">
            <TR><TD><B>SSTable Components</B></TD></TR>
            <TR><TD ALIGN="LEFT">• Data.db</TD></TR>
            <TR><TD ALIGN="LEFT">• Index.db</TD></TR>
            <TR><TD ALIGN="LEFT">• Filter.db</TD></TR>
            <TR><TD ALIGN="LEFT">• Statistics.db</TD></TR>
            <TR><TD ALIGN="LEFT">• Summary.db</TD></TR>
            <TR><TD ALIGN="LEFT">• TOC.txt</TD></TR>
        </TABLE>>, shape=none, fillcolor="white"];
    }

    filemsg [label="FileMessage\n(segment)", fillcolor="#FFC000", fontcolor="black"];

    subgraph cluster_target {
        label="Target Node";
        style="rounded,filled";
        fillcolor="#E8F4E8";
        color="#99CC99";

        buffer [label="Receive Buffer", fillcolor="#5B9BD5", fontcolor="white"];
        disk [label="Write to Disk", fillcolor="#70AD47", fontcolor="white"];

        buffer -> disk;
    }

    streamrecv [label="StreamReceived\n(acknowledgment)", fillcolor="#70AD47", fontcolor="white"];

    sstable -> filemsg;
    filemsg -> buffer [penwidth=2];
    disk -> streamrecv [style=dashed];
    streamrecv -> sstable [style=dashed, constraint=false];
}
```

### Segment Size and Buffering

| Parameter | Default | Description |
|-----------|---------|-------------|
| Segment size | 64 KB | Chunk size for file transfer |
| Send buffer | 1 MB | Outbound buffering per session |
| Receive buffer | 4 MB | Inbound buffering per session |
| Max concurrent transfers | 1 per host | Parallelism limit |

### Compression

Streaming data is compressed in transit:

```graphviz dot compression-pipeline.svg
digraph CompressionPipeline {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=LR;

    label="Streaming Compression Pipeline";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    data [label="SSTable\nData", fillcolor="#5B9BD5", fontcolor="white"];
    compress [label="LZ4\nCompression", fillcolor="#FFC000", fontcolor="black"];
    network [label="Network\nTransfer", fillcolor="#70AD47", fontcolor="white"];
    decompress [label="LZ4\nDecompression", fillcolor="#FFC000", fontcolor="black"];
    disk [label="Disk\nWrite", fillcolor="#5B9BD5", fontcolor="white"];

    data -> compress -> network -> decompress -> disk;

    stats [label="Compression ratio: 2:1 to 10:1\nCPU overhead: ~10-20%", shape=note, fillcolor="#E8E8E8", fontcolor="black"];
}
```

### Progress Tracking

Streaming progress is tracked at multiple granularities:

```bash
# View active streams
nodetool netstats

# Detailed streaming information
nodetool netstats -H

# Per-session progress
Mode: JOINING
    /10.0.1.2
        Receiving 15 files, 1.2 GB total. Already received 8 files, 650 MB
        /10.0.1.3
        Receiving 12 files, 980 MB total. Already received 12 files, 980 MB
```

### JMX Metrics

```
# Streaming metrics (JMX)
org.apache.cassandra.metrics:type=Streaming,name=TotalIncomingBytes
org.apache.cassandra.metrics:type=Streaming,name=TotalOutgoingBytes
org.apache.cassandra.metrics:type=Streaming,name=ActiveStreams
org.apache.cassandra.metrics:type=Streaming,name=StreamingTime
```

---

## Performance Considerations

### Network Impact

Streaming operations can saturate network capacity:

| Factor | Impact | Mitigation |
|--------|--------|------------|
| Bootstrap | Sustained high throughput | Schedule during low-traffic periods |
| Decommission | Sustained high throughput | Rate limit with `stream_throughput_outbound_megabits_per_sec` |
| Repair | Variable, depends on divergence | Use incremental repair |
| Hints | Lower throughput | Generally minimal impact |

### Disk I/O Impact

```graphviz dot streaming-io-patterns.svg
digraph StreamingIOPatterns {
    fontname="Helvetica";
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];
    rankdir=LR;

    label="Streaming I/O Patterns";
    labelloc="t";
    fontsize=12;

    node [shape=box, style="rounded,filled"];

    subgraph cluster_source {
        label="Source Node";
        style="rounded,filled";
        fillcolor="#FFE8E8";
        color="#CC9999";

        src [label="• Sequential read from SSTable files\n• Minimal random I/O\n• May compete with normal reads", fillcolor="#C55A11", fontcolor="white"];
    }

    subgraph cluster_target {
        label="Target Node";
        style="rounded,filled";
        fillcolor="#E8F4E8";
        color="#99CC99";

        tgt [label="• Sequential write to new SSTables\n• Post-streaming compaction required\n• Temporary 2x space usage", fillcolor="#70AD47", fontcolor="white"];
    }

    src -> tgt [label="streaming", penwidth=2];
}
```

### Memory Pressure

| Streaming Mode | Heap Usage | Recommendation |
|----------------|------------|----------------|
| Zero-copy | Minimal | Preferred when compatible |
| Traditional | Significant | Monitor GC during large operations |

### Throttling Configuration

```yaml
# Limit streaming to prevent impact on production workload

# Outbound throughput limit (Mb/s)
stream_throughput_outbound_megabits_per_sec: 200

# Inter-datacenter streaming limit
inter_dc_stream_throughput_outbound_megabits_per_sec: 25

# Compaction throughput (affects post-streaming compaction)
compaction_throughput_mb_per_sec: 64
```

---

## Operational Procedures

### Monitoring Streaming

```bash
# Active streams summary
nodetool netstats

# Streaming with progress
nodetool netstats -H

# Bootstrap progress
nodetool describecluster | grep -A5 "Bootstrapping"

# Repair progress
nodetool repair_admin list
```

### Troubleshooting

| Symptom | Possible Cause | Resolution |
|---------|----------------|------------|
| Streaming stuck | Network partition | Check connectivity between nodes |
| Slow streaming | Disk I/O saturation | Reduce throttle, check disk health |
| Streaming failures | Timeout | Increase `streaming_socket_timeout_in_ms` |
| OOM during streaming | Traditional mode on large data | Enable zero-copy or increase heap |

### Recovery from Failed Streaming

```bash
# If bootstrap fails
# Option 1: Clear data and retry
sudo rm -rf /var/lib/cassandra/data/*
nodetool bootstrap resume

# Option 2: Wipe and start fresh
sudo rm -rf /var/lib/cassandra/*
# Edit cassandra.yaml: auto_bootstrap: true
# Restart node

# If decommission fails
nodetool decommission  # Retry

# If repair streaming fails
nodetool repair -pr keyspace  # Retry affected ranges
```

---

## Related Documentation

- **[Replica Synchronization](replica-synchronization.md)** - Anti-entropy repair details
- **[Consistency](consistency.md)** - Consistency levels and guarantees
- **[Gossip Protocol](../gossip/index.md)** - Cluster state dissemination
- **[Compaction](../storage-engine/compaction/index.md)** - Post-streaming compaction
