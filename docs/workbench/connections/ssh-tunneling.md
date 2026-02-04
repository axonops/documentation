---
title: "SSH Tunneling"
description: "Connect to Cassandra clusters through SSH tunnels using AxonOps Workbench. Configure bastion hosts with password or key-based authentication."
meta:
  - name: keywords
    content: "SSH tunnel, bastion host, secure connection, private key, Cassandra SSH, AxonOps Workbench"
---

# SSH Tunneling

Many production Cassandra clusters are deployed in private networks that are not directly reachable from a developer workstation. Firewalls, VPNs, and cloud VPC boundaries all create legitimate barriers between your machine and the database nodes. AxonOps Workbench solves this with built-in SSH tunneling, allowing you to route your CQL connection through an intermediary host -- commonly called a bastion host or jump server -- that has network access to both your workstation and the Cassandra cluster.

## When to Use SSH Tunneling

SSH tunneling is the right choice when:

- Your Cassandra nodes reside in a private subnet with no public IP addresses.
- A firewall or security group blocks direct access to port 9042 from your network.
- Your organization mandates that all database access passes through a hardened bastion host for auditing and access control.
- You are connecting across cloud VPCs, on-premise data centers, or hybrid environments where direct routing is unavailable.

## How It Works

When you enable SSH tunneling, AxonOps Workbench establishes the connection in two stages:

```
┌─────────────────────┐         ┌─────────────────────┐         ┌─────────────────────┐
│  AxonOps Workbench  │──SSH───▸│    Bastion Host      │──CQL───▸│  Cassandra Cluster  │
│  (your machine)     │  :22    │    (jump server)     │  :9042  │  (private network)  │
└─────────────────────┘         └─────────────────────┘         └─────────────────────┘
```

1. **SSH connection** -- Workbench opens an encrypted SSH session to the bastion host using the credentials you provide (password or private key).
2. **Port forwarding** -- Through that SSH session, Workbench requests a forwarded connection from the bastion host to the Cassandra node on the CQL port. A local port is allocated automatically on your machine so that all CQL traffic is transparently routed through the tunnel.

The result is a secure, encrypted channel between your workstation and the Cassandra cluster, without exposing any database ports to the public internet.

## Configuring an SSH Tunnel

Open the connection dialog by creating a new connection or editing an existing one, then select the **SSH Tunnel** tab.

<!-- Screenshot: SSH Tunnel tab in the connection dialog showing all fields -->

### SSH Tunnel Fields

| Field | Description | Default |
| --- | --- | --- |
| **SSH Host** | The hostname or IP address of the bastion / jump server to SSH into. | -- |
| **SSH Port** | The port on which the SSH service is listening on the bastion host. | `22` |
| **Username** | The SSH username for authenticating with the bastion host. | -- |
| **Password** | The SSH password for password-based authentication. Leave blank if using a private key. | -- |
| **Private Key File** | Path to a PEM-encoded private key file for key-based authentication. Use the file selector to browse to the key on disk. | -- |
| **Passphrase** | The passphrase that protects your private key file. Leave blank if the key is unencrypted. | -- |

!!! tip
    You can use password authentication, private key authentication, or both simultaneously. If both a password and a private key are provided, Workbench will use whichever the SSH server accepts.

### Destination Address and Port

AxonOps Workbench automatically derives the destination address and port from the host and port you configured on the **Basic** tab of the connection dialog. The SSH tunnel forwards traffic to that Cassandra node as seen from the bastion host.

If the Cassandra node's address differs when viewed from the bastion host (for example, an internal DNS name or a private IP), the destination address defaults to `127.0.0.1` on the bastion host when no explicit override is present. In most deployments, the connection host you enter on the Basic tab is already the internal address, and no additional configuration is needed.

### Saving Credentials

At the bottom of the SSH Tunnel tab, the **Save SSH credentials locally** checkbox controls whether your SSH username, password, and passphrase are persisted with the connection. When enabled, credentials are encrypted using the installation's RSA key pair and stored via the operating system's native credential manager. When disabled, you will be prompted to enter your SSH credentials each time you connect.

<!-- Screenshot: Save SSH credentials checkbox at the bottom of the SSH Tunnel tab -->

## Timeout Settings

SSH tunnel timeouts are configured globally in the application settings, not per connection. Two timeout values control tunnel establishment:

| Setting | Description | Default |
| --- | --- | --- |
| **Ready Timeout** | Maximum time (in milliseconds) to wait for the SSH connection to be established with the bastion host. | `60000` (60 seconds) |
| **Forward Timeout** | Maximum time (in milliseconds) to wait for the port-forwarding channel to be opened through the SSH connection. | `60000` (60 seconds) |

These values are stored in the application configuration file under the `[sshtunnel]` section:

```ini
[sshtunnel]
readyTimeout=60000
forwardTimeout=60000
```

!!! info
    If you frequently connect over high-latency networks or through multiple network hops, consider increasing these timeout values to avoid premature connection failures.

## Troubleshooting

### Connection Timeout

**Symptom:** The connection attempt hangs and eventually fails with a timeout error.

**Possible causes and solutions:**

- The bastion host is unreachable from your network. Verify that you can reach the SSH host and port from your machine (for example, using `ssh` from a terminal).
- A firewall is blocking outbound connections on the SSH port. Confirm that your network allows outbound traffic on port 22 (or your custom SSH port).
- The timeout values are too low for your network conditions. Increase the **Ready Timeout** and **Forward Timeout** values in the application settings.

### Authentication Failed

**Symptom:** The connection fails immediately with an "Authentication failed" or "All configured authentication methods failed" error.

**Possible causes and solutions:**

- The SSH username or password is incorrect. Double-check the credentials with your system administrator.
- The private key file does not match the public key installed on the bastion host. Verify that the correct key pair is in use.
- The passphrase for the private key is incorrect or missing. If your key is passphrase-protected, ensure the **Passphrase** field is filled in.
- The SSH server does not accept the authentication method you are using. Some servers disable password authentication entirely and require key-based authentication, or vice versa.

### Port Forwarding Failed

**Symptom:** The SSH connection succeeds, but the tunnel fails with "Timed out while waiting for forwardOut" or a "Connection refused" error.

**Possible causes and solutions:**

- The Cassandra node is not reachable from the bastion host. SSH into the bastion host manually and verify that you can connect to the Cassandra host and CQL port (for example, using `cqlsh` or `nc`).
- Cassandra is not running or is not listening on the expected port. Confirm that the Cassandra process is active and bound to the correct address and port.
- The **Forward Timeout** is too short. Increase the value in the application settings if the Cassandra node takes time to respond through the bastion host.

!!! note
    When a "Connection refused" error occurs during port forwarding, AxonOps Workbench appends a reminder to ensure that Cassandra is up and running. This message indicates that the SSH tunnel itself was established successfully, but the bastion host could not reach the Cassandra node.

### Private Key Format Issues

**Symptom:** Authentication fails even though the private key path and passphrase are correct.

**Possible causes and solutions:**

- The key file is not in PEM format. AxonOps Workbench expects a PEM-encoded private key (the file typically begins with `-----BEGIN RSA PRIVATE KEY-----` or `-----BEGIN OPENSSH PRIVATE KEY-----`). If your key is in a different format, convert it using `ssh-keygen`:

    ```bash
    ssh-keygen -p -m PEM -f /path/to/your/key
    ```

- The key uses an unsupported algorithm. Workbench relies on the `ssh2` library for tunnel creation. While most key types are supported (RSA, DSA, ECDSA), **ed25519 keys with a passphrase** may not be fully decrypted by the built-in key parser. If you encounter issues with an ed25519 key, try using the key without a passphrase or switch to an RSA or ECDSA key.

!!! warning
    Ensure that your private key file has appropriate file-system permissions. On Linux and macOS, the key file should be readable only by your user (`chmod 600`). Overly permissive key files may be rejected by the SSH client library.

## Best Practices

- **Use key-based authentication** whenever possible. It is more secure than password authentication and avoids the need to store or transmit passwords.
- **Keep timeout values reasonable.** The 60-second defaults work well for most environments. Only increase them if you experience intermittent timeouts over slow or congested networks.
- **Test the connection** after configuring SSH tunnel settings. The **Test Connection** button validates the full path -- SSH tunnel establishment, port forwarding, and CQL handshake -- in a single step.
- **Rotate SSH keys regularly** in accordance with your organization's security policies. Update the private key file path in the connection dialog after each rotation.
