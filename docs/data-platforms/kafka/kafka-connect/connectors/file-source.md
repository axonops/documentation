---
title: "File Source Connector"
description: "Kafka Connect File Source connector. Log file streaming, file watching, and line parsing."
meta:
  - name: keywords
    content: "Kafka file source connector, FileStreamSource, file ingestion, log file connector"
---

# File Source Connector

Stream file contents to Kafka topics for log aggregation and file-based data ingestion.

---

## Overview

The File Source Connector reads files and writes their contents to Kafka, supporting:

- Line-by-line file reading
- File watching for new content
- Multiple file patterns
- Offset tracking for restarts

!!! warning "Production Use"
    The bundled FileStreamSourceConnector is intended for development and testing. For production file streaming, consider specialized connectors like Filebeat with Kafka output or dedicated log shipping solutions.

---

## Built-in Connector

Apache Kafka includes a basic file source connector:

```json
{
  "name": "file-source",
  "config": {
    "connector.class": "org.apache.kafka.connect.file.FileStreamSourceConnector",
    "tasks.max": "1",
    "file": "/var/log/application.log",
    "topic": "application-logs"
  }
}
```

### Limitations

| Limitation | Description |
|------------|-------------|
| Single file | Only reads one file per connector |
| No glob patterns | Cannot watch directory |
| No offset persistence | Restarts from beginning |
| No rotation handling | Does not follow rotated logs |

---

## Confluent SpoolDir Connector

For production use, the SpoolDir connector provides advanced file handling:

```bash
confluent-hub install jcustenborder/kafka-connect-spooldir:latest
```

### Basic Configuration

```json
{
  "name": "spooldir-source",
  "config": {
    "connector.class": "com.github.jcustenborder.kafka.connect.spooldir.SpoolDirCsvSourceConnector",
    "tasks.max": "1",

    "input.path": "/data/incoming",
    "finished.path": "/data/processed",
    "error.path": "/data/error",

    "topic": "file-data",
    "input.file.pattern": ".*\\.csv$"
  }
}
```

---

## SpoolDir File Formats

### CSV Files

```json
{
  "connector.class": "com.github.jcustenborder.kafka.connect.spooldir.SpoolDirCsvSourceConnector",
  "csv.first.row.as.header": "true",
  "csv.separator.char": ",",
  "csv.quote.char": "\"",
  "schema.generation.enabled": "true"
}
```

### JSON Files

```json
{
  "connector.class": "com.github.jcustenborder.kafka.connect.spooldir.SpoolDirJsonSourceConnector",
  "schema.generation.enabled": "true"
}
```

### Line-Delimited Files

```json
{
  "connector.class": "com.github.jcustenborder.kafka.connect.spooldir.SpoolDirLineDelimitedSourceConnector"
}
```

### Binary Files

```json
{
  "connector.class": "com.github.jcustenborder.kafka.connect.spooldir.SpoolDirBinaryFileSourceConnector"
}
```

---

## Directory Configuration

### Input Processing

```json
{
  "input.path": "/data/incoming",
  "input.file.pattern": ".*\\.csv$",
  "file.minimum.age.ms": "5000"
}
```

| Property | Description | Default |
|----------|-------------|:-------:|
| `input.path` | Directory to watch | Required |
| `input.file.pattern` | Regex for file matching | `.*` |
| `file.minimum.age.ms` | Min file age before processing | 0 |

### File Lifecycle

```json
{
  "finished.path": "/data/processed",
  "error.path": "/data/error",
  "cleanup.policy": "MOVE"
}
```

| Policy | Description |
|--------|-------------|
| `MOVE` | Move to finished/error path |
| `DELETE` | Delete after processing |
| `NONE` | Leave in place |

---

## Schema Configuration

### Schema Generation

```json
{
  "schema.generation.enabled": "true",
  "schema.generation.key.fields": "id"
}
```

### Predefined Schema

```json
{
  "schema.generation.enabled": "false",
  "key.schema": "{\"name\":\"key\",\"type\":\"STRING\"}",
  "value.schema": "{\"name\":\"event\",\"type\":\"STRUCT\",\"fields\":[{\"name\":\"id\",\"type\":\"STRING\"},{\"name\":\"timestamp\",\"type\":\"INT64\"},{\"name\":\"data\",\"type\":\"STRING\"}]}"
}
```

---

## Batch Processing

```json
{
  "batch.size": "1000",
  "empty.poll.wait.ms": "500"
}
```

| Property | Description | Default |
|----------|-------------|:-------:|
| `batch.size` | Records per batch | 1000 |
| `empty.poll.wait.ms` | Wait when no files | 500 |

---

## Error Handling

### File Errors

```json
{
  "error.path": "/data/error",
  "halt.on.error": "false"
}
```

### Record Errors

```json
{
  "errors.tolerance": "all",
  "errors.deadletterqueue.topic.name": "dlq-file-source",
  "errors.deadletterqueue.topic.replication.factor": 3,
  "errors.log.enable": "true"
}
```

---

## Complete CSV Example

```json
{
  "name": "csv-file-source",
  "config": {
    "connector.class": "com.github.jcustenborder.kafka.connect.spooldir.SpoolDirCsvSourceConnector",
    "tasks.max": "1",

    "input.path": "/data/incoming/csv",
    "finished.path": "/data/processed/csv",
    "error.path": "/data/error/csv",
    "input.file.pattern": ".*\\.csv$",
    "file.minimum.age.ms": "10000",

    "topic": "csv-events",

    "csv.first.row.as.header": "true",
    "csv.separator.char": ",",
    "csv.quote.char": "\"",
    "csv.escape.char": "\\",
    "csv.null.field.indicator": "NULL",

    "schema.generation.enabled": "true",
    "schema.generation.key.fields": "id",

    "batch.size": "1000",
    "cleanup.policy": "MOVE",

    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",

    "errors.tolerance": "all",
    "errors.deadletterqueue.topic.name": "dlq-csv-source",
    "errors.deadletterqueue.topic.replication.factor": 3
  }
}
```

---

## Complete JSON Lines Example

```json
{
  "name": "jsonl-file-source",
  "config": {
    "connector.class": "com.github.jcustenborder.kafka.connect.spooldir.SpoolDirJsonSourceConnector",
    "tasks.max": "1",

    "input.path": "/data/incoming/json",
    "finished.path": "/data/processed/json",
    "error.path": "/data/error/json",
    "input.file.pattern": ".*\\.jsonl$",

    "topic": "json-events",

    "schema.generation.enabled": "true",

    "batch.size": "500",
    "cleanup.policy": "MOVE",

    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false"
  }
}
```

---

## Log File Streaming

For streaming log files (append-only), consider the FilePulse connector:

```bash
confluent-hub install streamthoughts/kafka-connect-file-pulse:latest
```

```json
{
  "name": "log-file-source",
  "config": {
    "connector.class": "io.streamthoughts.kafka.connect.filepulse.source.FilePulseSourceConnector",
    "tasks.max": "1",

    "fs.listing.class": "io.streamthoughts.kafka.connect.filepulse.fs.LocalFSDirectoryListing",
    "fs.listing.directory.path": "/var/log/app",
    "fs.listing.filters": "io.streamthoughts.kafka.connect.filepulse.fs.filter.RegexFileListFilter",
    "file.filter.regex.pattern": ".*\\.log$",

    "fs.cleanup.policy.class": "io.streamthoughts.kafka.connect.filepulse.fs.clean.LogCleanupPolicy",

    "topic": "application-logs",

    "tasks.reader.class": "io.streamthoughts.kafka.connect.filepulse.fs.reader.LocalRowFileInputReader",
    "offset.strategy": "name+hash"
  }
}
```

---

## Performance Tuning

### Parallelism

```json
{
  "tasks.max": "3",
  "tasks.file.status.storage.class": "io.streamthoughts.kafka.connect.filepulse.state.InMemoryFileObjectStateBackingStore"
}
```

### Batch Size

```json
{
  "batch.size": "5000",
  "poll.interval.ms": "1000"
}
```

---

## Monitoring

### Connector Status

```bash
curl http://connect:8083/connectors/file-source/status
```

### File Processing Status

```bash
# Check input directory
ls -la /data/incoming/

# Check processed files
ls -la /data/processed/

# Check error files
ls -la /data/error/
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Files not processed | Pattern mismatch | Verify `input.file.pattern` |
| Permission denied | File permissions | Check connector user access |
| Schema errors | Inconsistent data | Enable schema generation |
| Files in error path | Parsing failures | Check file format |
| High memory usage | Large batch size | Reduce `batch.size` |

---

## Related Documentation

- [Connectors Overview](index.md) - All connectors
- [Kafka Connect](../index.md) - Connect framework
- [Error Handling](../error-handling.md) - DLQ configuration
