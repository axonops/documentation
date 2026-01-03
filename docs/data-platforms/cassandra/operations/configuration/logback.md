---
title: "Cassandra Logging Configuration (logback.xml)"
description: "Cassandra logback.xml configuration guide. Configure log levels, appenders, rotation policies, and output formats for system.log, debug.log, and audit logs."
meta:
  - name: keywords
    content: "Cassandra logback, logging configuration, log levels"
---

# Cassandra Logging Configuration (logback.xml)

Cassandra uses Logback for logging, configured via `logback.xml`. This file controls log levels, output destinations, formats, and rotation policies.

## Configuration File

| File | Location |
|------|----------|
| `logback.xml` | `/etc/cassandra/` |

Changes to `logback.xml` are detected automatically within 60 seconds—no restart required.

---

## Log Files

Cassandra produces several log files by default:

| Log File | Purpose | Default Location |
|----------|---------|------------------|
| `system.log` | Main operational log | `/var/log/cassandra/` |
| `debug.log` | Detailed debug output | `/var/log/cassandra/` |
| `gc.log` | Garbage collection (JVM-configured) | `/var/log/cassandra/` |

---

## Basic Structure

```xml
<configuration scan="true" scanPeriod="60 seconds">

  <!-- Appenders define where logs go -->
  <appender name="..." class="...">
    <!-- appender configuration -->
  </appender>

  <!-- Loggers define what gets logged -->
  <logger name="..." level="..."/>

  <!-- Root logger catches everything not matched by specific loggers -->
  <root level="INFO">
    <appender-ref ref="..."/>
  </root>

</configuration>
```

---

## Appenders

### Console Appender

Output to stdout (useful for containers):

```xml
<appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
  <encoder>
    <pattern>%-5level [%thread] %date{ISO8601} %F:%L - %msg%n</pattern>
  </encoder>
</appender>
```

### Rolling File Appender (system.log)

Standard file appender with rotation:

```xml
<appender name="SYSTEMLOG" class="ch.qos.logback.core.rolling.RollingFileAppender">
  <file>${cassandra.logdir}/system.log</file>
  <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
    <!-- Roll daily -->
    <fileNamePattern>${cassandra.logdir}/system.log.%d{yyyy-MM-dd}.%i.zip</fileNamePattern>
    <!-- Max 50MB per file -->
    <maxFileSize>50MB</maxFileSize>
    <!-- Keep 7 days of history -->
    <maxHistory>7</maxHistory>
    <!-- Cap total size at 5GB -->
    <totalSizeCap>5GB</totalSizeCap>
  </rollingPolicy>
  <encoder>
    <pattern>%-5level [%thread] %date{ISO8601} %F:%L - %msg%n</pattern>
  </encoder>
</appender>
```

### Debug Log Appender

Separate file for DEBUG level messages:

```xml
<appender name="DEBUGLOG" class="ch.qos.logback.core.rolling.RollingFileAppender">
  <file>${cassandra.logdir}/debug.log</file>
  <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
    <fileNamePattern>${cassandra.logdir}/debug.log.%d{yyyy-MM-dd}.%i.zip</fileNamePattern>
    <maxFileSize>50MB</maxFileSize>
    <maxHistory>7</maxHistory>
    <totalSizeCap>5GB</totalSizeCap>
  </rollingPolicy>
  <encoder>
    <pattern>%-5level [%thread] %date{ISO8601} %F:%L - %msg%n</pattern>
  </encoder>
</appender>
```

### Async Appender

Wrap appenders for non-blocking logging:

```xml
<appender name="ASYNCSYSTEMLOG" class="ch.qos.logback.classic.AsyncAppender">
  <queueSize>1024</queueSize>
  <discardingThreshold>0</discardingThreshold>
  <includeCallerData>true</includeCallerData>
  <appender-ref ref="SYSTEMLOG"/>
</appender>
```

---

## Log Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| `TRACE` | Most detailed | Deep debugging |
| `DEBUG` | Detailed information | Development, troubleshooting |
| `INFO` | Normal operations | Production default |
| `WARN` | Potential issues | Production monitoring |
| `ERROR` | Errors requiring attention | Always enabled |
| `OFF` | Disable logging | Specific loggers only |

---

## Logger Configuration

### Root Logger

Catches all log messages not matched by specific loggers:

```xml
<root level="INFO">
  <appender-ref ref="SYSTEMLOG"/>
  <appender-ref ref="STDOUT"/>
</root>
```

### Package-Specific Loggers

Control verbosity for specific components:

```xml
<!-- Reduce noisy components -->
<logger name="org.apache.cassandra.db.compaction" level="INFO"/>
<logger name="org.apache.cassandra.service.StorageService" level="INFO"/>

<!-- Increase verbosity for troubleshooting -->
<logger name="org.apache.cassandra.db.commitlog" level="DEBUG"/>
<logger name="org.apache.cassandra.streaming" level="DEBUG"/>
```

### Common Logger Configurations

| Logger | Level | Purpose |
|--------|-------|---------|
| `org.apache.cassandra` | INFO | All Cassandra components |
| `org.apache.cassandra.db.compaction` | INFO | Compaction operations |
| `org.apache.cassandra.db.commitlog` | INFO | Commit log operations |
| `org.apache.cassandra.streaming` | INFO | Streaming operations |
| `org.apache.cassandra.hints` | INFO | Hinted handoff |
| `org.apache.cassandra.repair` | INFO | Repair operations |
| `org.apache.cassandra.gms` | INFO | Gossip protocol |
| `org.apache.cassandra.net` | INFO | Internode messaging |
| `org.apache.cassandra.cql3` | INFO | CQL processing |
| `org.apache.cassandra.auth` | INFO | Authentication/authorization |

---

## Log Pattern Format

### Pattern Elements

| Element | Description | Example Output |
|---------|-------------|----------------|
| `%level` | Log level | `INFO` |
| `%-5level` | Log level, left-padded to 5 chars | `INFO ` |
| `%thread` | Thread name | `main` |
| `%date{ISO8601}` | ISO timestamp | `2024-01-15 10:30:45,123` |
| `%logger` | Logger name | `org.apache.cassandra.db.Memtable` |
| `%F` | Source file name | `Memtable.java` |
| `%L` | Line number | `234` |
| `%M` | Method name | `flush` |
| `%msg` | Log message | `Flushing memtable` |
| `%n` | Newline | |
| `%X{key}` | MDC value | Custom context |

### Standard Pattern

```xml
<pattern>%-5level [%thread] %date{ISO8601} %F:%L - %msg%n</pattern>
```

Output:
```
INFO  [main] 2024-01-15 10:30:45,123 StorageService.java:1234 - Starting listening for CQL clients
```

### JSON Pattern (for log aggregation)

```xml
<encoder class="ch.qos.logback.core.encoder.LayoutWrappingEncoder">
  <layout class="ch.qos.logback.contrib.json.classic.JsonLayout">
    <jsonFormatter class="ch.qos.logback.contrib.jackson.JacksonJsonFormatter"/>
    <timestampFormat>yyyy-MM-dd'T'HH:mm:ss.SSS'Z'</timestampFormat>
    <appendLineSeparator>true</appendLineSeparator>
  </layout>
</encoder>
```

---

## Rolling Policies

### Size and Time Based

Roll logs based on both size and time:

```xml
<rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
  <fileNamePattern>${cassandra.logdir}/system.log.%d{yyyy-MM-dd}.%i.zip</fileNamePattern>
  <maxFileSize>50MB</maxFileSize>
  <maxHistory>7</maxHistory>
  <totalSizeCap>5GB</totalSizeCap>
</rollingPolicy>
```

### Time Based Only

Roll logs daily without size limit:

```xml
<rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
  <fileNamePattern>${cassandra.logdir}/system.log.%d{yyyy-MM-dd}.zip</fileNamePattern>
  <maxHistory>30</maxHistory>
</rollingPolicy>
```

### Size Based Only

Roll logs based on size only:

```xml
<rollingPolicy class="ch.qos.logback.core.rolling.FixedWindowRollingPolicy">
  <fileNamePattern>${cassandra.logdir}/system.log.%i.zip</fileNamePattern>
  <minIndex>1</minIndex>
  <maxIndex>10</maxIndex>
</rollingPolicy>
<triggeringPolicy class="ch.qos.logback.core.rolling.SizeBasedTriggeringPolicy">
  <maxFileSize>100MB</maxFileSize>
</triggeringPolicy>
```

---

## Complete Examples

### Production Configuration

```xml
<configuration scan="true" scanPeriod="60 seconds">

  <!-- JMX configuration -->
  <jmxConfigurator/>

  <!-- System log -->
  <appender name="SYSTEMLOG" class="ch.qos.logback.core.rolling.RollingFileAppender">
    <file>${cassandra.logdir}/system.log</file>
    <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
      <fileNamePattern>${cassandra.logdir}/system.log.%d{yyyy-MM-dd}.%i.zip</fileNamePattern>
      <maxFileSize>50MB</maxFileSize>
      <maxHistory>7</maxHistory>
      <totalSizeCap>5GB</totalSizeCap>
    </rollingPolicy>
    <encoder>
      <pattern>%-5level [%thread] %date{ISO8601} %F:%L - %msg%n</pattern>
    </encoder>
  </appender>

  <!-- Debug log -->
  <appender name="DEBUGLOG" class="ch.qos.logback.core.rolling.RollingFileAppender">
    <file>${cassandra.logdir}/debug.log</file>
    <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
      <fileNamePattern>${cassandra.logdir}/debug.log.%d{yyyy-MM-dd}.%i.zip</fileNamePattern>
      <maxFileSize>50MB</maxFileSize>
      <maxHistory>7</maxHistory>
      <totalSizeCap>5GB</totalSizeCap>
    </rollingPolicy>
    <encoder>
      <pattern>%-5level [%thread] %date{ISO8601} %F:%L - %msg%n</pattern>
    </encoder>
    <!-- Only DEBUG level -->
    <filter class="ch.qos.logback.classic.filter.LevelFilter">
      <level>DEBUG</level>
      <onMatch>ACCEPT</onMatch>
      <onMismatch>DENY</onMismatch>
    </filter>
  </appender>

  <!-- Async wrappers -->
  <appender name="ASYNCSYSTEMLOG" class="ch.qos.logback.classic.AsyncAppender">
    <queueSize>1024</queueSize>
    <discardingThreshold>0</discardingThreshold>
    <includeCallerData>true</includeCallerData>
    <appender-ref ref="SYSTEMLOG"/>
  </appender>

  <appender name="ASYNCDEBUGLOG" class="ch.qos.logback.classic.AsyncAppender">
    <queueSize>1024</queueSize>
    <discardingThreshold>0</discardingThreshold>
    <includeCallerData>true</includeCallerData>
    <appender-ref ref="DEBUGLOG"/>
  </appender>

  <!-- Reduce noisy loggers -->
  <logger name="org.apache.cassandra.db.compaction.CompactionTask" level="INFO"/>
  <logger name="org.apache.cassandra.service.StorageProxy" level="INFO"/>

  <!-- Root logger -->
  <root level="INFO">
    <appender-ref ref="ASYNCSYSTEMLOG"/>
    <appender-ref ref="ASYNCDEBUGLOG"/>
  </root>

</configuration>
```

### Container/Kubernetes Configuration

```xml
<configuration scan="true" scanPeriod="60 seconds">

  <!-- Console output for container logs -->
  <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
    <encoder>
      <pattern>%-5level [%thread] %date{ISO8601} %logger{36} - %msg%n</pattern>
    </encoder>
  </appender>

  <!-- Async wrapper -->
  <appender name="ASYNCSTDOUT" class="ch.qos.logback.classic.AsyncAppender">
    <queueSize>1024</queueSize>
    <discardingThreshold>0</discardingThreshold>
    <appender-ref ref="STDOUT"/>
  </appender>

  <!-- Reduce verbosity -->
  <logger name="org.apache.cassandra.db.compaction" level="WARN"/>
  <logger name="org.apache.cassandra.gms.Gossiper" level="WARN"/>

  <root level="INFO">
    <appender-ref ref="ASYNCSTDOUT"/>
  </root>

</configuration>
```

### Debug/Troubleshooting Configuration

```xml
<configuration scan="true" scanPeriod="60 seconds">

  <appender name="SYSTEMLOG" class="ch.qos.logback.core.rolling.RollingFileAppender">
    <file>${cassandra.logdir}/system.log</file>
    <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
      <fileNamePattern>${cassandra.logdir}/system.log.%d{yyyy-MM-dd}.%i.zip</fileNamePattern>
      <maxFileSize>100MB</maxFileSize>
      <maxHistory>3</maxHistory>
      <totalSizeCap>10GB</totalSizeCap>
    </rollingPolicy>
    <encoder>
      <pattern>%-5level [%thread] %date{ISO8601} %logger{36}:%L - %msg%n</pattern>
    </encoder>
  </appender>

  <!-- Enable debug for specific subsystems -->
  <logger name="org.apache.cassandra.db.compaction" level="DEBUG"/>
  <logger name="org.apache.cassandra.streaming" level="DEBUG"/>
  <logger name="org.apache.cassandra.repair" level="DEBUG"/>
  <logger name="org.apache.cassandra.hints" level="DEBUG"/>
  <logger name="org.apache.cassandra.net" level="DEBUG"/>
  <logger name="org.apache.cassandra.gms" level="DEBUG"/>

  <root level="DEBUG">
    <appender-ref ref="SYSTEMLOG"/>
  </root>

</configuration>
```

---

## Runtime Log Level Changes

Modify log levels without restart using `nodetool`:

```bash
# View current levels
nodetool getlogginglevels

# Set level for specific logger
nodetool setlogginglevel org.apache.cassandra.db.compaction DEBUG

# Reset to configuration file settings
nodetool setlogginglevel org.apache.cassandra.db.compaction RESET
```

!!! note "Runtime vs Persistent Changes"
    Changes via `nodetool` are temporary and reset on restart. For persistent changes, modify `logback.xml`.

---

## Audit Logging

Cassandra 4.0+ includes built-in audit logging:

```xml
<!-- Audit log appender -->
<appender name="AUDIT" class="ch.qos.logback.core.rolling.RollingFileAppender">
  <file>${cassandra.logdir}/audit/audit.log</file>
  <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
    <fileNamePattern>${cassandra.logdir}/audit/audit.log.%d{yyyy-MM-dd}.%i.zip</fileNamePattern>
    <maxFileSize>50MB</maxFileSize>
    <maxHistory>30</maxHistory>
    <totalSizeCap>10GB</totalSizeCap>
  </rollingPolicy>
  <encoder>
    <pattern>%-5level [%thread] %date{ISO8601} - %msg%n</pattern>
  </encoder>
</appender>

<logger name="org.apache.cassandra.audit" level="INFO" additivity="false">
  <appender-ref ref="AUDIT"/>
</logger>
```

Enable in `cassandra.yaml`:

```yaml
audit_logging_options:
  enabled: true
  logger:
    - class_name: BinAuditLogger
  included_keyspaces: my_keyspace
  included_categories: QUERY,DML,DDL,AUTH
```

---

## Full Query Logging

Log all CQL queries for debugging:

```bash
# Enable via nodetool
nodetool enablefullquerylog --path /var/log/cassandra/fql

# Disable
nodetool disablefullquerylog

# Read logs
fqltool dump /var/log/cassandra/fql
```

---

## Slow Query Logging

Log queries exceeding threshold:

```yaml
# cassandra.yaml
slow_query_log_timeout_in_ms: 500
```

Slow queries appear in system.log at WARN level.

---

## Troubleshooting

### Log File Not Created

1. Check directory permissions:
   ```bash
   ls -la /var/log/cassandra/
   ```

2. Verify `cassandra.logdir` property:
   ```bash
   grep logdir /etc/cassandra/cassandra-env.sh
   ```

3. Check for XML syntax errors:
   ```bash
   xmllint --noout /etc/cassandra/logback.xml
   ```

### Disk Space Issues

Configure aggressive rotation:

```xml
<maxFileSize>25MB</maxFileSize>
<maxHistory>3</maxHistory>
<totalSizeCap>1GB</totalSizeCap>
```

### Performance Impact

Use async appenders to minimize logging overhead:

```xml
<appender name="ASYNC" class="ch.qos.logback.classic.AsyncAppender">
  <queueSize>1024</queueSize>
  <discardingThreshold>0</discardingThreshold>
  <neverBlock>true</neverBlock>
  <appender-ref ref="SYSTEMLOG"/>
</appender>
```

### Missing Stack Traces

Ensure `includeCallerData` is enabled for async appenders:

```xml
<appender name="ASYNC" class="ch.qos.logback.classic.AsyncAppender">
  <includeCallerData>true</includeCallerData>
  <appender-ref ref="SYSTEMLOG"/>
</appender>
```

---

## Best Practices

| Practice | Recommendation |
|----------|----------------|
| Production log level | INFO for root, WARN for noisy components |
| Async appenders | Always use for production |
| Rotation | Size + time based with totalSizeCap |
| Debug logs | Separate file, enable only when needed |
| Container deployments | Console output, let orchestrator handle rotation |
| Disk monitoring | Alert when log partition exceeds 80% |
| Retention | 7-30 days depending on compliance requirements |

---

## Related Documentation

- **[cassandra.yaml](cassandra-yaml/index.md)** - Main configuration
- **[JVM Options](jvm-options/index.md)** - GC logging configuration
- **[Monitoring](../monitoring/index.md)** - Log aggregation and alerting
