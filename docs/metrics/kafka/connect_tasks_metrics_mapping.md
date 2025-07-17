# Kafka Connect Tasks Dashboard Metrics Mapping

## Overview

The Kafka Connect Tasks Dashboard provides detailed monitoring of individual connector tasks, including task performance, error tracking, and sink-specific metrics. This dashboard helps identify task-level issues and optimize connector performance.

## Metrics Mapping

| Dashboard Metric | Description | Attributes |
|-----------------|-----------|-------------|
| **Task Performance Metrics** |
| `con_connector_task_metrics_` (function='running_ratio') | Ratio of time task is running vs paused | connector={connector}, task={task} |
| `con_connector_task_metrics_` (function='batch_size_avg') | Average batch size processed | connector={connector}, task={task} |
| `con_connector_task_metrics_` (function='offset_commit_success_percentage') | Percentage of successful offset commits | connector={connector}, task={task} |
| `con_connector_task_metrics_` (function='offset_commit_avg_time_ms') | Average time for offset commits | connector={connector}, task={task} |
| `con_connector_task_metrics_` (function='offset_commit_max_time_ms') | Maximum time for offset commits | connector={connector}, task={task} |
| **Task Error Metrics** |
| `con_task_error_metrics_` (function='deadletterqueue_produce_failures') | Failed attempts to produce to DLQ | connector={connector}, task={task} |
| `con_task_error_metrics_` (function='total_record_errors') | Total number of record-level errors | connector={connector}, task={task} |
| `con_task_error_metrics_` (function='total_record_failures') | Total number of record failures | connector={connector}, task={task} |
| `con_task_error_metrics_` (function='total_records_skipped') | Total number of skipped records | connector={connector}, task={task} |
| `con_task_error_metrics_` (function='total_retries') | Total number of retry attempts | connector={connector}, task={task} |
| **Sink Task Metrics** |
| `con_sink_task_metrics_` (function='partition_count') | Number of partitions assigned to task | connector={connector}, task={task} |
| `con_sink_task_metrics_` (function='sink_record_read_total') | Total records read from Kafka | connector={connector}, task={task} |
| `con_sink_task_metrics_` (function='sink_record_active_count') | Number of records being processed | connector={connector}, task={task} |
| `con_sink_task_metrics_` (function='sink_record_send_total') | Total records sent to sink | connector={connector}, task={task} |

## Query Examples

### Task Performance
```promql
# Running ratio per task
sum(con_connector_task_metrics_{function="running_ratio",type='kafka', node_type='connect', connector='$connector', task='$task'}) by (connector,task)

# Average batch size
sum(con_connector_task_metrics_{function="batch_size_avg",type='kafka', node_type='connect', connector='$connector', task='$task'}) by (connector,task)

# Offset commit success rate
sum(con_connector_task_metrics_{function="offset_commit_success_percentage",type='kafka', node_type='connect', connector='$connector', task='$task'}) by (connector,task) * 100
```

### Offset Commit Times
```promql
# Average commit time
sum(con_connector_task_metrics_{function="offset_commit_avg_time_ms",type='kafka', node_type='connect', connector='$connector', task='$task'}) by (connector,task)

# Maximum commit time
sum(con_connector_task_metrics_{function="offset_commit_max_time_ms",type='kafka', node_type='connect', connector='$connector', task='$task'}) by (connector,task)
```

### Error Tracking
```promql
# DLQ produce failures
sum(con_task_error_metrics_{function="deadletterqueue_produce_failures",type='kafka', node_type='connect', connector='$connector', task='$task'})

# Total record errors
sum(con_task_error_metrics_{function="total_record_errors",type='kafka', node_type='connect'})

# Total record failures
sum(con_task_error_metrics_{function="total_record_failures",type='kafka', node_type='connect'})

# Records skipped
sum(con_task_error_metrics_{function="total_records_skipped",type='kafka', node_type='connect'})

# Total retries
sum(con_task_error_metrics_{function="total_retries",type='kafka', node_type='connect'})
```

### Sink Task Metrics
```promql
# Partition count per sink task
sum(con_sink_task_metrics_{function="partition_count",type='kafka', node_type='connect', connector='$connector', task='$task'}) by (connector,task)

# Records read rate
sum(con_sink_task_metrics_{axonfunction="rate",function="sink_record_read_total",type='kafka', node_type='connect', connector='$connector', task='$task'}) by (connector,task)

# Active record count
sum(con_sink_task_metrics_{function="sink_record_active_count",type='kafka', node_type='connect', connector='$connector', task='$task'}) by (connector,task)

# Records sent rate
sum(con_sink_task_metrics_{axonfunction="rate", function="sink_record_send_total",type='kafka', node_type='connect', connector='$connector', task='$task'}) by (connector,task)
```

## Panel Organization

1. **Overview Section**
   - Empty row for spacing/organization

2. **Tasks Metrics**
   - Connector Tasks Batch Size
   - Connector Task Running Ratio
   - Connector Task Commit Success %
   - Connector Task Commit Avg vs Max time

3. **Task Error Metrics**
   - Deadletter Produce Failures (duplicate panels)
   - Record Errors
   - Record Failures
   - Record Skipped
   - Total Retries

4. **Sink Task Metrics**
   - Sink Task Record Active Count
   - Sink Task Record Read
   - Sink Task Partition Count
   - Sink Task Record Send

## Filters

- **host_id**: Filter by specific Connect worker node
- **connector**: Filter by specific connector name
- **task**: Filter by specific task ID

## Best Practices

1. **Task Performance Monitoring**
   - Running ratio should be close to 1.0 for active tasks
   - Monitor batch sizes for throughput optimization
   - Low commit success rate indicates processing issues

2. **Offset Commit Analysis**
   - High commit times indicate performance issues
   - Compare average vs max times for outliers
   - Frequent commit failures suggest configuration issues

3. **Error Management**
   - Monitor DLQ failures for error handling issues
   - Track record errors vs failures vs skipped
   - High retry counts indicate transient issues

4. **Sink Task Optimization**
   - Balance partition assignment across tasks
   - Monitor active record count for backpressure
   - Compare read vs send rates for processing lag

5. **Troubleshooting**
   - Low running ratio: Check for task pauses/failures
   - High error rates: Review connector configuration
   - DLQ failures: Check DLQ topic permissions
   - Commit failures: Verify offset storage configuration

6. **Performance Tuning**
   - Adjust batch sizes for optimal throughput
   - Tune commit intervals based on latency requirements
   - Configure appropriate retry policies
   - Monitor partition assignment balance

7. **Capacity Planning**
   - Track record processing rates
   - Monitor active record counts for memory usage
   - Plan task scaling based on partition count