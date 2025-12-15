---
title: "Client TLS Configuration"
description: "Configure TLS in Cassandra clients. Driver SSL settings and truststore configuration."
meta:
  - name: keywords
    content: "client TLS, driver SSL, truststore, client encryption"
---

# Client TLS Configuration

This section covers TLS configuration for Cassandra clients including cqlsh, Java driver, Python driver, and other language drivers.

## cqlsh Configuration

### Command Line Options

```bash
# Basic SSL connection
cqlsh --ssl hostname

# With explicit CA certificate
cqlsh --ssl --ssl-certfile=/path/to/ca-cert.pem hostname

# With client certificate (mutual TLS)
cqlsh --ssl \
    --ssl-certfile=/path/to/ca-cert.pem \
    --ssl-keyfile=/path/to/client-key.pem \
    --ssl-usercert=/path/to/client-cert.pem \
    hostname
```

### cqlshrc Configuration

Create `~/.cassandra/cqlshrc`:

```ini
[connection]
hostname = cassandra-node-1.example.com
port = 9042

[ssl]
# Enable SSL
certfile = /path/to/ca-cert.pem

# Validate server certificate
validate = true

# Client certificate (for mutual TLS)
userkey = /path/to/client-key.pem
usercert = /path/to/client-cert.pem

# TLS version
version = TLSv1_2
```

### cqlshrc with Authentication

```ini
[authentication]
username = app_user
password = app_password

[connection]
hostname = cassandra-node-1.example.com
port = 9042

[ssl]
certfile = /path/to/ca-cert.pem
validate = true
```

### Environment Variables

```bash
# Set SSL certificate path
export SSL_CERTFILE=/path/to/ca-cert.pem

# Use with cqlsh
cqlsh --ssl hostname
```

---

## Java Driver Configuration

### DataStax Java Driver 4.x

#### Programmatic Configuration

```java
import com.datastax.oss.driver.api.core.CqlSession;
import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManagerFactory;
import java.io.FileInputStream;
import java.security.KeyStore;

public class CassandraClient {

    public static CqlSession createSecureSession() throws Exception {
        // Load truststore
        KeyStore trustStore = KeyStore.getInstance("JKS");
        trustStore.load(
            new FileInputStream("/path/to/truststore.jks"),
            "truststore_password".toCharArray()
        );

        TrustManagerFactory tmf = TrustManagerFactory
            .getInstance(TrustManagerFactory.getDefaultAlgorithm());
        tmf.init(trustStore);

        SSLContext sslContext = SSLContext.getInstance("TLS");
        sslContext.init(null, tmf.getTrustManagers(), null);

        return CqlSession.builder()
            .addContactPoint(new InetSocketAddress("cassandra-node-1.example.com", 9042))
            .withLocalDatacenter("dc1")
            .withSslContext(sslContext)
            .withAuthCredentials("username", "password")
            .build();
    }
}
```

#### Mutual TLS Configuration

```java
public static CqlSession createMtlsSession() throws Exception {
    // Load keystore (client certificate)
    KeyStore keyStore = KeyStore.getInstance("PKCS12");
    keyStore.load(
        new FileInputStream("/path/to/client-keystore.p12"),
        "keystore_password".toCharArray()
    );

    KeyManagerFactory kmf = KeyManagerFactory
        .getInstance(KeyManagerFactory.getDefaultAlgorithm());
    kmf.init(keyStore, "keystore_password".toCharArray());

    // Load truststore
    KeyStore trustStore = KeyStore.getInstance("JKS");
    trustStore.load(
        new FileInputStream("/path/to/truststore.jks"),
        "truststore_password".toCharArray()
    );

    TrustManagerFactory tmf = TrustManagerFactory
        .getInstance(TrustManagerFactory.getDefaultAlgorithm());
    tmf.init(trustStore);

    SSLContext sslContext = SSLContext.getInstance("TLS");
    sslContext.init(kmf.getKeyManagers(), tmf.getTrustManagers(), null);

    return CqlSession.builder()
        .addContactPoint(new InetSocketAddress("cassandra-node-1.example.com", 9042))
        .withLocalDatacenter("dc1")
        .withSslContext(sslContext)
        .build();
}
```

#### File-Based Configuration (application.conf)

```hocon
datastax-java-driver {
    basic {
        contact-points = ["cassandra-node-1.example.com:9042"]
        load-balancing-policy.local-datacenter = dc1
    }

    advanced.ssl-engine-factory {
        class = DefaultSslEngineFactory

        # Truststore for server certificate validation
        truststore-path = /path/to/truststore.jks
        truststore-password = truststore_password

        # Keystore for client certificate (mutual TLS)
        keystore-path = /path/to/client-keystore.p12
        keystore-password = keystore_password

        # Hostname verification
        hostname-validation = true

        # Cipher suites
        cipher-suites = [
            "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
            "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256"
        ]
    }

    advanced.auth-provider {
        class = PlainTextAuthProvider
        username = app_user
        password = app_password
    }
}
```

### DataStax Java Driver 3.x (Legacy)

```java
import com.datastax.driver.core.Cluster;
import com.datastax.driver.core.SSLOptions;
import com.datastax.driver.core.RemoteEndpointAwareJdkSSLOptions;

Cluster cluster = Cluster.builder()
    .addContactPoint("cassandra-node-1.example.com")
    .withSSL(RemoteEndpointAwareJdkSSLOptions.builder()
        .withSSLContext(sslContext)
        .build())
    .withCredentials("username", "password")
    .build();
```

---

## Python Driver Configuration

### Basic SSL Connection

```python
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from ssl import SSLContext, PROTOCOL_TLS_CLIENT, CERT_REQUIRED

# Create SSL context
ssl_context = SSLContext(PROTOCOL_TLS_CLIENT)
ssl_context.verify_mode = CERT_REQUIRED
ssl_context.load_verify_locations('/path/to/ca-cert.pem')

# Create auth provider
auth_provider = PlainTextAuthProvider(
    username='app_user',
    password='app_password'
)

# Connect with SSL
cluster = Cluster(
    ['cassandra-node-1.example.com'],
    port=9042,
    ssl_context=ssl_context,
    auth_provider=auth_provider
)

session = cluster.connect()
```

### Mutual TLS Configuration

```python
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from ssl import SSLContext, PROTOCOL_TLS_CLIENT, CERT_REQUIRED

# Create SSL context with client certificate
ssl_context = SSLContext(PROTOCOL_TLS_CLIENT)
ssl_context.verify_mode = CERT_REQUIRED
ssl_context.load_verify_locations('/path/to/ca-cert.pem')
ssl_context.load_cert_chain(
    certfile='/path/to/client-cert.pem',
    keyfile='/path/to/client-key.pem',
    password='key_password'  # If key is encrypted
)

cluster = Cluster(
    ['cassandra-node-1.example.com'],
    ssl_context=ssl_context,
    auth_provider=PlainTextAuthProvider('user', 'pass')
)
```

### Hostname Verification

```python
from ssl import SSLContext, PROTOCOL_TLS_CLIENT, CERT_REQUIRED
import ssl

ssl_context = SSLContext(PROTOCOL_TLS_CLIENT)
ssl_context.verify_mode = CERT_REQUIRED
ssl_context.check_hostname = True  # Enable hostname verification
ssl_context.load_verify_locations('/path/to/ca-cert.pem')
```

---

## Node.js Driver Configuration

### Basic SSL Connection

```javascript
const cassandra = require('cassandra-driver');
const fs = require('fs');

const client = new cassandra.Client({
    contactPoints: ['cassandra-node-1.example.com'],
    localDataCenter: 'dc1',
    sslOptions: {
        ca: [fs.readFileSync('/path/to/ca-cert.pem')],
        rejectUnauthorized: true
    },
    credentials: {
        username: 'app_user',
        password: 'app_password'
    }
});

client.connect()
    .then(() => console.log('Connected'))
    .catch(err => console.error('Connection error', err));
```

### Mutual TLS Configuration

```javascript
const cassandra = require('cassandra-driver');
const fs = require('fs');

const client = new cassandra.Client({
    contactPoints: ['cassandra-node-1.example.com'],
    localDataCenter: 'dc1',
    sslOptions: {
        ca: [fs.readFileSync('/path/to/ca-cert.pem')],
        cert: fs.readFileSync('/path/to/client-cert.pem'),
        key: fs.readFileSync('/path/to/client-key.pem'),
        rejectUnauthorized: true
    }
});
```

---

## Go Driver Configuration (gocql)

### Basic SSL Connection

```go
package main

import (
    "crypto/tls"
    "crypto/x509"
    "io/ioutil"
    "log"

    "github.com/gocql/gocql"
)

func main() {
    // Load CA certificate
    caCert, err := ioutil.ReadFile("/path/to/ca-cert.pem")
    if err != nil {
        log.Fatal(err)
    }

    caCertPool := x509.NewCertPool()
    caCertPool.AppendCertsFromPEM(caCert)

    // Configure TLS
    tlsConfig := &tls.Config{
        RootCAs:    caCertPool,
        MinVersion: tls.VersionTLS12,
    }

    // Create cluster config
    cluster := gocql.NewCluster("cassandra-node-1.example.com")
    cluster.SslOpts = &gocql.SslOptions{
        Config: tlsConfig,
        EnableHostVerification: true,
    }
    cluster.Authenticator = gocql.PasswordAuthenticator{
        Username: "app_user",
        Password: "app_password",
    }

    session, err := cluster.CreateSession()
    if err != nil {
        log.Fatal(err)
    }
    defer session.Close()
}
```

### Mutual TLS Configuration

```go
// Load client certificate and key
cert, err := tls.LoadX509KeyPair(
    "/path/to/client-cert.pem",
    "/path/to/client-key.pem",
)
if err != nil {
    log.Fatal(err)
}

tlsConfig := &tls.Config{
    RootCAs:      caCertPool,
    Certificates: []tls.Certificate{cert},
    MinVersion:   tls.VersionTLS12,
}
```

---

## Connection Testing

### Test with OpenSSL

```bash
# Test TLS connection to Cassandra
openssl s_client -connect cassandra-node-1.example.com:9042 \
    -CAfile /path/to/ca-cert.pem \
    -servername cassandra-node-1.example.com

# Show certificate details
openssl s_client -connect cassandra-node-1.example.com:9042 \
    -CAfile /path/to/ca-cert.pem \
    2>/dev/null | openssl x509 -noout -text
```

### Test with cqlsh

```bash
# Verbose connection test
cqlsh --ssl --debug cassandra-node-1.example.com
```

---

## Related Documentation

- [Encryption Overview](index.md) - Why encryption is essential
- [Certificate Types](certificates.md) - Generating client certificates
- [Cassandra Configuration](configuration.md) - Server-side configuration
- [Troubleshooting](troubleshooting.md) - Common client issues
