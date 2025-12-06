# Time Bucketing Pattern

Time bucketing prevents unbounded partition growth by adding a time component to the partition key. Without it, time-series tables (IoT sensors, event logs, metrics) create partitions that grow indefinitely, eventually causing timeouts and OOM errors.

The pattern:
- Add a time bucket (hour, day, week, month) to the partition key
- Choose bucket size based on write volume and target partition size (< 100MB recommended)
- Query multiple buckets when spanning time ranges

This guide covers bucket sizing calculations and implementation patterns.

## The Unbounded Partition Problem

Consider a naive sensor data model:

```sql
CREATE TABLE sensor_readings (
    sensor_id TEXT,
    reading_time TIMESTAMP,
    temperature DOUBLE,
    humidity DOUBLE,
    PRIMARY KEY ((sensor_id), reading_time)
) WITH CLUSTERING ORDER BY (reading_time DESC);
```

This model seems reasonable—partition by sensor, sort by time. But watch what happens:

```
Year 1:   86,400 readings/day × 365 days = 31.5 million rows per sensor
Year 3:   94.6 million rows per sensor
Year 5:   157.7 million rows per sensor

At ~100 bytes/row:
Year 1:   3.15 GB per sensor partition
Year 3:   9.46 GB per sensor partition
Year 5:   15.77 GB per sensor partition
```

### What Goes Wrong

When a partition grows this large, operations fail in spectacular ways:

```
┌─────────────────────────────────────────────────────────────────────┐
│  PROBLEM 1: Read Timeouts                                           │
│  ─────────────────────────────────────────────────────────────────  │
│  Reading "last hour" requires finding rows in a 15GB partition.     │
│  Even with efficient indexing, this scans gigabytes of SSTable      │
│  data. Result: 30-second query, then timeout.                       │
├─────────────────────────────────────────────────────────────────────┤
│  PROBLEM 2: Memory Exhaustion                                       │
│  ─────────────────────────────────────────────────────────────────  │
│  Compaction must load partition into memory. A 15GB partition       │
│  requires 15GB+ heap during compaction. Your 8GB heap OOMs.         │
├─────────────────────────────────────────────────────────────────────┤
│  PROBLEM 3: Repair Failures                                         │
│  ─────────────────────────────────────────────────────────────────  │
│  Repair streams entire partitions between nodes. A 15GB partition   │
│  over a 1Gbps network takes 2+ minutes, during which the node       │
│  appears unresponsive. Hints queue up, causing cascading issues.    │
├─────────────────────────────────────────────────────────────────────┤
│  PROBLEM 4: Hot Spots                                               │
│  ─────────────────────────────────────────────────────────────────  │
│  Current time queries always hit the same partition. One node       │
│  serves 100% of writes for that sensor while others idle.           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## The Solution: Time Buckets

Add a time component to the partition key that limits each partition's time span:

```sql
CREATE TABLE sensor_readings (
    sensor_id TEXT,
    day DATE,                    -- Time bucket
    reading_time TIMESTAMP,
    temperature DOUBLE,
    humidity DOUBLE,
    PRIMARY KEY ((sensor_id, day), reading_time)
) WITH CLUSTERING ORDER BY (reading_time DESC);
```

Now each sensor-day combination is a separate partition:

```
Partition: (sensor_id='temp-001', day='2024-01-15')
┌──────────────────────────────────────────────────────────────────┐
│  Row 1: reading_time=2024-01-15 23:59:59, temp=22.1, humidity=45 │
│  Row 2: reading_time=2024-01-15 23:59:58, temp=22.0, humidity=45 │
│  ...                                                              │
│  Row 86400: reading_time=2024-01-15 00:00:00, temp=21.5, hum=47  │
└──────────────────────────────────────────────────────────────────┘
Size: 86,400 rows × ~100 bytes = 8.6 MB ✓

Partition: (sensor_id='temp-001', day='2024-01-16')
┌──────────────────────────────────────────────────────────────────┐
│  ... another day's data ...                                       │
└──────────────────────────────────────────────────────────────────┘
Size: 8.6 MB ✓
```

Five years of data now spans 1,825 partitions of 8.6MB each instead of one 15.77GB partition.

---

## Choosing the Right Bucket Size

The bucket size depends on your write rate and row size. Calculate the expected partition size:

```
Partition Size = (writes_per_time_unit) × (bucket_duration) × (bytes_per_row)
```

### Bucket Size Decision Matrix

| Write Rate | Row Size | Daily Bucket | Hourly Bucket | 10-Min Bucket |
|------------|----------|--------------|---------------|---------------|
| 1/sec | 100 B | 8.6 MB ✓ | 360 KB | 60 KB |
| 10/sec | 100 B | 86 MB ✓ | 3.6 MB ✓ | 600 KB |
| 100/sec | 100 B | 860 MB ✗ | 36 MB ✓ | 6 MB ✓ |
| 1000/sec | 100 B | 8.6 GB ✗ | 360 MB ✗ | 60 MB ✓ |
| 10000/sec | 100 B | 86 GB ✗ | 3.6 GB ✗ | 600 MB ✗ |
| 1/sec | 1 KB | 86 MB ✓ | 3.6 MB ✓ | 600 KB |
| 10/sec | 1 KB | 860 MB ✗ | 36 MB ✓ | 6 MB ✓ |
| 100/sec | 1 KB | 8.6 GB ✗ | 360 MB ✗ | 60 MB ✓ |

**Guidelines:**
- Target: 10MB - 100MB per partition
- Below 1MB: Partitions are too small (overhead dominates)
- Above 100MB: Risk of timeout issues
- Above 1GB: Serious problems guaranteed

### Bucket Type Reference

```sql
-- Yearly bucket (very low volume only)
PRIMARY KEY ((entity_id, year), timestamp)
-- year as INT: 2024

-- Monthly bucket
PRIMARY KEY ((entity_id, month), timestamp)
-- month as TEXT: '2024-01' or INT: 202401

-- Weekly bucket
PRIMARY KEY ((entity_id, week), timestamp)
-- week as TEXT: '2024-W03' or INT: 202403

-- Daily bucket (most common)
PRIMARY KEY ((entity_id, day), timestamp)
-- day as DATE: '2024-01-15'

-- Hourly bucket
PRIMARY KEY ((entity_id, hour), timestamp)
-- hour as TIMESTAMP: '2024-01-15 14:00:00+0000'

-- 10-minute bucket (high volume)
PRIMARY KEY ((entity_id, bucket), timestamp)
-- bucket as TIMESTAMP: '2024-01-15 14:30:00+0000'

-- Minute bucket (extreme volume)
PRIMARY KEY ((entity_id, minute), timestamp)
-- minute as TIMESTAMP: '2024-01-15 14:35:00+0000'
```

---

## Implementation Patterns

### Daily Bucketing (Recommended Default)

Most time-series use cases work well with daily buckets:

```sql
CREATE TABLE metrics (
    service_id TEXT,
    date DATE,
    metric_time TIMESTAMP,
    metric_name TEXT,
    value DOUBLE,
    tags MAP<TEXT, TEXT>,
    PRIMARY KEY ((service_id, date), metric_time, metric_name)
) WITH CLUSTERING ORDER BY (metric_time DESC, metric_name ASC)
  AND default_time_to_live = 2592000    -- 30 days
  AND compaction = {
      'class': 'TimeWindowCompactionStrategy',
      'compaction_window_size': '1',
      'compaction_window_unit': 'DAYS'
  };
```

**Application code (Python):**

```python
from datetime import date, datetime
from cassandra.cluster import Cluster

cluster = Cluster(['node1', 'node2', 'node3'])
session = cluster.connect('metrics_keyspace')

# Prepared statement (create once, reuse)
insert_stmt = session.prepare("""
    INSERT INTO metrics (service_id, date, metric_time, metric_name, value, tags)
    VALUES (?, ?, ?, ?, ?, ?)
""")

def write_metric(service_id: str, metric_name: str, value: float, tags: dict = None):
    now = datetime.utcnow()
    today = now.date()

    session.execute(insert_stmt, [
        service_id,
        today,           # Bucket: today's date
        now,             # Full timestamp
        metric_name,
        value,
        tags or {}
    ])

# Usage
write_metric('api-gateway', 'request_latency_ms', 45.2, {'endpoint': '/users'})
```

**Application code (Java):**

```java
import java.time.LocalDate;
import java.time.Instant;
import java.util.Map;

public class MetricsWriter {
    private final PreparedStatement insertStmt;
    private final CqlSession session;

    public MetricsWriter(CqlSession session) {
        this.session = session;
        this.insertStmt = session.prepare(
            "INSERT INTO metrics (service_id, date, metric_time, metric_name, value, tags) " +
            "VALUES (?, ?, ?, ?, ?, ?)"
        );
    }

    public void writeMetric(String serviceId, String metricName, double value, Map<String, String> tags) {
        Instant now = Instant.now();
        LocalDate today = LocalDate.now();

        session.execute(insertStmt.bind(
            serviceId,
            today,           // Bucket
            now,             // Full timestamp
            metricName,
            value,
            tags
        ));
    }
}
```

### Hourly Bucketing (High Volume)

For high-throughput streams:

```sql
CREATE TABLE events (
    tenant_id TEXT,
    hour TIMESTAMP,
    event_id TIMEUUID,
    event_type TEXT,
    payload TEXT,
    PRIMARY KEY ((tenant_id, hour), event_id)
) WITH CLUSTERING ORDER BY (event_id DESC)
  AND default_time_to_live = 604800;    -- 7 days
```

**Bucket calculation (critical!):**

```python
from datetime import datetime, timedelta

def get_hour_bucket(timestamp: datetime) -> datetime:
    """Truncate timestamp to the start of the hour."""
    return timestamp.replace(minute=0, second=0, microsecond=0)

# Example
event_time = datetime(2024, 1, 15, 14, 37, 22)  # 2:37:22 PM
bucket = get_hour_bucket(event_time)            # 2:00:00 PM
```

```java
import java.time.Instant;
import java.time.temporal.ChronoUnit;

public Instant getHourBucket(Instant timestamp) {
    return timestamp.truncatedTo(ChronoUnit.HOURS);
}
```

### Sub-Hour Bucketing (Extreme Volume)

For 10,000+ writes/second:

```sql
CREATE TABLE high_volume_events (
    stream_id TEXT,
    bucket_10min TIMESTAMP,
    event_id TIMEUUID,
    data BLOB,
    PRIMARY KEY ((stream_id, bucket_10min), event_id)
) WITH CLUSTERING ORDER BY (event_id DESC);
```

**10-minute bucket calculation:**

```python
def get_10min_bucket(timestamp: datetime) -> datetime:
    """Truncate timestamp to the start of 10-minute window."""
    minute = (timestamp.minute // 10) * 10
    return timestamp.replace(minute=minute, second=0, microsecond=0)

# Example
event_time = datetime(2024, 1, 15, 14, 37, 22)  # 2:37:22 PM
bucket = get_10min_bucket(event_time)           # 2:30:00 PM
```

---

## Querying Across Time Buckets

The trade-off of time bucketing: querying a time range requires querying multiple partitions.

### Single Bucket Query (Efficient)

```sql
-- Query: Last hour's data
SELECT * FROM metrics
WHERE service_id = 'api-gateway'
  AND date = '2024-01-15'
  AND metric_time >= '2024-01-15 14:00:00'
  AND metric_time < '2024-01-15 15:00:00';
```

### Multi-Bucket Query (Application Logic Required)

```python
from datetime import date, timedelta
from typing import List
from cassandra.query import SimpleStatement

def query_date_range(session, service_id: str, start_date: date, end_date: date) -> List:
    """Query metrics across multiple daily buckets."""

    select_stmt = session.prepare("""
        SELECT metric_time, metric_name, value
        FROM metrics
        WHERE service_id = ? AND date = ?
    """)

    results = []
    current = start_date

    while current <= end_date:
        rows = session.execute(select_stmt, [service_id, current])
        results.extend(rows)
        current += timedelta(days=1)

    return results

# Query last 7 days
today = date.today()
week_ago = today - timedelta(days=7)
metrics = query_date_range(session, 'api-gateway', week_ago, today)
```

### Parallel Multi-Bucket Queries (Performance Optimized)

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from typing import List

def query_date_range_parallel(session, service_id: str, start_date: date, end_date: date) -> List:
    """Query metrics across multiple buckets in parallel."""

    select_stmt = session.prepare("""
        SELECT metric_time, metric_name, value
        FROM metrics
        WHERE service_id = ? AND date = ?
    """)

    # Generate all dates in range
    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current)
        current += timedelta(days=1)

    # Query in parallel
    results = []
    with ThreadPoolExecutor(max_workers=min(len(dates), 10)) as executor:
        futures = {
            executor.submit(session.execute, select_stmt, [service_id, d]): d
            for d in dates
        }

        for future in as_completed(futures):
            rows = future.result()
            results.extend(rows)

    return results
```

```java
import java.util.concurrent.CompletableFuture;
import java.util.stream.Collectors;

public List<Row> queryDateRangeParallel(
        CqlSession session,
        String serviceId,
        LocalDate startDate,
        LocalDate endDate) {

    PreparedStatement selectStmt = session.prepare(
        "SELECT metric_time, metric_name, value FROM metrics WHERE service_id = ? AND date = ?"
    );

    // Generate all dates
    List<LocalDate> dates = startDate.datesUntil(endDate.plusDays(1))
        .collect(Collectors.toList());

    // Execute queries in parallel
    List<CompletableFuture<AsyncResultSet>> futures = dates.stream()
        .map(date -> session.executeAsync(selectStmt.bind(serviceId, date))
            .toCompletableFuture())
        .collect(Collectors.toList());

    // Collect results
    return futures.stream()
        .map(CompletableFuture::join)
        .flatMap(rs -> StreamSupport.stream(rs.currentPage().spliterator(), false))
        .collect(Collectors.toList());
}
```

### Using IN Clause (Limited Use)

```sql
-- Query specific buckets (limit to ~10 values)
SELECT * FROM metrics
WHERE service_id = 'api-gateway'
  AND date IN ('2024-01-13', '2024-01-14', '2024-01-15');
```

**Warning:** Large IN clauses create coordinator overhead. Keep under 10-20 values.

---

## Combining with TTL

Time-bucketed data usually has a retention period. Combine with TTL for automatic cleanup:

```sql
CREATE TABLE metrics (
    service_id TEXT,
    date DATE,
    metric_time TIMESTAMP,
    metric_name TEXT,
    value DOUBLE,
    PRIMARY KEY ((service_id, date), metric_time, metric_name)
) WITH default_time_to_live = 2592000   -- 30 days (data TTL)
  AND gc_grace_seconds = 86400;          -- 1 day (tombstone retention)
```

### TTL and Bucket Alignment

Align gc_grace_seconds with your repair schedule:

```
┌─────────────────────────────────────────────────────────────────────┐
│  RULE: gc_grace_seconds must be longer than your repair interval    │
│  ─────────────────────────────────────────────────────────────────  │
│  If repair runs weekly: gc_grace_seconds > 604800 (7 days)          │
│  If repair runs daily:  gc_grace_seconds > 86400 (1 day)            │
│                                                                     │
│  Why? Tombstones must exist on all replicas before being purged.    │
│  If purged too early, deleted data can "resurrect" during repair.   │
└─────────────────────────────────────────────────────────────────────┘
```

**Recommended settings:**

| Bucket Size | Data TTL | gc_grace_seconds | Repair Frequency |
|-------------|----------|------------------|------------------|
| Hourly | 24-72 hours | 4 hours | Every 4 hours |
| Daily | 7-30 days | 1-2 days | Daily |
| Weekly | 30-90 days | 3-7 days | Weekly |
| Monthly | 90-365 days | 7-10 days | Weekly |

### Explicit TTL on Insert

```sql
-- Override default TTL for specific rows
INSERT INTO metrics (service_id, date, metric_time, metric_name, value)
VALUES ('api-gateway', '2024-01-15', '2024-01-15 14:30:00', 'debug_latency', 123.4)
USING TTL 3600;  -- 1 hour (debug data expires faster)
```

---

## Advanced Patterns

### Multi-Resolution Time Series

Store data at multiple granularities for different query patterns:

```sql
-- High-resolution: raw data, short retention
CREATE TABLE metrics_raw (
    service_id TEXT,
    hour TIMESTAMP,
    metric_time TIMESTAMP,
    metric_name TEXT,
    value DOUBLE,
    PRIMARY KEY ((service_id, hour), metric_time, metric_name)
) WITH default_time_to_live = 86400;  -- 24 hours

-- Medium-resolution: 1-minute aggregates
CREATE TABLE metrics_1min (
    service_id TEXT,
    date DATE,
    minute TIMESTAMP,
    metric_name TEXT,
    avg_value DOUBLE,
    min_value DOUBLE,
    max_value DOUBLE,
    count BIGINT,
    PRIMARY KEY ((service_id, date), minute, metric_name)
) WITH default_time_to_live = 604800;  -- 7 days

-- Low-resolution: 1-hour aggregates
CREATE TABLE metrics_1hour (
    service_id TEXT,
    month TEXT,
    hour TIMESTAMP,
    metric_name TEXT,
    avg_value DOUBLE,
    min_value DOUBLE,
    max_value DOUBLE,
    count BIGINT,
    PRIMARY KEY ((service_id, month), hour, metric_name)
) WITH default_time_to_live = 7776000;  -- 90 days
```

**Query strategy:**
- Last 24 hours: Query `metrics_raw`
- Last 7 days: Query `metrics_1min`
- Last 90 days: Query `metrics_1hour`

### Rolling Window with Fixed Buckets

For use cases needing exactly N hours of history with automatic wraparound:

```sql
CREATE TABLE rolling_metrics (
    service_id TEXT,
    bucket INT,              -- 0-23 for 24-hour window
    metric_time TIMESTAMP,
    metric_name TEXT,
    value DOUBLE,
    PRIMARY KEY ((service_id, bucket), metric_time, metric_name)
) WITH CLUSTERING ORDER BY (metric_time DESC, metric_name ASC);
```

```python
def get_rolling_bucket(timestamp: datetime, num_buckets: int = 24, bucket_hours: int = 1) -> int:
    """
    Calculate rolling bucket number.

    For 24-hour window with hourly buckets:
    - Hour 0-1 → bucket 0
    - Hour 1-2 → bucket 1
    - ...
    - Hour 23-24 → bucket 23
    - Hour 24-25 → bucket 0 (wraps)
    """
    hours_since_epoch = int(timestamp.timestamp() / 3600)
    return (hours_since_epoch // bucket_hours) % num_buckets

# Data automatically overwrites when bucket cycles
# No need for TTL or explicit deletes
```

### Dynamic Bucket Sizing

Adjust bucket size based on entity volume:

```sql
CREATE TABLE adaptive_events (
    entity_id TEXT,
    bucket_id TEXT,          -- Format varies by entity
    event_time TIMESTAMP,
    event_id UUID,
    data TEXT,
    PRIMARY KEY ((entity_id, bucket_id), event_time, event_id)
);
```

```python
class AdaptiveBucketing:
    def __init__(self, session):
        self.session = session
        # Cache of entity → bucket_size mappings
        self.entity_bucket_sizes = {}

    def get_bucket(self, entity_id: str, timestamp: datetime) -> str:
        """
        High-volume entities use hourly buckets.
        Low-volume entities use daily buckets.
        """
        bucket_size = self.entity_bucket_sizes.get(entity_id, 'daily')

        if bucket_size == 'hourly':
            return timestamp.strftime('%Y-%m-%d-%H')  # '2024-01-15-14'
        else:
            return timestamp.strftime('%Y-%m-%d')     # '2024-01-15'

    def promote_to_hourly(self, entity_id: str):
        """Called when entity exceeds daily volume threshold."""
        self.entity_bucket_sizes[entity_id] = 'hourly'
```

---

## Monitoring and Maintenance

### Check Partition Sizes

```bash
# Table-level histogram
nodetool tablehistograms keyspace.metrics

# Look for:
# - Median partition size (50th percentile)
# - Large partitions (99th percentile, max)

# Example output:
# Partition Size (bytes)
#                              Percentile      Value
#                                    50%    8650752    # 8.6 MB - good
#                                    95%   12582912    # 12 MB - acceptable
#                                    99%   52428800    # 50 MB - monitor
#                                   Max   104857600    # 100 MB - investigate
```

### Identify Large Partitions

```bash
# Using sstablemetadata (offline analysis)
sstablemetadata /var/lib/cassandra/data/keyspace/table-*/nb-*-big-Data.db | \
  grep -E "(Partition|Size)"

# Using nodetool cfhistograms (deprecated but still works)
nodetool cfhistograms keyspace table
```

### Query Tracing

```sql
-- Enable tracing for specific queries
TRACING ON;

SELECT * FROM metrics
WHERE service_id = 'api-gateway'
  AND date = '2024-01-15'
LIMIT 100;

-- Look for:
-- - "Read X live rows and Y tombstone cells"
-- - Latency per node
-- - SSTable count
```

### JMX Metrics to Monitor

```
# Partition size distribution
org.apache.cassandra.metrics:type=Table,keyspace=*,scope=*,name=EstimatedPartitionSizeHistogram

# Large partition warnings
org.apache.cassandra.metrics:type=Table,keyspace=*,scope=*,name=MaxPartitionSize

# Tombstone warnings
org.apache.cassandra.metrics:type=Table,keyspace=*,scope=*,name=TombstoneScannedHistogram
```

---

## Common Mistakes

### Mistake 1: Bucket Too Large

```sql
-- WRONG: Monthly bucket for high-volume data
CREATE TABLE events (
    entity_id TEXT,
    month TEXT,
    event_time TIMESTAMP,
    PRIMARY KEY ((entity_id, month), event_time)
);

-- At 100 events/second: 259 million events/month = 25.9 GB partition
```

**Fix:** Use hourly or daily buckets for high-volume streams.

### Mistake 2: Bucket Too Small

```sql
-- WRONG: Minute bucket for low-volume data
CREATE TABLE events (
    entity_id TEXT,
    minute TIMESTAMP,
    event_time TIMESTAMP,
    PRIMARY KEY ((entity_id, minute), event_time)
);

-- At 1 event/minute: 1 row per partition (maximum overhead)
-- 1 year = 525,600 tiny partitions per entity
```

**Fix:** Use daily buckets for low-volume streams.

### Mistake 3: Forgetting to Query Multiple Buckets

```python
# WRONG: Only queries current bucket
def get_recent_events(session, entity_id):
    today = date.today()
    return session.execute(
        "SELECT * FROM events WHERE entity_id = ? AND date = ?",
        [entity_id, today]
    )
    # Misses events from yesterday that are still within "recent" window
```

**Fix:** Calculate all buckets that overlap with the query time range.

### Mistake 4: Misaligned TTL and gc_grace

```sql
-- WRONG: gc_grace too short for weekly repairs
CREATE TABLE metrics (...)
WITH default_time_to_live = 604800    -- 7 days
  AND gc_grace_seconds = 3600;         -- 1 hour

-- Tombstones purged before repair syncs them
-- Deleted data may "resurrect" from other replicas
```

**Fix:** gc_grace_seconds must exceed repair interval.

---

## Best Practices Summary

### Do

```
✓ Calculate expected partition size before choosing bucket
✓ Use daily buckets as the default starting point
✓ Align TWCS compaction window with bucket size
✓ Use TTL instead of explicit deletes
✓ Query single bucket when possible
✓ Use parallel async queries for multi-bucket reads
✓ Monitor partition sizes with nodetool tablehistograms
✓ Align gc_grace_seconds with repair schedule
```

### Don't

```
✗ Use buckets that create partitions > 100MB
✗ Use buckets that create partitions < 1MB
✗ Query unbounded date ranges without limits
✗ Use large IN clauses (> 20 values)
✗ Forget to handle bucket boundaries in application
✗ Set gc_grace_seconds shorter than repair interval
✗ Mix bucket sizes within the same table
```

---

## Next Steps

- **[Anti-Patterns](../anti-patterns/index.md)** - Large partition dangers
- **[TWCS Compaction](../../architecture/compaction/index.md)** - Time-series compaction
- **[E-Commerce Example](../examples/e-commerce.md)** - Complete schema design
- **[Operations Guide](../../operations/index.md)** - Production maintenance
