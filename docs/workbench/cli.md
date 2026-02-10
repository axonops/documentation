---
title: "CLI Reference"
description: "AxonOps Workbench command-line interface reference. Manage workspaces and connections, automate setup, and run CQL sessions from the terminal."
meta:
  - name: keywords
    content: "CLI, command line, automation, headless, import workspace, import connection, cqlsh, AxonOps Workbench"
---

# CLI Reference

AxonOps Workbench includes a built-in command-line interface (CLI) for managing workspaces and connections, automating environment setup, and launching interactive CQL sessions -- all without opening the graphical interface.

When you pass a supported argument to the workbench executable, the application automatically switches to CLI mode. Without any arguments, the regular GUI starts as usual.

```bash
./axonops-workbench -v          # CLI mode
./axonops-workbench             # Regular GUI mode
```

!!! note "Argument value syntax"
    When passing a value to an argument, you **must** use the equals sign (`=`). For example:

    ```bash
    ./axonops-workbench --list-connections workspace-0b5d20cb08    # Incorrect
    ./axonops-workbench --list-connections=workspace-0b5d20cb08    # Correct
    ```

!!! note "Windows users"
    On Windows, the shell may show the prompt immediately without waiting for Workbench to finish. Run it as follows to ensure the shell waits until completion:

    ```bash
    start /wait "" "AxonOps Workbench.exe" <arguments>
    ```

## Arguments Reference

| Argument | Value | Description |
|----------|-------|-------------|
| `--help`, `-h` | -- | Print all supported arguments. |
| `--version`, `-v` | -- | Print the current version of AxonOps Workbench. |
| `--list-workspaces` | -- | List all saved workspaces without their connections. |
| `--list-connections` | Workspace ID | List all saved connections in a specific workspace. |
| `--import-workspace` | JSON string, file path, or folder path | Import a workspace from inline JSON, a JSON file, or a workspace folder. |
| `--import-connection` | JSON file path | Import a connection from a JSON file. Supports SSH tunnel info and cqlsh.rc file paths. |
| `--connect` | Connection ID | Connect to a saved connection and start an interactive CQL session. |
| `--json` | -- | Output results as JSON instead of formatted text. Works with `--list-workspaces`, `--list-connections`, `--import-workspace`, and `--import-connection`. |
| `--delete-file` | -- | Delete the source file after a successful import. Ignored when `--import-workspace` receives a folder path. |
| `--test-connection` | `true` or `false` | Test a connection before importing it. With `true`, a failed test stops the import. With `false` or no value, the import continues regardless. |
| `--copy-to-default` | -- | When `--import-workspace` receives a folder path, copy the workspace to the default data directory instead of leaving it in its original location. |

## Workspace Operations

### Listing Workspaces

Retrieve a table of all saved workspaces along with their IDs and connection counts:

```bash
./axonops-workbench --list-workspaces
```

### Importing a Workspace

The `--import-workspace` argument accepts three types of input:

- **Inline JSON** -- pass a JSON string directly.
- **File path** -- pass an absolute path to a file containing valid JSON.
- **Folder path** -- pass an absolute path to a single workspace folder, or a parent folder containing multiple workspace folders (one depth level). When importing from a folder, all connections within that workspace are imported automatically.

**Workspace JSON structure:**

```json
{
    "name": "",
    "color": "",
    "defaultPath": "",
    "path": ""
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | The workspace's unique name. Duplicate or invalid names cause an error. |
| `color` | No | The workspace's accent color, in any CSS color format (HEX, RGB, HSL, etc.). |
| `defaultPath` | No | Set to `true` to store workspace data in the default location, or `false` to use a custom path. Defaults to `false`. |
| `path` | No | An absolute path where the workspace data folder will be created. Only used when `defaultPath` is `false`. |

**Examples:**

```bash
# Import from inline JSON
./axonops-workbench --import-workspace='{"name":"Production", "color":"#FF5733"}'

# Import from a JSON file
./axonops-workbench --import-workspace=/path/to/workspace.json

# Import from a folder and copy to the default data directory
./axonops-workbench --import-workspace=/path/to/workspaces/ --copy-to-default

# Import from a file and delete it after success
./axonops-workbench --import-workspace=/path/to/workspace.json --delete-file
```

!!! warning
    If a workspace with the same name already exists, the import process is terminated. Ensure workspace names are unique before importing.

## Connection Operations

### Listing Connections

Retrieve all connections in a specific workspace by passing the workspace ID:

```bash
./axonops-workbench --list-connections=workspace-0b5d20cb08
```

!!! tip
    Run `--list-workspaces` first to obtain workspace IDs.

### Importing a Connection

Import a connection by passing the absolute path to a JSON file. The file must contain valid JSON in one of the structures shown below.

```bash
./axonops-workbench --import-connection=/path/to/connection.json
```

**Apache Cassandra connection JSON structure:**

```json
{
    "basic": {
        "workspace_id": "",
        "name": "",
        "datacenter": "",
        "hostname": "",
        "port": "",
        "timestamp_generator": "",
        "cqlshrc": ""
    },
    "auth": {
        "username": "",
        "password": ""
    },
    "ssl": {
        "ssl": "",
        "certfile": "",
        "userkey": "",
        "usercert": "",
        "validate": ""
    },
    "ssh": {
        "host": "",
        "port": "",
        "username": "",
        "password": "",
        "privatekey": "",
        "passphrase": "",
        "destaddr": "",
        "destport": ""
    }
}
```

| Section | Field | Required | Description |
|---------|-------|----------|-------------|
| `basic` | `workspace_id` | Yes | ID of the target workspace. |
| `basic` | `name` | Yes | Unique connection name within the workspace. |
| `basic` | `hostname` | Yes | Hostname or IP address of the Cassandra node. |
| `basic` | `datacenter` | No | Datacenter to set when activating the connection. |
| `basic` | `port` | No | Connection port. Defaults to `9042`. |
| `basic` | `timestamp_generator` | No | Timestamp generator class for the connection. Leave empty for the default. |
| `basic` | `cqlshrc` | No | Absolute path to a `cqlsh.rc` configuration file. |
| `auth` | `username` | No | Cassandra authentication username. |
| `auth` | `password` | No | Cassandra authentication password. |
| `ssl` | `ssl` | No | Enable SSL/TLS for the connection. |
| `ssl` | `certfile` | No | Path to the CA certificate file. |
| `ssl` | `userkey` | No | Path to the user private key file. |
| `ssl` | `usercert` | No | Path to the user certificate file. |
| `ssl` | `validate` | No | Enable certificate validation. |
| `ssh` | `host` | No | SSH tunnel hostname. |
| `ssh` | `port` | No | SSH tunnel port. |
| `ssh` | `username` | No | SSH username. |
| `ssh` | `password` | No | SSH password. |
| `ssh` | `privatekey` | No | Path to the SSH private key file. |
| `ssh` | `passphrase` | No | Passphrase for the SSH private key. |
| `ssh` | `destaddr` | No | Destination address for the tunnel. |
| `ssh` | `destport` | No | Destination port for the tunnel. |

!!! info
    If authentication credentials exist in a referenced `cqlsh.rc` file, they are ignored. Always provide `username` and `password` in the JSON structure.

**DataStax Astra DB connection JSON structure:**

```json
{
    "workspace_id": "",
    "name": "",
    "username": "clientId in AstraDB",
    "password": "secret in AstraDB",
    "scb_path": ""
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `workspace_id` | Yes | ID of the target workspace. |
| `name` | Yes | Unique connection name within the workspace. |
| `username` | Yes | The Astra DB Client ID. |
| `password` | Yes | The Astra DB Client Secret. |
| `scb_path` | Yes | Absolute path to the Secure Connect Bundle (`.zip` file). |

### Testing a Connection Before Import

Add `--test-connection` to validate connectivity before finalizing the import:

```bash
# Stop the import if the connection test fails
./axonops-workbench --import-connection=/path/to/connection.json --test-connection=true

# Continue importing even if the test fails (feedback is still printed)
./axonops-workbench --import-connection=/path/to/connection.json --test-connection=false
```

When `--test-connection` is passed without a value, it defaults to `false` -- the import continues regardless of test outcome, but the result is printed to the terminal.

## Interactive CQL Sessions

The `--connect` argument launches a full interactive CQLsh session directly from your terminal, with no GUI required. Pass the connection ID to connect immediately:

```bash
./axonops-workbench --connect=connection-abc123
```

The workbench handles all connection complexity -- authentication, SSL/TLS, and SSH tunnels -- automatically before dropping you into the CQLsh prompt. Progress is displayed in the terminal, and you have full access to execute CQL commands interactively.

!!! tip
    To find connection IDs, run `--list-connections` with the target workspace ID.

## JSON Output Mode

Add the `--json` flag to any listing or import command to receive machine-readable JSON output instead of formatted tables. This is particularly useful for scripting and automation:

```bash
# List workspaces as JSON
./axonops-workbench --list-workspaces --json

# List connections as JSON
./axonops-workbench --list-connections=workspace-0b5d20cb08 --json

# Import a workspace with JSON output
./axonops-workbench --import-workspace='{"name":"Staging"}' --json
```

## Headless Linux

To use AxonOps Workbench on a headless Linux host (no display server), install and run `xvfb` to provide a virtual framebuffer:

| Distribution | Package Name | Install Command |
|---|---|---|
| Ubuntu / Debian | `xvfb` | `sudo apt install xvfb` |
| RHEL / CentOS | `xorg-x11-server-Xvfb` | `sudo yum install xorg-x11-server-Xvfb` |
| Arch Linux | `xorg-server-xvfb` | `sudo pacman -S xorg-server-xvfb` |
| Alpine | `xvfb` | `apk add xvfb` |

Before running the workbench, start the virtual display:

```bash
Xvfb :99 -screen 0 1280x720x24 & export DISPLAY=:99
```

Then run any CLI command as usual:

```bash
./axonops-workbench --list-workspaces
```

## Automation Examples

### Batch Workspace Setup

The following script creates a workspace, retrieves its ID, imports a connection, and validates it -- all in one pass:

```bash
#!/bin/bash
set -e

WORKBENCH="./axonops-workbench"

# Step 1: Import a workspace
echo "Creating workspace..."
$WORKBENCH --import-workspace='{"name":"Production", "color":"#2E86AB"}'

# Step 2: Retrieve the workspace ID
echo "Retrieving workspace ID..."
WORKSPACE_ID=$($WORKBENCH --list-workspaces --json | \
  python3 -c "import sys,json; ws=json.load(sys.stdin); print([w['id'] for w in ws if w['name']=='Production'][0])")
echo "Workspace ID: $WORKSPACE_ID"

# Step 3: Write the connection JSON file
cat > /tmp/connection.json <<EOF
{
    "basic": {
        "workspace_id": "$WORKSPACE_ID",
        "name": "prod-cassandra-1",
        "hostname": "cassandra.prod.internal",
        "port": "9042",
        "datacenter": "dc1"
    },
    "auth": {
        "username": "app_user",
        "password": "secure_password"
    }
}
EOF

# Step 4: Import and test the connection, then clean up the file
echo "Importing and testing connection..."
$WORKBENCH --import-connection=/tmp/connection.json --test-connection=true --delete-file

echo "Setup complete."
```

### CI/CD Integration

Use the CLI in continuous integration pipelines to validate that database connections are reachable before running integration tests:

```bash
#!/bin/bash
# ci-validate-connections.sh

WORKBENCH="./axonops-workbench"

# Import workspace and connection from checked-in config files
$WORKBENCH --import-workspace=ci/workspace.json --json
$WORKBENCH --import-connection=ci/connection.json --test-connection=true --json

if [ $? -ne 0 ]; then
    echo "Connection validation failed. Aborting pipeline."
    exit 1
fi

echo "Connection validated. Proceeding with tests."
```

### Automated CQL Script Execution

Combine `--connect` with standard shell piping to run CQL scripts non-interactively:

```bash
# Connect and run a CQL script
echo "DESCRIBE KEYSPACES;" | ./axonops-workbench --connect=connection-abc123
```
