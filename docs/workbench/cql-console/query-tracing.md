---
title: "Query Tracing"
description: "Trace CQL query execution in AxonOps Workbench. Visualize performance bottlenecks with interactive charts."
meta:
  - name: keywords
    content: "query tracing, performance analysis, execution plan, bottleneck, trace visualization, AxonOps Workbench"
---

# Query Tracing

Query tracing reveals exactly how Cassandra executes a query — which node coordinated the request, which replicas were contacted, and how much time was spent at each step. AxonOps Workbench makes trace data accessible through an interactive visual interface, turning raw trace events into a clear picture of query performance.

<!-- Screenshot: Query Tracing tab showing a timeline chart, doughnut chart, and activities table for a traced query -->

## Enabling Tracing

To trace a query, enable tracing in your CQL session before executing the statement. In the CQL Console, run:

```sql
TRACING ON;
```

Then execute your query as usual:

```sql
SELECT * FROM my_keyspace.users WHERE user_id = 123;
```

When tracing is enabled, Cassandra records detailed execution events for every subsequent query. Each traced query produces a **session ID** that uniquely identifies its trace data.

To disable tracing when you are finished:

```sql
TRACING OFF;
```

!!! note
    Tracing adds overhead to every query executed while it is active. Cassandra writes trace events to the `system_traces` keyspace on each participating node. Use tracing for targeted debugging and performance analysis, not for production traffic.

### Viewing a Trace

After running a traced query, the query output includes a tracing session ID. AxonOps Workbench provides a **tracing button** on each query result block that has an associated trace session. Click this button to fetch and display the trace data in the **Query Tracing** tab.

<!-- Screenshot: Query result block showing the tracing button enabled next to copy and download buttons -->

You can also search for a specific session by pasting its session ID into the search field at the top of the Query Tracing tab. The search field accepts session IDs and partial query text to help you locate traces across your session history.

## Understanding Trace Output

When you open a trace, AxonOps Workbench displays the session ID along with a timestamp badge, a set of source node filter buttons, interactive charts, and a detailed activities table.

### Trace Events

Each trace event represents a discrete step in the query execution pipeline. Cassandra records these events on both the coordinator node and the replica nodes involved in the query. The activities table displays the following fields for each event:

| Field | Description |
|-------|-------------|
| **Activity** | A description of what Cassandra did at this step (e.g., "Parsing SELECT statement", "Reading data from memtable", "Sending message to replica") |
| **Source** | The IP address of the node that recorded this event |
| **Source Data Center** | The data center to which the source node belongs |
| **Source Elapsed** | The time elapsed for this event relative to the previous event, displayed in milliseconds |
| **Source Port** | The port on the source node |
| **Thread** | The Cassandra thread that processed this event |
| **Event ID** | A time-based UUID identifying this specific event |
| **Session ID** | The tracing session ID that groups all events for this query |

### Reading the Timeline

Trace events are ordered chronologically, showing the full sequence of operations from the moment the coordinator receives the query to when the final response is assembled. A typical read query follows this pattern:

1. The **coordinator** parses the CQL statement and determines which replicas hold the requested data
2. The coordinator sends read requests to the appropriate **replica nodes**
3. Each replica reads data from its local storage (memtables and SSTables)
4. Replicas send responses back to the coordinator
5. The coordinator assembles the result and returns it to the client

The **Source Elapsed** column shows the incremental time between consecutive events. This makes it straightforward to identify which specific step consumed the most time during execution.

## Trace Visualization

AxonOps Workbench renders trace data using two interactive Chart.js charts that make it easy to spot where time is being spent.

<!-- Screenshot: Timeline bar chart and doughnut chart side by side showing trace activity distribution -->

### Timeline Chart

The timeline chart is a horizontal bar chart where each bar represents a trace event. The horizontal axis shows elapsed time in milliseconds, and each bar spans from the start to the end of that event relative to the trace session. Bars are color-coded to visually distinguish individual activities.

The timeline chart supports interactive exploration:

- **Zoom** — Hold `Ctrl` and scroll the mouse wheel to zoom in on a specific time range
- **Pan** — Hold `Ctrl` and drag to pan across the timeline
- **Reset zoom** — Click the zoom reset button to return to the full view
- **Click an event** — Click any bar in the chart to filter the activities table to that specific event

### Doughnut Chart

The doughnut chart displays the proportional time distribution across trace events. Each slice represents a single activity, sized according to the time it consumed relative to the total trace duration. Hover over a slice to see the elapsed time in milliseconds. Clicking a slice filters the activities table to that event.

### Filtering by Source Node

Above the charts, a row of **source filter buttons** shows each node that participated in the query. Each button displays the node IP address and, when available, its data center name as a badge. Click a source button to filter both the charts and the activities table to show only events from that node.

The **All** button resets the view to show events from all nodes. This filtering is useful for isolating coordinator activity from replica activity, or for comparing performance across replicas.

## Common Trace Patterns

Understanding what normal and abnormal traces look like helps you quickly diagnose performance issues.

### Healthy Trace

A well-performing query trace shows:

- Low and consistent elapsed times between events (sub-millisecond to low single-digit milliseconds)
- Coordinator and replica events interleaved in a tight sequence
- Total trace duration proportional to the consistency level (more replicas contacted means slightly longer traces)

### High Coordinator Latency

If the coordinator node shows large elapsed times before contacting replicas, look for:

- Excessive garbage collection pauses on the coordinator
- High coordinator load causing thread pool contention
- Network delays between the client and the coordinator

### Slow Replica Responses

When replicas show disproportionately large elapsed times compared to the coordinator, investigate:

- Disk I/O bottlenecks on the replica — particularly if the trace shows time spent reading from SSTables
- Compaction backlog causing excessive SSTable reads
- Uneven data distribution placing too much load on specific replicas

### Tombstone Warnings

Traces that include tombstone-scanning activity indicate that Cassandra is reading through deleted data markers. High tombstone counts degrade read performance and can appear as:

- Events mentioning tombstone scans or tombstone thresholds
- Unexpectedly long elapsed times during the read phase

!!! warning
    If you see tombstone-related events in your traces, review your data model and deletion patterns. Consider adjusting `gc_grace_seconds` or restructuring your tables to minimize tombstone accumulation.

### Large Partition Warnings

Traces involving large partitions show elevated read times because Cassandra must scan more data within a single partition. Indicators include:

- High elapsed times during memtable or SSTable reads for a single partition key
- A disproportionate number of read events relative to the amount of data returned

!!! tip
    Use query tracing to validate data model decisions. If traces consistently show large partition reads, consider refining your partition key strategy to distribute data more evenly.

## Trace Data Source

Behind the scenes, Cassandra stores trace data in two system tables:

- **`system_traces.sessions`** — Contains one row per traced query with the session ID, coordinator address, duration, and query parameters
- **`system_traces.events`** — Contains the individual trace events for each session, including the activity description, source node, and elapsed time

AxonOps Workbench retrieves trace data by querying these tables using the session ID that Cassandra returns when tracing is enabled. The `getQueryTrace` method fetches both the session metadata and all associated events, then presents them in the visual interface.

### Session ID Correlation

Each traced query produces a unique session ID (a UUID). This session ID is the key for correlating trace data:

- The session ID appears in the query result output when tracing is active
- It is displayed as a badge in the Query Tracing tab for each traced query
- You can use it to search for a specific trace in the Query Tracing tab
- Multiple traces are preserved in the tab during your session, allowing you to compare traces side by side

### Copying Trace Data

Each trace result includes a **copy button** that copies the full trace data to your clipboard in JSON format. The toast notification confirms the copy and shows the data size. This is useful for sharing trace data with team members or including it in performance reports.

!!! tip
    Trace data in `system_traces` has a default TTL (time to live) of 24 hours. If you need to reference a trace later, copy the data or take note of the session ID while the trace is still available.
