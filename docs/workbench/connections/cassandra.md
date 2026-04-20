---
title: "Apache Cassandra Connections"
description: "Connect to Apache Cassandra and DataStax Enterprise clusters. Configure authentication, consistency levels, cqlsh.rc, and connection variables."
meta:
  - name: keywords
    content: "Cassandra connection, DSE, authentication, consistency level, cqlsh.rc, variables, AxonOps Workbench"
---

# Apache Cassandra Connections

AxonOps Workbench connects directly to Apache Cassandra and DataStax Enterprise clusters using the CQL native protocol. The connection dialog provides a structured interface for configuring your cluster endpoint, authentication credentials, consistency levels, and the underlying `cqlsh.rc` configuration -- all from a single window.

## Basic Connection

The **Basic** tab of the connection dialog contains the core parameters needed to reach your cluster.

| Field | Description | Required |
| --- | --- | --- |
| **Connection Name** | A human-readable label for this connection (e.g., `Production Node 1`). Must be unique within the workspace. | Yes |
| **Datacenter** | The Cassandra datacenter name to connect to (e.g., `datacenter1`). | No |
| **Hostname** | The IP address or hostname of a Cassandra node (e.g., `192.168.0.10`). | Yes |
| **Port** | The CQL native transport port. Defaults to `9042`. | Yes |
| **Connection Time** | Controls the timestamp generator used during insert operations. Options are **Client-Side Time** (desktop time, using `MonotonicTimestampGenerator`), **Server-Side Time** (Cassandra server time, using `None`), or **Not Set**. | No |
| **Page Size** | The default number of rows returned per page for query results. Defaults to `100`. | No |

<!-- Screenshot: Basic tab of the Apache Cassandra connection dialog showing connection name, datacenter, hostname, port, connection time, and page size fields -->

### Testing a Connection

Before saving, click the **Test Connection** button in the bottom-right corner of the dialog. Workbench will attempt to establish a CQL session using the current settings -- including any authentication, SSH tunnel, or SSL configuration you have provided.

- A spinning indicator appears while the connection attempt is in progress.
- If the test succeeds, a confirmation message is displayed.
- If the test fails, an error message describes what went wrong (unreachable host, authentication failure, SSL handshake error, etc.).
- You can click the **Terminate** button to cancel a test that is taking too long.

!!! tip
    Always test your connection before saving. This catches configuration mistakes early and avoids troubleshooting failed connections after the fact.

## Authentication

The **Authentication** tab lets you provide credentials for clusters that have Cassandra native authentication enabled (the `PasswordAuthenticator`).

| Field | Description |
| --- | --- |
| **Username** | The Cassandra username (e.g., `cassandra`). |
| **Password** | The corresponding password. A toggle button lets you reveal or hide the password text. |
| **Save authentication credentials locally** | When checked (the default), credentials are persisted securely on your machine so you do not have to re-enter them each time you connect. |

### Credential Security

AxonOps Workbench never stores credentials in plain-text configuration files. Instead, it uses a two-layer security model:

- **OS Keychain Storage** -- Credentials are stored in your operating system's native credential manager using the [keytar](https://github.com/nickhurst/keytar){:target="_blank"} library.
- **RSA Encryption** -- Each Workbench installation generates a unique RSA key pair. Sensitive connection data is encrypted at rest with this key before being passed to the keychain.

!!! info "Keychain backends by operating system"
    The underlying keychain backend depends on your platform:

    - **macOS** -- Keychain Services (the system Keychain)
    - **Windows** -- Windows Credential Manager
    - **Linux** -- libsecret (used by GNOME Keyring, KWallet, and other Secret Service implementations)

    On Linux, ensure that `libsecret` and a Secret Service provider (such as GNOME Keyring) are installed and running. Without one, credential storage will not function.

## Consistency Levels

When executing CQL statements in the CQL Console, you can set the consistency level for both regular and serial (lightweight transaction) operations. These settings appear in the query toolbar and control how many replicas must acknowledge a read or write before the operation is considered successful.

### Regular Consistency Levels

The following regular consistency levels are available:

| Level | Description |
| --- | --- |
| `ANY` | A write must be written to at least one node (including hinted handoff). Not valid for reads. |
| `ONE` | A single replica must respond. |
| `TWO` | Two replicas must respond. |
| `THREE` | Three replicas must respond. |
| `QUORUM` | A majority of replicas across all datacenters must respond. |
| `LOCAL_QUORUM` | A majority of replicas in the local datacenter must respond. |
| `EACH_QUORUM` | A majority of replicas in each datacenter must respond. Only valid for writes. |
| `ALL` | All replicas must respond. |
| `LOCAL_ONE` | A single replica in the local datacenter must respond. |

### Serial Consistency Levels

Serial consistency levels apply only to lightweight transactions (`IF NOT EXISTS`, `IF` conditions):

| Level | Description |
| --- | --- |
| `SERIAL` | Linearizable consistency across all datacenters. |
| `LOCAL_SERIAL` | Linearizable consistency within the local datacenter only. |

!!! tip "When to change consistency levels"
    The defaults (`LOCAL_ONE` for reads, `LOCAL_ONE` for writes, `LOCAL_SERIAL` for serial) are suitable for most development workflows. Consider changing them when:

    - You need **stronger consistency guarantees** for testing -- use `LOCAL_QUORUM` or `QUORUM` to simulate production read/write behavior.
    - You are running **lightweight transactions** and need to control whether the serial phase spans all datacenters (`SERIAL`) or just the local one (`LOCAL_SERIAL`).
    - You want to **verify replication** by reading at `ALL` to confirm data has reached every replica.

    Avoid using `ALL` for routine work, as a single unavailable replica will cause the operation to fail.

## cqlsh.rc Configuration

Every Cassandra connection in AxonOps Workbench is backed by a `cqlsh.rc` configuration file. This file controls low-level connection behavior including timeouts, SSL settings, COPY options, and pre/post-connect scripts.

### Built-in Editor

The connection dialog includes a built-in Monaco editor (the same editor that powers VS Code) for directly editing the `cqlsh.rc` content. You can toggle between the form view and the editor view using the **Switch Editor** button in the dialog footer.

<!-- Screenshot: The cqlsh.rc editor view inside the connection dialog showing the Monaco editor with syntax highlighting -->

The editor provides:

- Syntax highlighting for INI-style configuration
- The ability to toggle between the structured form and raw editor using the **Switch Editor** button
- An **Expand Editor** button to view and edit the configuration in a larger window

### Sensitive Data Detection

Workbench actively monitors the `cqlsh.rc` content for sensitive data. If it detects uncommented `username`, `password`, or `credentials` fields in the file, it highlights the offending lines in red and displays a warning glyph in the editor margin.

!!! warning
    Do not place usernames, passwords, or credentials directly in the `cqlsh.rc` file. Use the **Authentication** tab instead, which stores credentials securely in your OS keychain. If Workbench detects sensitive data in the editor, the affected lines are flagged to alert you.

### Default cqlsh.rc Template

When you create a new connection, Workbench populates the editor with a default `cqlsh.rc` template. This template includes all standard sections with their options commented out:

| Section | Purpose |
| --- | --- |
| `[authentication]` | Credentials file path and default keyspace |
| `[auth_provider]` | Custom authentication provider class |
| `[ui]` | Display settings (colors, time format, timezone, float precision, encoding) |
| `[cql]` | CQL version and default page size |
| `[connection]` | Hostname, port, SSL toggle, timeouts, and timestamp generator |
| `[csv]` | Field size limit for CSV operations |
| `[tracing]` | Maximum trace wait time |
| `[ssl]` | Certificate file paths and TLS version |
| `[certfiles]` | Per-host certificate overrides |
| `[preconnect]` | Scripts to execute before connecting |
| `[postconnect]` | Scripts to execute after connecting |
| `[copy]` | Shared COPY TO / COPY FROM options |
| `[copy-to]` | COPY TO specific options |
| `[copy-from]` | COPY FROM specific options |

The `[connection]` section is pre-configured with `hostname`, `port = 9042`, and `timestamp_generator = None` as active (uncommented) values. All other options are commented out by default and can be enabled as needed.

### Custom cqlsh.rc Path

Each connection stores its `cqlsh.rc` file within the connection's own folder structure inside the workspace directory, at the path:

```
<workspace>/<connection-folder>/config/cqlsh.rc
```

When a connection is used to launch a CQL session, Workbench passes this file to cqlsh via the `--cqlshrc` flag, ensuring that each connection uses its own isolated configuration.

## Connection Variables

Variables allow you to parameterize values across your connections and `cqlsh.rc` files. Instead of hard-coding hostnames, ports, or other values that change between environments, you can define a variable once and reference it anywhere using the `${variable_name}` syntax.

### What Variables Are

A variable is a named placeholder with a value and a scope. When Workbench processes your `cqlsh.rc` files and SSH tunnel configurations, it replaces `${variable_name}` references with the corresponding values. This makes it straightforward to:

- Share a single set of connection templates across development, staging, and production environments
- Change a hostname or port in one place and have it propagate to all connections that reference it
- Keep environment-specific values out of your `cqlsh.rc` files

### Managing Variables

Variables are managed in the **Settings** dialog under the **Variables** section. Each variable has three attributes:

| Attribute | Description |
| --- | --- |
| **Name** | The variable identifier. Must contain only letters, digits, and underscores. Must start with a letter or underscore. |
| **Value** | The value that will be substituted wherever the variable is referenced. |
| **Scope** | Which workspaces the variable applies to. You can select **All Workspaces** or limit it to specific workspaces. |

### Manifest and Values Files

Variables are persisted in two separate stores within the OS keychain:

- **Manifest** (`AxonOpsWorkbenchVarsManifest`) -- Contains variable names and their scope assignments. This is the "shape" of your variable set.
- **Values** (`AxonOpsWorkbenchVarsValues`) -- Contains the full variable objects including their actual values.

This separation ensures that the structure of your variables can be inspected without exposing sensitive values.

### Nested Variables

Variable values can reference other variables. For example, if you define:

- `cluster_host` = `192.168.1.100`
- `cluster_endpoint` = `${cluster_host}:9042`

Workbench recursively resolves nested references, so `${cluster_endpoint}` evaluates to `192.168.1.100:9042`. The editor provides an eye toggle button next to variable values that contain nested references, allowing you to see the resolved value.

### Collision Detection

When you save variables, Workbench checks for collisions to prevent ambiguity:

- **Name collisions** -- Two variables with the same name and overlapping scope are not allowed.
- **Value collisions** -- Two variables with the same value and overlapping scope are flagged, because Workbench would not be able to determine which variable name to substitute during reverse mapping.

If a collision is detected, the conflicting fields are highlighted and a descriptive error message explains how to resolve the issue (either rename the variable or adjust its scope).

### Variable Scoping

Each variable can be scoped to:

- **All Workspaces** -- The variable is available in every workspace. Selecting this option deselects all individual workspace selections.
- **Specific Workspaces** -- The variable is only available in the selected workspaces. If you subsequently select all workspaces individually, Workbench automatically switches back to the "All Workspaces" scope.

When Workbench resolves variables for a given connection, it only considers variables whose scope includes the active workspace (or whose scope is set to "All Workspaces").

## DataStax Enterprise

DataStax Enterprise (DSE) clusters use the same Apache Cassandra connection dialog. To connect to a DSE cluster:

1. Open the connection dialog and select the **Apache Cassandra** connection type.
2. Enter the hostname and port of a DSE node in the **Basic** tab.
3. Provide authentication credentials in the **Authentication** tab if your DSE cluster has authentication enabled.
4. Configure SSH tunneling or SSL/TLS as needed.

!!! note
    DSE clusters expose the CQL native transport on the same default port (`9042`) as open-source Cassandra. AxonOps Workbench communicates with DSE through the standard CQL protocol, so no additional configuration is required beyond what you would provide for an Apache Cassandra connection. DSE-specific features such as DSE Graph or DSE Search are outside the scope of CQL connections.
