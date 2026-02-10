---
title: "Schema Management"
description: "Browse, create, alter, and compare database schemas in AxonOps Workbench. Visual metadata tree with DDL generation."
meta:
  - name: keywords
    content: "schema browser, DDL, metadata, keyspace, table, UDT, schema diff, AxonOps Workbench"
---

# Schema Management

AxonOps Workbench provides a comprehensive set of tools for exploring, creating, modifying, and comparing Cassandra schemas. The metadata browser gives you a navigable tree view of your entire cluster schema, while visual dialogs let you build and alter schema objects without writing CQL by hand. A built-in schema diff editor rounds out the toolset by letting you compare schema versions side by side.

<!-- Screenshot: Schema management overview showing the metadata tree on the left and a work area on the right -->

---

## Metadata Browser

The metadata browser presents your cluster's schema as an interactive tree view in the left panel of each connection's work area. It organizes all schema objects into a hierarchical structure that mirrors the logical layout of your Cassandra data model.

### Tree View Hierarchy

Each connected cluster displays its schema in the following hierarchy:

- **Keyspaces** -- the top-level containers for all schema objects
    - **Replication Strategy** -- the keyspace's replication configuration (strategy class, replication factor, datacenter mapping)
    - **Tables** -- all standard tables within the keyspace, with a count indicator
        - **Counter Tables** -- tables containing `counter` columns are grouped separately for easy identification
        - For each table:
            - **Primary Key** -- the full primary key with partition and clustering columns identified
            - **Partition Key** -- the partition key columns
            - **Clustering Keys** -- the clustering key columns
            - **Static Columns** -- columns declared as `STATIC`
            - **Columns** -- all columns with their CQL data types, including partition key, clustering key, and regular columns
            - **Compaction** -- the compaction strategy and related settings such as `bloom_filter_fp_chance`
            - **Options** -- table-level options including compression, caching, TTL, and gc_grace_seconds
            - **Triggers** -- any triggers attached to the table
            - **Views** -- materialized views based on the table, each with its own partition key, clustering keys, and column breakdown
    - **Indexes** -- secondary indexes defined in the keyspace, showing index kind (e.g., composites, keys, custom) and the associated table
    - **User Defined Types** -- UDTs with their field names and types
    - **User Defined Functions** -- UDFs with attributes for determinism, monotonicity, null-input handling, language, return type, and arguments
    - **User Defined Aggregates** -- UDAs with their state function, final function, state type, and arguments

<!-- Screenshot: Metadata tree expanded to show a keyspace with tables, columns, indexes, UDTs, functions, and aggregates -->

### System Keyspaces

AxonOps Workbench automatically identifies and groups Cassandra's internal system keyspaces into a dedicated **System Keyspaces** node at the top of the tree. The recognized system keyspaces are:

- `system`
- `system_auth`
- `system_distributed`
- `system_schema`
- `system_traces`

System keyspaces are visually separated from your application keyspaces, keeping the tree focused on the schema you work with day to day. Certain operations -- such as dropping a keyspace -- are disabled for system keyspaces to prevent accidental damage.

### Right-Click Context Menu

Right-clicking on a node in the metadata tree opens a context menu with actions appropriate to that node type. The available actions are organized into DDL (schema) and DML (data) categories.

**Keyspaces node (root):**

| Action | Description |
|--------|-------------|
| Create Keyspace | Open the keyspace creation dialog |

**Keyspace node:**

| Action | Description |
|--------|-------------|
| Create UDT | Open the UDT creation dialog for this keyspace |
| Create Table | Open the table creation dialog for this keyspace |
| Create Counter Table | Open the counter table creation dialog |
| Alter Keyspace | Open the keyspace alteration dialog |
| Drop Keyspace | Drop the keyspace (with confirmation) |

**Table node:**

| Action | Description |
|--------|-------------|
| Alter Table | Open the table alteration dialog |
| Drop Table | Drop the table (with confirmation) |
| Truncate Table | Remove all data from the table (with confirmation) |
| Insert Row | Open the row insertion dialog |
| Insert Row as JSON | Open the JSON row insertion dialog |
| Select Row | Generate a SELECT query for this table |
| Select Row as JSON | Generate a SELECT JSON query for this table |
| Delete Row/Column | Open the row or column deletion dialog |

**Counter table node:**

| Action | Description |
|--------|-------------|
| Increment/Decrement Counter(s) | Open the counter update dialog |

**UDT node:**

| Action | Description |
|--------|-------------|
| Alter UDT | Open the UDT alteration dialog |
| Drop UDT | Drop the UDT (with confirmation) |

!!! tip
    Right-click context menus are also available on container nodes such as the **Tables** and **User Defined Types** groups, giving you quick access to create new objects within a keyspace without first selecting the keyspace itself.

### Refreshing Metadata

After making schema changes -- whether through the CQL Console or the visual dialogs -- you can refresh the metadata tree to reflect the latest state of your cluster. This re-fetches the full cluster metadata and rebuilds the tree view.

---

## DDL Generation

AxonOps Workbench can generate the `CREATE` statement (DDL) for any schema object in your cluster. This is the same output you would get from running `DESCRIBE` or `DESC` commands in CQLSH, but available directly from the UI.

### Generating DDL

Right-click on any keyspace, table, or the cluster root node in the metadata tree and select the CQL description option. The Workbench retrieves the DDL through its internal `getDDL` method, which supports scoping to:

- **Cluster** -- generates `CREATE KEYSPACE` and `CREATE TABLE` statements for the entire cluster
- **Keyspace** -- generates all DDL within a single keyspace
- **Table** -- generates the `CREATE TABLE` statement for a specific table

The generated DDL is displayed in a syntax-highlighted editor panel where you can review, copy, or export it.

### DESCRIBE Commands

You can also generate DDL by running `DESCRIBE` (or `DESC`) commands directly in the CQL Console:

```sql
-- Describe the entire cluster
DESCRIBE CLUSTER;

-- Describe a specific keyspace
DESCRIBE KEYSPACE my_keyspace;

-- Describe a specific table
DESC TABLE my_keyspace.my_table;
```

The output is syntax-highlighted in the results panel, making it easy to read and copy.

!!! info
    The `DESCRIBE` and `DESC` keywords are interchangeable. Both are recognized by the CQL Console's auto-completion and syntax highlighting.

---

## Schema Diff

The schema diff tab provides a Monaco-powered side-by-side diff editor for comparing schema definitions. It is accessible from the **Schema Diff** tab in the connection work area.

<!-- Screenshot: Schema diff tab showing two versions of a CREATE TABLE statement compared side by side -->

### How It Works

The schema diff editor uses the same Monaco diff view found in VS Code, highlighting additions, deletions, and modifications between two schema texts. Paste or load the DDL for two versions of a schema object, and the diff editor renders an inline comparison with:

- **Green highlights** for added lines
- **Red highlights** for removed lines
- **Inline character-level diffs** for modified lines

### Use Cases

Schema diff is valuable in several scenarios:

- **Comparing environments** -- Paste the DDL from a staging keyspace on the left and the production keyspace on the right to identify discrepancies before a deployment.
- **Tracking schema changes** -- Compare the current DDL of a table against a previously saved version to review what has changed over time.
- **Reviewing migrations** -- Validate that a migration script produces the expected schema by comparing the before and after states.
- **Auditing drift** -- Detect unintended schema differences across clusters that should be identical.

!!! tip
    Use the DDL generation feature to quickly obtain the `CREATE` statements you want to compare, then paste them into the schema diff editor.

---

## Creating Schema

AxonOps Workbench provides visual creation dialogs for keyspaces, tables, counter tables, and user-defined types. Each dialog generates the corresponding CQL statement and places it in the CQL Console editor, where you can review it before executing.

### Keyspaces

To create a new keyspace, right-click on the **Keyspaces** root node in the metadata tree and select **Create Keyspace**.

The keyspace creation dialog includes:

- **Keyspace name** -- must be unique within the cluster
- **Replication strategy** -- choose between `SimpleStrategy` and `NetworkTopologyStrategy`
- **Replication factor** -- for `SimpleStrategy`, a single replication factor; for `NetworkTopologyStrategy`, a replication factor per datacenter

The dialog is pre-populated with the datacenters detected from your connected cluster, making `NetworkTopologyStrategy` configuration straightforward.

!!! warning
    `SimpleStrategy` is intended for development purposes only. For production deployments and multi-datacenter clusters, always use `NetworkTopologyStrategy`. Avoid switching from `SimpleStrategy` to `NetworkTopologyStrategy` in multi-DC clusters without careful planning.

### Tables

To create a table, right-click on a keyspace or its **Tables** container node and select **Create Table**.

The table creation dialog provides a visual interface for defining:

- **Table name** -- must be unique within the keyspace
- **Columns** -- add columns with names, CQL data types, and optional UDT types from the keyspace
- **Primary key** -- designate partition key and clustering key columns
- **Clustering order** -- set ascending or descending sort order for each clustering column

#### Version-Specific Metadata Defaults

When creating a table, AxonOps Workbench applies sensible default metadata values that correspond to your connected Cassandra version. The following defaults are applied for Cassandra 4.0, 4.1, and 5.0:

| Property | Default Value |
|----------|---------------|
| `additional_write_policy` | `99p` |
| `bloom_filter_fp_chance` | `0.01` |
| `caching` | `{"keys": "ALL", "rows_per_partition": "NONE"}` |
| `compaction` | `SizeTieredCompactionStrategy` (min threshold: 4, max: 32) |
| `compression` | `LZ4Compressor` (chunk length: 16 KB) |
| `crc_check_chance` | `1.0` |
| `default_time_to_live` | `0` |
| `gc_grace_seconds` | `864000` (10 days) |
| `max_index_interval` | `2048` |
| `memtable_flush_period_in_ms` | `0` |
| `min_index_interval` | `128` |
| `read_repair` | `BLOCKING` |
| `speculative_retry` | `99p` |

These defaults match the Apache Cassandra defaults for each respective version and can be customized in the creation dialog before generating the CQL statement.

### Counter Tables

Counter tables have special constraints in Cassandra -- non-key columns must use the `counter` data type, and counter columns cannot be mixed with non-counter columns. AxonOps Workbench provides a dedicated **Create Counter Table** option (available from the keyspace, Tables container, or Counter Tables container context menu) that enforces these constraints in the visual dialog.

### User-Defined Types (UDTs)

To create a UDT, right-click on a keyspace or its **User Defined Types** container node and select **Create UDT**.

The UDT creation dialog lets you:

- **Name the type** -- must be unique within the keyspace
- **Define fields** -- add fields with names and CQL data types
- **Reference other UDTs** -- fields can use other UDTs already defined in the same keyspace as their type

The dialog lists all existing UDTs in the keyspace so you can reference them when defining nested types.

!!! note
    If the keyspace has no existing UDTs, the dialog will indicate that no UDT types are available for field references. You can still create a UDT using only native CQL data types.

---

## Altering Schema

AxonOps Workbench provides visual dialogs for modifying existing schema objects. Like the creation dialogs, each alteration dialog generates the appropriate CQL statement and places it in the CQL Console for review before execution.

### Altering Keyspaces

Right-click on a keyspace node and select **Alter Keyspace** to open the alteration dialog. You can modify:

- **Replication strategy** -- switch between `SimpleStrategy` and `NetworkTopologyStrategy`
- **Replication factor** -- adjust the replication factor for the selected strategy

!!! warning
    Changing replication strategy or factor on a production keyspace requires running `nodetool repair` on all nodes to ensure data consistency. Plan these changes carefully, especially in multi-datacenter environments.

The keyspace name cannot be changed through the alter dialog. To rename a keyspace, you must create a new keyspace and migrate the data.

### Altering Tables

Right-click on a table node and select **Alter Table** to open the alteration dialog. Supported modifications include:

- **Adding columns** -- define new columns with name and data type
- **Dropping columns** -- remove existing non-key columns
- **Modifying table properties** -- change options such as compaction strategy, compression, caching, TTL defaults, and `gc_grace_seconds`

!!! danger
    Dropping a column removes all data stored in that column across all rows. This operation is irreversible. Always verify your intent before executing the generated `ALTER TABLE` statement.

The table name and primary key columns cannot be changed after creation. These are fundamental to Cassandra's data distribution and storage model.

### Altering User-Defined Types

Right-click on a UDT node and select **Alter UDT** to open the alteration dialog. You can:

- **Add new fields** -- extend the type with additional fields
- **Rename fields** -- change the name of existing fields

The UDT name itself cannot be altered. If you need to rename a UDT, you must create a new type, migrate your data, and drop the old type.

!!! note
    When altering a UDT, the dialog shows all existing UDTs in the keyspace (excluding the one being altered) for use as field types. If the keyspace contains only the UDT being modified, no UDT field types will be available for reference.

### Dropping Schema Objects

The following schema objects can be dropped through the right-click context menu:

- **Keyspaces** -- `DROP KEYSPACE` (not available for system keyspaces)
- **Tables** -- `DROP TABLE`
- **UDTs** -- `DROP TYPE`

Each drop action displays a confirmation dialog that clearly names the object being dropped and warns that the action is irreversible. The generated CQL statement is placed in the console for review before execution.

### Truncating Tables

The **Truncate Table** option removes all rows from a table while preserving the table structure. This is available from the table right-click context menu and also requires confirmation before execution.

---

## Best Practices

- **Refresh metadata after changes** -- Always refresh the metadata tree after creating, altering, or dropping schema objects to ensure the tree reflects the current cluster state.
- **Review generated CQL** -- The visual dialogs place generated statements in the CQL Console rather than executing them directly. Take advantage of this to review and adjust the CQL before running it.
- **Use schema diff before deploying** -- Compare staging and production schemas before applying migrations to catch unintended differences.
- **Back up DDL regularly** -- Use the DDL generation feature to export and version-control your schema definitions.
- **Prefer NetworkTopologyStrategy** -- For any cluster that may grow beyond a single datacenter, start with `NetworkTopologyStrategy` to avoid a disruptive migration later.
