---
title: "AxonOps Workbench"
description: "AxonOps Workbench is a free, open-source desktop application for Apache Cassandra. A Cassandra-native query editor, schema browser, and cluster manager for developers and DBAs on macOS, Windows, and Linux."
meta:
  - name: keywords
    content: "AxonOps Workbench, Cassandra GUI, Cassandra desktop client, CQL editor, Cassandra schema browser, open source Cassandra tool, Cassandra IDE"
---

# AxonOps Workbench

AxonOps Workbench is a free, open-source desktop application purpose-built for Apache Cassandra. It provides developers and database administrators with a Cassandra-native query editor, schema browser, and connection manager -- all in a single, secure, cross-platform application.

Unlike generic database tools, AxonOps Workbench understands Cassandra's data model, CQL syntax, and cluster topology. Connections stay local to your machine, queries execute directly against your clusters, and there is no cloud dependency or telemetry.

---

## Key Features

<div class="grid cards" markdown>

-   :material-console-line:{ .lg .middle } **CQL Console**

    ---

    Full-featured query editor with CQL syntax highlighting, auto-completion, multi-tab support, and result export.

    [:octicons-arrow-right-24: Open CQL Console docs](cql-console/index.md)

-   :material-connection:{ .lg .middle } **Connection Management**

    ---

    Connect to local, remote, and cloud Cassandra clusters with support for SSL/TLS, authentication, and SSH tunneling.

    [:octicons-arrow-right-24: Manage connections](connections/index.md)

-   :material-database-search:{ .lg .middle } **Schema Browser**

    ---

    Explore keyspaces, tables, columns, indexes, materialized views, and user-defined types in a navigable tree view.

    [:octicons-arrow-right-24: Browse schema](schema.md)

-   :material-docker:{ .lg .middle } **Local Clusters**

    ---

    Spin up local Cassandra clusters with Docker directly from the Workbench for development and testing.

    [:octicons-arrow-right-24: Run local clusters](getting-started/local-clusters.md)

-   :material-folder-multiple:{ .lg .middle } **Workspaces**

    ---

    Organize connections, queries, and snippets into workspaces for different projects or environments.

    [:octicons-arrow-right-24: Set up workspaces](workspaces.md)

-   :material-chart-line:{ .lg .middle } **Query Tracing**

    ---

    Trace CQL query execution to understand performance characteristics and identify bottlenecks.

    [:octicons-arrow-right-24: Trace queries](cql-console/query-tracing.md)

-   :material-content-save:{ .lg .middle } **CQL Snippets**

    ---

    Save, organize, and reuse frequently used CQL statements across sessions and workspaces.

    [:octicons-arrow-right-24: Manage snippets](snippets.md)

-   :material-powershell:{ .lg .middle } **CLI**

    ---

    Launch and control AxonOps Workbench from the command line for scripting and automation workflows.

    [:octicons-arrow-right-24: CLI reference](cli.md)

-   :material-cog:{ .lg .middle } **Settings**

    ---

    Configure editor preferences, keyboard shortcuts, themes, and application behavior.

    [:octicons-arrow-right-24: Configure settings](settings.md)

-   :material-link-variant:{ .lg .middle } **AxonOps Integration**

    ---

    Connect to AxonOps Cloud or self-hosted AxonOps for cluster monitoring, alerting, and operational insights.

    [:octicons-arrow-right-24: Integrate with AxonOps](axonops-integration.md)

</div>

---

## Supported Databases

AxonOps Workbench works with the following Apache Cassandra-compatible databases:

- **Apache Cassandra** -- versions 4.0, 4.1, and 5.0
- **DataStax Enterprise (DSE)** -- DSE clusters with Cassandra workloads
- **DataStax Astra DB** -- cloud-native Cassandra-as-a-Service

---

## Supported Platforms

AxonOps Workbench runs natively on all major desktop operating systems:

- **macOS** -- Intel (x64) and Apple Silicon (arm64)
- **Windows** -- x64
- **Linux** -- x64 and arm64 (.deb and .AppImage packages)

---

## Open Source

AxonOps Workbench is released under the [Apache License 2.0](license.md), giving you the freedom to use, modify, and distribute it without restriction.

Source code, issue tracking, and contribution guidelines are available on [GitHub](https://github.com/axonops/axonops-workbench-cassandra){:target="_blank"}.

---

## Quick Start

Get up and running with AxonOps Workbench in three steps:

1. **Install** -- Download and install the application for your platform.
    [:octicons-arrow-right-24: Installation guide](getting-started/installation.md)

2. **Connect** -- Add your first Cassandra cluster connection.
    [:octicons-arrow-right-24: First steps](getting-started/first-steps.md)

3. **Query** -- Open the CQL Console and run your first query.
    [:octicons-arrow-right-24: Run your first query](cql-console/index.md)
