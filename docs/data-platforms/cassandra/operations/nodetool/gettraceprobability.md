---
title: "nodetool gettraceprobability"
description: "Display query tracing probability in Cassandra using nodetool gettraceprobability."
meta:
  - name: keywords
    content: "nodetool gettraceprobability, query tracing, trace probability, Cassandra debugging"
---

# nodetool gettraceprobability

Displays the current probability of tracing CQL requests on the node.

---

## Synopsis

```bash
nodetool [connection_options] gettraceprobability
```
See [connection options](index.md#connection-options) for connection options.

## Description

`nodetool gettraceprobability` shows the current probability (0.0 to 1.0) that any given CQL request will be traced. This setting controls Cassandra's probabilistic tracing feature, which samples a percentage of requests for detailed performance analysis.

### What is Request Tracing?

Request tracing in Cassandra records detailed timing information about how a CQL query is processed across the cluster. When a request is traced, Cassandra captures:

- **Coordinator activity** - Time spent parsing, planning, and coordinating the query
- **Replica communication** - Time to send requests to and receive responses from replica nodes
- **Per-replica processing** - What each replica did (memtable reads, SSTable reads, bloom filter checks)
- **Latency breakdown** - Microsecond-level timing for each operation phase

Trace data is written to the `system_traces` keyspace, which contains two tables:

| Table | Contents |
|-------|----------|
| `system_traces.sessions` | One row per traced request with summary information |
| `system_traces.events` | Detailed events for each traced request |

### Why Probabilistic Tracing?

Tracing has significant overhead—each traced request generates multiple writes to `system_traces`. Enabling tracing for all requests (probability 1.0) would:

- Increase write amplification substantially
- Consume significant disk space
- Impact cluster performance

Probabilistic tracing allows sampling a small percentage of requests to gather representative performance data without overwhelming the cluster. For example, with 0.001 (0.1%) probability on a cluster handling 100,000 requests/second, approximately 100 requests/second would be traced—enough for analysis without significant overhead.

---

## Examples

### Basic Usage

```bash
nodetool gettraceprobability
```

### Sample Output

```
Current trace probability: 0.0
```

A value of `0.0` means no requests are being traced (the default).

---

## Understanding Probability Values

| Value | Percentage | Meaning | Use Case |
|-------|------------|---------|----------|
| 0.0 | 0% | No tracing (default) | Normal production operation |
| 0.0001 | 0.01% | 1 in 10,000 requests | High-traffic production sampling |
| 0.001 | 0.1% | 1 in 1,000 requests | Production performance monitoring |
| 0.01 | 1% | 1 in 100 requests | Active troubleshooting |
| 0.1 | 10% | 1 in 10 requests | Development/testing |
| 1.0 | 100% | All requests | Brief debugging only |

!!! warning "Performance Impact"
    Values above 0.01 (1%) can noticeably impact performance on busy clusters. Values of 0.1 or higher should only be used briefly during active debugging sessions or in non-production environments.

---

## Viewing Trace Data

Once tracing is enabled and requests are sampled, trace data can be queried from `system_traces`:

### View Recent Trace Sessions

```cql
SELECT * FROM system_traces.sessions
WHERE started_at > toTimestamp(now()) - 1h
LIMIT 10;
```

### View Events for a Specific Trace

```cql
-- First, get a session_id from sessions table
SELECT session_id, coordinator, request, started_at, duration
FROM system_traces.sessions LIMIT 5;

-- Then query events for that session
SELECT activity, source, source_elapsed, thread
FROM system_traces.events
WHERE session_id = <session_id_from_above>;
```

### Example Trace Output

```
 activity                                          | source        | source_elapsed
---------------------------------------------------+---------------+----------------
 Parsing SELECT * FROM users WHERE id = ?          | 192.168.1.101 |             52
 Preparing statement                               | 192.168.1.101 |            118
 Determining replicas for query                    | 192.168.1.101 |            156
 Sending READ message to /192.168.1.102           | 192.168.1.101 |            203
 READ message received from /192.168.1.101        | 192.168.1.102 |             45
 Executing single-partition query on users        | 192.168.1.102 |            112
 Acquiring sstable references                      | 192.168.1.102 |            158
 Bloom filter allows skipping sstable 1           | 192.168.1.102 |            201
 Partition index with 1 entries found             | 192.168.1.102 |            289
 Seeking to partition indexed section             | 192.168.1.102 |            334
 Merging memtable contents                        | 192.168.1.102 |            412
 Read 1 live rows and 0 tombstone cells           | 192.168.1.102 |            498
 Enqueuing response to /192.168.1.101             | 192.168.1.102 |            534
 Processing response from /192.168.1.102          | 192.168.1.101 |           2341
 Request complete                                  | 192.168.1.101 |           2456
```

---

## Use Cases

### Verify Tracing is Disabled

Before performance testing, ensure tracing isn't adding overhead:

```bash
nodetool gettraceprobability
# Should return 0.0
```

### Check if Debugging Session is Active

Verify if someone enabled tracing for troubleshooting:

```bash
nodetool gettraceprobability
# If > 0.0, tracing is active
```

### Audit Cluster Configuration

Include in cluster health checks:

```bash
#!/bin/bash
# Check trace probability on all nodes

for node in $(nodetool status | grep "^UN" | awk '{print $2}'); do
    prob=$(ssh "$node" 'nodetool gettraceprobability 2>/dev/null | grep -oE "[0-9]+\.[0-9]+"')
    if [ "$prob" != "0.0" ]; then
        echo "WARNING: $node has trace probability $prob"
    fi
done
```

---

## Trace Probability and Performance

The relationship between trace probability and overhead:

| Probability | Overhead | `system_traces` Growth | Recommended Duration |
|-------------|----------|------------------------|----------------------|
| 0.0 | None | None | Indefinite (default) |
| 0.0001-0.001 | Minimal | Slow | Days to weeks |
| 0.001-0.01 | Low | Moderate | Hours to days |
| 0.01-0.1 | Moderate | Fast | Minutes to hours |
| 0.1-1.0 | High | Very fast | Minutes only |

!!! tip "Cleaning Up Trace Data"
    Trace data accumulates in `system_traces` with a default TTL of 24 hours. For extended tracing sessions, consider:

    - Lowering the TTL: `ALTER TABLE system_traces.sessions WITH default_time_to_live = 3600;`
    - Manually truncating: `TRUNCATE system_traces.sessions; TRUNCATE system_traces.events;`

---

## Comparing with CQL TRACING

Cassandra offers two tracing mechanisms:

| Feature | Probabilistic Tracing | CQL `TRACING ON` |
|---------|----------------------|------------------|
| Scope | All requests cluster-wide | Single cqlsh session |
| Control | `nodetool settraceprobability` | `TRACING ON/OFF` in cqlsh |
| Sampling | Percentage-based | All queries in session |
| Use case | Production monitoring | Interactive debugging |
| Persistence | `system_traces` tables | `system_traces` tables |

```cql
-- CQL session-level tracing (alternative to probabilistic)
TRACING ON;
SELECT * FROM my_keyspace.my_table WHERE id = 123;
TRACING OFF;
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [settraceprobability](settraceprobability.md) | Set the trace probability |
| [proxyhistograms](proxyhistograms.md) | View latency histograms |
| [tablehistograms](tablehistograms.md) | View per-table latency histograms |