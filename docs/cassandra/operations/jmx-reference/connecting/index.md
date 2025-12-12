# Connecting to Cassandra JMX

Access Cassandra metrics and operations via JMX.

## Local Connection

### nodetool (Recommended)

```bash
# Default local connection
nodetool status

# Specify host and port
nodetool -h 127.0.0.1 -p 7199 status
```

### JConsole

```bash
# Connect locally
jconsole

# Select local Cassandra process from list
```

### VisualVM

```bash
# Launch VisualVM
visualvm

# Add local application
# Or connect via JMX: service:jmx:rmi:///jndi/rmi://localhost:7199/jmxrmi
```

## Remote Connection

### Enable Remote JMX

```bash
# /etc/cassandra/cassandra-env.sh

# Enable remote JMX
JVM_OPTS="$JVM_OPTS -Dcom.sun.management.jmxremote"
JVM_OPTS="$JVM_OPTS -Dcom.sun.management.jmxremote.port=7199"
JVM_OPTS="$JVM_OPTS -Dcom.sun.management.jmxremote.rmi.port=7199"
JVM_OPTS="$JVM_OPTS -Djava.rmi.server.hostname=<node_ip>"

# Without authentication (NOT for production)
JVM_OPTS="$JVM_OPTS -Dcom.sun.management.jmxremote.authenticate=false"
JVM_OPTS="$JVM_OPTS -Dcom.sun.management.jmxremote.ssl=false"
```

### Connect Remotely

```bash
# nodetool
nodetool -h 192.168.1.10 -p 7199 status

# JConsole
jconsole 192.168.1.10:7199
```

## Secure JMX Connection

### Enable Authentication

```bash
# /etc/cassandra/cassandra-env.sh
JVM_OPTS="$JVM_OPTS -Dcom.sun.management.jmxremote.authenticate=true"
JVM_OPTS="$JVM_OPTS -Dcom.sun.management.jmxremote.password.file=/etc/cassandra/jmxremote.password"
JVM_OPTS="$JVM_OPTS -Dcom.sun.management.jmxremote.access.file=/etc/cassandra/jmxremote.access"
```

### Create Password File

```bash
# /etc/cassandra/jmxremote.password
cassandra cassandra_password
readonly readonly_password
```

### Create Access File

```bash
# /etc/cassandra/jmxremote.access
cassandra readwrite
readonly readonly
```

### Set Permissions

```bash
chmod 400 /etc/cassandra/jmxremote.password
chmod 400 /etc/cassandra/jmxremote.access
chown cassandra:cassandra /etc/cassandra/jmxremote.*
```

### Connect with Authentication

```bash
nodetool -h 192.168.1.10 -p 7199 -u cassandra -pw cassandra_password status
```

## SSL/TLS for JMX

### Generate Keystore

```bash
keytool -genkeypair -alias jmx-server \
    -keyalg RSA -keysize 2048 \
    -validity 365 \
    -keystore /etc/cassandra/jmx-keystore.jks \
    -storepass keystorepass
```

### Enable SSL

```bash
# /etc/cassandra/cassandra-env.sh
JVM_OPTS="$JVM_OPTS -Dcom.sun.management.jmxremote.ssl=true"
JVM_OPTS="$JVM_OPTS -Dcom.sun.management.jmxremote.ssl.need.client.auth=true"
JVM_OPTS="$JVM_OPTS -Djavax.net.ssl.keyStore=/etc/cassandra/jmx-keystore.jks"
JVM_OPTS="$JVM_OPTS -Djavax.net.ssl.keyStorePassword=keystorepass"
JVM_OPTS="$JVM_OPTS -Djavax.net.ssl.trustStore=/etc/cassandra/jmx-truststore.jks"
JVM_OPTS="$JVM_OPTS -Djavax.net.ssl.trustStorePassword=truststorepass"
```

## Programmatic Access

### Java Client

```java
import javax.management.*;
import javax.management.remote.*;
import java.util.*;

public class CassandraJMX {
    public static void main(String[] args) throws Exception {
        String host = "localhost";
        int port = 7199;

        JMXServiceURL url = new JMXServiceURL(
            "service:jmx:rmi:///jndi/rmi://" + host + ":" + port + "/jmxrmi"
        );

        // With authentication
        Map<String, Object> env = new HashMap<>();
        env.put(JMXConnector.CREDENTIALS, new String[]{"cassandra", "password"});

        JMXConnector connector = JMXConnectorFactory.connect(url, env);
        MBeanServerConnection mbs = connector.getMBeanServerConnection();

        // Access StorageService
        ObjectName storageService = new ObjectName(
            "org.apache.cassandra.db:type=StorageService"
        );

        String clusterName = (String) mbs.getAttribute(storageService, "ClusterName");
        System.out.println("Cluster: " + clusterName);

        connector.close();
    }
}
```

### Python Client

```python
from jmxquery import JMXConnection, JMXQuery

# Connect
jmx = JMXConnection("service:jmx:rmi:///jndi/rmi://localhost:7199/jmxrmi")

# Query metrics
metrics = jmx.query([
    JMXQuery(mBeanName="org.apache.cassandra.metrics:type=Client,name=connectedNativeClients",
             attribute="Value")
])

for metric in metrics:
    print(f"{metric.attribute}: {metric.value}")
```

## JMX URLs

### Service URL Format

```
service:jmx:rmi:///jndi/rmi://<host>:<port>/jmxrmi
```

### Common Ports

| Port | Purpose |
|------|---------|
| 7199 | Default JMX port |
| 7200 | Alternative if 7199 in use |

## Troubleshooting

### Connection Refused

```bash
# Check JMX is enabled
ps aux | grep cassandra | grep jmxremote

# Check port is listening
netstat -tlnp | grep 7199
ss -tlnp | grep 7199
```

### Authentication Failed

```bash
# Check password file permissions
ls -la /etc/cassandra/jmxremote.*

# Should be 400 owned by cassandra user
```

### SSL Handshake Error

```bash
# Verify keystore
keytool -list -keystore /etc/cassandra/jmx-keystore.jks

# Test connection with debug
java -Djavax.net.debug=ssl -jar jmxterm.jar
```

---

## Next Steps

- **[JMX MBeans](../mbeans/index.md)** - MBean reference
- **[JMX Metrics](../metrics/index.md)** - Metrics guide
- **[Monitoring](../../monitoring/index.md)** - Monitoring setup
