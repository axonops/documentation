---
title: "Query Execution"
description: "Execute CQL queries in AxonOps Workbench. Run single or multiple statements, use the SOURCE command, paginate results, and query history."
meta:
  - name: keywords
    content: "CQL query, execute, SOURCE command, pagination, query history, destructive warning, AxonOps Workbench"
---

# Query Execution

AxonOps Workbench provides a full-featured CQL execution environment that goes well beyond a basic query runner. You can execute single statements or batches, run CQL scripts from external files, page through large result sets, and recall previously executed queries from a searchable history -- all within the CQL Console.

---

## Running Queries

### Single Statement

To execute a single CQL statement, type it into the editor and press the **Execute** button or use the keyboard shortcut:

| Platform | Shortcut |
| --- | --- |
| **macOS** | <kbd>Cmd</kbd> + <kbd>Enter</kbd> |
| **Windows / Linux** | <kbd>Ctrl</kbd> + <kbd>Enter</kbd> |

The result is displayed directly beneath the statement in the interactive terminal area. For `SELECT` queries, results are rendered in a tabular format. For data-modification and schema-change statements, Workbench confirms that the CQL statement was executed successfully.

<!-- Screenshot: Single SELECT query with tabular results displayed below the editor -->

### Multiple Statements

You can write several CQL statements in a single editor block, separated by semicolons. When you execute, Workbench sends all statements to the server and processes them sequentially. Each statement's output is displayed in order within the results area.

```sql
CREATE KEYSPACE IF NOT EXISTS demo
  WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE demo;

CREATE TABLE IF NOT EXISTS users (
  user_id uuid PRIMARY KEY,
  name text,
  email text
);

INSERT INTO users (user_id, name, email)
  VALUES (uuid(), 'Alice', 'alice@example.com');

SELECT * FROM users;
```

If an error occurs during execution, Workbench stops processing at the failed statement and reports the error, leaving subsequent statements unexecuted.

!!! tip
    Keep related statements together in a single block for scripting workflows such as schema migrations or seed data inserts.

---

## SOURCE Command

The `SOURCE` command lets you execute CQL statements stored in an external file, directly from the Workbench console. This is useful for running migration scripts, seed data files, or any reusable CQL that you maintain outside the editor.

### Syntax

```sql
SOURCE '/path/to/file.cql';
```

The file path must be an absolute path enclosed in single quotes. The file should contain valid CQL statements separated by semicolons, just as you would write them in the editor.

### Executing CQL Files

You can also execute CQL files through the **Execute File** button in the session action bar. This opens a file picker dialog where you can select one or more `.cql` or `.sql` files to run.

<!-- Screenshot: Execute File dialog with file picker and stop-on-error toggle -->

### Progress Tracking

When executing a file, Workbench displays real-time progress as each statement in the file is processed. The results area shows which statements have completed and whether they succeeded or failed.

### Stop on Error

By default, file execution halts when a statement produces an error. This **stop-on-error** behavior prevents cascading failures -- for example, if a `CREATE TABLE` statement fails, subsequent `INSERT` statements that depend on that table are not attempted.

You can toggle stop-on-error from the execution dialog when running files.

!!! note
    The `SOURCE` command is a CQLSH shell command, not a CQL statement. It is processed by the Workbench session layer rather than sent directly to the Cassandra server.

---

## Destructive Command Safety

AxonOps Workbench identifies potentially destructive CQL commands and displays a warning before they are executed. This safety mechanism helps prevent accidental data loss or unintended schema changes, particularly in production environments.

!!! warning
    Always double-check the target keyspace and table before confirming a destructive operation. Destructive commands may cause irreversible data loss.

### Protected Commands

The following CQL commands are classified as destructive and trigger a confirmation prompt:

| Command | Risk |
| --- | --- |
| `DELETE` | Removes rows or columns from a table |
| `DROP` | Removes keyspaces, tables, indexes, or other schema objects |
| `TRUNCATE` | Removes all data from a table |
| `INSERT` | Adds or overwrites rows (upsert behavior in Cassandra) |
| `UPDATE` | Modifies existing row data |
| `ALTER` | Changes keyspace or table schema |
| `BATCH` | Groups multiple modification statements |
| `CREATE` | Creates new schema objects (protected because it can alter cluster state) |
| `GRANT` | Assigns permissions to roles |
| `REVOKE` | Removes permissions from roles |

When a destructive command is detected, Workbench displays a confirmation dialog. You must explicitly confirm the action before the statement is sent to the server.

The destructive command warning also appears inline in the CQL Snippets editor when a snippet contains any of the protected commands, alerting you before you save or execute the snippet.

---

## Query History

Workbench automatically records every CQL statement you execute, building a per-connection history that you can search and re-execute at any time.

### Browsing History

You can navigate through your query history directly from the editor using keyboard shortcuts:

| Action | Platform | Shortcut |
| --- | --- | --- |
| **Previous statement** | macOS | <kbd>Cmd</kbd> + <kbd>Up Arrow</kbd> |
| | Windows / Linux | <kbd>Ctrl</kbd> + <kbd>Up Arrow</kbd> |
| **Next statement** | macOS | <kbd>Cmd</kbd> + <kbd>Down Arrow</kbd> |
| | Windows / Linux | <kbd>Ctrl</kbd> + <kbd>Down Arrow</kbd> |

Each press of the shortcut replaces the current editor content with the next or previous statement from your history, allowing you to cycle through past queries rapidly.

### History Panel

Click the **History** button in the session action bar to open the full history panel. This panel displays a numbered list of previously executed statements for the current connection, with the most recent entries at the top.

From the history panel you can:

- Browse the complete list of past statements
- Click any entry to load it into the editor for re-execution
- Clear the entire history for the current connection

<!-- Screenshot: History panel showing a list of previously executed CQL statements -->

!!! info
    Workbench stores up to **30 statements** per connection. When the limit is reached, the oldest entry is removed to make room for new ones. Duplicate statements are automatically deduplicated.

---

## Pagination

Cassandra queries can return very large result sets. Workbench uses cursor-based pagination to retrieve results in manageable pages, preventing excessive memory usage and keeping the interface responsive.

### How Pagination Works

When you execute a `SELECT` query, Workbench fetches the first page of results based on the configured page size. If additional rows are available beyond the current page, a **Fetch next page** button appears below the results table. Each click retrieves the next page from the server using the Cassandra driver's cursor, and appends the new rows to the existing result set.

Pagination continues until all matching rows have been retrieved or you choose to stop fetching.

<!-- Screenshot: Results table with "Fetch next page" button visible below the data -->

### Configuring Page Size

The page size determines how many rows are returned per page. You can view and change the current page size from the **Page Size** indicator in the session action bar.

To change the page size:

1. Click the **Page Size** button in the session action bar.
2. Enter the desired number of rows per page in the input field.
3. Click **Change paging size** to apply.

Alternatively, you can set the page size directly using the CQLSH `PAGING` command in the editor:

```sql
PAGING 200;
```

To check the current paging status:

```sql
PAGING;
```

To disable paging entirely:

```sql
PAGING OFF;
```

!!! tip
    A page size of **100** is the default. For tables with wide rows or large column values, consider using a smaller page size to keep response times fast. For narrow result sets, a larger page size reduces the number of fetches needed.

### Last Page Navigation

When all pages have been fetched, a **Last** button appears next to the pagination controls, allowing you to jump directly to the final page of results in the table view.

---

## Consistency Level

Workbench allows you to set the consistency level for your queries, controlling how many replicas must respond before a result is returned to the client.

### Setting the Consistency Level

Click the **Consistency Level** indicator in the session action bar to select from the available levels:

**Regular consistency levels:**

- `ANY`
- `LOCAL_ONE`
- `ONE`
- `TWO`
- `THREE`
- `QUORUM`
- `LOCAL_QUORUM`
- `EACH_QUORUM`
- `ALL`

**Serial consistency levels (for lightweight transactions):**

- `SERIAL`
- `LOCAL_SERIAL`

You can also set the consistency level using the CQLSH `CONSISTENCY` command:

```sql
CONSISTENCY QUORUM;
```

And for serial consistency:

```sql
SERIAL CONSISTENCY LOCAL_SERIAL;
```

The active consistency level is displayed in the session action bar so you always know which level is in effect.

!!! note
    The consistency level applies to all queries executed in the current session. For details on configuring the default consistency level at connection time, see [Connection Configuration](../connections/cassandra.md).

---

## Keyboard Shortcuts Reference

The following shortcuts are available in the CQL Console for query execution and history navigation:

| Action | macOS | Windows / Linux |
| --- | --- | --- |
| Execute statement | <kbd>Cmd</kbd> + <kbd>Enter</kbd> | <kbd>Ctrl</kbd> + <kbd>Enter</kbd> |
| Previous history statement | <kbd>Cmd</kbd> + <kbd>Up Arrow</kbd> | <kbd>Ctrl</kbd> + <kbd>Up Arrow</kbd> |
| Next history statement | <kbd>Cmd</kbd> + <kbd>Down Arrow</kbd> | <kbd>Ctrl</kbd> + <kbd>Down Arrow</kbd> |
| Clear console | <kbd>Cmd</kbd> + <kbd>L</kbd> | <kbd>Ctrl</kbd> + <kbd>L</kbd> |
