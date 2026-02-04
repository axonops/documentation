---
title: "First Steps"
description: "Create your first workspace, connect to a Cassandra cluster, and run your first CQL query in AxonOps Workbench."
meta:
  - name: keywords
    content: "getting started, first steps, create workspace, connect Cassandra, first query, AxonOps Workbench"
---

# First Steps

This guide walks you through your first session with AxonOps Workbench -- from creating a workspace and connecting to a Cassandra cluster, to browsing your schema and running your first CQL query.

---

## 1. Create a Workspace

Workspaces are organizational containers that group related connections, much like projects in an IDE. You might create separate workspaces for different environments (Development, Staging, Production) or different teams and applications.

Each workspace is stored as a folder on disk containing a `connections.json` manifest and individual connection configuration folders. This makes workspaces portable and easy to share through version control.

### Steps

1. From the home screen, click the **+** button in the bottom-right corner of the workspaces panel, or click the prompt in the center of an empty workspaces list.
2. In the **Add Workspace** dialog, enter a **Workspace Name** -- for example, `Development`.
3. Choose a **Workspace Color** to visually distinguish this workspace in the sidebar. Click the color field to open the color picker.
4. Optionally, set a custom **Workspace Path** by clicking the folder icon next to the path field. To revert to the default storage location, click the reset icon.
5. Click **Add Workspace** to save.

<!-- Screenshot: Add Workspace dialog with name, color, and path fields -->

Your new workspace appears on the home screen. Click it to open it and begin adding connections.

!!! info
    By default, workspace data is stored in the application's internal data directory. Setting a custom path is useful when you want to keep workspace configurations alongside a project repository or share them with your team.

---

## 2. Add a Connection

With your workspace open, you can add connections to Apache Cassandra, DataStax Enterprise, or DataStax Astra DB clusters.

### Apache Cassandra / DataStax Enterprise

1. Click the **+** button in the bottom-right corner of the connections panel, or click the prompt in the center of an empty connections list.
2. In the **Add Connection** dialog, ensure **Apache Cassandra** is selected at the top.
3. In the **Basic** section, fill in the following fields:

    | Field | Description | Required |
    | --- | --- | --- |
    | **Connection Name** | A display name for this connection (e.g., `Local Dev Node`) | Yes |
    | **Cassandra Data Center** | The datacenter name (e.g., `datacenter1`) | No |
    | **Cassandra Hostname** | The IP address or hostname of a Cassandra node (e.g., `192.168.0.10` or `localhost`) | Yes |
    | **Port** | The CQL native transport port (default: `9042`) | Yes |

4. If your cluster requires authentication, click the **Authentication** section on the left side of the dialog, then enter your **Username** and **Password**. The *Save authentication credentials locally* option stores credentials securely in your operating system's keychain.
5. Click **Test Connection** to verify that the Workbench can reach your cluster with the provided settings.
6. Once the test succeeds, click **Add Connection** to save.

<!-- Screenshot: Add Connection dialog for Apache Cassandra showing the Basic section with hostname and port fields -->

### DataStax Astra DB

1. Click the **+** button to open the **Add Connection** dialog.
2. Select **DataStax AstraDB** at the top of the dialog.
3. Fill in the following fields:

    | Field | Description |
    | --- | --- |
    | **Connection Name** | A display name for this Astra DB connection |
    | **Username (Client ID)** | The Client ID from your Astra DB application token |
    | **Password (Client Secret)** | The Client Secret from your Astra DB application token |
    | **Secure Connection Bundle** | The Secure Connect Bundle (SCB) ZIP file downloaded from the Astra DB console |

4. To provide the SCB file, click the file selector field and browse to the ZIP file on disk. You can also drag and drop the bundle file directly onto the field.
5. Click **Test Connection** to verify, then click **Add Connection** to save.

<!-- Screenshot: Add Connection dialog for DataStax Astra DB showing Client ID, Client Secret, and SCB fields -->

!!! tip
    The connection dialog also provides sections for **SSH Tunnel**, **SSL Configuration**, and **AxonOps Integration**. For detailed instructions on these advanced options, see the [Connections](../connections/index.md) guide and the [SSH Tunneling](../connections/ssh-tunneling.md) page.

---

## 3. Browse Your Schema

Once connected, AxonOps Workbench loads your cluster's metadata and displays it in an interactive tree view.

### The Metadata Tree

The metadata tree appears in the left panel of the work area after you open a connection. It provides a hierarchical view of your cluster's schema:

- **Keyspaces** -- Top-level nodes representing each keyspace in the cluster
    - **Tables** -- The tables within each keyspace
        - **Columns** -- Individual column definitions with data types
    - **Materialized Views** -- Any materialized views defined in the keyspace
    - **User-Defined Types (UDTs)** -- Custom types created in the keyspace
    - **Indexes** -- Secondary indexes defined on tables

### Navigating the Tree

- **Expand** a node by clicking the arrow icon next to it, or by double-clicking the node name.
- **Search** the tree using the search bar at the top of the metadata panel. Results are highlighted as you type, and you can navigate between matches using the up/down arrows.
- **Refresh** the metadata tree by clicking the refresh button at the bottom of the panel. This reloads the schema from the cluster, picking up any changes made outside the Workbench.

<!-- Screenshot: Metadata tree showing expanded keyspace with tables, columns, and UDTs -->

!!! tip
    Right-clicking on a keyspace, table, or other schema object opens a context menu with actions such as creating new objects within that keyspace. You can also use the `DESCRIBE` command in the CQL Console to retrieve the full DDL statement for any schema object.

---

## 4. Run Your First Query

With a connection open, you are ready to execute CQL statements against your cluster.

### Open the CQL Editor

The CQL editor is the main work area that appears when you open a connection. It provides syntax highlighting, auto-completion, and multi-tab support so you can work with several queries simultaneously.

### Execute a Query

1. Click in the editor area and type a simple CQL query, for example:

    ```sql
    SELECT * FROM system_schema.keyspaces;
    ```

2. Click the **Execute** button, or use the keyboard shortcut displayed next to the button.
3. The results appear in a table below the editor, showing column names as headers and rows of data.

<!-- Screenshot: CQL editor with a SELECT query and results displayed in the table below -->

### Working with Results

- **Pagination** -- For queries that return large result sets, the Workbench paginates the output automatically. The default page size is 100 rows, which you can configure in the connection settings. Use the navigation controls below the results table to move between pages.
- **Export** -- Query results can be exported to CSV, JSON, or other formats for further analysis.
- **Multi-tab** -- Open additional editor tabs to work on multiple queries without losing your place. Each tab maintains its own query text, execution history, and results.

!!! info
    The page size for query results is configured per connection. You can adjust it in the **Basic** section of the connection dialog under the **Page Size** field (default: `100`).

---

## Next Steps

Now that you have a workspace, a connection, and your first query results, explore the rest of what AxonOps Workbench has to offer:

- **[CQL Console](../cql-console/index.md)** -- Discover advanced editor features including auto-completion, query history, and query tracing.
- **[Local Clusters](local-clusters.md)** -- Spin up local Cassandra clusters with Docker or Podman for development and testing.
- **[SSH Tunneling](../connections/ssh-tunneling.md)** -- Connect to clusters behind firewalls or in private subnets through an SSH bastion host.
- **[CQL Snippets](../snippets.md)** -- Save, organize, and reuse frequently used CQL statements across sessions and workspaces.
