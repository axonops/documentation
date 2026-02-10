---
title: "Workspaces"
description: "Organize your Cassandra connections with workspaces in AxonOps Workbench. Create, customize, and share workspace configurations."
meta:
  - name: keywords
    content: "workspaces, organize connections, share configuration, AxonOps Workbench"
---

# Workspaces

Workspaces are organizational containers in AxonOps Workbench that let you group related database connections together. Think of them as projects -- each workspace can hold multiple connections, making it straightforward to separate development, staging, and production environments or to organize connections by team or application.

## What is a Workspace?

Every connection in AxonOps Workbench belongs to a workspace. When you first launch the application, a default sandbox workspace is available for quick experimentation. Beyond that, you can create as many workspaces as you need, each with its own name, color, storage path, and set of connections.

Workspaces provide:

- **Logical grouping** of connections by project, environment, or team
- **Visual identification** through customizable colors
- **Flexible storage** with default or custom directory paths
- **Portability** through import and export capabilities

## Creating a Workspace

To create a new workspace:

1. Open the workspace management area from the left sidebar.
2. Click the button to add a new workspace.
3. Fill in the workspace details:

    - **Name** -- A unique name for the workspace. This name is also used to generate the workspace folder name on disk.
    - **Color** -- Choose a color to visually distinguish this workspace from others. A color picker is provided for precise selection.
    - **Path** -- Select where workspace data should be stored. You can use the default data directory or specify a custom path on your filesystem.

4. Confirm creation. The workbench creates a dedicated folder for the workspace and initializes a `connections.json` manifest inside it.

!!! note
    Workspace names must be unique. If you attempt to create a workspace with a name that already exists, the operation will be rejected.

## Workspace Colors

Each workspace can be assigned a color that appears throughout the interface, making it easy to identify which workspace you are working in at a glance. This is particularly useful when managing many workspaces simultaneously.

The color picker supports any standard color format, including HEX (e.g., `#FF5733`), RGB, and HSL values.

<!-- Screenshot: Workspace color picker showing a workspace with a custom color applied -->

## Managing Workspaces

### Switching Workspaces

The workspace switcher in the left sidebar displays all available workspaces. Click on any workspace to switch to it and view its connections. Workspaces are sorted alphabetically for easy navigation.

### Editing a Workspace

You can update a workspace's name, color, or storage path at any time:

1. Select the workspace you want to edit.
2. Open the edit dialog.
3. Modify the desired fields.
4. Save your changes.

When you rename a workspace or change its storage path, the workbench automatically moves the workspace folder and all its contents to the new location.

### Deleting a Workspace

When you delete a workspace, the workbench removes:

- The workspace entry from the master `workspaces.json` manifest
- The workspace folder and all files within it, including connection data

!!! warning
    Deleting a workspace permanently removes all connections and associated data stored within it. This action cannot be undone.

## Storage

Workspace data is stored as JSON files on your local filesystem. The overall structure is:

```
data/
  workspaces/
    workspaces.json          # Master manifest listing all workspaces
    my-project/              # Individual workspace folder
      connections.json       # Connections manifest for this workspace
      _snippets/             # CQL snippets scoped to this workspace
      connection-folder-1/   # Data for a specific connection
      connection-folder-2/
    another-workspace/
      connections.json
      ...
```

### Default Path vs. Custom Path

- **Default path** -- Workspace folders are created inside the application's built-in `data/workspaces/` directory. This is the simplest option and works well for most users.
- **Custom path** -- You can specify any accessible directory on your filesystem. This is useful when you want to store workspace data on a shared drive, a specific partition, or alongside your project source code.

The `workspaces.json` master manifest tracks the location of each workspace, recording whether it uses the default path or a custom one.

## Sharing Workspaces

Workspaces are portable. Because all workspace data is stored as standard JSON files in a well-defined folder structure, you can share workspaces with team members or transfer them between machines.

### Exporting a Workspace

To share a workspace, copy its folder from the data directory. The folder contains everything needed to recreate the workspace: connection definitions, snippets, and configuration.

### Importing a Workspace via the CLI

AxonOps Workbench provides command-line arguments for importing workspaces programmatically:

**Import from a JSON string:**

```bash
./axonops-workbench --import-workspace='{"name":"Production", "color":"#FF5733"}'
```

**Import from a JSON file:**

```bash
./axonops-workbench --import-workspace=/path/to/workspace.json
```

**Import from an existing workspace folder:**

```bash
./axonops-workbench --import-workspace=/path/to/workspace-folder/
```

When importing from a folder path, the workbench detects workspaces (including nested workspace folders one level deep) and imports them along with their connections.

### Additional CLI Flags

| Flag | Description |
|------|-------------|
| `--copy-to-default` | Copies the imported workspace folder into the default data directory. Without this flag, folder-based imports reference the workspace at its original path. |
| `--delete-file` | Deletes the source JSON file after a successful import. Ignored when the source is a folder. |
| `--json` | Outputs import results as a JSON string instead of formatted text, useful for scripting and automation. |

**Example -- automated import with cleanup:**

```bash
./axonops-workbench --import-workspace=/path/to/workspace.json --copy-to-default --delete-file
```

### Source Control

Because workspace data is stored as plain JSON files, you can commit workspace configurations to version control. This enables teams to share a consistent set of connection definitions across environments.

!!! tip
    When sharing workspace configurations through source control, be mindful of sensitive data such as credentials. Connection files may contain authentication details that should not be committed to a repository. Consider using SSH key-based authentication or environment-specific configuration to avoid exposing secrets.

### Listing Workspaces via the CLI

To view all saved workspaces from the command line:

```bash
./axonops-workbench --list-workspaces
```

Add `--json` for machine-readable output:

```bash
./axonops-workbench --list-workspaces --json
```
