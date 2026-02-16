---
title: "CQL Console"
description: "AxonOps Workbench CQL Console — a Monaco Editor-powered query editor with syntax highlighting, auto-completion, multi-tab support, and destructive command safety for Apache Cassandra."
meta:
  - name: keywords
    content: "CQL Console, CQL editor, Monaco Editor, syntax highlighting, auto-completion, query editor, Cassandra query, AxonOps Workbench"
---

# CQL Console

The CQL Console is the primary workspace in AxonOps Workbench — a Monaco Editor-powered query editor purpose-built for Cassandra Query Language. Built on the same editor technology as VS Code, the CQL Console provides a rich editing experience with syntax highlighting, context-aware auto-completion, and multi-tab support for working with your Cassandra clusters.

<!-- Screenshot: CQL Console showing Monaco editor with syntax highlighting and auto-completion dropdown -->

## Editor Features

### Syntax Highlighting

The CQL Console provides CQL-specific syntax highlighting with color coding for:

- **Keywords** — CQL commands such as `SELECT`, `INSERT`, `CREATE TABLE`, and `ALTER`
- **Data types** — Type identifiers including `text`, `int`, `uuid`, `timestamp`, and collection types
- **Functions** — Built-in functions such as `now()`, `toTimestamp()`, and aggregate functions
- **String literals** — Quoted values and constants
- **Comments** — Single-line and multi-line comment blocks

The editor also visually distinguishes between CQL statements and CQLSH shell commands, making it easy to identify the type of command you are writing.

### Auto-Completion

The CQL Console provides context-aware suggestions as you type, drawing from both the CQL language specification and your connected cluster's live schema:

- **CQL keywords and commands** — `SELECT`, `INSERT`, `CREATE TABLE`, `ALTER KEYSPACE`, and other standard CQL statements
- **CQLSH commands** — `DESCRIBE`, `SOURCE`, `CONSISTENCY`, `TRACING`, and other shell-level commands
- **Keyspace names** — All keyspaces available on the connected cluster
- **Table names** — Tables scoped to the active keyspace
- **Column names** — Columns scoped to the table referenced in the current query context

Auto-completion accelerates query writing and helps prevent typos in schema object names.

### Multi-Tab Support

The CQL Console supports multiple editor tabs per connection, allowing you to work on several queries at once:

- Open multiple editor tabs within a single connection
- Each tab maintains its own query state and result set
- Switch between tabs without losing your work

This is particularly useful when you need to cross-reference data across tables or iterate on related queries simultaneously.

### Destructive Command Safety

AxonOps Workbench detects potentially destructive CQL commands before they are executed and prompts you for confirmation. The following commands are protected:

- `DELETE`
- `DROP`
- `TRUNCATE`
- `INSERT`
- `UPDATE`
- `ALTER`
- `BATCH`
- `CREATE`
- `GRANT`
- `REVOKE`

!!! warning
    Destructive command detection is configurable. Review your Workbench settings to adjust which commands require confirmation and to enable or disable this safety feature.

### Keyboard Shortcuts

The CQL Console supports keyboard shortcuts for common operations, allowing you to work more efficiently without reaching for the mouse:

| Shortcut | Action |
| --- | --- |
| Execute query | Run the current CQL statement |
| Execute all | Run all statements in the editor |
| New tab | Open a new editor tab |
| Close tab | Close the current editor tab |
| Next tab / Previous tab | Switch between open editor tabs |

Keyboard shortcuts are configurable in **Settings**. For the full shortcut reference, see the [Query Execution](query-execution.md) guide.

## Notifications

The CQL Console includes an in-app notification center that keeps you informed about query activity and system events:

- **Query status** — Notifications when queries complete successfully or encounter errors
- **Warning messages** — Alerts about potential issues such as large result sets or tombstone warnings
- **Connection events** — Status changes for the active database connection

The notification indicator in the toolbar shows the count of unseen notifications. Click the indicator to open the notification panel and review recent messages.

## Detailed Guides

For in-depth coverage of specific CQL Console capabilities, see the following pages:

- **[Query Execution](query-execution.md)** — Running queries, the SOURCE command, pagination, and query history
- **[Query Tracing](query-tracing.md)** — Performance analysis with interactive trace visualization
- **[Results & Export](results-export.md)** — Exporting data to CSV and PDF, clipboard copy as JSON, and working with BLOB columns
