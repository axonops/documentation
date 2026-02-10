---
title: "Troubleshooting"
description: "Troubleshoot common AxonOps Workbench issues. Connection failures, authentication errors, SSL problems, Docker issues, and query errors."
meta:
  - name: keywords
    content: "troubleshooting, connection failure, authentication error, SSL error, Docker, AxonOps Workbench"
---

# Troubleshooting

This page covers common issues you may encounter when using AxonOps Workbench and provides steps to resolve them.

## Connection Issues

### Cannot Connect to Cluster

If the workbench fails to establish a connection to your Cassandra cluster, work through the following checklist:

- **Hostname and port** -- Verify that the hostname (or IP address) and port are correct. The default Cassandra native transport port is `9042`.
- **Cassandra is running** -- Confirm the Cassandra process is running on the target host. Use `nodetool status` or check the system service status.
- **Firewall rules** -- Ensure that your firewall allows traffic on the configured port between your machine and the Cassandra node.
- **Datacenter setting** -- If you specified a datacenter in the connection dialog, confirm it matches a datacenter name reported by `nodetool status`. An incorrect datacenter name can prevent the driver from discovering nodes.
- **Network connectivity** -- Run a basic connectivity test from your machine:

    ```bash
    telnet <hostname> 9042
    ```

    or:

    ```bash
    nc -zv <hostname> 9042
    ```

!!! tip
    Use the `--test-connection` CLI argument to validate connectivity before importing a connection. See the [CLI Reference](cli.md) for details.

### Authentication Failed

If you receive an authentication error:

- **Credentials** -- Double-check the username and password in the connection dialog. Cassandra credentials are case-sensitive.
- **Authenticator configuration** -- Confirm that the Cassandra cluster has authentication enabled (`authenticator: PasswordAuthenticator` in `cassandra.yaml`). If authentication is disabled on the server but credentials are provided in the workbench, the connection may still fail.
- **Role permissions** -- Verify that the user role has `LOGIN` permission and the necessary grants on the target keyspaces.

### Connection Timeout

If connections are timing out:

- **Network latency** -- High latency or unstable network conditions can cause timeouts. Test connectivity with `ping` or `traceroute`.
- **SSH tunnel timeouts** -- If using an SSH tunnel, the workbench has configurable timeout values for tunnel establishment (`readyTimeout`) and port forwarding (`forwardTimeout`), both defaulting to 60 seconds. For slow networks, consider checking these values in the application configuration.
- **Overloaded cluster** -- A Cassandra node under heavy load may be slow to accept new connections. Check node health with `nodetool status` and `nodetool tpstats`.

## SSL/TLS Issues

### Certificate Errors

SSL/TLS connection failures are typically caused by certificate configuration problems.

**Wrong CA certificate:**
Ensure the CA certificate file (`certfile`) matches the certificate authority that signed the Cassandra node's certificate. If the server uses a certificate chain, the CA file must include the full chain.

**Expired certificate:**
Check the certificate expiry date:

```bash
openssl x509 -in /path/to/cert.pem -noout -enddate
```

If the certificate has expired, obtain a renewed certificate from your certificate authority.

**Hostname mismatch:**
The certificate's Common Name (CN) or Subject Alternative Name (SAN) must match the hostname you are connecting to. Verify with:

```bash
openssl x509 -in /path/to/cert.pem -noout -text | grep -A1 "Subject Alternative Name"
```

**Self-signed certificates:**

!!! danger
    Disabling certificate validation reduces security and should only be used in development or testing environments. Never disable validation for production connections.

If you are using self-signed certificates and encounter validation errors, you can disable certificate validation in the connection's SSL settings by unchecking the **Validate** option. This bypasses hostname and CA verification.

### Key Format Issues

- Ensure private key files are in PEM format. If your key is in a different format (e.g., PKCS#12), convert it first:

    ```bash
    openssl pkcs12 -in keystore.p12 -out userkey.pem -nodes -nocerts
    ```

- Confirm that the private key file is not password-protected unless the workbench supports passphrase entry for client certificates.
- Verify file permissions on key files. On Linux and macOS, private keys should be readable only by the owner:

    ```bash
    chmod 600 /path/to/userkey.pem
    ```

## SSH Tunnel Issues

### Tunnel Establishment Failed

If the SSH tunnel cannot be established:

- **SSH host reachability** -- Verify that the SSH host is reachable from your machine on the specified SSH port (default `22`).
- **Credentials** -- Check the SSH username and password, or ensure the private key file path is correct and the key has appropriate permissions (`chmod 600`).
- **Host key verification** -- If the SSH server's host key has changed (e.g., after a server rebuild), you may need to update your `known_hosts` file.
- **SSH server configuration** -- Confirm that the SSH server allows TCP forwarding. Check for `AllowTcpForwarding yes` in the server's `sshd_config`.

### Port Forwarding Failed

If the tunnel is established but port forwarding fails:

- **Destination address and port** -- Verify that the `destaddr` and `destport` values in the SSH configuration point to the correct Cassandra host and port as reachable from the SSH server.
- **Port conflicts** -- Ensure the local port used for tunneling is not already in use by another process.
- **Firewall on the SSH host** -- The SSH server must be able to reach the Cassandra node on the specified destination address and port.

## Local Cluster Issues

### Docker or Podman Not Found

AxonOps Workbench uses Docker or Podman to manage local (sandbox) Cassandra clusters. If the workbench cannot find your container runtime:

- **Verify installation** -- Confirm Docker or Podman is installed and accessible from the command line:

    ```bash
    docker --version
    # or
    podman --version
    ```

- **Container management tool setting** -- In **Settings**, check that the **Containers Management Tool** is set to the correct runtime (`docker` or `podman`). By default, this is set to `none`.
- **Custom paths** -- If Docker or Podman is installed in a non-standard location, configure the path in the application settings under **Containers Management Tool Paths**.

### Cluster Won't Start

If a local cluster fails to start:

- **Port conflicts** -- Cassandra's default ports (`9042`, `7000`, `7001`, `7199`) may be in use by another process. Check for conflicts:

    ```bash
    lsof -i :9042
    # or on Linux
    ss -tlnp | grep 9042
    ```

- **Insufficient disk space** -- Docker containers need adequate disk space. Check available space with `df -h` and ensure Docker has sufficient storage.
- **Docker daemon not running** -- Verify the Docker daemon is active:

    ```bash
    sudo systemctl status docker
    ```

- **Resource limits** -- Cassandra requires a minimum of 2 GB of memory. Ensure your Docker environment has sufficient resources allocated (check Docker Desktop settings on macOS and Windows).

### Permission Errors on Linux

If you encounter permission errors when managing local clusters on Linux:

- **Docker group membership** -- Add your user to the `docker` group to avoid needing `sudo`:

    ```bash
    sudo usermod -aG docker $USER
    ```

    Log out and log back in for the change to take effect.

- **Podman rootless mode** -- If using Podman in rootless mode, ensure your user has the necessary sub-UID and sub-GID ranges configured in `/etc/subuid` and `/etc/subgid`.

## Query Issues

### Execution Errors

**Syntax errors:**
CQL syntax errors are reported with the line and position of the error. Common causes include missing semicolons, mismatched quotes, and incorrect keyword usage. Refer to the [Apache Cassandra CQL documentation](https://cassandra.apache.org/doc/latest/cassandra/cql/){:target="_blank"} for correct syntax.

**No keyspace selected:**
If you see `No keyspace has been specified`, run a `USE` statement to select a keyspace before executing table-level queries:

```sql
USE my_keyspace;
SELECT * FROM my_table LIMIT 10;
```

Alternatively, qualify table names with the keyspace:

```sql
SELECT * FROM my_keyspace.my_table LIMIT 10;
```

**Table not found:**
Verify the table exists in the current keyspace:

```sql
DESCRIBE TABLES;
```

Table and keyspace names are case-sensitive when quoted. If the table was created with double-quoted names, you must use the same casing.

### Slow Query Performance

If queries are running slowly:

- **Enable Query Tracing** -- Use the tracing feature in the CQL console to see how the query is executed across nodes. This reveals the time spent on each operation and helps identify bottlenecks.

    ```sql
    TRACING ON;
    SELECT * FROM my_keyspace.my_table WHERE id = 'abc123';
    TRACING OFF;
    ```

- **Check query patterns** -- Avoid `SELECT *` on large tables without a `WHERE` clause. Full table scans are expensive in Cassandra.
- **Review the data model** -- Ensure your queries match the table's partition key and clustering columns. Queries that require `ALLOW FILTERING` are typically inefficient and should be avoided in production.

## Application Issues

### App Won't Start

If AxonOps Workbench fails to launch:

- **Check system requirements** -- Ensure your operating system and hardware meet the minimum requirements. AxonOps Workbench runs on Windows, macOS, and Linux.
- **Clear application configuration** -- A corrupted configuration file can prevent startup. Locate and remove the configuration directory to reset to defaults:

    - **Windows:** `%APPDATA%/AxonOps Workbench/`
    - **macOS:** `~/Library/Application Support/AxonOps Workbench/`
    - **Linux:** `~/.config/AxonOps Workbench/`

    !!! warning
        Clearing the configuration directory removes all saved workspaces and connections. Export your data first if possible.

- **Reinstall the application** -- Download the latest version from the [AxonOps Workbench releases page](https://github.com/axonops/axonops-workbench-cassandra/releases){:target="_blank"} and perform a clean installation.
- **Check log files** -- Application logs can reveal startup errors. Log files are located in:

    - **Windows:** `%APPDATA%/AxonOps Workbench/logs/`
    - **macOS:** `~/Library/Logs/AxonOps Workbench/`
    - **Linux:** `~/.config/AxonOps Workbench/logs/`

### Update Issues

If the application fails to update:

- **Manual update** -- Download the latest version directly from the [releases page](https://github.com/axonops/axonops-workbench-cassandra/releases){:target="_blank"} and install it over the existing version.
- **Check network access** -- Automatic updates require access to GitHub. Verify that your network allows outbound connections to `github.com`.
- **Permissions** -- On Linux and macOS, ensure the application directory is writable by your user.

## Getting Help

If the steps above do not resolve your issue:

- **GitHub Issues** -- Search for existing issues or open a new one at [github.com/axonops/axonops-workbench-cassandra/issues](https://github.com/axonops/axonops-workbench-cassandra/issues){:target="_blank"}. Include the following information:

    - AxonOps Workbench version (`--version`)
    - Operating system and version
    - Steps to reproduce the issue
    - Relevant log file excerpts

- **Log files** -- Always attach relevant log files when reporting issues. Logs contain timestamps, error messages, and stack traces that help diagnose problems quickly.
