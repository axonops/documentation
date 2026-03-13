---
title: "Connections"
description: "Connect AxonOps Workbench to Apache Cassandra clusters and DataStax Astra DB with SSH tunneling and SSL/TLS encryption support."
meta:
  - name: keywords
    content: "AxonOps Workbench connections, Cassandra connection, Astra DB connection, SSH tunnel, SSL TLS, database connection"
---

# Connections

AxonOps Workbench supports multiple connection types for Apache Cassandra, including direct connections to on-premise or self-hosted clusters and managed cloud databases through DataStax Astra DB. Every connection method is backed by enterprise-grade security features such as SSH tunneling and full SSL/TLS certificate chain support.

## Connection Types

| Type | Use Case | Authentication | Encryption |
| --- | --- | --- | --- |
| Apache Cassandra | Direct connection to on-premise or self-hosted clusters | Username / Password | Optional SSL/TLS |
| DataStax Astra DB | DataStax managed cloud Cassandra | Client ID / Secret | Built-in via Secure Connect Bundle |

## Security Features

AxonOps Workbench takes a defense-in-depth approach to securing your database credentials and network traffic:

- **OS Keychain Storage** -- Credentials are stored in the operating system's native credential manager (macOS Keychain, Windows Credential Manager, or Linux libsecret) rather than in plain-text configuration files.
- **Per-Installation RSA Key Encryption** -- Each Workbench installation generates a unique RSA key pair used to encrypt sensitive connection data at rest.
- **SSH Tunneling** -- Connect to clusters that are not directly reachable from your workstation by routing traffic through an SSH bastion host. This is essential for network-restricted or private-subnet deployments.
- **SSL/TLS Certificate Chain Support** -- Configure trusted CA certificates, client certificates, and private keys for mutual TLS authentication with your cluster.

## Connection Dialog

When you create or edit a connection, the connection dialog presents five tabs:

1. **Basic** -- Configure the core connection parameters including hostname, port, and datacenter name.
2. **Authentication** -- Provide your username and password for Cassandra native authentication, or your Client ID and Client Secret for Astra DB.
3. **SSH Tunnel** -- Set up an SSH tunnel by specifying the bastion host, SSH port, SSH username, and authentication method (password or private key).
4. **SSL** -- Enable SSL/TLS and configure your CA certificate, client certificate, and client private key for encrypted and mutually authenticated connections.
5. **AxonOps** -- Link this connection to an AxonOps Dashboard instance for integrated monitoring and management alongside your CQL workflow.

<!-- Screenshot: Connection dialog showing the five tabs (Basic, Authentication, SSH Tunnel, SSL, AxonOps) -->

!!! tip
    Use the **Test Connection** button before saving to verify that your hostname, credentials, and any tunnel or SSL settings are configured correctly. This avoids troubleshooting failed connections after the fact.

## Detailed Guides

For step-by-step instructions on each connection type and security feature, see the following pages:

- [Apache Cassandra](cassandra.md) -- Connect to self-hosted or on-premise Cassandra clusters.
- [DataStax Astra DB](astra-db.md) -- Connect to DataStax Astra DB using a Secure Connect Bundle.
- [SSH Tunneling](ssh-tunneling.md) -- Route connections through an SSH bastion host for network-restricted clusters.
- [SSL/TLS](ssl-tls.md) -- Configure SSL/TLS encryption and mutual certificate authentication.
