# Cassandra Logging Configuration

Configure and analyze Cassandra logs for monitoring and troubleshooting.

## Log Files

| Log File | Purpose | Location |
|----------|---------|----------|
| `system.log` | Main application log | `/var/log/cassandra/` |
| `debug.log` | Detailed debug information | `/var/log/cassandra/` |
| `gc.log` | Garbage collection | `/var/log/cassandra/` |
| `audit.log` | Security audit (if enabled) | `/var/log/cassandra/` |

## Logback Configuration

### Location

```
/etc/cassandra/logback.xml
```

### Basic Configuration

```xml
<configuration scan="true" scanPeriod="60 seconds">
  <jmxConfigurator />

  <!-- Console appender -->
  <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
    <encoder>
      <pattern>%-5level [%thread] %date{ISO8601} %F:%L - %msg%n</pattern>
    </encoder>
  </appender>

  <!-- System log -->
  <appender name="SYSTEMLOG" class="ch.qos.logback.core.rolling.RollingFileAppender">
    <file>${cassandra.logdir}/system.log</file>
    <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
      <fileNamePattern>${cassandra.logdir}/system.log.%d{yyyy-MM-dd}.%i.zip</fileNamePattern>
      <maxFileSize>50MB</maxFileSize>
      <maxHistory>7</maxHistory>
      <totalSizeCap>500MB</totalSizeCap>
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
      <totalSizeCap>500MB</totalSizeCap>
    </rollingPolicy>
    <encoder>
      <pattern>%-5level [%thread] %date{ISO8601} %F:%L - %msg%n</pattern>
    </encoder>
  </appender>

  <!-- Root logger -->
  <root level="INFO">
    <appender-ref ref="SYSTEMLOG" />
    <appender-ref ref="STDOUT" />
  </root>

  <!-- Debug logger -->
  <logger name="org.apache.cassandra" level="DEBUG" additivity="false">
    <appender-ref ref="DEBUGLOG" />
  </logger>
</configuration>
```

## Dynamic Log Level Changes

```bash
# Get current levels
nodetool getlogginglevels

# Set log level (temporary)
nodetool setlogginglevel org.apache.cassandra DEBUG

# Set specific class
nodetool setlogginglevel org.apache.cassandra.db.compaction DEBUG

# Reset to INFO
nodetool setlogginglevel org.apache.cassandra INFO
```

## Important Log Messages

### Startup Messages

```
INFO  - Cassandra version: 4.1.3
INFO  - Starting up...
INFO  - Hostname: node1.example.com:7000
INFO  - JVM vendor/version: OpenJDK / 11.0.x
INFO  - Heap size: 8192/8192 MB
INFO  - Node /10.0.0.1 is now part of the cluster
```

### Warning Signs

```
# Tombstone warnings
WARN  - Read 5000 tombstones for query SELECT ...

# Large partition warnings
WARN  - Compacting large partition keyspace/table:key (150MB)

# GC warnings
WARN  - GC pause of 1500ms

# Dropped messages
WARN  - MUTATION messages were dropped in last 5000ms
```

## Log Analysis

### Common Searches

```bash
# Find errors
grep -i "error\|exception" /var/log/cassandra/system.log

# Find warnings
grep -i "warn" /var/log/cassandra/system.log | tail -100

# Compaction activity
grep -i "compaction" /var/log/cassandra/system.log

# GC pauses
grep -i "gc pause" /var/log/cassandra/gc.log

# Slow queries
grep -i "slow" /var/log/cassandra/system.log
```

---

## Next Steps

- **[Log Analysis](analysis.md)** - Detailed analysis
- **[Log Aggregation](aggregation.md)** - Centralized logging
- **[Alerting](../alerting/index.md)** - Alert configuration
