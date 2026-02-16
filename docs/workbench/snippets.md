---
title: "CQL Snippets"
description: "Save, organize, and reuse CQL queries as snippets in AxonOps Workbench. Scope snippets to workspaces, connections, keyspaces, or tables."
meta:
  - name: keywords
    content: "CQL snippets, save queries, reuse, templates, AxonOps Workbench"
---

# CQL Snippets

CQL Snippets let you save, organize, and reuse CQL queries directly within AxonOps Workbench. Each snippet is stored as a `.cql` file with YAML frontmatter metadata, making snippets both human-readable and easy to manage outside the application.

## What are Snippets?

A snippet is a saved CQL query paired with metadata such as a title, author, creation date, and optional scope. Snippets serve as reusable templates for queries you run frequently -- schema inspection statements, common data lookups, administrative commands, or any CQL you want to keep at hand.

Key characteristics of snippets:

- Stored as individual `.cql` files on disk
- Include YAML frontmatter with metadata (title, author, date, associations)
- Can be scoped to different levels of your workspace hierarchy
- Accessible from a dedicated sidebar panel

## Creating a Snippet

To create a new snippet:

1. Write or paste your CQL query in the CQL Console.
2. Save the query as a snippet using the save action.
3. Provide a title for the snippet. The title is used to generate the filename on disk.
4. Select the scope level (workspace, connection, keyspace, or table) to control where the snippet appears.

The snippet is saved as a `.cql` file in a `_snippets` folder within the appropriate workspace directory. A random identifier is appended to the filename to prevent naming conflicts.

### Author Name

Each snippet records an author name in its metadata. You can configure the default author name in **Settings > Features** under the **CQL Snippets Author Name** field. When set, this name is automatically included in every new snippet you create.

## Snippet Scoping

Snippets can be associated with different levels of your workspace hierarchy. The scope determines where a snippet appears in the sidebar tree and which context it is relevant to.

| Scope | Description | Visible From |
|-------|-------------|--------------|
| **Workspace** | Available across all connections in the workspace | Workspace node in the snippets tree |
| **Connection** | Tied to a specific cluster connection | Connection node and below |
| **Keyspace** | Associated with a particular keyspace | Keyspace node and its tables |
| **Table** | Scoped to a specific table | Table node only |

The scoping mechanism uses an `associated_with` array in the snippet's frontmatter:

- An empty or absent `associated_with` field means the snippet is scoped to the workspace level.
- A single-element array `[connectionID]` scopes the snippet to a specific connection.
- A two-element array `[connectionID, keyspaceName]` scopes it to a keyspace.
- A three-element array `[connectionID, keyspaceName, tableName]` scopes it to a table.

This hierarchical scoping keeps your snippet library organized as it grows, ensuring that relevant queries appear in the right context.

## File Format

Snippets are plain-text `.cql` files with YAML frontmatter at the top. Here is an example:

```sql
---
title: Find large partitions
author: Jane Smith
created_date: 2025-01-15T10:30:00Z
associated_with:
  - connection-a1b2c3d4
  - my_keyspace
---
SELECT token(id), id, partition_size
FROM my_keyspace.my_table
WHERE token(id) > ?
LIMIT 100;
```

The frontmatter section (between the `---` markers) contains:

| Field | Description |
|-------|-------------|
| `title` | Display name for the snippet |
| `author` | Name of the snippet creator |
| `created_date` | ISO 8601 timestamp of when the snippet was created |
| `associated_with` | Array defining the snippet's scope (see Snippet Scoping above) |

Everything after the closing `---` marker is the CQL query body.

## Managing Snippets

### Browsing Snippets

The snippets sidebar presents your saved snippets in a tree view that mirrors your workspace structure:

- **Workspaces** -- Top-level node listing all workspaces
- **Connections** -- Each connection within a workspace, expandable to show keyspaces and tables
- **Orphaned Snippets** -- A dedicated section for snippets whose associated connection no longer exists

Expanding a node in the tree loads the connection's metadata (keyspaces and tables) so you can browse snippets at every level.

<!-- Screenshot: Snippets sidebar tree view showing workspaces, connections, keyspaces, and tables -->

### Editing a Snippet

To update an existing snippet:

1. Select the snippet from the sidebar.
2. Modify the CQL query or metadata as needed.
3. Save the changes. The updated content is written back to the same `.cql` file on disk.

### Deleting a Snippet

To remove a snippet, select it and choose the delete action. This permanently removes the `.cql` file from the filesystem.

!!! warning
    Deleting a snippet is irreversible. The file is removed from disk and cannot be recovered through the application.

### Orphaned Snippets

When a connection is deleted but its associated snippets remain on disk, those snippets become orphaned. AxonOps Workbench automatically detects orphaned snippets and displays them under the **Orphaned Snippets** section in the sidebar tree.

Orphaned snippets occur when:

- A connection has been removed from the workspace
- The snippet's `associated_with` references a connection ID that no longer exists

You can review orphaned snippets to decide whether to delete them or reassign them by editing their frontmatter.

## Storage Location

Snippets are stored in `_snippets` folders within the workspace directory structure:

```
data/
  workspaces/
    _snippets/                        # Global snippets
      my-query-a1b2.cql
    my-workspace/
      _snippets/                      # Workspace-level snippets
        find-large-partitions-c3d4.cql
        check-compaction-e5f6.cql
      connections.json
```

Workspace-level and connection-scoped snippets reside in the `_snippets` folder inside the workspace directory. The scope is determined by the `associated_with` metadata within each file, not by the file's physical location.

!!! tip
    Because snippets are plain `.cql` files with readable frontmatter, you can create, edit, or organize them using any text editor. This also makes it straightforward to share snippets with your team through version control or file sharing.
