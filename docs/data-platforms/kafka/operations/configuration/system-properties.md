---
title: "Kafka System Properties"
description: "Apache Kafka JVM system properties and environment variables. Runtime configuration for JVM, logging, security, and debugging."
meta:
  - name: keywords
    content: "Kafka system properties, JVM settings, environment variables, Kafka startup"
---

# System Properties

System properties are JVM-level settings that configure Kafka's runtime behavior. These are set via command-line arguments (`-D`) or environment variables.

---

## Setting System Properties

### Command Line

```bash
# In kafka-server-start.sh or as KAFKA_OPTS
export KAFKA_OPTS="-Djava.security.auth.login.config=/etc/kafka/jaas.conf"

# Or directly
java -Djava.security.auth.login.config=/etc/kafka/jaas.conf \
     -jar kafka.jar
```

### Environment Variables

```bash
# JVM heap settings
export KAFKA_HEAP_OPTS="-Xms6g -Xmx6g"

# JVM options
export KAFKA_JVM_PERFORMANCE_OPTS="-XX:+UseG1GC -XX:MaxGCPauseMillis=20"

# Additional JVM options
export KAFKA_OPTS="-Djavax.net.debug=ssl"

# GC logging
export KAFKA_GC_LOG_OPTS="-Xlog:gc*:file=/var/log/kafka/gc.log:time,level,tags"

# JMX settings
export KAFKA_JMX_OPTS="-Dcom.sun.management.jmxremote=true"
export JMX_PORT=9999
```

### Configuration Files

**jvm.options:**
```
# Heap
-Xms6g
-Xmx6g

# GC
-XX:+UseG1GC
-XX:MaxGCPauseMillis=20
-XX:InitiatingHeapOccupancyPercent=35

# GC logging (JDK 11+)
-Xlog:gc*:file=/var/log/kafka/gc.log:time,level,tags:filecount=10,filesize=100M
```

---

## Security Properties

### JAAS Configuration

```bash
# Point to JAAS configuration file
-Djava.security.auth.login.config=/etc/kafka/jaas.conf
```

**jaas.conf example:**
```
KafkaServer {
    org.apache.kafka.common.security.scram.ScramLoginModule required
    username="admin"
    password="admin-secret";
};

KafkaClient {
    org.apache.kafka.common.security.scram.ScramLoginModule required
    username="client"
    password="client-secret";
};
```

### Kerberos Properties

```bash
# Kerberos realm and KDC
-Djava.security.krb5.realm=EXAMPLE.COM
-Djava.security.krb5.kdc=kdc.example.com

# Or use krb5.conf
-Djava.security.krb5.conf=/etc/krb5.conf

# Debug Kerberos
-Dsun.security.krb5.debug=true
```

### SSL/TLS Properties

```bash
# Trust store (system-wide)
-Djavax.net.ssl.trustStore=/etc/kafka/ssl/truststore.jks
-Djavax.net.ssl.trustStorePassword=password

# Key store (system-wide)
-Djavax.net.ssl.keyStore=/etc/kafka/ssl/keystore.jks
-Djavax.net.ssl.keyStorePassword=password

# SSL debugging
-Djavax.net.debug=ssl
-Djavax.net.debug=ssl:handshake
-Djavax.net.debug=all
```

### Security Manager (Deprecated in JDK 17+)

```bash
# Enable security manager
-Djava.security.manager
-Djava.security.policy=/etc/kafka/security.policy
```

---

## Logging Properties

### Log4j Configuration

```bash
# Log4j 1.x configuration file
-Dlog4j.configuration=file:/etc/kafka/log4j.properties

# Log4j 2.x configuration file
-Dlog4j.configurationFile=/etc/kafka/log4j2.properties

# Log4j debug mode
-Dlog4j.debug=true
```

### Kafka Logging

```bash
# Kafka logs directory
-Dkafka.logs.dir=/var/log/kafka

# Disable console appender
-Dkafka.console.logger.level=OFF
```

**log4j.properties example:**
```properties
log4j.rootLogger=INFO, stdout, kafkaAppender

log4j.appender.stdout=org.apache.log4j.ConsoleAppender
log4j.appender.stdout.layout=org.apache.log4j.PatternLayout
log4j.appender.stdout.layout.ConversionPattern=[%d] %p %m (%c)%n

log4j.appender.kafkaAppender=org.apache.log4j.RollingFileAppender
log4j.appender.kafkaAppender.File=${kafka.logs.dir}/server.log
log4j.appender.kafkaAppender.MaxFileSize=100MB
log4j.appender.kafkaAppender.MaxBackupIndex=10
log4j.appender.kafkaAppender.layout=org.apache.log4j.PatternLayout
log4j.appender.kafkaAppender.layout.ConversionPattern=[%d] %p %m (%c)%n

# Request logging
log4j.logger.kafka.request.logger=WARN
log4j.logger.kafka.network.RequestChannel$=WARN

# Controller logging
log4j.logger.kafka.controller=TRACE
log4j.logger.state.change.logger=TRACE
```

---

## JVM Memory Properties

### Heap Configuration

```bash
# Initial and maximum heap size
-Xms6g
-Xmx6g

# Young generation size (if not using G1GC)
-Xmn2g

# Metaspace
-XX:MetaspaceSize=256m
-XX:MaxMetaspaceSize=256m
```

### Direct Memory

```bash
# Maximum direct memory
-XX:MaxDirectMemorySize=2g
```

### Memory-Related System Properties

```bash
# Disable explicit GC (System.gc() calls)
-XX:+DisableExplicitGC

# Use large pages (requires OS configuration)
-XX:+UseLargePages
```

---

## Garbage Collection Properties

### G1GC (Recommended)

```bash
-XX:+UseG1GC
-XX:MaxGCPauseMillis=20
-XX:InitiatingHeapOccupancyPercent=35
-XX:G1HeapRegionSize=16m
-XX:G1ReservePercent=15
-XX:G1NewSizePercent=5
-XX:G1MaxNewSizePercent=40
```

### ZGC (JDK 15+, Low Latency)

```bash
-XX:+UseZGC
-XX:+ZGenerational  # JDK 21+
```

### GC Logging (JDK 11+)

```bash
-Xlog:gc*:file=/var/log/kafka/gc.log:time,level,tags:filecount=10,filesize=100M
-Xlog:gc+heap=debug:file=/var/log/kafka/gc-heap.log
-Xlog:safepoint:file=/var/log/kafka/safepoint.log
```

### GC Logging (JDK 8)

```bash
-Xloggc:/var/log/kafka/gc.log
-XX:+PrintGCDetails
-XX:+PrintGCDateStamps
-XX:+PrintGCTimeStamps
-XX:+UseGCLogFileRotation
-XX:NumberOfGCLogFiles=10
-XX:GCLogFileSize=100M
```

---

## JMX Properties

### Enabling JMX

```bash
# Enable JMX remote access
-Dcom.sun.management.jmxremote=true
-Dcom.sun.management.jmxremote.port=9999
-Dcom.sun.management.jmxremote.rmi.port=9999
-Dcom.sun.management.jmxremote.local.only=false

# Without authentication (development only)
-Dcom.sun.management.jmxremote.authenticate=false
-Dcom.sun.management.jmxremote.ssl=false

# With authentication
-Dcom.sun.management.jmxremote.authenticate=true
-Dcom.sun.management.jmxremote.password.file=/etc/kafka/jmxremote.password
-Dcom.sun.management.jmxremote.access.file=/etc/kafka/jmxremote.access
```

### JMX with SSL

```bash
-Dcom.sun.management.jmxremote.ssl=true
-Dcom.sun.management.jmxremote.ssl.need.client.auth=true
-Djavax.net.ssl.keyStore=/etc/kafka/ssl/jmx-keystore.jks
-Djavax.net.ssl.keyStorePassword=password
-Djavax.net.ssl.trustStore=/etc/kafka/ssl/jmx-truststore.jks
-Djavax.net.ssl.trustStorePassword=password
```

### Hostname Binding

```bash
# Bind JMX to specific hostname
-Djava.rmi.server.hostname=broker1.example.com

# For Docker/Kubernetes
-Djava.rmi.server.hostname=${HOSTNAME}
```

---

## Network Properties

### DNS and Hostname

```bash
# DNS cache TTL
-Dsun.net.inetaddr.ttl=30
-Dsun.net.inetaddr.negative.ttl=10

# Prefer IPv4
-Djava.net.preferIPv4Stack=true
```

### TCP Settings

```bash
# TCP keepalive (platform-dependent)
-Dsun.net.client.defaultConnectTimeout=30000
-Dsun.net.client.defaultReadTimeout=30000
```

---

## Debugging Properties

### General Debugging

```bash
# Enable assertions
-ea

# Remote debugging
-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:5005
```

### Kafka-Specific Debugging

```bash
# Log request processing
-Dkafka.request.logger=DEBUG

# Log controller state changes
-Dstate.change.logger=TRACE

# Network request/response logging
-Dkafka.network.RequestChannel.debug=true
```

### SSL Debugging

```bash
# All SSL debugging
-Djavax.net.debug=all

# Handshake only
-Djavax.net.debug=ssl:handshake

# Certificate chain
-Djavax.net.debug=ssl:handshake:verbose

# Record-level debugging
-Djavax.net.debug=ssl:record
```

---

## File System Properties

### Paths

```bash
# Temporary directory
-Djava.io.tmpdir=/var/kafka/tmp

# User directory
-Duser.dir=/opt/kafka
```

### File Encoding

```bash
# Character encoding
-Dfile.encoding=UTF-8

# Standard streams encoding
-Dstdout.encoding=UTF-8
-Dstderr.encoding=UTF-8
```

---

## Environment Variables Reference

### Kafka Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `KAFKA_HEAP_OPTS` | JVM heap settings | `-Xmx1G -Xms1G` |
| `KAFKA_JVM_PERFORMANCE_OPTS` | GC and performance settings | (varies) |
| `KAFKA_GC_LOG_OPTS` | GC logging settings | (varies) |
| `KAFKA_JMX_OPTS` | JMX settings | (varies) |
| `KAFKA_OPTS` | Additional JVM options | (none) |
| `KAFKA_LOG4J_OPTS` | Log4j settings | (varies) |
| `JMX_PORT` | JMX port | (none) |
| `KAFKA_DEBUG` | Enable debug mode | (none) |

### Producer/Consumer Environment Variables

| Variable | Description |
|----------|-------------|
| `KAFKA_PRODUCER_OPTS` | Additional producer JVM options |
| `KAFKA_CONSUMER_OPTS` | Additional consumer JVM options |

---

## Production Recommendations

### Broker JVM Options

```bash
export KAFKA_HEAP_OPTS="-Xms6g -Xmx6g"

export KAFKA_JVM_PERFORMANCE_OPTS="
  -XX:+UseG1GC
  -XX:MaxGCPauseMillis=20
  -XX:InitiatingHeapOccupancyPercent=35
  -XX:+ExplicitGCInvokesConcurrent
  -XX:+ParallelRefProcEnabled
  -XX:+UseStringDeduplication
  -XX:+PerfDisableSharedMem
  -Djava.awt.headless=true
"

export KAFKA_GC_LOG_OPTS="
  -Xlog:gc*:file=/var/log/kafka/gc.log:time,level,tags:filecount=10,filesize=100M
"

export KAFKA_JMX_OPTS="
  -Dcom.sun.management.jmxremote=true
  -Dcom.sun.management.jmxremote.authenticate=false
  -Dcom.sun.management.jmxremote.ssl=false
  -Dcom.sun.management.jmxremote.port=9999
  -Djava.rmi.server.hostname=${HOSTNAME}
"
```

### Security Checklist

| Property | Production Setting |
|----------|-------------------|
| JMX authentication | Enabled |
| JMX SSL | Enabled |
| SSL debugging | Disabled |
| Remote debugging | Disabled |
| Assertions | Disabled |

---

## Related Documentation

- [Configuration Overview](index.md) - Configuration guide
- [Broker Configuration](broker.md) - Broker settings
- [Configuration Providers](configuration-providers.md) - External configuration
- [Performance](../performance/index.md) - Performance tuning
- [Monitoring](../monitoring/index.md) - Metrics and monitoring